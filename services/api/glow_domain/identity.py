"""Distinct opaque identities, explicit versioned chart mappings and the age state's seam."""

from dataclasses import dataclass
from datetime import date, datetime
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
# ``AgeAssurancePort``. SV1 records ``unknown`` at sign-up and builds no check. SV2 (its brief's
# D7; DM-52) adds the adult check from the self-entered birth date and one transition beside
# ``record``: the date's one home is the age state's row, written only by ``transition``, and
# SV3 reads a member's age through ``age_years``, in whole years, never the date. ``AgeAssurance``
# itself still carries no birth date; P09.2 adds the stores' age signals as further states and
# methods; SV3's eligibility reads the state.


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


# -- SV2's adult check (D7; G-01; P04's rule) -----------------------------------------------

# The adult age, a fixed rule (OD-55's D3; the age floor is 18, OD-60).
ADULT_AGE = 18
# The rule the check applies, recorded as the age state's policy version: 18 or over on the
# server's UTC date, read from the database clock after the locks, with a 29 February birthday
# falling on 1 March in a common year (P04's ``leapBirthday: 'march_1'``).
ADULT_POLICY_VERSION = "adult.self-declaration.v1"


class AdultOutcome(Enum):
    PASS = "pass"
    UNDER_AGE = "under_age"
    FUTURE = "future"


def whole_years(birth_date: date, today: date) -> int:
    """Whole years from ``birth_date`` to ``today``. A 29 February birthday has passed on
    1 March of a common year, and on 29 February of a leap year (P04's rule)."""
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


def adult_outcome(birth_date: date, today: date) -> AdultOutcome:
    """The adult check (D7): a date in the future fails; otherwise 18 whole years pass."""
    if birth_date > today:
        return AdultOutcome.FUTURE
    if whole_years(birth_date, today) >= ADULT_AGE:
        return AdultOutcome.PASS
    return AdultOutcome.UNDER_AGE


@dataclass(frozen=True)
class AgeTransition:
    """D7's one transition: to ``self_declared_adult`` with the date that passed and the rule's
    version, or back to ``unknown`` with neither. ``recorded_at`` is the database's time."""

    account_id: AccountId
    state: AgeAssuranceState
    birth_date: date | None
    recorded_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("AgeTransition requires an application AccountId.")
        if not isinstance(self.state, AgeAssuranceState):
            raise TypeError("AgeTransition requires an explicit age state.")
        if not isinstance(self.recorded_at, datetime) or self.recorded_at.utcoffset() is None:
            raise ValueError("recorded_at must be an aware instant.")
        if self.state is AgeAssuranceState.SELF_DECLARED_ADULT:
            if not isinstance(self.birth_date, date) or isinstance(self.birth_date, datetime):
                raise ValueError("A self-declared adult state needs its birth date.")
        elif self.birth_date is not None:
            raise ValueError("An unknown age state has no birth date.")

    @property
    def method(self) -> AgeAssuranceMethod:
        if self.state is AgeAssuranceState.SELF_DECLARED_ADULT:
            return AgeAssuranceMethod.SELF_DECLARATION
        return AgeAssuranceMethod.NONE

    @property
    def policy_version(self) -> str | None:
        return ADULT_POLICY_VERSION if self.state is AgeAssuranceState.SELF_DECLARED_ADULT else None


class AgeAssurancePort(Protocol):
    """The only way to read or write an account's age state."""

    def read(self, account_id: AccountId) -> AgeAssurance | None: ...

    def record(self, assurance: AgeAssurance) -> None: ...

    def transition(self, change: AgeTransition) -> str:
        """SV2 (D7): in the caller's transaction, after the account row lock, ``unknown`` to
        ``self_declared_adult`` with the date, a new date for a ``self_declared_adult`` state,
        or back to ``unknown``; anything else is refused. It bumps the account's
        ``eligibility_version``. Returns ``applied`` or ``no_change``."""
        ...

    def age_years(self, account_id: AccountId, today: date) -> int | None:
        """SV2 (D4): the member's age in whole years from the age state's date, or None while
        the state is ``unknown``; never the date."""
        ...
