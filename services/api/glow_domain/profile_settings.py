"""The settings store's closed schemas, launch defaults and fixed limits (SV2's brief, D2; OD-60;
OD-61). Pure domain rules, independent of Django.

Every OD-60 choice is a setting: one append-only version per publication, its content checked
here against the setting's closed schema and the fixed limits **before anything is written**.
The fixed limits are code, never data: a publication that crosses one is refused, and the
refusal names the limit (``FIXED_LIMITS``), never a value. The launch defaults (``LAUNCH_DEFAULTS``)
are version 1 of each setting, seeded by migration 0007, which holds the same content as a
literal (a test holds the two equal).

Two launch values are not recorded anywhere and are not invented here (the session's report
says so): OD-60 names no starting list for orientation, so its version 1 holds no value (a
member can state none until a publication adds values, and every member is "not stated"
meanwhile); and OD-60 names no distance choices, so version 1 offers one, ``anywhere``, which
filters nothing.

The media policy (D10) is Stage B's.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from glow_domain import profile_fields as pf

GENDER_LIST = "profile.gender"
ORIENTATION_LIST = "profile.orientation"
LOOKING_FOR_LIST = "profile.looking_for"
RELATIONSHIP_LIST = "profile.relationship_status"
LIST_SETTINGS: dict[str, str] = {
    pf.GENDER: GENDER_LIST,
    pf.ORIENTATION: ORIENTATION_LIST,
    pf.LOOKING_FOR: LOOKING_FOR_LIST,
    pf.RELATIONSHIP_STATUS: RELATIONSHIP_LIST,
}
NARROWING = "profile.narrowing"
AGE_RANGE = "profile.age_range"
LOCATION = "profile.location"
RESURFACING = "discovery.resurfacing"
UNDO = "discovery.undo"
REMATCH = "discovery.rematch"
HISTORY = "chat.history"
STAFF_APPROVAL = "identity.staff_approval"
ONBOARDING_CONSENT = "consent.onboarding"
SENSITIVE_CONSENT = "consent.sensitive_profile"

ALL_SETTINGS: tuple[str, ...] = (
    GENDER_LIST,
    ORIENTATION_LIST,
    LOOKING_FOR_LIST,
    RELATIONSHIP_LIST,
    NARROWING,
    AGE_RANGE,
    LOCATION,
    RESURFACING,
    UNDO,
    REMATCH,
    HISTORY,
    STAFF_APPROVAL,
    ONBOARDING_CONSENT,
    SENSITIVE_CONSENT,
)
# The settings a member's catalog read and their profile commands depend on, in this order.
CATALOG_SETTINGS: tuple[str, ...] = (
    GENDER_LIST,
    ORIENTATION_LIST,
    LOOKING_FOR_LIST,
    RELATIONSHIP_LIST,
    NARROWING,
    AGE_RANGE,
    LOCATION,
)

LAUNCH_SUBJECT = "system:launch-default"
# The seed's reason: OD-60, or for D18's setting the register row of Nathan's answers of
# 10 November 2026 (OD-61).
LAUNCH_REASONS: dict[str, str] = {
    name: ("OD-61" if name == STAFF_APPROVAL else "OD-60") for name in ALL_SETTINGS
}

AGE_FLOOR = 18
AGE_CEILING = 150
LIST_TOTAL_MAX = 200
LABEL_MAX = 80
CONSENT_TEXT_MAX = 4000
DISTANCE_CHOICES_MAX = 20
MILES_MAX = 5000
WAITING_DAYS_MAX = 3650
STAFF_SUBJECT = re.compile(r"(?:staff|system):[A-Za-z0-9._@-]{1,200}")
REASON = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._:/-]{0,99}")
POLICY_VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}")

HISTORY_CAUSES: tuple[str, ...] = (
    "own_pause",
    "other_pause",
    "restriction",
    "suspension",
    "withdrawn_consent",
)
HISTORY_VALUES = ("hidden", "read_only")

# -- the fixed limits (D2): code, not data --------------------------------------------------

SCHEMA = "schema"
MATCHING_USES_LIST_VALUES = "matching_uses_list_values"
LIST_RESERVED_VALUE = "list_reserved_value"
LIST_VALUE_REMOVED = "list_value_removed"
LIST_LIVE_VALUES = "list_live_values_over_50"
AGE_FLOOR_18 = "age_floor_18"
NO_COORDINATES_OR_DISTANCE = "no_exact_coordinates_or_distance"
REMATCH_NEVER_AFTER_BLOCK_OR_REPORT = "rematch_never_after_block_or_report"
UNMATCH_BLOCK_HIDDEN = "unmatch_and_block_stay_hidden"
DELETION_AS_UNMATCH = "deletion_works_as_unmatch"
SHOW_ME_NEVER_SHOWN = "show_me_never_shown"
NOT_STATED_KEEP_ALL_ONLY = "not_stated_seen_only_by_keep_all"
MORE_READABLE_NEEDS_CONSENT = "more_readable_needs_consent_wording"
STAFF_APPROVAL_IDENTITY_ONLY = "staff_approval_stands_in_for_identity_verification_only"

FIXED_LIMITS: dict[str, str] = {
    MATCHING_USES_LIST_VALUES: "matching uses list values",
    AGE_FLOOR_18: "the age floor is 18",
    NO_COORDINATES_OR_DISTANCE: "never exact coordinates or an exact distance",
    REMATCH_NEVER_AFTER_BLOCK_OR_REPORT: "rematch never after a block or a report",
    UNMATCH_BLOCK_HIDDEN: "unmatch and block stay hidden",
    DELETION_AS_UNMATCH: "a deletion works as an unmatch",
    SHOW_ME_NEVER_SHOWN: '"show me" is never shown',
    NOT_STATED_KEEP_ALL_ONLY: (
        "a member who states none in an optional field appears only to viewers who keep all"
    ),
    MORE_READABLE_NEEDS_CONSENT: (
        "a change to H that makes more readable reaches a member only after they accept the"
        " consent wording that describes it"
    ),
    LIST_LIVE_VALUES: "no list holds more than 50 live values",
    STAFF_APPROVAL_IDENTITY_ONLY: (
        "a staff approval without identity verification stands in for that one requirement only"
    ),
    LIST_RESERVED_VALUE: 'a list value is never the reserved "all" or "not-stated"',
    LIST_VALUE_REMOVED: "a published list value is retired, never removed, so its holders keep it",
}

ONBOARDING_TEXT = (
    "Development text, not Glow's final wording (P08 writes it). Glow uses what you tell it to"
    " suggest people to you and you to them. Your gender, together with the genders you choose"
    " to see, can reveal your sexual orientation. If messaging with a match stops because one of"
    " you pauses, a profile is restricted or suspended, or a consent is withdrawn, the"
    " conversation stays readable to both of you, but no new message can be sent; an unmatch or"
    " a block hides it, and a deleted account works as an unmatch. You can withdraw this"
    " consent at any time, and your profile then stops being shown."
)
SENSITIVE_TEXT = (
    "Development text, not Glow's final wording (P08 writes it). With this consent you may add"
    " your sexual orientation, your own words for it and your relationship status, and narrow"
    " whom you see by orientation or relationship status. Glow uses them only to match people"
    " both ways, and shows them only if you choose. Anyone who narrows whom they see by one of"
    " these fields learns it about everyone they are shown, even members who do not show it."
    " You can withdraw this consent at any time: Glow then removes these values, your own words"
    " and your narrowed choices for them, and you appear as not stated, to people who see"
    " everyone."
)


def _values(*pairs: tuple[str, str]) -> list[dict[str, Any]]:
    return [{"id": value_id, "label": label, "retired": False} for value_id, label in pairs]


LAUNCH_DEFAULTS: dict[str, dict[str, Any]] = {
    GENDER_LIST: {
        "matching": "list_values",
        "pick_limit": 1,
        "values": _values(("woman", "Woman"), ("man", "Man"), ("non-binary", "Non-binary")),
    },
    # OD-60 names no starting orientation list: none is invented (see the module's docstring).
    ORIENTATION_LIST: {"matching": "list_values", "pick_limit": 1, "values": []},
    LOOKING_FOR_LIST: {
        "matching": "list_values",
        "pick_limit": None,
        "values": _values(
            ("long-term", "A long-term relationship"),
            ("short-term", "Something short-term"),
            ("casual", "Something casual"),
            ("new-friends", "New friends"),
            ("figuring-it-out", "Still figuring it out"),
        ),
    },
    RELATIONSHIP_LIST: {
        "matching": "list_values",
        "pick_limit": 1,
        "values": _values(
            ("single", "Single"),
            ("separated-or-divorcing", "Separated or divorcing"),
            (
                "partnered-open-or-non-monogamous",
                "Partnered, in an open or non-monogamous relationship",
            ),
        ),
    },
    NARROWING: {
        "narrowable": {field: True for field in pf.FIELDS},
        "show_me_shown": False,
        "not_stated_seen_by": "keep_all",
    },
    AGE_RANGE: {"default_minimum": AGE_FLOOR, "default_maximum": None, "direction": "both_ways"},
    # OD-60 names no distance choices: one that filters nothing (see the module's docstring).
    LOCATION: {
        "chosen_area": True,
        "approximate_location": True,
        "distance_choices": [{"id": "anywhere", "label": "Anywhere", "miles": None}],
        "default_distance": "anywhere",
        "store_coordinates": False,
        "show_distance": False,
    },
    RESURFACING: {"enabled": False, "waiting_days": None},
    UNDO: {"enabled": False, "waiting_days": None},
    REMATCH: {"enabled": False, "waiting_days": None, "after_block": False, "after_report": False},
    HISTORY: {
        **{cause: "read_only" for cause in HISTORY_CAUSES},
        "unmatch": "hidden",
        "block": "hidden",
        "deletion": "as_unmatch",
        "consent_policy_version": f"{ONBOARDING_CONSENT}.v1",
    },
    STAFF_APPROVAL: {"enabled": False, "stands_in_for": ["identity_verification"]},
    ONBOARDING_CONSENT: {"development": True, "text": ONBOARDING_TEXT},
    SENSITIVE_CONSENT: {"development": True, "text": SENSITIVE_TEXT},
}


def policy_version(name: str, number: int) -> str:
    """The client-facing label of a setting's version, as its pointer holds it."""
    return f"{name}.v{number}"


def catalog_version(numbers: Mapping[str, int]) -> str:
    """The member's catalog version: the version numbers of ``CATALOG_SETTINGS``, in order."""
    return "catalog." + ".".join(str(numbers[name]) for name in CATALOG_SETTINGS)


def staff_subject_ok(value: object) -> bool:
    return isinstance(value, str) and STAFF_SUBJECT.fullmatch(value) is not None


def reason_ok(value: object) -> bool:
    return isinstance(value, str) and REASON.fullmatch(value) is not None


# -- the closed schemas --------------------------------------------------------------------


def _keys(value: object, keys: tuple[str, ...]) -> bool:
    return isinstance(value, dict) and set(value) == set(keys)


def _int(value: object, low: int, high: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def _bool(value: object) -> bool:
    return isinstance(value, bool)


def _list_refusals(content: Any, current: Any) -> list[str]:
    if not _keys(content, ("matching", "pick_limit", "values")):
        return [SCHEMA]
    refusals: list[str] = []
    if content["matching"] != "list_values":
        refusals.append(MATCHING_USES_LIST_VALUES)
    limit = content["pick_limit"]
    if limit is not None and not _int(limit, 1, pf.SET_MAX):
        return [SCHEMA]
    values = content["values"]
    if not isinstance(values, list) or len(values) > LIST_TOTAL_MAX:
        return [SCHEMA]
    ids: list[str] = []
    for value in values:
        if not _keys(value, ("id", "label", "retired")):
            return [SCHEMA]
        if not isinstance(value["id"], str) or not pf.text_ok(value["label"], LABEL_MAX):
            return [SCHEMA]
        if not _bool(value["retired"]):
            return [SCHEMA]
        if value["id"] in pf.RESERVED_IDS:
            refusals.append(LIST_RESERVED_VALUE)
        elif pf.VALUE_ID.fullmatch(value["id"]) is None:
            return [SCHEMA]
        ids.append(value["id"])
    if len(set(ids)) != len(ids):
        return [SCHEMA]
    if sum(1 for value in values if not value["retired"]) > pf.SET_MAX:
        refusals.append(LIST_LIVE_VALUES)
    if isinstance(current, dict):
        published = {value["id"] for value in current.get("values", [])}
        if not published <= set(ids):
            refusals.append(LIST_VALUE_REMOVED)
    return refusals


def _narrowing_refusals(content: Any) -> list[str]:
    if not _keys(content, ("narrowable", "show_me_shown", "not_stated_seen_by")):
        return [SCHEMA]
    narrowable = content["narrowable"]
    if not _keys(narrowable, pf.FIELDS) or not all(_bool(v) for v in narrowable.values()):
        return [SCHEMA]
    refusals: list[str] = []
    if content["show_me_shown"] is not False:
        if not _bool(content["show_me_shown"]):
            return [SCHEMA]
        refusals.append(SHOW_ME_NEVER_SHOWN)
    if content["not_stated_seen_by"] != "keep_all":
        if not isinstance(content["not_stated_seen_by"], str):
            return [SCHEMA]
        refusals.append(NOT_STATED_KEEP_ALL_ONLY)
    return refusals


def _age_range_refusals(content: Any) -> list[str]:
    if not _keys(content, ("default_minimum", "default_maximum", "direction")):
        return [SCHEMA]
    minimum, maximum = content["default_minimum"], content["default_maximum"]
    if not _int(minimum, 0, AGE_CEILING):
        return [SCHEMA]
    if maximum is not None and not _int(maximum, 0, AGE_CEILING):
        return [SCHEMA]
    if content["direction"] not in ("both_ways", "viewer_only"):
        return [SCHEMA]
    refusals: list[str] = []
    if minimum < AGE_FLOOR or (maximum is not None and maximum < AGE_FLOOR):
        refusals.append(AGE_FLOOR_18)
    if maximum is not None and maximum < minimum:
        refusals.append(SCHEMA)
    return refusals


def _location_refusals(content: Any) -> list[str]:
    keys = (
        "chosen_area",
        "approximate_location",
        "distance_choices",
        "default_distance",
        "store_coordinates",
        "show_distance",
    )
    if not _keys(content, keys):
        return [SCHEMA]
    if not all(
        _bool(content[key]) for key in keys if key not in ("distance_choices", "default_distance")
    ):
        return [SCHEMA]
    if not (content["chosen_area"] or content["approximate_location"]):
        return [SCHEMA]
    choices = content["distance_choices"]
    if not isinstance(choices, list) or not 1 <= len(choices) <= DISTANCE_CHOICES_MAX:
        return [SCHEMA]
    ids: list[str] = []
    for choice in choices:
        if not _keys(choice, ("id", "label", "miles")):
            return [SCHEMA]
        if not isinstance(choice["id"], str) or pf.VALUE_ID.fullmatch(choice["id"]) is None:
            return [SCHEMA]
        if not pf.text_ok(choice["label"], LABEL_MAX):
            return [SCHEMA]
        if choice["miles"] is not None and not _int(choice["miles"], 1, MILES_MAX):
            return [SCHEMA]
        ids.append(choice["id"])
    if len(set(ids)) != len(ids) or content["default_distance"] not in ids:
        return [SCHEMA]
    if content["store_coordinates"] or content["show_distance"]:
        return [NO_COORDINATES_OR_DISTANCE]
    return []


def _discovery_refusals(content: Any, rematch: bool) -> list[str]:
    keys = ("enabled", "waiting_days") + (("after_block", "after_report") if rematch else ())
    if not _keys(content, keys) or not _bool(content["enabled"]):
        return [SCHEMA]
    days = content["waiting_days"]
    if days is not None and not _int(days, 1, WAITING_DAYS_MAX):
        return [SCHEMA]
    if content["enabled"] and days is None:
        return [SCHEMA]
    if rematch:
        if not (_bool(content["after_block"]) and _bool(content["after_report"])):
            return [SCHEMA]
        if content["after_block"] or content["after_report"]:
            return [REMATCH_NEVER_AFTER_BLOCK_OR_REPORT]
    return []


def _history_refusals(content: Any, current: Any, onboarding_version: str | None) -> list[str]:
    keys = (*HISTORY_CAUSES, "unmatch", "block", "deletion", "consent_policy_version")
    if not _keys(content, keys):
        return [SCHEMA]
    if not all(content[cause] in HISTORY_VALUES for cause in HISTORY_CAUSES):
        return [SCHEMA]
    version = content["consent_policy_version"]
    if not isinstance(version, str) or POLICY_VERSION.fullmatch(version) is None:
        return [SCHEMA]
    refusals: list[str] = []
    if content["unmatch"] != "hidden" or content["block"] != "hidden":
        refusals.append(UNMATCH_BLOCK_HIDDEN)
    if content["deletion"] != "as_unmatch":
        refusals.append(DELETION_AS_UNMATCH)
    if isinstance(current, dict):
        more_readable = any(
            current.get(cause) == "hidden" and content[cause] == "read_only"
            for cause in HISTORY_CAUSES
        )
        if more_readable and (
            onboarding_version is None
            or version != onboarding_version
            or version == current.get("consent_policy_version")
        ):
            refusals.append(MORE_READABLE_NEEDS_CONSENT)
        if not more_readable and version != current.get("consent_policy_version"):
            # D2 (DM-55, Z6): a publication that makes nothing more readable keeps the version the
            # current setting names, so the limit cannot be crossed in two publications (the label
            # moved first, then a cause made readable under a version members already accepted).
            refusals.append(MORE_READABLE_NEEDS_CONSENT)
    return refusals


def _staff_approval_refusals(content: Any) -> list[str]:
    if not _keys(content, ("enabled", "stands_in_for")) or not _bool(content["enabled"]):
        return [SCHEMA]
    if not isinstance(content["stands_in_for"], list):
        return [SCHEMA]
    if content["stands_in_for"] != ["identity_verification"]:
        return [STAFF_APPROVAL_IDENTITY_ONLY]
    return []


def _consent_refusals(content: Any) -> list[str]:
    if not _keys(content, ("development", "text")) or not _bool(content["development"]):
        return [SCHEMA]
    if not pf.text_ok(content["text"], CONSENT_TEXT_MAX):
        return [SCHEMA]
    return []


def publication_refusals(
    name: str,
    content: Any,
    current: Any = None,
    *,
    onboarding_consent_version: str | None = None,
) -> tuple[str, ...]:
    """Why ``content`` cannot be published as the next version of ``name``, given the current
    version's content (``None`` for the launch default), or nothing. ``chat.history`` also needs
    the onboarding consent's current version label (the H rule)."""
    if name in LIST_SETTINGS.values():
        found = _list_refusals(content, current)
    elif name == NARROWING:
        found = _narrowing_refusals(content)
    elif name == AGE_RANGE:
        found = _age_range_refusals(content)
    elif name == LOCATION:
        found = _location_refusals(content)
    elif name in (RESURFACING, UNDO):
        found = _discovery_refusals(content, rematch=False)
    elif name == REMATCH:
        found = _discovery_refusals(content, rematch=True)
    elif name == HISTORY:
        found = _history_refusals(content, current, onboarding_consent_version)
    elif name == STAFF_APPROVAL:
        found = _staff_approval_refusals(content)
    elif name in (ONBOARDING_CONSENT, SENSITIVE_CONSENT):
        found = _consent_refusals(content)
    else:
        found = [SCHEMA]
    return tuple(dict.fromkeys(found))


def field_list(
    field: str, content: Mapping[str, Any], narrowing: Mapping[str, Any], setting_version: int
) -> pf.FieldList:
    """One field's list from its setting's content and the narrowing setting's."""
    return pf.FieldList(
        field,
        tuple(
            pf.ListValue(value["id"], value["label"], bool(value["retired"]))
            for value in content["values"]
        ),
        content["pick_limit"],
        bool(narrowing["narrowable"][field]),
        setting_version,
    )
