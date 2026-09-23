"""Fail-closed pair eligibility from explicit, already-evaluated policy inputs.

No age threshold, preference range, identity verification, location algorithm,
or evidence validity is invented here. Their owning services supply decisions.
"""

from dataclasses import dataclass
from enum import Enum

from .identity import AccountId, require_nonblank


class PredicateOutcome(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class BlockState(Enum):
    CLEAR = "clear"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class Subject(Enum):
    VIEWER = "viewer"
    CANDIDATE = "candidate"
    PAIR = "pair"


class EligibilityRule(Enum):
    SELF = "self"
    ADULT = "adult"
    CONSENT = "consent"
    VERIFIED = "verified"
    ACTIVE = "active"
    COMPLETE = "complete"
    VISIBLE = "visible"
    MODERATION = "moderation"
    PREFERENCE = "preference"
    BLOCK = "block"


@dataclass(frozen=True)
class EligibilitySnapshot:
    account_id: AccountId
    snapshot_version: str
    adult: PredicateOutcome
    consent: PredicateOutcome
    verified: PredicateOutcome
    active: PredicateOutcome
    complete: PredicateOutcome
    visible: PredicateOutcome
    moderation: PredicateOutcome

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("EligibilitySnapshot requires an application AccountId.")
        require_nonblank(self.snapshot_version, "snapshot_version")
        if any(not isinstance(outcome, PredicateOutcome) for _, outcome in self.assessments()):
            raise TypeError("Every eligibility predicate requires an explicit outcome.")

    def assessments(self) -> tuple[tuple[EligibilityRule, PredicateOutcome], ...]:
        return (
            (EligibilityRule.ADULT, self.adult),
            (EligibilityRule.CONSENT, self.consent),
            (EligibilityRule.VERIFIED, self.verified),
            (EligibilityRule.ACTIVE, self.active),
            (EligibilityRule.COMPLETE, self.complete),
            (EligibilityRule.VISIBLE, self.visible),
            (EligibilityRule.MODERATION, self.moderation),
        )


@dataclass(frozen=True)
class PairPolicyInputs:
    policy_version: str
    viewer_accepts_candidate: PredicateOutcome
    candidate_accepts_viewer: PredicateOutcome
    viewer_blocks_candidate: BlockState
    candidate_blocks_viewer: BlockState

    def __post_init__(self) -> None:
        require_nonblank(self.policy_version, "policy_version")
        if not all(
            isinstance(value, PredicateOutcome)
            for value in (self.viewer_accepts_candidate, self.candidate_accepts_viewer)
        ):
            raise TypeError("Both preference directions require explicit outcomes.")
        if not all(
            isinstance(value, BlockState)
            for value in (self.viewer_blocks_candidate, self.candidate_blocks_viewer)
        ):
            raise TypeError("Both block directions require explicit states.")


@dataclass(frozen=True)
class EligibilityExclusion:
    subject: Subject
    rule: EligibilityRule
    outcome: PredicateOutcome


@dataclass(frozen=True)
class PairEligibility:
    viewer_id: AccountId
    candidate_id: AccountId
    viewer_snapshot_version: str
    candidate_snapshot_version: str
    policy_version: str
    exclusions: tuple[EligibilityExclusion, ...]

    @property
    def eligible(self) -> bool:
        return not self.exclusions


def evaluate_pair(
    viewer: EligibilitySnapshot,
    candidate: EligibilitySnapshot,
    policy: PairPolicyInputs,
) -> PairEligibility:
    exclusions: list[EligibilityExclusion] = []
    if viewer.account_id == candidate.account_id:
        exclusions.append(
            EligibilityExclusion(Subject.PAIR, EligibilityRule.SELF, PredicateOutcome.FAIL)
        )
    for subject, snapshot in ((Subject.VIEWER, viewer), (Subject.CANDIDATE, candidate)):
        for rule, outcome in snapshot.assessments():
            if outcome is not PredicateOutcome.PASS:
                exclusions.append(EligibilityExclusion(subject, rule, outcome))
    for subject, outcome in (
        (Subject.VIEWER, policy.viewer_accepts_candidate),
        (Subject.CANDIDATE, policy.candidate_accepts_viewer),
    ):
        if outcome is not PredicateOutcome.PASS:
            exclusions.append(EligibilityExclusion(subject, EligibilityRule.PREFERENCE, outcome))
    for subject, state in (
        (Subject.VIEWER, policy.viewer_blocks_candidate),
        (Subject.CANDIDATE, policy.candidate_blocks_viewer),
    ):
        if state is not BlockState.CLEAR:
            outcome = (
                PredicateOutcome.FAIL if state is BlockState.BLOCKED else PredicateOutcome.UNKNOWN
            )
            exclusions.append(EligibilityExclusion(subject, EligibilityRule.BLOCK, outcome))
    return PairEligibility(
        viewer.account_id,
        candidate.account_id,
        viewer.snapshot_version,
        candidate.snapshot_version,
        policy.policy_version,
        tuple(exclusions),
    )
