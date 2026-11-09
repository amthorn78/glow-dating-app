"""Glow's wording for every message allauth asks its account adapter to send (the SV1 brief's D8).

Plain text, Glow's name only (ADR 0003, S15: no indication that anything happens outside Glow),
no link, no tracking, and no account detail beyond what the message needs: no address but the
recipient's own, no IP address and no device. A code message holds the code and its expiry.
The wording is SV1's; the members' final copy is a product decision before P11 sends mail.

A message allauth asks for that Glow has not worded is refused (``UnwordedMessage``), so no
template of allauth's, with its links, is ever rendered. In SV1 the unknown-account message is
never asked for (``ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS`` is off), and neither the password-set notice
nor the email-deleted notice is reachable: every member has a usable password, and with
``ACCOUNT_CHANGE_EMAIL`` an account holds one address. Both are worded all the same.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from allauth.account import app_settings as account_settings


@dataclass(frozen=True)
class Message:
    subject: str
    body: str


class UnwordedMessage(LookupError):
    """allauth asked for a message Glow has not worded."""


_IGNORE = "If you did not ask for this, you can ignore this message."


def _minutes(seconds: int) -> str:
    minutes = max(1, seconds // 60)
    return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"


def _code(context: Mapping[str, Any]) -> str:
    code = context.get("code")
    if not isinstance(code, str) or not code:
        raise UnwordedMessage("a code message without its code")
    return code


def _verification(context: Mapping[str, Any], purpose: str) -> Message:
    expiry = _minutes(account_settings.EMAIL_VERIFICATION_BY_CODE_TIMEOUT)
    return Message(
        "Your Glow verification code",
        f"Your Glow verification code is {_code(context)}.\n\n"
        f"It expires in {expiry}. Enter it in the Glow app {purpose}.\n\n{_IGNORE}",
    )


def _password_reset_code(context: Mapping[str, Any]) -> Message:
    expiry = _minutes(account_settings.PASSWORD_RESET_BY_CODE_TIMEOUT)
    return Message(
        "Your Glow password reset code",
        f"Your Glow password reset code is {_code(context)}.\n\n"
        f"It expires in {expiry}. Enter it in the Glow app to choose a new password.\n\n"
        "If you did not ask to reset your password, you can ignore this message. "
        "Your password has not changed.",
    )


def _fixed(subject: str, body: str) -> Any:
    def render(context: Mapping[str, Any]) -> Message:
        return Message(subject, body)

    return render


_RESET_ADVICE = "If you did not do this, reset your password from the Glow app's sign-in screen."

_RENDERERS: dict[str, Any] = {
    # Sign-up's verification (D3), and a code to an address asked for later: an email change
    # or a sign-in with an address not yet verified.
    "account/email/email_confirmation_signup": lambda c: _verification(
        c, "to finish creating your account"
    ),
    "account/email/email_confirmation": lambda c: _verification(c, "to confirm this address"),
    "account/email/password_reset_code": _password_reset_code,
    # D3: Glow's own account-already-exists message, with no link.
    "account/email/account_already_exists": _fixed(
        "Your Glow account",
        "Someone tried to create a Glow account with this email address, which already has "
        "one.\n\nIf this was you, sign in to the Glow app. If you have forgotten your password, "
        "you can reset it from the sign-in screen.\n\nIf it was not you, you can ignore this "
        "message.",
    ),
    # D8: the account-change notices (G-04, UST-16), for every member.
    "account/email/password_changed": _fixed(
        "Your Glow password was changed",
        "The password for your Glow account was changed, and every device was signed out.\n\n"
        + _RESET_ADVICE,
    ),
    "account/email/password_set": _fixed(
        "A password was set for your Glow account",
        "A password was set for your Glow account, and every device was signed out.\n\n"
        + _RESET_ADVICE,
    ),
    "account/email/password_reset": _fixed(
        "Your Glow password was reset",
        "The password for your Glow account was reset, and every device was signed out.\n\n"
        "If you did not do this, reset your password again from the Glow app's sign-in screen.",
    ),
    # Sent to the old address: it names neither address.
    "account/email/email_changed": _fixed(
        "Your Glow email address was changed",
        "The email address for your Glow account was changed. Glow will no longer send "
        "messages about your account to this address.\n\nIf you did not make this change, "
        "contact Glow.",
    ),
    "account/email/email_deleted": _fixed(
        "An email address was removed from your Glow account",
        "An email address was removed from your Glow account.\n\nIf you did not make this "
        "change, contact Glow.",
    ),
}

WORDED = frozenset(_RENDERERS)


def render(template_prefix: str, context: Mapping[str, Any]) -> Message:
    renderer = _RENDERERS.get(template_prefix)
    if renderer is None:
        raise UnwordedMessage("Glow has not worded this message")
    message = renderer(context)
    assert isinstance(message, Message)
    return message
