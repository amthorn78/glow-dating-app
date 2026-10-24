"""The read phase (P06.2 Stage C1; the brief's "Stage C under OD-45", points b, c and e,
with DM-22's conditions): the app's conversation reads on the disposable database.

It runs after the delivery phase. Each case makes its own world under a ``read:`` run
tag (never a design world), delivers its events to this phase's own fixture provider,
and reads through the adapter (``glow_chat.reads``) with that provider's text read. The
reader is the world's lower account, through its session.

**The forced cases, for each revocation the suite applies** (P06.2's ten and D5's six:
blocks and unmatches by either member, suspension and deletion of either account, the
reader's sign-out and session expiry, pauses, restrictions and consent withdrawals of
either member), each judged by what PostgreSQL recorded:

- ``read_waits``: the revocation commits while the read waits between its provider call
  and its final check. The reader's backend is ``idle`` there (no transaction open, so no
  lock held across the call), the revocation is not observed waiting on it, and the read
  is refused; the revocation's commit precedes the final check's transaction start.
- ``check_holds``: the revocation arrives while the final check holds its shared locks,
  and is observed waiting on the reader's backend; the read returns its page, and the
  revocation commits after the final check began; the next read is refused.
- ``revocation_holds``: the revocation already holds its locks when the final check takes
  them; the final check is observed waiting on the revocation's backend, and once the
  revocation commits, the read is refused (DM-22 3.2's serialization, both ways).

``read.block_during_provider_call`` holds the provider call itself: a block by the other
member commits while it is held, with no wait recorded for the block (3.2), and the read
is refused.

**The named cases**: the order follows acceptance (2.2), pages and cursors, only text
Glow sent (2.1), a provider error fails the read (2.4), the cursor bound to its match
(6.4), a read writes nothing (2.3), no message text in a log line (2.5), unread and the
read cursor (point e, 6.3), and the conversation list (item 4, 6.1).

**The planted controls** (DM-22 3.3): two read variants composed from the adapter's own
steps in another order, one with the final check skipped and one with it before the
provider call, must each fail ``read.block_by_high.read_waits`` by its declared signal, a
missing refusal. No oracle rule judges a read (DM-22 item 3): a read writes nothing.

No provider is called but the in-memory fixture; nothing reaches a network.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import partial
from typing import Any
from uuid import UUID

from django.db import connection
from glow_domain.chat import TransactionProbe
from glow_domain.chat_provider_fixtures import FixtureChatProvider
from glow_domain.chat_reads import (
    HistoryRequest,
    PageCursor,
    ReadCursorCommand,
    ReadProbe,
    ReadResult,
)

from glow_ordering_proof import budget
from glow_ordering_proof.cases import (
    COMMIT_AFTER_REVOCATION,
    D5_REVOCATIONS,
    REFUSAL_MISSING,
    REVOCATIONS,
    Case,
    CaseResult,
    Context,
    Judge,
    Revocation,
    World,
    _wait_held,
    make_world,
    run_case,
    send_request,
)
from glow_ordering_proof.concurrency import Hold, PidSlot
from glow_ordering_proof.controls import ControlResult, Signal
from glow_ordering_proof.interface import Hooks, Result
from glow_ordering_proof.observe import LogContext, observe_lock_wait
from glow_ordering_proof.results import ReadReport

OTHER_TEXT = "hello from the other member"
OWN_TEXT = "hello back"
PROVIDER_TEXT = "fixture-provider-said: upstream detail that must not be kept"
# The tables a read could write; a read leaves every row of them as it found it (2.3).
WRITABLE_TABLES = (
    "glow_persistence_appaccount",
    "glow_persistence_accountsession",
    "glow_persistence_match",
    "glow_persistence_block",
    "glow_persistence_profile",
    "glow_persistence_consentdecision",
    "glow_persistence_chatbinding",
    "glow_persistence_chatidentity",
    "glow_persistence_messagesubmission",
    "glow_persistence_outboxevent",
    "glow_persistence_chatreadcursor",
)
BLOCK_REFUSALS = frozenset({"match_not_active", "blocked"})


class ReadCheckFailed(AssertionError):
    """A read phase fixture did not do what the case needs."""


def adapter_reads(texts: Any) -> Any:
    """The app's adapter (``glow_chat`` needs Django's registry, so it is imported here)."""
    from glow_chat.reads import OrmConversationReads

    return OrmConversationReads(texts)


@dataclass
class ReadPhase:
    ctx: Context
    provider: FixtureChatProvider
    delivery: Any  # glow_chat.delivery.OutboxDelivery
    make_reads: Callable[[Any], Any] = adapter_reads

    def reads(self, texts: Any = None) -> Any:
        return self.make_reads(self.provider if texts is None else texts)


# -- worlds and messages ------------------------------------------------------------------


def _models() -> Any:
    from glow_persistence import models

    return models


def _deliver(phase: ReadPhase) -> None:
    """Deliver every due chat event to this phase's provider; a retry is a fixture fault."""
    for _ in range(100):
        done = phase.delivery.deliver_due(limit=1000)
        if not done:
            return
        if done[-1].outcome in ("retry", "lost_lease"):
            raise ReadCheckFailed(f"delivery stalled: {done[-1].event_type} {done[-1].outcome}")
    raise ReadCheckFailed("delivery did not finish")


def _send(phase: ReadPhase, world: World, sender: UUID, key: str, text: str) -> UUID:
    sent = phase.ctx.subject.send(send_request(world, sender=sender, key=key, text=text))
    if sent.receipt is None:
        raise ReadCheckFailed(f"fixture send failed: {sent.label()}")
    return sent.receipt.submission_id


def _world(phase: ReadPhase) -> World:
    world = make_world(phase.ctx)
    _deliver(phase)
    return world


def _conversation(phase: ReadPhase) -> World:
    """A world with one delivered message from each member."""
    world = _world(phase)
    _send(phase, world, world.high, "k-other", OTHER_TEXT)
    _send(phase, world, world.low, "k-own", OWN_TEXT)
    _deliver(phase)
    return world


def _request(
    world: World,
    *,
    cursor: PageCursor | None = None,
    limit: int = 50,
    reader: UUID | None = None,
) -> HistoryRequest:
    session = world.session_of(reader) if reader is not None else world.session_low
    return HistoryRequest(session, world.match, cursor, limit)


def as_result(read: Any) -> Result:
    """A read's, a list's or a cursor command's result in the suite's ``Result``."""
    return Result(read.outcome, read.reason)


def _texts(read: ReadResult) -> list[str | None]:
    return [m.text for m in read.page.messages] if read.page is not None else []


def _read_calls(phase: ReadPhase) -> int:
    return sum(call.operation == "read_message_texts" for call in phase.provider.calls)


def backend_state(pid: int) -> str | None:
    """``pg_stat_activity.state`` of a backend: ``idle`` means no transaction is open."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT state FROM pg_stat_activity WHERE pid = %s", [pid])
        row = cursor.fetchone()
    return None if row is None else str(row[0])


def _event_id(submission_id: UUID) -> UUID:
    event: UUID = (
        _models()
        .OutboxEvent.objects.filter(event_type="message_submitted", aggregate_id=submission_id)
        .values_list("id", flat=True)
        .get()
    )
    return event


def _event_times(submission_id: UUID) -> tuple[Any, int]:
    """A message's acceptance time (its event's ``delivered_at``) and write order."""
    delivered_at, sequence = (
        _models()
        .OutboxEvent.objects.filter(event_type="message_submitted", aggregate_id=submission_id)
        .values_list("delivered_at", "sequence")
        .get()
    )
    return delivered_at, int(sequence)


def fingerprint() -> dict[str, tuple[int, int]]:
    """Every row of the writable tables by its identity and its row version (``xmin``):
    an insert, an update or a delete changes it; a row lock does not."""
    out: dict[str, tuple[int, int]] = {}
    with connection.cursor() as cursor:
        for table in WRITABLE_TABLES:
            cursor.execute(
                f"SELECT count(*), coalesce(sum(hashtext(id::text || ':' || xmin::text)), 0)"
                f" FROM {table}"
            )
            count, digest = cursor.fetchone()
            out[table] = (int(count), int(digest))
    return out


# -- the forced cases -------------------------------------------------------------------------


def _commit_before(judge: Judge, revoked_at: Any, moment: Any, what: str) -> None:
    judge.expect(
        revoked_at is not None and revoked_at < moment,
        f"commit order: the revocation {revoked_at} vs {what} {moment}",
        signal=COMMIT_AFTER_REVOCATION,
    )


def read_waits(rev: Revocation, phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """The revocation commits while the read waits between its provider call and its
    final check: the read is refused."""
    world = _conversation(phase)
    reads = phase.reads()
    hold, reader = Hold(), PidSlot()
    probe = ReadProbe(first=TransactionProbe(on_begin=reader.set), after_provider_call=hold.point)
    reading = ctx.workers[0].submit(lambda: reads.read_history(_request(world), probe=probe))
    if not _wait_held(hold, reading):
        hold.release.set()
        judge.fail(f"the read reached no hold point: {as_result(reading.result()).label()}")
        return
    pid = reader.wait()
    state = backend_state(pid)
    judge.expect(
        state == "idle",
        f"the reader's backend is {state!r} between its provider call and its final check",
    )
    writer = PidSlot()
    revoking = ctx.workers[1].submit(
        lambda: rev.act(world, ctx.subject, Hooks(on_begin=writer.set))
    )
    observed = observe_lock_wait(writer.wait(), holder_pid=pid, finished=revoking.done)
    judge.wait(observed, required=False)
    judge.expect(not observed.observed, "the revocation waited on the read")
    revoked = revoking.result(timeout=budget.HOLD_SECONDS)
    judge.outcome(revoked, f"{rev.title} (committed while the read waits)", "applied")
    hold.release.set()
    read = reading.result(timeout=budget.HOLD_SECONDS)
    rev.effect(world, judge)
    judge.outcome(
        as_result(read), "the read after its final check", "refused", reasons=rev.refusals
    )
    judge.note(f"the read held after its provider call, backend {pid} {state}")
    if read.outcome == "refused" and len(read.traces) == 2:
        revoked_at = ctx.evidence.revocation_commit(world, rev)
        _commit_before(judge, revoked_at, read.traces[1].started_at, "the final check's start")


def check_holds(rev: Revocation, phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """The revocation arrives while the final check holds its shared locks: it waits, and
    the read returns its page."""
    world = _conversation(phase)
    reads = phase.reads()
    hold, reader = Hold(), PidSlot()
    probe = ReadProbe(
        first=TransactionProbe(on_begin=reader.set), final=TransactionProbe(after_locks=hold.point)
    )
    reading = ctx.workers[0].submit(lambda: reads.read_history(_request(world), probe=probe))
    if not _wait_held(hold, reading):
        hold.release.set()
        judge.fail(f"the final check reached no hold point: {as_result(reading.result()).label()}")
        return
    pid = reader.wait()
    writer = PidSlot()
    revoking = ctx.workers[1].submit(
        lambda: rev.act(world, ctx.subject, Hooks(on_begin=writer.set))
    )
    judge.wait(observe_lock_wait(writer.wait(), holder_pid=pid, finished=revoking.done))
    hold.release.set()
    read = reading.result(timeout=budget.HOLD_SECONDS)
    revoked = revoking.result(timeout=budget.HOLD_SECONDS)
    judge.outcome(as_result(read), "the read (its final check held its locks)", "read")
    judge.expect(_texts(read) == [OTHER_TEXT, OWN_TEXT], f"page {_texts(read)}")
    judge.outcome(revoked, f"{rev.title} (arrived while the final check held)", "applied")
    rev.effect(world, judge)
    if read.outcome == "read" and len(read.traces) == 2:
        revoked_at = ctx.evidence.revocation_commit(world, rev)
        judge.expect(
            revoked_at is not None and revoked_at > read.traces[1].started_at,
            f"commit order: the revocation {revoked_at} before the final check's start"
            f" {read.traces[1].started_at}",
        )
    calls = _read_calls(phase)
    after = reads.read_history(_request(world))
    judge.outcome(as_result(after), "a read after the revocation", "refused", reasons=rev.refusals)
    # Point c: a refused member causes no provider read.
    judge.expect(_read_calls(phase) == calls, "a refused read called the provider")


def revocation_holds(rev: Revocation, phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """The revocation already holds its locks when the final check takes them: the final
    check waits on it, and the read is refused."""
    world = _conversation(phase)
    reads = phase.reads()
    read_hold, reader = Hold(), PidSlot()
    probe = ReadProbe(
        first=TransactionProbe(on_begin=reader.set), after_provider_call=read_hold.point
    )
    reading = ctx.workers[0].submit(lambda: reads.read_history(_request(world), probe=probe))
    if not _wait_held(read_hold, reading):
        read_hold.release.set()
        judge.fail(f"the read reached no hold point: {as_result(reading.result()).label()}")
        return
    rev_hold, writer = Hold(), PidSlot()
    revoking = ctx.workers[1].submit(
        lambda: rev.act(world, ctx.subject, Hooks(on_begin=writer.set, after_locks=rev_hold.point))
    )
    if not _wait_held(rev_hold, revoking):
        rev_hold.release.set()
        read_hold.release.set()
        judge.fail(f"the revocation reached no hold point: {revoking.result().label()}")
        return
    read_hold.release.set()  # the final check now takes its locks
    judge.wait(observe_lock_wait(reader.wait(), holder_pid=writer.wait(), finished=reading.done))
    rev_hold.release.set()
    revoked = revoking.result(timeout=budget.HOLD_SECONDS)
    read = reading.result(timeout=budget.HOLD_SECONDS)
    judge.outcome(revoked, f"{rev.title} (held its locks)", "applied")
    rev.effect(world, judge)
    judge.outcome(
        as_result(read), "the read (its final check waited)", "refused", reasons=rev.refusals
    )
    if read.outcome == "refused" and len(read.traces) == 2 and read.traces[1].ended_at:
        revoked_at = ctx.evidence.revocation_commit(world, rev)
        _commit_before(judge, revoked_at, read.traces[1].ended_at, "the final check's end")


class _HeldTexts:
    """The provider's text read, held inside the call until the harness releases it."""

    def __init__(self, inner: FixtureChatProvider, hold: Hold) -> None:
        self.inner = inner
        self.hold = hold

    def read_message_texts(self, channel_id: str, message_ids: tuple[str, ...]) -> dict[str, str]:
        self.hold.point()
        texts: dict[str, str] = self.inner.read_message_texts(channel_id, message_ids)
        return texts


def block_during_provider_call(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """DM-22 3.2: a block that commits during the provider call is not delayed by the
    read (no wait recorded for the block), and the read is refused."""
    world = _conversation(phase)
    call = Hold()
    reads = phase.reads(_HeldTexts(phase.provider, call))
    reader = PidSlot()
    probe = ReadProbe(first=TransactionProbe(on_begin=reader.set))
    reading = ctx.workers[0].submit(lambda: reads.read_history(_request(world), probe=probe))
    if not _wait_held(call, reading):
        call.release.set()
        judge.fail(f"the provider call was not reached: {as_result(reading.result()).label()}")
        return
    pid = reader.wait()
    state = backend_state(pid)
    judge.expect(state == "idle", f"the reader's backend is {state!r} during the provider call")
    writer = PidSlot()
    blocking = ctx.workers[1].submit(
        lambda: ctx.subject.block(world.high, world.low, hooks=Hooks(on_begin=writer.set))
    )
    observed = observe_lock_wait(writer.wait(), holder_pid=pid, finished=blocking.done)
    judge.wait(observed, required=False)
    judge.expect(not observed.observed, "the block waited on the read")
    try:
        # The provider call is still held: a block that waited on the read would time out.
        blocked = blocking.result(timeout=budget.WAIT_OBSERVATION_SECONDS)
    finally:
        call.release.set()
    judge.outcome(blocked, "a block by the other member during the provider call", "applied")
    read = reading.result(timeout=budget.HOLD_SECONDS)
    judge.outcome(as_result(read), "the read", "refused", reasons=BLOCK_REFUSALS)
    judge.note(f"the block committed while the provider call was held; reader backend {state}")


# -- the named cases --------------------------------------------------------------------------


def order_follows_acceptance(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """DM-22 2.2: a message accepted after a later one reaches the reader's next poll and
    counts as unread."""
    world = _world(phase)
    first = _send(phase, world, world.high, "k-first", "written first")
    second = _send(phase, world, world.high, "k-second", "written second")
    phase.provider.fail_next("send_message")  # the first message's first attempt fails
    retried = phase.delivery.deliver_due(limit=10)
    judge.expect(
        [(d.event_type, d.outcome) for d in retried] == [("message_submitted", "retry")],
        f"the first delivery: {[(d.event_type, d.outcome) for d in retried]}",
    )
    # A deliverer that does not hold a retried event at the head (a worker with backoff,
    # DM-20's note) delivers the later message first.
    delivered = phase.delivery._deliver(_event_id(second))
    judge.expect(delivered is not None and delivered.outcome == "delivered", f"{delivered}")
    reads = phase.reads()
    page = reads.read_history(_request(world))
    judge.outcome(as_result(page), "the reader's poll", "read")
    judge.expect(_texts(page) == ["written second"], f"page {_texts(page)}")
    listed = reads.list_conversations(world.session_low)
    unread = {e.match_id: e.unread for e in listed.conversations}.get(world.match)
    judge.expect(unread == 1, f"unread {unread}, expected 1")
    moved = reads.move_read_cursor(ReadCursorCommand(world.session_low, world.match, second))
    judge.outcome(as_result(moved), "the reader reads up to the later message", "moved")
    judge.expect(moved.entry is not None and moved.entry.unread == 0, f"{moved.entry}")
    _deliver(phase)  # now the first message is accepted, after the second
    first_at, first_seq = _event_times(first)
    second_at, second_seq = _event_times(second)
    judge.expect(
        first_at > second_at and first_seq < second_seq,
        f"not forced: first accepted {first_at} seq {first_seq}, second {second_at} {second_seq}",
    )
    newer = page.page.newer if page.page is not None else None
    poll = reads.read_history(_request(world, cursor=newer))
    judge.outcome(as_result(poll), "the reader's next poll", "read")
    judge.expect(_texts(poll) == ["written first"], f"next poll {_texts(poll)}")
    listed = reads.list_conversations(world.session_low)
    unread = {e.match_id: e.unread for e in listed.conversations}.get(world.match)
    judge.expect(unread == 1, f"unread after the late acceptance {unread}, expected 1")
    whole = reads.read_history(_request(world))
    judge.expect(_texts(whole) == ["written second", "written first"], f"order {_texts(whole)}")
    judge.note(
        "accepted in the order second, first (written first, second); the first reached the"
        " next poll and counted as unread"
    )


def pages_and_cursors(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """Older and newer pages by opaque cursors; the member's own pending and failed
    submissions on the newest page only, to that member only; "anything new?" with no new
    message makes no provider call."""
    from glow_domain.chat_provider import PROVIDER_REJECTED

    world = _world(phase)
    for i in range(7):
        _send(phase, world, world.high if i % 2 == 0 else world.low, f"k{i}", f"message {i}")
    _deliver(phase)
    reads = phase.reads()
    newest = reads.read_history(_request(world, limit=3))
    judge.expect(_texts(newest) == [f"message {i}" for i in (4, 5, 6)], f"{_texts(newest)}")
    assert newest.page is not None
    older = reads.read_history(_request(world, cursor=newest.page.older, limit=3))
    judge.expect(_texts(older) == [f"message {i}" for i in (1, 2, 3)], f"{_texts(older)}")
    assert older.page is not None
    oldest = reads.read_history(_request(world, cursor=older.page.older, limit=3))
    judge.expect(_texts(oldest) == ["message 0"], f"{_texts(oldest)}")
    judge.expect(
        oldest.page is not None and oldest.page.older is None, "an older cursor at the start"
    )
    calls = _read_calls(phase)
    nothing = reads.read_history(_request(world, cursor=newest.page.newer))
    judge.expect(
        nothing.page is not None
        and nothing.page.messages == ()
        and not nothing.page.provider_called
        and nothing.page.newer == newest.page.newer
        and _read_calls(phase) == calls,
        f"anything new: {nothing}",
    )
    own = _send(phase, world, world.low, "k-pending", "the reader's pending")
    _send(phase, world, world.high, "k-other-pending", "the other member's pending")
    head = reads.read_history(_request(world, limit=3))
    assert head.page is not None
    last = head.page.messages[-1]
    judge.expect(
        (last.submission_id, last.own, last.delivery, last.text)
        == (own, True, "pending", "the reader's pending"),
        f"own pending {last}",
    )
    judge.expect("the other member's pending" not in _texts(head), "the other's pending shown")
    calls = _read_calls(phase)
    polled = reads.read_history(_request(world, cursor=newest.page.newer))
    judge.expect(
        polled.page is not None
        and [m.delivery for m in polled.page.messages] == ["pending"]
        and _read_calls(phase) == calls,
        f"a poll with only the reader's pending: {polled}",
    )
    judge.expect(
        older.page is not None and all(m.delivery == "accepted" for m in older.page.messages),
        "an older page carries an unsent submission",
    )
    other_head = reads.read_history(_request(world, reader=world.high, limit=3))
    judge.expect(
        "the reader's pending" not in _texts(other_head)
        and "the other member's pending" in _texts(other_head),
        f"the other member's head {_texts(other_head)}",
    )
    phase.provider.fail_next("send_message", code=PROVIDER_REJECTED)  # the reader's, first
    _deliver(phase)
    after = reads.read_history(_request(world, limit=3))
    assert after.page is not None
    states = [(m.own, m.delivery, m.text) for m in after.page.messages]
    judge.expect(
        states[-1] == (True, "failed", "the reader's pending")
        and (False, "accepted", "the other member's pending") in states,
        f"after delivery {states}",
    )
    other_after = reads.read_history(_request(world, reader=world.high, limit=3))
    judge.expect("the reader's pending" not in _texts(other_after), "the reader's failed is shown")


def only_text_glow_sent(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """DM-22 2.1: a text altered by one character, a deleted message, a ``system`` and an
    ``error`` message are unavailable and counted; a planted message never appears."""
    world = _world(phase)
    labels = ("exact", "altered", "deleted", "system", "error")
    sent = {
        label: _send(phase, world, world.high, f"k-{label}", f"the {label} text")
        for label in labels
    }
    _deliver(phase)
    m = _models()
    channel = m.ChatBinding.objects.get(match_id=world.match).channel_ref
    refs = {
        label: m.MessageSubmission.objects.get(pk=sid).provider_message_ref
        for label, sid in sent.items()
    }
    phase.provider.edit_message(channel, refs["altered"], text="the altered texT")
    phase.provider.delete_message(channel, refs["deleted"])
    phase.provider.edit_message(channel, refs["system"], kind="system")
    phase.provider.edit_message(channel, refs["error"], kind="error")
    phase.provider.plant_message(channel, "0" * 32, "a provider notice Glow never sent")
    read = phase.reads().read_history(_request(world))
    judge.outcome(as_result(read), "the read", "read")
    judge.expect(_texts(read) == ["the exact text", None, None, None, None], f"{_texts(read)}")
    counted = read.page.reconciliation if read.page is not None else None
    judge.expect(
        counted is not None
        and (counted.missing, counted.mismatched, counted.unrequested) == (3, 1, 0),
        f"reconciliation {counted}",
    )
    judge.expect(
        all(t != "a provider notice Glow never sent" for t in _texts(read)), "a planted text shown"
    )


def provider_error_fails_the_read(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """DM-22 2.4: a provider error fails the read with Glow's code, never a page in which
    every message is unavailable; no provider text is kept."""
    from glow_domain.chat_provider import CHANNEL_UNAVAILABLE, PROVIDER_REJECTED

    world = _conversation(phase)
    reads = phase.reads()
    for code, text, wanted, retryable in (
        ("provider_unavailable", "fixture failure", "provider_unavailable", True),
        (None, PROVIDER_TEXT, "provider_unavailable", True),
        (PROVIDER_REJECTED, "fixture failure", PROVIDER_REJECTED, False),
        (CHANNEL_UNAVAILABLE, "fixture failure", CHANNEL_UNAVAILABLE, False),
    ):
        phase.provider.fail_next("read_message_texts", code=code, text=text)
        read = reads.read_history(_request(world))
        judge.outcome(
            as_result(read),
            f"a read whose provider call fails ({code})",
            "refused",
            reasons={wanted},
        )
        judge.expect(read.page is None and read.retryable == retryable, f"{read}")
        judge.expect(PROVIDER_TEXT not in repr(read), "provider text in the result")
    read = reads.read_history(_request(world))
    judge.outcome(as_result(read), "a read after the outages", "read")


def cursor_bound_to_match(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """DM-22 6.4: a cursor from another match is refused; so is one naming a message of
    another match, or a message that is not accepted."""
    a, b = _conversation(phase), _conversation(phase)
    reads = phase.reads()
    page_a = reads.read_history(_request(a))
    assert page_a.page is not None and page_a.page.newer is not None
    reasons = {"cursor_invalid"}
    foreign = reads.read_history(_request(b, cursor=page_a.page.newer))
    judge.outcome(as_result(foreign), "a cursor from another match", "refused", reasons=reasons)
    forged = PageCursor("older", b.match, page_a.page.messages[0].submission_id)
    judge.outcome(
        as_result(reads.read_history(_request(b, cursor=forged))),
        "a cursor naming another match's message",
        "refused",
        reasons=reasons,
    )
    pending = _send(phase, b, b.low, "k-pending", "not yet accepted")
    judge.outcome(
        as_result(reads.read_history(_request(b, cursor=PageCursor("newer", b.match, pending)))),
        "a cursor naming a pending submission",
        "refused",
        reasons=reasons,
    )
    _deliver(phase)
    judge.outcome(
        as_result(reads.read_history(_request(a, cursor=page_a.page.newer))),
        "the cursor on its own match",
        "read",
    )


def reads_write_nothing(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """DM-22 2.3: no row is written by a history read or the list, by what PostgreSQL holds
    (every row's ``xmin``), whether the read is served, refused or fails at the provider."""
    world = _conversation(phase)
    outsider = _conversation(phase)
    reads = phase.reads()
    before = fingerprint()
    page = reads.read_history(_request(world))
    reads.read_history(_request(world, cursor=page.page.newer if page.page else None))
    reads.list_conversations(world.session_low)
    reads.read_history(HistoryRequest(outsider.session_low, world.match))
    phase.provider.fail_next("read_message_texts")
    reads.read_history(_request(world))
    after = fingerprint()
    changed = sorted(table for table in WRITABLE_TABLES if before[table] != after[table])
    judge.expect(not changed, f"rows written by a read: {changed}")
    judge.outcome(as_result(page), "the read", "read")
    judge.note(f"{sum(c for c, _ in after.values())} rows unchanged across five reads and a list")


def no_text_in_logs(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """DM-22 2.5: no message text in any log line from the text read, the history read or
    the list, with every logger at DEBUG and Django's SQL log on."""
    world = _world(phase)
    secrets_ = ("SECRET-OTHER-TEXT", "SECRET-OWN-TEXT", "SECRET-PENDING-TEXT")
    other = _send(phase, world, world.high, "k-1", secrets_[0])
    _send(phase, world, world.low, "k-2", secrets_[1])
    _deliver(phase)
    _send(phase, world, world.low, "k-3", secrets_[2])
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    root, sql = logging.getLogger(), logging.getLogger("django.db.backends")
    handler = Capture(level=logging.DEBUG)
    saved = (root.level, sql.level, connection.force_debug_cursor)
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    sql.setLevel(logging.DEBUG)
    connection.force_debug_cursor = True
    try:
        reads = phase.reads()
        read = reads.read_history(_request(world))
        reads.list_conversations(world.session_low)
        reads.move_read_cursor(ReadCursorCommand(world.session_low, world.match, other))
        phase.provider.fail_next("read_message_texts", code=None, text=secrets_[0])
        reads.read_history(_request(world))
    finally:
        root.removeHandler(handler)
        root.setLevel(saved[0])
        sql.setLevel(saved[1])
        connection.force_debug_cursor = saved[2]
    judge.outcome(as_result(read), "the read", "read")
    judge.expect(
        set(secrets_) <= set(_texts(read)), f"the page did not carry the texts: {_texts(read)}"
    )
    sql_lines = sum(r.name == "django.db.backends" for r in records)
    judge.expect(sql_lines > 0, "the capture saw no SQL log line")
    leaked = [
        r.name
        for r in records
        if any(s in f"{r.getMessage()} {r.args!r} {r.exc_text or ''}" for s in secrets_)
    ]
    judge.expect(not leaked, f"message text in log lines from {sorted(set(leaked))}")
    judge.note(f"{len(records)} log records captured ({sql_lines} SQL), none with a message text")


def unread_and_read_cursor(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """Point e and DM-22 6.3: the read cursor moves only forward, to an accepted message of
    the match, for a member who passes the checks; unread counts only the other member's
    accepted messages after it; the other member's cursor is never returned."""
    world = _world(phase)
    others = [_send(phase, world, world.high, f"k-o{i}", f"from the other {i}") for i in range(3)]
    own = _send(phase, world, world.low, "k-own", "from the reader")
    _deliver(phase)
    reads = phase.reads()

    def unread(reader: UUID) -> int | None:
        listed = reads.list_conversations(world.session_of(reader))
        return {e.match_id: e.unread for e in listed.conversations}.get(world.match)

    def move(target: UUID) -> Any:
        return reads.move_read_cursor(ReadCursorCommand(world.session_low, world.match, target))

    judge.expect(unread(world.low) == 3, f"unread {unread(world.low)}, expected 3")
    judge.outcome(as_result(move(others[1])), "to the other's second message", "moved")
    judge.expect(unread(world.low) == 1, f"unread {unread(world.low)}, expected 1")
    judge.outcome(as_result(move(others[0])), "back to the first: not forward", "no_change")
    judge.outcome(as_result(move(others[1])), "the same again: a repeat", "no_change")
    judge.expect(unread(world.low) == 1, f"unread {unread(world.low)} after no change")
    judge.outcome(as_result(move(own)), "to the reader's own, later message", "moved")
    judge.expect(unread(world.low) == 0, f"unread {unread(world.low)}, expected 0")
    judge.expect(unread(world.high) == 1, f"the other member's unread {unread(world.high)}")
    pending = _send(phase, world, world.low, "k-pending", "not accepted yet")
    judge.outcome(
        as_result(move(pending)),
        "to a pending submission",
        "refused",
        reasons={"message_unavailable"},
    )
    elsewhere = _conversation(phase)
    foreign = (
        _models()
        .MessageSubmission.objects.filter(binding__match_id=elsewhere.match)
        .values_list("id", flat=True)
        .first()
    )
    judge.outcome(
        as_result(move(foreign)),
        "to another match's message",
        "refused",
        reasons={"message_unavailable"},
    )
    cursors = list(
        _models()
        .ChatReadCursor.objects.filter(match_id=world.match)
        .values_list("account_id", "last_read_id")
    )
    judge.expect(cursors == [(world.low, own)], f"cursor rows {cursors}")
    moved = move(own)
    judge.expect(
        moved.entry is not None and set(vars(moved.entry)) == {"match_id", "unread", "latest"},
        f"the command's entry {moved.entry}",
    )
    judge.outcome(
        ctx.subject.block(world.high, world.low), "a block by the other member", "applied"
    )
    judge.outcome(
        as_result(move(others[2])),
        "a cursor move after the block",
        "refused",
        reasons=BLOCK_REFUSALS,
    )


def conversation_list(phase: ReadPhase, ctx: Context, judge: Judge) -> None:
    """Item 4 and DM-22 6.1: the member's conversations from Glow's rows, with no provider
    call; the marker only over rows the member may see; a conversation the member may no
    longer see is not listed."""
    first = _conversation(phase)
    third = ctx.fixtures.create_account()
    second_match = ctx.fixtures.create_match(*sorted((first.low, third)))
    _deliver(phase)
    signed = ctx.subject.sign_in(third, ttl_seconds=300.0)
    if signed.session_id is None:
        raise ReadCheckFailed(f"fixture sign-in failed: {signed.label()}")
    low, high = sorted((first.low, third))
    sessions = {first.low: first.session_low, third: signed.session_id}
    second = World(low, high, second_match, sessions[low], sessions[high])
    newest = _send(phase, second, third, "k-third", "the newest conversation")
    _deliver(phase)
    reads = phase.reads()
    calls = len(phase.provider.calls)
    listed = reads.list_conversations(first.session_low)
    judge.outcome(as_result(listed), "the reader's list", "listed")
    order = [e.match_id for e in listed.conversations]
    judge.expect(order == [second.match, first.match], f"list order {order}")
    markers = {e.match_id: e.latest for e in listed.conversations}
    marker = markers.get(first.match)
    pending = _send(phase, first, first.high, "k-pending", "the other member's pending")
    relisted = reads.list_conversations(first.session_low)
    judge.expect(
        {e.match_id: e.latest for e in relisted.conversations}.get(first.match) == marker,
        "the other member's pending moved the reader's marker",
    )
    other_list = reads.list_conversations(first.session_high)
    other_marker = {e.match_id: e.latest for e in other_list.conversations}.get(first.match)
    judge.expect(
        other_marker is not None and other_marker.submission_id == pending,
        f"the sender's own marker {other_marker}",
    )
    judge.expect(
        markers.get(second.match) is not None and markers[second.match].submission_id == newest,
        f"marker {markers.get(second.match)}",
    )
    judge.expect(len(phase.provider.calls) == calls, "the list called the provider")
    state = ctx.state_subject
    judge.outcome(state.pause_profile(third), "a pause of the third member's profile", "applied")
    paused = [e.match_id for e in reads.list_conversations(first.session_low).conversations]
    judge.expect(paused == [first.match], f"listed while the other is paused: {paused}")
    judge.outcome(state.resume_profile(third), "resume", "applied")
    judge.outcome(ctx.subject.block(first.high, first.low), "a block in the first match", "applied")
    blocked = [e.match_id for e in reads.list_conversations(first.session_low).conversations]
    judge.expect(blocked == [second.match], f"listed after the block: {blocked}")
    judge.outcome(ctx.subject.sign_out(first.session_low), "the reader signs out", "applied")
    judge.outcome(
        as_result(reads.list_conversations(first.session_low)),
        "a list after the sign-out",
        "refused",
        reasons={"session_not_valid"},
    )


# -- the plan --------------------------------------------------------------------------------

FORCED: tuple[tuple[str, str, Callable[..., None]], ...] = (
    (
        "read_waits",
        "committed while the read waits between its provider call and its final check: refused",
        read_waits,
    ),
    (
        "check_holds",
        "arrives while the final check holds its shared locks: waits, and the page is returned",
        check_holds,
    ),
    (
        "revocation_holds",
        "already holds its locks when the final check takes them: the check waits, and the read"
        " is refused",
        revocation_holds,
    ),
)
NAMED: tuple[tuple[str, str, str, Callable[..., None]], ...] = (
    (
        "read.block_during_provider_call",
        "DM-22 3.2 no lock across the provider call",
        "a block commits during the provider call with no wait recorded; the read is refused",
        block_during_provider_call,
    ),
    (
        "read.order_follows_acceptance",
        "DM-22 2.2 the order follows visibility",
        "a message accepted after a later one reaches the next poll and counts as unread",
        order_follows_acceptance,
    ),
    (
        "read.pages_and_cursors",
        "point b pages and cursors",
        "older and newer pages; the member's own unsent on the newest page only; no provider"
        " call for nothing new",
        pages_and_cursors,
    ),
    (
        "read.only_text_glow_sent",
        "DM-22 2.1 only text Glow sent is shown",
        "an altered, a deleted, a system and an error message are unavailable and counted",
        only_text_glow_sent,
    ),
    (
        "read.provider_error_fails_the_read",
        "DM-22 2.4 a provider error fails the read",
        "each provider failure refuses the read with Glow's code",
        provider_error_fails_the_read,
    ),
    (
        "read.cursor_bound_to_match",
        "DM-22 6.4 the cursor is bound to its match",
        "a cursor from another match, or naming another match's or a pending message, is refused",
        cursor_bound_to_match,
    ),
    (
        "read.reads_write_nothing",
        "DM-22 2.3 a read writes nothing",
        "every row's xmin is unchanged across reads, a refused read, a failed read and a list",
        reads_write_nothing,
    ),
    (
        "read.no_text_in_logs",
        "DM-22 2.5 no message text in a log line",
        "every logger at DEBUG and the SQL log on through reads, a list and a cursor move",
        no_text_in_logs,
    ),
    (
        "read.unread_and_read_cursor",
        "point e and DM-22 6.3 unread and the read cursor",
        "forward only, idempotent, to an accepted message of the match, after the checks",
        unread_and_read_cursor,
    ),
    (
        "read.conversation_list",
        "item 4 and DM-22 6.1 the conversation list",
        "no provider call; the marker over visible rows only; a conversation no longer visible"
        " not listed",
        conversation_list,
    ),
)
REVOCATIONS_READ: tuple[Revocation, ...] = (*REVOCATIONS, *D5_REVOCATIONS)
CONTROL_TARGET = "read.block_by_high.read_waits"


def _guarantee(rev: Revocation) -> str:
    return f"P06.2 C1 point c: no history after {rev.kind} (DM-22 3.2)"


def cases_for(phase: ReadPhase) -> tuple[Case, ...]:
    """Every read case, bound to ``phase``: the forced cases per revocation, then the
    named cases."""
    forced = [
        Case(
            f"read.{rev.id}.{name}",
            _guarantee(rev),
            f"{rev.title} {title}",
            partial(lambda run, rev, ctx, judge: run(rev, phase, ctx, judge), run, rev),
        )
        for rev in REVOCATIONS_READ
        for name, title, run in FORCED
    ]
    named = [
        Case(
            case_id, guarantee, title, partial(lambda run, ctx, judge: run(phase, ctx, judge), run)
        )
        for case_id, guarantee, title, run in NAMED
    ]
    return (*forced, *named)


def plan() -> list[dict[str, str]]:
    """The read phase's case plan, offline: id, guarantee and title of every case."""
    placeholder = ReadPhase(None, None, None)  # type: ignore[arg-type]
    return [
        {"id": c.id, "guarantee": c.guarantee, "title": c.title} for c in cases_for(placeholder)
    ]


# -- the planted controls (DM-22 3.3) --------------------------------------------------------


def final_check_skipped(texts: Any) -> Any:
    """A read variant from the adapter's own steps with the final check left out."""
    from glow_chat.reads import OrmConversationReads

    class FinalCheckSkipped(OrmConversationReads):  # type: ignore[misc]
        def read_history(self, request: Any, *, probe: Any = None) -> Any:
            probe = probe or ReadProbe()
            selected, refused, _ = self._first_check(request, probe)
            if selected is None:
                return refused
            texts, failure = self._provider_texts(selected, probe)
            if failure:
                return ReadResult("refused", failure)
            return ReadResult("read", page=self._page(request, selected, texts, True))

    return FinalCheckSkipped(texts)


def final_check_before_call(texts: Any) -> Any:
    """A read variant from the adapter's own steps with the final check before the
    provider call."""
    from glow_chat.reads import OrmConversationReads

    class FinalCheckBeforeCall(OrmConversationReads):  # type: ignore[misc]
        def read_history(self, request: Any, *, probe: Any = None) -> Any:
            probe = probe or ReadProbe()
            selected, refused, _ = self._first_check(request, probe)
            if selected is None:
                return refused
            outcome, reason, _ = self._final_check(request, probe)
            if outcome != "ok":
                return ReadResult("refused", reason)
            texts, failure = self._provider_texts(selected, probe)
            if failure:
                return ReadResult("refused", failure)
            return ReadResult("read", page=self._page(request, selected, texts, True))

    return FinalCheckBeforeCall(texts)


@dataclass(frozen=True)
class ReadControl:
    id: str
    variant: str
    make_reads: Callable[[Any], Any]
    signal: Signal = Signal(case=frozenset({REFUSAL_MISSING}))


READ_CONTROLS: tuple[ReadControl, ...] = (
    ReadControl("read.final_check_skipped", "broken: the final check skipped", final_check_skipped),
    ReadControl(
        "read.final_check_before_call",
        "broken: the final check before the provider call",
        final_check_before_call,
    ),
)


def run_read_control(phase: ReadPhase, control: ReadControl) -> ControlResult:
    """The control's variant must fail the forced case "committed while the read waits"
    by a missing refusal, in this run."""
    broken = replace(phase, make_reads=control.make_reads)
    target = next(case for case in cases_for(broken) if case.id == CONTROL_TARGET)
    phase.ctx.log.context = LogContext(run_tag=f"control:{control.id}", variant="adapter:planted")
    result: CaseResult = run_case(broken.ctx, target)
    met = control.signal.met(result.signals, ())
    signal = "; ".join(result.failures) or "the case passed under the broken variant"
    if not met:
        signal = f"not the declared signal (case signals {sorted(result.signals)}): {signal}"
    return ControlResult(
        control.id,
        "DM-22 3.3 the forced case can fail",
        "planted",
        CONTROL_TARGET,
        control.variant,
        met,
        signal,
        case=result,
        declared=control.signal.describe(),
    )


def run_read_phase(ctx: Context) -> ReadReport:
    """Every read case on the adapter, then the planted controls, each under its own run
    tag, with this phase's own fixture provider."""
    from glow_chat.delivery import OutboxDelivery

    provider = FixtureChatProvider(environment="test")
    phase = ReadPhase(ctx, provider, OutboxDelivery(provider))
    report = ReadReport()
    started = time.monotonic()
    ctx.log.context = LogContext(run_tag="read:forced", variant="adapter")
    for case in cases_for(phase):
        report.cases.append(run_case(ctx, case))
    for control in READ_CONTROLS:
        report.controls.append(run_read_control(phase, control))
    report.seconds = time.monotonic() - started
    return report
