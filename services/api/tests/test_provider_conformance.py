"""Reusable app-side fixture cases. P11 must adapt them to the supported provider.

No database, socket, HDE, real birth detail or provider credential is used.
"""

from dataclasses import asdict, replace
from datetime import UTC, date, datetime, time
from unittest import TestCase
from unittest.mock import patch

from glow_domain.compatibility import (
    CompatibilityRequest,
    FixtureCase,
    FixtureCompatibilityProvider,
    fixture_cache_key,
)
from glow_domain.eligibility import PredicateOutcome
from glow_domain.identity import AccountId, ChartMappingState
from glow_domain.provider_contracts import (
    BirthInput,
    BoundCompatibilityResult,
    ChartResolutionState,
    CompatibilityOutcome,
    ExpectedProviderFailure,
    FailureCode,
    LifecycleRequest,
    MappingOutboxEvent,
    MappingWrite,
    RetryPolicy,
    TimePrecision,
    evaluate_with_retry,
    project_fixture_compatibility,
)
from glow_domain.provider_fixtures import (
    CandidateWork,
    FixtureAccountMappingState,
    FixtureChartResolver,
    FixtureCompatibilityBatchService,
    FixtureEngineLifecycle,
    FixtureMappingUnitOfWork,
    ScriptedCompatibilityProvider,
)
from glow_domain.trusted_eligibility import (
    BoundPairPolicy,
    PairEligibilityEvidence,
    PairEvidenceVersion,
    PolicyReadiness,
    TrustedEligibilityService,
)
from tests.test_domain import mapping, policy, provenance, snapshot


def birth_input():
    return BirthInput(
        AccountId("viewer"),
        "synthetic-birth-input-v1",
        date(1990, 1, 1),
        time(12, 34),
        TimePrecision.KNOWN,
        "Synthetic city; no real subject",
        "Etc/UTC",
        "explicit-synthetic-zone-fixture",
        "synthetic-consent-v1",
        True,
    )


def request():
    return CompatibilityRequest(mapping("viewer", "fixture-chart-a"), mapping("candidate", "b"))


class NoNetworkCase(TestCase):
    def setUp(self):
        guard = patch("socket.socket", side_effect=AssertionError("Network is forbidden."))
        guard.start()
        self.addCleanup(guard.stop)


class BirthAndChartConformanceTests(NoNetworkCase):
    def resolver(self, state=ChartResolutionState.RESOLVED, supplied=None):
        return FixtureChartResolver(
            "test", state, provenance(), supplied or mapping("viewer", "fixture-chart-a")
        )

    def test_civil_facts_preserved_and_private_repr(self):
        value = birth_input()
        self.assertEqual(value.local_time, time(12, 34))
        self.assertEqual(value.birth_date, date(1990, 1, 1))
        self.assertEqual(value.timezone_name, "Etc/UTC")
        for private in ("1990", "12, 34", "Synthetic city", "Etc/UTC"):
            self.assertNotIn(private, repr(value))

    def test_malformed_birth_input_rejected_without_normalization(self):
        for kwargs in (
            {"account_id": "viewer"},
            {"birth_date": datetime(1990, 1, 1)},
            {"birth_date": "1990-01-01"},
            {"local_time": time(12, 34, tzinfo=UTC)},
            {"local_time": None},
            {"local_time": "12:34"},
            {"time_precision": "known"},
            {"time_precision": TimePrecision.UNKNOWN},
            {"place_label": "   "},
            {"place_label": "\ud800"},
            {"timezone_name": None},
            {"timezone_provenance": None},
            {"consent_granted": 1},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises((TypeError, ValueError)):
                replace(birth_input(), **kwargs)

    def test_unknown_approximate_or_timezone_missing_is_ambiguous(self):
        inputs = (
            replace(birth_input(), local_time=None, time_precision=TimePrecision.UNKNOWN),
            replace(birth_input(), time_precision=TimePrecision.APPROXIMATE),
            replace(birth_input(), timezone_name=None, timezone_provenance=None),
        )
        for value in inputs:
            result = self.resolver().resolve(value, value.input_version, "resolve-1")
            self.assertEqual(result.state, ChartResolutionState.AMBIGUOUS)
            self.assertIsNone(result.mapping)

    def test_pending_unavailable_unsupported_do_not_invent_chart(self):
        for state in (
            ChartResolutionState.PENDING,
            ChartResolutionState.UNAVAILABLE,
            ChartResolutionState.UNSUPPORTED,
        ):
            value = birth_input()
            result = self.resolver(state).resolve(value, value.input_version, "resolve-1")
            self.assertEqual(result.state, state)
            self.assertIsNone(result.mapping)

    def test_only_explicit_matching_mapping_can_resolve(self):
        value = birth_input()
        result = self.resolver().resolve(value, value.input_version, "resolve-1")
        self.assertEqual(result.mapping.engine_reference.value, "fixture-chart-a")
        for supplied in (
            mapping("another-account", "fixture-chart-a"),
            replace(mapping("viewer", "fixture-chart-a"), birth_input_version="old"),
        ):
            with self.assertRaises(ValueError):
                self.resolver(supplied=supplied).resolve(value, value.input_version, "resolve-1")
        with self.assertRaises(ValueError):
            FixtureChartResolver("test", ChartResolutionState.RESOLVED, provenance()).resolve(
                value, value.input_version, "resolve-1"
            )

    def test_replay_is_idempotent_changed_input_conflicts_and_stale_result_revokes(self):
        resolver, value = self.resolver(), birth_input()
        first = resolver.resolve(value, value.input_version, "resolve-1")
        self.assertEqual(first, resolver.resolve(value, value.input_version, "resolve-1"))
        with self.assertRaises(ExpectedProviderFailure) as error:
            resolver.resolve(
                replace(value, place_label="Changed city"), value.input_version, "resolve-1"
            )
        self.assertEqual(error.exception.code, FailureCode.IDEMPOTENCY_CONFLICT)
        self.assertEqual(
            resolver.resolve(value, "new-input-version", "resolve-1").state,
            ChartResolutionState.STALE,
        )
        self.assertEqual(
            resolver.resolve(
                replace(value, consent_granted=False), value.input_version, "resolve-1"
            ).state,
            ChartResolutionState.CONSENT_REQUIRED,
        )


class CompatibilityConformanceCases:
    """Adapter factory seam for rerunning expected output/failure cases at P11.

    A future live adapter needs authorized sandbox scenarios and supported
    contract mappings; inheriting this mixin alone supplies none of those rights.
    """

    def provider(self, script):
        raise NotImplementedError

    def test_bounded_retry_preserves_request_and_idempotency(self):
        provider = self.provider((FailureCode.TIMEOUT, FailureCode.OUTAGE, FixtureCase.PENDING))
        result = evaluate_with_retry(provider, request(), provenance(), "pair-1", RetryPolicy(3))
        self.assertEqual(result.attempts, 3)
        self.assertIsNone(result.failure)
        again = evaluate_with_retry(provider, request(), provenance(), "pair-1", RetryPolicy(3))
        self.assertEqual(result.output, again.output)

    def test_retry_exhaustion_and_unsupported_do_not_become_ready(self):
        for code, attempts in (
            (FailureCode.TIMEOUT, 3),
            (FailureCode.OUTAGE, 3),
            (FailureCode.UNSUPPORTED, 1),
        ):
            result = evaluate_with_retry(
                self.provider((code,)), request(), provenance(), "pair-1", RetryPolicy(3)
            )
            self.assertEqual(result.attempts, attempts)
            self.assertEqual(result.failure, code)
            self.assertIsNone(result.output)

    def test_changed_direction_or_input_cannot_reuse_idempotency(self):
        provider = self.provider((FixtureCase.READY_SYNTHETIC,))
        evaluate_with_retry(provider, request(), provenance(), "pair-1", RetryPolicy(1))
        for changed in (
            CompatibilityRequest(request().candidate, request().viewer),
            replace(request(), candidate=replace(request().candidate, birth_input_version="v2")),
        ):
            result = evaluate_with_retry(provider, changed, provenance(), "pair-1", RetryPolicy(1))
            self.assertEqual(result.failure, FailureCode.IDEMPOTENCY_CONFLICT)


class FixtureCompatibilityConformanceTests(CompatibilityConformanceCases, NoNetworkCase):
    def provider(self, script):
        return ScriptedCompatibilityProvider("test", provenance(), script)

    def test_retry_bounds(self):
        for attempts in (0, 4, -1, True, 1.5):
            with self.assertRaises(ValueError):
                RetryPolicy(attempts)

    def test_unexpected_programming_error_propagates(self):
        class Defect:
            def evaluate(self, request, idempotency_key):
                raise RuntimeError("deliberate fixture programming defect")

        with self.assertRaises(RuntimeError):
            evaluate_with_retry(Defect(), request(), provenance(), "pair-1", RetryPolicy(3))

    def test_malformed_typed_failure_is_distinct_from_undeclared_adapter_type(self):
        typed = evaluate_with_retry(
            self.provider((FailureCode.MALFORMED_OUTPUT,)),
            request(),
            provenance(),
            "pair-1",
            RetryPolicy(3),
        )
        self.assertEqual(typed.failure, FailureCode.MALFORMED_OUTPUT)
        self.assertEqual(typed.attempts, 1)

        class MalformedAdapter:
            def evaluate(self, request, idempotency_key):
                return {"score": 0.9}

        with self.assertRaises(TypeError):
            evaluate_with_retry(
                MalformedAdapter(), request(), provenance(), "pair-1", RetryPolicy(1)
            )

    def test_output_binding_rejects_wrong_pair_version_and_provenance(self):
        variations = (
            (
                CompatibilityRequest(request().candidate, request().viewer),
                provenance(),
                FailureCode.IDENTITY_MISMATCH,
            ),
            (
                replace(request(), viewer=replace(request().viewer, mapping_version="v2")),
                provenance(),
                FailureCode.STALE,
            ),
            (
                request(),
                replace(provenance(), simulated_engine_contract_version="new"),
                FailureCode.UNSUPPORTED,
            ),
        )
        for wrong_request, wrong_provenance, code in variations:
            result = FixtureCompatibilityProvider(
                "test", FixtureCase.READY_SYNTHETIC, wrong_provenance
            ).evaluate_pair(wrong_request)

            class WrongOutput:
                def evaluate(
                    self,
                    incoming,
                    idempotency_key,
                    wrong_request=wrong_request,
                    wrong_provenance=wrong_provenance,
                    result=result,
                ):
                    return BoundCompatibilityResult(
                        fixture_cache_key(wrong_request, wrong_provenance), result
                    )

            outcome = evaluate_with_retry(
                WrongOutput(), request(), provenance(), "pair-1", RetryPolicy(1)
            )
            self.assertEqual(outcome.failure, code)

    def test_projection_is_closed_numeric_free_and_stale_aware(self):
        result = evaluate_with_retry(
            self.provider((FixtureCase.READY_SYNTHETIC,)),
            request(),
            provenance(),
            "pair-1",
            RetryPolicy(1),
        )
        key = fixture_cache_key(request(), provenance())
        self.assertEqual(
            asdict(project_fixture_compatibility(result, key)),
            {"status": "pending", "source": "fixture"},
        )
        for changed in (
            replace(request(), viewer=replace(request().viewer, birth_input_version="v2")),
            replace(request(), candidate=replace(request().candidate, mapping_version="v2")),
            CompatibilityRequest(request().candidate, request().viewer),
        ):
            self.assertEqual(
                project_fixture_compatibility(
                    result, fixture_cache_key(changed, provenance())
                ).status,
                "stale",
            )


class EvidenceRepository:
    def __init__(self):
        self.excluded = set()
        self.version = "synthetic-snapshot-v1"
        self.calls = []

    def acquire(self, viewer_id, candidate_id):
        self.calls.append((viewer_id, candidate_id))
        viewer = replace(snapshot(viewer_id.value), snapshot_version=self.version)
        candidate = replace(snapshot(candidate_id.value), snapshot_version=self.version)
        if candidate_id.value in self.excluded:
            candidate = replace(candidate, visible=PredicateOutcome.FAIL)
        version = PairEvidenceVersion(
            viewer_id,
            candidate_id,
            self.version,
            self.version,
            policy().policy_version,
            "vp1",
            "cp1",
            "vb1",
            "cb1",
        )
        return PairEligibilityEvidence(
            viewer, candidate, BoundPairPolicy(version, policy(), PolicyReadiness.RESOLVED), version
        )


class MappingRepository:
    def __init__(self):
        self.items = {
            name: mapping(name, f"explicit-fixture-chart-{name}")
            for name in ("viewer", "candidate", "another")
        }
        self.calls = []

    def get(self, account_id):
        self.calls.append(account_id)
        return self.items.get(account_id.value)


class BatchConformanceTests(NoNetworkCase):
    def setUp(self):
        super().setUp()
        self.evidence = EvidenceRepository()
        self.mappings = MappingRepository()
        self.provider = ScriptedCompatibilityProvider("test", provenance(), (FixtureCase.PENDING,))

    def service(self, provider=None):
        return FixtureCompatibilityBatchService(
            "test",
            TrustedEligibilityService(self.evidence),
            self.mappings,
            provider or self.provider,
            provenance(),
            RetryPolicy(3),
        )

    def test_empty_or_ineligible_candidates_never_reach_mapping_or_provider(self):
        empty = self.service().evaluate(AccountId("viewer"), ())
        self.assertEqual(empty.state, "empty")
        self.evidence.excluded.add("candidate")
        result = self.service().evaluate(
            AccountId("viewer"), (CandidateWork(AccountId("candidate"), "pair-1"),)
        )
        self.assertEqual(result.state, "empty")
        self.assertEqual(self.mappings.calls, [])
        self.assertEqual(self.provider.calls, 0)

    def test_missing_mismatched_pending_identity_never_calls_provider(self):
        cases = (
            (None, "missing_identity"),
            (mapping("wrong", "fixture"), "identity_mismatch"),
            (
                replace(
                    mapping("candidate", "fixture"),
                    state=ChartMappingState.PENDING,
                    engine_reference=None,
                ),
                "pending_identity",
            ),
        )
        for value, expected in cases:
            self.mappings.items["candidate"] = value
            result = self.service().evaluate(
                AccountId("viewer"), (CandidateWork(AccountId("candidate"), "pair-1"),)
            )
            self.assertEqual(result.entries[0].state, expected)
        self.assertEqual(self.provider.calls, 0)

    def test_partial_batch_keeps_per_pair_failure_without_inventing_results(self):
        self.provider = ScriptedCompatibilityProvider(
            "test", provenance(), (FixtureCase.PENDING, FailureCode.OUTAGE)
        )
        result = self.service().evaluate(
            AccountId("viewer"),
            (
                CandidateWork(AccountId("candidate"), "pair-1"),
                CandidateWork(AccountId("another"), "pair-2"),
            ),
        )
        self.assertEqual(result.state, "partial")
        self.assertEqual([item.state for item in result.entries], ["evaluated", "failed"])
        self.assertEqual(result.entries[1].compatibility.attempts, 3)
        self.assertEqual(self.provider.calls, 4)

    def test_stale_eligibility_mapping_and_withdrawal_drop_provider_output(self):
        for mutation, expected in (
            (lambda: setattr(self.evidence, "version", "v2"), "reload_required"),
            (lambda: self.evidence.excluded.add("candidate"), "excluded"),
            (
                lambda: self.mappings.items.update(
                    candidate=replace(self.mappings.items["candidate"], mapping_version="v2")
                ),
                "stale",
            ),
        ):
            self.evidence = EvidenceRepository()
            self.mappings = MappingRepository()
            provider = self.provider

            class ChangesDuringCall:
                def evaluate(self, request, idempotency_key, provider=provider, mutation=mutation):
                    result = provider.evaluate(request, idempotency_key)
                    mutation()
                    return result

            result = self.service(ChangesDuringCall()).evaluate(
                AccountId("viewer"), (CandidateWork(AccountId("candidate"), "pair-1"),)
            )
            self.assertEqual(result.entries[0].state, expected)
            self.assertIsNone(result.entries[0].compatibility)

    def test_eligibility_is_rechecked_before_retry(self):
        evidence = self.evidence

        class RevokesDuringTimeout:
            calls = 0

            def evaluate(self, request, idempotency_key):
                self.calls += 1
                evidence.excluded.add("candidate")
                raise ExpectedProviderFailure(FailureCode.TIMEOUT)

        provider = RevokesDuringTimeout()
        result = self.service(provider).evaluate(
            AccountId("viewer"), (CandidateWork(AccountId("candidate"), "pair-1"),)
        )
        self.assertEqual(provider.calls, 1)
        self.assertEqual(result.entries[0].state, "excluded")

    def test_later_pair_cannot_leave_earlier_revoked_or_changed_result_in_batch(self):
        for mutation, expected in (
            (lambda: self.evidence.excluded.add("candidate"), "excluded"),
            (
                lambda: self.mappings.items.update(
                    candidate=replace(self.mappings.items["candidate"], mapping_version="v2")
                ),
                "stale",
            ),
        ):
            self.evidence = EvidenceRepository()
            self.mappings = MappingRepository()
            provider = ScriptedCompatibilityProvider("test", provenance(), (FixtureCase.PENDING,))

            class ChangesEarlierPair:
                def evaluate(self, request, idempotency_key, provider=provider, mutation=mutation):
                    result = provider.evaluate(request, idempotency_key)
                    if request.candidate.account_id == AccountId("another"):
                        mutation()
                    return result

            result = self.service(ChangesEarlierPair()).evaluate(
                AccountId("viewer"),
                (
                    CandidateWork(AccountId("candidate"), "pair-1"),
                    CandidateWork(AccountId("another"), "pair-2"),
                ),
            )
            self.assertEqual(result.state, "partial")
            self.assertEqual(result.entries[0].state, expected)
            self.assertIsNone(result.entries[0].compatibility)
            self.assertEqual(result.entries[1].state, "evaluated")

    def test_batch_budget_duplicate_ids_and_duplicate_keys_rejected(self):
        for candidates in (
            tuple(CandidateWork(AccountId(str(i)), str(i)) for i in range(21)),
            (
                CandidateWork(AccountId("candidate"), "1"),
                CandidateWork(AccountId("candidate"), "2"),
            ),
            (CandidateWork(AccountId("candidate"), "1"), CandidateWork(AccountId("another"), "1")),
        ):
            with self.assertRaises(ValueError):
                self.service().evaluate(AccountId("viewer"), candidates)
        self.assertEqual(self.provider.calls, 0)
        self.assertEqual(self.evidence.calls, [])


class LifecycleAndUnitOfWorkConformanceTests(NoNetworkCase):
    def test_shared_unknown_zero_and_absent_chart_never_claim_deleted(self):
        for count, chart, expected in (
            (None, request().viewer, "ownership_unknown"),
            (2, request().viewer, "preserve_shared_chart"),
            (0, request().viewer, "await_supported_deletion_rights"),
            (0, None, "reconcile_prior_references"),
        ):
            lifecycle = FixtureEngineLifecycle("test")
            intent = LifecycleRequest(AccountId("viewer"), chart, "delete-v1", count)
            result = lifecycle.plan_detachment(intent, "delete-1")
            self.assertFalse(result.complete)
            self.assertEqual(result.engine_action, expected)
            self.assertEqual(result.app_reference_action, "invalidate_app_reference")
            self.assertEqual(result, lifecycle.plan_detachment(intent, "delete-1"))
            with self.assertRaises(ExpectedProviderFailure):
                lifecycle.plan_detachment(replace(intent, deletion_version="delete-v2"), "delete-1")

    def test_wrong_account_mapping_rejected(self):
        with self.assertRaises(ValueError):
            LifecycleRequest(AccountId("other"), request().viewer, "delete-v1", 0)

    def uow(self):
        return FixtureMappingUnitOfWork(
            "test",
            FixtureAccountMappingState(
                AccountId("viewer"), "account-v1", "synthetic-birth-input-v1", True, False, None
            ),
        )

    def write(self):
        return MappingWrite(
            AccountId("viewer"), "account-v1", "synthetic-birth-input-v1", None, request().viewer
        )

    def event(self):
        return MappingOutboxEvent(
            "mapping-changed-1", AccountId("viewer"), request().viewer.mapping_version
        )

    def test_uow_mapping_and_event_commit_once_and_replay_conflict(self):
        uow, write, event = self.uow(), self.write(), self.event()
        self.assertTrue(uow.commit_mapping_and_event(write, event))
        self.assertTrue(uow.commit_mapping_and_event(write, event))
        self.assertEqual(uow.state.mapping, write.mapping)
        self.assertEqual(len(uow.events), 1)
        changed = replace(write, mapping=replace(write.mapping, mapping_version="new"))
        with self.assertRaises(ExpectedProviderFailure):
            uow.commit_mapping_and_event(changed, replace(event, mapping_version="new"))
        self.assertEqual(uow.state.mapping, write.mapping)

    def test_failed_cas_or_revocation_changes_neither_mapping_nor_event(self):
        for changes in (
            {"account_version": "new"},
            {"input_version": "new"},
            {"mapping": replace(request().viewer, mapping_version="new")},
            {"consent_current": False},
            {"deleted": True},
        ):
            uow = self.uow()
            uow.state = replace(uow.state, **changes)
            before = uow.state
            self.assertFalse(uow.commit_mapping_and_event(self.write(), self.event()))
            self.assertEqual(before, uow.state)
            self.assertEqual(uow.events, {})

    def test_cross_account_input_or_outbox_correspondence_rejected(self):
        for changes in ({"account_id": AccountId("other")}, {"expected_input_version": "old"}):
            with self.assertRaises(ValueError):
                replace(self.write(), **changes)
        uow = self.uow()
        with self.assertRaises(ValueError):
            uow.commit_mapping_and_event(
                self.write(), replace(self.event(), account_id=AccountId("other"))
            )
        self.assertEqual(uow.events, {})
        self.assertIsNone(uow.state.mapping)

    def test_runtime_malformed_internal_values_cannot_become_permission(self):
        for changes in (
            {"consent_current": "yes"},
            {"deleted": 0},
            {"account_id": "viewer"},
            {"mapping": "chart"},
            {"mapping": mapping("other", "fixture")},
            {"account_version": " "},
        ):
            with self.subTest(changes=changes), self.assertRaises((ValueError, TypeError)):
                replace(self.uow().state, **changes)
        with self.assertRaises(TypeError):
            replace(self.write(), mapping="chart")
        with self.assertRaises(TypeError):
            LifecycleRequest(AccountId("viewer"), "chart", "delete-v1", 0)
        for changes in ({"attempts": True}, {"failure": "timeout"}, {"output": "ready"}):
            with self.assertRaises((ValueError, TypeError)):
                replace(CompatibilityOutcome(None, FailureCode.OUTAGE, 1), **changes)

    def test_all_fixture_adapters_reject_staging_production_and_unknown_environment(self):
        for environment in ("staging", "production", "", "TEST"):
            for create in (
                lambda environment=environment: FixtureChartResolver(
                    environment, ChartResolutionState.PENDING, provenance()
                ),
                lambda environment=environment: ScriptedCompatibilityProvider(
                    environment, provenance(), (FixtureCase.PENDING,)
                ),
                lambda environment=environment: FixtureEngineLifecycle(environment),
                lambda environment=environment: FixtureMappingUnitOfWork(
                    environment, self.uow().state
                ),
                lambda environment=environment: FixtureCompatibilityBatchService(
                    environment,
                    TrustedEligibilityService(EvidenceRepository()),
                    MappingRepository(),
                    ScriptedCompatibilityProvider("test", provenance(), (FixtureCase.PENDING,)),
                    provenance(),
                    RetryPolicy(1),
                ),
            ):
                with self.assertRaises(ValueError):
                    create()

    def test_mutating_fixture_environment_cannot_bypass_call_guard(self):
        lifecycle = FixtureEngineLifecycle("test")
        lifecycle.environment = "production"
        with self.assertRaises(ValueError):
            lifecycle.plan_detachment(
                LifecycleRequest(AccountId("viewer"), None, "delete-v1", None), "delete-1"
            )
