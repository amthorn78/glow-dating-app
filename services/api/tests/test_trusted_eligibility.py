"""Pair acquisition conformance under in-memory, non-atomic test substitutes."""

from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch

from glow_domain.eligibility import BlockState, EligibilityRule, PredicateOutcome, Subject
from glow_domain.identity import AccountId, EngineChartReference
from glow_domain.trusted_eligibility import (
    BoundPairPolicy,
    EligibilityDecisionState,
    EvidenceProblem,
    PairEligibilityEvidence,
    PairEvidenceVersion,
    PolicyReadiness,
    TrustedEligibilityService,
)
from tests.test_domain import policy, snapshot


def evidence():
    viewer = snapshot("viewer")
    candidate = snapshot("candidate")
    inputs = policy()
    version = PairEvidenceVersion(
        viewer.account_id,
        candidate.account_id,
        viewer.snapshot_version,
        candidate.snapshot_version,
        inputs.policy_version,
        "viewer-preference-v1",
        "candidate-preference-v1",
        "viewer-block-v1",
        "candidate-block-v1",
    )
    return PairEligibilityEvidence(
        viewer, candidate, BoundPairPolicy(version, inputs, PolicyReadiness.RESOLVED), version
    )


class RecordingEvidenceRepository:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def acquire(self, viewer_id, candidate_id):
        self.calls.append((viewer_id, candidate_id))
        return self.value


class TrustedEligibilityTests(TestCase):
    def setUp(self):
        self.evidence = evidence()
        self.repository = RecordingEvidenceRepository(self.evidence)
        self.service = TrustedEligibilityService(self.repository)
        self.viewer = AccountId("viewer")
        self.candidate = AccountId("candidate")

    def evaluate(self, expected=None):
        return self.service.evaluate(self.viewer, self.candidate, expected)

    def test_service_acquires_current_source_on_every_call_without_network(self):
        with patch("socket.socket", side_effect=AssertionError("No external calls allowed")):
            first = self.evaluate()
            second = self.evaluate(first.evidence_version)
        self.assertEqual(first.state, EligibilityDecisionState.READY)
        self.assertEqual(second.state, EligibilityDecisionState.READY)
        self.assertEqual(first.evidence_version, self.evidence.current_version)
        self.assertEqual(self.repository.calls, [(self.viewer, self.candidate)] * 2)

    def test_client_boolean_or_untyped_evidence_is_not_accepted(self):
        for expected in (True, False, {"eligible": True}, policy()):
            with self.subTest(expected=type(expected).__name__), self.assertRaises(TypeError):
                self.evaluate(expected)
        self.assertEqual(self.repository.calls, [])
        self.repository.value = {"trusted": True, "eligible": True}
        with self.assertRaises(TypeError):
            self.evaluate()

    def test_engine_identity_cannot_be_used_as_account(self):
        with self.assertRaises(TypeError):
            self.service.evaluate(EngineChartReference("viewer"), self.candidate)
        self.assertEqual(self.repository.calls, [])

    def test_missing_evidence_and_unresolved_policy_fail_closed(self):
        self.repository.value = None
        self.assertEqual(self.evaluate().problem, EvidenceProblem.MISSING_EVIDENCE)
        self.repository.value = replace(
            self.evidence,
            policy=replace(self.evidence.policy, readiness=PolicyReadiness.PENDING),
        )
        result = self.evaluate()
        self.assertEqual(result.state, EligibilityDecisionState.REJECTED)
        self.assertEqual(result.problem, EvidenceProblem.POLICY_PENDING)
        self.assertIsNone(result.eligibility)

    def test_both_snapshot_account_mismatches_and_reversed_pair_are_rejected(self):
        for field in ("viewer", "candidate"):
            with self.subTest(field=field):
                self.repository.value = replace(self.evidence, **{field: snapshot("stranger")})
                self.assertEqual(self.evaluate().problem, EvidenceProblem.WRONG_PAIR)
        self.repository.value = self.evidence
        result = self.service.evaluate(self.candidate, self.viewer)
        self.assertEqual(result.problem, EvidenceProblem.WRONG_PAIR)

    def test_policy_and_current_revision_vectors_are_both_pair_bound(self):
        wrong = replace(self.evidence.current_version, candidate_id=AccountId("stranger"))
        for value in (
            replace(self.evidence, policy=replace(self.evidence.policy, version=wrong)),
            replace(self.evidence, current_version=wrong),
        ):
            with self.subTest(value=value):
                self.repository.value = value
                self.assertEqual(self.evaluate().problem, EvidenceProblem.WRONG_PAIR)

    def test_wrong_pair_action_token_rejects_before_evidence_acquisition(self):
        wrong = replace(self.evidence.current_version, viewer_id=self.candidate)
        self.assertEqual(self.evaluate(wrong).problem, EvidenceProblem.WRONG_PAIR)
        self.assertEqual(self.repository.calls, [])

    def test_any_source_revision_change_invalidates_bound_policy(self):
        for field in (
            "viewer_snapshot_version",
            "candidate_snapshot_version",
            "policy_version",
            "viewer_preference_version",
            "candidate_preference_version",
            "viewer_block_version",
            "candidate_block_version",
        ):
            with self.subTest(field=field):
                self.repository.value = replace(
                    self.evidence,
                    current_version=replace(self.evidence.current_version, **{field: "changed"}),
                )
                result = self.evaluate()
                self.assertEqual(result.state, EligibilityDecisionState.RELOAD_REQUIRED)
                self.assertEqual(result.problem, EvidenceProblem.INCONSISTENT_VERSION)
                self.assertIsNone(result.eligibility)

    def test_snapshots_and_policy_must_match_their_revision_binding(self):
        values = [
            replace(
                self.evidence,
                **{field: replace(getattr(self.evidence, field), snapshot_version="unbound")},
            )
            for field in ("viewer", "candidate")
        ]
        values.append(
            replace(
                self.evidence,
                policy=replace(
                    self.evidence.policy,
                    inputs=replace(self.evidence.policy.inputs, policy_version="unbound"),
                ),
            )
        )
        for value in values:
            with self.subTest(value=value):
                self.repository.value = value
                self.assertEqual(self.evaluate().problem, EvidenceProblem.INCONSISTENT_VERSION)

    def test_stale_action_is_rejected_even_if_current_pair_remains_eligible(self):
        previous = self.evidence.current_version
        current = replace(previous, viewer_preference_version="preference-v2")
        self.repository.value = replace(
            self.evidence,
            current_version=current,
            policy=replace(self.evidence.policy, version=current),
        )
        result = self.evaluate(previous)
        self.assertTrue(result.eligibility.eligible)
        self.assertEqual(result.state, EligibilityDecisionState.RELOAD_REQUIRED)
        self.assertEqual(result.problem, EvidenceProblem.STALE_ACTION)
        self.assertEqual(self.evaluate(current).state, EligibilityDecisionState.READY)

    def test_withdrawn_consent_suspension_pause_deletion_invalidate_both_people(self):
        # The owning acquisition adapter maps actual lifecycle states to these
        # predicates and increments the snapshot version. These are fixture facts.
        for person, subject in (("viewer", Subject.VIEWER), ("candidate", Subject.CANDIDATE)):
            for state, predicate, rule in (
                ("withdrawn_consent", "consent", EligibilityRule.CONSENT),
                ("suspended", "moderation", EligibilityRule.MODERATION),
                ("paused", "visible", EligibilityRule.VISIBLE),
                ("deletion_pending", "active", EligibilityRule.ACTIVE),
                ("deleted", "active", EligibilityRule.ACTIVE),
            ):
                with self.subTest(person=person, state=state):
                    old_version = self.evidence.current_version
                    current = replace(old_version, **{f"{person}_snapshot_version": state})
                    changed = replace(
                        getattr(self.evidence, person),
                        snapshot_version=state,
                        **{predicate: PredicateOutcome.FAIL},
                    )
                    self.repository.value = replace(
                        self.evidence,
                        **{person: changed},
                        current_version=current,
                        policy=replace(self.evidence.policy, version=current),
                    )
                    result = self.evaluate(old_version)
                    self.assertEqual(result.state, EligibilityDecisionState.EXCLUDED)
                    self.assertEqual(result.eligibility.exclusions[0].subject, subject)
                    self.assertEqual(result.eligibility.exclusions[0].rule, rule)

    def test_all_unknown_safety_predicates_deny_both_people(self):
        for person in ("viewer", "candidate"):
            for predicate in (
                "adult",
                "consent",
                "verified",
                "active",
                "complete",
                "visible",
                "moderation",
            ):
                with self.subTest(person=person, predicate=predicate):
                    self.repository.value = replace(
                        self.evidence,
                        **{
                            person: replace(
                                getattr(self.evidence, person),
                                **{predicate: PredicateOutcome.UNKNOWN},
                            )
                        },
                    )
                    self.assertEqual(self.evaluate().state, EligibilityDecisionState.EXCLUDED)

    def test_preferences_and_blocks_are_checked_in_both_directions(self):
        for field, outcomes in (
            ("viewer_accepts_candidate", (PredicateOutcome.FAIL, PredicateOutcome.UNKNOWN)),
            ("candidate_accepts_viewer", (PredicateOutcome.FAIL, PredicateOutcome.UNKNOWN)),
            ("viewer_blocks_candidate", (BlockState.BLOCKED, BlockState.UNKNOWN)),
            ("candidate_blocks_viewer", (BlockState.BLOCKED, BlockState.UNKNOWN)),
        ):
            for outcome in outcomes:
                with self.subTest(field=field, outcome=outcome):
                    self.repository.value = replace(
                        self.evidence,
                        policy=replace(
                            self.evidence.policy,
                            inputs=replace(self.evidence.policy.inputs, **{field: outcome}),
                        ),
                    )
                    self.assertEqual(self.evaluate().state, EligibilityDecisionState.EXCLUDED)

    def test_unexpected_repository_errors_are_not_disguised_as_normal_exclusion(self):
        with patch.object(self.repository, "acquire", side_effect=RuntimeError("defect")):
            with self.assertRaisesRegex(RuntimeError, "defect"):
                self.evaluate()

    def test_revision_and_policy_types_reject_missing_decisions(self):
        with self.assertRaises(ValueError):
            replace(self.evidence.current_version, viewer_block_version="")
        with self.assertRaises(TypeError):
            replace(self.evidence.policy, readiness=True)
        with self.assertRaises(TypeError):
            replace(self.evidence, viewer={"eligible": True})
