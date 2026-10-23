"""The conformance run of the Stream adapter (P06.2 Stage B2; the brief's design point g,
with DM-16 1.1, 4.3, 4.4, 4.6, 4.7 and 5.2).

``python -m glow_stream_proof conformance`` runs the app's Stream adapter
(``services/api/glow_domain/chat_provider_stream.py``) against the development application,
on the harness's own server client, so that every request the adapter makes passes the
run's guard, is counted in the usage ledger before it is sent, is checked for a charge or
limit signal, and is redacted like every other request of this harness. The run is a
:class:`~glow_stream_proof.proof_run.ProofRun` (its preflight, its guard scope, its
cleanup, its end of run), with the adapter's rows in place of the bypass matrix.

**The import route** (DM-16 4.6): :func:`load_api_modules` adds ``services/api`` to the
import path for this command only and imports the adapter, the port, the fixture adapter and
the token module, which load without Django.

**Two subjects, one contract** (design point f): every operation row is made on the fixture
adapter in memory and on the Stream adapter live, with the same identifiers, and the two
outcomes are compared. A difference is a finding, reported, never fixed silently; for the
causes delivery acts on (the provider halves of F3 and CX6: a removal from a channel Stream
does not have, and a deactivation, a revocation or a channel creation naming a user Stream
does not have) a difference blocks B2's merge until it is dispositioned (DM-16 5.2). Two
rows are stated as recorded: a send by a removed member (4.7), where the fixture refuses
and Stream's answer is recorded (an acceptance is a reported difference, not a failure), and
a token whose ``iat`` equals the sent cut-off, which shows Stream's comparison at the
whole-second boundary.

**Identifiers**: the run's prefix plus ``secrets.token_hex(16)`` (49 characters), so the
guard's ownership by prefix, ``verify-clean`` and ``cleanup --apply`` work unchanged.

**Before its first changing request** (1.1) the command runs ``configuration.verify`` and
``products.verify`` on a fresh snapshot (:func:`start_refusals`) and refuses to start unless
both are empty; then the run's own preflight runs as for ``run``.
"""

from __future__ import annotations

import importlib
import json
import secrets
import sys
import time
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from types import ModuleType
from typing import Any

from . import matrix
from . import proof_run as pr
from .client_bridge import ClientSessionEnded
from .credentials import ServerCredentials
from .proof_run import PREFIX_ROOT, ProofRun, RunStopped
from .redaction import Redactor, describe_token
from .server_api import ServerApi
from .usage import UsageLedger
from .workdir import PROOF_ROOT

API_ROOT = PROOF_ROOT.parent.parent / "services" / "api"
T = pr.T
# A token signed after a revocation is used only once the wall clock has passed its
# ``iat`` by this margin, so Stream never sees an ``iat`` in its own future.
AFTER_REVOCATION_MARGIN_SECONDS = 3.0
# A user object's standard keys, as Stream's listing returns them; any other key a
# provisioned user carries is recorded by name (never by value).
USER_STANDARD_KEYS = frozenset(
    {
        "id",
        "role",
        "created_at",
        "updated_at",
        "last_active",
        "banned",
        "online",
        "invisible",
        "language",
        "shadow_banned",
        "teams",
        "blocked_user_ids",
        "custom",
        "deactivated_at",
        "revoke_tokens_issued_before",
        "privacy_settings",
        "teams_role",
        "ban_expires",
        "deleted_at",
        "avg_response_time",
    }
)
CHANNEL_STANDARD_KEYS = frozenset(
    {
        "id",
        "cid",
        "type",
        "created_at",
        "updated_at",
        "last_message_at",
        "created_by",
        "frozen",
        "disabled",
        "config",
        "own_capabilities",
        "member_count",
        "message_count",
        "custom",
        "hidden",
        "blocked",
        "truncated_at",
        "truncated_by",
        "deleted_at",
        "team",
        "cooldown",
        "filter_tags",
        "auto_translation_enabled",
        "auto_translation_language",
        "hide_messages_before",
        "mute_expires_at",
        "muted",
    }
)
TEXT = "hello from the conformance run"

Modules = tuple[ModuleType, ModuleType, ModuleType, ModuleType]


def load_api_modules() -> Modules:
    """The import route (DM-16 4.6): ``services/api`` joins the import path for this
    command only, and the port, the fixture adapter, the Stream adapter and the token module
    are imported; each loads without Django."""
    path = str(API_ROOT)
    if path not in sys.path:
        sys.path.insert(0, path)
    port = importlib.import_module("glow_domain.chat_provider")
    fixtures = importlib.import_module("glow_domain.chat_provider_fixtures")
    adapter = importlib.import_module("glow_domain.chat_provider_stream")
    tokens = importlib.import_module("glow_domain.chat_tokens")
    return port, fixtures, adapter, tokens


def start_refusals(snapshot: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    """The two verifications the command runs before its first changing request (DM-16
    1.1): the chat configuration's differences from the proof's target, and Video and Feeds'
    differences from the lockdown target. Both must be empty."""
    from . import configuration, products

    chat = [p for p in configuration.verify(snapshot) if not p.startswith("video/feeds: ")]
    locked = products.verify(snapshot.get("products") or {})
    return chat, locked


@dataclass
class Row:
    """One conformance row: what the fixture (or the design) says, and what Stream gave."""

    row_id: str
    description: str
    expected: str
    observed: str
    verdict: str
    reason: str = ""
    detail: dict[str, Any] = field(default_factory=dict)


PASS = "PASS"
DIFFERENCE = "DIFFERENCE"
RECORDED = "RECORDED"
FAIL = "FAIL"
INCONCLUSIVE = "INCONCLUSIVE"
BLOCKING = "a code that differs from the fixture's; blocks B2's merge until dispositioned (5.2)"


class ConformanceRun(ProofRun):
    """A :class:`ProofRun` whose cases are the adapter's rows (design point g)."""

    def __init__(
        self,
        credentials: ServerCredentials,
        api: ServerApi,
        ledger: UsageLedger,
        redactor: Redactor,
        environ: Mapping[str, str],
        *,
        prefix: str,
        accept_dashboard_user: bool,
        modules: Modules | None = None,
    ) -> None:
        super().__init__(
            credentials,
            api,
            ledger,
            redactor,
            environ,
            prefix=prefix,
            accept_dashboard_user=accept_dashboard_user,
        )
        self.port, self.fixtures, self.adapter_module, self.tokens = (
            modules if modules is not None else load_api_modules()
        )
        # The adapter on the harness's own client: every request passes the guard (4.3).
        self.adapter = self.adapter_module.StreamChatProvider(api.sdk)
        self.fixture = self.fixtures.FixtureChatProvider("test")
        self.rows: list[Row] = []
        # Each Glow code the adapter gave, with the HTTP status and Stream code that decided
        # it (4.5), and the row that shows it.
        self.mappings: list[dict[str, Any]] = []
        self.ids: dict[str, str] = {}

    # -- identifiers and the ledger --------------------------------------------------------

    def _id(self, key: str) -> str:
        """A random identifier of the run's own: its prefix plus 32 hexadecimal characters."""
        if key not in self.ids:
            self.ids[key] = f"{self.prefix}{secrets.token_hex(16)}"
            self.ctx[key] = self.ids[key]
        return self.ids[key]

    def _new_user(self, key: str) -> str:
        user_id = self._id(key)
        if user_id not in self.users:
            self.ledger.reserve("users", 1)
            self.users.append(user_id)
        return user_id

    def _new_channel(self, key: str) -> str:
        channel_id = self._id(key)
        cid = f"{T}:{channel_id}"
        if cid not in self.channels:
            self.ledger.reserve("channels", 1)
            self.channels.append(cid)
        return channel_id

    def _message(self, key: str) -> str:
        message_id = self._id(key)
        self.messages.add(message_id)
        return message_id

    # -- rows ----------------------------------------------------------------------------

    def _outcome(self, call: Callable[[], Any]) -> tuple[str, dict[str, Any]]:
        """``ok``, ``already`` or the Glow code; a Stream error's status and number beside
        it (two numbers, never Stream's text). The harness's stop types and every other
        exception propagate (4.1)."""
        try:
            receipt = call()
        except self.port.ChatProviderError as error:
            detail = {"code": str(error.code)}
            if hasattr(error, "status"):
                detail["status"] = error.status
                detail["number"] = error.number
            return str(error.code), detail
        return ("already" if receipt.already else "ok"), {}

    def _row(
        self,
        row_id: str,
        description: str,
        expected: str,
        observed: str,
        *,
        reason: str = "",
        detail: dict[str, Any] | None = None,
        recorded: bool = False,
        blocking: bool = False,
    ) -> Row:
        if recorded:
            verdict = RECORDED
            reason = reason or (
                "as the fixture" if observed == expected else "differs from the fixture"
            )
        elif observed == expected:
            verdict = PASS
        else:
            verdict = DIFFERENCE
            reason = reason or (BLOCKING if blocking else "differs from the fixture: a finding")
        row = Row(row_id, description, expected, observed, verdict, reason, detail or {})
        self.rows.append(row)
        return row

    def _both(
        self,
        row_id: str,
        description: str,
        operation: str,
        *args: Any,
        recorded: bool = False,
        blocking: bool = False,
    ) -> Row:
        """One operation on both subjects, the fixture first; the fixture's outcome is the
        expectation unless the row is stated as recorded (4.7)."""
        fixture_outcome, _ = self._outcome(lambda: getattr(self.fixture, operation)(*args))
        live_outcome, detail = self._outcome(lambda: getattr(self.adapter, operation)(*args))
        if detail.get("code"):
            self.mappings.append(
                {
                    "row": row_id,
                    "operation": operation,
                    "code": detail["code"],
                    "status": detail.get("status"),
                    "number": detail.get("number"),
                    "decided_by": "Stream's HTTP status and numeric code"
                    if detail.get("status") is not None
                    else "the adapter's read: Stream does not hold the object",
                }
            )
        return self._row(
            row_id,
            description,
            fixture_outcome,
            live_outcome,
            detail={"operation": operation, **detail},
            recorded=recorded,
            blocking=blocking,
        )

    def _fact(
        self, row_id: str, description: str, ok: bool | None, evidence: dict[str, Any]
    ) -> Row:
        """A read-back or a token check: expected as designed, observed as Stream shows."""
        if ok is None:
            row = self._row(
                row_id, description, "as designed", "not shown", reason="", detail=evidence
            )
            row.verdict = INCONCLUSIVE
            row.reason = "Stream's answer was not recorded"
            return row
        row = self._row(
            row_id,
            description,
            "as designed",
            "as designed" if ok else "not as designed",
            detail=evidence,
        )
        if not ok:
            row.verdict = FAIL
            row.reason = "Stream shows otherwise"
        return row

    # -- reads of Stream's state, through the harness's client -----------------------------

    def _read_user(self, user_id: str) -> Mapping[str, Any] | None:
        result = self.api.get(
            "/api/v2/users",
            params={
                "payload": json.dumps(
                    {
                        "filter_conditions": {"id": {"$in": [user_id]}},
                        "include_deactivated_users": True,
                    }
                )
            },
        )
        users = result.body.get("users") if isinstance(result.body, Mapping) else None
        for user in users or []:
            if isinstance(user, Mapping) and user.get("id") == user_id:
                return dict(user)
        return None

    def _read_channel(self, channel_id: str) -> Mapping[str, Any] | None:
        result = self.api.raw(
            "POST",
            "/api/v2/chat/channels",
            body={"filter_conditions": {"cid": f"{T}:{channel_id}"}, "limit": 1},
        )
        channels = result.body.get("channels") if isinstance(result.body, Mapping) else None
        for entry in channels or []:
            channel = entry.get("channel") if isinstance(entry, Mapping) else None
            if isinstance(channel, Mapping) and channel.get("cid") == f"{T}:{channel_id}":
                return dict(entry)
        return None

    def _read_message(self, message_id: str) -> Mapping[str, Any] | None:
        result = self.api.get(f"/api/v2/chat/messages/{message_id}")
        message = result.body.get("message") if isinstance(result.body, Mapping) else None
        return dict(message) if isinstance(message, Mapping) and result.ok else None

    @staticmethod
    def _user_shape(user: Mapping[str, Any]) -> dict[str, Any]:
        custom = user.get("custom")
        return {
            "role": user.get("role"),
            "has_name": "name" in user,
            "has_image": "image" in user,
            "custom_keys": sorted(custom) if isinstance(custom, Mapping) else custom,
            "other_keys": sorted(set(user) - USER_STANDARD_KEYS),
            "deactivated": user.get("deactivated_at") is not None,
            "has_revocation_cutoff": user.get("revoke_tokens_issued_before") is not None,
        }

    @staticmethod
    def _channel_shape(entry: Mapping[str, Any]) -> dict[str, Any]:
        channel = entry.get("channel") or {}
        members = entry.get("members") or []
        custom = channel.get("custom")
        return {
            "member_user_ids": sorted(
                str(m.get("user_id")) for m in members if isinstance(m, Mapping)
            ),
            "has_name": "name" in channel,
            "has_image": "image" in channel,
            "custom_keys": sorted(custom) if isinstance(custom, Mapping) else custom,
            "other_keys": sorted(set(channel) - CHANNEL_STANDARD_KEYS),
        }

    def _plain_user(self, user: Mapping[str, Any] | None) -> bool | None:
        if user is None:
            return None
        shape = self._user_shape(user)
        return bool(
            shape["role"] == "user"
            and not shape["has_name"]
            and not shape["has_image"]
            and not shape["custom_keys"]
        )

    def _members_are(self, channel_id: str, members: list[str]) -> tuple[bool | None, Any]:
        entry = self._read_channel(channel_id)
        shape = self._channel_shape(entry) if entry else None
        if shape is None:
            return None, "not read"
        return shape["member_user_ids"] == sorted(members), shape

    # -- tokens ------------------------------------------------------------------------

    def _grant(self, user_id: str, issued_at: datetime) -> Any:
        """A grant from the domain rule, for a valid session of an active account, with the
        issue time given (the database's clock in the app; the host's here)."""
        tokens = self.tokens
        grant = tokens.grant_chat_token(
            account=tokens.TokenAccount("active", 1),
            session=tokens.TokenSession("valid", 1, issued_at + timedelta(hours=2)),
            user_ref=user_id,
            identity_active=True,
            now=issued_at,
        )
        if not isinstance(grant, tokens.TokenGrant):
            raise RuntimeError("the token rule refused a grant the run expected")
        return grant

    def _sign(self, user_id: str, issued_at: datetime) -> tuple[str, dict[str, Any]]:
        """The signer's token for a grant issued at ``issued_at``, and its claims relative
        to the grant (never the token itself)."""
        grant = self._grant(user_id, issued_at)
        token = self.adapter_module.sign_chat_token(grant, self.api.sdk)
        described = describe_token(token)
        claims = described.get("claims")
        claims = claims if isinstance(claims, dict) else {}
        iat, exp = claims.get("iat"), claims.get("exp")
        issue = int(issued_at.replace(microsecond=0).timestamp())
        expiry = int(grant.expires_at.replace(microsecond=0).timestamp())
        return token, {
            "alg": described.get("alg"),
            "claim_names": sorted(claims),
            "iat_minus_truncated_issue": iat - issue if isinstance(iat, int) else None,
            "exp_minus_truncated_expiry": exp - expiry if isinstance(exp, int) else None,
            "exp_minus_iat": exp - iat if isinstance(iat, int) and isinstance(exp, int) else None,
            "user_id_is_the_grants": claims.get("user_id") == user_id,
        }

    def _token_check(
        self, label: str, user_id: str, token: str, channel_id: str | None
    ) -> dict[str, Any]:
        """A new client session with ``token``: connect, then read ``channel_id`` when
        connected; closed afterwards. Stream's answers, by outcome, status and code."""
        out: dict[str, Any] = {}
        session = None
        try:
            session = self._session(label, token, max_api_calls=10)
            connected = pr._ws_answer(
                self._send(session, "connect", max_calls=3, user={"id": user_id})
            )
            out["connect"] = pr._observed(connected)
            out["connect_outcome"] = connected.outcome
            if connected.note:
                out["connect_note"] = self._text(RuntimeError(connected.note))
            if connected.outcome == "success" and channel_id is not None:
                read = pr._http_answer(
                    self._send(
                        session,
                        "call",
                        max_calls=2,
                        target="channel",
                        method="query",
                        args=[matrix.READ_OPTIONS],
                        type=T,
                        id=channel_id,
                    )
                )
                out["read"] = pr._observed(read)
                out["read_outcome"] = read.outcome
                if read.note:
                    out["read_note"] = self._text(RuntimeError(read.note))
        except ClientSessionEnded as exc:
            out["error"] = self._text(exc)
        finally:
            if session is not None:
                self.sessions.pop(label, None)
                session.close()
        return out

    @staticmethod
    def _accepted(check: Mapping[str, Any], *, with_read: bool) -> bool | None:
        """Whether the token was accepted: the connect succeeded and, when asked, the read.
        ``None`` when Stream's answer was not recorded."""
        connect = check.get("connect_outcome")
        if connect is None or connect == "no-response":
            return None
        if connect != "success":
            return False
        if not with_read:
            return True
        read = check.get("read_outcome")
        if read is None or read == "no-response":
            return None
        return bool(read == "success")

    @staticmethod
    def _refused(check: Mapping[str, Any], *, at_read: bool) -> bool | None:
        """Whether Stream refused: at the connect, or (``at_read``) at the channel read after
        a connect that succeeded. ``None`` when no answer was recorded."""
        connect = check.get("connect_outcome")
        if connect is None or connect == "no-response":
            return None
        if connect != "success":
            return True
        if not at_read:
            return False
        read = check.get("read_outcome")
        if read is None or read == "no-response":
            return None
        return bool(read != "success")

    # -- the rows ------------------------------------------------------------------------

    def rows_provisioning(self) -> None:
        u1 = self._new_user("U1")
        self._both("P1", "provisioning creates the user with its ID only", "provision_user", u1)
        user = self._read_user(u1)
        self._fact(
            "P2",
            "read back: role user, no name, image or custom field",
            self._plain_user(user),
            {"shape": self._user_shape(user) if user else "not read"},
        )
        self._both("P3", "provisioning repeated returns already", "provision_user", u1)
        u2 = self._new_user("U2")
        self._both("P4", "the second member is provisioned", "provision_user", u2)

    def rows_channel(self) -> None:
        u1, u2 = self.ids["U1"], self.ids["U2"]
        c1 = self._new_channel("C1")
        self._both(
            "C1",
            "channel creation in glow-match with the two members",
            "create_channel",
            c1,
            (u1, u2),
        )
        same, shape = self._members_are(c1, [u1, u2])
        plain = (
            None
            if not isinstance(shape, dict)
            else not shape["has_name"] and not shape["has_image"] and not shape["custom_keys"]
        )
        self._fact(
            "C2",
            "read back: exactly the two members, no name, image or custom data",
            None if same is None or plain is None else same and plain,
            {"shape": shape},
        )
        self._both(
            "C3", "channel creation repeated returns already", "create_channel", c1, (u1, u2)
        )
        self._both(
            "C4",
            "channel creation naming a user Stream does not have",
            "create_channel",
            self._id("C2"),
            (u1, self._id("U9")),
            blocking=True,
        )

    def rows_send(self) -> None:
        u1, c1 = self.ids["U1"], self.ids["C1"]
        m1 = self._message("M1")
        self._both(
            "M1", "a message with its committed ID and text", "send_message", c1, u1, m1, TEXT
        )
        message = self._read_message(m1)
        self._fact(
            "M2",
            "read back: the committed ID, the text and the sender",
            None
            if message is None
            else message.get("id") == m1
            and message.get("text") == TEXT
            and (message.get("user") or {}).get("id") == u1,
            {
                "id_matches": message.get("id") == m1 if message else None,
                "cid_matches": message.get("cid") == f"{T}:{c1}" if message else None,
            },
        )
        self._both("M3", "the send repeated returns already", "send_message", c1, u1, m1, TEXT)
        self._both(
            "M4",
            "a send to a channel Stream does not have",
            "send_message",
            self._id("CX"),
            u1,
            self._message("M3"),
            "nowhere",
        )
        self._both(
            "M5",
            "a send by a user Stream does not have",
            "send_message",
            c1,
            self._id("U9"),
            self._message("M4"),
            "nobody",
        )

    def rows_signer(self) -> None:
        u1, c1 = self.ids["U1"], self.ids["C1"]
        token, relative = self._sign(u1, datetime.now(UTC))
        backdate = int(self.adapter_module.IAT_BACKDATE_SECONDS)
        self._fact(
            "T1",
            "the token's iat and exp are the grant's, truncated to the second",
            relative["alg"] == "HS256"
            and relative["claim_names"] == ["exp", "iat", "user_id"]
            and relative["iat_minus_truncated_issue"] == -backdate
            and relative["exp_minus_truncated_expiry"] == 0
            and relative["user_id_is_the_grants"],
            {**relative, "backdate_seconds": backdate},
        )
        check = self._token_check("T2", u1, token, c1)
        self._fact(
            "T2",
            "a token from the signer is accepted: connect and read the channel",
            self._accepted(check, with_read=True),
            check,
        )

    def rows_removal(self) -> None:
        u1, u2, c1 = self.ids["U1"], self.ids["U2"], self.ids["C1"]
        self._both("R1", "removal of both members", "remove_members", c1, (u1, u2))
        empty, shape = self._members_are(c1, [])
        self._fact("R2", "read back: no member remains", empty, {"shape": shape})
        token, _ = self._sign(u1, datetime.now(UTC))
        check = self._token_check("R3", u1, token, c1)
        self._fact(
            "R3",
            "the removed member's own client can no longer read the channel",
            self._refused(check, at_read=True),
            check,
        )
        self._both("R4", "removal repeated returns already", "remove_members", c1, (u1, u2))
        self._both(
            "R5", "channel creation repeated after the removal", "create_channel", c1, (u1, u2)
        )
        empty, shape = self._members_are(c1, [])
        self._fact("R6", "read back: the members were not re-added (4.4)", empty, {"shape": shape})
        self._both(
            "R7",
            "a send by a removed member, after the removal (4.7)",
            "send_message",
            c1,
            u1,
            self._message("M2"),
            "after the removal",
            recorded=True,
        )
        self._both(
            "R8",
            "removal from a channel Stream does not have",
            "remove_members",
            self._id("CX"),
            (u1, u2),
            blocking=True,
        )

    def rows_deactivation(self) -> None:
        u3, u2, c1 = self._new_user("U3"), self.ids["U2"], self.ids["C1"]
        self._both("D1", "a third user is provisioned", "provision_user", u3)
        self._both("D2", "deactivation", "deactivate_user", u3)
        self.deactivated_users.add(u3)
        token, _ = self._sign(u3, datetime.now(UTC))
        check = self._token_check("D3", u3, token, None)
        self._fact(
            "D3",
            "the deactivated user's signed token is refused",
            self._refused(check, at_read=False),
            check,
        )
        self._both("D4", "deactivation repeated returns already", "deactivate_user", u3)
        self._both("D5", "re-provisioning a deactivated user returns already", "provision_user", u3)
        user = self._read_user(u3)
        shape = self._user_shape(user) if user else None
        self._fact(
            "D6",
            "read back: still deactivated after the re-provisioning (4.4)",
            None if shape is None else bool(shape["deactivated"]),
            {"shape": shape or "not read"},
        )
        check = self._token_check("D7", u3, token, None)
        self._fact(
            "D7",
            "the deactivated user's token is still refused after the re-provisioning (4.4)",
            self._refused(check, at_read=False),
            check,
        )
        self._both(
            "D8",
            "channel creation naming a deactivated member",
            "create_channel",
            self._id("C4"),
            (u3, u2),
        )
        self._both(
            "D9",
            "a send by a deactivated user",
            "send_message",
            c1,
            u3,
            self._message("M5"),
            "gone",
        )
        self._both(
            "D10",
            "deactivation of a user Stream does not have",
            "deactivate_user",
            self._id("U9"),
            blocking=True,
        )

    def rows_revocation(self) -> None:
        u4, u2 = self._new_user("U4"), self.ids["U2"]
        self._both("V1", "a fourth user is provisioned", "provision_user", u4)
        c3 = self._new_channel("C3")
        self._both("V2", "its channel is created", "create_channel", c3, (u4, u2))
        # The cut-off is an exact second; revocation_cutoff_sent sends it one second later.
        exact = datetime.now(UTC).replace(microsecond=0)
        sent = self.tokens.revocation_cutoff_sent(exact)
        before, before_claims = self._sign(u4, exact - timedelta(microseconds=500_000))
        at, at_claims = self._sign(u4, exact + timedelta(microseconds=400_000))
        self._both(
            "V3",
            "a per-user revocation with the cut-off from revocation_cutoff_sent",
            "revoke_user_tokens",
            u4,
            sent,
        )
        user = self._read_user(u4)
        held = user.get("revoke_tokens_issued_before") if user else None
        held_seconds = int(held / 1e9) if isinstance(held, int | float) else None
        self._fact(
            "V4",
            "read back: the cut-off Stream holds is the exact second plus one",
            None if held_seconds is None else held_seconds == int(sent.timestamp()),
            {
                "held_minus_exact_seconds": held_seconds - int(exact.timestamp())
                if held_seconds is not None
                else None,
                "sent_minus_exact_seconds": int((sent - exact).total_seconds()),
            },
        )
        check = self._token_check("V5", u4, before, c3)
        self._fact(
            "V5",
            "a token whose iat is before the cut-off is refused",
            self._refused(check, at_read=True),
            {**check, **before_claims},
        )
        check = self._token_check("V6", u4, at, c3)
        self._fact(
            "V6",
            "a token issued in the cut-off's second (iat equal to the exact second) is refused",
            self._refused(check, at_read=True),
            {**check, **at_claims},
        )
        ready = sent + timedelta(seconds=1 + AFTER_REVOCATION_MARGIN_SECONDS)
        wait = (ready - datetime.now(UTC)).total_seconds()
        if wait > 0:
            time.sleep(wait)
        at_sent, at_sent_claims = self._sign(u4, sent)
        check = self._token_check("V7", u4, at_sent, c3)
        accepted = self._accepted(check, with_read=True)
        self._row(
            "V7",
            "a token whose iat equals the sent cut-off: Stream's comparison at the boundary",
            "recorded",
            "accepted" if accepted else ("refused" if accepted is False else "not shown"),
            reason="shows whether Stream revokes iat < cut-off (strict) or iat <= cut-off",
            detail={**check, **at_sent_claims},
            recorded=True,
        )
        after, after_claims = self._sign(u4, sent + timedelta(seconds=1))
        check = self._token_check("V8", u4, after, c3)
        self._fact(
            "V8",
            "a token signed after the cut-off is accepted",
            self._accepted(check, with_read=True),
            {**check, **after_claims},
        )
        self._both("V9", "the revocation repeated returns already", "revoke_user_tokens", u4, sent)
        earlier, _ = self._outcome(
            lambda: self.adapter.revoke_user_tokens(u4, sent - timedelta(seconds=10))
        )
        user = self._read_user(u4)
        held_after = user.get("revoke_tokens_issued_before") if user else None
        self._fact(
            "V10",
            "a revocation with an earlier cut-off sends nothing and lowers nothing (4.4)",
            earlier == "already" and held_after == held,
            {"outcome": earlier, "cut_off_unchanged": held_after == held},
        )
        self._both(
            "V11", "re-provisioning after the revocation returns already", "provision_user", u4
        )
        check = self._token_check("V12", u4, before, c3)
        self._fact(
            "V12",
            "the revoked token is still refused after the re-provisioning (4.4)",
            self._refused(check, at_read=True),
            check,
        )
        self._both(
            "V13",
            "revocation of a user Stream does not have",
            "revoke_user_tokens",
            self._id("U9"),
            sent,
            blocking=True,
        )

    def run_rows(self, progress: Callable[[], None] | None = None) -> None:
        for step in (
            self.rows_provisioning,
            self.rows_channel,
            self.rows_send,
            self.rows_signer,
            self.rows_removal,
            self.rows_deactivation,
            self.rows_revocation,
        ):
            step()
            if progress is not None:
                progress()

    # -- results -------------------------------------------------------------------------

    def verdict_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self.rows:
            counts[row.verdict] = counts.get(row.verdict, 0) + 1
        return dict(sorted(counts.items()))

    def results(self) -> dict[str, Any]:
        base = super().results()
        rows = []
        for row in self.rows:
            entry = asdict(row)
            # Identifiers generalized, the text redacted, as every record of this harness.
            entry["detail"] = json.loads(
                self.redactor.text(pr._generic(json.dumps(row.detail, default=str), self.ctx))
            )
            rows.append(entry)
        base.update(
            {
                "rows": rows,
                "verdicts": self.verdict_counts(),
                "mappings": self.mappings,
                "api_calls_used": self.ledger.summary()["run"]["api_calls"],
            }
        )
        return base


def render(results: Mapping[str, Any]) -> str:
    """The rows and the mappings as Markdown (redacted, identifiers generalized)."""
    lines = [
        f"Conformance run `{results['prefix']}`",
        "",
        "| Row | Description | Expected | Observed | Verdict |",
        "|---|---|---|---|---|",
    ]
    for row in results["rows"]:
        verdict = row["verdict"] + (f": {row['reason']}" if row.get("reason") else "")
        lines.append(
            f"| {row['row_id']} | {row['description']} | {row['expected']} | "
            f"{row['observed']} | {verdict} |"
        )
    lines += [
        "",
        f"Verdicts: {results['verdicts']}",
        "",
        "| Row | Operation | Glow code | HTTP status | Stream code | Decided by |",
        "|---|---|---|---|---|---|",
    ]
    for m in results["mappings"]:
        lines.append(
            f"| {m['row']} | {m['operation']} | {m['code']} | {m['status']} | {m['number']} | "
            f"{m['decided_by']} |"
        )
    lines += ["", f"API calls used by the run: {results['api_calls_used']}"]
    for key, title in (
        ("notes", "Notes:"),
        ("stops", "Stops recorded:"),
        ("stop_signals", "Charge or limit signals:"),
        ("post_run_problems", "After the run:"),
    ):
        if results.get(key):
            lines += ["", title] + [f"- {n}" for n in results[key]]
    return "\n".join(lines) + "\n"


__all__ = [
    "API_ROOT",
    "ConformanceRun",
    "PREFIX_ROOT",
    "Row",
    "RunStopped",
    "load_api_modules",
    "render",
    "start_refusals",
]
