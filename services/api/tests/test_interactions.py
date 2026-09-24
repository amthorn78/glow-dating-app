"""Interaction state, trust/commit races, private receipts and shared conformance."""

import importlib.util
import json
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from glow_domain.discovery import QUEUE_LIFETIME_MS
from glow_domain.discovery_fixtures import build_discovery_fixture
from glow_domain.eligibility import BlockState
from glow_domain.identity import AccountId
from glow_domain.interaction_fixtures import build_interaction_fixture
from glow_domain.interactions import (
    CORPUS,
    MAX_EVENTS,
    MAX_RECEIPTS,
    MAX_VERSION,
    FixtureIdentityRegistry,
    FixtureInteractionRepository,
    FixtureInteractionWorker,
    _capture_intent,
)

spec = importlib.util.spec_from_file_location(
    "interaction_contracts", CORPUS.parents[1] / "runtime.py"
)
contract_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract_runtime)


class InteractionTests(TestCase):
    def setUp(self):
        self.network = patch("socket.socket", side_effect=AssertionError("No live adapters"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.reset()

    def reset(self):
        self.fixture = build_interaction_fixture()
        self.source = self.fixture.discovery.source
        self.repo = self.fixture.repository
        self.a = self.fixture.session(AccountId("discovery-viewer"), "session-a")
        self.b = self.fixture.session(AccountId("discovery-jules"), "session-b")
        self.c = self.fixture.session(AccountId("discovery-morgan"), "session-c")

    def target(self, name):
        return self.fixture.registry.account(AccountId(name))

    def intent(
        self,
        service=None,
        target="discovery-jules",
        *,
        key="like-1",
        action="like",
        version=0,
        mode="recommended",
        refresh=True,
    ):
        service = service or self.a
        page, batch = service.page(mode=mode, request_id="request", refresh=refresh)
        self.assertIsNotNone(batch, page)
        identity = self.target(target)
        self.assertIn(identity.profile_uuid, batch.profile_ids)
        return {
            "operation": "interaction",
            "meta": {"idempotency_key": key, "expected_version": version},
            "target_profile_id": identity.profile_uuid,
            "action": action,
            "batch_id": batch.batch_id,
            "batch_version": batch.version,
        }

    def unmatch(self, match, *, key="unmatch-1", version=None):
        return {
            "operation": "unmatch",
            "match_id": match["match_id"],
            "meta": {
                "idempotency_key": key,
                "expected_version": version if version is not None else match["version"],
            },
        }

    def block(self, target="discovery-jules", *, action="block", key="block-1", version=0):
        return {
            "operation": "block",
            "target_profile_id": self.target(target).profile_uuid,
            "action": action,
            "meta": {"idempotency_key": key, "expected_version": version},
        }

    def committed(self, service, intent, **kwargs):
        result = service.command(intent, **kwargs)
        self.assertEqual(result.code, "committed", result)
        self.assertTrue(
            contract_runtime.valid("production", "InteractionCommandResult", result.value)
        )
        return result.value

    def match(self):
        first = self.intent()
        self.committed(self.a, first)
        second = self.intent(self.b, "discovery-viewer", key="like-2")
        self.committed(self.b, second)
        matches = self.a.matches()
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["state"], "active")
        return matches[0], first, second

    def assert_empty(self):
        self.assertEqual(
            self.repo.counts,
            {"directions": 0, "matches": 0, "blocks": 0, "receipts": 0, "events": 0, "pending": 0},
        )

    def test_shared_raw_traces(self):
        for case in json.loads(CORPUS.read_text())["cases"]:
            with self.subTest(case=case["name"]):
                self.reset()
                sessions = {"discovery-viewer": self.a, "discovery-jules": self.b}
                originals, last_batches = {}, {}
                for step in case["steps"]:
                    service = sessions[step["actor"]]
                    target = next(
                        row
                        for row in self.fixture.registry.identities
                        if row.profile_id == step["target_profile_id"]
                    )
                    key = (step["actor"], step["idempotency_key"])
                    if step.get("replay_intent"):
                        intent = originals[key]
                    elif step["action"] in {"like", "pass"}:
                        if step["expected"].get("error"):
                            intent = {
                                **last_batches[step["actor"]],
                                "target_profile_id": target.profile_uuid,
                                "action": step["action"],
                                "meta": {
                                    "idempotency_key": step["idempotency_key"],
                                    "expected_version": step["expected_version"],
                                },
                            }
                        else:
                            intent = self.intent(
                                service,
                                target.account_id.value,
                                key=step["idempotency_key"],
                                action=step["action"],
                                version=step["expected_version"],
                            )
                            last_batches[step["actor"]] = intent
                    elif step["action"] == "unmatch":
                        intent = self.unmatch(
                            service.matches()[0],
                            key=step["idempotency_key"],
                            version=step["expected_version"],
                        )
                    else:
                        intent = self.block(
                            target.account_id.value,
                            action=step["action"],
                            key=step["idempotency_key"],
                            version=step["expected_version"],
                        )
                    originals[key] = intent
                    result = service.command(intent)
                    if "error" in step["expected"]:
                        self.assertEqual(result.code, step["expected"]["error"])
                    else:
                        self.assertEqual(result.code, "committed", result)
                        self.assertEqual(
                            result.value["receipt"]["outcome_code"],
                            step["expected"]["outcome_code"],
                        )
                        self.assertTrue(
                            contract_runtime.valid(
                                "production", "InteractionCommandResult", result.value
                            )
                        )
                events = Counter(event.kind for event in self.repo.events)
                actual = {
                    "directional_count": self.repo.counts["directions"],
                    "match_count": self.repo.counts["matches"],
                    "active_match_count": sum(
                        m.state == "active" for m in self.repo._state.matches.values()
                    ),
                    "match_created_events": events["match_created"],
                    "contact_revoked_events": events["contact_revoked"],
                    "block_changed_events": events["block_changed"],
                }
                self.assertEqual(actual, case["expected"])

    def test_unilateral_receipt_privacy_and_consumption_both_modes_refresh(self):
        intent = self.intent(action="pass")
        before_calls = self.fixture.discovery.provider.total_calls
        result = self.committed(self.a, intent)
        self.assertEqual(self.fixture.discovery.provider.total_calls, before_calls)
        self.assertIsNone(result["current_projection"]["match_id"])
        self.assertEqual(self.b.matches(), ())
        self.assertEqual(self.repo.events, ())
        self.assertEqual(
            self.a.command(
                {**intent, "meta": {"expected_version": 1, "idempotency_key": "fresh"}}
            ).code,
            "stale_batch",
        )
        for mode in ("recommended", "broader"):
            page, _ = self.a.page(mode=mode, request_id="refresh", refresh=True)
            self.assertNotIn("profile-jules", [card["profile_id"] for card in page["items"]])
        replay = self.committed(self.a, intent)
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["receipt"], result["receipt"])
        self.assertEqual(self.repo.counts["receipts"], 1)

    def test_actor_target_uuid_and_closed_intent_rejections_no_writes(self):
        good = self.intent()
        variants = [
            {**good, "actor_id": "discovery-viewer"},
            {**good, "reciprocal": True},
            {**good, "operation": "match"},
            {**good, "target_profile_id": "profile-jules"},
            {**good, "batch_id": "fixture-queue"},
            {**good, "batch_version": True},
        ]
        for value in (-1, MAX_VERSION + 1, True, "0", 0.0):
            variants.append({**good, "meta": {**good["meta"], "expected_version": value}})
        for intent in variants:
            self.assertEqual(self.a.command(intent).code, "invalid_request")
            self.assertIsNone(_capture_intent(intent))
            self.assert_empty()
        for target in (
            self.target("discovery-viewer").profile_uuid,
            str(uuid4()),
            self.target("discovery-jules").account_uuid,
        ):
            self.assertEqual(
                self.a.command({**good, "target_profile_id": target}).code, "unavailable"
            )
            self.assert_empty()
        self.a.discovery.authority.replace(self.fixture.discovery.viewer, "other-session")
        self.assertEqual(self.a.command(good).code, "stale_batch")
        self.assert_empty()

    def test_cross_actor_cross_mode_expiry_and_refresh_reject(self):
        for mutate in (
            lambda: self.a.discovery.authority.replace(AccountId("discovery-morgan"), "session-c"),
            lambda: self.fixture.discovery.clock.set(
                self.fixture.discovery.clock.read() + QUEUE_LIFETIME_MS
            ),
            lambda: self.a.page(mode="recommended", request_id="new", refresh=True),
        ):
            self.reset()
            intent = self.intent()
            mutate()
            self.assertEqual(self.a.command(intent).code, "stale_batch")
            self.assert_empty()
        self.reset()
        intent = self.intent(mode="recommended")
        self.a.page(mode="broader", request_id="other")
        self.assertEqual(self.a.command(intent, mode="broader").code, "stale_batch")
        self.assert_empty()

    def test_registry_ambiguity_wrong_owner_and_forged_mapping(self):
        rows = self.fixture.registry.identities
        with self.assertRaises(ValueError):
            FixtureIdentityRegistry((*rows, rows[0]))
        intent = self.intent()
        facts = self.source._participants[AccountId("discovery-jules")]
        self.source.put_participant(replace(facts, profile_id="profile-morgan"))
        self.assertEqual(self.a.command(intent).code, "unavailable")
        self.assert_empty()

    def test_missing_policy_and_all_relevant_raw_facts_invalidate_pending_like(self):
        changes = {
            "consent_state": "withdrawn",
            "visibility": "paused",
            "moderation": "restricted",
            "account_state": "deleted",
            "chart_state": "unavailable",
            "approved_media": (),
            "accepted_options": ("demo_b",),
            "session_state": "revoked",
        }
        for actor in ("discovery-viewer", "discovery-jules"):
            for field_name, value in changes.items():
                with self.subTest(actor=actor, field=field_name):
                    self.reset()
                    intent = self.intent()
                    account = AccountId(actor)
                    self.source.put_participant(
                        replace(self.source._participants[account], **{field_name: value})
                    )
                    self.assertNotEqual(self.a.command(intent).code, "committed")
                    self.assert_empty()
        self.reset()
        intent = self.intent()
        self.a.policy_version = None
        self.assertEqual(self.a.command(intent).code, "policy_unresolved")
        self.assert_empty()

    def test_final_callback_same_value_remove_restore_mapping_registry_time_and_abort(self):
        for kind in (
            "same",
            "restore",
            "mapping",
            "registry",
            "clock",
            "session",
            "policy",
            "abort",
        ):
            with self.subTest(kind=kind):
                self.reset()
                intent = self.intent()
                target = AccountId("discovery-jules")
                facts = self.source._participants[target]

                def mutate(kind=kind, facts=facts, target=target):
                    if kind == "same":
                        self.source.put_participant(facts)
                    elif kind == "restore":
                        self.source.remove_participant(target)
                        self.source.put_participant(facts)
                    elif kind == "mapping":
                        self.fixture.discovery.mappings.put(
                            target, self.fixture.discovery.mappings.get(target)
                        )
                    elif kind == "registry":
                        self.fixture.registry.replace(self.fixture.registry.identities)
                    elif kind == "clock":
                        self.fixture.discovery.clock.set(self.fixture.discovery.clock.read())
                    elif kind == "session":
                        self.a.discovery.authority.replace(
                            self.fixture.discovery.viewer, "session-a"
                        )
                    elif kind == "policy":
                        self.source.set_policy(self.source._policy)
                    else:
                        raise RuntimeError("controlled abort")

                self.a.before_commit = mutate
                if kind == "abort":
                    with self.assertRaisesRegex(RuntimeError, "controlled abort"):
                        self.a.command(intent)
                else:
                    self.assertEqual(self.a.command(intent).code, "stale_version")
                self.assert_empty()

    def test_duplicate_pending_submission_and_reentrant_block_never_half_commit(self):
        intent = self.intent()
        nested = []
        self.a.before_commit = lambda: nested.append(self.a.command(intent))
        self.committed(self.a, intent)
        self.assertEqual([result.code for result in nested], ["in_progress"])
        self.assertEqual(self.repo.counts["directions"], 1)
        self.reset()
        intent = self.intent()
        self.a.before_commit = lambda: self.committed(self.b, self.block("discovery-viewer"))
        self.assertEqual(self.a.command(intent).code, "stale_version")
        self.assertEqual(
            self.repo.counts,
            {"directions": 0, "matches": 0, "blocks": 1, "receipts": 1, "events": 1, "pending": 0},
        )

    def test_reciprocal_interleave_one_match_and_real_two_session_commands(self):
        first = self.intent()
        second = self.intent(self.b, "discovery-viewer", key="second")
        self.a.before_commit = lambda: self.committed(self.b, second)
        self.assertEqual(self.a.command(first).code, "stale_version")
        self.assertEqual(self.repo.counts["directions"], 1)
        self.assertEqual(self.repo.counts["matches"], 0)
        self.a.before_commit = lambda: None
        first = self.intent(key="first-retry")
        self.committed(self.a, first)
        self.assertEqual(self.repo.counts["matches"], 1)
        self.assertEqual([event.kind for event in self.repo.events], ["match_created"])
        pair = next(iter(self.repo._state.matches))
        self.assertEqual(
            pair,
            tuple(
                sorted(
                    (
                        self.target("discovery-viewer").account_uuid,
                        self.target("discovery-jules").account_uuid,
                    )
                )
            ),
        )
        self.committed(self.b, second)
        self.assertEqual(self.repo.counts["matches"], 1)

    def test_original_receipt_after_unmatch_is_immutable_no_cached_active_grant(self):
        match, first, second = self.match()
        original = self.committed(self.b, second)["receipt"]
        unmatch = self.unmatch(match)
        self.committed(self.a, unmatch)
        replay = self.committed(self.b, second)
        self.assertEqual(replay["receipt"], original)
        self.assertIsNone(replay["current_projection"])
        self.assertEqual(self.a.matches()[0]["state"], "unmatched")
        self.assertEqual(self.b.matches()[0]["version"], 2)
        self.assertFalse(self.b.contact_decision(match["match_id"])["match_current"])
        self.assertFalse(self.b.contact_decision(match["match_id"])["send_allowed"])
        self.committed(self.a, unmatch)
        fresh = self.unmatch(self.a.matches()[0], key="repeat-new-key")
        self.committed(self.a, fresh)
        self.assertEqual(len(self.repo.events), 2)
        self.assertEqual(self.repo.counts["matches"], 1)
        self.assertEqual(self.c.command(unmatch).code, "unavailable")
        self.assertIsNone(self.c.match_projection(match["match_id"]))
        self.assertIsNone(self.a.match_projection(str(uuid4())))

    def test_unmatch_available_paused_consent_withdrawn_or_target_missing_without_provider(self):
        for change in ("pause", "consent", "target_missing"):
            self.reset()
            match, _, _ = self.match()
            actor = self.fixture.discovery.viewer
            if change == "target_missing":
                self.source.remove_participant(AccountId("discovery-jules"))
            else:
                fields = (
                    {"visibility": "paused"}
                    if change == "pause"
                    else {"consent_state": "withdrawn"}
                )
                self.source.put_participant(replace(self.source._participants[actor], **fields))
            before_calls = self.fixture.discovery.provider.total_calls
            self.committed(self.a, self.unmatch(match))
            self.assertEqual(next(iter(self.repo._state.matches.values())).state, "unmatched")
            self.assertEqual(self.fixture.discovery.provider.total_calls, before_calls)

    def test_same_value_restoration_permanently_restricts_match_and_late_worker(self):
        for kind in ("same", "restore", "mapping", "block"):
            self.reset()
            match, _, second = self.match()
            event = self.repo.events[0]
            target = AccountId("discovery-jules")
            facts = self.source._participants[target]
            if kind == "same":
                self.source.put_participant(facts)
            elif kind == "restore":
                self.source.put_participant(replace(facts, visibility="paused"))
                self.source.put_participant(facts)
            elif kind == "mapping":
                self.fixture.discovery.mappings.put(
                    target, self.fixture.discovery.mappings.get(target)
                )
            else:
                self.committed(self.b, self.block("discovery-viewer"))
                self.committed(
                    self.b,
                    self.block("discovery-viewer", action="unblock", key="unblock", version=1),
                )
            projection = self.a.match_projection(match["match_id"])
            self.assertEqual(projection["state"], "restricted")
            self.assertEqual(projection["version"], 2)
            self.assertFalse(self.a.contact_decision(match["match_id"])["match_current"])
            self.assertIsNone(self.committed(self.b, second)["current_projection"])
            worker = FixtureInteractionWorker(self.a)
            self.assertEqual(worker.consume(event), "stale")
            self.assertEqual(worker.consume(event), "duplicate")
            self.assertEqual(Counter(e.kind for e in self.repo.events)["contact_revoked"], 1)

    def test_block_works_paused_and_unmatched_and_does_not_reveal_other_direction(self):
        match, first, _ = self.match()
        self.committed(self.a, self.unmatch(match))
        actor = self.fixture.discovery.viewer
        self.source.put_participant(replace(self.source._participants[actor], visibility="paused"))
        result = self.committed(self.a, self.block())
        self.assertEqual(result["current_projection"]["state"], "active")
        self.assertIsNone(self.b.match_projection(match["match_id"]))
        self.assertIsNone(self.committed(self.a, first)["current_projection"])
        self.committed(self.a, self.block(action="unblock", key="unblock", version=1))
        self.assertEqual(self.a.match_projection(match["match_id"])["state"], "unmatched")

    def test_block_unblock_retires_old_unilateral_like(self):
        self.committed(self.a, self.intent())
        self.committed(self.b, self.block("discovery-viewer"))
        self.committed(
            self.b, self.block("discovery-viewer", action="unblock", key="unblock", version=1)
        )
        self.committed(self.b, self.intent(self.b, "discovery-viewer", key="second"))
        self.assertEqual(self.repo.counts["matches"], 0)

    def test_response_lost_replay_conflicts_original_versions_and_private_receipt(self):
        intent = self.intent()
        original = self.committed(self.a, intent)
        before = self.repo.counts
        for changes in (
            {"action": "pass"},
            {"target_profile_id": self.target("discovery-morgan").profile_uuid},
            {"batch_id": str(uuid4())},
            {"meta": {**intent["meta"], "expected_version": 1}},
        ):
            self.assertEqual(self.a.command({**intent, **changes}).code, "idempotency_conflict")
            self.assertEqual(self.repo.counts, before)
        replay = self.committed(self.a, deepcopy(intent))
        self.assertEqual(replay["receipt"], original["receipt"])
        self.assertEqual(self.repo.counts, before)
        receipt = next(iter(self.repo._state.receipts.values()))
        self.assertEqual(len(receipt.digest), 64)
        self.assertNotIn("profile", receipt.digest)
        self.assertEqual(
            set(replay["receipt"]), {"outcome_code", "object_ref", "committed_version"}
        )
        self.a.discovery.authority.replace(None, None)
        self.assertEqual(self.a.command(intent).code, "unavailable")

    def test_capacity_refuses_without_evicting_receipts_or_half_writes(self):
        intent = self.intent()
        result = self.committed(self.a, intent)
        first_receipt = next(iter(self.repo._state.receipts.values()))
        state = self.repo._state
        filled = {
            (self.fixture.discovery.viewer, "interaction", f"key-{i}"): first_receipt
            for i in range(MAX_RECEIPTS - 1)
        }
        self.repo._state = replace(state, receipts={**state.receipts, **filled})
        before = self.repo.counts
        self.assertEqual(self.a.command(self.block()).code, "capacity_exceeded")
        self.assertEqual(self.repo.counts, before)
        self.assertEqual(self.committed(self.a, intent)["receipt"], result["receipt"])
        self.reset()
        self.repo._state = replace(self.repo._state, discretionary_events=MAX_EVENTS)
        before = self.repo.counts
        self.assertEqual(self.a.command(self.block()).code, "capacity_exceeded")
        self.assertEqual(self.repo.counts, before)

    def test_event_contract_and_fake_worker_never_send(self):
        match, _, _ = self.match()
        event = self.repo.events[0]
        self.assertTrue(
            contract_runtime.valid("development", "DevelopmentInteractionEvent", event.public())
        )
        self.assertEqual(
            set(event.public()),
            {"event_id", "kind", "aggregate_id", "aggregate_version", "contract_version"},
        )
        worker = FixtureInteractionWorker(self.a)
        self.assertEqual(worker.consume(event), "observed_no_delivery")
        self.assertEqual(worker.consume(event), "duplicate")
        self.assertFalse(self.a.contact_decision(match["match_id"])["send_allowed"])
        self.assertEqual(worker.consume(replace(event, event_id=str(uuid4()))), "unavailable")

    def test_final_projection_callback_cannot_publish_active_after_source_change(self):
        match, _, _ = self.match()
        original = self.fixture.registry.account
        fired = False

        def mutate(account):
            nonlocal fired
            result = original(account)
            if account == AccountId("discovery-jules") and not fired:
                fired = True
                facts = self.source._participants[account]
                self.source.put_participant(replace(facts, visibility="paused"))
            return result

        with patch.object(self.fixture.registry, "account", side_effect=mutate):
            self.assertIsNone(self.a.match_projection(match["match_id"]))
        self.assertEqual(self.a.match_projection(match["match_id"])["state"], "restricted")

    def test_source_binding_replacement_restricts_match_and_does_not_revive_old_like(self):
        match, _, _ = self.match()
        replacement = build_discovery_fixture()
        replacement.source.acquire(AccountId("discovery-viewer"), AccountId("discovery-jules"))
        self.a.discovery.source = replacement.source
        self.a.discovery.batch = replace(
            self.a.discovery.batch,
            eligibility=replace(self.a.discovery.batch.eligibility, repository=replacement.source),
        )
        self.assertEqual(self.a.match_projection(match["match_id"])["state"], "restricted")
        self.assertEqual(Counter(e.kind for e in self.repo.events)["contact_revoked"], 1)

    def test_pending_reservations_are_bounded_and_do_not_evict_evidence(self):
        intent = self.intent()
        nested = []

        def recurse():
            index = len(self.repo._pending)
            next_intent = {
                **intent,
                "meta": {**intent["meta"], "idempotency_key": f"nested-{index}"},
            }
            nested.append((index, self.a.command(next_intent).code))

        self.a.before_commit = recurse
        self.assertEqual(self.a.command(intent).code, "stale_version")
        self.assertEqual(max(index for index, _ in nested), MAX_RECEIPTS)
        self.assertIn((MAX_RECEIPTS, "capacity_exceeded"), nested)
        self.assertEqual(self.repo.counts["pending"], 0)
        self.assertEqual(self.repo.counts["directions"], 1)
        self.assertEqual(self.repo.counts["receipts"], 1)

    def test_interaction_policy_same_value_restoration_aborts_commit(self):
        intent = self.intent()

        def restore():
            self.a.policy_version = None
            self.a.policy_version = "development-interactions-1"

        self.a.before_commit = restore
        self.assertEqual(self.a.command(intent).code, "stale_version")
        self.assert_empty()

    def test_unmatch_does_not_need_mapping_read_or_provider(self):
        match, _, _ = self.match()
        with patch.object(
            self.fixture.discovery.mappings,
            "publication_guard",
            side_effect=AssertionError("No mapping dependency"),
        ):
            self.committed(self.a, self.unmatch(match))
        self.assertEqual(self.a.match_projection(match["match_id"])["state"], "unmatched")

    def test_source_revocation_at_max_version_denies_without_wrapping_or_same_version_event(self):
        match, _, _ = self.match()
        state = self.repo._state
        row = next(iter(state.matches.values()))
        self.repo._state = replace(state, matches={row.pair: replace(row, version=MAX_VERSION)})
        self.source.put_participant(self.source._participants[AccountId("discovery-jules")])
        self.assertIsNone(self.a.match_projection(match["match_id"]))
        self.assertFalse(self.a.contact_decision(match["match_id"])["match_current"])
        self.assertEqual(len(self.repo.events), 1)
        self.assertEqual(
            self.a.command(self.unmatch({**match, "version": MAX_VERSION})).code,
            "capacity_exceeded",
        )

    def test_exact_command_decoder_matches_shared_schema_cases(self):
        corpus = json.loads((CORPUS.parents[1] / "corpus/shared-v1.json").read_text())
        checked = 0
        for case in corpus["cases"]:
            if case["scope"] == "production" and case["definition"] in {
                "InteractionIntent",
                "UnmatchIntent",
                "BlockIntent",
            }:
                with self.subTest(case=case["name"]):
                    self.assertEqual(_capture_intent(case["value"]) is not None, case["valid"])
                    checked += 1
        self.assertGreaterEqual(checked, 6)

    def test_repository_swap_during_revocation_cannot_copy_old_match_or_leave_pending(self):
        match, _, _ = self.match()
        replacement = FixtureInteractionRepository(environment="test")
        original_clock = self.source._clock
        fired = False

        def change_repository():
            nonlocal fired
            if not fired:
                fired = True
                self.a.repository = replacement
                person = self.source._participants[AccountId("discovery-jules")]
                self.source.put_participant(replace(person, visibility="paused"))
            return original_clock()

        self.source._clock = change_repository
        self.assertIsNone(self.a.match_projection(match["match_id"]))
        self.assertEqual(replacement.counts["matches"], 0)
        self.assertEqual(replacement.counts["events"], 0)
        self.reset()
        intent = self.intent()
        replacement = FixtureInteractionRepository(environment="test")
        self.a.before_commit = lambda: setattr(self.a, "repository", replacement)
        self.assertEqual(self.a.command(intent).code, "stale_version")
        self.assert_empty()
        self.assertEqual(replacement.counts["pending"], 0)

    def test_batch_binds_registry_incarnation_from_issuance(self):
        intent = self.intent()
        self.fixture.registry.replace(self.fixture.registry.identities)
        self.assertEqual(self.a.command(intent).code, "stale_batch")
        self.assert_empty()
        self.committed(self.a, self.intent(key="current-registry"))

    def test_batch_binds_registry_adapter_identity(self):
        intent = self.intent()
        self.a.registry = FixtureIdentityRegistry(self.fixture.registry.identities)
        self.assertEqual(self.a.command(intent).code, "stale_batch")
        self.assert_empty()
        self.committed(self.a, self.intent(key="current-adapter"))

    def test_fresh_unblock_after_removal_conflicts_but_original_receipt_replays(self):
        self.committed(self.a, self.block())
        original_intent = self.block(action="unblock", key="original-unblock", version=1)
        original = self.committed(self.a, original_intent)
        self.assertEqual(original["receipt"]["committed_version"], 2)
        self.assertEqual(original["current_projection"]["state"], "removed")
        before_state, before_counts = self.repo._state, self.repo.counts

        fresh_intent = self.block(action="unblock", key="fresh-unblock", version=2)
        self.assertEqual(self.a.command(fresh_intent).code, "state_conflict")
        self.assertIs(self.repo._state, before_state)
        self.assertEqual(self.repo.counts, before_counts)

        replay = self.committed(self.a, original_intent)
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["receipt"], original["receipt"])
        self.assertEqual(replay["current_projection"], original["current_projection"])
        self.assertIs(self.repo._state, before_state)
        self.assertEqual(self.repo.counts, before_counts)

        reblocked = self.committed(self.a, self.block(key="reblock", version=2))
        self.assertEqual(reblocked["current_projection"]["state"], "active")
        self.assertEqual(reblocked["receipt"]["committed_version"], 3)

    def test_unmatch_keeps_stored_pair_after_either_participant_uuid_replacement(self):
        for changed_account in ("discovery-viewer", "discovery-jules"):
            for caller in ("a", "b"):
                with self.subTest(changed_account=changed_account, caller=caller):
                    self.reset()
                    match, first_like, second_like = self.match()
                    stored_pair = next(iter(self.repo._state.matches))
                    registry = self.fixture.registry
                    registry.replace(
                        tuple(
                            replace(row, account_uuid=str(uuid4()))
                            if row.account_id == AccountId(changed_account)
                            else row
                            for row in registry.identities
                        )
                    )
                    service = getattr(self, caller)
                    command = self.unmatch(match)
                    result = self.committed(service, command)
                    self.assertEqual(tuple(self.repo._state.matches), (stored_pair,))
                    self.assertEqual(
                        [row.match_id for row in self.repo._state.matches.values()],
                        [match["match_id"]],
                    )
                    self.assertEqual(result["receipt"]["committed_version"], 2)
                    self.assertEqual(result["current_projection"]["state"], "unmatched")
                    self.assertEqual(result["current_projection"]["version"], 2)
                    self.assertEqual(self.a.matches()[0]["state"], "unmatched")
                    self.assertEqual(self.b.matches()[0]["state"], "unmatched")
                    self.assertIsNone(self.committed(self.a, first_like)["current_projection"])
                    self.assertIsNone(self.committed(self.b, second_like)["current_projection"])
                    self.assertEqual(self.repo.counts["receipts"], 3)
                    self.assertEqual(
                        [
                            (event.kind, event.aggregate_id, event.aggregate_version)
                            for event in self.repo.events
                        ],
                        [
                            ("match_created", match["match_id"], 1),
                            ("contact_revoked", match["match_id"], 2),
                        ],
                    )
                    state_before_replay = self.repo._state
                    replay = self.committed(service, command)
                    self.assertTrue(replay["replayed"])
                    self.assertEqual(replay["receipt"], result["receipt"])
                    self.assertEqual(replay["current_projection"], result["current_projection"])
                    self.assertIs(self.repo._state, state_before_replay)

    def test_block_updates_stored_match_after_participant_uuid_replacement(self):
        for changed_account in ("discovery-viewer", "discovery-jules"):
            with self.subTest(changed_account=changed_account):
                self.reset()
                match, _, _ = self.match()
                stored_pair = next(iter(self.repo._state.matches))
                registry = self.fixture.registry
                registry.replace(
                    tuple(
                        replace(row, account_uuid=str(uuid4()))
                        if row.account_id == AccountId(changed_account)
                        else row
                        for row in registry.identities
                    )
                )
                self.committed(self.a, self.block())
                self.assertEqual(tuple(self.repo._state.matches), (stored_pair,))
                current = self.repo._state.matches[stored_pair]
                self.assertEqual((current.state, current.version), ("restricted", 2))
                self.assertEqual(current.match_id, match["match_id"])
                self.assertEqual(self.repo.counts["receipts"], 3)
                self.assertEqual(
                    Counter(event.kind for event in self.repo.events),
                    {"match_created": 1, "block_changed": 1, "contact_revoked": 1},
                )

    def test_replay_keeps_receipt_but_suppresses_revoked_original_direction_authority(self):
        for action in ("like", "pass"):
            for change in (
                "same_value_actor",
                "same_value_target",
                "remove_restore_target",
                "same_value_mapping",
                "same_value_registry",
                "registry_adapter",
                "source_adapter",
                "mapping_adapter",
                "block_unblock",
            ):
                with self.subTest(action=action, change=change):
                    self.reset()
                    intent = self.intent(action=action)
                    original = self.committed(self.a, intent)
                    self.assertIsNotNone(original["current_projection"])
                    actor = self.fixture.discovery.viewer
                    target = AccountId("discovery-jules")
                    if change in {"same_value_actor", "same_value_target"}:
                        affected = actor if change == "same_value_actor" else target
                        self.source.put_participant(self.source._participants[affected])
                    elif change == "remove_restore_target":
                        facts = self.source._participants[target]
                        self.source.remove_participant(target)
                        self.source.put_participant(facts)
                    elif change == "same_value_mapping":
                        mappings = self.fixture.discovery.mappings
                        mappings.put(target, mappings.get(target))
                    elif change == "same_value_registry":
                        self.fixture.registry.replace(self.fixture.registry.identities)
                    elif change == "registry_adapter":
                        self.a.registry = FixtureIdentityRegistry(self.fixture.registry.identities)
                    elif change == "source_adapter":
                        replacement = build_discovery_fixture()
                        replacement.source.acquire(actor, target)
                        self.a.discovery.source = replacement.source
                        self.a.discovery.batch = replace(
                            self.a.discovery.batch,
                            eligibility=replace(
                                self.a.discovery.batch.eligibility, repository=replacement.source
                            ),
                        )
                    elif change == "mapping_adapter":
                        replacement = build_discovery_fixture()
                        self.a.discovery.batch = replace(
                            self.a.discovery.batch, mappings=replacement.mappings
                        )
                    else:
                        self.committed(self.a, self.block())
                        self.committed(
                            self.a, self.block(action="unblock", key="unblock", version=1)
                        )
                        self.assertFalse(self.repo._state.directions[(actor, target)].matchable)
                    self.assertEqual(
                        self.a.discovery.batch.eligibility.evaluate(actor, target).state.value,
                        "ready",
                    )
                    state_before_replay, counts_before_replay = self.repo._state, self.repo.counts
                    replay = self.committed(self.a, intent)
                    self.assertTrue(replay["replayed"])
                    self.assertEqual(replay["receipt"], original["receipt"])
                    self.assertIsNone(replay["current_projection"])
                    self.assertIs(self.repo._state, state_before_replay)
                    self.assertEqual(self.repo.counts, counts_before_replay)

    def test_unrelated_candidate_change_preserves_original_direction_projection(self):
        for action in ("like", "pass"):
            with self.subTest(action=action):
                self.reset()
                intent = self.intent(action=action)
                original = self.committed(self.a, intent)
                unrelated = AccountId("discovery-morgan")
                self.source.put_participant(self.source._participants[unrelated])
                replay = self.committed(self.a, intent)
                self.assertEqual(replay["receipt"], original["receipt"])
                self.assertEqual(replay["current_projection"], original["current_projection"])

    def test_original_direction_retains_clock_and_policy_authority_for_reciprocity(self):
        for change in ("clock_advance", "policy_missing", "policy_restore"):
            with self.subTest(change=change):
                self.reset()
                first = self.intent()
                original = self.committed(self.a, first)
                if change == "clock_advance":
                    clock = self.fixture.discovery.clock
                    clock.set(clock.read() + 1)
                else:
                    self.a.policy_version = None
                    if change == "policy_restore":
                        self.a.policy_version = "development-interactions-1"
                replay = self.committed(self.a, first)
                self.assertEqual(replay["receipt"], original["receipt"])
                self.assertIsNone(replay["current_projection"])
                second = self.intent(self.b, "discovery-viewer", key="reciprocal")
                self.committed(self.b, second)
                self.assertEqual(self.repo.counts["directions"], 2)
                self.assertEqual(self.repo.counts["matches"], 0)
                self.assertEqual(self.repo.events, ())

    def test_match_retains_both_original_policies_and_clock_authority(self):
        for change in (
            "clock_advance",
            "clock_adapter",
            "a_missing",
            "b_missing",
            "a_restore",
            "b_restore",
        ):
            with self.subTest(change=change):
                self.reset()
                match, _, _ = self.match()
                clock = self.fixture.discovery.clock
                if change == "clock_advance":
                    clock.set(clock.read() + 1)
                elif change == "clock_adapter":
                    self.a.discovery.clock = type(clock)(clock.read())
                else:
                    service = self.a if change.startswith("a_") else self.b
                    service.policy_version = None
                    if change.endswith("restore"):
                        service.policy_version = "development-interactions-1"
                self.assertEqual(self.a.match_projection(match["match_id"])["state"], "restricted")
                self.assertFalse(self.b.contact_decision(match["match_id"])["match_current"])
                self.assertEqual(self.repo.counts["matches"], 1)
                self.assertEqual(
                    Counter(event.kind for event in self.repo.events),
                    {"match_created": 1, "contact_revoked": 1},
                )
                self.a.policy_version = self.b.policy_version = "development-interactions-1"
                self.assertEqual(self.b.match_projection(match["match_id"])["state"], "restricted")

    def test_incoming_private_action_preserves_held_discovery_page_and_batch(self):
        for mode in ("recommended", "broader"):
            for action in ("like", "pass"):
                with self.subTest(mode=mode, action=action):
                    self.reset()
                    incoming = self.intent(self.b, "discovery-viewer", action=action)
                    held = self.intent(mode=mode)
                    before, _ = self.a.page(mode=mode, request_id="retained")
                    self.committed(self.b, incoming)
                    after, _ = self.a.page(mode=mode, request_id="retained")
                    self.assertEqual(after, before)
                    self.committed(self.a, held, mode=mode)
                    self.assertEqual(self.repo.counts["matches"], int(action == "like"))

    def test_unrelated_actions_preserve_viewer_queue_but_reverse_block_invalidates(self):
        for change in ("other_like", "other_block", "reverse_block"):
            with self.subTest(change=change):
                self.reset()
                held = self.intent()
                before, _ = self.a.page(mode="recommended", request_id="retained")
                if change == "other_like":
                    other = self.intent(self.c, "discovery-viewer", key="other")
                    self.committed(self.c, other)
                elif change == "other_block":
                    self.committed(self.c, self.block("discovery-jules"))
                else:
                    self.committed(self.b, self.block("discovery-viewer"))
                after, _ = self.a.page(mode="recommended", request_id="retained")
                if change == "reverse_block":
                    self.assertEqual(after["state"], "reload_required")
                    self.assertEqual(self.a.command(held).code, "stale_batch")
                    self.committed(
                        self.b,
                        self.block("discovery-viewer", action="unblock", key="unblock", version=1),
                    )
                    self.assertEqual(self.a.command(held).code, "stale_batch")
                else:
                    self.assertEqual(after, before)
                    self.committed(self.a, held)
                    self.assertEqual(self.repo.counts["matches"], 0)

    def test_block_invalidates_viewer_registered_during_final_callback(self):
        self.source.acquire(self.fixture.discovery.viewer, AccountId("discovery-jules"))
        observed = []
        self.a.before_commit = lambda: observed.append(
            self.b.page(mode="recommended", request_id="during-commit")
        )
        self.committed(self.a, self.block())
        self.assertEqual(observed[0][0]["state"], "ready")
        self.assertIsNotNone(observed[0][1])
        after, batch = self.b.page(mode="recommended", request_id="after-commit")
        self.assertEqual(after["state"], "reload_required")
        self.assertIsNone(batch)

    def test_unmatch_missing_other_registry_row_uses_retained_match_identity(self):
        for caller, missing_account in (("a", "discovery-jules"), ("b", "discovery-viewer")):
            with self.subTest(caller=caller):
                self.reset()
                match, _, _ = self.match()
                service = getattr(self, caller)
                original_rows = self.fixture.registry.identities
                self.fixture.registry.replace(
                    tuple(
                        row for row in original_rows if row.account_id != AccountId(missing_account)
                    )
                )
                command = self.unmatch(match)
                original = self.committed(service, command)
                self.assertEqual(
                    original["receipt"],
                    {
                        "outcome_code": "unmatched",
                        "object_ref": match["match_id"],
                        "committed_version": 2,
                    },
                )
                self.assertIsNone(original["current_projection"])
                self.assertEqual(self.repo.counts["matches"], 1)
                self.assertEqual(self.repo.counts["receipts"], 3)
                self.assertEqual(
                    Counter(event.kind for event in self.repo.events),
                    {"match_created": 1, "contact_revoked": 1},
                )
                state_before_replay = self.repo._state
                replay = self.committed(service, command)
                self.assertTrue(replay["replayed"])
                self.assertEqual(replay["receipt"], original["receipt"])
                self.assertIsNone(replay["current_projection"])
                self.assertIs(self.repo._state, state_before_replay)
                self.assertEqual(
                    service.command(self.unmatch(match, key="stale")).code, "stale_version"
                )
                conflicting = self.unmatch(match, version=2)
                self.assertEqual(service.command(conflicting).code, "idempotency_conflict")
                self.assertEqual(self.c.command(command).code, "unavailable")
                self.assertIs(self.repo._state, state_before_replay)
                # A current trusted session is still required, even for receipt recovery.
                actor = service.discovery.authority.read()[0]
                facts = self.source._participants[actor]
                self.source.put_participant(replace(facts, session_state="revoked"))
                self.assertEqual(service.command(command).code, "unavailable")
                self.assertIs(self.repo._state, state_before_replay)
                self.source.put_participant(facts)
                self.fixture.registry.replace(original_rows)
                restored = self.committed(service, command)
                self.assertEqual(restored["receipt"], original["receipt"])
                self.assertEqual(restored["current_projection"]["state"], "unmatched")
                self.assertIs(self.repo._state, state_before_replay)
                repeated = self.committed(service, self.unmatch(match, key="repeat", version=2))
                self.assertEqual(repeated["receipt"]["committed_version"], 2)
                self.assertEqual(len(self.repo.events), 2)

    def test_other_registry_removal_during_unmatch_aborts_then_retry_can_cleanup(self):
        for caller, missing_account in (("a", "discovery-jules"), ("b", "discovery-viewer")):
            with self.subTest(caller=caller):
                self.reset()
                match, _, _ = self.match()
                service = getattr(self, caller)
                retained_rows = tuple(
                    row
                    for row in self.fixture.registry.identities
                    if row.account_id != AccountId(missing_account)
                )
                before = self.repo._state
                service.before_commit = lambda rows=retained_rows: self.fixture.registry.replace(
                    rows
                )
                command = self.unmatch(match)
                self.assertEqual(service.command(command).code, "stale_version")
                self.assertIs(self.repo._state, before)
                self.assertEqual(self.repo.counts["pending"], 0)
                service.before_commit = lambda: None
                result = self.committed(service, command)
                self.assertIsNone(result["current_projection"])
                self.assertEqual(result["receipt"]["committed_version"], 2)
                self.assertEqual(self.repo.counts["matches"], 1)
                self.assertEqual(len(self.repo.events), 2)

    def test_unmatch_projection_withholds_registry_row_removed_by_final_lookup(self):
        for caller, missing_account in (("a", "discovery-jules"), ("b", "discovery-viewer")):
            with self.subTest(caller=caller):
                self.reset()
                match, _, _ = self.match()
                service = getattr(self, caller)
                registry = self.fixture.registry
                original_account = registry.account
                target = AccountId(missing_account)
                lookup_count = 0

                def remove_on_projection(
                    account, original_account=original_account, target=target, registry=registry
                ):
                    nonlocal lookup_count
                    result = original_account(account)
                    if account == target:
                        lookup_count += 1
                        if lookup_count == 2:
                            registry.replace(
                                tuple(
                                    row for row in registry.identities if row.account_id != target
                                )
                            )
                    return result

                command = self.unmatch(match)
                with patch.object(registry, "account", side_effect=remove_on_projection):
                    result = self.committed(service, command)
                self.assertIsNone(registry.account(target))
                self.assertIsNone(result["current_projection"])
                self.assertEqual(result["receipt"]["committed_version"], 2)
                self.assertEqual(next(iter(self.repo._state.matches.values())).state, "unmatched")
                self.assertEqual(len(self.repo.events), 2)
                before_replay = self.repo._state
                replay = self.committed(service, command)
                self.assertEqual(replay["receipt"], result["receipt"])
                self.assertIsNone(replay["current_projection"])
                self.assertIs(self.repo._state, before_replay)

    def two_matches(self):
        first, _, _ = self.match()
        self.committed(self.a, self.intent(target="discovery-morgan", key="like-morgan"))
        self.committed(self.c, self.intent(self.c, "discovery-viewer", key="morgan-reciprocal"))
        matches = self.a.matches()
        self.assertEqual(len(matches), 2)
        second = next(row for row in matches if row["match_id"] != first["match_id"])
        return first, second

    def test_match_list_rechecks_earlier_projection_after_later_source_callback(self):
        for earlier_state in ("active", "restricted", "unmatched"):
            with self.subTest(earlier_state=earlier_state):
                self.reset()
                first, second = self.two_matches()
                earlier_target = AccountId("discovery-jules")
                if earlier_state == "unmatched":
                    self.committed(self.a, self.unmatch(first))
                elif earlier_state == "restricted":
                    self.source.put_participant(self.source._participants[earlier_target])
                    self.assertEqual(
                        self.a.match_projection(first["match_id"])["state"], "restricted"
                    )
                original_acquire = self.source.acquire
                fired = False

                def remove_earlier(
                    viewer,
                    candidate,
                    original_acquire=original_acquire,
                    earlier_target=earlier_target,
                ):
                    nonlocal fired
                    result = original_acquire(viewer, candidate)
                    if AccountId("discovery-morgan") in (viewer, candidate) and not fired:
                        fired = True
                        self.source.remove_participant(earlier_target)
                    return result

                with patch.object(self.source, "acquire", side_effect=remove_earlier):
                    projected = self.a.matches()
                self.assertTrue(fired)
                self.assertEqual([row["match_id"] for row in projected], [second["match_id"]])

    def test_match_list_survives_unrelated_private_commit_in_later_callback(self):
        first, second = self.two_matches()
        iris, noor = AccountId("discovery-iris"), AccountId("discovery-noor")
        self.source.observe_block(iris, noor, BlockState.CLEAR)
        self.source.observe_block(noor, iris, BlockState.CLEAR)
        other = self.fixture.session(iris, "private-actor")
        private_intent = self.intent(other, "discovery-noor", key="private-like")
        original_acquire = self.source.acquire
        fired = False

        def private_commit(viewer, candidate):
            nonlocal fired
            result = original_acquire(viewer, candidate)
            if AccountId("discovery-morgan") in (viewer, candidate) and not fired:
                fired = True
                self.committed(other, private_intent)
            return result

        with patch.object(self.source, "acquire", side_effect=private_commit):
            projected = self.a.matches()
        self.assertTrue(fired)
        self.assertEqual(
            [row["match_id"] for row in projected], [first["match_id"], second["match_id"]]
        )
        self.assertTrue(all(row["state"] == "active" for row in projected))
        self.assertEqual(self.repo.counts["directions"], 5)

    def swap_jules_morgan_profile_uuids(self):
        registry = self.fixture.registry
        jules = registry.account(AccountId("discovery-jules"))
        morgan = registry.account(AccountId("discovery-morgan"))
        registry.replace(
            tuple(
                replace(row, profile_uuid=morgan.profile_uuid)
                if row == jules
                else replace(row, profile_uuid=jules.profile_uuid)
                if row == morgan
                else row
                for row in registry.identities
            )
        )

    def test_block_replay_cannot_project_a_reassigned_profile_target(self):
        command = self.block()
        original = self.committed(self.a, command)
        self.committed(self.a, self.block("discovery-morgan", key="block-morgan"))
        self.committed(
            self.a,
            self.block("discovery-morgan", action="unblock", key="unblock-morgan", version=1),
        )
        original_rows = self.fixture.registry.identities
        self.swap_jules_morgan_profile_uuids()
        before = self.repo._state
        replay = self.committed(self.a, command)
        self.assertEqual(replay["receipt"], original["receipt"])
        self.assertIsNone(replay["current_projection"])
        self.assertIs(self.repo._state, before)
        self.fixture.registry.replace(original_rows)
        restored = self.committed(self.a, command)
        self.assertEqual(restored["current_projection"], original["current_projection"])
        self.assertEqual(restored["receipt"], original["receipt"])
        self.assertIs(self.repo._state, before)

    def test_interaction_replay_cannot_project_new_direction_for_reassigned_uuid(self):
        for original_action, new_action in (("like", "pass"), ("pass", "like")):
            with self.subTest(original_action=original_action):
                self.reset()
                command = self.intent(action=original_action)
                original = self.committed(self.a, command)
                self.swap_jules_morgan_profile_uuids()
                new_command = self.intent(
                    target="discovery-morgan", key="new-target", action=new_action
                )
                self.assertEqual(new_command["target_profile_id"], command["target_profile_id"])
                self.committed(self.a, new_command)
                before = self.repo._state
                replay = self.committed(self.a, command)
                self.assertEqual(replay["receipt"], original["receipt"])
                self.assertIsNone(replay["current_projection"])
                self.assertIs(self.repo._state, before)

    def test_result_time_registry_rebind_suppresses_block_projection(self):
        command = self.block()
        original = self.committed(self.a, command)
        original_account = self.fixture.registry.account
        actor = self.fixture.discovery.viewer
        actor_lookups = 0

        def rebind_during_result(account):
            nonlocal actor_lookups
            result = original_account(account)
            if account == actor:
                actor_lookups += 1
                if actor_lookups == 2:
                    self.swap_jules_morgan_profile_uuids()
            return result

        before = self.repo._state
        with patch.object(self.fixture.registry, "account", side_effect=rebind_during_result):
            replay = self.committed(self.a, command)
        self.assertGreaterEqual(actor_lookups, 2)
        self.assertEqual(replay["receipt"], original["receipt"])
        self.assertIsNone(replay["current_projection"])
        self.assertIs(self.repo._state, before)

    def test_match_list_rechecks_both_block_directions_even_after_unblock(self):
        for earlier_state in ("active", "restricted", "unmatched"):
            for caller in ("a", "b"):
                for remove_block in (False, True):
                    with self.subTest(state=earlier_state, caller=caller, remove=remove_block):
                        self.reset()
                        first, second = self.two_matches()
                        if earlier_state == "unmatched":
                            self.committed(self.a, self.unmatch(first))
                        elif earlier_state == "restricted":
                            target = AccountId("discovery-jules")
                            self.source.put_participant(self.source._participants[target])
                            self.a.match_projection(first["match_id"])
                        service = getattr(self, caller)
                        target_name = "discovery-jules" if caller == "a" else "discovery-viewer"
                        original_acquire = self.source.acquire
                        fired = False

                        def change_block(
                            viewer,
                            candidate,
                            service=service,
                            target_name=target_name,
                            original_acquire=original_acquire,
                            remove_block=remove_block,
                        ):
                            nonlocal fired
                            result = original_acquire(viewer, candidate)
                            if AccountId("discovery-morgan") in (viewer, candidate) and not fired:
                                fired = True
                                self.committed(service, self.block(target_name))
                                if remove_block:
                                    self.committed(
                                        service,
                                        self.block(
                                            target_name, action="unblock", key="unblock", version=1
                                        ),
                                    )
                            return result

                        with patch.object(self.source, "acquire", side_effect=change_block):
                            projected = self.a.matches()
                        self.assertTrue(fired)
                        self.assertEqual(
                            [row["match_id"] for row in projected], [second["match_id"]]
                        )
