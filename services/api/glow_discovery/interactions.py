"""Who may contact whom (the SV3 brief's D9 to D12; F08, F09, F10 and F13), each command one
transaction (``glow_profiles.tx.run``), sealed until P11.

**The locks** (D2; DM-60 section 11). Every command locks both members' account rows ``FOR NO KEY
UPDATE`` in ``glow_chat``'s canonical order, the lower account first, before anything else, then
the settings it reads under their pointers' ``FOR SHARE`` locks, all in its first ``read_shared``
call, in name order (D19), then reads the time from ``clock_timestamp()``. Each account lock is
SV2's reviewed ``lock_account`` (DM-61), so no new lock site exists: the actor's account must be
``active`` (``forbidden`` otherwise); the other member's lock is held in any state, which the
checks below then judge. Every writer of a fact the checks read takes its owner's account row
first (SV2's D9; ``glow_chat``'s writers), every writer of a directional row is a command here,
and every writer of a batch is a page or a command here, each holding its owner's account row, so
nothing the checks read can change before the commit. ``glow_chat``'s writers nest inside as
savepoints, after these locks, so they take the same order; any result of theirs but ``applied``
or ``no_change`` refuses the whole transaction.

**Idempotency** (D9, D11) is SV2's: unique by actor, operation and key, with the stored digest
keyed as SV2's are (``glow_profiles.idempotency``'s ``digest`` and ``decide``), checked right after
the locks and before any staleness, so an identical command replays its original receipt with
the current projection after its batch is consumed; the same key with another intent is
``idempotency_conflict``. Only a committed command stores its record, with the receipt's outcome
code (``liked``, ``passed``, ``withdrawn``, ``unmatched``, ``blocked`` or ``unblocked``), its
object and its committed version. ``CommandMeta.expected_version`` addresses the directional row
for like, pass and undo, the match for unmatch, and the directional block for block and unblock
(zero for its absence; ``stale_version`` otherwise).

**Like and pass** (D9; F08) name a batch: the target must be in the actor's named batch at that
version, fresh (``ready``, unexpired, the actor's versions and the policy version current), and
the pair must pass D3 to D5 (``glow_domain.trusted_eligibility``'s service over the trusted
adapter's one-statement pair read, ``OrmPairActionTransaction``) and D7's consumption
(``predicates.UNCONSUMED``), all under the locks; otherwise the generic stale response
(``stale_version``, the same whatever the cause, D8) and nothing is written. A pass over the
actor's own like is ``state_conflict`` (F08 has no such entry). A committed like or pass consumes
its batch (F07's ``invalidate``: ``stale``, its version advanced). Neither changes anything of the
target's, so the target cannot learn of it. **A like that finds the target's ``liked`` row** makes
the match in the same transaction, through ``glow_chat``'s ``activate_reciprocal`` (D10 (a)),
whose documented precondition is this recheck.

**Undo** (D12; D13's ``InteractionUndoIntent``) withdraws the actor's most recent pass within
``discovery.undo``'s ``waiting_days`` of it, while the setting is on (``forbidden`` while off), and
only while that pass is the actor's latest decision (the latest ``decided_at`` of all their rows,
in any state; DM-75): one step, never a chain. The row is kept and its version advanced
(``withdrawn``), never deleted and created again.

**Unmatch, block and unblock** (D11; F10, F13) run ``glow_chat``'s ``unmatch``, ``block`` and
``unblock`` unchanged, with no eligibility or policy prerequisite: unmatch revokes contact and
never grants rematch; block works after an unmatch and while paused; unblock restores no match and
no send. Another member's match is ``not_found``.

**The actor's own versions** (D13; DM-74; correction B-C1): ``read_own_versions`` answers, for a
target profile ID, the actor's own directional row toward that profile's account and the actor's
own block of it, each state and version (``none`` and ``0`` where the actor has no row), so a
client that has lost its own command answers, or a second device, can learn the version each
command compares ``CommandMeta.expected_version`` with. It is one transaction holding the actor's
account row ``FOR SHARE`` first (``read_account_shared``), as the match read does, so it waits for
a command of the actor's in flight. Its answer depends only on the actor's own rows: it reads the
profile's account ID and nothing else of the profile, never answers ``not_found`` for a profile
(missing, not visible, paused, restricted, removed, excluded or blocking the actor alike), and
never reads a row whose actor is the other member, so their like, pass or block is never shown.

Nothing here logs or returns another member's private value, a count or a reason (D8, D17); a
refusal names a code and an internal reason, never a value. No answer names a block's direction,
but a match's state (``restricted`` only after a block) lets the member who did not block infer
it: D8's gap, carried to SV4 before P11 (DM-75).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from django.conf import settings as django_settings
from django.db.models import F
from django.db.models.functions import Now

from glow_chat.contact import OrmContactPersistence
from glow_discovery import contract, pages, policy, predicates
from glow_discovery.eligibility import OrmPairActionTransaction, parameters
from glow_domain.chat import ContactResult, TransactionProbe
from glow_domain.identity import AccountId
from glow_domain.trusted_eligibility import EligibilityDecisionState, TrustedEligibilityService
from glow_persistence.models import (
    Block,
    DirectionalInteraction,
    IdempotencyRecord,
    Match,
    Profile,
    RecommendationBatch,
    RecommendationEntry,
)
from glow_profiles import idempotency, settings_store
from glow_profiles.tx import (
    FORBIDDEN,
    NOT_FOUND,
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

# The idempotency records' operations (D9, D11, D12).
INTERACTION = "interaction"
UNDO = "interaction_undo"
UNMATCH = "unmatch"
BLOCK = "block"

STALE = "stale"


def chat() -> OrmContactPersistence:
    """``glow_chat``'s reviewed writers; the provider's name is the identity fragment's."""
    return OrmContactPersistence(provider=django_settings.GLOW_IDENTITY_CHAT_PROVIDER)


def _checked(result: ContactResult) -> ContactResult:
    """A nested ``glow_chat`` writer's result other than ``applied`` or ``no_change`` is a refusal
    of the whole transaction (as SV2's operations treat them)."""
    if result.outcome in ("applied", "no_change"):
        return result
    if result.outcome == "refused":
        code = NOT_FOUND if result.reason.endswith("_missing") else STATE_CONFLICT
        raise Refused(code, f"chat:{result.reason}")
    raise Refused(STATE_CONFLICT, f"chat_{result.outcome}:{result.reason}")


def _key(intent: dict[str, Any]) -> str:
    return str(intent["meta"]["idempotency_key"])


def _expected(intent: dict[str, Any]) -> int:
    return int(intent["meta"]["expected_version"])


def _account_of_profile(profile_id: str) -> UUID | None:
    """A profile's account, read before the locks: an identifier, which never changes."""
    found = Profile.objects.filter(pk=profile_id).values_list("account_id", flat=True).first()
    return UUID(str(found)) if found is not None else None


def _profile_of_account(account_id: UUID) -> str | None:
    found = Profile.objects.filter(account_id=account_id).values_list("id", flat=True).first()
    return str(found) if found is not None else None


def _lock_pair(tx: Tx, actor_id: UUID, other_id: UUID | None) -> None:
    """D2: both account rows ``FOR NO KEY UPDATE``, the lower first, through SV2's reviewed
    ``lock_account``. The actor's must be ``active``; the other's is held in any state (its lock
    is taken before ``lock_account`` judges it), and the checks after the locks judge it."""
    accounts = {actor_id} if other_id is None else {actor_id, other_id}
    for account_id in sorted(accounts):
        try:
            lock_account(tx, account_id)
        except Refused as refused:
            if account_id == actor_id or refused.reason != "account_not_active":
                raise


def _store(
    actor_id: UUID,
    operation: str,
    key: str,
    request_digest: str,
    *,
    outcome_code: str,
    result_ref: UUID,
    result_version: int,
    now: datetime,
) -> None:
    """The committed command's record (SV2's, with the receipt's outcome code)."""
    IdempotencyRecord.objects.create(
        actor_id=actor_id,
        operation=operation,
        key=key,
        request_digest=request_digest,
        result_ref=result_ref,
        result_version=result_version,
        outcome_code=outcome_code,
        state="completed",
        expires_at=now + idempotency.RECORD_LIFETIME,
    )


def _answer(
    outcome: str,
    record_receipt: dict[str, Any],
    projection: dict[str, Any] | None,
    *,
    replayed: bool,
) -> Result:
    """The served data is the current projection; the internal command result holds the original
    receipt and the replay flag (``detail["command_result"]``)."""
    result = contract.command_result(record_receipt, replayed, projection)
    if projection is None:
        raise Refused(NOT_FOUND, "projection_unavailable")
    return Result(outcome, data=projection, detail={"command_result": result})


def _receipt_of(record: Any) -> dict[str, Any]:
    return contract.receipt(
        str(record.outcome_code), str(record.result_ref), int(record.result_version)
    )


# -- projections ------------------------------------------------------------------------------


def _pair_match(actor_id: UUID, other_id: UUID) -> Any:
    low, high = sorted((actor_id, other_id))
    return Match.objects.filter(account_low_id=low, account_high_id=high).first()


def _interaction_projection(row: Any) -> dict[str, Any] | None:
    """The actor's own directional row as it is now: ``InteractionOutcome`` while ``liked`` or
    ``passed``, D13's ``InteractionUndoOutcome`` while ``withdrawn``."""
    target_profile = _profile_of_account(UUID(str(row.target_id)))
    if target_profile is None:
        return None
    if row.state == "withdrawn":
        return contract.undo_outcome(target_profile, int(row.version))
    match = None
    if row.state == "liked":
        found = _pair_match(UUID(str(row.actor_id)), UUID(str(row.target_id)))
        match = str(found.id) if found is not None else None
    return contract.interaction_outcome(target_profile, int(row.version), str(row.state), match)


def _match_projection(match: Any, actor_id: UUID) -> dict[str, Any] | None:
    low, high = UUID(str(match.account_low_id)), UUID(str(match.account_high_id))
    if actor_id not in (low, high):
        return None
    other = _profile_of_account(high if actor_id == low else low)
    if other is None:
        return None
    return contract.match_projection(str(match.id), int(match.version), other, str(match.state))


def _block_projection(block: Any) -> dict[str, Any] | None:
    target_profile = _profile_of_account(UUID(str(block.target_id)))
    if target_profile is None:
        return None
    return contract.block_outcome(target_profile, int(block.version), str(block.state))


# -- like and pass (D9, D10; F08, F09) ----------------------------------------------------------


@dataclass(frozen=True)
class _Pair:
    actor: UUID
    target: UUID


def _eligible(tx: Tx, selection: policy.Selection, pair: _Pair) -> bool:
    """D3 to D5 for the pair as locked, through the trusted adapter (D2), and D7's consumption."""
    decision = TrustedEligibilityService(OrmPairActionTransaction(selection)).evaluate(
        AccountId(str(pair.actor)), AccountId(str(pair.target))
    )
    if decision.state is not EligibilityDecisionState.READY:
        return False
    values = parameters(selection, pair.actor)
    values["candidate"] = pair.target
    tx.cursor.execute(predicates.UNCONSUMED, values)
    row = tx.cursor.fetchone()
    return row is not None and row[0] is True


def _batch_names(
    intent: dict[str, Any],
    pair: _Pair,
    viewer: pages.Viewer,
    selection: policy.Selection,
    now: datetime,
) -> Any:
    """D9: the actor's named batch at that version, fresh, holding the target; else ``None``."""
    batch = RecommendationBatch.objects.filter(pk=intent["batch_id"]).first()
    if batch is None or int(batch.version) != int(intent["batch_version"]):
        return None
    if not pages._fresh(batch, pair.actor, str(batch.collection), viewer.versions, selection, now):
        return None
    if not RecommendationEntry.objects.filter(batch_id=batch.id, candidate_id=pair.target).exists():
        return None
    return batch


def interact(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F08's like and pass, and F09's match on reciprocal likes (D9, D10)."""
    request_digest = idempotency.digest(INTERACTION, intent)

    def body(tx: Tx) -> Result:
        target_id = _account_of_profile(intent["target_profile_id"])
        _lock_pair(tx, account_id, target_id)
        selection = pages._selection(tx)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, INTERACTION, _key(intent), request_digest, now)
        if record is not idempotency.NEW:
            # Replay before staleness: the original receipt, with the current projection.
            row = DirectionalInteraction.objects.filter(
                pk=record.result_ref, actor_id=account_id
            ).first()
            projection = _interaction_projection(row) if row is not None else None
            return _answer("replayed", _receipt_of(record), projection, replayed=True)
        viewer = pages._viewer(tx, account_id, selection)
        if not viewer.eligible:
            raise Refused(FORBIDDEN, "viewer_not_eligible")
        if target_id is None or target_id == account_id:
            raise Refused(STALE_VERSION, f"{STALE}:target")
        pair = _Pair(account_id, target_id)
        row = DirectionalInteraction.objects.filter(
            actor_id=account_id, target_id=target_id
        ).first()
        if _expected(intent) != (0 if row is None else int(row.version)):
            raise Refused(STALE_VERSION, "stale_version")
        action = intent["action"]
        if action == "pass" and row is not None and row.state == "liked":
            # F08 has no pass over a like.
            raise Refused(STATE_CONFLICT, "pass_over_like")
        batch = _batch_names(intent, pair, viewer, selection, now)
        if batch is None:
            raise Refused(STALE_VERSION, f"{STALE}:batch")
        signal(tx.probe, "before_recheck")
        if not _eligible(tx, selection, pair):
            raise Refused(STALE_VERSION, f"{STALE}:pair")
        state = "liked" if action == "like" else "passed"
        if row is None:
            row = DirectionalInteraction.objects.create(
                actor_id=account_id,
                target_id=target_id,
                state=state,
                policy_version=selection.version,
                decided_at=now,
            )
        else:
            row.state = state
            row.version += 1
            row.policy_version = selection.version
            row.decided_at = now
            row.save(
                update_fields=["state", "version", "policy_version", "decided_at", "updated_at"]
            )
        # F07's invalidate: the named batch is consumed; the next action needs a fresh page.
        RecommendationBatch.objects.filter(pk=batch.id).update(
            state="stale", version=F("version") + 1, updated_at=Now()
        )
        if (
            state == "liked"
            and DirectionalInteraction.objects.filter(
                actor_id=target_id, target_id=account_id, state="liked"
            ).exists()
        ):
            # D10 (a): the match, under the locks already held, after the recheck above.
            activated = chat().activate_reciprocal(account_id, target_id)
            if activated.outcome != "applied":
                raise Refused(STATE_CONFLICT, f"chat:{activated.reason}")
            tx.events.extend(activated.events)
        _store(
            account_id,
            INTERACTION,
            _key(intent),
            request_digest,
            outcome_code=state,
            result_ref=row.id,
            result_version=int(row.version),
            now=now,
        )
        return _answer(
            "applied",
            contract.receipt(state, str(row.id), int(row.version)),
            _interaction_projection(row),
            replayed=False,
        )

    return run(body, probe)


# -- undo (D12; D13's InteractionUndoIntent) -------------------------------------------------


def undo(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """D12: the actor's most recent pass, withdrawn within ``discovery.undo``'s waiting period."""
    request_digest = idempotency.digest(UNDO, intent)

    def body(tx: Tx) -> Result:
        target_id = _account_of_profile(intent["target_profile_id"])
        _lock_pair(tx, account_id, target_id)
        setting = settings_store.read_shared(tx, policy.UNDO_SETTINGS)[policy.UNDO_SETTINGS[0]]
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, UNDO, _key(intent), request_digest, now)
        if record is not idempotency.NEW:
            row = DirectionalInteraction.objects.filter(
                pk=record.result_ref, actor_id=account_id
            ).first()
            projection = _interaction_projection(row) if row is not None else None
            return _answer("replayed", _receipt_of(record), projection, replayed=True)
        window = policy.undo_window(setting.content)
        if window is None:
            raise Refused(FORBIDDEN, "undo_off")
        row = (
            DirectionalInteraction.objects.filter(actor_id=account_id, target_id=target_id).first()
            if target_id is not None
            else None
        )
        if _expected(intent) != (0 if row is None else int(row.version)):
            raise Refused(STALE_VERSION, "stale_version")
        if row is None or row.state != "passed":
            raise Refused(STATE_CONFLICT, "no_pass")
        latest = (
            DirectionalInteraction.objects.filter(actor_id=account_id)
            .order_by("-decided_at", "-id")
            .values_list("id", flat=True)
            .first()
        )
        if latest != row.id:
            raise Refused(STATE_CONFLICT, "not_the_most_recent_pass")
        if now >= row.decided_at + window:
            raise Refused(STATE_CONFLICT, "undo_window_ended")
        row.state = "withdrawn"
        row.version += 1
        row.policy_version = setting.policy_version
        row.decided_at = now
        row.save(update_fields=["state", "version", "policy_version", "decided_at", "updated_at"])
        _store(
            account_id,
            UNDO,
            _key(intent),
            request_digest,
            outcome_code="withdrawn",
            result_ref=row.id,
            result_version=int(row.version),
            now=now,
        )
        return _answer(
            "applied",
            contract.receipt("withdrawn", str(row.id), int(row.version)),
            _interaction_projection(row),
            replayed=False,
        )

    return run(body, probe)


# -- unmatch (D11; F10) --------------------------------------------------------------------------


def unmatch(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F10: the participant's unmatch, through ``glow_chat``'s ``unmatch`` unchanged."""
    request_digest = idempotency.digest(UNMATCH, intent)

    def body(tx: Tx) -> Result:
        # Only identifiers before the locks: a match's pair never changes.
        pair = (
            Match.objects.filter(pk=intent["match_id"])
            .values_list("account_low_id", "account_high_id")
            .first()
        )
        if pair is None or account_id not in (pair[0], pair[1]):
            raise Refused(NOT_FOUND, "match_not_found")
        other_id = pair[1] if account_id == pair[0] else pair[0]
        _lock_pair(tx, account_id, UUID(str(other_id)))
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, UNMATCH, _key(intent), request_digest, now)
        match = Match.objects.filter(pk=intent["match_id"]).first()
        if match is None:
            raise Refused(NOT_FOUND, "match_not_found")
        if record is not idempotency.NEW:
            projection = _match_projection(match, account_id)
            return _answer("replayed", _receipt_of(record), projection, replayed=True)
        if _expected(intent) != int(match.version):
            raise Refused(STALE_VERSION, "stale_version")
        outcome = _checked(chat().unmatch(account_id, match.id))
        tx.events.extend(outcome.events)
        match.refresh_from_db()
        _store(
            account_id,
            UNMATCH,
            _key(intent),
            request_digest,
            outcome_code="unmatched",
            result_ref=match.id,
            result_version=int(match.version),
            now=now,
        )
        return _answer(
            "applied" if outcome.outcome == "applied" else "no_change",
            contract.receipt("unmatched", str(match.id), int(match.version)),
            _match_projection(match, account_id),
            replayed=False,
        )

    return run(body, probe)


# -- block and unblock (D11; F13) -------------------------------------------------------------


def block(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F13: the actor's block or unblock, through ``glow_chat``'s ``block`` and ``unblock``
    unchanged, in the actor's direction only."""
    request_digest = idempotency.digest(BLOCK, intent)

    def body(tx: Tx) -> Result:
        target_id = _account_of_profile(intent["target_profile_id"])
        if target_id is None:
            raise Refused(NOT_FOUND, "target_not_found")
        if target_id == account_id:
            raise Refused(STATE_CONFLICT, "self_target")
        _lock_pair(tx, account_id, target_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, BLOCK, _key(intent), request_digest, now)
        current = Block.objects.filter(actor_id=account_id, target_id=target_id).first()
        if record is not idempotency.NEW:
            projection = _block_projection(current) if current is not None else None
            return _answer("replayed", _receipt_of(record), projection, replayed=True)
        if _expected(intent) != (0 if current is None else int(current.version)):
            raise Refused(STALE_VERSION, "stale_version")
        writer = chat()
        if intent["action"] == "block":
            outcome = _checked(writer.block(account_id, target_id))
            code = "blocked"
        else:
            outcome = _checked(writer.unblock(account_id, target_id))
            code = "unblocked"
        tx.events.extend(outcome.events)
        current = Block.objects.filter(actor_id=account_id, target_id=target_id).first()
        if current is None:
            raise Refused(STATE_CONFLICT, "block_missing")
        _store(
            account_id,
            BLOCK,
            _key(intent),
            request_digest,
            outcome_code=code,
            result_ref=current.id,
            result_version=int(current.version),
            now=now,
        )
        return _answer(
            "applied",
            contract.receipt(code, str(current.id), int(current.version)),
            _block_projection(current),
            replayed=False,
        )

    return run(body, probe)


# -- the match read (F09; OwnedObjectRequest) -------------------------------------------------


def read_match(account_id: UUID, match_id: UUID) -> Result:
    """F09's ``MatchProjection`` for a participant; another member's match is ``not_found``."""

    def body(tx: Tx) -> Result:
        read_account_shared(tx, account_id)
        match = Match.objects.filter(pk=match_id).first()
        projection = _match_projection(match, account_id) if match is not None else None
        if projection is None:
            raise Refused(NOT_FOUND, "match_not_found")
        return Result("read", data=projection)

    return run(body)


# -- the actor's own versions (D13; DM-74; correction B-C1) -----------------------------------


def read_own_versions(
    account_id: UUID, profile_id: UUID, *, probe: TransactionProbe | None = None
) -> Result:
    """The actor's own directional row toward the profile's account and the actor's own block of
    it, each state and version (``none`` and ``0`` where the actor has none): the same answer
    whatever the profile's state, or whether it exists, and never the other member's rows."""

    def body(tx: Tx) -> Result:
        read_account_shared(tx, account_id)
        target_id = _account_of_profile(str(profile_id))
        row = (
            DirectionalInteraction.objects.filter(actor_id=account_id, target_id=target_id)
            .values_list("state", "version")
            .first()
            if target_id is not None
            else None
        )
        own_block = (
            Block.objects.filter(actor_id=account_id, target_id=target_id)
            .values_list("state", "version")
            .first()
            if target_id is not None
            else None
        )
        return Result("read", data=contract.own_versions(str(profile_id), row, own_block))

    return run(body, probe)
