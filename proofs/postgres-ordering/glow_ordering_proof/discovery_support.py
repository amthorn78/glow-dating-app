"""What the discovery cases share (SV3 Stage A; its brief's D14 and acceptance checks 1 to 6 and
12 to 14).

The cases' own members are built through SV1's sign-in and SV2's member routes, with SV2's suite's
own helpers (``profile_support.ProfileContext``, imported unchanged): synthetic members
(``@example.invalid``), each made ``visible`` through the routes, with the seeded chart and
identity verification SV2's suite writes in setup. Then:

- ``DiscoveryContext``: the page route, each served body checked against the contract's own schema
  (``schema_check.check_body``: an extra field, a count or a reason fails), and kept for the content
  checks (no area ID, coordinate, distance or birth date in any page);
- **Case isolation:** discovery reads the whole population, so every case begins with no
  ``visible`` profile: ``hide_everyone`` pauses every ``visible`` profile left by earlier cases, a
  direct write to the disposable database (test data, as SV2's suite seeds its rows), never an
  application writer;
- **Seeds in setup,** each named: the chart and identity rows SV2's suite seeds (``seed_chart``,
  ``seed_verified``); directional interactions and matches (D7's consumption is read, not written,
  in Stage A); a lagging age state or consent row (D3: ``visible`` can lag them); and the plans'
  population (Q13), written directly with every row completion requires;
- **Counters:** statements per page request (``count_statements``, through the connection's execute
  wrapper, which logs nothing) and compatibility port calls (``counting_port``);
- **The plans** (D14; DB11): each candidate query's ``EXPLAIN (ANALYZE, BUFFERS)``, run with a
  throwaway tie-break key, so no secret is in a plan's text.
"""

from __future__ import annotations

import json
import re
import secrets
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any
from uuid import UUID, uuid4

from glow_ordering_proof.identity_support import CaseFailed, Member, Reply, expect
from glow_ordering_proof.profile_support import (
    ProfileContext,
    ValueLedger,
    db_today,
)

PAGE = "/api/v1/discovery/page"
STAFF = "staff:discovery-proof"
REASON = "SV3-proof"
NEW_YORK = "35620"
PHILADELPHIA = "37980"
LOS_ANGELES = "31080"
CHICAGO = "16980"

__all__ = ["CaseFailed", "expect"]

AREA_ID = re.compile(r"\b[0-9]{5}\b")


@dataclass
class DiscoveryContext:
    profiles: ProfileContext
    # Every page body the route served, for the content checks.
    pages: list[dict[str, Any]] = field(default_factory=list)
    # Every member the suite built, by account, with what the case set up for them.
    areas: dict[str, str] = field(default_factory=dict)
    # Statements per page request, recorded by the bounds cases (D7).
    statements: dict[str, int] = field(default_factory=dict)
    # The recorded query plans (D14), by query.
    plans: dict[str, dict[str, Any]] = field(default_factory=dict)
    # The D8 measurement's record (what the two responses reveal).
    disclosure: dict[str, Any] = field(default_factory=dict)
    # Each member's profile ID, by account.
    profile_ids: dict[str, str] = field(default_factory=dict)
    # The case areas' internal points and the distances the cases compute: none may appear in any
    # page (D5). Kept apart from the value ledger, whose own words a card may show.
    private: ValueLedger = field(default_factory=ValueLedger)

    # -- members --------------------------------------------------------------------------

    def visible(self, *, birth_date: str | None = None, area: str = NEW_YORK) -> Member:
        """A ``visible`` member through SV1's and SV2's routes (``visible_member``), in ``area``."""
        member = self.profiles.visible_member(birth_date=birth_date)
        if area != NEW_YORK:
            self.profiles.data(self.profiles.area(member, area), "own_area", "the area")
            self.expect_visible(member)
        self.hold_area(area)
        self.areas[str(member.account_id)] = area
        return member

    def expect_visible(self, member: Member) -> None:
        state = self.profiles.get(member, "/api/v1/profile", "own_profile")["visibility"]
        expect(state == "visible", "the member is visible")

    def profile_id(self, member: Member) -> str:
        """The member's profile ID, read once through their own route (it never changes)."""
        key = str(member.account_id)
        if key not in self.profile_ids:
            found = self.profiles.get(member, "/api/v1/profile", "own_profile")["profile_id"]
            self.profile_ids[key] = str(found)
        return self.profile_ids[key]

    def hold_area(self, area_id: str) -> None:
        """The area's internal point joins the value ledger: it must appear in no output."""
        from glow_persistence.models import Area

        row = Area.objects.filter(area_id=area_id).values_list("latitude", "longitude").first()
        expect(row is not None, "the case's area exists")
        assert row is not None
        for value in row:
            self.profiles.values.add(str(value))
            self.private.add(str(value))

    # -- the page route -------------------------------------------------------------------

    def page_reply(
        self,
        member: Member,
        collection: str = "recommendations",
        cursor: str | None = None,
        limit: int = 50,
        **kw: Any,
    ) -> Reply:
        body = {"collection": collection, "cursor": cursor, "limit": limit}
        return self.profiles.call(member, "POST", PAGE, body, **kw)

    def page(
        self,
        member: Member,
        collection: str = "recommendations",
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        reply = self.page_reply(member, collection, cursor, limit)
        data = self.profiles.data(reply, "candidate_card_page", f"the {collection} page")
        expect(data["collection"] == collection, "the page names its collection")
        self.check_page(data)
        self.pages.append(data)
        return data

    def stale(self, member: Member, collection: str, cursor: str | None, what: str) -> Reply:
        reply = self.page_reply(member, collection, cursor)
        self.profiles.refused(reply, 409, "stale_version", what)
        return reply

    def pages_of(
        self, member: Member, collection: str = "recommendations", limit: int = 50
    ) -> list[dict[str, Any]]:
        """Every page of a fresh batch, following its cursors to the end."""
        found = [self.page(member, collection, None, limit)]
        while found[-1]["next_cursor"] is not None:
            expect(len(found) <= 100, "a batch's pages end")
            found.append(self.page(member, collection, found[-1]["next_cursor"], limit))
        return found

    @staticmethod
    def ids(page: dict[str, Any]) -> list[str]:
        return [str(card["profile_id"]) for card in page["items"]]

    def all_ids(self, pages: list[dict[str, Any]]) -> list[str]:
        return [profile for page in pages for profile in self.ids(page)]

    def sees(self, viewer: Member, collection: str = "recommendations") -> set[str]:
        return set(self.all_ids(self.pages_of(viewer, collection)))

    def check_page(self, data: dict[str, Any]) -> None:
        """D8 and D13 in every page: each card's profile ID twice and equal; no area ID; the card's
        own keys only (the schema check has refused any other field)."""
        for card in data["items"]:
            expect(card["profile_id"] == card["profile"]["profile_id"], "a card's IDs agree")
        text = json.dumps(data)
        expect(self.private.found_in(text) == 0, "a page carries no internal point or distance")
        for area_id in set(self.areas.values()):
            expect(
                re.search(rf"\b{area_id}\b", text) is None,
                "a page carries no member's area ID",
            )

    # -- isolation and seeds ---------------------------------------------------------------

    @staticmethod
    def hide_everyone() -> int:
        """Case isolation: every ``visible`` profile left by earlier cases is paused, in the
        disposable database (test data, never an application writer)."""
        from glow_persistence.models import Profile

        return int(Profile.objects.filter(state="visible").update(state="paused"))

    @staticmethod
    def publish(name: str, content: Any) -> Any:
        from glow_profiles import staff

        result = staff.publish_setting(
            name, content, staff_subject=STAFF, reason=REASON, request_id=uuid4()
        )
        expect(result.outcome == "applied", f"the suite's publication of {name} applies")
        return result

    @staticmethod
    def current_label(name: str) -> str:
        from glow_profiles import settings_store

        return str(settings_store.read_unlocked(name).policy_version)

    @staticmethod
    def current(name: str) -> dict[str, Any]:
        from glow_profiles import settings_store

        content: dict[str, Any] = json.loads(json.dumps(settings_store.read_unlocked(name).content))
        return content

    def set_sets(self, member: Member, sets: dict[str, list[str]]) -> None:
        self.profiles.data(self.profiles.sets(member, sets), "own_preferences", "the sets")

    def set_filters(
        self,
        member: Member,
        *,
        minimum: int = 18,
        maximum: int | None = None,
        distance: str = "anywhere",
    ) -> None:
        current = self.profiles.get(member, "/api/v1/profile/filters", "own_filters")
        body = {
            "operation": "filters",
            "meta": self.profiles.meta(current["version"]),
            "policy_version": self.profiles.catalog(member)["policy_version"],
            "minimum_age": minimum,
            "maximum_age": maximum,
            "distance_choice": distance,
        }
        reply = self.profiles.command(member, "/api/v1/profile/filters", body)
        self.profiles.data(reply, "own_filters", "the filters")

    def set_field(self, member: Member, name: str, values: list[str], **kw: Any) -> None:
        reply = self.profiles.field(member, name, values, **kw)
        self.profiles.data(reply, "own_profile_fields", f"the {name} field")

    def accept_sensitive(self, member: Member) -> None:
        self.profiles.data(
            self.profiles.sensitive(member, "accepted"), "sensitive_consent", "sensitive consent"
        )

    @staticmethod
    def seed_interaction(actor: UUID, target: UUID, state: str) -> None:
        """D7 (Q5): a directional interaction, written in setup; no Stage A code writes one."""
        from glow_persistence.models import DirectionalInteraction

        DirectionalInteraction.objects.create(
            actor_id=actor, target_id=target, state=state, policy_version="fixture:sv3-seed"
        )

    @staticmethod
    def seed_match(first: UUID, second: UUID, state: str) -> None:
        """D7 (Q5): a match on the canonical pair, written in setup; no Stage A code writes one."""
        from glow_persistence.models import Match

        low, high = sorted((first, second))
        Match.objects.create(account_low_id=low, account_high_id=high, state=state)

    @staticmethod
    def block(actor: UUID, target: UUID) -> None:
        """A block through ``glow_chat``'s reviewed writer (Stage A has no block route)."""
        from glow_profiles import operations

        result = operations.chat().block(actor, target)
        expect(result.outcome == "applied", "the block applies")

    @staticmethod
    def unblock(actor: UUID, target: UUID) -> None:
        from glow_profiles import operations

        result = operations.chat().unblock(actor, target)
        expect(result.outcome == "applied", "the unblock applies")

    # -- counters ---------------------------------------------------------------------------

    @staticmethod
    @contextmanager
    def count_statements() -> Iterator[list[int]]:
        """The statements this thread's connection runs inside the block (none is logged)."""
        from django.db import connection

        counted = [0]

        def count(execute: Callable[..., Any], sql: str, params: Any, many: bool, ctx: Any) -> Any:
            counted[0] += 1
            return execute(sql, params, many, ctx)

        with connection.execute_wrapper(count):
            yield counted

    @staticmethod
    @contextmanager
    def counting_port(case: str | None = "explicitly-synthetic-ready") -> Iterator[list[int]]:
        """The compatibility port the pages use, counting its calls; ``case`` selects the fixture's
        case (``None``: no port selected, the runtime's case)."""
        from unittest import mock

        from django.test import override_settings
        from glow_discovery import policy

        calls = [0]
        real = policy.compatibility_port

        class Counting:
            def __init__(self, inner: Any) -> None:
                self.inner = inner

            def evaluate_pair(self, request: Any) -> Any:
                calls[0] += 1
                return self.inner.evaluate_pair(request)

        def port() -> Any:
            inner = real()
            return None if inner is None else Counting(inner)

        with (
            override_settings(GLOW_DISCOVERY_COMPATIBILITY_FIXTURE=case),
            mock.patch.object(policy, "compatibility_port", port),
        ):
            yield calls


# -- the expected card (D13), from the candidate's own rows -------------------------------------


def expected_details(account_id: UUID) -> dict[str, Any]:
    """What the card must show of the candidate: ``displayed`` over their field rows, and their
    area's name, read from the disposable database."""
    from glow_discovery import contract
    from glow_persistence.models import Area, Profile, ProfileFieldChoice

    rows = {
        row.field: {"value_ids": row.value_ids, "own_words": row.own_words, "shown": row.shown}
        for row in ProfileFieldChoice.objects.filter(account_id=account_id)
    }
    profile = Profile.objects.get(account_id=account_id)
    name = Area.objects.filter(pk=profile.area_id).values_list("name", flat=True).first()
    found: dict[str, Any] | None = contract.details(rows, name)
    assert found is not None
    return found


def expected_refs(account_id: UUID) -> list[str]:
    """The candidate's approved photos' references, through SV2's ``delivery_reference``."""
    from glow_persistence.models import MediaAsset
    from glow_profiles import media

    refs: list[str] = []
    for asset_id in (
        MediaAsset.objects.filter(account_id=account_id, state="approved")
        .order_by("position")
        .values_list("id", flat=True)
    ):
        result = media.delivery_reference(asset_id)
        reference = result.detail.get("delivery_ref") if result.ok else None
        if isinstance(reference, str):
            refs.append(reference)
    return refs


# -- the plans' population (Q13): every row completion requires, written directly ------------


def seed_population(count: int, areas: tuple[str, ...], consent_label: str) -> list[UUID]:
    """``count`` visible members written directly in setup, each with every row SV2's completion
    reads (onboarding consent at the current version, the adult age state with its date, a profile
    with a summary and an area, gender and "looking for", an approved photo, a resolved chart and an
    identity verification), every "show me" set at all and the launch filters. Their emails are
    synthetic (``@example.invalid``) and their passwords unusable; none signs in."""
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from glow_persistence.models import (
        AccountAgeState,
        AppAccount,
        Area,
        BirthInput,
        ConsentDecision,
        EngineIdentity,
        IdentityVerification,
        MediaAsset,
        Preferences,
        PreferenceSetEntry,
        Profile,
        ProfileFieldChoice,
    )

    now = timezone.now()
    today = db_today()
    tag = secrets.token_hex(3)
    area_rows = {row.area_id: row for row in Area.objects.filter(area_id__in=areas)}
    users = get_user_model().objects.bulk_create(
        [
            get_user_model()(
                username=f"population-{tag}-{i}",
                email=f"population-{tag}-{i}@example.invalid",
                password="!" + secrets.token_hex(20),
            )
            for i in range(count)
        ]
    )
    accounts = AppAccount.objects.bulk_create(
        [AppAccount(auth_user_id=user.pk, state="active") for user in users]
    )
    ids = [UUID(str(account.id)) for account in accounts]

    def born(i: int) -> date:
        return today - timedelta(days=365 * (20 + i % 40) + 40 + i % 300)

    AccountAgeState.objects.bulk_create(
        [
            AccountAgeState(
                account_id=a,
                state="self_declared_adult",
                method="self_declaration",
                recorded_at=now,
                policy_version="adult.self-declaration.v1",
                birth_date=born(i),
            )
            for i, a in enumerate(ids)
        ]
    )
    ConsentDecision.objects.bulk_create(
        [
            ConsentDecision(
                account_id=a,
                purpose="onboarding",
                policy_version=consent_label,
                state="accepted",
                decided_at=now,
                version=1,
            )
            for a in ids
        ]
    )
    Profile.objects.bulk_create(
        [
            Profile(
                account_id=a,
                display_name=f"Population Member {i}",
                bio="A synthetic seeded member.",
                area=area_rows[areas[i % len(areas)]],
                state="visible",
            )
            for i, a in enumerate(ids)
        ]
    )
    Preferences.objects.bulk_create(
        [
            Preferences(account_id=a, minimum_age=18, maximum_age=None, distance_choice="anywhere")
            for a in ids
        ]
    )
    PreferenceSetEntry.objects.bulk_create(
        [
            PreferenceSetEntry(account_id=a, field=f, value_id="all")
            for a in ids
            for f in ("gender", "orientation", "looking_for", "relationship_status")
        ]
    )
    genders = ("woman", "man", "non-binary")
    ProfileFieldChoice.objects.bulk_create(
        [
            row
            for i, a in enumerate(ids)
            for row in (
                ProfileFieldChoice(
                    account_id=a,
                    field="gender",
                    value_ids=[genders[i % 3]],
                    setting_version=1,
                    shown=True,
                ),
                ProfileFieldChoice(
                    account_id=a,
                    field="looking_for",
                    value_ids=["long-term"],
                    setting_version=1,
                    shown=True,
                ),
            )
        ]
    )
    MediaAsset.objects.bulk_create(
        [
            MediaAsset(
                account_id=a,
                provider="fixture",
                storage_ref=secrets.token_hex(16),
                approved_variant_ref="delivery-" + secrets.token_hex(16),
                position=0,
                state="approved",
                review_ref=uuid4(),
                detection="no_detector",
            )
            for a in ids
        ]
    )
    inputs = BirthInput.objects.bulk_create(
        [
            BirthInput(
                account_id=a,
                birth_date=born(i),
                local_time="04:13:27",
                time_precision="known",
                place_label="Synthetic Seeded Place",
                consent_version=consent_label,
                state="resolved",
            )
            for i, a in enumerate(ids)
        ]
    )
    EngineIdentity.objects.bulk_create(
        [
            EngineIdentity(
                account_id=row.account_id,
                birth_input=row,
                engine_reference=f"fixture:engine-reference-{tag}-{i}",
                state="resolved",
                engine_version="fixture:engine-version",
                contract_version="fixture:contract-version",
                adapter_version="fixture:adapter-version",
            )
            for i, row in enumerate(inputs)
        ]
    )
    IdentityVerification.objects.bulk_create(
        [
            IdentityVerification(
                account_id=a,
                state="verified",
                method="automated_check",
                provider_reference=f"fixture:verification-{tag}-{i}",
                decided_at=now,
            )
            for i, a in enumerate(ids)
        ]
    )
    return ids


def explain(statement: str, values: dict[str, Any]) -> dict[str, Any]:
    """``EXPLAIN (ANALYZE, BUFFERS)`` of one statement with a throwaway tie-break key (the real
    pads are secrets); the plan's text, its execution time and the node types it uses."""
    from django.db import connection

    throwaway = dict(values)
    throwaway["ipad"], throwaway["opad"] = secrets.token_bytes(64), secrets.token_bytes(64)
    with connection.cursor() as cursor:
        cursor.execute("EXPLAIN (ANALYZE, BUFFERS) " + statement, throwaway)
        lines = [str(row[0]) for row in cursor.fetchall()]
    timing = [line for line in lines if line.startswith("Execution Time")]
    nodes = sorted(
        {
            match.group(1).strip()
            for line in lines
            if (
                match := re.match(
                    r"\s*(?:->\s*)?([A-Z][A-Za-z ]+?)(?: on | using |  \(|\s\()", line
                )
            )
        }
    )
    return {"plan": lines, "execution": timing[0] if timing else "", "nodes": nodes}
