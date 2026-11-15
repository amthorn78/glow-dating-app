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

**Stage B's requests** (D9, D11 and D12) are the existing closed ``InteractionIntent``,
``UnmatchIntent`` and ``BlockIntent``, and D13's new ``InteractionUndoIntent`` (an added DTO; no
existing DTO changes), each with ``CommandMeta`` (an idempotency key and the expected version);
parsed as ``PageRequest`` is. **Their responses** are the current projections: the existing
``InteractionOutcome``, ``MatchProjection`` and ``BlockOutcome``, and D13's new
``InteractionUndoOutcome`` for a withdrawn pass. The receipt (``CommandReceipt``, or D13's new
``InteractionUndoReceipt``) and the replay flag form the internal ``InteractionCommandResult`` (or
D13's new ``InteractionUndoCommandResult``), which the operations return beside the projection;
neither joins the served envelope (the contract's "P05.3 internal interaction result and identity
bridge"). No projection carries another member's private value, a count, a reason or a block's
direction (D8).

**The actor's own versions** (D13; DM-74; correction B-C1) are D13's new ``OwnInteractionVersions``
(an added DTO; no existing DTO changes; no request DTO, since the read takes the profile ID in its
path): the profile ID as asked, the actor's own directional row's state (``none``, ``liked``,
``passed`` or ``withdrawn``) and version, and the actor's own block's state (``none``, ``active`` or
``removed``) and version, each ``none`` and ``0`` where the actor has no row. It never carries the
other member's row, a count or a reason (D8).
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from glow_discovery import policy
from glow_domain import profile_fields as pf
from glow_profiles.contract import (
    COMMAND_META,
    MAX_VERSION,
    Checker,
    Invalid,
    closed,
    const,
    enum,
    instant,
    integer,
    nullable,
    uuid_text,
    wire_id,
)

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


# Stage B's requests (D9, D11, D12; D13's additions).
INTERACTION_INTENT = closed(
    {
        "operation": const("interaction"),
        "meta": COMMAND_META,
        "target_profile_id": uuid_text,
        "batch_id": uuid_text,
        "batch_version": integer(1, MAX_VERSION),
        "action": enum("like", "pass"),
    }
)
UNDO_INTENT = closed(
    {
        "operation": const("interaction_undo"),
        "meta": COMMAND_META,
        "target_profile_id": uuid_text,
    }
)
UNMATCH_INTENT = closed(
    {"operation": const("unmatch"), "meta": COMMAND_META, "match_id": uuid_text}
)
BLOCK_INTENT = closed(
    {
        "operation": const("block"),
        "meta": COMMAND_META,
        "target_profile_id": uuid_text,
        "action": enum("block", "unblock"),
    }
)
REQUESTS: dict[str, Checker] = {
    "PageRequest": PAGE_REQUEST,
    "InteractionIntent": INTERACTION_INTENT,
    "InteractionUndoIntent": UNDO_INTENT,
    "UnmatchIntent": UNMATCH_INTENT,
    "BlockIntent": BLOCK_INTENT,
}


def parse(definition: str, body: bytes) -> dict[str, Any]:
    """The body as its DTO, or ``Invalid``; decoded as SV2's ``contract.parse`` does."""
    try:
        value = json.loads(
            body.decode("utf-8"), parse_constant=_reject_constant, parse_float=_number
        )
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise Invalid(definition) from None
    REQUESTS[definition](value, definition)
    assert isinstance(value, dict)
    return value


def parse_page_request(body: bytes) -> dict[str, Any]:
    """The body as a ``PageRequest``, or ``Invalid``."""
    return parse("PageRequest", body)


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


# -- Stage B's projections and receipts (D9 to D13) ---------------------------------------------


def interaction_outcome(
    target_profile_id: str, version: int, state: str, match_id: str | None
) -> dict[str, Any]:
    """``InteractionOutcome``: the actor's own like or pass. ``match_id`` is the pair's match, which
    only a like can have (the schema holds a pass's to null); an unreciprocated like has none."""
    return {
        "kind": "interaction",
        "target_profile_id": target_profile_id,
        "version": int(version),
        "state": state,
        "match_id": match_id if state == "liked" else None,
    }


def undo_outcome(target_profile_id: str, version: int) -> dict[str, Any]:
    """D13's ``InteractionUndoOutcome``: the actor's own pass, withdrawn (D12)."""
    return {
        "kind": "interaction_undo",
        "target_profile_id": target_profile_id,
        "version": int(version),
        "state": "withdrawn",
    }


def match_projection(
    match_id: str, version: int, other_profile_id: str, state: str
) -> dict[str, Any]:
    """``MatchProjection``, for a participant only: the other member's profile ID and the state,
    never who restricted it or why."""
    return {
        "kind": "match",
        "match_id": match_id,
        "version": int(version),
        "other_profile_id": other_profile_id,
        "state": state,
    }


def block_outcome(target_profile_id: str, version: int, state: str) -> dict[str, Any]:
    """``BlockOutcome``: the actor's own block, in the actor's direction only (F13)."""
    return {
        "kind": "block",
        "target_profile_id": target_profile_id,
        "version": int(version),
        "state": state,
    }


OWN_VERSIONS = "own_interaction_versions"


def own_versions(
    target_profile_id: str,
    interaction: tuple[str, int] | None,
    block: tuple[str, int] | None,
) -> dict[str, Any]:
    """D13's ``OwnInteractionVersions``: the actor's own directional row and own block toward the
    profile, each ``(state, version)``, or ``None`` where the actor has no row (``none`` and
    ``0``). Built from the actor's own rows only (DM-74)."""
    interaction_state, interaction_version = interaction or ("none", 0)
    block_state, block_version = block or ("none", 0)
    return {
        "kind": OWN_VERSIONS,
        "target_profile_id": target_profile_id,
        "interaction_state": str(interaction_state),
        "interaction_version": int(interaction_version),
        "block_state": str(block_state),
        "block_version": int(block_version),
    }


def receipt(outcome_code: str, object_ref: str, committed_version: int) -> dict[str, Any]:
    """The immutable receipt: ``CommandReceipt``, or D13's ``InteractionUndoReceipt`` for
    ``withdrawn``."""
    return {
        "outcome_code": outcome_code,
        "object_ref": object_ref,
        "committed_version": int(committed_version),
    }


def command_result(
    receipt_value: dict[str, Any], replayed: bool, projection: dict[str, Any] | None
) -> dict[str, Any]:
    """The internal ``InteractionCommandResult`` (or, for an undo's receipt, D13's
    ``InteractionUndoCommandResult``): the original receipt, the replay flag and the current
    projection where the DTO's rule allows it (null otherwise). Never served."""
    allowed: tuple[str, ...]
    if receipt_value["outcome_code"] == "withdrawn":
        kind = "interaction_undo_command_result"
        allowed = ("interaction_undo", "interaction")
    else:
        kind = "interaction_command_result"
        allowed = {
            "liked": ("interaction",),
            "passed": ("interaction",),
            "unmatched": ("match",),
            "blocked": ("block",),
            "unblocked": ("block",),
        }[receipt_value["outcome_code"]]
    current = projection if projection is not None and projection["kind"] in allowed else None
    return {
        "kind": kind,
        "receipt": receipt_value,
        "replayed": replayed,
        "current_projection": current,
    }
