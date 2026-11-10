"""The outbox events SV2's writers emit (schema ``glow-profiles-1``; the SV2 brief's D2 and D9).

Each carries only an aggregate reference, its version and a payload reference: never a value
(no field value, own words, set, date, time, coordinate or text). They are logical events for
SV3's invalidation and make no provider call; ``glow_chat``'s delivery reads only its own schema.
``glow_chat``'s own writers, which SV2 nests, emit their events as before (``profile_paused``,
``profile_resumed``, ``profile_restricted``, ``consent_accepted``, ``consent_withdrawn``).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from glow_persistence.models import OutboxEvent
from glow_profiles.tx import Tx

SCHEMA_VERSION = "glow-profiles-1"

POLICY_PUBLISHED = "policy_published"
PROFILE_EDITED = "profile_edited"
PROFILE_COMPLETED = "profile_completed"
# The demotion that follows another write (the registry's F04 requirement_removed, system).
PROFILE_DEMOTED = "profile_demoted"
PROFILE_FIELD_CHANGED = "profile_field_changed"
PREFERENCES_CHANGED = "preferences_changed"
AREA_CHANGED = "area_changed"
SENSITIVE_CONSENT_ACCEPTED = "sensitive_consent_accepted"
SENSITIVE_CONSENT_WITHDRAWN = "sensitive_consent_withdrawn"
AGE_STATE_CHANGED = "age_state_changed"
BIRTH_INPUT_SUBMITTED = "birth_input_submitted"
# A new eligibility date stopped the current birth input being current (F03 date_changed).
BIRTH_INPUT_INVALIDATED = "birth_input_invalidated"
IDENTITY_VERIFICATION_CHANGED = "identity_verification_changed"

ALL: tuple[str, ...] = (
    POLICY_PUBLISHED,
    PROFILE_EDITED,
    PROFILE_COMPLETED,
    PROFILE_DEMOTED,
    PROFILE_FIELD_CHANGED,
    PREFERENCES_CHANGED,
    AREA_CHANGED,
    SENSITIVE_CONSENT_ACCEPTED,
    SENSITIVE_CONSENT_WITHDRAWN,
    AGE_STATE_CHANGED,
    BIRTH_INPUT_SUBMITTED,
    BIRTH_INPUT_INVALIDATED,
    IDENTITY_VERIFICATION_CHANGED,
)


def emit(
    tx: Tx,
    event_type: str,
    *,
    aggregate_id: UUID,
    aggregate_version: int,
    payload_ref: UUID,
    now: datetime,
) -> None:
    if event_type not in ALL:
        raise ValueError("not an SV2 event type")
    event = OutboxEvent.objects.create(
        aggregate_id=aggregate_id,
        aggregate_version=aggregate_version,
        event_type=event_type,
        schema_version=SCHEMA_VERSION,
        dedup_key=f"{event_type}:{aggregate_id}:{aggregate_version}",
        payload_ref=payload_ref,
        state="pending",
        available_at=now,
    )
    tx.events.append(event.id)
