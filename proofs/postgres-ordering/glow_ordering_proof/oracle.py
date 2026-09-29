"""The commit-order oracle (item 6.1).

With ``track_commit_timestamp=on``, ``pg_xact_commit_timestamp(xmin)`` is the commit
time of the transaction that wrote a row. Every writer of the proof leaves one row in
its own transaction (the send its ``MessageSubmission`` and log row; each revocation
its log row), so the oracle compares commit times PostgreSQL recorded, over every row,
never call order or what the harness believes happened.

Rules, for every ``MessageSubmission`` S:

- O1 S has exactly one ``send`` log row, committed in the same transaction.
- O2 no applied contact revocation of S's match committed before or with S, whatever
  its version: a block or unmatch whose log row carries a contact version (the one that
  turned the match ``restricted`` or ``unmatched``). In P06.DB a block or unmatch is
  never undone for its match (an unblock leaves the match ``restricted``, and there is
  no rematch), so this rule must hold for every row the design writes. The rule does
  not compare versions: a send stored at the version the revocation set is still a send
  after the revocation (P06.DB-C1, the exact-head review's F2). O6 stays beside it.
- O3 no sign-out or expiry of S's session committed before or with S.
- O4 no suspension or deletion of either member of S's match committed before or with S.
- O5 S committed before its session's expiry time.
- O6 S's contact version is the match's version as of S's commit: one plus the number
  of contact revocations of the match committed before S.
- O7 S's epoch is the actor's epoch as of S's commit: one plus the number of account
  revocations of the actor committed before S; and the session's own epoch.
- O8 one row per (actor, idempotency key).

Equal commit timestamps count as violations. ``evaluate`` reads the rows from the
database; ``judge`` applies the rules to them, so the rules are testable offline.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import connection

from glow_ordering_proof.observe import LOG_TABLE

CONTACT_KINDS = ("block", "unmatch")
ACCOUNT_KINDS = ("suspend", "delete")
SESSION_KINDS = ("sign_out", "expire")


@dataclass(frozen=True)
class Violation:
    rule: str
    run_tag: str
    case_id: str | None
    iteration: int | None
    submission_id: UUID | None
    detail: str

    def to_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "run_tag": self.run_tag,
            "case_id": self.case_id,
            "iteration": self.iteration,
            "submission_id": str(self.submission_id) if self.submission_id else None,
            "detail": self.detail,
        }


@dataclass
class OracleReport:
    submissions: int
    revocations: int
    violations: list[Violation] = field(default_factory=list)
    by_tag: dict[str, int] = field(default_factory=dict)  # submissions per run_tag

    def violations_for(self, run_tag: str) -> list[Violation]:
        return [v for v in self.violations if v.run_tag == run_tag]

    def to_dict(self) -> dict[str, object]:
        counts = Counter(v.run_tag for v in self.violations)
        return {
            "submissions": self.submissions,
            "revocations": self.revocations,
            "submissions_by_tag": dict(sorted(self.by_tag.items())),
            "violations": [v.to_dict() for v in self.violations],
            "violations_by_tag": dict(sorted(counts.items())),
        }


@dataclass(frozen=True)
class SubmissionRow:
    """A ``MessageSubmission`` with its send log row, as the oracle reads it."""

    id: UUID
    actor: UUID
    contact_version: int
    idempotency_key: str
    match: UUID
    low: UUID
    high: UUID
    committed: datetime | None
    log_rows: int
    log_committed: datetime | None
    session: UUID | None
    epoch: int | None
    run_tag: str
    case_id: str | None
    iteration: int | None


@dataclass(frozen=True)
class RevocationRow:
    """A revocation's log row, as the oracle reads it."""

    kind: str
    match: UUID | None
    actor: UUID | None
    session: UUID | None
    contact_version: int | None
    committed: datetime


def _fetch(cursor: Any, sql: str, params: list[object] | None = None) -> list[tuple[Any, ...]]:
    cursor.execute(sql, params or [])
    return list(cursor.fetchall())


def evaluate(
    *, run_tag: str | None = None, case_id: str | None = None, iteration: int | None = None
) -> OracleReport:
    """Every submission, or those of one run_tag, one case or race (``case_id``) and one
    iteration when given. A race's per-iteration check names its own ``case_id``, since
    races share a run tag and number their iterations from 1 (P06.DB-C1, F1). The
    revocations and sessions are always read whole."""
    where = []
    params: list[object] = []
    if run_tag is not None:
        where.append("l.run_tag = %s")
        params.append(run_tag)
    if case_id is not None:
        where.append("l.case_id = %s")
        params.append(case_id)
    if iteration is not None:
        where.append("l.iteration = %s")
        params.append(iteration)
    tag_filter = (" WHERE " + " AND ".join(where)) if where else ""
    with connection.cursor() as cursor:
        rows = _fetch(
            cursor,
            f"""
            SELECT s.id, s.actor_id, s.contact_version, s.idempotency_key, b.match_id,
                   m.account_low_id, m.account_high_id, pg_xact_commit_timestamp(s.xmin),
                   (SELECT count(*) FROM {LOG_TABLE} x
                     WHERE x.submission_id = s.id AND x.kind = 'send'),
                   pg_xact_commit_timestamp(l.xmin), l.session_id, l.epoch,
                   coalesce(l.run_tag, 'untagged'), l.case_id, l.iteration
            FROM glow_persistence_messagesubmission s
            JOIN glow_persistence_chatbinding b ON b.id = s.binding_id
            JOIN glow_persistence_match m ON m.id = b.match_id
            LEFT JOIN {LOG_TABLE} l ON l.submission_id = s.id AND l.kind = 'send'
            {tag_filter}
            ORDER BY s.id
            """,
            params,
        )
        submissions = [SubmissionRow(*row) for row in rows]
        revocation_rows = _fetch(
            cursor,
            f"""
            SELECT kind, match_id, actor_id, session_id, contact_version,
                   pg_xact_commit_timestamp(xmin)
            FROM {LOG_TABLE}
            WHERE kind IN ('block', 'unmatch', 'suspend', 'delete', 'sign_out', 'expire')
            """,
        )
        revocations = [RevocationRow(*row) for row in revocation_rows if row[5] is not None]
        sessions = {
            row[0]: (row[1], row[2], row[3])
            for row in _fetch(
                cursor,
                "SELECT id, account_id, epoch, expires_at FROM glow_persistence_accountsession",
            )
        }
    return judge(submissions, revocations, sessions)


def judge(
    submissions: list[SubmissionRow],
    revocations: list[RevocationRow],
    sessions: dict[UUID, tuple[UUID, int, datetime]],
) -> OracleReport:
    """The rules O1 to O8 over rows already read; ``sessions`` maps a session id to its
    (account id, epoch, expires_at)."""
    report = OracleReport(len(submissions), len(revocations))
    keys: Counter[tuple[UUID, str]] = Counter()
    for s in submissions:
        report.by_tag[s.run_tag] = report.by_tag.get(s.run_tag, 0) + 1
        keys[(s.actor, s.idempotency_key)] += 1

        def flag(rule: str, detail: str, s: SubmissionRow = s) -> None:
            report.violations.append(
                Violation(rule, s.run_tag, s.case_id, s.iteration, s.id, detail)
            )

        if s.committed is None:
            flag("O1", "no commit timestamp for the submission")
            continue
        if s.log_rows != 1 or s.log_committed != s.committed:
            flag(
                "O1",
                f"{s.log_rows} send log rows; log commit {s.log_committed},"
                f" row commit {s.committed}",
            )
            continue
        contact_before = 0
        for r in revocations:
            if r.kind in CONTACT_KINDS and r.match == s.match and r.contact_version is not None:
                if r.committed < s.committed:
                    contact_before += 1
                if r.committed <= s.committed:
                    flag(
                        "O2",
                        f"{r.kind} v{r.contact_version} committed {r.committed.isoformat()}"
                        f" before/with the send at v{s.contact_version}"
                        f" committed {s.committed.isoformat()}",
                    )
            elif r.kind in SESSION_KINDS and s.session is not None and r.session == s.session:
                if r.committed <= s.committed:
                    flag(
                        "O3",
                        f"{r.kind} of the session committed {r.committed.isoformat()}"
                        f" before/with the send committed {s.committed.isoformat()}",
                    )
            elif r.kind in ACCOUNT_KINDS and r.actor in (s.low, s.high):
                if r.committed <= s.committed:
                    flag(
                        "O4",
                        f"{r.kind} of a member committed {r.committed.isoformat()}"
                        f" before/with the send committed {s.committed.isoformat()}",
                    )
        if s.contact_version != 1 + contact_before:
            flag(
                "O6",
                f"contact version {s.contact_version}, but {contact_before} contact revocations"
                " of the match committed before the send",
            )
        if s.session is None or s.session not in sessions:
            flag("O5", "the send's session is unknown")
        else:
            account, session_epoch, expires_at = sessions[s.session]
            if not s.committed < expires_at:
                flag(
                    "O5",
                    f"committed {s.committed.isoformat()} at or after the session's expiry"
                    f" {expires_at.isoformat()}",
                )
            account_before = sum(
                1
                for r in revocations
                if r.kind in ACCOUNT_KINDS and r.actor == account and r.committed < s.committed
            )
            if s.epoch != 1 + account_before or s.epoch != session_epoch:
                flag(
                    "O7",
                    f"epoch {s.epoch}; session epoch {session_epoch};"
                    f" {account_before} account revocations committed before the send",
                )
    for (actor, key), count in keys.items():
        if count > 1:
            report.violations.append(
                Violation(
                    "O8", "any", None, None, None, f"{count} rows for actor {actor} key {key}"
                )
            )
    return report
