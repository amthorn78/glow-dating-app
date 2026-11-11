"""Photos: the F05 writers and reads (the SV2 brief's D9, D10, D17 and D19; OD-61; OD-62).

Each is one transaction (``tx.run``) that locks the photo owner's account row ``FOR UPDATE`` first
(DM-13 4.1), so a photo writer, a completion check and a withdrawal cannot interleave; then, when
it ends with D9's recompute, ``consent.onboarding`` with the media policy's pointer in one
``read_shared`` call (D19); then its own rows ``FOR UPDATE``. Every state change goes through
``transition``, which allows only F05's registry transitions (``glow_domain.media.TRANSITIONS``),
bumps the asset's version, withholds delivery in every state but ``approved`` and emits the
change's outbox event (references only).

**The member's commands** (``MediaIntent``; F05 ``owner``): ``request_upload`` issues a grant
within the media policy's limits (a new asset ``upload_pending``); ``remove`` withholds delivery at
once and moves to ``removal_pending``; ``reorder`` takes exactly the current approved set, with
collision-safe temporary positions in the same transaction. Another member's asset is
``not_found``. **The member's reads** are their own collection and assets only.

**The store's events** (F05 ``provider``) reach the domain only through the storage port, which
authenticates each before the domain sees it (``record_upload``, ``acknowledge_deletion``); no
member route reaches either. A completion is adopted only if it is the first that matches its
grant's key, within the grant's time and the byte limit of the media policy version the grant
records; any other changes nothing. A deletion is recorded only for an object whose purge was
requested; ``removed`` follows the acknowledgment of every object of the asset.

**The system's steps** (F05 ``system``): ``review``, Glow's own processing on the adopted original
only, then G-02's seam for every adopted upload (given the variant, or the original when
processing made none; an upload with no variant is rejected with ``no_variant``); ``run_check``,
the automated check's approval or rejection, written to ``StaffAudit`` with a ``system:``
subject, asking the hold port before approval and never acting on an asset under a staff
restriction; ``request_purge``, asking the hold port before the store is asked to delete; and
``delivery_reference``, an approved variant's reference for P11's delivery, asking the hold port
first. Staff's restriction on a report is ``staff.restrict_media``.

**D9:** the check's approval ends with the recompute (``requirements_met`` when it meets the last
requirement); the removal or restriction of the last approved photo demotes a ``visible`` profile
(``requirement_removed``). Nothing here logs or returns an object key, an original's reference or
photo bytes.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from django.db.models import Max, Sum

from glow_domain import media as md
from glow_domain import profile_settings as ps
from glow_domain.chat import TransactionProbe
from glow_persistence.models import MediaAsset, MediaObject, MediaUploadGrant, StaffAudit
from glow_profiles import contract, events, idempotency, recompute, settings_store
from glow_profiles.media_fixtures import default_ports
from glow_profiles.tx import (
    FORBIDDEN,
    NOT_FOUND,
    PROVIDER_UNAVAILABLE,
    STALE_VERSION,
    STATE_CONFLICT,
    Refused,
    Result,
    Tx,
    clock,
    lock_account,
    read_account_shared,
    run,
    signal,
)

OPERATION = "media"
# Positions: a new photo goes after the last; reorder moves through temporary positions above
# every real one (the data model: "a collision-safe temporary position strategy inside one UOW").
POSITION_MAX = 29_999
TEMPORARY_POSITION = 30_000
REASON_CODE = re.compile(r"[a-z_]{1,64}")

# Each F05 transition's outbox event (schema ``glow-profiles-1``; references only).
EVENT_OF = {
    "uploaded": events.MEDIA_UPLOADED,
    "review": events.MEDIA_IN_REVIEW,
    "approve": events.MEDIA_APPROVED,
    "reject": events.MEDIA_REJECTED,
    "reorder": events.MEDIA_REORDERED,
    "remove": events.MEDIA_REMOVAL_REQUESTED,
    "purged": events.MEDIA_PURGED,
    "restrict_media": events.MEDIA_RESTRICTED,
}


def _ports(ports: md.MediaPorts | None) -> md.MediaPorts:
    return ports if ports is not None else default_ports()


def _key(intent: dict[str, Any]) -> str:
    return str(intent["meta"]["idempotency_key"])


def _expected(intent: dict[str, Any]) -> int:
    return int(intent["meta"]["expected_version"])


def locked_asset(account_id: UUID, asset_id: UUID | str) -> Any:
    """The account's asset ``FOR UPDATE``, or ``None`` when it is not this account's."""
    return MediaAsset.objects.select_for_update().filter(pk=asset_id, account_id=account_id).first()


def transition(
    tx: Tx,
    asset_id: UUID,
    event: str,
    now: datetime,
    *,
    delivery_ref: str | None = None,
    review_ref: UUID | None = None,
    restriction_ref: UUID | None = None,
    removal_requested_at: datetime | None = None,
    detection: str | None = None,
    rejection_reason: str | None = None,
    position: int | None = None,
) -> Any:
    """One F05 transition of an asset the transaction holds, the only writer of a photo's state:
    refused unless the registry has it; delivery withheld in every state but ``approved`` (D10);
    the asset's version bumped and its event emitted."""
    asset = MediaAsset.objects.select_for_update().get(pk=asset_id)
    after = md.next_state(event, str(asset.state))
    if after is None:
        raise Refused(STATE_CONFLICT, "media_transition")
    asset.state = after
    asset.version += 1
    if after != md.APPROVED:
        asset.approved_variant_ref = None
    elif event == "approve":
        asset.approved_variant_ref = delivery_ref
        asset.review_ref = review_ref
    if restriction_ref is not None:
        asset.restriction_ref = restriction_ref
    if removal_requested_at is not None:
        asset.removal_requested_at = removal_requested_at
    if detection is not None:
        asset.detection = detection
    if rejection_reason is not None:
        asset.rejection_reason = rejection_reason
    if position is not None:
        asset.position = position
    asset.save()
    events.emit(
        tx,
        EVENT_OF[event],
        aggregate_id=asset.id,
        aggregate_version=int(asset.version),
        payload_ref=asset.id,
        now=now,
    )
    return asset


# -- reads ------------------------------------------------------------------------------------


def approved_ids(account_id: UUID) -> list[str]:
    """The account's approved photos, in their order: ``OwnProfile.media_ids``."""
    return [
        str(asset_id)
        for asset_id in MediaAsset.objects.filter(account_id=account_id, state=md.APPROVED)
        .order_by("position")
        .values_list("id", flat=True)
    ]


def collection_version(account_id: UUID) -> int:
    """``MediaCollection.version``, the aggregate revision (P04.3's semantics): 1 when empty, and
    advanced by every asset's creation and every transition, since each bumps an asset's version
    and no asset row is ever deleted."""
    total = MediaAsset.objects.filter(account_id=account_id).aggregate(total=Sum("version"))
    return 1 + int(total["total"] or 0)


def _current(account_id: UUID) -> list[Any]:
    return list(
        MediaAsset.objects.filter(account_id=account_id)
        .exclude(state=md.REMOVED)
        .order_by("position")
    )


def collection(account_id: UUID) -> dict[str, Any]:
    return contract.media_collection(collection_version(account_id), _current(account_id))


def read_asset(account_id: UUID, asset_id: UUID | None) -> dict[str, Any]:
    asset = MediaAsset.objects.filter(pk=asset_id, account_id=account_id).first()
    if asset is None:
        raise Refused(NOT_FOUND, "asset_missing")
    return contract.media_lifecycle(asset)


# -- the member's commands (MediaIntent; F05 owner) -------------------------------------------


def command(account_id: UUID, intent: dict[str, Any]) -> Result:
    """The member's ``MediaIntent``, by its action."""
    if intent["action"] == "request_upload":
        return request_upload(account_id, intent)
    if intent["action"] == "remove":
        return remove_photo(account_id, intent)
    return reorder_photos(account_id, intent)


def request_upload(
    account_id: UUID,
    intent: dict[str, Any],
    *,
    probe: TransactionProbe | None = None,
    ports: md.MediaPorts | None = None,
) -> Result:
    """F05 ``upload_grant``: a new asset and its grant, within the media policy's limits (D10):
    short-lived, opaque and one-use by Glow's own record, recording the policy version it was
    issued under. The store's credential for the grant's key goes to no member; the route returns
    ``MediaUploadGrant`` unchanged (DM-57 U3)."""
    digest = idempotency.digest(OPERATION, intent)
    adapters = _ports(ports)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        policy = settings_store.read_shared(tx, [ps.MEDIA_POLICY])[ps.MEDIA_POLICY]
        assets = list(
            MediaAsset.objects.select_for_update()
            .filter(account_id=account_id)
            .exclude(state=md.REMOVED)
        )
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, OPERATION, _key(intent), digest, now)
        if record is not idempotency.NEW:
            grant = MediaUploadGrant.objects.filter(
                asset_id=record.result_ref, account_id=account_id
            ).first()
            if grant is None:
                raise Refused(NOT_FOUND, "asset_missing")
            return Result("replayed", data=contract.media_upload_grant(grant))
        if _expected(intent) != collection_version(account_id):
            raise Refused(STALE_VERSION, "stale_version")
        if sum(1 for asset in assets if asset.state in md.LIVE) >= policy.content["live_photos"]:
            raise Refused(STATE_CONFLICT, "photo_limit")
        if len(assets) >= ps.MEDIA_COLLECTION:
            raise Refused(STATE_CONFLICT, "collection_full")
        highest = (
            MediaAsset.objects.filter(account_id=account_id)
            .exclude(state=md.REMOVED)
            .aggregate(highest=Max("position"))["highest"]
        )
        position = 1 if highest is None else int(highest) + 1
        if position > POSITION_MAX:
            raise Refused(STATE_CONFLICT, "positions_exhausted")
        if md.next_state("upload_grant", "none") != md.UPLOAD_PENDING:
            raise Refused(STATE_CONFLICT, "media_transition")
        key = md.new_object_key()
        expires_at = now + timedelta(seconds=int(policy.content["grant_seconds"]))
        asset = MediaAsset.objects.create(
            account_id=account_id,
            provider=adapters.storage.name,
            storage_ref=key,
            position=position,
            state=md.UPLOAD_PENDING,
        )
        MediaObject.objects.create(asset=asset, role="original", key=key)
        grant = MediaUploadGrant.objects.create(
            account_id=account_id,
            asset=asset,
            grant_ref=md.new_reference(),
            object_key=key,
            policy_version=policy.policy_version,
            issued_at=now,
            expires_at=expires_at,
        )
        # The credential stays with the adapter: no member is given it in SV2 (DM-57 U3).
        adapters.storage.issue_upload(key, int(policy.content["max_bytes"]), expires_at)
        events.emit(
            tx,
            events.MEDIA_UPLOAD_GRANTED,
            aggregate_id=asset.id,
            aggregate_version=int(asset.version),
            payload_ref=asset.id,
            now=now,
        )
        idempotency.store(
            account_id,
            OPERATION,
            _key(intent),
            digest,
            result_ref=asset.id,
            result_version=int(asset.version),
            now=now,
        )
        return Result("applied", data=contract.media_upload_grant(grant))

    return run(body, probe)


def remove_photo(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F05 ``remove``: delivery withheld at once, the owner's removal recorded, ``removal_pending``
    (D10). Never refused for an asset the owner holds, whatever its state; a repeat is
    ``no_change``. It ends with D9's recompute: the removal of the last approved photo demotes a
    ``visible`` profile (``requirement_removed``)."""
    digest = idempotency.digest(OPERATION, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        # D19: the recompute's consent.onboarding with the media policy, in one call.
        settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT, ps.MEDIA_POLICY])
        asset = locked_asset(account_id, intent["asset_id"])
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, OPERATION, _key(intent), digest, now)
        if asset is None:
            # Another member's asset, or none (D17).
            raise Refused(NOT_FOUND, "asset_missing")
        if record is not idempotency.NEW:
            return Result("replayed", data=contract.media_lifecycle(asset))
        if _expected(intent) != int(asset.version):
            raise Refused(STALE_VERSION, "stale_version")
        unchanged = asset.state in (md.REMOVAL_PENDING, md.REMOVED)
        if not unchanged:
            asset = transition(tx, asset.id, "remove", now, removal_requested_at=now)
        # D9: the shared recompute (F04 ``requirement_removed`` for the last approved photo).
        recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW)
        idempotency.store(
            account_id,
            OPERATION,
            _key(intent),
            digest,
            result_ref=asset.id,
            result_version=int(asset.version),
            now=now,
        )
        return Result("no_change" if unchanged else "applied", data=contract.media_lifecycle(asset))

    return run(body, probe)


def reorder_photos(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F05 ``reorder``: exactly the current approved set, owned, in a new order. The approved
    photos take the positions they already hold, in the order given, each moved first to a
    temporary position above every real one, in this one transaction, so the unique current
    position is never held twice."""
    digest = idempotency.digest(OPERATION, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        assets = list(
            MediaAsset.objects.select_for_update()
            .filter(account_id=account_id)
            .exclude(state=md.REMOVED)
            .order_by("position")
        )
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, OPERATION, _key(intent), digest, now)
        if record is not idempotency.NEW:
            return Result("replayed", data=collection(account_id))
        wanted = [str(value) for value in intent["ordered_asset_ids"]]
        if not set(wanted) <= {str(asset.id) for asset in assets}:
            # Another member's asset, or none (D17).
            raise Refused(NOT_FOUND, "asset_missing")
        if _expected(intent) != collection_version(account_id):
            raise Refused(STALE_VERSION, "stale_version")
        approved = {str(asset.id): asset for asset in assets if asset.state == md.APPROVED}
        if sorted(wanted) != sorted(approved):
            raise Refused(STATE_CONFLICT, "not_the_approved_set")
        slots = sorted(int(asset.position) for asset in approved.values())
        moves = [
            (approved[asset_id], slot)
            for asset_id, slot in zip(wanted, slots, strict=True)
            if int(approved[asset_id].position) != slot
        ]
        for index, (asset, _slot) in enumerate(moves):
            asset.position = TEMPORARY_POSITION + index
            asset.save(update_fields=["position", "updated_at"])
        for asset, slot in moves:
            transition(tx, asset.id, "reorder", now, position=slot)
        idempotency.store(
            account_id,
            OPERATION,
            _key(intent),
            digest,
            result_ref=account_id,
            result_version=collection_version(account_id),
            now=now,
        )
        return Result("applied" if moves else "no_change", data=collection(account_id))

    return run(body, probe)


# -- the store's events (F05 provider), through the storage port only -------------------------


def record_upload(raw: object, *, ports: md.MediaPorts | None = None) -> Result:
    """F05 ``uploaded``: the store's completion, authenticated by the storage adapter. Adopted only
    if it is the first that matches its grant's key, within the grant's time and the byte limit of
    the media policy version the grant records (D10; DM-57 U3, U4); any other completion, a
    duplicate or an out-of-order one, changes nothing, and its object is not adopted (deleting
    such an object is the adapter's, in P11)."""
    adapters = _ports(ports)
    event = adapters.storage.receive(raw)
    if not isinstance(event, md.UploadCompleted):
        return Result("refused", FORBIDDEN, "event_not_authenticated")
    found = MediaUploadGrant.objects.filter(object_key=event.key).first()
    if found is None:
        return Result("no_change", reason="no_grant_for_key")
    account_id = found.account_id

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        grant = (
            MediaUploadGrant.objects.select_for_update()
            .filter(object_key=event.key, account_id=account_id)
            .first()
        )
        if grant is None:
            raise Refused(NOT_FOUND, "grant_missing")
        asset = locked_asset(account_id, grant.asset_id)
        original = (
            MediaObject.objects.select_for_update()
            .filter(asset_id=grant.asset_id, role="original", key=grant.object_key)
            .first()
        )
        signal(tx.probe, "after_locks")
        now = clock(tx)
        if asset is None or original is None:
            raise Refused(NOT_FOUND, "asset_missing")
        if grant.used_at is not None or asset.state != md.UPLOAD_PENDING:
            return Result("no_change", reason="not_awaiting_upload")
        if event.uploaded_at > grant.expires_at:
            return Result("no_change", reason="grant_expired")
        limit = settings_store.version_content(ps.MEDIA_POLICY, grant.policy_version)["max_bytes"]
        if not 1 <= event.byte_size <= int(limit):
            return Result("no_change", reason="over_byte_limit")
        original.byte_size = event.byte_size
        original.entity_tag = event.entity_tag
        original.adopted_at = now
        original.save(update_fields=["byte_size", "entity_tag", "adopted_at", "updated_at"])
        grant.used_at = event.uploaded_at
        grant.save(update_fields=["used_at", "updated_at"])
        adopted = transition(tx, asset.id, "uploaded", now)
        return Result("applied", detail={"asset_id": str(adopted.id), "state": adopted.state})

    return run(body)


def acknowledge_deletion(raw: object, *, ports: md.MediaPorts | None = None) -> Result:
    """The store's acknowledgment that one object is deleted, authenticated by the storage
    adapter. Recorded only for an object of an asset whose purge was requested; a duplicate or an
    out-of-order acknowledgment changes nothing. F05 ``purged`` follows the acknowledgment of
    every object of the asset, the original and each variant (D10)."""
    adapters = _ports(ports)
    event = adapters.storage.receive(raw)
    if not isinstance(event, md.ObjectDeleted):
        return Result("refused", FORBIDDEN, "event_not_authenticated")
    found = MediaObject.objects.filter(key=event.key).select_related("asset").first()
    if found is None:
        return Result("no_change", reason="unknown_object")
    account_id, asset_id = found.asset.account_id, found.asset_id

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        asset = locked_asset(account_id, asset_id)
        held = MediaObject.objects.select_for_update().filter(key=event.key).first()
        signal(tx.probe, "after_locks")
        now = clock(tx)
        if asset is None or held is None:
            raise Refused(NOT_FOUND, "asset_missing")
        if held.deleted_at is not None:
            return Result("no_change", reason="already_deleted")
        if asset.state != md.REMOVAL_PENDING or asset.purge_requested_at is None:
            return Result("no_change", reason="purge_not_requested")
        held.deleted_at = now
        held.save(update_fields=["deleted_at", "updated_at"])
        remaining = MediaObject.objects.filter(asset_id=asset.id, deleted_at__isnull=True)
        if not remaining.exists():
            asset = transition(tx, asset.id, "purged", now)
        return Result("applied", detail={"state": asset.state})

    return run(body)


# -- the system's steps (F05 system) ----------------------------------------------------------


def _owner(asset_id: UUID) -> UUID | None:
    found = MediaAsset.objects.filter(pk=asset_id).values_list("account_id", flat=True).first()
    return None if found is None else UUID(str(found))


def _decision_audit(tx: Tx, asset: Any, action: str, reason: str) -> UUID:
    """The automated check's decision in ``StaffAudit``, with its ``system:`` subject (D10)."""
    row = StaffAudit.objects.create(
        staff_subject=md.CHECK_SUBJECT,
        scope="moderation",
        action=action,
        object_type="media_asset",
        object_id=asset.id,
        reason_code=reason,
        request_id=uuid4(),
        before_version=int(asset.version),
        after_version=int(asset.version) + 1,
    )
    return UUID(str(row.id))


def review(
    asset_id: UUID,
    *,
    probe: TransactionProbe | None = None,
    ports: md.MediaPorts | None = None,
) -> Result:
    """F05 ``review``, the system review step: Glow's own processing on the adopted original
    only, checked against its completion's size and entity tag and the bounds of the policy
    version its grant records, writing the variant under a new key; then G-02's seam, given the
    variant, or the original when processing made none (DM-57 U1). An upload with no variant
    moves to ``review_pending`` and is rejected (``system``) with ``no_variant``, so a file made
    to fail processing cannot skip the seam. An unavailable store changes nothing."""
    adapters = _ports(ports)
    found = _owner(asset_id)
    if found is None:
        return Result("refused", NOT_FOUND, "asset_missing")
    account_id: UUID = found

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        asset = locked_asset(account_id, asset_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        if asset is None:
            raise Refused(NOT_FOUND, "asset_missing")
        if asset.state != md.QUARANTINED:
            return Result("no_change", reason="not_quarantined")
        original = (
            MediaObject.objects.select_for_update()
            .filter(asset_id=asset.id, role="original", adopted_at__isnull=False)
            .first()
        )
        grant = MediaUploadGrant.objects.filter(asset_id=asset.id).first()
        if original is None or grant is None:
            raise Refused(STATE_CONFLICT, "no_adopted_original")
        content = settings_store.version_content(ps.MEDIA_POLICY, grant.policy_version)
        bounds = md.Bounds(
            tuple(content["types"]),
            int(content["max_bytes"]),
            int(content["max_width"]),
            int(content["max_height"]),
            int(content["max_pixels"]),
        )
        variant_key = md.new_object_key()
        try:
            processed = adapters.processing.process(
                original.key,
                int(original.byte_size),
                str(original.entity_tag),
                bounds,
                variant_key,
            )
        except md.StoreUnavailable:
            # Not a processing failure: nothing changes, and the step can run again.
            raise Refused(PROVIDER_UNAVAILABLE, "store_unavailable") from None
        if processed.variant_size is not None:
            MediaObject.objects.create(
                asset=asset, role="variant", key=variant_key, byte_size=processed.variant_size
            )
            seam_key = variant_key
        else:
            seam_key = original.key
        detection = adapters.detection.inspect(asset.id, seam_key)
        if detection.route != "review" or detection.detector != md.NO_DETECTOR:
            # G-02: SV2 builds only the route to review, with no detector configured.
            raise Refused(STATE_CONFLICT, "detection_route_not_built")
        asset = transition(tx, asset.id, "review", now, detection=detection.detector)
        if processed.variant_size is None:
            _decision_audit(tx, asset, "reject", md.NO_VARIANT)
            asset = transition(tx, asset.id, "reject", now, rejection_reason=md.NO_VARIANT)
        return Result("applied", detail={"state": asset.state})

    return run(body, probe)


def run_check(
    asset_id: UUID,
    *,
    probe: TransactionProbe | None = None,
    ports: md.MediaPorts | None = None,
) -> Result:
    """F05 ``approve`` or ``reject`` from ``review_pending``: the automated check's decision
    (OD-61), written to ``StaffAudit`` with a ``system:`` subject. The check never acts on an
    asset under a staff restriction (only the staff decision that closes the report clears one),
    and an approval asks the hold port first. An approval ends with D9's recompute, which makes
    the profile ``visible`` when it meets the last requirement (``requirements_met``)."""
    adapters = _ports(ports)
    found = _owner(asset_id)
    if found is None:
        return Result("refused", NOT_FOUND, "asset_missing")
    account_id: UUID = found

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        # D19: the recompute's consent.onboarding with the media policy, in one call; the
        # decision needs the policy current (P04.3).
        settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT, ps.MEDIA_POLICY])
        asset = locked_asset(account_id, asset_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        if asset is None:
            raise Refused(NOT_FOUND, "asset_missing")
        if asset.state != md.REVIEW_PENDING:
            return Result("no_change", reason="not_in_review")
        if asset.restriction_ref is not None:
            # D10: the check never clears a staff restriction.
            return Result("no_change", reason="restricted")
        variant = (
            MediaObject.objects.filter(asset_id=asset.id, role="variant")
            .order_by("-created_at")
            .first()
        )
        decided = adapters.check.decide(asset.id, None if variant is None else variant.key)
        if decided.decision == "undecided":
            return Result("no_change", reason="undecided")
        if decided.decision == "approve":
            if variant is None:
                raise Refused(STATE_CONFLICT, "no_variant")
            if adapters.hold.held(asset.id):
                return Result("no_change", reason="held")
            review_ref = _decision_audit(tx, asset, "approve", md.APPROVED_BY_CHECK)
            asset = transition(
                tx,
                asset.id,
                "approve",
                now,
                delivery_ref=adapters.storage.delivery_reference(variant.key),
                review_ref=review_ref,
            )
            # D9: the shared recompute (F04 ``requirements_met`` when this meets the last one).
            change = recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW)
            return Result("applied", detail={"state": asset.state, "profile": change.after})
        if decided.decision == "reject":
            reason = decided.reason if REASON_CODE.fullmatch(decided.reason) else "rejected"
            _decision_audit(tx, asset, "reject", reason)
            asset = transition(tx, asset.id, "reject", now, rejection_reason=reason)
            return Result("applied", detail={"state": asset.state})
        raise Refused(STATE_CONFLICT, "unknown_decision")

    return run(body, probe)


def request_purge(
    asset_id: UUID,
    *,
    probe: TransactionProbe | None = None,
    ports: md.MediaPorts | None = None,
) -> Result:
    """The purge of a removed asset (D10): asks the hold port first, then asks the store to
    delete every object of the asset not yet acknowledged deleted. The asset stays
    ``removal_pending`` until the store acknowledges each (``acknowledge_deletion``)."""
    adapters = _ports(ports)
    found = _owner(asset_id)
    if found is None:
        return Result("refused", NOT_FOUND, "asset_missing")
    account_id: UUID = found

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        asset = locked_asset(account_id, asset_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        if asset is None:
            raise Refused(NOT_FOUND, "asset_missing")
        if asset.state != md.REMOVAL_PENDING:
            return Result("no_change", reason="not_removal_pending")
        if adapters.hold.held(asset.id):
            # A hold survives deletion (G-05): delivery is already withheld; only the purge waits.
            return Result("no_change", reason="held")
        keys = tuple(
            MediaObject.objects.filter(asset_id=asset.id, deleted_at__isnull=True)
            .order_by("created_at")
            .values_list("key", flat=True)
        )
        try:
            adapters.storage.delete(keys)
        except md.StoreUnavailable:
            raise Refused(PROVIDER_UNAVAILABLE, "store_unavailable") from None
        asset.purge_requested_at = now
        asset.save(update_fields=["purge_requested_at", "updated_at"])
        return Result("applied", detail={"objects": len(keys)})

    return run(body, probe)


def delivery_reference(asset_id: UUID, *, ports: md.MediaPorts | None = None) -> Result:
    """For P11's authorized delivery (no route in SV2): an approved variant's reference, asking
    the hold port first; ``None`` for any other state, a restriction, a removal or a hold. Never
    the original's, never an object key, never a public address."""
    adapters = _ports(ports)
    found = _owner(asset_id)
    if found is None:
        return Result("refused", NOT_FOUND, "asset_missing")
    account_id: UUID = found

    def body(tx: Tx) -> Result:
        read_account_shared(tx, account_id)
        asset = MediaAsset.objects.filter(pk=asset_id, account_id=account_id).first()
        if asset is None:
            raise Refused(NOT_FOUND, "asset_missing")
        deliverable = (
            asset.state == md.APPROVED
            and asset.restriction_ref is None
            and asset.removal_requested_at is None
            and not adapters.hold.held(asset.id)
        )
        return Result(
            "read", detail={"delivery_ref": asset.approved_variant_ref if deliverable else None}
        )

    return run(body)
