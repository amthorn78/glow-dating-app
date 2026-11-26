"""What the chat cases share (SV4 A2; its brief's D8 to D10).

The cases' own members are built through SV1's sign-in and SV2's member routes, with the discovery
suite's helpers (``discovery_support.DiscoveryContext``, imported unchanged), and matched the only
way there is, reciprocal likes through SV3's like (``interaction_cases._matched``, unchanged). Then:

- **The provider** (D8): one in-memory fixture provider (``FixtureChatProvider``, the test
  environment's), the one ``chat_settings`` names as the history read's text reader
  (``text_reader``). Every chat event is delivered to it through ``glow_chat``'s
  ``OutboxDelivery``, as the ordering suite's read phase delivers; no provider call leaves the
  process;
- **The routes** (D8): ``ChatContext``'s helpers send each request through Django's test client
  with the member's own access token, as SV1's device does, and check every served body against
  the contract's own schema (``ProfileContext.data``: an extra field fails); the versions they
  send come from the reads a client has (the match read's ``version``, D6), never from a row;
- **The values**: each message's text is synthetic and unique to the run, and joins the value
  ledger, so the suite's scan finds it in no log record, write or results JSON; the provider's
  own identifiers (channels and messages) join it too, so none is served or logged;
- **Holds** (``Hold``): a transaction probe that holds its transaction at any of its points until
  the case releases it, recording its backend; it only signals and waits (DM-13 2.1);
- **The list's statements** (``lock_statements``): every statement this thread's connection runs
  inside a block that takes a row lock, with its parameters, kept in memory for the bounded-lock
  case's check and never logged;
- **F12** (SV4 B1; its brief's D16, D19 and D29): the token store and the push transport the chat
  settings name (``token_store``, ``push_transport``), the in-memory fixtures of the test
  environment, the token store observed as the suite calls it (each reference it issues, and
  whether each ``put`` ran inside a transaction, AM4); the synthetic push tokens, a pool derived
  from the run's ``SECRET_KEY`` (``chat_scan.push_tokens``), every one held among the run's
  secrets from the start; and each installation identifier, made at random and held among the
  member values, so neither a token nor an installation is logged, written or served. F12's routes
  are called with the member's own access token and the ``Glow-Installation-Id`` header.

Rows written only in setup (a seeded population and its matches, a state no writer leaves) are test
data, never an application writer, and each is named where a case writes it.
"""

from __future__ import annotations

import re
import secrets
import threading
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from glow_ordering_proof.discovery_support import DiscoveryContext
from glow_ordering_proof.identity_support import Member, Reply, expect
from glow_ordering_proof.profile_support import ProfileContext

MESSAGES = "/api/v1/chat/messages"
CONVERSATIONS = "/api/v1/chat/conversations"
HISTORY = "/api/v1/chat/history"
READ_CURSOR = "/api/v1/chat/read-cursor"
MATCHES = "/api/v1/matches"
CHAT_ROUTES = (MESSAGES, CONVERSATIONS, HISTORY, READ_CURSOR)
# SV4 B1 (D19): F12's three routes, and the header naming the requesting installation.
NOTIFICATIONS = "/api/v1/notifications"
DEVICE = "/api/v1/notifications/device"
NOTIFICATION_SETTINGS = "/api/v1/notifications/settings"
NOTIFICATION_ROUTES = (NOTIFICATIONS, DEVICE, NOTIFICATION_SETTINGS)
INSTALLATION_HEADER = "Glow-Installation-Id"

REACH_SECONDS = 10.0
HOLD_SECONDS = 60.0

_PROVIDER: Any = None
_PROVIDER_LOCK = threading.Lock()
_TRANSPORT: Any = None


def provider() -> Any:
    """The suite's one fixture provider: delivery's target and the reads' text reader."""
    global _PROVIDER
    from glow_domain.chat_provider_fixtures import FixtureChatProvider

    with _PROVIDER_LOCK:
        if _PROVIDER is None:
            _PROVIDER = FixtureChatProvider(environment="test")
        return _PROVIDER


def text_reader() -> Any:
    """D8: the factory ``chat_settings`` names (``GLOW_CHAT_TEXT_READER``)."""
    return provider()


class ObservedTokenStore:
    """The suite's token store: the in-memory fixture (``FixtureTokenStore``, the test
    environment's), each call passed to it unchanged and observed: the reference each ``put``
    issued, and whether a transaction was open on the calling connection when it ran (AM4: the
    ``put`` runs before the command's transaction, never inside it). Nothing observed is logged."""

    def __init__(self) -> None:
        from glow_domain.notification_fixtures import FixtureTokenStore

        self.fixture = FixtureTokenStore(environment="test")
        self.issued: list[str] = []
        self.inside_a_transaction: list[bool] = []

    def __repr__(self) -> str:
        return "ObservedTokenStore(<fixture>)"

    def put(self, token: Any) -> Any:
        from django.db import connection

        self.inside_a_transaction.append(
            bool(connection.in_atomic_block or not connection.get_autocommit())
        )
        reference = self.fixture.put(token)
        self.issued.append(str(reference.value))
        return reference

    def discard(self, reference: Any) -> None:
        self.fixture.discard(reference)


_TOKENS: ObservedTokenStore | None = None


def token_store() -> ObservedTokenStore:
    """D16 (DM-101's AM1): the factory ``chat_settings`` names (``GLOW_NOTIFICATIONS_TOKEN_STORE``),
    the suite's one token store."""
    global _TOKENS
    with _PROVIDER_LOCK:
        if _TOKENS is None:
            _TOKENS = ObservedTokenStore()
        return _TOKENS


def push_transport() -> Any:
    """D16 (DM-101's AM1): the factory ``chat_settings`` names
    (``GLOW_NOTIFICATIONS_PUSH_TRANSPORT``), the suite's one push transport, the in-memory fixture
    (``FixturePushTransport``). SV4 B1 calls no transport; SV4 B2's deliverer takes this one."""
    global _TRANSPORT
    from glow_domain.notification_fixtures import FixturePushTransport

    with _PROVIDER_LOCK:
        if _TRANSPORT is None:
            _TRANSPORT = FixturePushTransport(environment="test")
        return _TRANSPORT


class Hold:
    """A transaction probe that holds its transaction at the named points (``after_first_lock``,
    ``after_locks``, ``before_commit``) until the case releases them; it records its backend's
    pid. It only signals and waits (DM-13 2.1)."""

    POINTS = ("after_first_lock", "after_locks", "before_commit")
    after_first_lock: Callable[[], None] | None
    after_locks: Callable[[], None] | None
    before_commit: Callable[[], None] | None

    def __init__(self, *points: str) -> None:
        unknown = set(points) - set(self.POINTS)
        if unknown:
            raise ValueError("an unknown hold point")
        self.pid: int | None = None
        self.reached = {name: threading.Event() for name in points}
        self.release = {name: threading.Event() for name in points}
        for name in self.POINTS:
            setattr(self, name, self._hold(name) if name in points else None)

    def on_begin(self, pid: int) -> None:
        self.pid = pid

    def _hold(self, name: str) -> Callable[[], None]:
        def hold() -> None:
            self.reached[name].set()
            self.release[name].wait(HOLD_SECONDS)

        return hold

    def wait_pid(self) -> int:
        deadline = threading.Event()
        for _ in range(int(REACH_SECONDS * 100)):
            if self.pid is not None:
                return self.pid
            deadline.wait(0.01)
        raise AssertionError("the transaction did not report its backend")

    def free(self) -> None:
        for event in self.release.values():
            event.set()


@dataclass
class Sent:
    """Every statement inside a block that takes a row lock, with its parameters; in memory only."""

    statements: list[tuple[str, Any]] = field(default_factory=list)
    order: list[str] = field(default_factory=list)


LOCKING = re.compile(r"\bFOR\s+(NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\b", re.IGNORECASE)


@contextmanager
def lock_statements() -> Iterator[Sent]:
    """Every statement this thread's connection runs inside the block: each locking statement's
    text and parameters, and the order of every statement's first word, for the bounded list's
    check (D8). Nothing recorded is logged or kept after the case."""
    from django.db import connection

    sent = Sent()

    def record(execute: Callable[..., Any], sql: str, params: Any, many: bool, ctx: Any) -> Any:
        text = str(sql)
        sent.order.append(text)
        if LOCKING.search(text):
            sent.statements.append((text, params))
        return execute(sql, params, many, ctx)

    with connection.execute_wrapper(record):
        yield sent


@dataclass
class ChatContext:
    discovery: DiscoveryContext
    delivery: Any = None
    # The texts the cases sent, by submission ID, for the history checks; each is in the ledger.
    texts: dict[str, str] = field(default_factory=dict)
    # SV4 B1 (D29): the push tokens the cases drew from the pool, in order, and the installations
    # they made; each token is among the run's secrets, each installation among its member values.
    drawn_tokens: list[str] = field(default_factory=list)
    installations: list[str] = field(default_factory=list)

    @property
    def profiles(self) -> ProfileContext:
        return self.discovery.profiles

    # -- members and matches -------------------------------------------------------------------

    def visible(self, **kwargs: Any) -> Member:
        return self.discovery.visible(**kwargs)

    def matched(self, first: Member, second: Member) -> Any:
        """A match made the only way there is, reciprocal likes through SV3's like; then every
        chat event delivered, so its channel exists at the provider."""
        from glow_ordering_proof.interaction_cases import _matched

        match = _matched(self.discovery, first, second)
        self.deliver()
        return match

    def deliver(self) -> int:
        """Every due chat event delivered to the suite's provider; a retry is a fixture fault."""
        from glow_chat.delivery import OutboxDelivery

        if self.delivery is None:
            self.delivery = OutboxDelivery(provider())
        count = 0
        for _ in range(100):
            done = self.delivery.deliver_due(limit=1000)
            if not done:
                self.hold_provider_ids()
                return count
            count += len(done)
            expect(
                done[-1].outcome not in ("retry", "lost_lease"),
                f"delivery stalled: {done[-1].event_type} {done[-1].outcome}",
            )
        raise AssertionError("delivery did not finish")

    def hold_provider_ids(self) -> None:
        """The provider's own identifiers join the value ledger: none may be served or logged."""
        from glow_persistence.models import ChatBinding, ChatIdentity, MessageSubmission

        for value in (
            *ChatBinding.objects.exclude(channel_ref=None).values_list("channel_ref", flat=True),
            *ChatIdentity.objects.values_list("user_ref", flat=True),
            *MessageSubmission.objects.exclude(provider_message_ref=None).values_list(
                "provider_message_ref", flat=True
            ),
            # SV4 B1: the token store's references, none of which is served or logged either.
            *token_store().issued,
        ):
            self.profiles.values.add(str(value))

    # -- F12's routes (SV4 B1; D19) -------------------------------------------------------------

    def push_token(self) -> str:
        """The next synthetic push token of the run's pool (``chat_scan.push_tokens``), held among
        the run's secrets from the start; a case that would draw past the pool fails."""
        from django.conf import settings

        from glow_ordering_proof.chat_scan import PUSH_TOKEN_POOL, push_tokens

        index = len(self.drawn_tokens)
        expect(index < PUSH_TOKEN_POOL, "the run's pool holds another push token")
        token = push_tokens(str(settings.SECRET_KEY), index + 1)[index]
        self.drawn_tokens.append(token)
        return token

    def installation(self) -> str:
        """A new installation identifier, made at random, as the app makes one for each installation
        (P09.2; AM7), held among the member values: never logged, printed or served."""
        value = str(uuid.uuid4())
        self.profiles.values.add(value)
        self.installations.append(value)
        return value

    def notification_call(
        self,
        member: Member,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        *,
        installation: str | None,
        **kwargs: Any,
    ) -> Reply:
        """F12's routes, with the member's own access token and, unless ``None``, the
        ``Glow-Installation-Id`` header."""
        headers = dict(kwargs.pop("headers", None) or {})
        if installation is not None:
            headers[INSTALLATION_HEADER] = installation
        return self.profiles.call(member, method, path, body, headers=headers, **kwargs)

    def device_body(
        self,
        installation: str,
        action: str,
        version: int,
        *,
        token: str | None = None,
        key: str | None = None,
    ) -> dict[str, Any]:
        return {
            "operation": "device",
            "meta": {"idempotency_key": key or self.profiles.key(), "expected_version": version},
            "device_id": installation,
            "action": action,
            "provider_token": token,
        }

    def register(
        self,
        member: Member,
        installation: str,
        version: int = 0,
        *,
        token: str | None = None,
        key: str | None = None,
    ) -> Reply:
        """A ``DeviceIntent`` ``register`` from the installation, with a new token of the pool."""
        body = self.device_body(
            installation, "register", version, token=token or self.push_token(), key=key
        )
        return self.notification_call(member, "POST", DEVICE, body, installation=installation)

    def revoke(
        self, member: Member, installation: str, version: int, *, key: str | None = None
    ) -> Reply:
        body = self.device_body(installation, "revoke", version, key=key)
        return self.notification_call(member, "POST", DEVICE, body, installation=installation)

    def settings_body(
        self, match: bool, message: bool, version: int, *, key: str | None = None
    ) -> dict[str, Any]:
        return {
            "operation": "notifications",
            "meta": {"idempotency_key": key or self.profiles.key(), "expected_version": version},
            "match_notifications": match,
            "message_notifications": message,
        }

    def save_settings(
        self,
        member: Member,
        installation: str,
        match: bool,
        message: bool,
        version: int,
        *,
        key: str | None = None,
    ) -> Reply:
        body = self.settings_body(match, message, version, key=key)
        return self.notification_call(
            member, "POST", NOTIFICATION_SETTINGS, body, installation=installation
        )

    def read_settings(self, member: Member, installation: str) -> Reply:
        return self.notification_call(member, "GET", NOTIFICATIONS, installation=installation)

    def notifications(self, reply: Reply, what: str) -> dict[str, Any]:
        """A served ``NotificationSettings``, checked against the contract's schema."""
        return self.profiles.data(reply, "notifications", what)

    # -- the reads a client has ----------------------------------------------------------------

    def match_read(self, member: Member, match_id: Any) -> Reply:
        return self.profiles.call(member, "GET", f"{MATCHES}/{match_id}")

    def match_version(self, member: Member, match_id: Any) -> int:
        """D6: the version a send carries, as a participant learns it, from the match read; a
        match read that is refused fails the case (A2R-8), never a version made up for it."""
        reply = self.match_read(member, match_id)
        return int(self.profiles.data(reply, "match", "the match read")["version"])

    def match_list(self, member: Member) -> dict[str, Any]:
        reply = self.profiles.call(member, "GET", MATCHES)
        return self.profiles.data(reply, "match_list", "the match list")

    # -- chat's routes (D8) --------------------------------------------------------------------

    def text(self) -> str:
        """A synthetic message, unique to the run; it joins the value ledger."""
        value = f"A synthetic chat message {secrets.token_hex(8)}."
        self.profiles.values.add(value)
        return value

    def message(
        self,
        member: Member,
        match_id: Any,
        *,
        text: str | None = None,
        key: str | None = None,
        expected: int | None = None,
    ) -> dict[str, Any]:
        return {
            "operation": "message",
            "meta": {
                "idempotency_key": key or self.profiles.key(),
                "expected_version": (
                    self.match_version(member, match_id) if expected is None else expected
                ),
            },
            "match_id": str(match_id),
            "text": text if text is not None else self.text(),
        }

    def send(self, member: Member, body: dict[str, Any]) -> Reply:
        return self.profiles.call(member, "POST", MESSAGES, body)

    def sent(self, member: Member, match_id: Any, *, deliver: bool = True) -> str:
        """A send through the route, answered ``pending``; then delivered, so it is accepted."""
        body = self.message(member, match_id)
        served = self.profiles.data(self.send(member, body), "message", "the send")
        expect(served["state"] == "pending" and served["version"] == 1, "a new send is pending")
        self.texts[str(served["submission_id"])] = str(body["text"])
        if deliver:
            self.deliver()
        return str(served["submission_id"])

    def history_reply(
        self, member: Member, match_id: Any, cursor: str | None = None, limit: int = 50
    ) -> Reply:
        body = {"match_id": str(match_id), "cursor": cursor, "limit": limit}
        return self.profiles.call(member, "POST", HISTORY, body)

    def history(
        self, member: Member, match_id: Any, cursor: str | None = None, limit: int = 50
    ) -> dict[str, Any]:
        reply = self.history_reply(member, match_id, cursor, limit)
        page = self.profiles.data(reply, "message_page", "the history page")
        expect(page["match_id"] == str(match_id), "the page names its match")
        return page

    def conversations_reply(self, member: Member) -> Reply:
        return self.profiles.call(member, "GET", CONVERSATIONS)

    def conversations(self, member: Member) -> dict[str, dict[str, Any]]:
        """The member's list, by match ID."""
        reply = self.conversations_reply(member)
        listed = self.profiles.data(reply, "conversation_list", "the conversation list")
        return {str(c["match_id"]): c for c in listed["conversations"]}

    def cursor_reply(self, member: Member, match_id: Any, submission_id: str) -> Reply:
        body = {
            "operation": "read_cursor",
            "match_id": str(match_id),
            "submission_id": submission_id,
        }
        return self.profiles.call(member, "POST", READ_CURSOR, body)

    def cursor(self, member: Member, match_id: Any, submission_id: str) -> dict[str, Any]:
        reply = self.cursor_reply(member, match_id, submission_id)
        return self.profiles.data(reply, "conversation", "the read cursor")

    # -- what every surface serves a member about one match (D4, D5) ---------------------------

    def surfaces(self, member: Member, match_id: Any, submission_id: str) -> dict[str, Any]:
        """What chat's routes and the match routes serve ``member`` about the match, each as its
        status and code, or its served state: the send (with the version the match read gives),
        the history page, the list entry, the read cursor, the match read and the match list."""

        def outcome(reply: Reply) -> tuple[int, str]:
            body = reply.body or {}
            if reply.status == 200:
                data = body.get("data") or {}
                return 200, str(data.get("state", data.get("kind", "")))
            return reply.status, str(body.get("code"))

        listed = self.conversations(member)
        entry = listed.get(str(match_id))
        read = self.match_read(member, match_id)
        read_data = (read.body or {}).get("data") or {}
        return {
            "send": outcome(self.send(member, self.message(member, match_id))),
            "history": outcome(self.history_reply(member, match_id)),
            "listed": None if entry is None else entry["state"],
            "cursor": outcome(self.cursor_reply(member, match_id, submission_id)),
            "match": (read.status, read_data.get("state"), read_data.get("version")),
            "match_list": [m["match_id"] for m in self.match_list(member)["matches"]].count(
                str(match_id)
            ),
        }


def session_of(member: Member) -> UUID:
    """The member's valid session, for a call of the reads with a probe (the routes' own code)."""
    from glow_persistence.models import AccountSession

    found = (
        AccountSession.objects.filter(account_id=member.account_id, state="valid")
        .order_by("-created_at")
        .values_list("id", flat=True)
        .first()
    )
    expect(found is not None, "the member has a valid session")
    return UUID(str(found))


def route_reads() -> Any:
    """The reads chat's routes serve (``glow_chat.route_reads``), with the suite's provider."""
    from glow_chat.route_reads import RouteConversationReads

    return RouteConversationReads(provider())
