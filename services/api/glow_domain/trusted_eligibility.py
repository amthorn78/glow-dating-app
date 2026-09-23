"""Server-owned eligibility acquisition and pair/version binding.

These internal types are not an HTTP input or an authentication mechanism.
Only the application composition root selects the evidence repository. There
is no production persistence adapter here; a conforming P11 adapter must read
authoritative state, not validate a client's assertion that it is trusted.
"""

from contextlib import AbstractContextManager
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .eligibility import EligibilitySnapshot, PairEligibility, PairPolicyInputs, evaluate_pair
from .identity import AccountId, require_nonblank


@dataclass(frozen=True)
class PairEvidenceVersion:
    """Directional revision vector, including negative block observations.

    Revisions are opaque equality tokens, never sorted or interpreted as time.
    Every relevant source change must invalidate its revision, including the
    first insertion of a block where no block row previously existed.
    """

    viewer_id: AccountId
    candidate_id: AccountId
    viewer_snapshot_version: str
    candidate_snapshot_version: str
    policy_version: str
    viewer_preference_version: str
    candidate_preference_version: str
    viewer_block_version: str
    candidate_block_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.viewer_id, AccountId) or not isinstance(
            self.candidate_id, AccountId
        ):
            raise TypeError("Evidence revisions require application AccountId values.")
        for name in (
            "viewer_snapshot_version",
            "candidate_snapshot_version",
            "policy_version",
            "viewer_preference_version",
            "candidate_preference_version",
            "viewer_block_version",
            "candidate_block_version",
        ):
            require_nonblank(getattr(self, name), name)

    def identifies(self, viewer_id: AccountId, candidate_id: AccountId) -> bool:
        return (self.viewer_id, self.candidate_id) == (viewer_id, candidate_id)


class PolicyReadiness(Enum):
    RESOLVED = "resolved"
    PENDING = "pending"


@dataclass(frozen=True)
class BoundPairPolicy:
    version: PairEvidenceVersion
    inputs: PairPolicyInputs
    readiness: PolicyReadiness

    def __post_init__(self) -> None:
        if not isinstance(self.version, PairEvidenceVersion):
            raise TypeError("Policy inputs require explicit pair/version binding.")
        if not isinstance(self.inputs, PairPolicyInputs):
            raise TypeError("Policy inputs must be typed internal decisions.")
        if not isinstance(self.readiness, PolicyReadiness):
            raise TypeError("Policy readiness must be explicit.")


@dataclass(frozen=True)
class PairEligibilityEvidence:
    viewer: EligibilitySnapshot
    candidate: EligibilitySnapshot
    policy: BoundPairPolicy
    current_version: PairEvidenceVersion

    def __post_init__(self) -> None:
        if not isinstance(self.viewer, EligibilitySnapshot) or not isinstance(
            self.candidate, EligibilitySnapshot
        ):
            raise TypeError("Evidence requires both typed account snapshots.")
        if not isinstance(self.policy, BoundPairPolicy) or not isinstance(
            self.current_version, PairEvidenceVersion
        ):
            raise TypeError("Evidence requires policy binding and current source revisions.")


class EligibilityEvidenceRepository(Protocol):
    def acquire(
        self, viewer_id: AccountId, candidate_id: AccountId
    ) -> PairEligibilityEvidence | None:
        """Read server-owned state and evaluate the currently selected policy.

        Never deserialize supplied eligibility booleans, a saved result or a
        client's current_version as authoritative evidence. None means source
        data is missing; unavailable dependencies must not produce PASS.
        """
        ...


class EligibilityDecisionState(Enum):
    READY = "ready"
    EXCLUDED = "excluded"
    RELOAD_REQUIRED = "reload_required"
    REJECTED = "rejected"


class EvidenceProblem(Enum):
    MISSING_EVIDENCE = "missing_evidence"
    WRONG_PAIR = "wrong_pair"
    INCONSISTENT_VERSION = "inconsistent_version"
    POLICY_PENDING = "policy_pending"
    STALE_ACTION = "stale_action"


@dataclass(frozen=True)
class EligibilityDecision:
    state: EligibilityDecisionState
    eligibility: PairEligibility | None = None
    evidence_version: PairEvidenceVersion | None = None
    problem: EvidenceProblem | None = None


@dataclass(frozen=True)
class TrustedEligibilityService:
    repository: EligibilityEvidenceRepository

    def evaluate(
        self,
        viewer_id: AccountId,
        candidate_id: AccountId,
        expected: PairEvidenceVersion | None = None,
    ) -> EligibilityDecision:
        """Acquire and evaluate afresh; expected is only a rejection condition.

        READY permits continuing the bounded discovery/interaction workflow.
        It is never an authentication, mutual-match or send authorization.
        Privileged writes additionally require their action-specific rules and
        the transaction contract below. No retry or side effect is performed.
        """
        if not isinstance(viewer_id, AccountId) or not isinstance(candidate_id, AccountId):
            raise TypeError("Eligibility requires application AccountId values.")
        if expected is not None:
            if not isinstance(expected, PairEvidenceVersion):
                raise TypeError("Expected eligibility version must be typed, never a boolean.")
            if not expected.identifies(viewer_id, candidate_id):
                return EligibilityDecision(
                    EligibilityDecisionState.REJECTED, problem=EvidenceProblem.WRONG_PAIR
                )

        evidence = self.repository.acquire(viewer_id, candidate_id)
        if evidence is None:
            return EligibilityDecision(
                EligibilityDecisionState.REJECTED, problem=EvidenceProblem.MISSING_EVIDENCE
            )
        if not isinstance(evidence, PairEligibilityEvidence):
            raise TypeError("Evidence repository returned an unexpected type.")
        bound = evidence.policy.version
        current = evidence.current_version
        if (
            evidence.viewer.account_id != viewer_id
            or evidence.candidate.account_id != candidate_id
            or not bound.identifies(viewer_id, candidate_id)
            or not current.identifies(viewer_id, candidate_id)
        ):
            return EligibilityDecision(
                EligibilityDecisionState.REJECTED, problem=EvidenceProblem.WRONG_PAIR
            )
        if (
            bound != current
            or bound.viewer_snapshot_version != evidence.viewer.snapshot_version
            or bound.candidate_snapshot_version != evidence.candidate.snapshot_version
            or bound.policy_version != evidence.policy.inputs.policy_version
        ):
            return EligibilityDecision(
                EligibilityDecisionState.RELOAD_REQUIRED,
                problem=EvidenceProblem.INCONSISTENT_VERSION,
            )
        if evidence.policy.readiness is not PolicyReadiness.RESOLVED:
            return EligibilityDecision(
                EligibilityDecisionState.REJECTED, problem=EvidenceProblem.POLICY_PENDING
            )
        eligibility = evaluate_pair(evidence.viewer, evidence.candidate, evidence.policy.inputs)
        if not eligibility.eligible:
            return EligibilityDecision(EligibilityDecisionState.EXCLUDED, eligibility, current)
        if expected is not None and expected != current:
            return EligibilityDecision(
                EligibilityDecisionState.RELOAD_REQUIRED,
                eligibility,
                current,
                EvidenceProblem.STALE_ACTION,
            )
        return EligibilityDecision(EligibilityDecisionState.READY, eligibility, current)


class PairActionTransaction(EligibilityEvidenceRepository, Protocol):
    """Future single application transaction; no implementation or SQL proof.

    acquire reads current predicates and revisions under the same protected
    boundary as the staged action and outbox. Other domain repositories within
    this unit own action-specific staging, actor/session and match checks.
    """

    def commit_if_current(self, expected: PairEvidenceVersion) -> bool:
        """Atomically compare all revisions and commit staged state plus outbox.

        False must roll back everything; no provider work may run beforehand.
        An implementation must also prevent concurrent insertions/changes of
        absent block and relationship rows from escaping the comparison.
        """
        ...


class PairActionUnitOfWork(Protocol):
    def begin_pair_action(
        self, viewer_id: AccountId, candidate_id: AccountId
    ) -> AbstractContextManager[PairActionTransaction]:
        """Rollback on exception or exit without a successful checked commit."""
        ...
