"""The discovery cases (SV3 Stage A; its brief's acceptance checks 1 to 6 and 12 to 14, with D2 to
D8, D13, D18 and D19; DM-60's examples), each run through the HTTP endpoints with Django's test
client on the disposable discovery database, signed in through SV1's identity routes and built
through SV2's member routes.

Every case makes its own synthetic members and begins with no other ``visible`` profile
(``DiscoveryContext.hide_everyone``). Settings are global: a case that publishes one restores what
later cases rely on. Each case declares the acceptance checks it covers and returns a short detail
line or raises ``CaseFailed``; neither ever holds a member's value.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from functools import partial
from typing import Any
from unittest import mock
from uuid import UUID, uuid4

from glow_ordering_proof.discovery_support import (
    CHICAGO,
    LOS_ANGELES,
    NEW_YORK,
    PAGE,
    PHILADELPHIA,
    DiscoveryContext,
    expected_details,
    expected_refs,
    explain,
    seed_population,
)
from glow_ordering_proof.identity_support import CaseFailed, Member, expect
from glow_ordering_proof.profile_support import (
    ORIENTATION_VALUES,
    RecordingHold,
    db_today,
    test_ports,
    years_ago,
)


@dataclass(frozen=True)
class Case:
    case_id: str
    checks: tuple[str, ...]
    run: Callable[[DiscoveryContext], str]


CASES: list[Case] = []
# The suite's case count, pinned: a case lost or added without this changing fails the run before
# any case runs, and the offline tests.
CASE_COUNT = 40


def case(
    case_id: str, *checks: str
) -> Callable[[Callable[[DiscoveryContext], str]], Callable[[DiscoveryContext], str]]:
    def register(function: Callable[[DiscoveryContext], str]) -> Callable[[DiscoveryContext], str]:
        CASES.append(Case(case_id, checks, function))
        return function

    return register


# -- helpers --------------------------------------------------------------------------------


def _selection() -> Any:
    """The selection as the pages read it, without locks (the adapter's own use)."""
    from glow_discovery import policy
    from glow_profiles import settings_store

    found = {name: settings_store.read_unlocked(name) for name in policy.SELECTION_SETTINGS}
    return policy.selection(found, db_today())


def _service() -> Any:
    from glow_discovery.eligibility import OrmEligibilityEvidence
    from glow_domain.trusted_eligibility import TrustedEligibilityService

    return TrustedEligibilityService(OrmEligibilityEvidence(_selection()))


def _decision(viewer: Member | UUID, candidate: Member | UUID) -> Any:
    from glow_domain.identity import AccountId

    def account(who: Member | UUID) -> AccountId:
        return AccountId(str(who.account_id if isinstance(who, Member) else who))

    return _service().evaluate(account(viewer), account(candidate))


def _ready(viewer: Member, candidate: Member) -> bool:
    from glow_domain.trusted_eligibility import EligibilityDecisionState

    return bool(_decision(viewer, candidate).state is EligibilityDecisionState.READY)


def _rules(viewer: Member, candidate: Member) -> set[tuple[str, str]]:
    decision = _decision(viewer, candidate)
    if decision.eligibility is None:
        return set()
    return {(e.subject.value, e.rule.value) for e in decision.eligibility.exclusions}


def _sees(ctx: DiscoveryContext, viewer: Member, candidate: Member) -> bool:
    """Whether a fresh recommendations batch of ``viewer`` holds ``candidate``, and the trusted
    adapter agrees (D2: one rule set for both)."""
    shown = ctx.profile_id(candidate) in ctx.sees(viewer)
    expect(shown == _ready(viewer, candidate), "the page and the trusted adapter agree")
    return shown


def _both(ctx: DiscoveryContext, first: Member, second: Member) -> tuple[bool, bool]:
    return _sees(ctx, first, second), _sees(ctx, second, first)


def _account(account_id: UUID) -> Any:
    from glow_persistence.models import AppAccount

    return AppAccount.objects.get(pk=account_id)


def _visibility(ctx: DiscoveryContext, member: Member, action: str) -> None:
    current = ctx.profiles.get(member, "/api/v1/profile", "own_profile")
    body = {
        "operation": "visibility",
        "meta": ctx.profiles.meta(current["version"]),
        "action": action,
    }
    ctx.profiles.data(
        ctx.profiles.command(member, "/api/v1/profile/visibility", body), "own_profile", action
    )


def _summary(ctx: DiscoveryContext, member: Member, summary: str) -> str:
    reply = ctx.profiles.profile(member, summary=summary)
    return str(ctx.profiles.data(reply, "own_profile", "the profile edit")["visibility"])


def _profile_state(account_id: UUID, state: str) -> None:
    """A profile state written in setup (test data), for the states no member route reaches."""
    from glow_persistence.models import Profile

    Profile.objects.filter(account_id=account_id).update(state=state)


def _refused_page(ctx: DiscoveryContext, member: Member, status: int, code: str, what: str) -> None:
    ctx.profiles.refused(ctx.page_reply(member), status, code, what)


def _batches(account_id: UUID) -> set[str]:
    from glow_persistence.models import RecommendationBatch

    return {
        str(b)
        for b in RecommendationBatch.objects.filter(account_id=account_id).values_list(
            "id", flat=True
        )
    }


def _stale_shape(reply: Any) -> dict[str, Any]:
    body = dict(reply.body or {})
    body.pop("request_id", None)
    return body


def _empty_shape(page: dict[str, Any]) -> dict[str, Any]:
    shape = dict(page)
    for name in ("batch_id", "expires_at"):
        shape.pop(name, None)
    return shape


class _Probe:
    """A transaction probe for the pages (D2): it only signals; the case's callback runs the
    concurrent writes in another thread, on its own connection, and waits for them."""

    on_begin = None
    after_first_lock = None
    after_locks = None
    before_commit = None

    def __init__(self, before_recheck: Callable[[], None]) -> None:
        self.before_recheck = before_recheck


def _in_thread(work: Callable[[], None]) -> None:
    from django.db import connection

    failure: list[BaseException] = []

    def run() -> None:
        try:
            work()
        except BaseException as exc:  # noqa: BLE001 - re-raised by type in the case's thread
            failure.append(exc)
        finally:
            connection.close()

    thread = threading.Thread(target=run)
    thread.start()
    thread.join(60)
    expect(not thread.is_alive(), "the concurrent writes finished")
    if failure:
        raise CaseFailed(f"the concurrent writes failed: {type(failure[0]).__name__}")


# -- 1. the predicates (acceptance check 1; D2, D3) -------------------------------------------


@case("adapter.both_ways_agree", "1", "Outcome 1", "D2", "D3")
def adapter_both_ways_agree(ctx: DiscoveryContext) -> str:
    from django.db import transaction
    from glow_discovery.eligibility import OrmPairActionTransaction
    from glow_domain.identity import AccountId
    from glow_domain.trusted_eligibility import EligibilityDecisionState, EvidenceProblem

    viewer, candidate = ctx.visible(), ctx.visible()
    expect(_both(ctx, viewer, candidate) == (True, True), "two visible members see each other")
    expect(ctx.profile_id(viewer) not in ctx.sees(viewer), "a member is never their own candidate")
    expect(ctx.sees(viewer, "discovery") == set(), "broader leaves out the recommended")
    missing = _decision(viewer, uuid4())
    expect(missing.state is EligibilityDecisionState.REJECTED, "a missing account is rejected")
    expect(missing.problem is EvidenceProblem.MISSING_EVIDENCE, "as missing evidence")
    expect(("pair", "self") in _rules(viewer, viewer), "a member is never their own candidate")
    selection = _selection()
    pair = OrmPairActionTransaction(selection)
    v, c = AccountId(str(viewer.account_id)), AccountId(str(candidate.account_id))
    with transaction.atomic():
        evidence = pair.acquire(v, c)
        expect(evidence is not None, "the action's read finds both members")
        assert evidence is not None
        expect(pair.commit_if_current(evidence.current_version), "unchanged evidence is current")
    ctx.set_filters(candidate, minimum=19)
    with transaction.atomic():
        expect(not pair.commit_if_current(evidence.current_version), "a change makes it stale")
    try:
        pair.acquire(v, c)
    except RuntimeError:
        outside = True
    else:
        outside = False
    expect(outside, "the action's read refuses to run outside a transaction")
    return "both directions; the adapter agrees with the pages; missing, self and stale refused"


@case("predicates.adult_state", "1", "D3")
def adult_state(ctx: DiscoveryContext) -> str:
    from glow_persistence.models import AccountAgeState

    viewer, candidate = ctx.visible(), ctx.visible()
    kept = AccountAgeState.objects.get(account_id=candidate.account_id)
    born = kept.birth_date
    # D3: visible can lag the age state, so ADULT is read directly. The lag is seeded in setup.
    AccountAgeState.objects.filter(pk=kept.pk).update(
        state="unknown", method="none", policy_version=None, birth_date=None
    )
    ctx.expect_visible(candidate)
    expect(not _sees(ctx, viewer, candidate), "an unknown age state excludes the candidate")
    expect(("candidate", "adult") in _rules(viewer, candidate), "by the adult rule")
    AccountAgeState.objects.filter(pk=kept.pk).update(
        state="self_declared_adult",
        method="self_declaration",
        policy_version="adult.self-declaration.v1",
        birth_date=born,
    )
    expect(_sees(ctx, viewer, candidate), "restored, the candidate passes")
    own = AccountAgeState.objects.get(account_id=viewer.account_id)
    before = _batches(viewer.account_id)
    AccountAgeState.objects.filter(pk=own.pk).update(
        state="unknown", method="none", policy_version=None, birth_date=None
    )
    _refused_page(ctx, viewer, 403, "forbidden", "a viewer outside the accepted states")
    expect(_batches(viewer.account_id) == before, "no batch is computed for them")
    AccountAgeState.objects.filter(pk=own.pk).update(
        state="self_declared_adult",
        method="self_declaration",
        policy_version="adult.self-declaration.v1",
        birth_date=own.birth_date,
    )
    expect(_sees(ctx, viewer, candidate), "restored, the viewer pages again")
    return "unknown excludes the candidate and refuses the viewer, each passing when restored"


@case("predicates.consent", "1", "D3", "D7")
def consent(ctx: DiscoveryContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import ConsentDecision

    viewer, candidate, other = ctx.visible(), ctx.visible(), ctx.visible()
    first = ctx.page(viewer, limit=1)
    expect(first["next_cursor"] is not None, "a first page with a cursor")
    # DM-54, Q3: a new onboarding version fails every older acceptance at once, and every batch.
    ctx.publish(ps.ONBOARDING_CONSENT, ctx.current(ps.ONBOARDING_CONSENT))
    ctx.stale(viewer, "recommendations", first["next_cursor"], "a cursor after a new consent")
    ctx.expect_visible(candidate)
    _refused_page(ctx, viewer, 403, "forbidden", "a viewer at an old consent version")
    ctx.profiles.accept_onboarding(viewer)
    expect(not _sees(ctx, viewer, candidate), "a candidate at an old version is excluded")
    expect(("candidate", "consent") in _rules(viewer, candidate), "by the consent rule")
    ctx.profiles.accept_onboarding(candidate)
    ctx.profiles.accept_onboarding(other)
    expect(_sees(ctx, viewer, candidate), "accepted at the current version, it passes")
    # Every reader filters by purpose: sensitive decisions numbered above the onboarding one change
    # nothing; a sensitive decision alone never satisfies it.
    latest = (
        ConsentDecision.objects.filter(account_id=candidate.account_id, purpose="onboarding")
        .order_by("-version")
        .first()
    )
    assert latest is not None
    label = ctx.current_label(ps.SENSITIVE_CONSENT)
    for number in range(1, int(latest.version) + 3):
        ConsentDecision.objects.create(
            account_id=candidate.account_id,
            purpose="sensitive_profile",
            policy_version=label,
            state="accepted",
            decided_at=latest.decided_at,
            version=number,
        )
    expect(_sees(ctx, viewer, candidate), "sensitive decisions numbered above it change nothing")
    withdrawn = ConsentDecision.objects.create(
        account_id=candidate.account_id,
        purpose="onboarding",
        policy_version=latest.policy_version,
        state="withdrawn",
        decided_at=latest.decided_at,
        version=int(latest.version) + 1,
    )
    expect(not _sees(ctx, viewer, candidate), "a latest withdrawal excludes, visible or not")
    withdrawn.delete()
    expect(_sees(ctx, viewer, candidate), "the acceptance passes again")
    held = list(
        ConsentDecision.objects.filter(account_id=candidate.account_id, purpose="onboarding")
    )
    ConsentDecision.objects.filter(account_id=candidate.account_id, purpose="onboarding").delete()
    expect(not _sees(ctx, viewer, candidate), "a sensitive decision alone, or none, excludes")
    ConsentDecision.objects.bulk_create(held)
    expect(_sees(ctx, viewer, candidate), "restored, it passes")
    reply = ctx.profiles.withdraw_onboarding(candidate)
    ctx.profiles.data(reply, "onboarding", "the withdrawal")
    expect(not _sees(ctx, viewer, candidate), "a withdrawal through the route excludes")
    ctx.profiles.accept_onboarding(candidate)
    expect(_sees(ctx, viewer, candidate), "an acceptance restores")
    return "old version, withdrawal, missing and purpose each exclude; restored each passes"


@case("predicates.profile_states", "1", "D3")
def profile_states(ctx: DiscoveryContext) -> str:
    from glow_profiles import staff

    viewer, candidate = ctx.visible(), ctx.visible()
    _visibility(ctx, candidate, "pause")
    expect(not _sees(ctx, viewer, candidate), "a paused candidate is excluded")
    _visibility(ctx, candidate, "resume")
    expect(_sees(ctx, viewer, candidate), "resumed, it passes")
    expect(_summary(ctx, candidate, "") == "incomplete", "a cleared summary makes it incomplete")
    expect(not _sees(ctx, viewer, candidate), "an incomplete candidate is excluded")
    expect(_summary(ctx, candidate, "Back again.") == "visible", "completed again")
    expect(_sees(ctx, viewer, candidate), "visible again, it passes")
    restricted = staff.restrict_profile(
        candidate.account_id,
        staff_subject="staff:discovery-proof",
        reason="SV3-proof",
        request_id=uuid4(),
    )
    expect(restricted.outcome == "applied", "staff restrict the profile")
    expect(not _sees(ctx, viewer, candidate), "a restricted candidate is excluded")
    _profile_state(candidate.account_id, "removed")
    expect(not _sees(ctx, viewer, candidate), "a removed candidate is excluded")
    _profile_state(candidate.account_id, "visible")
    expect(_sees(ctx, viewer, candidate), "restored, it passes")
    _visibility(ctx, viewer, "pause")
    _refused_page(ctx, viewer, 403, "forbidden", "a paused viewer")
    _visibility(ctx, viewer, "resume")
    expect(_summary(ctx, viewer, "") == "incomplete", "the viewer made incomplete")
    _refused_page(ctx, viewer, 403, "forbidden", "an incomplete viewer")
    expect(_summary(ctx, viewer, "Back again.") == "visible", "the viewer completed again")
    _profile_state(viewer.account_id, "restricted")
    _refused_page(ctx, viewer, 403, "forbidden", "a restricted viewer")
    _profile_state(viewer.account_id, "removed")
    _refused_page(ctx, viewer, 403, "forbidden", "a removed viewer")
    _profile_state(viewer.account_id, "visible")
    expect(_sees(ctx, viewer, candidate), "restored, the viewer pages again")
    return "paused, incomplete, restricted and removed each exclude and refuse; restored each pass"


@case("predicates.account_states", "1", "D3", "12")
def account_states(ctx: DiscoveryContext) -> str:
    from glow_persistence.models import AppAccount
    from glow_profiles import operations

    viewer, candidate = ctx.visible(), ctx.visible()
    ctx.profile_id(candidate)
    expect(operations.chat().suspend(candidate.account_id).outcome == "applied", "suspended")
    expect(not _sees(ctx, viewer, candidate), "a suspended candidate is excluded")
    AppAccount.objects.filter(pk=candidate.account_id).update(state="active")
    expect(_sees(ctx, viewer, candidate), "active again (setup), it passes")
    expect(operations.chat().delete(candidate.account_id).outcome == "applied", "deletion asked")
    expect(not _sees(ctx, viewer, candidate), "a deletion-pending candidate is excluded")
    AppAccount.objects.filter(pk=candidate.account_id).update(state="deleted")
    expect(not _sees(ctx, viewer, candidate), "a deleted candidate is excluded")
    AppAccount.objects.filter(pk=candidate.account_id).update(state="active")
    expect(_sees(ctx, viewer, candidate), "active again (setup), it passes")
    expect(operations.chat().suspend(viewer.account_id).outcome == "applied", "viewer suspended")
    reply = ctx.page_reply(viewer)
    ctx.profiles.refused(reply, 401, "unauthenticated", "a suspended viewer has no actor")
    # SV1's actor and the account row lock refuse first; the viewer's own predicate, the statement
    # each page runs, fails the account too.
    from django.db import connection
    from glow_discovery import predicates
    from glow_discovery.eligibility import parameters

    with connection.cursor() as cursor:
        cursor.execute(predicates.VIEWER, parameters(_selection(), viewer.account_id))
        expect(
            cursor.fetchone()[0] is False, "the viewer's own predicate fails a suspended account"
        )
    return "suspended, deletion-pending and deleted each exclude; a suspended viewer has no page"


@case("predicates.blocks", "1", "D3", "D7")
def blocks(ctx: DiscoveryContext) -> str:
    viewer, candidate = ctx.visible(), ctx.visible()
    ctx.block(viewer.account_id, candidate.account_id)
    expect(_both(ctx, viewer, candidate) == (False, False), "the viewer's block excludes both ways")
    ctx.unblock(viewer.account_id, candidate.account_id)
    expect(_both(ctx, viewer, candidate) == (True, True), "unblocked, both pass")
    ctx.block(candidate.account_id, viewer.account_id)
    expect(_both(ctx, viewer, candidate) == (False, False), "the candidate's block, both ways")
    ctx.unblock(candidate.account_id, viewer.account_id)
    expect(_both(ctx, viewer, candidate) == (True, True), "unblocked, both pass")
    # D7: a block bumps only its actor's blocks_version, so the viewer's batch stays fresh, and
    # each page rechecks both directions for every entry.
    third = ctx.visible()
    first = ctx.page(viewer, limit=1)
    shown = ctx.ids(first)[0]
    blocker = third if shown == ctx.profile_id(candidate) else candidate
    blocker_id = ctx.profile_id(blocker)
    ctx.block(blocker.account_id, viewer.account_id)
    second = ctx.page(viewer, "recommendations", first["next_cursor"], 1)
    expect(
        blocker_id not in ctx.ids(second), "a block by the candidate drops them at the next page"
    )
    expect(second["state"] == "empty", "and nothing else was left")
    return "a block in either direction excludes both ways and is rechecked on every page"


@case("predicates.missing_rows", "1", "D3")
def missing_rows(ctx: DiscoveryContext) -> str:
    from glow_persistence.models import AccountAgeState, Preferences, PreferenceSetEntry

    viewer, candidate = ctx.visible(), ctx.visible()
    held = Preferences.objects.get(account_id=candidate.account_id)
    Preferences.objects.filter(pk=held.pk).delete()
    expect(not _sees(ctx, viewer, candidate), "no preferences row fails closed")
    expect(("candidate", "preference") in _rules(viewer, candidate), "as the candidate's direction")
    held.save(force_insert=True)
    expect(_sees(ctx, viewer, candidate), "restored, it passes")
    sets = list(PreferenceSetEntry.objects.filter(account_id=candidate.account_id, field="gender"))
    PreferenceSetEntry.objects.filter(account_id=candidate.account_id, field="gender").delete()
    expect(not _sees(ctx, viewer, candidate), "no set row for a field fails closed")
    PreferenceSetEntry.objects.bulk_create(sets)
    expect(_sees(ctx, viewer, candidate), "restored, it passes")
    age = AccountAgeState.objects.get(account_id=candidate.account_id)
    AccountAgeState.objects.filter(pk=age.pk).delete()
    expect(not _sees(ctx, viewer, candidate), "no age state row fails closed")
    expect(("candidate", "adult") in _rules(viewer, candidate), "as unknown, never a pass")
    age.save(force_insert=True)
    expect(_sees(ctx, viewer, candidate), "restored, it passes")
    return "a missing preferences, set or age state row each fails closed"


# -- 2. the two-way rule (acceptance check 2; D4) ---------------------------------------------


def _sensitive_pair(ctx: DiscoveryContext) -> tuple[Member, Member]:
    ctx.profiles.ensure_test_lists()
    viewer, candidate = ctx.visible(), ctx.visible()
    ctx.accept_sensitive(viewer)
    ctx.accept_sensitive(candidate)
    return viewer, candidate


@case("two_way.each_field_both_directions", "2", "D4")
def each_field_both_directions(ctx: DiscoveryContext) -> str:
    from glow_ordering_proof.profile_support import RELATIONSHIP_VALUE

    viewer, candidate = _sensitive_pair(ctx)
    a, b = ORIENTATION_VALUES[0], ORIENTATION_VALUES[1]
    ctx.set_field(viewer, "orientation", [a])
    ctx.set_field(candidate, "orientation", [b])
    ctx.set_field(viewer, "relationship_status", [RELATIONSHIP_VALUE])
    ctx.set_field(candidate, "relationship_status", [RELATIONSHIP_VALUE])
    expect(_both(ctx, viewer, candidate) == (True, True), "every set keeps all")
    # (field, the viewer's own value, the candidate's own value, a value neither holds)
    fields = (
        ("gender", "woman", "woman", "man"),
        ("looking_for", "long-term", "long-term", "casual"),
        ("orientation", a, b, ORIENTATION_VALUES[2]),
        ("relationship_status", RELATIONSHIP_VALUE, RELATIONSHIP_VALUE, "single"),
    )
    checked = 0
    for name, viewer_value, candidate_value, neither in fields:
        for narrower, wanted in ((viewer, candidate_value), (candidate, viewer_value)):
            ctx.set_sets(narrower, {name: [neither]})
            expect(not _sees(ctx, viewer, candidate), f"{name}: a miss in one direction excludes")
            ctx.set_sets(narrower, {name: [wanted]})
            expect(_sees(ctx, viewer, candidate), f"{name}: a match passes")
            ctx.set_sets(narrower, {})
            checked += 1
    return f"{checked} field directions: each excludes on a miss and passes on a match"


@case("two_way.keep_all", "2", "D4")
def keep_all(ctx: DiscoveryContext) -> str:
    from glow_domain import profile_settings as ps

    viewer, candidate = _sensitive_pair(ctx)
    expect(_sees(ctx, viewer, candidate), "keep-all sees a member with no orientation row")
    ctx.set_field(candidate, "orientation", ["not-stated"])
    expect(_sees(ctx, viewer, candidate), "keep-all sees a member who states none")
    # A value the console adds after the viewer's set was saved: keep-all still matches it.
    content = ctx.current(ps.GENDER_LIST)
    added = "fixture-gender-later"
    if added not in {value["id"] for value in content["values"]}:
        content["values"].append({"id": added, "label": "Fixture later value", "retired": False})
        ctx.publish(ps.GENDER_LIST, content)
    ctx.set_field(candidate, "gender", [added])
    expect(_sees(ctx, viewer, candidate), "keep-all matches a value added after it was set")
    ctx.set_field(candidate, "gender", ["woman"])
    return "keep-all matches not stated and a later list value"


@case("two_way.narrowed_never_not_stated", "2", "D4")
def narrowed_never_not_stated(ctx: DiscoveryContext) -> str:
    viewer, silent = _sensitive_pair(ctx)
    stated_none, stated = ctx.visible(), ctx.visible()
    ctx.accept_sensitive(stated_none)
    ctx.accept_sensitive(stated)
    a = ORIENTATION_VALUES[0]
    ctx.set_field(viewer, "orientation", [a])
    ctx.set_field(stated_none, "orientation", ["not-stated"])
    ctx.set_field(stated, "orientation", [a])
    ctx.set_sets(viewer, {"orientation": [a]})
    seen = ctx.sees(viewer)
    expect(ctx.profile_id(silent) not in seen, "a missing orientation row is not stated, excluded")
    expect(ctx.profile_id(stated_none) not in seen, "not stated is in no narrowed set")
    expect(ctx.profile_id(stated) in seen, "a stated match passes")
    expect(_ready(viewer, stated) and not _ready(viewer, silent), "the adapter agrees")
    ctx.set_sets(viewer, {})
    return "a narrowed set never matches not stated, a missing row included"


@case("two_way.retired_value", "2", "D4")
def retired_value(ctx: DiscoveryContext) -> str:
    from glow_domain import profile_settings as ps

    viewer, candidate = _sensitive_pair(ctx)
    content = ctx.current(ps.RELATIONSHIP_LIST)
    value = "fixture-relationship-retiring"
    content["values"].append({"id": value, "label": "Fixture retiring value", "retired": False})
    ctx.publish(ps.RELATIONSHIP_LIST, content)
    ctx.set_field(candidate, "relationship_status", [value])
    ctx.set_field(viewer, "relationship_status", [value])
    ctx.set_sets(viewer, {"relationship_status": [value]})
    expect(_sees(ctx, viewer, candidate), "a narrowed set matches the value")
    content = ctx.current(ps.RELATIONSHIP_LIST)
    for entry in content["values"]:
        if entry["id"] == value:
            entry["retired"] = True
    ctx.publish(ps.RELATIONSHIP_LIST, content)
    expect(_sees(ctx, viewer, candidate), "retired, it stays matchable for its holder")
    return "a retired value stays matchable in a narrowed set"


@case("two_way.not_narrowable", "2", "D4")
def not_narrowable(ctx: DiscoveryContext) -> str:
    from glow_domain import profile_settings as ps

    viewer, candidate = ctx.visible(), ctx.visible()
    ctx.set_sets(viewer, {"gender": ["man"]})
    expect(not _sees(ctx, viewer, candidate), "a narrowed gender set excludes")
    content = ctx.current(ps.NARROWING)
    content["narrowable"]["gender"] = False
    ctx.publish(ps.NARROWING, content)
    try:
        expect(_sees(ctx, viewer, candidate), "a field not narrowable reads as keeping all")
    finally:
        content["narrowable"]["gender"] = True
        ctx.publish(ps.NARROWING, content)
    expect(not _sees(ctx, viewer, candidate), "narrowable again, the set applies")
    ctx.set_sets(viewer, {})
    return "a field made not narrowable reads as keep-all; narrowable again, the set applies"


# -- 3. age (acceptance check 3; D4) ----------------------------------------------------------


@case("age.range_both_ways", "3", "D4")
def range_both_ways(ctx: DiscoveryContext) -> str:
    from glow_domain import profile_settings as ps

    viewer = ctx.visible(birth_date=years_ago(30, days=-40))
    older = ctx.visible(birth_date=years_ago(45, days=-40))
    same = ctx.visible(birth_date=years_ago(30, days=-40))
    ctx.set_filters(viewer, minimum=25, maximum=35)
    seen = ctx.sees(viewer)
    expect(ctx.profile_id(older) not in seen, "outside the viewer's range, excluded")
    expect(ctx.profile_id(same) in seen, "within it, included")
    ctx.set_filters(same, minimum=18, maximum=25)
    expect(ctx.profile_id(same) not in ctx.sees(viewer), "both ways: the viewer outside theirs")
    content = ctx.current(ps.AGE_RANGE)
    content["direction"] = "viewer_only"
    ctx.publish(ps.AGE_RANGE, content)
    try:
        expect(ctx.profile_id(same) in ctx.sees(viewer), "viewer only: their range is not applied")
    finally:
        content["direction"] = "both_ways"
        ctx.publish(ps.AGE_RANGE, content)
    expect(ctx.profile_id(same) not in ctx.sees(viewer), "both ways again")
    return "the range applies to the candidate, and to the viewer under both_ways"


LEAP_BIRTHS = ("2008-02-29", "2008-02-28", "2008-03-01", "2000-02-29", "2008-09-23", "2008-09-24")
LEAP_TODAYS = (
    "2026-02-28",
    "2026-03-01",
    "2026-09-23",
    "2026-09-24",
    "2027-02-28",
    "2027-03-01",
    "2028-02-28",
    "2028-02-29",
    "2028-03-01",
)


@case("age.leap_days_and_age_state", "3", "D4", "13")
def leap_days_and_age_state(ctx: DiscoveryContext) -> str:
    from django.db import connection
    from glow_discovery import predicates
    from glow_domain.identity import whole_years
    from glow_persistence.models import BirthInput

    statement = "SELECT " + predicates.AGE.format(birth="%(birth)s::date")
    pairs = 0
    with connection.cursor() as cursor:
        for born in LEAP_BIRTHS:
            for today in LEAP_TODAYS:
                cursor.execute(statement, {"birth": born, "today": today})
                found = cursor.fetchone()[0]
                expected = whole_years(date.fromisoformat(born), date.fromisoformat(today))
                expect(found == expected, "the SQL rule is age_years' at a leap-day case")
                pairs += 1
    # D4: the age state's date, never the birth input's.
    viewer = ctx.visible()
    candidate = ctx.visible(birth_date=years_ago(30, days=-40))
    BirthInput.objects.filter(account_id=candidate.account_id).update(
        birth_date=date.fromisoformat(years_ago(60, days=-40))
    )
    ctx.set_filters(viewer, minimum=25, maximum=35)
    page = ctx.page(viewer)
    cards = [card for card in page["items"] if card["profile_id"] == ctx.profile_id(candidate)]
    expect(len(cards) == 1, "the age state's age decides the range, not the birth input's")
    expect(cards[0]["profile"]["age"] == 30, "and the card's age is the age state's")
    for body in ctx.pages:
        expect("birth" not in json.dumps(body), "no page carries a birth field")
    return f"{pairs} leap-day pairs agree; the age state's date is used, never the birth input's"


def _set_birth(member: Member, born: date) -> None:
    """The age state's date, written in setup (test data, as ``predicates.adult_state`` seeds a
    lagging age state). SV2's adult check refuses no old date; a direct write keeps it brief."""
    from glow_persistence.models import AccountAgeState

    updated = AccountAgeState.objects.filter(account_id=member.account_id).update(birth_date=born)
    expect(updated == 1, "the member's age state is set")


def _years_back(today: date, years: int, days: int = 0) -> date:
    """The date ``years`` whole years before ``today`` (its birthday today), moved by ``days``. On
    29 February the birthday is 28 February, so the age is still exactly ``years``."""
    try:
        then = today.replace(year=today.year - years)
    except ValueError:
        then = today.replace(year=today.year - years, day=28)
    return then + timedelta(days=days)


@case("age.ceiling_150_shown_151_excluded", "1", "3", "D3", "DM-62")
def ceiling_150_shown_151_excluded(ctx: DiscoveryContext) -> str:
    """ADULT's age ceiling (the brief's D3, Y1; check 3, Y2; Codex's CX3) at the server's date: 150
    whole years is shown and 151 is excluded, as a candidate in the selection and in a page's
    recheck, as a viewer (a 403 with no batch), and in the trusted adapter's pair read. Every page
    is checked against the production schema, whose ``CandidateProfile.age`` maximum is 150."""
    from glow_domain import profile_settings as ps

    today = db_today()
    viewer = ctx.visible()
    at_150, turning, at_151 = ctx.visible(), ctx.visible(), ctx.visible()
    _set_birth(at_150, _years_back(today, ps.AGE_CEILING))
    _set_birth(turning, _years_back(today, ps.AGE_CEILING + 1, days=1))
    _set_birth(at_151, _years_back(today, ps.AGE_CEILING + 1))
    # The selection, and the pair read beside it (``_sees`` compares the two).
    expect(_sees(ctx, viewer, at_150), "150 whole years is shown")
    expect(_sees(ctx, viewer, turning), "151 tomorrow is 150 today, and shown")
    expect(not _sees(ctx, viewer, at_151), "151 whole years is excluded")
    expect(("candidate", "adult") in _rules(viewer, at_151), "the pair read excludes 151 by ADULT")
    expect(("candidate", "adult") not in _rules(viewer, at_150), "and passes 150")
    ages = [
        card["profile"]["age"]
        for card in ctx.pages[-1]["items"]
        if card["profile_id"] in {ctx.profile_id(at_150), ctx.profile_id(turning)}
    ]
    expect(ages == [ps.AGE_CEILING] * 2, "the cards carry 150, the contract's maximum")
    # Every page's recheck: a candidate who passes 150 during a batch is dropped at the next page.
    first = ctx.page(viewer, limit=1)
    shown = ctx.ids(first)
    expect(len(shown) == 1 and first["next_cursor"] is not None, "a first page and a cursor")
    later = at_150 if ctx.profile_id(at_150) not in shown else turning
    _set_birth(later, _years_back(today, ps.AGE_CEILING + 1))
    rest = [first]
    while rest[-1]["next_cursor"] is not None:
        rest.append(ctx.page(viewer, "recommendations", rest[-1]["next_cursor"], 1))
    expect(ctx.profile_id(later) not in ctx.all_ids(rest[1:]), "passing 150, dropped at recheck")
    _set_birth(later, _years_back(today, ps.AGE_CEILING))
    # The viewer: at 151, a 403 and no batch; the pair read refuses them too.
    before = _batches(viewer.account_id)
    _set_birth(viewer, _years_back(today, ps.AGE_CEILING + 1))
    _refused_page(ctx, viewer, 403, "forbidden", "a viewer at 151 whole years")
    expect(_batches(viewer.account_id) == before, "no batch is computed for them")
    expect(("viewer", "adult") in _rules(viewer, at_150), "the pair read refuses a viewer at 151")
    _set_birth(viewer, _years_back(today, ps.AGE_CEILING))
    expect(_sees(ctx, viewer, at_150), "a viewer at 150 pages, and sees 150")
    return (
        "150 shown and 151 excluded at the server's date, in the selection, the recheck and the"
        " pair read; a viewer at 151 refused with no batch; every card at most 150"
    )


# The leap-day cases ``age.leap_days_and_age_state`` uses, 132 years earlier (1876 and 1868 are
# leap years, as 2008 and 2000 are), so that the same days put the ages at 149 to 152.
CEILING_BIRTHS = tuple(f"{int(born[:4]) - 132}{born[4:]}" for born in LEAP_BIRTHS)


@case("age.ceiling_at_leap_days", "3", "D3", "D4", "DM-62")
def ceiling_at_leap_days(ctx: DiscoveryContext) -> str:
    """ADULT's ceiling at the leap-day cases (Y2): for each date, ``MEMBER``'s ``adult`` (which the
    selection, the recheck, the viewer's read and the pair read share) is ``whole_years`` at most
    150, as the viewer (``VIEWER``) and as the candidate (``PAIR``)."""
    from django.db import connection
    from glow_discovery import predicates
    from glow_discovery.eligibility import parameters
    from glow_domain import profile_settings as ps
    from glow_domain.identity import whole_years

    viewer, member = ctx.visible(), ctx.visible()
    selection = _selection()
    own = f"WITH v AS ({predicates.MEMBER} WHERE a.id = %(viewer)s) SELECT v.adult, v.age FROM v"
    pairs = 0
    reached: set[int] = set()
    with connection.cursor() as cursor:
        for born in CEILING_BIRTHS:
            _set_birth(member, date.fromisoformat(born))
            for today in LEAP_TODAYS:
                years = whole_years(date.fromisoformat(born), date.fromisoformat(today))
                wanted = years <= ps.AGE_CEILING
                values = parameters(selection, member.account_id)
                values["today"] = today
                cursor.execute(own, values)
                adult, age = cursor.fetchone()
                expect(age == years, "the SQL rule is whole_years' at a leap-day case")
                expect(adult is wanted, "ADULT's ceiling is whole_years at most 150")
                cursor.execute(predicates.VIEWER, values)
                expect(cursor.fetchone()[0] is wanted, "as the viewer: their own read")
                pair = parameters(selection, viewer.account_id)
                pair.update(candidate=member.account_id, today=today)
                cursor.execute(predicates.PAIR, pair)
                expect(cursor.fetchone()[16] is wanted, "as the candidate: the pair read")
                if years in (ps.AGE_CEILING, ps.AGE_CEILING + 1):
                    reached.add(years)
                pairs += 1
    expect(reached == {150, 151}, "both sides of the ceiling fall on the leap-day cases")
    _set_birth(member, _years_back(db_today(), 30))
    return f"{pairs} leap-day pairs: ADULT is whole_years at most 150, as viewer and as candidate"


# -- 4. distance (acceptance check 4; D5) -----------------------------------------------------


@case("distance.zero_boundary_viewer_only", "4", "D5", "13")
def distance_cases(ctx: DiscoveryContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import Area, OutboxEvent
    from glow_profiles import areas

    points = {
        row.area_id: areas.AreaPoint(
            row.area_id, row.name, float(row.latitude), float(row.longitude)
        )
        for row in Area.objects.filter(area_id__in=(NEW_YORK, PHILADELPHIA))
    }
    miles = areas.miles_between(points[NEW_YORK], points[PHILADELPHIA])
    ctx.profiles.values.add(repr(miles))
    ctx.private.add(repr(miles))
    expect(abs(miles - round(miles)) > 0.001, "the boundary is not a whole mile")
    below, above = math.floor(miles), math.ceil(miles)
    content = ctx.current(ps.LOCATION)
    wanted = {
        "fixture-within-1": 1,
        f"fixture-within-{below}": below,
        f"fixture-within-{above}": above,
    }
    have = {choice["id"] for choice in content["distance_choices"]}
    for choice_id, limit in wanted.items():
        if choice_id not in have:
            content["distance_choices"].append(
                {"id": choice_id, "label": f"Fixture {limit} miles", "miles": limit}
            )
    ctx.publish(ps.LOCATION, content)
    viewer = ctx.visible()
    same = ctx.visible()
    near = ctx.visible(area=PHILADELPHIA)
    events = OutboxEvent.objects.exclude(event_type="preferences_changed").count()
    ctx.set_filters(viewer, distance="fixture-within-1")
    seen = ctx.sees(viewer)
    expect(ctx.profile_id(same) in seen, "one area is distance zero")
    expect(ctx.profile_id(near) not in seen, "another area beyond one mile is excluded")
    ctx.set_filters(viewer, distance=f"fixture-within-{below}")
    expect(ctx.profile_id(near) not in ctx.sees(viewer), "just short of the boundary, excluded")
    ctx.set_filters(viewer, distance=f"fixture-within-{above}")
    expect(ctx.profile_id(near) in ctx.sees(viewer), "within the boundary, included")
    ctx.set_filters(near, distance="fixture-within-1")
    expect(
        ctx.profile_id(near) in ctx.sees(viewer), "distance applies in the viewer's direction only"
    )
    ctx.set_filters(viewer, distance="anywhere")
    seen = ctx.sees(viewer)
    expect({ctx.profile_id(same), ctx.profile_id(near)} <= seen, "anywhere filters nothing")
    # The filters' own writes emit preferences_changed; the pages emit nothing.
    after = OutboxEvent.objects.exclude(event_type="preferences_changed").count()
    expect(after == events, "the pages wrote no outbox event")
    for body in ctx.pages:
        text = json.dumps(body)
        expect("miles" not in text and "latitude" not in text, "no page names a distance or point")
        expect(not any(isinstance(v, float) for v in _numbers(body)), "no page holds a fraction")
    return "one area is zero; the boundary includes at its ceiling and excludes below; viewer only"


@case("distance.choice_no_longer_offered", "4", "D5", "C2")
def choice_no_longer_offered(ctx: DiscoveryContext) -> str:
    """D5's choice the setting does not offer (the exact-head review's F2): a viewer whose distance
    choice the location setting stops offering gets an empty page, in the same area and beyond,
    and the trusted adapter agrees; the choice is never read as no limit."""
    from glow_domain import profile_settings as ps

    original = ctx.current(ps.LOCATION)
    choice = "fixture-within-withdrawn"
    offered = ctx.current(ps.LOCATION)
    offered["distance_choices"] = [c for c in offered["distance_choices"] if c["id"] != choice] + [
        {"id": choice, "label": "Fixture 3000 miles", "miles": 3000}
    ]
    ctx.publish(ps.LOCATION, offered)
    try:
        viewer = ctx.visible()
        same = ctx.visible()
        near = ctx.visible(area=PHILADELPHIA)
        ctx.set_filters(viewer, distance=choice)
        expect(_sees(ctx, viewer, same), "within an offered choice: the same area is shown")
        expect(_sees(ctx, viewer, near), "within an offered choice: another area is shown")
        withdrawn = ctx.current(ps.LOCATION)
        withdrawn["distance_choices"] = [
            c for c in withdrawn["distance_choices"] if c["id"] != choice
        ]
        ctx.publish(ps.LOCATION, withdrawn)
        held = {c["id"] for c in ctx.current(ps.LOCATION)["distance_choices"]}
        expect(choice not in held, "the choice is no longer offered")
        expect(not _sees(ctx, viewer, same), "a choice no longer offered fails: the same area")
        expect(not _sees(ctx, viewer, near), "a choice no longer offered fails: another area")
        page = ctx.page(viewer)
        expect(page["state"] == "empty" and page["items"] == [], "the viewer's page is empty")
        expect(ctx.profile_id(viewer) in ctx.sees(same), "the other direction is unaffected")
    finally:
        ctx.publish(ps.LOCATION, original)
    return "a distance choice the location setting no longer offers fails D5 for every candidate"


def _numbers(value: Any) -> list[Any]:
    if isinstance(value, dict):
        return [n for item in value.values() for n in _numbers(item)]
    if isinstance(value, list):
        return [n for item in value for n in _numbers(item)]
    return [value] if isinstance(value, int | float) and not isinstance(value, bool) else []


# -- 5. pages (acceptance check 5; D6, D7) ----------------------------------------------------


@case("pages.recommended_then_broader", "5", "D6", "D7")
def recommended_then_broader(ctx: DiscoveryContext) -> str:
    viewer = ctx.visible()
    members = [ctx.visible() for _ in range(4)]
    ids = {ctx.profile_id(m) for m in members}
    with ctx.counting_port() as calls:
        recommended = ctx.sees(viewer)
        expect(recommended == ids, "every eligible ready pair is recommended")
        expect(calls[0] == 4, "the port is asked once for each selected pair")
        expect(ctx.sees(viewer, "discovery") == set(), "broader leaves the recommended out")
        expect(calls[0] == 4, "broader asks the port nothing")
    with ctx.counting_port("unsupported-contract") as calls:
        expect(ctx.sees(viewer) == set(), "unsupported pairs are left out of recommendations")
        expect(calls[0] == 4, "after asking the port")
        expect(ctx.sees(viewer, "discovery") == ids, "broader still serves them")
    with ctx.counting_port():
        expect(ctx.sees(viewer) == ids, "recommended again")
        late = ctx.visible()
        expect(ctx.sees(viewer, "discovery") == {ctx.profile_id(late)}, "broader: the rest only")
    return "recommended first; broader serves the eligible not in the current recommendations"


@case("pages.random_stable_order", "5", "D6", "DM-61")
def random_stable_order(ctx: DiscoveryContext) -> str:
    """The random tie-break (D6; DM-61 K2; check 5, K4): the order is stable within a batch, across
    its pages, as the entries' positions keep it; two batches over the same 12 candidates in one
    band are ordered differently; neither is an order computable from the batch's and the
    profiles' IDs; and no executed statement or parameter, nor any statement's text as the
    client-side binding cursor sends it, carries a value derived from ``SECRET_KEY`` (Codex's CX2).
    """
    from django.conf import settings
    from glow_discovery import predicates
    from glow_persistence.models import RecommendationEntry

    from glow_ordering_proof.discovery_support import derived_from_secret_key, record_statements

    viewer = ctx.visible()
    members = [ctx.visible() for _ in range(12)]
    everyone = {ctx.profile_id(m) for m in members}

    def positions(batch: str) -> list[str]:
        return [
            str(p)
            for p in RecommendationEntry.objects.filter(batch_id=UUID(batch))
            .order_by("position")
            .values_list("candidate__profile__id", flat=True)
        ]

    # Each batch's positions are read before the next batch replaces it (one per collection).
    with record_statements() as sent:
        batches = [ctx.pages_of(viewer, limit=3)]
        kept = [positions(batches[0][0]["batch_id"])]
        again = ctx.page(viewer, "recommendations", batches[0][0]["next_cursor"], 3)
        batches.append(ctx.pages_of(viewer, limit=3))
        kept.append(positions(batches[1][0]["batch_id"]))
    orders: list[list[str]] = []
    issued: list[str] = []
    for pages, stored_order in zip(batches, kept, strict=True):
        served = ctx.all_ids(pages)
        expect(len(served) == 12 and set(served) == everyone, "every candidate once, in one band")
        batch = pages[0]["batch_id"]
        expect(served == stored_order, "stable within a batch: the pages follow the positions")
        expect(served != sorted(served), "not the profile IDs' order")
        unkeyed = sorted(served, key=lambda p: hashlib.sha256(f"{batch}:{p}".encode()).digest())
        expect(served != unkeyed, "not an order computable from the batch's and profiles' IDs")
        orders.append(served)
        issued += [str(page["next_cursor"]) for page in pages if page["next_cursor"]]
    expect(ctx.ids(again) == ctx.ids(batches[0][1]), "the same cursor gives the same page")
    expect(batches[0][0]["batch_id"] != batches[1][0]["batch_id"], "a new batch")
    expect(orders[0] != orders[1], "two batches over the same candidates are ordered differently")
    stored = [f.name for f in RecommendationEntry._meta.get_fields() if "tie" in f.name]
    expect(stored == [], "the tie-break is stored nowhere")
    ledger = [str(settings.SECRET_KEY), *derived_from_secret_key()]
    ledger += [cursor.split(".")[2] for cursor in issued]
    expect(sent.client_side and sent.as_sent > 0, "the statements were read as they were sent")
    expect(predicates.TIE_BREAK + " AS tie_break" in "\n".join(sent.texts), "the draw was sent")
    expect(
        sent.holds(ledger) == 0, "no statement or parameter carries a value derived from the key"
    )
    return (
        f"12 candidates in one band: stable within each of two batches, ordered differently; no"
        f" value derived from SECRET_KEY in {sent.statements} statements ({sent.as_sent} read as"
        f" sent, client-side binding)"
    )


@case("pages.stale_cursors", "5", "12", "D7", "D8")
def stale_cursors(ctx: DiscoveryContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import RecommendationBatch

    viewer, other = ctx.visible(), ctx.visible()
    for _ in range(2):
        ctx.visible()
    replies = []

    def fresh() -> str:
        cursor = ctx.page(viewer, limit=1)["next_cursor"]
        expect(cursor is not None, "a cursor")
        assert cursor is not None
        expect(ctx.page(viewer, "recommendations", cursor, 1)["state"] == "ready", "it works")
        return str(cursor)

    cursor = fresh()
    batch_hex, offset, mac = cursor.split(".")
    forged = [
        f"{batch_hex}.{offset}.{mac[:-1]}{'0' if mac[-1] != '0' else '1'}",
        f"{batch_hex}.02.{mac}",
        f"{uuid4().hex}.{offset}.{mac}",
    ]
    for value in forged:
        replies.append(ctx.stale(viewer, "recommendations", value, "a forged cursor"))
    replies.append(ctx.stale(other, "recommendations", cursor, "another viewer's cursor"))
    replies.append(ctx.stale(viewer, "discovery", cursor, "the other collection's cursor"))
    RecommendationBatch.objects.filter(pk=UUID(hex=batch_hex)).update(
        expires_at=RecommendationBatch.objects.get(pk=UUID(hex=batch_hex)).created_at
    )
    replies.append(ctx.stale(viewer, "recommendations", cursor, "an expired batch"))
    cursor = fresh()
    later = fresh()
    replies.append(ctx.stale(viewer, "recommendations", cursor, "a deleted batch"))
    expect(len(_batches(viewer.account_id)) == 1, "one batch per viewer and collection")
    ctx.set_filters(viewer, minimum=19)
    replies.append(ctx.stale(viewer, "recommendations", later, "the viewer's own change"))
    cursor = fresh()
    ctx.publish(ps.RESURFACING, ctx.current(ps.RESURFACING))
    replies.append(ctx.stale(viewer, "recommendations", cursor, "a discovery setting published"))
    cursor = fresh()
    ctx.publish(ps.LOCATION, ctx.current(ps.LOCATION))
    replies.append(ctx.stale(viewer, "recommendations", cursor, "a profile setting published"))
    # C2 (the exact-head review's F2): each of the viewer's other two versions moved alone, and a
    # batch that is not ready.

    def versions() -> tuple[int, int, int]:
        account = _account(viewer.account_id)
        return (
            int(account.eligibility_version),
            int(account.preferences_version),
            int(account.blocks_version),
        )

    cursor = fresh()
    before = versions()
    edited = _summary(ctx, viewer, "A synthetic summary, edited after the batch.")
    expect(edited == "visible", "the viewer stays visible after the edit")
    after = versions()
    expect(
        after[0] > before[0] and after[1:] == before[1:],
        "the profile edit moves the viewer's eligibility_version alone",
    )
    replies.append(ctx.stale(viewer, "recommendations", cursor, "the eligibility_version moved"))
    cursor = fresh()
    before = versions()
    ctx.block(viewer.account_id, other.account_id)
    after = versions()
    expect(
        after[2] > before[2] and after[:2] == before[:2],
        "the viewer's block moves the viewer's blocks_version alone",
    )
    replies.append(ctx.stale(viewer, "recommendations", cursor, "the blocks_version moved"))
    cursor = fresh()
    # Stage B's consumption marks a batch stale; Stage A has no writer of it (test data).
    RecommendationBatch.objects.filter(pk=UUID(hex=cursor.split(".")[0])).update(state="stale")
    replies.append(ctx.stale(viewer, "recommendations", cursor, "a batch that is not ready"))
    ctx.unblock(viewer.account_id, other.account_id)
    shapes = {json.dumps(_stale_shape(reply), sort_keys=True) for reply in replies}
    expect(len(shapes) == 1, "every stale cursor gets the same generic response")
    return (
        f"{len(replies)} stale cursors refused alike: forged, another's, expired, deleted, outdated"
        " (the viewer's three versions, a setting), and a batch not ready"
    )


@case("pages.dropped_between_pages", "5", "D7")
def dropped_between_pages(ctx: DiscoveryContext) -> str:
    viewer = ctx.visible()
    members = {ctx.profile_id(m): m for m in (ctx.visible() for _ in range(6))}
    first = ctx.page(viewer, limit=2)
    from glow_persistence.models import RecommendationEntry

    order = [
        str(p)
        for p in RecommendationEntry.objects.filter(batch_id=UUID(first["batch_id"]))
        .order_by("position")
        .values_list("candidate__profile__id", flat=True)
    ]
    expect(order[:2] == ctx.ids(first), "the first page is the batch's first entries")
    leaving = members[order[2]]
    _visibility(ctx, leaving, "pause")
    rest = [first]
    while rest[-1]["next_cursor"] is not None:
        rest.append(ctx.page(viewer, "recommendations", rest[-1]["next_cursor"], 2))
    seen = ctx.all_ids(rest)
    expect(order[2] not in seen, "a candidate made ineligible between pages is dropped")
    expect(len(seen) == len(set(seen)) == 5, "no duplicate, nothing else lost")
    return "a paused candidate drops at the next page; five distinct cards across pages"


@case("pages.recheck_is_one_snapshot", "5", "D2", "DM-60 4")
def recheck_is_one_snapshot(ctx: DiscoveryContext) -> str:
    from glow_discovery import keys, pages
    from glow_profiles import operations

    viewer, candidate = ctx.visible(), ctx.visible()
    ctx.set_sets(viewer, {"gender": ["woman"]})
    first = ctx.page(viewer, limit=1)
    expect(ctx.profile_id(candidate) in ctx.ids(first), "the candidate is in the batch")
    batch = UUID(first["batch_id"])
    ctx.set_field(candidate, "gender", ["man"])
    fields = ctx.profiles.get(candidate, "/api/v1/profile/fields", "own_profile_fields")
    profile = ctx.profiles.get(candidate, "/api/v1/profile", "own_profile")
    catalog = ctx.profiles.catalog(candidate)["policy_version"]

    def race() -> None:
        # Between the page's locks and its recheck: the candidate states a match again, then pauses.
        def writes() -> None:
            done = operations.set_field(
                candidate.account_id,
                {
                    "operation": "profile_field",
                    "meta": {
                        "idempotency_key": f"race-{uuid4().hex}",
                        "expected_version": fields["gender"]["version"],
                    },
                    "policy_version": catalog,
                    "field": "gender",
                    "value_ids": ["woman"],
                    "own_words": None,
                    "shown": False,
                },
            )
            expect(done.outcome == "applied", "the field write commits")
            paused = operations.set_visibility(
                candidate.account_id,
                {
                    "operation": "visibility",
                    "meta": {
                        "idempotency_key": f"race-{uuid4().hex}",
                        "expected_version": profile["version"],
                    },
                    "action": "pause",
                },
            )
            expect(paused.outcome == "applied", "the pause commits")

        _in_thread(writes)

    cursor = keys.cursor(viewer.account_id, "recommendations", batch, 0)
    result = pages.continue_page(
        viewer.account_id, "recommendations", cursor, 50, probe=_Probe(race)
    )
    expect(result.ok and result.data is not None, "the page reads")
    assert result.data is not None
    shown = [card["profile_id"] for card in result.data["items"]]
    expect(
        ctx.profile_id(candidate) not in shown, "never visible-and-matching at one moment: dropped"
    )
    return "a page's recheck reads one snapshot: no mix of two moments shows a paused profile"


# C4 (F6; DM-68): a write is anything but a read. A statement is a read only if, with its leading
# whitespace removed and its case ignored, it begins with the word SELECT or WITH and holds none
# of the words INSERT, UPDATE, DELETE, MERGE, INTO, TRUNCATE or COPY; any other statement is a
# write. So a writer's row lock (FOR UPDATE, FOR NO KEY UPDATE) is a write, and FOR SHARE is not.
READ_START = re.compile(r"(SELECT|WITH)\b", re.IGNORECASE)
WRITE_WORDS = re.compile(r"\b(INSERT|UPDATE|DELETE|MERGE|INTO|TRUNCATE|COPY)\b", re.IGNORECASE)


def is_write(sql: str) -> bool:
    """Whether a statement counts as a write (C4; F6): anything that is not a read."""
    text = str(sql).lstrip()
    return READ_START.match(text) is None or WRITE_WORDS.search(text) is not None


class _Statements:
    """A transaction probe that marks a page's transaction's phases: from its start
    (``on_begin``), from its candidate read's probe point (``before_selection`` or
    ``before_recheck``), and from its commit (``before_commit``); with the connection's execute
    wrapper (``record``) it keeps each statement's text and parameters in its phase. It only
    signals (DM-13 2.1); nothing recorded is logged or kept beyond the case."""

    after_first_lock = None
    after_locks = None

    def __init__(self) -> None:
        self.phase = "outside"
        self.points: list[str] = []
        self.committed = False
        self.seen: dict[str, list[tuple[str, Any]]] = {
            "outside": [],
            "transaction": [],
            "candidates": [],
            "committed": [],
        }

    def on_begin(self, pid: int) -> None:
        self.phase = "transaction"

    def before_selection(self) -> None:
        self.points.append("before_selection")
        self.phase = "candidates"

    def before_recheck(self) -> None:
        self.points.append("before_recheck")
        self.phase = "candidates"

    def before_commit(self) -> None:
        self.committed = True
        self.phase = "committed"

    def record(
        self, execute: Callable[..., Any], sql: str, params: Any, many: bool, ctx: Any
    ) -> Any:
        self.seen[self.phase].append((str(sql), params))
        return execute(sql, params, many, ctx)

    def in_transaction(self) -> list[tuple[str, Any]]:
        return self.seen["transaction"] + self.seen["candidates"]


def _member_tables() -> frozenset[str]:
    """The tables that hold members' rows: every table the selection and the recheck read, but
    the batch's own two."""
    from glow_discovery import predicates

    named = set(re.findall(r"glow_persistence_[a-z_]+", predicates.SELECTION + predicates.RECHECK))
    return frozenset(named - {"glow_persistence_recommendationentry"})


def _reads_members(sql: str, tables: frozenset[str]) -> bool:
    return any(table in sql for table in tables)


def _parameters(params: Any) -> list[str]:
    if params is None:
        return []
    values = params.values() if isinstance(params, dict) else params
    return [str(value) for value in values]


# C3 (S1; DM-67): the one shape of a read of the viewer's own account row before the probe point:
# one SELECT with no subquery, whose only table is the account table, whose only condition is its
# primary key equal to one parameter; it may order by the key, take LIMIT 1, and end in FOR NO KEY
# UPDATE or FOR SHARE. A column may carry an alias (``values_list``'s). Its only parameter must be
# the viewer's ID (``listed``).
_ACCOUNT = r'"?glow_persistence_appaccount"?'
_NAME = r'"?[a-z_][a-z0-9_]*"?'
_COLUMN = rf"(?:{_ACCOUNT}\.)?{_NAME}(?: AS {_NAME})?"
_KEY = rf'(?:{_ACCOUNT}\.)?"?id"?'
OWN_ACCOUNT_READ = re.compile(
    rf"SELECT {_COLUMN}(?:, {_COLUMN})* FROM {_ACCOUNT} WHERE {_KEY} = %s"
    rf"(?: ORDER BY {_KEY}(?: ASC)?)?(?: LIMIT 1)?(?: FOR (?:NO KEY UPDATE|SHARE))?"
)


def listed(sql: str, params: Any, viewer_id: str, viewer_statement: str) -> bool:
    """Whether a statement that reads a member table before the probe point is on C3's list (S1;
    DM-67): ``predicates.VIEWER`` exactly (``viewer_statement``), with the viewer's ID as its
    ``viewer`` parameter; or a read of the viewer's own account row in ``OWN_ACCOUNT_READ``'s
    shape, whose only parameter is the viewer's ID."""
    if sql == viewer_statement:
        return isinstance(params, dict) and str(params.get("viewer")) == viewer_id
    if OWN_ACCOUNT_READ.fullmatch(" ".join(sql.split())) is None:
        return False
    return isinstance(params, list | tuple) and _parameters(params) == [viewer_id]


@case("pages.one_snapshot_statements", "5", "D2", "DM-60 4", "C2")
def one_snapshot_statements(ctx: DiscoveryContext) -> str:
    """One snapshot, counted (D2; DM-60 Q1; the exact-head review's F1): in each page's
    transaction, the statements that read candidates' rows are exactly one selection
    (``predicates.SELECTION``) in a page with no cursor, and exactly one recheck
    (``predicates.RECHECK``) in a page with a cursor; from the probe point before it to the commit,
    no other statement reads a member's row; before it, before the transaction begins and in it,
    a statement that reads a member table passes only if it is on C3's list (``listed``: S1;
    DM-67); and a page with a cursor writes nothing, in any phase the probe records, the photo
    reads after its commit included (C3's S2): every statement it sends is a read, one that begins
    with ``SELECT`` or ``WITH`` and holds none of the words ``INSERT``, ``UPDATE``, ``DELETE``,
    ``MERGE``, ``INTO``, ``TRUNCATE`` or ``COPY``, so no writer's row lock either (``is_write``;
    C4's F6)."""
    from django.db import connection
    from glow_discovery import pages, predicates

    viewer = ctx.visible()
    others = [ctx.visible() for _ in range(3)]
    ids = {ctx.profile_id(m) for m in others}
    tables = _member_tables()
    expect({"glow_persistence_profile", "glow_persistence_block"} <= tables, "the member tables")
    viewer_id = str(viewer.account_id)
    counted: list[str] = []
    listed_reads: list[str] = []

    def recorded(work: Callable[[_Statements], Any]) -> tuple[Any, _Statements]:
        probe = _Statements()
        with connection.execute_wrapper(probe.record):
            result = work(probe)
        expect(result.ok and result.data is not None, "the page reads")
        return result, probe

    def check(probe: _Statements, statement: str, other: str, what: str) -> None:
        inside = probe.in_transaction()
        expect(bool(inside) and probe.committed, f"{what}: its transaction recorded to the commit")
        expect(
            sum(sql == statement for sql, _ in inside) == 1
            and not any(sql == other for sql, _ in inside),
            f"{what}: exactly one candidate statement in the transaction",
        )
        after = [sql for sql, _ in probe.seen["candidates"] if _reads_members(sql, tables)]
        expect(
            after == [statement],
            f"{what}: from the probe point to the commit, one statement reads members"
            f" ({len(after)} did)",
        )
        before = [
            (sql, params)
            for phase in ("outside", "transaction")
            for sql, params in probe.seen[phase]
            if _reads_members(sql, tables)
        ]
        for sql, params in before:
            expect(
                listed(sql, params, viewer_id, predicates.VIEWER),
                f"{what}: before the probe point, only the statements on the list read members",
            )
        counted.append(f"{what} {len(inside)}")
        listed_reads.append(str(len(before)))

    created, probe = recorded(
        lambda probe: pages.create(viewer.account_id, "recommendations", 1, probe=probe)
    )
    assert created.data is not None
    expect(probe.points == ["before_selection"], "the selection's probe point")
    check(probe, predicates.SELECTION, predicates.RECHECK, "a page with no cursor")
    writes = [sql for sql, _ in probe.seen["candidates"] if is_write(sql)]
    expect(bool(writes), "a page with no cursor writes its batch (the write check sees writes)")
    cursor = created.data["next_cursor"]
    expect(cursor is not None, "a cursor: the viewer has more than one candidate")
    shown = [str(card["profile_id"]) for card in created.data["items"]]
    following, probe = recorded(
        lambda probe: pages.continue_page(
            viewer.account_id, "recommendations", str(cursor), 50, probe=probe
        )
    )
    assert following.data is not None
    expect(probe.points == ["before_recheck"], "the recheck's probe point")
    check(probe, predicates.RECHECK, predicates.SELECTION, "a page with a cursor")
    # C3 (S2): every phase, the photo reads after the commit included.
    expect(bool(probe.seen["committed"]), "a page with a cursor: its photo reads recorded")
    written = [sql for phase in probe.seen.values() for sql, _ in phase if is_write(sql)]
    expect(not written, f"a page with a cursor writes nothing ({len(written)} writes)")
    shown += [str(card["profile_id"]) for card in following.data["items"]]
    expect(set(shown) == ids and len(shown) == len(ids), "the two pages hold every candidate once")
    _, probe = recorded(lambda probe: pages.create(viewer.account_id, "discovery", 50, probe=probe))
    check(probe, predicates.SELECTION, predicates.RECHECK, "a broader page with no cursor")
    return (
        "one selection, or one recheck, is the only statement reading members after its probe"
        f" point; a cursor page writes nothing (statements per transaction: {', '.join(counted)};"
        f" listed reads of members before the probe point: {', '.join(listed_reads)})"
    )


@case("pages.empty_and_no_provider_call", "5", "6", "D7", "D8")
def empty_and_no_provider_call(ctx: DiscoveryContext) -> str:
    viewer = ctx.visible()
    shapes = []
    with ctx.counting_port() as calls:
        alone = ctx.page(viewer)
        expect(alone["state"] == "empty" and calls[0] == 0, "an empty market: empty, no port call")
        shapes.append(_empty_shape(alone))
        candidate = ctx.visible()
        ctx.block(viewer.account_id, candidate.account_id)
        blocked = ctx.page(viewer)
        expect(blocked["state"] == "empty" and calls[0] == 0, "all excluded: empty, no port call")
        shapes.append(_empty_shape(blocked))
        ctx.unblock(viewer.account_id, candidate.account_id)
        ctx.block(candidate.account_id, viewer.account_id)
        shapes.append(_empty_shape(ctx.page(viewer)))
        ctx.unblock(candidate.account_id, viewer.account_id)
        ctx.set_sets(viewer, {"looking_for": ["casual"]})
        shapes.append(_empty_shape(ctx.page(viewer)))
        expect(calls[0] == 0, "no provider call for any empty batch")
    expect(len({json.dumps(s, sort_keys=True) for s in shapes}) == 1, "empty reads the same")
    broader = ctx.page(viewer, "discovery")
    expect(broader["state"] == "empty", "broader is empty too")
    return "empty for no market, either block and a filter alike, with no provider call"


@case("pages.port_states", "5", "D6")
def port_states(ctx: DiscoveryContext) -> str:
    viewer = ctx.visible()
    members = {ctx.profile_id(ctx.visible()) for _ in range(2)}
    for case_name, state in (
        ("pending-chart", "pending"),
        ("engine-unavailable", "unavailable"),
        (None, "unavailable"),
    ):
        with ctx.counting_port(case_name) as calls:
            page = ctx.page(viewer)
            expect(page["state"] == state, f"the port's {case_name} is the batch's {state}")
            expect(page["items"] == [] and page["next_cursor"] is None, "with no items or cursor")
            expect(calls[0] == (0 if case_name is None else 2), "the port asked as selected")
            expect(ctx.sees(viewer, "discovery") == members, "broader still serves them")
    return "pending and unavailable (and no port) make recommendations so; broader serves"


@case("pages.consumption", "5", "D7")
def consumption(ctx: DiscoveryContext) -> str:
    viewer = ctx.visible()
    liked, passed, active, restricted, unmatched, untouched = (ctx.visible() for _ in range(6))
    target_view = ctx.page(liked, limit=1)
    ctx.seed_interaction(viewer.account_id, liked.account_id, "liked")
    ctx.seed_interaction(viewer.account_id, passed.account_id, "passed")
    ctx.seed_interaction(untouched.account_id, viewer.account_id, "liked")
    for member, state in ((active, "active"), (restricted, "restricted"), (unmatched, "unmatched")):
        ctx.seed_match(viewer.account_id, member.account_id, state)
    # A like or pass changes nothing in its target's batches or their freshness.
    if target_view["next_cursor"] is not None:
        page = ctx.page(liked, "recommendations", target_view["next_cursor"], 1)
        expect(page["state"] in ("ready", "empty"), "the target's batch stays fresh")
    for member in (liked, passed, active, restricted, unmatched, untouched):
        ctx.profile_id(member)
    expected = {ctx.profile_id(untouched)}
    expect(ctx.sees(viewer) == expected, "recommendations: consumed pairs excluded")
    with ctx.counting_port("unsupported-contract"):
        expect(ctx.sees(viewer) == set(), "no current recommendations batch")
    expect(ctx.sees(viewer, "discovery") == expected, "broader: consumed pairs excluded")
    for member in (active, restricted, unmatched):
        expect(ctx.profile_id(viewer) not in ctx.sees(member), "a match excludes both ways")
    expect(ctx.profile_id(viewer) in ctx.sees(liked), "a like changes nothing for its target")
    # Each page's recheck drops a candidate consumed since the batch was built.
    late = [ctx.visible() for _ in range(2)]
    first = ctx.page(viewer, limit=1)
    remaining = [m for m in (untouched, *late) if ctx.profile_id(m) not in ctx.ids(first)]
    ctx.seed_interaction(viewer.account_id, remaining[0].account_id, "passed")
    ctx.seed_match(viewer.account_id, remaining[1].account_id, "active")
    rest = [first]
    while rest[-1]["next_cursor"] is not None:
        rest.append(ctx.page(viewer, "recommendations", rest[-1]["next_cursor"], 1))
    seen = set(ctx.all_ids(rest[1:]))
    expect(not {ctx.profile_id(m) for m in remaining[:2]} & seen, "consumed since: dropped")
    return "liked, passed and each match state excluded in both collections and on recheck"


@case("pages.one_batch_per_collection", "5", "12", "D7")
def one_batch_per_collection(ctx: DiscoveryContext) -> str:
    from glow_persistence.models import RecommendationBatch, RecommendationEntry

    viewer = ctx.visible()
    ctx.visible()
    ctx.visible()
    made = []
    for collection in (
        "recommendations",
        "discovery",
        "recommendations",
        "discovery",
        "recommendations",
    ):
        made.append(ctx.page(viewer, collection)["batch_id"])
    held = RecommendationBatch.objects.filter(account_id=viewer.account_id)
    expect(held.count() == 2, "one batch per collection")
    gone = [UUID(b) for b in made[:-2]]
    expect(not RecommendationEntry.objects.filter(batch_id__in=gone).exists(), "with entries gone")
    for limit in (0, 51):
        reply = ctx.page_reply(viewer, limit=limit)
        ctx.profiles.refused(reply, 400, "invalid_request", f"a page of {limit}")
    return "creating a batch deletes the collection's earlier one; a page is 1 to 50"


# -- page creation under concurrency, and the account locks' mode (D2, D14; DM-61) -------------

# How long a case waits for a transaction to reach a point it reaches without waiting on a lock;
# a held transaction is released at the latest after HOLD_SECONDS.
REACH_SECONDS = 10.0
HOLD_SECONDS = 60.0


class _Held:
    """A transaction probe that holds its transaction at named points (``after_first_lock``,
    ``before_commit``) until the case releases each; it records its backend's pid. It only
    signals and waits (DM-13 2.1)."""

    after_locks = None

    def __init__(self, *points: str) -> None:
        self.pid: int | None = None
        self.reached = {name: threading.Event() for name in points}
        self.release = {name: threading.Event() for name in points}
        for name in ("after_first_lock", "before_commit"):
            setattr(self, name, self._hold(name) if name in points else None)

    def on_begin(self, pid: int) -> None:
        self.pid = pid

    def _hold(self, name: str) -> Callable[[], None]:
        def hold() -> None:
            self.reached[name].set()
            self.release[name].wait(HOLD_SECONDS)

        return hold

    def free(self) -> None:
        for event in self.release.values():
            event.set()


class _Worker:
    """One transaction on its own thread and its own connection (D14: separate connections)."""

    def __init__(self, work: Callable[[], Any]) -> None:
        self.result: Any = None
        self.error: str | None = None
        self.thread = threading.Thread(target=self._run, args=(work,), daemon=True)

    def _run(self, work: Callable[[], Any]) -> None:
        from django.db import connection

        try:
            self.result = work()
        except BaseException as exc:  # noqa: BLE001 - recorded by type only
            self.error = type(exc).__name__
        finally:
            connection.close()

    def start(self) -> _Worker:
        self.thread.start()
        return self

    def ended(self) -> bool:
        return not self.thread.is_alive()

    def done(self, timeout: float) -> bool:
        self.thread.join(timeout)
        return not self.thread.is_alive()

    def outcome(self) -> str:
        """The result by its codes only (``applied``, or ``error:provider_unavailable:...``)."""
        if self.error is not None:
            return f"raised:{self.error}"
        if self.result is None:
            return "none"
        parts = (self.result.outcome, getattr(self.result, "code", ""), self.result.reason)
        return ":".join(str(part) for part in parts if part)

    def ok(self) -> bool:
        return self.error is None and self.result is not None and self.result.outcome == "applied"


def _finish(probes: list[_Held], workers: list[_Worker]) -> None:
    for probe in probes:
        probe.free()
    for worker in workers:
        expect(worker.done(HOLD_SECONDS + 30), "the concurrent transactions finished")


def _has_entry(result: Any, candidate: Member) -> bool:
    from glow_persistence.models import RecommendationEntry

    batch = UUID(str(result.data["batch_id"]))
    return bool(
        RecommendationEntry.objects.filter(
            batch_id=batch, candidate_id=candidate.account_id
        ).exists()
    )


@case("concurrency.two_viewers_create_at_once", "5", "D2", "D14", "DM-61")
def two_viewers_create_at_once(ctx: DiscoveryContext) -> str:
    """Codex's CX1: two mutually eligible viewers create batches at once, from separate
    connections, each holding its own account lock before either writes its entries (each entry's
    foreign-key check takes ``FOR KEY SHARE`` on the other's account), in both orders. Both pages
    succeed: ``FOR NO KEY UPDATE`` does not block ``FOR KEY SHARE``."""
    from glow_discovery import pages

    one, two = ctx.visible(), ctx.visible()
    expect(_both(ctx, one, two) == (True, True), "two mutually eligible viewers")
    for leader, follower in ((one, two), (two, one)):
        probes = {m.account_id: _Held("after_first_lock", "before_commit") for m in (one, two)}
        workers = {
            m.account_id: _Worker(
                partial(
                    pages.create, m.account_id, "recommendations", 50, probe=probes[m.account_id]
                )
            )
            for m in (one, two)
        }
        lead, follow = probes[leader.account_id], probes[follower.account_id]
        try:
            for worker in workers.values():
                worker.start()
            holding = all(
                p.reached["after_first_lock"].wait(REACH_SECONDS) for p in probes.values()
            )
            lead.release["after_first_lock"].set()
            led = lead.reached["before_commit"].wait(REACH_SECONDS)
            follow.release["after_first_lock"].set()
            followed = follow.reached["before_commit"].wait(REACH_SECONDS)
        finally:
            _finish(list(probes.values()), list(workers.values()))
        outcomes = ", ".join(w.outcome() for w in workers.values())
        expect(holding, "each viewer held its own account lock before either wrote its entries")
        expect(all(w.ok() for w in workers.values()), f"both pages succeed ({outcomes})")
        expect(led and followed, "each wrote its entries while the other held its account lock")
        expect(
            _has_entry(workers[one.account_id].result, two)
            and _has_entry(workers[two.account_id].result, one),
            "each batch holds an entry referencing the other's account",
        )
    return "both orders: each held its own account, wrote entries referencing the other's; both ok"


@case("concurrency.block_races_page_creation", "5", "D2", "D14", "DM-61")
def block_races_page_creation(ctx: DiscoveryContext) -> str:
    """The second cycle (DM-61 3.1): ``glow_chat``'s ``block`` by a candidate of the viewer, the
    candidate's account below the viewer's, so the block locks the candidate first and then the
    viewer, races the viewer's page creation, which locks the viewer and then writes an entry
    referencing the candidate. Both interleavings, from separate connections; both succeed."""
    from glow_discovery import pages
    from glow_profiles import operations

    from glow_ordering_proof.observe import observe_lock_wait

    candidate, viewer = sorted((ctx.visible(), ctx.visible()), key=lambda m: m.account_id)
    expect(candidate.account_id < viewer.account_id, "the candidate's account is the lower")
    expect(_sees(ctx, viewer, candidate), "the candidate is eligible for the viewer")
    seen: list[str] = []
    for page_first in (True, False):
        page_probe = _Held("after_first_lock", "before_commit")
        block_probe = _Held("after_first_lock", "before_commit")
        page = _Worker(
            partial(pages.create, viewer.account_id, "recommendations", 50, probe=page_probe)
        )
        block = _Worker(
            partial(
                operations.chat().block, candidate.account_id, viewer.account_id, probe=block_probe
            )
        )
        waited = None
        try:
            block.start()
            blocking = block_probe.reached["after_first_lock"].wait(REACH_SECONDS)
            page.start()
            paging = page_probe.reached["after_first_lock"].wait(REACH_SECONDS)
            if page_first:
                page_probe.release["after_first_lock"].set()
                wrote = page_probe.reached["before_commit"].wait(REACH_SECONDS)
                page_probe.release["before_commit"].set()
                block_probe.release["after_first_lock"].set()
            else:
                block_probe.release["after_first_lock"].set()
                assert block_probe.pid is not None and page_probe.pid is not None
                waited = observe_lock_wait(
                    block_probe.pid,
                    holder_pid=page_probe.pid,
                    finished=block.ended,
                    timeout=REACH_SECONDS,
                )
                page_probe.release["after_first_lock"].set()
                wrote = page_probe.reached["before_commit"].wait(REACH_SECONDS)
        finally:
            _finish([page_probe, block_probe], [page, block])
        order = "page first" if page_first else "block first"
        outcomes = f"page {page.outcome()}, block {block.outcome()}"
        expect(blocking and paging, f"{order}: each held its first account lock")
        expect(page.ok() and block.ok(), f"{order}: both succeed ({outcomes})")
        expect(wrote, f"{order}: the page wrote its entries while the block held the candidate")
        expect(_has_entry(page.result, candidate), f"{order}: the batch references the candidate")
        if waited is not None:
            expect(waited.observed, f"{order}: the block waited on the viewer's account lock")
        seen.append(order)
        ctx.unblock(candidate.account_id, viewer.account_id)
    return f"{' and '.join(seen)}: the block and the page both succeed; no cycle through the FK"


@case("concurrency.page_does_not_wait_on_a_candidates_writer", "5", "D2", "D14", "DM-61")
def page_does_not_wait_on_a_candidates_writer(ctx: DiscoveryContext) -> str:
    """The rule itself (DM-61 K3): while a writer of the candidate's (SV2's profile edit) holds
    the candidate's account lock, the page's transaction, which holds the viewer's account and
    writes an entry referencing the candidate's, commits without waiting on it. After that commit,
    the page reads each card's photo through SV2's ``delivery_reference``, its own transaction,
    which takes the photo owner's account ``FOR SHARE`` and so waits for the writer in flight, as
    SV2 designed every read to (``read_account_shared``); it holds none of the page's locks, so no
    cycle can form through it. The case records that wait and the page's result after it."""
    import time

    from glow_discovery import pages
    from glow_persistence.models import RecommendationEntry
    from glow_profiles import operations

    from glow_ordering_proof.observe import observe_lock_wait

    viewer, candidate = ctx.visible(), ctx.visible()
    expect(_sees(ctx, viewer, candidate), "the candidate is eligible for the viewer")
    current = ctx.profiles.get(candidate, "/api/v1/profile", "own_profile")
    intent = {
        "operation": "profile",
        "meta": {"idempotency_key": f"c1-{uuid4().hex}", "expected_version": current["version"]},
        "display_name": "Synthetic Member",
        "summary": "A synthetic member, edited while a page is made.",
    }
    earlier = {UUID(b) for b in _batches(viewer.account_id)}

    def committed() -> bool:
        return bool(
            RecommendationEntry.objects.filter(
                batch__account_id=viewer.account_id, candidate_id=candidate.account_id
            )
            .exclude(batch_id__in=earlier)
            .exists()
        )

    held = _Held("after_first_lock")
    page_probe = _Held()
    writer = _Worker(partial(operations.save_profile, candidate.account_id, intent, probe=held))
    page = _Worker(
        partial(pages.create, viewer.account_id, "recommendations", 50, probe=page_probe)
    )
    in_insert = photo_read = ""
    written = still_held = False
    try:
        writer.start()
        holding = held.reached["after_first_lock"].wait(REACH_SECONDS)
        page.start()
        deadline = time.monotonic() + REACH_SECONDS
        while not (written := committed()) and time.monotonic() < deadline:
            time.sleep(0.01)
        if page_probe.pid is not None and held.pid is not None:
            observed = observe_lock_wait(
                page_probe.pid, holder_pid=held.pid, finished=page.ended, timeout=REACH_SECONDS
            )
            if written:
                photo_read = observed.summary() if observed.observed else ""
            else:
                in_insert = observed.summary()
        still_held = writer.thread.is_alive() and not held.release["after_first_lock"].is_set()
    finally:
        _finish([held, page_probe], [writer, page])
    expect(holding, "the candidate's writer held the candidate's account lock")
    expect(
        written and still_held,
        f"the page's transaction committed its entry while the writer held the candidate's"
        f" account ({in_insert or 'no wait observed'})",
    )
    expect(bool(photo_read), "after its commit, the page's photo read (FOR SHARE) waited for it")
    expect(page.ok() and writer.ok(), f"both succeed (page {page.outcome()}, {writer.outcome()})")
    expect(_has_entry(page.result, candidate), "the batch references the held account")
    return (
        "the page's transaction committed its entry referencing the held account without waiting;"
        " its photo read after the commit then waited for the writer (SV2's FOR SHARE read)"
    )


@case("locks.account_locks_no_key_update", "5", "D2", "D14", "DM-61")
def account_locks_no_key_update(ctx: DiscoveryContext) -> str:
    """The scan (DM-61 K3): no explicit lock of an ``AppAccount`` row in ``services/api`` or the
    reference design is anything but ``FOR NO KEY UPDATE`` (``account_lock_scan``), and the scan
    finds each of the locks C1 changed."""
    from glow_ordering_proof import account_lock_scan

    locks = account_lock_scan.scan()
    bad = account_lock_scan.violations(locks)
    expect(
        not bad,
        "every account lock is FOR NO KEY UPDATE: "
        + "; ".join(f"{lock.where()} {lock.mode}" for lock in bad),
    )
    found = account_lock_scan.sites(locks)
    expect(found == account_lock_scan.EXPECTED_SITES, "the scan finds the seven account locks")
    total, joined = account_lock_scan.calls()
    return (
        f"{len(locks)} explicit account locks, in services/api and the reference, all no-key;"
        f" {total} select_for_update calls read, {joined} locking a queryset that joins (C2)"
    )


# -- 6. disclosure (acceptance check 6; D8) ---------------------------------------------------


@case("disclosure.population_of_one", "6", "D8")
def population_of_one(ctx: DiscoveryContext) -> str:
    viewer, candidate = ctx.visible(), ctx.visible()
    ctx.set_sets(viewer, {"gender": ["woman"]})
    on = ctx.page(viewer)
    ctx.set_sets(viewer, {"gender": ["man"]})
    off = ctx.page(viewer)
    ctx.set_sets(viewer, {})
    candidate_id = ctx.profile_id(candidate)
    expect(ctx.ids(on) == [candidate_id], "the filter on: the one member shown")
    expect(off["state"] == "empty", "the filter off-target: empty")
    ctx.hide_everyone()
    market = ctx.page(ctx.visible())
    expect(_empty_shape(off) == _empty_shape(market), "the empty page reads as an empty market's")
    card = on["items"][0]
    ctx.disclosure = {
        "population": 1,
        "filter_on": {"state": on["state"], "cards": len(on["items"])},
        "filter_off": {"state": off["state"], "cards": 0},
        "card_gender_shown": card["details"]["gender"] is not None,
        "revealed": (
            "the viewer learns that the one member's gender is in the narrowed set (accepted by"
            " OD-60); the card itself does not show the gender while its flag is off, and the"
            " empty page is the same as an empty market's"
        ),
    }
    return "population of one: on shows the member, off is an empty market's page"


@case("disclosure.no_count_reason_or_private_value", "6", "13", "D8", "D13")
def no_private_value(ctx: DiscoveryContext) -> str:
    from glow_ordering_proof.profile_support import RELATIONSHIP_VALUE

    viewer, candidate = _sensitive_pair(ctx)
    ctx.set_field(candidate, "relationship_status", [RELATIONSHIP_VALUE], shown=False)
    ctx.set_field(
        candidate,
        "orientation",
        [ORIENTATION_VALUES[2]],
        own_words="Synthetic hidden words",
        shown=False,
    )
    ctx.set_field(candidate, "looking_for", ["long-term"])
    ctx.set_sets(candidate, {"looking_for": ["long-term", "new-friends"], "gender": ["woman"]})
    ctx.set_filters(candidate, minimum=21, maximum=61)
    before = ctx.page(viewer)
    cards = [c for c in before["items"] if c["profile_id"] == ctx.profile_id(candidate)]
    expect(len(cards) == 1, "the candidate is shown")
    card = cards[0]
    expect(
        card["details"] == expected_details(candidate.account_id), "exactly the displayed fields"
    )
    expect(card["profile"] == _expected_profile(candidate.account_id), "exactly the profile's own")
    text = json.dumps(card)
    for hidden in ("new-friends", RELATIONSHIP_VALUE, ORIENTATION_VALUES[2], "Synthetic hidden"):
        expect(hidden not in text, "no set, hidden field or filter value on the card")
    expect(
        set(before)
        == {
            "kind",
            "collection",
            "batch_id",
            "version",
            "state",
            "items",
            "next_cursor",
            "expires_at",
        },
        "no count or reason on the page",
    )
    ctx.seed_interaction(candidate.account_id, viewer.account_id, "liked")
    after = ctx.page(viewer)
    again = [c for c in after["items"] if c["profile_id"] == ctx.profile_id(candidate)]
    expect(again == cards, "an unreciprocated like changes nothing the target sees")
    ctx.block(candidate.account_id, viewer.account_id)
    one, other = ctx.page(viewer), ctx.page(candidate)
    expect(_empty_shape(one) == _empty_shape(other), "neither page shows who blocked")
    return "the card shows its displayed fields only; no count, reason, set, filter or direction"


def _expected_profile(account_id: UUID) -> dict[str, Any]:
    """What ``CandidateProfile`` must hold of the candidate, from their own rows."""
    from glow_domain.identity import whole_years
    from glow_persistence.models import AccountAgeState, Profile

    profile = Profile.objects.get(account_id=account_id)
    born = AccountAgeState.objects.get(account_id=account_id).birth_date
    return {
        "profile_id": str(profile.id),
        "display_name": profile.display_name,
        "age": whole_years(born, db_today()),
        "summary": profile.bio,
        "media_delivery_refs": expected_refs(account_id),
        "compatibility": {"status": "pending"},
    }


# -- the card (D13) ---------------------------------------------------------------------------


@case("card.fields_area_and_photos", "6", "D13")
def card_fields_area_and_photos(ctx: DiscoveryContext) -> str:
    from glow_profiles import media

    from glow_ordering_proof.profile_support import RELATIONSHIP_VALUE

    viewer, candidate = _sensitive_pair(ctx)
    ctx.set_field(candidate, "gender", ["non-binary"], own_words="Synthetic own words", shown=True)
    ctx.set_field(
        candidate,
        "orientation",
        [ORIENTATION_VALUES[0]],
        own_words="Synthetic orient words",
        shown=True,
    )
    ctx.set_field(candidate, "relationship_status", [RELATIONSHIP_VALUE], shown=True)
    ctx.set_field(candidate, "looking_for", ["long-term", "new-friends"])
    held = ctx.profiles.approved_photo(candidate)
    third = ctx.profiles.approved_photo(candidate)
    removal = ctx.profiles.media_intent(candidate, "remove", asset_id=third)
    ctx.profiles.data(ctx.profiles.command(candidate, "/api/v1/media", removal), "media", "removed")
    ctx.profiles.uploaded_photo(candidate)
    hold = RecordingHold({UUID(held)})
    with mock.patch.object(media, "default_ports", lambda: test_ports(hold=hold)):
        page = ctx.page(viewer)
        expected = expected_refs(candidate.account_id)
    card = next(c for c in page["items"] if c["profile_id"] == ctx.profile_id(candidate))
    expect(card["details"] == expected_details(candidate.account_id), "the shown fields, exactly")
    for name in ("display_name", "summary", "age", "compatibility"):
        expect(card["profile"][name] == _expected_profile(candidate.account_id)[name], name)
    expect(card["details"]["gender"]["own_words"] is not None, "with the own words")
    expect(card["details"]["relationship_status"] is not None, "relationship status shown")
    expect(card["details"]["area_name"], "the area's name")
    expect(card["profile"]["media_delivery_refs"] == expected, "approved, deliverable photos only")
    expect(len(expected) == 1, "the held, removed and unapproved photos have no reference")
    expect(UUID(held) in hold.asked, "the hold port was asked")
    ctx.set_field(candidate, "gender", ["non-binary"], own_words="Synthetic own words", shown=False)
    page = ctx.page(viewer)
    card = next(c for c in page["items"] if c["profile_id"] == ctx.profile_id(candidate))
    expect(card["details"]["gender"] is None, "a field whose flag is off is not shown")
    return (
        "the card shows the flagged fields with own words, the area's name and deliverable photos"
    )


# -- 12. the route (acceptance check 12) ------------------------------------------------------


@case("route.refusals", "12", "D13")
def route_refusals(ctx: DiscoveryContext) -> str:
    viewer = ctx.visible()
    refused = 0
    reply = ctx.profiles.call(
        viewer, "POST", PAGE, {"collection": "discovery", "cursor": None, "limit": 5}, bearer=False
    )
    ctx.profiles.refused(reply, 401, "unauthenticated", "no token")
    refused += 1
    reply = ctx.profiles.call(
        viewer,
        "POST",
        PAGE,
        {"collection": "discovery", "cursor": None, "limit": 5},
        bearer="not-a-token",
    )
    ctx.profiles.refused(reply, 401, "unauthenticated", "a bad token")
    refused += 1
    for method in ("GET", "PUT", "DELETE"):
        ctx.profiles.refused(
            ctx.profiles.call(viewer, method, PAGE, None), 405, "invalid_request", method
        )
        refused += 1
    ctx.profiles.refused(
        ctx.profiles.call(
            viewer,
            "POST",
            PAGE + "?collection=discovery",
            {"collection": "discovery", "cursor": None, "limit": 5},
        ),
        400,
        "invalid_request",
        "a query string",
    )
    ctx.profiles.refused(
        ctx.profiles.call(
            viewer,
            "POST",
            PAGE,
            {"collection": "discovery", "cursor": None, "limit": 5},
            content_type="text/plain",
        ),
        400,
        "invalid_request",
        "another content type",
    )
    refused += 2
    good = {"collection": "discovery", "cursor": None, "limit": 5}
    for bad in (
        {**good, "extra": 1},
        {"collection": "discovery", "limit": 5},
        {**good, "limit": 1.5},
        {**good, "limit": "5"},
        {**good, "collection": "everyone"},
        {**good, "cursor": "a" * 101},
        {**good, "cursor": "abc\n"},
        {**good, "cursor": ""},
        {**good, "viewer_id": str(uuid4())},
    ):
        ctx.profiles.refused(
            ctx.profiles.call(viewer, "POST", PAGE, bad),
            400,
            "invalid_request",
            "not a PageRequest",
        )
        refused += 1
    for raw in (b"not json", b'{"collection": "discovery", "cursor": null, "limit": NaN}', b"[]"):
        response = viewer.device.client.generic(
            "POST",
            PAGE,
            data=raw,
            content_type="application/json",
            headers={"Authorization": f"Bearer {viewer.device.access}"},
        )
        expect(response.status_code == 400, "a body the parser cannot hold")
        refused += 1
    return f"{refused} refusals: no actor, a method, a query, a type, not a PageRequest"


# -- 14. one pointer order (acceptance check 14; D19) -------------------------------------------


@case("pointers.name_order", "14", "D19")
def pointer_order(ctx: DiscoveryContext) -> str:
    from glow_discovery import policy
    from glow_profiles import settings_store

    viewer = ctx.visible()
    ctx.visible()
    ctx.visible()
    # Each call is grouped by the identity its transaction is given at its start (C2; the
    # exact-head review's F4): the backend's PID and the transaction's start time, which ``run``
    # reads first (its ``Trace``), not ``id(tx)``, which CPython reuses once a Tx is freed.
    Identity = tuple[int, str]
    calls: list[tuple[Identity, tuple[str, ...], tuple[str, ...]]] = []
    real = settings_store.read_shared

    def recording(tx: Any, names: Any) -> Any:
        listed = tuple(names)
        found = real(tx, listed)
        identity = (int(tx.trace.backend_pid), tx.trace.started_at.isoformat())
        calls.append((identity, listed, tuple(tx.pointers)))
        return found

    with mock.patch.object(settings_store, "read_shared", recording):
        first = ctx.page(viewer, limit=1)
        expect(first["next_cursor"] is not None, "a cursor: the viewer has two candidates")
        ctx.page(viewer, "recommendations", first["next_cursor"], 1)
        ctx.page(viewer, "discovery")
    transactions: dict[Identity, list[tuple[tuple[str, ...], tuple[str, ...]]]] = {}
    for identity, names, held in calls:
        transactions.setdefault(identity, []).append((names, held))
    expect(len(transactions) == 3, "each of the three pages' transactions read its settings")
    for seen in transactions.values():
        expect(len(seen) == 1, "all the pointers in the transaction's first read_shared call")
        names, held = seen[0]
        expect(tuple(sorted(names)) == policy.SELECTION_SETTINGS, "the selection's settings")
        expect(list(held) == sorted(held), "held in name order")
    return (
        f"{len(transactions)} transactions (two pages with no cursor, one by cursor), each taking"
        " its pointers once, in name order"
    )


# -- 13. no private value in a log (acceptance check 13) ----------------------------------------


@case("logs.no_private_value", "13", "D8", "D17")
def logs_no_private_value(ctx: DiscoveryContext) -> str:
    import logging

    viewer = ctx.visible(area=CHICAGO)
    candidate = ctx.visible(area=LOS_ANGELES)
    ctx.set_field(candidate, "gender", ["woman"], own_words="Synthetic logged words", shown=True)
    records: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(self.format(record))

    handler = Capture(level=logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        ctx.pages_of(viewer)
        ctx.stale(viewer, "recommendations", "f" * 32 + ".01." + "0" * 64, "a forged cursor")
        ctx.page_reply(viewer, limit=99)
    finally:
        root.removeHandler(handler)
    text = "\n".join(records)
    expect(ctx.profiles.values.found_in(text) == 0, "no member value in the DEBUG capture")
    expect(ctx.profiles.ledger.found_in(text) == 0, "no secret in the DEBUG capture")
    for area_id in (CHICAGO, LOS_ANGELES):
        expect(re.search(rf"\b{area_id}\b", text) is None, "no area ID in the DEBUG capture")
    return f"{len(records)} DEBUG records: no member value, secret or area ID"


# -- the schema's own refusals (the P11 plan's DB04, for the batch and entry tables) ------------


BATCH_TABLES = ("glow_persistence_recommendationbatch", "glow_persistence_recommendationentry")


def _foreign_keys() -> dict[tuple[str, str], str]:
    """The foreign keys PostgreSQL holds on the two tables, by table and column, from the catalog
    (Django names them itself)."""
    from django.db import connection

    found: dict[tuple[str, str], str] = {}
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT t.relname, a.attname, c.conname FROM pg_catalog.pg_constraint c"
            " JOIN pg_catalog.pg_class t ON c.conrelid = t.oid"
            " JOIN pg_catalog.pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)"
            " WHERE c.contype = 'f' AND t.relname = ANY(%s)",
            [list(BATCH_TABLES)],
        )
        for table, column, name in cursor.fetchall():
            found[(str(table), str(column))] = str(name)
    return found


@case("constraints.batch_writes_are_refused", "DB04", "D7", "D18")
def batch_writes_are_refused(ctx: DiscoveryContext) -> str:
    """A direct write no SV3 code makes, against each constraint the batch and entry tables hold
    from migrations 0002 and 0010, and their foreign keys, is refused by PostgreSQL itself, naming
    that constraint, and leaves nothing behind. Harness writes only; the error's text is read for
    the constraint's name and never kept."""
    import importlib

    from django.db import IntegrityError, transaction
    from django.db.migrations.operations.models import AddConstraint
    from django.utils import timezone
    from glow_persistence.models import RecommendationBatch, RecommendationEntry

    owner, first, second = ctx.profiles.member(), ctx.profiles.member(), ctx.profiles.member()
    now = timezone.now()

    def batch(**changes: Any) -> Any:
        values: dict[str, Any] = {
            "account_id": owner.account_id,
            "collection": "recommendations",
            "eligibility_version": 1,
            "preferences_version": 1,
            "blocks_version": 1,
            "policy_version": "discovery.1.1.1.1.1",
            "limit": 100,
            "state": "ready",
            "expires_at": now,
        }
        values.update(changes)
        return RecommendationBatch.objects.create(**values)

    held = batch()

    def entry(**changes: Any) -> Any:
        values: dict[str, Any] = {
            "batch_id": held.id,
            "candidate_id": first.account_id,
            "position": 0,
            "candidate_eligibility_version": 1,
            "candidate_preferences_version": 1,
            "candidate_blocks_version": 1,
        }
        values.update(changes)
        return RecommendationEntry.objects.create(**values)

    entry()

    def snapshot() -> tuple[int, int]:
        return RecommendationBatch.objects.count(), RecommendationEntry.objects.count()

    keys = _foreign_keys()
    writes: list[tuple[str, Callable[[], Any]]] = [
        ("batch_collection", lambda: batch(collection="everyone")),
        ("batch_one_per_collection", lambda: batch()),
        ("batch_bound", lambda: batch(collection="discovery", limit=0)),
        ("batch_bound", lambda: batch(collection="discovery", limit=101)),
        ("batch_elig_revision", lambda: batch(collection="discovery", eligibility_version=0)),
        (
            "glow_persistence_recommendationbatch_state",
            lambda: batch(collection="discovery", state="open"),
        ),
        (
            "glow_persistence_recommendationbatch_version",
            lambda: batch(collection="discovery", version=0),
        ),
        ("batch_distinct_candidate", lambda: entry(position=1)),
        ("batch_position", lambda: entry(candidate_id=second.account_id)),
        ("entry_position_bound", lambda: entry(candidate_id=second.account_id, position=100)),
        (
            "entry_elig_revision",
            lambda: entry(
                candidate_id=second.account_id, position=1, candidate_eligibility_version=0
            ),
        ),
        (
            "glow_persistence_recommendationentry_version",
            lambda: entry(candidate_id=second.account_id, position=1, version=0),
        ),
        (
            keys[(BATCH_TABLES[1], "batch_id")],
            lambda: entry(batch_id=uuid4(), position=1, candidate_id=second.account_id),
        ),
        (keys[(BATCH_TABLES[1], "candidate_id")], lambda: entry(candidate_id=uuid4(), position=1)),
        (keys[(BATCH_TABLES[0], "account_id")], lambda: batch(account_id=uuid4())),
    ]
    declared: set[str] = set()
    for name in ("0002_app_domain", "0010_batch_collection"):
        migration = importlib.import_module(f"glow_persistence.migrations.{name}")
        declared |= {
            operation.constraint.name
            for operation in migration.Migration.operations
            if isinstance(operation, AddConstraint)
            and operation.model_name in ("recommendationbatch", "recommendationentry")
        }
    covered = {constraint for constraint, _ in writes}
    expect(declared <= covered, "a write for every constraint the two tables declare")
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
    RecommendationBatch.objects.filter(pk=held.pk).delete()
    return (
        f"{len(writes)} malformed direct writes refused by PostgreSQL, each by its constraint:"
        f" all {len(declared)} the two tables declare (0002 and 0010) and three foreign keys"
    )


# -- the plans and the bounds at 1,000 members (D7, D14 Q13; DB11) ----------------------------


@case("plans.population_and_bounds", "5", "D7", "D14", "DB11")
def plans_population_and_bounds(ctx: DiscoveryContext) -> str:
    from glow_discovery import policy, predicates
    from glow_discovery.eligibility import parameters
    from glow_domain import profile_settings as ps
    from glow_persistence.models import Profile, RecommendationEntry
    from glow_profiles import requirements

    label = ctx.current_label(ps.ONBOARDING_CONSENT)
    seeded = seed_population(1000, (NEW_YORK, PHILADELPHIA, LOS_ANGELES, CHICAGO), label)
    for account_id in seeded:
        profile = Profile.objects.get(account_id=account_id)
        expect(
            requirements.missing(account_id, profile, label) == [], "a seeded member is complete"
        )
    viewer = ctx.visible()
    counts: dict[str, int] = {}
    with ctx.count_statements() as counted:
        first = ctx.page(viewer, limit=50)
    counts["recommendations page 1 (creates the batch)"] = counted[0]
    expect(len(first["items"]) == 50 and first["next_cursor"], "a page holds 50, with a cursor")
    batch = UUID(first["batch_id"])
    expect(RecommendationEntry.objects.filter(batch_id=batch).count() == policy.BATCH_LIMIT, "100")
    with ctx.count_statements() as counted:
        second = ctx.page(viewer, "recommendations", first["next_cursor"], 50)
    counts["recommendations page 2 (cursor)"] = counted[0]
    expect(len(second["items"]) == 50 and second["next_cursor"] is None, "the batch ends at 100")
    with ctx.count_statements() as counted:
        broader = ctx.page(viewer, "discovery", None, 50)
    counts["discovery page 1 (creates the batch)"] = counted[0]
    expect(not set(ctx.ids(broader)) & set(ctx.ids(first) + ctx.ids(second)), "broader: the rest")
    ctx.statements = counts
    # D7's bound: a fixed number for the page's transaction and the actor, and four for each card's
    # photo (SV2's delivery_reference: its owner, then its own transaction), each card with one.
    for name, number in counts.items():
        expect(number <= 60 + 4 * 50, f"bounded statements: {name}")
    selection = _selection()
    values = parameters(selection, viewer.account_id)
    values.update(batch=str(uuid4()), exclude_batch=None, limit=policy.BATCH_LIMIT)
    ctx.plans["selection (recommendations)"] = explain(predicates.SELECTION, values)
    values.update(exclude_batch=batch)
    ctx.plans["selection (broader, leaving out the recommendations batch)"] = explain(
        predicates.SELECTION, values
    )
    recheck = parameters(selection, viewer.account_id)
    recheck.update(batch_id=batch, offset=0, limit=51)
    ctx.plans["recheck (a page of 50)"] = explain(predicates.RECHECK, recheck)
    pair = parameters(selection, viewer.account_id)
    pair.update(candidate=seeded[0])
    ctx.plans["pair (the trusted adapter)"] = explain(predicates.PAIR, pair)
    ctx.plans["viewer"] = explain(predicates.VIEWER, parameters(selection, viewer.account_id))
    return (
        f"1,000 seeded complete members; batches of 100, pages of 50; statements per page "
        f"{sorted(counts.values())}; {len(ctx.plans)} plans recorded"
    )


def run_case(ctx: DiscoveryContext, entry: Case) -> tuple[bool, str]:
    from django.core.cache import cache

    cache.clear()
    ctx.profiles.identity.case_id = entry.case_id
    ctx.profiles.watch_store()
    ctx.hide_everyone()
    try:
        outcome = True, entry.run(ctx)
    except CaseFailed as failed:
        outcome = False, f"FAILED: {failed}"
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        outcome = False, f"ERROR: {type(exc).__name__}"
    try:
        ctx.profiles.hold_media()
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        return False, f"ERROR: the value ledger's photo values: {type(exc).__name__}"
    return outcome


def plan() -> tuple[str, ...]:
    return tuple(entry.case_id for entry in CASES)
