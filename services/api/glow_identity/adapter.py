"""Glow's account adapter (``ACCOUNT_ADAPTER``; the SV1 brief's D3, D4, D6 and D8).

Each override binds one of allauth's flows to Glow's account or session rows, or words a
message, and changes nothing else in the flow:

- ``save_user``: the auth user, its ``AppAccount`` (``unverified``) and its ``unknown`` age state
  in one transaction (D4). allauth opens no transaction around headless sign-up, so the steps it
  takes after ``save_user`` (the address row among them) are outside it; a failure there leaves
  an ``unverified`` account that cannot sign in.
- ``populate_username``: a random opaque username, so nothing of the email is copied into a
  column email sign-in never uses (D4).
- ``send_mail`` and ``send_account_already_exists_mail``: Glow's wording, with no link (D3, D8).
- ``confirm_email``: after allauth marks an address verified, F01's ``verified`` transition (D6).
- ``post_login``: the sign-in hook. allauth's own ``post_login`` sends ``user_logged_in``, whose
  ``usersessions`` receiver creates the sign-in's ``UserSession``; then ``open_session`` records
  the ``AccountSession`` and the Django session's expiry is aligned with it. If it does not
  apply, the allauth session ends in the same request and the response carries no token (D6).
- ``logout``: ``sign_out`` for this session, then allauth's logout (D6).
- ``set_password`` (a password change or reset): ``sign_out`` for every valid session of the
  account, then the new password, whose hash ends every allauth session of the user (D6).
- ``get_phone``: Glow records no phone number; the phone route allauth serves regardless is
  refused (403) instead of failing with a server error.
"""

from __future__ import annotations

import logging
import secrets
from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_username
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.headless.base.response import AuthenticationResponse, ForbiddenResponse
from django.core.mail import EmailMessage
from django.db import transaction

from glow_domain.identity import AccountId, unknown_age_assurance
from glow_identity import age, messages, revocation
from glow_persistence.models import AppAccount

logger = logging.getLogger("glow_identity.adapter")

# An opaque username: random, never derived from the email, and valid for auth.User's
# username validator (letters, digits and @.+-_).
_USERNAME_PREFIX = "g"


def opaque_username() -> str:
    return _USERNAME_PREFIX + secrets.token_hex(16)


class GlowAccountAdapter(DefaultAccountAdapter):  # type: ignore[misc]
    # -- sign-up (D4) ------------------------------------------------------------------------

    def populate_username(self, request: Any, user: Any) -> None:
        if not user_username(user):
            user_username(user, opaque_username())

    def save_user(self, request: Any, user: Any, form: Any, commit: bool = True) -> Any:
        if not commit:
            raise ValueError("Glow saves a new user together with its account and age state")
        with transaction.atomic():
            saved = super().save_user(request, user, form, commit=True)
            account = AppAccount.objects.create(auth_user=saved, state="unverified")
            age.OrmAgeAssurance().record(
                unknown_age_assurance(AccountId(str(account.pk)), age.db_clock())
            )
        return saved

    # -- messages (D3, D8) -------------------------------------------------------------------

    def send_mail(self, template_prefix: str, email: str, context: dict[str, Any]) -> None:
        message = messages.render(template_prefix, context)
        EmailMessage(message.subject, message.body, self.get_from_email(), [email]).send()

    def send_account_already_exists_mail(self, email: str) -> None:
        # allauth's own builds the sign-up and reset links, which raise in headless-only mode.
        self.send_mail("account/email/account_already_exists", email, {})

    # -- verification (D6) -------------------------------------------------------------------

    def confirm_email(self, request: Any, email_address: Any) -> bool:
        confirmed = bool(super().confirm_email(request, email_address))
        if confirmed:
            outcome = revocation.verify_account_of(email_address.user)
            # If it did not apply, the next sign-in takes it again (open_sign_in_session).
            logger.info("verified transition after verification: %s", outcome.outcome)
        return confirmed

    # -- sign-in (D4, D6) --------------------------------------------------------------------

    def post_login(self, request: Any, user: Any, **kwargs: Any) -> Any:
        response = super().post_login(request, user, **kwargs)
        try:
            opened = revocation.open_sign_in_session(request, user)
        except Exception:  # noqa: BLE001 - fail closed; the line names no value
            logger.warning("sign-in session not opened: error")
            opened = False
        if opened:
            return response
        revocation.end_failed_sign_in(request)
        # A response built now, after the session ended: unauthenticated, and no token.
        return AuthenticationResponse(request)

    # -- logout, password change and reset (D6) ----------------------------------------

    def logout(self, request: Any) -> None:
        revocation.sign_out_current_session(request)
        super().logout(request)

    def set_password(self, user: Any, password: str) -> None:
        revocation.sign_out_account(user)
        super().set_password(user, password)

    # -- phone numbers (not a Glow feature) ----------------------------------------------

    def get_phone(self, user: Any) -> Any:
        """Glow records no phone number. allauth 65.21.1 serves ``account/phone`` whatever the
        configuration, and its default adapter raises ``NotImplementedError`` there for a
        signed-in member, a server error. Glow refuses the request (403) and nothing changes.
        Phone is neither a login method nor a sign-up field, so no other path reads it, and
        allauth still sees no phone implementation (``_has_phone_impl``)."""
        raise ImmediateHttpResponse(ForbiddenResponse(self.request))
