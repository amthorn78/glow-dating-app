"""What the database records: the proof log, lock waits and clocks.

Evidence comes from the database. Every guarantee is judged by rows, commit times and
lock waits PostgreSQL recorded, never by what the harness believes it did.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import connection

from glow_ordering_proof import budget
from glow_ordering_proof.interface import Result

LOG_TABLE = "proof_writer_log"

# Each writer inserts one row in its own transaction, so pg_xact_commit_timestamp(xmin)
# of that row is the writer's commit time (item 6.1). ``xact_start`` defaults to now(),
# the transaction's start. A writer that rolled back has no row of its own; the harness
# then records an attempt row afterwards, with the aborted transaction's start and end
# times as the writer read them from the database clock, for the overlap count (6.3).
LOG_DDL = f"""
CREATE TABLE IF NOT EXISTS {LOG_TABLE} (
    id bigserial PRIMARY KEY,
    kind text NOT NULL,
    outcome text NOT NULL,
    run_tag text NOT NULL,
    variant text NOT NULL,
    case_id text,
    iteration integer,
    submission_id uuid,
    match_id uuid,
    actor_id uuid,
    target_id uuid,
    session_id uuid,
    contact_version bigint,
    epoch bigint,
    xact_start timestamptz NOT NULL DEFAULT now(),
    attempt_start timestamptz,
    ended_at timestamptz,
    note text
)
"""


@dataclass
class LogContext:
    run_tag: str
    variant: str
    case_id: str | None = None
    iteration: int | None = None


class ProofLog:
    """The proof's own log table; writers record through ``record`` inside their
    transaction, and the harness records attempts afterwards."""

    def __init__(self) -> None:
        self.context = LogContext(run_tag="setup", variant="reference")

    def ensure_table(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute(LOG_DDL)

    def record(
        self,
        cursor: Any,
        *,
        kind: str,
        outcome: str,
        submission_id: UUID | None = None,
        match_id: UUID | None = None,
        actor_id: UUID | None = None,
        target_id: UUID | None = None,
        session_id: UUID | None = None,
        contact_version: int | None = None,
        epoch: int | None = None,
        attempt_start: datetime | None = None,
        ended_at: datetime | None = None,
        note: str | None = None,
    ) -> None:
        context = self.context
        cursor.execute(
            f"INSERT INTO {LOG_TABLE} (kind, outcome, run_tag, variant, case_id, iteration,"
            " submission_id, match_id, actor_id, target_id, session_id, contact_version, epoch,"
            " attempt_start, ended_at, note)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [
                kind,
                outcome,
                context.run_tag,
                context.variant,
                context.case_id,
                context.iteration,
                submission_id,
                match_id,
                actor_id,
                target_id,
                session_id,
                contact_version,
                epoch,
                attempt_start,
                ended_at,
                note,
            ],
        )

    def record_attempt(
        self,
        result: Result,
        *,
        kind: str,
        match_id: UUID | None = None,
        actor_id: UUID | None = None,
        target_id: UUID | None = None,
        session_id: UUID | None = None,
        contact_version: int | None = None,
    ) -> None:
        """After a writer that committed nothing of its own: its attempt, with the
        database-clock start and end it read inside its transaction."""
        timing = result.timing
        with connection.cursor() as cursor:
            self.record(
                cursor,
                kind=f"{kind}_attempt",
                outcome=result.label(),
                match_id=match_id,
                actor_id=actor_id,
                target_id=target_id,
                session_id=session_id,
                contact_version=contact_version,
                attempt_start=timing.started_at if timing else None,
                ended_at=timing.ended_at if timing else None,
            )


@dataclass(frozen=True)
class ObservedWait:
    """A second connection observed waiting on a lock, from pg_stat_activity, pg_locks
    and pg_blocking_pids (item 6.2). ``holder_pid`` is the backend that holds the locks;
    ``blocking_pids`` is what ``pg_blocking_pids`` returned for the waiting backend at
    the last poll that found it waiting on a lock (P06.DB-C1, F4)."""

    pid: int
    observed: bool
    wait_event_type: str | None
    wait_event: str | None
    locktype: str | None
    mode: str | None
    polls: int
    elapsed_ms: int
    ended_first: bool = False
    holder_pid: int | None = None
    blocking_pids: tuple[int, ...] = ()

    def summary(self) -> str:
        blockers = ",".join(str(p) for p in self.blocking_pids) or "none"
        if not self.observed:
            text = "no wait observed" + (" (writer finished first)" if self.ended_first else "")
            if self.wait_event_type == "Lock":
                text += (
                    f" (pid {self.pid} waited on a lock, blocked by [{blockers}],"
                    f" not by the holder pid {self.holder_pid})"
                )
            return text
        return (
            f"pid {self.pid} wait_event_type={self.wait_event_type} wait_event={self.wait_event}"
            f" pg_locks not granted: {self.locktype}/{self.mode}"
            f" pg_blocking_pids=[{blockers}] (holder pid {self.holder_pid})"
            f" after {self.polls} polls, {self.elapsed_ms} ms"
        )


def waits_on_holder(
    wait_event_type: str | None, blocking_pids: tuple[int, ...], holder_pid: int
) -> bool:
    """The decision for a forced case: the arriver waits on a lock, and the holder's
    backend is among the backends ``pg_blocking_pids`` names. A wait on any other
    backend is not the forced interleaving and does not count as observed."""
    return wait_event_type == "Lock" and holder_pid in blocking_pids


def observe_lock_wait(
    pid: int,
    *,
    holder_pid: int,
    finished: Callable[[], bool],
    timeout: float = budget.WAIT_OBSERVATION_SECONDS,
) -> ObservedWait:
    """Poll pg_stat_activity for ``pid`` until it waits on a lock that the holder's
    backend (``holder_pid``) holds, it finishes, or the timeout passes. Uses this
    thread's own connection (autocommit)."""
    started = time.monotonic()
    polls = 0
    last: tuple[str | None, str | None, tuple[int, ...]] = (None, None, ())

    def elapsed() -> int:
        return int((time.monotonic() - started) * 1000)

    with connection.cursor() as cursor:
        while True:
            polls += 1
            cursor.execute(
                "SELECT wait_event_type, wait_event, pg_blocking_pids(pid)"
                " FROM pg_stat_activity WHERE pid = %s",
                [pid],
            )
            row = cursor.fetchone()
            if row is not None and row[0] == "Lock":
                blockers = tuple(int(p) for p in (row[2] or ()))
                last = (row[0], row[1], blockers)
                if waits_on_holder(row[0], blockers, holder_pid):
                    cursor.execute(
                        "SELECT locktype, mode FROM pg_locks WHERE pid = %s AND NOT granted",
                        [pid],
                    )
                    lock = cursor.fetchone() or (None, None)
                    return ObservedWait(
                        pid,
                        True,
                        row[0],
                        row[1],
                        lock[0],
                        lock[1],
                        polls,
                        elapsed(),
                        holder_pid=holder_pid,
                        blocking_pids=blockers,
                    )
            ended = finished()
            if ended or time.monotonic() - started > timeout:
                return ObservedWait(
                    pid,
                    False,
                    last[0],
                    last[1],
                    None,
                    None,
                    polls,
                    elapsed(),
                    ended_first=ended,
                    holder_pid=holder_pid,
                    blocking_pids=last[2],
                )
            time.sleep(0.002)


def db_clock() -> datetime:
    with connection.cursor() as cursor:
        cursor.execute("SELECT clock_timestamp()")
        value = cursor.fetchone()[0]
    assert isinstance(value, datetime)
    return value


def xact_start_of(pid: int) -> datetime | None:
    """The start of the transaction a backend is in, from pg_stat_activity."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT xact_start FROM pg_stat_activity WHERE pid = %s", [pid])
        row = cursor.fetchone()
    value = row[0] if row else None
    assert value is None or isinstance(value, datetime)
    return value


def server_facts() -> dict[str, str]:
    """What the run records beside the image digest: version and the settings the proof
    depends on. No connection option is included."""
    facts: dict[str, str] = {}
    with connection.cursor() as cursor:
        for label, statement in (
            ("version", "SELECT version()"),
            ("track_commit_timestamp", "SHOW track_commit_timestamp"),
            ("default_transaction_isolation", "SHOW default_transaction_isolation"),
            ("deadlock_timeout", "SHOW deadlock_timeout"),
            ("current_user", "SELECT current_user"),
            ("current_database", "SELECT current_database()"),
            (
                "superuser",
                "SELECT rolsuper::text FROM pg_roles WHERE rolname = current_user",
            ),
        ):
            cursor.execute(statement)
            facts[label] = str(cursor.fetchone()[0])
    return facts


def migration_ledger() -> list[tuple[str, str, str]]:
    """The applied ledger, from django_migrations itself."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY id")
        return [(str(app), str(name), applied.isoformat()) for app, name, applied in cursor]
