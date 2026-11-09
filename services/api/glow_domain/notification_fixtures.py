"""In-memory fixtures for the notification ports (P06.3, D1 and D3): a token store, a push
transport and a world of accounts, sessions, matches and messages that answers the composer's
facts and the sessions' checks. Development and test only; no provider, network, credential or
database. The tokens they handle are synthetic test data (``synthetic_token``).

- **The token store** keeps each token under a fresh opaque reference. ``refuse_next_put`` and
  ``fail_next_discard`` inject a refusal or a failure. ``resolve`` exists for tests only; the
  domain never calls it.
- **The transport** records what it was given (the device's reference, the idempotency key and
  the content) and refuses a repeated idempotency key as a ``repeat``. ``fail_next`` makes the
  next send fail before acceptance; ``lose_next_answer`` makes it accept and then fail, as a
  transport whose answer was lost.
- **The world** holds Glow's rows as the composer and the session checks read them, and lets a
  test change them between deliveries.
"""

from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

from .notifications import (
    AccountFacts,
    MatchFacts,
    MemberFacts,
    MessageFacts,
    NotificationService,
    ProviderToken,
    PushRequest,
    PushTransportError,
    SessionFacts,
    TokenReference,
    TokenStoreError,
    TransportOutcome,
)
from .provider_fixtures import require_fixture_environment

FIXTURE_NOW = datetime(2026, 11, 8, 12, 0, tzinfo=UTC)
SESSION_LIFETIME = timedelta(hours=1)


def synthetic_token(label: str | int) -> str:
    """An obviously synthetic push token: test data, never a device's."""
    return f"SYNTHETIC-FIXTURE-PUSH-TOKEN-{label}-NOT-A-REAL-DEVICE-TOKEN"


class FixtureTokenStore:
    """Holds synthetic tokens under opaque references. No network, no persistence."""

    def __init__(self, environment: str) -> None:
        require_fixture_environment(environment)
        self._held: dict[str, str] = {}
        self._refuse_puts = 0
        self._fail_discards = 0
        self.puts = 0
        self.discarded: list[TokenReference] = []
        self._lock = threading.Lock()

    def __repr__(self) -> str:
        return "FixtureTokenStore(<fixture>)"

    def refuse_next_put(self, count: int = 1) -> None:
        self._refuse_puts += count

    def fail_next_discard(self, count: int = 1) -> None:
        self._fail_discards += count

    def put(self, token: ProviderToken) -> TokenReference:
        with self._lock:
            if self._refuse_puts:
                self._refuse_puts -= 1
                raise TokenStoreError()
            self.puts += 1
            reference = TokenReference(f"fixture-token-ref-{uuid.uuid4().hex}")
            self._held[reference.value] = token.reveal()
            return reference

    def discard(self, reference: TokenReference) -> None:
        with self._lock:
            if self._fail_discards:
                self._fail_discards -= 1
                raise TokenStoreError()
            self._held.pop(reference.value, None)
            self.discarded.append(reference)

    @property
    def held(self) -> int:
        return len(self._held)

    def resolve(self, reference: TokenReference) -> str | None:
        """For tests only (a transport adapter's job, P11B): the token a reference holds, or
        ``None`` once discarded."""
        return self._held.get(reference.value)


@dataclass(frozen=True)
class RecordedPush:
    """What the transport was given: the reference's value, the key and the content's payload."""

    reference: str
    idempotency_key: str
    payload: dict[str, object]
    outcome: str


class FixturePushTransport:
    """Records each push request and refuses a repeated idempotency key."""

    def __init__(self, environment: str) -> None:
        require_fixture_environment(environment)
        self.recorded: list[RecordedPush] = []
        self._accepted: set[str] = set()
        self._fail = 0
        self._lose = 0
        self._lock = threading.Lock()

    def __repr__(self) -> str:
        return "FixturePushTransport(<fixture>)"

    def fail_next(self, count: int = 1) -> None:
        self._fail += count

    def lose_next_answer(self, count: int = 1) -> None:
        self._lose += count

    def send(self, request: PushRequest) -> TransportOutcome:
        with self._lock:
            payload = request.content.as_payload()
            key = request.idempotency_key
            if key in self._accepted:
                self.recorded.append(RecordedPush(request.device.value, key, payload, "repeat"))
                return "repeat"
            if self._fail:
                self._fail -= 1
                self.recorded.append(RecordedPush(request.device.value, key, payload, "failed"))
                raise PushTransportError()
            self._accepted.add(key)
            if self._lose:
                self._lose -= 1
                self.recorded.append(RecordedPush(request.device.value, key, payload, "lost"))
                raise PushTransportError()
            self.recorded.append(RecordedPush(request.device.value, key, payload, "accepted"))
            return "accepted"

    def accepted_keys(self) -> frozenset[str]:
        return frozenset(self._accepted)


@dataclass
class _Account:
    state: str = "active"
    session_epoch: int = 1
    profile_state: str | None = "visible"
    consent_state: str | None = "accepted"


@dataclass
class _Match:
    state: str
    participants: tuple[UUID, UUID]
    completed_by: UUID


class FixtureNotificationWorld:
    """Glow's rows as the notification service reads them: accounts with their profile and
    consent, sessions, matches, blocks and message submissions. It implements both
    ``SessionAuthority`` and ``DeliveryFacts``; ``reads`` counts the composer's fact reads."""

    def __init__(self, environment: str, clock: Callable[[], datetime]) -> None:
        require_fixture_environment(environment)
        self._clock = clock
        self._accounts: dict[UUID, _Account] = {}
        self._sessions: dict[UUID, SessionFacts] = {}
        self._matches: dict[UUID, _Match] = {}
        self._blocks: set[tuple[UUID, UUID]] = set()
        self._messages: dict[UUID, MessageFacts] = {}
        self.reads = 0

    def __repr__(self) -> str:
        return "FixtureNotificationWorld(<fixture>)"

    # -- what a test sets up and changes ----------------------------------------------------

    def add_account(self) -> UUID:
        account_id = uuid.uuid4()
        self._accounts[account_id] = _Account()
        return account_id

    def open_session(self, account_id: UUID, lifetime: timedelta = SESSION_LIFETIME) -> UUID:
        account = self._accounts[account_id]
        session_id = uuid.uuid4()
        self._sessions[session_id] = SessionFacts(
            account_id, "valid", account.session_epoch, self._clock() + lifetime
        )
        return session_id

    def end_session(self, session_id: UUID, state: str = "revoked") -> None:
        self._sessions[session_id] = replace(self._sessions[session_id], state=state)

    def bump_epoch(self, account_id: UUID) -> None:
        self._accounts[account_id].session_epoch += 1

    def set_account(self, account_id: UUID, state: str) -> None:
        """A suspension or a deletion: the state changes and the session epoch moves on."""
        account = self._accounts[account_id]
        account.state = state
        if state != "active":
            account.session_epoch += 1

    def set_profile(self, account_id: UUID, state: str | None) -> None:
        self._accounts[account_id].profile_state = state

    def set_consent(self, account_id: UUID, state: str | None) -> None:
        self._accounts[account_id].consent_state = state

    def add_match(self, earlier: UUID, completed_by: UUID) -> UUID:
        """An active match: ``earlier`` liked first, and ``completed_by``'s like matched it."""
        match_id = uuid.uuid4()
        self._matches[match_id] = _Match("active", (earlier, completed_by), completed_by)
        return match_id

    def set_match(self, match_id: UUID, state: str) -> None:
        self._matches[match_id].state = state

    def block(self, actor: UUID, target: UUID) -> None:
        self._blocks.add((actor, target))

    def unblock(self, actor: UUID, target: UUID) -> None:
        self._blocks.discard((actor, target))

    def add_message(self, match_id: UUID, sender: UUID, state: str = "accepted") -> UUID:
        submission_id = uuid.uuid4()
        self._messages[submission_id] = MessageFacts(match_id, sender, state)
        return submission_id

    def set_message(self, submission_id: UUID, state: str) -> None:
        self._messages[submission_id] = replace(self._messages[submission_id], state=state)

    # -- SessionAuthority -------------------------------------------------------------------

    def session(self, session_id: UUID) -> SessionFacts | None:
        return self._sessions.get(session_id)

    def account(self, account_id: UUID) -> AccountFacts | None:
        account = self._accounts.get(account_id)
        return None if account is None else AccountFacts(account.state, account.session_epoch)

    # -- DeliveryFacts ----------------------------------------------------------------------

    def match(self, match_id: UUID) -> MatchFacts | None:
        self.reads += 1
        match = self._matches.get(match_id)
        if match is None:
            return None
        first, second = match.participants
        blocked = (first, second) in self._blocks or (second, first) in self._blocks
        return MatchFacts(match.state, match.participants, match.completed_by, blocked)

    def message(self, submission_id: UUID) -> MessageFacts | None:
        self.reads += 1
        return self._messages.get(submission_id)

    def member(self, account_id: UUID) -> MemberFacts | None:
        self.reads += 1
        account = self._accounts.get(account_id)
        if account is None:
            return None
        return MemberFacts(account.state, account.profile_state, account.consent_state)


@dataclass
class FixtureClock:
    now: datetime = FIXTURE_NOW

    def __call__(self) -> datetime:
        return self.now

    def advance(self, delta: timedelta) -> None:
        self.now = self.now + delta


@dataclass(frozen=True)
class NotificationFixture:
    service: NotificationService
    world: FixtureNotificationWorld
    tokens: FixtureTokenStore
    transport: FixturePushTransport
    clock: FixtureClock


def notification_fixture(environment: str = "test") -> NotificationFixture:
    """The service over the three fixtures, on fixture time."""
    clock = FixtureClock()
    world = FixtureNotificationWorld(environment, clock)
    tokens = FixtureTokenStore(environment)
    transport = FixturePushTransport(environment)
    service = NotificationService(
        environment=environment,
        sessions=world,
        facts=world,
        tokens=tokens,
        transport=transport,
        clock=clock,
    )
    return NotificationFixture(service, world, tokens, transport, clock)
