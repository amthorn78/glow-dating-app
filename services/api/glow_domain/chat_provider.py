"""The chat provider port (P06.2 Stage A; Stage B adds the Stream adapter beside it).

Each operation is one provider call and takes only identifiers, the two members and,
for a message, its text: there is no parameter for a channel, member or user name,
image or custom field, and no operation creates an invite, a call, a feed or an
activity (the brief, item 3; the architecture document, sections 3 and 6). Every
identifier is Glow's own random value, committed before the call, so a retry repeats
the same call and never creates a second channel, message or member.

A provider adapter raises only ``ChatProviderError`` with a Glow code. Whatever else
it raises is mapped to ``PROVIDER_UNAVAILABLE`` by the caller; no provider text is
ever stored, logged or shown.
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

# The five operations, and the arguments each may carry. Nothing else exists.
OPERATIONS: dict[str, frozenset[str]] = {
    "create_channel": frozenset({"channel_id", "members"}),
    "send_message": frozenset({"channel_id", "sender", "message_id", "text"}),
    "remove_members": frozenset({"channel_id", "members"}),
    "deactivate_user": frozenset({"user_id"}),
    "revoke_user_tokens": frozenset({"user_id", "issued_before"}),
}


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


@dataclass(frozen=True)
class ProviderReceipt:
    """What the provider confirmed: the identifier it now holds (the one Glow sent),
    and whether it already held it before this call (a retry)."""

    ref: str
    already: bool = False


class ChatProvider(Protocol):
    name: str

    def create_channel(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        """The match's channel with exactly its two members."""

    def send_message(
        self, channel_id: str, sender: str, message_id: str, text: str
    ) -> ProviderReceipt:
        """An authorized message, sent on the member's behalf by the server."""

    def remove_members(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        """Both members leave the channel; its history stays at the provider (D6)."""

    def deactivate_user(self, user_id: str) -> ProviderReceipt: ...

    def revoke_user_tokens(self, user_id: str, issued_before: datetime) -> ProviderReceipt:
        """Every token of the user issued before the cut-off stops working."""
