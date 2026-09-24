"""Pure-domain safety/identity tests; no Django setup, SQL or provider access."""

from dataclasses import FrozenInstanceError, asdict, replace
from unittest import TestCase
from unittest.mock import patch

from glow_domain.compatibility import (
    PORT_VERSION,
    CompatibilityRequest,
    CompatibilityStatus,
    FixtureCase,
    FixtureCompatibilityProvider,
    FixtureCompatibilityResult,
    FixtureProvenance,
    SymmetryGuarantee,
    fixture_cache_key,
)
from glow_domain.eligibility import (
    BlockState,
    EligibilityRule,
    EligibilitySnapshot,
    PairPolicyInputs,
    PredicateOutcome,
    Subject,
    evaluate_pair,
)
from glow_domain.identity import AccountId, ChartMapping, ChartMappingState, EngineChartReference
from glow_domain.ports import FixtureCompatibilityPort


def snapshot(account: str) -> EligibilitySnapshot:
    return EligibilitySnapshot(
        AccountId(account),
        "synthetic-snapshot-v1",
        PredicateOutcome.PASS,
        PredicateOutcome.PASS,
        PredicateOutcome.PASS,
        PredicateOutcome.PASS,
        PredicateOutcome.PASS,
        PredicateOutcome.PASS,
        PredicateOutcome.PASS,
    )


def policy() -> PairPolicyInputs:
    return PairPolicyInputs(
        "synthetic-policy-v1",
        PredicateOutcome.PASS,
        PredicateOutcome.PASS,
        BlockState.CLEAR,
        BlockState.CLEAR,
    )


def mapping(account: str, engine: str) -> ChartMapping:
    return ChartMapping(
        AccountId(account),
        ChartMappingState.RESOLVED,
        EngineChartReference(engine),
        "synthetic-birth-input-v1",
        "synthetic-mapping-v1",
    )


def provenance() -> FixtureProvenance:
    return FixtureProvenance(
        "synthetic-fixtures-v1",
        "synthetic-adapter-v1",
        "synthetic-engine-v1",
        "synthetic-engine-contract-v1",
    )


class EligibilityTests(TestCase):
    def test_all_explicit_predicates_pass_without_implying_match_or_auth(self):
        result = evaluate_pair(snapshot("viewer"), snapshot("candidate"), policy())
        self.assertTrue(result.eligible)
        self.assertEqual(result.exclusions, ())
        self.assertEqual(result.policy_version, "synthetic-policy-v1")
        self.assertEqual(result.viewer_snapshot_version, "synthetic-snapshot-v1")
        self.assertFalse(hasattr(result, "match"))
        self.assertFalse(hasattr(result, "token"))

    def test_every_failed_or_unknown_safety_predicate_excludes_either_person(self):
        for subject in (Subject.VIEWER, Subject.CANDIDATE):
            for field in (
                "adult",
                "consent",
                "verified",
                "active",
                "complete",
                "visible",
                "moderation",
            ):
                for outcome in (PredicateOutcome.FAIL, PredicateOutcome.UNKNOWN):
                    with self.subTest(subject=subject, field=field, outcome=outcome):
                        viewer, candidate = snapshot("viewer"), snapshot("candidate")
                        if subject is Subject.VIEWER:
                            viewer = replace(viewer, **{field: outcome})
                        else:
                            candidate = replace(candidate, **{field: outcome})
                        result = evaluate_pair(viewer, candidate, policy())
                        self.assertFalse(result.eligible)
                        self.assertEqual(len(result.exclusions), 1)
                        self.assertEqual(result.exclusions[0].subject, subject)
                        self.assertEqual(result.exclusions[0].rule, EligibilityRule(field))
                        self.assertEqual(result.exclusions[0].outcome, outcome)

    def test_reciprocal_preferences_require_both_directions_explicitly(self):
        for field in ("viewer_accepts_candidate", "candidate_accepts_viewer"):
            for outcome in (PredicateOutcome.FAIL, PredicateOutcome.UNKNOWN):
                with self.subTest(field=field, outcome=outcome):
                    result = evaluate_pair(
                        snapshot("viewer"),
                        snapshot("candidate"),
                        replace(policy(), **{field: outcome}),
                    )
                    self.assertFalse(result.eligible)
                    self.assertEqual(result.exclusions[0].rule, EligibilityRule.PREFERENCE)

    def test_either_direction_block_or_unknown_block_state_overrides_other_passes(self):
        for field in ("viewer_blocks_candidate", "candidate_blocks_viewer"):
            for state in (BlockState.BLOCKED, BlockState.UNKNOWN):
                with self.subTest(field=field, state=state):
                    result = evaluate_pair(
                        snapshot("viewer"),
                        snapshot("candidate"),
                        replace(policy(), **{field: state}),
                    )
                    self.assertFalse(result.eligible)
                    self.assertEqual(result.exclusions[0].rule, EligibilityRule.BLOCK)

    def test_self_and_multiple_exclusions_are_deterministic(self):
        viewer = replace(snapshot("same"), adult=PredicateOutcome.UNKNOWN)
        candidate = replace(snapshot("same"), active=PredicateOutcome.FAIL)
        inputs = replace(policy(), candidate_blocks_viewer=BlockState.BLOCKED)
        result = evaluate_pair(viewer, candidate, inputs)
        self.assertEqual(result, evaluate_pair(viewer, candidate, inputs))
        self.assertEqual(
            tuple((exclusion.subject, exclusion.rule) for exclusion in result.exclusions),
            (
                (Subject.PAIR, EligibilityRule.SELF),
                (Subject.VIEWER, EligibilityRule.ADULT),
                (Subject.CANDIDATE, EligibilityRule.ACTIVE),
                (Subject.CANDIDATE, EligibilityRule.BLOCK),
            ),
        )

    def test_missing_typed_decisions_cannot_be_interpreted_as_permission(self):
        with self.assertRaises(TypeError):
            replace(snapshot("viewer"), adult=True)
        with self.assertRaises(TypeError):
            replace(policy(), viewer_accepts_candidate="pass")
        with self.assertRaises(TypeError):
            replace(policy(), candidate_blocks_viewer=None)


class IdentityAndCacheTests(TestCase):
    def test_account_and_engine_identity_remain_distinct_even_with_same_value(self):
        self.assertNotEqual(AccountId("same-value"), EngineChartReference("same-value"))
        self.assertEqual(AccountId(" opaque value ").value, " opaque value ")
        with self.assertRaises(ValueError):
            replace(mapping("app-id", "engine-id"), engine_reference=AccountId("app-id"))
        with self.assertRaises(ValueError):
            replace(mapping("app-id", "engine-id"), engine_reference=None)

    def test_pending_mapping_has_no_engine_identity_and_cannot_be_cached(self):
        pending = ChartMapping(
            AccountId("viewer"), ChartMappingState.PENDING, None, "input-v2", "map-v2"
        )
        request = CompatibilityRequest(
            pending, mapping("candidate", "chart-candidate"), policy().policy_version
        )
        with self.assertRaises(ValueError):
            fixture_cache_key(request, provenance())
        with self.assertRaises(ValueError):
            replace(pending, engine_reference=EngineChartReference("invented-chart"))

    def test_cache_preserves_direction_without_a_specific_guarantee(self):
        viewer, candidate = mapping("viewer", "chart-v"), mapping("candidate", "chart-c")
        self.assertNotEqual(
            fixture_cache_key(
                CompatibilityRequest(viewer, candidate, policy().policy_version), provenance()
            ),
            fixture_cache_key(
                CompatibilityRequest(candidate, viewer, policy().policy_version), provenance()
            ),
        )

    def test_declared_symmetry_is_bound_to_engine_and_contract_versions(self):
        viewer, candidate = mapping("viewer", "chart-v"), mapping("candidate", "chart-c")
        guarantee = SymmetryGuarantee(
            "synthetic-engine-v1", "synthetic-engine-contract-v1", "synthetic-test-case-only"
        )
        self.assertEqual(
            fixture_cache_key(
                CompatibilityRequest(viewer, candidate, policy().policy_version),
                provenance(),
                guarantee,
            ),
            fixture_cache_key(
                CompatibilityRequest(candidate, viewer, policy().policy_version),
                provenance(),
                guarantee,
            ),
        )
        for field in ("simulated_engine_version", "simulated_engine_contract_version"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                fixture_cache_key(
                    CompatibilityRequest(viewer, candidate, policy().policy_version),
                    provenance(),
                    replace(guarantee, **{field: "different-version"}),
                )

    def test_cache_changes_with_every_identity_and_provenance_revision(self):
        request = CompatibilityRequest(
            mapping("viewer", "chart-v"), mapping("candidate", "chart-c"), policy().policy_version
        )
        baseline = fixture_cache_key(request, provenance())
        self.assertNotEqual(
            baseline,
            fixture_cache_key(replace(request, eligibility_policy_version="changed"), provenance()),
        )
        for field, value in (
            ("account_id", AccountId("changed-account")),
            ("engine_reference", EngineChartReference("changed-chart")),
            ("birth_input_version", "changed-input"),
            ("mapping_version", "changed-map"),
        ):
            for side in ("viewer", "candidate"):
                with self.subTest(side=side, field=field):
                    changed = replace(
                        request, **{side: replace(getattr(request, side), **{field: value})}
                    )
                    self.assertNotEqual(baseline, fixture_cache_key(changed, provenance()))
        for field in (
            "fixture_set_version",
            "adapter_version",
            "simulated_engine_version",
            "simulated_engine_contract_version",
        ):
            with self.subTest(field=field):
                self.assertNotEqual(
                    baseline,
                    fixture_cache_key(request, replace(provenance(), **{field: "changed"})),
                )
        self.assertEqual(asdict(baseline)["provenance"]["source"], "fixture")
        self.assertEqual(asdict(baseline)["provenance"]["port_version"], PORT_VERSION)

    def test_compatibility_requires_explicit_policy_and_immutable_mappings(self):
        request = CompatibilityRequest(
            mapping("viewer", "chart-v"), mapping("candidate", "chart-c"), policy().policy_version
        )
        for changes in (
            {"viewer": "viewer"},
            {"candidate": {"account_id": "candidate"}},
            {"eligibility_policy_version": None},
            {"eligibility_policy_version": " "},
        ):
            with self.subTest(changes=changes), self.assertRaises((TypeError, ValueError)):
                replace(request, **changes)

    def test_domain_dtos_are_immutable(self):
        for dto, field, value in (
            (AccountId("viewer"), "value", "changed"),
            (snapshot("viewer"), "adult", PredicateOutcome.PASS),
            (mapping("viewer", "chart-v"), "mapping_version", "changed"),
            (provenance(), "source", "engine"),
            (
                CompatibilityRequest(
                    mapping("viewer", "chart-v"),
                    mapping("candidate", "chart-c"),
                    policy().policy_version,
                ),
                "eligibility_policy_version",
                "changed",
            ),
        ):
            with self.subTest(dto=type(dto).__name__), self.assertRaises(FrozenInstanceError):
                setattr(dto, field, value)


class FixtureProviderTests(TestCase):
    def test_all_declared_states_are_deterministic_synthetic_and_have_no_scores(self):
        request = CompatibilityRequest(
            mapping("viewer", "chart-v"), mapping("candidate", "chart-c"), policy().policy_version
        )
        for case, expected in (
            (FixtureCase.PENDING, CompatibilityStatus.PENDING),
            (FixtureCase.UNAVAILABLE, CompatibilityStatus.UNAVAILABLE),
            (FixtureCase.UNSUPPORTED, CompatibilityStatus.UNSUPPORTED),
            (FixtureCase.READY_SYNTHETIC, CompatibilityStatus.READY),
        ):
            with (
                self.subTest(case=case),
                patch("socket.socket", side_effect=AssertionError("network")),
            ):
                provider: FixtureCompatibilityPort = FixtureCompatibilityProvider(
                    "test", case, provenance()
                )
                result = provider.evaluate_pair(request)
                self.assertEqual(result, provider.evaluate_pair(request))
                self.assertEqual(result.status, expected)
                self.assertTrue(result.synthetic)
                self.assertEqual(result.provenance.source, "fixture")
                self.assertFalse(hasattr(result, "band"))
                self.assertFalse(hasattr(result, "score"))

    def test_ready_requires_explicit_synthetic_case_and_resolved_pair(self):
        with self.assertRaises(ValueError):
            FixtureCompatibilityResult(CompatibilityStatus.READY, FixtureCase.PENDING, provenance())
        request = CompatibilityRequest(
            ChartMapping(
                AccountId("viewer"), ChartMappingState.PENDING, None, "input-v1", "map-v1"
            ),
            mapping("candidate", "chart-c"),
            policy().policy_version,
        )
        provider = FixtureCompatibilityProvider("test", FixtureCase.READY_SYNTHETIC, provenance())
        self.assertEqual(provider.evaluate_pair(request).status, CompatibilityStatus.PENDING)

    def test_provider_has_no_live_environment_or_implicit_case(self):
        for environment in ("production", "staging", "", "dev"):
            with self.subTest(environment=environment), self.assertRaises(ValueError):
                FixtureCompatibilityProvider(environment, FixtureCase.READY_SYNTHETIC, provenance())
        with self.assertRaises(TypeError):
            FixtureCompatibilityProvider("test", "ready", provenance())
