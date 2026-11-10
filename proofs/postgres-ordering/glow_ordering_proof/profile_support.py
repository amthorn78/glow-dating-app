"""What the profile cases share (SV2 Stage A; its brief's D12 and acceptance checks 1 to 9, 11
and 12).

It signs members in through SV1's identity routes with the identity suite's own helpers
(``identity_support``, imported unchanged): synthetic members (``@example.invalid``), the fixture
mail's codes, and Django's test client. Then:

- ``ValueLedger``: every member value the run sends that must appear in no output (coordinates,
  birth dates, times and places, own words, sensitive field values). It holds them only to show
  that none is ever logged, printed or written; it never prints one.
- ``ProfileContext``: the member routes, each served body checked against its DTO with the
  contract's own schema (``schema_check.check_body``), so an extra field fails; and helpers that
  drive a member to each state through the routes.
- **The test's seeds** (D8, D18): a resolved chart (both resolution states ``resolved``, the
  mapping's ``engine_reference``, ``engine_version``, ``contract_version`` and ``adapter_version``
  each beginning ``fixture:``) and a ``verified`` identity verification (a ``fixture:``
  reference), each written in the case's own setup through the ORM in the disposable database.
  No SV2 code writes either.
"""

from __future__ import annotations

import json
import re
import secrets
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any
from uuid import UUID, uuid4

from glow_ordering_proof.identity_support import (
    CaseFailed,
    Context,
    Member,
    Reply,
    SecretLedger,
    expect,
)

PROFILE = "/api/v1/profile"
COMPLETION = "/api/v1/profile/completion"
VISIBILITY = "/api/v1/profile/visibility"
FIELDS = "/api/v1/profile/fields"
PREFERENCES = "/api/v1/profile/preferences"
FILTERS = "/api/v1/profile/filters"
AREA = "/api/v1/profile/area"
NEAREST = "/api/v1/profile/area/nearest"
CATALOG = "/api/v1/profile/catalog"
CONSENT = "/api/v1/consent"
SENSITIVE = "/api/v1/consent/sensitive"
ADULT = "/api/v1/eligibility/adult"
BIRTH = "/api/v1/birth-input"

STAFF = "staff:profile-proof"
# Synthetic test values the suite publishes into the lists (no launch value is changed): OD-60
# names no orientation list, so the suite publishes fixture values to exercise the field.
ORIENTATION_VALUES = ("fixture-orientation-a", "fixture-orientation-b", "fixture-orientation-c")
RELATIONSHIP_VALUE = "fixture-relationship-z"
NEW_YORK = "35620"
LOS_ANGELES = "31080"

__all__ = ["CaseFailed", "expect"]


ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
ISO_TIME = re.compile(r"[0-9]{2}:[0-9]{2}:[0-9]{2}")
DECIMAL = re.compile(r"-?[0-9]+\.[0-9]{4,}")
# The coarsest precision a coordinate is searched at: three decimals, about 110 metres, finer
# than the state laws' precise geolocation (1,750 or 1,850 feet; the recheck record).
COARSEST_DECIMALS = 3


def forms(value: str) -> tuple[str, ...]:
    """Every form the code could print ``value`` in (C2, finding 5): as sent and as JSON escapes
    it; a date also as Python's ``repr``, compact, numeric and in prose ("29 February 2008"); a
    time as Python's ``repr``; a coordinate also without its sign, and rounded and truncated to
    every lower precision down to three decimals. Forms shorter than five characters are not
    searched."""
    found = {value, json.dumps(value)[1:-1]}
    if ISO_DATE.fullmatch(value):
        try:
            day = date.fromisoformat(value)
        except ValueError:
            day = None
        if day is not None:
            month = MONTHS[day.month - 1]
            found |= {
                f"date({day.year}, {day.month}, {day.day})",
                f"{day.year:04d}{day.month:02d}{day.day:02d}",
                f"{day.day} {month} {day.year}",
                f"{day.day:02d} {month} {day.year}",
                f"{month} {day.day}, {day.year}",
                f"{day.day:02d}/{day.month:02d}/{day.year}",
                f"{day.month:02d}/{day.day:02d}/{day.year}",
                f"{day.day}.{day.month}.{day.year}",
            }
    elif ISO_TIME.fullmatch(value):
        hour, minute, second = (int(part) for part in value.split(":"))
        found.add(f"time({hour}, {minute}, {second})")
    elif DECIMAL.fullmatch(value):
        unsigned = value.lstrip("-")
        decimals = len(unsigned.split(".")[1])
        for text in (value, unsigned):
            found.add(text)
            for places in range(COARSEST_DECIMALS, decimals):
                found.add(f"{float(text):.{places}f}")
                found.add(text[: text.index(".") + 1 + places])
    return tuple(sorted(form for form in found if len(form) >= 5))


MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


class ValueLedger:
    """Member values the run handles that must appear in no output, in any of their forms."""

    def __init__(self) -> None:
        self._values: dict[str, tuple[str, ...]] = {}
        self._lock = threading.Lock()

    def add(self, value: object) -> None:
        if isinstance(value, float):
            value = repr(value)
        if not isinstance(value, str) or len(value) < 5:
            return
        with self._lock:
            if value not in self._values:
                self._values[value] = forms(value)

    def count(self) -> int:
        with self._lock:
            return len(self._values)

    def found_in(self, text: str) -> int:
        """How many distinct values appear in ``text`` in any of their forms (``forms``): as
        sent, as JSON escapes them (a non-ASCII value in a JSON body), as Python prints a date or
        a time, a date in prose, a coordinate at a lower precision. The values are never
        returned."""
        with self._lock:
            held = tuple(self._values.values())
        return sum(1 for found in held if any(form in text for form in found))


@dataclass
class ProfileContext:
    identity: Context
    values: ValueLedger
    # Every body a member route served, for the content checks (no coordinate, no distance).
    served: list[dict[str, Any]] = field(default_factory=list)
    # Every response's headers, as text, for the value scan (D5: no coordinate in a header).
    headers: list[str] = field(default_factory=list)
    # Every command that committed, by actor and key, so that every stored idempotency digest
    # can be checked against its own command (C2, finding 6).
    intents: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    _keys: Iterator[int] = field(default_factory=lambda: iter(range(1, 10_000_000)))

    @property
    def ledger(self) -> SecretLedger:
        return self.identity.ledger

    # -- members and requests ---------------------------------------------------------------

    def member(self) -> Member:
        return self.identity.member()

    def key(self) -> str:
        return f"k{next(self._keys)}"

    def call(
        self,
        member: Member,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        *,
        bearer: str | None | bool = True,
        headers: dict[str, str] | None = None,
        content_type: str | None = None,
    ) -> Reply:
        # As SV1's device sends a request (``identity_support.Device.call``), keeping the
        # response, so that its headers are read too. No profile route returns a credential.
        token = member.device.access if bearer is True else (bearer or None)
        sent = dict(headers or {})
        if token:
            sent["Authorization"] = f"Bearer {token}"
        response = member.device.client.generic(
            method,
            path,
            data=b"" if body is None else _json(body),
            content_type=content_type or "application/json",
            headers=sent,
        )
        reply = Reply(response.status_code, _parsed(response))
        if method == "POST" and reply.status == 200 and body is not None:
            self.remember(member.account_id, body)
        self.headers.append("\n".join(f"{name}: {value}" for name, value in response.items()))
        if reply.body is not None:
            self.served.append(reply.body)
        return reply

    def remember(self, account_id: UUID, intent: dict[str, Any]) -> None:
        """A command that committed (through a route, or called directly by a case): the first
        intent under its actor and key is the one its record binds."""
        key = (intent.get("meta") or {}).get("idempotency_key")
        if isinstance(key, str):
            self.intents.setdefault((str(account_id), key), intent)

    @staticmethod
    def data(reply: Reply, kind: str, what: str) -> dict[str, Any]:
        """The reply's data, after the body is checked against the contract (D17)."""
        from glow_ordering_proof.schema_check import check_body

        expect(reply.status == 200, f"{what}: answers 200")
        expect(not check_body("AppResponse", reply.body), f"{what}: the body is its DTO")
        data = (reply.body or {}).get("data")
        expect(isinstance(data, dict) and data.get("kind") == kind, f"{what}: is {kind}")
        assert isinstance(data, dict)
        return data

    @staticmethod
    def refused(reply: Reply, status: int, code: str, what: str) -> None:
        from glow_ordering_proof.schema_check import check_body

        expect(reply.status == status, f"{what}: answers {status}")
        expect(not check_body("Error", reply.body), f"{what}: the body is the contract's Error")
        expect((reply.body or {}).get("code") == code, f"{what}: the code is {code}")

    # -- reads --------------------------------------------------------------------------------

    def catalog(self, member: Member) -> dict[str, Any]:
        return self.data(self.call(member, "GET", CATALOG), "profile_catalog", "the catalog")

    def get(self, member: Member, path: str, kind: str) -> dict[str, Any]:
        return self.data(self.call(member, "GET", path), kind, f"GET {path}")

    # -- commands through the routes --------------------------------------------------------

    def command(self, member: Member, path: str, body: dict[str, Any]) -> Reply:
        return self.call(member, "POST", path, body)

    def meta(self, expected: int) -> dict[str, Any]:
        return {"idempotency_key": self.key(), "expected_version": expected}

    def accept_onboarding(self, member: Member) -> dict[str, Any]:
        current = self.get(member, CONSENT, "onboarding")
        version = self.catalog(member)["consents"]["onboarding"]["policy_version"]
        body = {
            "operation": "consent",
            "meta": self.meta(current["version"]),
            "policy_version": version,
            "decision": "accepted",
        }
        return self.data(self.command(member, CONSENT, body), "onboarding", "consent accepted")

    def withdraw_onboarding(self, member: Member) -> Reply:
        current = self.get(member, CONSENT, "onboarding")
        version = self.catalog(member)["consents"]["onboarding"]["policy_version"]
        return self.command(
            member,
            CONSENT,
            {
                "operation": "consent",
                "meta": self.meta(current["version"]),
                "policy_version": version,
                "decision": "withdrawn",
            },
        )

    def sensitive(self, member: Member, decision: str) -> Reply:
        current = self.get(member, SENSITIVE, "sensitive_consent")
        version = self.catalog(member)["consents"]["sensitive_profile"]["policy_version"]
        return self.command(
            member,
            SENSITIVE,
            {
                "operation": "sensitive_consent",
                "meta": self.meta(current["version"]),
                "policy_version": version,
                "decision": decision,
            },
        )

    def adult(self, member: Member, birth_date: str) -> Reply:
        current = self.get(member, ADULT, "own_age_state")
        self.values.add(birth_date)
        return self.command(
            member,
            ADULT,
            {
                "operation": "adult_check",
                "meta": self.meta(current["version"]),
                "birth_date": birth_date,
            },
        )

    def birth_input(
        self,
        member: Member,
        birth_date: str,
        *,
        local_time: str | None = "04:13:27",
        precision: str = "known",
        expected: int | None = None,
        place: str | None = None,
    ) -> Reply:
        return self.command(
            member,
            BIRTH,
            self.birth_body(
                member,
                birth_date,
                local_time=local_time,
                precision=precision,
                expected=expected,
                place=place,
            ),
        )

    def birth_body(
        self,
        member: Member,
        birth_date: str,
        *,
        local_time: str | None = "04:13:27",
        precision: str = "known",
        expected: int | None = None,
        place: str | None = None,
    ) -> dict[str, Any]:
        """A birth input command's body, with a new key; its values go to the ledger."""
        if expected is None:
            current = self.call(member, "GET", BIRTH)
            expected = (
                0
                if current.status == 404
                else self.data(current, "birth_input", "the birth input")["version"]
            )
        place = place or f"Synthetic Place {secrets.token_hex(3)}"
        for value in (birth_date, local_time, place):
            self.values.add(value)
        return {
            "operation": "birth_input",
            "meta": self.meta(expected),
            "input": {
                "birth_date": birth_date,
                "local_time": local_time,
                "time_precision": precision,
                "place_label": place,
                "timezone_name": None,
                "timezone_provenance": None,
            },
        }

    def profile(self, member: Member, summary: str = "A synthetic member.") -> Reply:
        current = self.call(member, "GET", PROFILE)
        expected = (
            0 if current.status == 404 else self.data(current, "own_profile", "profile")["version"]
        )
        return self.command(
            member,
            PROFILE,
            {
                "operation": "profile",
                "meta": self.meta(expected),
                "display_name": "Synthetic Member",
                "summary": summary,
            },
        )

    def field(
        self,
        member: Member,
        name: str,
        values: list[str],
        *,
        own_words: str | None = None,
        shown: bool | None = None,
        expected: int | None = None,
        policy_version: str | None = None,
    ) -> Reply:
        if expected is None:
            expected = self.get(member, FIELDS, "own_profile_fields")[name]["version"]
        if policy_version is None:
            policy_version = self.catalog(member)["policy_version"]
        if own_words is not None:
            self.values.add(own_words)
        return self.command(
            member,
            FIELDS,
            {
                "operation": "profile_field",
                "meta": self.meta(expected),
                "policy_version": policy_version,
                "field": name,
                "value_ids": values,
                "own_words": own_words,
                "shown": (name == "looking_for") if shown is None else shown,
            },
        )

    def sets(self, member: Member, sets: dict[str, list[str]]) -> Reply:
        current = self.get(member, PREFERENCES, "own_preferences")
        return self.command(
            member,
            PREFERENCES,
            {
                "operation": "preferences",
                "meta": self.meta(current["version"]),
                "policy_version": self.catalog(member)["policy_version"],
                "selections": [
                    {"dimension": name, "accepted_option_ids": sets.get(name, ["all"])}
                    for name in ("gender", "orientation", "looking_for", "relationship_status")
                ],
            },
        )

    def area(self, member: Member, area_id: str) -> Reply:
        current = self.get(member, PROFILE, "own_profile")
        return self.command(
            member,
            AREA,
            {"operation": "area", "meta": self.meta(current["version"]), "area_id": area_id},
        )

    # -- composite states -------------------------------------------------------------------

    def adult_date(self, years: int = 30) -> str:
        today = db_today()
        try:
            born = today.replace(year=today.year - years)
        except ValueError:
            born = today.replace(year=today.year - years, day=28)
        return (born - timedelta(days=37)).isoformat()

    def ready_member(self, *, birth_date: str | None = None) -> Member:
        """A member with every requirement but the seeded ones and the completing edit: onboarding
        consent, the adult check, a birth input, a profile, a gender, "looking for" and an area."""
        member = self.member()
        born = birth_date or self.adult_date()
        self.accept_onboarding(member)
        self.data(self.adult(member, born), "own_age_state", "the adult check")
        self.data(self.birth_input(member, born), "birth_input", "the birth input")
        self.data(self.profile(member), "own_profile", "the profile")
        self.data(self.field(member, "gender", ["woman"]), "own_profile_fields", "gender")
        self.data(
            self.field(member, "looking_for", ["long-term"]), "own_profile_fields", "looking for"
        )
        self.data(self.area(member, NEW_YORK), "own_area", "the area")
        return member

    def visible_member(self, *, birth_date: str | None = None) -> Member:
        """A ``visible`` member: ``ready_member``, the two seeds, then the completing edit."""
        member = self.ready_member(birth_date=birth_date)
        seed_chart(member.account_id)
        seed_verified(member.account_id)
        done = self.data(self.profile(member), "own_profile", "the completing edit")
        expect(done["visibility"] == "visible", "the completing edit makes the profile visible")
        return member

    def missing(self, member: Member) -> list[str]:
        return list(self.get(member, COMPLETION, "own_completion")["missing"])

    # -- staff (no route; P07's console calls these) ------------------------------------------

    @staticmethod
    def publish(name: str, content: Any) -> Any:
        from glow_profiles import staff

        return staff.publish_setting(
            name, content, staff_subject=STAFF, reason="SV2-proof", request_id=uuid4()
        )

    def ensure_test_lists(self) -> None:
        """The suite's synthetic orientation and relationship values, published once through the
        settings store, so the sensitive fields can be exercised."""
        import copy

        from glow_domain import profile_settings as ps
        from glow_profiles import settings_store

        for name, wanted in (
            (ps.ORIENTATION_LIST, ORIENTATION_VALUES),
            (ps.RELATIONSHIP_LIST, (RELATIONSHIP_VALUE,)),
        ):
            current = settings_store.read_unlocked(name)
            have = {value["id"] for value in current.content["values"]}
            missing = [value for value in wanted if value not in have]
            if missing:
                content = copy.deepcopy(current.content)
                content["values"] += [
                    {"id": value, "label": f"Fixture value {index}", "retired": False}
                    for index, value in enumerate(missing, start=1)
                ]
                result = self.publish(name, content)
                expect(result.outcome == "applied", f"the suite's test values publish in {name}")
        for value in (*ORIENTATION_VALUES, RELATIONSHIP_VALUE):
            self.values.add(value)


def _json(body: dict[str, Any]) -> bytes:
    return json.dumps(body).encode("utf-8")


def _parsed(response: Any) -> dict[str, Any] | None:
    if not response.get("Content-Type", "").startswith("application/json"):
        return None
    try:
        value = json.loads(response.content.decode("utf-8"))
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def db_today() -> date:
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT (clock_timestamp() AT TIME ZONE 'UTC')::date")
        value = cursor.fetchone()[0]
    assert isinstance(value, date)
    return value


def years_ago(years: int, *, days: int = 0) -> str:
    today = db_today()
    try:
        then = today.replace(year=today.year - years)
    except ValueError:
        # 29 February in a common year: P04's rule puts the birthday on 1 March.
        then = today.replace(year=today.year - years, month=3, day=1)
    return (then + timedelta(days=days)).isoformat()


# -- the test's seeds (D8, D18): test data in the disposable database, never app code ---------


def seed_chart(account_id: UUID) -> None:
    from glow_persistence.models import BirthInput, EngineIdentity

    current = BirthInput.objects.filter(account_id=account_id).order_by("-version").first()
    expect(current is not None, "the member has a birth input to seed a chart for")
    assert current is not None
    current.state = "resolved"
    current.save(update_fields=["state", "updated_at"])
    tag = secrets.token_hex(4)
    EngineIdentity.objects.update_or_create(
        account_id=account_id,
        defaults={
            "birth_input": current,
            "state": "resolved",
            "engine_reference": f"fixture:engine-reference-{tag}",
            "engine_version": "fixture:engine-version",
            "contract_version": "fixture:contract-version",
            "adapter_version": "fixture:adapter-version",
        },
    )


def seed_verified(account_id: UUID) -> None:
    from django.utils import timezone
    from glow_persistence.models import IdentityVerification

    IdentityVerification.objects.update_or_create(
        account_id=account_id,
        defaults={
            "state": "verified",
            "method": "automated_check",
            "provider_reference": f"fixture:verification-{secrets.token_hex(4)}",
            "staff_subject": None,
            "reason": None,
            "decided_at": timezone.now(),
        },
    )
