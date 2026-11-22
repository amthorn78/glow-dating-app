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
cause read-only runs first, and the two cases that publish a cause ``hidden`` (``ar13.*`` and
``d5.each_cause_hidden``) run last, in that order.

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
    HISTORY,
    HOLD_SECONDS,
    MATCHES,
    MESSAGES,
    REACH_SECONDS,
    READ_CURSOR,
    ChatContext,
    Hold,
    lock_statements,
    provider,
    route_reads,
    session_of,
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
CASE_COUNT = 15


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


def _internal_send_reason(member: Member, match_id: Any) -> str:
    """The send's own reason for the same state, through ``glow_chat``'s ``send`` (the route
    serves one code for it; the reason is the adapter's, never served)."""
    from glow_domain.chat import SendCommand

    result = _chat().send(
        SendCommand(session_of(member), UUID(str(match_id)), 1, f"k{uuid4().hex}", "x" * 10)
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
        for name, reply in (
            ("no token", call("POST", path, body, bearer=False)),
            ("a refused token", call("POST", path, body, bearer="not-a-token")),
        ):
            _refused(ctx, reply, 401, "unauthenticated", f"{what}: {name}")
            expect("WWW-Authenticate: Bearer" in _last_headers(ctx), f"{what}: the challenge")
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
    the same key with another text is ``idempotency_conflict``; another version is
    ``stale_version``; neither writes; once contact has ended the replay is refused as every
    stopped send is (``not_found``)."""
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
            409,
            "stale_version",
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
    return "pending, replayed, accepted; conflict and stale refused, writing nothing; ended: 404"


# -- 3. history, list and read cursor for both members (D8, D5) ----------------------------------


@case("reads.history_list_and_cursor_for_both", "D8", "D5", "F11")
def reads_for_both(ctx: ChatContext) -> str:
    """Both members read the history, each their own side; pages and cursors follow acceptance;
    the list shows each the other's unread messages and the latest marker; the read cursor moves
    forward only; a cursor or a message of another match is refused; the member's own pending
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
    return "both sides read; pages and cursors in acceptance order; unread and cursor; refusals"


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
    settings = connection.settings_dict
    before = settings.get("ATOMIC_REQUESTS")
    settings["ATOMIC_REQUESTS"] = True
    try:
        sent = ctx.profiles.data(ctx.send(one, ctx.message(one, match.id)), "message", "send")
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


# -- 14. AR-13: a publication of chat.history during a read (after every read-only case) ----


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


# -- 15. each D5 cause hidden once the setting says so (runs last) ---------------------------------


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
