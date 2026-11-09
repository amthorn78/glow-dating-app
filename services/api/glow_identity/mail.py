"""SV1's mail seam (the SV1 brief's D8): Django's email backend, which allauth sends through.

``FixtureEmailBackend`` records each message in memory. It has no network code: it opens no
connection, reads no SMTP setting and names no provider, so nothing it is given leaves the
process. Glow's account adapter words every message (``glow_identity.messages``), in plain text
only; the backend refuses a message with copies, alternatives or attachments. P11 and M07 choose
the provider (OD-50).
"""

from __future__ import annotations

import threading
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from django.core.mail.backends.base import BaseEmailBackend


@dataclass(frozen=True)
class RecordedMessage:
    to: tuple[str, ...]
    subject: str
    body: str
    from_email: str


_lock = threading.Lock()
_outbox: list[RecordedMessage] = []


def outbox() -> tuple[RecordedMessage, ...]:
    with _lock:
        return tuple(_outbox)


def clear() -> None:
    with _lock:
        _outbox.clear()


class RefusedMessage(ValueError):
    """A message that is not plain text to its own recipients."""


class FixtureEmailBackend(BaseEmailBackend):  # type: ignore[misc]
    def send_messages(self, email_messages: Sequence[Any]) -> int:
        recorded: list[RecordedMessage] = []
        for message in email_messages:
            if message.cc or message.bcc or getattr(message, "reply_to", None):
                raise RefusedMessage("a Glow message has its recipients only")
            if message.attachments or getattr(message, "alternatives", None):
                raise RefusedMessage("a Glow message is plain text only")
            if message.content_subtype != "plain":
                raise RefusedMessage("a Glow message is plain text only")
            recorded.append(
                RecordedMessage(
                    to=tuple(str(address) for address in message.to),
                    subject=str(message.subject),
                    body=str(message.body),
                    from_email=str(message.from_email),
                )
            )
        with _lock:
            _outbox.extend(recorded)
        return len(recorded)
