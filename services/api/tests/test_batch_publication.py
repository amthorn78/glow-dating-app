"""Final-read regressions using actual fact/link writers and callback-capable ports."""

from dataclasses import replace
from datetime import date
from unittest.mock import patch

from glow_domain.eligibility import BlockState
from glow_domain.eligibility_facts import DEVELOPMENT_POLICY, FixtureEligibilityRepository
from glow_domain.fixture_coherence import (
    FixtureChartMappingRepository,
    FixtureReadGuard,
    FixtureRevision,
    capture_revisions,
    guard_is_current,
)
from glow_domain.identity import AccountId, ChartMappingState, EngineChartReference
from glow_domain.provider_fixtures import CandidateWork, FixtureCompatibilityBatchService
from glow_domain.trusted_eligibility import EvidenceUnavailable, TrustedEligibilityService
from tests import test_provider_conformance as fixtures


class FinalReadHarness:
    """Name existing phases without replacing their reads or changing call order."""

    def __init__(self, owner, order, phase, mutation):
        self.phase = None
        self.target = None
        self.events = []
        self.reads = 0
        self.fired = False
        self.order = order
        harness = self

        class PhasedService(FixtureCompatibilityBatchService):
            def _evaluate_one(self, viewer, item):
                harness.phase = "provider_work"
                result = super()._evaluate_one(viewer, item)
                harness.phase = "final_mapping"
                return result

            def _revalidate(self, viewer, prepared):
                harness.target = prepared.outcome.account_id.value
                harness.events.append((harness.phase, harness.target))
                return super()._revalidate(viewer, prepared)

            def _revalidate_eligibility(self, viewer, outcome, version):
                harness.phase = "final_acquisition"
                harness.target = outcome.account_id.value
                harness.events.append((harness.phase, harness.target))
                return super()._revalidate_eligibility(viewer, outcome, version)

        def maybe_mutate():
            if not harness.fired and harness.phase == phase and harness.target == order[-1]:
                harness.fired = True
                harness.events.append(("mutation", order[-1]))
                mutation()

        def clock():
            harness.reads += 1
            if phase == "final_acquisition":
                maybe_mutate()
            return owner.today

        original_get = owner.mappings.get

        def get(account_id):
            value = original_get(account_id)
            if phase == "final_mapping" and account_id == AccountId(order[-1]):
                maybe_mutate()
            return value

        owner.evidence._clock = clock
        owner.mappings.get = get
        normal = owner.service()
        self.service = PhasedService(
            normal.environment,
            normal.eligibility,
            normal.mappings,
            normal.provider,
            normal.provenance,
            normal.retry_policy,
        )

    def run(self):
        return self.service.evaluate(
            AccountId("viewer"),
            tuple(CandidateWork(AccountId(name), f"pair-{name}") for name in self.order),
        )


class BatchPublicationTests(fixtures.NoNetworkCase):
    reset_sources = fixtures.FactDerivedBatchConformanceTests.reset_sources
    service = fixtures.FactDerivedBatchConformanceTests.service

    def setUp(self):
        super().setUp()
        self.reset_sources()

    def assert_last_phase_mutation(self, harness, phase):
        self.assertTrue(harness.fired)
        self.assertLess(
            harness.events.index((phase, harness.order[0])),
            harness.events.index(("mutation", harness.order[-1])),
        )
        self.assertEqual(harness.reads, 14)
        self.assertEqual(len(self.mappings.calls), 12)
        self.assertEqual(self.provider.calls, 2)

    def person_named(self, name):
        return getattr(self, f"{name}_facts")

    def mutate_facts(self, kind, target, earlier):
        person = self.person_named(target)
        if kind == "consent":
            self.evidence.put_participant(replace(person, consent_state="withdrawn"))
        elif kind == "media":
            self.evidence.put_participant(replace(person, approved_media=()))
        elif kind == "block":
            other = earlier if target == "viewer" else "viewer"
            self.evidence.observe_block(AccountId(target), AccountId(other), BlockState.BLOCKED)
        elif kind == "policy":
            self.evidence.set_policy(None)
        elif kind == "remove":
            self.evidence.remove_participant(person.account_id)
        elif kind == "source":
            self.evidence.put_participant(replace(person, source_id="replacement-source"))
        elif kind == "generation":
            self.evidence.put_participant(replace(person, generation=2))
        elif kind == "same_value":
            self.evidence.put_participant(person)
        else:
            raise AssertionError(kind)

    def restore_facts(self, kind, target, earlier):
        if kind == "block":
            other = earlier if target == "viewer" else "viewer"
            self.evidence.observe_block(AccountId(target), AccountId(other), BlockState.CLEAR)
        elif kind == "policy":
            self.evidence.set_policy(DEVELOPMENT_POLICY)
        else:
            self.evidence.put_participant(self.person_named(target))

    def test_unchanged_two_pair_control_in_both_orders(self):
        for order in (("candidate", "another"), ("another", "candidate")):
            with self.subTest(order=order):
                self.reset_sources()
                harness = FinalReadHarness(self, order, "none", lambda: None)
                result = harness.run()
                self.assertEqual(result.state, "evaluated")
                self.assertEqual([entry.state for entry in result.entries], ["evaluated"] * 2)
                self.assertTrue(all(entry.compatibility.output for entry in result.entries))
                self.assertEqual(harness.reads, 14)
                self.assertEqual(len(self.mappings.calls), 12)
                self.assertEqual(self.provider.calls, 2)

    def test_final_acquisition_revocation_and_restoration_cannot_publish_earlier_output(self):
        for order in (("candidate", "another"), ("another", "candidate")):
            for shared in (False, True):
                for kind in (
                    "consent",
                    "media",
                    "block",
                    "policy",
                    "remove",
                    "source",
                    "generation",
                    "same_value",
                ):
                    for restore in (False, True):
                        with self.subTest(order=order, shared=shared, kind=kind, restore=restore):
                            self.reset_sources()
                            earlier = order[0]
                            target = "viewer" if shared else earlier

                            def mutation(
                                kind=kind, target=target, earlier=earlier, restore=restore
                            ):
                                self.mutate_facts(kind, target, earlier)
                                if restore:
                                    self.restore_facts(kind, target, earlier)

                            harness = FinalReadHarness(self, order, "final_acquisition", mutation)
                            result = harness.run()
                            self.assert_last_phase_mutation(harness, "final_acquisition")
                            self.assertEqual(result.entries[0].state, "reload_required")
                            self.assertIsNone(result.entries[0].compatibility)
                            if shared or kind == "policy":
                                self.assertIsNone(result.entries[1].compatibility)
                            else:
                                self.assertEqual(result.entries[1].state, "evaluated")
                                self.assertIsNotNone(result.entries[1].compatibility.output)

    def test_final_mapping_changes_and_same_value_restoration_invalidate_captured_links(self):
        for order in (("candidate", "another"), ("another", "candidate")):
            for shared in (False, True):
                for kind in (
                    "input",
                    "mapping",
                    "identity",
                    "engine",
                    "pending",
                    "remove",
                    "same_value",
                ):
                    for restore in (False, True):
                        with self.subTest(order=order, shared=shared, kind=kind, restore=restore):
                            self.reset_sources()
                            target = AccountId("viewer" if shared else order[0])
                            original = self.mappings.get(target)
                            self.mappings.calls.clear()
                            changed = {
                                "input": replace(original, birth_input_version="input-2"),
                                "mapping": replace(original, mapping_version="mapping-2"),
                                "identity": replace(original, account_id=AccountId("replacement")),
                                "engine": replace(
                                    original, engine_reference=EngineChartReference("other")
                                ),
                                "pending": replace(
                                    original, state=ChartMappingState.PENDING, engine_reference=None
                                ),
                                "remove": None,
                                "same_value": original,
                            }[kind]

                            def mutation(
                                target=target, changed=changed, original=original, restore=restore
                            ):
                                self.mappings.put(target, changed)
                                if restore:
                                    self.mappings.put(target, original)

                            harness = FinalReadHarness(self, order, "final_mapping", mutation)
                            result = harness.run()
                            self.assert_last_phase_mutation(harness, "final_mapping")
                            self.assertEqual(result.entries[0].state, "stale")
                            self.assertIsNone(result.entries[0].compatibility)
                            self.assertEqual(
                                result.entries[1].state, "stale" if shared else "evaluated"
                            )
                            self.assertEqual(result.entries[1].compatibility is None, shared)

    def test_later_final_clock_observation_invalidates_earlier_policy_and_age(self):
        for order in (("candidate", "another"), ("another", "candidate")):
            self.reset_sources()
            self.evidence.set_policy(replace(DEVELOPMENT_POLICY, effective_until="2026-09-24"))
            harness = FinalReadHarness(
                self, order, "final_acquisition", lambda: setattr(self, "today", date(2026, 9, 24))
            )
            result = harness.run()
            self.assert_last_phase_mutation(harness, "final_acquisition")
            self.assertEqual(
                [entry.state for entry in result.entries], ["reload_required", "rejected"]
            )
            self.assertTrue(all(entry.compatibility is None for entry in result.entries))

    def test_unsupported_missing_and_unavailable_coherence_fail_closed(self):
        work = (CandidateWork(AccountId("candidate"), "pair"),)
        for source_name in ("evidence", "mappings"):
            for capability in (None, lambda *args: None, lambda *args: FixtureReadGuard(())):
                with self.subTest(source=source_name, capability=capability):
                    self.reset_sources()
                    getattr(self, source_name).publication_guard = capability
                    result = self.service().evaluate(AccountId("viewer"), work)
                    self.assertIsNone(result.entries[0].compatibility)
                    self.assertEqual(self.provider.calls, 0)
                    self.assertEqual(self.mappings.calls, [])
            self.reset_sources()
            with patch.object(
                getattr(self, source_name), "publication_guard", side_effect=EvidenceUnavailable()
            ):
                result = self.service().evaluate(AccountId("viewer"), work)
                self.assertIsNone(result.entries[0].compatibility)
                self.assertEqual(self.provider.calls, 0)
        self.reset_sources()
        service = replace(
            self.service(),
            mappings={AccountId("candidate"): self.mappings.get(AccountId("candidate"))},
        )
        self.assertEqual(service.evaluate(AccountId("viewer"), work).entries[0].state, "stale")
        self.assertEqual(self.provider.calls, 0)

    def test_guard_acquisition_callback_cannot_stamp_old_permission_with_new_revision(self):
        for source_name in ("evidence", "mappings"):
            self.reset_sources()
            source = getattr(self, source_name)
            original = source.publication_guard

            def capture(*accounts, original=original):
                self.evidence.put_participant(
                    replace(self.candidate_facts, consent_state="withdrawn")
                )
                return original(*accounts)

            source.publication_guard = capture
            result = self.service().evaluate(
                AccountId("viewer"), (CandidateWork(AccountId("candidate"), "pair"),)
            )
            self.assertEqual(result.entries[0].state, "excluded")
            self.assertIsNone(result.entries[0].compatibility)
            self.assertEqual(self.provider.calls, 0)

    def test_continuously_mutating_clock_and_mapping_reads_finish_without_retrying_provider(self):
        for source_name in ("evidence", "mappings"):
            self.reset_sources()
            reads = []
            if source_name == "evidence":

                def clock(reads=reads):
                    reads.append("clock")
                    self.evidence.put_participant(self.candidate_facts)
                    return self.today

                self.evidence._clock = clock
            else:
                original_get = self.mappings.get
                original_mapping = original_get(AccountId("candidate"))

                def get(
                    account_id,
                    reads=reads,
                    original_get=original_get,
                    original_mapping=original_mapping,
                ):
                    reads.append("mapping")
                    result = original_get(account_id)
                    self.mappings.put(AccountId("candidate"), original_mapping)
                    return result

                self.mappings.get = get
            result = self.service().evaluate(
                AccountId("viewer"), (CandidateWork(AccountId("candidate"), "pair"),)
            )
            self.assertIsNone(result.entries[0].compatibility)
            self.assertLessEqual(len(reads), 4)
            self.assertEqual(self.provider.calls, 0)

    def test_initial_denial_stays_denied_after_later_restoration_without_mapping_work(self):
        self.evidence.put_participant(replace(self.candidate_facts, consent_state="withdrawn"))
        harness = FinalReadHarness(
            self,
            ("candidate", "another"),
            "final_acquisition",
            lambda: self.evidence.put_participant(self.candidate_facts),
        )
        result = harness.run()
        self.assertTrue(harness.fired)
        self.assertEqual(result.entries[0].state, "excluded")
        self.assertIsNone(result.entries[0].compatibility)
        self.assertNotIn(AccountId("candidate"), self.mappings.calls)
        self.assertEqual(self.provider.calls, 1)


class ConcreteGuardTests(fixtures.NoNetworkCase):
    def test_pure_check_rejects_custom_getter_equality_and_revision_subclasses(self):
        class RevisionWithGetter(FixtureRevision):
            def __getattribute__(self, name):
                raise AssertionError("A supplied getter ran.")

        class CounterWithEquality(int):
            def __eq__(self, other):
                raise AssertionError("A supplied equality ran.")

        class GuardWithGetter(FixtureReadGuard):
            def __getattribute__(self, name):
                raise AssertionError("A supplied guard getter ran.")

        revision = FixtureRevision()
        for guard in (
            GuardWithGetter(((revision, 0),)),
            FixtureReadGuard(((RevisionWithGetter(), 0),)),
            FixtureReadGuard(((revision, CounterWithEquality(0)),)),
        ):
            self.assertFalse(guard_is_current(guard))
        self.assertTrue(guard_is_current(capture_revisions(revision)))
        guard = capture_revisions(revision)
        revision.advance()
        self.assertFalse(guard_is_current(guard))

    def test_mapping_delete_reinsert_and_same_value_put_advance_retained_cell(self):
        source = FixtureChartMappingRepository(environment="test")
        account = AccountId("absent")
        guard = source.publication_guard(account)
        source.put(account, None)
        self.assertFalse(guard_is_current(guard))
        guard = source.publication_guard(account)
        source.put(account, None)
        self.assertFalse(guard_is_current(guard))

    def test_missing_participant_removal_and_policy_restoration_advance_retained_cells(self):
        source = FixtureEligibilityRepository(lambda: date(2026, 9, 23), environment="test")
        account = AccountId("absent")
        guard = source.publication_guard(account)
        source.remove_participant(account)
        self.assertFalse(guard_is_current(guard))
        guard = source.publication_guard(account)
        source.set_policy(None)
        source.set_policy(DEVELOPMENT_POLICY)
        self.assertFalse(guard_is_current(guard))
        self.assertEqual(
            TrustedEligibilityService(source).evaluate(account, account).state.value, "rejected"
        )
