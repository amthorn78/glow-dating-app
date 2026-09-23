"""Application-service tests with temporary test-only read repositories."""

from dataclasses import replace
from unittest import TestCase

from glow_domain.compatibility import CompatibilityStatus, FixtureCase, FixtureCompatibilityProvider
from glow_domain.eligibility import BlockState, PredicateOutcome, Subject
from glow_domain.identity import AccountId, ChartMapping, ChartMappingState, EngineChartReference
from glow_domain.pair_evaluation import (
    FixturePairEvaluationService,
    PairEvaluationState,
    RejectionReason,
)
from tests.test_domain import mapping, policy, provenance, snapshot


class ReadRepository:
    def __init__(self, values):
        self.values = values
        self.calls = []

    def get(self, account_id):
        self.calls.append(account_id)
        return self.values.get(account_id)


class RecordingFixtureProvider:
    def __init__(self):
        self.delegate = FixtureCompatibilityProvider(
            "test", FixtureCase.READY_SYNTHETIC, provenance()
        )
        self.calls = []
        self.error = None

    def evaluate_pair(self, request):
        self.calls.append(request)
        if self.error:
            raise self.error
        return self.delegate.evaluate_pair(request)


class PairEvaluationTests(TestCase):
    def setUp(self):
        self.viewer_id = AccountId("viewer")
        self.candidate_id = AccountId("candidate")
        self.snapshots = ReadRepository(
            {self.viewer_id: snapshot("viewer"), self.candidate_id: snapshot("candidate")}
        )
        self.mappings = ReadRepository(
            {
                self.viewer_id: mapping("viewer", "chart-v"),
                self.candidate_id: mapping("candidate", "chart-c"),
            }
        )
        self.provider = RecordingFixtureProvider()
        self.service = FixturePairEvaluationService(
            "test", self.snapshots, self.mappings, self.provider
        )

    def evaluate(self, inputs=None):
        return self.service.evaluate(
            self.viewer_id, self.candidate_id, policy() if inputs is None else inputs
        )

    def test_eligible_pair_resolves_by_app_id_and_returns_explicit_fixture_result(self):
        result = self.evaluate()
        self.assertEqual(result.state, PairEvaluationState.COMPATIBILITY_EVALUATED)
        self.assertEqual(result.mode, "fixture")
        self.assertTrue(result.eligibility.eligible)
        self.assertTrue(result.compatibility.synthetic)
        self.assertEqual(result.compatibility.status, CompatibilityStatus.READY)
        self.assertEqual(self.snapshots.calls, [self.viewer_id, self.candidate_id])
        self.assertEqual(self.mappings.calls, [self.viewer_id, self.candidate_id])
        self.assertEqual(len(self.provider.calls), 1)
        self.assertEqual(
            self.provider.calls[0].viewer.engine_reference, EngineChartReference("chart-v")
        )

    def test_all_safety_failures_and_unknowns_stop_before_mapping_or_provider_reads(self):
        for account_id in (self.viewer_id, self.candidate_id):
            for predicate in (
                "adult",
                "consent",
                "verified",
                "active",
                "complete",
                "visible",
                "moderation",
            ):
                for outcome in (PredicateOutcome.FAIL, PredicateOutcome.UNKNOWN):
                    with self.subTest(account_id=account_id, predicate=predicate, outcome=outcome):
                        original = self.snapshots.values[account_id]
                        self.snapshots.values[account_id] = replace(
                            original, **{predicate: outcome}
                        )
                        result = self.evaluate()
                        self.assertEqual(result.state, PairEvaluationState.EXCLUDED)
                        self.assertIsNone(result.compatibility)
                        self.assertEqual(self.mappings.calls, [])
                        self.assertEqual(self.provider.calls, [])
                        self.snapshots.values[account_id] = original

    def test_preference_unknowns_and_both_block_directions_stop_provider(self):
        cases = (
            ("viewer_accepts_candidate", PredicateOutcome.UNKNOWN),
            ("candidate_accepts_viewer", PredicateOutcome.FAIL),
            ("viewer_blocks_candidate", BlockState.UNKNOWN),
            ("candidate_blocks_viewer", BlockState.BLOCKED),
        )
        for field, value in cases:
            with self.subTest(field=field):
                self.assertEqual(
                    self.evaluate(replace(policy(), **{field: value})).state,
                    PairEvaluationState.EXCLUDED,
                )
                self.assertEqual(self.mappings.calls, [])
                self.assertEqual(self.provider.calls, [])

    def test_missing_or_mismatched_snapshots_reject_before_provider(self):
        for account_id, subject in (
            (self.viewer_id, Subject.VIEWER),
            (self.candidate_id, Subject.CANDIDATE),
        ):
            for value, reason in (
                (None, RejectionReason.MISSING_SNAPSHOT),
                (snapshot("wrong-account"), RejectionReason.SNAPSHOT_IDENTITY_MISMATCH),
            ):
                with self.subTest(account_id=account_id, reason=reason):
                    original = self.snapshots.values[account_id]
                    self.snapshots.values[account_id] = value
                    result = self.evaluate()
                    self.assertEqual(result.state, PairEvaluationState.REJECTED_INPUT)
                    self.assertEqual(result.rejection.reason, reason)
                    self.assertEqual(result.rejection.subject, subject)
                    self.assertEqual(self.provider.calls, [])
                    self.assertEqual(self.mappings.calls, [])
                    self.snapshots.values[account_id] = original

    def test_missing_or_wrong_account_mapping_never_reaches_provider(self):
        for account_id, subject in (
            (self.viewer_id, Subject.VIEWER),
            (self.candidate_id, Subject.CANDIDATE),
        ):
            for value, reason in (
                (None, RejectionReason.MISSING_MAPPING),
                (
                    mapping("wrong-account", "chart-other"),
                    RejectionReason.MAPPING_IDENTITY_MISMATCH,
                ),
            ):
                with self.subTest(account_id=account_id, reason=reason):
                    original = self.mappings.values[account_id]
                    self.mappings.values[account_id] = value
                    result = self.evaluate()
                    self.assertEqual(result.state, PairEvaluationState.REJECTED_INPUT)
                    self.assertEqual(result.rejection.reason, reason)
                    self.assertEqual(result.rejection.subject, subject)
                    self.assertEqual(self.provider.calls, [])
                    self.mappings.values[account_id] = original

    def test_pending_identity_stays_pending_without_provider_or_invented_provenance(self):
        for account_id in (self.viewer_id, self.candidate_id):
            with self.subTest(account_id=account_id):
                original = self.mappings.values[account_id]
                self.mappings.values[account_id] = ChartMapping(
                    account_id,
                    ChartMappingState.PENDING,
                    None,
                    "changed-input-v2",
                    "pending-map-v2",
                )
                result = self.evaluate()
                self.assertEqual(result.state, PairEvaluationState.PENDING_IDENTITY)
                self.assertTrue(result.eligibility.eligible)
                self.assertIsNone(result.compatibility)
                self.assertEqual(self.provider.calls, [])
                self.mappings.values[account_id] = original

    def test_repeated_requests_read_fresh_snapshots_and_mappings_without_cache(self):
        self.assertEqual(self.evaluate().state, PairEvaluationState.COMPATIBILITY_EVALUATED)
        active = self.snapshots.values[self.candidate_id]
        self.snapshots.values[self.candidate_id] = replace(active, active=PredicateOutcome.FAIL)
        self.assertEqual(self.evaluate().state, PairEvaluationState.EXCLUDED)
        self.assertEqual(len(self.provider.calls), 1)
        self.snapshots.values[self.candidate_id] = replace(active, snapshot_version="snapshot-v2")
        self.mappings.values[self.candidate_id] = replace(
            self.mappings.values[self.candidate_id],
            engine_reference=EngineChartReference("new-chart"),
            birth_input_version="new-input",
            mapping_version="new-map",
        )
        result = self.evaluate()
        self.assertEqual(result.eligibility.candidate_snapshot_version, "snapshot-v2")
        self.assertEqual(
            self.provider.calls[-1].candidate.engine_reference, EngineChartReference("new-chart")
        )
        self.assertEqual(self.snapshots.calls, [self.viewer_id, self.candidate_id] * 3)
        self.assertEqual(self.mappings.calls, [self.viewer_id, self.candidate_id] * 2)

    def test_typed_unavailable_result_is_preserved_and_exceptions_are_not_hidden(self):
        self.provider.delegate = FixtureCompatibilityProvider(
            "test", FixtureCase.UNAVAILABLE, provenance()
        )
        self.assertEqual(self.evaluate().compatibility.status, CompatibilityStatus.UNAVAILABLE)
        for error in (ValueError("programming issue"), RuntimeError("unexpected provider issue")):
            with self.subTest(error=type(error).__name__):
                self.provider.error = error
                with self.assertRaises(type(error)) as caught:
                    self.evaluate()
                self.assertIs(caught.exception, error)

    def test_runtime_wrong_types_are_programmer_errors_not_silent_unavailable(self):
        with self.assertRaises(TypeError):
            self.service.evaluate(EngineChartReference("viewer"), self.candidate_id, policy())
        with self.assertRaises(TypeError):
            self.service.evaluate(self.viewer_id, self.candidate_id, None)
        self.snapshots.values[self.viewer_id] = {"account_id": "viewer"}
        with self.assertRaises(TypeError):
            self.evaluate()
        self.assertEqual(self.provider.calls, [])

    def test_service_requires_explicit_fixture_environment(self):
        for environment in ("production", "staging", "", "dev", None):
            with self.subTest(environment=environment), self.assertRaises(ValueError):
                FixturePairEvaluationService(
                    environment, self.snapshots, self.mappings, self.provider
                )
        for environment in ("development", "test"):
            service = FixturePairEvaluationService(
                environment, self.snapshots, self.mappings, self.provider
            )
            self.assertEqual(
                service.evaluate(self.viewer_id, self.candidate_id, policy()).mode, "fixture"
            )
