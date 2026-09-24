"""Bounded synchronous fixture publication guards, not database transactions.

Repositories retain revision cells for their lifetime; every affecting writer
advances the same cell, including deletion and same-value restoration. Reads
may still invoke callbacks. Publication checks only captured concrete cells,
after the last such read, without calling a repository or a supplied getter.
"""

from dataclasses import dataclass

from .identity import AccountId, ChartMapping
from .trusted_eligibility import EvidenceUnavailable


class FixtureRevision:
    __slots__ = ("_value",)

    def __init__(self) -> None:
        self._value = 0

    def advance(self) -> None:
        self._value += 1


@dataclass(frozen=True, slots=True)
class FixtureReadGuard:
    checks: tuple[tuple[FixtureRevision, int], ...]


def capture_revisions(*revisions: FixtureRevision) -> FixtureReadGuard:
    if any(type(revision) is not FixtureRevision for revision in revisions):
        raise TypeError("Fixture publication requires concrete revision cells.")
    return FixtureReadGuard(
        tuple((revision, object.__getattribute__(revision, "_value")) for revision in revisions)
    )


def guard_is_current(guard: FixtureReadGuard | None) -> bool:
    """Pure final check: no virtual attribute reads, equality or hash callbacks."""
    if type(guard) is not FixtureReadGuard:
        return False
    checks = object.__getattribute__(guard, "checks")
    if type(checks) is not tuple or not checks:
        return False
    for check in checks:
        if type(check) is not tuple or len(check) != 2:
            return False
        revision, expected = check
        if type(revision) is not FixtureRevision or type(expected) is not int:
            return False
        current = object.__getattribute__(revision, "_value")
        if type(current) is not int or current != expected:
            return False
    return True


def acquire_guard(source: object, *accounts: AccountId) -> FixtureReadGuard | None:
    """Optional fixture capability; absence/unavailability cannot publish output.

    This lookup/call is callback-capable and must precede the normal source
    rechecks. It is never called at the final publication acceptance boundary.
    """
    try:
        acquire = getattr(source, "publication_guard", None)
        guard = acquire(*accounts) if callable(acquire) else None
    except EvidenceUnavailable:
        return None
    return guard if type(guard) is FixtureReadGuard and guard_is_current(guard) else None


class FixtureChartMappingRepository:
    """Account–chart links with explicit writer participation in publication.

    No chart mathematics or engine storage. A get-only dictionary cannot prove
    monotonic invalidation and is deliberately not adapted by copying values.
    """

    def __init__(self, *, environment: str) -> None:
        if environment not in {"development", "test"}:
            raise ValueError("Fixture mappings are restricted to development and test.")
        self._mappings: dict[AccountId, ChartMapping] = {}
        self._revisions: dict[AccountId, FixtureRevision] = {}

    def _revision(self, account_id: AccountId) -> FixtureRevision:
        if not isinstance(account_id, AccountId):
            raise TypeError("Fixture mappings require application AccountIds.")
        if account_id not in self._revisions:
            self._revisions[account_id] = FixtureRevision()
        return self._revisions[account_id]

    def put(self, account_id: AccountId, mapping: ChartMapping | None) -> None:
        if mapping is not None and not isinstance(mapping, ChartMapping):
            raise TypeError("Fixture mappings require typed chart mappings.")
        revision = self._revision(account_id)
        if mapping is None:
            self._mappings.pop(account_id, None)
        else:
            self._mappings[account_id] = mapping
        revision.advance()

    def get(self, account_id: AccountId) -> ChartMapping | None:
        return self._mappings.get(account_id)

    def publication_guard(self, *accounts: AccountId) -> FixtureReadGuard:
        return capture_revisions(*(self._revision(account_id) for account_id in accounts))
