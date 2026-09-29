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
    """A second connection observed waiting on a lock, from pg_stat_activity and
    pg_locks (item 6.2)."""

    pid: int
    observed: bool
    wait_event_type: str | None
    wait_event: str | None
    locktype: str | None
    mode: str | None
    polls: int
    elapsed_ms: int
    ended_first: bool = False

    def summary(self) -> str:
        if not self.observed:
            return "no wait observed" + (" (writer finished first)" if self.ended_first else "")
        return (
            f"pid {self.pid} wait_event_type={self.wait_event_type} wait_event={self.wait_event}"
            f" pg_locks not granted: {self.locktype}/{self.mode} after {self.polls} polls,"
            f" {self.elapsed_ms} ms"
        )


def observe_lock_wait(
    pid: int,
    *,
    finished: Callable[[], bool],
    timeout: float = budget.WAIT_OBSERVATION_SECONDS,
) -> ObservedWait:
    """Poll pg_stat_activity for ``pid`` until its wait_event_type is 'Lock', it finishes,
    or the timeout passes. Uses this thread's own connection (autocommit)."""
    started = time.monotonic()
    polls = 0
    with connection.cursor() as cursor:
        while True:
            polls += 1
            cursor.execute(
                "SELECT wait_event_type, wait_event FROM pg_stat_activity WHERE pid = %s", [pid]
            )
            row = cursor.fetchone()
            if row is not None and row[0] == "Lock":
                cursor.execute(
                    "SELECT locktype, mode FROM pg_locks WHERE pid = %s AND NOT granted", [pid]
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
                    int((time.monotonic() - started) * 1000),
                )
            if finished():
                return ObservedWait(
                    pid,
                    False,
                    None,
                    None,
                    None,
                    None,
                    polls,
                    int((time.monotonic() - started) * 1000),
                    ended_first=True,
                )
            if time.monotonic() - started > timeout:
                return ObservedWait(
                    pid,
                    False,
                    None,
                    None,
                    None,
                    None,
                    polls,
                    int((time.monotonic() - started) * 1000),
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
