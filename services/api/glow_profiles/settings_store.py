"""The settings store (the SV2 brief's D2; OD-60; OD-61).

Every setting is one append-only ``SettingVersion`` row per version, with ``PolicyRevision`` as
its current pointer. A member's command reads the settings it depends on under their pointers'
locks (``FOR SHARE``, after the account row lock, in name order), so a publication, which locks
the pointer ``FOR UPDATE``, and the command cannot cross: the command reads the version before
or the version after, never a mix.

A change is made only through ``publish``, a staff operation (no route; P07's console calls it
later) that takes a staff subject and a reason: one transaction that locks the pointer, checks the
content against the setting's closed schema and the fixed limits in code
(``glow_domain.profile_settings``) before anything is written, then writes the next version,
moves the pointer, writes a ``StaffAudit`` row and emits ``policy_published``. A refusal names
the limit it crosses and writes nothing. A change applies from then on: no member's data is
rewritten.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from glow_domain import profile_settings as ps
from glow_domain.chat import TransactionProbe
from glow_persistence.models import PolicyRevision, SettingVersion, StaffAudit
from glow_profiles import events
from glow_profiles.tx import (
    IDEMPOTENCY_CONFLICT,
    INVALID_REQUEST,
    POLICY_UNRESOLVED,
    Refused,
    Result,
    Tx,
    clock,
    run,
    signal,
)


@dataclass(frozen=True)
class Setting:
    name: str
    number: int
    policy_version: str
    content: dict[str, Any]
    version_id: UUID
    pointer_id: UUID


def _setting(name: str, pointer_id: UUID, policy_version: str, artifact_ref: UUID) -> Setting:
    row = SettingVersion.objects.filter(pk=artifact_ref, name=name).first()
    if row is None:
        raise Refused(POLICY_UNRESOLVED, "setting_version_missing")
    if ps.policy_version(name, int(row.number)) != policy_version:
        raise Refused(POLICY_UNRESOLVED, "setting_pointer_mismatch")
    return Setting(name, int(row.number), policy_version, row.content, row.id, pointer_id)


def read_shared(tx: Tx, names: Iterable[str]) -> dict[str, Setting]:
    """The current version of each setting, its pointer locked ``FOR SHARE``, in name order (the
    data model: "Policy pointer is transactionally locked alongside actions"). A setting with no
    pointer is ``policy_unresolved``: no permissive default."""
    found: dict[str, Setting] = {}
    for name in sorted(set(names)):
        tx.cursor.execute(
            "SELECT id, policy_version, artifact_ref FROM glow_persistence_policyrevision"
            " WHERE name = %s FOR SHARE",
            [name],
        )
        row = tx.cursor.fetchone()
        if row is None:
            raise Refused(POLICY_UNRESOLVED, "setting_unresolved")
        found[name] = _setting(name, row[0], str(row[1]), row[2])
    return found


def read_unlocked(name: str) -> Setting:
    """A setting's current version without a lock, for a read that writes nothing."""
    pointer = PolicyRevision.objects.filter(name=name).first()
    if pointer is None:
        raise Refused(POLICY_UNRESOLVED, "setting_unresolved")
    return _setting(name, pointer.id, str(pointer.policy_version), pointer.artifact_ref)


def history(name: str) -> list[dict[str, Any]]:
    """Every version of a setting, oldest first (staff and tests read the audit trail)."""
    return [
        {
            "number": int(row.number),
            "content": row.content,
            "published_at": row.published_at,
            "staff_subject": row.staff_subject,
            "reason": row.reason,
        }
        for row in SettingVersion.objects.filter(name=name).order_by("number")
    ]


def publish(
    name: str,
    content: Any,
    *,
    staff_subject: str,
    reason: str,
    request_id: UUID,
    probe: TransactionProbe | None = None,
) -> Result:
    """Publishes the next version of ``name`` (D2): refused, with nothing written, if the
    content crosses a fixed limit or fails its closed schema."""
    if name not in ps.ALL_SETTINGS:
        return Result("refused", INVALID_REQUEST, "unknown_setting")
    if not ps.staff_subject_ok(staff_subject) or not ps.reason_ok(reason):
        return Result("refused", INVALID_REQUEST, "staff_subject_or_reason")

    def body(tx: Tx) -> Result:
        pointer = PolicyRevision.objects.select_for_update().filter(name=name).first()
        if pointer is None:
            raise Refused(POLICY_UNRESOLVED, "setting_unresolved")
        signal(tx.probe, "after_first_lock")
        current = _setting(name, pointer.id, str(pointer.policy_version), pointer.artifact_ref)
        onboarding: str | None = None
        if name == ps.HISTORY:
            # H's rule reads the onboarding consent's current version under its pointer's lock.
            onboarding = read_shared(tx, [ps.ONBOARDING_CONSENT])[
                ps.ONBOARDING_CONSENT
            ].policy_version
        signal(tx.probe, "after_locks")
        refusals = ps.publication_refusals(
            name, content, current.content, onboarding_consent_version=onboarding
        )
        if refusals:
            # Refused before anything is written; the reason names the limits, never a value.
            raise Refused(INVALID_REQUEST, "refused:" + ",".join(refusals))
        if StaffAudit.objects.filter(request_id=request_id).exists():
            raise Refused(IDEMPOTENCY_CONFLICT, "request_id_used")
        now = clock(tx)
        number = current.number + 1
        row = SettingVersion.objects.create(
            name=name,
            number=number,
            content=content,
            published_at=now,
            staff_subject=staff_subject,
            reason=reason,
        )
        pointer.policy_version = ps.policy_version(name, number)
        pointer.artifact_ref = row.id
        pointer.version += 1
        pointer.save(update_fields=["policy_version", "artifact_ref", "version", "updated_at"])
        StaffAudit.objects.create(
            staff_subject=staff_subject,
            scope="settings",
            action="publish",
            object_type="setting_version",
            object_id=row.id,
            reason_code=reason,
            request_id=request_id,
            before_version=current.number,
            after_version=number,
        )
        events.emit(
            tx,
            events.POLICY_PUBLISHED,
            aggregate_id=pointer.id,
            aggregate_version=number,
            payload_ref=row.id,
            now=now,
        )
        return Result(
            "applied",
            detail={"name": name, "number": number, "policy_version": pointer.policy_version},
        )

    return run(body, probe)
