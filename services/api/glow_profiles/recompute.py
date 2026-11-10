"""D9's one shared recompute (the SV2 brief's D9; DM-54, Y3 to Y5): what moves a profile to
``visible``, and what moves it back.

Every writer of a completion requirement ends, in its own transaction and on rows read after the
account row lock, with ``recompute``:

- an ``incomplete`` profile with nothing missing becomes ``visible``;
- a ``visible`` profile with anything missing becomes ``incomplete``;
- ``paused``, ``restricted`` and ``removed`` stay as they are (a paused profile is rechecked by
  resume; restriction and removal are not the member's to undo).

The writers (D9's list for Stage A): the profile edit, the four fields, the area, the onboarding
consent's accept and withdraw, the adult check and the birth input; and staff's approval without
ID verification and its revocation. So a profile shows as soon as its last requirement is met,
whoever meets it, and a requirement that lapsed without a write (a new onboarding consent version)
demotes at the member's next requirement write. Nothing else in SV2 moves a profile to or from
``incomplete``; ``glow_chat``'s pause, resume and restriction are the other writers of the state.

**The registry entry** (``flows-v1.json``, F04) each change is:

- a completion in an F04 owner command (the profile edit, the fields, the area): ``complete``
  (``owner``); one that follows a write in another flow (the consent, the adult check, the birth
  input, staff's approval): ``requirements_met`` (``system``);
- a demotion in the profile edit: the owner's ``edit`` from ``visible`` to ``incomplete`` (the
  cleared summary, the contract's "Compound actions"), carried by the edit's own
  ``profile_edited``; any other: ``requirement_removed`` (``system``), with ``profile_demoted``.

Every completion emits ``profile_completed``. A change bumps the profile's version and the
account's ``eligibility_version`` (the profile edit's own write already bumps both, and the change
rides on it). Events carry references, never values.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import connection
from django.db.models import F
from django.db.models.functions import Now

from glow_domain import profile_settings as ps
from glow_persistence.models import AppAccount, Profile
from glow_profiles import events, requirements, settings_store
from glow_profiles.tx import Tx

# The writer that ends with the recompute, which decides the registry entry of a change.
PROFILE_EDIT = "profile_edit"
F04_OWNER = "f04_owner"
OTHER_FLOW = "other_flow"
WRITERS = (PROFILE_EDIT, F04_OWNER, OTHER_FLOW)

# F04's registry entries a change is one of.
COMPLETE = "complete"
REQUIREMENTS_MET = "requirements_met"
EDIT = "edit"
REQUIREMENT_REMOVED = "requirement_removed"

INCOMPLETE = "incomplete"
VISIBLE = "visible"


def next_state(state: str, missing: list[str] | tuple[str, ...]) -> str:
    """The recompute's rule on one profile's state and its missing requirements. Only
    ``incomplete`` and ``visible`` move; every other state stays as it is."""
    if state == INCOMPLETE and not missing:
        return VISIBLE
    if state == VISIBLE and missing:
        return INCOMPLETE
    return state


def entry(writer: str, before: str, after: str) -> str | None:
    """The F04 registry entry of a change from ``before`` to ``after`` made by ``writer``."""
    if writer not in WRITERS:
        raise ValueError("not a requirement writer")
    if before == after:
        return None
    if (before, after) == (INCOMPLETE, VISIBLE):
        return REQUIREMENTS_MET if writer == OTHER_FLOW else COMPLETE
    if (before, after) == (VISIBLE, INCOMPLETE):
        return EDIT if writer == PROFILE_EDIT else REQUIREMENT_REMOVED
    raise ValueError("not a recompute change")


@dataclass(frozen=True)
class Recomputed:
    """The profile as the recompute left it (``None`` when the account has none), its state
    before and after, the registry entry of the change (``None`` when unchanged) and what is
    still missing."""

    profile: Any
    before: str | None
    after: str | None
    entry: str | None
    missing: tuple[str, ...]


def recompute(tx: Tx, account_id: UUID, now: datetime, *, writer: str) -> Recomputed:
    """D9's recompute, the last state change of a requirement writer's transaction. The caller
    has taken the account row lock first (DM-13 4.1); this reads the onboarding consent policy's
    pointer ``FOR SHARE`` and the profile ``FOR UPDATE``, then every requirement on the current
    rows."""
    if writer not in WRITERS:
        raise ValueError("not a requirement writer")
    if not connection.in_atomic_block:
        raise RuntimeError("transaction_required")
    onboarding = settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])[ps.ONBOARDING_CONSENT]
    profile = Profile.objects.select_for_update().filter(account_id=account_id).first()
    missing = tuple(requirements.missing(account_id, profile, onboarding.policy_version))
    if profile is None:
        return Recomputed(None, None, None, None, missing)
    before = str(profile.state)
    after = next_state(before, missing)
    change = entry(writer, before, after)
    if change is None:
        return Recomputed(profile, before, after, None, missing)
    profile.state = after
    if writer != PROFILE_EDIT:
        profile.version += 1
    profile.save(update_fields=["state", "version", "updated_at"])
    if writer != PROFILE_EDIT:
        AppAccount.objects.filter(pk=account_id).update(
            eligibility_version=F("eligibility_version") + 1,
            version=F("version") + 1,
            updated_at=Now(),
        )
    event = (
        events.PROFILE_COMPLETED
        if after == VISIBLE
        else events.PROFILE_DEMOTED
        if change == REQUIREMENT_REMOVED
        else None
    )
    if event is not None:
        events.emit(
            tx,
            event,
            aggregate_id=profile.id,
            aggregate_version=int(profile.version),
            payload_ref=profile.id,
            now=now,
        )
    return Recomputed(profile, before, after, change, missing)
