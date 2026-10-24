"""The conversation reads (P06.2 Stage C1, OD-45; the brief's "Stage C under OD-45",
points b, c and e): pure domain types, independent of Django.

Under Nathan's D8 answer (OD-45) the app holds no provider credential, and Glow's API
serves a conversation's history and its new messages. Glow's rows define the
conversation; the provider supplies only the texts. ``glow_chat.reads`` implements
``ConversationReads`` over the models; it runs only under the disposable-database
proof's settings until P11 wires it and serves the reads. No HTTP route is attached.

**Whatever refuses a send refuses a read** (point c). The history read, the conversation
list and the read-cursor command make the send's checks, in the send's order, on rows
read under the send's shared locks (``FOR SHARE``, as B1's grant): a valid, current
session of an ``active`` account; the match ``active`` with no block either way; neither
member suspended or deleted; neither profile paused or restricted; both onboarding
consents accepted. The rule is the interim default under F06 (DM-22 3.1); the history
question goes to Nathan before P11 serves the reads.

**Two checks around the provider call** (DM-22 3.2). The history read checks before the
provider call, so a refused member causes no provider read, and its transaction ends
before the call; no lock is held across it. After the call it checks again in a new
transaction that takes the same shared locks, and returns the page only if that check
passes too. A page with no accepted message makes no provider call, so it has nothing to
check again: its one check is its answer, as the list's is.

**The order follows acceptance** (DM-22 2.2). Accepted messages are ordered by the
moment Glow recorded the provider's acceptance: the ``delivered_at`` of the message's
``message_submitted`` outbox event (the database's ``clock_timestamp()`` in the
receipt's transaction), then that event's ``sequence``. The page, the "newer than" and
"older than" cursors, the unread count and the read cursor's "forward" all use it, so a
message accepted after a later one sorts after it and reaches the reader's next poll as
new and unread. It holds while one channel's receipts commit in the order of their
``delivered_at``, as they do under the one deliverer at a time the outbox assumes (the
data model, "Delivery"); a deployed worker with concurrent deliverers keeps that (P11).

**Only text Glow sent is shown** (DM-22 2.1). A provider's text is shown only if the
digest of the match ID, the row's ``contact_version`` and that text equals the row's
``request_digest`` (``glow_domain.chat.request_digest``). A message the provider does not
return (it returns none whose type is not ``regular`` or that is marked deleted) or whose
text fails the digest is "unavailable", one state with no reason (6.2), and counted in the
result for P11's reconciliation (2.3: a read writes nothing).

**A provider error fails the read** (DM-22 2.4): it is refused with the Glow code, the
retryable ``provider_unavailable`` for an outage; never a page in which every message is
unavailable.
"""

from __future__ import annotations

import base64
import binascii
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from .chat import TransactionProbe, TransactionTrace, request_digest
from .chat_provider import RETRYABLE, TEXT_READ_LIMIT

# A page's largest number of accepted messages: the production page limit, which is also
# the text read's cap, so a page's texts come in one provider call.
PAGE_LIMIT = TEXT_READ_LIMIT
# The member's own pending and failed submissions on the newest page: the most recent ones.
UNSENT_LIMIT = 50
# The conversation list's ceiling: the conversations with the latest activity.
LIST_LIMIT = 200

# Refusal reasons the reads add to the send's (``glow_domain.chat``).
CURSOR_INVALID = "cursor_invalid"
MESSAGE_UNAVAILABLE = "message_unavailable"

Direction = Literal["older", "newer"]
DeliveryState = Literal["pending", "accepted", "failed"]
ReadOutcome = Literal["read", "refused", "deadlock", "error"]

_CURSOR_VERSION = 1
_CURSOR_FORM = re.compile(r"c[A-Za-z0-9_-]{46}")


class CursorError(ValueError):
    """A page cursor that cannot be read; the request is refused as stale (6.4)."""


@dataclass(frozen=True)
class PageCursor:
    """Where a page continues: older or newer than one accepted message of one match.

    Its text is opaque to the client and bound to the match it was issued for (DM-22
    6.4): a read refuses a cursor whose match is not the request's, or whose message is
    not an accepted message of that match. It carries Glow's identifiers only, never a
    provider's."""

    direction: Direction
    match_id: UUID
    boundary: UUID

    def encode(self) -> str:
        raw = (
            bytes((_CURSOR_VERSION, 0 if self.direction == "older" else 1))
            + self.match_id.bytes
            + self.boundary.bytes
        )
        return "c" + base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @classmethod
    def decode(cls, text: str) -> PageCursor:
        if not isinstance(text, str) or not _CURSOR_FORM.fullmatch(text):
            raise CursorError("not a page cursor")
        try:
            raw = base64.urlsafe_b64decode(text[1:] + "==")
        except (binascii.Error, ValueError) as error:
            raise CursorError("not a page cursor") from error
        if len(raw) != 34 or raw[0] != _CURSOR_VERSION or raw[1] not in (0, 1):
            raise CursorError("not a page cursor")
        cursor = cls(
            "older" if raw[1] == 0 else "newer", UUID(bytes=raw[2:18]), UUID(bytes=raw[18:34])
        )
        if cursor.encode() != text:
            raise CursorError("not a page cursor")
        return cursor


@dataclass(frozen=True)
class HistoryRequest:
    """A page of one conversation for a member's session. The actor is the session's
    account, never a field of the request. No cursor: the newest page."""

    session_id: UUID
    match_id: UUID
    cursor: PageCursor | None = None
    limit: int = PAGE_LIMIT

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= PAGE_LIMIT:
            raise ValueError("a page holds 1 to PAGE_LIMIT messages")


@dataclass(frozen=True)
class ReadCursorCommand:
    """Move the member's own read cursor to an accepted message of the match."""

    session_id: UUID
    match_id: UUID
    submission_id: UUID


@dataclass(frozen=True)
class HistoryMessage:
    """One message of a page, as Glow's rows hold it. ``text`` is ``None`` for the
    "unavailable" state. ``delivery`` is the submission's state; the projection shows it
    for the member's own messages only."""

    submission_id: UUID
    own: bool
    at: datetime
    delivery: DeliveryState
    text: str | None


@dataclass(frozen=True)
class Reconciliation:
    """What a history read counted for P11's reconciliation (DM-22 2.3): accepted messages
    the provider answered without, texts that failed the digest, and IDs the provider
    returned that the read did not ask for (dropped)."""

    missing: int = 0
    mismatched: int = 0
    unrequested: int = 0


@dataclass(frozen=True)
class HistoryPage:
    match_id: UUID
    messages: tuple[HistoryMessage, ...]
    older: PageCursor | None
    newer: PageCursor | None
    provider_called: bool
    reconciliation: Reconciliation


@dataclass(frozen=True)
class ReadResult:
    """A history read: ``read`` with its page, or a refusal with a Glow code. ``traces``
    holds the first check's transaction and, after a provider call, the final check's."""

    outcome: ReadOutcome
    reason: str = ""
    page: HistoryPage | None = None
    traces: tuple[TransactionTrace, ...] = ()

    @property
    def retryable(self) -> bool:
        return self.outcome == "refused" and self.reason in RETRYABLE


@dataclass(frozen=True)
class LatestMarker:
    """A conversation's latest message, over the rows the member may see (DM-22 6.1):
    Glow's submission ID and Glow's time, and no text."""

    submission_id: UUID
    at: datetime


@dataclass(frozen=True)
class ConversationEntry:
    match_id: UUID
    unread: int
    latest: LatestMarker | None


@dataclass(frozen=True)
class ListResult:
    outcome: Literal["listed", "refused", "deadlock", "error"]
    reason: str = ""
    conversations: tuple[ConversationEntry, ...] = ()
    trace: TransactionTrace | None = None


@dataclass(frozen=True)
class CursorResult:
    outcome: Literal["moved", "no_change", "refused", "deadlock", "error"]
    reason: str = ""
    entry: ConversationEntry | None = None
    trace: TransactionTrace | None = None


@dataclass
class ReadProbe:
    """Hold points a caller may observe a history read at: inside its first check's
    transaction, between the provider call and the final check (no transaction is open
    there), and inside the final check's transaction. Each only signals and waits."""

    first: TransactionProbe | None = None
    after_provider_call: Callable[[], None] | None = None
    final: TransactionProbe | None = None


class TextReader(Protocol):
    """The one provider operation the history read uses (the chat provider port's)."""

    def read_message_texts(
        self, channel_id: str, message_ids: tuple[str, ...]
    ) -> dict[str, str]: ...


class ConversationReads(Protocol):
    def read_history(
        self, request: HistoryRequest, *, probe: ReadProbe | None = None
    ) -> ReadResult: ...

    def list_conversations(
        self, session_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ListResult: ...

    def move_read_cursor(
        self, command: ReadCursorCommand, *, probe: TransactionProbe | None = None
    ) -> CursorResult: ...


# -- the page, from Glow's rows and the provider's texts ---------------------------------


@dataclass(frozen=True)
class AcceptedRow:
    """An accepted submission as the first check read it: its acceptance time, and what
    the digest check needs. The provider message ID never leaves the server."""

    submission_id: UUID
    own: bool
    accepted_at: datetime
    contact_version: int
    request_digest: str
    provider_message_ref: str


@dataclass(frozen=True)
class UnsentRow:
    """One of the member's own pending or failed submissions, with its spool text (or
    ``None`` once the spool is cleared) and its send time."""

    submission_id: UUID
    sent_at: datetime
    delivery: Literal["pending", "failed"]
    text: str | None


def page_messages(
    match_id: UUID,
    accepted: Sequence[AcceptedRow],
    unsent: Sequence[UnsentRow],
    texts: Mapping[str, object],
) -> tuple[tuple[HistoryMessage, ...], Reconciliation]:
    """The page's messages: each accepted row with the provider's text only if its digest
    is the row's (2.1), else unavailable and counted; then the member's own unsent rows
    with their spool text. ``texts`` is what the provider returned, by its message ID."""
    asked = {row.provider_message_ref for row in accepted}
    missing = mismatched = 0
    messages: list[HistoryMessage] = []
    for row in accepted:
        text = texts.get(row.provider_message_ref)
        shown: str | None = None
        if not isinstance(text, str):
            missing += 1
        elif request_digest(match_id, row.contact_version, text) != row.request_digest:
            mismatched += 1
        else:
            shown = text
        messages.append(
            HistoryMessage(row.submission_id, row.own, row.accepted_at, "accepted", shown)
        )
    for unsent_row in unsent:
        messages.append(
            HistoryMessage(
                unsent_row.submission_id,
                True,
                unsent_row.sent_at,
                unsent_row.delivery,
                unsent_row.text,
            )
        )
    unrequested = sum(1 for key in texts if key not in asked)
    return tuple(messages), Reconciliation(missing, mismatched, unrequested)
