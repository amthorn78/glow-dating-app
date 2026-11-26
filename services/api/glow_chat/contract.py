"""Chat's routes' contract (``gapp-api-v1``; the SV4 brief's D8 and D9), sealed until integration.

**The requests** are the contract's closed intents, checked with SV2's checkers
(``glow_profiles.contract``), so the rules for numbers, strings, identifiers and unknown fields
are the same as every other route's: ``MessageIntent`` (``operation: message``, ``CommandMeta``,
the match ID and the text: 1 to 4000 code points, not blank, no unpaired surrogate and no U+0000,
which the database cannot store), ``MessagePageRequest`` (the match ID, a nullable cursor of the
contract's pattern, a limit of 1 to 50) and ``ReadCursorIntent`` (``operation: read_cursor``, the
match ID and the submission ID). A body that is not its DTO is ``invalid_request``, with nothing
echoed.

**The responses** are built from an allowlist of each DTO's keys: ``MessageSubmission`` (the
submission's ID, version and state; never its text), ``ConversationSummary`` and
``ConversationList``. A conversation the read rule serves with no cause is ``open``; one it
serves read-only (the SV4 brief's D5: a cause ``chat.history`` marks ``read_only``) is
``read_only`` (D9), the same state for every cause, with its count and its marker kept. Neither
says which cause, and a conversation the member may no longer see is not served at all.

**The send's refusals** (D8; OD-60, H; D4; DM-96 AG13). Every refusal that comes from either
member's state or from the end of contact, ``match_not_active``, ``blocked``,
``account_not_active``, ``profile_unavailable`` and ``consent_not_current`` (with their missing
forms), answers one code, ``not_found``, the same for each, so a member never learns which cause
stopped a send. It is the code the reads answer for every refusal about the conversation or the
other member (``glow_domain.chat_projections.error_for``), so the send tells a member no more
than the history read does, and the code the mobile fixture and client already treat as
"unavailable". A version other than the match's answers ``not_found`` too, and so does a
session the send finds ended once it holds its locks: the send checks part of either member's
state after the version and the session (A2R-1, A2R-2; DM-99), so another answer for either
would tell causes apart. The same key with another intent is ``idempotency_conflict``, and a
session that is missing when the send reads or locks it is ``unauthenticated``.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from typing import Any

from glow_domain import chat
from glow_domain import chat_projections as projections
from glow_domain.chat_reads import PAGE_LIMIT, ConversationEntry
from glow_profiles.contract import (
    COMMAND_META,
    Checker,
    Invalid,
    closed,
    const,
    integer,
    nullable,
    text,
    uuid_text,
    wire_id,
)

# MessageIntent's text ceiling (the contract's ``maxLength``), in code points.
TEXT_LIMIT = 4000

MESSAGE_INTENT = closed(
    {
        "operation": const("message"),
        "meta": COMMAND_META,
        "match_id": uuid_text,
        "text": text(TEXT_LIMIT),
    }
)
MESSAGE_PAGE_REQUEST = closed(
    {"match_id": uuid_text, "cursor": nullable(wire_id), "limit": integer(1, PAGE_LIMIT)}
)
READ_CURSOR_INTENT = closed(
    {"operation": const("read_cursor"), "match_id": uuid_text, "submission_id": uuid_text}
)
REQUESTS: dict[str, Checker] = {
    "MessageIntent": MESSAGE_INTENT,
    "MessagePageRequest": MESSAGE_PAGE_REQUEST,
    "ReadCursorIntent": READ_CURSOR_INTENT,
}

OPEN = "open"
READ_ONLY = "read_only"

NOT_FOUND = "not_found"
STALE_VERSION = "stale_version"
IDEMPOTENCY_CONFLICT = "idempotency_conflict"

# D8: the send's refusals from either member's state or from the end of contact, each with the
# form a missing row takes. All answer ``SEND_STOPPED``, one code, the same for each.
SEND_STOPPED = NOT_FOUND
STOPPED_REASONS: frozenset[str] = frozenset(
    {
        chat.MATCH_NOT_ACTIVE,
        chat.BLOCKED,
        chat.ACCOUNT_NOT_ACTIVE,
        chat.PROFILE_UNAVAILABLE,
        chat.CONSENT_NOT_CURRENT,
        chat.PROFILE_MISSING,
        chat.NO_CONSENT,
    }
)


def _reject_constant(name: str) -> Any:
    raise ValueError("a non-finite number is not JSON")


def _number(literal: str) -> Any:
    value = float(literal)
    if math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def parse(definition: str, body: bytes) -> dict[str, Any]:
    """The body as its DTO, or ``Invalid``; decoded as SV2's and SV3's ``parse`` do."""
    try:
        value = json.loads(
            body.decode("utf-8"), parse_constant=_reject_constant, parse_float=_number
        )
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise Invalid(definition) from None
    REQUESTS[definition](value, definition)
    assert isinstance(value, dict)
    return value


# -- responses -----------------------------------------------------------------------------


def message_submission(submission_id: str, version: int, state: str) -> dict[str, Any]:
    """``MessageSubmission``: the submission's ID, version and delivery state; never its text."""
    return {
        "kind": "message",
        "submission_id": submission_id,
        "version": int(version),
        "state": state,
    }


def conversation_summary(entry: ConversationEntry, *, read_only: bool) -> dict[str, Any]:
    """A conversation the member may see: ``open``, or ``read_only`` for every cause D5 serves
    read-only, with its count and marker kept either way (D9)."""
    if entry.unread < 0:
        raise ValueError("an unread count is never negative")
    return {
        "kind": "conversation",
        "match_id": str(entry.match_id),
        "state": READ_ONLY if read_only else OPEN,
        "unread_count": entry.unread,
        "latest": projections.latest_marker(entry.latest),
    }


def conversation_list(entries: Iterable[tuple[ConversationEntry, bool]]) -> dict[str, Any]:
    return {
        "kind": "conversation_list",
        "conversations": [
            conversation_summary(entry, read_only=read_only) for entry, read_only in entries
        ],
    }


# -- refusals --------------------------------------------------------------------------------


def send_error(outcome: str, reason: str) -> tuple[str, bool]:
    """A refused send as the contract's ``Error`` code and whether it is retryable (D8).

    ``SEND_STOPPED`` (``not_found``, not retryable), one body for each, answers every stopped
    cause (``STOPPED_REASONS``), and also (A2R-1, A2R-2; DM-99):

    - ``stale_contact_version``, a version other than the match's;
    - the session's reasons ``contact.send`` raises once it holds its locks: ``session_changed``,
      ``session_not_valid``, ``session_expired`` and ``session_epoch_stale``.

    Why: ``send`` checks the match's state and both accounts before the session's state, a block
    after it, and both profiles and both consents after the version, so any other answer for
    either would tell a member which cause stopped the send. ``session_missing`` (the read before
    the locks) and ``accountsession_missing`` (the session's lock finding no row) are found before
    any cause is checked and stay ``unauthenticated``, as SV1's door answers; the same key with
    another intent is ``idempotency_conflict``; everything else about the match (not theirs,
    missing, its channel not usable) is the generic unavailable object; a deadlock or a database
    error is ``state_conflict``, as ``chat_projections.error_for`` maps them."""
    if outcome in ("deadlock", "error"):
        return projections.error_for(outcome, reason)
    if reason in STOPPED_REASONS or reason == chat.STALE_CONTACT_VERSION:
        return SEND_STOPPED, False
    if reason in (
        chat.SESSION_CHANGED,
        chat.SESSION_NOT_VALID,
        chat.SESSION_EXPIRED,
        chat.SESSION_EPOCH_STALE,
    ):
        return SEND_STOPPED, False
    if reason == chat.IDEMPOTENCY_CONFLICT:
        return IDEMPOTENCY_CONFLICT, False
    return projections.error_for("refused", reason)


def read_error(outcome: str, reason: str, *, conversation: bool = False) -> tuple[str, bool]:
    """A refused read as the contract's ``Error`` code: ``chat_projections.error_for``, but for one
    conversation's own reads (``conversation``: the history read and the read cursor, DM-99's
    AK1), whose session's reasons ``reads._authorize`` raises once it holds its locks
    (``session_changed``, ``session_not_valid``, ``session_expired``, ``session_epoch_stale``)
    answer ``not_found``, the code a hidden conversation answers: the read rule checks the block
    and the causes after the session, so ``unauthenticated`` there would tell a cause published
    ``hidden`` from an ended contact. ``session_missing``, ``accountsession_missing``, SV1's door
    and the conversation list, which refuses as a whole and names no conversation, keep
    ``unauthenticated``."""
    if (
        conversation
        and outcome == "refused"
        and reason
        in (
            chat.SESSION_CHANGED,
            chat.SESSION_NOT_VALID,
            chat.SESSION_EXPIRED,
            chat.SESSION_EPOCH_STALE,
        )
    ):
        return NOT_FOUND, False
    return projections.error_for(outcome, reason)
