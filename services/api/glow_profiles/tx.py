"""One SV2 operation's transaction (the SV2 brief's D6 and D9; DM-13 4.1; DM-52).

- **The whole of its transaction:** an SV2 operation never runs inside a transaction its caller
  opened (it is ``error`` / ``transaction_open`` before any statement), and its block is durable.
  ``glow_chat``'s writers, which SV2 calls on purpose, nest inside it as savepoints; any result of
  theirs other than ``applied`` or ``no_change`` is a refusal that rolls the whole transaction
  back.
- **The account row first:** every writer locks the actor's ``AppAccount`` row ``FOR UPDATE``
  before anything else, so a requirement's writer and a completion check cannot interleave.
  ``lock_account`` refuses an account that is not ``active``; only F05's purge and the store's
  deletion acknowledgment take the row in any state (``lock_account_any_state``; DM-58 item 9).
- **The time** is ``clock_timestamp()`` read after the locks.
- **A refusal** names a contract error code and an internal reason, both codes, never a value. A
  deadlock or any other database error becomes a result, by type only; nothing is retried.
- A ``TransactionProbe`` may observe the operation at its hold points; it only signals and waits.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

from django.db import IntegrityError, connection, transaction

from glow_domain.chat import TransactionProbe
from glow_domain.chat import TransactionTrace as Trace
from glow_persistence.models import AppAccount

DEADLOCK_DETECTED = "40P01"
TRANSACTION_OPEN = "transaction_open"

# The contract's error codes (gapp-api-v1's Error) and their planned HTTP statuses.
INVALID_REQUEST = "invalid_request"
UNAUTHENTICATED = "unauthenticated"
FORBIDDEN = "forbidden"
NOT_FOUND = "not_found"
STATE_CONFLICT = "state_conflict"
STALE_VERSION = "stale_version"
IDEMPOTENCY_CONFLICT = "idempotency_conflict"
POLICY_UNRESOLVED = "policy_unresolved"
PROVIDER_UNAVAILABLE = "provider_unavailable"
STATUS: dict[str, int] = {
    INVALID_REQUEST: 400,
    UNAUTHENTICATED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    STATE_CONFLICT: 409,
    STALE_VERSION: 409,
    IDEMPOTENCY_CONFLICT: 409,
    POLICY_UNRESOLVED: 409,
    PROVIDER_UNAVAILABLE: 503,
}


class Refused(Exception):
    """A refusal inside an operation: a contract code and an internal reason, never a value."""

    def __init__(self, code: str, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason


class _Rollback(Exception):
    def __init__(self, refused: Refused, trace: Trace) -> None:
        super().__init__(refused.reason)
        self.refused = refused
        self.trace = trace


@dataclass(frozen=True)
class Result:
    """``applied``, ``no_change``, ``replayed``, ``read``, ``refused`` or ``error``."""

    outcome: str
    code: str = ""
    reason: str = ""
    data: dict[str, Any] | None = None
    trace: Trace | None = None
    events: tuple[UUID, ...] = ()
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.outcome in ("applied", "no_change", "replayed", "read")


@dataclass
class Tx:
    cursor: Any
    trace: Trace
    probe: TransactionProbe | None
    events: list[UUID] = field(default_factory=list)
    # D19: the settings pointers this transaction holds, in the order it locked them. Only
    # ``settings_store`` records and checks them.
    pointers: list[str] = field(default_factory=list)


def caller_transaction_open() -> bool:
    return bool(connection.in_atomic_block or not connection.get_autocommit())


def signal(probe: TransactionProbe | None, name: str) -> None:
    callback = getattr(probe, name, None) if probe is not None else None
    if callback is not None:
        callback()


def clock(tx: Tx) -> datetime:
    tx.cursor.execute("SELECT clock_timestamp()")
    value = tx.cursor.fetchone()[0]
    assert isinstance(value, datetime)
    return value


def utc_date(instant: datetime) -> date:
    return instant.astimezone(UTC).date()


def run(body: Callable[[Tx], Result], probe: TransactionProbe | None = None) -> Result:
    """One SV2 transaction. A refusal rolls back and is a result; a deadlock or any other
    database error is a result by type only; nothing is retried."""
    trace: Trace | None = None
    try:
        if caller_transaction_open():
            return Result("error", PROVIDER_UNAVAILABLE, TRANSACTION_OPEN)
        with transaction.atomic(durable=True):
            cursor = connection.cursor()
            # The transaction's first statement: its backend and its start.
            cursor.execute("SELECT pg_backend_pid(), now()")
            pid, started = cursor.fetchone()
            trace = Trace(int(pid), started)
            if probe is not None and probe.on_begin is not None:
                probe.on_begin(int(pid))
            tx = Tx(cursor, trace, probe)
            try:
                result = body(tx)
            except Refused as refused:
                raise _Rollback(refused, replace(trace, ended_at=clock(tx))) from None
            signal(probe, "before_commit")
            result = replace(result, trace=trace, events=tuple(tx.events))
    except _Rollback as rollback:
        return Result(
            "refused", rollback.refused.code, rollback.refused.reason, trace=rollback.trace
        )
    except Exception as exc:  # noqa: BLE001 - a result the caller judges; never retried
        cause = exc.__cause__
        # The driver's DeadlockDetected, by its SQLSTATE: the API installs no driver.
        if getattr(cause, "sqlstate", None) == DEADLOCK_DETECTED:
            return Result("error", PROVIDER_UNAVAILABLE, "DeadlockDetected", trace=trace)
        if isinstance(exc, IntegrityError):
            return Result(
                "error", STATE_CONFLICT, f"IntegrityError:{type(cause).__name__}", trace=trace
            )
        return Result("error", PROVIDER_UNAVAILABLE, type(exc).__name__, trace=trace)
    return result


def lock_account(tx: Tx, account_id: UUID) -> Any:
    """The actor's account row, ``FOR UPDATE``, before anything else (DM-13 4.1). An absent row
    is a refusal; the actor class has already refused an account that is not ``active``."""
    account = AppAccount.objects.select_for_update().filter(pk=account_id).first()
    if account is None:
        raise Refused(NOT_FOUND, "account_missing")
    signal(tx.probe, "after_first_lock")
    if account.state != "active":
        raise Refused(FORBIDDEN, "account_not_active")
    return account


def lock_account_any_state(tx: Tx, account_id: UUID) -> Any:
    """The photo owner's account row, ``FOR UPDATE``, first, in any account state: only for F05's
    purge and the store's deletion acknowledgment, which only reduce what Glow holds (D10;
    DM-58 item 9), so a photo removed before its owner is suspended or asks for deletion is
    still purged. An absent row is a refusal, as for ``lock_account``; ``glow_chat``'s account
    revocation takes the same row ``FOR UPDATE``, so the two still serialize. Every other step
    keeps ``lock_account`` or ``read_account_shared``."""
    account = AppAccount.objects.select_for_update().filter(pk=account_id).first()
    if account is None:
        raise Refused(NOT_FOUND, "account_missing")
    signal(tx.probe, "after_first_lock")
    return account


def read_account_shared(tx: Tx, account_id: UUID) -> None:
    """A read's consistent view: the account row ``FOR SHARE``, so the read waits for a writer
    of the account in flight (every writer takes it ``FOR UPDATE`` first) and reads its result."""
    tx.cursor.execute(
        "SELECT state FROM glow_persistence_appaccount WHERE id = %s FOR SHARE", [account_id]
    )
    row = tx.cursor.fetchone()
    if row is None:
        raise Refused(NOT_FOUND, "account_missing")
    if row[0] != "active":
        raise Refused(FORBIDDEN, "account_not_active")
