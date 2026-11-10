"""The profile cases (SV2 Stage A; its brief's acceptance checks 1 to 9, 11 and 12, with D2 to
D9, D11, D13, D17 and D18), each run through the HTTP endpoints with Django's test client on the
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
    ProfileContext,
    expect,
    seed_chart,
    seed_verified,
    years_ago,
)


@dataclass(frozen=True)
class Case:
    case_id: str
    checks: tuple[str, ...]
    run: Callable[[ProfileContext], str]


CASES: list[Case] = []


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
    """Which tables hold any of ``texts`` in any row (every column, as JSON text)."""
    from django.db import connection

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
    ctx.data(ctx.sensitive(member, "withdrawn"), "sensitive_consent", "withdrawn")
    rows = ProfileFieldChoice.objects.filter(account_id=member.account_id)
    expect(not rows.filter(field__in=("orientation", "relationship_status")).exists(), "removed")
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
    return "values, own words, narrowed sets and the commands' records removed; sets reset"


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
    return "18 today and 29 February 2008 pass through the route; the fixtures' boundaries hold"


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
    data = ctx.data(ctx.adult(first, years_ago(17)), "own_age_state", "the corrected date")
    expect(data["state"] == "unknown" and data["birth_date"] is None, "unknown, the date cleared")
    row = AccountAgeState.objects.get(account_id=first.account_id)
    expect(row.state == "unknown" and row.birth_date is None, "stored as unknown with no date")
    expect(_profile_row(first.account_id).state == "incomplete", "the visible profile demoted")
    expect(send("send-adult-2").outcome == "refused", "so a send is refused")
    current = BirthInput.objects.filter(account_id=first.account_id).order_by("-version")[0]
    expect(current.state == "missing", "the birth input holding another date stops being current")
    return "a failing rerun sets unknown, clears the date and demotes; the send is refused"


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
    ctx.data(ctx.adult(member, years_ago(16)), "own_age_state", "a failing rerun")
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
    seed_chart(member.account_id)
    seed_verified(member.account_id)
    stays(member, ["area"], "the area")

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
                ctx.data(ctx.adult(member, years_ago(15)), "own_age_state", "failing rerun")
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
    ctx.data(ctx.adult(member, years_ago(16)), "own_age_state", "a failing rerun")
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
    demotions = {member.account_id: 0 for member in (by_area, by_field, by_adult, by_accept)}
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
    edits = _events(_profile_row(by_edit.account_id).pk, "profile_demoted")
    _edit(ctx, by_edit)
    demoted(by_edit, "the profile edit (the owner's edit)", event=False)
    expect(_events(_profile_row(by_edit.account_id).pk, "profile_demoted") == edits, "no event")
    # Accepting the new version is the last requirement again (F04 requirements_met).
    accepted = ctx.accept_onboarding(by_accept)
    expect(accepted["policy_version"] == current, "the new version accepted")
    expect(_profile_row(by_accept.account_id).state == "visible", "accepting it completes")
    ctx.data(ctx.area(by_accept, LOS_ANGELES), "own_area", "an area change, now current")
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
        "a lapsed consent version demoted at the area, a field, the adult check and the edit;"
        " its acceptance completed; paused, restricted and removed stayed"
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
# The schema's own refusals (the P11 plan's DB04, for SV2's tables)
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
# Acceptance check 12: the stored digests (D17); the scans run after every case
# =============================================================================================


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
    return "the stored digest is keyed: not the unkeyed SHA-256 and not another key's"


def run_case(ctx: ProfileContext, entry: Case) -> tuple[bool, str]:
    from django.core.cache import cache

    cache.clear()
    ctx.identity.case_id = entry.case_id
    try:
        return True, entry.run(ctx)
    except CaseFailed as failed:
        return False, f"FAILED: {failed}"
    except BaseException as exc:  # noqa: BLE001 - recorded by type only; never a value
        return False, f"ERROR: {type(exc).__name__}"


def plan() -> tuple[str, ...]:
    return tuple(entry.case_id for entry in CASES)


_ = threading  # the lock cases' workers are threads (concurrency.Worker)
