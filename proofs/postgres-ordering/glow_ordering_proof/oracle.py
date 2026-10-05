"""The commit-order oracle (item 6.1), for both subjects (P06.2, D3).

With ``track_commit_timestamp=on``, ``pg_xact_commit_timestamp(xmin)`` is the commit
time of the transaction that wrote a row. The oracle compares commit times PostgreSQL
recorded, over every row, never call order or what the harness believes happened.

Each subject has its own reader, and both feed the same rules (``judge``):

- **The reference design** writes one proof-log row in each writer's transaction (the
  send its ``MessageSubmission`` and log row; each revocation its log row). Its rows are
  the submissions whose binding's provider is ``proof``.
- **The app's adapter** writes no proof row. Its witnesses are its own rows: each
  ``MessageSubmission`` with the ``message_submitted`` event written in the same
  transaction (the same ``xmin``), and the outbox events and consent decisions its
  revocations write (schema ``glow-chat-1``). The harness's call rows add only context:
  the run tag, the request's session and the transaction's start. Its rows are the
  submissions whose binding's provider is the adapter's (``fixture`` in Stage A).

Rules, for every ``MessageSubmission`` S:

- O1 S has exactly one send witness, committed in the same transaction (the reference:
  its send log row; the adapter: its ``message_submitted`` event with S's ``xmin``), and
  exactly one authorization claims it.
- O2 no applied contact revocation of S's match committed before or with S, whatever its
  version (a block or unmatch whose witness carries a contact version). A block or
  unmatch is never undone for its match, so this holds for every row the designs write
  (P06.DB-C1, F2). O6 stays beside it.
- O3 no sign-out or expiry of S's session committed before or with S.
- O4 no suspension or deletion of either member of S's match committed before or with S.
- O5 (narrowed in P06.2 for CX2; the brief's D4) S's session had not expired when S's
  checks ran. The design reads the time after its locks (P06.DB 5.2), so a send that
  checked before the expiry may commit after it. What the database shows is when the
  checks ran at the earliest: after S began, and after every writer that held a row S
  locks and ended while S ran (S waited for it). S is a violation when it committed at or
  after its session's expiry and it began at or after the expiry, or such a writer ended
  at or after the expiry. That keeps the detection of the ``transaction_start_time``
  control, whose send waited past the expiry on the other member's send.
- O6 S's contact version is the match's version as of S's commit: one plus the number of
  contact revocations of the match committed before S.
- O7 S's epoch is the actor's epoch as of S's commit: one plus the number of account
  revocations of the actor committed before S; and the session's own epoch.
- O8 one row per (actor, idempotency key).
- O9 (P06.2, CX1) S's actor is its session's account and a member of S's match.
- O10 (P06.2 D5, the adapter only; the reference design excludes D5) as of S's commit,
  neither member's profile is paused or restricted, and each member's latest onboarding
  consent decision is ``accepted``.

And over the subject's matches, accounts, sessions and profiles:

- O0 (P06.2) every revocation PostgreSQL holds has its witness: a match's contact version
  is one plus its contact witnesses, an account's epoch one plus its account witnesses,
  a session is not ``valid`` exactly when it has an end witness, and a profile's version
  is one plus its profile witnesses, ending in its current state. Without it, a
  revocation applied without a witness would be invisible to O2 to O4.

Equal commit timestamps count as violations. ``judge`` applies the rules to rows
already read, so the rules are testable offline.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import connection

from glow_ordering_proof.observe import ADAPTER_CALL_TABLE, LOG_TABLE, WORLD_TABLE

CONTACT_KINDS = ("block", "unmatch", "contact_revoked")
ACCOUNT_KINDS = ("suspend", "delete", "access_revoked")
SESSION_KINDS = ("sign_out", "expire", "session_revoked", "session_expired")
EPOCH_KINDS = ("session_epoch_bumped",)
PROFILE_OFF = ("profile_paused", "profile_restricted")
PROFILE_KINDS = (*PROFILE_OFF, "profile_resumed")
CONSENT_KINDS = ("consent_accepted", "consent_withdrawn")
PROFILE_STATE = {
    "profile_paused": "paused",
    "profile_restricted": "restricted",
    "profile_resumed": "visible",
}

REFERENCE_PROVIDER = "proof"
ADAPTER_SCHEMA = "glow-chat-1"
ONBOARDING = "onboarding"

Tag = tuple[str, str | None, int | None]
UNTAGGED: Tag = ("untagged", None, None)


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
    census: dict[str, int] = field(default_factory=dict)  # O0's entities, by kind

    def violations_for(self, run_tag: str) -> list[Violation]:
        return [v for v in self.violations if v.run_tag == run_tag]

    def to_dict(self) -> dict[str, object]:
        counts = Counter(v.run_tag for v in self.violations)
        return {
            "submissions": self.submissions,
            "revocations": self.revocations,
            "submissions_by_tag": dict(sorted(self.by_tag.items())),
            "census": dict(sorted(self.census.items())),
            "violations": [v.to_dict() for v in self.violations],
            "violations_by_tag": dict(sorted(counts.items())),
        }


@dataclass(frozen=True)
class SubmissionRow:
    """A ``MessageSubmission`` with its send witness, as the oracle reads it."""

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
    # P06.2: the start of S's transaction (now() inside it), and how many authorizations
    # claim S (the adapter's call rows; the reference's log row is its own claim).
    started: datetime | None = None
    claims: int = 1


@dataclass(frozen=True)
class RevocationRow:
    """A revocation's witness, as the oracle reads it."""

    kind: str
    match: UUID | None
    actor: UUID | None
    session: UUID | None
    contact_version: int | None
    committed: datetime


@dataclass(frozen=True)
class WriterRow:
    """Any writer's transaction (O5): the rows it locked and when it ended (its commit,
    or the clock read just before its rollback)."""

    kind: str
    locks: frozenset[UUID]
    ended: datetime


@dataclass
class Census:
    """The subject's current state (O0) and the run tag of each entity's world."""

    matches: dict[UUID, int] = field(default_factory=dict)  # contact_version
    accounts: dict[UUID, int] = field(default_factory=dict)  # session_epoch
    sessions: dict[UUID, tuple[UUID, str]] = field(default_factory=dict)  # account, state
    profiles: dict[UUID, tuple[int, str]] = field(default_factory=dict)  # account: version, state
    tags: dict[UUID, Tag] = field(default_factory=dict)
    epoch_witnesses: bool = False  # the adapter also writes session_epoch_bumped


def _fetch(cursor: Any, sql: str, params: list[object] | None = None) -> list[tuple[Any, ...]]:
    cursor.execute(sql, params or [])
    return list(cursor.fetchall())


def _locks(kind: str, *ids: UUID | None) -> frozenset[UUID]:
    return frozenset(i for i in ids if i is not None)


def _session_only(kind: str) -> bool:
    return kind.removesuffix("_attempt") in SESSION_KINDS


def _tag_filter(
    prefix: str, run_tag: str | None, case_id: str | None, iteration: int | None
) -> tuple[list[str], list[object]]:
    where: list[str] = []
    params: list[object] = []
    for column, value in (("run_tag", run_tag), ("case_id", case_id), ("iteration", iteration)):
        if value is not None:
            where.append(f"{prefix}.{column} = %s")
            params.append(value)
    return where, params


def _world_tags(cursor: Any, subject: str) -> dict[UUID, Tag]:
    tags: dict[UUID, Tag] = {}
    for match, low, high, run_tag, case_id, iteration in _fetch(
        cursor,
        f"SELECT match_id, low_id, high_id, run_tag, case_id, iteration FROM {WORLD_TABLE}"
        " WHERE subject = %s ORDER BY id",
        [subject],
    ):
        for entity in (match, low, high):
            tags.setdefault(entity, (run_tag, case_id, iteration))
    return tags


def _census(cursor: Any, provider: str, subject: str, *, profiles: bool) -> Census:
    census = Census(epoch_witnesses=profiles)
    for match, version in _fetch(
        cursor,
        "SELECT m.id, m.contact_version FROM glow_persistence_match m"
        " JOIN glow_persistence_chatbinding b ON b.match_id = m.id WHERE b.provider = %s",
        [provider],
    ):
        census.matches[match] = int(version)
    member_sql = (
        "SELECT a.id, a.session_epoch FROM glow_persistence_appaccount a WHERE EXISTS"
        " (SELECT 1 FROM glow_persistence_match m JOIN glow_persistence_chatbinding b"
        " ON b.match_id = m.id WHERE b.provider = %s"
        " AND a.id IN (m.account_low_id, m.account_high_id))"
    )
    for account, epoch in _fetch(cursor, member_sql, [provider]):
        census.accounts[account] = int(epoch)
    for session, account, state in _fetch(
        cursor, "SELECT id, account_id, state FROM glow_persistence_accountsession"
    ):
        if account in census.accounts:
            census.sessions[session] = (account, str(state))
    if profiles:
        for account, version, state in _fetch(
            cursor, "SELECT account_id, version, state FROM glow_persistence_profile"
        ):
            if account in census.accounts:
                census.profiles[account] = (int(version), str(state))
    tags = _world_tags(cursor, subject)
    for session, (account, _) in census.sessions.items():
        if account in tags:
            tags.setdefault(session, tags[account])
    census.tags = tags
    return census


# -- the reference design's reader -------------------------------------------------------


def evaluate(
    *,
    run_tag: str | None = None,
    case_id: str | None = None,
    iteration: int | None = None,
    provider: str = REFERENCE_PROVIDER,
) -> OracleReport:
    """The reference design's rows: every submission of its bindings, or those of one
    run_tag, one case or race (``case_id``) and one iteration when given. A race's
    per-iteration check names its own ``case_id``, since races share a run tag and number
    their iterations from 1 (P06.DB-C1, F1). The revocations and sessions are always read
    whole; O0 runs when no case or iteration is named."""
    where, params = _tag_filter("l", run_tag, case_id, iteration)
    tag_filter = " AND " + " AND ".join(where) if where else ""
    with connection.cursor() as cursor:
        rows = _fetch(
            cursor,
            f"""
            SELECT s.id, s.actor_id, s.contact_version, s.idempotency_key, b.match_id,
                   m.account_low_id, m.account_high_id, pg_xact_commit_timestamp(s.xmin),
                   (SELECT count(*) FROM {LOG_TABLE} x
                     WHERE x.submission_id = s.id AND x.kind = 'send'),
                   pg_xact_commit_timestamp(l.xmin), l.session_id, l.epoch,
                   coalesce(l.run_tag, 'untagged'), l.case_id, l.iteration, l.xact_start
            FROM glow_persistence_messagesubmission s
            JOIN glow_persistence_chatbinding b ON b.id = s.binding_id
            JOIN glow_persistence_match m ON m.id = b.match_id
            LEFT JOIN {LOG_TABLE} l ON l.submission_id = s.id AND l.kind = 'send'
            WHERE b.provider = %s{tag_filter}
            ORDER BY s.id
            """,
            [provider, *params],
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
        writers: list[WriterRow] = []
        for kind, match, actor, target, session, low, high, ended in _fetch(
            cursor,
            f"""
            SELECT l.kind, l.match_id, l.actor_id, l.target_id, l.session_id,
                   m.account_low_id, m.account_high_id,
                   coalesce(l.ended_at, pg_xact_commit_timestamp(l.xmin))
            FROM {LOG_TABLE} l LEFT JOIN glow_persistence_match m ON m.id = l.match_id
            """,
        ):
            if ended is None:
                continue
            locks = (
                _locks(kind, session)
                if _session_only(kind)
                else _locks(kind, match, actor, target, session, low, high)
            )
            writers.append(WriterRow(str(kind), locks, ended))
        census = None
        if case_id is None and iteration is None:
            census = _census(cursor, provider, "reference", profiles=False)
    return judge(submissions, revocations, sessions, writers=writers, census=census, scope=run_tag)


# -- the app's adapter's reader ---------------------------------------------------------


def evaluate_adapter(
    *,
    run_tag: str | None = None,
    case_id: str | None = None,
    iteration: int | None = None,
    provider: str = "fixture",
    schema: str = ADAPTER_SCHEMA,
) -> OracleReport:
    """The adapter's rows, judged by the same rules with D5's O10. Its submissions are
    those of its bindings; the run tag, the session and the start come from the
    authorization's call row, and a submission no call row claims is ``untagged``."""
    where, params = _tag_filter("c", run_tag, case_id, iteration)
    tag_filter = " AND " + " AND ".join(where) if where else ""
    with connection.cursor() as cursor:
        rows = _fetch(
            cursor,
            f"""
            SELECT s.id, s.actor_id, s.contact_version, s.idempotency_key, b.match_id,
                   m.account_low_id, m.account_high_id, pg_xact_commit_timestamp(s.xmin),
                   (SELECT count(*) FROM glow_persistence_outboxevent o
                     WHERE o.schema_version = %s AND o.event_type = 'message_submitted'
                       AND o.payload_ref = s.id),
                   (SELECT pg_xact_commit_timestamp(o.xmin) FROM glow_persistence_outboxevent o
                     WHERE o.schema_version = %s AND o.event_type = 'message_submitted'
                       AND o.payload_ref = s.id AND o.xmin = s.xmin LIMIT 1),
                   c.session_id, sess.epoch, coalesce(c.run_tag, 'untagged'), c.case_id,
                   c.iteration, c.started_at,
                   (SELECT count(*) FROM {ADAPTER_CALL_TABLE} k
                     WHERE k.submission_id = s.id AND k.outcome = 'authorized')
            FROM glow_persistence_messagesubmission s
            JOIN glow_persistence_chatbinding b ON b.id = s.binding_id
            JOIN glow_persistence_match m ON m.id = b.match_id
            LEFT JOIN LATERAL (
                SELECT * FROM {ADAPTER_CALL_TABLE} k
                WHERE k.submission_id = s.id AND k.outcome = 'authorized'
                ORDER BY k.id LIMIT 1
            ) c ON true
            LEFT JOIN glow_persistence_accountsession sess ON sess.id = c.session_id
            WHERE b.provider = %s{tag_filter}
            ORDER BY s.id
            """,
            [schema, schema, provider, *params],
        )
        submissions = [SubmissionRow(*row) for row in rows]
        revocations: list[RevocationRow] = []
        writers: list[WriterRow] = []
        for kind, aggregate, version, committed, low, high, b_actor, b_target, p_account in _fetch(
            cursor,
            """
            SELECT o.event_type, o.aggregate_id, o.aggregate_version,
                   pg_xact_commit_timestamp(o.xmin), m.account_low_id, m.account_high_id,
                   bl.actor_id, bl.target_id, p.account_id
            FROM glow_persistence_outboxevent o
            LEFT JOIN glow_persistence_match m ON m.id = o.aggregate_id
            LEFT JOIN glow_persistence_block bl ON bl.id = o.aggregate_id
            LEFT JOIN glow_persistence_profile p ON p.id = o.aggregate_id
            WHERE o.schema_version = %s
            """,
            [schema],
        ):
            if committed is None:
                continue
            kind = str(kind)
            if kind == "contact_revoked":
                revocations.append(RevocationRow(kind, aggregate, None, None, version, committed))
                writers.append(WriterRow(kind, _locks(kind, aggregate, low, high), committed))
            elif kind in ("access_revoked", "session_epoch_bumped"):
                revocations.append(RevocationRow(kind, None, aggregate, None, None, committed))
                writers.append(WriterRow(kind, _locks(kind, aggregate), committed))
            elif kind in ("session_revoked", "session_expired"):
                revocations.append(RevocationRow(kind, None, None, aggregate, None, committed))
                writers.append(WriterRow(kind, _locks(kind, aggregate), committed))
            elif kind in PROFILE_KINDS:
                revocations.append(RevocationRow(kind, None, p_account, None, version, committed))
                writers.append(WriterRow(kind, _locks(kind, p_account), committed))
            elif kind == "match_activated":
                writers.append(WriterRow(kind, _locks(kind, aggregate, low, high), committed))
            elif kind == "block_changed":
                writers.append(WriterRow(kind, _locks(kind, b_actor, b_target), committed))
        for account, state, version, committed in _fetch(
            cursor,
            "SELECT account_id, state, version, pg_xact_commit_timestamp(xmin)"
            " FROM glow_persistence_consentdecision WHERE purpose = %s",
            [ONBOARDING],
        ):
            if committed is None:
                continue
            kind = f"consent_{state}"
            revocations.append(RevocationRow(kind, None, account, None, version, committed))
            writers.append(WriterRow(kind, _locks(kind, account), committed))
        for s in submissions:
            if s.committed is not None:
                locks = _locks("send", s.match, s.low, s.high, s.session)
                writers.append(WriterRow("send", locks, s.committed))
        for kind, match, actor, target, session, low, high, ended in _fetch(
            cursor,
            f"""
            SELECT c.kind, c.match_id, c.actor_id, c.target_id, c.session_id,
                   m.account_low_id, m.account_high_id, c.ended_at
            FROM {ADAPTER_CALL_TABLE} c
            LEFT JOIN glow_persistence_match m ON m.id = c.match_id
            WHERE c.ended_at IS NOT NULL
            """,
        ):
            locks = (
                _locks(kind, session)
                if _session_only(kind)
                else _locks(kind, match, actor, target, session, low, high)
            )
            writers.append(WriterRow(str(kind), locks, ended))
        sessions = {
            row[0]: (row[1], row[2], row[3])
            for row in _fetch(
                cursor,
                "SELECT id, account_id, epoch, expires_at FROM glow_persistence_accountsession",
            )
        }
        census = None
        if case_id is None and iteration is None:
            census = _census(cursor, provider, "adapter", profiles=True)
    return judge(
        submissions,
        revocations,
        sessions,
        writers=writers,
        census=census,
        d5=True,
        scope=run_tag,
    )


# -- the rules ----------------------------------------------------------------------------


def _o5(s: SubmissionRow, expires_at: datetime, writers: Iterable[WriterRow]) -> str | None:
    """Why S's checks must have run at or after its session's expiry, or None."""
    if s.committed is None or s.committed < expires_at:
        return None
    if s.started is not None and s.started >= expires_at:
        return (
            f"began {s.started.isoformat()} at or after the session's expiry"
            f" {expires_at.isoformat()}"
        )
    mine = _locks("send", s.match, s.low, s.high, s.session)
    for w in writers:
        if not (w.locks & mine) or not (expires_at <= w.ended < s.committed):
            continue
        if s.started is not None and w.ended <= s.started:
            continue
        return (
            f"waited on a {w.kind} that ended {w.ended.isoformat()}, at or after the session's"
            f" expiry {expires_at.isoformat()}; committed {s.committed.isoformat()}"
        )
    return None


def _o10(s: SubmissionRow, index: _Index) -> list[str]:
    """D5, as of S's commit: both profiles visible, both latest consents accepted."""
    assert s.committed is not None
    found: list[str] = []
    for member in (s.low, s.high):
        profile = index.profile.get(member, [])
        before = [r for r in profile if r.committed < s.committed]
        if before and before[-1].kind in PROFILE_OFF:
            found.append(f"a member's profile was {PROFILE_STATE[before[-1].kind]} before the send")
        if any(r.committed == s.committed and r.kind in PROFILE_OFF for r in profile):
            found.append("a member's profile changed with the send")
        consent = index.consent.get(member, [])
        decided = [r for r in consent if r.committed < s.committed]
        if not decided or decided[-1].kind != "consent_accepted":
            found.append("a member's latest onboarding consent was not accepted before the send")
        if any(r.committed == s.committed and r.kind == "consent_withdrawn" for r in consent):
            found.append("a member's consent was withdrawn with the send")
    return found


@dataclass
class _Index:
    """The revocations by the key each rule looks them up by, in commit order."""

    contact: dict[UUID, list[RevocationRow]] = field(default_factory=dict)
    session: dict[UUID, list[RevocationRow]] = field(default_factory=dict)
    account: dict[UUID, list[RevocationRow]] = field(default_factory=dict)
    profile: dict[UUID, list[RevocationRow]] = field(default_factory=dict)
    consent: dict[UUID, list[RevocationRow]] = field(default_factory=dict)

    @classmethod
    def of(cls, revocations: list[RevocationRow]) -> _Index:
        index = cls()
        for r in sorted(revocations, key=lambda r: r.committed):
            if r.kind in CONTACT_KINDS and r.match is not None and r.contact_version is not None:
                index.contact.setdefault(r.match, []).append(r)
            elif r.kind in SESSION_KINDS and r.session is not None:
                index.session.setdefault(r.session, []).append(r)
            elif r.kind in ACCOUNT_KINDS and r.actor is not None:
                index.account.setdefault(r.actor, []).append(r)
            elif r.kind in PROFILE_KINDS and r.actor is not None:
                index.profile.setdefault(r.actor, []).append(r)
            elif r.kind in CONSENT_KINDS and r.actor is not None:
                index.consent.setdefault(r.actor, []).append(r)
        return index


def _o0(census: Census, revocations: list[RevocationRow]) -> list[tuple[UUID, str]]:
    """Every revocation PostgreSQL holds has its witness."""
    found: list[tuple[UUID, str]] = []
    contact: dict[UUID, list[int]] = {}
    account: Counter[UUID] = Counter()
    epoch: Counter[UUID] = Counter()
    ended: Counter[UUID] = Counter()
    profile: dict[UUID, list[RevocationRow]] = {}
    for r in revocations:
        if r.kind in CONTACT_KINDS and r.match is not None and r.contact_version is not None:
            contact.setdefault(r.match, []).append(r.contact_version)
        elif r.kind in ACCOUNT_KINDS and r.actor is not None:
            account[r.actor] += 1
        elif r.kind in EPOCH_KINDS and r.actor is not None:
            epoch[r.actor] += 1
        elif r.kind in SESSION_KINDS and r.session is not None:
            ended[r.session] += 1
        elif r.kind in PROFILE_KINDS and r.actor is not None:
            profile.setdefault(r.actor, []).append(r)
    for match, version in census.matches.items():
        versions = sorted(contact.get(match, []))
        if versions != list(range(2, version + 1)):
            found.append((match, f"contact version {version}, witnessed versions {versions}"))
    for acc, session_epoch in census.accounts.items():
        if account[acc] != session_epoch - 1:
            found.append((acc, f"epoch {session_epoch}, {account[acc]} account witnesses"))
        if census.epoch_witnesses and epoch[acc] != session_epoch - 1:
            found.append((acc, f"epoch {session_epoch}, {epoch[acc]} token-revocation witnesses"))
    for session, (_, state) in census.sessions.items():
        wanted = 0 if state == "valid" else 1
        if ended[session] != wanted:
            found.append((session, f"session {state}, {ended[session]} end witnesses"))
    for acc, (version, state) in census.profiles.items():
        rows = sorted(profile.get(acc, []), key=lambda r: r.committed)
        last = PROFILE_STATE[rows[-1].kind] if rows else "visible"
        if len(rows) != version - 1 or last != state:
            found.append((acc, f"profile v{version} {state}, {len(rows)} witnesses ending {last}"))
    return found


def judge(
    submissions: list[SubmissionRow],
    revocations: list[RevocationRow],
    sessions: dict[UUID, tuple[UUID, int, datetime]],
    *,
    writers: Iterable[WriterRow] = (),
    census: Census | None = None,
    d5: bool = False,
    scope: str | None = None,
) -> OracleReport:
    """The rules over rows already read; ``sessions`` maps a session id to its (account
    id, epoch, expires_at). O0 runs when a ``census`` is given; its violations are kept
    for the run tag in ``scope`` only, when one is given."""
    writers = list(writers)
    index = _Index.of(revocations)
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
                f"{s.log_rows} send witnesses; witness commit {s.log_committed},"
                f" row commit {s.committed}",
            )
            continue
        if s.claims != 1:
            flag("O1", f"{s.claims} authorizations claim the submission")
        contact_before = 0
        for r in index.contact.get(s.match, []):
            if r.committed < s.committed:
                contact_before += 1
            if r.committed <= s.committed:
                flag(
                    "O2",
                    f"{r.kind} v{r.contact_version} committed {r.committed.isoformat()}"
                    f" before/with the send at v{s.contact_version}"
                    f" committed {s.committed.isoformat()}",
                )
        for r in index.session.get(s.session, []) if s.session is not None else []:
            if r.committed <= s.committed:
                flag(
                    "O3",
                    f"{r.kind} of the session committed {r.committed.isoformat()}"
                    f" before/with the send committed {s.committed.isoformat()}",
                )
        for member in (s.low, s.high):
            for r in index.account.get(member, []):
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
            late = _o5(s, expires_at, writers)
            if late is not None:
                flag("O5", late)
            account_before = sum(
                1 for r in index.account.get(account, []) if r.committed < s.committed
            )
            if s.epoch != 1 + account_before or s.epoch != session_epoch:
                flag(
                    "O7",
                    f"epoch {s.epoch}; session epoch {session_epoch};"
                    f" {account_before} account revocations committed before the send",
                )
            if s.actor != account:
                flag("O9", "the submission's actor is not its session's account")
        if s.actor not in (s.low, s.high):
            flag("O9", "the submission's actor is not a member of its match")
        if d5:
            for detail in _o10(s, index):
                flag("O10", detail)
    for (actor, key), count in keys.items():
        if count > 1:
            report.violations.append(
                Violation(
                    "O8", "any", None, None, None, f"{count} rows for actor {actor} key {key}"
                )
            )
    if census is not None:
        report.census = {
            "matches": len(census.matches),
            "accounts": len(census.accounts),
            "sessions": len(census.sessions),
            "profiles": len(census.profiles),
        }
        for entity, detail in _o0(census, revocations):
            tag = census.tags.get(entity, UNTAGGED)
            if scope is None or tag[0] == scope:
                report.violations.append(Violation("O0", tag[0], tag[1], tag[2], None, detail))
    return report
