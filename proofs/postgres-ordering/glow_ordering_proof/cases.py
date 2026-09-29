"""The race suite: forced interleavings on two real connections, and the named cases.

Every case is judged by what the database recorded: rows, commit timestamps and lock
waits. A forced "while it holds the locks" case passes only if the second connection
was observed waiting (item 6.2). The suite drives the ``OrderingSubject`` interface
only, so P06.2 can run it against the app's adapter.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Collection
from concurrent.futures import Future
from dataclasses import dataclass, field
from functools import partial
from uuid import UUID

from glow_ordering_proof import budget
from glow_ordering_proof.concurrency import Barrier, Hold, PidSlot, Worker
from glow_ordering_proof.dbreads import (
    account_row,
    block_state,
    deletion_recorded,
    log_commit,
    match_row,
    outbox_count,
    session_row,
    submission_commit,
    submissions_of,
)
from glow_ordering_proof.interface import (
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


@dataclass
class CaseResult:
    case_id: str
    guarantee: str
    title: str
    passed: bool
    waits: list[ObservedWait] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "guarantee": self.guarantee,
            "title": self.title,
            "passed": self.passed,
            "waits": [w.summary() for w in self.waits],
            "notes": self.notes,
            "failures": self.failures,
        }


class Judge:
    def __init__(self, case: Case) -> None:
        self.case = case
        self.failures: list[str] = []
        self.notes: list[str] = []
        self.waits: list[ObservedWait] = []

    def expect(self, ok: bool, message: str) -> bool:
        if not ok:
            self.failures.append(message)
        return ok

    def outcome(
        self, result: Result, what: str, *outcomes: str, reasons: Collection[str] = ()
    ) -> bool:
        ok = result.outcome in outcomes and (not reasons or result.reason in reasons)
        if not ok:
            wanted = "/".join(outcomes) + (f" ({'|'.join(sorted(reasons))})" if reasons else "")
            self.failures.append(f"{what}: {result.label()}, expected {wanted}")
        else:
            self.notes.append(f"{what}: {result.label()}")
        return ok

    def wait(self, observed: ObservedWait, *, required: bool = True) -> None:
        self.waits.append(observed)
        if required and not observed.observed:
            self.failures.append("the second connection was not observed waiting on a lock")

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
        )


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
        judge.failures.append(f"harness error: {type(exc).__name__}: {exc}")
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
    second connection and is observed waiting (pg_stat_activity, pg_locks); then the
    holder is released and both finish."""
    hold = Hold()
    pid = PidSlot()
    hooks_holder = (
        Hooks(after_first_lock=hold.point)
        if hold_at == "after_first_lock"
        else Hooks(after_locks=hold.point)
    )
    first = ctx.workers[0].submit(lambda: holder(hooks_holder))
    if not _wait_held(hold, first):
        hold.release.set()
        result = first.result(timeout=budget.HOLD_SECONDS)
        judge.failures.append(f"the holder finished before its hold point: {result.label()}")
        return (
            result,
            Result("error", "arriver_not_started"),
            ObservedWait(0, False, None, None, None, None, 0, 0),
        )
    second = ctx.workers[1].submit(lambda: arriver(Hooks(on_begin=pid.set)))
    observed = observe_lock_wait(pid.wait(), finished=second.done)
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
REVOCATION_BY_ID = {r.id: r for r in REVOCATIONS}


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
            rev_at = log_commit(ctx.log, rev.kind)
            judge.expect(
                rev_at is not None and send_at < rev_at,
                f"commit order: send {send_at.isoformat()} vs revocation"
                f" {rev_at.isoformat() if rev_at else None}",
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
    judge.expect(blocked.outcome != "deadlock" and sent.outcome != "deadlock", "deadlock")
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
    judge.expect(deadlocks == 0, f"{deadlocks} deadlocks")
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
)


def all_cases() -> tuple[Case, ...]:
    forced_cases = [case for rev in REVOCATIONS for case in _forced_cases(rev)]
    return (*forced_cases, *NAMED_CASES)


CASE_BY_ID = {case.id: case for case in all_cases()}


def plan() -> list[dict[str, str]]:
    """The case plan, offline: id, guarantee and title of every case."""
    return [{"id": c.id, "guarantee": c.guarantee, "title": c.title} for c in all_cases()]


def run_all(ctx: Context, cases: Collection[Case] | None = None) -> list[CaseResult]:
    return [run_case(ctx, case) for case in (cases or all_cases())]
