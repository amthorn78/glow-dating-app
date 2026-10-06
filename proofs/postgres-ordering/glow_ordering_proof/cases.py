"""The race suite: forced interleavings on two real connections, and the named cases.

Every case is judged by what the database recorded: rows, commit timestamps and lock
waits. A forced "while it holds the locks" case passes only if the second connection
was observed waiting (item 6.2). The suite drives the ``OrderingSubject`` interface
only, so P06.2 runs it against the app's adapter too (D3): each subject's evidence is
read where that subject writes it (``evidence``).

P06.2 adds CX2's boundary (``named.session_expires_after_check``, both subjects) and
D5's three revocations of contact (a paused or restricted profile, a withdrawn
onboarding consent), each with its four interleavings, for the adapter only: the
reference design excludes them (P06.DB 5.6). Stage B1 adds, for the adapter only, the
match activation against the D5 writers both ways (CX5; DM-15 6.1), the token grant
against the epoch bump and a sign-out with the app's clock skewed ahead (F1; DM-14
item 3), and the F2 and F5 nits (``B1_CASES``).
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Collection, Iterator
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import partial
from typing import cast
from uuid import UUID

from glow_ordering_proof import budget
from glow_ordering_proof.concurrency import Barrier, Hold, PidSlot, Worker
from glow_ordering_proof.dbreads import (
    account_row,
    activation_commit,
    block_state,
    consent_row,
    deletion_recorded,
    event_times,
    identity_row,
    match_between,
    match_row,
    outbox_count,
    profile_row,
    session_row,
    submission_commit,
    submissions_of,
)
from glow_ordering_proof.evidence import Evidence
from glow_ordering_proof.interface import (
    ContactStateSubject,
    FixtureFactory,
    Hooks,
    OrderingSubject,
    Result,
    SendRequest,
)
from glow_ordering_proof.observe import (
    ObservedWait,
    ProofLog,
    db_clock,
    observe_lock_wait,
    xact_start_of,
)

SESSION_TTL = 300.0
Writer = Callable[[Hooks | None], Result]


@dataclass
class Context:
    subject: OrderingSubject
    fixtures: FixtureFactory
    log: ProofLog
    workers: list[Worker]
    evidence: Evidence
    # The subject's name in the world table, and whether it carries D5's writers.
    name: str = "reference"
    d5: bool = False

    @property
    def state_subject(self) -> ContactStateSubject:
        if not self.d5:
            raise RuntimeError("this subject carries no D5 writer")
        subject = self.subject
        assert isinstance(subject, ContactStateSubject)
        return subject


@dataclass
class World:
    """Two accounts, their match with its binding, and one valid session each."""

    low: UUID
    high: UUID
    match: UUID
    session_low: UUID
    session_high: UUID

    def session_of(self, account: UUID) -> UUID:
        return self.session_low if account == self.low else self.session_high

    def other(self, account: UUID) -> UUID:
        return self.high if account == self.low else self.low


def make_world(ctx: Context, *, ttl: float = SESSION_TTL) -> World:
    first, second = ctx.fixtures.create_account(), ctx.fixtures.create_account()
    low, high = sorted((first, second))
    match = ctx.fixtures.create_match(low, high)
    ctx.log.record_world(ctx.name, match, low, high)
    sessions = []
    for account in (low, high):
        signed = ctx.subject.sign_in(account, ttl_seconds=ttl)
        if signed.outcome != "applied" or signed.session_id is None:
            raise RuntimeError(f"fixture sign-in failed: {signed.label()}")
        sessions.append(signed.session_id)
    return World(low, high, match, sessions[0], sessions[1])


def send_request(
    world: World,
    *,
    sender: UUID | None = None,
    session: UUID | None = None,
    contact_version: int = 1,
    key: str | None = None,
    text: str = "proof message",
) -> SendRequest:
    sender = world.low if sender is None else sender
    return SendRequest(
        session_id=session or world.session_of(sender),
        match_id=world.match,
        contact_version=contact_version,
        idempotency_key=key or f"key-{uuid.uuid4().hex}",
        text=text,
    )


# -- judging ------------------------------------------------------------------------

# What kind of failure a case recorded, so a negative control is judged by the signal
# its broken switch must produce and not by any failure (P06.DB-C1, F3).
WAIT_NOT_OBSERVED = "wait_not_observed"  # the arriver was not seen waiting on the holder
COMMIT_AFTER_REVOCATION = "commit_after_revocation"  # the send committed after it
REFUSAL_MISSING = "refusal_missing"  # a send expected refused was authorized or replayed
DEADLOCK = "deadlock"  # a writer's transaction was a deadlock victim
DATABASE_ERROR = "database_error"  # a writer returned another database error
HARNESS_ERROR = "harness_error"  # the case raised: its judgement is incomplete
OTHER = "other"  # any other expectation that did not hold
CASE_SIGNALS = frozenset(
    {
        WAIT_NOT_OBSERVED,
        COMMIT_AFTER_REVOCATION,
        REFUSAL_MISSING,
        DEADLOCK,
        DATABASE_ERROR,
        HARNESS_ERROR,
        OTHER,
    }
)


@dataclass
class CaseResult:
    case_id: str
    guarantee: str
    title: str
    passed: bool
    waits: list[ObservedWait] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    signals: frozenset[str] = frozenset()

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "guarantee": self.guarantee,
            "title": self.title,
            "passed": self.passed,
            "waits": [w.summary() for w in self.waits],
            "notes": self.notes,
            "failures": self.failures,
            "signals": sorted(self.signals),
        }


class Judge:
    def __init__(self, case: Case) -> None:
        self.case = case
        self.failures: list[str] = []
        self.notes: list[str] = []
        self.waits: list[ObservedWait] = []
        self.signals: set[str] = set()

    def fail(self, message: str, signal: str = OTHER) -> None:
        self.failures.append(message)
        self.signals.add(signal)

    def expect(self, ok: bool, message: str, *, signal: str = OTHER) -> bool:
        if not ok:
            self.fail(message, signal)
        return ok

    def outcome(
        self, result: Result, what: str, *outcomes: str, reasons: Collection[str] = ()
    ) -> bool:
        ok = result.outcome in outcomes and (not reasons or result.reason in reasons)
        if not ok:
            wanted = "/".join(outcomes) + (f" ({'|'.join(sorted(reasons))})" if reasons else "")
            self.fail(
                f"{what}: {result.label()}, expected {wanted}", outcome_signal(result, outcomes)
            )
        else:
            self.notes.append(f"{what}: {result.label()}")
        return ok

    def wait(self, observed: ObservedWait, *, required: bool = True) -> None:
        self.waits.append(observed)
        if required and not observed.observed:
            self.fail(
                "the second connection was not observed waiting on the holder's lock",
                WAIT_NOT_OBSERVED,
            )

    def note(self, message: str) -> None:
        self.notes.append(message)

    def finish(self) -> CaseResult:
        return CaseResult(
            self.case.id,
            self.case.guarantee,
            self.case.title,
            not self.failures,
            self.waits,
            self.notes,
            self.failures,
            frozenset(self.signals),
        )


def outcome_signal(result: Result, expected: Collection[str]) -> str:
    """The signal of an unexpected outcome."""
    if result.outcome == "deadlock":
        return DEADLOCK
    if result.outcome == "error":
        return DATABASE_ERROR
    if "refused" in expected and result.outcome in ("authorized", "replayed"):
        return REFUSAL_MISSING
    return OTHER


@dataclass(frozen=True)
class Case:
    id: str
    guarantee: str
    title: str
    run: Callable[[Context, Judge], None]


def run_case(ctx: Context, case: Case) -> CaseResult:
    ctx.log.context.case_id = case.id
    judge = Judge(case)
    try:
        case.run(ctx, judge)
    except Exception as exc:  # noqa: BLE001 - a harness error fails the case visibly
        judge.fail(f"harness error: {type(exc).__name__}: {exc}", HARNESS_ERROR)
    finally:
        ctx.log.context.case_id = None
    return judge.finish()


# -- forced interleavings --------------------------------------------------------------


def _wait_held(hold: Hold, future: Future[Result]) -> bool:
    deadline = budget.HOLD_SECONDS
    step = 0.01
    waited = 0.0
    while waited < deadline:
        if hold.wait_held(step):
            return True
        if future.done():
            return False
        waited += step
    return False


def forced(
    ctx: Context,
    judge: Judge,
    holder: Writer,
    arriver: Writer,
    *,
    hold_at: str = "after_locks",
    before_release: Callable[[int], None] | None = None,
    wait_required: bool = True,
) -> tuple[Result, Result, ObservedWait]:
    """The holder runs on one connection to its hold point; the arriver starts on a
    second connection and is observed waiting on the holder's backend (pg_stat_activity,
    pg_locks, pg_blocking_pids); then the holder is released and both finish."""
    hold = Hold()
    pid = PidSlot()
    holder_pid = PidSlot()
    hooks_holder = (
        Hooks(on_begin=holder_pid.set, after_first_lock=hold.point)
        if hold_at == "after_first_lock"
        else Hooks(on_begin=holder_pid.set, after_locks=hold.point)
    )
    first = ctx.workers[0].submit(lambda: holder(hooks_holder))
    if not _wait_held(hold, first):
        hold.release.set()
        result = first.result(timeout=budget.HOLD_SECONDS)
        judge.fail(f"the holder finished before its hold point: {result.label()}")
        return (
            result,
            Result("error", "arriver_not_started"),
            ObservedWait(0, False, None, None, None, None, 0, 0),
        )
    second = ctx.workers[1].submit(lambda: arriver(Hooks(on_begin=pid.set)))
    observed = observe_lock_wait(pid.wait(), holder_pid=holder_pid.wait(), finished=second.done)
    judge.wait(observed, required=wait_required)
    if before_release is not None and observed.pid:
        before_release(observed.pid)
    hold.release.set()
    r1 = first.result(timeout=budget.HOLD_SECONDS)
    r2 = second.result(timeout=budget.HOLD_SECONDS)
    return r1, r2, observed


# -- the revocations of contact --------------------------------------------------------


@dataclass(frozen=True)
class Revocation:
    id: str
    title: str
    kind: str  # the proof log kind its transaction writes
    act: Callable[[World, OrderingSubject, Hooks | None], Result]
    refusals: frozenset[str]
    effect: Callable[[World, Judge], None]
    # What it revokes: the match, an account or the session (the adapter's witness).
    aggregate: Callable[[World], UUID] = lambda world: world.match


def _block(by: str) -> Revocation:
    def act(world: World, subject: OrderingSubject, hooks: Hooks | None) -> Result:
        actor = world.low if by == "low" else world.high
        return subject.block(actor, world.other(actor), hooks=hooks)

    def effect(world: World, judge: Judge) -> None:
        actor = world.low if by == "low" else world.high
        judge.expect(match_row(world.match) == ("restricted", 2), "match not restricted at v2")
        judge.expect(block_state(actor, world.other(actor)) == "active", "block row not active")
        judge.expect(account_row(actor)[2] == 2, "blocks_version not bumped")
        judge.expect(outbox_count("contact_revoked", world.match) == 1, "no contact_revoked event")

    return Revocation(
        f"block_by_{by}",
        f"a block by the {by} account (the sender is the low account)",
        "block",
        act,
        frozenset({"match_not_active", "blocked"}),
        effect,
    )


def _unmatch(by: str) -> Revocation:
    def act(world: World, subject: OrderingSubject, hooks: Hooks | None) -> Result:
        actor = world.low if by == "low" else world.high
        return subject.unmatch(actor, world.match, hooks=hooks)

    def effect(world: World, judge: Judge) -> None:
        judge.expect(match_row(world.match) == ("unmatched", 2), "match not unmatched at v2")
        judge.expect(outbox_count("contact_revoked", world.match) == 1, "no contact_revoked event")

    return Revocation(
        f"unmatch_by_{by}",
        f"an unmatch by the {by} account",
        "unmatch",
        act,
        frozenset({"match_not_active"}),
        effect,
    )


def _account_wide(op: str, which: str) -> Revocation:
    def act(world: World, subject: OrderingSubject, hooks: Hooks | None) -> Result:
        account = world.low if which == "low" else world.high
        return (subject.suspend if op == "suspend" else subject.delete)(account, hooks=hooks)

    def effect(world: World, judge: Judge) -> None:
        account = world.low if which == "low" else world.high
        state, epoch, _ = account_row(account)
        wanted = "suspended" if op == "suspend" else "deletion_pending"
        judge.expect(state == wanted, f"account state {state}, expected {wanted}")
        judge.expect(epoch == 2, f"session_epoch {epoch}, expected 2")
        judge.expect(outbox_count("access_revoked", account) == 1, "no access_revoked event")
        if op == "delete":
            job, tombstone, row_exists = deletion_recorded(account)
            judge.expect(job, "no DeletionJob with access revoked")
            judge.expect(tombstone, "no tombstone")
            judge.expect(row_exists, "account row hard-deleted")

    who = "the sender's account" if which == "low" else "the other member's account"
    return Revocation(
        f"{op}_{which}",
        f"{'a suspension' if op == 'suspend' else 'a deletion'} of {who}",
        op,
        act,
        frozenset({"account_not_active"}),
        effect,
        lambda world: world.low if which == "low" else world.high,
    )


def _session_end(op: str) -> Revocation:
    def act(world: World, subject: OrderingSubject, hooks: Hooks | None) -> Result:
        method = subject.sign_out if op == "sign_out" else subject.expire_session
        return method(world.session_low, hooks=hooks)

    def effect(world: World, judge: Judge) -> None:
        state = session_row(world.session_low)[0]
        wanted = "revoked" if op == "sign_out" else "expired"
        judge.expect(state == wanted, f"session state {state}, expected {wanted}")
        event = "session_revoked" if op == "sign_out" else "session_expired"
        judge.expect(outbox_count(event, world.session_low) == 1, f"no {event} event")

    return Revocation(
        f"{op}_sender",
        "a sign-out of the sending session"
        if op == "sign_out"
        else "an administrative expiry of the sending session",
        op if op == "sign_out" else "expire",
        act,
        frozenset({"session_not_valid"}),
        effect,
        lambda world: world.session_low,
    )


REVOCATIONS: tuple[Revocation, ...] = (
    _block("low"),
    _block("high"),
    _unmatch("low"),
    _unmatch("high"),
    _account_wide("suspend", "low"),
    _account_wide("suspend", "high"),
    _account_wide("delete", "low"),
    _account_wide("delete", "high"),
    _session_end("sign_out"),
    _session_end("expire"),
)


def _profile(op: str, which: str) -> Revocation:
    """P06.2 D5: a pause or a restriction of a member's profile."""

    def account_of(world: World) -> UUID:
        return world.low if which == "low" else world.high

    def act(world: World, subject: OrderingSubject, hooks: Hooks | None) -> Result:
        state = cast(ContactStateSubject, subject)
        writer = state.pause_profile if op == "pause" else state.restrict_profile
        return writer(account_of(world), hooks=hooks)

    def effect(world: World, judge: Judge) -> None:
        wanted = "paused" if op == "pause" else "restricted"
        state, version, events = profile_row(account_of(world), f"profile_{wanted}")
        judge.expect((state, version) == (wanted, 2), f"profile {state} v{version}")
        judge.expect(events == 1, f"{events} profile_{wanted} events")

    who = "the sender's" if which == "low" else "the other member's"
    return Revocation(
        f"{op}_{which}",
        f"{'a pause' if op == 'pause' else 'a restriction'} of {who} profile",
        op,
        act,
        frozenset({"profile_unavailable"}),
        effect,
        account_of,
    )


def _consent(which: str) -> Revocation:
    """P06.2 D5: a withdrawal of a member's onboarding consent."""

    def account_of(world: World) -> UUID:
        return world.low if which == "low" else world.high

    def act(world: World, subject: OrderingSubject, hooks: Hooks | None) -> Result:
        return cast(ContactStateSubject, subject).withdraw_consent(account_of(world), hooks=hooks)

    def effect(world: World, judge: Judge) -> None:
        latest = consent_row(account_of(world))
        judge.expect(latest == ("withdrawn", 2), f"latest consent {latest}")

    who = "the sender's" if which == "low" else "the other member's"
    return Revocation(
        f"withdraw_{which}",
        f"a withdrawal of {who} onboarding consent",
        "withdraw",
        act,
        frozenset({"consent_not_current"}),
        effect,
        account_of,
    )


D5_REVOCATIONS: tuple[Revocation, ...] = (
    _profile("pause", "low"),
    _profile("pause", "high"),
    _profile("restrict", "low"),
    _profile("restrict", "high"),
    _consent("low"),
    _consent("high"),
)
REVOCATION_BY_ID = {r.id: r for r in (*REVOCATIONS, *D5_REVOCATIONS)}


def _forced_cases(rev: Revocation) -> list[Case]:
    def sequential_send_first(ctx: Context, judge: Judge) -> None:
        world = make_world(ctx)
        sent = ctx.subject.send(send_request(world, key="k1"))
        judge.outcome(sent, "send before the revocation", "authorized")
        judge.outcome(rev.act(world, ctx.subject, None), rev.title, "applied")
        rev.effect(world, judge)
        after = ctx.subject.send(send_request(world, key="k2"))
        judge.outcome(
            after, "send after the revocation (old version)", "refused", reasons=rev.refusals
        )
        if rev.kind in ("block", "unmatch"):
            bumped = ctx.subject.send(send_request(world, key="k3", contact_version=2))
            judge.outcome(
                bumped,
                "send after the revocation (new version)",
                "refused",
                reasons={"match_not_active"},
            )
        rows = submissions_of(world.match)
        judge.expect(len(rows) == 1 and rows[0][1] == 1, f"submissions {rows}, expected one at v1")
        if sent.receipt:
            judge.expect(
                outbox_count("message_submitted", sent.receipt.submission_id) == 1,
                "no message_submitted event for the authorization",
            )

    def sequential_revocation_first(ctx: Context, judge: Judge) -> None:
        world = make_world(ctx)
        judge.outcome(rev.act(world, ctx.subject, None), rev.title, "applied")
        rev.effect(world, judge)
        after = ctx.subject.send(send_request(world, key="k1"))
        judge.outcome(after, "send after the revocation", "refused", reasons=rev.refusals)
        judge.expect(submissions_of(world.match) == [], "a submission was committed")

    def send_holds(ctx: Context, judge: Judge) -> None:
        world = make_world(ctx)
        request = send_request(world, key="k1")
        sent, revoked, _ = forced(
            ctx,
            judge,
            lambda hooks: ctx.subject.send(request, hooks=hooks),
            lambda hooks: rev.act(world, ctx.subject, hooks),
        )
        judge.outcome(sent, "send (held its locks)", "authorized")
        judge.outcome(revoked, rev.title + " (arrived while the send held)", "applied")
        rev.effect(world, judge)
        rows = submissions_of(world.match)
        judge.expect(len(rows) == 1 and rows[0][1] == 1, f"submissions {rows}, expected one at v1")
        if sent.receipt and revoked.outcome == "applied":
            send_at = submission_commit(sent.receipt.submission_id)
            rev_at = ctx.evidence.revocation_commit(world, rev)
            judge.expect(
                rev_at is not None and send_at < rev_at,
                f"commit order: send {send_at.isoformat()} vs revocation"
                f" {rev_at.isoformat() if rev_at else None}",
                signal=COMMIT_AFTER_REVOCATION,
            )
            judge.note("commit timestamps: send before the revocation")

    def revocation_holds(ctx: Context, judge: Judge) -> None:
        world = make_world(ctx)
        request = send_request(world, key="k1")
        revoked, sent, _ = forced(
            ctx,
            judge,
            lambda hooks: rev.act(world, ctx.subject, hooks),
            lambda hooks: ctx.subject.send(request, hooks=hooks),
        )
        judge.outcome(revoked, rev.title + " (held its locks)", "applied")
        judge.outcome(
            sent, "send (arrived while the revocation held)", "refused", reasons=rev.refusals
        )
        rev.effect(world, judge)
        judge.expect(submissions_of(world.match) == [], "a submission was committed")

    guarantee = {
        "block": "DB06 block (first block: no Block row exists before)",
        "unmatch": "DB06 unmatch",
        "suspend": "DB06/DB09 suspension (epoch)",
        "delete": "DB06/DB09 deletion (lifecycle, epoch)",
        "sign_out": "DB09 sign-out (5.1)",
        "expire": "DB09 administrative expiry (5.1)",
        "pause": "P06.2 D5 profile pause (DM-13 4.1)",
        "restrict": "P06.2 D5 profile restriction (DM-13 4.1)",
        "withdraw": "P06.2 D5 consent withdrawal (DM-13 4.1)",
    }[rev.kind]
    return [
        Case(
            f"{rev.id}.sequential_send_first",
            guarantee,
            f"{rev.title}: the send commits first, sequentially",
            sequential_send_first,
        ),
        Case(
            f"{rev.id}.sequential_revocation_first",
            guarantee,
            f"{rev.title}: the revocation commits first, sequentially",
            sequential_revocation_first,
        ),
        Case(
            f"{rev.id}.send_holds",
            guarantee,
            f"{rev.title} arrives while the send holds its locks",
            send_holds,
        ),
        Case(
            f"{rev.id}.revocation_holds",
            guarantee,
            f"the send arrives while {rev.title} holds its locks",
            revocation_holds,
        ),
    ]


# -- the named cases -----------------------------------------------------------------


def positive_send(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    judge.outcome(ctx.subject.send(send_request(world, key="k1")), "first send", "authorized")
    judge.outcome(ctx.subject.send(send_request(world, key="k2")), "second send", "authorized")
    judge.outcome(ctx.subject.sign_out(world.session_high), "the other member signs out", "applied")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k3")),
        "send after the other member's sign-out (no revocation of contact)",
        "authorized",
    )
    judge.outcome(
        ctx.subject.send(send_request(world, sender=world.high, key="k4")),
        "the signed-out member's send",
        "refused",
        reasons={"session_not_valid"},
    )
    judge.expect(len(submissions_of(world.match)) == 3, "expected three submissions")


def stale_contact_version(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    judge.outcome(
        ctx.subject.send(send_request(world, key="k1", contact_version=2)),
        "send with a contact version ahead of the match",
        "refused",
        reasons={"stale_contact_version"},
    )
    judge.outcome(
        ctx.subject.send(send_request(world, key="k2", contact_version=0)),
        "send with a contact version behind the match",
        "refused",
        reasons={"stale_contact_version"},
    )
    judge.expect(submissions_of(world.match) == [], "a submission was committed")
    judge.expect(match_row(world.match) == ("active", 1), "the match changed")


def retry_identical(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    request = send_request(world, key="k1")
    first = ctx.subject.send(request)
    again = ctx.subject.send(request)
    judge.outcome(first, "first request", "authorized")
    judge.outcome(again, "identical retry", "replayed")
    judge.expect(
        first.receipt is not None
        and again.receipt is not None
        and first.receipt.submission_id == again.receipt.submission_id,
        "the retry did not return the first receipt",
    )
    judge.expect(len(submissions_of(world.match)) == 1, "the retry created a second row")


def retry_different_request(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    judge.outcome(
        ctx.subject.send(send_request(world, key="k1", text="one")), "first", "authorized"
    )
    judge.outcome(
        ctx.subject.send(send_request(world, key="k1", text="two")),
        "same key, different request",
        "refused",
        reasons={"idempotency_conflict"},
    )
    judge.expect(len(submissions_of(world.match)) == 1, "expected one row")


def retry_after_revocation(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    request = send_request(world, key="k1")
    judge.outcome(ctx.subject.send(request), "first request", "authorized")
    judge.outcome(ctx.subject.block(world.high, world.low), "block by the other member", "applied")
    retry = ctx.subject.send(request)
    judge.outcome(
        retry,
        "identical retry after the revocation",
        "refused",
        reasons={"match_not_active", "blocked"},
    )
    judge.expect(retry.receipt is None, "the retry after a revocation returned the old receipt")
    judge.expect(len(submissions_of(world.match)) == 1, "expected one row")


def racing_duplicates(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    request = send_request(world, key="k1")
    first, second, _ = forced(
        ctx,
        judge,
        lambda hooks: ctx.subject.send(request, hooks=hooks),
        lambda hooks: ctx.subject.send(request, hooks=hooks),
    )
    judge.outcome(first, "first identical request (held)", "authorized")
    judge.outcome(second, "second identical request (waited)", "replayed")
    judge.expect(
        first.receipt is not None
        and second.receipt is not None
        and first.receipt.submission_id == second.receipt.submission_id,
        "the two requests did not yield one receipt",
    )
    judge.expect(len(submissions_of(world.match)) == 1, "expected exactly one row")
    judge.expect(
        first.outcome != "error" and second.outcome != "error",
        "a database error reached the caller",
    )


def unblock_no_resurrect(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    judge.outcome(ctx.subject.block(world.high, world.low), "block", "applied")
    judge.outcome(ctx.subject.unblock(world.high, world.low), "unblock", "applied")
    judge.expect(block_state(world.high, world.low) == "removed", "block row not removed")
    judge.expect(match_row(world.match) == ("restricted", 2), "the unblock changed the match")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k1", contact_version=1)),
        "send with the old contact version",
        "refused",
        reasons={"match_not_active"},
    )
    judge.outcome(
        ctx.subject.send(send_request(world, key="k2", contact_version=2)),
        "send with the new contact version",
        "refused",
        reasons={"match_not_active"},
    )
    judge.outcome(
        ctx.subject.block(world.high, world.low), "re-block (removed to active)", "applied"
    )
    judge.expect(block_state(world.high, world.low) == "active", "re-block did not activate")
    judge.expect(account_row(world.high)[2] == 4, "blocks_version not bumped three times")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k3", contact_version=2)),
        "send after the re-block",
        "refused",
        reasons={"match_not_active", "blocked"},
    )
    judge.expect(submissions_of(world.match) == [], "a submission was committed")


def session_expires_during_wait(ctx: Context, judge: Judge) -> None:
    """5.2: the sender's session expires while its send waits on a lock held by the
    other member's send. The design reads the clock after the locks and refuses."""
    world = make_world(ctx)
    short = ctx.subject.sign_in(world.low, ttl_seconds=3.0)
    judge.outcome(short, "short-lived sign-in", "applied")
    assert short.session_id is not None
    expires_at = session_row(short.session_id)[2]
    holder_request = send_request(world, sender=world.high, key="k-holder")
    waiting_request = send_request(world, session=short.session_id, key="k-waiting")

    def before_release(pid: int) -> None:
        started = xact_start_of(pid)
        judge.expect(
            started is not None and started < expires_at,
            "not forced: the waiting send's transaction began after the session's expiry",
        )
        judge.note(
            f"waiting send began at {started.isoformat() if started else None},"
            f" session expires at {expires_at.isoformat()}"
        )
        while db_clock() <= expires_at:
            pass
        judge.note("released after the database clock passed the session's expiry")

    held, waited, _ = forced(
        ctx,
        judge,
        lambda hooks: ctx.subject.send(holder_request, hooks=hooks),
        lambda hooks: ctx.subject.send(waiting_request, hooks=hooks),
        before_release=before_release,
    )
    judge.outcome(held, "the other member's send (held)", "authorized")
    judge.outcome(
        waited,
        "the send whose session expired while waiting",
        "refused",
        reasons={"session_expired"},
    )
    rows = submissions_of(world.match)
    judge.expect(len(rows) == 1 and rows[0][2] == "k-holder", f"submissions {rows}")


def opposing_first_lock_block_high_vs_send(ctx: Context, judge: Judge) -> None:
    """5.3: a block by the higher account holds its first lock (the lower account, in the
    canonical order); the lower account's send arrives. No deadlock, no violation."""
    world = make_world(ctx)
    request = send_request(world, key="k1")
    blocked, sent, _ = forced(
        ctx,
        judge,
        lambda hooks: ctx.subject.block(world.high, world.low, hooks=hooks),
        lambda hooks: ctx.subject.send(request, hooks=hooks),
        hold_at="after_first_lock",
    )
    judge.outcome(blocked, "block by the higher account (held its first lock)", "applied")
    judge.outcome(
        sent, "send by the lower account", "refused", reasons={"match_not_active", "blocked"}
    )
    judge.expect(
        blocked.outcome != "deadlock" and sent.outcome != "deadlock", "deadlock", signal=DEADLOCK
    )
    judge.expect(match_row(world.match) == ("restricted", 2), "match not restricted")


def opposing_first_lock_suspend_high_vs_block_low(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    suspended, blocked, _ = forced(
        ctx,
        judge,
        lambda hooks: ctx.subject.suspend(world.high, hooks=hooks),
        lambda hooks: ctx.subject.block(world.low, world.high, hooks=hooks),
        hold_at="after_first_lock",
    )
    judge.outcome(suspended, "suspension of the higher account (held)", "applied")
    judge.outcome(blocked, "block by the lower account (waited on the higher account)", "applied")
    judge.expect(match_row(world.match) == ("restricted", 2), "match not restricted")
    judge.expect(account_row(world.high)[0] == "suspended", "account not suspended")


def opposing_blocks_both_sides(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    first, second, _ = forced(
        ctx,
        judge,
        lambda hooks: ctx.subject.block(world.high, world.low, hooks=hooks),
        lambda hooks: ctx.subject.block(world.low, world.high, hooks=hooks),
        hold_at="after_first_lock",
    )
    judge.outcome(first, "block by the higher account (held its first lock)", "applied")
    judge.outcome(second, "block by the lower account (waited)", "applied")
    judge.expect(block_state(world.high, world.low) == "active", "high->low block missing")
    judge.expect(block_state(world.low, world.high) == "active", "low->high block missing")
    judge.expect(match_row(world.match) == ("restricted", 2), "match not restricted once at v2")


def opposing_four_writers(ctx: Context, judge: Judge) -> None:
    """Four writers together, ten times: a send, a block by each side and a suspension.
    No deadlock, no error, and every outcome in its allowed set."""
    deadlocks = 0
    for round_ in range(10):
        world = make_world(ctx)
        barrier = Barrier(4)
        request = send_request(world, key=f"k{round_}")

        def gated(writer: Callable[[], Result], barrier: Barrier = barrier) -> Callable[[], Result]:
            def run() -> Result:
                barrier.wait()
                return writer()

            return run

        futures = [
            ctx.workers[0].submit(gated(partial(ctx.subject.send, request))),
            ctx.workers[1].submit(gated(partial(ctx.subject.block, world.low, world.high))),
            ctx.workers[2].submit(gated(partial(ctx.subject.block, world.high, world.low))),
            ctx.workers[3].submit(gated(partial(ctx.subject.suspend, world.high))),
        ]
        results = [f.result(timeout=budget.HOLD_SECONDS) for f in futures]
        deadlocks += sum(r.outcome == "deadlock" for r in results)
        judge.expect(results[0].outcome in ("authorized", "refused"), f"send: {results[0].label()}")
        for label, result in zip(
            ("block low", "block high", "suspend high"), results[1:], strict=True
        ):
            judge.expect(result.outcome == "applied", f"{label}: {result.label()}")
        judge.expect(match_row(world.match)[0] == "restricted", "match not restricted")
    judge.expect(deadlocks == 0, f"{deadlocks} deadlocks", signal=DEADLOCK)
    judge.note("40 writers in 10 rounds, no deadlock")


def sign_in_revocations(ctx: Context, judge: Judge) -> None:
    """Item 3: sign-out and expiry revoke one session; suspension and deletion revoke
    every session of the account through the epoch; a stale-epoch session cannot send."""
    world = make_world(ctx)
    second_device = ctx.subject.sign_in(world.low, ttl_seconds=SESSION_TTL)
    judge.outcome(second_device, "second device sign-in", "applied")
    assert second_device.session_id is not None
    judge.expect(session_row(second_device.session_id)[1] == 1, "session not bound to epoch 1")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k1")), "send via device 1", "authorized"
    )
    judge.outcome(ctx.subject.sign_out(world.session_low), "sign-out of device 1", "applied")
    judge.outcome(ctx.subject.sign_out(world.session_low), "repeated sign-out", "no_change")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k2")),
        "send via device 1 after sign-out",
        "refused",
        reasons={"session_not_valid"},
    )
    judge.outcome(
        ctx.subject.send(send_request(world, session=second_device.session_id, key="k3")),
        "send via device 2 (unaffected by device 1's sign-out)",
        "authorized",
    )
    judge.outcome(
        ctx.subject.expire_session(second_device.session_id),
        "administrative expiry of device 2",
        "applied",
    )
    judge.outcome(
        ctx.subject.send(send_request(world, session=second_device.session_id, key="k4")),
        "send via device 2 after expiry",
        "refused",
        reasons={"session_not_valid"},
    )
    third = ctx.subject.sign_in(world.low, ttl_seconds=SESSION_TTL)
    judge.outcome(third, "third sign-in", "applied")
    assert third.session_id is not None
    judge.outcome(
        ctx.subject.send(send_request(world, session=third.session_id, key="k5")),
        "send via the third session",
        "authorized",
    )
    judge.outcome(ctx.subject.suspend(world.low), "suspension", "applied")
    judge.expect(
        session_row(third.session_id)[:2] == ("valid", 1), "session row changed by suspension"
    )
    judge.expect(account_row(world.low)[1] == 2, "epoch not bumped")
    judge.outcome(
        ctx.subject.send(send_request(world, session=third.session_id, key="k6")),
        "send via the third session after suspension (stale epoch, account suspended)",
        "refused",
        reasons={"account_not_active", "session_epoch_stale"},
    )
    judge.outcome(
        ctx.subject.sign_in(world.low, ttl_seconds=SESSION_TTL),
        "sign-in while suspended",
        "refused",
        reasons={"account_not_active"},
    )
    # The other member: deletion revokes every session of that account through its epoch.
    other_second = ctx.subject.sign_in(world.high, ttl_seconds=SESSION_TTL)
    assert other_second.session_id is not None
    judge.outcome(ctx.subject.delete(world.high), "deletion of the other member", "applied")
    judge.outcome(ctx.subject.delete(world.high), "repeated deletion", "no_change")
    for label, session in (("device 1", world.session_high), ("device 2", other_second.session_id)):
        judge.outcome(
            ctx.subject.send(
                send_request(world, sender=world.high, session=session, key=f"k-{label}")
            ),
            f"the deleted member's send via {label}",
            "refused",
            reasons={"account_not_active", "session_epoch_stale"},
        )
    judge.expect(len(submissions_of(world.match)) == 3, "expected three submissions to remain")


def deletion_keeps_authorization(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    sent = ctx.subject.send(send_request(world, key="k1"))
    judge.outcome(sent, "send", "authorized")
    judge.outcome(ctx.subject.delete(world.low), "deletion of the sender", "applied")
    rows = submissions_of(world.match)
    judge.expect(len(rows) == 1, "the committed authorization was erased")
    job, tombstone, _ = deletion_recorded(world.low)
    judge.expect(job, "no DeletionJob with access revoked")
    judge.expect(tombstone, "no tombstone")
    judge.expect(account_row(world.low)[0] == "deletion_pending", "account not deletion_pending")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k2")),
        "send after deletion",
        "refused",
        reasons={"account_not_active"},
    )
    judge.outcome(
        ctx.subject.send(send_request(world, sender=world.high, key="k3")),
        "the other member's send after the deletion",
        "refused",
        reasons={"account_not_active"},
    )


def unmatch_repeat_is_safe(ctx: Context, judge: Judge) -> None:
    world = make_world(ctx)
    judge.outcome(ctx.subject.unmatch(world.low, world.match), "unmatch", "applied")
    judge.outcome(
        ctx.subject.unmatch(world.high, world.match), "repeated unmatch by the other", "no_change"
    )
    judge.expect(match_row(world.match) == ("unmatched", 2), "contact version bumped twice")
    judge.outcome(ctx.subject.block(world.low, world.high), "block after unmatch", "applied")
    judge.expect(match_row(world.match) == ("unmatched", 2), "block changed an unmatched match")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k1", contact_version=2)),
        "send",
        "refused",
        reasons={"match_not_active"},
    )


def session_expires_after_check(ctx: Context, judge: Judge) -> None:
    """CX2 (the brief's D4, confirmed by DM-13): the send's checks pass before its
    session expires, and a delay between the checks and the commit carries the commit
    past the expiry. The design authorizes it, since expiry is checked at a time read
    after the locks (P06.DB 5.2); O5, narrowed to match, must not count it. The delay is
    the subject's hold point before its commit: the adapter's ``before_commit``, and for
    the reference design the proof log's call just before its send row."""
    world = make_world(ctx)
    short = ctx.subject.sign_in(world.low, ttl_seconds=3.0)
    judge.outcome(short, "short-lived sign-in", "applied")
    assert short.session_id is not None
    expires_at = session_row(short.session_id)[2]
    request = send_request(world, session=short.session_id, key="k-boundary")
    hold = Hold()
    pid = PidSlot()
    ctx.log.before_send_record = hold.point
    try:
        future = ctx.workers[0].submit(
            lambda: ctx.subject.send(
                request, hooks=Hooks(on_begin=pid.set, before_commit=hold.point)
            )
        )
        if not _wait_held(hold, future):
            hold.release.set()
            judge.fail(
                f"the send reached no hold point before its commit: {future.result().label()}"
            )
            return
        started = xact_start_of(pid.wait())
        judge.expect(
            started is not None and started < expires_at,
            "not forced: the send's transaction began after the session's expiry",
        )
        while db_clock() <= expires_at:
            time.sleep(0.01)
        judge.note("released after the database clock passed the session's expiry")
        hold.release.set()
        sent = future.result(timeout=budget.HOLD_SECONDS)
    finally:
        ctx.log.before_send_record = None
    judge.outcome(sent, "the send whose checks ran before the expiry", "authorized")
    if sent.receipt is not None:
        committed = submission_commit(sent.receipt.submission_id)
        judge.expect(
            committed >= expires_at,
            f"the boundary was not crossed: committed {committed.isoformat()},"
            f" expiry {expires_at.isoformat()}",
        )
        judge.note(f"committed {committed.isoformat()} after the expiry {expires_at.isoformat()}")


def d5_restored(ctx: Context, judge: Judge) -> None:
    """P06.2 D5, the positive side: resuming a paused profile and accepting consent again
    let the member send again; a restriction is not lifted by a resume."""
    subject = ctx.state_subject
    world = make_world(ctx)
    judge.outcome(subject.pause_profile(world.high), "pause the other member's profile", "applied")
    judge.outcome(subject.pause_profile(world.high), "repeated pause", "no_change")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k1")),
        "send while paused",
        "refused",
        reasons={"profile_unavailable"},
    )
    judge.outcome(subject.resume_profile(world.high), "resume", "applied")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k2")), "send after resume", "authorized"
    )
    judge.outcome(subject.withdraw_consent(world.low), "withdraw the sender's consent", "applied")
    judge.outcome(subject.withdraw_consent(world.low), "repeated withdrawal", "no_change")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k3")),
        "send after withdrawal",
        "refused",
        reasons={"consent_not_current"},
    )
    judge.outcome(subject.accept_consent(world.low), "accept again", "applied")
    judge.expect(consent_row(world.low) == ("accepted", 3), f"consent {consent_row(world.low)}")
    judge.outcome(
        ctx.subject.send(send_request(world, key="k4")), "send after re-acceptance", "authorized"
    )
    judge.outcome(subject.restrict_profile(world.low), "restrict the sender's profile", "applied")
    judge.outcome(
        subject.resume_profile(world.low),
        "a resume does not lift a restriction",
        "refused",
        reasons={"profile_unavailable"},
    )
    judge.outcome(
        ctx.subject.send(send_request(world, key="k5")),
        "send while restricted",
        "refused",
        reasons={"profile_unavailable"},
    )
    judge.expect(len(submissions_of(world.match)) == 2, "expected two submissions")


NAMED_CASES: tuple[Case, ...] = (
    Case("named.positive_send", "positive control", "sends that must be authorized", positive_send),
    Case(
        "named.stale_contact_version",
        "DB06 stale contact version",
        "a stale contact version is refused",
        stale_contact_version,
    ),
    Case(
        "named.retry_identical",
        "5.4 retry rule 1",
        "an identical retry returns the first receipt",
        retry_identical,
    ),
    Case(
        "named.retry_different_request",
        "5.4 retry rule 2",
        "the same key with a different request is refused",
        retry_different_request,
    ),
    Case(
        "named.retry_after_revocation",
        "5.4 retry rule 3",
        "a retry after a revocation is refused",
        retry_after_revocation,
    ),
    Case(
        "named.racing_duplicates",
        "5.4 retry rule 4",
        "two identical requests racing yield one row",
        racing_duplicates,
    ),
    Case(
        "named.unblock_no_resurrect",
        "DB06 unblock does not resurrect",
        "block, unblock, then sends with the old and new versions",
        unblock_no_resurrect,
    ),
    Case(
        "named.session_expires_during_wait",
        "5.2 time read after the locks",
        "a session that expires while the send waits",
        session_expires_during_wait,
    ),
    Case(
        "named.opposing_first_lock_block_high_vs_send",
        "5.3 canonical lock order",
        "a block by the higher account holding its first lock against a send",
        opposing_first_lock_block_high_vs_send,
    ),
    Case(
        "named.opposing_first_lock_suspend_high_vs_block_low",
        "5.3 canonical lock order",
        "a suspension holding the higher account against a block by the lower",
        opposing_first_lock_suspend_high_vs_block_low,
    ),
    Case(
        "named.opposing_blocks_both_sides",
        "5.3 canonical lock order",
        "a block by each side, one holding its first lock",
        opposing_blocks_both_sides,
    ),
    Case(
        "named.opposing_four_writers",
        "5.3 no deadlock",
        "a send, a block by each side and a suspension together, ten rounds",
        opposing_four_writers,
    ),
    Case(
        "named.sign_in_revocations",
        "DB09 sign-in revocations (item 3)",
        "sign-out, expiry, suspension and deletion against sessions",
        sign_in_revocations,
    ),
    Case(
        "named.deletion_keeps_authorization",
        "5.6 deletion is a lifecycle transition",
        "deletion leaves the committed authorization in place",
        deletion_keeps_authorization,
    ),
    Case(
        "named.unmatch_repeat_is_safe",
        "DB06 repeated unmatch",
        "a repeated unmatch and a block after an unmatch change nothing",
        unmatch_repeat_is_safe,
    ),
    Case(
        "named.session_expires_after_check",
        "CX2 expiry checked at a time read after the locks (P06.2 D4)",
        "a session that expires between the send's checks and its commit",
        session_expires_after_check,
    ),
)
D5_NAMED_CASES: tuple[Case, ...] = (
    Case(
        "named.d5_restored",
        "P06.2 D5 resume and re-acceptance",
        "resuming a profile and accepting consent again restore sending; a resume does not"
        " lift a restriction",
        d5_restored,
    ),
)


def all_cases(*, d5: bool = False) -> tuple[Case, ...]:
    revocations = (*REVOCATIONS, *D5_REVOCATIONS) if d5 else REVOCATIONS
    forced_cases = [case for rev in revocations for case in _forced_cases(rev)]
    # B1_CASES is defined below; the adapter (d5) is the only subject that carries it.
    extra = (*D5_NAMED_CASES, *B1_CASES) if d5 else ()
    return (*forced_cases, *NAMED_CASES, *extra)


# -- P06.2 B1: the adapter's match activation against the profile and consent writers
# (CX5; DM-15 6.1), the token grant against the epoch bump (F1; DM-14 item 3), and the
# F2 and F5 nits. The adapter only: the reference design has no activation of its own
# (its fixtures write the match directly), no grant and no D5 writer. ---------------------


@dataclass(frozen=True)
class Pair:
    """Two accounts ready to match, not yet matched."""

    low: UUID
    high: UUID

    def account(self, which: str) -> UUID:
        return self.low if which == "low" else self.high


def make_pair(ctx: Context) -> Pair:
    first, second = ctx.fixtures.create_account(), ctx.fixtures.create_account()
    low, high = sorted((first, second))
    return Pair(low, high)


def _sessions_for(ctx: Context, pair: Pair, match_id: UUID) -> World:
    """After an activation applied: its world row (the delivery phase checks it as a
    design world) and one session per member, for the send that follows."""
    ctx.log.record_world(ctx.name, match_id, pair.low, pair.high)
    sessions = []
    for account in (pair.low, pair.high):
        signed = ctx.subject.sign_in(account, ttl_seconds=SESSION_TTL)
        if signed.outcome != "applied" or signed.session_id is None:
            raise RuntimeError(f"fixture sign-in failed: {signed.label()}")
        sessions.append(signed.session_id)
    return World(pair.low, pair.high, match_id, sessions[0], sessions[1])


@contextmanager
def skewed_app_clock(ahead: timedelta = timedelta(hours=1)) -> Iterator[None]:
    """The app server's clock deliberately ahead of the database's (F1 point 5): what
    Django writes into ``created_at`` and ``updated_at``. The adapter's issue time and the
    bump's cut-off come from ``clock_timestamp()`` under the locks, so the skew must not
    reach them; a case shows it in the rows it reads back."""
    from django.utils import timezone

    real = timezone.now
    timezone.now = lambda: real() + ahead
    try:
        yield
    finally:
        timezone.now = real


APP_CLOCK_SKEW = timedelta(hours=1)


def _b1_writer(op: str, which: str) -> Callable[[Context, Pair, Hooks | None], Result]:
    def act(ctx: Context, pair: Pair, hooks: Hooks | None) -> Result:
        subject = ctx.state_subject
        method = {
            "pause": subject.pause_profile,
            "restrict": subject.restrict_profile,
            "withdraw": subject.withdraw_consent,
        }[op]
        return method(pair.account(which), hooks=hooks)

    return act


def _activation_cases(op: str, which: str) -> list[Case]:
    rev = REVOCATION_BY_ID[f"{op}_{which}"]
    act = _b1_writer(op, which)
    refusals = rev.refusals
    who = "the first member's" if which == "low" else "the second member's"
    writer = {"pause": "a pause", "restrict": "a restriction", "withdraw": "a withdrawal"}[op]
    title = f"{writer} of {who} {'onboarding consent' if op == 'withdraw' else 'profile'}"

    def activate(ctx: Context, pair: Pair, hooks: Hooks | None) -> Result:
        return ctx.state_subject.activate_match(pair.low, pair.high, hooks=hooks)

    def world_of(pair: Pair, match_id: UUID) -> World:
        # For the evidence reader: the writer's witness is found by the account.
        return World(pair.low, pair.high, match_id, match_id, match_id)

    def send_refused_after(ctx: Context, judge: Judge, world: World) -> None:
        judge.outcome(
            ctx.subject.send(send_request(world, key="k-after")),
            f"a send after {title}",
            "refused",
            reasons=refusals,
        )
        judge.expect(submissions_of(world.match) == [], "a submission was committed")

    def sequential_writer_first(ctx: Context, judge: Judge) -> None:
        pair = make_pair(ctx)
        judge.outcome(act(ctx, pair, None), title, "applied")
        judge.outcome(
            activate(ctx, pair, None), f"activation after {title}", "refused", reasons=refusals
        )
        judge.expect(match_between(pair.low, pair.high) is None, "a match was created")

    def sequential_activation_first(ctx: Context, judge: Judge) -> None:
        pair = make_pair(ctx)
        activated = activate(ctx, pair, None)
        judge.outcome(activated, "activation", "applied")
        found = match_between(pair.low, pair.high)
        if not judge.expect(found is not None and found[1] == "active", f"match {found}"):
            return
        assert found is not None
        judge.outcome(act(ctx, pair, None), f"{title} after the activation", "applied")
        rev.effect(world_of(pair, found[0]), judge)
        send_refused_after(ctx, judge, _sessions_for(ctx, pair, found[0]))

    def activation_holds(ctx: Context, judge: Judge) -> None:
        pair = make_pair(ctx)
        activated, written, _ = forced(
            ctx,
            judge,
            lambda hooks: activate(ctx, pair, hooks),
            lambda hooks: act(ctx, pair, hooks),
        )
        judge.outcome(activated, "activation (held its locks)", "applied")
        judge.outcome(written, f"{title} (arrived while the activation held)", "applied")
        found = match_between(pair.low, pair.high)
        if not judge.expect(found is not None, "no match after the activation"):
            return
        assert found is not None
        rev.effect(world_of(pair, found[0]), judge)
        if activated.outcome == "applied" and written.outcome == "applied":
            activated_at = activation_commit(found[0])
            written_at = ctx.evidence.revocation_commit(world_of(pair, found[0]), rev)
            judge.expect(
                activated_at is not None and written_at is not None and activated_at < written_at,
                f"commit order: activation {activated_at} vs the writer {written_at}",
                signal=COMMIT_AFTER_REVOCATION,
            )
            judge.note("commit timestamps: the activation before the writer")
        send_refused_after(ctx, judge, _sessions_for(ctx, pair, found[0]))

    def writer_holds(ctx: Context, judge: Judge) -> None:
        pair = make_pair(ctx)
        written, activated, _ = forced(
            ctx,
            judge,
            lambda hooks: act(ctx, pair, hooks),
            lambda hooks: activate(ctx, pair, hooks),
        )
        judge.outcome(written, f"{title} (held its locks)", "applied")
        judge.outcome(
            activated,
            f"activation (arrived while {title} held)",
            "refused",
            reasons=refusals,
        )
        judge.expect(match_between(pair.low, pair.high) is None, "a match was created")

    guarantee = f"P06.2 B1 activation's checks (CX5): {rev.kind}"
    prefix = f"activation.{op}_{which}"
    return [
        Case(
            f"{prefix}.sequential_writer_first",
            guarantee,
            f"{title} commits first, sequentially; the activation refuses",
            sequential_writer_first,
        ),
        Case(
            f"{prefix}.sequential_activation_first",
            guarantee,
            f"the activation commits first, sequentially; {title} follows and a send refuses",
            sequential_activation_first,
        ),
        Case(
            f"{prefix}.activation_holds",
            guarantee,
            f"{title} arrives while the activation holds its locks; a send refuses afterwards",
            activation_holds,
        ),
        Case(
            f"{prefix}.writer_holds",
            guarantee,
            f"the activation arrives while {title} holds its locks, and refuses",
            writer_holds,
        ),
    ]


B1_ACTIVATION_CASES: tuple[Case, ...] = tuple(
    case
    for op in ("pause", "restrict", "withdraw")
    for which in ("low", "high")
    for case in _activation_cases(op, which)
)


# -- the token grant ----------------------------------------------------------------------

GRANT_REFUSED_AFTER_BUMP = frozenset({"account_not_active", "session_epoch_stale"})
TOKEN_GUARANTEE = "P06.2 B1 token grant under the account and session locks (F1)"


def _provisioned_world(ctx: Context) -> World:
    """A world whose first member's identity is provisioned (a fixture write: the
    delivery phase, which provisions, runs after the cases)."""
    world = make_world(ctx)
    provision = getattr(ctx.fixtures, "provision_identity", None)
    if provision is None:
        raise RuntimeError("this subject's fixtures cannot provision an identity")
    provision(world.low)
    return world


def _grant(ctx: Context, world: World, hooks: Hooks | None = None) -> Result:
    return ctx.state_subject.grant_token(world.session_low, hooks=hooks)


def _bump_cutoff(world: World) -> tuple[datetime, datetime]:
    """The bump's cut-off, the time it read after its account lock (the event's
    ``available_at``), and the app clock at the event's save (``created_at``)."""
    times = event_times("session_epoch_bumped", world.low)
    if times is None:
        raise RuntimeError("no session_epoch_bumped event")
    return times


def _judge_grant_before_bump(judge: Judge, granted: Result, world: World) -> None:
    """The grant's issue time precedes the bump's cut-off, both from the database clock,
    while the app's clock (skewed ahead) shows in the row the app stamped."""
    issued_at = granted.detail.get("issued_at")
    if not judge.expect(isinstance(issued_at, datetime), "the grant carries no issue time"):
        return
    assert isinstance(issued_at, datetime)
    cutoff, created_at = _bump_cutoff(world)
    judge.expect(
        issued_at < cutoff,
        f"the issue time {issued_at.isoformat()} is not before the cut-off {cutoff.isoformat()}",
        signal=COMMIT_AFTER_REVOCATION,
    )
    skew = created_at - cutoff
    judge.expect(
        skew > APP_CLOCK_SKEW - timedelta(minutes=5),
        f"the app clock skew did not show: created_at - cut-off = {skew}",
    )
    judge.expect(
        issued_at < cutoff + timedelta(minutes=5),
        "the issue time followed the skewed app clock, not the database's",
    )
    judge.note(
        f"issued {issued_at.isoformat()} before the cut-off {cutoff.isoformat()}; the app"
        f" clock, {skew} ahead, stamped created_at and reached neither"
    )


def token_pending_identity_refused(ctx: Context, judge: Judge) -> None:
    """DM-15 5.1: an identity the provider does not hold yet refuses a grant."""
    world = make_world(ctx)
    judge.outcome(
        _grant(ctx, world),
        "a grant for a pending identity",
        "refused",
        reasons={"no_chat_identity"},
    )
    row = identity_row(world.low)
    judge.expect(row is not None and row[0] == "pending", f"identity {row}")


def token_sequential_grant_first(ctx: Context, judge: Judge) -> None:
    world = _provisioned_world(ctx)
    with skewed_app_clock(APP_CLOCK_SKEW):
        granted = _grant(ctx, world)
        judge.outcome(granted, "grant before the bump", "granted")
        judge.outcome(ctx.subject.suspend(world.low), "suspension (the epoch bump)", "applied")
    if granted.outcome == "granted":
        _judge_grant_before_bump(judge, granted, world)
    judge.outcome(
        _grant(ctx, world), "grant after the bump", "refused", reasons=GRANT_REFUSED_AFTER_BUMP
    )


def token_sequential_bump_first(ctx: Context, judge: Judge) -> None:
    world = _provisioned_world(ctx)
    with skewed_app_clock(APP_CLOCK_SKEW):
        judge.outcome(ctx.subject.suspend(world.low), "suspension (the epoch bump)", "applied")
        judge.outcome(
            _grant(ctx, world), "grant after the bump", "refused", reasons=GRANT_REFUSED_AFTER_BUMP
        )


def token_grant_holds(ctx: Context, judge: Judge) -> None:
    """A grant that commits just before a bump: the bump waits on the grant's shared
    locks, and the issue time precedes the cut-off (F1 point 5, second case)."""
    world = _provisioned_world(ctx)
    with skewed_app_clock(APP_CLOCK_SKEW):
        granted, bumped, _ = forced(
            ctx,
            judge,
            lambda hooks: _grant(ctx, world, hooks),
            lambda hooks: ctx.subject.suspend(world.low, hooks=hooks),
        )
    judge.outcome(granted, "grant (held its shared locks)", "granted")
    judge.outcome(bumped, "suspension (arrived while the grant held)", "applied")
    if granted.outcome == "granted" and bumped.outcome == "applied":
        _judge_grant_before_bump(judge, granted, world)


def token_bump_holds(ctx: Context, judge: Judge) -> None:
    """A grant forced to wait on a bump that holds the account lock refuses after it (F1
    point 5, first case)."""
    world = _provisioned_world(ctx)
    with skewed_app_clock(APP_CLOCK_SKEW):
        bumped, granted, _ = forced(
            ctx,
            judge,
            lambda hooks: ctx.subject.suspend(world.low, hooks=hooks),
            lambda hooks: _grant(ctx, world, hooks),
        )
    judge.outcome(bumped, "suspension (held the account lock)", "applied")
    judge.outcome(
        granted,
        "grant (arrived while the bump held)",
        "refused",
        reasons=GRANT_REFUSED_AFTER_BUMP,
    )
    judge.expect(account_row(world.low)[1] == 2, "epoch not bumped")


def token_sign_out_holds(ctx: Context, judge: Judge) -> None:
    """The session row is the grant's second shared lock: a grant that arrives while a
    sign-out holds it waits, and refuses."""
    world = _provisioned_world(ctx)
    ended, granted, _ = forced(
        ctx,
        judge,
        lambda hooks: ctx.subject.sign_out(world.session_low, hooks=hooks),
        lambda hooks: _grant(ctx, world, hooks),
    )
    judge.outcome(ended, "sign-out (held the session row)", "applied")
    judge.outcome(
        granted,
        "grant (arrived while the sign-out held)",
        "refused",
        reasons={"session_not_valid"},
    )


B1_TOKEN_CASES: tuple[Case, ...] = (
    Case(
        "token.pending_identity_refused",
        TOKEN_GUARANTEE,
        "a grant for an identity the provider does not hold yet is refused (DM-15 5.1)",
        token_pending_identity_refused,
    ),
    Case(
        "token.sequential_grant_first",
        TOKEN_GUARANTEE,
        "a grant, then the bump: the issue time precedes the cut-off; a later grant refuses",
        token_sequential_grant_first,
    ),
    Case(
        "token.sequential_bump_first",
        TOKEN_GUARANTEE,
        "the bump, then a grant: refused",
        token_sequential_bump_first,
    ),
    Case(
        "token.grant_holds",
        TOKEN_GUARANTEE,
        "the bump arrives while the grant holds its shared locks: issued before the cut-off",
        token_grant_holds,
    ),
    Case(
        "token.bump_holds",
        TOKEN_GUARANTEE,
        "the grant arrives while the bump holds the account lock: refused after it",
        token_bump_holds,
    ),
    Case(
        "token.sign_out_holds",
        TOKEN_GUARANTEE,
        "the grant arrives while a sign-out holds the session row: refused after it",
        token_sign_out_holds,
    ),
)


# -- F2 and F5 ------------------------------------------------------------------------------


def _harness_holder(lock_account: UUID, then: Callable[[], None]) -> Writer:
    """A harness transaction on a worker's connection: it locks one account row FOR
    UPDATE, holds there, and then, still inside its transaction, makes the change
    ``then`` writes, which no app writer ever makes (F2): the arriver that waited on the
    account lock reads the changed key under its own locks."""

    def run(hooks: Hooks | None) -> Result:
        from django.db import connection, transaction

        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SELECT pg_backend_pid()")
            pid = int(cursor.fetchone()[0])
            if hooks is not None and hooks.on_begin is not None:
                hooks.on_begin(pid)
            cursor.execute(
                "SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR UPDATE",
                [lock_account],
            )
            if hooks is not None and hooks.after_first_lock is not None:
                hooks.after_first_lock()
            if hooks is not None and hooks.after_locks is not None:
                hooks.after_locks()
            then()
        return Result("applied")

    return run


def _set_session_account(session_id: UUID, account_id: UUID) -> None:
    from glow_persistence.models import AccountSession

    AccountSession.objects.filter(pk=session_id).update(account_id=account_id)


def _set_match_pair(match_id: UUID, low: UUID, high: UUID) -> None:
    from glow_persistence.models import Match

    Match.objects.filter(pk=match_id).update(account_low_id=low, account_high_id=high)


def f2_session_account_changed_under_wait(ctx: Context, judge: Judge) -> None:
    """F2: the send re-checks the locked session's account against its pre-lock read. A
    harness transaction holds the sender's account lock and moves the session to another
    account before it commits; the send that waited on the lock refuses."""
    world = make_world(ctx)
    other = ctx.fixtures.create_account()
    request = send_request(world, key="k-f2-session")
    try:
        held, sent, _ = forced(
            ctx,
            judge,
            _harness_holder(world.low, lambda: _set_session_account(world.session_low, other)),
            lambda hooks: ctx.subject.send(request, hooks=hooks),
        )
        judge.outcome(held, "the harness transaction that moved the session", "applied")
        judge.outcome(
            sent,
            "the send that waited on the account lock",
            "refused",
            reasons={"session_changed"},
        )
        judge.expect(submissions_of(world.match) == [], "a submission was committed")
    finally:
        _set_session_account(world.session_low, world.low)
    judge.outcome(
        ctx.subject.send(send_request(world, key="k-f2-session-after")),
        "a send after the session was moved back",
        "authorized",
    )


def f2_match_pair_changed_under_wait(ctx: Context, judge: Judge) -> None:
    """F2: ``unmatch`` re-checks the locked match's pair against its pre-lock read. A
    harness transaction holds the actor's account lock and points the match at two other
    accounts before it commits; the unmatch that waited refuses, and changes nothing."""
    world = make_world(ctx)
    low, high = sorted((ctx.fixtures.create_account(), ctx.fixtures.create_account()))
    try:
        held, unmatched, _ = forced(
            ctx,
            judge,
            _harness_holder(world.low, lambda: _set_match_pair(world.match, low, high)),
            lambda hooks: ctx.subject.unmatch(world.low, world.match, hooks=hooks),
        )
        judge.outcome(held, "the harness transaction that re-paired the match", "applied")
        judge.outcome(
            unmatched,
            "the unmatch that waited on the account lock",
            "refused",
            reasons={"match_changed"},
        )
    finally:
        _set_match_pair(world.match, world.low, world.high)
    judge.expect(match_row(world.match) == ("active", 1), "the refused unmatch changed the match")
    judge.expect(outbox_count("contact_revoked", world.match) == 0, "a contact_revoked event")


def f5_self_block_refused(ctx: Context, judge: Judge) -> None:
    """F5: a block whose actor is its own target is refused with a Glow code before any
    write; the no-self constraint is never reached."""
    world = make_world(ctx)
    judge.outcome(
        ctx.subject.block(world.low, world.low), "a self-block", "refused", reasons={"self_target"}
    )
    judge.expect(block_state(world.low, world.low) is None, "a Block row was written")
    judge.expect(account_row(world.low)[2] == 1, "blocks_version bumped")
    judge.expect(match_row(world.match) == ("active", 1), "the match changed")


B1_NAMED_CASES: tuple[Case, ...] = (
    Case(
        "named.f2_session_account_changed_under_wait",
        "P06.2 B1 F2: the locked session's account against the pre-lock read",
        "a session moved to another account while the send waits is refused",
        f2_session_account_changed_under_wait,
    ),
    Case(
        "named.f2_match_pair_changed_under_wait",
        "P06.2 B1 F2: the locked match's pair against the pre-lock read",
        "a match re-paired while the unmatch waits is refused",
        f2_match_pair_changed_under_wait,
    ),
    Case(
        "named.f5_self_block_refused",
        "P06.2 B1 F5: a self-block is refused before the write",
        "a block whose actor is its target is refused, and nothing is written",
        f5_self_block_refused,
    ),
)

B1_CASES: tuple[Case, ...] = (*B1_ACTIVATION_CASES, *B1_TOKEN_CASES, *B1_NAMED_CASES)


CASE_BY_ID = {case.id: case for case in all_cases(d5=True)}


def plan(*, d5: bool = False) -> list[dict[str, str]]:
    """The case plan, offline: id, guarantee and title of every case."""
    return [{"id": c.id, "guarantee": c.guarantee, "title": c.title} for c in all_cases(d5=d5)]


def run_all(ctx: Context, cases: Collection[Case] | None = None) -> list[CaseResult]:
    return [run_case(ctx, case) for case in (cases or all_cases(d5=ctx.d5))]
