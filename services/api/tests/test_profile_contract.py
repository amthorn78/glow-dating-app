"""SV2 Stage A, D11 and D17: the routes' contract.

- The server's closed request checks (``glow_profiles.contract``) decide every shared corpus case
  of their definitions as the contract's own validator (``packages/contracts/runtime.py``) does,
  and every case one change away from a valid one (each value replaced, a field removed or added,
  a list emptied or an entry repeated), through ``parse`` as well.
- Every projection validates as its DTO and inside ``AppResponse``; an extra field fails.
- A refusal names the field's path, never its value (the coordinates included).
"""

import importlib.util
import json
import unittest
import uuid
from collections.abc import Iterator
from datetime import date, time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from glow_domain import profile_fields as pf
from glow_domain import profile_settings as ps
from glow_profiles import contract

REPO_ROOT = Path(__file__).resolve().parents[3]


def runtime() -> Any:
    spec = importlib.util.spec_from_file_location(
        "glow_contract_runtime", REPO_ROOT / "packages" / "contracts" / "runtime.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CORPUS = json.loads((REPO_ROOT / "packages/contracts/corpus/shared-v1.json").read_text())["cases"]

# Values a field might be given instead of its own: each type, the bounds the DTOs use, blank and
# over-long text, an unpaired surrogate, a trailing newline, reserved IDs and malformed dates.
PROBES: tuple[Any, ...] = (
    None,
    True,
    False,
    0,
    1,
    -1,
    1.0,
    2.5,
    -0.0,
    17,
    18,
    150,
    151,
    2**53 - 1,
    2**53,
    "",
    " ",
    "x",
    "x" * 41,
    "x" * 81,
    "x" * 101,
    "x" * 201,
    "x" * 501,
    "\u3000",
    "a\ud800",
    "a\n",
    "all",
    "not-stated",
    "woman",
    "35620",
    "3562",
    "35620\n",
    "2000-02-29",
    "2001-02-29",
    "0000-01-01",
    "12:00:00",
    "24:00:00",
    "unknown",
    "known",
    "accepted",
    "withdrawn",
    "pause",
    [],
    ["all"],
    ["woman", "woman"],
    [f"value-{number}" for number in range(51)],
    [{}],
    {},
)


def _paths(value: Any, path: tuple[Any, ...] = ()) -> Iterator[tuple[Any, ...]]:
    yield path
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _paths(item, (*path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _paths(item, (*path, index))


def _at(value: Any, path: tuple[Any, ...]) -> Any:
    for step in path:
        value = value[step]
    return value


def _replace(value: Any, path: tuple[Any, ...], new: Any) -> Any:
    if not path:
        return new
    head, rest = path[0], path[1:]
    if isinstance(value, dict):
        return {**value, head: _replace(value[head], rest, new)}
    copy = list(value)
    copy[head] = _replace(value[head], rest, new)
    return copy


def variants(value: Any) -> Iterator[Any]:
    """Every value one change away from ``value``."""
    for path in _paths(value):
        current = _at(value, path)
        for probe in PROBES:
            yield _replace(value, path, probe)
        if isinstance(current, dict):
            yield _replace(value, path, {**current, "fixture_extra": 1})
            for key in current:
                yield _replace(value, path, {k: v for k, v in current.items() if k != key})
        if isinstance(current, list) and current:
            yield _replace(value, path, [*current, current[0]])
            yield _replace(value, path, [])


class RequestParityTests(unittest.TestCase):
    def test_the_server_decides_every_corpus_case_as_the_contract_does(self) -> None:
        validator = runtime()
        decided: set[tuple[str, bool]] = set()
        for row in CORPUS:
            if row["scope"] != "production" or row["definition"] not in contract.REQUESTS:
                continue
            with self.subTest(case=row["name"]):
                expected = validator.valid("production", row["definition"], row["value"])
                self.assertEqual(expected, row["valid"])
                self.assertEqual(contract.valid(row["definition"], row["value"]), expected)
                decided.add((row["definition"], expected))
        # Each definition has corpus cases both ways, so no definition passes by having none.
        self.assertEqual(
            decided, {(name, way) for name in contract.REQUESTS for way in (True, False)}
        )

    def test_the_server_decides_every_case_one_change_away_as_the_contract_does(self) -> None:
        validator = runtime()
        disagreements = []
        checked = 0
        for row in CORPUS:
            if (
                row["scope"] != "production"
                or row["definition"] not in contract.REQUESTS
                or not row["valid"]
            ):
                continue
            for value in variants(row["value"]):
                expected = validator.valid("production", row["definition"], value)
                served = contract.valid(row["definition"], value)
                try:
                    contract.parse(row["definition"], json.dumps(value).encode())
                    parsed = True
                except contract.Invalid:
                    parsed = False
                if not expected == served == parsed:
                    disagreements.append((row["name"], json.dumps(value)[:200]))
                checked += 1
        self.assertEqual(disagreements, [])
        self.assertGreater(checked, 5000)

    def test_an_integral_number_is_an_integer_as_the_contract_decides(self) -> None:
        body: dict[str, Any] = {
            "operation": "visibility",
            "meta": {"idempotency_key": "fixture-key", "expected_version": 2.0},
            "action": "pause",
        }
        self.assertTrue(runtime().valid("production", "VisibilityIntent", body))
        parsed = contract.parse("VisibilityIntent", json.dumps(body).encode())
        self.assertIs(type(parsed["meta"]["expected_version"]), int)
        self.assertEqual(parsed["meta"]["expected_version"], 2)
        body["meta"]["expected_version"] = 2.5
        self.assertFalse(contract.valid("VisibilityIntent", body))

    def test_every_request_the_routes_take_is_a_contract_definition(self) -> None:
        schema = runtime().SCHEMAS["production"]["$defs"]
        self.assertTrue(set(contract.REQUESTS) <= set(schema))
        self.assertEqual(
            set(contract.REQUESTS),
            {
                "ProfileIntent",
                "PreferencesIntent",
                "VisibilityIntent",
                "ConsentIntent",
                "BirthInputIntent",
                "ProfileFieldIntent",
                "FiltersIntent",
                "AreaIntent",
                "AreaQuery",
                "SensitiveConsentIntent",
                "AdultCheckIntent",
                # SV2 Stage B: F05's owner command, an existing DTO.
                "MediaIntent",
            },
        )

    def test_parse_refuses_what_json_or_the_dto_does_not_allow(self) -> None:
        for body in (
            b"{",
            b'{"latitude": NaN, "longitude": 0}',
            b'{"latitude": Infinity, "longitude": 0}',
            b'{"latitude": 1e999, "longitude": 0}',
            b"\xff\xfe",
            b"[]",
        ):
            with self.subTest(body=body[:12]):
                with self.assertRaises(contract.Invalid):
                    contract.parse("AreaQuery", body)
        self.assertEqual(
            contract.parse("AreaQuery", b'{"latitude": 40.5, "longitude": -74.25}'),
            {"latitude": 40.5, "longitude": -74.25},
        )

    def test_a_refusal_names_the_field_never_its_value(self) -> None:
        for body in (
            {"latitude": 91.7123457, "longitude": -74.0067891},
            {"latitude": "40.7123457", "longitude": -74.0067891},
            {"latitude": 40.7123457, "longitude": -74.0067891, "accuracy": 3},
        ):
            with self.subTest(body=body):
                with self.assertRaises(contract.Invalid) as raised:
                    contract.parse("AreaQuery", json.dumps(body).encode())
                text = str(raised.exception) + repr(raised.exception)
                for value in ("40.7123457", "74.0067891", "91.7123457"):
                    self.assertNotIn(value, text)
                self.assertTrue(raised.exception.path.startswith("AreaQuery"))


def _row(**values: Any) -> SimpleNamespace:
    return SimpleNamespace(**values)


class ProjectionTests(unittest.TestCase):
    """D17: each builder returns exactly its DTO's fields, which the contract validates."""

    def valid(self, definition: str, data: dict[str, Any]) -> None:
        validator = runtime()
        self.assertTrue(validator.valid("production", definition, data), definition)
        body = contract.app_response(data, contract.new_request_id())
        self.assertTrue(validator.valid("production", "AppResponse", body), definition)
        self.assertFalse(
            validator.valid("production", definition, {**data, "fixture_extra": 1}),
            f"{definition} must refuse an extra field",
        )

    def test_each_projection_validates_as_its_dto(self) -> None:
        catalog = {
            field: ps.field_list(
                field, ps.LAUNCH_DEFAULTS[name], ps.LAUNCH_DEFAULTS[ps.NARROWING], 1
            )
            for field, name in ps.LIST_SETTINGS.items()
        }
        version = ps.catalog_version({name: 1 for name in ps.CATALOG_SETTINGS})
        profile = _row(
            id=uuid.uuid4(),
            version=3,
            display_name="Synthetic Member",
            bio="A synthetic member.",
            state="visible",
        )
        self.valid("OwnProfile", contract.own_profile(profile))
        rows = {
            "gender": _row(version=2, value_ids=["woman"], own_words="Own words", shown=True),
            "looking_for": _row(version=1, value_ids=["casual"], own_words=None, shown=True),
        }
        fields = contract.own_profile_fields(rows, catalog, version)
        self.valid("OwnProfileFields", fields)
        self.assertEqual(fields["orientation"]["value_ids"], [pf.NOT_STATED])
        self.assertEqual(fields["orientation"]["version"], 0)
        preferences = _row(
            version=2,
            policy_version=version,
            minimum_age=18,
            maximum_age=None,
            distance_choice="anywhere",
        )
        self.valid("OwnPreferences", contract.own_preferences(preferences, {"gender": ["man"]}))
        self.valid("OwnFilters", contract.own_filters(preferences))
        area = _row(area_id="35620", name="New York-Newark-Jersey City, NY-NJ Metro Area")
        self.valid("OwnArea", contract.own_area(profile, area))
        self.valid("OwnArea", contract.own_area(profile, None))
        nearest = contract.nearest_area(area.area_id, area.name)
        self.valid("NearestArea", nearest)
        self.assertEqual(set(nearest), {"kind", "area_id", "area_name"})
        consents = {
            "onboarding": ("consent.onboarding.v1", "Development text."),
            "sensitive_profile": ("consent.sensitive_profile.v1", "Development text."),
        }
        self.valid(
            "ProfileCatalog",
            contract.profile_catalog(
                version,
                catalog,
                ps.LAUNCH_DEFAULTS[ps.AGE_RANGE],
                ps.LAUNCH_DEFAULTS[ps.LOCATION],
                consents,
            ),
        )
        self.valid("OwnCompletion", contract.own_completion(profile, ["chart"]))
        self.valid("OwnCompletion", contract.own_completion(None, ["consent", "profile_fields"]))
        decision = _row(version=2, state="accepted", policy_version="consent.onboarding.v1")
        self.valid("OnboardingEligibility", contract.onboarding_eligibility(decision, []))
        self.valid("OnboardingEligibility", contract.onboarding_eligibility(None, ["consent"]))
        self.valid("OwnSensitiveConsent", contract.sensitive_consent(None))
        self.valid("OwnSensitiveConsent", contract.sensitive_consent(decision))
        self.valid(
            "OwnAgeState", contract.own_age_state(_row(version=1, state="unknown", birth_date=None))
        )
        self.valid(
            "OwnAgeState",
            contract.own_age_state(
                _row(version=2, state="self_declared_adult", birth_date=date(1990, 6, 15))
            ),
        )
        revision = _row(
            id=uuid.uuid4(),
            version=2,
            birth_date=date(1990, 6, 15),
            local_time=time(4, 13, 27),
            time_precision="approximate",
            place_label="Synthetic Place",
            timezone_name=None,
            timezone_provenance=None,
            state="pending",
        )
        self.valid("OwnBirthInput", contract.own_birth_input(revision, None))
        mapping = _row(birth_input_id=revision.id, state="resolved", version=4)
        self.assertEqual(contract.own_birth_input(revision, mapping)["mapping_version"], 4)

    def test_the_catalog_returns_no_distance_radius_and_no_coordinate(self) -> None:
        location = dict(ps.LAUNCH_DEFAULTS[ps.LOCATION])
        location["distance_choices"] = [{"id": "near", "label": "Near", "miles": 25}]
        location["default_distance"] = "near"
        catalog = {
            field: ps.field_list(
                field, ps.LAUNCH_DEFAULTS[name], ps.LAUNCH_DEFAULTS[ps.NARROWING], 1
            )
            for field, name in ps.LIST_SETTINGS.items()
        }
        data = contract.profile_catalog(
            "catalog.1.1.1.1.1.1.1",
            catalog,
            ps.LAUNCH_DEFAULTS[ps.AGE_RANGE],
            location,
            {
                "onboarding": ("consent.onboarding.v1", "x"),
                "sensitive_profile": ("consent.sensitive_profile.v1", "x"),
            },
        )
        text = json.dumps(data)
        for word in ("miles", "25", "latitude", "longitude", "store_coordinates", "show_distance"):
            self.assertNotIn(word, text)

    def test_errors_validate_and_name_no_value(self) -> None:
        validator = runtime()
        for code in ("invalid_request", "forbidden", "not_found", "stale_version"):
            body = contract.error(code, contract.new_request_id())
            self.assertTrue(validator.valid("production", "Error", body))
            self.assertEqual(set(body), {"contract_version", "request_id", "code", "retryable"})


if __name__ == "__main__":
    unittest.main()
