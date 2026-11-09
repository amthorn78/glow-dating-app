"""SV1's revocation service (the SV1 brief's D6): one lock protocol, two layers.

**Glow's layer** is ``glow_chat``'s reviewed operations (``open_session``, ``sign_out``,
``expire_session``, ``suspend`` and ``delete``), each its own transaction under P06.DB's lock
protocol, writing its outbox events; and F01's ``verified`` transition, which ``glow_chat`` does
not have and this module adds under the same rules (``mark_verified``). **allauth's layer** is
its sessions: the ``UserSession`` row of each sign-in and the Django session it names.

Glow's step commits first; then allauth's session or sessions end, so allauth's own endpoints,
which never consult ``AccountSession``, refuse them too. Between the two commits the actor class
already refuses the ``AccountSession``. Both steps are idempotent: a request whose second step
fails answers with an error, and a repeat completes it, because a repeat of the first step is
"no change" and the second step runs again.

No call runs inside an open transaction (``require_no_transaction``): each ``glow_chat``
operation is the whole of its transaction, as P06.DB proved it. Nothing here logs a session
key, token, code or password; a log line names an outcome only.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from importlib import import_module
from typing import Any
from uuid import UUID

from allauth.account.models import EmailAddress
from allauth.usersessions.models import UserSession
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as django_logout
from django.db import connection, transaction

from glow_chat.contact import OrmContactPersistence
from glow_domain.chat import ContactResult
from glow_persistence.models import AccountSession, AppAccount

logger = logging.getLogger("glow_identity.revocation")


class TransactionOpen(RuntimeError):
    """A revocation was asked for inside an open transaction; nothing ran."""


class RevocationError(RuntimeError):
    """A step did not apply. The request answers with an error; a repeat completes it."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class Outcome:
    outcome: str  # "applied", "no_change" or "refused"
    reason: str | None = None


def require_no_transaction() -> None:
    """D6: SV1 never calls a ``glow_chat`` operation inside an open transaction, where it would
    become a savepoint whose locks and events commit only with the caller's transaction."""
    if connection.in_atomic_block or not connection.get_autocommit():
        raise TransactionOpen("transaction_open")


def contact() -> OrmContactPersistence:
    return OrmContactPersistence(provider=settings.GLOW_IDENTITY_CHAT_PROVIDER)


def session_lifetime() -> timedelta:
    lifetime = settings.GLOW_IDENTITY_SESSION_LIFETIME
    if not isinstance(lifetime, timedelta) or lifetime <= timedelta(0):
        raise RevocationError("session_lifetime_invalid")
    return lifetime


def _checked(result: ContactResult) -> ContactResult:
    if result.outcome in ("applied", "no_change"):
        return result
    raise RevocationError(f"{result.outcome}:{result.reason}")


# -- F01's verified transition (unverified to active, role auth) -------------------------


def mark_verified(account_id: UUID) -> Outcome:
    """D6 (DM-45 6.1): its own transaction; the account row locked ``FOR UPDATE`` before
    anything else; a refusal unless the state is ``unverified`` (an ``active`` account is no
    change); ``version`` and ``eligibility_version`` bumped. It runs after allauth marks the
    address verified, and again at the next sign-in if it did not commit."""
    require_no_transaction()
    with transaction.atomic():
        account = AppAccount.objects.select_for_update().filter(pk=account_id).first()
        if account is None:
            return Outcome("refused", "account_missing")
        if account.state == "active":
            return Outcome("no_change", "already_active")
        if account.state != "unverified":
            return Outcome("refused", "account_not_unverified")
        account.state = "active"
        account.version += 1
        account.eligibility_version += 1
        account.save(update_fields=["state", "version", "eligibility_version", "updated_at"])
    return Outcome("applied")


def _account_of(user_id: Any) -> UUID | None:
    value = AppAccount.objects.filter(auth_user_id=user_id).values_list("pk", flat=True).first()
    return value if isinstance(value, UUID) else None


def verify_account_of(user: Any) -> Outcome:
    """The verified transition for the account of a user whose address allauth has just
    marked verified."""
    account_id = _account_of(user.pk)
    if account_id is None:
        return Outcome("refused", "account_missing")
    return mark_verified(account_id)


# -- sign-in (D4, D5, D6) -----------------------------------------------------------------


def open_sign_in_session(request: Any, user: Any) -> bool:
    """D6: ``open_session`` for a sign-in, after allauth has created its ``UserSession``.

    The account first takes the ``verified`` transition if its address is verified and it
    did not commit before. Then ``open_session`` locks the account, refuses one that is not
    ``active``, and records the session at the current epoch, with ``UserSession``'s primary
    key as its reference (D5) and the configured lifetime. The Django session's expiry is set
    to the ``AccountSession``'s ``expires_at``, so allauth's own endpoints stop at the same
    instant (D2). False means the sign-in must fail closed."""
    require_no_transaction()
    account_id = _account_of(user.pk)
    if account_id is None:
        return False
    state = AppAccount.objects.filter(pk=account_id).values_list("state", flat=True).first()
    if (
        state == "unverified"
        and EmailAddress.objects.filter(user_id=user.pk, verified=True).exists()
    ):
        retried = mark_verified(account_id)
        logger.info("verified transition at sign-in: %s", retried.outcome)
    session_key = request.session.session_key
    if not session_key:
        return False
    reference = (
        UserSession.objects.filter(session_key=session_key, user_id=user.pk)
        .values_list("pk", flat=True)
        .first()
    )
    if reference is None:
        return False
    result = contact().open_session(
        account_id, auth_session_ref=str(reference), lifetime=session_lifetime()
    )
    if result.outcome != "applied" or result.session_id is None:
        logger.info("sign-in refused by open_session: %s", result.reason)
        return False
    expires_at = AccountSession.objects.values_list("expires_at", flat=True).get(
        pk=result.session_id
    )
    request.session.set_expiry(expires_at)
    return True


def end_failed_sign_in(request: Any) -> None:
    """D6: the sign-in fails closed. allauth's session of this sign-in ends in the same
    request: its ``UserSession`` row is deleted and the Django session is flushed, so no token
    from this sign-in names a session that exists."""
    session_key = request.session.session_key
    if session_key:
        UserSession.objects.filter(session_key=session_key).delete()
    django_logout(request)


# -- ending sessions (D6) ------------------------------------------------------------------


def _sign_out_reference(reference: str) -> None:
    """Glow's layer for one allauth session: ``sign_out`` for the ``AccountSession`` whose
    reference it is, if there is one and it is still valid."""
    for session_id in AccountSession.objects.filter(
        auth_session_ref=reference, state="valid"
    ).values_list("pk", flat=True):
        _checked(contact().sign_out(session_id))


def sign_out_current_session(request: Any) -> None:
    """Logout's first step: ``sign_out`` for this request's session."""
    require_no_transaction()
    session_key = getattr(request.session, "session_key", None)
    if not session_key:
        return
    reference = (
        UserSession.objects.filter(session_key=session_key).values_list("pk", flat=True).first()
    )
    if reference is not None:
        _sign_out_reference(str(reference))


def sign_out_account(user: Any) -> None:
    """A password change or reset: ``sign_out`` for every valid session of the account. The
    password's new hash then ends every allauth session of the user."""
    require_no_transaction()
    account_id = _account_of(user.pk)
    if account_id is None:
        return
    for session_id in AccountSession.objects.filter(
        account_id=account_id, state="valid"
    ).values_list("pk", flat=True):
        _checked(contact().sign_out(session_id))


def end_user_session(user_session: Any) -> None:
    """One session chosen from allauth's session list (DM-46 N1): ``sign_out`` for its
    ``AccountSession``, if there is one, then the row's own ``end()``."""
    require_no_transaction()
    _sign_out_reference(str(user_session.pk))
    user_session.end()


def end_replayed_session(session_key: str) -> None:
    """D2: a replayed refresh token ends its session at both layers."""
    require_no_transaction()
    user_session = UserSession.objects.filter(session_key=session_key).first()
    if user_session is None:
        engine = import_module(settings.SESSION_ENGINE)
        engine.SessionStore().delete(session_key)
        return
    _sign_out_reference(str(user_session.pk))
    user_session.end()


def expire_found(session_id: UUID) -> None:
    """D6: ``expire_session`` marks an expired ``AccountSession`` when it is found."""
    require_no_transaction()
    _checked(contact().expire_session(session_id))


# -- suspension and deletion (D6; P07 and P08 own the requests) ------------------------


def suspend_account(account_id: UUID) -> Outcome:
    return _revoke_account(account_id, "suspend")


def delete_account(account_id: UUID) -> Outcome:
    return _revoke_account(account_id, "delete")


def _revoke_account(account_id: UUID, operation: str) -> Outcome:
    """``suspend`` or ``delete`` (the epoch bumped; ``access_revoked`` and
    ``session_epoch_bumped`` written; for deletion, the job and the tombstone), then every
    allauth session of the user ends and the auth user is made inactive, so allauth refuses a
    new sign-in. A repeat after a failed second step is "no change" at Glow's layer and runs
    the second step again."""
    require_no_transaction()
    persistence = contact()
    if operation == "suspend":
        result = persistence.suspend(account_id)
    else:
        result = persistence.delete(account_id)
    if result.outcome == "refused":
        return Outcome("refused", result.reason)
    _checked(result)
    user_id = AppAccount.objects.values_list("auth_user_id", flat=True).get(pk=account_id)
    for user_session in UserSession.objects.filter(user_id=user_id):
        user_session.end()
    get_user_model().objects.filter(pk=user_id).update(is_active=False)
    return Outcome(result.outcome, result.reason)
