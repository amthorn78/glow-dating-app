"""Cooperative bounded execution only; no queue, persistence or activation.

Operations must enforce the supplied per-attempt timeout in their actual I/O,
and freshly authorize each invocation, including an idempotent replay. A sync
callback cannot be forcibly interrupted here. Unknown exceptions fail loudly
with a fixed error, without exposing arbitrary adapter exception text.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from time import monotonic as system_monotonic
from time import sleep as system_sleep

from .provider_contracts import ExpectedProviderFailure, FailureCode


class ExecutionState(Enum):
    SUCCESS = "success"
    EXHAUSTED = "exhausted"
    PERMANENT_FAILURE = "permanent_failure"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    CANCELLED = "cancelled"


class WorkerExecutionError(RuntimeError):
    """A defect, never translated into synthetic provider success or retried."""


@dataclass(frozen=True)
class RetryBudget:
    max_attempts: int
    total_seconds: float
    attempt_seconds: float
    initial_backoff_seconds: float
    max_backoff_seconds: float

    def __post_init__(self) -> None:
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 5:
            raise ValueError("Worker attempts must be between one and five.")
        for value, maximum in (
            (self.total_seconds, 300),
            (self.attempt_seconds, 60),
            (self.initial_backoff_seconds, 30),
            (self.max_backoff_seconds, 30),
        ):
            if (
                type(value) not in {int, float}
                or not 0 < value <= maximum
                or not math.isfinite(value)
            ):
                raise ValueError("Worker time budget is outside its bounded range.")
        if self.attempt_seconds > self.total_seconds:
            raise ValueError("Attempt timeout exceeds total deadline.")
        if self.initial_backoff_seconds > self.max_backoff_seconds:
            raise ValueError("Initial delay exceeds maximum backoff.")


@dataclass(frozen=True)
class AttemptContext:
    attempt: int
    deadline: float
    timeout_seconds: float
    idempotency_key: str = field(repr=False)


@dataclass(frozen=True)
class WorkerObservation:
    kind: str
    attempt: int
    outcome: str
    error_code: str = "none"
    duration_ms: float = 0
    delay_ms: float = 0


@dataclass(frozen=True)
class ExecutionResult[T]:
    state: ExecutionState
    attempts: int
    value: T | None = field(default=None, repr=False)
    failure: FailureCode | None = None


def execute_with_retry[T](
    operation: Callable[[AttemptContext], T],
    *,
    idempotency_key: str,
    budget: RetryBudget,
    monotonic: Callable[[], float] = system_monotonic,
    sleep: Callable[[float], None] = system_sleep,
    cancelled: Callable[[], bool] = lambda: False,
    observer: Callable[[WorkerObservation], None] = lambda observation: None,
) -> ExecutionResult[T]:
    """Retry only TIMEOUT/OUTAGE within total, per-attempt and count budgets.

    Stable keys do not themselves prevent duplicate effects. The provider/UOW
    must enforce payload-bound idempotency and current authorization. No result
    cache or replay ledger exists here. Cancellation/deadline after a call can
    mean an uncertain external effect; reconcile before scheduling further work.
    """
    if not isinstance(budget, RetryBudget):
        raise ValueError("Worker requires a validated budget.")
    if (
        not isinstance(idempotency_key, str)
        or not 1 <= len(idempotency_key) <= 128
        or not idempotency_key.isascii()
        or not idempotency_key.isprintable()
        or not idempotency_key.strip()
    ):
        raise ValueError("Worker requires a bounded opaque idempotency key.")
    previous_time = -math.inf

    def now() -> float:
        nonlocal previous_time
        value = monotonic()
        if (
            type(value) not in {int, float}
            or not -1e300 <= value <= 1e300
            or not math.isfinite(value)
            or value < previous_time
        ):
            raise WorkerExecutionError("Worker monotonic clock is invalid.") from None
        previous_time = value
        return value

    started = now()
    deadline = started + budget.total_seconds
    attempts = 0

    def finish(state: ExecutionState, failure: FailureCode | None = None) -> ExecutionResult[T]:
        observer(
            WorkerObservation(
                "completed",
                attempts,
                state.value,
                failure.value
                if failure is not None
                else (
                    state.value
                    if state in {ExecutionState.CANCELLED, ExecutionState.DEADLINE_EXCEEDED}
                    else "none"
                ),
                min(300_000.0, max(0.0, (now() - started) * 1000)),
            )
        )
        return ExecutionResult(state, attempts, failure=failure)

    while attempts < budget.max_attempts:
        if cancelled():
            return finish(ExecutionState.CANCELLED)
        current = now()
        if current >= deadline:
            return finish(ExecutionState.DEADLINE_EXCEEDED)
        attempts += 1
        timeout = min(budget.attempt_seconds, deadline - current)
        context = AttemptContext(attempts, current + timeout, timeout, idempotency_key)
        observer(WorkerObservation("attempt", attempts, "attempt"))
        try:
            value = operation(context)
        except ExpectedProviderFailure as error:
            failure = error.code
        except Exception:
            observer(
                WorkerObservation(
                    "completed",
                    attempts,
                    "unexpected_failure",
                    "unexpected_failure",
                )
            )
            raise WorkerExecutionError("Worker operation failed unexpectedly.") from None
        else:
            if cancelled():
                return finish(ExecutionState.CANCELLED)
            if now() >= context.deadline:
                return finish(ExecutionState.DEADLINE_EXCEEDED)
            finish(ExecutionState.SUCCESS)
            return ExecutionResult(ExecutionState.SUCCESS, attempts, value=value)
        if cancelled():
            return finish(ExecutionState.CANCELLED, failure)
        if now() >= deadline:
            return finish(ExecutionState.DEADLINE_EXCEEDED, failure)
        if failure not in {FailureCode.TIMEOUT, FailureCode.OUTAGE}:
            return finish(ExecutionState.PERMANENT_FAILURE, failure)
        if attempts == budget.max_attempts:
            return finish(ExecutionState.EXHAUSTED, failure)
        delay = min(
            budget.initial_backoff_seconds * 2 ** (attempts - 1), budget.max_backoff_seconds
        )
        if now() + delay >= deadline:
            return finish(ExecutionState.DEADLINE_EXCEEDED, failure)
        observer(
            WorkerObservation("retry", attempts, "retry", failure.value, delay_ms=delay * 1000)
        )
        wait_until = now() + delay
        while True:
            if cancelled():
                return finish(ExecutionState.CANCELLED, failure)
            remaining = wait_until - now()
            if remaining <= 0:
                break
            # Short waits give cooperative cancellation a bounded polling interval.
            sleep(min(0.1, remaining))
    raise AssertionError("Validated worker budget must terminate inside its bounds.")
