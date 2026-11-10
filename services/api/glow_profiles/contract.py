"""The member's routes' contract (``gapp-api-v1``; the SV2 brief's D11 and D17): the closed
request checks, and the response projections.

**Requests are closed intents:** each route parses its JSON body and checks it against its DTO
here, with the contract's rules (unknown or missing fields fail; text lengths count Unicode scalar
values; unpaired surrogates and blank text fail; identifiers allow no trailing newline). The
contract's own validators decide the same cases (``tests/test_profile_contract.py`` runs the
shared corpus through both). A refusal names the field's path, never its value.

**Responses are projections:** each builder below returns exactly its DTO's fields, the owner's
own data only (D17). The API's tests validate them with the contract's own validator, and the
proof checks each served body against the schema.
"""

from __future__ import annotations

import json
import math
import re
import uuid
from collections.abc import Callable
from datetime import date
from typing import Any

from glow_domain import profile_fields as pf
from glow_domain import profile_settings as ps

CONTRACT_VERSION = "gapp-api-v1"
MAX_VERSION = 9007199254740991

UUID_TEXT = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
DATE_TEXT = re.compile(r"(?!0000)[0-9]{4}-[0-9]{2}-[0-9]{2}")
TIME_TEXT = re.compile(r"([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]")
AREA_ID = re.compile(r"[0-9]{5}")


class Invalid(Exception):
    """A request that is not its DTO. ``path`` names the field, never its value."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.path = path


Checker = Callable[[Any, str], None]


def closed(properties: dict[str, Checker]) -> Checker:
    def check(value: Any, at: str) -> None:
        if not isinstance(value, dict) or set(value) != set(properties):
            raise Invalid(at)
        for name, item in properties.items():
            item(value[name], f"{at}.{name}")

    return check


def const(expected: Any) -> Checker:
    def check(value: Any, at: str) -> None:
        if type(value) is not type(expected) or value != expected:
            raise Invalid(at)

    return check


def enum(*allowed: str) -> Checker:
    def check(value: Any, at: str) -> None:
        if not isinstance(value, str) or value not in allowed:
            raise Invalid(at)

    return check


def boolean(value: Any, at: str) -> None:
    if type(value) is not bool:
        raise Invalid(at)


def _integral(value: Any) -> Any:
    # JSON has one number type, and JSON Schema's integer is any number with no fractional part:
    # ``1.0`` is the integer 1, as the contract's validators decide. ``parse`` hands the
    # operations an int, so a request's digest does not depend on how a number was written.
    if type(value) is float and math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def integer(low: int, high: int) -> Checker:
    def check(value: Any, at: str) -> None:
        value = _integral(value)
        if type(value) is not int or not low <= value <= high:
            raise Invalid(at)

    return check


def number(low: float, high: float) -> Checker:
    def check(value: Any, at: str) -> None:
        if type(value) not in (int, float) or not math.isfinite(value):
            raise Invalid(at)
        if not low <= value <= high:
            raise Invalid(at)

    return check


def text(maximum: int) -> Checker:
    def check(value: Any, at: str) -> None:
        if not pf.text_ok(value, maximum):
            raise Invalid(at)

    return check


def summary(value: Any, at: str) -> None:
    if value != "" or not isinstance(value, str):
        text(500)(value, at)


def wire_id(value: Any, at: str) -> None:
    if not isinstance(value, str) or pf.WIRE_ID.fullmatch(value) is None or pf.has_surrogate(value):
        raise Invalid(at)


def uuid_text(value: Any, at: str) -> None:
    if not isinstance(value, str) or UUID_TEXT.fullmatch(value) is None:
        raise Invalid(at)


def date_text(value: Any, at: str) -> None:
    if not isinstance(value, str) or DATE_TEXT.fullmatch(value) is None:
        raise Invalid(at)
    try:
        date.fromisoformat(value)
    except ValueError:
        raise Invalid(at) from None


def time_text(value: Any, at: str) -> None:
    if not isinstance(value, str) or TIME_TEXT.fullmatch(value) is None:
        raise Invalid(at)


def area_id(value: Any, at: str) -> None:
    if not isinstance(value, str) or AREA_ID.fullmatch(value) is None:
        raise Invalid(at)


def nullable(item: Checker) -> Checker:
    def check(value: Any, at: str) -> None:
        if value is not None:
            item(value, at)

    return check


def array(item: Checker, *, max_items: int, min_items: int = 0, unique: bool = False) -> Checker:
    def check(value: Any, at: str) -> None:
        if not isinstance(value, list) or not min_items <= len(value) <= max_items:
            raise Invalid(at)
        for index, entry in enumerate(value):
            item(entry, f"{at}[{index}]")
        if unique and len({json.dumps(entry, sort_keys=True) for entry in value}) != len(value):
            raise Invalid(at)

    return check


COMMAND_META = closed({"idempotency_key": wire_id, "expected_version": integer(0, MAX_VERSION)})


def _birth_input(value: Any, at: str) -> None:
    closed(
        {
            "birth_date": date_text,
            "local_time": nullable(time_text),
            "time_precision": enum("known", "approximate", "unknown"),
            "place_label": text(200),
            "timezone_name": nullable(text(100)),
            "timezone_provenance": nullable(text(200)),
        }
    )(value, at)
    if (value["time_precision"] == "unknown") != (value["local_time"] is None):
        raise Invalid(f"{at}.local_time")
    if (value["timezone_name"] is None) != (value["timezone_provenance"] is None):
        raise Invalid(f"{at}.timezone_provenance")


def _profile_field_intent(value: Any, at: str) -> None:
    closed(
        {
            "operation": const("profile_field"),
            "meta": COMMAND_META,
            "policy_version": wire_id,
            "field": enum(*pf.FIELDS),
            "value_ids": array(wire_id, max_items=pf.SET_MAX, min_items=1, unique=True),
            "own_words": nullable(text(pf.OWN_WORDS_MAX)),
            "shown": boolean,
        }
    )(value, at)
    if (
        value["field"] in (pf.LOOKING_FOR, pf.RELATIONSHIP_STATUS)
        and value["own_words"] is not None
    ):
        raise Invalid(f"{at}.own_words")
    if value["field"] == pf.LOOKING_FOR and value["shown"] is not True:
        raise Invalid(f"{at}.shown")


def _preferences_intent(value: Any, at: str) -> None:
    closed(
        {
            "operation": const("preferences"),
            "meta": COMMAND_META,
            "policy_version": wire_id,
            "selections": array(
                closed(
                    {
                        "dimension": wire_id,
                        "accepted_option_ids": array(wire_id, max_items=pf.SET_MAX, unique=True),
                    }
                ),
                max_items=20,
            ),
        }
    )(value, at)
    dimensions = [entry["dimension"] for entry in value["selections"]]
    if len(set(dimensions)) != len(dimensions):
        raise Invalid(f"{at}.selections")


REQUESTS: dict[str, Checker] = {
    "ProfileIntent": closed(
        {
            "operation": const("profile"),
            "meta": COMMAND_META,
            "display_name": text(80),
            "summary": summary,
        }
    ),
    "PreferencesIntent": _preferences_intent,
    "VisibilityIntent": closed(
        {"operation": const("visibility"), "meta": COMMAND_META, "action": enum("pause", "resume")}
    ),
    "ConsentIntent": closed(
        {
            "operation": const("consent"),
            "meta": COMMAND_META,
            "policy_version": wire_id,
            "decision": enum("accepted", "withdrawn"),
        }
    ),
    "BirthInputIntent": closed(
        {"operation": const("birth_input"), "meta": COMMAND_META, "input": _birth_input}
    ),
    "ProfileFieldIntent": _profile_field_intent,
    "FiltersIntent": closed(
        {
            "operation": const("filters"),
            "meta": COMMAND_META,
            "policy_version": wire_id,
            "minimum_age": integer(ps.AGE_FLOOR, ps.AGE_CEILING),
            "maximum_age": nullable(integer(ps.AGE_FLOOR, ps.AGE_CEILING)),
            "distance_choice": wire_id,
        }
    ),
    "AreaIntent": closed({"operation": const("area"), "meta": COMMAND_META, "area_id": area_id}),
    # D5: the phone's approximate location, in the body only, bounded, and never echoed.
    "AreaQuery": closed({"latitude": number(-90, 90), "longitude": number(-180, 180)}),
    "SensitiveConsentIntent": closed(
        {
            "operation": const("sensitive_consent"),
            "meta": COMMAND_META,
            "policy_version": wire_id,
            "decision": enum("accepted", "withdrawn"),
        }
    ),
    "AdultCheckIntent": closed(
        {"operation": const("adult_check"), "meta": COMMAND_META, "birth_date": date_text}
    ),
}


def _reject_constant(name: str) -> Any:
    raise ValueError("a non-finite number is not JSON")


def _number(literal: str) -> Any:
    return _integral(float(literal))


def parse(definition: str, body: bytes) -> dict[str, Any]:
    """The request body as its DTO, or ``Invalid`` naming the definition or the field."""
    try:
        value = json.loads(
            body.decode("utf-8"), parse_constant=_reject_constant, parse_float=_number
        )
    except (UnicodeDecodeError, ValueError):
        raise Invalid(definition) from None
    REQUESTS[definition](value, definition)
    assert isinstance(value, dict)
    return value


def valid(definition: str, value: Any) -> bool:
    """For the parity test: whether the server's check accepts ``value``."""
    try:
        REQUESTS[definition](value, definition)
    except Invalid:
        return False
    return True


# -- responses (D17: the owner's own data, exactly the DTO's fields) -------------------------


def new_request_id() -> str:
    return str(uuid.uuid4())


def app_response(data: dict[str, Any], request_id: str) -> dict[str, Any]:
    return {"contract_version": CONTRACT_VERSION, "request_id": request_id, "data": data}


def error(code: str, request_id: str, *, retryable: bool = False) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "code": code,
        "retryable": retryable,
    }


def own_profile(profile: Any) -> dict[str, Any]:
    return {
        "kind": "own_profile",
        "profile_id": str(profile.id),
        "version": int(profile.version),
        "display_name": profile.display_name,
        "summary": profile.bio,
        "visibility": profile.state,
        # Stage B adds the approved photos.
        "media_ids": [],
    }


def own_field(field: str, row: Any, catalog_list: pf.FieldList) -> dict[str, Any]:
    if row is None:
        values = [pf.NOT_STATED] if field in pf.OPTIONAL_FIELDS else []
        return {
            "version": 0,
            "value_ids": values,
            "own_words": None,
            "shown": field == pf.LOOKING_FOR,
            "choose_again": False,
        }
    values = list(row.value_ids)
    return {
        "version": int(row.version),
        "value_ids": values,
        "own_words": row.own_words,
        "shown": bool(row.shown),
        "choose_again": any(value in catalog_list.retired_ids for value in values),
    }


def own_profile_fields(
    rows: dict[str, Any], lists: dict[str, pf.FieldList], catalog_version: str
) -> dict[str, Any]:
    return {
        "kind": "own_profile_fields",
        "policy_version": catalog_version,
        **{field: own_field(field, rows.get(field), lists[field]) for field in pf.FIELDS},
    }


def own_preferences(preferences: Any, sets: dict[str, list[str]]) -> dict[str, Any]:
    return {
        "kind": "own_preferences",
        "version": int(preferences.version),
        "policy_version": preferences.policy_version,
        "selections": [
            {"dimension": field, "accepted_option_ids": list(sets.get(field, [pf.ALL]))}
            for field in pf.FIELDS
        ],
    }


def own_filters(preferences: Any) -> dict[str, Any]:
    return {
        "kind": "own_filters",
        "version": int(preferences.version),
        "policy_version": preferences.policy_version,
        "minimum_age": int(preferences.minimum_age),
        "maximum_age": None if preferences.maximum_age is None else int(preferences.maximum_age),
        "distance_choice": preferences.distance_choice,
    }


def own_area(profile: Any, area: Any) -> dict[str, Any]:
    return {
        "kind": "own_area",
        "version": int(profile.version),
        "area_id": None if area is None else area.area_id,
        "area_name": None if area is None else area.name,
    }


def nearest_area(area_id_value: str, name: str) -> dict[str, Any]:
    # D5: the nearest area only; never the coordinates sent, and never a distance.
    return {"kind": "nearest_area", "area_id": area_id_value, "area_name": name}


def _catalog_field(field_list: pf.FieldList) -> dict[str, Any]:
    return {
        "values": [
            {"id": v.value_id, "label": v.label} for v in field_list.values if not v.retired
        ],
        "retired_values": [
            {"id": v.value_id, "label": v.label} for v in field_list.values if v.retired
        ],
        "pick_limit": field_list.pick_limit,
        "narrowable": field_list.narrowable,
    }


def profile_catalog(
    catalog_version: str,
    lists: dict[str, pf.FieldList],
    age_range: dict[str, Any],
    location: dict[str, Any],
    consents: dict[str, tuple[str, str]],
) -> dict[str, Any]:
    return {
        "kind": "profile_catalog",
        "policy_version": catalog_version,
        **{field: _catalog_field(lists[field]) for field in pf.FIELDS},
        "age_range": {
            "default_minimum": age_range["default_minimum"],
            "default_maximum": age_range["default_maximum"],
            "direction": age_range["direction"],
        },
        "location": {
            "chosen_area": location["chosen_area"],
            "approximate_location": location["approximate_location"],
            # Labels only: a distance choice's radius stays in the setting (no distance is ever
            # returned, D5).
            "distance_choices": [
                {"id": choice["id"], "label": choice["label"]}
                for choice in location["distance_choices"]
            ],
            "default_distance": location["default_distance"],
        },
        "consents": {
            purpose: {"policy_version": version, "text": wording}
            for purpose, (version, wording) in consents.items()
        },
    }


def own_completion(profile: Any, missing: list[str]) -> dict[str, Any]:
    return {
        "kind": "own_completion",
        "visibility": "incomplete" if profile is None else profile.state,
        "missing": list(missing),
    }


def onboarding_eligibility(latest: Any, requirements: list[str]) -> dict[str, Any]:
    return {
        "kind": "onboarding",
        "version": (0 if latest is None else int(latest.version)) + 1,
        "state": "required" if latest is None else latest.state,
        "requirements": list(requirements),
        "policy_version": None if latest is None else latest.policy_version,
    }


def sensitive_consent(latest: Any) -> dict[str, Any]:
    return {
        "kind": "sensitive_consent",
        "version": (0 if latest is None else int(latest.version)) + 1,
        "state": "not_given" if latest is None else latest.state,
        "policy_version": None if latest is None else latest.policy_version,
    }


def own_age_state(row: Any) -> dict[str, Any]:
    return {
        "kind": "own_age_state",
        "version": int(row.version),
        "state": row.state,
        "birth_date": None if row.birth_date is None else row.birth_date.isoformat(),
    }


def own_birth_input(row: Any, mapping: Any) -> dict[str, Any]:
    mapped = (
        mapping is not None and mapping.birth_input_id == row.id and mapping.state == "resolved"
    )
    return {
        "kind": "birth_input",
        "input_id": str(row.id),
        "version": int(row.version),
        "input": {
            "birth_date": row.birth_date.isoformat(),
            "local_time": None if row.local_time is None else row.local_time.strftime("%H:%M:%S"),
            "time_precision": row.time_precision,
            "place_label": row.place_label,
            "timezone_name": row.timezone_name,
            "timezone_provenance": row.timezone_provenance,
        },
        "resolution": row.state,
        "mapping_version": int(mapping.version) if mapped else None,
    }
