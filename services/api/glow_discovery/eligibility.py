"""The trusted eligibility adapter (the SV3 brief's D2 and D3; Outcome item 1): the ORM behind
``glow_domain.trusted_eligibility``'s ``TrustedEligibilityService``.

``OrmEligibilityEvidence.acquire`` reads both members' authoritative rows (account, age state,
consent, profile, the four fields and both "show me" sets, age range, area, and both block
directions) in **one statement** (``predicates.PAIR``), so in PostgreSQL's READ COMMITTED it reads
one snapshot; it never takes a client's assertion. Its ``PairEvidenceVersion`` is built from both
accounts' ``eligibility_version``, ``preferences_version`` and ``blocks_version``, both profiles'
versions and the selection's policy version (D2). A missing account is missing evidence
(``None``); a missing profile, age state, preferences or set row reads as unknown or as a failure,
never a pass (D3: unknown denies). The predicates are ``predicates``' own, the ones the selection
and each page's recheck apply, so the adapter and the pages cannot disagree; consumption (D7) is the
pages' and is not read here.

``OrmPairActionTransaction`` is the ``PairActionTransaction`` protocol for an action that already
holds its locks (Stage B's like, D9: both accounts' rows in ``glow_chat``'s canonical order, then
the settings' pointers in name order): ``acquire`` reads as above, inside the caller's transaction,
and ``commit_if_current`` reads again and reports whether every revision still equals the one the
action checked. It writes nothing; the caller's transaction commits or rolls back.
"""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from django.db import connection

from glow_discovery import policy, predicates
from glow_domain.eligibility import (
    BlockState,
    EligibilitySnapshot,
    PairPolicyInputs,
    PredicateOutcome,
)
from glow_domain.identity import AccountId
from glow_domain.trusted_eligibility import (
    BoundPairPolicy,
    PairEligibilityEvidence,
    PairEvidenceVersion,
    PolicyReadiness,
)


def outcome(value: object) -> PredicateOutcome:
    """A predicate's SQL value: true passes, false fails, NULL (a missing row) is unknown."""
    if value is True:
        return PredicateOutcome.PASS
    if value is False:
        return PredicateOutcome.FAIL
    return PredicateOutcome.UNKNOWN


def parameters(selection: policy.Selection, viewer: UUID) -> dict[str, Any]:
    """The statements' parameters for one viewer under one selection. None is a key or is derived
    from one (D6; DM-61 K2): the tie-break is drawn inside the selection."""
    found: dict[str, Any] = {
        "viewer": viewer,
        "today": selection.today,
        "adult_states": list(policy.ACCEPTED_AGE_STATES),
        "consent": selection.onboarding_consent,
        "both_ways": selection.both_ways,
        "choices": json.dumps(dict(selection.distance_miles), sort_keys=True),
    }
    for field, narrowable in selection.narrowable.items():
        found[f"narrow_{field}"] = narrowable
    return found


def _snapshot(account_id: AccountId, row: tuple[Any, ...]) -> tuple[EligibilitySnapshot, str]:
    (_, eligibility, preferences, blocks, profile_version, account, profile, adult, consent) = row
    shown = PredicateOutcome.UNKNOWN if profile is None else outcome(profile == "visible")
    moderation = PredicateOutcome.UNKNOWN if profile is None else outcome(profile != "restricted")
    version = f"{int(eligibility)}.{int(profile_version or 0)}"
    snapshot = EligibilitySnapshot(
        account_id=account_id,
        snapshot_version=version,
        adult=outcome(adult),
        consent=outcome(consent),
        verified=shown,
        active=outcome(account == "active"),
        complete=shown,
        visible=shown,
        moderation=moderation,
    )
    return snapshot, f"{int(preferences)}:{int(blocks)}"


class OrmEligibilityEvidence:
    """``EligibilityEvidenceRepository`` over the ORM's rows, under one selection's policy."""

    def __init__(self, selection: policy.Selection) -> None:
        self.selection = selection

    def acquire(
        self, viewer_id: AccountId, candidate_id: AccountId
    ) -> PairEligibilityEvidence | None:
        viewer, candidate = UUID(viewer_id.value), UUID(candidate_id.value)
        found = parameters(self.selection, viewer)
        found["candidate"] = candidate
        with connection.cursor() as cursor:
            cursor.execute(predicates.PAIR, found)
            row = cursor.fetchone()
        if row is None or row[0] is None or row[9] is None:
            return None
        viewer_snapshot, viewer_counters = _snapshot(viewer_id, row[0:9])
        candidate_snapshot, candidate_counters = _snapshot(candidate_id, row[9:18])
        viewer_accepts, candidate_accepts, viewer_blocks, candidate_blocks = row[18:22]
        inputs = PairPolicyInputs(
            policy_version=self.selection.version,
            viewer_accepts_candidate=outcome(viewer_accepts),
            candidate_accepts_viewer=outcome(candidate_accepts),
            viewer_blocks_candidate=BlockState.BLOCKED if viewer_blocks else BlockState.CLEAR,
            candidate_blocks_viewer=BlockState.BLOCKED if candidate_blocks else BlockState.CLEAR,
        )
        version = PairEvidenceVersion(
            viewer_id=viewer_id,
            candidate_id=candidate_id,
            viewer_snapshot_version=viewer_snapshot.snapshot_version,
            candidate_snapshot_version=candidate_snapshot.snapshot_version,
            policy_version=self.selection.version,
            viewer_preference_version=viewer_counters.split(":")[0],
            candidate_preference_version=candidate_counters.split(":")[0],
            viewer_block_version=viewer_counters.split(":")[1],
            candidate_block_version=candidate_counters.split(":")[1],
        )
        return PairEligibilityEvidence(
            viewer=viewer_snapshot,
            candidate=candidate_snapshot,
            policy=BoundPairPolicy(version, inputs, PolicyReadiness.RESOLVED),
            current_version=version,
        )


class OrmPairActionTransaction(OrmEligibilityEvidence):
    """``PairActionTransaction`` inside a caller's transaction that already holds the action's
    locks (D2's actions; Stage B's like)."""

    def acquire(
        self, viewer_id: AccountId, candidate_id: AccountId
    ) -> PairEligibilityEvidence | None:
        if not connection.in_atomic_block:
            raise RuntimeError("pair_action_requires_a_transaction")
        return super().acquire(viewer_id, candidate_id)

    def commit_if_current(self, expected: PairEvidenceVersion) -> bool:
        evidence = self.acquire(expected.viewer_id, expected.candidate_id)
        return evidence is not None and evidence.current_version == expected
