"""Internal fixture application service: eligibility precedes compatibility.

Inputs are trusted internal account IDs and explicit policy decisions, not an
authenticated HTTP request. Reads are repeated on every call but are not atomic
or durable. No ranking, recommendation queue, like, match or storage is created.
"""

from dataclasses import dataclass, field
from enum import Enum

from .compatibility import CompatibilityRequest, FixtureCompatibilityResult
from .eligibility import (
    EligibilitySnapshot,
    PairEligibility,
    PairPolicyInputs,
    Subject,
    evaluate_pair,
)
from .identity import AccountId, ChartMapping, ChartMappingState
from .ports import ChartMappingRepository, EligibilitySnapshotRepository, FixtureCompatibilityPort


class PairEvaluationState(Enum):
    REJECTED_INPUT = "rejected_input"
    EXCLUDED = "excluded"
    PENDING_IDENTITY = "pending_identity"
    COMPATIBILITY_EVALUATED = "compatibility_evaluated"


class RejectionReason(Enum):
    MISSING_SNAPSHOT = "missing_snapshot"
    SNAPSHOT_IDENTITY_MISMATCH = "snapshot_identity_mismatch"
    MISSING_MAPPING = "missing_mapping"
    MAPPING_IDENTITY_MISMATCH = "mapping_identity_mismatch"


@dataclass(frozen=True)
class InputRejection:
    reason: RejectionReason
    subject: Subject


@dataclass(frozen=True)
class FixturePairEvaluation:
    state: PairEvaluationState
    viewer_id: AccountId
    candidate_id: AccountId
    eligibility: PairEligibility | None = None
    compatibility: FixtureCompatibilityResult | None = None
    rejection: InputRejection | None = None
    mode: str = field(default="fixture", init=False)


@dataclass(frozen=True)
class FixturePairEvaluationService:
    environment: str
    snapshots: EligibilitySnapshotRepository
    mappings: ChartMappingRepository
    provider: FixtureCompatibilityPort

    def __post_init__(self) -> None:
        if self.environment not in {"development", "test"}:
            raise ValueError("Fixture pair evaluation is restricted to development and test.")

    def evaluate(
        self,
        viewer_id: AccountId,
        candidate_id: AccountId,
        policy: PairPolicyInputs,
    ) -> FixturePairEvaluation:
        if not isinstance(viewer_id, AccountId) or not isinstance(candidate_id, AccountId):
            raise TypeError("Pair evaluation requires application AccountId values.")
        if not isinstance(policy, PairPolicyInputs):
            raise TypeError("Pair evaluation requires explicit PairPolicyInputs.")

        viewer = self.snapshots.get(viewer_id)
        candidate = self.snapshots.get(candidate_id)
        for subject, requested_id, snapshot in (
            (Subject.VIEWER, viewer_id, viewer),
            (Subject.CANDIDATE, candidate_id, candidate),
        ):
            if snapshot is None:
                return FixturePairEvaluation(
                    PairEvaluationState.REJECTED_INPUT,
                    viewer_id,
                    candidate_id,
                    rejection=InputRejection(RejectionReason.MISSING_SNAPSHOT, subject),
                )
            if not isinstance(snapshot, EligibilitySnapshot):
                raise TypeError("Snapshot repository returned an unexpected value type.")
            if snapshot.account_id != requested_id:
                return FixturePairEvaluation(
                    PairEvaluationState.REJECTED_INPUT,
                    viewer_id,
                    candidate_id,
                    rejection=InputRejection(RejectionReason.SNAPSHOT_IDENTITY_MISMATCH, subject),
                )
        # The loop establishes these facts at runtime; state them explicitly for
        # type narrowing instead of casting missing inputs into valid snapshots.
        if viewer is None or candidate is None:
            raise AssertionError("Validated snapshots unexpectedly absent.")
        eligibility = evaluate_pair(viewer, candidate, policy)
        if not eligibility.eligible:
            return FixturePairEvaluation(
                PairEvaluationState.EXCLUDED,
                viewer_id,
                candidate_id,
                eligibility=eligibility,
            )

        viewer_mapping = self.mappings.get(viewer_id)
        candidate_mapping = self.mappings.get(candidate_id)
        for subject, requested_id, mapping in (
            (Subject.VIEWER, viewer_id, viewer_mapping),
            (Subject.CANDIDATE, candidate_id, candidate_mapping),
        ):
            if mapping is None:
                return FixturePairEvaluation(
                    PairEvaluationState.REJECTED_INPUT,
                    viewer_id,
                    candidate_id,
                    eligibility=eligibility,
                    rejection=InputRejection(RejectionReason.MISSING_MAPPING, subject),
                )
            if not isinstance(mapping, ChartMapping):
                raise TypeError("Mapping repository returned an unexpected value type.")
            if mapping.account_id != requested_id:
                return FixturePairEvaluation(
                    PairEvaluationState.REJECTED_INPUT,
                    viewer_id,
                    candidate_id,
                    eligibility=eligibility,
                    rejection=InputRejection(RejectionReason.MAPPING_IDENTITY_MISMATCH, subject),
                )
        if viewer_mapping is None or candidate_mapping is None:
            raise AssertionError("Validated mappings unexpectedly absent.")
        if any(
            mapping.state is not ChartMappingState.RESOLVED
            for mapping in (viewer_mapping, candidate_mapping)
        ):
            return FixturePairEvaluation(
                PairEvaluationState.PENDING_IDENTITY,
                viewer_id,
                candidate_id,
                eligibility=eligibility,
            )

        # The existing port defines unavailable as a typed result. It declares
        # no catchable exception family: programming/adapter errors propagate.
        result = self.provider.evaluate_pair(
            CompatibilityRequest(viewer_mapping, candidate_mapping)
        )
        if not isinstance(result, FixtureCompatibilityResult):
            raise TypeError("Compatibility provider must return an explicit fixture result.")
        return FixturePairEvaluation(
            PairEvaluationState.COMPATIBILITY_EVALUATED,
            viewer_id,
            candidate_id,
            eligibility=eligibility,
            compatibility=result,
        )
