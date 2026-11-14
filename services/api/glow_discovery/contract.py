"""The page route's contract (``gapp-api-v1``; the SV3 brief's D13, for Stage A's parts).

**The request** is the existing ``PageRequest``, closed: the collection, a nullable cursor of the
contract's pattern (at most 100 characters) and a limit of 1 to 50. A body that is not it is
``invalid_request``, with nothing echoed. The checks are SV2's (``glow_profiles.contract``'s
checkers), so the rules for numbers, strings and unknown fields are the same.

**The response** is the new ``CandidateCardPage`` (D13 (a); DM-60 Q12), every existing DTO
unchanged: ``CandidatePage``'s fields with ``kind: candidate_card_page`` and the collection, whose
items are ``CandidateCard`` wrappers. Each card holds the existing ``CandidateProfile`` unchanged,
its ``profile_id`` again at the card's top level (so the contract's unique-key rule over a page's
``items``, in ``runtime.py`` and the app's ``validation.ts``, applies to cards unchanged), and the
new ``CandidateDetails``: "looking for" always; gender, orientation and relationship status only
while that field's ``shown`` flag is on, with the member's own words for gender and orientation
(display only); and the area's name. A card never carries a "show me" set, a filter, an area ID, an
internal point, a distance, a birth date, a count or a reason (D8). ``compatibility`` is ``pending``
for every card: no ready compatibility projection is serializable in this baseline, and a synthetic
ready result still projects ``pending`` (P05.2's rule).
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from glow_discovery import policy
from glow_domain import profile_fields as pf
from glow_profiles.contract import Invalid, closed, enum, instant, integer, nullable, wire_id

PAGE_REQUEST = closed(
    {
        "collection": enum(*policy.COLLECTIONS),
        "cursor": nullable(wire_id),
        "limit": integer(1, policy.PAGE_MAX),
    }
)
CARD_PAGE = "candidate_card_page"
PENDING = {"status": "pending"}


def _reject_constant(name: str) -> Any:
    raise ValueError("a non-finite number is not JSON")


def _number(literal: str) -> Any:
    value = float(literal)
    if math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def parse_page_request(body: bytes) -> dict[str, Any]:
    """The body as a ``PageRequest``, or ``Invalid``; decoded as SV2's ``contract.parse`` does."""
    try:
        value = json.loads(
            body.decode("utf-8"), parse_constant=_reject_constant, parse_float=_number
        )
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise Invalid("PageRequest") from None
    PAGE_REQUEST(value, "PageRequest")
    assert isinstance(value, dict)
    return value


def _fields(raw: object) -> dict[str, pf.FieldState]:
    rows = json.loads(raw) if isinstance(raw, str) else raw
    found: dict[str, pf.FieldState] = {}
    if isinstance(rows, Mapping):
        for field, row in rows.items():
            if field in pf.FIELDS and isinstance(row, Mapping):
                found[str(field)] = pf.FieldState(
                    tuple(str(value) for value in row.get("value_ids") or ()),
                    row.get("own_words"),
                    row.get("shown") is True,
                )
    return found


def details(raw_fields: object, area_name: object) -> dict[str, Any] | None:
    """``CandidateDetails`` from the candidate's field rows and area, through
    ``glow_domain.profile_fields.displayed`` (D3's display rules); ``None`` when "looking for" is
    missing, which a ``visible`` profile always has (the card is then left out, failing closed)."""
    shown = pf.displayed(_fields(raw_fields))

    def ids(field: str) -> list[str]:
        values = shown.get(field, {}).get("value_ids", [])
        return [str(value) for value in values] if isinstance(values, list) else []

    def worded(field: str) -> dict[str, Any] | None:
        entry = shown.get(field)
        if entry is None:
            return None
        words = entry.get("own_words")
        return {"value_ids": ids(field), "own_words": words if isinstance(words, str) else None}

    looking_for = ids(pf.LOOKING_FOR)
    if not looking_for:
        return None
    relationship = ids(pf.RELATIONSHIP_STATUS)
    return {
        "looking_for": looking_for,
        "gender": worded(pf.GENDER),
        "orientation": worded(pf.ORIENTATION),
        "relationship_status": {"value_ids": relationship} if relationship else None,
        "area_name": area_name if isinstance(area_name, str) and area_name else None,
    }


def card(row: Mapping[str, Any], refs: list[str]) -> dict[str, Any]:
    profile_id = str(row["profile_id"])
    return {
        "profile_id": profile_id,
        "profile": {
            "profile_id": profile_id,
            "display_name": row["display_name"],
            "age": int(row["age"]),
            "summary": row["bio"],
            "media_delivery_refs": list(refs),
            "compatibility": dict(PENDING),
        },
        "details": row["details"],
    }


def page(
    *,
    collection: str,
    batch_id: str,
    version: int,
    state: str,
    items: list[dict[str, Any]],
    next_cursor: str | None,
    expires_at: datetime,
) -> dict[str, Any]:
    return {
        "kind": CARD_PAGE,
        "collection": collection,
        "batch_id": batch_id,
        "version": int(version),
        "state": state,
        "items": items,
        "next_cursor": next_cursor,
        "expires_at": instant(expires_at),
    }
