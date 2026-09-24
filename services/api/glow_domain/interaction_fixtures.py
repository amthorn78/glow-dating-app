"""Controlled fictional multi-session composition; never a client reciprocity flag."""

from dataclasses import dataclass

from .compatibility import FixtureCase
from .discovery import DiscoveryMember, FixtureDiscoveryAuthority, FixtureDiscoveryService
from .discovery_fixtures import PROVENANCE, DiscoveryFixture, build_discovery_fixture
from .identity import AccountId
from .interactions import (
    FixtureIdentityRegistry,
    FixtureInteractionRepository,
    FixtureInteractionService,
    load_identity_registry,
)
from .provider_fixtures import ScriptedCompatibilityProvider


@dataclass(frozen=True)
class InteractionFixture:
    discovery: DiscoveryFixture
    registry: FixtureIdentityRegistry
    repository: FixtureInteractionRepository

    def session(self, actor: AccountId, session_id: str) -> FixtureInteractionService:
        if self.registry.account(actor) is None:
            raise ValueError("Unknown internal fixture account.")
        fixture = self.discovery
        discovery = FixtureDiscoveryService(
            environment="test",
            source=fixture.source,
            batch=fixture.service.batch,
            authority=FixtureDiscoveryAuthority(actor, session_id),
            clock=fixture.clock,
            consumption=self.repository,
        )
        return FixtureInteractionService(
            environment="test",
            discovery=discovery,
            registry=self.registry,
            repository=self.repository,
        )


def build_interaction_fixture() -> InteractionFixture:
    fixture = build_discovery_fixture()
    # Including the viewer permits a second real fixture command session to
    # discover/like them. This seeds no directional action or match.
    fixture.source.replace_population(
        (
            *fixture.source.select("recommended"),
            DiscoveryMember(fixture.viewer, "profile-viewer", 0),
        )
    )
    fixture.provider.providers[fixture.viewer] = ScriptedCompatibilityProvider(
        "test", PROVENANCE, (FixtureCase.READY_SYNTHETIC,)
    )
    return InteractionFixture(
        fixture, load_identity_registry(), FixtureInteractionRepository(environment="test")
    )
