"""The harness's stand-in for the app's match and block state.

The app, not Stream, decides whether a send is authorized: the pair must have a
current match whose channel is the target, the sender must be one of the pair,
and neither person may have blocked the other. This is fixture state held in
memory for the proof; the real authority is the app's persisted relationship
state (P05.3, P11).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Reason = Literal["authorized", "no_current_match", "not_a_participant", "blocked", "empty_text"]


@dataclass(frozen=True)
class SendDecision:
    allowed: bool
    reason: Reason
    recipient: str | None = None


@dataclass
class MatchState:
    # channel id -> the two user ids of its current match
    _channels: dict[str, frozenset[str]] = field(default_factory=dict)
    # (blocker, blocked)
    _blocks: set[tuple[str, str]] = field(default_factory=set)

    def add_match(self, user_a: str, user_b: str, channel_id: str) -> None:
        if user_a == user_b:
            raise ValueError("a match needs two different users")
        self._channels[channel_id] = frozenset({user_a, user_b})

    def unmatch(self, channel_id: str) -> None:
        self._channels.pop(channel_id, None)

    def block(self, blocker: str, blocked: str) -> None:
        self._blocks.add((blocker, blocked))

    def members(self, channel_id: str) -> frozenset[str] | None:
        return self._channels.get(channel_id)

    def is_blocked(self, user_a: str, user_b: str) -> bool:
        return (user_a, user_b) in self._blocks or (user_b, user_a) in self._blocks

    def send_decision(self, sender: str, channel_id: str, text: str) -> SendDecision:
        members = self._channels.get(channel_id)
        if members is None:
            return SendDecision(False, "no_current_match")
        if sender not in members:
            return SendDecision(False, "not_a_participant")
        (recipient,) = members - {sender}
        if self.is_blocked(sender, recipient):
            return SendDecision(False, "blocked")
        if not text.strip():
            return SendDecision(False, "empty_text")
        return SendDecision(True, "authorized", recipient)
