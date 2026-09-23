"""App-owned provisional ports, not HDE endpoints or a supported engine schema.

All executable adapters are explicitly synthetic. No data rights, provider
activation, persistent transaction, birth-time calculation or HD score is implied.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum
from typing import Protocol

from .compatibility import (
    CompatibilityRequest,
    CompatibilityStatus,
    FixtureCacheKey,
    FixtureCompatibilityResult,
    FixtureProvenance,
    fixture_cache_key,
)
from .identity import AccountId, ChartMapping, ChartMappingState, require_nonblank


class TimePrecision(Enum):
    KNOWN = "known"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BirthInput:
    account_id: AccountId
    input_version: str
    birth_date: date = field(repr=False)
    local_time: time | None = field(repr=False)
    time_precision: TimePrecision
    place_label: str = field(repr=False)
    timezone_name: str | None = field(repr=False)
    timezone_provenance: str | None = field(repr=False)
    consent_version: str
    consent_granted: bool

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("Birth input requires an application identity.")
        if not isinstance(self.birth_date, date) or isinstance(self.birth_date, datetime):
            raise TypeError("Birth date must be a civil date.")
        if not isinstance(self.time_precision, TimePrecision):
            raise TypeError("Time precision must be explicit.")
        if type(self.consent_granted) is not bool:
            raise TypeError("Consent decision must be explicit.")
        if self.local_time is not None and (
            not isinstance(self.local_time, time) or self.local_time.tzinfo is not None
        ):
            raise ValueError("Local birth time must remain a civil time.")
        if (self.time_precision is TimePrecision.UNKNOWN) != (self.local_time is None):
            raise ValueError("Unknown time and supplied civil time must agree.")
        for name in ("input_version", "place_label", "consent_version"):
            require_nonblank(getattr(self, name), name)
        if (self.timezone_name is None) != (self.timezone_provenance is None):
            raise ValueError("Timezone and its explicit provenance are paired.")
        if self.timezone_name is not None:
            require_nonblank(self.timezone_name, "timezone_name")
            if self.timezone_provenance is not None:
                require_nonblank(self.timezone_provenance, "timezone_provenance")
        for value in (self.place_label, self.timezone_name, self.timezone_provenance):
            if value is not None:
                try:
                    value.encode("utf-8", errors="strict")
                except UnicodeEncodeError as error:
                    raise ValueError(
                        "Birth text must contain valid Unicode scalar values."
                    ) from error


class FailureCode(Enum):
    TIMEOUT = "timeout"
    OUTAGE = "outage"
    UNSUPPORTED = "unsupported"
    MALFORMED_OUTPUT = "malformed_output"
    IDENTITY_MISMATCH = "identity_mismatch"
    STALE = "stale"
    CONSENT_REQUIRED = "consent_required"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"


class ExpectedProviderFailure(Exception):
    """Only adapters may translate known provider failures into this taxonomy.

    Arbitrary exceptions are defects and must propagate. No raw provider error
    text, input, token or response body is carried by the expected failure type.
    """

    def __init__(self, code: FailureCode) -> None:
        if not isinstance(code, FailureCode):
            raise TypeError("Provider failure requires a declared code.")
        self.code = code
        super().__init__(code.value)


class ChartResolutionState(Enum):
    PENDING = "pending"
    AMBIGUOUS = "ambiguous"
    RESOLVED = "resolved"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"
    STALE = "stale"
    CONSENT_REQUIRED = "consent_required"


@dataclass(frozen=True)
class ChartResolution:
    account_id: AccountId
    input_version: str
    state: ChartResolutionState
    provenance: FixtureProvenance
    mapping: ChartMapping | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("Resolution requires an application identity.")
        require_nonblank(self.input_version, "input_version")
        if not isinstance(self.state, ChartResolutionState):
            raise TypeError("Resolution requires an explicit state.")
        if not isinstance(self.provenance, FixtureProvenance):
            raise TypeError("Resolution requires fixture provenance.")
        if self.state is ChartResolutionState.RESOLVED:
            if (
                not isinstance(self.mapping, ChartMapping)
                or self.mapping.state is not ChartMappingState.RESOLVED
                or self.mapping.account_id != self.account_id
                or self.mapping.birth_input_version != self.input_version
            ):
                raise ValueError("Resolved identity must match the account and input version.")
        elif self.mapping is not None:
            raise ValueError("Unresolved input cannot assert a usable chart mapping.")


class ChartResolver(Protocol):
    def resolve(
        self, birth_input: BirthInput, current_input_version: str, idempotency_key: str
    ) -> ChartResolution:
        """Resolve entered facts; caller supplies trusted current input/consent state.

        Never perform engine writes without the separately supported contract and
        authority. Replay key with changed input must conflict. Recheck current
        account/input/consent revisions when accepting a result, including replay.
        """
        ...


@dataclass(frozen=True)
class BoundCompatibilityResult:
    key: FixtureCacheKey
    result: FixtureCompatibilityResult

    def __post_init__(self) -> None:
        if not isinstance(self.key, FixtureCacheKey) or not isinstance(
            self.result, FixtureCompatibilityResult
        ):
            raise TypeError("Bound output requires a typed identity and fixture result.")
        if self.key.provenance != self.result.provenance:
            raise ValueError("Result and request provenance must agree.")


class CompatibilityProvider(Protocol):
    def evaluate(
        self, request: CompatibilityRequest, idempotency_key: str
    ) -> BoundCompatibilityResult:
        """One ordered, eligible resolved pair with exact provenance.

        Allowed only after trusted eligibility. Known provider failures use
        ExpectedProviderFailure; programming defects must remain visible.
        Stable finalized key replays return the same outcome. Changed payload
        under that key conflicts. A01/A07 still own real retry/output rights.
        """
        ...


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int

    def __post_init__(self) -> None:
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 3:
            raise ValueError("Fixture attempts must be between one and three.")


@dataclass(frozen=True)
class CompatibilityOutcome:
    output: BoundCompatibilityResult | None
    failure: FailureCode | None
    attempts: int

    def __post_init__(self) -> None:
        if (self.output is None) == (self.failure is None):
            raise ValueError("Outcome must contain exactly one output or failure.")
        if self.output is not None and not isinstance(self.output, BoundCompatibilityResult):
            raise TypeError("Outcome output must be bound to its request.")
        if self.failure is not None and not isinstance(self.failure, FailureCode):
            raise TypeError("Outcome failure must use a declared code.")
        if type(self.attempts) is not int or not 1 <= self.attempts <= 3:
            raise ValueError("Outcome attempts must be an integer from one to three.")


def evaluate_with_retry(
    provider: CompatibilityProvider,
    request: CompatibilityRequest,
    provenance: FixtureProvenance,
    idempotency_key: str,
    policy: RetryPolicy,
) -> CompatibilityOutcome:
    """Bounded no-sleep fixture exercise, not a worker or production retry policy.

    The request must already have passed trusted eligibility. The future worker
    owns persisted attempts/backoff/deadline and revalidation before each attempt.
    """
    require_nonblank(idempotency_key, "idempotency_key")
    expected_key = fixture_cache_key(request, provenance)
    for attempt in range(1, policy.max_attempts + 1):
        try:
            output = provider.evaluate(request, idempotency_key)
        except ExpectedProviderFailure as error:
            if (
                error.code in {FailureCode.TIMEOUT, FailureCode.OUTAGE}
                and attempt < policy.max_attempts
            ):
                continue
            return CompatibilityOutcome(None, error.code, attempt)
        if not isinstance(output, BoundCompatibilityResult):
            raise TypeError("Adapter returned an undeclared result type.")
        if output.key.provenance != expected_key.provenance:
            return CompatibilityOutcome(None, FailureCode.UNSUPPORTED, attempt)
        if tuple(item.account_id for item in output.key.pair) != tuple(
            item.account_id for item in expected_key.pair
        ):
            return CompatibilityOutcome(None, FailureCode.IDENTITY_MISMATCH, attempt)
        if output.key != expected_key:
            return CompatibilityOutcome(None, FailureCode.STALE, attempt)
        return CompatibilityOutcome(output, None, attempt)
    raise AssertionError("A validated retry policy must attempt at least once.")


@dataclass(frozen=True)
class CompatibilityProjection:
    status: str
    source: str = field(default="fixture", init=False)

    def __post_init__(self) -> None:
        if self.status not in {"pending", "unavailable", "unsupported", "stale"}:
            raise ValueError("Fixture projections cannot assert a live compatibility result.")


def project_fixture_compatibility(
    outcome: CompatibilityOutcome, current_key: FixtureCacheKey
) -> CompatibilityProjection:
    """Numeric-free minimal app projection. Synthetic ready never becomes HD ready.

    This internal projection is not wired to HTTP. Public band/explanation output
    remains disabled until approved output/cache rights and live mapping exist.
    """
    if outcome.output is None:
        if outcome.failure is None:
            raise AssertionError("Validated failure outcome must have a failure code.")
        status = {
            FailureCode.UNSUPPORTED: "unsupported",
            FailureCode.STALE: "stale",
        }.get(outcome.failure, "unavailable")
        return CompatibilityProjection(status)
    if outcome.output.key != current_key:
        return CompatibilityProjection("stale")
    status = {
        CompatibilityStatus.READY: "pending",
        CompatibilityStatus.PENDING: "pending",
        CompatibilityStatus.UNAVAILABLE: "unavailable",
        CompatibilityStatus.UNSUPPORTED: "unsupported",
    }[outcome.output.result.status]
    return CompatibilityProjection(status)


@dataclass(frozen=True)
class LifecycleRequest:
    account_id: AccountId
    mapping: ChartMapping | None
    deletion_version: str
    shared_reference_count: int | None

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("Lifecycle requires an application identity.")
        require_nonblank(self.deletion_version, "deletion_version")
        if self.mapping is not None and not isinstance(self.mapping, ChartMapping):
            raise TypeError("Lifecycle mapping must have an explicit typed identity.")
        if self.mapping is not None and self.mapping.account_id != self.account_id:
            raise ValueError("Lifecycle mapping belongs to a different account.")
        if self.shared_reference_count is not None and (
            type(self.shared_reference_count) is not int or self.shared_reference_count < 0
        ):
            raise ValueError("Reference count must be explicit, unknown or nonnegative.")


@dataclass(frozen=True)
class LifecycleObligation:
    account_id: AccountId
    deletion_version: str
    app_reference_action: str
    engine_action: str
    complete: bool = field(default=False, init=False)
    source: str = field(default="fixture", init=False)


class EngineLifecycle(Protocol):
    def plan_detachment(
        self, request: LifecycleRequest, idempotency_key: str
    ) -> LifecycleObligation:
        """App-only obligation planning; never proof of engine deletion.

        Immediate access/visibility revocation and tombstone belong to the app
        transaction. Shared/unknown chart rights remain blocked. No reference
        count, including zero, supplies permission to delete an engine chart.
        """
        ...


class BirthInputRepository(Protocol):
    def get_current(self, account_id: AccountId) -> BirthInput | None:
        """Return current private own-account input; never an engine lookup."""
        ...


@dataclass(frozen=True)
class MappingWrite:
    account_id: AccountId
    expected_account_version: str
    expected_input_version: str
    expected_mapping_version: str | None
    mapping: ChartMapping

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId) or not isinstance(self.mapping, ChartMapping):
            raise TypeError("Mapping write requires typed app identity and chart mapping.")
        if self.account_id != self.mapping.account_id:
            raise ValueError("Mapping writes must remain within one account.")
        if self.mapping.birth_input_version != self.expected_input_version:
            raise ValueError("Mapping writes must use the current input version.")
        for name in ("expected_account_version", "expected_input_version"):
            require_nonblank(getattr(self, name), name)
        if self.expected_mapping_version is not None:
            require_nonblank(self.expected_mapping_version, "expected_mapping_version")


@dataclass(frozen=True)
class MappingOutboxEvent:
    dedup_key: str
    account_id: AccountId
    mapping_version: str
    kind: str = field(default="mapping_changed", init=False)

    def __post_init__(self) -> None:
        require_nonblank(self.dedup_key, "dedup_key")
        require_nonblank(self.mapping_version, "mapping_version")
        if not isinstance(self.account_id, AccountId):
            raise TypeError("Event requires application identity.")


class MappingUnitOfWork(Protocol):
    def commit_mapping_and_event(self, write: MappingWrite, event: MappingOutboxEvent) -> bool:
        """Atomically CAS all expected versions, mapping and deduplicated outbox event.

        False means stale/current-state rejection with no writes. Conflict or
        exception must roll back both changes. Enforce account/input ownership,
        current consent/deletion eligibility and event/mapping correspondence.
        The prerequisite resolver work follows a separate committed request
        outbox. This result-acceptance transaction makes no provider call inside
        its boundary; further consumers dispatch only after this commit. Real
        transaction and crash recovery proof belongs to P11.
        """
        ...
