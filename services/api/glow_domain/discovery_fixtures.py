"""Repository-fixture composition. Never mounted as a production/HTTP trust adapter."""

import json
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .compatibility import CompatibilityRequest, FixtureCase, FixtureProvenance
from .discovery import (
    DiscoveryMember,
    FixtureDiscoveryAuthority,
    FixtureDiscoveryClock,
    FixtureDiscoveryService,
    FixtureDiscoverySource,
)
from .eligibility import BlockState
from .eligibility_facts import DevelopmentEligibilityPolicy, MediaFact, ParticipantFacts
from .fixture_coherence import FixtureChartMappingRepository
from .identity import AccountId, ChartMapping, ChartMappingState, EngineChartReference
from .provider_contracts import BoundCompatibilityResult, FailureCode, RetryPolicy
from .provider_fixtures import FixtureCompatibilityBatchService, ScriptedCompatibilityProvider
from .trusted_eligibility import TrustedEligibilityService

CORPUS_PATH = Path(__file__).resolve().parents[3] / "packages/contracts/fixtures/discovery-v1.json"
PROVENANCE = FixtureProvenance("discovery-v1", "fixture-adapter-1", "synthetic-1", "fixture-1")


def participant_from_fixture(value: dict[str, Any]) -> ParticipantFacts:
    """Load bundled internal raw facts, never request-shaped authorization."""
    fields = dict(value)
    fields["account_id"] = AccountId(fields["account_id"])
    if fields["accepted_options"] is not None:
        fields["accepted_options"] = tuple(fields["accepted_options"])
    if fields["approved_media"] is not None:
        fields["approved_media"] = tuple(
            MediaFact(**{**asset, "owner_id": AccountId(asset["owner_id"])})
            for asset in fields["approved_media"]
        )
    return ParticipantFacts(**fields)


def mapping_from_fixture(value: dict[str, Any]) -> ChartMapping:
    return ChartMapping(
        AccountId(value["account_id"]),
        ChartMappingState(value["state"]),
        EngineChartReference(value["engine_reference"]) if value["engine_reference"] else None,
        value["birth_input_version"],
        value["mapping_version"],
    )


class PopulationCompatibilityProvider:
    """One existing scripted provider per independent fictional candidate."""

    def __init__(self, environment: str, states: dict[AccountId, str]) -> None:
        scripts: dict[str, tuple[FailureCode | FixtureCase, ...]] = {
            "ready": (FixtureCase.READY_SYNTHETIC,),
            "pending": (FixtureCase.PENDING,),
            "unavailable": (FixtureCase.UNAVAILABLE,),
            "error": (FailureCode.OUTAGE,),
        }
        self.providers = {
            identity: ScriptedCompatibilityProvider(environment, PROVENANCE, scripts[state])
            for identity, state in states.items()
        }
        self.calls: deque[AccountId] = deque(maxlen=120)
        self.total_calls = 0

    def evaluate(
        self, request: CompatibilityRequest, idempotency_key: str
    ) -> BoundCompatibilityResult:
        self.calls.append(request.candidate.account_id)
        self.total_calls += 1
        provider = self.providers[request.candidate.account_id]
        # Two retained keys per candidate match the two-mode queue bound. An
        # older in-memory replay cache entry is disposable, never authorization.
        if idempotency_key not in provider._keys and len(provider._keys) >= 2:
            oldest = next(iter(provider._keys))
            provider._keys.pop(oldest)
            provider._results.pop(oldest, None)
        return provider.evaluate(request, idempotency_key)


@dataclass(frozen=True)
class DiscoveryFixture:
    service: FixtureDiscoveryService
    source: FixtureDiscoverySource
    mappings: FixtureChartMappingRepository
    provider: PopulationCompatibilityProvider
    authority: FixtureDiscoveryAuthority
    clock: FixtureDiscoveryClock
    viewer: AccountId
    session_id: str


def build_discovery_fixture(
    *, environment: str = "test", max_attempts: int = 3
) -> DiscoveryFixture:
    corpus = json.loads(CORPUS_PATH.read_text())
    clock = FixtureDiscoveryClock(int(datetime.fromisoformat(corpus["clock"]).timestamp() * 1000))
    source = FixtureDiscoverySource(
        clock.today,
        DevelopmentEligibilityPolicy(**corpus["policy"]),
        environment=environment,
    )
    viewer = participant_from_fixture(corpus["viewer"]["facts"])
    source.put_participant(viewer)
    mappings = FixtureChartMappingRepository(environment=environment)
    mappings.put(viewer.account_id, mapping_from_fixture(corpus["viewer"]["mapping"]))
    members: list[DiscoveryMember] = []
    states: dict[AccountId, str] = {}
    for row in corpus["candidates"]:
        identity = AccountId(row["account_id"])
        if row["facts"] is not None:
            facts = participant_from_fixture(row["facts"])
            source.put_participant(facts)
            profile_id = facts.profile_id
        else:
            profile_id = f"profile-{identity.value.removeprefix('discovery-')}"
        if profile_id is None:
            raise ValueError("Fixture members require distinct profile identities.")
        if row["mapping"] is not None:
            mappings.put(identity, mapping_from_fixture(row["mapping"]))
        for side, block in row["blocks"].items():
            if block is not None:
                actor, target = (
                    (viewer.account_id, identity)
                    if side == "viewer"
                    else (
                        identity,
                        viewer.account_id,
                    )
                )
                source.observe_block(actor, target, BlockState(block))
        members.append(DiscoveryMember(identity, profile_id, row["recommendation_priority"]))
        states[identity] = row["provider_state"]
    source.replace_population(tuple(members))
    provider = PopulationCompatibilityProvider(environment, states)
    batch = FixtureCompatibilityBatchService(
        environment,
        TrustedEligibilityService(source),
        mappings,
        provider,
        PROVENANCE,
        RetryPolicy(max_attempts),
    )
    session_id = "discovery-session-1"
    authority = FixtureDiscoveryAuthority(viewer.account_id, session_id)
    service = FixtureDiscoveryService(
        environment=environment,
        source=source,
        batch=batch,
        authority=authority,
        clock=clock,
    )
    return DiscoveryFixture(
        service, source, mappings, provider, authority, clock, viewer.account_id, session_id
    )
