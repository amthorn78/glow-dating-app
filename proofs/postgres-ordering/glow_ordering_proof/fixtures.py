"""Fixtures for the cases: accounts through the maintained authentication persistence,
matches with a locally created binding. No provider is called."""

from __future__ import annotations

import uuid
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction
from glow_persistence.models import AppAccount, ChatBinding, Match


class DjangoFixtures:
    """``FixtureFactory`` over the reviewed models."""

    def create_account(self) -> UUID:
        # django.contrib.auth creates the user; no password is set (credentials are the
        # maintained library's, out of P06.DB's scope), and no email address is used.
        with transaction.atomic():
            user = get_user_model().objects.create_user(username=f"proof-{uuid.uuid4().hex}")
            # The account starts active: verification is not part of the proof (D6).
            account = AppAccount.objects.create(auth_user=user, state="active")
        assert isinstance(account.id, UUID)
        return account.id

    def create_match(self, first: UUID, second: UUID) -> UUID:
        low, high = sorted((first, second))
        with transaction.atomic():
            match = Match.objects.create(account_low_id=low, account_high_id=high, state="active")
            ChatBinding.objects.create(
                match=match,
                provider="proof",
                channel_ref=f"proof-channel-{match.id}",
                state="active",
            )
        assert isinstance(match.id, UUID)
        return match.id


def pair_of(match_id: UUID) -> tuple[UUID, UUID]:
    match = Match.objects.filter(pk=match_id).values("account_low_id", "account_high_id").get()
    low, high = match["account_low_id"], match["account_high_id"]
    assert isinstance(low, UUID) and isinstance(high, UUID)
    return low, high
