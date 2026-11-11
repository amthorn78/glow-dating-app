"""Completion's requirements (the SV2 brief's D9; OD-61) and the owner's completion read (D11).

A profile moves from ``incomplete`` to ``visible`` only with every requirement met, read on rows
after the account row lock, which every writer of a requirement takes first:

- ``consent``: the account's latest onboarding consent decision is ``accepted``, at the consent
  policy's current version (filtered by purpose: a ``sensitive_profile`` decision never counts);
- ``adult_check``: the age state is ``self_declared_adult``;
- ``profile_fields``: a display name, a non-empty summary, a gender and at least one "looking for"
  value;
- ``area``: a home area;
- ``photo``: at least one approved photo, approved by the automated check (SV2 Stage B; D10). A
  photo under a staff restriction is back in review, and one its owner removed is
  ``removal_pending``, so neither counts;
- ``chart``: the current birth input revision and its mapping are both ``resolved``, and the
  mapping points at that revision. SV2 has no HDE, so nothing resolves in the sealed runtime; a
  test seeds both in its own setup;
- ``identity_verification``: ``verified`` by the automated check, or ``staff_approved``.

No staff review stands between a complete profile and ``visible`` (OD-61). The sensitive fields
are not required.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from glow_domain import profile_fields as pf
from glow_domain.chat import ONBOARDING_CONSENT_PURPOSE
from glow_persistence.models import (
    AccountAgeState,
    BirthInput,
    ConsentDecision,
    EngineIdentity,
    IdentityVerification,
    MediaAsset,
    ProfileFieldChoice,
)

CONSENT = "consent"
ADULT_CHECK = "adult_check"
PROFILE_FIELDS = "profile_fields"
AREA = "area"
PHOTO = "photo"
CHART = "chart"
IDENTITY_VERIFICATION = "identity_verification"
# The completion read's closed list (D11), in order.
ALL: tuple[str, ...] = (
    CONSENT,
    ADULT_CHECK,
    PROFILE_FIELDS,
    AREA,
    PHOTO,
    CHART,
    IDENTITY_VERIFICATION,
)


def latest_decision(account_id: UUID, purpose: str) -> Any:
    """The account's latest decision for one purpose. Every reader filters by purpose (D6)."""
    return (
        ConsentDecision.objects.filter(account_id=account_id, purpose=purpose)
        .order_by("-version")
        .first()
    )


def onboarding_current(account_id: UUID, current_policy_version: str) -> bool:
    latest = latest_decision(account_id, ONBOARDING_CONSENT_PURPOSE)
    return (
        latest is not None
        and latest.state == "accepted"
        and latest.policy_version == current_policy_version
    )


def current_birth_input(account_id: UUID) -> Any:
    return BirthInput.objects.filter(account_id=account_id).order_by("-version").first()


def chart_resolved(account_id: UUID) -> bool:
    current = current_birth_input(account_id)
    if current is None or current.state != "resolved":
        return False
    mapping = EngineIdentity.objects.filter(account_id=account_id).first()
    return (
        mapping is not None and mapping.state == "resolved" and mapping.birth_input_id == current.id
    )


def _field_values(account_id: UUID, field: str) -> list[str]:
    row = ProfileFieldChoice.objects.filter(account_id=account_id, field=field).first()
    if row is None:
        return []
    return [value for value in row.value_ids if value != pf.NOT_STATED]


def missing(account_id: UUID, profile: Any, onboarding_policy_version: str) -> list[str]:
    """What the profile still needs, in the closed list's order, read on the current rows."""
    found: list[str] = []
    if not onboarding_current(account_id, onboarding_policy_version):
        found.append(CONSENT)
    age = AccountAgeState.objects.filter(account_id=account_id).first()
    if age is None or age.state != "self_declared_adult":
        found.append(ADULT_CHECK)
    fields_ok = (
        profile is not None
        and pf.text_ok(profile.display_name, 80)
        and pf.text_ok(profile.bio, 500)
        and bool(_field_values(account_id, pf.GENDER))
        and bool(_field_values(account_id, pf.LOOKING_FOR))
    )
    if not fields_ok:
        found.append(PROFILE_FIELDS)
    if profile is None or profile.area_id is None:
        found.append(AREA)
    if not MediaAsset.objects.filter(account_id=account_id, state="approved").exists():
        found.append(PHOTO)
    if not chart_resolved(account_id):
        found.append(CHART)
    verification = IdentityVerification.objects.filter(account_id=account_id).first()
    if verification is None or verification.state not in ("verified", "staff_approved"):
        found.append(IDENTITY_VERIFICATION)
    return found
