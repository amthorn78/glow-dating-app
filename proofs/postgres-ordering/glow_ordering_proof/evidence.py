"""Where each subject's evidence is in the database (P06.2, D3).

The suite judges both subjects by what PostgreSQL recorded. The reference design writes
proof-log rows in its own transactions; the app's adapter writes none, so its evidence
is its own rows: each ``MessageSubmission``, and the outbox event or consent decision
each writer committed. ``ReferenceEvidence`` keeps P06.DB's reads exactly;
``AdapterEvidence`` reads the adapter's rows, with the harness's call rows for context
(the run tag, the request's session, a transaction's start, and a rolled-back writer's
end, as the adapter read them from the database clock).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from django.db import connection

from glow_ordering_proof import dbreads, oracle
from glow_ordering_proof.interface import Result
from glow_ordering_proof.observe import ADAPTER_CALL_TABLE, ProofLog

if TYPE_CHECKING:
    from glow_ordering_proof.cases import Revocation, World

Interval = tuple[str, datetime, datetime]


class Evidence(Protocol):
    name: str

    def revocation_commit(self, world: World, rev: Revocation) -> datetime | None:
        """The commit time of the revocation the current case applied."""

    def intervals(self, run_tag: str, case_id: str, iteration: int) -> list[Interval]:
        """Each writer's [start, end] in one race's iteration, sign-ins excluded."""

    def evaluate(
        self,
        *,
        run_tag: str | None = None,
        case_id: str | None = None,
        iteration: int | None = None,
    ) -> oracle.OracleReport: ...

    def record_attempt(self, result: Result, **record: Any) -> None:
        """After a stress writer that committed nothing of its own."""


class ReferenceEvidence:
    """P06.DB's reads, unchanged: the proof log the reference design writes."""

    name = "reference"

    def __init__(self, log: ProofLog) -> None:
        self.log = log

    def revocation_commit(self, world: World, rev: Revocation) -> datetime | None:
        return dbreads.log_commit(self.log, rev.kind)

    def intervals(self, run_tag: str, case_id: str, iteration: int) -> list[Interval]:
        from glow_ordering_proof import stress

        return stress._intervals(run_tag, case_id, iteration)

    def evaluate(
        self,
        *,
        run_tag: str | None = None,
        case_id: str | None = None,
        iteration: int | None = None,
    ) -> oracle.OracleReport:
        return oracle.evaluate(run_tag=run_tag, case_id=case_id, iteration=iteration)

    def record_attempt(self, result: Result, **record: Any) -> None:
        self.log.record_attempt(result, **record)


# The adapter's witness of each revocation the cases apply: (table, event type or
# decision state, how the aggregate is found).
_ADAPTER_WITNESS = {
    "block": "contact_revoked",
    "unmatch": "contact_revoked",
    "suspend": "access_revoked",
    "delete": "access_revoked",
    "sign_out": "session_revoked",
    "expire": "session_expired",
    "pause": "profile_paused",
    "restrict": "profile_restricted",
}


def _one(sql: str, params: list[object]) -> Any:
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
    return row[0] if row else None


def adapter_intervals(run_tag: str, case_id: str, iteration: int) -> list[Interval]:
    """Each adapter writer's [start, end] in one race's iteration: its start as the adapter
    read it (``now()`` inside its transaction), and its end, the commit timestamp of the
    row it wrote (its submission, or its first outbox event) or, after a rollback, the
    clock it read just before it. Only this run tag's, race's and iteration's rows; never
    a sign-in (P06.DB-C1, F1; the review's R4)."""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT c.kind, c.started_at,
                   coalesce(c.ended_at, pg_xact_commit_timestamp(s.xmin),
                            pg_xact_commit_timestamp(o.xmin))
            FROM {ADAPTER_CALL_TABLE} c
            LEFT JOIN glow_persistence_messagesubmission s
                   ON s.id = c.submission_id AND c.outcome = 'authorized'
            LEFT JOIN glow_persistence_outboxevent o ON o.id = c.event_ids[1]
            WHERE c.run_tag = %s AND c.case_id = %s AND c.iteration = %s AND c.kind <> 'sign_in'
            """,
            [run_tag, case_id, iteration],
        )
        rows = cursor.fetchall()
    return [(str(k), s, e) for k, s, e in rows if s is not None and e is not None]


class AdapterEvidence:
    """The adapter's own rows (``glow_chat``'s schema ``glow-chat-1``)."""

    name = "adapter"

    def revocation_commit(self, world: World, rev: Revocation) -> datetime | None:
        aggregate = rev.aggregate(world)
        if rev.kind == "withdraw":
            value = _one(
                "SELECT pg_xact_commit_timestamp(xmin) FROM glow_persistence_consentdecision"
                " WHERE account_id = %s AND purpose = %s AND state = 'withdrawn'"
                " ORDER BY version DESC LIMIT 1",
                [aggregate, oracle.ONBOARDING],
            )
        elif rev.kind in ("pause", "restrict"):
            value = _one(
                "SELECT pg_xact_commit_timestamp(o.xmin) FROM glow_persistence_outboxevent o"
                " JOIN glow_persistence_profile p ON p.id = o.aggregate_id"
                " WHERE p.account_id = %s AND o.event_type = %s AND o.schema_version = %s"
                " ORDER BY o.aggregate_version DESC LIMIT 1",
                [aggregate, _ADAPTER_WITNESS[rev.kind], oracle.ADAPTER_SCHEMA],
            )
        else:
            value = _one(
                "SELECT pg_xact_commit_timestamp(xmin) FROM glow_persistence_outboxevent"
                " WHERE aggregate_id = %s AND event_type = %s AND schema_version = %s"
                " ORDER BY aggregate_version DESC LIMIT 1",
                [aggregate, _ADAPTER_WITNESS[rev.kind], oracle.ADAPTER_SCHEMA],
            )
        assert value is None or isinstance(value, datetime)
        return value

    def intervals(self, run_tag: str, case_id: str, iteration: int) -> list[Interval]:
        return adapter_intervals(run_tag, case_id, iteration)

    def evaluate(
        self,
        *,
        run_tag: str | None = None,
        case_id: str | None = None,
        iteration: int | None = None,
    ) -> oracle.OracleReport:
        return oracle.evaluate_adapter(run_tag=run_tag, case_id=case_id, iteration=iteration)

    def record_attempt(self, result: Result, **record: Any) -> None:
        # The adapter subject records every call itself, outside the adapter's
        # transaction; nothing goes into the reference design's proof log.
        return None
