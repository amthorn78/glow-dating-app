"""Minimal internal read/provider protocols; no storage implementation.

The compatibility result is deliberately fixture-only until the supported live
HDE contract is obtained. These are not HTTP routes or engine wire types.
"""

from typing import Protocol

from .compatibility import CompatibilityRequest, FixtureCompatibilityResult
from .eligibility import EligibilitySnapshot
from .identity import AccountId, ChartMapping


class EligibilitySnapshotRepository(Protocol):
    def get(self, account_id: AccountId) -> EligibilitySnapshot | None:
        """Return an explicit current snapshot, or None when absent."""
        ...


class ChartMappingRepository(Protocol):
    def get(self, account_id: AccountId) -> ChartMapping | None:
        """Resolve by app identity; never coerce it into an engine chart identity."""
        ...


class FixtureCompatibilityPort(Protocol):
    def evaluate_pair(self, request: CompatibilityRequest) -> FixtureCompatibilityResult:
        """Return a typed, explicitly synthetic state without exposing engine internals."""
        ...
