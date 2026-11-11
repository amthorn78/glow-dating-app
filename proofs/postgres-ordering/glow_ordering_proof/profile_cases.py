"""The profile cases (SV2 Stage A; its brief's acceptance checks 1 to 9, 11 and 12, with D2 to
D9, D11, D13, D17 and D18; SV2 Stage B, checks 10 and 13 with check 9's photo requirement and
checks 11 and 12 for the photo routes, with D9, D10, D17 and D19), each run through the HTTP
endpoints with Django's test client on the
disposable profile database, signed in through SV1's identity routes.

Every case makes its own synthetic members. Settings are global: a case that publishes adds test
values only (no launch value changes), and every case reads the catalog it acts on. Each case
declares the acceptance checks it covers, and returns a short detail line or raises
``CaseFailed``; neither ever holds a member's value.
"""

from __future__ import annotations

import copy
import json
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from glow_ordering_proof.profile_support import (
    ADULT,
    AREA,
    BIRTH,
    CATALOG,
    COMPLETION,
    CONSENT,
    FIELDS,
    FILTERS,
    LOS_ANGELES,
    MEDIA,
    NEAREST,
    NEW_YORK,
    ORIENTATION_VALUES,
    PREFERENCES,
    PROFILE,
    RELATIONSHIP_VALUE,
    SENSITIVE,
    STAFF,
    VISIBILITY,
    CaseFailed,
    DecidingCheck,
    ProfileContext,
    RecordingDetector,
    RecordingHold,
    RecordingProcessing,
    db_today,
    expect,
    forms,
    grant_key,
    seed_chart,
    seed_verified,
    synthetic_png,
    test_ports,
    years_ago,
)


@dataclass(frozen=True)
class Case:
    case_id: str
    checks: tuple[str, ...]
    run: Callable[[ProfileContext], str]


CASES: list[Case] = []
# The suite's case count, pinned (C2, finding 15): a case lost or added without this changing
# fails the run before any case runs, and the offline tests. SV2 Stage B's correction C2 adds
# two (a hold stopping the check's approval; migration 0008's constraints).
CASE_COUNT = 69


def case(
    case_id: str, *checks: str
) -> Callable[[Callable[[ProfileContext], str]], Callable[[ProfileContext], str]]:
    def register(function: Callable[[ProfileContext], str]) -> Callable[[ProfileContext], str]:
        CASES.append(Case(case_id, checks, function))
        return function

    return register


def _counts() -> dict[str, int]:
    from glow_persistence.models import (
        IdempotencyRecord,
        OutboxEvent,
        PolicyRevision,
        SettingVersion,
        StaffAudit,
    )

    return {
        "versions": SettingVersion.objects.count(),
        "audits": StaffAudit.objects.count(),
        "events": OutboxEvent.objects.count(),
        "pointers": sum(PolicyRevision.objects.values_list("version", flat=True)),
        "records": IdempotencyRecord.objects.count(),
    }


def _events(aggregate_id: Any, event_type: str) -> int:
    from glow_persistence.models import OutboxEvent

    return int(OutboxEvent.objects.filter(aggregate_id=aggregate_id, event_type=event_type).count())


def _profile_row(account_id: UUID) -> Any:
    from glow_persistence.models import Profile

    return Profile.objects.get(account_id=account_id)


def _account(account_id: UUID) -> Any:
    from glow_persistence.models import AppAccount

    return AppAccount.objects.get(pk=account_id)


def _backend_pid() -> int:
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_backend_pid()")
        return int(cursor.fetchone()[0])


# =============================================================================================
# Acceptance check 1: the settings (D2)
# =============================================================================================


@case("settings.launch_defaults", "1", "D2", "D18")
def settings_launch_defaults(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import StaffAudit
    from glow_profiles import settings_store

    for name in ps.ALL_SETTINGS:
        first = settings_store.history(name)[0]
        expect(first["number"] == 1, f"{name}: version 1 is the launch default")
        expect(first["content"] == ps.LAUNCH_DEFAULTS[name], f"{name}: the launch content")
        expect(first["staff_subject"] == ps.LAUNCH_SUBJECT, f"{name}: system:launch-default")
        expect(first["reason"] == ps.LAUNCH_REASONS[name], f"{name}: OD-60, or OD-61")
    expect(
        StaffAudit.objects.filter(action="seed_launch_default").count() == len(ps.ALL_SETTINGS),
        "each seeded version has its audit row",
    )
    staff = settings_store.read_unlocked(ps.STAFF_APPROVAL)
    expect(staff.content["enabled"] is False, "staff approval without identity verification is off")
    member = ctx.member()
    catalog = ctx.catalog(member)
    expect(
        [v["id"] for v in catalog["gender"]["values"]][:3] == ["woman", "man", "non-binary"],
        "the catalog offers OD-60's gender list",
    )
    expect(catalog["looking_for"]["pick_limit"] is None, "looking for: any number")
    expect(catalog["gender"]["pick_limit"] == 1, "gender: one")
    expect(catalog["age_range"]["default_minimum"] == 18, "the age range starts at 18")
    expect(catalog["age_range"]["direction"] == "both_ways", "applied both ways")
    expect(
        catalog["location"]["chosen_area"] and catalog["location"]["approximate_location"],
        "both ways of locating are offered",
    )
    return f"{len(ps.ALL_SETTINGS)} settings read their launch defaults; staff approval is off"


@case("settings.publication_writes_version_audit_event", "1", "D2")
def settings_publication(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import OutboxEvent, PolicyRevision, StaffAudit
    from glow_profiles import settings_store

    before = settings_store.read_unlocked(ps.GENDER_LIST)
    old_rows = settings_store.history(ps.GENDER_LIST)
    content = copy.deepcopy(before.content)
    added = f"fixture-gender-{uuid4().hex[:8]}"
    content["values"].append({"id": added, "label": "Fixture gender", "retired": False})
    result = ctx.publish(ps.GENDER_LIST, content)
    expect(result.outcome == "applied", "the publication applies")
    after = settings_store.read_unlocked(ps.GENDER_LIST)
    expect(after.number == before.number + 1, "a new version is written")
    expect(after.content == content, "with the published content")
    pointer = PolicyRevision.objects.get(name=ps.GENDER_LIST)
    expect(pointer.artifact_ref == after.version_id, "the pointer moved to it")
    expect(pointer.policy_version == ps.policy_version(ps.GENDER_LIST, after.number), "label")
    audit = StaffAudit.objects.filter(object_id=after.version_id, action="publish").first()
    expect(audit is not None and audit.staff_subject == STAFF, "a StaffAudit row names the staff")
    expect(
        audit is not None
        and audit.before_version == before.number
        and audit.after_version == after.number,
        "the audit holds the old and new version",
    )
    events = OutboxEvent.objects.filter(event_type="policy_published", payload_ref=after.version_id)
    expect(events.count() == 1, "policy_published is emitted")
    event = events.first()
    expect(event is not None and event.schema_version == "glow-profiles-1", "SV2's schema")
    expect(settings_store.history(ps.GENDER_LIST)[: len(old_rows)] == old_rows, "append-only")
    return f"version {after.number} written with its audit row and policy_published"


def _crossing_publications() -> list[tuple[str, str, Callable[[dict[str, Any]], None]]]:
    from glow_domain import profile_settings as ps

    def reserved(content: dict[str, Any]) -> None:
        content["values"].append({"id": "all", "label": "All", "retired": False})

    def removed(content: dict[str, Any]) -> None:
        content["values"] = content["values"][1:]

    def over_fifty(content: dict[str, Any]) -> None:
        content["values"] += [
            {"id": f"fixture-many-{i}", "label": "Many", "retired": False} for i in range(51)
        ]

    def matching(content: dict[str, Any]) -> None:
        content["matching"] = "own_words"

    def age(content: dict[str, Any]) -> None:
        content["default_minimum"] = 17

    def coordinates(content: dict[str, Any]) -> None:
        content["store_coordinates"] = True

    def distance(content: dict[str, Any]) -> None:
        content["show_distance"] = True

    def rematch_block(content: dict[str, Any]) -> None:
        content["after_block"] = True

    def rematch_report(content: dict[str, Any]) -> None:
        content["after_report"] = True

    def unmatch(content: dict[str, Any]) -> None:
        content["unmatch"] = "read_only"

    def deletion(content: dict[str, Any]) -> None:
        content["deletion"] = "read_only"

    def readable(content: dict[str, Any]) -> None:
        content["own_pause"] = "read_only"

    def show_me(content: dict[str, Any]) -> None:
        content["show_me_shown"] = True

    def not_stated(content: dict[str, Any]) -> None:
        content["not_stated_seen_by"] = "everyone"

    def stands_in(content: dict[str, Any]) -> None:
        content["stands_in_for"] = ["identity_verification", "adult_check"]

    return [
        (ps.GENDER_LIST, ps.LIST_RESERVED_VALUE, reserved),
        (ps.GENDER_LIST, ps.LIST_VALUE_REMOVED, removed),
        (ps.LOOKING_FOR_LIST, ps.LIST_LIVE_VALUES, over_fifty),
        (ps.GENDER_LIST, ps.MATCHING_USES_LIST_VALUES, matching),
        (ps.AGE_RANGE, ps.AGE_FLOOR_18, age),
        (ps.LOCATION, ps.NO_COORDINATES_OR_DISTANCE, coordinates),
        (ps.LOCATION, ps.NO_COORDINATES_OR_DISTANCE, distance),
        (ps.REMATCH, ps.REMATCH_NEVER_AFTER_BLOCK_OR_REPORT, rematch_block),
        (ps.REMATCH, ps.REMATCH_NEVER_AFTER_BLOCK_OR_REPORT, rematch_report),
        (ps.HISTORY, ps.UNMATCH_BLOCK_HIDDEN, unmatch),
        (ps.HISTORY, ps.DELETION_AS_UNMATCH, deletion),
        (ps.NARROWING, ps.SHOW_ME_NEVER_SHOWN, show_me),
        (ps.NARROWING, ps.NOT_STATED_KEEP_ALL_ONLY, not_stated),
        (ps.STAFF_APPROVAL, ps.STAFF_APPROVAL_IDENTITY_ONLY, stands_in),
        ("readable", ps.MORE_READABLE_NEEDS_CONSENT, readable),
    ]


@case("settings.fixed_limits_refused_before_any_write", "1", "D2")
def settings_fixed_limits(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store

    # H at a cause made hidden first (a decrease needs no consent), so that making it readable
    # again crosses the H rule unless new consent wording names it.
    history = copy.deepcopy(settings_store.read_unlocked(ps.HISTORY).content)
    if history["own_pause"] != "hidden":
        history["own_pause"] = "hidden"
        expect(ctx.publish(ps.HISTORY, history).outcome == "applied", "H can become less readable")
    refused = 0
    for name, limit, cross in _crossing_publications():
        target = ps.HISTORY if name == "readable" else name
        content = copy.deepcopy(settings_store.read_unlocked(target).content)
        cross(content)
        before = _counts()
        result = ctx.publish(target, content)
        expect(result.outcome == "refused", f"{limit}: the publication is refused")
        expect(limit in result.reason, f"{limit}: the refusal names the limit")
        expect(_counts() == before, f"{limit}: nothing is written")
        refused += 1
    return f"{refused} crossing publications refused, each naming its limit, nothing written"


@case("settings.pointer_read_under_lock", "1", "D2")
def settings_pointer_locked(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_domain.chat import TransactionProbe
    from glow_profiles import operations, settings_store

    from glow_ordering_proof.concurrency import Hold, PidSlot, Worker
    from glow_ordering_proof.observe import observe_lock_wait

    member = ctx.ready_member()
    catalog = ctx.catalog(member)
    current = settings_store.read_unlocked(ps.GENDER_LIST).content
    intent = {
        "operation": "profile_field",
        "meta": ctx.meta(ctx.get(member, FIELDS, "own_profile_fields")["gender"]["version"]),
        "policy_version": catalog["policy_version"],
        "field": "gender",
        "value_ids": ["man"],
        "own_words": None,
        "shown": False,
    }
    holder, arriver = Worker("profile-publisher"), Worker("profile-member")
    try:
        hold, slot = Hold(), PidSlot()
        probe = TransactionProbe(on_begin=slot.set, before_commit=hold.point)
        publishing = holder.submit(
            lambda: settings_store.publish(
                ps.GENDER_LIST,
                copy.deepcopy(current),
                staff_subject=STAFF,
                reason="SV2-proof",
                request_id=uuid4(),
                probe=probe,
            )
        )
        expect(hold.wait_held(), "the publication holds the pointer's lock")
        arriver_pid = arriver.run(_backend_pid)
        writing = arriver.submit(lambda: operations.set_field(member.account_id, intent))
        wait = observe_lock_wait(arriver_pid, holder_pid=slot.wait(), finished=writing.done)
        hold.release.set()
        published = publishing.result(timeout=30)
        written = writing.result(timeout=30)
    finally:
        hold.release.set()
        holder.close()
        arriver.close()
    expect(wait.observed, "the member's write waited on the publication's pointer lock")
    expect(published.outcome == "applied", "the publication committed")
    expect(
        written.outcome == "refused" and written.code == "stale_version",
        "the write read the new version after it, and its catalog was stale",
    )
    return wait.summary()


@case("settings.retired_value_stays_matchable", "1", "2", "D2", "D3")
def settings_retired(ctx: ProfileContext) -> str:
    from glow_domain import profile_fields as pf
    from glow_domain import profile_settings as ps
    from glow_persistence.models import ProfileFieldChoice
    from glow_profiles import settings_store

    holder = ctx.ready_member()
    value = f"fixture-retiring-{uuid4().hex[:8]}"
    content = copy.deepcopy(settings_store.read_unlocked(ps.GENDER_LIST).content)
    content["values"].append({"id": value, "label": "Fixture retiring", "retired": False})
    expect(ctx.publish(ps.GENDER_LIST, content).outcome == "applied", "a value is added")
    ctx.data(ctx.field(holder, "gender", [value]), "own_profile_fields", "the holder picks it")
    for entry in content["values"]:
        if entry["id"] == value:
            entry["retired"] = True
    expect(ctx.publish(ps.GENDER_LIST, content).outcome == "applied", "the value is retired")
    row = ProfileFieldChoice.objects.get(account_id=holder.account_id, field="gender")
    expect(row.value_ids == [value], "the holder still holds it")
    own = ctx.get(holder, FIELDS, "own_profile_fields")["gender"]
    expect(own["value_ids"] == [value] and own["choose_again"] is True, "asked to choose again")
    catalog = ctx.catalog(holder)
    expect(value not in [v["id"] for v in catalog["gender"]["values"]], "not offered")
    expect(value in [v["id"] for v in catalog["gender"]["retired_values"]], "listed as retired")
    # Matchable: a viewer who keeps all genders, or narrowed before it retired, sees the holder.
    expect(pf.sees([pf.ALL], row.value_ids), "a viewer who keeps all sees the holder")
    expect(pf.sees([value], row.value_ids), "a narrowed set holding it still matches")
    newcomer = ctx.ready_member()
    refused = ctx.field(newcomer, "gender", [value])
    ctx.refused(refused, 400, "invalid_request", "a retired value for a new choice")
    again = ctx.field(holder, "gender", [value])
    ctx.refused(again, 400, "invalid_request", "the holder's next edit chooses again")
    return "the holder keeps and matches the retired value; a new choice of it is refused"


# =============================================================================================
# Acceptance checks 2 and 3: the fields and the "show me" sets (D3)
# =============================================================================================


@case("fields.values_within_pick_limits", "2", "D3")
def fields_values(ctx: ProfileContext) -> str:
    ctx.ensure_test_lists()
    member = ctx.ready_member()
    ctx.data(ctx.sensitive(member, "accepted"), "sensitive_consent", "the sensitive consent")
    for name, values in (
        ("gender", ["man"]),
        ("orientation", [ORIENTATION_VALUES[0]]),
        ("looking_for", ["long-term", "casual", "new-friends"]),
        ("relationship_status", [RELATIONSHIP_VALUE]),
    ):
        data = ctx.data(ctx.field(member, name, values), "own_profile_fields", f"{name} saved")
        expect(data[name]["value_ids"] == values, f"{name} holds the chosen values")
    refusals = 0
    for name, values in (
        ("gender", ["woman", "man"]),
        ("orientation", list(ORIENTATION_VALUES[:2])),
        ("relationship_status", ["single", RELATIONSHIP_VALUE]),
        ("gender", ["fixture-unknown-value"]),
        ("looking_for", ["fixture-unknown-value"]),
        ("gender", ["not-stated"]),
        ("looking_for", ["all"]),
    ):
        ctx.refused(ctx.field(member, name, values), 400, "invalid_request", f"{name} refused")
        refusals += 1
    return f"each field accepts list values within its pick limit; {refusals} refusals"


@case("fields.sensitive_needs_consent", "2", "3", "D3", "D6")
def fields_sensitive(ctx: ProfileContext) -> str:
    ctx.ensure_test_lists()
    member = ctx.ready_member()
    for name, values, words in (
        ("orientation", [ORIENTATION_VALUES[1]], None),
        ("relationship_status", ["single"], None),
        ("orientation", ["not-stated"], f"Words {uuid4().hex[:6]}"),
    ):
        ctx.refused(
            ctx.field(member, name, values, own_words=words), 403, "forbidden", f"{name} refused"
        )
    for sets in ({"orientation": [ORIENTATION_VALUES[0]]}, {"relationship_status": ["single"]}):
        ctx.refused(ctx.sets(member, sets), 403, "forbidden", "a narrowed sensitive set refused")
    # Leaving either unset carries nothing, and gender's own words are not sensitive.
    ctx.data(ctx.field(member, "orientation", ["not-stated"]), "own_profile_fields", "unset")
    ctx.data(
        ctx.field(member, "gender", ["woman"], own_words=f"Words {uuid4().hex[:6]}", shown=True),
        "own_profile_fields",
        "gender's own words",
    )
    ctx.data(ctx.sensitive(member, "accepted"), "sensitive_consent", "the consent accepted")
    ctx.data(
        ctx.field(
            member, "orientation", [ORIENTATION_VALUES[1]], own_words=f"Own {uuid4().hex[:6]}"
        ),
        "own_profile_fields",
        "orientation with its own words",
    )
    ctx.data(ctx.sets(member, {"orientation": [ORIENTATION_VALUES[1]]}), "own_preferences", "set")
    return (
        "orientation, relationship status, orientation's own words and narrowing need the consent"
    )


@case("fields.own_words_bounded_and_displayed_only_when_shown", "2", "D3")
def fields_own_words(ctx: ProfileContext) -> str:
    from glow_domain import profile_fields as pf
    from glow_persistence.models import ProfileFieldChoice

    member = ctx.ready_member()
    forty = "é" * 39 + "x"
    ctx.data(ctx.field(member, "gender", ["woman"], own_words=forty), "own_profile_fields", "40")
    ctx.refused(
        ctx.field(member, "gender", ["woman"], own_words=forty + "y"), 400, "invalid_request", "41"
    )
    ctx.refused(
        ctx.field(member, "gender", ["woman"], own_words="  　 "), 400, "invalid_request", "blank"
    )
    row = ProfileFieldChoice.objects.get(account_id=member.account_id, field="gender")
    state = pf.FieldState(tuple(row.value_ids), row.own_words, row.shown)
    expect(row.shown is False, "the display flag is off until the member turns it on")
    expect("gender" not in pf.displayed({"gender": state}), "hidden: neither value nor own words")
    words = f"Words {uuid4().hex[:6]}"
    ctx.data(
        ctx.field(member, "gender", ["woman"], own_words=words, shown=True),
        "own_profile_fields",
        "shown",
    )
    row = ProfileFieldChoice.objects.get(account_id=member.account_id, field="gender")
    shown = pf.displayed({"gender": pf.FieldState(tuple(row.value_ids), row.own_words, row.shown)})
    expect(shown.get("gender", {}).get("own_words") == words, "shown with the flag on")
    return "own words bounded at 40 code points, never displayed with the flag off"


@case("sets.start_at_all_and_stay_the_owners", "3", "D3", "D17")
def sets_start_at_all(ctx: ProfileContext) -> str:
    from glow_persistence.models import PreferenceSetEntry

    first, second = ctx.ready_member(), ctx.ready_member()
    data = ctx.get(first, PREFERENCES, "own_preferences")
    expect(
        all(entry["accepted_option_ids"] == ["all"] for entry in data["selections"]),
        "every set starts at all",
    )
    rows = PreferenceSetEntry.objects.filter(account_id=first.account_id)
    expect(
        sorted(rows.values_list("field", "value_id"))
        == sorted(
            (field, "all")
            for field in ("gender", "orientation", "looking_for", "relationship_status")
        ),
        "stored as the all marker's own rows",
    )
    ctx.data(ctx.sets(first, {"gender": ["man"]}), "own_preferences", "a narrowed set")
    other = ctx.get(second, PREFERENCES, "own_preferences")
    expect(
        all(entry["accepted_option_ids"] == ["all"] for entry in other["selections"]),
        "another member reads only their own sets",
    )
    ctx.refused(ctx.sets(first, {"gender": []}), 400, "invalid_request", "an empty set")
    ctx.refused(ctx.sets(first, {"gender": ["all", "man"]}), 400, "invalid_request", "all and more")
    ctx.refused(ctx.sets(first, {"gender": ["fixture-unknown"]}), 400, "invalid_request", "unknown")
    return "sets start at the all marker's rows, take list values only, are read by their owner"


def _member_values(account_id: UUID) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    from glow_persistence.models import PreferenceSetEntry, ProfileFieldChoice

    values = {
        row.field: list(row.value_ids)
        for row in ProfileFieldChoice.objects.filter(account_id=account_id)
    }
    sets: dict[str, list[str]] = {}
    for field, value in (
        PreferenceSetEntry.objects.filter(account_id=account_id)
        .order_by("field", "position")
        .values_list("field", "value_id")
    ):
        sets.setdefault(field, []).append(value)
    return values, sets


@case("sets.all_marker_not_stated_and_decliners", "3", "D3", "D6")
def sets_marker(ctx: ProfileContext) -> str:
    from glow_domain import profile_fields as pf
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store

    ctx.ensure_test_lists()
    keeper, narrower, decliner = ctx.ready_member(), ctx.ready_member(), ctx.ready_member()
    # A value the console adds after the keeper set their sets is in every set that keeps all.
    added = f"fixture-added-{uuid4().hex[:8]}"
    content = copy.deepcopy(settings_store.read_unlocked(ps.GENDER_LIST).content)
    content["values"].append({"id": added, "label": "Fixture added", "retired": False})
    expect(ctx.publish(ps.GENDER_LIST, content).outcome == "applied", "a value is added")
    holder = ctx.ready_member()
    ctx.data(ctx.field(holder, "gender", [added]), "own_profile_fields", "a newcomer holds it")
    ctx.data(ctx.sensitive(narrower, "accepted"), "sensitive_consent", "consent to narrow")
    ctx.data(
        ctx.sets(narrower, {"orientation": [ORIENTATION_VALUES[0]], "gender": ["woman", added]}),
        "own_preferences",
        "narrowed",
    )
    ctx.refused(
        ctx.sets(narrower, {"orientation": ["not-stated"]}), 400, "invalid_request", "not-stated"
    )
    keeper_values, keeper_sets = _member_values(keeper.account_id)
    holder_values, holder_sets = _member_values(holder.account_id)
    narrower_values, narrower_sets = _member_values(narrower.account_id)
    decliner_values, decliner_sets = _member_values(decliner.account_id)
    expect(pf.two_way(keeper_values, keeper_sets, holder_values, holder_sets), "added value seen")
    # The decliner states no orientation: seen by viewers who keep all, not by a narrower.
    expect("orientation" not in decliner_values, "the decliner states none")
    expect(pf.two_way(keeper_values, keeper_sets, decliner_values, decliner_sets), "seen by all")
    expect(
        not pf.sees(narrower_sets["orientation"], decliner_values.get("orientation", ())),
        "not-stated is in no narrowed set",
    )
    return "all includes a value the console adds; not-stated only in all; decliners are seen"


# =============================================================================================
# Acceptance check 4: the age range (D4)
# =============================================================================================


@case("filters.age_range_floor_and_order", "4", "D4", "D5")
def filters_age(ctx: ProfileContext) -> str:
    from glow_persistence.models import Preferences

    member = ctx.ready_member()
    current = ctx.get(member, FILTERS, "own_filters")
    expect(current["minimum_age"] == 18 and current["maximum_age"] is None, "the default range")
    catalog = ctx.catalog(member)

    def filters(minimum: Any, maximum: Any, distance: str = "anywhere") -> Any:
        now = ctx.get(member, FILTERS, "own_filters")
        return ctx.command(
            member,
            FILTERS,
            {
                "operation": "filters",
                "meta": ctx.meta(now["version"]),
                "policy_version": catalog["policy_version"],
                "minimum_age": minimum,
                "maximum_age": maximum,
                "distance_choice": distance,
            },
        )

    ctx.refused(filters(17, None), 400, "invalid_request", "a minimum below 18")
    # The operation's own floor, behind the contract's: a minimum below 18 that reached it is
    # refused there too, and nothing is written.
    from glow_profiles import operations

    now = ctx.get(member, FILTERS, "own_filters")
    direct = operations.set_filters(
        member.account_id,
        {
            "operation": "filters",
            "meta": {"idempotency_key": ctx.key(), "expected_version": now["version"]},
            "policy_version": catalog["policy_version"],
            "minimum_age": 17,
            "maximum_age": None,
            "distance_choice": "anywhere",
        },
    )
    expect(direct.outcome == "refused" and direct.reason == "age_floor", "the operation's floor")
    ctx.refused(filters(30, 29), 400, "invalid_request", "a maximum below the minimum")
    ctx.refused(filters(18, None, "fixture-unknown-distance"), 400, "invalid_request", "distance")
    saved = ctx.data(filters(25, 40), "own_filters", "a range")
    expect(saved["minimum_age"] == 25 and saved["maximum_age"] == 40, "saved")
    row = Preferences.objects.get(account_id=member.account_id)
    expect(row.minimum_age == 25 and row.maximum_age == 40, "stored")
    return "a minimum below 18 (at the route and at the operation) and a maximum below it refused"


# =============================================================================================
# Acceptance check 5: the location (D5)
# =============================================================================================

COORDINATES = (40.7123457, -74.0067891)
COORDINATE_TEXT = ("40.7123457", "-74.0067891", "7123457", "0067891")


def _remember_coordinates(ctx: ProfileContext) -> None:
    for text in COORDINATE_TEXT:
        ctx.values.add(text)


def _found_in_database(texts: tuple[str, ...]) -> list[str]:
    """Which tables hold any of ``texts`` in any row (every column, as JSON text), in any form
    the code could store it in (``profile_support.forms``: a date in prose or as Python prints
    it, a coordinate at a lower precision, down to three decimals)."""
    from django.db import connection

    texts = tuple(sorted({form for text in texts for form in forms(text)}))
    found: list[str] = []
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' ORDER BY 1"
        )
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            cursor.execute(f'SELECT row_to_json(t)::text FROM "{table}" AS t')
            for (row,) in cursor.fetchall():
                if any(text in row for text in texts):
                    found.append(table)
                    break
    return found


@case("area.chosen_by_id", "5", "D5")
def area_by_id(ctx: ProfileContext) -> str:
    member = ctx.member()
    ctx.accept_onboarding(member)
    ctx.data(ctx.profile(member), "own_profile", "the profile")
    data = ctx.data(ctx.area(member, LOS_ANGELES), "own_area", "an area by ID")
    expect(data["area_id"] == LOS_ANGELES and data["area_name"], "kept with its name")
    ctx.refused(ctx.area(member, "00000"), 400, "invalid_request", "an unknown area")
    expect(_profile_row(member.account_id).area.area_id == LOS_ANGELES, "only the area is kept")
    return "an area is chosen by its ID; an unknown ID is refused"


@case("area.nearest_query_changes_nothing", "5", "D5")
def area_query(ctx: ProfileContext) -> str:
    from glow_persistence.models import IdempotencyRecord, OutboxEvent

    _remember_coordinates(ctx)
    member = ctx.member()
    ctx.data(ctx.profile(member), "own_profile", "the profile")
    profile = _profile_row(member.account_id)
    before = (_counts(), OutboxEvent.objects.count(), IdempotencyRecord.objects.count())
    reply = ctx.command(member, NEAREST, {"latitude": COORDINATES[0], "longitude": COORDINATES[1]})
    data = ctx.data(reply, "nearest_area", "the phone-location query")
    expect(data["area_id"] == NEW_YORK, "the nearest area's internal point")
    expect(
        set(data) == {"kind", "area_id", "area_name"}, "the area only: no coordinate, no distance"
    )
    after = (_counts(), OutboxEvent.objects.count(), IdempotencyRecord.objects.count())
    expect(after == before, "no row, no event and no idempotency record is written")
    again = _profile_row(member.account_id)
    expect(again.area_id is None and again.version == profile.version, "the area is not set")
    kept = ctx.data(ctx.area(member, data["area_id"]), "own_area", "the member sets it by ID")
    expect(kept["area_id"] == NEW_YORK, "kept only when the member sets it")
    return "the query returns the nearest area and changes nothing; the member then sets it"


@case("area.coordinates_never_kept_or_echoed", "5", "12", "D5")
def area_coordinates(ctx: ProfileContext) -> str:
    _remember_coordinates(ctx)
    member = ctx.member()
    # The member has a profile, so a profile row is one more place the coordinates must not be.
    ctx.data(ctx.profile(member), "own_profile", "the profile")
    body = {"latitude": COORDINATES[0], "longitude": COORDINATES[1]}
    ctx.data(ctx.command(member, NEAREST, body), "nearest_area", "a query")
    # Never in a URL or a query string: a query string is refused, and nothing is echoed.
    in_url = ctx.call(member, "POST", f"{NEAREST}?latitude={COORDINATES[0]}", body)
    ctx.refused(in_url, 400, "invalid_request", "coordinates in a query string")
    as_get = ctx.call(member, "GET", f"{NEAREST}?latitude={COORDINATES[0]}")
    expect(as_get.status in (400, 405), "a GET with coordinates is refused")
    # Never read from a header: only the body counts.
    headers = {"X-Latitude": COORDINATE_TEXT[0], "X-Longitude": COORDINATE_TEXT[1]}
    ctx.refused(
        ctx.call(member, "POST", NEAREST, None, headers=headers),
        400,
        "invalid_request",
        "coordinates in headers only",
    )
    # A JSON body without them, beside headers that carry them: the body alone is read.
    ctx.refused(
        ctx.call(member, "POST", NEAREST, {}, headers=headers),
        400,
        "invalid_request",
        "coordinates in headers beside a JSON body without them",
    )
    # Out of range, or of the wrong type: refused, and the error names no value.
    for bad in (
        {"latitude": 91.7123457, "longitude": COORDINATES[1]},
        {"latitude": "40.7123457", "longitude": COORDINATES[1]},
        {"latitude": COORDINATES[0], "longitude": COORDINATES[1], "accuracy": 3},
    ):
        reply = ctx.command(member, NEAREST, bad)
        ctx.refused(reply, 400, "invalid_request", "a bad query")
        expect(not any(t in json.dumps(reply.body) for t in COORDINATE_TEXT), "no value echoed")
    # The validation message and its exception carry the field's path, never the value.
    from glow_profiles import contract

    try:
        contract.parse("AreaQuery", json.dumps({"latitude": 91.7123457, "longitude": 0}).encode())
        raise CaseFailed("an out-of-range latitude parses")
    except contract.Invalid as invalid:
        expect(not any(t in str(invalid) for t in COORDINATE_TEXT), "the exception's text")
    for body_text in map(json.dumps, ctx.served):
        expect(not any(t in body_text for t in COORDINATE_TEXT), "no response holds them")
    for header_text in ctx.headers:
        expect(not any(t in header_text for t in COORDINATE_TEXT), "no response header holds them")
    found = _found_in_database(COORDINATE_TEXT)
    expect(not found, "no table holds the coordinates (outbox and idempotency records included)")
    return (
        "never stored, returned (in a body or a header), echoed, read from a URL or a header,"
        " or in an exception"
    )


@case("area.no_route_returns_a_distance", "5", "D5", "D17")
def area_no_distance(ctx: ProfileContext) -> str:
    member = ctx.ready_member()
    for path in (PROFILE, FIELDS, PREFERENCES, FILTERS, AREA, CATALOG, COMPLETION):
        ctx.call(member, "GET", path)
    ctx.command(member, NEAREST, {"latitude": 34.0522342, "longitude": -118.2436849})
    for value in ("34.0522342", "-118.2436849"):
        ctx.values.add(value)
    for body in ctx.served:
        text = json.dumps(body)
        for word in ("distance_miles", "miles", "kilometres", "latitude", "longitude", '"km"'):
            expect(word not in text, f"no served body names {word}")
    return f"{len(ctx.served)} served bodies: no distance, no radius, no coordinate"


@case("area.file_hash_and_925_areas", "5", "D5")
def area_file(ctx: ProfileContext) -> str:
    import hashlib
    import importlib

    from glow_persistence.models import Area
    from glow_profiles import areas_source

    data = areas_source.DERIVED_FILE.read_bytes()
    expect(hashlib.sha256(data).hexdigest() == areas_source.DERIVED_SHA256, "the pinned hash")
    loaded = areas_source.read_derived(data)
    expect(len(loaded) == 925, "925 areas in the file")
    migration = importlib.import_module("glow_persistence.migrations.0006_area_table")
    expect(migration.AREA_FILE_SHA256 == areas_source.DERIVED_SHA256, "the migration pins it")
    expect(Area.objects.count() == 925, "925 areas loaded")
    stored = sorted(Area.objects.values_list("area_id", flat=True))
    expect(stored == [area.area_id for area in loaded], "the table's IDs are the file's")
    expect(not Area.objects.filter(name__contains=", PR ").exists(), "no Puerto Rico area")
    return "the committed table matches its pinned hash and holds 925 areas, none in Puerto Rico"


# =============================================================================================
# Acceptance check 6: consent (D6)
# =============================================================================================


def _match(ctx: ProfileContext, first: Any, second: Any) -> tuple[Any, Callable[[str], Any]]:
    """An active match between two visible members (glow_chat's activation, the proof's way to
    make one), and a send by the first through glow_chat's send check."""
    from glow_chat.contact import OrmContactPersistence
    from glow_domain.chat import SendCommand
    from glow_persistence.models import Match

    chat = OrmContactPersistence(provider="fixture")
    activated = chat.activate_match(first.account_id, second.account_id)
    expect(activated.outcome == "applied", "glow_chat activates the match")
    match = Match.objects.get(pk=activated.match_id)
    session = ctx.identity.account_session_of(first.device.access)

    def send(key: str) -> Any:
        current = Match.objects.get(pk=match.pk)
        return chat.send(
            SendCommand(session.pk, current.pk, current.contact_version, key, "Synthetic hello")
        )

    return match, send


@case("consent.onboarding_reaches_the_send_check", "6", "9", "D6", "D9")
def consent_send(ctx: ProfileContext) -> str:
    first, second = ctx.visible_member(), ctx.visible_member()
    _, send = _match(ctx, first, second)
    expect(send("send-1").outcome == "authorized", "a send is authorized")
    withdrawn = ctx.data(ctx.withdraw_onboarding(first), "onboarding", "withdrawn")
    expect(withdrawn["state"] == "withdrawn", "the withdrawal is recorded through glow_chat")
    expect(_events(first.account_id, "consent_withdrawn") == 1, "glow_chat's own event")
    expect(_profile_row(first.account_id).state == "incomplete", "a visible profile is demoted")
    refused = send("send-2")
    expect(refused.outcome == "refused", "a send is refused after the withdrawal")
    accepted = ctx.accept_onboarding(first)
    expect(accepted["state"] == "accepted", "accepted again through glow_chat")
    expect(_events(first.account_id, "consent_accepted") >= 2, "glow_chat's acceptance events")
    return f"the send check refuses after the withdrawal ({refused.reason})"


@case("consent.old_version_refused", "6", "D6")
def consent_old_version(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import ConsentDecision
    from glow_profiles import settings_store

    member = ctx.member()
    old = ctx.catalog(member)["consents"]["onboarding"]["policy_version"]
    for name in (ps.ONBOARDING_CONSENT, ps.SENSITIVE_CONSENT):
        content = copy.deepcopy(settings_store.read_unlocked(name).content)
        content["text"] += f" (revision {uuid4().hex[:6]})"
        expect(ctx.publish(name, content).outcome == "applied", f"{name} gets a new version")
    catalog = ctx.catalog(member)
    current = catalog["consents"]["onboarding"]["policy_version"]
    expect(current != old, "the onboarding consent's version moved")
    stale = ctx.command(
        member,
        CONSENT,
        {
            "operation": "consent",
            "meta": ctx.meta(1),
            "policy_version": old,
            "decision": "accepted",
        },
    )
    ctx.refused(stale, 409, "stale_version", "an old onboarding version")
    expect(not ConsentDecision.objects.filter(account_id=member.account_id).exists(), "nothing")
    old_sensitive = ps.policy_version(ps.SENSITIVE_CONSENT, 1)
    stale = ctx.command(
        member,
        SENSITIVE,
        {
            "operation": "sensitive_consent",
            "meta": ctx.meta(1),
            "policy_version": old_sensitive,
            "decision": "accepted",
        },
    )
    ctx.refused(stale, 409, "stale_version", "an old sensitive version")
    expect(not ConsentDecision.objects.filter(account_id=member.account_id).exists(), "nothing")
    expect(
        ctx.accept_onboarding(member)["policy_version"] == current, "the current one is accepted"
    )
    return "an old version of either consent is refused and writes nothing"


@case("consent.purposes_never_satisfy_or_revoke_each_other", "6", "D6")
def consent_purposes(ctx: ProfileContext) -> str:
    from glow_persistence.models import ConsentDecision

    # A member with no onboarding decision, whose sensitive decisions are the latest of all.
    lonely = ctx.member()
    for decision in ("accepted", "withdrawn", "accepted"):
        ctx.data(ctx.sensitive(lonely, decision), "sensitive_consent", f"sensitive {decision}")
    expect("consent" in ctx.missing(lonely), "a sensitive decision does not satisfy onboarding")
    expect(ctx.get(lonely, CONSENT, "onboarding")["state"] == "required", "onboarding: required")
    # A visible member whose latest decision of all is a sensitive withdrawal.
    member = ctx.visible_member()
    other = ctx.visible_member()
    _, send = _match(ctx, member, other)
    for decision in ("accepted", "withdrawn", "accepted", "withdrawn"):
        ctx.data(ctx.sensitive(member, decision), "sensitive_consent", f"sensitive {decision}")
    latest = ConsentDecision.objects.filter(account_id=member.account_id).order_by("-version")[0]
    expect(latest.purpose == "sensitive_profile", "the highest version is the sensitive one")
    expect(
        "consent" not in ctx.missing(member), "a sensitive withdrawal does not revoke onboarding"
    )
    expect(_profile_row(member.account_id).state == "visible", "the profile stays visible")
    expect(send("send-purpose").outcome == "authorized", "glow_chat's send check filters too")
    return "neither purpose's decision satisfies or revokes the other, in SV2 and glow_chat"


@case("consent.sensitive_withdrawal_scope", "3", "6", "D6", "D17")
def consent_sensitive_withdrawal(ctx: ProfileContext) -> str:
    from glow_persistence.models import IdempotencyRecord, PreferenceSetEntry, ProfileFieldChoice

    ctx.ensure_test_lists()
    member = ctx.visible_member()
    ctx.data(ctx.sensitive(member, "accepted"), "sensitive_consent", "accepted")
    words = f"Own {uuid4().hex[:6]}"
    ctx.data(
        ctx.field(member, "orientation", [ORIENTATION_VALUES[2]], own_words=words, shown=True),
        "own_profile_fields",
        "orientation",
    )
    ctx.data(ctx.field(member, "relationship_status", ["single"]), "own_profile_fields", "status")
    ctx.data(
        ctx.sets(
            member,
            {"orientation": [ORIENTATION_VALUES[0]], "relationship_status": ["single"]},
        ),
        "own_preferences",
        "narrowed",
    )
    carried = ("profile_field.orientation", "profile_field.relationship_status", "preferences")
    records = IdempotencyRecord.objects.filter(actor_id=member.account_id)
    expect(records.filter(operation__in=carried).count() >= 3, "the commands left records")
    kept = records.exclude(operation__in=carried).count()
    sensitive = ("orientation", "relationship_status")
    before = {
        row.field: row
        for row in ProfileFieldChoice.objects.filter(
            account_id=member.account_id, field__in=sensitive
        )
    }
    expect(set(before) == set(sensitive), "both rows exist before the withdrawal")
    changed = {field: _events(row.pk, "profile_field_changed") for field, row in before.items()}
    ctx.data(ctx.sensitive(member, "withdrawn"), "sensitive_consent", "withdrawn")
    # C2 (DM-55, Z13): each row is set to "not stated" in place, with its event, so every earlier
    # event still names an existing record.
    for field, old in before.items():
        row = ProfileFieldChoice.objects.filter(pk=old.pk).first()
        expect(row is not None, f"{field}: the row still exists")
        assert row is not None
        expect(row.value_ids == ["not-stated"], f"{field}: not stated in place")
        expect(row.own_words is None and row.shown is False, f"{field}: no own words, flag off")
        expect(row.setting_version == old.setting_version, f"{field}: its setting version kept")
        expect(row.version == old.version + 1, f"{field}: its version bumped")
        expect(
            _events(row.pk, "profile_field_changed") == changed[field] + 1,
            f"{field}: profile_field_changed for it",
        )
    rows = ProfileFieldChoice.objects.filter(account_id=member.account_id)
    expect(rows.filter(field__in=sensitive).count() == 2, "both rows kept")
    own = ctx.get(member, FIELDS, "own_profile_fields")
    expect(own["orientation"]["value_ids"] == ["not-stated"], "orientation reads not stated")
    expect(own["orientation"]["own_words"] is None, "orientation's own words are removed")
    expect(own["relationship_status"]["value_ids"] == ["not-stated"], "status reads not stated")
    sets = {
        field: list(values)
        for field, values in (
            (
                "orientation",
                PreferenceSetEntry.objects.filter(
                    account_id=member.account_id, field="orientation"
                ).values_list("value_id", flat=True),
            ),
            (
                "relationship_status",
                PreferenceSetEntry.objects.filter(
                    account_id=member.account_id, field="relationship_status"
                ).values_list("value_id", flat=True),
            ),
        )
    }
    expect(sets == {"orientation": ["all"], "relationship_status": ["all"]}, "both sets reset")
    expect(not records.filter(operation__in=carried).exists(), "their idempotency records deleted")
    expect(records.exclude(operation__in=carried).count() == kept + 1, "others kept")
    expect(_profile_row(member.account_id).state == "visible", "never hidden from keep-all viewers")
    # A row that already holds "not stated", with no own words and its flag off, is left as it
    # is, with no event; the other is reset with its event.
    second = ctx.visible_member()
    ctx.data(ctx.sensitive(second, "accepted"), "sensitive_consent", "accepted")
    ctx.data(
        ctx.field(second, "orientation", [ORIENTATION_VALUES[0]], shown=True),
        "own_profile_fields",
        "orientation",
    )
    ctx.data(
        ctx.field(second, "relationship_status", ["not-stated"], shown=False),
        "own_profile_fields",
        "already not stated",
    )
    quiet = ProfileFieldChoice.objects.get(
        account_id=second.account_id, field="relationship_status"
    )
    loud = ProfileFieldChoice.objects.get(account_id=second.account_id, field="orientation")
    quiet_events = _events(quiet.pk, "profile_field_changed")
    loud_events = _events(loud.pk, "profile_field_changed")
    ctx.data(ctx.sensitive(second, "withdrawn"), "sensitive_consent", "withdrawn")
    after = ProfileFieldChoice.objects.get(pk=quiet.pk)
    expect(
        (after.value_ids, after.own_words, after.shown, after.version, after.updated_at)
        == (quiet.value_ids, quiet.own_words, quiet.shown, quiet.version, quiet.updated_at),
        "an already reset row is unchanged",
    )
    expect(_events(quiet.pk, "profile_field_changed") == quiet_events, "with no event")
    reset = ProfileFieldChoice.objects.get(pk=loud.pk)
    expect(reset.value_ids == ["not-stated"] and reset.shown is False, "the other is reset")
    expect(_events(loud.pk, "profile_field_changed") == loud_events + 1, "with its event")
    # Every profile_field_changed event of the run names an existing row (Z15).
    from glow_persistence.models import OutboxEvent

    named = set(
        OutboxEvent.objects.filter(event_type="profile_field_changed").values_list(
            "payload_ref", flat=True
        )
    )
    existing = set(ProfileFieldChoice.objects.filter(pk__in=named).values_list("pk", flat=True))
    expect(named == existing, "every profile_field_changed event names an existing row")
    return (
        "rows set to not stated in place with their events, an already reset row left alone;"
        " own words, narrowed sets and the commands' records removed; sets reset"
    )


@case("consent.withdrawal_on_a_paused_profile_stays_paused", "6", "9", "D9")
def consent_paused(ctx: ProfileContext) -> str:
    member = ctx.visible_member()
    profile = ctx.get(member, PROFILE, "own_profile")
    paused = ctx.data(
        ctx.command(
            member,
            VISIBILITY,
            {"operation": "visibility", "meta": ctx.meta(profile["version"]), "action": "pause"},
        ),
        "own_profile",
        "paused",
    )
    expect(paused["visibility"] == "paused", "paused through glow_chat")
    ctx.data(ctx.withdraw_onboarding(member), "onboarding", "withdrawn")
    expect(_profile_row(member.account_id).state == "paused", "a paused profile stays paused")
    return "a withdrawal leaves a paused profile paused"


# =============================================================================================
# Acceptance check 7: the adult check (D7)
# =============================================================================================


@case("adult.eighteen_today_and_the_leap_days_pass", "7", "D7")
def adult_pass(ctx: ProfileContext) -> str:
    from datetime import date

    from glow_domain.identity import AdultOutcome, adult_outcome

    for born in (years_ago(18), "2008-02-29"):
        member = ctx.member()
        data = ctx.data(ctx.adult(member, born), "own_age_state", "the adult check")
        expect(data["state"] == "self_declared_adult" and data["birth_date"] == born, "passes")
    # The onboarding fixtures' leap-day boundary (P04), on the rule's own function: the server's
    # clock cannot be set, so the boundary days are given to it.
    expect(adult_outcome(date(2008, 2, 29), date(2026, 2, 28)) is AdultOutcome.UNDER_AGE, "28 Feb")
    expect(adult_outcome(date(2008, 2, 29), date(2026, 3, 1)) is AdultOutcome.PASS, "1 Mar")
    expect(adult_outcome(date(2008, 9, 23), date(2026, 9, 23)) is AdultOutcome.PASS, "18 today")
    expect(adult_outcome(date(2008, 9, 24), date(2026, 9, 23)) is AdultOutcome.UNDER_AGE, "a day")
    return "18 today and the leap-day date pass through the route; the fixtures' boundaries hold"


@case("adult.failing_dates_are_refused_and_not_stored", "7", "D7")
def adult_fail(ctx: ProfileContext) -> str:
    from glow_persistence.models import AccountAgeState

    member = ctx.member()
    before = _account(member.account_id).eligibility_version
    for born, status, code in (
        (years_ago(18, days=1), 403, "forbidden"),
        (years_ago(-1), 400, "invalid_request"),
        ("2001-02-29", 400, "invalid_request"),
    ):
        ctx.refused(ctx.adult(member, born), status, code, "a failing date")
        row = AccountAgeState.objects.get(account_id=member.account_id)
        expect(row.state == "unknown" and row.birth_date is None and row.version == 1, "unchanged")
    expect(_account(member.account_id).eligibility_version == before, "no bump without a change")
    return "under 18, a future date and an invalid date are refused; the state stays unknown"


@case("adult.a_corrected_date_reruns_and_demotes", "7", "9", "D7", "D9")
def adult_rerun(ctx: ProfileContext) -> str:
    from glow_persistence.models import AccountAgeState, BirthInput

    first, second = ctx.visible_member(), ctx.visible_member()
    _, send = _match(ctx, first, second)
    expect(send("send-adult-1").outcome == "authorized", "a send is authorized")
    # C2 (DM-55): refused (forbidden), with no idempotency record, while the reset commits.
    ctx.refused(ctx.adult(first, years_ago(17)), 403, "forbidden", "the corrected date")
    data = ctx.get(first, ADULT, "own_age_state")
    expect(data["state"] == "unknown" and data["birth_date"] is None, "unknown, the date cleared")
    row = AccountAgeState.objects.get(account_id=first.account_id)
    expect(row.state == "unknown" and row.birth_date is None, "stored as unknown with no date")
    expect(_profile_row(first.account_id).state == "incomplete", "the visible profile demoted")
    expect(send("send-adult-2").outcome == "refused", "so a send is refused")
    current = BirthInput.objects.filter(account_id=first.account_id).order_by("-version")[0]
    expect(current.state == "missing", "the birth input holding another date stops being current")
    return "a failing rerun is refused, sets unknown, clears the date and demotes; no send"


@case("adult.a_birth_input_with_another_date_changes_it", "7", "D7")
def adult_birth_date(ctx: ProfileContext) -> str:
    from glow_persistence.models import AccountAgeState

    member = ctx.ready_member(birth_date=years_ago(30))
    other = years_ago(31, days=-40)
    ctx.data(ctx.birth_input(member, other), "birth_input", "another date")
    row = AccountAgeState.objects.get(account_id=member.account_id)
    expect(row.birth_date.isoformat() == other and row.state == "self_declared_adult", "one date")
    return "the birth input's date becomes the age state's, and the check reran"


@case("adult.transition_bumps_and_waits_on_the_account_lock", "7", "D7")
def adult_lock(ctx: ProfileContext) -> str:
    from django.db import transaction
    from django.utils import timezone
    from glow_chat.contact import OrmContactPersistence
    from glow_domain.chat import TransactionProbe
    from glow_domain.identity import AccountId, AgeAssuranceState, AgeTransition
    from glow_identity.age import OrmAgeAssurance

    from glow_ordering_proof.concurrency import Hold, PidSlot, Worker
    from glow_ordering_proof.observe import observe_lock_wait

    member = ctx.member()
    ctx.accept_onboarding(member)
    before = _account(member.account_id).eligibility_version
    ctx.data(ctx.adult(member, years_ago(25)), "own_age_state", "the adult check")
    expect(
        _account(member.account_id).eligibility_version == before + 1,
        "the transition bumps eligibility_version",
    )
    holder, arriver, prober = Worker("age-holder"), Worker("age-arriver"), Worker("age-prober")
    chat = OrmContactPersistence(provider="fixture")

    def age_row_free() -> bool:
        from django.db import DatabaseError
        from glow_persistence.models import AccountAgeState

        try:
            with transaction.atomic():
                rows = AccountAgeState.objects.select_for_update(nowait=True)
                list(rows.filter(account_id=member.account_id))
        except DatabaseError:
            return False
        return True

    def transition() -> str:
        with transaction.atomic():
            return str(
                OrmAgeAssurance().transition(
                    AgeTransition(
                        AccountId(str(member.account_id)),
                        AgeAssuranceState.UNKNOWN,
                        None,
                        timezone.now(),
                    )
                )
            )

    try:
        hold, slot = Hold(), PidSlot()
        probe = TransactionProbe(on_begin=slot.set, before_commit=hold.point)
        withdrawing = holder.submit(lambda: chat.withdraw_consent(member.account_id, probe=probe))
        expect(hold.wait_held(), "a writer holds the account row")
        arriver_pid = arriver.run(_backend_pid)
        moving = arriver.submit(transition)
        wait = observe_lock_wait(arriver_pid, holder_pid=slot.wait(), finished=moving.done)
        free = prober.run(age_row_free) if wait.observed and not moving.done() else None
        hold.release.set()
        withdrawn = withdrawing.result(timeout=30)
        moved = moving.result(timeout=30)
    finally:
        hold.release.set()
        holder.close()
        arriver.close()
        prober.close()
    expect(wait.observed, "the transition waited on the account row lock")
    expect(free is True, "while it waits, it holds no lock on the age state's row: account first")
    expect(
        withdrawn.outcome == "applied" and moved == "applied", "both applied, one after the other"
    )
    return wait.summary()


@case("adult.a_new_date_makes_the_birth_input_missing", "7", "8", "D7", "D8")
def adult_new_date(ctx: ProfileContext) -> str:
    from glow_persistence.models import BirthInput, EngineIdentity

    member = ctx.ready_member()
    seed_chart(member.account_id)
    ctx.data(ctx.adult(member, years_ago(40)), "own_age_state", "a new passing date")
    current = BirthInput.objects.filter(account_id=member.account_id).order_by("-version")[0]
    expect(current.state == "missing", "the current revision is missing")
    mapping = EngineIdentity.objects.get(account_id=member.account_id)
    expect(mapping.state == "pending" and mapping.engine_reference is None, "mapping pending")
    expect(mapping.adapter_version == "fixture:adapter-version", "its adapter_version kept")
    read = ctx.get(member, BIRTH, "birth_input")
    expect(read["resolution"] == "missing", "the owner reads it as missing")
    expect("chart" in ctx.missing(member), "completion reads it as no birth input")
    return "a new eligibility date sets the current revision missing and the mapping pending"


# =============================================================================================
# Acceptance check 8: the private birth input (D8)
# =============================================================================================


@case("birth.submit_correct_change_write_private_revisions", "8", "11", "D8", "D17")
def birth_revisions(ctx: ProfileContext) -> str:
    from glow_persistence.models import BirthInput, EngineIdentity

    member = ctx.ready_member()
    born = ctx.get(member, ADULT, "own_age_state")["birth_date"]
    first = ctx.get(member, BIRTH, "birth_input")
    expect(first["version"] == 1 and first["resolution"] == "pending", "submitted, pending")
    second = ctx.data(
        ctx.birth_input(member, born, local_time="21:56:08"), "birth_input", "correct"
    )
    expect(second["version"] == 2 and second["input_id"] != first["input_id"], "a new revision")
    BirthInput.objects.filter(pk=second["input_id"]).update(state="resolved")
    third = ctx.data(ctx.birth_input(member, born, local_time="09:08:07"), "birth_input", "change")
    expect(third["version"] == 3 and third["resolution"] == "pending", "a change, pending")
    expect(BirthInput.objects.filter(account_id=member.account_id).count() == 3, "three revisions")
    expect(not EngineIdentity.objects.filter(account_id=member.account_id).exists(), "no mapping")
    stranger = ctx.member()
    for input_id in (first["input_id"], third["input_id"]):
        ctx.refused(ctx.call(stranger, "GET", f"{BIRTH}/{input_id}"), 404, "not_found", "theirs")
        own = ctx.get(member, f"{BIRTH}/{input_id}", "birth_input")
        expect(own["input_id"] == input_id, "the owner reads each revision")
    ctx.refused(ctx.call(stranger, "GET", BIRTH), 404, "not_found", "no input of their own")
    return "three private revisions; no route returns another member's input"


@case("birth.a_time_is_required_and_approximate_is_kept", "8", "D8")
def birth_time(ctx: ProfileContext) -> str:
    member = ctx.member()
    ctx.accept_onboarding(member)
    born = years_ago(33)
    ctx.data(ctx.adult(member, born), "own_age_state", "adult")
    unknown = ctx.birth_input(member, born, local_time=None, precision="unknown", expected=0)
    ctx.refused(unknown, 400, "invalid_request", "an unknown time")
    kept = ctx.data(
        ctx.birth_input(member, born, local_time="06:45:12", precision="approximate", expected=0),
        "birth_input",
        "an approximate time",
    )
    expect(kept["input"]["local_time"] == "06:45:12", "keeps its entered value")
    expect(kept["input"]["time_precision"] == "approximate", "and its precision")
    return "an unknown time is refused; an approximate time keeps its value"


@case("birth.needs_the_adult_pass_and_current_consent", "8", "D8")
def birth_prerequisites(ctx: ProfileContext) -> str:
    member = ctx.member()
    born = years_ago(29)
    ctx.refused(ctx.birth_input(member, born, expected=0), 403, "forbidden", "no adult pass")
    ctx.data(ctx.adult(member, born), "own_age_state", "adult")
    ctx.refused(ctx.birth_input(member, born, expected=0), 403, "forbidden", "no consent")
    ctx.accept_onboarding(member)
    ctx.data(ctx.birth_input(member, born, expected=0), "birth_input", "then accepted")
    return "the birth input needs the adult pass and the current onboarding consent"


@case("birth.a_seeded_mapping_returns_to_pending", "8", "D8")
def birth_mapping(ctx: ProfileContext) -> str:
    from glow_persistence.models import BirthInput, EngineIdentity

    member = ctx.ready_member()
    seed_chart(member.account_id)
    mapping = EngineIdentity.objects.get(account_id=member.account_id)
    expect(mapping.engine_reference.startswith("fixture:"), "the seed is marked fixture:")
    born = ctx.get(member, ADULT, "own_age_state")["birth_date"]
    new = ctx.data(ctx.birth_input(member, born, local_time="11:22:33"), "birth_input", "new")
    mapping = EngineIdentity.objects.get(account_id=member.account_id)
    expect(mapping.state == "pending", "pending")
    expect(
        mapping.engine_reference is None
        and mapping.engine_version is None
        and mapping.contract_version is None,
        "its engine reference and versions cleared",
    )
    expect(mapping.adapter_version == "fixture:adapter-version", "its adapter_version kept")
    expect(str(mapping.birth_input_id) == new["input_id"], "pointing at the new revision")
    expect(new["mapping_version"] is None, "no mapping version is returned")
    expect(BirthInput.objects.filter(account_id=member.account_id).count() == 2, "two revisions")
    return "a new revision returns the test's seeded mapping to pending, at the new revision"


# =============================================================================================
# Acceptance check 9: visibility and completion (D9, D18)
# =============================================================================================


def _edit(ctx: ProfileContext, member: Any, summary: str = "A synthetic member.") -> dict[str, Any]:
    return ctx.data(ctx.profile(member, summary), "own_profile", "the profile edit")


def _visibility(ctx: ProfileContext, member: Any, action: str) -> Any:
    profile = ctx.get(member, PROFILE, "own_profile")
    return ctx.command(
        member,
        VISIBILITY,
        {"operation": "visibility", "meta": ctx.meta(profile["version"]), "action": action},
    )


@case("completion.refuses_each_missing_requirement", "9", "D9")
def completion_each(ctx: ProfileContext) -> str:
    results: list[str] = []

    def stays(member: Any, expected: list[str], what: str) -> None:
        edited = _edit(ctx, member)
        expect(edited["visibility"] == "incomplete", f"{what}: completion is refused")
        expect(ctx.missing(member) == expected, f"{what}: the read lists exactly {expected}")
        results.append(what)

    member = ctx.ready_member()
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    ctx.data(ctx.withdraw_onboarding(member), "onboarding", "withdrawn")
    stays(member, ["consent"], "consent")

    member = ctx.ready_member()
    seed_verified(member.account_id)
    ctx.refused(ctx.adult(member, years_ago(16)), 403, "forbidden", "a failing rerun")
    # The rerun also makes the birth input stop being current, so the chart is missing too.
    stays(member, ["adult_check", "chart"], "the adult check")

    member = ctx.member()
    ctx.accept_onboarding(member)
    born = ctx.adult_date()
    ctx.data(ctx.adult(member, born), "own_age_state", "adult")
    ctx.data(ctx.birth_input(member, born), "birth_input", "birth")
    ctx.data(ctx.profile(member), "own_profile", "profile")
    ctx.data(ctx.field(member, "gender", ["man"]), "own_profile_fields", "gender only")
    ctx.data(ctx.area(member, NEW_YORK), "own_area", "area")
    # SV2 Stage B (D9): an approved photo, through Stage B's own path.
    ctx.approved_photo(member)
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    stays(member, ["profile_fields"], "the profile's fields (no looking for)")

    member = ctx.member()
    ctx.accept_onboarding(member)
    born = ctx.adult_date()
    ctx.data(ctx.adult(member, born), "own_age_state", "adult")
    ctx.data(ctx.birth_input(member, born), "birth_input", "birth")
    ctx.data(ctx.profile(member), "own_profile", "profile")
    ctx.data(ctx.field(member, "gender", ["man"]), "own_profile_fields", "gender")
    ctx.data(ctx.field(member, "looking_for", ["casual"]), "own_profile_fields", "looking for")
    ctx.approved_photo(member)
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    stays(member, ["area"], "the area")

    # SV2 Stage B (D9): at least one approved photo.
    member = ctx.ready_member(photo=False)
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    stays(member, ["photo"], "a photo")

    member = ctx.ready_member()
    seed_verified(member.account_id)
    stays(member, ["chart"], "the chart")

    member = ctx.ready_member()
    seed_chart(member.account_id)
    stays(member, ["identity_verification"], "identity verification")

    member = ctx.ready_member()
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    edited = _edit(ctx, member, "")
    expect(edited["visibility"] == "incomplete", "an empty summary refuses completion")
    expect(ctx.missing(member) == ["profile_fields"], "the summary is a profile field")
    results.append("the summary")
    return f"completion refused for each missing requirement: {len(results)} checks"


@case("completion.needs_the_chart_and_identity_verification_seeded", "9", "D8", "D9", "D18")
def completion_seeded(ctx: ProfileContext) -> str:
    from glow_domain.identity_verification import FixtureIdentityCheck
    from glow_persistence.models import EngineIdentity, IdentityVerification
    from glow_profiles.identity_verification import OrmIdentityVerification

    member = ctx.ready_member()
    expect(ctx.missing(member) == ["chart", "identity_verification"], "both missing")
    expect(_edit(ctx, member)["visibility"] == "incomplete", "refused without either")
    # No SV2 code writes either: the check's seam passes no one, and its port refuses.
    expect(FixtureIdentityCheck().request_check(member.account_id).status == "unavailable", "seam")
    from django.utils import timezone

    outcome = OrmIdentityVerification(timezone.now()).record_check_passed(member.account_id, "x")
    expect(outcome.outcome == "refused", "the port refuses a verified verdict in SV2")
    expect(not IdentityVerification.objects.filter(account_id=member.account_id).exists(), "none")
    expect(not EngineIdentity.objects.filter(account_id=member.account_id).exists(), "no mapping")
    seed_chart(member.account_id)
    expect(_edit(ctx, member)["visibility"] == "incomplete", "refused without verification")
    seed_verified(member.account_id)
    expect(_edit(ctx, member)["visibility"] == "visible", "passes with both seeded in setup")
    # A resolved mapping is the chart only at the current revision (D8): one that points at an
    # older revision does not complete the profile. Harness writes, as the seeds are.
    from glow_persistence.models import BirthInput

    born = ctx.get(member, ADULT, "own_age_state")["birth_date"]
    new = ctx.data(ctx.birth_input(member, born, local_time="10:20:30"), "birth_input", "new")
    expect(_profile_row(member.account_id).state == "incomplete", "a new revision demotes")
    old = BirthInput.objects.get(account_id=member.account_id, version=new["version"] - 1)
    BirthInput.objects.filter(pk=new["input_id"]).update(state="resolved")
    EngineIdentity.objects.filter(account_id=member.account_id).update(
        state="resolved",
        birth_input=old,
        engine_reference="fixture:engine-reference-old",
        engine_version="fixture:engine-version",
        contract_version="fixture:contract-version",
    )
    expect("chart" in ctx.missing(member), "a mapping at an older revision is no chart")
    expect(_edit(ctx, member)["visibility"] == "incomplete", "so completion is refused")
    EngineIdentity.objects.filter(account_id=member.account_id).update(
        birth_input_id=new["input_id"]
    )
    expect(_edit(ctx, member)["visibility"] == "visible", "at the current revision it completes")
    return (
        "completion refused without the chart or identity verification, or with a mapping at an"
        " older revision; passes with both seeded"
    )


@case("visibility.pause_and_resume_through_glow_chat", "9", "D9")
def visibility_pause(ctx: ProfileContext) -> str:
    first, second = ctx.visible_member(), ctx.visible_member()
    _, send = _match(ctx, first, second)
    paused = ctx.data(_visibility(ctx, first, "pause"), "own_profile", "paused")
    expect(paused["visibility"] == "paused", "paused")
    expect(_events(_profile_row(first.account_id).pk, "profile_paused") == 1, "glow_chat's event")
    expect(send("send-pause").outcome == "refused", "a send is refused while paused")
    resumed = ctx.data(_visibility(ctx, first, "resume"), "own_profile", "resumed")
    expect(resumed["visibility"] == "visible", "visible again")
    expect(_events(_profile_row(first.account_id).pk, "profile_resumed") == 1, "glow_chat's event")
    expect(send("send-resume").outcome == "authorized", "and a send is authorized")
    return "pause and resume go through glow_chat; a send is refused while paused"


@case("visibility.resume_rechecks_completion", "9", "D9")
def visibility_resume(ctx: ProfileContext) -> str:
    member = ctx.visible_member()
    ctx.data(_visibility(ctx, member, "pause"), "own_profile", "paused")
    ctx.data(ctx.withdraw_onboarding(member), "onboarding", "withdrawn while paused")
    refused = _visibility(ctx, member, "resume")
    ctx.refused(refused, 403, "forbidden", "resume of an incomplete profile")
    expect(_profile_row(member.account_id).state == "paused", "it stays paused")
    ctx.accept_onboarding(member)
    resumed = ctx.data(_visibility(ctx, member, "resume"), "own_profile", "resumed")
    expect(resumed["visibility"] == "visible", "resumed once complete")
    return "resume refuses an incomplete profile before glow_chat's resume_profile"


@case("staff.approval_gated_narrow_survives_and_is_revocable", "9", "D18")
def staff_approval(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import IdentityVerification, StaffAudit
    from glow_profiles import settings_store, staff

    member = ctx.ready_member()
    seed_chart(member.account_id)
    off = copy.deepcopy(settings_store.read_unlocked(ps.STAFF_APPROVAL).content)
    if off["enabled"]:
        off["enabled"] = False
        expect(ctx.publish(ps.STAFF_APPROVAL, off).outcome == "applied", "switched off first")

    def approve(account_id: UUID) -> Any:
        return staff.approve_without_id(
            account_id, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
        )

    audits = StaffAudit.objects.count()
    refused = approve(member.account_id)
    expect(refused.outcome == "refused" and refused.code == "forbidden", "refused while off")
    expect(not IdentityVerification.objects.filter(account_id=member.account_id).exists(), "none")
    expect(StaffAudit.objects.count() == audits, "nothing audited")
    on = copy.deepcopy(off)
    on["enabled"] = True
    expect(ctx.publish(ps.STAFF_APPROVAL, on).outcome == "applied", "switched on")
    approved = approve(member.account_id)
    expect(approved.outcome == "applied", "approved while on")
    row = IdentityVerification.objects.get(account_id=member.account_id)
    expect(row.state == "staff_approved" and row.staff_subject == STAFF, "staff_approved")
    expect(
        StaffAudit.objects.filter(object_id=row.pk, action="approve_without_id").exists(), "audited"
    )
    expect(ctx.missing(member) == [], "it satisfies identity verification")
    # Only that requirement: another member's other requirements stay missing.
    other = ctx.member()
    expect(approve(other.account_id).outcome == "applied", "another approval")
    missing = ctx.missing(other)
    expect("identity_verification" not in missing, "identity verification is met")
    expect(
        {"consent", "adult_check", "profile_fields", "area", "chart"} <= set(missing), "only that"
    )
    expect(_edit(ctx, member)["visibility"] == "visible", "the approved member completes")
    expect(ctx.publish(ps.STAFF_APPROVAL, off).outcome == "applied", "switched off again")
    expect(
        IdentityVerification.objects.get(account_id=member.account_id).state == "staff_approved",
        "a past approval survives the switch-off",
    )
    late = ctx.member()
    expect(approve(late.account_id).code == "forbidden", "a new approval is refused once off")
    revoked = staff.revoke_approval(
        member.account_id, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
    )
    expect(revoked.outcome == "applied", "staff revoke it at any time")
    expect(
        IdentityVerification.objects.get(account_id=member.account_id).state == "unverified", "x"
    )
    expect(_profile_row(member.account_id).state == "incomplete", "revoked: demoted")
    member_refusal = staff.approve_without_id(
        member.account_id, staff_subject="member:someone", reason="x", request_id=uuid4()
    )
    expect(member_refusal.outcome == "refused", "only a staff subject approves")
    return "refused while off; narrow; survives the switch-off; revoked, it demotes"


EXPECTED_PROFILE_ROUTES = frozenset(
    {
        "api/v1/profile",
        "api/v1/profile/completion",
        "api/v1/profile/visibility",
        "api/v1/profile/fields",
        "api/v1/profile/preferences",
        "api/v1/profile/filters",
        "api/v1/profile/area",
        "api/v1/profile/area/nearest",
        "api/v1/profile/catalog",
        "api/v1/profile/<uuid:profile_id>",
        "api/v1/consent",
        "api/v1/consent/sensitive",
        "api/v1/eligibility/adult",
        "api/v1/birth-input",
        "api/v1/birth-input/<uuid:input_id>",
        # SV2 Stage B: F05's member routes (D10, D11); no provider, system or staff step.
        "api/v1/media",
        "api/v1/media/<uuid:asset_id>",
    }
)


@case("staff.no_member_route_reaches_a_staff_operation", "9", "D1", "D18")
def staff_no_route(ctx: ProfileContext) -> str:
    from glow_ordering_proof.identity_cases import EXPECTED_ROUTES, served_routes

    routes = served_routes()
    expect(routes == EXPECTED_ROUTES | EXPECTED_PROFILE_ROUTES, "SV1's routes and SV2's only")
    for route in routes:
        for word in ("staff", "setting", "approve", "revoke", "restrict", "publish"):
            expect(word not in route, f"no route names {word}")
    member = ctx.member()
    for path in ("/api/v1/staff/approve", "/api/v1/settings", "/api/v1/profile/approve"):
        reply = ctx.call(member, "POST", path, {})
        expect(reply.status == 404, f"{path} is not served")
    sv1, sv2 = len(EXPECTED_ROUTES), len(EXPECTED_PROFILE_ROUTES)
    return f"{len(routes)} routes: SV1's {sv1} and SV2's {sv2}; no staff route"


@case("completion.each_change_emits_its_event", "9", "D2", "D9")
def completion_events(ctx: ProfileContext) -> str:
    from glow_persistence.models import (
        AccountAgeState,
        BirthInput,
        OutboxEvent,
        Preferences,
        ProfileFieldChoice,
    )

    member = ctx.visible_member()
    account = member.account_id
    profile = _profile_row(account)
    age = AccountAgeState.objects.get(account_id=account)
    birth = BirthInput.objects.filter(account_id=account).order_by("version")[0]
    field = ProfileFieldChoice.objects.get(account_id=account, field="gender")
    preferences = Preferences.objects.get(account_id=account)
    expected = {
        (profile.pk, "profile_edited"),
        (profile.pk, "profile_completed"),
        (profile.pk, "area_changed"),
        (field.pk, "profile_field_changed"),
        (age.pk, "age_state_changed"),
        (birth.pk, "birth_input_submitted"),
    }
    found = set(
        OutboxEvent.objects.filter(
            aggregate_id__in={profile.pk, age.pk, birth.pk, field.pk}
        ).values_list("aggregate_id", "event_type")
    )
    expect(expected <= found, "the profile's changes emitted their events")
    ctx.data(ctx.sets(member, {"gender": ["man"]}), "own_preferences", "a set")
    expect(_events(preferences.pk, "preferences_changed") >= 1, "preferences_changed")
    ctx.data(ctx.withdraw_onboarding(member), "onboarding", "withdrawn")
    expect(_events(profile.pk, "profile_demoted") == 1, "profile_demoted")
    for event in OutboxEvent.objects.filter(schema_version="glow-profiles-1"):
        expect(len(str(event.payload_ref)) == 36, "events carry references, never values")
    return "every change emitted its event; events carry references only"


@case("completion.takes_the_account_lock_first_and_sees_a_withdrawal", "9", "D9")
def completion_lock(ctx: ProfileContext) -> str:
    from glow_chat.contact import OrmContactPersistence
    from glow_domain.chat import TransactionProbe
    from glow_profiles import operations

    from glow_ordering_proof.concurrency import Hold, PidSlot, Worker
    from glow_ordering_proof.observe import observe_lock_wait

    member = ctx.ready_member()
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    profile = ctx.get(member, PROFILE, "own_profile")
    intent = {
        "operation": "profile",
        "meta": ctx.meta(profile["version"]),
        "display_name": "Synthetic Member",
        "summary": "A synthetic member.",
    }
    chat = OrmContactPersistence(provider="fixture")
    holder, arriver = Worker("withdrawal-holder"), Worker("completion-arriver")
    try:
        hold, slot = Hold(), PidSlot()
        probe = TransactionProbe(on_begin=slot.set, before_commit=hold.point)
        withdrawing = holder.submit(lambda: chat.withdraw_consent(member.account_id, probe=probe))
        expect(hold.wait_held(), "the withdrawal holds the account row")
        arriver_pid = arriver.run(_backend_pid)
        completing = arriver.submit(lambda: operations.save_profile(member.account_id, intent))
        wait = observe_lock_wait(arriver_pid, holder_pid=slot.wait(), finished=completing.done)
        hold.release.set()
        withdrawn = withdrawing.result(timeout=30)
        completed = completing.result(timeout=30)
    finally:
        hold.release.set()
        holder.close()
        arriver.close()
    expect(wait.observed, "the completion waited on the account row lock")
    expect(withdrawn.outcome == "applied", "the withdrawal committed first")
    expect(completed.outcome == "applied", "the edit applied")
    ctx.remember(member.account_id, intent)
    expect(_profile_row(member.account_id).state == "incomplete", "and saw the withdrawal")
    first = wait.summary()
    # The other order: a completion holds the lock; a withdrawal waits and demotes after it.
    other = ctx.ready_member()
    seed_chart(other.account_id)
    seed_verified(other.account_id)
    profile = ctx.get(other, PROFILE, "own_profile")
    intent = dict(intent, meta=ctx.meta(profile["version"]))
    consent = ctx.get(other, CONSENT, "onboarding")
    withdrawal = {
        "operation": "consent",
        "meta": ctx.meta(consent["version"]),
        "policy_version": ctx.catalog(other)["consents"]["onboarding"]["policy_version"],
        "decision": "withdrawn",
    }
    holder, arriver = Worker("completion-holder"), Worker("withdrawal-arriver")
    try:
        hold, slot = Hold(), PidSlot()
        probe = TransactionProbe(on_begin=slot.set, before_commit=hold.point)
        completing = holder.submit(
            lambda: operations.save_profile(other.account_id, intent, probe=probe)
        )
        expect(hold.wait_held(), "the completion holds the account row")
        arriver_pid = arriver.run(_backend_pid)
        withdrawing = arriver.submit(
            lambda: operations.decide_onboarding_consent(other.account_id, withdrawal)
        )
        wait = observe_lock_wait(arriver_pid, holder_pid=slot.wait(), finished=withdrawing.done)
        hold.release.set()
        completed = completing.result(timeout=30)
        withdrawn = withdrawing.result(timeout=30)
    finally:
        hold.release.set()
        holder.close()
        arriver.close()
    expect(wait.observed, "the withdrawal waited on the completion's account row lock")
    expect(completed.outcome == "applied" and withdrawn.outcome == "applied", "both applied")
    ctx.remember(other.account_id, intent)
    ctx.remember(other.account_id, withdrawal)
    expect(_profile_row(other.account_id).state == "incomplete", "the withdrawal demoted it")
    return f"{first}; {wait.summary()}"


@case("completion.removals_demote_and_empty_values_are_refused", "9", "D9")
def completion_removals(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store, staff

    def prepared(removal: str, paused: bool) -> Any:
        """A visible member (paused if asked) whose identity verification is a staff approval
        when the removal is its revocation, and the test's seed otherwise."""
        member = ctx.ready_member()
        seed_chart(member.account_id)
        if removal == "approval":
            switch = copy.deepcopy(settings_store.read_unlocked(ps.STAFF_APPROVAL).content)
            switch["enabled"] = True
            expect(ctx.publish(ps.STAFF_APPROVAL, switch).outcome == "applied", "switched on")
            approved = staff.approve_without_id(
                member.account_id, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
            )
            expect(approved.outcome == "applied", "approved")
            switch["enabled"] = False
            expect(ctx.publish(ps.STAFF_APPROVAL, switch).outcome == "applied", "switched off")
        else:
            seed_verified(member.account_id)
        expect(_edit(ctx, member)["visibility"] == "visible", f"{removal}: visible first")
        if paused:
            ctx.data(_visibility(ctx, member, "pause"), "own_profile", "paused")
        return member

    demoted = 0
    for removal in ("consent", "summary", "birth_input", "adult_rerun", "approval"):
        for paused in (False, True):
            member = prepared(removal, paused)
            born = ctx.get(member, ADULT, "own_age_state")["birth_date"]
            if removal == "consent":
                ctx.data(ctx.withdraw_onboarding(member), "onboarding", "withdrawn")
            elif removal == "summary":
                _edit(ctx, member, "")
            elif removal == "birth_input":
                ctx.data(ctx.birth_input(member, born, local_time="12:34:56"), "birth_input", "new")
            elif removal == "adult_rerun":
                ctx.refused(ctx.adult(member, years_ago(15)), 403, "forbidden", "failing rerun")
            else:
                revoked = staff.revoke_approval(
                    member.account_id, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
                )
                expect(revoked.outcome == "applied", "revoked")
            state = _profile_row(member.account_id).state
            wanted = "paused" if paused else "incomplete"
            expect(state == wanted, f"{removal}: {'stays paused' if paused else 'demoted'}")
            demoted += 1
    member = ctx.visible_member()
    profile = ctx.get(member, PROFILE, "own_profile")
    empty_name = ctx.command(
        member,
        PROFILE,
        {
            "operation": "profile",
            "meta": ctx.meta(profile["version"]),
            "display_name": "",
            "summary": "x",
        },
    )
    ctx.refused(empty_name, 400, "invalid_request", "an empty display name")
    for name in ("gender", "looking_for"):
        ctx.refused(ctx.field(member, name, []), 400, "invalid_request", f"an empty {name}")
    cleared = ctx.command(
        member,
        AREA,
        {"operation": "area", "meta": ctx.meta(profile["version"]), "area_id": None},
    )
    ctx.refused(cleared, 400, "invalid_request", "a cleared area")
    expect(_profile_row(member.account_id).state == "visible", "a refused edit changes nothing")
    return f"{demoted} removals demoted or left paused; four emptying edits refused"


# ---------------------------------------------------------------------------------------------
# Correction C1 (DM-54, Y3 to Y5): every requirement writer ends with D9's one recompute
# ---------------------------------------------------------------------------------------------


def _switch_staff_approval(ctx: ProfileContext, enabled: bool) -> None:
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store

    switch = copy.deepcopy(settings_store.read_unlocked(ps.STAFF_APPROVAL).content)
    if switch["enabled"] is not enabled:
        switch["enabled"] = enabled
        expect(ctx.publish(ps.STAFF_APPROVAL, switch).outcome == "applied", "switched")


def _new_onboarding_version(ctx: ProfileContext) -> str:
    """A new onboarding consent version, published as staff will (``consent.old_version_refused``
    does the same); every member's accepted version lapses without a write."""
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store

    content = copy.deepcopy(settings_store.read_unlocked(ps.ONBOARDING_CONSENT).content)
    content["text"] += f" (revision {uuid4().hex[:6]})"
    expect(ctx.publish(ps.ONBOARDING_CONSENT, content).outcome == "applied", "a new version")
    return str(settings_store.read_unlocked(ps.ONBOARDING_CONSENT).policy_version)


@case("completion.every_requirement_writer_meeting_the_last_one_makes_it_visible", "9", "D9")
def recompute_completes(ctx: ProfileContext) -> str:
    from glow_profiles import staff

    shown: list[str] = []

    def completed(member: Any, before: int, what: str) -> None:
        profile = _profile_row(member.account_id)
        expect(profile.state == "visible", f"{what}: the profile is visible")
        expect(ctx.missing(member) == [], f"{what}: nothing is missing")
        expect(_events(profile.pk, "profile_completed") == before + 1, f"{what}: profile_completed")
        shown.append(what)

    def incomplete(member: Any, what: str) -> int:
        profile = _profile_row(member.account_id)
        expect(profile.state == "incomplete", f"{what}: incomplete first")
        return _events(profile.pk, "profile_completed")

    # The profile edit (F04 owner complete): every other requirement met first.
    member = ctx.ready_member()
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    before = incomplete(member, "the profile edit")
    expect(ctx.missing(member) == [], "the seeds met the last two without a write")
    _edit(ctx, member)
    completed(member, before, "the profile edit")

    # A field (F04 owner complete): "looking for" is the last requirement.
    member = ctx.member()
    ctx.accept_onboarding(member)
    born = ctx.adult_date()
    ctx.data(ctx.adult(member, born), "own_age_state", "adult")
    ctx.data(ctx.birth_input(member, born), "birth_input", "birth")
    ctx.data(ctx.profile(member), "own_profile", "profile")
    ctx.data(ctx.field(member, "gender", ["woman"]), "own_profile_fields", "gender")
    ctx.data(ctx.area(member, NEW_YORK), "own_area", "area")
    # SV2 Stage B (D9): an approved photo, through Stage B's own path.
    ctx.approved_photo(member)
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    before = incomplete(member, "a field")
    expect(ctx.missing(member) == ["profile_fields"], "only the field is missing")
    ctx.data(ctx.field(member, "looking_for", ["casual"]), "own_profile_fields", "looking for")
    completed(member, before, "a field (looking for)")

    # A field that is no requirement still ends with the recompute (the sensitive fields): the
    # seeds met the last requirements without a write, and the orientation write completes it.
    ctx.ensure_test_lists()
    member = ctx.ready_member()
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    ctx.data(ctx.sensitive(member, "accepted"), "sensitive_consent", "the sensitive consent")
    before = incomplete(member, "orientation")
    ctx.data(
        ctx.field(member, "orientation", [ORIENTATION_VALUES[0]]), "own_profile_fields", "orient."
    )
    completed(member, before, "a field (orientation)")

    # The area (F04 owner complete).
    member = ctx.member()
    ctx.accept_onboarding(member)
    born = ctx.adult_date()
    ctx.data(ctx.adult(member, born), "own_age_state", "adult")
    ctx.data(ctx.birth_input(member, born), "birth_input", "birth")
    ctx.data(ctx.profile(member), "own_profile", "profile")
    ctx.data(ctx.field(member, "gender", ["man"]), "own_profile_fields", "gender")
    ctx.data(ctx.field(member, "looking_for", ["casual"]), "own_profile_fields", "looking for")
    ctx.approved_photo(member)
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    before = incomplete(member, "the area")
    expect(ctx.missing(member) == ["area"], "only the area is missing")
    ctx.data(ctx.area(member, LOS_ANGELES), "own_area", "the area")
    completed(member, before, "the area")

    # The onboarding consent's accept (F04 requirements_met, system).
    member = ctx.visible_member()
    ctx.data(ctx.withdraw_onboarding(member), "onboarding", "withdrawn")
    before = incomplete(member, "the onboarding consent")
    expect(ctx.missing(member) == ["consent"], "only the consent is missing")
    accepted = ctx.accept_onboarding(member)
    expect("profile" not in accepted["requirements"], "the read sees the profile visible")
    completed(member, before, "the onboarding consent's accept")

    # The adult check (F04 requirements_met): a failing rerun, the chart seeded again, then the
    # date that passed before.
    born = ctx.adult_date(31)
    member = ctx.visible_member(birth_date=born)
    ctx.refused(ctx.adult(member, years_ago(16)), 403, "forbidden", "a failing rerun")
    seed_chart(member.account_id)
    before = incomplete(member, "the adult check")
    expect(ctx.missing(member) == ["adult_check"], "only the adult check is missing")
    ctx.data(ctx.adult(member, born), "own_age_state", "the adult check passes again")
    completed(member, before, "the adult check")

    # Staff's approval without ID verification (F04 requirements_met).
    member = ctx.ready_member()
    seed_chart(member.account_id)
    before = incomplete(member, "the staff approval")
    expect(ctx.missing(member) == ["identity_verification"], "only verification is missing")
    _switch_staff_approval(ctx, True)
    approved = staff.approve_without_id(
        member.account_id, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
    )
    _switch_staff_approval(ctx, False)
    expect(approved.outcome == "applied", "approved")
    expect(approved.detail.get("profile") == "visible", "the operation reports it visible")
    completed(member, before, "the staff approval")

    # The birth input cannot meet the last requirement in Stage A: its new revision is pending,
    # so the chart is missing until P11's adapter resolves it (its recompute is shown demoting).
    member = ctx.ready_member()
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    born = ctx.get(member, ADULT, "own_age_state")["birth_date"]
    ctx.data(ctx.birth_input(member, born, local_time="07:31:45"), "birth_input", "a new one")
    expect(_profile_row(member.account_id).state == "incomplete", "a birth input never completes")
    expect(ctx.missing(member) == ["chart"], "its new revision's chart is missing")
    return f"{len(shown)} writers each made the profile visible: " + ", ".join(shown)


@case("completion.a_write_that_finds_a_requirement_missing_demotes", "9", "D9")
def recompute_demotes(ctx: ProfileContext) -> str:
    from glow_persistence.models import Profile
    from glow_profiles import staff

    by_area, by_field, by_adult, by_edit, by_accept = (ctx.visible_member() for _ in range(5))
    paused, restricted, removed = (ctx.visible_member() for _ in range(3))
    ctx.data(_visibility(ctx, paused, "pause"), "own_profile", "paused")
    outcome = staff.restrict_profile(
        restricted.account_id, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
    )
    expect(outcome.outcome == "applied", "restricted through glow_chat's writer")
    # Harness write: SV2 has no writer to removed (F18's deletion is P08's).
    Profile.objects.filter(account_id=removed.account_id).update(state="removed")
    current = _new_onboarding_version(ctx)
    # The requirement lapsed without a write: nothing moved yet.
    for member in (by_area, by_field, by_adult, by_edit, by_accept):
        expect(_profile_row(member.account_id).state == "visible", "a lapse alone moves nothing")
        expect(ctx.missing(member) == ["consent"], "the lapsed consent is missing")
    demotions = {
        member.account_id: 0 for member in (by_area, by_field, by_adult, by_edit, by_accept)
    }
    for account_id in demotions:
        demotions[account_id] = _events(_profile_row(account_id).pk, "profile_demoted")

    def demoted(member: Any, what: str, *, event: bool = True) -> None:
        profile = _profile_row(member.account_id)
        expect(profile.state == "incomplete", f"{what}: the visible profile is demoted")
        if event:
            expect(
                _events(profile.pk, "profile_demoted") == demotions[member.account_id] + 1,
                f"{what}: profile_demoted (requirement_removed)",
            )

    ctx.data(ctx.area(by_area, LOS_ANGELES), "own_area", "an area change")
    demoted(by_area, "the area")
    ctx.data(ctx.field(by_field, "gender", ["non-binary"]), "own_profile_fields", "a gender")
    demoted(by_field, "a field")
    born = ctx.get(by_adult, ADULT, "own_age_state")["birth_date"]
    ctx.data(ctx.adult(by_adult, born), "own_age_state", "the same date again")
    demoted(by_adult, "the adult check's unchanged date")
    # C2 (DM-55, section 6): the profile edit that finds a lapse it did not cause demotes as
    # requirement_removed, with profile_demoted, like every other writer.
    _edit(ctx, by_edit)
    demoted(by_edit, "the profile edit finding a lapse (requirement_removed)")
    # Accepting the new version is the last requirement again (F04 requirements_met): the member
    # is demoted first, so the acceptance is what completes the profile.
    ctx.data(ctx.area(by_accept, LOS_ANGELES), "own_area", "an area change, the consent lapsed")
    demoted(by_accept, "the area, before the acceptance")
    completions = _events(_profile_row(by_accept.account_id).pk, "profile_completed")
    accepted = ctx.accept_onboarding(by_accept)
    expect(accepted["policy_version"] == current, "the new version accepted")
    expect(_profile_row(by_accept.account_id).state == "visible", "accepting it completes")
    expect(
        _events(_profile_row(by_accept.account_id).pk, "profile_completed") == completions + 1,
        "the acceptance emits profile_completed",
    )
    ctx.data(ctx.area(by_accept, NEW_YORK), "own_area", "an area change, now current")
    expect(_profile_row(by_accept.account_id).state == "visible", "nothing missing: it stays")
    # paused, restricted and removed stay as they are.
    ctx.data(ctx.area(paused, LOS_ANGELES), "own_area", "a paused member's area change")
    expect(_profile_row(paused.account_id).state == "paused", "a paused profile stays paused")
    expect("consent" in ctx.missing(paused), "though the consent is missing")
    for member, state in ((restricted, "restricted"), (removed, "removed")):
        ctx.data(ctx.withdraw_onboarding(member), "onboarding", f"{state}: withdrawn")
        expect(_profile_row(member.account_id).state == state, f"{state}: stays {state}")
        ctx.accept_onboarding(member)
        expect(ctx.missing(member) == [], f"{state}: nothing missing")
        expect(_profile_row(member.account_id).state == state, f"{state}: still {state}")
    return (
        "a lapsed consent version demoted at the area, a field, the adult check and the edit,"
        " each with profile_demoted; its acceptance completed a demoted profile; paused,"
        " restricted and removed stayed"
    )


@case("birth.a_failing_date_is_refused_and_nothing_of_it_is_stored", "7", "8", "D7", "D8", "D9")
def birth_failing_date(ctx: ProfileContext) -> str:
    from glow_persistence.models import (
        AccountAgeState,
        BirthInput,
        EngineIdentity,
        IdempotencyRecord,
        OutboxEvent,
    )

    def snapshot(account_id: UUID) -> dict[str, Any]:
        mapping = EngineIdentity.objects.filter(account_id=account_id).first()
        age = AccountAgeState.objects.get(account_id=account_id)
        account = _account(account_id)
        profile = _profile_row(account_id)
        return {
            "inputs": [
                (str(row.pk), row.version, row.state)
                for row in BirthInput.objects.filter(account_id=account_id).order_by("version")
            ],
            "age": (age.state, age.birth_date, age.version),
            "account": (account.eligibility_version, account.version),
            "profile": (profile.state, profile.version),
            "mapping": None if mapping is None else (mapping.state, mapping.version),
            "events": OutboxEvent.objects.count(),
            "records": IdempotencyRecord.objects.filter(actor_id=account_id).count(),
        }

    results: list[str] = []
    for paused in (False, True):
        member = ctx.visible_member()
        account = member.account_id
        if paused:
            ctx.data(_visibility(ctx, member, "pause"), "own_profile", "paused")
        held = BirthInput.objects.filter(account_id=account).order_by("-version")[0]
        age_row = AccountAgeState.objects.get(account_id=account)
        profile = _profile_row(account)
        before = snapshot(account)
        counts = {
            "age": _events(age_row.pk, "age_state_changed"),
            "held": _events(held.pk, "birth_input_invalidated"),
            "demoted": _events(profile.pk, "profile_demoted"),
        }
        failing = years_ago(17, days=-123)
        place = f"Synthetic Failing Place {uuid4().hex[:8]}"
        body = ctx.birth_body(member, failing, local_time="02:47:19", place=place)
        ctx.refused(ctx.command(member, BIRTH, body), 403, "forbidden", "a failing birth date")
        # Nothing of it is stored.
        rows = BirthInput.objects.filter(account_id=account)
        expect(rows.count() == len(before["inputs"]), "no revision is written")
        expect(
            not BirthInput.objects.filter(birth_date=failing).exists()
            and not BirthInput.objects.filter(place_label=place).exists()
            and not rows.filter(local_time="02:47:19").exists(),
            "no row holds its date, time or place",
        )
        expect(_found_in_database((place, failing)) == [], "no table holds its place or date")
        expect(
            IdempotencyRecord.objects.filter(actor_id=account).count() == before["records"],
            "no idempotency record is stored",
        )
        # The failing rerun committed.
        age = AccountAgeState.objects.get(account_id=account)
        expect(age.state == "unknown" and age.birth_date is None, "the age state is unknown")
        expect(_events(age.pk, "age_state_changed") == counts["age"] + 1, "age_state_changed")
        held.refresh_from_db()
        expect(held.state == "missing", "the current birth input is missing")
        expect(
            _events(held.pk, "birth_input_invalidated") == counts["held"] + 1,
            "birth_input_invalidated",
        )
        mapping = EngineIdentity.objects.get(account_id=account)
        expect(
            mapping.state == "pending"
            and mapping.engine_reference is None
            and mapping.birth_input_id == held.pk,
            "its mapping is back to pending, at that revision",
        )
        state = _profile_row(account).state
        if paused:
            expect(state == "paused", "a paused profile stays paused")
            expect(_events(profile.pk, "profile_demoted") == counts["demoted"], "no demotion")
        else:
            expect(state == "incomplete", "the visible profile is incomplete")
            expect(_events(profile.pk, "profile_demoted") == counts["demoted"] + 1, "demoted")
        expect(_account(account).eligibility_version > before["account"][0], "eligibility bumped")
        read = ctx.get(member, BIRTH, "birth_input")
        expect(read["input_id"] == str(held.pk) and read["resolution"] == "missing", "owner read")
        expect(ctx.get(member, ADULT, "own_age_state")["birth_date"] is None, "no date read")
        # A retry of the same command, and a new one, is refused and changes nothing more.
        after = snapshot(account)
        ctx.refused(ctx.command(member, BIRTH, body), 403, "forbidden", "the same command again")
        expect(snapshot(account) == after, "the retry changes no row")
        again = ctx.birth_body(member, failing, local_time="02:47:19", place=place)
        ctx.refused(ctx.command(member, BIRTH, again), 403, "forbidden", "a new command")
        expect(snapshot(account) == after, "a new command changes no row")
        results.append("paused" if paused else "visible")
    return (
        "refused with nothing of it stored; the rerun committed (unknown, missing, pending,"
        f" demoted or left paused); retries changed nothing: {', '.join(results)}"
    )


# =============================================================================================
# Correction C2 (DM-55): the date first at both age writers, the history limit in two steps, the
# sensitive consent's current version, the profile edit's lapse, the account row lock, age_years
# =============================================================================================


def _age_snapshot(account_id: UUID) -> dict[str, Any]:
    """Every row a date's refusal could change, for one account."""
    from glow_persistence.models import (
        AccountAgeState,
        BirthInput,
        EngineIdentity,
        IdempotencyRecord,
        OutboxEvent,
    )

    mapping = EngineIdentity.objects.filter(account_id=account_id).first()
    age = AccountAgeState.objects.get(account_id=account_id)
    account = _account(account_id)
    profile = _profile_row(account_id)
    return {
        "inputs": [
            (str(row.pk), row.version, row.state)
            for row in BirthInput.objects.filter(account_id=account_id).order_by("version")
        ],
        "age": (age.state, age.birth_date, age.version),
        "account": (account.eligibility_version, account.version),
        "profile": (profile.state, profile.version),
        "mapping": None if mapping is None else (mapping.state, mapping.version),
        "events": OutboxEvent.objects.count(),
        "records": IdempotencyRecord.objects.filter(actor_id=account_id).count(),
    }


def _expect_reset(ctx: ProfileContext, member: Any, before: dict[str, Any], what: str) -> None:
    """D7 (DM-55, Z2): a date under 18 from a self-declared adult reset the account, stored no
    idempotency record, and nothing of the date; a retry is refused and changes nothing."""
    from glow_persistence.models import AccountAgeState, BirthInput, EngineIdentity

    account = member.account_id
    age = AccountAgeState.objects.get(account_id=account)
    expect(age.state == "unknown" and age.birth_date is None, f"{what}: the age state is unknown")
    held = BirthInput.objects.filter(account_id=account).order_by("-version")[0]
    expect(held.state == "missing", f"{what}: the current birth input is missing")
    expect(
        [row[0] for row in _age_snapshot(account)["inputs"]] == [r[0] for r in before["inputs"]],
        f"{what}: no revision is written",
    )
    mapping = EngineIdentity.objects.filter(account_id=account).first()
    expect(
        mapping is None or (mapping.state == "pending" and mapping.engine_reference is None),
        f"{what}: its mapping is back to pending",
    )
    profile = _profile_row(account)
    expect(profile.state == "incomplete", f"{what}: the visible profile is incomplete")
    for aggregate, event, wanted in (
        (age.pk, "age_state_changed", before["counts"]["age"] + 1),
        (held.pk, "birth_input_invalidated", before["counts"]["held"] + 1),
        (profile.pk, "profile_demoted", before["counts"]["demoted"] + 1),
    ):
        expect(_events(aggregate, event) == wanted, f"{what}: {event}")
    after = _age_snapshot(account)
    expect(after["records"] == before["records"], f"{what}: no idempotency record is stored")
    expect(after["account"][0] > before["account"][0], f"{what}: eligibility_version bumped")


def _counted(member: Any) -> dict[str, Any]:
    from glow_persistence.models import AccountAgeState, BirthInput

    account = member.account_id
    snapshot = _age_snapshot(account)
    held = BirthInput.objects.filter(account_id=account).order_by("-version")[0]
    snapshot["counts"] = {
        "age": _events(AccountAgeState.objects.get(account_id=account).pk, "age_state_changed"),
        "held": _events(held.pk, "birth_input_invalidated"),
        "demoted": _events(_profile_row(account).pk, "profile_demoted"),
    }
    return snapshot


@case("adult.a_self_declared_adults_date_comes_first_at_both_writers", "7", "8", "D7", "D8")
def adult_date_first(ctx: ProfileContext) -> str:
    future, minor = years_ago(-1), years_ago(17, days=-45)

    def adult_body(member: Any, born: str, expected: int | None = None) -> dict[str, Any]:
        if expected is None:
            expected = ctx.get(member, ADULT, "own_age_state")["version"]
        ctx.values.add(born)
        return {"operation": "adult_check", "meta": ctx.meta(expected), "birth_date": born}

    shown: list[str] = []
    # A future date, at each writer: 400, and no row changes.
    for writer in ("the eligibility step", "the birth input"):
        member = ctx.visible_member()
        before = _age_snapshot(member.account_id)
        if writer == "the eligibility step":
            reply = ctx.command(member, ADULT, adult_body(member, future))
        else:
            reply = ctx.command(member, BIRTH, ctx.birth_body(member, future))
        ctx.refused(reply, 400, "invalid_request", f"{writer}: a future date")
        expect(
            _age_snapshot(member.account_id) == before, f"{writer}: a future date changes nothing"
        )
        shown.append(f"future at {writer}")
    # A date under 18, at each writer, alone and behind each of the request's other refusals:
    # 403, with the reset committed, no idempotency record, and a retry refused that changes
    # nothing more.
    plans: list[tuple[str, Callable[[Any], dict[str, Any]], str]] = [
        ("the eligibility step", lambda m: adult_body(m, minor), ADULT),
        ("the eligibility step behind a stale version", lambda m: adult_body(m, minor, 99), ADULT),
        ("the birth input", lambda m: ctx.birth_body(m, minor), BIRTH),
        (
            "the birth input behind a stale version",
            lambda m: ctx.birth_body(m, minor, expected=99),
            BIRTH,
        ),
        (
            "the birth input behind a birth time not given",
            lambda m: ctx.birth_body(m, minor, local_time=None, precision="unknown"),
            BIRTH,
        ),
    ]
    for what, make, path in plans:
        member = ctx.visible_member()
        before = _counted(member)
        body = make(member)
        ctx.refused(ctx.command(member, path, body), 403, "forbidden", what)
        _expect_reset(ctx, member, before, what)
        settled = _age_snapshot(member.account_id)
        ctx.refused(ctx.command(member, path, body), 403, "forbidden", f"{what}: the retry")
        expect(_age_snapshot(member.account_id) == settled, f"{what}: the retry changes nothing")
        again = make(member) if path == BIRTH else adult_body(member, minor)
        ctx.refused(ctx.command(member, path, again), 403, "forbidden", f"{what}: a new command")
        expect(_age_snapshot(member.account_id) == settled, f"{what}: a new command, nothing")
        shown.append(what)
    # Behind a lapsed onboarding consent (a new version, published last: it lapses every member).
    member = ctx.visible_member()
    _new_onboarding_version(ctx)
    before = _counted(member)
    what = "the birth input behind a lapsed onboarding consent"
    ctx.refused(ctx.command(member, BIRTH, ctx.birth_body(member, minor)), 403, "forbidden", what)
    _expect_reset(ctx, member, before, what)
    shown.append(what)
    # An unknown account: the existing refusals hold, and nothing changes.
    from glow_persistence.models import AccountAgeState, OutboxEvent

    stranger = ctx.member()
    ctx.accept_onboarding(stranger)
    # Each check's label names the date's kind, never the date (C3, finding 3).
    for born, status, code, what in (
        (future, 400, "invalid_request", "an unknown account's future date"),
        (minor, 403, "forbidden", "an unknown account's date under 18"),
    ):
        age = AccountAgeState.objects.get(account_id=stranger.account_id)
        events_before = OutboxEvent.objects.count()
        ctx.refused(ctx.command(stranger, ADULT, adult_body(stranger, born)), status, code, what)
        again = AccountAgeState.objects.get(account_id=stranger.account_id)
        expect(
            (again.state, again.birth_date, again.version) == ("unknown", None, age.version),
            "an unknown account's state is unchanged",
        )
        ctx.refused(
            ctx.command(stranger, BIRTH, ctx.birth_body(stranger, born, expected=0)),
            403,
            "forbidden",
            "the birth input's adult-check gate",
        )
        expect(OutboxEvent.objects.count() == events_before, "no event for an unknown account")
    return "; ".join(shown) + "; an unknown account's refusals hold"


@case("settings.history_limit_not_crossed_in_two_publications", "1", "D2")
def settings_history_two_steps(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store

    history = copy.deepcopy(settings_store.read_unlocked(ps.HISTORY).content)
    if history["own_pause"] != "hidden":
        history["own_pause"] = "hidden"
        expect(ctx.publish(ps.HISTORY, history).outcome == "applied", "a cause made hidden")
    label = history["consent_policy_version"]
    current = _new_onboarding_version(ctx)
    expect(current != label, "a newer onboarding version than the one the setting names")
    # The first step of the two: the label alone moves. Refused, and nothing is written.
    relabelled = dict(copy.deepcopy(history), consent_policy_version=current)
    before = _counts()
    refused = ctx.publish(ps.HISTORY, relabelled)
    expect(refused.outcome == "refused", "the label alone cannot move")
    expect(ps.MORE_READABLE_NEEDS_CONSENT in refused.reason, "the refusal names the limit")
    expect(_counts() == before, "the first step writes nothing")
    # The direct change: more readable under the version already named. Still refused.
    direct = dict(copy.deepcopy(history), own_pause="read_only")
    refused = ctx.publish(ps.HISTORY, direct)
    expect(refused.outcome == "refused", "the direct change is refused")
    expect(_counts() == before, "the direct change writes nothing")
    # A new onboarding version, then a more readable change naming it: allowed.
    allowed = dict(copy.deepcopy(history), own_pause="read_only", consent_policy_version=current)
    expect(ctx.publish(ps.HISTORY, allowed).outcome == "applied", "the change naming it applies")
    return "the two-step path is refused at its first step; the new version then allows it"


@case("fields.sensitive_needs_the_current_consent_version", "2", "3", "6", "D3", "D6")
def fields_sensitive_version(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store

    ctx.ensure_test_lists()
    member = ctx.ready_member()
    saves: list[tuple[str, Callable[[], Any]]] = [
        ("a sensitive value", lambda: ctx.field(member, "orientation", [ORIENTATION_VALUES[1]])),
        (
            "orientation's own words",
            lambda: ctx.field(
                member, "orientation", ["not-stated"], own_words=f"Own {uuid4().hex[:6]}"
            ),
        ),
        ("a narrowed sensitive set", lambda: ctx.sets(member, {"relationship_status": ["single"]})),
    ]

    def all_refused(when: str) -> None:
        for what, save in saves:
            ctx.refused(save(), 403, "forbidden", f"{what} {when}")

    all_refused("before the consent is accepted")
    ctx.data(ctx.sensitive(member, "accepted"), "sensitive_consent", "accepted")
    ctx.data(ctx.sensitive(member, "withdrawn"), "sensitive_consent", "withdrawn")
    all_refused("after its withdrawal")
    accepted = ctx.data(ctx.sensitive(member, "accepted"), "sensitive_consent", "accepted again")
    content = copy.deepcopy(settings_store.read_unlocked(ps.SENSITIVE_CONSENT).content)
    content["text"] += f" (revision {uuid4().hex[:6]})"
    expect(ctx.publish(ps.SENSITIVE_CONSENT, content).outcome == "applied", "a new version")
    current = ctx.catalog(member)["consents"]["sensitive_profile"]["policy_version"]
    expect(current != accepted["policy_version"], "the accepted version is now an old one")
    all_refused("at an old version")
    # A save that carries no sensitive data still succeeds at an old version.
    ctx.data(ctx.field(member, "gender", ["man"]), "own_profile_fields", "gender, old version")
    ctx.data(ctx.sets(member, {"gender": ["woman"]}), "own_preferences", "a set, old version")
    ctx.data(ctx.field(member, "orientation", ["not-stated"]), "own_profile_fields", "left unset")
    # Accepting the current version (F02 accept_sensitive from accepted) allows each again.
    renewed = ctx.data(ctx.sensitive(member, "accepted"), "sensitive_consent", "the current one")
    expect(renewed["policy_version"] == current, "the current version accepted")
    for what, save in saves:
        reply = save()
        expect(reply.status == 200, f"{what} at the current version: answers 200")
    return "each sensitive save refused before acceptance, after withdrawal and at an old version"


@case("completion.the_profile_edit_is_the_owners_edit_only_when_it_clears_the_summary", "9", "D9")
def profile_edit_entries(ctx: ProfileContext) -> str:
    clearer, finder, both = (ctx.visible_member() for _ in range(3))

    def counts(member: Any) -> tuple[int, int, int, int]:
        profile = _profile_row(member.account_id)
        return (
            int(profile.version),
            int(_account(member.account_id).eligibility_version),
            _events(profile.pk, "profile_demoted"),
            _events(profile.pk, "profile_edited"),
        )

    def check(member: Any, summary: str, bumps: int, demoted: int, what: str) -> None:
        version, eligibility, demotions, edits = counts(member)
        _edit(ctx, member, summary)
        after = counts(member)
        expect(_profile_row(member.account_id).state == "incomplete", f"{what}: demoted")
        expect(after[0] == version + bumps, f"{what}: the profile's version bumped {bumps}")
        expect(after[1] == eligibility + bumps, f"{what}: eligibility_version bumped {bumps}")
        expect(after[2] == demotions + demoted, f"{what}: profile_demoted {demoted}")
        expect(after[3] == edits + 1, f"{what}: the edit's own profile_edited")

    # The edit that clears the summary: the owner's edit, riding on the edit's own write.
    check(clearer, "", 1, 0, "the cleared summary")
    _new_onboarding_version(ctx)
    # A lapse the edit finds but did not cause: requirement_removed, a transition of its own.
    check(finder, "A synthetic member, edited.", 2, 1, "a lapse the edit found")
    # Clearing the summary while another requirement has lapsed: still the owner's edit.
    check(both, "", 1, 0, "the cleared summary beside a lapse")
    return (
        "edit when the edit clears the summary, whatever else is missing; else requirement_removed"
    )


@case("completion.a_second_writer_waits_for_the_account_row_lock", "9", "D9")
def account_row_lock(ctx: ProfileContext) -> str:
    from django.db import DatabaseError, transaction
    from glow_domain.chat import TransactionProbe
    from glow_persistence.models import Profile
    from glow_profiles import operations

    from glow_ordering_proof.concurrency import Hold, PidSlot, Worker
    from glow_ordering_proof.observe import observe_lock_wait

    member = ctx.ready_member()
    catalog = ctx.catalog(member)
    filters = ctx.get(member, FILTERS, "own_filters")
    holding = {
        "operation": "filters",
        "meta": ctx.meta(filters["version"]),
        "policy_version": catalog["policy_version"],
        "minimum_age": 21,
        "maximum_age": None,
        "distance_choice": "anywhere",
    }
    profile = ctx.get(member, PROFILE, "own_profile")
    arriving = {"operation": "area", "meta": ctx.meta(profile["version"]), "area_id": LOS_ANGELES}
    passed = threading.Event()

    def profile_row_free() -> bool:
        try:
            with transaction.atomic():
                rows = Profile.objects.select_for_update(nowait=True)
                list(rows.filter(account_id=member.account_id))
        except DatabaseError:
            return False
        return True

    # Two SV2 writers of one account whose own rows are disjoint (the preferences; the profile):
    # only the account row lock orders them.
    holder, arriver, prober = Worker("filters-holder"), Worker("area-arriver"), Worker("prober")
    try:
        hold, slot = Hold(), PidSlot()
        probe = TransactionProbe(on_begin=slot.set, before_commit=hold.point)
        held = holder.submit(
            lambda: operations.set_filters(member.account_id, holding, probe=probe)
        )
        expect(hold.wait_held(), "the first writer holds the account row")
        arriver_pid = arriver.run(_backend_pid)
        moving = arriver.submit(
            lambda: operations.set_area(
                member.account_id, arriving, probe=TransactionProbe(after_first_lock=passed.set)
            )
        )
        wait = observe_lock_wait(arriver_pid, holder_pid=slot.wait(), finished=moving.done)
        waiting_at_first_lock = wait.observed and not moving.done() and not passed.is_set()
        free = prober.run(profile_row_free) if wait.observed and not moving.done() else None
        hold.release.set()
        first = held.result(timeout=30)
        second = moving.result(timeout=30)
    finally:
        hold.release.set()
        holder.close()
        arriver.close()
        prober.close()
    expect(wait.observed, "the second writer waited on the first's lock")
    expect(waiting_at_first_lock, "it waited at the account row, before passing its first lock")
    expect(free is True, "while it waited it held no lock on its own row: the account first")
    expect(first.outcome == "applied" and second.outcome == "applied", "both applied, in order")
    expect(passed.is_set(), "it passed the account row once the first committed")
    ctx.remember(member.account_id, holding)
    ctx.remember(member.account_id, arriving)
    return wait.summary()


@case("adult.age_years_is_whole_years_never_the_date", "7", "D4", "D7")
def adult_age_years(ctx: ProfileContext) -> str:
    from datetime import date

    from glow_domain.identity import AccountId
    from glow_identity.age import OrmAgeAssurance

    member = ctx.member()
    account = AccountId(str(member.account_id))
    port = OrmAgeAssurance()
    today = db_today()
    expect(port.age_years(account, today) is None, "None while the state is unknown")
    for born, years in ((years_ago(30, days=1), 29), (years_ago(30), 30), (years_ago(18), 18)):
        ctx.data(ctx.adult(member, born), "own_age_state", "a passing date")
        found = port.age_years(account, today)
        expect(type(found) is int, "an integer, never the date")
        expect(not isinstance(found, date), "never a date")
        # The label names no age (C3, finding 3: no check's label holds a member value).
        expect(found == years, "whole years, as the date gives them")
    return "whole years for a self-declared adult, None while unknown; an integer, never the date"


# =============================================================================================
# The schema's own refusals (the P11 plan's DB04, for SV2's tables: migration 0005's constraints
# and, since SV2 Stage B's correction C2, migration 0008's)
# =============================================================================================


@case("constraints.malformed_direct_writes_are_refused", "D2", "D3", "D4", "D5", "D6", "D7", "D18")
def constraints_refuse(ctx: ProfileContext) -> str:
    """A direct write no SV2 writer makes, against each constraint migration 0005 declares, is
    refused by PostgreSQL itself, naming that constraint, and leaves nothing behind. Harness
    writes only; the error's text is read for the constraint's name and never kept."""
    from django.db import IntegrityError, transaction
    from django.utils import timezone
    from glow_persistence.models import (
        AccountAgeState,
        Area,
        ConsentDecision,
        IdentityVerification,
        Preferences,
        PreferenceSetEntry,
        Profile,
        ProfileFieldChoice,
        SettingVersion,
    )

    member, newcomer = ctx.ready_member(), ctx.member()
    account, other = member.account_id, newcomer.account_id
    now = timezone.now()

    def snapshot() -> tuple[Any, ...]:
        return (
            SettingVersion.objects.count(),
            ConsentDecision.objects.count(),
            Area.objects.count(),
            ProfileFieldChoice.objects.count(),
            PreferenceSetEntry.objects.count(),
            IdentityVerification.objects.count(),
            tuple(
                Preferences.objects.filter(account_id=account)
                .values_list("minimum_age", "maximum_age")
                .get()
            ),
            tuple(
                AccountAgeState.objects.filter(account_id=other)
                .values_list("state", "birth_date")
                .get()
            ),
            tuple(
                ProfileFieldChoice.objects.filter(account_id=account, field="looking_for")
                .values_list("own_words", "shown")
                .get()
            ),
            Profile.objects.filter(account_id=account).values_list("area_id", flat=True).get(),
        )

    writes: list[tuple[str, Callable[[], Any]]] = [
        (
            "setting_version_positive",
            lambda: SettingVersion.objects.create(
                name="profile.gender",
                number=0,
                content={},
                published_at=now,
                staff_subject=STAFF,
                reason="SV2-proof",
            ),
        ),
        (
            "setting_version_number",
            lambda: SettingVersion.objects.create(
                name="profile.gender",
                number=1,
                content={},
                published_at=now,
                staff_subject=STAFF,
                reason="SV2-proof",
            ),
        ),
        (
            "age_state_birth_date",
            lambda: AccountAgeState.objects.filter(account_id=other).update(birth_date=now.date()),
        ),
        (
            "consent_purpose",
            lambda: ConsentDecision.objects.create(
                account_id=account,
                purpose="fixture-purpose",
                policy_version="fixture.v1",
                state="accepted",
                decided_at=now,
                version=99,
            ),
        ),
        (
            "area_internal_point",
            lambda: Area.objects.create(
                area_id="99999", name="Fixture Area", latitude="91.000000", longitude="0.000000"
            ),
        ),
        (
            "preferences_age_floor",
            lambda: Preferences.objects.filter(account_id=account).update(minimum_age=17),
        ),
        (
            "preferences_age_range",
            lambda: Preferences.objects.filter(account_id=account).update(
                minimum_age=30, maximum_age=29
            ),
        ),
        (
            "profile_field_choice",
            lambda: ProfileFieldChoice.objects.create(
                account_id=account, field="gender", value_ids=["woman"], setting_version=1
            ),
        ),
        (
            "profile_field_name",
            lambda: ProfileFieldChoice.objects.create(
                account_id=other, field="fixture-field", value_ids=["woman"], setting_version=1
            ),
        ),
        (
            "profile_field_own_words",
            lambda: ProfileFieldChoice.objects.filter(
                account_id=account, field="looking_for"
            ).update(own_words="Fixture words"),
        ),
        (
            "profile_field_shown",
            lambda: ProfileFieldChoice.objects.filter(
                account_id=account, field="looking_for"
            ).update(shown=False),
        ),
        (
            "preference_set_not_stated",
            lambda: PreferenceSetEntry.objects.create(
                account_id=account, field="orientation", value_id="not-stated"
            ),
        ),
        (
            "preference_set_value",
            lambda: PreferenceSetEntry.objects.create(
                account_id=account, field="gender", value_id="all"
            ),
        ),
        (
            "identity_verification_provenance",
            lambda: IdentityVerification.objects.create(
                account_id=account, state="verified", method="automated_check", decided_at=now
            ),
        ),
        (
            "identity_verification_provenance",
            lambda: IdentityVerification.objects.create(
                account_id=other, state="staff_approved", method="staff_approval", decided_at=now
            ),
        ),
        (
            # Django names a foreign key's constraint by a hash; the error names its kind.
            "violates foreign key constraint",
            lambda: Profile.objects.filter(account_id=account).update(area_id=uuid4()),
        ),
        (
            "violates foreign key constraint",
            lambda: PreferenceSetEntry.objects.create(
                account_id=uuid4(), field="gender", value_id="all"
            ),
        ),
        # Each new model's version and state checks, and the rest of its own checks: each
        # write breaks one constraint only (PostgreSQL tests CHECK constraints in name order).
        (
            "glow_persistence_area_version",
            lambda: Area.objects.create(
                area_id="99998",
                name="Fixture Area",
                latitude="10.000000",
                longitude="10.000000",
                version=0,
            ),
        ),
        (
            "glow_persistence_settingversion_version",
            lambda: SettingVersion.objects.create(
                name="profile.gender",
                number=99,
                content={},
                published_at=now,
                staff_subject=STAFF,
                reason="SV2-proof",
                version=0,
            ),
        ),
        (
            "glow_persistence_identityverification_version",
            lambda: IdentityVerification.objects.create(account_id=other, version=0),
        ),
        (
            "glow_persistence_identityverification_state",
            lambda: IdentityVerification.objects.create(account_id=other, state="fixture-state"),
        ),
        (
            "glow_persistence_preferencesetentry_version",
            lambda: PreferenceSetEntry.objects.create(
                account_id=account, field="gender", value_id="man", version=0
            ),
        ),
        (
            "preference_set_field",
            lambda: PreferenceSetEntry.objects.create(
                account_id=account, field="fixture-field", value_id="man"
            ),
        ),
        (
            "glow_persistence_profilefieldchoice_version",
            lambda: ProfileFieldChoice.objects.create(
                account_id=other,
                field="orientation",
                value_ids=["not-stated"],
                setting_version=1,
                version=0,
            ),
        ),
        (
            "profile_field_setting_version",
            lambda: ProfileFieldChoice.objects.create(
                account_id=other, field="gender", value_ids=["woman"], setting_version=0
            ),
        ),
    ]
    # Every constraint migration 0005 declares has its write here.
    import importlib

    from django.db.migrations.operations.models import AddConstraint, CreateModel

    schema = importlib.import_module("glow_persistence.migrations.0005_profiles_settings")
    declared = {
        operation.constraint.name
        for operation in schema.Migration.operations
        if isinstance(operation, AddConstraint)
    } | {
        constraint.name
        for operation in schema.Migration.operations
        if isinstance(operation, CreateModel)
        for constraint in operation.options.get("constraints", [])
    }
    covered = {constraint for constraint, _ in writes}
    expect(declared <= covered, "a write for every constraint migration 0005 declares")
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
    return (
        f"{len(writes)} malformed direct writes refused by PostgreSQL, each by its constraint:"
        f" all {len(declared)} that migration 0005 declares, and two foreign keys"
    )


# The unique keys, foreign keys and column checks PostgreSQL holds on migration 0008's two new
# tables beyond the constraints it declares, by table, kind and (first) column. Django names them
# itself; the case reads each name from the catalog. Django's ``version >= 0`` column checks are
# shadowed by 0008's own ``version >= 1``, so they are held here but have no write of their own.
ASSETS_TABLE = "glow_persistence_mediaasset"
OBJECTS_TABLE = "glow_persistence_mediaobject"
GRANTS_TABLE = "glow_persistence_mediauploadgrant"
MEDIA_CATALOG = {
    (OBJECTS_TABLE, "u", "key"),
    (OBJECTS_TABLE, "f", "asset_id"),
    (OBJECTS_TABLE, "c", "byte_size"),
    (OBJECTS_TABLE, "c", "version"),
    (GRANTS_TABLE, "u", "grant_ref"),
    (GRANTS_TABLE, "u", "object_key"),
    (GRANTS_TABLE, "u", "asset_id"),
    (GRANTS_TABLE, "f", "asset_id"),
    (GRANTS_TABLE, "f", "account_id"),
    (GRANTS_TABLE, "c", "version"),
}
SHADOWED = {(OBJECTS_TABLE, "c", "version"), (GRANTS_TABLE, "c", "version")}


@case("constraints.malformed_media_writes_are_refused", "10", "D10")
def constraints_media(ctx: ProfileContext) -> str:
    """SV2 Stage B, correction C2 (the exact-head review's F5): a direct write no SV2 writer
    makes, against each constraint migration 0008 declares, and against each unique key, foreign
    key and column check PostgreSQL holds on 0008's two new tables, is refused by PostgreSQL
    itself, naming that constraint, and leaves nothing behind. Each write breaks one constraint
    only. Harness writes only; the error's text is read for the constraint's name and never
    kept."""
    import importlib
    from datetime import timedelta

    from django.db import IntegrityError, connection, transaction
    from django.db.migrations.operations.models import AddConstraint, CreateModel
    from django.db.models import F
    from django.utils import timezone
    from glow_persistence.models import MediaAsset, MediaObject, MediaUploadGrant

    member = ctx.member()
    approved = UUID(ctx.approved_photo(member))
    pending = UUID(ctx.request_upload(member)["asset_id"])
    issued = MediaUploadGrant.objects.get(asset_id=approved)
    original = MediaObject.objects.get(asset_id=approved, role="original")
    now = timezone.now()
    expect(
        MediaObject.objects.filter(asset_id=approved, role="variant").count() == 1,
        "the approved photo has one variant",
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT rel.relname, con.contype, att.attname, con.conname"
            " FROM pg_constraint con"
            " JOIN pg_class rel ON rel.oid = con.conrelid"
            " JOIN pg_attribute att"
            " ON att.attrelid = con.conrelid AND att.attnum = con.conkey[1]"
            " WHERE rel.relname IN (%s, %s, %s) AND con.contype IN ('u', 'f', 'c')",
            [ASSETS_TABLE, OBJECTS_TABLE, GRANTS_TABLE],
        )
        rows = cursor.fetchall()
    schema = importlib.import_module("glow_persistence.migrations.0008_media_lifecycle")
    declared = {
        operation.constraint.name
        for operation in schema.Migration.operations
        if isinstance(operation, AddConstraint)
    } | {
        constraint.name
        for operation in schema.Migration.operations
        if isinstance(operation, CreateModel)
        for constraint in operation.options.get("constraints", [])
    }
    others = [row for row in rows if row[0] != ASSETS_TABLE and row[3] not in declared]
    catalog = {(table, kind, column): conname for table, kind, column, conname in others}
    expect(len(catalog) == len(others), "one catalog name for each table, kind and column")
    expect(
        set(catalog) == MEDIA_CATALOG, "the catalog holds the unique keys, foreign keys and checks"
    )
    expect(
        {row[3] for row in rows} >= declared - {"media_one_original"},
        "the catalog holds every check migration 0008 declares (its partial unique is an index)",
    )

    def grant(asset_id: UUID) -> Any:
        return MediaUploadGrant.objects.filter(asset_id=asset_id)

    def variant() -> Any:
        return MediaObject.objects.filter(asset_id=approved, role="variant")

    writes: list[tuple[str, Callable[[], Any]]] = [
        (
            "media_delivery_only_approved",
            lambda: MediaAsset.objects.filter(pk=pending).update(
                approved_variant_ref="delivery-fixture"
            ),
        ),
        (
            "media_approved_unrevoked",
            lambda: MediaAsset.objects.filter(pk=approved).update(restriction_ref=uuid4()),
        ),
        (
            "media_removal_record",
            lambda: MediaAsset.objects.filter(pk=pending).update(state="removal_pending"),
        ),
        (
            "media_seam_passed",
            lambda: MediaAsset.objects.filter(pk=approved).update(detection=None),
        ),
        (
            "glow_persistence_mediaobject_version",
            lambda: MediaObject.objects.filter(asset_id=pending).update(version=0),
        ),
        (
            "media_object_role",
            lambda: MediaObject.objects.create(asset_id=pending, role="fixture-role", key=md_key()),
        ),
        (
            "media_object_opaque_key",
            lambda: MediaObject.objects.create(
                asset_id=pending, role="variant", key="Fixture-Key-Not-Hex"
            ),
        ),
        ("media_object_adoption_evidence", lambda: variant().update(adopted_at=now)),
        (
            "media_one_original",
            lambda: MediaObject.objects.create(asset_id=approved, role="original", key=md_key()),
        ),
        ("glow_persistence_mediauploadgrant_version", lambda: grant(pending).update(version=0)),
        ("media_grant_expiry", lambda: grant(pending).update(expires_at=F("issued_at"))),
        (
            "media_grant_used_in_time",
            lambda: grant(pending).update(used_at=F("expires_at") + timedelta(seconds=1)),
        ),
        (
            "media_grant_opaque_key",
            lambda: grant(pending).update(object_key="Fixture-Key-Not-Hex"),
        ),
        (
            catalog[(OBJECTS_TABLE, "u", "key")],
            lambda: MediaObject.objects.create(asset_id=pending, role="variant", key=original.key),
        ),
        (
            catalog[(OBJECTS_TABLE, "f", "asset_id")],
            lambda: MediaObject.objects.filter(asset_id=pending).update(asset_id=uuid4()),
        ),
        (catalog[(OBJECTS_TABLE, "c", "byte_size")], lambda: variant().update(byte_size=-1)),
        (
            catalog[(GRANTS_TABLE, "u", "grant_ref")],
            lambda: grant(pending).update(grant_ref=issued.grant_ref),
        ),
        (
            catalog[(GRANTS_TABLE, "u", "object_key")],
            lambda: grant(pending).update(object_key=issued.object_key),
        ),
        (
            catalog[(GRANTS_TABLE, "u", "asset_id")],
            lambda: grant(pending).update(asset_id=approved),
        ),
        (
            catalog[(GRANTS_TABLE, "f", "asset_id")],
            lambda: grant(pending).update(asset_id=uuid4()),
        ),
        (
            catalog[(GRANTS_TABLE, "f", "account_id")],
            lambda: grant(pending).update(account_id=uuid4()),
        ),
    ]
    covered = {constraint for constraint, _ in writes}
    expect(declared <= covered, "a write for every constraint migration 0008 declares")
    expect(
        {catalog[entry] for entry in MEDIA_CATALOG - SHADOWED} <= covered,
        "a write for every other unique key, foreign key and column check of its tables",
    )
    assets = [approved, pending]

    def snapshot() -> tuple[Any, ...]:
        return (
            MediaAsset.objects.count(),
            MediaObject.objects.count(),
            MediaUploadGrant.objects.count(),
            tuple(
                MediaAsset.objects.filter(pk__in=assets)
                .order_by("pk")
                .values_list(
                    "state", "approved_variant_ref", "restriction_ref", "detection", "version"
                )
            ),
            tuple(
                MediaObject.objects.filter(asset_id__in=assets)
                .order_by("key")
                .values_list("asset_id", "role", "key", "version", "byte_size", "adopted_at")
            ),
            tuple(
                MediaUploadGrant.objects.filter(asset_id__in=assets)
                .order_by("grant_ref")
                .values_list(
                    "asset_id",
                    "account_id",
                    "grant_ref",
                    "object_key",
                    "version",
                    "expires_at",
                    "used_at",
                )
            ),
        )

    before = snapshot()
    for constraint, write in writes:
        named = False
        try:
            with transaction.atomic():
                write()
        except IntegrityError as error:
            named = f'constraint "{constraint}"' in str(error)
        expect(named, f"PostgreSQL refuses the write by {constraint}")
    expect(snapshot() == before, "the refused writes leave nothing behind")
    return (
        f"{len(writes)} malformed direct writes refused by PostgreSQL, each by its constraint:"
        f" all {len(declared)} that migration 0008 declares, and {len(writes) - len(declared)}"
        " unique keys, foreign keys and column checks of its two tables"
    )


# =============================================================================================
# Acceptance check 11: ownership, authentication and versions (D11, D17)
# =============================================================================================


@case("ownership.every_route_refuses_strangers_and_stale_versions", "11", "D11", "D17")
def ownership(ctx: ProfileContext) -> str:
    owner, stranger = ctx.ready_member(), ctx.ready_member()
    paths = (
        PROFILE,
        COMPLETION,
        FIELDS,
        PREFERENCES,
        FILTERS,
        AREA,
        CATALOG,
        CONSENT,
        SENSITIVE,
        ADULT,
        BIRTH,
    )
    for path in paths:
        ctx.refused(ctx.call(owner, "GET", path, bearer=False), 401, "unauthenticated", path)
    for path in (
        PROFILE,
        VISIBILITY,
        FIELDS,
        PREFERENCES,
        FILTERS,
        AREA,
        NEAREST,
        CONSENT,
        SENSITIVE,
        ADULT,
        BIRTH,
    ):
        ctx.refused(ctx.call(owner, "POST", path, {}, bearer=False), 401, "unauthenticated", path)
    ctx.refused(ctx.call(owner, "GET", PROFILE, bearer="not-a-token"), 401, "unauthenticated", "x")
    theirs = ctx.get(stranger, PROFILE, "own_profile")["profile_id"]
    ctx.refused(ctx.call(owner, "GET", f"{PROFILE}/{theirs}"), 404, "not_found", "their profile")
    mine = ctx.get(owner, PROFILE, "own_profile")["profile_id"]
    expect(ctx.get(owner, f"{PROFILE}/{mine}", "own_profile")["profile_id"] == mine, "own by ID")
    their_birth = ctx.get(stranger, BIRTH, "birth_input")["input_id"]
    ctx.refused(ctx.call(owner, "GET", f"{BIRTH}/{their_birth}"), 404, "not_found", "their input")
    # A stale version on every command route.
    catalog = ctx.catalog(owner)
    stale = {"idempotency_key": ctx.key(), "expected_version": 99}
    for path, body in (
        (PROFILE, {"operation": "profile", "meta": stale, "display_name": "x", "summary": "y"}),
        (VISIBILITY, {"operation": "visibility", "meta": stale, "action": "pause"}),
        (
            FIELDS,
            {
                "operation": "profile_field",
                "meta": stale,
                "policy_version": catalog["policy_version"],
                "field": "gender",
                "value_ids": ["man"],
                "own_words": None,
                "shown": False,
            },
        ),
        (
            PREFERENCES,
            {
                "operation": "preferences",
                "meta": stale,
                "policy_version": catalog["policy_version"],
                "selections": [
                    {"dimension": f, "accepted_option_ids": ["all"]}
                    for f in ("gender", "orientation", "looking_for", "relationship_status")
                ],
            },
        ),
        (
            FILTERS,
            {
                "operation": "filters",
                "meta": stale,
                "policy_version": catalog["policy_version"],
                "minimum_age": 18,
                "maximum_age": None,
                "distance_choice": "anywhere",
            },
        ),
        (AREA, {"operation": "area", "meta": stale, "area_id": NEW_YORK}),
        (
            CONSENT,
            {
                "operation": "consent",
                "meta": stale,
                "policy_version": catalog["consents"]["onboarding"]["policy_version"],
                "decision": "accepted",
            },
        ),
        (
            SENSITIVE,
            {
                "operation": "sensitive_consent",
                "meta": stale,
                "policy_version": catalog["consents"]["sensitive_profile"]["policy_version"],
                "decision": "accepted",
            },
        ),
        (ADULT, {"operation": "adult_check", "meta": stale, "birth_date": years_ago(30)}),
        (
            BIRTH,
            {
                "operation": "birth_input",
                "meta": stale,
                "input": {
                    "birth_date": years_ago(30),
                    "local_time": "10:11:12",
                    "time_precision": "known",
                    "place_label": "Synthetic Place",
                    "timezone_name": None,
                    "timezone_provenance": None,
                },
            },
        ),
    ):
        stale = {"idempotency_key": ctx.key(), "expected_version": 99}
        body = dict(body, meta=stale)
        ctx.refused(ctx.command(owner, path, body), 409, "stale_version", f"stale {path}")
    ctx.refused(ctx.call(owner, "PUT", PROFILE, {}), 405, "invalid_request", "another method")
    ctx.refused(
        ctx.call(owner, "POST", FIELDS, {"operation": "profile_field"}, content_type="text/plain"),
        400,
        "invalid_request",
        "not JSON",
    )
    return "unauthenticated, another member's object and stale versions are refused on every route"


@case("ownership.a_replay_and_a_conflicting_key", "11", "D17")
def ownership_replay(ctx: ProfileContext) -> str:
    member = ctx.ready_member()
    catalog = ctx.catalog(member)
    current = ctx.get(member, FIELDS, "own_profile_fields")["gender"]["version"]
    body = {
        "operation": "profile_field",
        "meta": {"idempotency_key": "replay-key", "expected_version": current},
        "policy_version": catalog["policy_version"],
        "field": "gender",
        "value_ids": ["man"],
        "own_words": None,
        "shown": False,
    }
    first = ctx.data(ctx.command(member, FIELDS, body), "own_profile_fields", "applied")
    again = ctx.data(ctx.command(member, FIELDS, body), "own_profile_fields", "replayed")
    expect(again["gender"] == first["gender"], "the same key and intent replay")
    conflicting = dict(body, value_ids=["woman"])
    ctx.refused(ctx.command(member, FIELDS, conflicting), 409, "idempotency_conflict", "conflict")
    return "a replay returns the current projection; another intent under the key conflicts"


# =============================================================================================
# Acceptance check 12: the stored digests (D17); the scans run once, after the last case
# =============================================================================================


# =============================================================================================
# SV2 Stage B: photos (acceptance check 10, with check 9's photo requirement and checks 11 and 12
# for the new routes; D9, D10, D17) and one pointer order (check 13; D19)
# =============================================================================================


def _lifecycle(ctx: ProfileContext, member: Any, asset_id: str) -> dict[str, Any]:
    return ctx.data(ctx.call(member, "GET", f"{MEDIA}/{asset_id}"), "media", "the asset")


def _asset_row(asset_id: str) -> Any:
    from glow_persistence.models import MediaAsset

    return MediaAsset.objects.get(pk=asset_id)


def _objects(asset_id: str) -> list[Any]:
    from glow_persistence.models import MediaObject

    return list(MediaObject.objects.filter(asset_id=asset_id).order_by("created_at"))


def _media_policy() -> dict[str, Any]:
    from glow_domain import profile_settings as ps
    from glow_profiles import settings_store

    return copy.deepcopy(settings_store.read_unlocked(ps.MEDIA_POLICY).content)


def _publish_media(ctx: ProfileContext, content: dict[str, Any]) -> Any:
    from glow_domain import profile_settings as ps

    return ctx.publish(ps.MEDIA_POLICY, content)


@case("media.policy_is_development_media_1_within_ceilings", "1", "10", "D2", "D10")
def media_policy(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import SettingVersion, StaffAudit
    from glow_profiles import settings_store

    first = SettingVersion.objects.get(name=ps.MEDIA_POLICY, number=1)
    expect(first.content == ps.LAUNCH_DEFAULTS[ps.MEDIA_POLICY], "version 1 is development-media-1")
    expect(first.reason == "development-media-1", "seeded with the reason development-media-1")
    expect(first.staff_subject == ps.LAUNCH_SUBJECT, "seeded by system:launch-default")
    expect(
        StaffAudit.objects.filter(object_id=first.id, action="seed_launch_default").count() == 1,
        "the seed's audit row",
    )
    current = settings_store.read_unlocked(ps.MEDIA_POLICY)
    expect(current.number == 1, "the pointer names version 1")
    refused = 0
    for changes in (
        {"types": ["image/png", "image/gif"]},
        {"max_bytes": ps.MEDIA_BYTES + 1},
        {"max_pixels": ps.MEDIA_PIXELS + 1},
        {"live_photos": ps.MEDIA_COLLECTION + 1},
    ):
        before = _counts()
        result = _publish_media(ctx, {**current.content, **changes})
        expect(result.outcome == "refused", "a publication above a ceiling is refused")
        expect(result.code == "invalid_request", "as invalid_request")
        expect(_counts() == before, "nothing is written")
        refused += 1
    expect(settings_store.read_unlocked(ps.MEDIA_POLICY).number == 1, "the pointer is unmoved")
    return f"media.policy v1 is development-media-1; {refused} ceilings refused, nothing written"


@case("media.grant_within_the_policys_limits", "10", "11", "D10", "D17")
def media_grant(ctx: ProfileContext) -> str:
    from glow_domain import profile_settings as ps
    from glow_persistence.models import MediaAsset, MediaUploadGrant
    from glow_profiles.media_fixtures import default_storage

    member = ctx.member()
    empty = ctx.media(member)
    expect(empty["version"] == 1 and empty["items"] == [], "an empty collection is version 1")
    grant = ctx.request_upload(member)
    row = MediaUploadGrant.objects.get(asset_id=grant["asset_id"])
    expect(row.account_id == member.account_id, "the grant is the member's")
    expect(row.policy_version == "media.policy.v1", "it records the version it was issued under")
    seconds = (row.expires_at - row.issued_at).total_seconds()
    expect(seconds == _media_policy()["grant_seconds"], "short-lived: the policy's grant time")
    expect(row.used_at is None, "one-use: not yet used")
    key = row.object_key
    asset = MediaAsset.objects.get(pk=grant["asset_id"])
    expect(asset.state == "upload_pending" and asset.storage_ref == key, "upload_pending")
    for identifier in (member.account_id, grant["asset_id"]):
        expect(UUID(str(identifier)).hex not in key, "the key holds no ID")
        expect(str(identifier) not in key, "the key holds no ID in any form")
    expect(len(key) == 32 and set(key) <= set("0123456789abcdef"), "the key is opaque")
    credential = default_storage().credentials[key]
    expect(credential.max_bytes == _media_policy()["max_bytes"], "the credential's byte limit")
    texts = json.dumps(ctx.served) + "\n".join(ctx.headers)
    expect(key not in texts, "no response holds the object key")
    expect(credential.token not in texts, "no member is given the store's credential")
    expect(set(grant) == {"kind", "asset_id", "grant_ref", "expires_at"}, "the DTO unchanged")
    expect("/" not in grant["grant_ref"], "the grant reference holds no address")
    listed = ctx.media(member)
    expect([item["state"] for item in listed["items"]] == ["upload_pending"], "listed pending")
    expect(listed["version"] == 2, "the collection's version advanced")
    # A replay answers the same grant; another intent under the key is a conflict.
    body = ctx.media_intent(member, "request_upload")
    first = ctx.data(ctx.command(member, MEDIA, body), "media_upload_grant", "a second grant")
    again = ctx.data(ctx.command(member, MEDIA, body), "media_upload_grant", "its replay")
    expect(again == first, "the replay answers the same grant")
    other = dict(body, action="reorder", ordered_asset_ids=[first["asset_id"]])
    ctx.refused(ctx.command(member, MEDIA, other), 409, "idempotency_conflict", "another intent")
    stale = ctx.media_intent(member, "request_upload", expected=1)
    ctx.refused(ctx.command(member, MEDIA, stale), 409, "stale_version", "a stale version")
    # The policy's live photos: four at most (development-media-1); a fifth is refused, and
    # nothing is written.
    while (
        MediaAsset.objects.filter(account_id=member.account_id).count()
        < ps.LAUNCH_DEFAULTS[ps.MEDIA_POLICY]["live_photos"]
    ):
        ctx.request_upload(member)
    before = (MediaAsset.objects.count(), MediaUploadGrant.objects.count(), _counts())
    beyond = ctx.command(member, MEDIA, ctx.media_intent(member, "request_upload"))
    ctx.refused(beyond, 409, "state_conflict", "a grant beyond the policy's limits")
    after = (MediaAsset.objects.count(), MediaUploadGrant.objects.count(), _counts())
    expect(after == before, "the refused grant writes nothing")
    # A rejected or removed photo is not live: a removal frees a place.
    ctx.data(
        ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=grant["asset_id"])),
        "media",
        "a pending upload removed",
    )
    ctx.request_upload(member)
    return "a grant within the policy's limits, one-use and short-lived; the fifth refused"


@case("media.an_upload_moves_only_through_quarantine_the_seam_and_review", "10", "D10")
def media_path(ctx: ProfileContext) -> str:
    from glow_persistence.models import StaffAudit
    from glow_profiles import media
    from glow_profiles.media_fixtures import default_storage

    member = ctx.member()
    grant = ctx.request_upload(member)
    asset_id = UUID(grant["asset_id"])
    key = grant_key(asset_id)
    approving = test_ports(check=DecidingCheck())
    # Before its completion: neither the review step nor the check moves it.
    expect(media.review(asset_id).reason == "not_quarantined", "no review before quarantine")
    expect(media.run_check(asset_id, ports=approving).reason == "not_in_review", "no approval")
    expect(_lifecycle(ctx, member, str(asset_id))["state"] == "upload_pending", "still pending")
    # Another object, written at another key, is never read for this asset.
    stranger = md_key()
    default_storage().put(stranger, synthetic_png(5, 5))
    adopted = media.record_upload(ctx.put_photo(str(asset_id), synthetic_png(3, 2)))
    expect(adopted.outcome == "applied", "the completion is adopted")
    expect(_lifecycle(ctx, member, str(asset_id))["state"] == "quarantined", "quarantined")
    expect(media.run_check(asset_id, ports=approving).reason == "not_in_review", "no approval")
    storage = default_storage()
    processing = RecordingProcessing(storage)
    detector = RecordingDetector()
    reads = len(storage.reads)
    reviewed = media.review(asset_id, ports=test_ports(processing=processing, detection=detector))
    expect(reviewed.outcome == "applied", "the system review step ran")
    expect(processing.asked == [key], "processing read the adopted original only")
    expect(storage.reads[reads:] == [key], "the store was read at the original's key only")
    objects = _objects(str(asset_id))
    expect([o.role for o in objects] == ["original", "variant"], "an original and a variant")
    variant = objects[1].key
    expect(variant != key and stranger not in (key, variant), "each object has its own key")
    expect(detector.given == [(asset_id, variant)], "G-02's seam was given the variant")
    row = _asset_row(str(asset_id))
    expect(row.state == "review_pending" and row.detection == "no_detector", "no detector")
    for object_key in (key, variant):
        expect(len(object_key) == 32 and str(asset_id) not in object_key, "keys are opaque")
        expect(UUID(str(member.account_id)).hex not in object_key, "no account ID in a key")
    hold = RecordingHold()
    approved = media.run_check(asset_id, ports=test_ports(check=DecidingCheck(), hold=hold))
    expect(approved.outcome == "applied", "the check approved it")
    expect(hold.asked == [asset_id], "the approval asked the hold port first")
    audit = StaffAudit.objects.get(object_id=asset_id, action="approve")
    expect(audit.staff_subject == "system:photo-check", "written with a system: subject")
    lifecycle = _lifecycle(ctx, member, str(asset_id))
    reference = lifecycle["approved_delivery_ref"]
    expect(lifecycle["state"] == "approved" and reference, "approved, with its reference")
    expect(reference not in (key, variant) and key not in reference, "never a key")
    expect(storage.references[reference] == variant, "the reference is the variant's only")
    expect(row.review_ref is None and _asset_row(str(asset_id)).review_ref == audit.id, "review")
    delivered = media.delivery_reference(asset_id, ports=test_ports(hold=hold))
    expect(delivered.detail["delivery_ref"] == reference, "delivery returns the variant's")
    expect(hold.asked == [asset_id, asset_id], "delivery asked the hold port first")
    held = RecordingHold({asset_id})
    withheld = media.delivery_reference(asset_id, ports=test_ports(hold=held))
    expect(withheld.detail["delivery_ref"] is None, "a hold withholds delivery")
    return "upload_pending, quarantined, the seam with the variant, review, approval (system)"


def md_key() -> str:
    from glow_domain import media as md

    return str(md.new_object_key())


@case("media.an_upload_with_no_variant_passes_the_seam_and_is_rejected", "10", "D10")
def media_no_variant(ctx: ProfileContext) -> str:
    from glow_persistence.models import StaffAudit
    from glow_profiles import media
    from glow_profiles.media_fixtures import default_storage

    member = ctx.member()
    storage = default_storage()
    shown = []
    for what in ("an original that no longer matches its completion", "a file that is no PNG"):
        grant = ctx.request_upload(member)
        asset_id = UUID(grant["asset_id"])
        key = grant_key(asset_id)
        data = synthetic_png() if what.startswith("an original") else b"GIF89a" + bytes(64)
        expect(media.record_upload(ctx.put_photo(str(asset_id), data)).outcome == "applied", "in")
        if what.startswith("an original"):
            # The object at the key changed after its completion was adopted.
            storage.objects[key] = synthetic_png(4, 4)
        detector = RecordingDetector()
        reviewed = media.review(asset_id, ports=test_ports(detection=detector))
        expect(reviewed.outcome == "applied", "the review step ran")
        expect(detector.given == [(asset_id, key)], "the seam was given the original")
        row = _asset_row(str(asset_id))
        expect(row.state == "rejected", "rejected")
        expect(row.rejection_reason == "no_variant", "with the reason that no variant was made")
        expect(row.detection == "no_detector", "it passed the seam")
        expect([o.role for o in _objects(str(asset_id))] == ["original"], "no variant written")
        audit = StaffAudit.objects.get(object_id=asset_id, action="reject")
        expect(audit.staff_subject == "system:photo-check", "the system's rejection")
        expect(_events(asset_id, "media_in_review") == 1, "it passed review_pending")
        expect(_lifecycle(ctx, member, str(asset_id))["approved_delivery_ref"] is None, "none")
        shown.append(what)
    # An unavailable store is not such a failure: nothing changes, and the step runs again.
    grant = ctx.request_upload(member)
    asset_id = UUID(grant["asset_id"])
    expect(media.record_upload(ctx.put_photo(str(asset_id))).outcome == "applied", "adopted")
    before = (_asset_row(str(asset_id)).version, _counts(), len(_objects(str(asset_id))))
    storage.unavailable = True
    try:
        down = media.review(asset_id)
    finally:
        storage.unavailable = False
    expect(down.outcome == "refused" and down.code == "provider_unavailable", "unavailable")
    after = (_asset_row(str(asset_id)).version, _counts(), len(_objects(str(asset_id))))
    expect(after == before, "an unavailable store changes nothing")
    expect(_asset_row(str(asset_id)).state == "quarantined", "still quarantined")
    expect(media.review(asset_id).outcome == "applied", "the step can run again")
    expect(_asset_row(str(asset_id)).state == "review_pending", "and moves it to review")
    return f"{len(shown)} uploads with no variant passed the seam and were rejected; a store down"


@case("media.completions_are_matched_to_their_grant", "10", "D10")
def media_completions(ctx: ProfileContext) -> str:
    from datetime import timedelta

    from glow_domain import media as md
    from glow_persistence.models import MediaUploadGrant
    from glow_profiles import media
    from glow_profiles.media_fixtures import default_storage

    storage = default_storage()
    member = ctx.member()
    # A completion for a key no grant names, and an event the adapter did not issue.
    unknown = media.record_upload(storage.put(md_key(), synthetic_png()))
    expect(unknown.outcome == "no_change", "a completion for no grant's key changes nothing")
    grant = ctx.request_upload(member)
    asset_id = UUID(grant["asset_id"])
    key = grant_key(asset_id)
    forged = md.UploadCompleted(uuid4(), key, 71, "0" * 32, db_now())
    refused = media.record_upload(forged)
    expect(refused.outcome == "refused" and refused.code == "forbidden", "unauthenticated")
    expect(_asset_row(str(asset_id)).state == "upload_pending", "nothing changed")
    # Above the byte limit of the policy version the grant records: not adopted.
    limit = _media_policy()["max_bytes"]
    big = media.record_upload(storage.put(key, bytes(limit + 1)))
    expect(big.reason == "over_byte_limit", "an oversize completion changes nothing")
    original = _objects(str(asset_id))[0]
    expect(original.adopted_at is None, "its object is not adopted")
    # The first completion that matches is adopted; a second one for the key changes nothing.
    data = synthetic_png(2, 3)
    good = ctx.put_photo(str(asset_id), data)
    expect(media.record_upload(good).outcome == "applied", "the matching completion is adopted")
    adopted = _objects(str(asset_id))[0]
    expect(adopted.byte_size == len(data) and adopted.adopted_at is not None, "its size")
    second = media.record_upload(ctx.put_photo(str(asset_id), synthetic_png(6, 6)))
    expect(second.reason == "not_awaiting_upload", "a second completion changes nothing")
    again = _objects(str(asset_id))[0]
    expect(
        (again.byte_size, again.entity_tag) == (adopted.byte_size, adopted.entity_tag),
        "the adopted original is unchanged",
    )
    duplicate = media.record_upload(good)
    expect(duplicate.reason == "not_awaiting_upload", "a duplicate event changes nothing")
    expect(MediaUploadGrant.objects.get(asset_id=asset_id).used_at is not None, "used once")
    # After the grant's time: not adopted.
    late_grant = ctx.request_upload(member)
    late_row = MediaUploadGrant.objects.get(asset_id=late_grant["asset_id"])
    late = ctx.put_photo(
        late_grant["asset_id"], uploaded_at=late_row.expires_at + timedelta(seconds=1)
    )
    expect(media.record_upload(late).reason == "grant_expired", "an expired grant adopts nothing")
    # The byte limit is the grant's version's, not the current one's.
    issued = ctx.request_upload(member)
    current = _media_policy()
    small = {**current, "max_bytes": 32}
    expect(_publish_media(ctx, small).outcome == "applied", "a smaller byte limit published")
    try:
        under_old = media.record_upload(ctx.put_photo(issued["asset_id"], synthetic_png()))
        expect(under_old.outcome == "applied", "adopted under the version its grant records")
        newer = ctx.request_upload(member)
        version = MediaUploadGrant.objects.get(asset_id=newer["asset_id"]).policy_version
        expect(version != "media.policy.v1", "the newer grant records the newer version")
        over_new = media.record_upload(ctx.put_photo(newer["asset_id"], synthetic_png()))
        expect(over_new.reason == "over_byte_limit", "refused under the newer grant's version")
    finally:
        expect(_publish_media(ctx, current).outcome == "applied", "the limit published back")
    return "completions matched to their grant's key, time and version's byte limit"


def db_now() -> Any:
    from django.utils import timezone

    return timezone.now()


@case("media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction", "10", "D10")
def media_check(ctx: ProfileContext) -> str:
    from glow_persistence.models import StaffAudit
    from glow_profiles import media, staff

    member = ctx.member()
    asset_id = UUID(ctx.uploaded_photo(member))
    expect(media.review(asset_id).outcome == "applied", "reviewed")
    # The runtime's check approves nothing.
    runtime = media.run_check(asset_id)
    expect(runtime.reason == "undecided", "the runtime's check approves nothing")
    expect(_asset_row(str(asset_id)).state == "review_pending", "still in review")
    # No member route approves or rejects: the intent has no such action.
    for action in ("approve", "reject", "uploaded", "purged"):
        body = ctx.media_intent(member, "request_upload")
        body["action"] = action
        ctx.refused(ctx.command(member, MEDIA, body), 400, "invalid_request", "no member event")
    rejecting = test_ports(check=DecidingCheck("reject", "fixture_reason"))
    expect(media.run_check(asset_id, ports=rejecting).outcome == "applied", "rejected")
    row = _asset_row(str(asset_id))
    expect(row.state == "rejected" and row.rejection_reason == "fixture_reason", "its reason")
    audit = StaffAudit.objects.get(object_id=asset_id, action="reject")
    expect(audit.staff_subject == "system:photo-check", "a system: subject")
    # A staff restriction on a report: back to review, delivery withheld, and the check never
    # clears it.
    photo = UUID(ctx.approved_photo(member))
    request = uuid4()
    restricted = staff.restrict_media(
        photo, staff_subject=STAFF, reason="report-fixture", request_id=request
    )
    expect(restricted.outcome == "applied", "staff restricted it")
    row = _asset_row(str(photo))
    expect(row.state == "review_pending" and row.restriction_ref is not None, "a revocation")
    expect(_lifecycle(ctx, member, str(photo))["approved_delivery_ref"] is None, "withheld")
    expect(StaffAudit.objects.get(request_id=request).staff_subject == STAFF, "the staff's subject")
    approving = test_ports(check=DecidingCheck())
    kept = media.run_check(photo, ports=approving)
    expect(kept.reason == "restricted", "the check never clears a staff restriction")
    expect(_asset_row(str(photo)).state == "review_pending", "it stays restricted")
    again = staff.restrict_media(
        photo, staff_subject=STAFF, reason="report-fixture", request_id=uuid4()
    )
    expect(again.outcome == "refused" and again.code == "state_conflict", "only an approved one")
    member_subject = staff.restrict_media(
        photo, staff_subject="member:x", reason="report-fixture", request_id=uuid4()
    )
    expect(member_subject.outcome == "refused", "a member's subject is refused")
    # An approval never undoes an owner's removal.
    pending = UUID(ctx.uploaded_photo(member))
    expect(media.review(pending).outcome == "applied", "in review")
    removed = ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=str(pending)))
    ctx.data(removed, "media", "the owner removed it while in review")
    after = media.run_check(pending, ports=approving)
    expect(after.reason == "not_in_review", "the check cannot approve a removed photo")
    row = _asset_row(str(pending))
    expect(row.state == "removal_pending" and row.approved_variant_ref is None, "still removed")
    subjects = set(
        StaffAudit.objects.filter(action__in=["approve", "reject"]).values_list(
            "staff_subject", flat=True
        )
    )
    expect(subjects == {"system:photo-check"}, "every approval and rejection is the system's")
    return "approve and reject are the check's (system); restriction kept; removal never undone"


@case("media.a_hold_stops_the_checks_approval", "10", "D9", "D10")
def media_held(ctx: ProfileContext) -> str:
    """SV2 Stage B, correction C2 (the exact-head review's F1): with the photo held (the test's
    hold port holding that asset), the check that decides to approve it changes nothing: the
    outcome is ``held``, the photo stays ``review_pending``, with no approval ``StaffAudit`` row,
    no delivery reference issued or stored, no event and no change to the profile, which still
    misses its photo. Released, the same check approves it and the profile completes, so the hold
    alone stopped it."""
    from glow_persistence.models import OutboxEvent, StaffAudit
    from glow_profiles import media
    from glow_profiles.media_fixtures import default_storage

    member = ctx.ready_member(photo=False)
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    _edit(ctx, member)
    expect(ctx.missing(member) == ["photo"], "only a photo is missing")
    asset_id = UUID(ctx.uploaded_photo(member))
    expect(media.review(asset_id).outcome == "applied", "reviewed")
    profile = _profile_row(member.account_id)
    storage = default_storage()

    def snapshot() -> tuple[Any, ...]:
        row = _asset_row(str(asset_id))
        current = _profile_row(member.account_id)
        return (
            row.state,
            row.version,
            row.approved_variant_ref,
            row.review_ref,
            current.state,
            current.version,
            StaffAudit.objects.filter(object_id=asset_id).count(),
            OutboxEvent.objects.filter(aggregate_id__in=[asset_id, profile.pk]).count(),
            len(storage.references),
        )

    before = snapshot()
    expect(before[0] == "review_pending" and before[4] == "incomplete", "in review; incomplete")
    for _ in range(2):
        hold, check = RecordingHold({asset_id}), DecidingCheck()
        held = media.run_check(asset_id, ports=test_ports(check=check, hold=hold))
        expect(held.outcome == "no_change" and held.reason == "held", "the outcome is held")
        expect(check.asked == [asset_id], "the check decided to approve it")
        expect(hold.asked == [asset_id], "the hold port was asked, and holds it")
        expect(snapshot() == before, "nothing changed: photo, audit, events, reference, profile")
    expect(
        not StaffAudit.objects.filter(object_id=asset_id, action="approve").exists(),
        "no approval StaffAudit row",
    )
    lifecycle = _lifecycle(ctx, member, str(asset_id))
    expect(lifecycle["state"] == "review_pending", "still review_pending")
    expect(lifecycle["approved_delivery_ref"] is None, "no delivery reference")
    expect(ctx.missing(member) == ["photo"], "the profile still misses its photo")
    expect(ctx.get(member, PROFILE, "own_profile")["media_ids"] == [], "no photo is listed")
    released = media.run_check(
        asset_id, ports=test_ports(check=DecidingCheck(), hold=RecordingHold())
    )
    expect(released.outcome == "applied", "released, the check approves it")
    expect(released.detail.get("profile") == "visible", "and the profile completes")
    expect(
        StaffAudit.objects.filter(object_id=asset_id, action="approve").count() == 1,
        "one approval StaffAudit row, after the release",
    )
    return "the check's approval held twice with nothing written; released, it approves"


@case("media.removal_withholds_delivery_and_completes_on_every_objects_purge", "10", "D10")
def media_removal(ctx: ProfileContext) -> str:
    from glow_domain import media as md
    from glow_profiles import media
    from glow_profiles.media_fixtures import default_storage

    storage = default_storage()
    member = ctx.member()
    photo = UUID(ctx.approved_photo(member))
    keys = [o.key for o in _objects(str(photo))]
    expect(len(keys) == 2, "an original and a variant")
    expect(media.delivery_reference(photo).detail["delivery_ref"], "delivered while approved")
    removed = ctx.data(
        ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=str(photo))),
        "media",
        "removed",
    )
    expect(removed["state"] == "removal_pending", "removal_pending")
    expect(removed["approved_delivery_ref"] is None, "delivery withheld at once")
    expect(media.delivery_reference(photo).detail["delivery_ref"] is None, "nothing delivers it")
    repeat = ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=str(photo)))
    expect(ctx.data(repeat, "media", "removed again")["state"] == "removal_pending", "repeat")
    # An acknowledgment before the purge is requested is out of order: nothing changes.
    early = media.acknowledge_deletion(storage.acknowledge(keys[0]))
    expect(early.reason == "purge_not_requested", "an out-of-order acknowledgment")
    # The purge asks the hold port first; a hold stops it.
    held = RecordingHold({photo})
    deletions = len(storage.deletions)
    stopped = media.request_purge(photo, ports=test_ports(hold=held))
    expect(stopped.reason == "held" and held.asked == [photo], "the hold port was asked")
    expect(len(storage.deletions) == deletions, "nothing deleted under a hold")
    expect(_asset_row(str(photo)).purge_requested_at is None, "no purge requested")
    asking = RecordingHold()
    expect(media.request_purge(photo, ports=test_ports(hold=asking)).outcome == "applied", "go")
    expect(asking.asked == [photo], "the purge asked the hold port first")
    expect(sorted(storage.deletions[deletions:]) == sorted(keys), "every object is deleted")
    forged = media.acknowledge_deletion(md.ObjectDeleted(uuid4(), keys[0]))
    expect(forged.outcome == "refused" and forged.code == "forbidden", "unauthenticated")
    first = media.acknowledge_deletion(storage.acknowledge(keys[0]))
    expect(first.outcome == "applied", "one object acknowledged")
    expect(_asset_row(str(photo)).state == "removal_pending", "not removed until every object")
    duplicate = media.acknowledge_deletion(storage.acknowledge(keys[0]))
    expect(duplicate.reason == "already_deleted", "a duplicate acknowledgment changes nothing")
    expect(_asset_row(str(photo)).state == "removal_pending", "still pending")
    last = media.acknowledge_deletion(storage.acknowledge(keys[1]))
    expect(last.outcome == "applied", "the last object acknowledged")
    expect(_asset_row(str(photo)).state == "removed", "removed on every object's purge")
    expect(_events(photo, "media_purged") == 1, "media_purged")
    expect(all(o.deleted_at is not None for o in _objects(str(photo))), "each acknowledged")
    return "removal withheld delivery at once; removed only when both objects were acknowledged"


# SV2 Stage B, correction C1 (DM-58 item 9): the purge and the store's deletion acknowledgment
# run in any account state, under the account row's lock; every other photo step refuses an
# account that is not active. The owner is suspended or asks for deletion through glow_chat's own
# writers (``suspend``, ``delete``), called unchanged.


def _withheld(asset_id: UUID) -> bool:
    """Delivery withheld: no reference on the row, and the system read returns none (it refuses
    an owner who is not active, and returns none for an asset that is not approved)."""
    from glow_profiles import media

    read = media.delivery_reference(asset_id)
    return (
        _asset_row(str(asset_id)).approved_variant_ref is None
        and read.outcome in ("read", "refused")
        and read.detail.get("delivery_ref") is None
    )


def _inactive_refusal(result: Any) -> bool:
    return (result.outcome, result.code, result.reason) == (
        "refused",
        "forbidden",
        "account_not_active",
    )


@case("media.a_photo_removed_before_its_owner_is_suspended_is_still_purged", "10", "D10")
def media_purge_after_suspension(ctx: ProfileContext) -> str:
    from glow_chat.contact import OrmContactPersistence
    from glow_profiles import media
    from glow_profiles.media_fixtures import default_storage

    storage = default_storage()
    member = ctx.member()
    photo = UUID(ctx.approved_photo(member))
    keys = [o.key for o in _objects(str(photo))]
    expect(len(keys) == 2, "an original and a variant")
    removed = ctx.data(
        ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=str(photo))),
        "media",
        "removed",
    )
    expect(removed["state"] == "removal_pending", "removal_pending")
    expect(removed["approved_delivery_ref"] is None and _withheld(photo), "withheld at once")
    suspended = OrmContactPersistence(provider="fixture").suspend(member.account_id)
    expect(suspended.outcome == "applied", "glow_chat suspended the owner")
    expect(_account(member.account_id).state == "suspended", "the owner is suspended")
    expect(_withheld(photo), "withheld after the suspension")
    # The purge still asks the hold port first, whatever the owner's state: a hold stops it.
    deletions = len(storage.deletions)
    held = RecordingHold({photo})
    stopped = media.request_purge(photo, ports=test_ports(hold=held))
    expect(stopped.reason == "held" and held.asked == [photo], "a hold stops the purge")
    expect(len(storage.deletions) == deletions, "nothing deleted under a hold")
    asking = RecordingHold()
    purge = media.request_purge(photo, ports=test_ports(hold=asking))
    expect(purge.outcome == "applied", "the purge is asked for a suspended owner")
    expect(asking.asked == [photo], "the purge asked the hold port first")
    expect(sorted(storage.deletions[deletions:]) == sorted(keys), "every object is deleted")
    expect(_withheld(photo), "withheld while the purge is pending")
    first = media.acknowledge_deletion(storage.acknowledge(keys[0]))
    expect(first.outcome == "applied", "one object acknowledged for a suspended owner")
    expect(_asset_row(str(photo)).state == "removal_pending", "not removed until every object")
    expect(_withheld(photo), "withheld after one acknowledgment")
    last = media.acknowledge_deletion(storage.acknowledge(keys[1]))
    expect(last.outcome == "applied", "the last object acknowledged for a suspended owner")
    expect(_asset_row(str(photo)).state == "removed", "removed after every object's acknowledgment")
    expect(_events(photo, "media_purged") == 1, "media_purged")
    expect(all(o.deleted_at is not None for o in _objects(str(photo))), "each acknowledged")
    expect(_withheld(photo), "withheld once removed")
    expect(_account(member.account_id).state == "suspended", "the account is unchanged")
    return "removed, then suspended: the purge asked the hold port, both objects acknowledged"


@case("media.a_purge_asked_before_its_owner_asks_for_deletion_completes", "10", "D10")
def media_purge_after_deletion_request(ctx: ProfileContext) -> str:
    from glow_chat.contact import OrmContactPersistence
    from glow_persistence.models import DeletionJob
    from glow_profiles import media
    from glow_profiles.media_fixtures import default_storage

    storage = default_storage()
    member = ctx.member()
    photo = UUID(ctx.approved_photo(member))
    keys = [o.key for o in _objects(str(photo))]
    expect(len(keys) == 2, "an original and a variant")
    ctx.data(
        ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=str(photo))),
        "media",
        "removed",
    )
    expect(_withheld(photo), "withheld at once")
    deletions = len(storage.deletions)
    asking = RecordingHold()
    purge = media.request_purge(photo, ports=test_ports(hold=asking))
    expect(purge.outcome == "applied", "the purge is asked while the owner is active")
    expect(asking.asked == [photo], "the purge asked the hold port first")
    expect(sorted(storage.deletions[deletions:]) == sorted(keys), "every object is deleted")
    deleting = OrmContactPersistence(provider="fixture").delete(member.account_id)
    expect(deleting.outcome == "applied", "glow_chat recorded the deletion request")
    expect(_account(member.account_id).state == "deletion_pending", "the owner asked to delete")
    expect(DeletionJob.objects.filter(account_id=member.account_id).count() == 1, "its job")
    expect(_withheld(photo), "withheld after the deletion request")
    first = media.acknowledge_deletion(storage.acknowledge(keys[0]))
    expect(first.outcome == "applied", "one object acknowledged after the deletion request")
    expect(_asset_row(str(photo)).state == "removal_pending", "not removed until every object")
    expect(_withheld(photo), "withheld after one acknowledgment")
    duplicate = media.acknowledge_deletion(storage.acknowledge(keys[0]))
    expect(duplicate.reason == "already_deleted", "a duplicate acknowledgment changes nothing")
    last = media.acknowledge_deletion(storage.acknowledge(keys[1]))
    expect(last.outcome == "applied", "the last object acknowledged after the deletion request")
    expect(_asset_row(str(photo)).state == "removed", "removed after every object's acknowledgment")
    expect(_events(photo, "media_purged") == 1, "media_purged")
    expect(_withheld(photo), "withheld once removed")
    expect(_account(member.account_id).state == "deletion_pending", "the account is unchanged")
    return "purge asked, then deletion requested: both acknowledgments completed the purge"


@case("media.every_other_photo_step_refuses_an_inactive_owner", "10", "D10")
def media_inactive_owner(ctx: ProfileContext) -> str:
    from glow_chat.contact import OrmContactPersistence
    from glow_persistence.models import MediaObject, MediaUploadGrant
    from glow_profiles import media, staff

    chat = OrmContactPersistence(provider="fixture")
    refused = 0
    for revoke, becomes in ((chat.suspend, "suspended"), (chat.delete, "deletion_pending")):
        member = ctx.member()
        pending = UUID(ctx.request_upload(member)["asset_id"])
        quarantined = UUID(ctx.uploaded_photo(member))
        in_review = UUID(ctx.uploaded_photo(member))
        expect(media.review(in_review).outcome == "applied", "in review while active")
        photo = UUID(ctx.approved_photo(member))
        completion = ctx.put_photo(str(pending))
        expect(revoke(member.account_id).outcome == "applied", "glow_chat revoked the account")
        expect(_account(member.account_id).state == becomes, "the owner is not active")
        before = (
            _counts(),
            MediaObject.objects.count(),
            [(row.state, row.version) for row in map(_asset_row, map(str, (pending, quarantined)))],
            [(row.state, row.version) for row in map(_asset_row, map(str, (in_review, photo)))],
        )
        adopted = media.record_upload(completion)
        expect(_inactive_refusal(adopted), "record_upload refuses an inactive owner")
        expect(MediaUploadGrant.objects.get(asset_id=pending).used_at is None, "not adopted")
        reviewed = media.review(quarantined)
        expect(_inactive_refusal(reviewed), "review refuses an inactive owner")
        approving = test_ports(check=DecidingCheck())
        checked = media.run_check(in_review, ports=approving)
        expect(_inactive_refusal(checked), "run_check refuses an inactive owner")
        expect(approving.check.asked == [], "the check was never asked")
        restricted = staff.restrict_media(
            photo, staff_subject=STAFF, reason="report-fixture", request_id=uuid4()
        )
        expect(_inactive_refusal(restricted), "staff's restriction refuses an inactive owner")
        delivered = media.delivery_reference(photo)
        expect(_inactive_refusal(delivered), "the delivery read refuses an inactive owner")
        after = (
            _counts(),
            MediaObject.objects.count(),
            [(row.state, row.version) for row in map(_asset_row, map(str, (pending, quarantined)))],
            [(row.state, row.version) for row in map(_asset_row, map(str, (in_review, photo)))],
        )
        expect(after == before, "nothing changed for an inactive owner")
        refused += 5
    return f"{refused} steps refused for a suspended and a deleting owner (account_not_active)"


@case("media.reorder_and_every_route_refuses_another_members_photo", "10", "11", "D10", "D17")
def media_ownership(ctx: ProfileContext) -> str:
    owner, stranger = ctx.ready_member(photo=False), ctx.member()
    photos = [ctx.approved_photo(owner) for _ in range(3)]
    theirs = ctx.approved_photo(stranger)
    collection = ctx.media(owner)
    expect([i["asset_id"] for i in collection["items"]] == photos, "in upload order")
    wanted = [photos[2], photos[0], photos[1]]
    reordered = ctx.data(
        ctx.command(owner, MEDIA, ctx.media_intent(owner, "reorder", ordered=wanted)),
        "media_collection",
        "reordered",
    )
    expect([i["asset_id"] for i in reordered["items"]] == wanted, "the new order")
    expect(reordered["version"] > collection["version"], "the collection's version advanced")
    expect(ctx.get(owner, PROFILE, "own_profile")["media_ids"] == wanted, "the profile's order")
    ctx.refused(
        ctx.command(owner, MEDIA, ctx.media_intent(owner, "reorder", ordered=wanted[:2])),
        409,
        "state_conflict",
        "not the whole approved set",
    )
    ctx.refused(
        ctx.command(owner, MEDIA, ctx.media_intent(owner, "reorder", ordered=[*wanted, theirs])),
        404,
        "not_found",
        "reorder with another owner's photo",
    )
    ctx.refused(
        ctx.command(owner, MEDIA, ctx.media_intent(owner, "reorder", ordered=wanted, expected=1)),
        409,
        "stale_version",
        "a stale collection",
    )
    ctx.refused(
        ctx.command(owner, MEDIA, ctx.media_intent(owner, "remove", asset_id=theirs, expected=1)),
        404,
        "not_found",
        "removal of another owner's photo",
    )
    ctx.refused(ctx.call(owner, "GET", f"{MEDIA}/{theirs}"), 404, "not_found", "their photo")
    expect(theirs not in json.dumps(ctx.media(owner)), "their photo is in no collection of mine")
    ctx.refused(
        ctx.command(
            owner, MEDIA, ctx.media_intent(owner, "remove", asset_id=photos[0], expected=99)
        ),
        409,
        "stale_version",
        "a stale asset version",
    )
    for method, body in (("GET", None), ("POST", ctx.media_intent(owner, "request_upload"))):
        reply = ctx.call(owner, method, MEDIA, body, bearer=False)
        ctx.refused(reply, 401, "unauthenticated", "no session")
    ctx.refused(ctx.call(owner, "GET", f"{MEDIA}?state=approved"), 400, "invalid_request", "query")
    extra = {**ctx.media_intent(owner, "request_upload"), "filename": "fixture.png"}
    ctx.refused(ctx.command(owner, MEDIA, extra), 400, "invalid_request", "an extra field")
    expect(_lifecycle(ctx, stranger, theirs)["state"] == "approved", "theirs is unchanged")
    return "reorder of the whole approved set; another member's photo refused at every route"


@case("media.the_photo_requirement_completes_and_its_removal_demotes", "9", "10", "D9", "D10")
def media_requirement(ctx: ProfileContext) -> str:
    from glow_profiles import media, staff

    shown: list[str] = []
    member = ctx.ready_member(photo=False)
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    _edit(ctx, member)
    expect(ctx.missing(member) == ["photo"], "only a photo is missing")
    profile = _profile_row(member.account_id)
    expect(profile.state == "incomplete", "incomplete without a photo")
    completed = _events(profile.pk, "profile_completed")
    asset_id = UUID(ctx.uploaded_photo(member))
    expect(media.review(asset_id).outcome == "applied", "reviewed")
    expect(_profile_row(member.account_id).state == "incomplete", "a photo in review is none")
    approved = media.run_check(asset_id, ports=test_ports(check=DecidingCheck()))
    expect(approved.detail.get("profile") == "visible", "the check's approval completes it")
    expect(_profile_row(member.account_id).state == "visible", "visible (requirements_met)")
    expect(_events(profile.pk, "profile_completed") == completed + 1, "profile_completed")
    expect(ctx.get(member, PROFILE, "own_profile")["media_ids"] == [str(asset_id)], "listed")
    shown.append("the check's approval")
    # A second photo: removing one keeps the profile visible; removing the last demotes it.
    second = ctx.approved_photo(member)
    demoted = _events(profile.pk, "profile_demoted")
    ctx.data(
        ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=second)),
        "media",
        "one of two removed",
    )
    expect(_profile_row(member.account_id).state == "visible", "one approved photo remains")
    ctx.data(
        ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=str(asset_id))),
        "media",
        "the last removed",
    )
    expect(_profile_row(member.account_id).state == "incomplete", "the last removal demotes")
    expect(_events(profile.pk, "profile_demoted") == demoted + 1, "profile_demoted")
    expect(ctx.missing(member) == ["photo"], "the photo is missing again")
    shown.append("the removal of the last approved photo")
    # Staff's restriction of the last approved photo demotes too.
    member = ctx.visible_member()
    photo = UUID(ctx.media(member)["items"][0]["asset_id"])
    restricted = staff.restrict_media(
        photo, staff_subject=STAFF, reason="report-fixture", request_id=uuid4()
    )
    expect(restricted.detail.get("profile") == "incomplete", "the restriction demotes")
    expect(_profile_row(member.account_id).state == "incomplete", "incomplete")
    expect(ctx.missing(member) == ["photo"], "a restricted photo is no approved photo")
    shown.append("the restriction of the last approved photo")
    # A paused profile stays paused, and resume rechecks it.
    member = ctx.visible_member()
    photo_id = ctx.media(member)["items"][0]["asset_id"]
    ctx.data(_visibility(ctx, member, "pause"), "own_profile", "paused")
    ctx.data(
        ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=photo_id)),
        "media",
        "removed while paused",
    )
    expect(_profile_row(member.account_id).state == "paused", "a paused profile stays paused")
    ctx.refused(_visibility(ctx, member, "resume"), 403, "forbidden", "resume rechecks it")
    shown.append("a paused profile")
    return f"{len(shown)} photo writers recomputed: " + ", ".join(shown)


@case("pointers.one_order_in_every_transaction", "13", "D19")
def pointers_order(ctx: ProfileContext) -> str:
    from unittest import mock

    from glow_domain import profile_settings as ps
    from glow_persistence.models import OutboxEvent
    from glow_profiles import events, media, settings_store, staff, tx

    calls: list[tuple[Any, tuple[str, ...]]] = []
    holds: list[tuple[Any, str]] = []
    original_read, original_hold = settings_store.read_shared, settings_store._hold

    def reading(transaction: Any, names: Any) -> Any:
        calls.append((transaction, tuple(sorted(set(names)))))
        return original_read(transaction, names)

    def holding(transaction: Any, name: str) -> None:
        holds.append((transaction, name))
        original_hold(transaction, name)

    member = ctx.ready_member()
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    ctx.ensure_test_lists()
    with (
        mock.patch.object(settings_store, "read_shared", reading),
        mock.patch.object(settings_store, "_hold", holding),
    ):
        # D19's four transactions, and Stage B's writers that recompute.
        ctx.data(ctx.field(member, "gender", ["man"]), "own_profile_fields", "set_field")
        ctx.data(ctx.area(member, LOS_ANGELES), "own_area", "set_area")
        ctx.catalog(member)
        _switch_staff_approval(ctx, True)
        other = ctx.ready_member()
        seed_chart(other.account_id)
        approved = staff.approve_without_id(
            other.account_id, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
        )
        _switch_staff_approval(ctx, False)
        expect(approved.outcome == "applied", "staff's approval without ID")
        photo = ctx.media(member)["items"][0]["asset_id"]
        ctx.data(
            ctx.command(member, MEDIA, ctx.media_intent(member, "remove", asset_id=photo)),
            "media",
            "a photo removed",
        )
        ctx.approved_photo(member)
        restricted = staff.restrict_media(
            UUID(ctx.media(member)["items"][-1]["asset_id"]),
            staff_subject=STAFF,
            reason="report-fixture",
            request_id=uuid4(),
        )
        expect(restricted.outcome == "applied", "a restriction")
        _edit(ctx, member)
        current = settings_store.read_unlocked(ps.HISTORY).content
        expect(ctx.publish(ps.HISTORY, current).outcome == "applied", "a history publication")
    transactions: dict[int, list[tuple[str, ...]]] = {}
    for transaction, names in calls:
        transactions.setdefault(id(transaction), []).append(names)
    held: dict[int, list[str]] = {}
    for transaction, name in holds:
        held.setdefault(id(transaction), [])
        if name not in held[id(transaction)]:
            held[id(transaction)].append(name)
    expect(len(transactions) >= 8, "the transactions were seen")
    for order in held.values():
        expect(order == sorted(order), "every transaction locked its pointers in name order")
    for sequence in transactions.values():
        first = set(sequence[0])
        later = {name for names in sequence[1:] for name in names}
        if ps.HISTORY not in first:
            expect(later <= first, "every pointer a member or staff writer reads is in its first")
    recomputing = [s for s in transactions.values() if len(s) > 1]
    expect(recomputing, "writers that recompute read consent.onboarding again")
    for sequence in recomputing:
        if ps.HISTORY not in sequence[0]:
            expect(ps.ONBOARDING_CONSENT in sequence[0], "consent.onboarding in the first call")

    # A lock out of order is an internal error that rolls the transaction back.
    marker = uuid4()

    def out_of_order(transaction: Any) -> Any:
        events.emit(
            transaction,
            events.PROFILE_EDITED,
            aggregate_id=marker,
            aggregate_version=1,
            payload_ref=marker,
            now=db_now(),
        )
        settings_store.read_shared(transaction, [ps.LOCATION])
        settings_store.read_shared(transaction, [ps.ONBOARDING_CONSENT])
        return tx.Result("applied")

    result = tx.run(out_of_order)
    expect(result.outcome == "error" and result.code == "provider_unavailable", "an error")
    expect(result.reason == "PointerOrderError", "named by its type, never a member's refusal")
    expect(not OutboxEvent.objects.filter(aggregate_id=marker).exists(), "rolled back whole")
    expect(media.delivery_reference(UUID(photo)).outcome == "read", "reads take no pointer")
    return (
        f"{len(transactions)} transactions locked their pointers in name order; a lock out of"
        " order is an internal error that rolls back"
    )


@case("media.no_key_original_or_bytes_in_any_response", "12", "D10", "D17")
def media_disclosure(ctx: ProfileContext) -> str:
    from glow_persistence.models import MediaObject
    from glow_profiles.media_fixtures import default_storage

    member = ctx.member()
    ctx.approved_photo(member)
    keys = list(MediaObject.objects.values_list("key", flat=True))
    tokens = [credential.token for credential in default_storage().credentials.values()]
    served = json.dumps(ctx.served) + "\n".join(ctx.headers)
    expect(keys and tokens, "the run made objects and credentials")
    expect(not [key for key in keys if key in served], "no response holds an object key")
    expect(not [token for token in tokens if token in served], "nor the store's credential")
    for data in default_storage().objects.values():
        expect(data.hex()[:48] not in served, "nor a photo's bytes")
    references = [
        item["approved_delivery_ref"]
        for item in ctx.media(member)["items"]
        if item["approved_delivery_ref"]
    ]
    expect(references, "an approved photo's reference is served to its owner")
    for reference in references:
        ctx.values.add(reference)
    return f"{len(keys)} object keys and {len(tokens)} credentials served to no one"


@case("digests.keyed_and_not_reproducible_without_the_key", "12", "D17")
def digests(ctx: ProfileContext) -> str:
    import hashlib

    from django.conf import settings
    from django.utils.crypto import salted_hmac
    from glow_persistence.models import IdempotencyRecord
    from glow_profiles import idempotency

    member = ctx.ready_member()
    catalog = ctx.catalog(member)
    current = ctx.get(member, FIELDS, "own_profile_fields")["gender"]["version"]
    body = {
        "operation": "profile_field",
        "meta": {"idempotency_key": "digest-key", "expected_version": current},
        "policy_version": catalog["policy_version"],
        "field": "gender",
        "value_ids": ["non-binary"],
        "own_words": None,
        "shown": False,
    }
    ctx.data(ctx.command(member, FIELDS, body), "own_profile_fields", "saved")
    record = IdempotencyRecord.objects.get(
        actor_id=member.account_id, operation="profile_field.gender", key="digest-key"
    )
    canonical = idempotency.canonical(body)
    expect(len(record.request_digest) == 64, "64 hexadecimal characters")
    expect(record.request_digest != hashlib.sha256(canonical.encode()).hexdigest(), "not unkeyed")
    other_key = salted_hmac(
        idempotency.SALT_PREFIX + "profile_field.gender",
        canonical,
        secret="another-key-not-the-run's-" + "x" * 30,
        algorithm="sha256",
    ).hexdigest()
    expect(record.request_digest != other_key, "not reproducible without the run's key")
    keyed = salted_hmac(
        idempotency.SALT_PREFIX + "profile_field.gender",
        canonical,
        secret=settings.SECRET_KEY,
        algorithm="sha256",
    ).hexdigest()
    expect(record.request_digest == keyed, "it is the run's keyed digest")
    # Every command's stored digest (C2, finding 6): each record the run left, checked against
    # the command that committed it, under its own operation's salt.
    operations = set()
    checked = 0
    for stored in IdempotencyRecord.objects.all():
        intent = ctx.intents.get((str(stored.actor_id), stored.key))
        expect(intent is not None, f"{stored.operation}: the record's command is known")
        assert intent is not None
        text = idempotency.canonical(intent)
        expect(len(stored.request_digest) == 64, f"{stored.operation}: 64 characters")
        expect(
            stored.request_digest != hashlib.sha256(text.encode()).hexdigest(),
            f"{stored.operation}: not the unkeyed SHA-256",
        )
        expect(
            stored.request_digest
            == salted_hmac(
                idempotency.SALT_PREFIX + stored.operation,
                text,
                secret=settings.SECRET_KEY,
                algorithm="sha256",
            ).hexdigest(),
            f"{stored.operation}: keyed by the run's key, under its operation's salt",
        )
        operations.add(stored.operation.split(".")[0])
        checked += 1
    expect(operations == COMMAND_OPERATIONS, "every kind of command's digest is checked")
    return (
        f"every stored digest ({checked}, of {len(operations)} kinds of command) is keyed: not the"
        " unkeyed SHA-256 and not another key's"
    )


# Every kind of SV2 command that stores an idempotency record (a field's operation by its root).
COMMAND_OPERATIONS = {
    "profile",
    "profile_field",
    "preferences",
    "filters",
    "area",
    "consent",
    "sensitive_consent",
    "adult_check",
    "birth_input",
    "visibility",
    # SV2 Stage B: the member's photo commands (MediaIntent).
    "media",
}


def run_case(ctx: ProfileContext, entry: Case) -> tuple[bool, str]:
    from django.core.cache import cache

    cache.clear()
    ctx.identity.case_id = entry.case_id
    # SV2 Stage B, correction C2 (F4): the photos' keys, credentials and bytes join the value
    # ledger as the store writes them, and after the case from their rows and the store.
    ctx.watch_store()
    try:
        outcome = True, entry.run(ctx)
    except CaseFailed as failed:
        outcome = False, f"FAILED: {failed}"
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        outcome = False, f"ERROR: {type(exc).__name__}"
    try:
        ctx.hold_media()
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        return False, f"ERROR: the value ledger's photo values: {type(exc).__name__}"
    return outcome


def plan() -> tuple[str, ...]:
    return tuple(entry.case_id for entry in CASES)


_ = threading  # the lock cases' workers are threads (concurrency.Worker)
