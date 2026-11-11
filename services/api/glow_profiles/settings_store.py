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

**One pointer order** (the brief's D19; DM-56 V5; DM-57 U8). Every transaction locks settings
pointers in name order: it never locks a pointer whose name sorts before one it already holds,
unless it already holds that pointer. This module is the only code that locks a ``PolicyRevision``
row (``read_shared``'s ``FOR SHARE`` and ``publish``'s ``FOR UPDATE``), and it records each
transaction's held pointers on its ``Tx``, the publication's own included, before any further
read. A lock out of order raises ``PointerOrderError``: a programming error, never a member's
refusal, so ``tx.run`` rolls the transaction back and answers it as any unexpected exception
(``provider_unavailable``, retryable, with the error's type as the internal reason). Members take
their account row first and then pointers in this order; publications take pointers only, in
this order, and never an account row; so no wait cycle can form whatever PostgreSQL's queueing
does. SV2's member and staff transactions meet the rule by taking all their pointers in their
first ``read_shared`` call; a pointer read again later in the same transaction, as the recompute
rereads ``consent.onboarding``, is already held and waits for nothing.

A setting's earlier version is read by its label with ``version_content`` (no lock: versions are
append-only), as the media completion checks the byte limit of the version its grant records.
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


class PointerOrderError(RuntimeError):
    """D19: a settings pointer locked out of name order. A programming error, never a refusal:
    it is not ``Refused``, so ``tx.run`` rolls the transaction back and answers it as an internal
    error (``provider_unavailable``), never as a member's refusal. Its message is a code."""

    def __init__(self) -> None:
        super().__init__("pointer_out_of_order")


def _hold(tx: Tx, name: str) -> None:
    """Records ``name`` as held by ``tx`` before its lock is taken, and refuses (D19) a pointer
    that sorts before one the transaction already holds unless it already holds that one."""
    if name in tx.pointers:
        return
    if any(held > name for held in tx.pointers):
        raise PointerOrderError()
    tx.pointers.append(name)


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
    pointer is ``policy_unresolved``: no permissive default. Each lock is checked against the
    transaction's held pointers first (D19)."""
    found: dict[str, Setting] = {}
    for name in sorted(set(names)):
        _hold(tx, name)
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


def version_content(name: str, policy_version: str) -> dict[str, Any]:
    """The content of one recorded version of ``name``, by its label, with no lock: setting
    versions are append-only, so a version once written never changes (D10: a media completion is
    checked against the version its grant records, not the current one)."""
    for row in SettingVersion.objects.filter(name=name).order_by("number"):
        if ps.policy_version(name, int(row.number)) == policy_version:
            content: dict[str, Any] = row.content
            return content
    raise Refused(POLICY_UNRESOLVED, "setting_version_missing")


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
        # D19 (DM-57 U8): the publication's own pointer is recorded as held before its lock and
        # before any pointer it reads (``chat.history``'s ``consent.onboarding``, which sorts
        # after it).
        _hold(tx, name)
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
