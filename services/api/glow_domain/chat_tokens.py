"""The chat token rules (P06.2 item 4, D6): who may hold a provider user token.

A token grant is issued only for a valid, unexpired session at its account's current
epoch, of an ``active`` account that has a provider identity. It lives one hour. It is
refused after a suspension or a deletion, because a token issued after a per-user
revocation works (the architecture document, section 8). After a block the user keeps
its token for its other matches; removal from the blocked match's channel ends its
reads there.

This is a domain function with offline tests. It signs nothing, issues no real token
and calls no provider; P11 serves the endpoint and Stage B2's adapter signs. The
persistence adapter (``glow_chat.contact``, Stage B1) runs these checks on the locked
account and session rows with the database's clock as ``now`` (F1; DM-14 item 3), so the
issue time and a revocation's cut-off come from one clock.

A provider's per-user token revocation compares a token's issue time with its cut-off in
whole seconds. ``revocation_cutoff_sent`` is the value sent for a cut-off: the next whole
second, strictly after the exact time (DM-15 5.2), so every token issued at or before the
cut-off is covered; Glow keeps the exact time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from . import chat

TOKEN_LIFETIME = timedelta(hours=1)
NO_CHAT_IDENTITY = "no_chat_identity"


def revocation_cutoff_sent(cutoff: datetime) -> datetime:
    """The cut-off as sent to the provider: the next whole second, strictly greater than
    the exact cut-off, so a cut-off of exactly 10.000000 s is sent as 11 (DM-15 5.2). A
    token whose ``iat`` is the issue time truncated to the second is then revoked whenever
    it was issued at or before the cut-off."""
    if cutoff.tzinfo is None:
        raise ValueError("an aware time is required")
    return cutoff.replace(microsecond=0) + timedelta(seconds=1)


@dataclass(frozen=True)
class TokenAccount:
    state: str
    session_epoch: int


@dataclass(frozen=True)
class TokenSession:
    state: str
    epoch: int
    expires_at: datetime


@dataclass(frozen=True)
class TokenGrant:
    """What the provider adapter would sign: the opaque user ID and the lifetime."""

    user_ref: str
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class TokenRefusal:
    code: str


def grant_chat_token(
    *,
    account: TokenAccount,
    session: TokenSession,
    user_ref: str | None,
    identity_active: bool,
    now: datetime,
) -> TokenGrant | TokenRefusal:
    """A one-hour grant, or the Glow code that refuses it. ``now`` must be aware.
    ``identity_active`` means provisioned and not deactivated (DM-15 5.1): an identity the
    provider does not hold yet is refused with ``no_chat_identity``."""
    if now.tzinfo is None:
        raise ValueError("an aware time is required")
    if account.state != "active":
        return TokenRefusal(chat.ACCOUNT_NOT_ACTIVE)
    if session.state != "valid":
        return TokenRefusal(chat.SESSION_NOT_VALID)
    if session.expires_at <= now:
        return TokenRefusal(chat.SESSION_EXPIRED)
    if session.epoch != account.session_epoch:
        return TokenRefusal(chat.SESSION_EPOCH_STALE)
    if not user_ref or not identity_active:
        return TokenRefusal(NO_CHAT_IDENTITY)
    return TokenGrant(user_ref, now, now + TOKEN_LIFETIME)
