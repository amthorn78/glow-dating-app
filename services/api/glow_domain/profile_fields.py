"""The four two-way list fields, the member's own words and the display choices (SV2's brief, D3;
OD-60, P1). Pure domain rules, independent of Django: no storage, no route.

- **The fields:** gender, orientation, looking for and relationship status. Each has an
  admin-managed list (a setting in D2's store), the member's own value and a "show me" set.
- **Own values** are list value IDs. Orientation and relationship status are optional: a member
  may leave either unset, which is the reserved ``not-stated`` value; saving either, or
  orientation's own words, needs the sensitive-fields consent (D6). Gender and "looking for" are
  completion requirements (D9), so neither has ``not-stated``.
- **"Show me" sets** start at all. "All" is its own marker, the reserved ``all``, never the list of
  current values: it includes values the console adds later and ``not-stated``. A narrowed set
  is an explicit list of live values, and never holds ``not-stated`` or ``all``.
- **The two-way rule,** which SV3 applies: a field matches when at least one of each person's
  values is in the other's set, for every field. A member who states none in an optional field
  is therefore seen only by viewers who keep all of that field (OD-60's fixed limit).
- **Own words:** at most 40 code points, for display only: never matched, searched or ranked.
- **Display:** gender, orientation and relationship status each show only when the member turns
  their flag on; "looking for" is shown; a "show me" set is never shown.

The text rules are the contract's (``packages/contracts``): lengths count Unicode scalar values,
unpaired surrogates are invalid, and non-blank text holds a code point outside the Unicode
White_Space set plus the BOM. Nothing is trimmed or normalized.
"""

from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass

GENDER = "gender"
ORIENTATION = "orientation"
LOOKING_FOR = "looking_for"
RELATIONSHIP_STATUS = "relationship_status"
FIELDS: tuple[str, ...] = (GENDER, ORIENTATION, LOOKING_FOR, RELATIONSHIP_STATUS)
# The sensitive fields (D6; G-10): saved, and narrowed, only with the sensitive-fields consent.
SENSITIVE_FIELDS: frozenset[str] = frozenset({ORIENTATION, RELATIONSHIP_STATUS})
# The fields a member may leave unset (D3, D9): exactly the sensitive ones.
OPTIONAL_FIELDS: frozenset[str] = SENSITIVE_FIELDS
# Own words, display only (D3): gender and orientation; orientation's are sensitive.
OWN_WORDS_FIELDS: frozenset[str] = frozenset({GENDER, ORIENTATION})
# The display flags (D3): off until the member turns them on; "looking for" is always shown.
DISPLAY_FIELDS: frozenset[str] = frozenset({GENDER, ORIENTATION, RELATIONSHIP_STATUS})

ALL = "all"
NOT_STATED = "not-stated"
RESERVED_IDS: frozenset[str] = frozenset({ALL, NOT_STATED})
OWN_WORDS_MAX = 40
# The contract's bound on one "show me" set (PreferenceSelection.accepted_option_ids), which is
# also D2's fixed limit on the live values of one list.
SET_MAX = 50

# The wire form of an option ID (the contract's PolicyVersion-like identifier), and the stricter
# form the settings store accepts for a new list value.
WIRE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}")
VALUE_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")

# The contract's White_Space set plus the BOM (production-contracts.md, "Wire and error rules").
WHITESPACE: frozenset[str] = frozenset(
    [chr(c) for c in range(0x09, 0x0E)]
    + [" ", "\u0085", " ", " "]
    + [chr(c) for c in range(0x2000, 0x200B)]
    + [" ", " ", " ", " ", "　", "﻿"]
)


def has_surrogate(text: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in text)


def nonblank(text: str) -> bool:
    return any(character not in WHITESPACE for character in text)


def text_ok(value: object, maximum: int) -> bool:
    """Non-blank text of 1 to ``maximum`` code points with no unpaired surrogate."""
    return (
        isinstance(value, str)
        and 1 <= len(value) <= maximum
        and not has_surrogate(value)
        and nonblank(value)
    )


@dataclass(frozen=True)
class ListValue:
    value_id: str
    label: str
    retired: bool


@dataclass(frozen=True)
class FieldList:
    """One field's current list, from its setting (D2), with whether members may narrow by it."""

    field: str
    values: tuple[ListValue, ...]
    pick_limit: int | None
    narrowable: bool
    setting_version: int

    @property
    def live_ids(self) -> frozenset[str]:
        return frozenset(v.value_id for v in self.values if not v.retired)

    @property
    def retired_ids(self) -> frozenset[str]:
        return frozenset(v.value_id for v in self.values if v.retired)

    @property
    def all_ids(self) -> frozenset[str]:
        return frozenset(v.value_id for v in self.values)


# Refusal reasons: codes, never a value.
EMPTY = "empty"
RESERVED_VALUE = "reserved_value"
DUPLICATE = "duplicate"
OVER_PICK_LIMIT = "over_pick_limit"
UNKNOWN_VALUE = "unknown_value"
RETIRED_VALUE = "retired_value"
NOT_NARROWABLE = "not_narrowable"
OWN_WORDS_INVALID = "own_words_invalid"
OWN_WORDS_NOT_ALLOWED = "own_words_not_allowed"
SHOWN_NOT_ALLOWED = "shown_not_allowed"


def own_value_refusal(field: str, value_ids: list[str], catalog: FieldList) -> str | None:
    """A new choice of the member's own value for ``field``, or a refusal code.

    Every edit is a new choice: a retired value is refused even if the member holds it, so the
    member chooses again at their next edit (D2), while the value they hold stays valid and
    matchable until then."""
    if field in OPTIONAL_FIELDS and value_ids == [NOT_STATED]:
        return None
    if not value_ids:
        return EMPTY
    if any(value in RESERVED_IDS for value in value_ids):
        return RESERVED_VALUE
    if len(set(value_ids)) != len(value_ids):
        return DUPLICATE
    if catalog.pick_limit is not None and len(value_ids) > catalog.pick_limit:
        return OVER_PICK_LIMIT
    for value in value_ids:
        if value not in catalog.all_ids:
            return UNKNOWN_VALUE
        if value in catalog.retired_ids:
            return RETIRED_VALUE
    return None


def show_me_refusal(field: str, value_ids: list[str], catalog: FieldList) -> str | None:
    """A "show me" set for ``field``: the ``all`` marker alone, or a narrowed list of live
    values of a field members may narrow by (D2, D3)."""
    if value_ids == [ALL]:
        return None
    if not value_ids:
        return EMPTY
    if any(value in RESERVED_IDS for value in value_ids):
        return RESERVED_VALUE
    if len(set(value_ids)) != len(value_ids):
        return DUPLICATE
    if not catalog.narrowable:
        return NOT_NARROWABLE
    for value in value_ids:
        if value not in catalog.all_ids:
            return UNKNOWN_VALUE
        if value in catalog.retired_ids:
            return RETIRED_VALUE
    return None


def narrowed(value_ids: Collection[str]) -> bool:
    return list(value_ids) != [ALL]


def own_words_refusal(field: str, own_words: object) -> str | None:
    if own_words is None:
        return None
    if field not in OWN_WORDS_FIELDS:
        return OWN_WORDS_NOT_ALLOWED
    if not text_ok(own_words, OWN_WORDS_MAX):
        return OWN_WORDS_INVALID
    return None


def shown_refusal(field: str, shown: object) -> str | None:
    if not isinstance(shown, bool):
        return SHOWN_NOT_ALLOWED
    if field == LOOKING_FOR and shown is not True:
        return SHOWN_NOT_ALLOWED
    return None


def carries_sensitive(field: str, value_ids: list[str], own_words: object) -> bool:
    """Whether a field edit saves sensitive data (D6): a stated orientation or relationship
    status, or orientation's own words. Leaving either unset carries nothing."""
    if field not in SENSITIVE_FIELDS:
        return False
    return value_ids != [NOT_STATED] or own_words is not None


# -- the two-way rule (D3; SV3 applies it) ----------------------------------------------------


def sees(viewer_set: Collection[str], own_values: Collection[str]) -> bool:
    """Whether a viewer whose set for a field is ``viewer_set`` sees a member whose own values
    in that field are ``own_values``: the set keeps all, or at least one stated value is in it.
    ``not-stated``, or no value, is in no narrowed set."""
    if ALL in viewer_set:
        return True
    return any(value in viewer_set for value in own_values if value != NOT_STATED)


def two_way(
    first_values: Mapping[str, Collection[str]],
    first_sets: Mapping[str, Collection[str]],
    second_values: Mapping[str, Collection[str]],
    second_sets: Mapping[str, Collection[str]],
) -> bool:
    """Whether two members see each other: for every field, each one's values are in the other's
    set. A field a member has not saved counts as not stated, and a missing set as all."""
    for field in FIELDS:
        if not sees(first_sets.get(field, (ALL,)), second_values.get(field, ())):
            return False
        if not sees(second_sets.get(field, (ALL,)), first_values.get(field, ())):
            return False
    return True


# -- display (D3; the candidate projection that reads these flags is SV3's) -------------------


@dataclass(frozen=True)
class FieldState:
    value_ids: tuple[str, ...]
    own_words: str | None
    shown: bool


def displayed(fields: Mapping[str, FieldState]) -> dict[str, dict[str, object]]:
    """What a candidate projection may show of a member's fields: a display field only when its
    flag is on, with its own words only then; "looking for" always; a "show me" set never (this
    function is not given one). A value left unset is not shown."""
    shown: dict[str, dict[str, object]] = {}
    for field in FIELDS:
        state = fields.get(field)
        if state is None:
            continue
        values = [value for value in state.value_ids if value != NOT_STATED]
        if not values and state.own_words is None:
            continue
        if field in DISPLAY_FIELDS and not state.shown:
            continue
        entry: dict[str, object] = {"value_ids": values}
        if field in OWN_WORDS_FIELDS and state.own_words is not None:
            entry["own_words"] = state.own_words
        shown[field] = entry
    return shown
