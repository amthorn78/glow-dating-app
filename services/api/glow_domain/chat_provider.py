"""The chat provider port (P06.2 Stage A; Stage B1 adds user provisioning, CX4; Stage
B2 adds the Stream adapter beside it).

Each operation is one provider call and takes only identifiers, the two members and,
for a message, its text: there is no parameter for a channel, member or user name,
image or custom field, and no operation creates an invite, a call, a feed or an
activity (the brief, item 3; the architecture document, sections 3 and 6). Every
identifier is Glow's own random value, committed before the call, so a retry repeats
the same call and never creates a second channel, message or member. A provider needs
a user before a channel names it (CX4): ``provision_user`` creates the opaque user,
idempotently, and is delivered before the channel that names it (DM-15 3.1 to 3.5).

A provider adapter raises only ``ChatProviderError`` with a Glow code. Whatever else
it raises is mapped to ``PROVIDER_UNAVAILABLE`` by the caller; no provider text is
ever stored, logged or shown.

**The text read** (P06.2 Stage C1, OD-45; the brief's "Stage C under OD-45", point b).
Glow's rows define a conversation, and the provider is asked only for the texts of the
messages Glow committed: ``read_message_texts`` takes a channel ID and a page's message
IDs, at most ``TEXT_READ_LIMIT``, and returns, for each of those messages the provider
holds as a ``regular`` message with no deleted marker, its ID and its text, and nothing
else. A message the provider holds of another type, or deleted, is left out, so the
caller shows it as unavailable (DM-22 2.1). Asking for no ID, more than the cap or one ID
twice is the caller's error, refused before any request.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol

ChatErrorCode = Literal[
    "provider_unavailable",
    "provider_rejected",
    "channel_unavailable",
    "member_unavailable",
]
PROVIDER_UNAVAILABLE: ChatErrorCode = "provider_unavailable"
PROVIDER_REJECTED: ChatErrorCode = "provider_rejected"
CHANNEL_UNAVAILABLE: ChatErrorCode = "channel_unavailable"
MEMBER_UNAVAILABLE: ChatErrorCode = "member_unavailable"
ERROR_CODES: frozenset[str] = frozenset(
    {PROVIDER_UNAVAILABLE, PROVIDER_REJECTED, CHANNEL_UNAVAILABLE, MEMBER_UNAVAILABLE}
)
# Only an outage is worth repeating; every other code is final for the event.
RETRYABLE: frozenset[str] = frozenset({PROVIDER_UNAVAILABLE})

# The seven operations, and the arguments each may carry. Nothing else exists.
OPERATIONS: dict[str, frozenset[str]] = {
    "provision_user": frozenset({"user_id"}),
    "create_channel": frozenset({"channel_id", "members"}),
    "send_message": frozenset({"channel_id", "sender", "message_id", "text"}),
    "remove_members": frozenset({"channel_id", "members"}),
    "deactivate_user": frozenset({"user_id"}),
    "revoke_user_tokens": frozenset({"user_id", "issued_before"}),
    # P06.2 Stage C1: the texts of a page's messages, by the IDs Glow committed.
    "read_message_texts": frozenset({"channel_id", "message_ids"}),
}

# The most message IDs one text read may ask for (P06.2 Stage C1): a page's texts come in
# one call, so the cap is the production page limit, ``MessagePageRequest.limit``'s 50.
TEXT_READ_LIMIT = 50


class ChatProviderError(Exception):
    """A provider failure, as a Glow code only. The message is the code itself."""

    def __init__(self, code: ChatErrorCode) -> None:
        if code not in ERROR_CODES:
            raise ValueError("unknown chat error code")
        super().__init__(code)
        self.code: ChatErrorCode = code

    @property
    def retryable(self) -> bool:
        return self.code in RETRYABLE


def error_code(error: BaseException) -> ChatErrorCode:
    """The Glow code for anything a provider call raised; never its text."""
    if isinstance(error, ChatProviderError):
        return error.code
    return PROVIDER_UNAVAILABLE


def text_read_ids(message_ids: tuple[str, ...]) -> tuple[str, ...]:
    """The IDs one text read may ask for: at least one, at most ``TEXT_READ_LIMIT``, each a
    non-empty string, none twice. Anything else is the caller's error, refused here, before
    any request (P06.2 Stage C1)."""
    if not isinstance(message_ids, tuple) or not message_ids:
        raise ValueError("a text read asks for at least one message ID")
    if len(message_ids) > TEXT_READ_LIMIT:
        raise ValueError("a text read asks for at most TEXT_READ_LIMIT message IDs")
    if not all(isinstance(message_id, str) and message_id for message_id in message_ids):
        raise ValueError("a message ID is a non-empty string")
    if len(set(message_ids)) != len(message_ids):
        raise ValueError("a text read asks for each message ID once")
    return message_ids


@dataclass(frozen=True)
class ProviderReceipt:
    """What the provider confirmed: the identifier it now holds (the one Glow sent),
    and whether it already held it before this call (a retry)."""

    ref: str
    already: bool = False


class ChatProvider(Protocol):
    name: str

    def provision_user(self, user_id: str) -> ProviderReceipt:
        """The opaque user, with no name, image or custom field (CX4; DM-15 3.4). A user
        the provider already holds is returned with ``already=True``."""

    def create_channel(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        """The match's channel with exactly its two members, each provisioned before."""

    def send_message(
        self, channel_id: str, sender: str, message_id: str, text: str
    ) -> ProviderReceipt:
        """An authorized message, sent on the member's behalf by the server."""

    def remove_members(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        """Both members leave the channel; its history stays at the provider (D6)."""

    def deactivate_user(self, user_id: str) -> ProviderReceipt: ...

    def revoke_user_tokens(self, user_id: str, issued_before: datetime) -> ProviderReceipt:
        """Every token of the user issued before the cut-off stops working."""

    def read_message_texts(self, channel_id: str, message_ids: tuple[str, ...]) -> dict[str, str]:
        """For each asked message the provider holds as a ``regular`` message with no
        deleted marker: its ID and its text, and nothing else (P06.2 Stage C1). A message
        the provider does not return is the caller's "unavailable"; a provider failure is a
        ``ChatProviderError``, never a partial answer."""
