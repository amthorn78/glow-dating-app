"""The server's projections of the conversation reads into the production contracts (P06.2
Stage C1; the brief's "Stage C under OD-45", point f; DM-21 2.3; DM-22 6.1 to 6.4).

Each function turns a ``glow_domain.chat_reads`` result into a DTO of
``packages/contracts/production/gapp-api-v1.schema.json``: ``ConversationList``,
``ConversationSummary``, ``MessagePage``, and an ``Error`` for a refusal. They read only
the domain types' fields, which hold Glow's identifiers, Glow's times and the text Glow
sent; no provider ID, timestamp or field exists in them to project, and each DTO is
built from an allowlist of its keys. "Unavailable" is one state with no reason (6.2). A
refusal tells the member no more than the match's projection shows (F10, F13): every
reason about the conversation or the other member is ``not_found``.

The requests go the other way: ``page_request`` and ``read_cursor_command`` turn a
validated ``MessagePageRequest`` or ``ReadCursorIntent`` and the authenticated session
into the domain's request; the session, never a field of the request, names the actor.

Nothing here logs, and nothing is served: P11 serves the endpoints.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from . import chat
from .chat_provider import ERROR_CODES, RETRYABLE
from .chat_reads import (
    CURSOR_INVALID,
    ConversationEntry,
    HistoryMessage,
    HistoryPage,
    HistoryRequest,
    LatestMarker,
    ListResult,
    PageCursor,
    ReadCursorCommand,
)

CONTRACT_VERSION = "gapp-api-v1"

# Reasons about the member's own session: the client restarts authentication.
_UNAUTHENTICATED = frozenset(
    {
        chat.SESSION_MISSING,
        chat.SESSION_NOT_VALID,
        chat.SESSION_EXPIRED,
        chat.SESSION_EPOCH_STALE,
        chat.SESSION_CHANGED,
        "accountsession_missing",
    }
)


def instant(moment: datetime) -> str:
    """Glow's time as the contracts' ``Instant``: UTC, whole seconds, truncated."""
    if moment.tzinfo is None:
        raise ValueError("an aware time is required")
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def latest_marker(marker: LatestMarker | None) -> dict[str, Any] | None:
    """Glow's submission ID and Glow's time; never text (6.1)."""
    if marker is None:
        return None
    return {"submission_id": str(marker.submission_id), "at": instant(marker.at)}


def conversation_summary(entry: ConversationEntry) -> dict[str, Any]:
    """A conversation the member may see: always ``open``. ``closed`` carries no count
    and no marker, and only a later push or the app's own state uses it."""
    if entry.unread < 0:
        raise ValueError("an unread count is never negative")
    return {
        "kind": "conversation",
        "match_id": str(entry.match_id),
        "state": "open",
        "unread_count": entry.unread,
        "latest": latest_marker(entry.latest),
    }


def conversation_list(result: ListResult) -> dict[str, Any]:
    if result.outcome != "listed":
        raise ValueError("only a listed result has conversations")
    return {
        "kind": "conversation_list",
        "conversations": [conversation_summary(entry) for entry in result.conversations],
    }


def conversation_message(message: HistoryMessage) -> dict[str, Any]:
    """One message: the text Glow sent, or the one unavailable state; the delivery state
    for the member's own messages only. Another member's message is an accepted one."""
    if not message.own and message.delivery != "accepted":
        raise ValueError("another member's pending or failed submission never appears")
    return {
        "submission_id": str(message.submission_id),
        "author": "own" if message.own else "other",
        "at": instant(message.at),
        "content": "text" if message.text is not None else "unavailable",
        "text": message.text,
        "delivery": message.delivery if message.own else None,
    }


def message_page(page: HistoryPage) -> dict[str, Any]:
    return {
        "kind": "message_page",
        "match_id": str(page.match_id),
        "messages": [conversation_message(message) for message in page.messages],
        "older_cursor": page.older.encode() if page.older is not None else None,
        "newer_cursor": page.newer.encode() if page.newer is not None else None,
    }


def error_for(outcome: str, reason: str) -> tuple[str, bool]:
    """A read's refusal as the contracts' ``Error`` code and whether it is retryable.

    The member's own session: ``unauthenticated``. A page cursor that is not this match's
    (6.4): ``stale_version``. A provider failure: ``provider_unavailable``, retryable only
    for an outage (2.4). A deadlock: ``state_conflict``, retryable; another database
    error: ``state_conflict``. Everything about the conversation or the other member:
    ``not_found``, the generic unavailable object (F10, F13)."""
    if outcome == "deadlock":
        return "state_conflict", True
    if outcome == "error":
        return "state_conflict", False
    if reason in _UNAUTHENTICATED:
        return "unauthenticated", False
    if reason == CURSOR_INVALID:
        return "stale_version", False
    if reason in ERROR_CODES:
        return "provider_unavailable", reason in RETRYABLE
    return "not_found", False


def error(outcome: str, reason: str, request_id: UUID) -> dict[str, Any]:
    code, retryable = error_for(outcome, reason)
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": str(request_id),
        "code": code,
        "retryable": retryable,
    }


def response(data: Mapping[str, Any], request_id: UUID) -> dict[str, Any]:
    """The ``AppResponse`` envelope around one DTO."""
    return {"contract_version": CONTRACT_VERSION, "request_id": str(request_id), "data": dict(data)}


def page_request(dto: Mapping[str, Any], session_id: UUID) -> HistoryRequest:
    """A validated ``MessagePageRequest`` for the authenticated session. A cursor that
    cannot be read raises ``CursorError`` (a ``stale_version`` refusal)."""
    match_id = UUID(dto["match_id"])
    text = dto["cursor"]
    cursor = PageCursor.decode(text) if text is not None else None
    return HistoryRequest(session_id, match_id, cursor, int(dto["limit"]))


def read_cursor_command(dto: Mapping[str, Any], session_id: UUID) -> ReadCursorCommand:
    """A validated ``ReadCursorIntent`` for the authenticated session."""
    if dto.get("operation") != "read_cursor":
        raise ValueError("not a read-cursor intent")
    return ReadCursorCommand(session_id, UUID(dto["match_id"]), UUID(dto["submission_id"]))
