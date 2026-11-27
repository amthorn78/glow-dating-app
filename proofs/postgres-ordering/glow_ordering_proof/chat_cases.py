"""The chat cases (SV4 A2; its brief's D8 to D10, with D3 to D6 through the routes, and A1's
review's AR-12 and AR-13), each run through the HTTP endpoints with Django's test client on the
disposable chat database, signed in through SV1's identity routes, built through SV2's member
routes and matched through SV3's like.

Every case makes its own synthetic members and begins with no other ``visible`` profile
(``DiscoveryContext.hide_everyone``, as the discovery suite's cases do). The routes are called with
no enclosing transaction and autocommit on, as Django's ``TransactionTestCase`` calls them; no
Django ``TestCase`` is used, since every read refuses its atomic block (``transactions.*`` shows
it; the P11 plan's R4). Each case declares the checks it covers and returns a short detail line
or raises ``CaseFailed``; neither ever holds a member's value or a message's text.

**The order.** ``chat.history`` cannot be made more readable under the launch consent version (SV2's
D2): a cause published ``hidden`` stays hidden for the rest of the run. So every case that needs a
cause read-only runs first, and the three cases that read or publish a cause ``hidden``
(``ar13.*``, ``d5.each_cause_hidden`` and ``reads.session_ended_in_locks_answers_as_hidden``) run
last, in that order. SV4 B1's cases (``notifications.*``: F12's devices and settings through F12's
routes; its brief's D16 to D20 and D29) run just before them, and read no conversation.

Rows written only in setup (a seeded population and its matches, an active block beside an active
match, a withdrawn consent with a visible profile, an ``incomplete`` profile) are test data, named
where a case writes each, never an application writer.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from uuid import UUID, uuid4

from glow_ordering_proof.chat_support import (
    CONVERSATIONS,
    DEVICE,
    HISTORY,
    HOLD_SECONDS,
    MATCHES,
    MESSAGES,
    NOTIFICATION_SETTINGS,
    NOTIFICATIONS,
    REACH_SECONDS,
    READ_CURSOR,
    BeginHold,
    ChatContext,
    Hold,
    commit_answer_lost,
    handle_write_fails,
    lock_statements,
    provider,
    route_reads,
    session_of,
    token_store,
)
from glow_ordering_proof.identity_support import CaseFailed, Member, Reply, expect


@dataclass(frozen=True)
class Case:
    case_id: str
    checks: tuple[str, ...]
    run: Callable[[ChatContext], str]


CASES: list[Case] = []
# The suite's case count, pinned: a case lost or added without this changing fails the run before
# any case runs, and the offline tests.
CASE_COUNT = 37


def case(
    case_id: str, *checks: str
) -> Callable[[Callable[[ChatContext], str]], Callable[[ChatContext], str]]:
    def register(function: Callable[[ChatContext], str]) -> Callable[[ChatContext], str]:
        CASES.append(Case(case_id, checks, function))
        return function

    return register


# -- helpers --------------------------------------------------------------------------------


def _chat() -> Any:
    from glow_profiles import operations

    return operations.chat()


def _outcome(reply: Reply) -> tuple[int, str]:
    body = reply.body or {}
    if reply.status == 200:
        data = body.get("data") or {}
        return 200, str(data.get("state", data.get("kind", "")))
    return reply.status, str(body.get("code"))


def _refused(ctx: ChatContext, reply: Reply, status: int, code: str, what: str) -> None:
    ctx.profiles.refused(reply, status, code, what)


def _error_body(reply: Reply) -> str:
    """The refusal's body without its request ID, for comparing two refusals."""
    return json.dumps(
        {k: v for k, v in (reply.body or {}).items() if k != "request_id"}, sort_keys=True
    )


def _last_headers(ctx: ChatContext) -> str:
    return str(ctx.profiles.headers[-1])


def _pair(ctx: ChatContext) -> tuple[Member, Member, Any]:
    first, second = ctx.visible(), ctx.visible()
    return first, second, ctx.matched(first, second)


def _internal_send_reason(member: Member, match_id: Any, version: int = 1) -> str:
    """The send's own reason for the same state, through ``glow_chat``'s ``send`` (the route
    serves one code for it; the reason is the adapter's, never served)."""
    from glow_domain.chat import SendCommand

    result = _chat().send(
        SendCommand(session_of(member), UUID(str(match_id)), version, f"k{uuid4().hex}", "x" * 10)
    )
    return str(result.reason or result.outcome)


def _visibility(ctx: ChatContext, member: Member, action: str) -> None:
    from glow_ordering_proof.discovery_cases import _visibility as visibility

    visibility(ctx.discovery, member, action)


def _unmatch(ctx: ChatContext, actor: Member, match: Any) -> None:
    from glow_ordering_proof.interaction_cases import _unmatch as unmatch

    _, reply = unmatch(ctx.discovery, actor, match)
    ctx.profiles.data(reply, "match", "the unmatch")


def _block(ctx: ChatContext, actor: Member, target: Member, action: str = "block") -> None:
    from glow_ordering_proof.interaction_cases import _block as block

    _, reply = block(ctx.discovery, actor, target, action)
    ctx.profiles.data(reply, "block", f"the {action}")


def _like(ctx: ChatContext, actor: Member, target: Member) -> dict[str, Any]:
    from glow_ordering_proof.interaction_cases import _act

    return _act(ctx.discovery, actor, target, "like")


def _text_reads() -> int:
    return sum(1 for call in provider().calls if call.operation == "read_message_texts")


def _publish_history(ctx: ChatContext, **changes: str) -> None:
    from glow_domain import profile_settings as ps

    content = ctx.discovery.current(ps.HISTORY)
    content.update(changes)
    ctx.discovery.publish(ps.HISTORY, content)


def _waiting_on(holder_pid: int, ended: Callable[[], bool]) -> int | None:
    """The backend that waits on ``holder_pid``'s lock, read from ``pg_stat_activity`` on this
    thread's own connection, or ``None`` if none waits before ``ended`` or the reach time."""
    import threading
    import time

    from django.db import connection

    deadline = time.monotonic() + REACH_SECONDS
    pause = threading.Event()
    with connection.cursor() as cursor:
        while time.monotonic() < deadline and not ended():
            cursor.execute(
                "SELECT pid FROM pg_stat_activity WHERE %s = ANY(pg_blocking_pids(pid))",
                [holder_pid],
            )
            row = cursor.fetchone()
            if row is not None:
                return int(row[0])
            pause.wait(0.01)
    return None


def _while_held(
    writer: Callable[[Hold], Any], route: Callable[[], Reply], what: str
) -> tuple[Reply, Any]:
    """``writer`` holds its transaction at its commit, with its row locked; the route's request,
    made then, passes SV1's door (which reads with no lock, so sees the row as it stood) and waits
    on that row at its own lock (observed in ``pg_stat_activity``); the writer then commits, and
    the route reads the row as the writer left it. Returns the route's reply and the writer's
    result."""
    from glow_ordering_proof.discovery_cases import _Worker
    from glow_ordering_proof.observe import observe_lock_wait

    held = Hold("before_commit")
    holder = _Worker(partial(writer, held))
    request = _Worker(route)
    waited = None
    try:
        holder.start()
        expect(held.reached["before_commit"].wait(REACH_SECONDS), f"{what}: the writer holds it")
        request.start()
        assert held.pid is not None
        pid = _waiting_on(held.pid, request.ended)
        if pid is not None:
            waited = observe_lock_wait(
                pid, holder_pid=held.pid, finished=request.ended, timeout=REACH_SECONDS
            )
    finally:
        held.free()
        expect(holder.done(HOLD_SECONDS + 30) and request.done(HOLD_SECONDS + 30), "both ended")
    expect(waited is not None and waited.observed, f"{what}: the route waited on the writer")
    expect(holder.error is None and request.error is None, f"{what}: neither raised")
    expect(isinstance(request.result, Reply), f"{what}: the route answered")
    return request.result, holder.result


def _ended_in_locks(
    ctx: ChatContext, member: Member, route: Callable[[], Reply], what: str
) -> Reply:
    """The member's session ends once the route's request has passed SV1's door and before its
    session lock: ``glow_chat``'s sign-out (the session row, ``FOR UPDATE``) is held at its commit
    while the request waits on that row, so the route finds the session revoked once it holds its
    locks (A2R-2; DM-99's AK1 and AK2)."""
    session = session_of(member)
    reply, signed_out = _while_held(lambda held: _chat().sign_out(session, probe=held), route, what)
    expect(signed_out is not None and signed_out.outcome == "applied", f"{what}: signed out")
    return reply


def _account_suspended_as_test_data(account_id: Any, held: Hold) -> int:
    """Test data inside a held transaction: the account ``suspended`` with its session left
    ``valid`` at its epoch, a state no writer leaves (a suspension also moves the epoch). The list's
    own-account check is the one it reaches, as a real writer's would be: the list checks its own
    account before the session's state, expiry and epoch, so a suspension or a deletion that
    commits after the request has passed SV1's door, and before the list's account lock is
    granted, reaches the check too (A2-C1's delta review, F1; DM-100)."""
    from django.db import connection, transaction
    from glow_persistence.models import AppAccount

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_backend_pid()")
            held.on_begin(int(cursor.fetchone()[0]))
        changed = AppAccount.objects.filter(pk=account_id).update(state="suspended")
        assert held.before_commit is not None
        held.before_commit()
    return int(changed)


# -- 1. the routes refuse what is not their DTO (D8) ----------------------------------------------


@case("routes.refuse_what_is_not_their_dto", "D8", "SV1 actor")
def routes_refuse(ctx: ChatContext) -> str:
    """Each route answers its DTO to a signed-in member and refuses, as the contract's ``Error``
    naming a code and never a value, with nothing cached: no token or a refused token (401); a
    body that is not its DTO, a field naming an actor, a query string or another content type
    (400); another method (405). The list and the match list refuse a body and a query string."""
    one, two, match = _pair(ctx)
    submission = ctx.sent(one, match.id)
    bodies = {
        MESSAGES: ctx.message(one, match.id),
        HISTORY: {"match_id": str(match.id), "cursor": None, "limit": 50},
        READ_CURSOR: {
            "operation": "read_cursor",
            "match_id": str(match.id),
            "submission_id": submission,
        },
    }
    count = 0
    for path, body in bodies.items():
        what = path.rsplit("/", 1)[1]
        call = partial(ctx.profiles.call, one)
        for name, bearer in (("no token", False), ("a refused token", "not-a-token")):
            # Each reply's own headers (A2R-8): the challenge checked on the no-token reply too.
            reply = call("POST", path, body, bearer=bearer)
            _refused(ctx, reply, 401, "unauthenticated", f"{what}: {name}")
            expect(
                "WWW-Authenticate: Bearer" in _last_headers(ctx), f"{what}: {name}: the challenge"
            )
        for name, sent in (
            ("an extra field", {**body, "extra": "x"}),
            ("a session field", {**body, "session_id": str(uuid4())}),
            ("an actor field", {**body, "actor_id": str(two.account_id)}),
        ):
            _refused(ctx, call("POST", path, sent), 400, "invalid_request", f"{what}: {name}")
        _refused(ctx, call("POST", path + "?x=1", body), 400, "invalid_request", f"{what}: query")
        _refused(
            ctx,
            call("POST", path, body, content_type="text/plain"),
            400,
            "invalid_request",
            f"{what}: content type",
        )
        for method in ("GET", "PUT", "PATCH", "DELETE"):
            _refused(ctx, call(method, path, body), 405, "invalid_request", f"{what}: {method}")
            expect("Cache-Control: no-store" in _last_headers(ctx), f"{what}: no-store")
        count += 1
    for path in (CONVERSATIONS, MATCHES):
        what = path.rsplit("/", 1)[1]
        call = partial(ctx.profiles.call, one)
        _refused(ctx, call("GET", path, {"x": 1}), 400, "invalid_request", f"{what}: a body")
        _refused(ctx, call("GET", path + "?state=open"), 400, "invalid_request", f"{what}: query")
        _refused(ctx, call("POST", path, {}), 405, "invalid_request", f"{what}: POST")
        _refused(ctx, call("GET", path, bearer=False), 401, "unauthenticated", f"{what}: token")
        count += 1
    ctx.conversations(one)
    expect("Cache-Control: no-store" in _last_headers(ctx), "a served list is not cached")
    ctx.history(one, match.id)
    expect("Cache-Control: no-store" in _last_headers(ctx), "a served page is not cached")
    return f"{count} routes refuse what is not their DTO, each as the contract's Error"


# -- 2. the send, its replay and its conflict (D8, D6) -----------------------------------------


@case("send.replay_conflict_and_version", "D8", "D6", "F11")
def send_replay(ctx: ChatContext) -> str:
    """A send answers ``MessageSubmission`` (pending), with the match read's version as its
    expected version (D6); the same intent replays the same submission, its state the current one;
    the same key with another text is ``idempotency_conflict``; another version answers the one
    code, ``not_found``, as every stopped send does (A2-C1; DM-99); neither writes; once contact
    has ended the replay is refused the same way."""
    from glow_persistence.models import MessageSubmission

    one, two, match = _pair(ctx)
    expect(ctx.match_version(one, match.id) == 1, "the match read's version is 1")
    body = ctx.message(one, match.id)
    first = ctx.profiles.data(ctx.send(one, body), "message", "the send")
    expect(first["state"] == "pending" and first["version"] == 1, "the send is pending")
    replay = ctx.profiles.data(ctx.send(one, body), "message", "the replay")
    expect(replay == first, "the same intent replays the same submission")
    ctx.deliver()
    accepted = ctx.profiles.data(ctx.send(one, body), "message", "the replay after delivery")
    expect(
        accepted["submission_id"] == first["submission_id"] and accepted["state"] == "accepted",
        "a replay after delivery is the same submission, accepted",
    )
    rows = MessageSubmission.objects.filter(actor_id=one.account_id).count()
    _refused(
        ctx,
        ctx.send(one, {**body, "text": ctx.text()}),
        409,
        "idempotency_conflict",
        "the same key with another text",
    )
    for version in (0, 2):
        _refused(
            ctx,
            ctx.send(one, ctx.message(one, match.id, expected=version)),
            404,
            "not_found",
            f"the version {version}",
        )
    expect(
        MessageSubmission.objects.filter(actor_id=one.account_id).count() == rows,
        "the refused sends wrote nothing",
    )
    other = ctx.sent(two, match.id)
    page = ctx.history(one, match.id)
    expect(
        [(m["submission_id"], m["author"]) for m in page["messages"]]
        == [(first["submission_id"], "own"), (other, "other")],
        "both sends, in acceptance order",
    )
    _unmatch(ctx, two, match)
    _refused(ctx, ctx.send(one, body), 404, "not_found", "the replay after the unmatch")
    return (
        "pending, replayed, accepted; conflict and wrong version refused, none written; ended: 404"
    )


# -- 3. history, list and read cursor for both members (D8, D5) ----------------------------------


@case("reads.history_list_and_cursor_for_both", "D8", "D5", "F11")
def reads_for_both(ctx: ChatContext) -> str:
    """Both members read the history, each their own side; pages and cursors follow acceptance;
    the list shows each the other's unread messages and the latest marker; each member's read
    cursor moves forward only, and neither member's move changes the other's unread count; a
    cursor or a message of another match is refused; the member's own pending
    message is theirs alone; no served body carries a provider's identifier."""
    from glow_persistence.models import ChatBinding, MessageSubmission

    one, two, match = _pair(ctx)
    sent = [ctx.sent(one, match.id), ctx.sent(two, match.id), ctx.sent(one, match.id)]
    sent += [ctx.sent(two, match.id), ctx.sent(one, match.id)]
    authors = ["own", "other", "own", "other", "own"]
    for member, mine in ((one, authors), (two, [_flip(a) for a in authors])):
        page = ctx.history(member, match.id)
        expect(
            [m["submission_id"] for m in page["messages"]] == sent, "the order follows acceptance"
        )
        expect([m["author"] for m in page["messages"]] == mine, "each member's own side")
        expect(
            [m["text"] for m in page["messages"]] == [ctx.texts[s] for s in sent],
            "only text Glow sent is shown",
        )
        expect(
            all(m["content"] == "text" for m in page["messages"])
            and [m["delivery"] for m in page["messages"]]
            == ["accepted" if a == "own" else None for a in mine],
            "the delivery state for the member's own messages only",
        )
    # Pages of two, following the older cursor to the end, then polling the newer one.
    newest = ctx.history(one, match.id, limit=2)
    seen = [m["submission_id"] for m in newest["messages"]]
    expect(seen == sent[3:] and newest["older_cursor"] is not None, "the newest page of two")
    cursor = newest["older_cursor"]
    while cursor is not None:
        older = ctx.history(one, match.id, cursor, limit=2)
        seen = [m["submission_id"] for m in older["messages"]] + seen
        cursor = older["older_cursor"]
    expect(seen == sent, "the older pages, to the end")
    polled = ctx.history(one, match.id, newest["newer_cursor"], limit=2)
    expect(polled["messages"] == [], "nothing newer yet")
    listed = ctx.conversations(one)[str(match.id)]
    expect(
        listed["state"] == "open"
        and listed["unread_count"] == 2
        and listed["latest"]["submission_id"] == sent[-1],
        "the list: open, the other's two unread, the latest marker",
    )
    expect(ctx.conversations(two)[str(match.id)]["unread_count"] == 3, "the other's side")
    moved = ctx.cursor(one, match.id, sent[3])
    expect(moved["state"] == "open" and moved["unread_count"] == 0, "the cursor moves")
    again = ctx.cursor(one, match.id, sent[1])
    expect(again["unread_count"] == 0, "a cursor behind the current one changes nothing")
    # Each member's cursor is their own (D10; DM-99's AK11): the other's move changes neither
    # member's unread count but the mover's.
    expect(ctx.conversations(two)[str(match.id)]["unread_count"] == 3, "the other's unread kept")
    theirs = ctx.cursor(two, match.id, sent[2])
    expect(theirs["state"] == "open" and theirs["unread_count"] == 1, "the other's cursor moves")
    behind = ctx.cursor(two, match.id, sent[0])
    expect(behind["unread_count"] == 1, "the other's cursor behind changes nothing")
    expect(ctx.conversations(one)[str(match.id)]["unread_count"] == 0, "the first's unread kept")
    expect(ctx.conversations(two)[str(match.id)]["unread_count"] == 1, "the other's own count")
    # Another match's message and page cursor are refused.
    three, four, other_match = _pair(ctx)
    foreign = ctx.sent(three, other_match.id)
    _refused(ctx, ctx.cursor_reply(one, match.id, foreign), 404, "not_found", "another's message")
    foreign_page = ctx.history(three, other_match.id, limit=1)
    expect(foreign_page["newer_cursor"] is not None, "the other match's cursor")
    _refused(
        ctx,
        ctx.history_reply(one, match.id, foreign_page["newer_cursor"]),
        409,
        "stale_version",
        "another match's page cursor",
    )
    # The member's own pending message is theirs alone.
    body = ctx.message(two, match.id)
    pending = ctx.profiles.data(ctx.send(two, body), "message", "an undelivered send")
    own_page = ctx.history(two, match.id)
    expect(
        own_page["messages"][-1]["submission_id"] == pending["submission_id"]
        and own_page["messages"][-1]["delivery"] == "pending"
        and own_page["messages"][-1]["text"] == body["text"],
        "the sender sees their own pending message",
    )
    expect(
        pending["submission_id"]
        not in [m["submission_id"] for m in ctx.history(one, match.id)["messages"]],
        "the other member never sees it",
    )
    expect(
        ctx.conversations(one)[str(match.id)]["latest"]["submission_id"] == sent[-1],
        "nor in their latest marker",
    )
    ctx.deliver()
    # No served body carries a provider's identifier.
    refs = {
        *ChatBinding.objects.exclude(channel_ref=None).values_list("channel_ref", flat=True),
        *MessageSubmission.objects.exclude(provider_message_ref=None).values_list(
            "provider_message_ref", flat=True
        ),
    }
    served = json.dumps(ctx.profiles.served)
    expect(refs and not any(str(ref) in served for ref in refs), "no provider ID is served")
    return "both sides read; pages and cursors in acceptance order; each one's cursor; refusals"


def _flip(author: str) -> str:
    return "other" if author == "own" else "own"


# -- 4. the send's refusals from either member's state answer one code (D8) ---------------------


@case("send.five_refusals_one_code", "D8", "OD-60 H", "D4", "DM-96 AG13")
def five_refusals(ctx: ChatContext) -> str:
    """Each refusal of a send that comes from either member's state or the end of contact
    (``match_not_active``, ``blocked``, ``account_not_active``, ``profile_unavailable``,
    ``consent_not_current``) answers ``not_found``, the same body for each, so a member never
    learns which cause stopped a send; the adapter's own reason for each state differs."""
    from glow_persistence.models import Block

    def unmatched(one: Member, two: Member, match: Any) -> None:
        _unmatch(ctx, two, match)

    def blocked(one: Member, two: Member, match: Any) -> None:
        # Test data: an active block beside an active match, a state no writer leaves (a block
        # ends an active match as an unmatch does, D4), so the send's block check is reached.
        Block.objects.create(actor_id=two.account_id, target_id=one.account_id, state="active")

    def suspended(one: Member, two: Member, match: Any) -> None:
        expect(_chat().suspend(two.account_id).outcome == "applied", "the suspension")

    def deleted(one: Member, two: Member, match: Any) -> None:
        expect(_chat().delete(two.account_id).outcome == "applied", "the deletion")

    def paused(one: Member, two: Member, match: Any) -> None:
        _visibility(ctx, two, "pause")

    def own_paused(one: Member, two: Member, match: Any) -> None:
        _visibility(ctx, one, "pause")

    def restricted(one: Member, two: Member, match: Any) -> None:
        expect(_chat().restrict_profile(two.account_id).outcome == "applied", "the restriction")

    def withdrawn(one: Member, two: Member, match: Any) -> None:
        from glow_ordering_proof.interaction_cases import _seed_withdrawn_consent

        # Test data: a withdrawal with the profile left visible (SV2's withdrawal hides it), so
        # the consent check is reached on its own.
        _seed_withdrawn_consent(two)

    causes: list[tuple[str, Callable[[Member, Member, Any], None], str]] = [
        ("the unmatch", unmatched, "match_not_active"),
        ("the block", blocked, "blocked"),
        ("the other's suspension", suspended, "account_not_active"),
        ("the other's deletion", deleted, "account_not_active"),
        ("the other's pause", paused, "profile_unavailable"),
        ("the sender's own pause", own_paused, "profile_unavailable"),
        ("the other's restriction", restricted, "profile_unavailable"),
        ("the other's withdrawn consent", withdrawn, "consent_not_current"),
    ]
    bodies = set()
    reasons = set()
    for name, apply, reason in causes:
        one, two, match = _pair(ctx)
        ctx.sent(one, match.id)
        apply(one, two, match)
        reply = ctx.send(one, ctx.message(one, match.id, expected=1))
        _refused(ctx, reply, 404, "not_found", name)
        bodies.add(_error_body(reply))
        found = _internal_send_reason(one, match.id)
        expect(found == reason, f"{name}: the adapter's own reason ({found})")
        reasons.add(found)
    expect(len(bodies) == 1, "every refusal answers the same body")
    expect(len(reasons) == 5, "five reasons, one code")
    return f"{len(causes)} causes, {len(reasons)} internal reasons, one served code (not_found)"


# -- 5. each D5 cause read-only at launch (D5, D9) ----------------------------------------------


def _cause_writers(ctx: ChatContext) -> list[tuple[str, Callable[[Member, Member], None]]]:
    """Each D5 cause (OD-60 H's five keys; SV2's ``incomplete`` read as a pause), applied with the
    reader first and the other member second."""
    from glow_persistence.models import Profile

    def incomplete(member: Member) -> None:
        # Test data: an incomplete profile (a lost requirement), as A1's read phase writes it.
        Profile.objects.filter(account_id=member.account_id).update(state="incomplete")

    def withdraw(member: Member) -> None:
        ctx.profiles.data(ctx.profiles.withdraw_onboarding(member), "onboarding", "withdrawal")

    def withdrawn_alone(member: Member) -> None:
        # A2's review, A2R-6 (taken by SV4 B1): SV2's withdrawal also makes the profile
        # ``incomplete``, so the two causes above are a pause too. Test data: a withdrawal with the
        # profile left visible (``interaction_cases._seed_withdrawn_consent``), so the withdrawn
        # consent is the conversation's one cause, and a read rule that ignored it would fail.
        from glow_ordering_proof.interaction_cases import _seed_withdrawn_consent

        _seed_withdrawn_consent(member)

    return [
        ("own_pause", lambda reader, other: _visibility(ctx, reader, "pause")),
        ("other_pause", lambda reader, other: _visibility(ctx, other, "pause")),
        ("own_incomplete", lambda reader, other: incomplete(reader)),
        ("other_incomplete", lambda reader, other: incomplete(other)),
        ("own_restriction", lambda reader, other: _ok(_chat().restrict_profile(reader.account_id))),
        (
            "other_restriction",
            lambda reader, other: _ok(_chat().restrict_profile(other.account_id)),
        ),
        ("other_suspension", lambda reader, other: _ok(_chat().suspend(other.account_id))),
        ("own_withdrawal", lambda reader, other: withdraw(reader)),
        ("other_withdrawal", lambda reader, other: withdraw(other)),
        ("own_withdrawal_alone", lambda reader, other: withdrawn_alone(reader)),
        ("other_withdrawal_alone", lambda reader, other: withdrawn_alone(other)),
    ]


def _ok(result: Any) -> None:
    expect(result.outcome == "applied", f"the writer applies ({result.outcome})")


@case("d5.each_cause_read_only", "D5", "D9", "OD-60 H")
def each_cause_read_only(ctx: ChatContext) -> str:
    """At launch every cause reads ``read_only``: the history page is served, the list serves the
    conversation as ``read_only`` with its count and marker kept, the read cursor moves and answers
    ``read_only``, the match list still holds the match, and the send is refused with the one
    code; before the cause the conversation is ``open``."""
    done = []
    for name, apply in _cause_writers(ctx):
        reader, other, match = _pair(ctx)
        theirs = ctx.sent(other, match.id)
        ctx.sent(reader, match.id)
        before = ctx.conversations(reader)[str(match.id)]
        expect(before["state"] == "open" and before["unread_count"] == 1, f"{name}: open before")
        apply(reader, other)
        page = ctx.history(reader, match.id)
        expect(len(page["messages"]) == 2, f"{name}: the history is served")
        listed = ctx.conversations(reader).get(str(match.id))
        expect(
            listed is not None
            and listed["state"] == "read_only"
            and listed["unread_count"] == 1
            and listed["latest"] is not None,
            f"{name}: listed read_only, its count and marker kept",
        )
        moved = ctx.cursor(reader, match.id, theirs)
        expect(
            moved["state"] == "read_only" and moved["unread_count"] == 0,
            f"{name}: the cursor moves, read_only",
        )
        _refused(
            ctx,
            ctx.send(reader, ctx.message(reader, match.id)),
            404,
            "not_found",
            f"{name}: the send is refused",
        )
        expect(
            [m["match_id"] for m in ctx.match_list(reader)["matches"]] == [str(match.id)],
            f"{name}: the match list still holds it",
        )
        done.append(name)
    return f"{len(done)} causes read_only at launch: served, listed, cursor; send refused"


# -- 6. unmatch, block and deletion hidden (D5) ----------------------------------------------


@case("ended.unmatch_block_deletion_hidden", "D5", "D9", "OD-12", "OD-60 H")
def ended_hidden(ctx: ChatContext) -> str:
    """After an unmatch, a block or the other member's deletion, neither member can send or see the
    conversation: the history and the cursor are ``not_found``, the list and the match list leave
    it out, and the send answers the one code."""

    def unmatch(one: Member, two: Member, match: Any) -> None:
        _unmatch(ctx, two, match)

    def block(one: Member, two: Member, match: Any) -> None:
        _block(ctx, two, one)

    def delete(one: Member, two: Member, match: Any) -> None:
        _ok(_chat().delete(two.account_id))

    count = 0
    for name, end, both in (
        ("unmatch", unmatch, True),
        ("block", block, True),
        ("deletion", delete, False),
    ):
        one, two, match = _pair(ctx)
        submission = ctx.sent(two, match.id)
        end(one, two, match)
        for member in (one, two) if both else (one,):
            who = f"{name}, {'the reader' if member is one else 'the ender'}"
            _refused(ctx, ctx.history_reply(member, match.id), 404, "not_found", f"{who}: history")
            _refused(
                ctx,
                ctx.cursor_reply(member, match.id, submission),
                404,
                "not_found",
                f"{who}: cursor",
            )
            _refused(
                ctx,
                ctx.send(member, ctx.message(member, match.id)),
                404,
                "not_found",
                f"{who}: send",
            )
            expect(str(match.id) not in ctx.conversations(member), f"{who}: not listed")
            expect(
                str(match.id) not in [m["match_id"] for m in ctx.match_list(member)["matches"]],
                f"{who}: not in the match list",
            )
            count += 1
    return f"unmatch, block and deletion hide the conversation ({count} members checked)"


# -- 7. D4's sameness for the member who did not block --------------------------------------------


@case("d4.block_and_unmatch_serve_the_same", "D4", "DM-75", "DM-96", "F13")
def d4_sameness(ctx: ChatContext) -> str:
    """What a member who did not block is served on every chat surface and the match routes (the
    send, the history, the list, the read cursor, the match read and the match list) is the same
    after a block as after an unmatch, and stays so after the blocker's unblock and unmatch."""
    blocked, blocker, blocked_match = _pair(ctx)
    unmatched, ender, unmatched_match = _pair(ctx)
    one = ctx.sent(blocked, blocked_match.id)
    ctx.sent(blocker, blocked_match.id)
    two = ctx.sent(unmatched, unmatched_match.id)
    ctx.sent(ender, unmatched_match.id)
    _block(ctx, blocker, blocked)
    _unmatch(ctx, ender, unmatched_match)
    expected = {
        "send": (404, "not_found"),
        "history": (404, "not_found"),
        "listed": None,
        "cursor": (404, "not_found"),
        "match": (200, "unmatched", 2),
        "match_list": 0,
    }
    steps = 0

    def compare(step: str) -> None:
        nonlocal steps
        after_block = ctx.surfaces(blocked, blocked_match.id, one)
        after_unmatch = ctx.surfaces(unmatched, unmatched_match.id, two)
        expect(
            after_block == after_unmatch, f"{step}: the same ({after_block} and {after_unmatch})"
        )
        expect(after_block == expected, f"{step}: as an ended match ({after_block})")
        steps += 1

    compare("after the block and the unmatch")
    _block(ctx, blocker, blocked, "unblock")
    compare("after the blocker's unblock")
    from glow_ordering_proof.interaction_cases import _unmatch as unmatch_route

    _, again = unmatch_route(ctx.discovery, blocker, blocked_match)
    _, again_other = unmatch_route(ctx.discovery, ender, unmatched_match)
    expect(
        _outcome(again) == _outcome(again_other) == (200, "unmatched"),
        "the enders' later unmatch answers the same",
    )
    compare("after the blocker's unmatch")
    return f"{steps} steps, every surface the same after a block as after an unmatch"


# -- 8. D3's retired likes, through the routes ----------------------------------------------------


@case("d3.retired_likes_make_no_conversation", "D3", "C-01", "F09")
def d3_retired(ctx: ChatContext) -> str:
    """A like made before a block between the pair, by either member, never makes a match: the
    later like is recorded with no match, and neither member has a match or a conversation."""
    done = 0
    for by_liker in (True, False):
        liker, liked = ctx.visible(), ctx.visible()
        _like(ctx, liker, liked)
        blocker, blocked = (liker, liked) if by_liker else (liked, liker)
        _block(ctx, blocker, blocked)
        _block(ctx, blocker, blocked, "unblock")
        later = _like(ctx, liked, liker)
        expect(later["state"] == "liked" and later["match_id"] is None, "recorded, no match")
        for member in (liker, liked):
            expect(ctx.match_list(member)["matches"] == [], "no match listed")
            expect(ctx.conversations(member) == {}, "no conversation")
        done += 1
    return f"{done} retired likes (a block by the liker and by the liked) made no conversation"


# -- 9. the match list (D9) ---------------------------------------------------------------------


@case("match_list.active_matches_newest_first", "D9", "F09")
def match_list(ctx: ChatContext) -> str:
    """A member's ``MatchList``: the matches the member may still see, each a ``MatchProjection``
    served ``active``, equal to the match read's, newest first; an unmatched match and one whose
    other member's account is being deleted are left out; another member's match is never
    listed; a member with no match lists none."""
    member = ctx.visible()
    others = [ctx.visible() for _ in range(4)]
    matches = [ctx.matched(member, other) for other in others]
    _unmatch(ctx, others[2], matches[2])
    _ok(_chat().delete(others[3].account_id))
    listed = ctx.match_list(member)["matches"]
    expect(
        [m["match_id"] for m in listed] == [str(matches[1].id), str(matches[0].id)],
        "the active matches, newest first",
    )
    for entry, other in zip(listed, (others[1], others[0]), strict=True):
        expect(entry["state"] == "active" and entry["version"] == 1, "served active")
        expect(entry["other_profile_id"] == ctx.discovery.profile_id(other), "the other's profile")
        read = ctx.profiles.data(ctx.match_read(member, entry["match_id"]), "match", "the read")
        expect(read == entry, "each entry is the match read's projection")
    theirs = ctx.match_list(others[0])["matches"]
    expect([m["match_id"] for m in theirs] == [str(matches[0].id)], "the other member's own list")
    expect(ctx.match_list(ctx.visible())["matches"] == [], "a member with no match lists none")
    return "two active of four, newest first; unmatched and deletion left out"


# -- 10. a wrong member's every route is not_found (D8) -------------------------------------------


@case("wrong_member.every_route_not_found", "D8", "F11", "OwnedObjectRequest")
def wrong_member(ctx: ChatContext) -> str:
    """A member who is not a participant is answered ``not_found`` by every route that names the
    match (the send, the history, the read cursor, the match read), and finds it in neither list;
    a match that does not exist answers the same."""
    one, two, match = _pair(ctx)
    submission = ctx.sent(one, match.id)
    stranger = ctx.visible()
    ghost = uuid4()
    for match_id in (match.id, ghost):
        what = "another's match" if match_id == match.id else "no match"
        _refused(
            ctx,
            ctx.send(stranger, ctx.message(stranger, match_id, expected=1)),
            404,
            "not_found",
            f"{what}: send",
        )
        _refused(ctx, ctx.history_reply(stranger, match_id), 404, "not_found", f"{what}: history")
        _refused(
            ctx,
            ctx.cursor_reply(stranger, match_id, submission),
            404,
            "not_found",
            f"{what}: cursor",
        )
        _refused(ctx, ctx.match_read(stranger, match_id), 404, "not_found", f"{what}: match read")
    expect(ctx.conversations(stranger) == {}, "not in the stranger's list")
    expect(ctx.match_list(stranger)["matches"] == [], "not in the stranger's match list")
    expect(len(ctx.history(two, match.id)["messages"]) == 1, "the participants still read it")
    return "another's match and a missing one: not_found on every route, in no list"


# -- 11. no read runs inside a caller's transaction (D8; the P11 plan's R4) ----------------------


@case("transactions.non_atomic_requests", "D8", "R4", "DM-22 3.2")
def non_atomic(ctx: ChatContext) -> str:
    """Chat's views are ``non_atomic_requests``: with ``ATOMIC_REQUESTS`` on, each still answers,
    since no request transaction wraps it. Inside a caller's transaction (an atomic block, or a
    Django test case's), every read refuses before any statement, with no provider call, so no
    ``TestCase`` can test these views."""
    from django.db import connection, transaction

    one, two, match = _pair(ctx)
    submission = ctx.sent(two, match.id)
    # The send's body, its version from SV3's match read, built before ATOMIC_REQUESTS is on: that
    # read refuses inside it (A2-C1's resume message; A2R-8: no version is made up for it).
    body = ctx.message(one, match.id)
    settings = connection.settings_dict
    before = settings.get("ATOMIC_REQUESTS")
    settings["ATOMIC_REQUESTS"] = True
    try:
        sent = ctx.profiles.data(ctx.send(one, body), "message", "send")
        page = ctx.history(one, match.id)
        listed = ctx.conversations(one)
        moved = ctx.cursor(one, match.id, submission)
    finally:
        settings["ATOMIC_REQUESTS"] = before
    expect(sent["state"] == "pending", "with ATOMIC_REQUESTS on, the send answers")
    expect(len(page["messages"]) == 2 and str(match.id) in listed, "and the reads answer")
    expect(moved["unread_count"] == 0, "and the cursor moves")
    ctx.deliver()
    calls = _text_reads()
    refused = 0
    blocks: list[tuple[str, Callable[[], Any]]] = [
        ("an atomic block", transaction.atomic),
        ("a test case's block", _test_case_atomic),
    ]
    for name, block in blocks:
        with block():
            replies = [
                ctx.history_reply(one, match.id),
                ctx.conversations_reply(one),
                ctx.cursor_reply(one, match.id, submission),
            ]
        for reply in replies:
            _refused(ctx, reply, 409, "state_conflict", f"inside {name}")
            refused += 1
    expect(_text_reads() == calls, "no provider call inside a caller's transaction")
    return f"answered with ATOMIC_REQUESTS on; {refused} reads refused inside a caller's block"


def _test_case_atomic() -> Any:
    """An atomic block marked as a Django test case's own (``TestCase`` marks its block so)."""
    from django.db import transaction

    block = transaction.atomic()
    block._from_testcase = True
    return block


# -- 12. AR-12: a like committed while a block waits; a match after an unblock --------------------


@case("ar12.like_while_a_block_waits_and_a_match_after_unblock", "AR-12", "D3", "D4", "F09", "F13")
def ar12(ctx: ChatContext) -> str:
    """A1's review's AR-12. A reciprocal like holds both account rows at its commit while a block
    by one member waits on them (observed); the like commits the match, then the block ends it as
    an unmatch does and retires both likes, so no conversation is served. And a pair that blocks and
    unblocks before either likes, then likes each other, makes a match, and chats."""
    from glow_discovery import interactions
    from glow_persistence.models import DirectionalInteraction, Match

    from glow_ordering_proof.discovery_cases import _Worker
    from glow_ordering_proof.interaction_cases import _intent, _match_of
    from glow_ordering_proof.observe import observe_lock_wait

    first, second = ctx.visible(), ctx.visible()
    _like(ctx, first, second)
    page = ctx.discovery.page(second)
    body = _intent(ctx.discovery, second, first, "like", page)
    ctx.profiles.remember(second.account_id, body)
    held, blocking = Hold("before_commit"), Hold()
    like = _Worker(partial(interactions.interact, second.account_id, body, probe=held))
    block = _Worker(partial(_chat().block, first.account_id, second.account_id, probe=blocking))
    waited = None
    try:
        like.start()
        holding = held.reached["before_commit"].wait(REACH_SECONDS)
        block.start()
        pid = blocking.wait_pid()
        assert held.pid is not None
        waited = observe_lock_wait(
            pid, holder_pid=held.pid, finished=block.ended, timeout=REACH_SECONDS
        )
    finally:
        held.free()
        expect(like.done(HOLD_SECONDS + 30) and block.done(HOLD_SECONDS + 30), "both finished")
    expect(holding, "the like held its locks at its commit")
    expect(waited is not None and waited.observed, "the block waited on the like")
    expect(like.result is not None and like.result.outcome == "applied", "the like committed")
    expect(block.result is not None and block.result.outcome == "applied", "then the block")
    match = _match_of(first, second)
    expect(match is not None and Match.objects.get(pk=match.id).state == "unmatched", "ended")
    ctx.deliver()
    retired = DirectionalInteraction.objects.filter(
        actor_id__in=(first.account_id, second.account_id),
        target_id__in=(first.account_id, second.account_id),
        state="liked",
    ).values_list("retired_at", flat=True)
    expect(len(retired) == 2 and all(r is not None for r in retired), "both likes retired")
    for member in (first, second):
        expect(ctx.conversations(member) == {}, "no conversation")
        expect(ctx.match_list(member)["matches"] == [], "no match listed")
        _refused(ctx, ctx.history_reply(member, match.id), 404, "not_found", "no history")
    # A pair that blocks and unblocks before either likes, then likes each other.
    third, fourth = ctx.visible(), ctx.visible()
    _block(ctx, third, fourth)
    _block(ctx, third, fourth, "unblock")
    after = ctx.matched(third, fourth)
    submission = ctx.sent(fourth, after.id)
    expect(
        [m["submission_id"] for m in ctx.history(third, after.id)["messages"]] == [submission],
        "the match made after the unblock chats",
    )
    expect(ctx.conversations(third)[str(after.id)]["state"] == "open", "listed open")
    return (
        "the like committed while the block waited, then the block ended it; a match after unblock"
    )


# -- 13. the list's bounded locks (D8; the P11 plan's C1 finding 4) -------------------------------

POPULATION = 205


@case("list.bounded_locks", "D8", "C1 finding 4", "D9")
def bounded_locks(ctx: ChatContext) -> str:
    """With more active matches than the list's bound, the list reads its candidates (the top 200
    by latest activity) before its first lock, then locks only those, one statement per table:
    the accounts they name, then their matches, then the session. A writer holding an account
    the bound left out does not hold the list up; a writer holding one it kept does, until it
    commits. The match list holds 200, newest first."""
    from django.db.models import Q
    from glow_domain import profile_settings as ps
    from glow_persistence.models import Match

    from glow_ordering_proof.discovery_cases import _Worker
    from glow_ordering_proof.discovery_support import NEW_YORK, seed_population
    from glow_ordering_proof.observe import observe_lock_wait

    member, partner, match = _pair(ctx)
    ctx.sent(partner, match.id)
    # Test data: a seeded population (SV3's plans' seeds) and an active match with each.
    seeded = seed_population(
        POPULATION, (NEW_YORK,), ctx.discovery.current_label(ps.ONBOARDING_CONSENT)
    )
    Match.objects.bulk_create(
        [
            Match(
                account_low_id=min(member.account_id, other),
                account_high_id=max(member.account_id, other),
                state="active",
            )
            for other in seeded
        ]
    )
    seeded_matches = sorted(
        Match.objects.filter(
            Q(account_low_id=member.account_id) | Q(account_high_id=member.account_id),
            state="active",
        )
        .exclude(pk=match.id)
        .values_list("id", flat=True)
    )
    expect(len(seeded_matches) == POPULATION, "the seeded matches")
    kept = {match.id, *seeded_matches[-199:]}
    left_out = set(seeded_matches[:-199])
    pair_of = dict(
        (row[0], {row[1], row[2]})
        for row in Match.objects.filter(pk__in=seeded_matches).values_list(
            "id", "account_low_id", "account_high_id"
        )
    )
    left_out_accounts = {a for m in left_out for a in pair_of[m]} - {member.account_id}
    with lock_statements() as sent:
        listed = ctx.conversations(member)
    expect(len(listed) == 200, f"the list serves 200 ({len(listed)})")
    expect(next(iter(listed)) == str(match.id), "the conversation with a message first")
    expect(set(listed) == {str(m) for m in kept}, "the top 200 by latest activity")
    locks = [(sql, params) for sql, params in sent.statements if "FOR SHARE" in sql.upper()]
    accounts = [p for sql, p in locks if "glow_persistence_appaccount" in sql]
    matches = [p for sql, p in locks if "glow_persistence_match" in sql]
    sessions = [p for sql, p in locks if "glow_persistence_accountsession" in sql]
    expect(len(accounts) == 1 and len(matches) == 1 and len(sessions) == 1, "one per table")
    locked_accounts = {UUID(str(a)) for a in accounts[0][0]}
    locked_matches = {UUID(str(m)) for m in matches[0][0]}
    expect(len(locked_matches) == 200 and locked_matches == kept, "only the bound's matches")
    expect(len(locked_accounts) == 201, f"their accounts and the member's ({len(locked_accounts)})")
    expect(not locked_accounts & left_out_accounts, "no account the bound left out")
    first_lock = next(i for i, sql in enumerate(sent.order) if "FOR SHARE" in sql.upper())
    candidates = [i for i, sql in enumerate(sent.order) if "LIMIT %s" in sql and "latest_at" in sql]
    expect(len(candidates) == 1 and candidates[0] < first_lock, "the candidates read first")
    expect(len(ctx.match_list(member)["matches"]) == 200, "the match list holds 200")
    # A writer holding an account the bound left out does not hold the list up.
    outside = sorted(left_out_accounts)[0]
    held = Hold("after_first_lock")
    writer = _Worker(partial(_chat().pause_profile, outside, probe=held))
    lister = None
    try:
        writer.start()
        expect(held.reached["after_first_lock"].wait(REACH_SECONDS), "the writer holds its row")
        lister = _Worker(lambda: ctx.conversations(member))
        lister.start()
        free = lister.done(REACH_SECONDS)
    finally:
        held.free()
        expect(writer.done(HOLD_SECONDS + 30), "the writer finished")
        if lister is not None:
            expect(lister.done(HOLD_SECONDS + 30), "the list finished")
    expect(free and lister is not None and lister.error is None, "not held up by a left-out row")
    # A writer holding an account the bound kept does, until it commits.
    held, reading = Hold("after_first_lock"), Hold()
    writer = _Worker(partial(_chat().pause_profile, partner.account_id, probe=held))
    reads = route_reads()
    session = session_of(member)
    reader = _Worker(partial(reads.list_conversations, session, probe=reading))
    waited = None
    try:
        writer.start()
        expect(held.reached["after_first_lock"].wait(REACH_SECONDS), "the writer holds its row")
        reader.start()
        pid = reading.wait_pid()
        assert held.pid is not None
        waited = observe_lock_wait(
            pid, holder_pid=held.pid, finished=reader.ended, timeout=REACH_SECONDS
        )
    finally:
        held.free()
        expect(writer.done(HOLD_SECONDS + 30) and reader.done(HOLD_SECONDS + 30), "both finished")
    expect(waited is not None and waited.observed, "the list waited on a kept row's writer")
    expect(reader.result is not None and reader.result.outcome == "listed", "then listed")
    return f"{POPULATION + 1} active matches: 200 candidates locked in one statement per table"


# -- 14. the send under every row of the review's probe table (A2-C1; DM-99's AK2) ---------------


@case("send.one_answer_for_every_version_and_session", "D8", "OD-60 H", "A2R-1", "A2R-2", "AK2")
def send_one_answer(ctx: ChatContext) -> str:
    """A2's exact-head review's probe table, as a case. Under each row (no cause; the other member
    suspended; the other's pause, the own pause, the other's restriction, the other's consent
    withdrawn; an unmatch, a block, the other's deletion), the send with the current version
    (the match read's), with a wrong version (0 and 7) and with a session ended once the send
    holds its locks: every stopped send answers one status, code and body (``not_found``, 404),
    though the adapter's own reasons differ, and writes nothing; with no cause the current
    version is served (200), and the other two answer the same one code."""
    from glow_persistence.models import Block, MessageSubmission

    def suspended(one: Member, two: Member, match: Any) -> None:
        _ok(_chat().suspend(two.account_id))

    def paused(one: Member, two: Member, match: Any) -> None:
        _visibility(ctx, two, "pause")

    def own_paused(one: Member, two: Member, match: Any) -> None:
        _visibility(ctx, one, "pause")

    def restricted(one: Member, two: Member, match: Any) -> None:
        _ok(_chat().restrict_profile(two.account_id))

    def withdrawn(one: Member, two: Member, match: Any) -> None:
        from glow_ordering_proof.interaction_cases import _seed_withdrawn_consent

        # Test data: a withdrawal with the profile left visible, as case 4 writes it.
        _seed_withdrawn_consent(two)

    def unmatched(one: Member, two: Member, match: Any) -> None:
        _unmatch(ctx, two, match)

    def blocked(one: Member, two: Member, match: Any) -> None:
        # Test data: an active block beside an active match, as case 4 writes it.
        Block.objects.create(actor_id=two.account_id, target_id=one.account_id, state="active")

    def deleted(one: Member, two: Member, match: Any) -> None:
        _ok(_chat().delete(two.account_id))

    rows: list[tuple[str, Callable[[Member, Member, Any], None] | None]] = [
        ("no cause", None),
        ("the other member suspended", suspended),
        ("the other's pause", paused),
        ("the own pause", own_paused),
        ("the other's restriction", restricted),
        ("the other's consent withdrawn", withdrawn),
        ("an unmatch", unmatched),
        ("a block", blocked),
        ("the other's deletion", deleted),
    ]
    bodies: set[str] = set()
    reasons: set[str] = set()
    refused = 0
    for name, apply in rows:
        one, two, match = _pair(ctx)
        if apply is not None:
            apply(one, two, match)
        current = ctx.match_version(one, match.id)
        replies: dict[str, Reply] = {}
        if apply is None:
            served = ctx.send(one, ctx.message(one, match.id, expected=current))
            expect(
                ctx.profiles.data(served, "message", f"{name}: the current version")["state"]
                == "pending",
                f"{name}: the current version is served",
            )
        written = MessageSubmission.objects.filter(actor_id=one.account_id).count()
        if apply is not None:
            replies[f"the version {current} (current)"] = ctx.send(
                one, ctx.message(one, match.id, expected=current)
            )
        for version in (0, 7):
            replies[f"the version {version}"] = ctx.send(
                one, ctx.message(one, match.id, expected=version)
            )
        # The adapter's own reason at a wrong version, while the session is valid; never served.
        reasons.add(_internal_send_reason(one, match.id, 0))
        at_current = ctx.message(one, match.id, expected=current)
        replies["a session ended in its locks"] = _ended_in_locks(
            ctx, one, partial(ctx.send, one, at_current), f"{name}: the send"
        )
        expect(
            MessageSubmission.objects.filter(actor_id=one.account_id).count() == written,
            f"{name}: the refused sends wrote nothing",
        )
        for answer, reply in replies.items():
            _refused(ctx, reply, 404, "not_found", f"{name}: {answer}")
            bodies.add(_error_body(reply))
            refused += 1
    expect(len(bodies) == 1, f"one body for every stopped send ({len(bodies)})")
    expect(
        reasons == {"stale_contact_version", "account_not_active", "match_not_active", "blocked"},
        f"the adapter's reasons at version 0 differ ({', '.join(sorted(reasons))})",
    )
    return (
        f"{len(rows)} rows, {refused} stopped sends: one status, code and body (404 not_found);"
        f" the adapter's reasons at version 0: {', '.join(sorted(reasons))}"
    )


# -- 15. the list's own checks, each proven (A2-C1; A2R-3) ----------------------------------------


@case("list.block_session_and_own_account_checks", "D8", "D5", "A2R-3")
def list_checks(ctx: ChatContext) -> str:
    """The served list's checks (``route_reads.RouteConversationReads._list``), each by a case
    that fails without it: an active block beside an active match (test data) is listed to neither
    member; a list whose session ends once the request has passed SV1's door is refused
    ``unauthenticated``; and a list whose account is no longer ``active`` once it holds its locks
    is refused ``not_found`` (``account_not_active``, through ``error_for``, as A1's reads refuse
    it). The last is reached inside a race with SV1's door, here by test data: the list checks its
    own account before the session's state, expiry and epoch (``route_reads.py``), so a real
    suspension or deletion that commits after the request has passed SV1's door, and before the
    list's account lock is granted, reaches it too, and the list answers ``not_found`` (404)
    (A2-C1's delta review, F1; DM-100)."""
    from glow_persistence.models import Block

    one, two, match = _pair(ctx)
    ctx.sent(two, match.id)
    for member in (one, two):
        expect(str(match.id) in ctx.conversations(member), "listed before the block")
    # Test data: an active block beside an active match, a state no writer leaves (D4).
    Block.objects.create(actor_id=two.account_id, target_id=one.account_id, state="active")
    for member in (one, two):
        expect(str(match.id) not in ctx.conversations(member), "a block is listed to neither")
    three, four, other = _pair(ctx)
    expect(str(other.id) in ctx.conversations(three), "listed before the session ends")
    ended = _ended_in_locks(ctx, three, partial(ctx.conversations_reply, three), "the list")
    _refused(ctx, ended, 401, "unauthenticated", "a list whose session ended in its locks")
    five, six, third = _pair(ctx)
    expect(str(third.id) in ctx.conversations(five), "listed before the account changes")
    reply, changed = _while_held(
        partial(_account_suspended_as_test_data, five.account_id),
        partial(ctx.conversations_reply, five),
        "the list's own account",
    )
    expect(changed == 1, "the account row changed (test data)")
    _refused(ctx, reply, 404, "not_found", "a list whose account is not active in its locks")
    return "a block not listed; an ended session and an inactive own account refused, each waited"


# =============================================================================================
# SV4 B1 (its brief's D16 to D20 and D29's B1 cases; DM-101's AM1 to AM7 and AM13): F12's devices
# and notification settings, through F12's three routes, on the chat suite's own database. Each
# case makes its own members (signed in through SV1's routes; F12 needs no profile) and its own
# installations, made at random; every push token comes from the run's pool (``push_token``). They
# run before the cases that read or publish a cause ``hidden``, and read no conversation.
# =============================================================================================


def _f12_member(ctx: ChatContext) -> Member:
    """A verified, signed-in member with an ``active`` account (SV1's routes)."""
    return ctx.profiles.member()


def _registration(account_id: Any, installation: str) -> Any:
    from glow_persistence.models import DeviceRegistration

    return DeviceRegistration.objects.filter(
        account_id=account_id, installation_id=installation
    ).first()


def _pending() -> set[str]:
    from glow_persistence.models import PendingTokenDiscard

    return {
        str(ref) for ref in PendingTokenDiscard.objects.values_list("token_secret_ref", flat=True)
    }


def _token_of(reference: str) -> str | None:
    """The token a reference holds in the suite's store (the fixture's test-only ``resolve``, a
    transport adapter's job, P11B), or ``None`` once discarded. Never logged."""
    from glow_domain.notifications import TokenReference

    found = token_store().fixture.resolve(TokenReference(reference))
    return None if found is None else str(found)


def _references_of(token: str) -> list[str]:
    """Every reference the store issued for ``token`` (a replay's ``put`` issues another)."""
    return [ref for ref in token_store().issued if _token_of(ref) == token]


def _issued_by(call: Callable[[], Any]) -> tuple[Any, list[str]]:
    """``call``'s result, and the references the store issued while it ran, in order (SV4 B1-C1):
    a reference a command discarded resolves to no token any more, so it is found by when it was
    issued, never by its token."""
    before = len(token_store().issued)
    result = call()
    return result, token_store().issued[before:]


def _served(result: Any) -> Any:
    """A command's result as F12's routes serve it: the contract's code and whether it is
    retryable (``glow_notifications.contract.refusal``)."""
    from glow_notifications.contract import refusal  # type: ignore[import-not-found]

    return refusal(result.outcome, result.reason)


def _discarded_at_once(references: list[str]) -> list[tuple[bool, bool]]:
    """For each reference: whether the store no longer holds its token, and whether a pending
    discard is left (SV4 B1-C1; DM-102's AN1: a known outcome discards at once)."""
    pending = _pending()
    return [(_token_of(ref) is None, ref in pending) for ref in references]


def _f12_settings(
    version: int, state: str = "active", match: bool = False, message: bool = False
) -> dict[str, Any]:
    return {
        "kind": "notifications",
        "version": version,
        "match_notifications": match,
        "message_notifications": message,
        "device_state": state,
    }


def _adapter() -> Any:
    """F12's ORM adapter with the suite's token store, for the cases that hold a command at a hold
    point (the routes call it the same way, through the factory hook)."""
    from glow_notifications.persistence import (  # type: ignore[import-not-found]
        OrmNotificationPersistence,
    )

    return OrmNotificationPersistence(tokens=token_store())


def _f12_caller(member: Member, installation: str) -> Any:
    from glow_domain.notifications import Caller

    return Caller(UUID(str(member.account_id)), session_of(member), UUID(installation))


def _held_against(
    writer: Callable[[Hold], Any], call: Callable[[], Any], what: str
) -> tuple[Any, Any]:
    """As ``_while_held``, for a call that is the adapter's own, not a route's: ``writer`` holds
    its transaction at its commit; ``call``, made then, waits on it (observed in
    ``pg_stat_activity``); the writer then commits. Returns the call's result and the writer's."""
    from glow_ordering_proof.discovery_cases import _Worker
    from glow_ordering_proof.observe import observe_lock_wait

    held = Hold("before_commit")
    holder = _Worker(partial(writer, held))
    request = _Worker(call)
    waited = None
    try:
        holder.start()
        expect(held.reached["before_commit"].wait(REACH_SECONDS), f"{what}: the writer holds it")
        request.start()
        assert held.pid is not None
        pid = _waiting_on(held.pid, request.ended)
        if pid is not None:
            waited = observe_lock_wait(
                pid, holder_pid=held.pid, finished=request.ended, timeout=REACH_SECONDS
            )
    finally:
        held.free()
        expect(holder.done(HOLD_SECONDS + 30) and request.done(HOLD_SECONDS + 30), "both ended")
    expect(waited is not None and waited.observed, f"{what}: it waited on the writer")
    expect(holder.error is None and request.error is None, f"{what}: neither raised")
    return request.result, holder.result


# -- B1-1. F12's routes refuse what is not their DTO (D19; AM6) -----------------------------------


@case("notifications.routes_refuse_what_is_not_their_dto", "D19", "AM6", "SV1 actor", "R4")
def notification_routes_refuse(ctx: ChatContext) -> str:
    """Each F12 route answers its DTO to a signed-in member and refuses, as the contract's
    ``Error`` naming a code and never a value, with nothing cached: no token or a refused token
    (401, with the challenge); no ``Glow-Installation-Id`` header, a malformed one, or one that is
    not lower case (400); a body that is not the intent, a field naming an actor, an account, a
    session or (for the settings) an installation, a query string or another content type (400);
    another method (405). The read refuses a body and a query string. No refusal changes the
    registration. On A2's pattern (``transactions.non_atomic_requests``), the views are
    ``non_atomic_requests``: with ``ATOMIC_REQUESTS`` on, each route still answers, since no
    request transaction wraps it; inside a caller's transaction (an atomic block, or a Django test
    case's), each command and the read refuse (``transaction_open``: ``state_conflict``) before
    any statement, and the store takes no token."""
    from django.db import connection, transaction

    member = _f12_member(ctx)
    installation = ctx.installation()
    first = ctx.notifications(ctx.register(member, installation), "the register")
    expect(first == _f12_settings(1), "a first register: version 1, active, both kinds off")
    expect("Cache-Control: no-store" in _last_headers(ctx), "a served answer is not cached")
    bodies = {
        DEVICE: ctx.device_body(installation, "revoke", 1),
        NOTIFICATION_SETTINGS: ctx.settings_body(True, False, 1),
    }
    count = 0
    for path, body in bodies.items():
        what = path.rsplit("/", 1)[1]

        def call(
            sent: Any, header: str | None = installation, path: str = path, **kwargs: Any
        ) -> Reply:
            return ctx.notification_call(member, "POST", path, sent, installation=header, **kwargs)

        for name, bearer in (("no token", False), ("a refused token", "not-a-token")):
            _refused(ctx, call(body, bearer=bearer), 401, "unauthenticated", f"{what}: {name}")
            expect(
                "WWW-Authenticate: Bearer" in _last_headers(ctx), f"{what}: {name}: the challenge"
            )
        for name, header in (
            ("no installation header", None),
            ("an upper-case installation", installation.upper()),
            ("an installation that is not a UUID", "not-an-installation"),
            ("two installations", f"{installation}, {installation}"),
        ):
            _refused(ctx, call(body, header), 400, "invalid_request", f"{what}: {name}")
        extras = [("an extra field", {"extra": "x"}), ("a session field", {"session_id": "s"})]
        extras += [("an actor field", {"actor_id": str(uuid4())})]
        extras += [("an account field", {"account_id": str(member.account_id)})]
        if path == NOTIFICATION_SETTINGS:
            extras += [("an installation field", {"device_id": installation})]
        for name, extra in extras:
            _refused(ctx, call({**body, **extra}), 400, "invalid_request", f"{what}: {name}")
        _refused(
            ctx,
            ctx.notification_call(member, "POST", path + "?x=1", body, installation=installation),
            400,
            "invalid_request",
            f"{what}: a query string",
        )
        _refused(
            ctx,
            call(body, content_type="text/plain"),
            400,
            "invalid_request",
            f"{what}: another content type",
        )
        for method in ("GET", "PUT", "PATCH", "DELETE"):
            reply = ctx.notification_call(member, method, path, body, installation=installation)
            _refused(ctx, reply, 405, "invalid_request", f"{what}: {method}")
            expect("Cache-Control: no-store" in _last_headers(ctx), f"{what}: {method}: no-store")
        count += 1
    read = partial(ctx.notification_call, member)
    _refused(
        ctx,
        read("GET", NOTIFICATIONS, {"x": 1}, installation=installation),
        400,
        "invalid_request",
        "the read: a body",
    )
    _refused(
        ctx,
        read("GET", NOTIFICATIONS + "?state=active", installation=installation),
        400,
        "invalid_request",
        "the read: a query string",
    )
    _refused(
        ctx,
        read("GET", NOTIFICATIONS, installation=None),
        400,
        "invalid_request",
        "the read: no installation header",
    )
    _refused(
        ctx,
        read("POST", NOTIFICATIONS, {}, installation=installation),
        405,
        "invalid_request",
        "the read: POST",
    )
    _refused(
        ctx,
        read("GET", NOTIFICATIONS, installation=installation, bearer=False),
        401,
        "unauthenticated",
        "the read: no token",
    )
    expect("WWW-Authenticate: Bearer" in _last_headers(ctx), "the read: the challenge")
    served = ctx.notifications(ctx.read_settings(member, installation), "the read")
    expect(served == first, "the read serves the registration as it stands")
    expect("Cache-Control: no-store" in _last_headers(ctx), "a served read is not cached")
    row = _registration(member.account_id, installation)
    expect(row is not None and (row.state, row.version) == ("active", 1), "nothing changed it")
    # The views are non_atomic_requests (A2's pattern): with ATOMIC_REQUESTS on, each answers.
    second = ctx.installation()
    settings = connection.settings_dict
    before = settings.get("ATOMIC_REQUESTS")
    settings["ATOMIC_REQUESTS"] = True
    try:
        registered = ctx.notifications(ctx.register(member, second), "ATOMIC_REQUESTS on: register")
        changed = ctx.notifications(
            ctx.save_settings(member, second, True, False, 1), "ATOMIC_REQUESTS on: settings"
        )
        read_on = ctx.notifications(ctx.read_settings(member, second), "ATOMIC_REQUESTS on: read")
    finally:
        settings["ATOMIC_REQUESTS"] = before
    expect(registered == _f12_settings(1), "with ATOMIC_REQUESTS on, the device route answers")
    expect(
        changed == read_on == _f12_settings(2, match=True),
        "with ATOMIC_REQUESTS on, the settings route and the read answer",
    )
    # Inside a caller's transaction, each refuses before any statement, with no put (AM4).
    store = token_store()
    issued = len(store.issued)
    inside = 0
    blocks: list[tuple[str, Callable[[], Any]]] = [
        ("an atomic block", transaction.atomic),
        ("a test case's block", _test_case_atomic),
    ]
    for name, block in blocks:
        with block():
            replies = [
                ctx.register(member, second, 2),
                ctx.save_settings(member, second, False, False, 2),
                ctx.read_settings(member, second),
            ]
        for reply in replies:
            _refused(ctx, reply, 409, "state_conflict", f"inside {name}")
            inside += 1
    expect(len(store.issued) == issued, "the store took no token inside a caller's transaction")
    row = _registration(member.account_id, second)
    expect((row.state, row.version) == ("active", 2), "no refusal inside a block changed it")
    return (
        f"{count + 1} routes refuse what is not their DTO, each as the contract's Error; each"
        f" answers with ATOMIC_REQUESTS on; {inside} refused inside a caller's block"
    )


# -- B1-2. register, rotate, revoke and register again (F12; D17, D18) ----------------------------


@case("notifications.register_rotate_revoke_and_register_again", "D17", "D18", "D19", "F12")
def register_rotate_revoke(ctx: ChatContext) -> str:
    """F12's transitions for one installation of one account, through the device route: a
    register (version 1, the session recorded), a rotation from another session of the account
    (the new session recorded, the old token discarded after the commit), a revoke (the reference
    cleared, ``ended_by`` ``revoke``, the token discarded) and a register again (version 4); each
    answer is the requesting installation's ``NotificationSettings``, the read serves the same, and
    each receipt carries its transition's code."""
    from glow_persistence.models import IdempotencyRecord

    member = _f12_member(ctx)
    installation = ctx.installation()
    tokens = [ctx.push_token() for _ in range(3)]
    first = ctx.notifications(
        ctx.register(member, installation, 0, token=tokens[0]), "the register"
    )
    expect(first == _f12_settings(1), "registered: version 1, active")
    row = _registration(member.account_id, installation)
    expect(
        (row.state, row.ended_by, str(row.session_id)) == ("active", None, str(session_of(member))),
        "the row: active, its session recorded",
    )
    old = str(row.token_secret_ref)
    expect(_token_of(old) == tokens[0], "the row holds the store's reference, never the token")
    # A rotation from a second session of the account: F12's rotate (a register on active).
    phone = Member(
        member.email,
        member.password,
        member.user_id,
        member.account_id,
        ctx.profiles.identity.sign_in(member),
    )
    rotated = ctx.notifications(ctx.register(phone, installation, 1, token=tokens[1]), "rotation")
    expect(rotated == _f12_settings(2), "rotated: version 2, active")
    row = _registration(member.account_id, installation)
    expect(str(row.session_id) == str(session_of(phone)), "the rotating session is recorded")
    expect(_token_of(str(row.token_secret_ref)) == tokens[1], "the new token's reference is held")
    expect(_token_of(old) is None and old not in _pending(), "the old token is discarded")
    expect(
        ctx.notifications(ctx.read_settings(member, installation), "the read") == rotated,
        "the read serves the same",
    )
    second = str(row.token_secret_ref)
    revoked = ctx.notifications(ctx.revoke(member, installation, 2), "the revoke")
    expect(revoked == _f12_settings(3, "revoked"), "revoked: version 3")
    row = _registration(member.account_id, installation)
    expect(
        (row.state, row.ended_by, row.token_secret_ref) == ("revoked", "revoke", None),
        "the row: revoked by the owner, no reference",
    )
    expect(_token_of(second) is None and second not in _pending(), "its token is discarded")
    expect(
        ctx.notifications(ctx.read_settings(member, installation), "the read") == revoked,
        "the read serves the revoked registration",
    )
    again = ctx.notifications(ctx.register(member, installation, 3, token=tokens[2]), "again")
    expect(again == _f12_settings(4), "registered again: version 4, active")
    row = _registration(member.account_id, installation)
    expect((row.state, row.ended_by) == ("active", None), "active again, with no ending")
    codes = list(
        IdempotencyRecord.objects.filter(
            actor_id=member.account_id, operation="notifications.device"
        )
        .order_by("created_at")
        .values_list("outcome_code", flat=True)
    )
    expect(codes == ["register", "rotate", "revoke", "register"], f"the receipts' codes {codes}")
    return "register 1, rotate 2 (from another session), revoke 3, register 4; old tokens discarded"


# -- B1-3. a transfer between accounts (F12; D17's one active row per installation) -------------


@case("notifications.transfer_between_accounts", "D17", "D18", "F12")
def transfer_between_accounts(ctx: ChatContext) -> str:
    """Registering an installation active for another account revokes that account's registration
    of it first, in the same transaction (``ended_by`` ``transfer``, its reference cleared and its
    token discarded), and the earlier account reads its registration ``revoked``; the transfer back
    does the same the other way. One row per account and installation, one ``active``."""
    from glow_persistence.models import DeviceRegistration

    first, second = _f12_member(ctx), _f12_member(ctx)
    installation = ctx.installation()
    ctx.notifications(ctx.register(first, installation), "the first account's register")
    held = str(_registration(first.account_id, installation).token_secret_ref)
    took = ctx.notifications(ctx.register(second, installation, 0), "the transfer")
    expect(took == _f12_settings(1), "the second account registers it: version 1, active")
    row = _registration(first.account_id, installation)
    expect(
        (row.state, row.ended_by, row.token_secret_ref, row.version)
        == ("revoked", "transfer", None, 2),
        "the first account's row: revoked by the transfer, version 2",
    )
    expect(_token_of(held) is None and held not in _pending(), "its token is discarded")
    expect(
        ctx.notifications(ctx.read_settings(first, installation), "the earlier account's read")
        == _f12_settings(2, "revoked"),
        "the earlier account reads its registration revoked",
    )
    back = ctx.notifications(ctx.register(first, installation, 2), "the transfer back")
    expect(back == _f12_settings(3), "the transfer back: the first account's row, version 3")
    row = _registration(second.account_id, installation)
    expect(
        (row.state, row.ended_by, row.version) == ("revoked", "transfer", 2),
        "the second account's row: revoked by the transfer back",
    )
    rows = DeviceRegistration.objects.filter(installation_id=installation)
    expect(rows.count() == 2 and rows.filter(state="active").count() == 1, "two rows, one active")
    return "transferred and back: the earlier account's row revoked each time, one active row"


# -- B1-4. each refusal D19 lists, by its code (D19; AM6) ----------------------------------------


@case("notifications.each_refusal_its_code", "D19", "AM6", "F12")
def each_refusal_its_code(ctx: ChatContext) -> str:
    """D19's codes: another installation's ``device_id`` is ``forbidden``; a stale version
    ``stale_version``; a revoke of no active registration, and a settings change without one,
    ``state_conflict``; the token store's refusal ``provider_unavailable``, retryable, with nothing
    saved; the read of an installation with no registration for the account ``not_found``, another
    account's included. None changes a registration."""
    member = _f12_member(ctx)
    mine, other, fresh = ctx.installation(), ctx.installation(), ctx.installation()
    ctx.notifications(ctx.register(member, mine), "the register")
    elsewhere = ctx.device_body(other, "register", 0, token=ctx.push_token())
    _refused(
        ctx,
        ctx.notification_call(member, "POST", DEVICE, elsewhere, installation=mine),
        403,
        "forbidden",
        "another installation's device_id",
    )
    expect(_registration(member.account_id, other) is None, "the other installation untouched")
    _refused(ctx, ctx.register(member, mine, 5), 409, "stale_version", "a stale version")
    _refused(ctx, ctx.revoke(member, fresh, 0), 409, "state_conflict", "a revoke of none")
    _refused(
        ctx,
        ctx.save_settings(member, fresh, True, True, 0),
        409,
        "state_conflict",
        "settings with no registration",
    )
    _refused(ctx, ctx.read_settings(member, fresh), 404, "not_found", "a read of none")
    ctx.notifications(ctx.revoke(member, mine, 1), "the revoke")
    _refused(ctx, ctx.revoke(member, mine, 2), 409, "state_conflict", "a revoke of a revoked one")
    _refused(
        ctx,
        ctx.save_settings(member, mine, True, False, 2),
        409,
        "state_conflict",
        "settings on a revoked registration",
    )
    store = token_store()
    issued = len(store.issued)
    store.fixture.refuse_next_put()
    refused = ctx.register(member, fresh, 0)
    _refused(ctx, refused, 503, "provider_unavailable", "the token store's refusal")
    expect((refused.body or {}).get("retryable") is True, "the store's refusal is retryable")
    expect(
        _registration(member.account_id, fresh) is None and len(store.issued) == issued,
        "the store's refusal saves nothing and issues no reference",
    )
    stranger = _f12_member(ctx)
    _refused(
        ctx, ctx.read_settings(stranger, mine), 404, "not_found", "another account's installation"
    )
    row = _registration(member.account_id, mine)
    expect((row.state, row.version) == ("revoked", 2), "no refusal changed the registration")
    return "forbidden, stale_version, state_conflict (4), provider_unavailable, not_found (2)"


# -- B1-5. a replay and a conflict (CommandMeta; D18; AM4, AM5) ------------------------------------


@case("notifications.replay_and_conflict", "D18", "AM4", "AM5", "CommandMeta")
def replay_and_conflict(ctx: ChatContext) -> str:
    """The same device intent replays (the current projection, nothing changed); another token
    under the key is ``idempotency_conflict``; each discards the reference the store took for it at
    once, its outcome known, so the store no longer holds its token, no pending discard is left and
    no registration holds it (AM4; B1-C1, DM-102's AN1). The same settings intent under the same key
    replays from its installation and is ``idempotency_conflict`` from another installation of the
    account (AM5: the digest binds the requesting installation)."""
    from glow_persistence.models import DeviceRegistration

    member = _f12_member(ctx)
    installation, phone = ctx.installation(), ctx.installation()
    token = ctx.push_token()
    body = ctx.device_body(installation, "register", 0, token=token, key="f12-replayed")
    device = partial(ctx.notification_call, member, "POST", DEVICE, installation=installation)
    first = ctx.notifications(device(body), "the register")
    row = _registration(member.account_id, installation)
    replied, replayed = _issued_by(partial(device, body))
    replay = ctx.notifications(replied, "the replay")
    expect(replay == first, "the replay serves the current projection")
    after = _registration(member.account_id, installation)
    expect(
        (after.version, after.token_secret_ref) == (row.version, row.token_secret_ref),
        "a replay changes nothing",
    )
    expect(
        len(replayed) == 1 and replayed[0] != row.token_secret_ref,
        "the replay's put issued one more reference",
    )
    other = ctx.device_body(installation, "register", 0, token=ctx.push_token(), key="f12-replayed")
    conflict, conflicted = _issued_by(partial(device, other))
    _refused(ctx, conflict, 409, "idempotency_conflict", "the same key with another token")
    held = set(DeviceRegistration.objects.values_list("token_secret_ref", flat=True))
    for name, refs in (("the replay's", replayed), ("the conflict's", conflicted)):
        expect(
            _discarded_at_once(refs) == [(True, False)] and refs[0] not in held,
            f"{name} reference: the store no longer holds its token, and no pending discard is"
            " left, in no registration",
        )
    ctx.notifications(ctx.register(member, phone), "the second installation's register")
    version = int(first["version"])
    settings = ctx.settings_body(True, False, version, key="f12-settings-replayed")
    changed = ctx.notifications(
        ctx.notification_call(
            member, "POST", NOTIFICATION_SETTINGS, settings, installation=installation
        ),
        "the settings change",
    )
    again = ctx.notifications(
        ctx.notification_call(
            member, "POST", NOTIFICATION_SETTINGS, settings, installation=installation
        ),
        "the settings replay",
    )
    expect(again == changed, "the settings intent replays from its installation")
    # The other installation's registration advanced with the account's settings, so the intent's
    # version is stale there too: a refusal other than idempotency_conflict would tell which
    # check came first, and the digest's binding is what answers.
    expect(_registration(member.account_id, phone).version == version + 1, "the phone advanced")
    _refused(
        ctx,
        ctx.notification_call(member, "POST", NOTIFICATION_SETTINGS, settings, installation=phone),
        409,
        "idempotency_conflict",
        "the same key and body from another installation",
    )
    return "replayed and conflicted, each new reference discarded; another installation conflicts"


# -- B1-6. a settings change advances every registration of the account (P06.3's versions) ------


@case("notifications.settings_advance_every_registration", "D18", "F12")
def settings_advance_every_registration(ctx: ChatContext) -> str:
    """The settings are the account's: a change from one installation advances every registration
    of the account (a revoked one included), the other installation reads the new settings at its
    new version, and its earlier version is ``stale_version``."""
    from glow_persistence.models import NotificationSettings

    member = _f12_member(ctx)
    tablet, phone, old = ctx.installation(), ctx.installation(), ctx.installation()
    for installation in (tablet, phone, old):
        ctx.notifications(ctx.register(member, installation), "a register")
    ctx.notifications(ctx.revoke(member, old, 1), "the third's revoke")
    changed = ctx.notifications(ctx.save_settings(member, tablet, True, False, 1), "the change")
    expect(changed == _f12_settings(2, match=True), "the change: version 2, match on")
    expect(
        ctx.notifications(ctx.read_settings(member, phone), "the phone's read")
        == _f12_settings(2, match=True),
        "the other installation reads the account's settings, advanced",
    )
    expect(_registration(member.account_id, old).version == 3, "the revoked one advanced too")
    _refused(
        ctx,
        ctx.save_settings(member, phone, False, False, 1),
        409,
        "stale_version",
        "the other installation's earlier version",
    )
    from_phone = ctx.notifications(
        ctx.save_settings(member, phone, False, True, 2), "the phone's change"
    )
    expect(from_phone == _f12_settings(3, message=True), "the phone's change: version 3")
    expect(
        ctx.notifications(ctx.read_settings(member, tablet), "the tablet's read")
        == _f12_settings(3, message=True),
        "the tablet reads it at version 3",
    )
    chosen = NotificationSettings.objects.get(account_id=member.account_id)
    expect(
        (chosen.version, chosen.match_notifications, chosen.message_notifications)
        == (2, False, True),
        "the account's settings row: its second revision",
    )
    return "each change advanced all three registrations; the earlier version was stale"


# -- B1-7. the bound of active registrations (D25) --------------------------------------------


@case("notifications.bound_of_active_registrations", "D25", "AM12", "F12")
def bound_of_active_registrations(ctx: ChatContext) -> str:
    """An account holds at most 10 active registrations (provisional, D25): an eleventh is
    ``state_conflict``, with nothing saved and its reference discarded at once, so the store no
    longer holds its token and no pending discard is left (B1-C1, DM-102's AN1); a rotation at the
    bound adds none and is served; once one is revoked, the eleventh registers."""
    from glow_persistence.models import DeviceRegistration

    member = _f12_member(ctx)
    installations = [ctx.installation() for _ in range(10)]
    for installation in installations:
        ctx.notifications(ctx.register(member, installation), "a register below the bound")
    eleventh = ctx.installation()
    token = ctx.push_token()
    reply, issued = _issued_by(partial(ctx.register, member, eleventh, 0, token=token))
    _refused(ctx, reply, 409, "state_conflict", "an eleventh active registration")
    expect(_registration(member.account_id, eleventh) is None, "the eleventh saved nothing")
    expect(
        _discarded_at_once(issued) == [(True, False)],
        "the store no longer holds its token, and no pending discard is left",
    )
    rotated = ctx.notifications(ctx.register(member, installations[0], 1), "a rotation")
    expect(rotated == _f12_settings(2), "a rotation at the bound is served")
    ctx.notifications(ctx.revoke(member, installations[1], 1), "a revoke")
    ctx.notifications(ctx.register(member, eleventh), "the eleventh, after a revoke")
    active = DeviceRegistration.objects.filter(account_id=member.account_id, state="active")
    expect(active.count() == 10, "ten active registrations, the bound")
    return (
        "ten active; the eleventh refused, discarded; a rotation served; after a revoke, registered"
    )


# -- B1-8. a register refused once its session's sign-out commits (AM3, AM4, AM13) ----------------


@case("notifications.register_refused_once_its_sessions_sign_out_commits", "D18", "AM3", "AM4")
def register_refused_once_signed_out(ctx: ChatContext) -> str:
    """A register that reaches its session's row while that session's sign-out holds it (held at
    its commit; the register has passed SV1's door, which reads with no lock, and the store has
    taken its token) waits on that row at its own ``FOR SHARE`` lock (observed), and once the
    sign-out commits it finds the session revoked: ``unauthenticated``, with the challenge (AM6).
    No registration is committed for the ended session, and the token's reference, in no
    registration, is discarded at once, its outcome known: the store no longer holds the token,
    and no pending discard is left (AM4; B1-C1, DM-102's AN1)."""
    from glow_persistence.models import DeviceRegistration

    member = _f12_member(ctx)
    installation = ctx.installation()
    token = ctx.push_token()
    reply, references = _issued_by(
        partial(
            _ended_in_locks,
            ctx,
            member,
            partial(ctx.register, member, installation, 0, token=token),
            "the register",
        )
    )
    _refused(ctx, reply, 401, "unauthenticated", "a register whose session ended in its locks")
    expect("WWW-Authenticate: Bearer" in _last_headers(ctx), "the 401 carries the challenge")
    expect(_registration(member.account_id, installation) is None, "no registration committed")
    held = set(DeviceRegistration.objects.values_list("token_secret_ref", flat=True))
    expect(
        _discarded_at_once(references) == [(True, False)] and references[0] not in held,
        "the store took the token; it no longer holds it, and no pending discard is left",
    )
    return "the register waited on the sign-out, then was refused; its reference discarded"


# -- B1-9. two accounts register one new installation at once (AM13; D17) -------------------------


@case("notifications.two_accounts_one_new_installation", "D17", "D18", "AM13")
def two_accounts_one_installation(ctx: ChatContext) -> str:
    """Two accounts register one new installation at once: the first, held at its commit, has
    written its ``active`` row; the second, through the route, finds no holder and waits at its
    own row on the one-``active``-row constraint (observed); once the first commits, the second is
    ``state_conflict``. One ``active`` row, the first's; none for the second, whose reference is
    discarded at once, its outcome known (a failure inside its transaction): the store no longer
    holds its token, and no pending discard is left (B1-C1, DM-102's AN1)."""
    from glow_persistence.models import DeviceRegistration

    first, second = _f12_member(ctx), _f12_member(ctx)
    installation = ctx.installation()
    body = ctx.device_body(installation, "register", 0, token=ctx.push_token())
    token = ctx.push_token()
    caller = _f12_caller(first, installation)
    (reply, held), issued = _issued_by(
        partial(
            _while_held,
            lambda hold: _adapter().device(caller, body, probe=hold),
            partial(ctx.register, second, installation, 0, token=token),
            "the second account's register",
        )
    )
    expect(held is not None and held.outcome == "applied", "the first account's register")
    _refused(ctx, reply, 409, "state_conflict", "the second account's register")
    rows = DeviceRegistration.objects.filter(installation_id=installation)
    active = [str(row.account_id) for row in rows.filter(state="active")]
    expect(active == [str(first.account_id)], "one active row, the first account's")
    expect(not rows.filter(account_id=second.account_id).exists(), "no row for the second")
    winner = str(_registration(first.account_id, installation).token_secret_ref)
    expect(
        _discarded_at_once([ref for ref in issued if ref != winner]) == [(True, False)],
        "the second's reference: the store no longer holds its token, no pending discard is left",
    )
    return "one active row, the first account's; the second waited, then was refused"


# -- B1-10. a transfer whose other account changes under the locks (AM13; D18) --------------------


@case("notifications.transfer_changed_under_the_locks", "D18", "AM13", "F12")
def transfer_changed_under_the_locks(ctx: ChatContext) -> str:
    """A register reads the installation's holder with no lock, then locks both accounts, the lower
    first. Here a third account's transfer of the installation holds the holder's account row at
    its commit; the register waits on it (observed), and once the transfer commits it finds the
    holder changed under its locks: refused, ``transfer_changed`` (``state_conflict``), never a
    revocation of an account it did not lock. One ``active`` row, the transfer's."""
    from glow_persistence.models import DeviceRegistration

    holder, taker, latecomer = _f12_member(ctx), _f12_member(ctx), _f12_member(ctx)
    installation = ctx.installation()
    ctx.notifications(ctx.register(holder, installation), "the holder's register")
    taking = ctx.device_body(installation, "register", 0, token=ctx.push_token())
    late = ctx.device_body(installation, "register", 0, token=ctx.push_token())
    taker_caller = _f12_caller(taker, installation)
    late_caller = _f12_caller(latecomer, installation)
    result, taken = _held_against(
        lambda hold: _adapter().device(taker_caller, taking, probe=hold),
        lambda: _adapter().device(late_caller, late),
        "the latecomer's register",
    )
    expect(taken is not None and taken.outcome == "applied", "the third account's transfer")
    expect(
        result is not None and (result.outcome, result.reason) == ("refused", "transfer_changed"),
        f"the latecomer: refused, transfer_changed ({getattr(result, 'reason', None)})",
    )
    rows = DeviceRegistration.objects.filter(installation_id=installation)
    active = [str(row.account_id) for row in rows.filter(state="active")]
    expect(active == [str(taker.account_id)], "one active row, the transfer's")
    expect(not rows.filter(account_id=latecomer.account_id).exists(), "no row for the latecomer")
    expect(
        _registration(holder.account_id, installation).ended_by == "transfer",
        "the holder's row ended by the transfer it waited on",
    )
    return "the register waited on the transfer, then refused transfer_changed; one active row"


# -- B1-11. the custody rules are database constraints (D17; AM2) ---------------------------------


@case("notifications.custody_rules_are_constraints", "D17", "AM2", "D25")
def custody_rules_are_constraints(ctx: ChatContext) -> str:
    """Test data, each write in its own atomic block: the database refuses an ``active``
    registration with no reference or an empty one, a ``revoked`` one holding a reference or with
    no ending, an ``active`` one with an ending, an unknown ending, a second ``active`` row for one
    installation, a second row for one account and installation, one reference in two
    registrations, a pending discard twice or empty, a ledger row in another state, and two ledger
    rows for one event and installation."""
    from django.db import IntegrityError, transaction
    from django.utils import timezone
    from glow_persistence.models import (
        DeviceRegistration,
        NotificationLedgerEntry,
        OutboxEvent,
        PendingTokenDiscard,
    )

    member, other = _f12_member(ctx), _f12_member(ctx)
    session, other_session = session_of(member), session_of(other)
    installation = uuid4()
    refused: list[str] = []

    def refuses(what: str, write: Callable[[], Any]) -> None:
        try:
            with transaction.atomic():
                write()
        except IntegrityError:
            refused.append(what)
            return
        raise CaseFailed(f"the database refuses {what}")

    def row(**fields: Any) -> Any:
        base = {
            "account_id": member.account_id,
            "installation_id": installation,
            "session_id": session,
        }
        return lambda: DeviceRegistration.objects.create(**{**base, **fields})

    ref = f"test-data-reference-{uuid4().hex}"
    refuses("an active row with no reference", row(state="active", token_secret_ref=None))
    refuses("an active row with an empty reference", row(state="active", token_secret_ref=""))
    refuses(
        "a revoked row holding a reference",
        row(state="revoked", ended_by="revoke", token_secret_ref=ref),
    )
    refuses("a revoked row with no ending", row(state="revoked", token_secret_ref=None))
    refuses(
        "an active row with an ending", row(state="active", ended_by="logout", token_secret_ref=ref)
    )
    refuses("an unknown ending", row(state="revoked", ended_by="deleted", token_secret_ref=None))
    # Test data: one active row, kept, so the rules that compare rows have one to compare to.
    DeviceRegistration.objects.create(
        account_id=member.account_id,
        installation_id=installation,
        session_id=session,
        state="active",
        token_secret_ref=ref,
    )
    refuses(
        "a second active row for one installation",
        lambda: DeviceRegistration.objects.create(
            account_id=other.account_id,
            installation_id=installation,
            session_id=other_session,
            state="active",
            token_secret_ref=f"test-data-reference-{uuid4().hex}",
        ),
    )
    refuses(
        "a second row for one account and installation",
        row(state="revoked", ended_by="revoke", token_secret_ref=None),
    )
    refuses(
        "one reference in two registrations",
        row(installation_id=uuid4(), state="active", token_secret_ref=ref),
    )
    pending = f"test-data-reference-{uuid4().hex}"
    PendingTokenDiscard.objects.create(token_secret_ref=pending)
    refuses(
        "one reference twice in the pending discards",
        lambda: PendingTokenDiscard.objects.create(token_secret_ref=pending),
    )
    refuses(
        "an empty pending discard", lambda: PendingTokenDiscard.objects.create(token_secret_ref="")
    )
    now = timezone.now()
    event = OutboxEvent.objects.create(
        aggregate_id=uuid4(),
        aggregate_version=1,
        event_type="test_data",
        schema_version="test-data",
        dedup_key=f"test-data:{uuid4().hex}",
        payload_ref=uuid4(),
        state="delivered",
        available_at=now,
        delivered_at=now,
    )
    NotificationLedgerEntry.objects.create(event=event, installation_id=installation)
    refuses(
        "a ledger row in another state",
        lambda: NotificationLedgerEntry.objects.create(
            event=event, installation_id=uuid4(), state="queued"
        ),
    )
    refuses(
        "two ledger rows for one event and installation",
        lambda: NotificationLedgerEntry.objects.create(event=event, installation_id=installation),
    )
    return f"{len(refused)} writes refused by the database's constraints (test data)"


# =============================================================================================
# SV4 B1-C1 (B1's exact-head review, B1R-1 to B1R-3; DM-102's AN1, AN2 and AN11): the new
# reference's handle, written before the command's transaction and consumed by the save; a known
# outcome discards the reference at once, an unknown one leaves the handle to SV4 B2's sweep. Each
# failure is simulated from the suite's side (``chat_support``), with no switch in the adapter.
# They run before ``notifications.no_token_in_any_row_or_answer``, which checks their references.
# =============================================================================================


# -- B1-C1-1. a failed discard waits for the sweep (B1R-3) ----------------------------------------


@case("notifications.a_failed_discard_waits_for_the_sweep", "D18", "B1R-3", "DM-102")
def a_failed_discard_waits(ctx: ChatContext) -> str:
    """B1's review's B1R-3: with the store's discard made to fail once (the fixture's
    ``fail_next_discard``), a rotation, a revoke and a transfer are each served and each leave the
    reference it retired in the pending discards, its token still held by the store, and the
    registration's row without it, for SV4 B2's sweep (D24)."""
    store = token_store().fixture
    member, taker = _f12_member(ctx), _f12_member(ctx)
    installation, other = ctx.installation(), ctx.installation()
    ctx.notifications(ctx.register(member, installation), "the register")
    ctx.notifications(ctx.register(member, other), "the second installation's register")

    def retired_waits(what: str, account: Any, held_at: str, step: Callable[[], Any]) -> None:
        old = str(_registration(account, held_at).token_secret_ref)
        store.fail_next_discard()
        step()
        row = _registration(account, held_at)
        expect(old in _pending(), f"{what}: the retired reference waits in the pending discards")
        expect(_token_of(old) is not None, f"{what}: its token is still held by the store")
        expect(row.token_secret_ref != old, f"{what}: the registration's row no longer holds it")

    retired_waits(
        "the rotation",
        member.account_id,
        installation,
        lambda: ctx.notifications(ctx.register(member, installation, 1), "the rotation"),
    )
    retired_waits(
        "the revoke",
        member.account_id,
        installation,
        lambda: ctx.notifications(ctx.revoke(member, installation, 2), "the revoke"),
    )
    retired_waits(
        "the transfer",
        member.account_id,
        other,
        lambda: ctx.notifications(ctx.register(taker, other, 0), "the transfer"),
    )
    return "a rotation, a revoke and a transfer, each discard failed: each retired one pending"


# -- B1-C1-2. the handle's write fails (B1R-1; AN1) ------------------------------------------------


@case("notifications.a_failed_handle_write_discards_at_once", "D18", "AN1", "B1R-1")
def a_failed_handle_write(ctx: ChatContext) -> str:
    """B1's review's B1R-1, under AN1: the handle's write fails (simulated, ``handle_write_fails``:
    the database unreachable for that one statement), so the store discards the reference at
    once; nothing is saved, no row holds the reference, and the command answers
    ``state_conflict`` (409, not retryable)."""
    from glow_persistence.models import DeviceRegistration

    member = _f12_member(ctx)
    installation = ctx.installation()
    with handle_write_fails() as refused:
        reply, issued = _issued_by(partial(ctx.register, member, installation))
    expect(refused == [1], "the handle's write failed once (simulated)")
    _refused(ctx, reply, 409, "state_conflict", "a register whose handle's write failed")
    expect((reply.body or {}).get("retryable") is False, "not retryable")
    expect(len(issued) == 1, "the store took the token")
    expect(_discarded_at_once(issued) == [(True, False)], "the store discarded it at once")
    expect(
        not DeviceRegistration.objects.filter(token_secret_ref=issued[0]).exists()
        and _registration(member.account_id, installation) is None,
        "nothing saved: no registration holds the reference",
    )
    return "the handle's write failed: the reference discarded at once, no row, state_conflict"


# -- B1-C1-3. a known refusal discards at once (AN1) -----------------------------------------------


@case("notifications.a_known_refusal_discards_at_once", "D18", "AN1", "D25")
def a_known_refusal(ctx: ChatContext) -> str:
    """AN1: a register refused inside its transaction, by a stale version and by the bound (D25),
    and a replay, each with its outcome known, discard the reference the store took for it at once:
    the store no longer holds its token, and no pending discard is left. The saved reference is
    held, and its handle was consumed."""
    member = _f12_member(ctx)
    installations = [ctx.installation() for _ in range(10)]
    first = installations[0]
    body = ctx.device_body(first, "register", 0, token=ctx.push_token())
    device = partial(ctx.notification_call, member, "POST", DEVICE, installation=first)
    ctx.notifications(device(body), "the register")
    for installation in installations[1:]:
        ctx.notifications(ctx.register(member, installation), "a register below the bound")
    seen: dict[str, list[str]] = {}
    reply, seen["a stale version"] = _issued_by(partial(ctx.register, member, first, 5))
    _refused(ctx, reply, 409, "stale_version", "a stale version")
    eleventh = ctx.installation()
    reply, seen["the bound"] = _issued_by(partial(ctx.register, member, eleventh, 0))
    _refused(ctx, reply, 409, "state_conflict", "an eleventh active registration")
    reply, seen["a replay"] = _issued_by(partial(device, body))
    ctx.notifications(reply, "the replay")
    for what, references in seen.items():
        expect(
            _discarded_at_once(references) == [(True, False)],
            f"{what}: the store no longer holds its token, and no pending discard is left",
        )
    saved = str(_registration(member.account_id, first).token_secret_ref)
    expect(
        _token_of(saved) is not None and saved not in _pending(),
        "the saved reference is held, its handle consumed",
    )
    return "a stale version, the bound and a replay: each reference discarded at once"


# -- B1-C1-4. an unknown outcome after the commit (B1R-2; AN1) ------------------------------------


@case("notifications.an_unknown_outcome_leaves_the_handle", "D18", "AN1", "B1R-2")
def an_unknown_outcome(ctx: ChatContext) -> str:
    """B1R-2's proof: a register whose commit takes effect and whose acknowledgement is then lost
    (simulated, ``commit_answer_lost``, as B1's review simulated it) answers ``error``, served
    ``state_conflict``; its outcome is unknown, so nothing is discarded. The registration is
    ``active`` with the reference, the reference is not pending (the save consumed its handle),
    and the store still holds its token. A later revoke by the owner is accepted, and discards the
    token."""
    member = _f12_member(ctx)
    installation = ctx.installation()
    token = ctx.push_token()
    body = ctx.device_body(installation, "register", 0, token=token)
    caller = _f12_caller(member, installation)
    with commit_answer_lost() as lost:
        result, issued = _issued_by(lambda: _adapter().device(caller, body))
    expect(lost == [1], "the commit took effect, then its answer was lost (simulated)")
    expect(
        (result.outcome, result.reason) == ("error", "OperationalError"),
        f"the register answers error ({result.outcome})",
    )
    expect(_served(result) == ("state_conflict", False), "state_conflict")
    row = _registration(member.account_id, installation)
    expect(
        len(issued) == 1
        and row is not None
        and row.state == "active"
        and row.token_secret_ref == issued[0],
        "the registration committed, active with the reference",
    )
    expect(issued[0] not in _pending(), "the reference is not pending: its handle was consumed")
    expect(_token_of(issued[0]) == token, "the store still holds its token")
    revoked = ctx.notifications(ctx.revoke(member, installation, 1), "the owner's revoke")
    expect(revoked == _f12_settings(2, "revoked"), "the owner's later revoke is accepted")
    expect(_discarded_at_once(issued) == [(True, False)], "and discards the token")
    return "the commit's answer lost: the registration active, not pending; a later revoke served"


# -- B1-C1-5. a save that finds its handle gone refuses (AN1, AN2) ---------------------------------


@case("notifications.a_save_whose_handle_is_gone_refuses", "D18", "AN1", "D24")
def a_save_whose_handle_is_gone(ctx: ChatContext) -> str:
    """AN1's first condition: a register held at its transaction's start (``BeginHold``, the
    probe's ``on_begin``) has written its handle; another connection removes the handle's row, as
    SV4 B2's sweep would (D24); the save then finds it gone and refuses (``token_handle_missing``,
    served ``state_conflict``), and no registration holds the reference, which the command, its
    outcome known, has discarded. The case then discards it through the store, as the sweep would
    after removing the row (AN2), which changes nothing (AN11), so no token is held by no row."""
    from glow_domain.notifications import TokenReference
    from glow_persistence.models import DeviceRegistration, PendingTokenDiscard

    from glow_ordering_proof.discovery_cases import _Worker

    member = _f12_member(ctx)
    installation = ctx.installation()
    body = ctx.device_body(installation, "register", 0, token=ctx.push_token())
    caller = _f12_caller(member, installation)
    before = len(token_store().issued)
    held = BeginHold()
    worker = _Worker(lambda: _adapter().device(caller, body, probe=held))
    try:
        worker.start()
        expect(held.reached.wait(REACH_SECONDS), "the register holds at its transaction's start")
        issued = token_store().issued[before:]
        expect(len(issued) == 1, "the store took the token")
        expect(issued[0] in _pending(), "its handle was written before the transaction")
        removed, _ = PendingTokenDiscard.objects.filter(token_secret_ref=issued[0]).delete()
        expect(removed == 1, "another connection removes the handle's row, as the sweep would")
    finally:
        held.free()
        expect(worker.done(HOLD_SECONDS + 30), "the register ended")
    expect(worker.error is None, "the register raised nothing")
    result = worker.result
    expect(
        (result.outcome, result.reason) == ("refused", "token_handle_missing"),
        f"the save refuses ({result.outcome})",
    )
    expect(_served(result) == ("state_conflict", False), "state_conflict")
    expect(
        not DeviceRegistration.objects.filter(token_secret_ref=issued[0]).exists()
        and _registration(member.account_id, installation) is None,
        "no registration holds the reference",
    )
    expect(_token_of(issued[0]) is None, "the command discarded it at once")
    token_store().discard(TokenReference(issued[0]))
    expect(
        _discarded_at_once(issued) == [(True, False)],
        "the sweep's discard changes nothing: no row, no token",
    )
    return "the handle removed at the transaction's start: the save refused, nothing held"


# -- B1-C1-6. a reused reference is refused (AN1, AN11) -------------------------------------------


@case("notifications.a_reused_reference_is_refused", "D18", "AN1", "AN11", "B1R-5")
def a_reused_reference(ctx: ChatContext) -> str:
    """AN1's second condition, against a store that breaks AN11 (the fixture's ``reuse_next_put``:
    its next ``put`` returns a reference it already gave out). A register given a reference an
    active registration holds, or one a pending discard holds, is the store's refusal
    (``token_store_refused``: ``provider_unavailable``, 503, retryable), with nothing written and
    nothing discarded: the earlier holder's row and its pending discards are unchanged, and its
    token is still held. Under concurrency too: a register given the reference that a first
    registration's save is committing waits on the pending discards' uniqueness (observed), writes
    its handle once the save commits, reads the registrations again, and is refused, its handle's
    row removed, the first registration's token still held."""
    from glow_domain.notifications import TokenReference
    from glow_persistence.models import IdempotencyRecord, PendingTokenDiscard

    store = token_store().fixture
    holder, other = _f12_member(ctx), _f12_member(ctx)
    mine = ctx.installation()
    ctx.notifications(ctx.register(holder, mine), "the holder's register")
    row = _registration(holder.account_id, mine)
    reference = str(row.token_secret_ref)
    token = _token_of(reference)

    def refused_reuse(what: str) -> None:
        pending = PendingTokenDiscard.objects.count()
        installation = ctx.installation()
        store.reuse_next_put(TokenReference(reference))
        reply = ctx.register(other, installation)
        _refused(ctx, reply, 503, "provider_unavailable", what)
        expect((reply.body or {}).get("retryable") is True, f"{what}: the store's refusal")
        expect(_registration(other.account_id, installation) is None, f"{what}: nothing saved")
        expect(PendingTokenDiscard.objects.count() == pending, f"{what}: no handle written")
        expect(_token_of(reference) == token, f"{what}: the holder's token is still held")

    refused_reuse("a reference an active registration holds")
    after = _registration(holder.account_id, mine)
    expect(
        (after.state, after.version, after.token_secret_ref) == ("active", 1, reference),
        "the holder's registration is unchanged",
    )
    store.fail_next_discard()
    ctx.notifications(ctx.revoke(holder, mine, 1), "the holder's revoke, its discard failed")
    expect(reference in _pending(), "the revoked reference waits in the pending discards")
    refused_reuse("a reference a pending discard holds")
    expect(reference in _pending(), "its pending discard is unchanged")
    expect(
        not IdempotencyRecord.objects.filter(
            actor_id=other.account_id, operation="notifications.device"
        ).exists(),
        "no record written for the refused registers",
    )
    # Under concurrency: the first registration's save holds at its commit, its handle deleted
    # and its row written; the second register is given the same reference.
    first, second = _f12_member(ctx), _f12_member(ctx)
    one, two = ctx.installation(), ctx.installation()
    first_body = ctx.device_body(one, "register", 0, token=ctx.push_token())
    second_body = ctx.device_body(two, "register", 0, token=ctx.push_token())
    first_caller, second_caller = _f12_caller(first, one), _f12_caller(second, two)
    given: list[str] = []

    def reused() -> Any:
        given.append(token_store().issued[-1])
        store.reuse_next_put(TokenReference(given[0]))
        return _adapter().device(second_caller, second_body)

    result, saved = _held_against(
        lambda hold: _adapter().device(first_caller, first_body, probe=hold),
        reused,
        "the second register's handle",
    )
    expect(saved is not None and saved.outcome == "applied", "the first registration's save")
    expect(
        result is not None
        and (result.outcome, result.reason) == ("refused", "token_store_refused"),
        f"the second register: the store's refusal ({getattr(result, 'outcome', None)})",
    )
    held_row = _registration(first.account_id, one)
    expect(
        held_row.state == "active" and str(held_row.token_secret_ref) == given[0],
        "the first registration holds the reference",
    )
    expect(given[0] not in _pending(), "no pending discard is left: the handle's row removed")
    expect(_token_of(given[0]) is not None, "the first registration's token is still held")
    expect(_registration(second.account_id, two) is None, "nothing saved for the second")
    return "a reused reference refused, alone (a registration's, a pending one's) and concurrently"


# -- B1-C1-7. a failure inside the transaction is known (AN1) -------------------------------------


@case("notifications.a_failure_inside_the_transaction_is_known", "D18", "AN1", "AM13")
def a_failure_inside_the_transaction(ctx: ChatContext) -> str:
    """AN1's third condition, in case 9's race (two accounts register one new installation): the
    losing command's failure, the one-``active``-row constraint's ``IntegrityError``, is raised
    inside its transaction's body, so its outcome is known. It answers ``error``, served
    ``state_conflict``, and its reference is discarded at once: the store no longer holds its
    token, and no pending discard is left. The winner's reference is held, its handle consumed."""
    first, second = _f12_member(ctx), _f12_member(ctx)
    installation = ctx.installation()
    first_body = ctx.device_body(installation, "register", 0, token=ctx.push_token())
    second_body = ctx.device_body(installation, "register", 0, token=ctx.push_token())
    first_caller = _f12_caller(first, installation)
    second_caller = _f12_caller(second, installation)
    (result, won), issued = _issued_by(
        partial(
            _held_against,
            lambda hold: _adapter().device(first_caller, first_body, probe=hold),
            lambda: _adapter().device(second_caller, second_body),
            "the second account's register",
        )
    )
    expect(won is not None and won.outcome == "applied", "the first account's register")
    expect(
        result is not None
        and result.outcome == "error"
        and str(result.reason).startswith("IntegrityError"),
        f"the second: a database error inside its transaction ({getattr(result, 'outcome', None)})",
    )
    expect(_served(result) == ("state_conflict", False), "state_conflict")
    winner = str(_registration(first.account_id, installation).token_secret_ref)
    expect(len(issued) == 2 and winner in issued, "the store took both tokens")
    expect(
        _discarded_at_once([ref for ref in issued if ref != winner]) == [(True, False)],
        "the loser's reference: the store no longer holds its token, no pending discard is left",
    )
    expect(
        _token_of(winner) is not None and winner not in _pending(),
        "the winner's reference is held, its handle consumed",
    )
    return "the loser's IntegrityError, inside its transaction: known, its reference discarded"


# -- B1-12. no token in any row, log line or answer; each reference's custody (D29; AM4) ---------


@case("notifications.no_token_in_any_row_or_answer", "D29", "AM4", "DM-101 11")
def no_token_in_any_row_or_answer(ctx: ChatContext) -> str:
    """After every other F12 case: no push token the cases drew is in any row of any table (the
    database search names each ``table.column`` it finds one in, never the value), nor in any
    served answer, nor any reference or installation identifier; every ``put`` ran before its
    command's transaction (AM4); and every reference the store issued is held by exactly one
    active registration or pending discard while its token is held, and by no row once it is
    discarded. The log lines and the results JSON are the suite's scan's, which holds every token
    of the pool among the run's secrets, and the job's own check's."""
    from glow_persistence.models import DeviceRegistration

    from glow_ordering_proof.profile_cases import _found_in_database, _named

    tokens = tuple(ctx.drawn_tokens)
    expect(len(tokens) >= 10, f"the F12 cases drew their push tokens ({len(tokens)})")
    found = _found_in_database(tokens)
    expect(not found, f"no push token in any row{_named(found)}")
    store = token_store()
    references = tuple(store.issued)
    served = json.dumps(ctx.profiles.served)
    for kind, values in (
        ("a push token", tokens),
        ("a token reference", references),
        ("an installation identifier", tuple(ctx.installations)),
    ):
        expect(not any(value in served for value in values), f"{kind} in no served answer")
    expect(
        bool(store.inside_a_transaction) and not any(store.inside_a_transaction),
        "every put ran before its command's transaction",
    )
    active = set(
        DeviceRegistration.objects.filter(state="active").values_list("token_secret_ref", flat=True)
    )
    pending = _pending()
    for reference in references:
        held = (reference in active) + (reference in pending)
        expect(
            held == (0 if _token_of(reference) is None else 1),
            "each reference held exactly once while its token is, by no row once discarded",
        )
    where = set(_found_in_database(references))
    expect(
        where
        <= {
            "glow_persistence_deviceregistration.token_secret_ref",
            "glow_persistence_pendingtokendiscard.token_secret_ref",
        },
        f"a reference only in a registration or a pending discard{_named(sorted(where))}",
    )
    return (
        f"{len(tokens)} tokens in no row and no answer; {len(references)} references, each held"
        " once or discarded; every put before its transaction"
    )


# -- 16. AR-13: a publication of chat.history during a read (after every read-only case) ----


@case("ar13.history_publication_during_a_read", "AR-13", "D5", "D19")
def ar13(ctx: ChatContext) -> str:
    """A1's review's AR-13. A read and a publication of ``chat.history`` cannot cross: a
    publication waits on a read that holds the setting's pointer (observed), and the read is served
    as the setting stood; a read waits on a publication that holds it (observed), and then reads
    the new setting, so a cause just published ``hidden`` hides the conversation."""
    from glow_domain import profile_settings as ps
    from glow_domain.chat_reads import HistoryRequest, ReadProbe
    from glow_profiles import staff

    from glow_ordering_proof.discovery_cases import _Worker
    from glow_ordering_proof.observe import observe_lock_wait

    reader, other, match = _pair(ctx)
    ctx.sent(other, match.id)
    _visibility(ctx, reader, "pause")
    expect(ctx.conversations(reader)[str(match.id)]["state"] == "read_only", "read-only first")
    request = HistoryRequest(session_of(reader), UUID(str(match.id)))

    def publication(probe: Any, **changes: str) -> Callable[[], Any]:
        content = ctx.discovery.current(ps.HISTORY)
        content.update(changes)
        return partial(
            staff.publish_setting,
            ps.HISTORY,
            content,
            staff_subject="staff:chat-proof",
            reason="SV4-proof",
            request_id=uuid4(),
            probe=probe,
        )

    # The read holds the pointer at its final check; a publication (a cause that is not this
    # conversation's) waits on it; the read is served as the setting stood.
    holding, publishing = Hold("after_locks"), Hold()
    read = _Worker(partial(route_reads().read_history, request, probe=ReadProbe(final=holding)))
    publish = _Worker(publication(publishing, restriction="hidden"))
    waited = None
    try:
        read.start()
        expect(holding.reached["after_locks"].wait(REACH_SECONDS), "the read holds the pointer")
        publish.start()
        pid = publishing.wait_pid()
        assert holding.pid is not None
        waited = observe_lock_wait(
            pid, holder_pid=holding.pid, finished=publish.ended, timeout=REACH_SECONDS
        )
    finally:
        holding.free()
        expect(read.done(HOLD_SECONDS + 30) and publish.done(HOLD_SECONDS + 30), "both finished")
    expect(waited is not None and waited.observed, "the publication waited on the read")
    expect(read.result is not None and read.result.outcome == "read", "the read was served")
    expect(publish.result is not None and publish.result.outcome == "applied", "then published")
    expect(ctx.conversations(reader)[str(match.id)]["state"] == "read_only", "still read-only")
    # The publication holds the pointer at its commit; the read waits on it, then reads it.
    held, reading = Hold("before_commit"), Hold()
    publish = _Worker(publication(held, own_pause="hidden"))
    read = _Worker(partial(route_reads().read_history, request, probe=ReadProbe(first=reading)))
    waited = None
    try:
        publish.start()
        expect(held.reached["before_commit"].wait(REACH_SECONDS), "the publication holds it")
        read.start()
        pid = reading.wait_pid()
        assert held.pid is not None
        waited = observe_lock_wait(
            pid, holder_pid=held.pid, finished=read.ended, timeout=REACH_SECONDS
        )
    finally:
        held.free()
        expect(read.done(HOLD_SECONDS + 30) and publish.done(HOLD_SECONDS + 30), "both finished")
    expect(waited is not None and waited.observed, "the read waited on the publication")
    expect(publish.result is not None and publish.result.outcome == "applied", "published")
    expect(
        read.result is not None
        and (read.result.outcome, read.result.reason) == ("refused", "conversation_hidden"),
        f"the read saw it: hidden ({read.result.outcome if read.result else None})",
    )
    _refused(ctx, ctx.history_reply(reader, match.id), 404, "not_found", "hidden through the route")
    expect(str(match.id) not in ctx.conversations(reader), "and not listed")
    return "each waited on the other; the read served as it stood, then saw the new setting"


# -- 17. each D5 cause hidden once the setting says so (after AR-13) -----------------------------


@case("d5.each_cause_hidden", "D5", "D9", "OD-60 H")
def each_cause_hidden(ctx: ChatContext) -> str:
    """With each cause published ``hidden`` in ``chat.history`` (in turn, each staying hidden),
    every conversation with that cause is hidden on every read: the history and the cursor are
    ``not_found`` and the list leaves it out, with one code for every cause; a conversation with no
    cause is still served ``open``."""
    from glow_domain import profile_settings as ps

    key = {
        "own_pause": "own_pause",
        "other_pause": "other_pause",
        "own_incomplete": "own_pause",
        "other_incomplete": "other_pause",
        "own_restriction": "restriction",
        "other_restriction": "restriction",
        "other_suspension": "suspension",
        "own_withdrawal": "withdrawn_consent",
        "other_withdrawal": "withdrawn_consent",
        "own_withdrawal_alone": "withdrawn_consent",
        "other_withdrawal_alone": "withdrawn_consent",
    }
    bodies = set()
    for name, apply in _cause_writers(ctx):
        cause = key[name]
        if ctx.discovery.current(ps.HISTORY)[cause] != "hidden":
            _publish_history(ctx, **{cause: "hidden"})
        reader, other, match = _pair(ctx)
        theirs = ctx.sent(other, match.id)
        apply(reader, other)
        history = ctx.history_reply(reader, match.id)
        cursor = ctx.cursor_reply(reader, match.id, theirs)
        _refused(ctx, history, 404, "not_found", f"{name}: the history is hidden")
        _refused(ctx, cursor, 404, "not_found", f"{name}: the cursor is hidden")
        expect(str(match.id) not in ctx.conversations(reader), f"{name}: not listed")
        bodies.add(_error_body(history))
        bodies.add(_error_body(cursor))
    expect(len(bodies) == 1, "one code for every hidden cause")
    one, two, match = _pair(ctx)
    ctx.sent(two, match.id)
    expect(ctx.conversations(one)[str(match.id)]["state"] == "open", "no cause: served open")
    return f"{len(key)} causes hidden by the setting, one code; no cause still open"


# -- 18. a conversation's reads with a session ended in their locks (last) -------------------------


@case("reads.session_ended_in_locks_answers_as_hidden", "D8", "D5", "AK1", "AK2")
def reads_session_ended(ctx: ChatContext) -> str:
    """The history read and the read cursor, each with a valid session and with a session ended
    once they hold their locks, answer the same under a cause published ``hidden`` (the other's
    pause) as under an unmatch: ``not_found``, one body (DM-99's AK1). The read rule checks the
    match before the session and the causes after it, so the session's refusal must not be
    ``unauthenticated`` there. It runs last, after ``d5.each_cause_hidden``, which the pinned plan
    keeps before it and which leaves every cause published ``hidden``, the other member's own pause
    among them, which its last check reads (the paused member lists the conversation no more). Its
    own publication below then changes nothing; run without that case before it, the case would
    fail at that check, since that publication hides the reader's cause only (A2-C1's delta review,
    F4)."""
    from glow_domain import profile_settings as ps

    if ctx.discovery.current(ps.HISTORY)["other_pause"] != "hidden":
        _publish_history(ctx, other_pause="hidden")
    bodies: set[str] = set()
    checked = 0
    for route in ("history", "cursor"):
        for cause in ("the other's pause, hidden", "an unmatch"):
            reader, other, match = _pair(ctx)
            theirs = ctx.sent(other, match.id)
            if cause == "an unmatch":
                _unmatch(ctx, other, match)
            else:
                _visibility(ctx, other, "pause")
            call: Callable[[], Reply] = (
                partial(ctx.history_reply, reader, match.id)
                if route == "history"
                else partial(ctx.cursor_reply, reader, match.id, theirs)
            )
            what = f"{route}, {cause}"
            for name, reply in (
                ("a valid session", call()),
                ("a session ended in its locks", _ended_in_locks(ctx, reader, call, what)),
            ):
                _refused(ctx, reply, 404, "not_found", f"{what}: {name}")
                bodies.add(_error_body(reply))
                checked += 1
            expect(str(match.id) not in ctx.conversations(other), f"{what}: not listed")
    expect(len(bodies) == 1, f"one body for both causes and both sessions ({len(bodies)})")
    return f"{checked} reads (history and cursor): hidden and unmatched answer alike, ended too"


# -- the run ------------------------------------------------------------------------------------


def run_case(ctx: ChatContext, entry: Case) -> tuple[bool, str]:
    """One case, isolated as the discovery suite's are (``discovery_cases.run_case``'s steps)."""
    from django.core.cache import cache

    cache.clear()
    profiles = ctx.profiles
    profiles.identity.case_id = entry.case_id
    profiles.watch_store()
    ctx.discovery.hide_everyone()
    try:
        outcome = True, entry.run(ctx)
    except CaseFailed as failed:
        outcome = False, f"FAILED: {failed}"
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        outcome = False, f"ERROR: {type(exc).__name__}"
    try:
        profiles.hold_media()
        ctx.hold_provider_ids()
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        return False, f"ERROR: the value ledger's held values: {type(exc).__name__}"
    return outcome


def plan() -> tuple[str, ...]:
    return tuple(entry.case_id for entry in CASES)
