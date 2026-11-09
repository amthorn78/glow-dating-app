"""Glow's token strategy (``HEADLESS_TOKEN_STRATEGY``; the SV1 brief's D2, with DM-46's N2).

allauth's JWT strategy, with one addition: **a replayed refresh token ends its session.** In
65.21.1 a replayed rotated refresh token is refused, but its session lives on, so a stolen
current refresh token used first keeps a session the member's next refresh cannot end.

A refresh is allauth's own first. When allauth refuses it, the token is a replay only if it
passes allauth's own checks, run with allauth's own functions in allauth's order: its signature,
its expiry and its type (``decode_token``), then the session it names exists
(``get_token_session``), then that session's user is the token's (``validate_token_user``), but
it carries a ``jti`` the session no longer holds. Only then does the session end, at both layers
(``revocation.end_replayed_session``). This adds no cryptography. A forged, expired or
wrong-type token, or one whose session no longer exists, is refused as allauth refuses it, and
nothing more is done. The app sends one refresh at a time: two refreshes with the same token, or
a retry after a lost response, are a replay (carried to P11's client wiring).
"""

from __future__ import annotations

from allauth.headless.tokens.strategies.jwt import JWTTokenStrategy, internal

from glow_identity import revocation


def replayed_session_key(refresh_token: str) -> str | None:
    """The session a refused refresh token was replayed against, or None."""
    payload = internal.decode_token(refresh_token, "refresh")
    if payload is None:
        return None
    session = internal.get_token_session(payload)
    if session is None:
        return None
    if internal.validate_token_user(payload, session) is None:
        return None
    if payload["jti"] in internal.get_refresh_token_state(session):
        return None
    session_key = session.session_key
    return session_key if isinstance(session_key, str) else None


class GlowJWTTokenStrategy(JWTTokenStrategy):  # type: ignore[misc]
    def refresh_token(self, refresh_token: str) -> tuple[str, str] | None:
        refreshed = super().refresh_token(refresh_token)
        if refreshed is not None:
            return refreshed  # type: ignore[no-any-return]
        session_key = replayed_session_key(refresh_token)
        if session_key is not None:
            revocation.end_replayed_session(session_key)
        return None
