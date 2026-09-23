"""Distinct opaque identities and explicit versioned chart mappings."""

from dataclasses import dataclass
from enum import Enum


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
