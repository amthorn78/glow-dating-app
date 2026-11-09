"""What the identity cases share (SV1; its brief's D10 and acceptance checks).

- ``SecretLedger``: every password, code, token, session key and key the run handles. It holds
  them only to show that none appears in any output; it never prints one.
- ``OutputCapture``: every log record at DEBUG, on the root logger, and everything the process
  writes to standard output and standard error while the suite runs (acceptance check 12).
- ``Device``: one app installation, Django's test client against the ``app`` client's endpoints
  with its own IP address. It keeps the tokens it is given, as the app would.
- ``Context``: synthetic members (``@example.invalid`` addresses, generated passwords) made
  through the HTTP endpoints, the fixture mail outbox and read-only database checks.
- ``recording_issued_codes``: each verification and reset code Glow's account adapter generates,
  recorded where it is issued, for the no-link check (``mail_forbidden_found``; correction C2).

A case fails with ``CaseFailed``, whose message names what failed and never a value.
"""

from __future__ import annotations

import io
import json
import logging
import re
import secrets
import sys
import threading
from collections.abc import Iterable, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from typing import Any, TextIO
from uuid import UUID

APP = "/_allauth/app/v1/"
ACCOUNT_ACCESS = "/api/v1/account/access"
CODE_PATTERN = re.compile(r"code is ([A-Z0-9]+(?:-[A-Z0-9]+)*)\.")
# What no message may hold (acceptance check 3; D8): a link, or a name but Glow's.
MAIL_FORBIDDEN = ("http", "://", "www.", "href", "<a", "allauth", "django", "example.com")
# The adapter methods that generate the codes a message carries (65.21.1).
CODE_GENERATORS = ("generate_email_verification_code", "generate_password_reset_code")


class CaseFailed(AssertionError):
    """A case's expectation did not hold. The message names no value."""


def expect(condition: object, what: str) -> None:
    if not condition:
        raise CaseFailed(what)


class SecretLedger:
    """Every secret value the run handles, kept to prove that none is ever output."""

    def __init__(self) -> None:
        self._values: set[str] = set()
        self._lock = threading.Lock()

    def add(self, value: object) -> None:
        if not isinstance(value, str) or len(value) < 6:
            return
        with self._lock:
            self._values.add(value)
            if value.count(".") == 2:  # a JWT: its parts are secrets too
                self._values.update(part for part in value.split(".") if len(part) >= 16)
            if "-" in value and len(value) <= 16:  # a dashed code, and its normalized form
                self._values.add(value.replace("-", ""))

    def count(self) -> int:
        with self._lock:
            return len(self._values)

    def found_in(self, text: str) -> int:
        """How many distinct secrets appear in ``text``. The values are never returned."""
        with self._lock:
            values = tuple(self._values)
        return sum(1 for value in values if value in text)


class _CaptureHandler(logging.Handler):
    def __init__(self, sink: list[str]) -> None:
        super().__init__(level=logging.DEBUG)
        self._sink = sink
        self.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._sink.append(self.format(record))
        except Exception:  # noqa: BLE001 - a record that cannot format is still counted
            self._sink.append(f"{record.levelname} {record.name} <unformattable>")


class _Tee(io.TextIOBase):
    def __init__(self, stream: TextIO, sink: list[str]) -> None:
        self._stream = stream
        self._sink = sink

    def write(self, text: str) -> int:
        self._sink.append(text)
        return self._stream.write(text)

    def flush(self) -> None:
        self._stream.flush()


class OutputCapture:
    """Every log record at DEBUG and every write to stdout and stderr, during the run."""

    def __init__(self) -> None:
        self.records: list[str] = []
        self.written: list[str] = []
        self._handler = _CaptureHandler(self.records)
        self._streams: tuple[TextIO, TextIO] | None = None
        self._level = logging.WARNING

    def install(self) -> None:
        root = logging.getLogger()
        self._level = root.level
        root.setLevel(logging.DEBUG)
        root.addHandler(self._handler)
        self._streams = (sys.stdout, sys.stderr)
        sys.stdout = _Tee(sys.stdout, self.written)
        sys.stderr = _Tee(sys.stderr, self.written)

    def uninstall(self) -> None:
        root = logging.getLogger()
        root.removeHandler(self._handler)
        root.setLevel(self._level)
        if self._streams is not None:
            sys.stdout, sys.stderr = self._streams
            self._streams = None

    def text(self) -> str:
        return "\n".join(self.records) + "\n" + "".join(self.written)


@dataclass
class Reply:
    status: int
    body: dict[str, Any] | None

    def meta(self) -> dict[str, Any]:
        meta = (self.body or {}).get("meta")
        return meta if isinstance(meta, dict) else {}

    def data(self) -> Any:
        return (self.body or {}).get("data")

    def tokens(self) -> set[str]:
        """Which credentials the reply carries (names only), in ``meta`` or ``data``."""
        data = self.data()
        carried = set(self.meta()) | (set(data) if isinstance(data, dict) else set())
        return {
            name for name in ("session_token", "access_token", "refresh_token") if name in carried
        }

    def flow_ids(self) -> set[str]:
        """The flows the reply offers, pending or not (a reauthentication answer's flows)."""
        data = self.data()
        flows = data.get("flows", []) if isinstance(data, dict) else []
        return {str(flow.get("id")) for flow in flows if isinstance(flow, dict)}

    def error_codes(self) -> list[str]:
        return [
            str(e.get("code")) for e in (self.body or {}).get("errors", []) if isinstance(e, dict)
        ]

    def pending(self) -> set[str]:
        data = self.data()
        flows = data.get("flows", []) if isinstance(data, dict) else []
        return {flow["id"] for flow in flows if isinstance(flow, dict) and flow.get("is_pending")}

    def shape(self) -> tuple[Any, ...]:
        """What enumeration resistance compares: the status, the keys, the flows and the
        credential names, never a value."""
        data = self.data()
        flows = data.get("flows", []) if isinstance(data, dict) else []
        flow_shape = tuple(sorted((str(f.get("id")), bool(f.get("is_pending"))) for f in flows))
        data_keys = tuple(sorted(data)) if isinstance(data, dict) else type(data).__name__
        return (
            self.status,
            tuple(sorted(self.body or {})),
            data_keys,
            flow_shape,
            tuple(sorted(self.tokens())),
        )


class Device:
    """One app installation: Django's test client with its own IP address."""

    def __init__(self, ledger: SecretLedger, ip: str) -> None:
        from django.test import Client

        self.ledger = ledger
        self.ip = ip
        self.client = Client(
            REMOTE_ADDR=ip, HTTP_USER_AGENT="glow-identity-proof", raise_request_exception=False
        )
        self.session_token: str | None = None
        self.access: str | None = None
        self.refresh: str | None = None

    def call(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        *,
        bearer: str | None = None,
        session_token: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Reply:
        sent = dict(headers or {})
        if bearer:
            sent["Authorization"] = f"Bearer {bearer}"
        if session_token:
            sent["X-Session-Token"] = session_token
        payload = json.dumps(body) if body is not None else ""
        response = self.client.generic(
            method, path, data=payload, content_type="application/json", headers=sent
        )
        parsed: dict[str, Any] | None = None
        if response.get("Content-Type", "").startswith("application/json"):
            try:
                value = json.loads(response.content.decode("utf-8"))
                parsed = value if isinstance(value, dict) else None
            except ValueError:
                parsed = None
        reply = Reply(response.status_code, parsed)
        # A sign-in puts its credentials in ``meta``; a refresh puts the new pair in ``data``
        # (allauth's RefreshTokenResponse).
        carriers = [reply.meta()]
        if isinstance(reply.data(), dict):
            carriers.append(reply.data())
        for carrier in carriers:
            for name in ("session_token", "access_token", "refresh_token"):
                self.ledger.add(carrier.get(name))
            if isinstance(carrier.get("session_token"), str):
                self.session_token = carrier["session_token"]
            if isinstance(carrier.get("access_token"), str):
                self.access = carrier["access_token"]
            if isinstance(carrier.get("refresh_token"), str):
                self.refresh = carrier["refresh_token"]
        return reply

    def app(
        self, method: str, endpoint: str, body: dict[str, Any] | None = None, **kw: Any
    ) -> Reply:
        return self.call(method, APP + endpoint, body, **kw)

    def account_access(self, bearer: str | None, **kw: Any) -> Reply:
        return self.call("GET", ACCOUNT_ACCESS, bearer=bearer, **kw)


@dataclass
class Member:
    email: str
    password: str
    user_id: int
    account_id: UUID
    device: Device


@dataclass
class Context:
    ledger: SecretLedger
    case_id: str = ""
    _ips: Iterator[int] = field(default_factory=lambda: iter(range(1, 1_000_000)))
    # Who may receive mail: an address an account was made with, or one a signed-in member
    # asked to move to; never an address that has no account (the unknown reset address).
    account_addresses: set[str] = field(default_factory=set)
    asked_addresses: set[str] = field(default_factory=set)
    unknown_addresses: set[str] = field(default_factory=set)
    # Every code the run issued, as allauth's adapter generated it (correction C2). Secrets:
    # each is in the ledger too, and none is ever output.
    issued_codes: list[str] = field(default_factory=list)

    # -- synthetic people ------------------------------------------------------------------

    def email(self) -> str:
        stem = re.sub(r"[^a-z0-9]+", "-", self.case_id.lower()).strip("-")[:24]
        return f"{stem}.{secrets.token_hex(4)}@example.invalid"

    def password(self) -> str:
        value = "Synthetic-" + secrets.token_urlsafe(18)
        self.ledger.add(value)
        return value

    def device(self) -> Device:
        # Each device gets its own address from the documentation ranges (RFC 5737).
        n = next(self._ips)
        nets = ("203.0.113", "198.51.100", "192.0.2")
        return Device(self.ledger, f"{nets[(n // 254) % 3]}.{1 + n % 254}")

    def record_issued_code(self, code: object) -> None:
        if isinstance(code, str) and code:
            self.ledger.add(code)
            self.issued_codes.append(code)

    @staticmethod
    def clear_rate_limits() -> None:
        """allauth's rate limits live in Django's cache, among them one verification mail per
        address every 10 seconds (by code, a second one within the window answers 429). A case
        that sends a second code to one address on purpose clears them first, as if the window
        had passed; every case starts with them cleared."""
        from django.core.cache import cache

        cache.clear()

    # -- mail ------------------------------------------------------------------------------

    @staticmethod
    def mail_mark() -> int:
        from glow_identity import mail

        return len(mail.outbox())

    @staticmethod
    def mail_since(mark: int, to: str | None = None) -> list[Any]:
        from glow_identity import mail

        messages = list(mail.outbox())[mark:]
        return [m for m in messages if to is None or to in m.to]

    def code_since(self, mark: int, to: str) -> str:
        messages = self.mail_since(mark, to)
        expect(messages, "a code message was sent to the address")
        found = CODE_PATTERN.search(messages[-1].body)
        expect(found, "the message holds a code")
        assert found is not None
        code = found.group(1)
        self.ledger.add(code)
        return code

    # -- members, through the HTTP endpoints -----------------------------------------------

    def sign_up(self, device: Device, email: str, password: str) -> Reply:
        self.account_addresses.add(email)
        return device.app("POST", "auth/signup", {"email": email, "password": password})

    def verify(self, device: Device, code: str, **kw: Any) -> Reply:
        return device.app(
            "POST", "auth/email/verify", {"key": code}, session_token=device.session_token, **kw
        )

    def member(self) -> Member:
        """A verified, signed-in member: sign-up, then the code from the fixture mail."""
        device = self.device()
        email, password = self.email(), self.password()
        mark = self.mail_mark()
        signed_up = self.sign_up(device, email, password)
        expect(signed_up.status == 401, "sign-up answers 401 with a pending verification")
        verified = self.verify(device, self.code_since(mark, email))
        expect(verified.status == 200, "verification signs the member in")
        expect(device.access and device.refresh, "verification returns the token pair")
        user_id, account_id = self.ids(email)
        return Member(email, password, user_id, account_id, device)

    @staticmethod
    def reauthenticate(device: Device, password: str) -> Reply:
        """``POST auth/reauthenticate`` with the device's access token (D3, correction C1):
        what an address change needs first, within 300 seconds, in the same session."""
        return device.app(
            "POST", "auth/reauthenticate", {"password": password}, bearer=device.access
        )

    def sign_in(self, member: Member) -> Device:
        device = self.device()
        reply = device.app(
            "POST", "auth/login", {"email": member.email, "password": member.password}
        )
        expect(reply.status == 200, "a verified member signs in")
        expect(device.access and device.refresh, "sign-in returns the token pair")
        return device

    # -- the database, read only -----------------------------------------------------------

    @staticmethod
    def ids(email: str) -> tuple[int, UUID]:
        from allauth.account.models import EmailAddress
        from glow_persistence.models import AppAccount

        user_id = EmailAddress.objects.values_list("user_id", flat=True).get(email=email)
        account_id = AppAccount.objects.values_list("pk", flat=True).get(auth_user_id=user_id)
        return int(user_id), account_id

    def session_key_of(self, access_token: str) -> str:
        """The harness's own read of a token's session key (allauth's decryption), for the
        checks; it is added to the ledger and never output."""
        from allauth.headless.tokens.strategies.jwt import internal

        payload = internal.decode_token(access_token, "access")
        if payload is None:
            payload = _unverified_claims(access_token)
        key = internal.session_key_from_sid(str(payload.get("sid", "")))
        expect(key, "the token names a session")
        assert key is not None
        self.ledger.add(key)
        return str(key)

    @staticmethod
    def django_session_exists(session_key: str) -> bool:
        from django.contrib.sessions.models import Session
        from django.utils import timezone

        return bool(
            Session.objects.filter(session_key=session_key, expire_date__gt=timezone.now()).exists()
        )

    @staticmethod
    def user_session_ref(session_key: str) -> str | None:
        from allauth.usersessions.models import UserSession

        pk = (
            UserSession.objects.filter(session_key=session_key).values_list("pk", flat=True).first()
        )
        return None if pk is None else str(pk)

    @staticmethod
    def account_session(reference: str) -> Any:
        from glow_persistence.models import AccountSession

        return AccountSession.objects.filter(auth_session_ref=reference).first()

    def account_session_of(self, access_token: str) -> Any:
        reference = self.user_session_ref(self.session_key_of(access_token))
        expect(reference is not None, "the token's session has its UserSession row")
        assert reference is not None
        row = self.account_session(reference)
        expect(row is not None, "the session has its AccountSession")
        return row

    @staticmethod
    def allauth_accepts(access_token: str) -> bool:
        """allauth's layer: JWTTokenAuthentication, with stateful validation as configured."""
        from allauth.headless.contrib.rest_framework.authentication import JWTTokenAuthentication
        from rest_framework.exceptions import AuthenticationFailed

        try:
            JWTTokenAuthentication().authenticate_credentials(access_token)
        except AuthenticationFailed:
            return False
        return True

    @staticmethod
    def events(aggregate_id: UUID, event_type: str) -> int:
        from glow_persistence.models import OutboxEvent

        return int(
            OutboxEvent.objects.filter(aggregate_id=aggregate_id, event_type=event_type).count()
        )

    @staticmethod
    def event_count() -> int:
        from glow_persistence.models import OutboxEvent

        return int(OutboxEvent.objects.count())


def _unverified_claims(token: str) -> dict[str, Any]:
    """A token's claims without checking it: the harness uses this only to find the session
    an expired token names, to show that the session was not ended."""
    import jwt

    claims = jwt.decode(token, options={"verify_signature": False})
    assert isinstance(claims, dict)
    return claims


def mail_forbidden_found(text: str, issued_codes: Iterable[str]) -> list[str]:
    """Which of ``MAIL_FORBIDDEN`` a message's text holds (acceptance check 3; D8), by name.

    Correction C2 (DM-48 C2.5): the check removes the exact code the case issued, every
    occurrence, before it looks for ``http`` and ``www.``. It removes nothing else and uses no
    pattern, so a link anywhere else in the message still fails it. A code is eight letters
    from allauth's alphabet, which has ``H``, ``T``, ``P`` and ``W``, so a code can spell
    ``HTTP``, or end in ``WWW`` before a sentence's full stop."""
    for code in issued_codes:
        if code:
            text = text.replace(code, "")
    lowered = text.lower()
    return [forbidden for forbidden in MAIL_FORBIDDEN if forbidden in lowered]


@contextmanager
def recording_issued_codes(ctx: Context) -> Iterator[None]:
    """Within the block, each code Glow's account adapter generates is recorded where it is
    issued (``Context.record_issued_code``), and returned to allauth unchanged."""
    from unittest import mock

    from glow_identity.adapter import GlowAccountAdapter

    def recorder(name: str) -> Any:
        generate = getattr(GlowAccountAdapter, name)

        def recorded(adapter: Any) -> Any:
            code = generate(adapter)
            ctx.record_issued_code(code)
            return code

        return recorded

    with ExitStack() as stack:
        for name in CODE_GENERATORS:
            stack.enter_context(mock.patch.object(GlowAccountAdapter, name, recorder(name)))
        yield


@contextmanager
def clock_ahead(module: Any, seconds: float) -> Iterator[None]:
    """allauth's code processes and its rate limiter read ``time.time()``; within the block,
    ``module``'s clock runs ``seconds`` ahead (the code limits' boundary, the limiter's window),
    and nothing else's. The limiter's ``cache_lock`` also calls ``time.monotonic()`` and
    ``time.sleep()`` (65.21.1, ``core/internal/ratelimit.py:47-56``), so the moved clock keeps
    both, unmoved (correction C2, DM-48 section 3)."""
    import time
    from types import SimpleNamespace
    from unittest import mock

    fake = SimpleNamespace(
        time=lambda: time.time() + seconds, monotonic=time.monotonic, sleep=time.sleep
    )
    with mock.patch.object(module, "time", fake):
        yield
