"""An in-memory chat provider for development and tests (P06.2 Stage A).

It keeps what a provider would hold for Glow: channels with their members and message
history, and users with their state and token cut-offs. It is idempotent as the real
adapter must be: a repeated create of a known channel, or a repeated message ID,
returns the existing object and creates nothing. Failures are injected only through
``fail_next``, before or after the call's effect, so a test can show a lost response.
Every call is recorded with its argument names, so a test can show that no name,
image or custom field was ever sent. It reaches no network.
"""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

from .chat_provider import (
    CHANNEL_UNAVAILABLE,
    MEMBER_UNAVAILABLE,
    OPERATIONS,
    PROVIDER_REJECTED,
    PROVIDER_UNAVAILABLE,
    ChatErrorCode,
    ChatProviderError,
    ProviderReceipt,
)
from .provider_fixtures import require_fixture_environment


@dataclass
class FixtureChannel:
    created_members: tuple[str, str]
    members: set[str]
    # (message ID, sender, text), in the order the provider accepted them.
    messages: list[tuple[str, str, str]] = field(default_factory=list)
    # The message count at each removal of members, in order.
    removals: list[int] = field(default_factory=list)


@dataclass
class FixtureUser:
    active: bool = True
    token_cutoffs: list[datetime] = field(default_factory=list)


@dataclass(frozen=True)
class FixtureCall:
    operation: str
    arguments: frozenset[str]
    outcome: str


@dataclass(frozen=True)
class ScheduledFailure:
    operation: str
    # None: raise something that is not a ChatProviderError, carrying provider text.
    code: ChatErrorCode | None
    after_effect: bool
    text: str


class FixtureProviderOutage(RuntimeError):
    """Stands in for whatever a real provider client raises, text included."""


class FixtureChatProvider:
    name = "fixture"

    def __init__(self, environment: str) -> None:
        require_fixture_environment(environment)
        self.channels: dict[str, FixtureChannel] = {}
        self.users: dict[str, FixtureUser] = {}
        self.calls: list[FixtureCall] = []
        self._failures: deque[ScheduledFailure] = deque()
        self._lock = threading.Lock()

    # -- failure injection -------------------------------------------------------------

    def fail_next(
        self,
        operation: str,
        *,
        code: ChatErrorCode | None = PROVIDER_UNAVAILABLE,
        after_effect: bool = False,
        text: str = "fixture provider failure text",
    ) -> None:
        """The next call of ``operation`` fails: before its effect, or after it (the
        provider acted, but its answer was lost)."""
        if operation not in OPERATIONS:
            raise ValueError("unknown operation")
        self._failures.append(ScheduledFailure(operation, code, after_effect, text))

    def _failure(self, operation: str) -> ScheduledFailure | None:
        for failure in self._failures:
            if failure.operation == operation:
                self._failures.remove(failure)
                return failure
        return None

    @staticmethod
    def _raise(failure: ScheduledFailure) -> None:
        if failure.code is None:
            raise FixtureProviderOutage(failure.text)
        raise ChatProviderError(failure.code)

    def _call(
        self,
        operation: str,
        arguments: dict[str, object],
        effect: Callable[[], ProviderReceipt],
    ) -> ProviderReceipt:
        if set(arguments) - OPERATIONS[operation]:
            raise AssertionError("an argument outside the operation's identifiers")
        with self._lock:
            failure = self._failure(operation)
            if failure is not None and not failure.after_effect:
                self.calls.append(FixtureCall(operation, frozenset(arguments), "failed_before"))
                self._raise(failure)
            try:
                receipt = effect()
            except ChatProviderError as error:
                self.calls.append(FixtureCall(operation, frozenset(arguments), error.code))
                raise
            if failure is not None:
                self.calls.append(FixtureCall(operation, frozenset(arguments), "failed_after"))
                self._raise(failure)
            outcome = "already" if receipt.already else "ok"
            self.calls.append(FixtureCall(operation, frozenset(arguments), outcome))
            return receipt

    # -- the port ----------------------------------------------------------------------

    def create_channel(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        def effect() -> ProviderReceipt:
            if len(set(members)) != 2:
                raise ChatProviderError(PROVIDER_REJECTED)
            existing = self.channels.get(channel_id)
            if existing is not None:
                if set(existing.created_members) != set(members):
                    raise ChatProviderError(PROVIDER_REJECTED)
                return ProviderReceipt(channel_id, already=True)
            for user_id in members:
                user = self.users.setdefault(user_id, FixtureUser())
                if not user.active:
                    raise ChatProviderError(MEMBER_UNAVAILABLE)
            self.channels[channel_id] = FixtureChannel(members, set(members))
            return ProviderReceipt(channel_id)

        return self._call("create_channel", {"channel_id": channel_id, "members": members}, effect)

    def send_message(
        self, channel_id: str, sender: str, message_id: str, text: str
    ) -> ProviderReceipt:
        def effect() -> ProviderReceipt:
            channel = self.channels.get(channel_id)
            if channel is None:
                raise ChatProviderError(CHANNEL_UNAVAILABLE)
            for known_id, known_sender, _ in channel.messages:
                if known_id == message_id:
                    if known_sender != sender:
                        raise ChatProviderError(PROVIDER_REJECTED)
                    return ProviderReceipt(message_id, already=True)
            user = self.users.get(sender)
            if user is None or not user.active or sender not in channel.members:
                raise ChatProviderError(MEMBER_UNAVAILABLE)
            channel.messages.append((message_id, sender, text))
            return ProviderReceipt(message_id)

        arguments = {"channel_id": channel_id, "sender": sender, "message_id": message_id}
        return self._call("send_message", {**arguments, "text": text}, effect)

    def remove_members(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        def effect() -> ProviderReceipt:
            channel = self.channels.get(channel_id)
            if channel is None:
                raise ChatProviderError(CHANNEL_UNAVAILABLE)
            present = channel.members & set(members)
            if not present:
                return ProviderReceipt(channel_id, already=True)
            channel.members -= set(members)
            channel.removals.append(len(channel.messages))
            return ProviderReceipt(channel_id)

        return self._call("remove_members", {"channel_id": channel_id, "members": members}, effect)

    def deactivate_user(self, user_id: str) -> ProviderReceipt:
        def effect() -> ProviderReceipt:
            user = self.users.get(user_id)
            if user is None:
                raise ChatProviderError(MEMBER_UNAVAILABLE)
            if not user.active:
                return ProviderReceipt(user_id, already=True)
            user.active = False
            return ProviderReceipt(user_id)

        return self._call("deactivate_user", {"user_id": user_id}, effect)

    def revoke_user_tokens(self, user_id: str, issued_before: datetime) -> ProviderReceipt:
        def effect() -> ProviderReceipt:
            user = self.users.get(user_id)
            if user is None:
                raise ChatProviderError(MEMBER_UNAVAILABLE)
            if issued_before in user.token_cutoffs:
                return ProviderReceipt(user_id, already=True)
            user.token_cutoffs.append(issued_before)
            return ProviderReceipt(user_id)

        arguments = {"user_id": user_id, "issued_before": issued_before}
        return self._call("revoke_user_tokens", arguments, effect)
