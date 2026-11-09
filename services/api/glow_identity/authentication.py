"""The actor, from maintained authentication (the SV1 brief's D7): the one DRF authentication
class SV2 to SV4 use. It is the only place a later slice gets an actor.

1. allauth's ``JWTTokenAuthentication`` authenticates the access token, with stateful validation
   on: its signature, expiry and type, then the session its ``sid`` names exists and that
   session's user is the token's (``validate_access_token``).
2. The session is taken from the validated token's own ``sid``, decrypted with allauth's own
   function (``session_key_from_sid``) and held in memory only, never logged; never from an
   ``X-Session-Token`` header, which allauth's ``get_session_token`` would prefer (D5).
3. The ``AccountSession`` is the one whose reference is that session's ``UserSession`` primary
   key, with its account. The actor is refused, as ``unauthenticated`` (the contract's 401),
   unless the account is ``active`` and the session is ``valid``, unexpired by the database's
   clock, and at the account's current epoch. An expired row is marked (``expire_session``).

It never takes an actor, account or session from the request body or from any header but the
access token.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from allauth.headless.contrib.rest_framework.authentication import JWTTokenAuthentication
from allauth.headless.tokens.strategies.jwt import internal
from allauth.usersessions.models import UserSession
from django.db.models import DateTimeField, Func
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from glow_identity import revocation
from glow_persistence.models import AccountSession

logger = logging.getLogger("glow_identity.authentication")

UNAUTHENTICATED = "unauthenticated"


@dataclass(frozen=True)
class Actor:
    """Glow's actor: the account and the session, as read for this request."""

    account_id: UUID
    account_version: int
    account_state: str
    session_id: UUID
    session_state: str


class _ClockTimestamp(Func):  # type: ignore[misc]
    function = "clock_timestamp"
    template = "%(function)s()"
    output_field = DateTimeField()


def _refuse(reason: str) -> AuthenticationFailed:
    logger.info("actor refused: %s", reason)
    return AuthenticationFailed(UNAUTHENTICATED)


def actor_for(user: Any, payload: dict[str, Any]) -> Actor:
    """The actor for a user and a validated access token's payload, or a refusal."""
    sid = payload.get("sid")
    session_key = internal.session_key_from_sid(sid) if isinstance(sid, str) else None
    if not session_key:
        raise _refuse("no_session")
    reference = (
        UserSession.objects.filter(session_key=session_key, user_id=user.pk)
        .values_list("pk", flat=True)
        .first()
    )
    del session_key
    if reference is None:
        raise _refuse("no_user_session")
    session = (
        AccountSession.objects.select_related("account")
        .annotate(checked_at=_ClockTimestamp())
        .filter(auth_session_ref=str(reference))
        .first()
    )
    if session is None:
        raise _refuse("no_account_session")
    account = session.account
    if account.auth_user_id != user.pk:
        raise _refuse("account_mismatch")
    if account.state != "active":
        raise _refuse("account_not_active")
    if session.state != "valid":
        raise _refuse("session_not_valid")
    if session.epoch != account.session_epoch:
        raise _refuse("session_epoch_stale")
    if session.expires_at <= session.checked_at:
        try:
            revocation.expire_found(session.pk)
        except Exception:  # noqa: BLE001 - refused either way; the next find marks it
            logger.warning("expired session not marked: error")
        raise _refuse("session_expired")
    return Actor(
        account_id=account.pk,
        account_version=int(account.version),
        account_state=str(account.state),
        session_id=session.pk,
        session_state=str(session.state),
    )


class GlowActorAuthentication(BaseAuthentication):  # type: ignore[misc]
    def authenticate(self, request: Any) -> tuple[Any, Actor] | None:
        credentials = JWTTokenAuthentication().authenticate(request)
        if credentials is None:
            return None
        user, payload = credentials
        if not isinstance(payload, dict):
            raise _refuse("no_payload")
        return user, actor_for(user, payload)

    def authenticate_header(self, request: Any) -> str:
        # A 401, not a 403, for a missing or refused token (the contract's unauthenticated).
        return str(JWTTokenAuthentication().authenticate_header(request))
