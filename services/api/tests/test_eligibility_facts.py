"""Current fact acquisition and shared development policy; no DB/provider access."""

import json
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from glow_domain.eligibility import BlockState, PredicateOutcome
from glow_domain.eligibility_facts import (
    DEVELOPMENT_POLICY,
    DevelopmentEligibilityPolicy,
    FixtureEligibilityRepository,
    MediaFact,
    ParticipantFacts,
    age_on,
)
from glow_domain.identity import AccountId, EngineChartReference
from glow_domain.trusted_eligibility import (
    EligibilityDecisionState,
    EvidenceProblem,
    EvidenceUnavailable,
    TrustedEligibilityService,
)

CORPUS = (
    Path(__file__).resolve().parents[3]
    / "packages/contracts/fixtures/reciprocal-eligibility-v1.json"
)
TODAY = date(2026, 9, 23)
VIEWER = AccountId("viewer")
CANDIDATE = AccountId("candidate")


def person(account="viewer", attribute="demo_a", accepted_options=("demo_b",)):
    return ParticipantFacts(
        account_id=AccountId(account),
        generation=1,
        source_id=f"source-{account}-1",
        profile_id=f"profile-{account}",
        birth_date="1990-06-15",
        account_state="active",
        session_state="valid",
        verified=True,
        consent_state="accepted",
        consent_version="development-consent-1",
        display_name=f"Fictional {account}",
        summary="Fictional participant.",
        visibility="visible",
        moderation="approved",
        chart_state="resolved",
        attribute=attribute,
        preference_dimension="demo_connection",
        preference_version="development-preferences-1",
        accepted_options=accepted_options,
        approved_media=(
            MediaFact(
                f"asset-{account}",
                AccountId(account),
                f"profile-{account}",
                1,
                "approved",
                "development-media-1",
                f"fixture-approved-{account}",
            ),
        ),
    )


def ready_repository(clock=lambda: TODAY):
    repository = FixtureEligibilityRepository(clock, environment="test")
    repository.put_participant(person())
    repository.put_participant(person("candidate", "demo_b", ("demo_a",)))
    repository.observe_block(VIEWER, CANDIDATE, BlockState.CLEAR)
    repository.observe_block(CANDIDATE, VIEWER, BlockState.CLEAR)
    return repository


def from_corpus(value):
    value = dict(value)
    value["account_id"] = AccountId(value["account_id"])
    if value["accepted_options"] is not None:
        value["accepted_options"] = tuple(value["accepted_options"])
    if value["approved_media"] is not None:
        value["approved_media"] = tuple(
            MediaFact(**{**asset, "owner_id": AccountId(asset["owner_id"])})
            for asset in value["approved_media"]
        )
    return ParticipantFacts(**value)


def repository_from_case(base, case):
    now = case.get("clock", base["clock"])

    def clock(now=now):
        return date.fromisoformat(now) if now else None

    policy_patch = case.get("policy", {})
    selected_policy = (
        None
        if policy_patch is None
        else DevelopmentEligibilityPolicy(**{**base["policy"], **policy_patch})
    )
    repository = FixtureEligibilityRepository(clock, selected_policy, environment="test")
    for side in ("viewer", "candidate"):
        if case.get("missing_participant") != side:
            repository.put_participant(from_corpus({**base[side], **case.get(side, {})}))
    for side, state in {**base["blocks"], **case.get("blocks", {})}.items():
        if state is not None:
            actor, target = (VIEWER, CANDIDATE) if side == "viewer" else (CANDIDATE, VIEWER)
            repository.observe_block(actor, target, BlockState(state))
    return repository


class FactEligibilityTests(TestCase):
    def test_repository_requires_explicit_development_or_test_environment(self):
        for environment in ("production", "staging", "", None):
            with self.subTest(environment=environment), self.assertRaises(ValueError):
                FixtureEligibilityRepository(lambda: TODAY, environment=environment)
        with self.assertRaises(TypeError):
            FixtureEligibilityRepository(lambda: TODAY)
        self.assertIsInstance(
            FixtureEligibilityRepository(lambda: TODAY, environment="development"),
            FixtureEligibilityRepository,
        )

    def test_canonical_cross_language_truth_table_from_raw_facts(self):
        corpus = json.loads(CORPUS.read_text())
        self.assertEqual(corpus["version"], "reciprocal-eligibility-v1")
        ids = [case["id"] for case in corpus["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        base = corpus["base"]
        for case in corpus["cases"]:
            with self.subTest(case=case["id"]):
                repository = repository_from_case(base, case)
                target = VIEWER if case.get("self_pair") else CANDIDATE
                with patch("socket.socket", side_effect=AssertionError("No network")):
                    result = TrustedEligibilityService(repository).evaluate(VIEWER, target)
                self.assertEqual(result.state.value, case["expected"]["state"])
                if result.state is EligibilityDecisionState.REJECTED or case.get("self_pair"):
                    continue
                evidence = repository.acquire(VIEWER, target)
                for side in ("viewer", "candidate"):
                    for rule, outcome in getattr(evidence, side).assessments():
                        expected = case["expected"].get(side, {}).get(rule.value, "pass")
                        self.assertEqual(outcome.value, expected, f"{side}.{rule.value}")
                for field, default in (
                    ("viewer_accepts_candidate", "pass"),
                    ("candidate_accepts_viewer", "pass"),
                    ("viewer_blocks_candidate", "clear"),
                    ("candidate_blocks_viewer", "clear"),
                ):
                    self.assertEqual(
                        getattr(evidence.policy.inputs, field).value,
                        case["expected"].get(field, default),
                        field,
                    )

    def test_every_source_replacement_invalidates_even_unchanged_values(self):
        source = person()
        for field, value in (
            ("birth_date", "1991-06-15"),
            ("consent_version", "old"),
            ("consent_state", "withdrawn"),
            ("session_state", "expired"),
            ("account_state", "suspended"),
            ("verified", False),
            ("summary", "Another biography"),
            ("display_name", "Different name"),
            ("visibility", "paused"),
            ("moderation", "restricted"),
            ("chart_state", "pending"),
            ("accepted_options", ("demo_a",)),
            ("attribute", "demo_b"),
            ("preference_dimension", None),
            ("preference_version", "future"),
            ("approved_media", ()),
            ("profile_id", "replacement-profile"),
            ("source_id", "replacement-source"),
        ):
            for side in ("viewer", "candidate"):
                with self.subTest(field=field, side=side):
                    repository = ready_repository()
                    service = TrustedEligibilityService(repository)
                    source = (
                        person() if side == "viewer" else person("candidate", "demo_b", ("demo_a",))
                    )
                    previous = service.evaluate(VIEWER, CANDIDATE).evidence_version
                    repository.put_participant(replace(source, **{field: value}))
                    repository.put_participant(source)
                    restored = service.evaluate(VIEWER, CANDIDATE, previous)
                    self.assertEqual(restored.state, EligibilityDecisionState.RELOAD_REQUIRED)
                    self.assertEqual(restored.problem, EvidenceProblem.STALE_ACTION)
                    self.assertNotEqual(
                        getattr(previous, f"{side}_snapshot_version"),
                        getattr(restored.evidence_version, f"{side}_snapshot_version"),
                    )
                    # Rewriting the same trusted value never revives earlier action versions.
                    repository.put_participant(source)
                    self.assertNotEqual(
                        restored.evidence_version,
                        service.evaluate(VIEWER, CANDIDATE).evidence_version,
                    )

    def test_absent_block_first_insertion_unblock_and_repeated_restoration(self):
        for actor, target, field in (
            (VIEWER, CANDIDATE, "viewer"),
            (CANDIDATE, VIEWER, "candidate"),
        ):
            with self.subTest(actor=actor):
                repository = ready_repository()
                service = TrustedEligibilityService(repository)
                old = service.evaluate(VIEWER, CANDIDATE).evidence_version
                for _ in range(3):
                    repository.observe_block(actor, target, BlockState.BLOCKED)
                    self.assertEqual(
                        service.evaluate(VIEWER, CANDIDATE, old).state,
                        EligibilityDecisionState.EXCLUDED,
                    )
                    repository.observe_block(actor, target, BlockState.CLEAR)
                    restored = service.evaluate(VIEWER, CANDIDATE, old)
                    self.assertEqual(restored.state, EligibilityDecisionState.RELOAD_REQUIRED)
                    self.assertNotEqual(
                        getattr(old, f"{field}_block_version"),
                        getattr(restored.evidence_version, f"{field}_block_version"),
                    )
                    self.assertNotEqual(
                        getattr(old, f"{field}_snapshot_version"),
                        getattr(restored.evidence_version, f"{field}_snapshot_version"),
                    )

    def test_missing_direction_never_becomes_clear_from_other_direction(self):
        repository = FixtureEligibilityRepository(lambda: TODAY, environment="test")
        repository.put_participant(person())
        repository.put_participant(person("candidate", "demo_b", ("demo_a",)))
        repository.observe_block(VIEWER, CANDIDATE, BlockState.CLEAR)
        evidence = repository.acquire(VIEWER, CANDIDATE)
        self.assertEqual(evidence.policy.inputs.candidate_blocks_viewer, BlockState.UNKNOWN)
        self.assertEqual(
            TrustedEligibilityService(repository).evaluate(VIEWER, CANDIDATE).state,
            EligibilityDecisionState.EXCLUDED,
        )

    def test_generation_and_media_generation_are_bound_and_restoration_stays_stale(self):
        repository = ready_repository()
        service = TrustedEligibilityService(repository)
        before = service.evaluate(VIEWER, CANDIDATE).evidence_version
        source = person()
        repository.put_participant(replace(source, generation=2))
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE).state, EligibilityDecisionState.EXCLUDED
        )
        media = tuple(replace(asset, generation=2) for asset in source.approved_media)
        repository.put_participant(replace(source, generation=2, approved_media=media))
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE, before).state,
            EligibilityDecisionState.RELOAD_REQUIRED,
        )
        repository.put_participant(source)
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE, before).state,
            EligibilityDecisionState.RELOAD_REQUIRED,
        )

    def test_removed_person_and_recreated_source_do_not_reset_revisions(self):
        repository = ready_repository()
        service = TrustedEligibilityService(repository)
        old = service.evaluate(VIEWER, CANDIDATE).evidence_version
        repository.remove_participant(VIEWER)
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE).problem, EvidenceProblem.MISSING_EVIDENCE
        )
        repository.put_participant(person())
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE, old).state, EligibilityDecisionState.RELOAD_REQUIRED
        )

    def test_policy_withdrawal_restoration_and_same_value_set_invalidate(self):
        repository = ready_repository()
        service = TrustedEligibilityService(repository)
        old = service.evaluate(VIEWER, CANDIDATE).evidence_version
        repository.set_policy(None)
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE).problem, EvidenceProblem.POLICY_PENDING
        )
        repository.set_policy(DEVELOPMENT_POLICY)
        restored = service.evaluate(VIEWER, CANDIDATE, old)
        self.assertEqual(restored.state, EligibilityDecisionState.RELOAD_REQUIRED)
        repository.set_policy(DEVELOPMENT_POLICY)
        self.assertNotEqual(
            restored.evidence_version, service.evaluate(VIEWER, CANDIDATE).evidence_version
        )

    def test_clock_changes_recompute_birth_boundary_and_policy_expiry_without_edits(self):
        current = [date(2026, 9, 22)]
        repository = ready_repository(lambda: current[0])
        repository.put_participant(replace(person(), birth_date="2008-09-23"))
        service = TrustedEligibilityService(repository)
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE).state, EligibilityDecisionState.EXCLUDED
        )
        current[0] = TODAY
        self.assertEqual(service.evaluate(VIEWER, CANDIDATE).state, EligibilityDecisionState.READY)
        repository.set_policy(replace(DEVELOPMENT_POLICY, effective_until="2026-09-24"))
        current[0] = date(2026, 9, 24)
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE).problem, EvidenceProblem.POLICY_PENDING
        )

    def test_clock_a_b_a_never_revives_an_old_ready_token(self):
        current = [TODAY]
        repository = ready_repository(lambda: current[0])
        service = TrustedEligibilityService(repository)
        old = service.evaluate(VIEWER, CANDIDATE).evidence_version
        current[0] += timedelta(days=1)
        second = service.evaluate(VIEWER, CANDIDATE).evidence_version
        current[0] = TODAY
        result = service.evaluate(VIEWER, CANDIDATE, old)
        self.assertEqual(result.state, EligibilityDecisionState.RELOAD_REQUIRED)
        self.assertNotEqual(result.evidence_version, second)
        self.assertNotEqual(result.evidence_version, old)

    def test_clock_dependency_reentrant_revocation_is_acquired_consistently(self):
        repository = ready_repository()

        def clock():
            repository.put_participant(replace(person(), consent_state="withdrawn"))
            return TODAY

        repository._clock = clock
        self.assertEqual(
            TrustedEligibilityService(repository).evaluate(VIEWER, CANDIDATE).state,
            EligibilityDecisionState.EXCLUDED,
        )

    def test_clock_dependency_reentrant_removal_is_expected_missing_evidence(self):
        repository = ready_repository()

        def clock():
            repository.remove_participant(VIEWER)
            return TODAY

        repository._clock = clock
        self.assertEqual(
            TrustedEligibilityService(repository).evaluate(VIEWER, CANDIDATE).problem,
            EvidenceProblem.MISSING_EVIDENCE,
        )

    def test_aware_datetime_uses_utc_and_naive_time_is_unavailable(self):
        repository = ready_repository(lambda: datetime(2026, 9, 23, tzinfo=UTC))
        self.assertEqual(
            TrustedEligibilityService(repository).evaluate(VIEWER, CANDIDATE).state,
            EligibilityDecisionState.READY,
        )
        repository._clock = lambda: datetime(2026, 9, 23)
        self.assertEqual(
            TrustedEligibilityService(repository).evaluate(VIEWER, CANDIDATE).problem,
            EvidenceProblem.POLICY_PENDING,
        )

    def test_media_requires_one_current_valid_asset_and_rejects_mixed_sources(self):
        repository = ready_repository()
        source = person()
        approved = source.approved_media[0]
        removed = replace(approved, asset_id="other-asset", state="removed")
        repository.put_participant(replace(source, approved_media=(approved, removed)))
        service = TrustedEligibilityService(repository)
        self.assertEqual(service.evaluate(VIEWER, CANDIDATE).state, EligibilityDecisionState.READY)
        repository.put_participant(
            replace(source, approved_media=(approved, replace(removed, owner_id=CANDIDATE)))
        )
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE).state, EligibilityDecisionState.EXCLUDED
        )
        repository.put_participant(replace(source, approved_media=(approved, approved)))
        self.assertEqual(
            service.evaluate(VIEWER, CANDIDATE).state, EligibilityDecisionState.EXCLUDED
        )

    def test_expected_unavailability_is_sanitized_but_programming_errors_propagate(self):
        with self.assertRaises(TypeError):
            EvidenceUnavailable("private reason")
        repository = ready_repository()
        service = TrustedEligibilityService(repository)
        with patch.object(repository, "acquire", side_effect=EvidenceUnavailable()):
            result = service.evaluate(VIEWER, CANDIDATE)
            self.assertEqual(result.problem, EvidenceProblem.MISSING_EVIDENCE)
            self.assertNotIn("private reason", repr(result))
        with patch.object(repository, "acquire", side_effect=RuntimeError("implementation defect")):
            with self.assertRaisesRegex(RuntimeError, "implementation defect"):
                service.evaluate(VIEWER, CANDIDATE)
        for bad in (True, {"account_id": "viewer", "eligible": True}):
            with self.assertRaises(TypeError):
                repository.put_participant(bad)
        with self.assertRaises(TypeError):
            repository.acquire(EngineChartReference("viewer"), CANDIDATE)
        with self.assertRaises(TypeError):
            replace(person(), accepted_options=["demo_a"])
        with self.assertRaises(TypeError):
            replace(person(), approved_media=[person().approved_media[0]])
        with self.assertRaises(TypeError):
            replace(person(), verified="true")
        with self.assertRaises(FrozenInstanceError):
            person().birth_date = "2000-01-01"
        with self.assertRaises(FrozenInstanceError):
            person().approved_media[0].state = "removed"

    def test_private_raw_facts_are_not_in_default_diagnostics(self):
        raw = person()
        for private in (
            raw.birth_date,
            raw.consent_version,
            raw.summary,
            raw.approved_media[0].delivery_ref,
        ):
            self.assertNotIn(private, repr(raw))
            self.assertNotIn(private, repr(raw.approved_media[0]))

    def test_age_projection_uses_the_fictional_date_instead_of_fixed_age(self):
        self.assertEqual(age_on("1990-06-15", TODAY), 36)
        self.assertEqual(age_on("1980-10-01", TODAY), 45)
        self.assertEqual(age_on("2008-02-29", date(2026, 2, 28)), 17)
        self.assertEqual(age_on("2008-02-29", date(2026, 3, 1)), 18)
        self.assertIsNone(age_on("2000-02-30", TODAY))
        self.assertIsNone(age_on("2027-01-01", TODAY))

    def test_profile_readiness_is_independent_from_reciprocal_preferences(self):
        repository = ready_repository()
        repository.put_participant(replace(person(), accepted_options=("demo_a",)))
        evidence = repository.acquire(VIEWER, CANDIDATE)
        self.assertEqual(evidence.viewer.complete, PredicateOutcome.PASS)
        self.assertEqual(evidence.policy.inputs.viewer_accepts_candidate, PredicateOutcome.FAIL)
        self.assertEqual(
            TrustedEligibilityService(repository).evaluate(VIEWER, CANDIDATE).state,
            EligibilityDecisionState.EXCLUDED,
        )
