"""Identity verification, and staff approval without it (SV2's brief, D18; OD-61). Pure domain
types and ports, independent of Django.

Nathan, 10 November 2026: "Approval must be automated based on ID verification" (a government
photo ID, checked by a verification company with a selfie matched to it, for every member before
their profile shows), and "I do need the ability to manually approve people without ID
verification, and to toggle that feature on and off".

- **One account-private record:** ``unverified``, ``verified`` when the automated check passes,
  or ``staff_approved`` when staff approve the member without it. It holds the method, the
  company's opaque reference or the staff subject and reason, and the time; Glow keeps no ID
  image, ID number or selfie. It is written only through ``IdentityVerificationPort``, after the
  account row lock, with the eligibility bump. It is not the contract's ``verify_identity``,
  which means email verification.
- **The automated check** is a seam with no provider (``IdentityCheckPort``): its fixture adapter
  passes no one, and no SV2 code writes ``verified``. P11 wires the company's adapter after
  Nathan's decision, and its verdict arrives through ``record_check_passed`` (the registry's
  ``provider`` role), which the adapter authenticates first.
- **Staff approval without identity verification** stands in for that one requirement only,
  never for the adult check, consent or any other (D2's fixed limit), and only while D2's
  setting allows it. Switching the setting off stops new approvals and leaves past ones; staff
  can revoke one at any time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID


class VerificationState(Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    STAFF_APPROVED = "staff_approved"


class VerificationMethod(Enum):
    NONE = "none"
    AUTOMATED_CHECK = "automated_check"
    STAFF_APPROVAL = "staff_approval"


# Completion's requirement (D9): passed by the automated check, or approved by staff.
SATISFIES_REQUIREMENT: frozenset[VerificationState] = frozenset(
    {VerificationState.VERIFIED, VerificationState.STAFF_APPROVED}
)
# D2's fixed limit: the one requirement a staff approval stands in for.
STAFF_APPROVAL_STANDS_IN_FOR: tuple[str, ...] = ("identity_verification",)


@dataclass(frozen=True)
class VerificationRecord:
    account_id: UUID
    state: VerificationState
    method: VerificationMethod
    decided_at: datetime | None

    @property
    def satisfies_requirement(self) -> bool:
        return self.state in SATISFIES_REQUIREMENT


@dataclass(frozen=True)
class PortOutcome:
    """``applied``, ``no_change`` or ``refused``, with a reason code (never a value)."""

    outcome: str
    reason: str = ""


class IdentityVerificationPort(Protocol):
    """The only way to write an account's identity verification record. Every write runs in
    the caller's transaction, after the account row lock, and bumps ``eligibility_version``."""

    def read(self, account_id: UUID) -> VerificationRecord: ...

    def record_check_passed(self, account_id: UUID, provider_reference: str) -> PortOutcome:
        """The automated check's verdict (``id_check_passed``; role ``provider``), from P11's
        authenticated adapter only. SV2's adapter refuses it: no SV2 code writes ``verified``."""
        ...

    def approve_without_id(self, account_id: UUID, staff_subject: str, reason: str) -> PortOutcome:
        """``approve_without_id``: ``unverified`` to ``staff_approved`` (role ``moderator``)."""
        ...

    def revoke_approval(self, account_id: UUID, staff_subject: str, reason: str) -> PortOutcome:
        """``revoke_approval``: ``staff_approved`` to ``unverified`` (role ``moderator``)."""
        ...


@dataclass(frozen=True)
class CheckOutcome:
    """What the automated check answered: ``unavailable`` while no provider is wired."""

    status: str


class IdentityCheckPort(Protocol):
    """The seam for the verification company (D18): it receives the member's request to be
    checked and answers, later, through ``IdentityVerificationPort.record_check_passed``."""

    def request_check(self, account_id: UUID) -> CheckOutcome: ...


class FixtureIdentityCheck:
    """The seam's only adapter in SV2: there is no provider, so it passes no one and never
    writes ``verified`` (D18). A test may seed ``verified`` in its own setup instead."""

    def request_check(self, account_id: UUID) -> CheckOutcome:
        return CheckOutcome("unavailable")
