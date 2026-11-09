"""Privacy-safe notifications at fixture scope (P06.3; F12; the brief's Outcome items 1 and 2,
D1 to D4). Pure domain logic, independent of Django and of every provider.

**The composer** (Outcome 1, D2, D4). ``NotificationService.deliver`` takes a typed trigger, a
``MatchActivated`` or a ``MessageAccepted``, that names its recipient, and composes at most one
push per active device of that recipient. A message notifies the other member of the match,
never its sender; a match notifies the member whose earlier like the reciprocal like matched,
never the member whose like completed it. The push carries only the kind, Glow's fixed wording
(the title ``Glow`` and one sentence per kind) and a fixed route, with no identifier, name, text,
count, birth data, compatibility data or provider detail. A trigger type has no field for any of
those, and the composer refuses a trigger with any field beyond its own.

**Whatever refuses a send refuses a notification.** The composer makes the send's checks, the
read rule of ``glow_domain/chat_reads.py`` ("Whatever refuses a send refuses a read"), on facts it
reads through the ``DeliveryFacts`` port on each delivery, never from the trigger: the match
active with no block either way; both accounts ``active``; both profiles ``visible`` (so neither
paused nor restricted); both latest onboarding consents ``accepted``. It also composes nothing
when the recipient's setting for the kind is off or the recipient has no active device. Each
refusal is a reason code that carries no personal data.

**No duplicate push.** The first delivery of a trigger that passes those checks fixes its
devices: the recipient's active devices then. A later delivery of the same trigger sends only to
a device of that set whose send the transport has not accepted and that is still active. The
ledger's key is the trigger's event ID with the installation's ``device_id``; it records a send
only when the transport accepts it, and the transport's idempotency key is the ledger's key, so a
send the transport accepted but the ledger did not record is refused as a repeat on the next
delivery, and the ledger then records it. Exactly-once delivery by a real provider is P11B's
(PV05).

**Devices and settings** (Outcome 2, D3; F12 per installation). Each installation's registration
for an account is ``none``, ``active`` or ``revoked``; the settings are the account's, both off
until changed. A ``register`` intent for an installation in ``none`` or ``revoked`` is F12's
``register``; for one already ``active`` for the same account it is F12's ``rotate`` (the
contract's ``DeviceIntent`` has no ``rotate`` action). ``revoke`` (the owner) and ``logout`` (the
system) move ``active`` to ``revoked``. A ``settings`` intent needs the requesting installation's
registration to be ``active``. Registering an installation active for another account first
revokes that account's registration, in the same unit of work. A command carries the actor's
account, its current session and its installation (``Caller``), never as intent fields, and a
session that is no longer current is refused. Each registration records the session that last
registered or rotated it; a registration whose session is no longer current is not active for
the composer. ``logout`` revokes the registrations the ending session made, and no other; it is
the system's F12 logout for any session that ends, which SV4 wires to ``session_revoked`` and
``session_expired`` (the brief, D9).

**Versions, at fixture scope.** The contract's ``NotificationSettings`` has one ``version`` and
one ``device_state``, so one number must let the app address both the installation's
registration and the account's settings. Here it is the installation's view revision: it starts
at 1 when the account first registers the installation, and advances with every change to that
registration and with every change to the account's settings (a settings change advances every
registration of the account in the same unit of work). A ``DeviceIntent``'s ``expected_version``
is 0 for an installation with no registration for the account, else that revision; a
``NotificationIntent``'s is the requesting installation's revision. A stale value is refused, the
same idempotency key with other content is a conflict, and a replay changes nothing (the data
model's rule). How the serving slice versions F12 is SV4's to decide (the brief, D9).

**Token custody.** The token goes to the ``TokenStore`` port before its opaque reference is
saved, and only the reference is kept; if the store refuses, nothing is saved. When a
registration ends (revoke, logout, transfer) or its token is replaced (rotate), the old token is
discarded through the port after the change; a failed discard is kept for retry, and the revoked
registration no longer holds its reference, so nothing here resolves it. The push request names
the device by its reference, never its token; only a transport adapter resolves it (P11B).
``ProviderToken`` and ``TokenReference`` print as withheld, and no read, log line, refusal,
exception message, receipt or composer output carries the token, nor any read, log line or
refusal the reference. There is no staff projection.

**Fixture scope** (D1, D3). State is in memory, guarded to development and test. The ports'
only implementations are the fixtures in ``notification_fixtures.py``. No HTTP route, ORM
adapter, outbox consumer, provider, network client or credential is attached: SV4 serves F12 and
wires the triggers, P09.2 brings the native module and P11B the transport (D9). The served
runtime imports none of this module (``tests/test_notifications.py``).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import re
import secrets
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, fields, replace
from datetime import datetime
from typing import Literal, NoReturn, Protocol
from uuid import UUID

from . import chat
from .provider_fixtures import require_fixture_environment

logger = logging.getLogger(__name__)

NotificationKind = Literal["match", "message"]
KINDS: tuple[NotificationKind, ...] = ("match", "message")

# D4: Glow's fixed wording, one sentence per kind under the title "Glow", and the fixed route
# each push opens behind the app's own session check. Nathan may change the wording; a change is
# an edit here and its test.
TITLE = "Glow"
WORDING: Mapping[NotificationKind, str] = {
    "match": "You have a new match.",
    "message": "You have a new message.",
}
ROUTES: Mapping[NotificationKind, str] = {"match": "/matches", "message": "/conversations"}

# The contract's names (D3).
SETTING_FIELDS: Mapping[NotificationKind, str] = {
    "match": "match_notifications",
    "message": "message_notifications",
}

# Refusal reasons: Glow's own codes, with no personal data. The send's codes are reused where the
# check is the send's.
TRIGGER_INVALID = "trigger_invalid"
TRIGGER_CONFLICT = "trigger_conflict"
MESSAGE_MISSING = "message_missing"
MESSAGE_NOT_ACCEPTED = "message_not_accepted"
MESSAGE_MATCH_MISMATCH = "message_match_mismatch"
RECIPIENT_IS_SENDER = "recipient_is_sender"
RECIPIENT_COMPLETED_MATCH = "recipient_completed_match"
SETTING_OFF = "setting_off"
NO_ACTIVE_DEVICE = "no_active_device"
ALREADY_DELIVERED = "already_delivered"
TRANSPORT_UNAVAILABLE = "transport_unavailable"
INTENT_INVALID = "intent_invalid"
WRONG_INSTALLATION = "wrong_installation"
SESSION_NOT_OWNER = "session_not_owner"
STALE_VERSION = "stale_version"
TRANSITION_FORBIDDEN = "transition_forbidden"
REGISTRATION_NOT_ACTIVE = "registration_not_active"
TOKEN_STORE_REFUSED = "token_store_refused"
FIXTURE_CAPACITY = "fixture_capacity"

# Bounds for one in-memory fixture service; not product limits.
MAX_RECEIPTS = 500
MAX_VERSION = 9_007_199_254_740_991

_UUID_FORM = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_KEY_FORM = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}")
# The contract's provider_token needs one character outside this whitespace class.
_NOT_WHITESPACE = re.compile(
    r"[^\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]"
)
_SURROGATE = re.compile(r"[\ud800-\udfff]")
_TOKEN_LIMIT = 4096


class IntentError(ValueError):
    """An intent that does not follow its contract. The message never echoes a value."""

    def __init__(self) -> None:
        super().__init__(INTENT_INVALID)


class TokenStoreError(Exception):
    """The token store refused or failed. The message is a fixed code, never a value."""

    def __init__(self) -> None:
        super().__init__(TOKEN_STORE_REFUSED)


class PushTransportError(Exception):
    """The push transport failed. The message is a fixed code, never a value."""

    def __init__(self) -> None:
        super().__init__(TRANSPORT_UNAVAILABLE)


# -- custody types -----------------------------------------------------------------------------


class ProviderToken:
    """A device's push token (F12's ``DeviceIntent.provider_token``). It is held only until the
    token store takes it; it prints as withheld and cannot be pickled or compared by value."""

    __slots__ = ("_value",)

    def __init__(self, value: object) -> None:
        if (
            not isinstance(value, str)
            or not 1 <= len(value) <= _TOKEN_LIMIT
            or _NOT_WHITESPACE.search(value) is None
            or _SURROGATE.search(value) is not None
        ):
            raise IntentError()
        self._value = value

    def reveal(self) -> str:
        """The value, for the token store's adapter only."""
        return self._value

    def __repr__(self) -> str:
        return "ProviderToken(<withheld>)"

    __str__ = __repr__

    def __reduce__(self) -> NoReturn:
        raise TypeError("a provider token is not serialized")


class TokenReference:
    """The token store's opaque reference for one stored token. It prints as withheld; only a
    transport adapter resolves it (P11B)."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not isinstance(value, str) or not value:
            raise ValueError("a token reference is a non-empty string")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TokenReference) and hmac.compare_digest(self._value, other._value)

    def __hash__(self) -> int:
        return hash(("TokenReference", self._value))

    def __repr__(self) -> str:
        return "TokenReference(<withheld>)"

    __str__ = __repr__


# -- the ports ---------------------------------------------------------------------------------


class TokenStore(Protocol):
    """Where a push token is kept. ``put`` returns the reference or raises ``TokenStoreError``;
    ``discard`` removes a stored token or raises ``TokenStoreError``. The domain never resolves a
    reference."""

    def put(self, token: ProviderToken) -> TokenReference: ...

    def discard(self, reference: TokenReference) -> None: ...


@dataclass(frozen=True)
class PushContent:
    """What a push shows and opens (D4): Glow's title and sentence, the kind and a fixed route."""

    title: str
    body: str
    kind: NotificationKind
    route: str

    def as_payload(self) -> dict[str, object]:
        return {
            "title": self.title,
            "body": self.body,
            "data": {"kind": self.kind, "route": self.route},
        }


@dataclass(frozen=True)
class PushRequest:
    """What the composer hands the transport: the device by its reference, the ledger's key as the
    idempotency key, and the content. The key is transport metadata, never shown on a device."""

    device: TokenReference
    idempotency_key: str
    content: PushContent


TransportOutcome = Literal["accepted", "repeat"]


class PushTransport(Protocol):
    """Sends one push. ``accepted``: taken now. ``repeat``: refused because the idempotency key was
    accepted before. A failure raises; whatever it raises counts as ``transport_unavailable``."""

    def send(self, request: PushRequest) -> TransportOutcome: ...


@dataclass(frozen=True)
class MatchFacts:
    state: str
    participants: tuple[UUID, UUID]
    # The member whose like completed the match (the reciprocal like).
    completed_by: UUID
    # An active block either way between the participants.
    blocked: bool


@dataclass(frozen=True)
class MessageFacts:
    match_id: UUID
    sender: UUID
    state: str


@dataclass(frozen=True)
class MemberFacts:
    account_state: str
    profile_state: str | None
    # The latest onboarding consent decision (``chat.ONBOARDING_CONSENT_PURPOSE``).
    consent_state: str | None


class DeliveryFacts(Protocol):
    """The facts the send's checks use, read on each delivery (never carried by a trigger)."""

    def match(self, match_id: UUID) -> MatchFacts | None: ...

    def message(self, submission_id: UUID) -> MessageFacts | None: ...

    def member(self, account_id: UUID) -> MemberFacts | None: ...


@dataclass(frozen=True)
class SessionFacts:
    account_id: UUID
    state: str
    epoch: int
    expires_at: datetime


@dataclass(frozen=True)
class AccountFacts:
    state: str
    session_epoch: int


class SessionAuthority(Protocol):
    """The maintained authentication's sessions, as Glow's rows hold them."""

    def session(self, session_id: UUID) -> SessionFacts | None: ...

    def account(self, account_id: UUID) -> AccountFacts | None: ...


# -- triggers ----------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MatchActivated:
    """A match activation, for the member whose earlier like the reciprocal like matched."""

    event_id: UUID
    match_id: UUID
    recipient: UUID


@dataclass(frozen=True, slots=True)
class MessageAccepted:
    """A message's acceptance (the delivery receipt that marks it ``accepted``), never its
    submission, for the other member of the match."""

    event_id: UUID
    match_id: UUID
    submission_id: UUID
    recipient: UUID


Trigger = MatchActivated | MessageAccepted
TRIGGER_KINDS: Mapping[type, NotificationKind] = {
    MatchActivated: "match",
    MessageAccepted: "message",
}


def trigger_fields(trigger_type: type) -> frozenset[str]:
    return frozenset(item.name for item in fields(trigger_type))


def parse_trigger(kind: object, data: object) -> Trigger:
    """A trigger from an event's reference payload (for SV4's wiring): exactly the kind's fields,
    each a canonical UUID string. Anything else raises ``IntentError``."""
    if kind not in ("match", "message") or not isinstance(data, Mapping):
        raise IntentError()
    if kind == "match":
        if set(data) != trigger_fields(MatchActivated):
            raise IntentError()
        return MatchActivated(
            _uuid(data["event_id"]), _uuid(data["match_id"]), _uuid(data["recipient"])
        )
    if set(data) != trigger_fields(MessageAccepted):
        raise IntentError()
    return MessageAccepted(
        _uuid(data["event_id"]),
        _uuid(data["match_id"]),
        _uuid(data["submission_id"]),
        _uuid(data["recipient"]),
    )


def _uuid(value: object) -> UUID:
    if not isinstance(value, str) or _UUID_FORM.fullmatch(value) is None:
        raise IntentError()
    return UUID(value)


def _trigger_kind(trigger: object) -> NotificationKind | None:
    """The kind of an exact trigger type whose every field is a UUID; ``None`` for anything else,
    including a subclass or any object carrying a field beyond the type's own."""
    kind = TRIGGER_KINDS.get(type(trigger))
    if kind is None or hasattr(trigger, "__dict__"):
        return None
    for item in fields(MatchActivated if kind == "match" else MessageAccepted):
        if type(getattr(trigger, item.name, None)) is not UUID:
            return None
    return kind


# -- intents, callers and results --------------------------------------------------------------


@dataclass(frozen=True)
class Caller:
    """The trusted request context: the session's account, the session and the requesting
    installation. It never comes from an intent's fields."""

    account_id: UUID
    session_id: UUID
    device_id: UUID


@dataclass(frozen=True)
class CommandMeta:
    idempotency_key: str
    expected_version: int


@dataclass(frozen=True)
class DeviceCommand:
    meta: CommandMeta
    device_id: UUID
    action: Literal["register", "revoke"]
    token: ProviderToken | None = field(repr=False, compare=False)


@dataclass(frozen=True)
class SettingsCommand:
    meta: CommandMeta
    match_notifications: bool
    message_notifications: bool


def _meta(value: object) -> CommandMeta:
    if not isinstance(value, Mapping) or set(value) != {"idempotency_key", "expected_version"}:
        raise IntentError()
    key, version = value["idempotency_key"], value["expected_version"]
    if not isinstance(key, str) or _KEY_FORM.fullmatch(key) is None:
        raise IntentError()
    if type(version) is not int or not 0 <= version <= MAX_VERSION:
        raise IntentError()
    return CommandMeta(key, version)


def parse_device_intent(intent: object) -> DeviceCommand:
    """F12's ``DeviceIntent``, exactly as the contract has it. The token becomes a
    ``ProviderToken`` at once. An invalid intent raises ``IntentError`` with no value in it."""
    keys = {"operation", "meta", "device_id", "action", "provider_token"}
    if not isinstance(intent, Mapping) or set(intent) != keys or intent["operation"] != "device":
        raise IntentError()
    meta = _meta(intent["meta"])
    device_id = _uuid(intent["device_id"])
    action = intent["action"]
    raw = intent["provider_token"]
    if action == "register":
        return DeviceCommand(meta, device_id, "register", ProviderToken(raw))
    if action == "revoke" and raw is None:
        return DeviceCommand(meta, device_id, "revoke", None)
    raise IntentError()


def parse_settings_intent(intent: object) -> SettingsCommand:
    """F12's ``NotificationIntent``, exactly as the contract has it."""
    keys = {"operation", "meta", "match_notifications", "message_notifications"}
    if not isinstance(intent, Mapping) or set(intent) != keys:
        raise IntentError()
    if intent["operation"] != "notifications":
        raise IntentError()
    match, message = intent["match_notifications"], intent["message_notifications"]
    if type(match) is not bool or type(message) is not bool:
        raise IntentError()
    return SettingsCommand(_meta(intent["meta"]), match, message)


RegistrationState = Literal["active", "revoked"]
EndedBy = Literal["revoke", "logout", "transfer"]


@dataclass(frozen=True)
class Registration:
    """One installation's registration for one account. ``version`` is the installation's view
    revision. ``reference`` is held only while active; ``ended_by`` names the last transition that
    ended it. ``session_id`` is the session that last registered or rotated it."""

    account_id: UUID
    device_id: UUID
    state: RegistrationState
    version: int
    session_id: UUID
    reference: TokenReference | None = field(repr=False)
    ended_by: EndedBy | None = None


@dataclass(frozen=True)
class Settings:
    match_notifications: bool = False
    message_notifications: bool = False
    version: int = 0


@dataclass(frozen=True)
class NotificationSettingsView:
    """F12's private projection for one installation of the owner: the contract's
    ``NotificationSettings``. It carries no token and no reference."""

    version: int
    match_notifications: bool
    message_notifications: bool
    device_state: RegistrationState

    def as_contract(self) -> dict[str, object]:
        return {
            "kind": "notifications",
            "version": self.version,
            "match_notifications": self.match_notifications,
            "message_notifications": self.message_notifications,
            "device_state": self.device_state,
        }


@dataclass(frozen=True)
class Receipt:
    """A committed command's immutable receipt: its digest (a keyed hash of the canonical intent,
    never the token), outcome code, object and committed version."""

    digest: str = field(repr=False)
    outcome_code: str
    device_id: UUID | None
    committed_version: int


CommandOutcome = Literal["applied", "replayed", "refused"]


@dataclass(frozen=True)
class CommandResult:
    outcome: CommandOutcome
    reason: str = ""
    receipt: Receipt | None = None
    settings: NotificationSettingsView | None = None
    # The F12 transition a device command made: register, rotate or revoke.
    transition: str = ""


@dataclass(frozen=True)
class ReadResult:
    """A settings read: ``read`` with the projection; ``absent`` (explicit) for an installation
    with no registration for the account, since the contract's ``device_state`` has no ``none``;
    or ``refused`` with a code."""

    outcome: Literal["read", "absent", "refused"]
    reason: str = ""
    settings: NotificationSettingsView | None = None


DeliveryOutcome = Literal["sent", "nothing", "refused"]


@dataclass(frozen=True)
class DeliveryResult:
    """``sent``: the transport accepted this many devices now (``sent``), with ``pending`` of the
    fixed devices left for a redelivery. ``nothing`` or ``refused``: no push, with a code."""

    outcome: DeliveryOutcome
    reason: str = ""
    sent: int = 0
    pending: int = 0


@dataclass(frozen=True)
class _Fixed:
    trigger: Trigger
    devices: frozenset[UUID]


# -- the service -------------------------------------------------------------------------------


class NotificationService:
    """F12's devices and settings and the notification composer, in memory (D3). Every command
    and delivery runs under one lock; a command's state is replaced only after all its checks."""

    def __init__(
        self,
        *,
        environment: str,
        sessions: SessionAuthority,
        facts: DeliveryFacts,
        tokens: TokenStore,
        transport: PushTransport,
        clock: Callable[[], datetime],
    ) -> None:
        require_fixture_environment(environment)
        self._sessions = sessions
        self._facts = facts
        self._tokens = tokens
        self._transport = transport
        self._clock = clock
        self._lock = threading.RLock()
        # A per-service key: a receipt's digest identifies its intent without exposing a token.
        self._digest_key = secrets.token_bytes(32)
        self._registrations: dict[tuple[UUID, UUID], Registration] = {}
        self._settings: dict[UUID, Settings] = {}
        self._receipts: dict[tuple[UUID, str, str], Receipt] = {}
        self._pending_discards: list[TokenReference] = []
        self._fixed: dict[UUID, _Fixed] = {}
        self._ledger: set[str] = set()

    def __repr__(self) -> str:
        return "NotificationService(<fixture>)"

    # -- reads for tests and the composer ----------------------------------------------------

    def registration(self, account_id: UUID, device_id: UUID) -> Registration | None:
        return self._registrations.get((account_id, device_id))

    def settings_of(self, account_id: UUID) -> Settings:
        return self._settings.get(account_id, Settings())

    @property
    def pending_discards(self) -> int:
        return len(self._pending_discards)

    def ledger_keys(self) -> frozenset[str]:
        return frozenset(self._ledger)

    # -- sessions ----------------------------------------------------------------------------

    def _session_refusal(self, account_id: UUID, session_id: UUID) -> str:
        """Empty when the session is the account's current one: valid, unexpired, at the account's
        epoch, of an ``active`` account. Otherwise the send's code for why not."""
        session = self._sessions.session(session_id)
        if session is None:
            return chat.SESSION_MISSING
        if session.account_id != account_id:
            return SESSION_NOT_OWNER
        account = self._sessions.account(account_id)
        if account is None:
            return chat.ACCOUNT_MISSING
        if account.state != "active":
            return chat.ACCOUNT_NOT_ACTIVE
        if session.state != "valid":
            return chat.SESSION_NOT_VALID
        if session.expires_at <= self._clock():
            return chat.SESSION_EXPIRED
        if session.epoch != account.session_epoch:
            return chat.SESSION_EPOCH_STALE
        return ""

    def _active_for_composer(self, registration: Registration | None) -> bool:
        return (
            registration is not None
            and registration.state == "active"
            and registration.reference is not None
            and not self._session_refusal(registration.account_id, registration.session_id)
        )

    # -- idempotency -------------------------------------------------------------------------

    def _digest(self, operation: str, canonical: Mapping[str, object]) -> str:
        text = json.dumps({"operation": operation, **canonical}, sort_keys=True)
        return hmac.new(self._digest_key, text.encode("utf-8"), hashlib.sha256).hexdigest()

    def _replay(
        self, key: tuple[UUID, str, str], digest: str, caller: Caller
    ) -> CommandResult | None:
        receipt = self._receipts.get(key)
        if receipt is None:
            return None
        if not hmac.compare_digest(receipt.digest, digest):
            return CommandResult("refused", chat.IDEMPOTENCY_CONFLICT)
        # A replay changes nothing; the projection is the current one.
        return CommandResult("replayed", receipt=receipt, settings=self._view(caller))

    def _view(self, caller: Caller) -> NotificationSettingsView | None:
        registration = self._registrations.get((caller.account_id, caller.device_id))
        if registration is None:
            return None
        settings = self.settings_of(caller.account_id)
        return NotificationSettingsView(
            registration.version,
            settings.match_notifications,
            settings.message_notifications,
            registration.state,
        )

    # -- F12: the owner's read ---------------------------------------------------------------

    def read(self, caller: Caller) -> ReadResult:
        """The owner's own settings for the requesting installation, from a current session."""
        with self._lock:
            refusal = self._session_refusal(caller.account_id, caller.session_id)
            if refusal:
                logger.debug("notification settings read refused: %s", refusal)
                return ReadResult("refused", refusal)
            view = self._view(caller)
            if view is None:
                return ReadResult("absent")
            return ReadResult("read", settings=view)

    # -- F12: register, rotate and revoke ----------------------------------------------------

    def device(self, caller: Caller, intent: object) -> CommandResult:
        with self._lock:
            refusal = self._session_refusal(caller.account_id, caller.session_id)
            if refusal:
                logger.debug("notification device command refused: %s", refusal)
                return CommandResult("refused", refusal)
            try:
                command = parse_device_intent(intent)
            except IntentError:
                logger.debug("notification device command refused: %s", INTENT_INVALID)
                return CommandResult("refused", INTENT_INVALID)
            if command.device_id != caller.device_id:
                return CommandResult("refused", WRONG_INSTALLATION)
            key = (caller.account_id, "device", command.meta.idempotency_key)
            canonical: dict[str, object] = {
                "device_id": str(command.device_id),
                "action": command.action,
                "provider_token": None if command.token is None else command.token.reveal(),
                "expected_version": command.meta.expected_version,
            }
            digest = self._digest("device", canonical)
            del canonical
            replayed = self._replay(key, digest, caller)
            if replayed is not None:
                logger.debug("notification device command: %s", replayed.outcome)
                return replayed
            if len(self._receipts) >= MAX_RECEIPTS:
                return CommandResult("refused", FIXTURE_CAPACITY)
            current = self._registrations.get((caller.account_id, command.device_id))
            if command.meta.expected_version != (0 if current is None else current.version):
                logger.debug("notification device command refused: %s", STALE_VERSION)
                return CommandResult("refused", STALE_VERSION)
            if command.action == "revoke":
                return self._revoke(caller, command, key, digest, current)
            return self._register(caller, command, key, digest, current)

    def _register(
        self,
        caller: Caller,
        command: DeviceCommand,
        key: tuple[UUID, str, str],
        digest: str,
        current: Registration | None,
    ) -> CommandResult:
        assert command.token is not None
        transition = "rotate" if current is not None and current.state == "active" else "register"
        # Custody: the store takes the token before any reference is saved; a refusal saves nothing.
        try:
            reference = self._tokens.put(command.token)
        except Exception:
            logger.debug("notification device command refused: %s", TOKEN_STORE_REFUSED)
            return CommandResult("refused", TOKEN_STORE_REFUSED)
        if not isinstance(reference, TokenReference):
            return CommandResult("refused", TOKEN_STORE_REFUSED)
        retired: list[TokenReference] = []
        registrations = dict(self._registrations)
        # The same unit of work: an installation active for another account is revoked first.
        for other_key, other in self._registrations.items():
            if (
                other.device_id == command.device_id
                and other.account_id != caller.account_id
                and other.state == "active"
            ):
                registrations[other_key] = replace(
                    other,
                    state="revoked",
                    version=other.version + 1,
                    reference=None,
                    ended_by="transfer",
                )
                if other.reference is not None:
                    retired.append(other.reference)
        if current is not None and current.state == "active" and current.reference is not None:
            # Rotate: the new token's reference replaces the old one, which is discarded.
            retired.append(current.reference)
        version = 1 if current is None else current.version + 1
        registrations[(caller.account_id, command.device_id)] = Registration(
            caller.account_id, command.device_id, "active", version, caller.session_id, reference
        )
        receipt = Receipt(digest, transition, command.device_id, version)
        self._registrations = registrations
        self._receipts[key] = receipt
        self._discard(retired)
        logger.debug("notification device command: %s", transition)
        return CommandResult(
            "applied", receipt=receipt, settings=self._view(caller), transition=transition
        )

    def _revoke(
        self,
        caller: Caller,
        command: DeviceCommand,
        key: tuple[UUID, str, str],
        digest: str,
        current: Registration | None,
    ) -> CommandResult:
        if current is None or current.state != "active":
            # F12 lists revoke from active only; every unlisted transition is forbidden.
            logger.debug("notification device command refused: %s", TRANSITION_FORBIDDEN)
            return CommandResult("refused", TRANSITION_FORBIDDEN)
        retired = [current.reference] if current.reference is not None else []
        ended = replace(
            current, state="revoked", version=current.version + 1, reference=None, ended_by="revoke"
        )
        receipt = Receipt(digest, "revoke", command.device_id, ended.version)
        self._registrations = {**self._registrations, (caller.account_id, command.device_id): ended}
        self._receipts[key] = receipt
        self._discard(retired)
        logger.debug("notification device command: revoke")
        return CommandResult(
            "applied", receipt=receipt, settings=self._view(caller), transition="revoke"
        )

    # -- F12: settings -----------------------------------------------------------------------

    def settings(self, caller: Caller, intent: object) -> CommandResult:
        with self._lock:
            refusal = self._session_refusal(caller.account_id, caller.session_id)
            if refusal:
                logger.debug("notification settings command refused: %s", refusal)
                return CommandResult("refused", refusal)
            try:
                command = parse_settings_intent(intent)
            except IntentError:
                logger.debug("notification settings command refused: %s", INTENT_INVALID)
                return CommandResult("refused", INTENT_INVALID)
            key = (caller.account_id, "notifications", command.meta.idempotency_key)
            digest = self._digest(
                "notifications",
                {
                    "device_id": str(caller.device_id),
                    "match_notifications": command.match_notifications,
                    "message_notifications": command.message_notifications,
                    "expected_version": command.meta.expected_version,
                },
            )
            replayed = self._replay(key, digest, caller)
            if replayed is not None:
                logger.debug("notification settings command: %s", replayed.outcome)
                return replayed
            if len(self._receipts) >= MAX_RECEIPTS:
                return CommandResult("refused", FIXTURE_CAPACITY)
            current = self._registrations.get((caller.account_id, caller.device_id))
            if current is None or current.state != "active":
                # F12 lists settings from active only.
                logger.debug("notification settings command refused: %s", REGISTRATION_NOT_ACTIVE)
                return CommandResult("refused", REGISTRATION_NOT_ACTIVE)
            if command.meta.expected_version != current.version:
                logger.debug("notification settings command refused: %s", STALE_VERSION)
                return CommandResult("refused", STALE_VERSION)
            previous = self.settings_of(caller.account_id)
            # Every installation's view of the account's settings advances together.
            registrations = {
                reg_key: replace(registration, version=registration.version + 1)
                if registration.account_id == caller.account_id
                else registration
                for reg_key, registration in self._registrations.items()
            }
            committed = registrations[(caller.account_id, caller.device_id)].version
            receipt = Receipt(digest, "settings", caller.device_id, committed)
            self._settings[caller.account_id] = Settings(
                command.match_notifications, command.message_notifications, previous.version + 1
            )
            self._registrations = registrations
            self._receipts[key] = receipt
            logger.debug("notification settings command: applied")
            return CommandResult("applied", receipt=receipt, settings=self._view(caller))

    # -- F12: the system's logout ------------------------------------------------------------

    def logout(self, session_id: UUID) -> tuple[UUID, ...]:
        """F12's ``logout`` by the system: every active registration the ending session made is
        revoked and its token discarded; the account's registrations from its other sessions stay
        active. Returns the installations revoked."""
        with self._lock:
            registrations = dict(self._registrations)
            retired: list[TokenReference] = []
            revoked: list[UUID] = []
            for reg_key, registration in self._registrations.items():
                if registration.state == "active" and registration.session_id == session_id:
                    registrations[reg_key] = replace(
                        registration,
                        state="revoked",
                        version=registration.version + 1,
                        reference=None,
                        ended_by="logout",
                    )
                    if registration.reference is not None:
                        retired.append(registration.reference)
                    revoked.append(registration.device_id)
            self._registrations = registrations
            self._discard(retired)
            logger.debug("notification logout: %d registrations revoked", len(revoked))
            return tuple(revoked)

    # -- custody: discards -------------------------------------------------------------------

    def _discard(self, references: list[TokenReference]) -> None:
        """After a change commits: each old token is discarded through the port; a failure is kept
        for ``retry_discards``. The change stands either way."""
        for reference in references:
            try:
                self._tokens.discard(reference)
            except Exception:
                self._pending_discards.append(reference)
                logger.warning("notification token discard failed; kept for retry")

    def retry_discards(self) -> int:
        """Tries each failed discard again; returns how many still wait."""
        with self._lock:
            waiting, self._pending_discards = self._pending_discards, []
            self._discard(waiting)
            return len(self._pending_discards)

    # -- the composer ------------------------------------------------------------------------

    def _contact_refusal(self, kind: NotificationKind, trigger: Trigger) -> str:
        """The send's checks, on facts read now (chat_reads.py: "Whatever refuses a send refuses a
        read"), and the trigger's recipient rule. Empty when the notification may go."""
        match = self._facts.match(trigger.match_id)
        if match is None:
            return chat.MATCH_MISSING
        if trigger.recipient not in match.participants:
            return chat.NOT_A_MEMBER
        if isinstance(trigger, MessageAccepted):
            message = self._facts.message(trigger.submission_id)
            if message is None:
                return MESSAGE_MISSING
            if message.match_id != trigger.match_id:
                return MESSAGE_MATCH_MISMATCH
            if message.sender not in match.participants:
                return chat.NOT_A_MEMBER
            if message.sender == trigger.recipient:
                return RECIPIENT_IS_SENDER
            if message.state != "accepted":
                return MESSAGE_NOT_ACCEPTED
        elif match.completed_by == trigger.recipient:
            return RECIPIENT_COMPLETED_MATCH
        if match.state != "active":
            return chat.MATCH_NOT_ACTIVE
        if match.blocked:
            return chat.BLOCKED
        members = [self._facts.member(account) for account in match.participants]
        for member in members:
            if member is None:
                return chat.ACCOUNT_MISSING
            if member.account_state != "active":
                return chat.ACCOUNT_NOT_ACTIVE
        for member in members:
            assert member is not None
            if member.profile_state != "visible":
                return chat.PROFILE_UNAVAILABLE
        for member in members:
            assert member is not None
            if member.consent_state != "accepted":
                return chat.CONSENT_NOT_CURRENT
        return ""

    def _active_devices(self, account_id: UUID) -> frozenset[UUID]:
        return frozenset(
            registration.device_id
            for registration in self._registrations.values()
            if registration.account_id == account_id and self._active_for_composer(registration)
        )

    @staticmethod
    def ledger_key(event_id: UUID, device_id: UUID) -> str:
        return f"{event_id}:{device_id}"

    def deliver(self, trigger: object) -> DeliveryResult:
        """One delivery of a trigger: a first one or a redelivery of the same event."""
        with self._lock:
            kind = _trigger_kind(trigger)
            if kind is None:
                logger.debug("notification delivery refused: %s", TRIGGER_INVALID)
                return DeliveryResult("refused", TRIGGER_INVALID)
            assert isinstance(trigger, MatchActivated | MessageAccepted)
            refusal = self._contact_refusal(kind, trigger)
            if refusal:
                logger.debug("notification delivery refused: %s", refusal)
                return DeliveryResult("refused", refusal)
            settings = self.settings_of(trigger.recipient)
            enabled = (
                settings.match_notifications if kind == "match" else settings.message_notifications
            )
            if not enabled:
                logger.debug("notification delivery refused: %s", SETTING_OFF)
                return DeliveryResult("refused", SETTING_OFF)
            fixed = self._fixed.get(trigger.event_id)
            if fixed is None:
                fixed = _Fixed(trigger, self._active_devices(trigger.recipient))
                self._fixed[trigger.event_id] = fixed
            elif fixed.trigger != trigger:
                logger.debug("notification delivery refused: %s", TRIGGER_CONFLICT)
                return DeliveryResult("refused", TRIGGER_CONFLICT)
            if not fixed.devices:
                logger.debug("notification delivery refused: %s", NO_ACTIVE_DEVICE)
                return DeliveryResult("refused", NO_ACTIVE_DEVICE)
            unsent = [
                device_id
                for device_id in sorted(fixed.devices)
                if self.ledger_key(trigger.event_id, device_id) not in self._ledger
            ]
            if not unsent:
                return DeliveryResult("nothing", ALREADY_DELIVERED)
            content = PushContent(TITLE, WORDING[kind], kind, ROUTES[kind])
            sent = pending = recorded = 0
            for device_id in unsent:
                registration = self._registrations.get((trigger.recipient, device_id))
                if not self._active_for_composer(registration):
                    continue
                assert registration is not None and registration.reference is not None
                ledger_key = self.ledger_key(trigger.event_id, device_id)
                request = PushRequest(registration.reference, ledger_key, content)
                try:
                    outcome = self._transport.send(request)
                except Exception:
                    pending += 1
                    continue
                if outcome == "accepted":
                    sent += 1
                    self._ledger.add(ledger_key)
                elif outcome == "repeat":
                    # Accepted by the transport earlier and not recorded then: record it now.
                    recorded += 1
                    self._ledger.add(ledger_key)
                else:
                    pending += 1
            logger.debug("notification delivery: %s sent %d pending %d", kind, sent, pending)
            if sent:
                return DeliveryResult("sent", sent=sent, pending=pending)
            if pending:
                return DeliveryResult("nothing", TRANSPORT_UNAVAILABLE, pending=pending)
            if recorded:
                return DeliveryResult("nothing", ALREADY_DELIVERED)
            # Every fixed device left is no longer active.
            return DeliveryResult("nothing", NO_ACTIVE_DEVICE)
