"""The staff operations SV2 builds (the SV2 brief's D1, D2, D9 and D18): domain operations, never
routes. P07 builds the staff-scoped admin API and the WordPress console that calls them; until
P07's staff authentication, a staff subject comes only from its caller in code, and no member
route reaches any of these. Each takes a staff subject (``staff:<id>``, or ``system:<id>`` for the
seed) and a reason, and writes ``StaffAudit`` with the caller's request ID.

- ``publish_setting``: D2's publication (``settings_store.publish``).
- ``approve_without_id``: D18's staff approval without identity verification, only while D2's
  setting allows it, read under its pointer's lock after the account row lock, so a switch-off
  and an approval cannot cross. It stands in for identity verification only.
- ``revoke_approval``: back to ``unverified``, at any time (the setting is not read); a ``visible``
  profile then becomes ``incomplete`` (D9's rule for a removed requirement).
- ``restrict_profile``: D9's restriction through ``glow_chat``'s ``restrict_profile``, nested.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from glow_domain import profile_settings as ps
from glow_domain.chat import TransactionProbe
from glow_persistence.models import Profile, StaffAudit
from glow_profiles import events, settings_store
from glow_profiles.identity_verification import OrmIdentityVerification
from glow_profiles.operations import _chat_checked, _demote_if_visible, chat
from glow_profiles.tx import (
    FORBIDDEN,
    IDEMPOTENCY_CONFLICT,
    INVALID_REQUEST,
    STATE_CONFLICT,
    Refused,
    Result,
    Tx,
    clock,
    lock_account,
    run,
    signal,
)


def publish_setting(
    name: str,
    content: Any,
    *,
    staff_subject: str,
    reason: str,
    request_id: UUID,
    probe: TransactionProbe | None = None,
) -> Result:
    return settings_store.publish(
        name,
        content,
        staff_subject=staff_subject,
        reason=reason,
        request_id=request_id,
        probe=probe,
    )


def _audited(
    tx: Tx,
    *,
    staff_subject: str,
    scope: str,
    action: str,
    object_type: str,
    object_id: UUID,
    reason: str,
    request_id: UUID,
    before: int | None,
    after: int | None,
) -> None:
    if StaffAudit.objects.filter(request_id=request_id).exists():
        raise Refused(IDEMPOTENCY_CONFLICT, "request_id_used")
    StaffAudit.objects.create(
        staff_subject=staff_subject,
        scope=scope,
        action=action,
        object_type=object_type,
        object_id=object_id,
        reason_code=reason,
        request_id=request_id,
        before_version=before,
        after_version=after,
    )


def _check_staff(staff_subject: str, reason: str) -> Result | None:
    if not ps.staff_subject_ok(staff_subject) or not staff_subject.startswith("staff:"):
        return Result("refused", INVALID_REQUEST, "staff_subject")
    if not ps.reason_ok(reason):
        return Result("refused", INVALID_REQUEST, "reason")
    return None


def approve_without_id(
    account_id: UUID,
    *,
    staff_subject: str,
    reason: str,
    request_id: UUID,
    probe: TransactionProbe | None = None,
) -> Result:
    refused = _check_staff(staff_subject, reason)
    if refused is not None:
        return refused

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        setting = settings_store.read_shared(tx, [ps.STAFF_APPROVAL])[ps.STAFF_APPROVAL]
        signal(tx.probe, "after_locks")
        if setting.content["enabled"] is not True:
            # D18: available only while D2's setting allows it (off at launch); nothing written.
            raise Refused(FORBIDDEN, "staff_approval_off")
        if setting.content["stands_in_for"] != ["identity_verification"]:
            raise Refused(FORBIDDEN, "staff_approval_scope")
        now = clock(tx)
        port = OrmIdentityVerification(now)
        before = port.row(account_id)
        outcome = port.approve_without_id(account_id, staff_subject, reason)
        if outcome.outcome == "refused":
            raise Refused(STATE_CONFLICT, outcome.reason)
        row = port.row(account_id)
        if outcome.outcome == "applied":
            _audited(
                tx,
                staff_subject=staff_subject,
                scope="identity",
                action="approve_without_id",
                object_type="identity_verification",
                object_id=row.id,
                reason=reason,
                request_id=request_id,
                before=None if before is None else int(before.version),
                after=int(row.version),
            )
            events.emit(
                tx,
                events.IDENTITY_VERIFICATION_CHANGED,
                aggregate_id=row.id,
                aggregate_version=int(row.version),
                payload_ref=row.id,
                now=now,
            )
        return Result(outcome.outcome, detail={"state": row.state})

    return run(body, probe)


def revoke_approval(
    account_id: UUID,
    *,
    staff_subject: str,
    reason: str,
    request_id: UUID,
    probe: TransactionProbe | None = None,
) -> Result:
    refused = _check_staff(staff_subject, reason)
    if refused is not None:
        return refused

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        profile = Profile.objects.select_for_update().filter(account_id=account_id).first()
        signal(tx.probe, "after_locks")
        now = clock(tx)
        port = OrmIdentityVerification(now)
        before = port.row(account_id)
        outcome = port.revoke_approval(account_id, staff_subject, reason)
        if outcome.outcome == "refused":
            raise Refused(STATE_CONFLICT, outcome.reason)
        row = port.row(account_id)
        _audited(
            tx,
            staff_subject=staff_subject,
            scope="identity",
            action="revoke_approval",
            object_type="identity_verification",
            object_id=row.id,
            reason=reason,
            request_id=request_id,
            before=None if before is None else int(before.version),
            after=int(row.version),
        )
        events.emit(
            tx,
            events.IDENTITY_VERIFICATION_CHANGED,
            aggregate_id=row.id,
            aggregate_version=int(row.version),
            payload_ref=row.id,
            now=now,
        )
        demoted = _demote_if_visible(tx, profile, now)
        return Result("applied", detail={"state": row.state, "demoted": demoted})

    return run(body, probe)


def restrict_profile(
    account_id: UUID,
    *,
    staff_subject: str,
    reason: str,
    request_id: UUID,
    probe: TransactionProbe | None = None,
) -> Result:
    refused = _check_staff(staff_subject, reason)
    if refused is not None:
        return refused

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        signal(tx.probe, "after_locks")
        before = Profile.objects.filter(account_id=account_id).first()
        outcome = _chat_checked(chat().restrict_profile(account_id))
        profile = Profile.objects.filter(account_id=account_id).first()
        if outcome.outcome == "applied":
            _audited(
                tx,
                staff_subject=staff_subject,
                scope="moderation",
                action="restrict_profile",
                object_type="profile",
                object_id=profile.id,
                reason=reason,
                request_id=request_id,
                before=None if before is None else int(before.version),
                after=int(profile.version),
            )
        # glow_chat's writer emits profile_restricted (glow-chat-1) itself.
        return Result(outcome.outcome, detail={"state": profile.state})

    return run(body, probe)
