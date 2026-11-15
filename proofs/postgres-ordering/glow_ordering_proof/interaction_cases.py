"""The interaction cases (SV3 Stage B; its brief's acceptance checks 7 to 12, with 13 and 14 for
Stage B's code; D9 to D13, D18 and D19; DB05 and DB10), registered in the discovery suite after
Stage A's cases (``discovery_cases.CASES``), on the same disposable discovery database.

Each case makes its own synthetic members through SV1's and SV2's routes and drives Stage B's
routes through HTTP with Django's test client: ``POST api/v1/discovery/interaction`` (like and
pass), ``POST api/v1/discovery/interaction/undo``, ``POST api/v1/matches/unmatch``,
``GET api/v1/matches/<id>`` and ``POST api/v1/blocks``. The concurrency cases (DB05, DB10) call the
operations from separate threads on separate connections, held at their probes, as Stage A's
page-creation cases do. Settings are global: a case that publishes one restores what later cases
rely on. Rows written only in setup (an earlier ``decided_at``, a seeded ``liked`` row) are test
data, never an application writer. No detail line holds a member's value.
"""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from datetime import timedelta
from functools import partial
from typing import Any
from unittest import mock
from uuid import UUID, uuid4

from glow_ordering_proof.discovery_cases import (
    REACH_SECONDS,
    _finish,
    _Held,
    _stale_shape,
    _visibility,
    _Worker,
    case,
)
from glow_ordering_proof.discovery_support import CHICAGO, LOS_ANGELES, DiscoveryContext
from glow_ordering_proof.identity_support import Member, expect

INTERACTION = "/api/v1/discovery/interaction"
UNDO = "/api/v1/discovery/interaction/undo"
UNMATCH = "/api/v1/matches/unmatch"
BLOCKS = "/api/v1/blocks"
MATCHES = "/api/v1/matches"
OPERATIONS = ("interaction", "interaction_undo", "unmatch", "block")
TEXT = "A synthetic message for the proof."


# -- helpers --------------------------------------------------------------------------------


def _pid(ctx: DiscoveryContext, member: Member) -> str:
    return ctx.profile_id(member)


def _row(actor: Member, target: Member) -> Any:
    from glow_persistence.models import DirectionalInteraction

    return DirectionalInteraction.objects.filter(
        actor_id=actor.account_id, target_id=target.account_id
    ).first()


def _version(actor: Member, target: Member) -> int:
    row = _row(actor, target)
    return 0 if row is None else int(row.version)


def _intent(
    ctx: DiscoveryContext,
    actor: Member,
    target: Member,
    action: str,
    page: dict[str, Any],
    *,
    expected: int | None = None,
    key: str | None = None,
) -> dict[str, Any]:
    return {
        "operation": "interaction",
        "meta": {
            "idempotency_key": key or ctx.profiles.key(),
            "expected_version": _version(actor, target) if expected is None else expected,
        },
        "target_profile_id": _pid(ctx, target),
        "batch_id": page["batch_id"],
        "batch_version": page["version"],
        "action": action,
    }


def _act(
    ctx: DiscoveryContext,
    actor: Member,
    target: Member,
    action: str,
    page: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """A like or pass through the route, on a fresh page unless one is given."""
    body = _intent(ctx, actor, target, action, page or ctx.page(actor))
    reply = ctx.profiles.command(actor, INTERACTION, body)
    return ctx.profiles.data(reply, "interaction", f"the {action}")


def _match_of(first: Member, second: Member) -> Any:
    from glow_persistence.models import Match

    low, high = sorted((first.account_id, second.account_id))
    return Match.objects.filter(account_low_id=low, account_high_id=high).first()


def _matched(ctx: DiscoveryContext, first: Member, second: Member) -> Any:
    """A match made the only way there is: reciprocal likes, through the route."""
    _act(ctx, first, second, "like")
    out = _act(ctx, second, first, "like")
    expect(out["match_id"] is not None, "the reciprocal like makes the match")
    match = _match_of(first, second)
    expect(match is not None and str(match.id) == out["match_id"], "the pair's one match")
    return match


def _undo(
    ctx: DiscoveryContext, actor: Member, target: Member, *, expected: int | None = None
) -> tuple[dict[str, Any], Any]:
    body = {
        "operation": "interaction_undo",
        "meta": {
            "idempotency_key": ctx.profiles.key(),
            "expected_version": _version(actor, target) if expected is None else expected,
        },
        "target_profile_id": _pid(ctx, target),
    }
    return body, ctx.profiles.command(actor, UNDO, body)


def _unmatch(
    ctx: DiscoveryContext, actor: Member, match: Any, *, expected: int | None = None
) -> tuple[dict[str, Any], Any]:
    from glow_persistence.models import Match

    current = Match.objects.get(pk=match.id)
    body = {
        "operation": "unmatch",
        "meta": {
            "idempotency_key": ctx.profiles.key(),
            "expected_version": int(current.version) if expected is None else expected,
        },
        "match_id": str(match.id),
    }
    return body, ctx.profiles.command(actor, UNMATCH, body)


def _block_version(actor: Member, target: Member) -> int:
    from glow_persistence.models import Block

    row = Block.objects.filter(actor_id=actor.account_id, target_id=target.account_id).first()
    return 0 if row is None else int(row.version)


def _block(
    ctx: DiscoveryContext,
    actor: Member,
    target: Member,
    action: str,
    *,
    expected: int | None = None,
) -> tuple[dict[str, Any], Any]:
    body = {
        "operation": "block",
        "meta": {
            "idempotency_key": ctx.profiles.key(),
            "expected_version": _block_version(actor, target) if expected is None else expected,
        },
        "target_profile_id": _pid(ctx, target),
        "action": action,
    }
    return body, ctx.profiles.command(actor, BLOCKS, body)


def _read_match(ctx: DiscoveryContext, member: Member, match_id: Any) -> Any:
    return ctx.profiles.call(member, "GET", f"{MATCHES}/{match_id}")


def _counts() -> tuple[int, int, int, int, int]:
    """What an interaction writes: directional rows and their versions, matches, the interaction
    commands' idempotency records, and the match's chat events."""
    from django.db.models import Sum
    from glow_chat import events
    from glow_persistence.models import (
        DirectionalInteraction,
        IdempotencyRecord,
        Match,
        OutboxEvent,
    )

    total = DirectionalInteraction.objects.aggregate(total=Sum("version"))["total"] or 0
    return (
        DirectionalInteraction.objects.count(),
        int(total),
        Match.objects.count(),
        IdempotencyRecord.objects.filter(operation__in=OPERATIONS).count(),
        OutboxEvent.objects.filter(
            event_type__in=(events.MATCH_ACTIVATED, events.IDENTITY_CREATED)
        ).count(),
    )


def _batch_state(batch_id: str) -> tuple[str, int] | None:
    from glow_persistence.models import RecommendationBatch

    row = RecommendationBatch.objects.filter(pk=batch_id).values_list("state", "version").first()
    return None if row is None else (str(row[0]), int(row[1]))


def _shown(ctx: DiscoveryContext, viewer: Member, collection: str = "recommendations") -> set[str]:
    return set(ctx.all_ids(ctx.pages_of(viewer, collection)))


def _session(member: Member) -> UUID:
    from glow_persistence.models import AccountSession

    found = (
        AccountSession.objects.filter(account_id=member.account_id, state="valid")
        .order_by("-created_at")
        .values_list("id", flat=True)
        .first()
    )
    expect(found is not None, "the member has a valid session")
    return UUID(str(found))


def _send(member: Member, match_id: Any) -> Any:
    from glow_discovery.interactions import chat
    from glow_domain.chat import SendCommand
    from glow_persistence.models import Match

    match = Match.objects.get(pk=match_id)
    return chat().send(
        SendCommand(_session(member), match.id, int(match.contact_version), f"k{uuid4().hex}", TEXT)
    )


def _db_now() -> Any:
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT clock_timestamp()")
        return cursor.fetchone()[0]


def _decided(actor: Member, target: Member, days_ago: float) -> None:
    """Test data: the row's ``decided_at`` moved back (no application writer moves it)."""
    from glow_persistence.models import DirectionalInteraction

    DirectionalInteraction.objects.filter(
        actor_id=actor.account_id, target_id=target.account_id
    ).update(decided_at=_db_now() - timedelta(days=days_ago))


def _seed_withdrawn_consent(member: Member) -> None:
    """Test data: a withdrawn onboarding decision after the member's acceptance, with the profile
    left ``visible``, a state no SV2 writer leaves (its withdrawal hides the profile), so that the
    contact checks' consent rule is reached on its own."""
    from django.db.models import Max
    from glow_persistence.models import ConsentDecision

    latest = ConsentDecision.objects.filter(account_id=member.account_id, purpose="onboarding")
    top = latest.aggregate(top=Max("version"))["top"] or 0
    label = latest.order_by("-version").values_list("policy_version", flat=True).first()
    ConsentDecision.objects.create(
        account_id=member.account_id,
        purpose="onboarding",
        policy_version=label,
        state="withdrawn",
        decided_at=_db_now(),
        version=top + 1,
    )


def _wait_pid(probe: _Held) -> int:
    deadline = time.monotonic() + REACH_SECONDS
    while probe.pid is None and time.monotonic() < deadline:
        time.sleep(0.01)
    expect(probe.pid is not None, "the transaction reported its backend")
    assert probe.pid is not None
    return probe.pid


def _publish(ctx: DiscoveryContext, name: str, content: Any) -> None:
    ctx.publish(name, content)


# -- 15. D14's reach (Stage B's item 2; DM-70, DM-73) ------------------------------------------


@case("row_locks.driver_forms_are_seen", "15", "D14", "Stage B item 2")
def driver_forms_are_seen(ctx: DiscoveryContext) -> str:
    """D14's reach (SV3 Stage B's item 2; DM-70, DM-73): each form that Django's execute wrappers
    do not see, planted with a harmless read, is seen by the record as sent through the driver
    itself, and judged: psycopg's ``stream`` and ``copy`` through Django's cursor, ``callproc``
    (Django's own psycopg 3 cursor class sends it as ``SELECT * FROM "name"(...)``), and the
    driver's own connection (its ``cursor()`` and its ``execute``); a read through Django's cursor
    is seen as Django's. And the migrated database defines no function, procedure, view or rule
    of its own, so no lock is taken out of a statement's sight (``row_locks.OWN_OBJECTS``)."""
    from django.db import connection

    from glow_ordering_proof import row_locks

    record = row_locks.active()
    expect(record is not None, "D14's record of the statements the suite sends is installed")
    assert record is not None
    connection.ensure_connection()
    driver = connection.connection
    forms: list[tuple[str, str, str]] = []
    with record.window() as seen:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS planted_django")
            cursor.fetchall()
            list(cursor.stream("SELECT 1 AS planted_stream"))
            with cursor.copy("COPY (SELECT 1 AS planted_copy) TO STDOUT") as copied:
                for _ in copied:
                    pass
            cursor.callproc("pg_backend_pid")
            cursor.fetchall()
        with driver.cursor() as raw:
            raw.execute("SELECT 1 AS planted_driver_cursor")
            raw.fetchall()
        driver.execute("SELECT 1 AS planted_driver_execute").fetchall()
    for source, text in (
        (row_locks.DJANGO, "SELECT 1 AS planted_django"),
        (row_locks.DRIVER, "SELECT 1 AS planted_stream"),
        (row_locks.DRIVER, "COPY (SELECT 1 AS planted_copy) TO STDOUT"),
        (row_locks.DRIVER, 'SELECT * FROM "pg_backend_pid"()'),
        (row_locks.DRIVER, "SELECT 1 AS planted_driver_cursor"),
        (row_locks.DRIVER, "SELECT 1 AS planted_driver_execute"),
    ):
        found = [item for item in seen if item.text == text]
        expect(
            len(found) == 1 and found[0].source == source,
            f"the record saw {text.split()[-1]} once, as {source}",
        )
        forms.append((source, text, "refused" if row_locks.refusal(text) else "passed"))
    with connection.cursor() as cursor:
        cursor.execute(row_locks.OWN_OBJECTS)
        own = cursor.fetchone()
    expect(own is not None and tuple(own) == (0, 0, 0), "no function, view or rule of its own")
    return (
        f"{len(forms)} forms seen and judged ({sum(s == row_locks.DRIVER for s, _, _ in forms)}"
        " through the driver itself: stream, copy, callproc, the driver's cursor and execute);"
        " the database's own functions, views and rules: 0, 0, 0"
    )


# -- 7. like and pass (acceptance check 7; D9; F08) ------------------------------------------


@case("interactions.like_and_pass_are_idempotent", "7", "D9", "F08", "Outcome 4")
def like_and_pass_are_idempotent(ctx: DiscoveryContext) -> str:
    """An identical repeat replays the original receipt with ``replayed`` and the current
    projection, and writes nothing; the same key with a changed action or target is
    ``idempotency_conflict``; a committed like or pass consumes its batch (F07's ``invalidate``),
    so a new command naming it is the generic stale response, while an identical repeat still
    replays (replay before staleness)."""
    from glow_discovery import interactions

    viewer, liked, passed = ctx.visible(), ctx.visible(), ctx.visible()
    page = ctx.page(viewer)
    expect({_pid(ctx, liked), _pid(ctx, passed)} <= set(ctx.ids(page)), "both in the batch")
    body = _intent(ctx, viewer, liked, "like", page)
    first = ctx.profiles.data(
        ctx.profiles.command(viewer, INTERACTION, body), "interaction", "like"
    )
    expect(
        first
        == {
            "kind": "interaction",
            "target_profile_id": _pid(ctx, liked),
            "version": 1,
            "state": "liked",
            "match_id": None,
        },
        "the like is the actor's own outcome, version 1, with no match",
    )
    expect(_batch_state(page["batch_id"]) == ("stale", page["version"] + 1), "the batch consumed")
    before = _counts()
    again = ctx.profiles.data(
        ctx.profiles.command(viewer, INTERACTION, body), "interaction", "again"
    )
    expect(again == first, "an identical repeat answers the same")
    expect(_counts() == before, "an identical repeat writes nothing")
    direct = interactions.interact(viewer.account_id, body)
    result = direct.detail.get("command_result") or {}
    row = _row(viewer, liked)
    expect(
        direct.outcome == "replayed"
        and result.get("replayed") is True
        and result.get("receipt")
        == {"outcome_code": "liked", "object_ref": str(row.id), "committed_version": 1},
        "the replay carries the original receipt and replayed: true",
    )
    changed = dict(body, action="pass")
    ctx.profiles.refused(
        ctx.profiles.command(viewer, INTERACTION, changed),
        409,
        "idempotency_conflict",
        "the same key with a changed action",
    )
    moved = dict(body, target_profile_id=_pid(ctx, passed))
    ctx.profiles.refused(
        ctx.profiles.command(viewer, INTERACTION, moved),
        409,
        "idempotency_conflict",
        "the same key with a changed target",
    )
    expect(_counts() == before, "a conflict writes nothing")
    named = _intent(ctx, viewer, passed, "pass", page)
    ctx.profiles.refused(
        ctx.profiles.command(viewer, INTERACTION, named),
        409,
        "stale_version",
        "a new command naming the consumed batch",
    )
    expect(_counts() == before, "the stale command writes nothing")
    fresh = ctx.page(viewer)
    expect(_pid(ctx, liked) not in ctx.ids(fresh), "the liked candidate is consumed")
    pbody = _intent(ctx, viewer, passed, "pass", fresh)
    p1 = ctx.profiles.data(ctx.profiles.command(viewer, INTERACTION, pbody), "interaction", "pass")
    expect(p1["state"] == "passed" and p1["version"] == 1, "the pass, version 1")
    expect(p1["match_id"] is None, "a pass has no match")
    held = _counts()
    p2 = ctx.profiles.data(
        ctx.profiles.command(viewer, INTERACTION, pbody), "interaction", "repeat"
    )
    expect(p2 == p1 and _counts() == held, "an identical pass replays and writes nothing")
    expect(_pid(ctx, passed) not in ctx.ids(ctx.page(viewer)), "the passed candidate is consumed")
    return (
        "an identical like and pass replay their receipts (replayed: true) and write nothing; a"
        " changed action or target conflicts; a consumed batch is stale to a new command"
    )


@case("interactions.stale_and_ineligible_are_refused", "7", "D8", "D9")
def stale_and_ineligible_are_refused(ctx: DiscoveryContext) -> str:
    """At commit, under the locks, the target must be in the actor's named batch at its version,
    fresh, and the pair must pass D3 to D5 and consumption; otherwise the generic stale response,
    the same whatever the cause (D8), and nothing is written."""
    viewer, target, other = ctx.visible(), ctx.visible(), ctx.visible()
    page = ctx.page(viewer)
    expect(_pid(ctx, target) in ctx.ids(page), "the target in the viewer's batch")
    others = ctx.page(other)
    late = ctx.visible()
    before = _counts()
    batch = _batch_state(page["batch_id"])
    shapes: list[dict[str, Any]] = []
    causes: list[str] = []

    def stale(body: dict[str, Any], what: str) -> None:
        reply = ctx.profiles.command(viewer, INTERACTION, body)
        ctx.profiles.refused(reply, 409, "stale_version", what)
        shapes.append(_stale_shape(reply))
        expect(_counts() == before, f"{what}: nothing written")
        expect(_batch_state(page["batch_id"]) == batch, f"{what}: the batch unchanged")
        causes.append(what)

    stale(
        dict(_intent(ctx, viewer, target, "like", page), batch_version=page["version"] + 1),
        "a stale batch version",
    )
    stale(_intent(ctx, viewer, target, "like", others), "another viewer's batch")
    stale(dict(_intent(ctx, viewer, target, "like", page), batch_id=str(uuid4())), "no batch")
    stale(_intent(ctx, viewer, late, "like", page), "a target outside the batch")
    stale(_intent(ctx, viewer, viewer, "like", page), "the actor as the target")
    stale(_intent(ctx, viewer, target, "pass", page, expected=3), "an expected version not 0")
    _visibility(ctx, target, "pause")
    stale(_intent(ctx, viewer, target, "like", page), "an ineligible target (paused)")
    _visibility(ctx, target, "resume")
    ctx.block(target.account_id, viewer.account_id)
    stale(_intent(ctx, viewer, target, "like", page), "an ineligible target (it blocked)")
    ctx.unblock(target.account_id, viewer.account_id)
    ctx.set_sets(viewer, {"gender": ["woman"]})
    stale(_intent(ctx, viewer, target, "like", page), "a batch the actor's own change made stale")
    expect(all(shape == shapes[0] for shape in shapes), "every stale refusal reads the same (D8)")
    ok = _act(ctx, viewer, target, "like")
    expect(ok["state"] == "liked", "with a fresh page the like applies")
    return f"{len(causes)} causes, each 409 stale_version, the same body, nothing written"


@case("interactions.unreciprocated_like_is_hidden", "7", "D8", "F08")
def unreciprocated_like_is_hidden(ctx: DiscoveryContext) -> str:
    """A like changes nothing of its target's: the target's batch keeps its state and version,
    the liker's card reads the same in the target's next page, and nothing served to the target
    names the like."""
    liker, target = ctx.visible(), ctx.visible()
    target_page = ctx.page(target)
    expect(_pid(ctx, liker) in ctx.ids(target_page), "the liker in the target's batch")
    held = _batch_state(target_page["batch_id"])
    card = next(c for c in target_page["items"] if c["profile_id"] == _pid(ctx, liker))
    served = len(ctx.profiles.served)
    out = _act(ctx, liker, target, "like")
    expect(out["match_id"] is None, "an unreciprocated like has no match")
    expect(_batch_state(target_page["batch_id"]) == held, "the target's batch is unchanged")
    after = ctx.page(target)
    again = next(c for c in after["items"] if c["profile_id"] == _pid(ctx, liker))
    expect(again == card, "the liker's card reads the same to the target")
    passed = _act(ctx, target, liker, "pass", after)
    expect(passed["match_id"] is None and passed["state"] == "passed", "the target's own pass")
    since = ctx.profiles.served[served:]
    target_bodies = [
        body for body in since if (body.get("data") or {}).get("kind") != "interaction"
    ]
    expect(
        not any("liked" in str(body.get("data")) for body in target_bodies),
        "no page served since names a like",
    )
    return "the target's batch, card and responses are unchanged by the like"


@case("interactions.pass_over_like_is_refused", "7", "D9", "F08")
def pass_over_like_is_refused(ctx: DiscoveryContext) -> str:
    """F08 has no pass from ``liked``: through a batch still fresh (the broader one, built before
    the recommendations batch the like consumed), a pass over the actor's own like is
    ``state_conflict`` and writes nothing; an expected version that is not the row's is
    ``stale_version`` first."""
    viewer, target = ctx.visible(), ctx.visible()
    broader = ctx.page(viewer, "discovery")
    expect(_pid(ctx, target) in ctx.ids(broader), "the target in the broader batch")
    liked = _act(ctx, viewer, target, "like", ctx.page(viewer))
    expect(liked["state"] == "liked", "the like")
    before = _counts()
    ctx.profiles.refused(
        ctx.profiles.command(viewer, INTERACTION, _intent(ctx, viewer, target, "pass", broader)),
        409,
        "state_conflict",
        "a pass over the actor's own like",
    )
    ctx.profiles.refused(
        ctx.profiles.command(
            viewer, INTERACTION, _intent(ctx, viewer, target, "pass", broader, expected=0)
        ),
        409,
        "stale_version",
        "an expected version from before the like",
    )
    expect(_counts() == before and _row(viewer, target).state == "liked", "nothing written")
    return "a pass over a like is state_conflict; the like stays"


# -- 8. the match (acceptance check 8; D10; F09; DB05) -----------------------------------------


@case("match.reciprocal_likes_make_one_match", "8", "D10", "F09", "Outcome 5")
def reciprocal_likes_make_one_match(ctx: DiscoveryContext) -> str:
    """Reciprocal likes make one ``Match`` on the canonical pair, one ``match_activated`` event,
    the chat binding and each member's identity (``glow_chat``'s ``activate_reciprocal``, D10
    (a)); the participants read it, another member does not; each drops from the other's
    pages."""
    from glow_chat import events
    from glow_discovery import interactions
    from glow_persistence.models import ChatBinding, ChatIdentity, OutboxEvent

    one, two, third = ctx.visible(), ctx.visible(), ctx.visible()
    body = _intent(ctx, one, two, "like", ctx.page(one))
    first = ctx.profiles.data(ctx.profiles.command(one, INTERACTION, body), "interaction", "like")
    expect(first["match_id"] is None, "the first like makes no match")
    second = _act(ctx, two, one, "like")
    match = _match_of(one, two)
    expect(match is not None and second["match_id"] == str(match.id), "the second like's match")
    expect(match.state == "active" and match.version == 1, "active, version 1")
    activated = OutboxEvent.objects.filter(
        event_type=events.MATCH_ACTIVATED, aggregate_id=match.id
    ).count()
    expect(activated == 1, "one match_activated event")
    expect(ChatBinding.objects.filter(match_id=match.id).count() == 1, "one chat binding")
    for member in (one, two):
        expect(
            ChatIdentity.objects.filter(account_id=member.account_id).count() == 1,
            "each member's chat identity",
        )
    replay = interactions.interact(one.account_id, body)
    current = (replay.data or {}).get("match_id")
    expect(replay.outcome == "replayed" and current == str(match.id), "the replay shows the match")
    for member, other in ((one, two), (two, one)):
        read = ctx.profiles.data(_read_match(ctx, member, match.id), "match", "the match read")
        expect(read["other_profile_id"] == _pid(ctx, other), "each reads the other's profile")
        expect(set(read) == {"kind", "match_id", "version", "other_profile_id", "state"}, "keys")
    ctx.profiles.refused(_read_match(ctx, third, match.id), 404, "not_found", "another member")
    for viewer, other in ((one, two), (two, one)):
        for collection in ("recommendations", "discovery"):
            expect(_pid(ctx, other) not in _shown(ctx, viewer, collection), "matched: not shown")
    return "one match, one match_activated event, one binding; participants only; not shown"


@case("match.no_route_creates_a_match", "8", "D10", "F09")
def no_route_creates_a_match(ctx: DiscoveryContext) -> str:
    """No route takes a match intent (F09): the suite serves exactly SV1's identity routes, SV2's
    member routes, Stage A's page route and Stage B's five action routes, each with its view, and
    no other (so no route at any path can create a match); Stage B's request DTOs are the four
    commands; an interaction's action is only like or pass; and no path makes a match."""
    from django.urls import get_resolver
    from glow_identity.urls import urlpatterns as identity_routes
    from glow_persistence.models import Match
    from glow_profiles.urls import urlpatterns as profile_routes

    def served(patterns: Any, prefix: str = "") -> set[tuple[str, str]]:
        found: set[tuple[str, str]] = set()
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                found |= served(pattern.url_patterns, prefix + str(pattern.pattern))
                continue
            callback = getattr(pattern, "callback", None)
            view = getattr(callback, "view_class", None) or callback
            found.add((prefix + str(pattern.pattern), str(getattr(view, "__qualname__", view))))
        return found

    one, two = ctx.visible(), ctx.visible()
    before = Match.objects.count()
    stage_b = {
        ("api/v1/discovery/page", "PageView"),
        ("api/v1/discovery/interaction", "InteractionView"),
        ("api/v1/discovery/interaction/undo", "UndoView"),
        ("api/v1/matches/unmatch", "UnmatchView"),
        ("api/v1/matches/<uuid:match_id>", "MatchView"),
        ("api/v1/blocks", "BlockView"),
    }
    everything = served(get_resolver().url_patterns)
    expected = served(identity_routes) | served(profile_routes) | stage_b
    expect(
        everything == expected,
        f"exactly the routes the suite serves ({len(everything - expected)} unexpected,"
        f" {len(expected - everything)} missing)",
    )
    definitions = set()
    for pattern in get_resolver().url_patterns:
        view = getattr(getattr(pattern, "callback", None), "view_class", None)
        if view is not None and getattr(view, "definition", None):
            definitions.add(str(view.definition))
    expect(
        definitions
        >= {"InteractionIntent", "InteractionUndoIntent", "UnmatchIntent", "BlockIntent"}
        and not any("match" in name.lower() and name != "UnmatchIntent" for name in definitions),
        f"the commands' requests ({', '.join(sorted(definitions))})",
    )
    body = dict(_intent(ctx, one, two, "like", ctx.page(one)), action="match")
    ctx.profiles.refused(ctx.profiles.command(one, INTERACTION, body), 400, "invalid_request", "m")
    reply = ctx.profiles.call(one, "POST", MATCHES, {"pair": [_pid(ctx, one), _pid(ctx, two)]})
    expect(reply.status == 404, "no route at the matches path")
    expect(Match.objects.count() == before, "no match written")
    return (
        f"exactly {len(expected)} routes served ({len(stage_b)} of SV3's), none taking a match"
        " intent; matches come only from reciprocal likes"
    )


@case("match.activate_reciprocal_refuses_what_activate_match_refuses", "8", "D10")
def activate_reciprocal_refuses(ctx: DiscoveryContext) -> str:
    """D10 (a)'s writer: ``activate_reciprocal`` refuses everything ``activate_match`` refuses,
    with the same reason (a self pair, an account not active, an active block, an existing pair,
    a profile not visible, a consent not current), and a missing ``liked`` row in either
    direction (``not_reciprocal``); a refusal writes nothing."""
    from glow_discovery.interactions import chat
    from glow_profiles import operations

    reasons: list[str] = []

    def both_refuse(first: UUID, second: UUID, reason: str, what: str) -> None:
        before = _counts()
        one = chat().activate_match(first, second)
        two = chat().activate_reciprocal(first, second)
        expect(
            (one.outcome, one.reason) == ("refused", reason)
            and (two.outcome, two.reason) == ("refused", reason),
            f"{what}: both refuse, {reason}",
        )
        expect(_counts() == before, f"{what}: nothing written")
        reasons.append(reason)

    def liked_pair() -> tuple[Member, Member]:
        a, b = ctx.visible(), ctx.visible()
        ctx.seed_interaction(a.account_id, b.account_id, "liked")
        ctx.seed_interaction(b.account_id, a.account_id, "liked")
        return a, b

    a, b = liked_pair()
    both_refuse(a.account_id, a.account_id, "not_a_member", "a self pair")
    ctx.block(a.account_id, b.account_id)
    both_refuse(a.account_id, b.account_id, "blocked", "an active block")
    c, d = liked_pair()
    ctx.seed_match(c.account_id, d.account_id, "unmatched")
    both_refuse(c.account_id, d.account_id, "match_exists", "an existing pair")
    e, f = liked_pair()
    _visibility(ctx, e, "pause")
    both_refuse(e.account_id, f.account_id, "profile_unavailable", "a paused profile")
    g, h = liked_pair()
    ctx.profiles.data(ctx.profiles.withdraw_onboarding(g), "onboarding", "the withdrawal")
    both_refuse(g.account_id, h.account_id, "profile_unavailable", "a withdrawal, which hides")
    n, o = liked_pair()
    _seed_withdrawn_consent(n)
    both_refuse(n.account_id, o.account_id, "consent_not_current", "a withdrawn consent")
    i, j = liked_pair()
    expect(operations.chat().suspend(i.account_id).outcome == "applied", "the suspension")
    both_refuse(i.account_id, j.account_id, "account_not_active", "a suspended account")
    k, m = ctx.visible(), ctx.visible()
    for liker, other in ((k, m), (m, k)):
        ctx.seed_interaction(liker.account_id, other.account_id, "liked")
        before = _counts()
        refused = chat().activate_reciprocal(k.account_id, m.account_id)
        expect((refused.outcome, refused.reason) == ("refused", "not_reciprocal"), "one way only")
        expect(_counts() == before, "a one-way like writes nothing")
        from glow_persistence.models import DirectionalInteraction

        DirectionalInteraction.objects.filter(
            actor_id=liker.account_id, target_id=other.account_id
        ).delete()
    reasons.append("not_reciprocal")
    return f"refused alike: {', '.join(reasons)}; a liked row missing either way: not_reciprocal"


@case("concurrency.reciprocal_likes_at_once", "8", "DB05", "D10", "D14")
def reciprocal_likes_at_once(ctx: DiscoveryContext) -> str:
    """DB05: simultaneous reciprocal likes from separate connections, in both arrival orders,
    make one match and one ``match_activated`` event: the two likes lock the same two accounts in
    the same order, so the later one waits, then finds the earlier one's ``liked`` row and makes
    the match, while the earlier one returns ``liked`` with no match. And repeated likes with fresh
    keys, at once from separate connections, make one row."""
    from glow_chat import events
    from glow_discovery import interactions
    from glow_persistence.models import DirectionalInteraction, Match, OutboxEvent

    from glow_ordering_proof.observe import observe_lock_wait

    seen: list[str] = []
    for low_first in (True, False):
        low, high = sorted((ctx.visible(), ctx.visible()), key=lambda m: m.account_id)
        intents = {
            low.account_id: _intent(ctx, low, high, "like", ctx.page(low)),
            high.account_id: _intent(ctx, high, low, "like", ctx.page(high)),
        }
        lead, follow = (low, high) if low_first else (high, low)
        lead_probe, follow_probe = _Held("after_first_lock", "before_commit"), _Held()
        leading = _Worker(
            partial(
                interactions.interact,
                lead.account_id,
                intents[lead.account_id],
                probe=lead_probe,
            )
        )
        following = _Worker(
            partial(
                interactions.interact,
                follow.account_id,
                intents[follow.account_id],
                probe=follow_probe,
            )
        )
        waited = None
        try:
            leading.start()
            holding = lead_probe.reached["after_first_lock"].wait(REACH_SECONDS)
            following.start()
            follower_pid = _wait_pid(follow_probe)
            assert lead_probe.pid is not None
            waited = observe_lock_wait(
                follower_pid,
                holder_pid=lead_probe.pid,
                finished=following.ended,
                timeout=REACH_SECONDS,
            )
            lead_probe.release["after_first_lock"].set()
            committing = lead_probe.reached["before_commit"].wait(REACH_SECONDS)
        finally:
            _finish([lead_probe, follow_probe], [leading, following])
        order = "the lower account's like first" if low_first else "the higher account's first"
        expect(holding and committing, f"{order}: the first like held its locks")
        expect(waited is not None and waited.observed, f"{order}: the second waited on them")
        expect(leading.ok() and following.ok(), f"{order}: both apply")
        expect(leading.result.data["match_id"] is None, f"{order}: the first makes no match")
        match = _match_of(low, high)
        expect(match is not None, f"{order}: the match")
        expect(following.result.data["match_id"] == str(match.id), f"{order}: the second's match")
        low_id, high_id = low.account_id, high.account_id
        expect(
            Match.objects.filter(account_low_id=low_id, account_high_id=high_id).count() == 1,
            f"{order}: one match on the canonical pair",
        )
        expect(
            OutboxEvent.objects.filter(
                event_type=events.MATCH_ACTIVATED, aggregate_id=match.id
            ).count()
            == 1,
            f"{order}: one match_activated event",
        )
        again = _intent(ctx, lead, follow, "like", ctx.page(lead))
        ctx.profiles.refused(
            ctx.profiles.command(lead, INTERACTION, again), 409, "stale_version", "a fresh key"
        )
        seen.append(order)
    actor, target = ctx.visible(), ctx.visible()
    page = ctx.page(actor)
    first = _intent(ctx, actor, target, "like", page)
    second = _intent(ctx, actor, target, "like", page)
    probes = [_Held("after_first_lock"), _Held("after_first_lock")]
    workers = [
        _Worker(partial(interactions.interact, actor.account_id, body, probe=probe))
        for body, probe in zip((first, second), probes, strict=True)
    ]
    try:
        workers[0].start()
        expect(probes[0].reached["after_first_lock"].wait(REACH_SECONDS), "the first holds")
        workers[1].start()
        _wait_pid(probes[1])
        probes[0].release["after_first_lock"].set()
        probes[1].release["after_first_lock"].set()
    finally:
        _finish(probes, workers)
    outcomes = sorted(worker.outcome() for worker in workers)
    expect(sum(worker.ok() for worker in workers) == 1, f"one like applies ({', '.join(outcomes)})")
    rows = DirectionalInteraction.objects.filter(
        actor_id=actor.account_id, target_id=target.account_id
    )
    expect(rows.count() == 1 and rows.first().version == 1, "one row, version 1")
    return f"{' and '.join(seen)}: one match, one event; fresh keys at once: one row"


# -- 9. changes during a like (acceptance check 9; DB10; D2) ----------------------------------


@case("concurrency.changes_during_a_like_are_seen", "9", "DB10", "D2", "D9", "D14")
def changes_during_a_like_are_seen(ctx: DiscoveryContext) -> str:
    """DB10: each change of D14's list (a block, an unblock, a pause, a consent withdrawal, a
    preference change, a settings publication), held at its commit while a like waits on its
    locks, from separate connections, is seen by the like once it commits: the like is refused
    with the generic stale response, or, after the unblock, applies."""
    from glow_discovery import interactions
    from glow_domain import profile_settings as ps
    from glow_profiles import operations, staff

    from glow_ordering_proof.observe import observe_lock_wait

    def pause(actor: Member, target: Member) -> Callable[..., Any]:
        version = ctx.profiles.get(target, "/api/v1/profile", "own_profile")["version"]
        body = {"operation": "visibility", "meta": ctx.profiles.meta(version), "action": "pause"}
        ctx.profiles.remember(target.account_id, body)
        return partial(operations.set_visibility, target.account_id, body)

    def withdraw(actor: Member, target: Member) -> Callable[..., Any]:
        current = ctx.profiles.get(target, "/api/v1/consent", "onboarding")
        label = ctx.profiles.catalog(target)["consents"]["onboarding"]["policy_version"]
        body = {
            "operation": "consent",
            "meta": ctx.profiles.meta(current["version"]),
            "policy_version": label,
            "decision": "withdrawn",
        }
        ctx.profiles.remember(target.account_id, body)
        return partial(operations.decide_onboarding_consent, target.account_id, body)

    def narrow(actor: Member, target: Member) -> Callable[..., Any]:
        current = ctx.profiles.get(target, "/api/v1/profile/preferences", "own_preferences")
        body = {
            "operation": "preferences",
            "meta": ctx.profiles.meta(current["version"]),
            "policy_version": ctx.profiles.catalog(target)["policy_version"],
            "selections": [
                {"dimension": name, "accepted_option_ids": ["man"] if name == "gender" else ["all"]}
                for name in ("gender", "orientation", "looking_for", "relationship_status")
            ],
        }
        ctx.profiles.remember(target.account_id, body)
        return partial(operations.set_preferences, target.account_id, body)

    def publish(actor: Member, target: Member) -> Callable[..., Any]:
        return partial(
            staff.publish_setting,
            ps.ONBOARDING_CONSENT,
            ctx.current(ps.ONBOARDING_CONSENT),
            staff_subject="staff:discovery-proof",
            reason="SV3-proof",
            request_id=uuid4(),
        )

    def block(actor: Member, target: Member) -> Callable[..., Any]:
        return partial(operations.chat().block, target.account_id, actor.account_id)

    def unblock(actor: Member, target: Member) -> Callable[..., Any]:
        ctx.block(target.account_id, actor.account_id)
        return partial(operations.chat().unblock, target.account_id, actor.account_id)

    # Each change, and what the like answers once it sees it: the generic stale response for a
    # change of the pair's eligibility; ``forbidden`` for the onboarding consent's new version,
    # which the actor's own acceptance then fails too (D3's CONSENT; the viewer's own predicate);
    # and, after the unblock, the like applies.
    changes: list[tuple[str, Callable[[Member, Member], Callable[..., Any]], str]] = [
        ("a block", block, "stale_version"),
        ("an unblock", unblock, "applied"),
        ("a pause", pause, "stale_version"),
        ("a consent withdrawal", withdraw, "stale_version"),
        ("a preference change", narrow, "stale_version"),
        ("a settings publication", publish, "forbidden"),
    ]
    seen: list[str] = []
    for name, prepare, answer in changes:
        actor, target = ctx.visible(), ctx.visible()
        page = ctx.page(actor)
        expect(_pid(ctx, target) in ctx.ids(page), f"{name}: the target in the actor's batch")
        writer = prepare(actor, target)
        body = _intent(ctx, actor, target, "like", page)
        held, like_probe = _Held("before_commit"), _Held()
        change = _Worker(partial(writer, probe=held))
        like = _Worker(partial(interactions.interact, actor.account_id, body, probe=like_probe))
        waited = None
        try:
            change.start()
            holding = held.reached["before_commit"].wait(REACH_SECONDS)
            like.start()
            pid = _wait_pid(like_probe)
            assert held.pid is not None
            waited = observe_lock_wait(
                pid, holder_pid=held.pid, finished=like.ended, timeout=REACH_SECONDS
            )
        finally:
            _finish([held, like_probe], [change, like])
        expect(holding, f"{name}: the change held its locks at its commit")
        expect(change.ok(), f"{name}: the change applies ({change.outcome()})")
        expect(waited is not None and waited.observed, f"{name}: the like waited on it")
        if answer == "applied":
            expect(like.ok(), f"{name}: the like sees it and applies ({like.outcome()})")
        else:
            expect(
                like.result is not None
                and (like.result.outcome, like.result.code) == ("refused", answer),
                f"{name}: the like sees it and is refused, {answer} ({like.outcome()})",
            )
            expect(_row(actor, target) is None, f"{name}: the refused like wrote nothing")
        seen.append(name)
    return f"{len(seen)} changes, each committed while a like waited, each seen by the like"


# -- 10. unmatch and block (acceptance check 10; D11; F10, F13) -------------------------------


@case("unmatch.revokes_contact_and_never_rematches", "10", "11", "D11", "D12", "F10")
def unmatch_revokes_contact(ctx: DiscoveryContext) -> str:
    """F10: a participant's unmatch, through ``glow_chat``'s ``unmatch``, revokes contact with no
    eligibility or policy prerequisite: a send applied before it is refused after it. Another
    member's match is ``not_found``; a stale version is ``stale_version``. Unmatch is final (D12):
    neither member appears in the other's pages, and no like makes a second match or reactivates
    the first."""
    from glow_chat import events
    from glow_persistence.models import Match, OutboxEvent

    one, two, third = ctx.visible(), ctx.visible(), ctx.visible()
    broader = ctx.page(one, "discovery")
    match = _matched(ctx, one, two)
    sent = _send(one, match.id)
    expect(sent.outcome == "authorized", f"a send before the unmatch applies ({sent.reason})")
    _, foreign = _unmatch(ctx, third, match)
    ctx.profiles.refused(foreign, 404, "not_found", "another member's match")
    _, stale = _unmatch(ctx, one, match, expected=match.version + 5)
    ctx.profiles.refused(stale, 409, "stale_version", "a stale version")
    body, reply = _unmatch(ctx, one, match)
    out = ctx.profiles.data(reply, "match", "the unmatch")
    expect(out["state"] == "unmatched" and out["version"] == match.version + 1, "unmatched")
    again = ctx.profiles.data(ctx.profiles.command(one, UNMATCH, body), "match", "the replay")
    expect(again == out, "an identical unmatch replays")
    refused = _send(one, match.id)
    expect(refused.outcome == "refused", f"a send after the unmatch is refused ({refused.reason})")
    _, by_two = _unmatch(ctx, two, match)
    theirs = ctx.profiles.data(by_two, "match", "the other's unmatch")
    expect(
        (theirs["match_id"], theirs["version"], theirs["state"])
        == (out["match_id"], out["version"], "unmatched")
        and theirs["other_profile_id"] == _pid(ctx, one),
        "the other's unmatch changes nothing",
    )
    revoked = OutboxEvent.objects.filter(event_type=events.CONTACT_REVOKED, aggregate_id=match.id)
    expect(revoked.count() == 1, "one contact_revoked event")
    for viewer, other in ((one, two), (two, one)):
        for collection in ("recommendations", "discovery"):
            expect(_pid(ctx, other) not in _shown(ctx, viewer, collection), "not shown again")
    held = (Match.objects.count(), Match.objects.get(pk=match.id).version)
    ctx.profiles.refused(
        ctx.profiles.command(one, INTERACTION, _intent(ctx, one, two, "like", broader)),
        409,
        "stale_version",
        "a like after the unmatch, through a batch from before the match",
    )
    current = Match.objects.get(pk=match.id)
    expect(
        (Match.objects.count(), current.version) == held and current.state == "unmatched",
        "no second match, and the first stays unmatched",
    )
    return "the unmatch revokes the send; final: not shown, no rematch; others refused"


@case("block.works_after_unmatch_and_while_paused", "10", "D11", "F13")
def block_after_unmatch_and_paused(ctx: DiscoveryContext) -> str:
    """F13: a block, through ``glow_chat``'s ``block``, works after an unmatch and while the actor
    is paused; it refuses a send; an unblock restores no match and no send. The blocked member
    cannot learn the direction: a restricted match reads the same to both participants, and the
    blocked member's own block answers as any first block does."""
    from glow_persistence.models import Match

    one, two = ctx.visible(), ctx.visible()
    match = _matched(ctx, one, two)
    _unmatch(ctx, one, match)
    first_block = _block(ctx, one, two, "block")[1]
    code = (first_block.body or {}).get("code")
    expect(first_block.status == 200, f"after an unmatch: answers {first_block.status} {code}")
    after = ctx.profiles.data(first_block, "block", "after an unmatch")
    expect(after["state"] == "active" and after["version"] == 1, "a block after an unmatch")
    lifted = ctx.profiles.data(_block(ctx, one, two, "unblock")[1], "block", "the unblock")
    expect(lifted["state"] == "removed" and lifted["version"] == 2, "removed")
    expect(Match.objects.get(pk=match.id).state == "unmatched", "the unblock restores no match")
    three, four = ctx.visible(), ctx.visible()
    paired = _matched(ctx, three, four)
    expect(_send(four, paired.id).outcome == "authorized", "a send before the block applies")
    _visibility(ctx, three, "pause")
    body, reply = _block(ctx, three, four, "block")
    paused = ctx.profiles.data(reply, "block", "while paused")
    expect(paused["state"] == "active", "a block while the actor is paused")
    replay = ctx.profiles.data(ctx.profiles.command(three, BLOCKS, body), "block", "the replay")
    expect(replay == paused, "an identical block replays")
    ctx.profiles.refused(
        ctx.profiles.command(three, BLOCKS, dict(body, action="unblock")),
        409,
        "idempotency_conflict",
        "the same key, the other action",
    )
    restricted = Match.objects.get(pk=paired.id)
    expect(restricted.state == "restricted", "the block restricts the match")
    expect(_send(four, paired.id).outcome == "refused", "a send after the block is refused")
    reads = [
        ctx.profiles.data(_read_match(ctx, member, paired.id), "match", "the read")
        for member in (three, four)
    ]
    expect(
        {r["state"] for r in reads} == {"restricted"}
        and {tuple(sorted(r)) for r in reads} == {tuple(sorted(reads[0]))},
        "both participants read the same restricted match, with no direction",
    )
    own = ctx.profiles.data(_block(ctx, four, three, "block")[1], "block", "the blocked's block")
    expect(own["state"] == "active" and own["version"] == 1, "the blocked member's own block")
    expect(set(own) == set(paused), "it answers as any first block does")
    ctx.profiles.data(_block(ctx, four, three, "unblock")[1], "block", "its unblock")
    ctx.profiles.data(_block(ctx, three, four, "unblock")[1], "block", "the unblock")
    _visibility(ctx, three, "resume")
    expect(Match.objects.get(pk=paired.id).state == "restricted", "no match restored")
    expect(_send(four, paired.id).outcome == "refused", "no send restored")
    ctx.profiles.refused(_block(ctx, one, two, "block", expected=7)[1], 409, "stale_version", "v")
    five, six = ctx.visible(), ctx.visible()
    _visibility(ctx, six, "pause")
    target_paused = ctx.profiles.data(_block(ctx, five, six, "block")[1], "block", "paused target")
    expect(target_paused["state"] == "active", "a block of a paused member")
    return "block after unmatch and while paused; send refused; unblock restores nothing; hidden"


# -- 11. resurfacing, undo and rematch (acceptance check 11; D12; OD-60 R) --------------------


@case("settings.resurfacing_off_and_on", "11", "D12", "D7")
def resurfacing_off_and_on(ctx: DiscoveryContext) -> str:
    """Off (the launch default), a pass excludes the pair from the actor's pages for good; on
    with a waiting period, a pass decided at least ``waiting_days`` ago excludes no longer, and a
    later one still does; a like over the actor's own resurfaced pass is F08's ``like`` from
    ``passed`` on the same row, its version advanced."""
    from glow_domain import profile_settings as ps

    viewer, early, recent = ctx.visible(), ctx.visible(), ctx.visible()
    expect(ctx.current(ps.RESURFACING)["enabled"] is False, "off at launch")
    _act(ctx, viewer, early, "pass")
    _act(ctx, viewer, recent, "pass")
    _decided(viewer, early, 400)
    expect(_pid(ctx, early) not in _shown(ctx, viewer), "off: a pass 400 days ago still excludes")
    try:
        _publish(ctx, ps.RESURFACING, {"enabled": True, "waiting_days": 7})
        _decided(viewer, early, 8)
        _decided(viewer, recent, 6)
        shown = _shown(ctx, viewer)
        expect(_pid(ctx, early) in shown, "on: a pass 8 days ago (waiting 7) resurfaces")
        expect(_pid(ctx, recent) not in shown, "on: a pass 6 days ago still excludes")
        row = _row(viewer, early)
        liked = _act(ctx, viewer, early, "like")
        expect(liked["state"] == "liked" and liked["version"] == 2, "a like over the pass")
        expect(_row(viewer, early).id == row.id, "the same row, its version advanced")
    finally:
        _publish(ctx, ps.RESURFACING, {"enabled": False, "waiting_days": None})
    return "off: a pass excludes for good; on (7 days): 8 days resurfaces, 6 does not; like over it"


@case("settings.undo_off_and_on", "11", "D12", "D13")
def undo_off_and_on(ctx: DiscoveryContext) -> str:
    """Off, undo is ``forbidden`` and writes nothing; on with a waiting period, only the actor's
    most recent pass, within ``waiting_days`` of it, is withdrawn: the row kept, its version
    advanced (an expected version from before it no longer matches); a withdrawn pass excludes
    nothing; a pass past the waiting period, or not the most recent, is ``state_conflict``."""
    from glow_discovery import interactions
    from glow_domain import profile_settings as ps
    from glow_persistence.models import IdempotencyRecord

    viewer, first, second, third = ctx.visible(), ctx.visible(), ctx.visible(), ctx.visible()
    expect(ctx.current(ps.UNDO)["enabled"] is False, "off at launch")
    _act(ctx, viewer, first, "pass")
    before = _counts()
    _, off = _undo(ctx, viewer, first)
    ctx.profiles.refused(off, 403, "forbidden", "undo while off")
    expect(_counts() == before, "nothing written while off")
    try:
        _publish(ctx, ps.UNDO, {"enabled": True, "waiting_days": 1})
        _act(ctx, viewer, second, "pass")
        _, older = _undo(ctx, viewer, first)
        ctx.profiles.refused(older, 409, "state_conflict", "a pass that is not the most recent")
        _, stale = _undo(ctx, viewer, second, expected=0)
        ctx.profiles.refused(stale, 409, "stale_version", "a stale version")
        row = _row(viewer, second)
        body, reply = _undo(ctx, viewer, second)
        out = ctx.profiles.data(reply, "interaction_undo", "the undo")
        expect(
            out
            == {
                "kind": "interaction_undo",
                "target_profile_id": _pid(ctx, second),
                "version": 2,
                "state": "withdrawn",
            },
            "the withdrawn pass, version 2",
        )
        expect(_row(viewer, second).id == row.id, "the same row, never deleted and recreated")
        expect(
            IdempotencyRecord.objects.filter(
                actor_id=viewer.account_id, operation="interaction_undo", outcome_code="withdrawn"
            ).count()
            == 1,
            "the undo's receipt",
        )
        replay = ctx.profiles.data(
            ctx.profiles.command(viewer, UNDO, body), "interaction_undo", "r"
        )
        expect(replay == out, "an identical undo replays")
        page = ctx.page(viewer)
        expect(_pid(ctx, second) in ctx.ids(page), "a withdrawn pass excludes nothing")
        ctx.profiles.refused(
            ctx.profiles.command(
                viewer, INTERACTION, _intent(ctx, viewer, second, "like", page, expected=1)
            ),
            409,
            "stale_version",
            "an expected version from before the undo",
        )
        liked = _act(ctx, viewer, second, "like", page)
        expect(liked["version"] == 3 and liked["state"] == "liked", "a like over the withdrawal")
        _act(ctx, viewer, third, "pass")
        _decided(viewer, first, 3)
        _decided(viewer, third, 2)
        body, late = _undo(ctx, viewer, third)
        ctx.profiles.refused(late, 409, "state_conflict", "a pass past the waiting period")
        direct = interactions.undo(viewer.account_id, dict(body, meta=ctx.profiles.meta(1)))
        expect(direct.reason == "undo_window_ended", "refused as past its waiting period")
    finally:
        _publish(ctx, ps.UNDO, {"enabled": False, "waiting_days": None})
    return (
        "off: forbidden; on (1 day): the most recent pass withdrawn, the row kept; others refused"
    )


@case("settings.rematch_cannot_be_switched_on", "11", "D12")
def rematch_cannot_be_switched_on(ctx: DiscoveryContext) -> str:
    """Rematch is not built (D12; DM-60): a publication of ``discovery.rematch`` with ``enabled``
    on is refused, naming ``rematch_not_built``, and writes nothing; with a block or a report
    allowed too, it names ``rematch_never_after_block_or_report`` as well."""
    from glow_domain import profile_settings as ps
    from glow_persistence.models import SettingVersion, StaffAudit
    from glow_profiles import staff

    def counts() -> tuple[int, int, str]:
        return (
            SettingVersion.objects.filter(name=ps.REMATCH).count(),
            StaffAudit.objects.count(),
            ctx.current_label(ps.REMATCH),
        )

    before = counts()
    reasons: list[str] = []
    for content in (
        {"enabled": True, "waiting_days": 30, "after_block": False, "after_report": False},
        {"enabled": True, "waiting_days": 30, "after_block": True, "after_report": False},
    ):
        result = staff.publish_setting(
            ps.REMATCH,
            content,
            staff_subject="staff:discovery-proof",
            reason="SV3-proof",
            request_id=uuid4(),
        )
        expect(result.outcome == "refused" and result.code == "invalid_request", "refused")
        expect(ps.REMATCH_NOT_BUILT in result.reason, "it names rematch_not_built")
        reasons.append(result.reason)
        expect(counts() == before, "nothing written")
    expect(ps.REMATCH_NEVER_AFTER_BLOCK_OR_REPORT in reasons[1], "and the block-or-report limit")
    return f"refused: {'; '.join(reasons)}; nothing written"


# -- 12. ownership (acceptance check 12; D13) --------------------------------------------------


@case("routes.interaction_refusals_and_ownership", "12", "D13")
def interaction_refusals_and_ownership(ctx: DiscoveryContext) -> str:
    """Every Stage B route refuses an unauthenticated request (401), another method (405), a query
    string, another content type and a body that is not its DTO (400); another member's match is
    ``not_found`` and another member's batch the generic stale response; a stale version is
    ``stale_version``. Every answer is the contract's, and nothing is cached."""
    one, two, third = ctx.visible(), ctx.visible(), ctx.visible()
    match = _matched(ctx, one, two)
    page = ctx.page(third)
    routes: list[tuple[str, str, dict[str, Any] | None]] = [
        ("POST", INTERACTION, _intent(ctx, third, one, "pass", page)),
        ("POST", UNDO, _undo_body(ctx, third, one)),
        ("POST", UNMATCH, _unmatch_body(ctx, match)),
        ("POST", BLOCKS, _block_body(ctx, one)),
        ("GET", f"{MATCHES}/{match.id}", None),
    ]
    checked = 0
    before = _counts()
    for method, path, body in routes:
        unauthenticated = ctx.profiles.call(third, method, path, body, bearer=False)
        ctx.profiles.refused(unauthenticated, 401, "unauthenticated", f"{path}: no token")
        other = "GET" if method == "POST" else "POST"
        ctx.profiles.refused(
            ctx.profiles.call(third, other, path, body), 405, "invalid_request", f"{path}: method"
        )
        ctx.profiles.refused(
            ctx.profiles.call(third, method, f"{path}?x=1", body), 400, "invalid_request", "query"
        )
        if body is not None:
            ctx.profiles.refused(
                ctx.profiles.call(third, method, path, body, content_type="text/plain"),
                400,
                "invalid_request",
                f"{path}: content type",
            )
            ctx.profiles.refused(
                ctx.profiles.call(third, method, path, dict(body, extra=1)),
                400,
                "invalid_request",
                f"{path}: not its DTO",
            )
        expect("Cache-Control: no-store" in ctx.profiles.headers[-1], f"{path}: no-store")
        checked += 1
    expect(_counts() == before, "no refusal writes")
    ctx.profiles.refused(
        ctx.profiles.command(third, UNMATCH, routes[2][2] or {}), 404, "not_found", "unmatch"
    )
    ctx.profiles.refused(_read_match(ctx, third, match.id), 404, "not_found", "another's match")
    ctx.profiles.refused(_read_match(ctx, third, uuid4()), 404, "not_found", "no such match")
    ctx.profiles.refused(
        ctx.profiles.command(two, INTERACTION, _intent(ctx, two, third, "like", page)),
        409,
        "stale_version",
        "another member's batch",
    )
    _, stale = _unmatch(ctx, one, match, expected=9)
    ctx.profiles.refused(stale, 409, "stale_version", "an unmatch at a stale version")
    _, blocked = _block(ctx, one, third, "block", expected=4)
    ctx.profiles.refused(blocked, 409, "stale_version", "a block at a stale version")
    stale_pass = _intent(ctx, one, third, "pass", ctx.page(one), expected=2)
    ctx.profiles.refused(
        ctx.profiles.command(one, INTERACTION, stale_pass),
        409,
        "stale_version",
        "an interaction at a stale version",
    )
    return f"{checked} routes refuse no token, another method, a query, a type, a body; ownership"


def _unmatch_body(ctx: DiscoveryContext, match: Any) -> dict[str, Any]:
    return {"operation": "unmatch", "meta": ctx.profiles.meta(1), "match_id": str(match.id)}


def _block_body(ctx: DiscoveryContext, target: Member) -> dict[str, Any]:
    return {
        "operation": "block",
        "meta": ctx.profiles.meta(0),
        "target_profile_id": _pid(ctx, target),
        "action": "block",
    }


def _undo_body(ctx: DiscoveryContext, actor: Member, target: Member) -> dict[str, Any]:
    return {
        "operation": "interaction_undo",
        "meta": ctx.profiles.meta(_version(actor, target)),
        "target_profile_id": _pid(ctx, target),
    }


# -- DB04 for Stage B's tables --------------------------------------------------------------------

INTERACTION_TABLES = (
    "glow_persistence_directionalinteraction",
    "glow_persistence_match",
    "glow_persistence_idempotencyrecord",
)
LOWEST = UUID("00000000-0000-4000-8000-000000000000")
HIGHEST = UUID("ffffffff-ffff-4fff-bfff-ffffffffffff")


@case("constraints.interaction_writes_are_refused", "DB04", "D9", "D10", "D12", "D18")
def interaction_writes_are_refused(ctx: DiscoveryContext) -> str:
    """A direct write no SV3 code makes, against each constraint the directional interaction,
    match and idempotency record tables declare (migration 0011's included: the interaction's
    ``withdrawn`` state and the receipt's ``withdrawn`` code), and their foreign keys, is refused by
    PostgreSQL itself, naming that constraint, and leaves nothing behind; a completed receipt with
    the ``withdrawn`` code is accepted. Harness writes only; the error's text is read for the
    constraint's name and never kept."""
    from django.db import IntegrityError, connection, transaction
    from django.utils import timezone
    from glow_persistence.models import DirectionalInteraction, IdempotencyRecord, Match

    one, two, three = ctx.profiles.member(), ctx.profiles.member(), ctx.profiles.member()
    low, high = sorted((one.account_id, two.account_id))
    other_low, other_high = sorted((one.account_id, three.account_id))
    now = timezone.now()

    def interaction(**changes: Any) -> Any:
        values: dict[str, Any] = {
            "actor_id": one.account_id,
            "target_id": two.account_id,
            "state": "liked",
            "policy_version": "fixture:sv3-db04",
        }
        values.update(changes)
        return DirectionalInteraction.objects.create(**values)

    def match(**changes: Any) -> Any:
        values: dict[str, Any] = {"account_low_id": low, "account_high_id": high}
        values.update(changes)
        return Match.objects.create(**values)

    def record(**changes: Any) -> Any:
        values: dict[str, Any] = {
            "actor_id": one.account_id,
            "operation": "interaction_undo",
            "key": "k-db04",
            "request_digest": "0" * 64,
            "result_ref": uuid4(),
            "result_version": 2,
            "outcome_code": "withdrawn",
            "state": "completed",
            "expires_at": now,
        }
        values.update(changes)
        return IdempotencyRecord.objects.create(**values)

    held = (interaction(), match(), record())
    expect(held[2].outcome_code == "withdrawn", "a completed receipt with withdrawn is accepted")

    def snapshot() -> tuple[int, int, int]:
        return (
            DirectionalInteraction.objects.count(),
            Match.objects.count(),
            IdempotencyRecord.objects.count(),
        )

    keys: dict[tuple[str, str], str] = {}
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT t.relname, a.attname, c.conname FROM pg_catalog.pg_constraint c"
            " JOIN pg_catalog.pg_class t ON c.conrelid = t.oid"
            " JOIN pg_catalog.pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)"
            " WHERE c.contype = 'f' AND t.relname = ANY(%s)",
            [list(INTERACTION_TABLES)],
        )
        for table, column, name in cursor.fetchall():
            keys[(str(table), str(column))] = str(name)
    swapped = {"actor_id": two.account_id, "target_id": one.account_id}
    writes: list[tuple[str, Callable[[], Any]]] = [
        (
            "glow_persistence_directionalinteraction_state",
            lambda: interaction(**swapped, state="undone"),
        ),
        (
            "glow_persistence_directionalinteraction_no_self",
            lambda: interaction(target_id=one.account_id),
        ),
        ("directional_interaction_pair", lambda: interaction()),
        (
            "glow_persistence_directionalinteraction_version",
            lambda: interaction(**swapped, version=0),
        ),
        (
            keys[(INTERACTION_TABLES[0], "actor_id")],
            lambda: interaction(actor_id=uuid4(), target_id=three.account_id),
        ),
        (
            keys[(INTERACTION_TABLES[0], "target_id")],
            lambda: interaction(actor_id=three.account_id, target_id=uuid4()),
        ),
        (
            "glow_persistence_match_state",
            lambda: match(account_low_id=other_low, account_high_id=other_high, state="open"),
        ),
        ("match_order", lambda: match(account_low_id=other_high, account_high_id=other_low)),
        ("match_pair", lambda: match()),
        (
            "match_contact_revision",
            lambda: match(account_low_id=other_low, account_high_id=other_high, contact_version=0),
        ),
        (
            "glow_persistence_match_version",
            lambda: match(account_low_id=other_low, account_high_id=other_high, version=0),
        ),
        (
            keys[(INTERACTION_TABLES[1], "account_low_id")],
            lambda: match(account_low_id=LOWEST, account_high_id=high),
        ),
        (
            keys[(INTERACTION_TABLES[1], "account_high_id")],
            lambda: match(account_low_id=low, account_high_id=HIGHEST),
        ),
        ("intent_dedup", lambda: record()),
        ("intent_result", lambda: record(key="k-db04-code", outcome_code="undone")),
        (
            "intent_result",
            lambda: record(key="k-db04-pending", state="pending"),
        ),
        (
            "glow_persistence_idempotencyrecord_version",
            lambda: record(key="k-db04-version", version=0),
        ),
        (
            "glow_persistence_idempotencyrecord_state",
            lambda: record(key="k-db04-state", state="done"),
        ),
    ]
    declared = {
        str(constraint.name)
        for model in (DirectionalInteraction, Match, IdempotencyRecord)
        for constraint in model._meta.constraints
    }
    covered = {constraint for constraint, _ in writes}
    expect(declared <= covered, f"a write for every constraint ({sorted(declared - covered)})")
    before = snapshot()
    for constraint, write in writes:
        named = False
        try:
            with transaction.atomic():
                write()
        except IntegrityError as error:
            named = constraint in str(error)
        expect(named, f"PostgreSQL refuses the write by {constraint}")
    expect(snapshot() == before, "the refused writes leave nothing behind")
    for row in held:
        type(row).objects.filter(pk=row.pk).delete()
    return (
        f"{len(writes)} malformed direct writes refused by PostgreSQL, each by its constraint: all"
        f" {len(declared)} the three tables declare (0011's included) and four foreign keys; a"
        " completed withdrawn receipt accepted"
    )


# -- 13 and 14 for Stage B's code ---------------------------------------------------------------


@case("interactions.logs_no_private_value", "13", "D8", "D17")
def interactions_logs_no_private_value(ctx: DiscoveryContext) -> str:
    """No log record, captured at DEBUG while Stage B's routes answer and refuse, holds a member's
    value (a birth date, a coordinate, a distance, own words, a "show me" set), a secret or an
    area ID."""
    one = ctx.visible(area=CHICAGO)
    two = ctx.visible(area=LOS_ANGELES)
    ctx.set_field(two, "gender", ["woman"], own_words="Synthetic interaction words", shown=True)
    ctx.set_sets(one, {"gender": ["woman"]})
    records: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(self.format(record))

    handler = Capture(level=logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        page = ctx.page(one)
        ctx.profiles.command(one, INTERACTION, dict(_intent(ctx, one, two, "like", page), extra=1))
        _act(ctx, one, two, "like", page)
        _act(ctx, two, one, "like")
        match = _match_of(one, two)
        _read_match(ctx, one, match.id)
        _undo(ctx, one, two)
        _unmatch(ctx, one, match)
        _block(ctx, two, one, "block")
        _block(ctx, two, one, "block", expected=9)
    finally:
        root.removeHandler(handler)
    text = "\n".join(records)
    expect(ctx.profiles.values.found_in(text) == 0, "no member value in the DEBUG capture")
    expect(ctx.profiles.ledger.found_in(text) == 0, "no secret in the DEBUG capture")
    for area_id in (CHICAGO, LOS_ANGELES):
        expect(re.search(rf"\b{area_id}\b", text) is None, "no area ID in the DEBUG capture")
    return f"{len(records)} DEBUG records: no member value, secret or area ID"


@case("interactions.pointer_order", "14", "D19")
def interactions_pointer_order(ctx: DiscoveryContext) -> str:
    """D19: each Stage B transaction that reads a setting takes all its pointers in its first
    ``read_shared`` call, in name order: the like the selection's settings, the undo its own."""
    from glow_discovery import policy
    from glow_profiles import settings_store

    one, two = ctx.visible(), ctx.visible()
    page = ctx.page(one)
    Identity = tuple[int, str]
    calls: list[tuple[Identity, tuple[str, ...], tuple[str, ...]]] = []
    real = settings_store.read_shared

    def recording(tx: Any, names: Any) -> Any:
        listed = tuple(names)
        found = real(tx, listed)
        calls.append(
            (
                (int(tx.trace.backend_pid), tx.trace.started_at.isoformat()),
                listed,
                tuple(tx.pointers),
            )
        )
        return found

    with mock.patch.object(settings_store, "read_shared", recording):
        _act(ctx, one, two, "pass", page)
        _undo(ctx, one, two)
    transactions: dict[Identity, list[tuple[tuple[str, ...], tuple[str, ...]]]] = {}
    for identity, names, held in calls:
        transactions.setdefault(identity, []).append((names, held))
    expect(len(transactions) == 2, "the pass's and the undo's transactions read their settings")
    wanted = [policy.SELECTION_SETTINGS, policy.UNDO_SETTINGS]
    for seen, expected_names in zip(transactions.values(), wanted, strict=True):
        expect(len(seen) == 1, "all the pointers in the transaction's first read_shared call")
        names, held = seen[0]
        expect(tuple(sorted(names)) == expected_names, "the transaction's settings")
        expect(list(held) == sorted(held), "held in name order")
    return "the pass and the undo each take their pointers once, in name order"
