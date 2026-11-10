"""The age state's port adapter (the SV1 brief's D9): ``AgeAssurancePort`` over
``glow_persistence.AccountAgeState``, the only code that writes the model.

SV1 writes one row per account, at sign-up, in the sign-up's transaction: ``unknown``, with no
method and no policy version. Changing a recorded state is the write of the slice that sets one
(P04's onboarding from the self-entered date; P09.2's store signals): it also bumps the account's
``eligibility_version`` under the account's row lock (the data model), so this adapter refuses to
overwrite a row.

SV2 (its brief's D7; DM-52) adds that write as one transition beside ``record``, which stays as
SV1 built it: ``transition`` runs only inside the caller's transaction, takes the account row
``FOR UPDATE`` first (DM-13 4.1; already held by an SV2 operation, which takes it first), then
the age state's row, and changes ``unknown`` to ``self_declared_adult`` with the date and the
rule's version, a ``self_declared_adult`` state to a new date, or ``self_declared_adult`` back to
``unknown``; it refuses anything else, and bumps the account's ``eligibility_version``. The date
is never logged, and ``age_years`` returns whole years, never the date.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from django.db import connection
from django.db.models import F
from django.db.models.functions import Now

from glow_domain.identity import (
    AccountId,
    AgeAssurance,
    AgeAssuranceMethod,
    AgeAssuranceState,
    AgeTransition,
    whole_years,
)
from glow_persistence.models import AccountAgeState, AppAccount


class AgeStateRecorded(RuntimeError):
    """The account already has a recorded age state; SV1 never overwrites one."""


class AgeTransitionRefused(RuntimeError):
    """D7's transition was refused; the reason is a code, never a value."""


def db_clock() -> datetime:
    with connection.cursor() as cursor:
        cursor.execute("SELECT clock_timestamp()")
        value = cursor.fetchone()[0]
    assert isinstance(value, datetime)
    return value


class OrmAgeAssurance:
    def read(self, account_id: AccountId) -> AgeAssurance | None:
        row = AccountAgeState.objects.filter(account_id=UUID(account_id.value)).first()
        if row is None:
            return None
        return AgeAssurance(
            account_id,
            AgeAssuranceState(row.state),
            AgeAssuranceMethod(row.method),
            row.recorded_at,
            row.policy_version,
        )

    def record(self, assurance: AgeAssurance) -> None:
        account = UUID(assurance.account_id.value)
        if AccountAgeState.objects.filter(account_id=account).exists():
            raise AgeStateRecorded("age_state_recorded")
        AccountAgeState.objects.create(
            account_id=account,
            state=assurance.state.value,
            method=assurance.method.value,
            recorded_at=assurance.recorded_at,
            policy_version=assurance.policy_version,
        )

    def transition(self, change: AgeTransition) -> str:
        """SV2 (D7): the one transition, in the caller's transaction, after the account row lock;
        ``applied`` or ``no_change``, or ``AgeTransitionRefused``."""
        if not connection.in_atomic_block:
            raise AgeTransitionRefused("transaction_required")
        account_id = UUID(change.account_id.value)
        # DM-13 4.1: the account row first, then the age state's row.
        if not AppAccount.objects.select_for_update().filter(pk=account_id).exists():
            raise AgeTransitionRefused("account_missing")
        row = AccountAgeState.objects.select_for_update().filter(account_id=account_id).first()
        if row is None:
            raise AgeTransitionRefused("age_state_missing")
        to_adult = change.state is AgeAssuranceState.SELF_DECLARED_ADULT
        if row.state == AgeAssuranceState.UNKNOWN.value and not to_adult:
            # unknown to unknown is no transition at all (D7: "refuses any other change").
            raise AgeTransitionRefused("no_transition")
        if to_adult and row.state == change.state.value and row.birth_date == change.birth_date:
            return "no_change"
        row.state = change.state.value
        row.method = change.method.value
        row.birth_date = change.birth_date
        row.policy_version = change.policy_version
        row.recorded_at = change.recorded_at
        row.version += 1
        row.save(
            update_fields=[
                "state",
                "method",
                "birth_date",
                "policy_version",
                "recorded_at",
                "version",
                "updated_at",
            ]
        )
        AppAccount.objects.filter(pk=account_id).update(
            eligibility_version=F("eligibility_version") + 1,
            version=F("version") + 1,
            updated_at=Now(),
        )
        return "applied"

    def age_years(self, account_id: AccountId, today: date) -> int | None:
        """SV2 (D4): whole years from the age state's date, or None while it is unknown."""
        born = (
            AccountAgeState.objects.filter(account_id=UUID(account_id.value))
            .values_list("birth_date", flat=True)
            .first()
        )
        if not isinstance(born, date):
            return None
        return whole_years(born, today)
