"""The chat contact port (P06.2 Stage A, D2): send authorization and every revocation
of contact, as commands a persistence adapter carries out in one transaction each.

Pure domain types, independent of Django. The adapter that implements
``ContactPersistence`` is ``glow_chat.contact`` over ``glow_persistence``'s models; it
runs only under the disposable-database proof's settings until P11 wires it (D2). No
HTTP route, served feature or provider call is attached to this port.

A writer never raises for a refusal: it returns a ``ContactResult`` whose ``reason``
is one of the Glow codes below. ``TransactionProbe`` lets a caller observe a writer
from inside its transaction (its backend and its hold points); a probe only signals
and waits, and never changes a lock, a check or a write (DM-13 2.1).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal, Protocol
from uuid import UUID

if TYPE_CHECKING:
    from .chat_tokens import TokenGrant

# D5 (DM-13 4.1): the one consent the production contracts define, F02's
# ConsentIntent, held as ConsentDecision rows under this purpose. A send needs the
# latest decision of both accounts to be ``accepted``.
ONBOARDING_CONSENT_PURPOSE = "onboarding"

Outcome = Literal[
    "authorized", "replayed", "applied", "no_change", "granted", "refused", "deadlock", "error"
]
# Outcomes whose transaction wrote rows. A grant (P06.2 B1) reads under shared locks and
# writes nothing: it is not a commit the oracle has a row for.
COMMITTED: frozenset[str] = frozenset({"authorized", "applied"})

# Refusal reasons: Glow's own codes, never a provider's or a database's text.
MATCH_MISSING = "match_missing"
MATCH_NOT_ACTIVE = "match_not_active"
MATCH_CHANGED = "match_changed"
# P06.2 B1 (F2): the locked session's account differs from the pre-lock read.
SESSION_CHANGED = "session_changed"
# P06.2 B1 (F5): a block whose actor is its own target, refused before any write.
SELF_TARGET = "self_target"
MATCH_EXISTS = "match_exists"
NOT_A_MEMBER = "not_a_member"
ACCOUNT_MISSING = "appaccount_missing"
ACCOUNT_NOT_ACTIVE = "account_not_active"
ACCOUNT_DELETED = "account_deleted"
SESSION_MISSING = "session_missing"
SESSION_NOT_VALID = "session_not_valid"
SESSION_EXPIRED = "session_expired"
SESSION_EPOCH_STALE = "session_epoch_stale"
BLOCKED = "blocked"
ALREADY_BLOCKED = "already_blocked"
NO_ACTIVE_BLOCK = "no_active_block"
STALE_CONTACT_VERSION = "stale_contact_version"
IDEMPOTENCY_CONFLICT = "idempotency_conflict"
BINDING_NOT_ACTIVE = "binding_not_active"
PROFILE_UNAVAILABLE = "profile_unavailable"
PROFILE_MISSING = "profile_missing"
CONSENT_NOT_CURRENT = "consent_not_current"
NO_CONSENT = "no_consent"


@dataclass(frozen=True)
class SendCommand:
    """A member's request to send. The actor is the session's account, never a field
    of the request."""

    session_id: UUID
    match_id: UUID
    contact_version: int
    idempotency_key: str
    text: str

    @property
    def request_digest(self) -> str:
        """The canonical request's digest: the same key with a different request is a
        conflict (data model, idempotency keys)."""
        canonical = f"{self.match_id}\n{self.contact_version}\n{self.text}".encode()
        return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class SendReceipt:
    """The immutable receipt of a committed send authorization."""

    submission_id: UUID
    contact_version: int
    request_digest: str


@dataclass(frozen=True)
class TransactionTrace:
    """What the database said about one writer's transaction: its backend, its start
    (``now()`` inside it) and, for a writer that rolled back, ``clock_timestamp()``
    read just before the rollback. A committed writer's end is its commit timestamp."""

    backend_pid: int
    started_at: datetime
    ended_at: datetime | None = None


@dataclass(frozen=True)
class ContactResult:
    outcome: Outcome
    reason: str = ""
    receipt: SendReceipt | None = None
    trace: TransactionTrace | None = None
    session_id: UUID | None = None
    match_id: UUID | None = None
    # The outbox events the transaction wrote, in order.
    events: tuple[UUID, ...] = ()
    # P06.2 B1: a token grant's result (outcome ``granted``), with its issue time read
    # from the database clock under the grant's locks.
    grant: TokenGrant | None = None
    detail: dict[str, object] = field(default_factory=dict)

    @property
    def committed(self) -> bool:
        return self.outcome in COMMITTED


@dataclass
class TransactionProbe:
    """Hold points a caller may observe a writer at. Each callable only signals and
    waits; none of them is a switch (DM-13 2.1)."""

    on_begin: Callable[[int], None] | None = None
    after_first_lock: Callable[[], None] | None = None
    after_locks: Callable[[], None] | None = None
    # After every check and write, before the commit (CX2's boundary).
    before_commit: Callable[[], None] | None = None


class ContactPersistence(Protocol):
    """Send authorization and every revocation of contact (P06.DB D5 with P06.2 D5).

    Every writer takes its row locks by primary key in the canonical order: the lower
    account, the higher account, the match, then the sending session."""

    def activate_match(
        self, first: UUID, second: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        """The canonical match of two active accounts with its chat binding: random
        channel and provider user IDs, committed with the identities' and the channel's
        outbox events before any provider call.

        This is the proof's and the conformance run's way to make a match, not F09's
        activation (CX5; DM-15 6.3): it checks, under both account locks, the accounts'
        state, an active block, an existing pair, and the send's own checks of both
        profiles and both onboarding consents (P06.2 B1). Reciprocal likes and current
        two-person eligibility are checked by the activation P11 wires, under the same
        locks. No runtime path calls this method."""

    def grant_token(
        self, session_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        """A chat token grant (P06.2 B1; F1, DM-14 item 3): in one transaction, the
        account row then the session row locked ``FOR SHARE`` in the send's order, the
        time read from the database clock under those locks, and every check of
        ``glow_domain.chat_tokens.grant_chat_token`` run on the locked rows with that time
        as ``now``. Outcome ``granted`` carries the grant with its issue time; a refusal
        carries the rule's code. Nothing is written and nothing is signed: B2's adapter
        signs from the issue time, and P11 serves the endpoint."""

    def open_session(
        self,
        account_id: UUID,
        *,
        auth_session_ref: str,
        lifetime: timedelta,
        probe: TransactionProbe | None = None,
    ) -> ContactResult:
        """An ``AccountSession`` at the account's current epoch. The non-secret
        ``auth_session_ref`` comes from the maintained authentication adapter."""

    def sign_out(
        self, session_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def expire_session(
        self, session_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        """An administrative expiry of one session."""

    def send(self, command: SendCommand, *, probe: TransactionProbe | None = None) -> ContactResult:
        """A ``MessageSubmission`` with its ``OutboxEvent``, in one transaction."""

    def block(
        self, actor_id: UUID, target_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def unblock(
        self, actor_id: UUID, target_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def unmatch(
        self, actor_id: UUID, match_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def suspend(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def delete(self, account_id: UUID, *, probe: TransactionProbe | None = None) -> ContactResult:
        """The deletion lifecycle transition, never a hard delete."""

    def pause_profile(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def resume_profile(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def restrict_profile(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def withdraw_consent(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult: ...

    def accept_consent(
        self, account_id: UUID, *, policy_version: str, probe: TransactionProbe | None = None
    ) -> ContactResult: ...
