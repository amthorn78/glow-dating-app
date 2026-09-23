"""Nonpersistent conformance substitutes; never network or HDE adapters."""

from dataclasses import dataclass, field

from .compatibility import (
    CompatibilityRequest,
    FixtureCacheKey,
    FixtureCase,
    FixtureCompatibilityProvider,
    FixtureProvenance,
    fixture_cache_key,
)
from .identity import AccountId, ChartMapping
from .ports import ChartMappingRepository
from .provider_contracts import (
    BirthInput,
    BoundCompatibilityResult,
    ChartResolution,
    ChartResolutionState,
    CompatibilityOutcome,
    CompatibilityProvider,
    ExpectedProviderFailure,
    FailureCode,
    LifecycleObligation,
    LifecycleRequest,
    MappingOutboxEvent,
    MappingWrite,
    RetryPolicy,
    TimePrecision,
    evaluate_with_retry,
)
from .trusted_eligibility import (
    EligibilityDecisionState,
    PairEvidenceVersion,
    TrustedEligibilityService,
)


def require_fixture_environment(environment: str) -> None:
    if environment not in {"development", "test"}:
        raise ValueError("Fixture providers are restricted to development and test.")


@dataclass
class FixtureChartResolver:
    environment: str
    state: ChartResolutionState
    provenance: FixtureProvenance
    supplied_mapping: ChartMapping | None = None
    _ledger: dict[str, tuple[BirthInput, ChartResolution]] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        require_fixture_environment(self.environment)
        if not isinstance(self.state, ChartResolutionState):
            raise TypeError("An explicit chart fixture state is required.")
        if not isinstance(self.provenance, FixtureProvenance):
            raise TypeError("Explicit fixture provenance is required.")

    def resolve(
        self, birth_input: BirthInput, current_input_version: str, idempotency_key: str
    ) -> ChartResolution:
        from .identity import require_nonblank

        require_fixture_environment(self.environment)
        if not isinstance(birth_input, BirthInput):
            raise TypeError("Resolver requires typed private birth input.")
        require_nonblank(current_input_version, "current_input_version")
        require_nonblank(idempotency_key, "idempotency_key")
        state = self.state
        # Current state wins over a replayed result. These arguments must come
        # from app-owned acquisition; this fixture is not HTTP authentication.
        if birth_input.input_version != current_input_version:
            state = ChartResolutionState.STALE
        elif not birth_input.consent_granted:
            state = ChartResolutionState.CONSENT_REQUIRED
        elif birth_input.time_precision is not TimePrecision.KNOWN or (
            birth_input.timezone_name is None
        ):
            state = ChartResolutionState.AMBIGUOUS
        if state in {ChartResolutionState.STALE, ChartResolutionState.CONSENT_REQUIRED}:
            return ChartResolution(
                birth_input.account_id, birth_input.input_version, state, self.provenance
            )
        prior = self._ledger.get(idempotency_key)
        if prior is not None:
            if prior[0] != birth_input:
                raise ExpectedProviderFailure(FailureCode.IDEMPOTENCY_CONFLICT)
            return prior[1]
        result = ChartResolution(
            birth_input.account_id,
            birth_input.input_version,
            state,
            self.provenance,
            self.supplied_mapping if state is ChartResolutionState.RESOLVED else None,
        )
        self._ledger[idempotency_key] = (birth_input, result)
        return result


@dataclass
class ScriptedCompatibilityProvider:
    """Each call consumes a declared synthetic failure/case until finalized.

    Finalized results replay identically in this object only. The ledger is
    ephemeral and does not certify durable provider idempotency or retries.
    """

    environment: str
    provenance: FixtureProvenance
    script: tuple[FailureCode | FixtureCase, ...]
    calls: int = field(default=0, init=False)
    _keys: dict[str, FixtureCacheKey] = field(default_factory=dict, init=False, repr=False)
    _results: dict[str, BoundCompatibilityResult] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        require_fixture_environment(self.environment)
        if not isinstance(self.provenance, FixtureProvenance):
            raise TypeError("Explicit fixture provenance is required.")
        if not self.script or any(
            not isinstance(step, (FailureCode, FixtureCase)) for step in self.script
        ):
            raise ValueError("An explicit nonempty synthetic script is required.")

    def evaluate(
        self, request: CompatibilityRequest, idempotency_key: str
    ) -> BoundCompatibilityResult:
        from .identity import require_nonblank

        require_fixture_environment(self.environment)
        require_nonblank(idempotency_key, "idempotency_key")
        if not isinstance(request, CompatibilityRequest):
            raise TypeError("Provider requires an ordered mapped pair.")
        key = fixture_cache_key(request, self.provenance)
        if idempotency_key in self._keys and self._keys[idempotency_key] != key:
            raise ExpectedProviderFailure(FailureCode.IDEMPOTENCY_CONFLICT)
        self._keys[idempotency_key] = key
        if idempotency_key in self._results:
            return self._results[idempotency_key]
        step = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        if isinstance(step, FailureCode):
            raise ExpectedProviderFailure(step)
        result = FixtureCompatibilityProvider(
            self.environment, step, self.provenance
        ).evaluate_pair(request)
        output = BoundCompatibilityResult(key, result)
        self._results[idempotency_key] = output
        return output


@dataclass
class FixtureEngineLifecycle:
    environment: str
    _ledger: dict[str, tuple[LifecycleRequest, LifecycleObligation]] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        require_fixture_environment(self.environment)

    def plan_detachment(
        self, request: LifecycleRequest, idempotency_key: str
    ) -> LifecycleObligation:
        from .identity import require_nonblank

        require_fixture_environment(self.environment)
        if not isinstance(request, LifecycleRequest):
            raise TypeError("Lifecycle requires a typed request.")
        require_nonblank(idempotency_key, "idempotency_key")
        prior = self._ledger.get(idempotency_key)
        if prior is not None:
            if prior[0] != request:
                raise ExpectedProviderFailure(FailureCode.IDEMPOTENCY_CONFLICT)
            return prior[1]
        if request.mapping is None or request.mapping.engine_reference is None:
            engine_action = "reconcile_prior_references"
        elif request.shared_reference_count is None:
            engine_action = "ownership_unknown"
        elif request.shared_reference_count > 0:
            engine_action = "preserve_shared_chart"
        else:
            engine_action = "await_supported_deletion_rights"
        result = LifecycleObligation(
            request.account_id, request.deletion_version, "invalidate_app_reference", engine_action
        )
        self._ledger[idempotency_key] = (request, result)
        return result


@dataclass(frozen=True)
class FixtureAccountMappingState:
    """Explicit server-side scenario state, never a client authorization DTO."""

    account_id: AccountId
    account_version: str
    input_version: str
    consent_current: bool
    deleted: bool
    mapping: ChartMapping | None

    def __post_init__(self) -> None:
        from .identity import require_nonblank

        if not isinstance(self.account_id, AccountId):
            raise TypeError("Fixture state requires an application identity.")
        for value in (self.consent_current, self.deleted):
            if type(value) is not bool:
                raise TypeError("Fixture consent/deletion decisions must be explicit booleans.")
        for name in ("account_version", "input_version"):
            require_nonblank(getattr(self, name), name)
        if self.mapping is not None:
            if not isinstance(self.mapping, ChartMapping):
                raise TypeError("Fixture mapping must use the typed chart mapping.")
            if (
                self.mapping.account_id != self.account_id
                or self.mapping.birth_input_version != self.input_version
            ):
                raise ValueError("Fixture mapping must match account and current birth input.")


@dataclass
class FixtureMappingUnitOfWork:
    """Minimal account/mapping/outbox fake, not a SQL or locking simulation."""

    environment: str
    state: FixtureAccountMappingState
    events: dict[str, MappingOutboxEvent] = field(default_factory=dict, init=False)
    _commits: dict[str, tuple[MappingWrite, MappingOutboxEvent]] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        require_fixture_environment(self.environment)
        if not isinstance(self.state, FixtureAccountMappingState):
            raise TypeError("Fixture unit of work requires explicit account state.")

    def commit_mapping_and_event(self, write: MappingWrite, event: MappingOutboxEvent) -> bool:
        from dataclasses import replace

        require_fixture_environment(self.environment)
        if not isinstance(write, MappingWrite) or not isinstance(event, MappingOutboxEvent):
            raise TypeError("Mapping commit requires typed write and outbox event.")
        if (
            event.account_id != write.account_id
            or event.mapping_version != write.mapping.mapping_version
        ):
            raise ValueError("Outbox event must bind to the same account and new mapping.")
        current = self.state
        if (
            current.account_id != write.account_id
            or current.account_version != write.expected_account_version
            or current.input_version != write.expected_input_version
            or not current.consent_current
            or current.deleted
        ):
            return False
        prior = self._commits.get(event.dedup_key)
        if prior is not None:
            if prior != (write, event):
                raise ExpectedProviderFailure(FailureCode.IDEMPOTENCY_CONFLICT)
            return True
        current_version = current.mapping.mapping_version if current.mapping else None
        if current_version != write.expected_mapping_version:
            return False
        # Validate everything before the two in-memory assignments. There is no
        # real transaction or concurrency guarantee in this fixture.
        self.state = replace(current, mapping=write.mapping)
        self.events[event.dedup_key] = event
        self._commits[event.dedup_key] = (write, event)
        return True


@dataclass(frozen=True)
class CandidateWork:
    account_id: AccountId
    idempotency_key: str

    def __post_init__(self) -> None:
        from .identity import require_nonblank

        if not isinstance(self.account_id, AccountId):
            raise TypeError("Candidate work requires an application identity.")
        require_nonblank(self.idempotency_key, "idempotency_key")


@dataclass(frozen=True)
class CandidateOutcome:
    account_id: AccountId
    state: str
    compatibility: CompatibilityOutcome | None = None


@dataclass(frozen=True)
class FixtureBatch:
    state: str
    entries: tuple[CandidateOutcome, ...]
    source: str = field(default="fixture", init=False)


@dataclass(frozen=True)
class _PreparedCandidate:
    outcome: CandidateOutcome
    version: PairEvidenceVersion | None = None
    request: CompatibilityRequest | None = None


@dataclass(frozen=True)
class FixtureCompatibilityBatchService:
    """Bounded app iteration, not an assumed engine batch endpoint.

    Re-acquisition and rejection are demonstrated; atomic race prevention is
    deliberately not claimed. The caller must never treat this as contact auth.
    """

    environment: str
    eligibility: TrustedEligibilityService
    mappings: ChartMappingRepository
    provider: CompatibilityProvider
    provenance: FixtureProvenance
    retry_policy: RetryPolicy

    def __post_init__(self) -> None:
        require_fixture_environment(self.environment)

    def evaluate(self, viewer: AccountId, candidates: tuple[CandidateWork, ...]) -> FixtureBatch:
        require_fixture_environment(self.environment)
        if not isinstance(viewer, AccountId):
            raise TypeError("Viewer must be an application identity.")
        if not isinstance(candidates, tuple) or any(
            not isinstance(item, CandidateWork) for item in candidates
        ):
            raise TypeError("Batch requires a typed bounded candidate tuple.")
        if len(candidates) > 20:
            raise ValueError("Fixture batches permit at most twenty candidates.")
        if len({item.account_id for item in candidates}) != len(candidates) or len(
            {item.idempotency_key for item in candidates}
        ) != len(candidates):
            raise ValueError("Batch identities and idempotency keys must be distinct.")
        prepared = tuple(self._evaluate_one(viewer, item) for item in candidates)
        # Later candidates may take time or change shared state. Revalidate
        # earlier outputs after all provider work before returning the batch.
        entries = tuple(self._revalidate(viewer, item) for item in prepared)
        if not entries or all(entry.state == "excluded" for entry in entries):
            state = "empty"
        elif all(entry.state == "evaluated" for entry in entries):
            state = "evaluated"
        else:
            state = "partial"
        return FixtureBatch(state, entries)

    def _revalidate(self, viewer: AccountId, prepared: _PreparedCandidate) -> CandidateOutcome:
        outcome = prepared.outcome
        if outcome.compatibility is None:
            return outcome
        if prepared.version is None or prepared.request is None:
            raise AssertionError("Prepared provider output must retain its acquisition evidence.")
        decision = self.eligibility.evaluate(viewer, outcome.account_id, prepared.version)
        if decision.state is not EligibilityDecisionState.READY:
            return CandidateOutcome(outcome.account_id, decision.state.value)
        if (self.mappings.get(viewer), self.mappings.get(outcome.account_id)) != (
            prepared.request.viewer,
            prepared.request.candidate,
        ):
            return CandidateOutcome(outcome.account_id, "stale")
        return outcome

    def _evaluate_one(self, viewer: AccountId, item: CandidateWork) -> _PreparedCandidate:
        from .identity import ChartMappingState

        expected_version: PairEvidenceVersion | None = None
        expected_request: CompatibilityRequest | None = None
        for attempt in range(1, self.retry_policy.max_attempts + 1):
            decision = self.eligibility.evaluate(viewer, item.account_id, expected_version)
            if decision.state is not EligibilityDecisionState.READY:
                return _PreparedCandidate(CandidateOutcome(item.account_id, decision.state.value))
            expected_version = decision.evidence_version
            viewer_mapping = self.mappings.get(viewer)
            candidate_mapping = self.mappings.get(item.account_id)
            if viewer_mapping is None or candidate_mapping is None:
                return _PreparedCandidate(CandidateOutcome(item.account_id, "missing_identity"))
            if not isinstance(viewer_mapping, ChartMapping) or not isinstance(
                candidate_mapping, ChartMapping
            ):
                raise TypeError("Mapping repository returned an undeclared type.")
            if (viewer_mapping.account_id, candidate_mapping.account_id) != (
                viewer,
                item.account_id,
            ):
                return _PreparedCandidate(CandidateOutcome(item.account_id, "identity_mismatch"))
            if any(
                mapping.state is not ChartMappingState.RESOLVED
                for mapping in (viewer_mapping, candidate_mapping)
            ):
                return _PreparedCandidate(CandidateOutcome(item.account_id, "pending_identity"))
            request = CompatibilityRequest(viewer_mapping, candidate_mapping)
            if expected_request is not None and expected_request != request:
                return _PreparedCandidate(CandidateOutcome(item.account_id, "stale"))
            expected_request = request
            outcome = evaluate_with_retry(
                self.provider, request, self.provenance, item.idempotency_key, RetryPolicy(1)
            )
            if outcome.failure in {FailureCode.TIMEOUT, FailureCode.OUTAGE} and (
                attempt < self.retry_policy.max_attempts
            ):
                continue
            # A provider can take time; discard results if either participant's
            # state or either mapping changed during that call.
            after = self.eligibility.evaluate(viewer, item.account_id, expected_version)
            if after.state is not EligibilityDecisionState.READY:
                return _PreparedCandidate(CandidateOutcome(item.account_id, after.state.value))
            if (self.mappings.get(viewer), self.mappings.get(item.account_id)) != (
                viewer_mapping,
                candidate_mapping,
            ):
                return _PreparedCandidate(CandidateOutcome(item.account_id, "stale"))
            final = CompatibilityOutcome(outcome.output, outcome.failure, attempt)
            return _PreparedCandidate(
                CandidateOutcome(
                    item.account_id, "evaluated" if outcome.output is not None else "failed", final
                ),
                expected_version,
                request,
            )
        raise AssertionError("A validated retry policy must attempt at least once.")
