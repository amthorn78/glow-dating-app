"""Distinct opaque identities, explicit versioned chart mappings and the age state's seam."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol


def require_nonblank(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonblank string.")


@dataclass(frozen=True)
class AccountId:
    value: str

    def __post_init__(self) -> None:
        require_nonblank(self.value, "AccountId")


@dataclass(frozen=True)
class EngineChartReference:
    value: str

    def __post_init__(self) -> None:
        require_nonblank(self.value, "EngineChartReference")


class ChartMappingState(Enum):
    PENDING = "pending"
    RESOLVED = "resolved"


@dataclass(frozen=True)
class ChartMapping:
    account_id: AccountId
    state: ChartMappingState
    engine_reference: EngineChartReference | None
    birth_input_version: str
    mapping_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("ChartMapping requires an application AccountId.")
        if not isinstance(self.state, ChartMappingState):
            raise TypeError("ChartMapping requires an explicit mapping state.")
        if self.state is ChartMappingState.RESOLVED:
            if not isinstance(self.engine_reference, EngineChartReference):
                raise ValueError("Resolved mapping requires a distinct EngineChartReference.")
        elif self.engine_reference is not None:
            raise ValueError("Pending mapping cannot assert a resolved engine reference.")
        require_nonblank(self.birth_input_version, "birth_input_version")
        require_nonblank(self.mapping_version, "mapping_version")


# -- The age state, behind a seam (SV1; G-01; OD-55's D3 (a); the SV1 brief's D9) ----------
#
# The account's recorded age state and the method that set it, read and written only through
# ``AgeAssurancePort``. SV1 records ``unknown`` at sign-up and builds no check. P04's onboarding
# holds the self-entered birth date, and a later slice writes ``self_declared_adult`` from it;
# P09.2 adds the stores' age signals as further states and methods; SV3's eligibility reads the
# state. No birth date is part of this type.


class AgeAssuranceState(Enum):
    UNKNOWN = "unknown"
    SELF_DECLARED_ADULT = "self_declared_adult"


class AgeAssuranceMethod(Enum):
    NONE = "none"
    SELF_DECLARATION = "self_declaration"


# Which method may set which state. Each store signal P09.2 adds brings its method and the
# states it may set; a state with no method listed cannot be recorded.
AGE_METHODS_BY_STATE: dict[AgeAssuranceState, frozenset[AgeAssuranceMethod]] = {
    AgeAssuranceState.UNKNOWN: frozenset({AgeAssuranceMethod.NONE}),
    AgeAssuranceState.SELF_DECLARED_ADULT: frozenset({AgeAssuranceMethod.SELF_DECLARATION}),
}


@dataclass(frozen=True)
class AgeAssurance:
    """One account's recorded age state: the state, the method that set it, when it was
    recorded and the policy version it was recorded under (none for ``unknown``)."""

    account_id: AccountId
    state: AgeAssuranceState
    method: AgeAssuranceMethod
    recorded_at: datetime
    policy_version: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("AgeAssurance requires an application AccountId.")
        if not isinstance(self.state, AgeAssuranceState):
            raise TypeError("AgeAssurance requires an explicit age state.")
        if not isinstance(self.method, AgeAssuranceMethod):
            raise TypeError("AgeAssurance requires the method that set the state.")
        if self.method not in AGE_METHODS_BY_STATE[self.state]:
            raise ValueError("This method cannot set this age state.")
        if not isinstance(self.recorded_at, datetime) or self.recorded_at.utcoffset() is None:
            raise ValueError("recorded_at must be an aware instant.")
        if self.state is AgeAssuranceState.UNKNOWN:
            if self.policy_version is not None:
                raise ValueError("An unknown age state has no policy version.")
        else:
            require_nonblank(self.policy_version, "policy_version")  # type: ignore[arg-type]


def unknown_age_assurance(account_id: AccountId, recorded_at: datetime) -> AgeAssurance:
    """The state sign-up records (SV1): nothing is known about the member's age."""
    return AgeAssurance(
        account_id, AgeAssuranceState.UNKNOWN, AgeAssuranceMethod.NONE, recorded_at, None
    )


class AgeAssurancePort(Protocol):
    """The only way to read or write an account's age state."""

    def read(self, account_id: AccountId) -> AgeAssurance | None: ...

    def record(self, assurance: AgeAssurance) -> None: ...
