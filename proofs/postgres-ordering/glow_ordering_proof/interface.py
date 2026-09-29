"""One small interface for the race suite (D1; DM-08 item 6, *consider*).

The suite drives send, block, unblock, unmatch, suspend, delete, sign-in, sign-out and
administrative expiry through ``OrderingSubject``. The reference design implements it
here (``reference.py``); P06.2 implements it over the app's persistence adapter and
runs the same suite, so "carried into the app" becomes a check.

Everything a writer returns is a ``Result``. A writer never raises for a refusal; it
raises only for a harness error. ``Hooks`` let the harness observe a writer from
inside its transaction: the backend pid when it begins, and hold points after its
first lock and after all its locks, which the forced interleavings use.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

Outcome = Literal["authorized", "replayed", "applied", "no_change", "refused", "deadlock", "error"]
COMMITTED_OUTCOMES: frozenset[str] = frozenset({"authorized", "applied"})


@dataclass(frozen=True)
class Receipt:
    """The immutable receipt of a committed send authorization."""

    submission_id: UUID
    contact_version: int
    request_digest: str


@dataclass(frozen=True)
class Timing:
    """Database-clock times of one writer's transaction. ``started_at`` is ``now()`` inside
    the transaction (its start). ``ended_at`` is ``clock_timestamp()`` read just before a
    rollback; a committed writer's end is its commit timestamp, read later from the row
    it wrote (``pg_xact_commit_timestamp(xmin)``)."""

    backend_pid: int
    started_at: datetime
    ended_at: datetime | None = None


@dataclass(frozen=True)
class Result:
    outcome: Outcome
    reason: str = ""
    receipt: Receipt | None = None
    timing: Timing | None = None
    session_id: UUID | None = None
    detail: Mapping[str, object] = field(default_factory=dict)

    @property
    def committed(self) -> bool:
        return self.outcome in COMMITTED_OUTCOMES

    def label(self) -> str:
        return f"{self.outcome}:{self.reason}" if self.reason else self.outcome


@dataclass(frozen=True)
class SendRequest:
    session_id: UUID
    match_id: UUID
    contact_version: int
    idempotency_key: str
    text: str

    @property
    def request_digest(self) -> str:
        """A digest of the canonical request: the same key with a different request is a
        conflict (data model, idempotency keys)."""
        canonical = f"{self.match_id}\n{self.contact_version}\n{self.text}".encode()
        return hashlib.sha256(canonical).hexdigest()


@dataclass
class Hooks:
    on_begin: Callable[[int], None] | None = None
    after_first_lock: Callable[[], None] | None = None
    after_locks: Callable[[], None] | None = None


class OrderingSubject(Protocol):
    def sign_in(
        self, account_id: UUID, *, ttl_seconds: float, hooks: Hooks | None = None
    ) -> Result:
        """A session for the account, bound to its current ``session_epoch``."""

    def sign_out(self, session_id: UUID, *, hooks: Hooks | None = None) -> Result: ...

    def expire_session(self, session_id: UUID, *, hooks: Hooks | None = None) -> Result:
        """An administrative expiry of one session."""

    def send(self, request: SendRequest, *, hooks: Hooks | None = None) -> Result:
        """A send authorization: a ``MessageSubmission`` with its ``OutboxEvent``."""

    def block(self, actor_id: UUID, target_id: UUID, *, hooks: Hooks | None = None) -> Result: ...

    def unblock(self, actor_id: UUID, target_id: UUID, *, hooks: Hooks | None = None) -> Result: ...

    def unmatch(self, actor_id: UUID, match_id: UUID, *, hooks: Hooks | None = None) -> Result: ...

    def suspend(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result: ...

    def delete(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        """The deletion lifecycle transition, never a hard delete (5.6)."""


class FixtureFactory(Protocol):
    def create_account(self) -> UUID:
        """A user through the maintained authentication persistence and its active
        ``AppAccount``."""

    def create_match(self, first: UUID, second: UUID) -> UUID:
        """An active match between two accounts with an active ``ChatBinding``, created
        locally with a stand-in channel reference; no provider is called."""
