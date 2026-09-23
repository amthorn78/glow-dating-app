"""Closed telemetry vocabulary: no raw records, request data or exception text."""

import io
import json
import logging
import logging.config
import math
from collections.abc import Callable, Mapping
from contextvars import ContextVar
from enum import Enum
from time import monotonic
from typing import Any
from uuid import UUID, uuid4

from glow_domain.worker_execution import WorkerObservation


class Event(Enum):
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"
    CONFIGURATION_REJECTED = "configuration_rejected"
    WORKER_ATTEMPT = "worker_attempt"
    WORKER_RETRY = "worker_retry"
    WORKER_COMPLETED = "worker_completed"
    FRAMEWORK_DIAGNOSTIC = "framework_diagnostic"
    SERVER_ERROR = "server_error"


_correlation: ContextVar[str | None] = ContextVar("glow_correlation", default=None)
_logger = logging.getLogger("glow.telemetry")
_routes = {
    "/health/live": "liveness",
    "/health/ready": "readiness",
    "/api/v1/development/recommendations": "development_recommendations",
}
_enums = {
    "route": {*_routes.values(), "unmatched"},
    "method": {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE", "other"},
    "status_class": {"1xx", "2xx", "3xx", "4xx", "5xx", "unknown"},
    "outcome": {
        "success",
        "failure",
        "rejected",
        "retry",
        "attempt",
        "exhausted",
        "permanent_failure",
        "deadline_exceeded",
        "cancelled",
        "unexpected_failure",
    },
    "error_code": {
        "none",
        "configuration_invalid",
        "unexpected_failure",
        "http_rejected",
        "timeout",
        "outage",
        "unsupported",
        "malformed_output",
        "identity_mismatch",
        "stale",
        "consent_required",
        "idempotency_conflict",
        "deadline_exceeded",
        "cancelled",
        "attempt_limit",
        "clock_invalid",
    },
    "component": {"api", "worker", "framework", "server"},
}
_numbers = {"duration_ms": 300_000.0, "delay_ms": 30_000.0, "attempt": 5.0}


def _is_correlation(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 36:
        return False
    try:
        parsed = UUID(value)
    except ValueError:
        return False
    return parsed.version == 4 and str(parsed) == value


def correlation_id(incoming: object = None) -> str:
    """Accept only one bounded canonical UUIDv4; regenerate every invalid value.

    This is untrusted tracing metadata, never an identity or idempotency key.
    """
    return incoming if isinstance(incoming, str) and _is_correlation(incoming) else str(uuid4())


def _validated_event(event: Event, fields: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(event, Event):
        raise ValueError("Telemetry event is not declared.")
    result: dict[str, object] = {"event": event.value}
    for name, value in fields.items():
        if name == "correlation_id":
            valid = _is_correlation(value)
        elif name in _enums:
            valid = isinstance(value, str) and value in _enums[name]
        elif name in _numbers:
            valid = (
                type(value) in {int, float}
                and 0 <= value <= _numbers[name]  # type: ignore[operator]
                and math.isfinite(value)  # type: ignore[arg-type]
                and (name != "attempt" or type(value) is int)
            )
        else:
            valid = False
        if not valid:
            raise ValueError("Telemetry field or value is not declared.")
        result[name] = value
    return result


def emit_event(event: Event, **fields: object) -> None:
    if "correlation_id" not in fields and _correlation.get() is not None:
        fields["correlation_id"] = _correlation.get()
    payload = _validated_event(event, fields)
    level = logging.ERROR if fields.get("outcome") == "unexpected_failure" else logging.INFO
    _logger.log(level, "", extra={"glow_event": payload})


def metric_labels(event: Event, **fields: object) -> dict[str, object]:
    """Closed dimensions for a future collector; never use IDs or measurements."""
    validated = _validated_event(event, fields)
    return {key: value for key, value in validated.items() if key == "event" or key in _enums}


class SafeJsonFormatter(logging.Formatter):
    """Never format msg/args, logger names, extras, exception/stack or requests.

    The final sink validates even custom event records again. Unexpected logging
    calls remain observable as a fixed diagnostic, with their payload discarded.
    """

    def format(self, record: logging.LogRecord) -> str:
        output: dict[str, object] = {
            "event": Event.FRAMEWORK_DIAGNOSTIC.value,
            "component": "framework",
        }
        supplied = getattr(record, "glow_event", None)
        if type(supplied) is dict:
            try:
                event = Event(supplied.get("event"))
                output = _validated_event(
                    event, {k: v for k, v in supplied.items() if k != "event"}
                )
            except Exception:
                # Formatting must never invoke logging's raw diagnostic fallback,
                # even for a malformed record produced by an unrelated library.
                pass
        output["level"] = (
            "error"
            if type(record.levelno) is int and record.levelno >= logging.ERROR
            else "warning"
            if type(record.levelno) is int and record.levelno >= logging.WARNING
            else "info"
        )
        current = _correlation.get()
        if current is not None and "correlation_id" not in output:
            output["correlation_id"] = current
        return json.dumps(output, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"safe": {"()": "glow_api.telemetry.SafeJsonFormatter"}},
    "handlers": {
        "safe": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "safe",
        },
    },
    "root": {"handlers": ["safe"], "level": "INFO"},
    "loggers": {
        "glow.telemetry": {"handlers": ["safe"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["safe"], "level": "INFO", "propagate": False},
        "django.server": {"handlers": ["safe"], "level": "INFO", "propagate": False},
        "gunicorn.error": {"handlers": ["safe"], "level": "INFO", "propagate": False},
        "gunicorn.access": {"handlers": [], "level": "CRITICAL", "propagate": False},
    },
}


def configure_logging() -> None:
    """Also used before settings validation, before Django configures logging."""
    logging.config.dictConfig(LOGGING)


def observe_worker(observation: WorkerObservation) -> None:
    """Explicit domain-to-telemetry bridge; no work identifiers/payload accepted."""
    event = {
        "attempt": Event.WORKER_ATTEMPT,
        "retry": Event.WORKER_RETRY,
        "completed": Event.WORKER_COMPLETED,
    }.get(observation.kind)
    if event is None:
        raise ValueError("Worker observation is not declared.")
    emit_event(
        event,
        component="worker",
        attempt=observation.attempt,
        outcome=observation.outcome,
        error_code=observation.error_code,
        duration_ms=observation.duration_ms,
        delay_ms=observation.delay_ms,
    )


class SafeErrorStream(io.TextIOBase):
    """WSGI stderr discards raw traceback chunks and emits one fixed event."""

    def __init__(self) -> None:
        super().__init__()
        self._reported = False

    def write(self, text: str) -> int:
        if text and not self._reported:
            self._reported = True
            emit_event(Event.SERVER_ERROR, component="server", error_code="unexpected_failure")
        return len(text)


class CorrelationMiddleware:
    def __init__(self, get_response: Callable[[Any], Any]) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        identifier = correlation_id(request.META.get("HTTP_X_CORRELATION_ID"))
        token = _correlation.set(identifier)
        request.correlation_id = identifier
        started = monotonic()
        route = _routes.get(request.path_info, "unmatched")
        method = request.method if request.method in _enums["method"] else "other"
        try:
            response = self.get_response(request)
            status = response.status_code
            status_class = f"{status // 100}xx" if 100 <= status <= 599 else "unknown"
            emit_event(
                Event.REQUEST_COMPLETED,
                component="api",
                route=route,
                method=method,
                status_class=status_class,
                outcome="failure" if status >= 400 else "success",
                duration_ms=min(300_000.0, max(0.0, (monotonic() - started) * 1000)),
            )
            response["X-Correlation-ID"] = identifier
            return response
        except Exception:
            emit_event(
                Event.REQUEST_FAILED,
                component="api",
                route=route,
                method=method,
                outcome="unexpected_failure",
                error_code="unexpected_failure",
            )
            raise
        finally:
            _correlation.reset(token)
