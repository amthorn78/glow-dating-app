"""The identity verification port's adapter over ``glow_persistence.IdentityVerification`` (the SV2
brief's D18; OD-61): the only code that writes the model.

Every write runs in the caller's transaction (an SV2 staff operation), after the account row
lock, and bumps ``eligibility_version``:

- ``approve_without_id``: ``unverified`` to ``staff_approved``, with the staff subject and reason;
  the staff operation has already checked D2's setting under its pointer's lock;
- ``revoke_approval``: ``staff_approved`` to ``unverified``;
- ``record_check_passed`` is refused: SV2 has no verification company, and no SV2 code writes
  ``verified`` (P11's authenticated provider adapter does, after Nathan's decision).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import connection
from django.db.models import F
from django.db.models.functions import Now

from glow_domain.identity_verification import (
    PortOutcome,
    VerificationMethod,
    VerificationRecord,
    VerificationState,
)
from glow_persistence.models import AppAccount, IdentityVerification


class OrmIdentityVerification:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def read(self, account_id: UUID) -> VerificationRecord:
        row = IdentityVerification.objects.filter(account_id=account_id).first()
        if row is None:
            return VerificationRecord(
                account_id, VerificationState.UNVERIFIED, VerificationMethod.NONE, None
            )
        return VerificationRecord(
            account_id,
            VerificationState(row.state),
            VerificationMethod(row.method),
            row.decided_at,
        )

    @staticmethod
    def _locked(account_id: UUID) -> Any:
        if not connection.in_atomic_block:
            raise RuntimeError("transaction_required")
        # DM-13 4.1: the account row first (already held by the staff operation).
        AppAccount.objects.select_for_update().filter(pk=account_id).exists()
        return (
            IdentityVerification.objects.select_for_update().filter(account_id=account_id).first()
        )

    @staticmethod
    def _bump(account_id: UUID) -> None:
        AppAccount.objects.filter(pk=account_id).update(
            eligibility_version=F("eligibility_version") + 1,
            version=F("version") + 1,
            updated_at=Now(),
        )

    def record_check_passed(self, account_id: UUID, provider_reference: str) -> PortOutcome:
        # No verification company in SV2 (D18): nothing writes ``verified``.
        return PortOutcome("refused", "no_provider")

    def approve_without_id(self, account_id: UUID, staff_subject: str, reason: str) -> PortOutcome:
        row = self._locked(account_id)
        if row is not None and row.state == VerificationState.STAFF_APPROVED.value:
            return PortOutcome("no_change", "already_staff_approved")
        if row is not None and row.state != VerificationState.UNVERIFIED.value:
            return PortOutcome("refused", "not_unverified")
        if row is None:
            row = IdentityVerification(account_id=account_id)
        else:
            row.version += 1
        row.state = VerificationState.STAFF_APPROVED.value
        row.method = VerificationMethod.STAFF_APPROVAL.value
        row.provider_reference = None
        row.staff_subject = staff_subject
        row.reason = reason
        row.decided_at = self.now
        row.save()
        self._bump(account_id)
        return PortOutcome("applied")

    def revoke_approval(self, account_id: UUID, staff_subject: str, reason: str) -> PortOutcome:
        row = self._locked(account_id)
        if row is None or row.state != VerificationState.STAFF_APPROVED.value:
            return PortOutcome("refused", "not_staff_approved")
        row.state = VerificationState.UNVERIFIED.value
        row.method = VerificationMethod.NONE.value
        row.provider_reference = None
        row.staff_subject = None
        row.reason = None
        row.decided_at = self.now
        row.version += 1
        row.save()
        self._bump(account_id)
        return PortOutcome("applied")

    def row(self, account_id: UUID) -> Any:
        return IdentityVerification.objects.filter(account_id=account_id).first()
