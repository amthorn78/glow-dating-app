"""Internal fixture-only compatibility states and versioned cache identity.

There is no engine contract, engine math, wire adapter or cache storage here.
The current result type cannot represent a genuine compatibility projection.
"""

from dataclasses import dataclass, field
from enum import Enum

from .identity import ChartMapping, ChartMappingState, require_nonblank

PORT_VERSION = "gapp-hde-port-v1"


class CompatibilityStatus(Enum):
    READY = "ready"
    PENDING = "pending"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"


class FixtureCase(Enum):
    PENDING = "pending-chart"
    UNAVAILABLE = "engine-unavailable"
    UNSUPPORTED = "unsupported-contract"
    READY_SYNTHETIC = "explicitly-synthetic-ready"


@dataclass(frozen=True)
class FixtureProvenance:
    fixture_set_version: str
    adapter_version: str
    simulated_engine_version: str
    simulated_engine_contract_version: str
    source: str = field(default="fixture", init=False)
    port_version: str = field(default=PORT_VERSION, init=False)

    def __post_init__(self) -> None:
        for field_name in (
            "fixture_set_version",
            "adapter_version",
            "simulated_engine_version",
            "simulated_engine_contract_version",
        ):
            require_nonblank(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class CompatibilityRequest:
    viewer: ChartMapping
    candidate: ChartMapping
    eligibility_policy_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.viewer, ChartMapping) or not isinstance(
            self.candidate, ChartMapping
        ):
            raise TypeError("Compatibility requires typed ordered chart mappings.")
        require_nonblank(self.eligibility_policy_version, "eligibility_policy_version")


@dataclass(frozen=True)
class FixtureCompatibilityResult:
    status: CompatibilityStatus
    case: FixtureCase
    provenance: FixtureProvenance

    def __post_init__(self) -> None:
        expected = {
            FixtureCase.PENDING: CompatibilityStatus.PENDING,
            FixtureCase.UNAVAILABLE: CompatibilityStatus.UNAVAILABLE,
            FixtureCase.UNSUPPORTED: CompatibilityStatus.UNSUPPORTED,
            FixtureCase.READY_SYNTHETIC: CompatibilityStatus.READY,
        }
        if not isinstance(self.provenance, FixtureProvenance):
            raise TypeError("Fixture compatibility requires explicit fixture provenance.")
        if self.case not in expected or expected[self.case] is not self.status:
            raise ValueError("Compatibility state must agree with its explicit synthetic case.")

    @property
    def synthetic(self) -> bool:
        return True


@dataclass(frozen=True)
class SymmetryGuarantee:
    """Caller-declared guarantee for one named contract/version, not proof itself."""

    simulated_engine_version: str
    simulated_engine_contract_version: str
    evidence_reference: str

    def __post_init__(self) -> None:
        for field_name in (
            "simulated_engine_version",
            "simulated_engine_contract_version",
            "evidence_reference",
        ):
            require_nonblank(getattr(self, field_name), field_name)


@dataclass(frozen=True, order=True)
class ChartCacheIdentity:
    account_id: str
    engine_reference: str
    birth_input_version: str
    mapping_version: str


@dataclass(frozen=True)
class FixtureCacheKey:
    provenance: FixtureProvenance
    pair: tuple[ChartCacheIdentity, ChartCacheIdentity]
    symmetry: SymmetryGuarantee | None
    eligibility_policy_version: str


def fixture_cache_key(
    request: CompatibilityRequest,
    provenance: FixtureProvenance,
    symmetry: SymmetryGuarantee | None = None,
) -> FixtureCacheKey:
    identities: list[ChartCacheIdentity] = []
    for mapping in (request.viewer, request.candidate):
        if mapping.state is not ChartMappingState.RESOLVED or mapping.engine_reference is None:
            raise ValueError("Unresolved chart identity cannot form a compatibility cache key.")
        identities.append(
            ChartCacheIdentity(
                mapping.account_id.value,
                mapping.engine_reference.value,
                mapping.birth_input_version,
                mapping.mapping_version,
            )
        )
    if symmetry is not None:
        if (
            symmetry.simulated_engine_version != provenance.simulated_engine_version
            or symmetry.simulated_engine_contract_version
            != provenance.simulated_engine_contract_version
        ):
            raise ValueError(
                "Symmetry guarantee must match the exact engine and contract versions."
            )
        identities.sort()
    return FixtureCacheKey(
        provenance, (identities[0], identities[1]), symmetry, request.eligibility_policy_version
    )


@dataclass(frozen=True)
class FixtureCompatibilityProvider:
    environment: str
    case: FixtureCase
    provenance: FixtureProvenance

    def __post_init__(self) -> None:
        if self.environment not in {"development", "test"}:
            raise ValueError("Fixture compatibility is restricted to development and test.")
        if not isinstance(self.case, FixtureCase):
            raise TypeError("An explicit fixture case is required.")
        if not isinstance(self.provenance, FixtureProvenance):
            raise TypeError("Explicit fixture provenance is required.")

    def evaluate_pair(self, request: CompatibilityRequest) -> FixtureCompatibilityResult:
        case = self.case
        if any(
            mapping.state is not ChartMappingState.RESOLVED
            for mapping in (request.viewer, request.candidate)
        ):
            case = FixtureCase.PENDING
        status = {
            FixtureCase.PENDING: CompatibilityStatus.PENDING,
            FixtureCase.UNAVAILABLE: CompatibilityStatus.UNAVAILABLE,
            FixtureCase.UNSUPPORTED: CompatibilityStatus.UNSUPPORTED,
            FixtureCase.READY_SYNTHETIC: CompatibilityStatus.READY,
        }[case]
        return FixtureCompatibilityResult(status, case, self.provenance)
