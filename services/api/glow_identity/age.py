"""The age state's port adapter (the SV1 brief's D9): ``AgeAssurancePort`` over
``glow_persistence.AccountAgeState``, the only code that writes the model.

SV1 writes one row per account, at sign-up, in the sign-up's transaction: ``unknown``, with no
method and no policy version. Changing a recorded state is the write of the slice that sets one
(P04's onboarding from the self-entered date; P09.2's store signals): it also bumps the account's
``eligibility_version`` under the account's row lock (the data model), so this adapter refuses to
overwrite a row.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from django.db import connection

from glow_domain.identity import (
    AccountId,
    AgeAssurance,
    AgeAssuranceMethod,
    AgeAssuranceState,
)
from glow_persistence.models import AccountAgeState


class AgeStateRecorded(RuntimeError):
    """The account already has a recorded age state; SV1 never overwrites one."""


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
