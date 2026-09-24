"""P05.2 independent facts, finite queues, closed projection and final-callback regressions."""

import importlib.util
import json
from collections import Counter
from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch

from glow_domain.compatibility import FixtureCase
from glow_domain.discovery import (
    MAX_CANDIDATES,
    PAGE_SIZE,
    QUEUE_LIFETIME_MS,
    DiscoveryMember,
    FixtureDiscoveryAuthority,
    FixtureDiscoveryService,
)
from glow_domain.discovery_fixtures import (
    CORPUS_PATH,
    PROVENANCE,
    build_discovery_fixture,
)
from glow_domain.eligibility import BlockState
from glow_domain.eligibility_facts import DEVELOPMENT_POLICY
from glow_domain.fixture_coherence import FixtureReadGuard
from glow_domain.identity import AccountId, EngineChartReference
from glow_domain.provider_contracts import ExpectedProviderFailure, FailureCode
from glow_domain.provider_fixtures import ScriptedCompatibilityProvider
from glow_domain.trusted_eligibility import EvidenceUnavailable

spec = importlib.util.spec_from_file_location(
    "discovery_contracts", CORPUS_PATH.parents[1] / "runtime.py"
)
contract_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract_runtime)


class DiscoveryTests(TestCase):
    def setUp(self):
        self.network = patch("socket.socket", side_effect=AssertionError("No live adapters"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.fixture = build_discovery_fixture()
        self.corpus = json.loads(CORPUS_PATH.read_text())

    def page(self, **overrides):
        return self.fixture.service.page(
            **{
                "viewer": self.fixture.viewer,
                "session_id": self.fixture.session_id,
                "mode": "recommended",
                "request_id": "request-1",
                **overrides,
            }
        )

    def assert_contract(self, page):
        self.assertTrue(
            contract_runtime.valid("development", "DevelopmentDiscoveryPage", page), page
        )

    def drain(self, mode="recommended"):
        pages, cursor = [], None
        for number in range(12):
            page = self.page(mode=mode, cursor=cursor, request_id=f"request-{number}")
            self.assert_contract(page)
            pages.append(page)
            cursor = page["next_cursor"]
            if cursor is None:
                return pages
        self.fail("Finite fixture queue cycled.")

    def test_shared_population_decisions_order_states_attempts_and_contract(self):
        expected = self.corpus["expected"]
        for mode in ("recommended", "broader"):
            with self.subTest(mode=mode):
                self.fixture = build_discovery_fixture()
                for identity, state in expected["pair_states"].items():
                    decision = self.fixture.service.batch.eligibility.evaluate(
                        self.fixture.viewer,
                        AccountId(identity),
                    )
                    self.assertEqual(decision.state.value, state)
                pages = self.drain(mode)
                profiles = [card["profile_id"] for page in pages for card in page["items"]]
                self.assertEqual(profiles, expected[f"{mode}_profile_ids"])
                self.assertEqual(len(profiles), len(set(profiles)))
                self.assertEqual([p["state"] for p in pages], expected["page_states_by_mode"][mode])
                self.assertEqual(len(pages), 3)
                self.assertIsNone(pages[-1]["next_cursor"])
                counts = Counter(identity.value for identity in self.fixture.provider.calls)
                self.assertEqual(
                    dict(counts),
                    {
                        identity: attempts
                        for identity, attempts in expected["provider_attempts_by_account"].items()
                        if attempts
                    },
                )

    def test_rejected_pairs_never_read_mappings_or_provider_in_either_mode(self):
        for identity, state in self.corpus["expected"]["pair_states"].items():
            if state == "ready":
                continue
            for mode in ("recommended", "broader"):
                with self.subTest(identity=identity, mode=mode):
                    self.fixture = build_discovery_fixture()
                    source = self.fixture.source
                    member = next(m for m in source.select(mode) if m.account_id.value == identity)
                    source.replace_population((member,))
                    with patch.object(
                        self.fixture.mappings, "get", wraps=self.fixture.mappings.get
                    ) as reads:
                        page = self.page(mode=mode)
                    self.assertEqual(page["state"], "empty")
                    self.assertEqual(page["items"], [])
                    self.assertEqual(reads.call_count, 0)
                    self.assertEqual(self.fixture.provider.total_calls, 0)

    def test_missing_policy_wrong_pair_and_asserted_client_readiness_fail_closed(self):
        self.fixture.source.set_policy(None)
        with patch.object(self.fixture.mappings, "get", wraps=self.fixture.mappings.get) as reads:
            self.assertEqual(self.page()["state"], "reload_required")
        self.assertEqual(reads.call_count, 0)
        self.assertEqual(self.fixture.provider.total_calls, 0)
        self.fixture = build_discovery_fixture()
        original = self.fixture.source.acquire

        def wrong(viewer, candidate):
            value = original(viewer, candidate)
            return (
                replace(value, candidate=replace(value.candidate, account_id=viewer))
                if value
                else None
            )

        with (
            patch.object(self.fixture.source, "acquire", side_effect=wrong),
            patch.object(
                self.fixture.mappings,
                "get",
                wraps=self.fixture.mappings.get,
            ) as reads,
        ):
            self.assertEqual(self.page()["items"], [])
        self.assertEqual(reads.call_count, 0)
        self.assertEqual(self.fixture.provider.total_calls, 0)
        with self.assertRaises(TypeError):
            self.fixture.service.page(
                viewer=self.fixture.viewer,
                session_id=self.fixture.session_id,
                mode="broader",
                request_id="request",
                ready=True,
            )

    def test_wrong_provider_pair_provenance_and_security_failures_suppress_projection(self):
        for kind in ("pair", "provenance"):
            with self.subTest(kind=kind):
                self.fixture = build_discovery_fixture()
                original = self.fixture.provider.evaluate

                def wrong_result(request, key, original=original, kind=kind):
                    output = original(request, key)
                    if kind == "pair":
                        return replace(output, key=replace(output.key, pair=output.key.pair[::-1]))
                    provenance = replace(output.result.provenance, adapter_version="wrong-adapter")
                    return replace(
                        output,
                        key=replace(output.key, provenance=provenance),
                        result=replace(output.result, provenance=provenance),
                    )

                with (
                    patch.object(self.fixture.provider, "evaluate", side_effect=wrong_result),
                    patch.object(
                        self.fixture.source,
                        "project",
                        wraps=self.fixture.source.project,
                    ) as projections,
                ):
                    page = self.page(mode="broader")
                self.assertEqual(page["items"], [])
                self.assertEqual(page["state"], "partial")
                self.assertEqual(projections.call_count, 0)
                self.assertEqual(self.fixture.provider.total_calls, 2)
                self.assert_contract(page)
        for failure in FailureCode:
            with self.subTest(failure=failure):
                self.fixture = build_discovery_fixture()
                with patch.object(
                    self.fixture.provider, "evaluate", side_effect=ExpectedProviderFailure(failure)
                ) as calls:
                    page = self.page(mode="broader")
                allowed = failure in {FailureCode.TIMEOUT, FailureCode.OUTAGE}
                self.assertEqual(len(page["items"]), 2 if allowed else 0)
                self.assertEqual(calls.call_count, 6 if allowed else 2)
                self.assertEqual(page["state"], "partial")
                self.assert_contract(page)

    def test_repeated_reads_stable_handles_refresh_and_independent_modes(self):
        first = self.page()
        repeat = self.page(request_id="retry")
        self.assertEqual(first["items"], repeat["items"])
        self.assertEqual(first["queue_id"], repeat["queue_id"])
        self.assertEqual(first["next_cursor"], repeat["next_cursor"])
        second = self.page(cursor=first["next_cursor"])
        self.assertEqual(second, self.page(cursor=first["next_cursor"]))
        broader = self.page(mode="broader")
        self.assertNotEqual(first["queue_id"], broader["queue_id"])
        self.assertEqual(second, self.page(cursor=first["next_cursor"]))
        refreshed = self.page(refresh=True)
        self.assertNotEqual(first["queue_id"], refreshed["queue_id"])
        self.assertEqual(refreshed["items"], first["items"])
        self.assertEqual(self.page(cursor=first["next_cursor"])["state"], "reload_required")
        self.assertEqual(broader["queue_id"], self.page(mode="broader")["queue_id"])

    def test_cursor_malformed_wrong_viewer_session_mode_and_expiration(self):
        first = self.page()
        calls = self.fixture.provider.total_calls
        for cursor in ("not-a-cursor", "", first["queue_id"], first["next_cursor"] + "\n"):
            with self.subTest(cursor=cursor):
                self.assertEqual(self.page(cursor=cursor)["state"], "reload_required")
        self.assertEqual(
            self.page(mode="broader", cursor=first["next_cursor"])["state"], "reload_required"
        )
        self.assertEqual(self.fixture.provider.total_calls, calls)
        for change in ({"viewer": AccountId("someone-else")}, {"session_id": "another-session"}):
            self.fixture = build_discovery_fixture()
            first = self.page()
            self.assertEqual(self.page(cursor=first["next_cursor"], **change)["items"], [])
            self.assertEqual(self.fixture.service._queues, {})
        self.fixture = build_discovery_fixture()
        first = self.page()
        self.fixture.clock.set(self.fixture.clock.read() + QUEUE_LIFETIME_MS)
        self.assertEqual(self.page(cursor=first["next_cursor"])["state"], "reload_required")
        self.assertEqual(self.page(refresh=True)["items"], first["items"])

    def test_scope_replacement_logout_same_value_source_and_clock_restore_revoke(self):
        for kind in (
            "same-facts",
            "remove-restore",
            "policy",
            "same-clock",
            "scope",
            "new-scope",
            "source",
            "logout",
        ):
            with self.subTest(kind=kind):
                self.fixture = build_discovery_fixture()
                first = self.page()
                f, source = self.fixture, self.fixture.source
                iris = source._participants[AccountId("discovery-iris")]
                if kind == "same-facts":
                    source.put_participant(iris)
                elif kind == "remove-restore":
                    source.remove_participant(iris.account_id)
                    source.put_participant(iris)
                elif kind == "policy":
                    source.set_policy(None)
                    source.set_policy(DEVELOPMENT_POLICY)
                elif kind == "same-clock":
                    f.clock.set(f.clock.read())
                elif kind == "scope":
                    f.authority.replace(f.viewer, f.session_id)
                elif kind == "new-scope":
                    f.service.authority = FixtureDiscoveryAuthority(f.viewer, f.session_id)
                elif kind == "source":
                    f.service.source = build_discovery_fixture().source
                elif kind == "logout":
                    f.authority.replace(None, None)
                calls = f.provider.total_calls
                page = self.page(cursor=first["next_cursor"])
                self.assertEqual(page["items"], [])
                self.assertIsNone(page["next_cursor"])
                self.assertEqual(page["state"], "reload_required")
                self.assertEqual(f.provider.total_calls, calls)

    def test_source_change_during_last_projection_discards_earlier_card_but_retains_control(self):
        for kind in (
            "consent",
            "same-facts",
            "media",
            "mapping",
            "mapping-restore",
            "remove-restore",
            "block",
        ):
            with self.subTest(kind=kind):
                self.fixture = build_discovery_fixture()
                f, source = self.fixture, self.fixture.source
                iris = source._participants[AccountId("discovery-iris")]
                original_project = source.project
                fired = []

                def project(
                    member,
                    original_project=original_project,
                    fired=fired,
                    kind=kind,
                    source=source,
                    iris=iris,
                    f=f,
                ):
                    card = original_project(member)
                    if member.account_id == AccountId("discovery-jules"):
                        fired.append(True)
                        if kind == "consent":
                            source.put_participant(replace(iris, consent_state="withdrawn"))
                        elif kind == "same-facts":
                            source.put_participant(iris)
                        elif kind == "media":
                            source.put_participant(replace(iris, approved_media=()))
                        elif kind in {"mapping", "mapping-restore"}:
                            mapping = f.mappings.get(iris.account_id)
                            f.mappings.put(iris.account_id, None)
                            if kind == "mapping-restore":
                                f.mappings.put(iris.account_id, mapping)
                        elif kind == "remove-restore":
                            source.remove_participant(iris.account_id)
                            source.put_participant(iris)
                        elif kind == "block":
                            source.observe_block(iris.account_id, f.viewer, BlockState.BLOCKED)
                    return card

                with patch.object(source, "project", side_effect=project):
                    page = self.page(mode="broader")
                self.assertEqual(fired, [True])
                self.assertEqual([p["profile_id"] for p in page["items"]], ["profile-jules"])
                self.assertEqual(page["state"], "partial")
                self.assertIsNone(page["next_cursor"])
                self.assertEqual(f.provider.total_calls, 2)
                self.assertEqual(self.page(mode="broader")["state"], "reload_required")
                self.assert_contract(page)

    def test_last_projection_shared_viewer_clock_or_source_replacement_discards_every_card(self):
        for kind in ("viewer", "viewer-mapping", "clock", "authority", "source"):
            with self.subTest(kind=kind):
                self.fixture = build_discovery_fixture()
                f, source = self.fixture, self.fixture.source
                original_project = source.project

                def project(
                    member, original_project=original_project, kind=kind, source=source, f=f
                ):
                    card = original_project(member)
                    if member.account_id == AccountId("discovery-jules"):
                        if kind == "viewer":
                            source.put_participant(source._participants[f.viewer])
                        elif kind == "viewer-mapping":
                            f.mappings.put(f.viewer, f.mappings.get(f.viewer))
                        elif kind == "clock":
                            f.clock.set(f.clock.read())
                        elif kind == "authority":
                            f.authority.replace(f.viewer, f.session_id)
                        elif kind == "source":
                            f.service.source = build_discovery_fixture().source
                    return card

                with patch.object(source, "project", side_effect=project):
                    page = self.page(mode="broader")
                self.assertEqual(page["items"], [])
                self.assertIsNone(page["next_cursor"])
                self.assertEqual(page["state"], "reload_required")
                self.assertEqual(f.provider.total_calls, 2)

    def test_missing_unavailable_empty_guard_participation_prevents_provider_work(self):
        for owner, attribute in (
            ("source", "publication_guard"),
            ("source", "population_guard"),
            ("mappings", "publication_guard"),
            ("clock", "publication_guard"),
            ("authority", "publication_guard"),
        ):
            for value in (None, lambda *args: None, lambda *args: FixtureReadGuard(())):
                with self.subTest(owner=owner, attribute=attribute, value=value):
                    self.fixture = build_discovery_fixture()
                    setattr(getattr(self.fixture, owner), attribute, value)
                    with patch.object(
                        self.fixture.mappings, "get", wraps=self.fixture.mappings.get
                    ) as reads:
                        page = self.page()
                    self.assertEqual(page["state"], "reload_required")
                    self.assertEqual(reads.call_count, 0)
                    self.assertEqual(self.fixture.provider.total_calls, 0)
        self.fixture = build_discovery_fixture()
        with patch.object(
            self.fixture.source, "population_guard", side_effect=EvidenceUnavailable()
        ):
            self.assertEqual(self.page()["state"], "reload_required")

    def test_projection_whitelist_mixed_media_bindings_and_no_private_payload(self):
        source = self.fixture.source
        identity = AccountId("discovery-iris")
        person = source._participants[identity]
        good = person.approved_media[0]
        for bad in (
            replace(good, generation=2, delivery_ref="fixture-approved-other"),
            replace(good, owner_id=self.fixture.viewer, delivery_ref="fixture-approved-other"),
            replace(good, profile_id="another-profile", delivery_ref="fixture-approved-other"),
            replace(good, state="quarantined", delivery_ref="fixture-approved-other"),
        ):
            bad = replace(bad, asset_id="asset-invalid")
            with self.subTest(bad=bad):
                self.fixture = build_discovery_fixture()
                source = self.fixture.source
                source.put_participant(replace(person, approved_media=(good, bad)))
                page = self.page(mode="broader")
                iris = next(
                    (item for item in page["items"] if item["profile_id"] == "profile-iris"), None
                )
                if bad.state == "quarantined":
                    self.assertEqual(iris["media_delivery_refs"], [good.delivery_ref])
                else:
                    self.assertIsNone(iris)
                self.assertNotIn("fixture-approved-other", json.dumps(page))
                self.assert_contract(page)
        rendered = json.dumps(page)
        for private in (
            "birth_date",
            "engine_reference",
            "accepted_options",
            "source_id",
            "blocks",
            "fixture-chart",
        ):
            self.assertNotIn(private, rendered)
        self.assertNotIn("1990-06-15", rendered)
        self.assertTrue(
            all(
                set(card)
                == {
                    "profile_id",
                    "display_name",
                    "age",
                    "summary",
                    "compatibility",
                    "media_delivery_refs",
                }
                for card in page["items"]
            )
        )

    def test_malformed_projection_and_identity_rejected_without_leaking(self):
        original = self.fixture.source.project
        with patch.object(
            self.fixture.source,
            "project",
            side_effect=lambda member: {
                **original(member),
                "birth_date": "private-birth-input",
            },
        ):
            page = self.page()
        self.assertEqual(page["items"], [])
        self.assertNotIn("private-birth-input", json.dumps(page))
        for identity in ("request/invalid", "request\n", "x" * 129):
            with self.assertRaises(ValueError):
                self.page(request_id=identity)
        with self.assertRaises(ValueError):
            self.page(viewer=AccountId("\ufeff"))
        for name, value in (
            ("age", 121),
            ("display_name", "x" * 81),
            ("summary", "x" * 501),
            ("display_name", "\ufeff"),
            ("summary", "\ufeff"),
        ):
            self.fixture = build_discovery_fixture()
            original = self.fixture.source.project
            with patch.object(
                self.fixture.source,
                "project",
                side_effect=lambda member, original=original, name=name, value=value: {
                    **original(member),
                    name: value,
                },
            ):
                page = self.page()
            self.assertEqual(page["items"], [])
            self.assert_contract(page)

    def test_selection_and_retention_bounds_including_many_refreshes(self):
        source, f = self.fixture.source, self.fixture
        sample = source._participants[AccountId("discovery-iris")]
        sample_map = f.mappings.get(sample.account_id)
        members = []
        for index in range(MAX_CANDIDATES):
            account = AccountId(f"bounded-{index:02}")
            profile = f"profile-bounded-{index:02}"
            media = replace(
                sample.approved_media[0],
                asset_id=f"asset-{index}",
                owner_id=account,
                profile_id=profile,
                delivery_ref=f"fixture-approved-bounded-{index}",
            )
            facts = replace(
                sample,
                account_id=account,
                source_id=f"source-{index}",
                profile_id=profile,
                approved_media=(media,),
            )
            source.put_participant(facts)
            source.observe_block(f.viewer, account, BlockState.CLEAR)
            source.observe_block(account, f.viewer, BlockState.CLEAR)
            f.mappings.put(
                account,
                replace(
                    sample_map,
                    account_id=account,
                    engine_reference=EngineChartReference(f"fixture-chart-{index}"),
                ),
            )
            f.provider.providers[account] = ScriptedCompatibilityProvider(
                "test", PROVENANCE, (FixtureCase.PENDING,)
            )
            members.append(DiscoveryMember(account, profile, 1))
        source.replace_population(tuple(members))
        with patch.object(source, "acquire", wraps=source.acquire) as reads:
            pages = self.drain()
        self.assertEqual(len(pages), MAX_CANDIDATES // PAGE_SIZE)
        self.assertEqual(len(set(call.args[1] for call in reads.call_args_list)), MAX_CANDIDATES)
        self.assertEqual(f.provider.total_calls, MAX_CANDIDATES)
        with self.assertRaises(ValueError):
            source.replace_population(tuple(members) + (members[0],))
        for index in range(80):
            self.page(refresh=True, mode="recommended" if index % 2 else "broader")
        self.assertEqual(len(f.service._queues), 2)
        self.assertLessEqual(len(f.provider.calls), 120)
        self.assertTrue(
            all(
                len(provider._keys) <= 2 and len(provider._results) <= 2
                for provider in f.provider.providers.values()
            )
        )
        self.assertTrue(
            all(
                len(queue.members) <= 20 and len(queue.cursors) <= 9
                for queue in f.service._queues.values()
            )
        )

    def test_fixture_production_guard_and_pending_only_control(self):
        with self.assertRaises(ValueError):
            build_discovery_fixture(environment="production")
        with self.assertRaises(ValueError):
            FixtureDiscoveryService(
                environment="production",
                source=self.fixture.source,
                batch=self.fixture.service.batch,
                authority=self.fixture.authority,
                clock=self.fixture.clock,
            )
        self.assertEqual(self.page(mode="broader")["state"], "ready")
        self.assertEqual(self.fixture.provider.total_calls, 2)
        self.assertTrue(
            all(
                card["compatibility"] == {"status": "pending", "source": "fixture"}
                for card in self.page(mode="broader")["items"]
            )
        )
