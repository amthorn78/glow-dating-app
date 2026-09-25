"""The app-side send path: check the match and block state, then send server-side.

A client never sends through Stream directly. The app server authorizes the
send against its own state and then sends through the server SDK on the user's
behalf. A refused send makes no Stream call at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .policy import MatchState, SendDecision


class MessageSender(Protocol):
    def send_as(self, channel_type: str, channel_id: str, user_id: str, text: str) -> Any: ...


@dataclass(frozen=True)
class SendOutcome:
    decision: SendDecision
    stream_called: bool
    message_id: str | None = None
    status: int | None = None


class AppSendService:
    def __init__(self, state: MatchState, sender: MessageSender, channel_type: str) -> None:
        self._state = state
        self._sender = sender
        self._channel_type = channel_type

    def send(self, sender_id: str, channel_id: str, text: str) -> SendOutcome:
        decision = self._state.send_decision(sender_id, channel_id, text)
        if not decision.allowed:
            return SendOutcome(decision=decision, stream_called=False)
        result = self._sender.send_as(self._channel_type, channel_id, sender_id, text)
        message_id = None
        body = getattr(result, "body", None)
        if isinstance(body, dict):
            message = body.get("message")
            if isinstance(message, dict) and isinstance(message.get("id"), str):
                message_id = message["id"]
        return SendOutcome(
            decision=decision,
            stream_called=True,
            message_id=message_id,
            status=getattr(result, "status", None),
        )
