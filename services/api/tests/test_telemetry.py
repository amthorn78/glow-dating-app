import contextlib
import io
import json
import logging
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID
from wsgiref.simple_server import make_server

from django.test import SimpleTestCase, override_settings
from django.urls import path

from glow_api.devserver import SafeRequestHandler, SafeWSGIServer
from glow_api.telemetry import (
    CorrelationMiddleware,
    Event,
    SafeErrorStream,
    SafeJsonFormatter,
    correlation_id,
    emit_event,
    metric_labels,
    observe_worker,
)
from glow_domain.provider_contracts import ExpectedProviderFailure, FailureCode
from glow_domain.worker_execution import RetryBudget, WorkerExecutionError, execute_with_retry

SENTINEL = "SYNTHETIC_PRIVATE_BIRTH_LOCATION_CHAT_TOKEN"
VALID_UUID = "12345678-1234-4234-8234-123456789abc"


@contextlib.contextmanager
def captured_events():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(SafeJsonFormatter())
    loggers = [logging.getLogger(name) for name in ("glow.telemetry", "django", "gunicorn.error")]
    for logger in loggers:
        logger.addHandler(handler)
    try:
        yield stream
    finally:
        for logger in loggers:
            logger.removeHandler(handler)


def fail_view(request):
    raise RuntimeError(SENTINEL)


urlpatterns = [path("failure/", fail_view)]


class TelemetryTests(TestCase):
    def test_correlation_requires_bounded_canonical_uuidv4(self):
        self.assertEqual(correlation_id(VALID_UUID), VALID_UUID)
        for incoming in (
            SENTINEL,
            "x" * 10000,
            None,
            5,
            VALID_UUID.upper(),
            "12345678-1234-1234-8234-123456789abc",
            f"{VALID_UUID},{VALID_UUID}",
            f"{VALID_UUID}\r\n{SENTINEL}",
        ):
            value = correlation_id(incoming)
            self.assertEqual(len(value), 36)
            self.assertEqual(UUID(value).version, 4)
            self.assertNotEqual(value, incoming)

    def test_closed_fields_reject_arbitrary_data_without_echoing_it(self):
        for fields in (
            {"body": SENTINEL},
            {"error_code": SENTINEL},
            {"route": SENTINEL},
            {"correlation_id": SENTINEL},
            {"duration_ms": float("nan")},
            {"duration_ms": float("inf")},
            {"duration_ms": 10**1000},
            {"attempt": True},
            {"attempt": 99},
        ):
            with self.subTest(fields=fields), self.assertRaises(ValueError) as raised:
                emit_event(Event.REQUEST_COMPLETED, **fields)
            self.assertNotIn(SENTINEL, str(raised.exception))

    def test_formatter_drops_raw_message_args_exception_stack_request_and_extra(self):
        formatter = SafeJsonFormatter()
        try:
            raise RuntimeError(SENTINEL)
        except RuntimeError:
            record = logging.LogRecord(
                SENTINEL,
                logging.ERROR,
                SENTINEL,
                1,
                "%s",
                (SENTINEL,),
                sys.exc_info(),
            )
        record.stack_info = SENTINEL
        record.request = {"Authorization": SENTINEL, "body": SENTINEL}
        record.secret = SENTINEL
        output = formatter.format(record)
        self.assertNotIn(SENTINEL, output)
        self.assertEqual(
            json.loads(output),
            {
                "event": "framework_diagnostic",
                "component": "framework",
                "level": "error",
            },
        )
        record.glow_event = {"event": "request_completed", "body": SENTINEL}
        self.assertNotIn(SENTINEL, formatter.format(record))
        record.glow_event = {"event": "request_completed", "duration_ms": 10**1000}
        record.levelno = SENTINEL
        self.assertEqual(json.loads(formatter.format(record))["event"], "framework_diagnostic")

    def test_wsgi_error_stream_discards_whole_traceback_and_reports_once(self):
        stream = SafeErrorStream()
        with captured_events() as captured:
            self.assertEqual(stream.write(SENTINEL), len(SENTINEL))
            stream.write(f"\nTraceback: {SENTINEL}\n")
        self.assertNotIn(SENTINEL, captured.getvalue())
        self.assertEqual(len(captured.getvalue().splitlines()), 1)
        self.assertEqual(json.loads(captured.getvalue())["event"], "server_error")

    def test_metric_labels_are_closed_and_exclude_correlations_and_values(self):
        labels = metric_labels(
            Event.REQUEST_COMPLETED,
            component="api",
            route="unmatched",
            method="GET",
            status_class="4xx",
            correlation_id=VALID_UUID,
            duration_ms=10,
        )
        self.assertNotIn("correlation_id", labels)
        self.assertNotIn("duration_ms", labels)
        self.assertEqual(labels["route"], "unmatched")

    def test_configuration_failure_does_not_echo_environment_values(self):
        env = {name: value for name, value in os.environ.items() if not name.startswith("GLOW_")}
        env["GLOW_ENV"] = SENTINEL
        completed = subprocess.run(
            [sys.executable, "-c", "import glow_api.settings"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertNotIn(SENTINEL, completed.stdout + completed.stderr)
        self.assertIn('"event":"configuration_rejected"', completed.stderr)

    def test_worker_success_retry_and_unknown_failure_telemetry_do_not_capture_payload(self):
        clock = [0.0]
        calls = []

        def operation(context):
            calls.append(context)
            if len(calls) == 1:
                error = ExpectedProviderFailure(FailureCode.TIMEOUT)
                error.args = (SENTINEL,)
                raise error
            return SENTINEL

        def sleep(seconds):
            clock[0] += seconds

        arguments = {
            "idempotency_key": SENTINEL,
            "budget": RetryBudget(3, 10, 1, 0.2, 1),
            "monotonic": lambda: clock[0],
            "sleep": sleep,
            "observer": observe_worker,
        }
        with captured_events() as captured:
            result = execute_with_retry(operation, **arguments)

            def broken(context):
                raise RuntimeError(SENTINEL)

            with self.assertRaises(WorkerExecutionError):
                execute_with_retry(broken, **arguments)
        self.assertEqual(result.value, SENTINEL)
        self.assertNotIn(SENTINEL, captured.getvalue())
        records = [json.loads(line) for line in captured.getvalue().splitlines()]
        self.assertIn("worker_retry", {record["event"] for record in records})
        self.assertIn("unexpected_failure", {record.get("outcome") for record in records})

    def test_middleware_exception_resets_context_without_capturing_raw_exception(self):
        request = Mock(
            META={"HTTP_X_CORRELATION_ID": VALID_UUID},
            path_info=f"/{SENTINEL}",
            method="GET",
        )
        middleware = CorrelationMiddleware(Mock(side_effect=RuntimeError(SENTINEL)))
        with captured_events() as captured:
            with self.assertRaises(RuntimeError):
                middleware(request)
            emit_event(Event.WORKER_ATTEMPT, attempt=1, outcome="attempt")
        records = [json.loads(line) for line in captured.getvalue().splitlines()]
        self.assertNotIn(SENTINEL, captured.getvalue())
        self.assertEqual(records[0]["correlation_id"], VALID_UUID)
        self.assertNotIn("correlation_id", records[-1])


class RequestTelemetryTests(SimpleTestCase):
    databases = set()

    def test_success_and_failure_requests_omit_raw_body_queries_headers_and_paths(self):
        with captured_events() as captured:
            response = self.client.get(
                f"/health/live?token={SENTINEL}",
                HTTP_AUTHORIZATION=f"Bearer {SENTINEL}",
                HTTP_X_CORRELATION_ID=VALID_UUID,
            )
            self.client.post(f"/{SENTINEL}?location={SENTINEL}", data={"chat": SENTINEL})
            self.client.get("/health/live", HTTP_HOST=f"{SENTINEL}.invalid")
        self.assertEqual(response.json(), {"status": "alive"})
        self.assertEqual(response["X-Correlation-ID"], VALID_UUID)
        self.assertNotIn(SENTINEL, captured.getvalue())
        records = [json.loads(line) for line in captured.getvalue().splitlines()]
        self.assertIn("unmatched", {record.get("route") for record in records})
        self.assertIn("4xx", {record.get("status_class") for record in records})

    def test_readiness_and_invalid_correlation_preserve_body_and_regenerate(self):
        response = self.client.get("/health/ready", HTTP_X_CORRELATION_ID=SENTINEL)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "status": "not_ready",
                "mode": "fixture",
                "reason": "live_integrations_not_configured",
            },
        )
        self.assertEqual(UUID(response["X-Correlation-ID"]).version, 4)

    @override_settings(ROOT_URLCONF=__name__)
    def test_django_caught_exception_does_not_log_message_or_traceback(self):
        self.client.raise_request_exception = False
        with captured_events() as captured:
            response = self.client.get(f"/failure/?birth={SENTINEL}")
        self.assertEqual(response.status_code, 500)
        self.assertNotIn(SENTINEL, captured.getvalue())
        self.assertIn('"status_class":"5xx"', captured.getvalue())

    def test_actual_wsgi_access_and_exception_stderr_do_not_leak_request_data(self):
        def broken_app(environ, start_response):
            raise RuntimeError(SENTINEL)

        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with (
            captured_events() as captured,
            make_server(
                "127.0.0.1",
                0,
                broken_app,
                server_class=SafeWSGIServer,
                handler_class=SafeRequestHandler,
            ) as server,
        ):
            thread = threading.Thread(target=server.handle_request, daemon=True)
            thread.start()
            try:
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    opener.open(f"http://127.0.0.1:{server.server_port}/{SENTINEL}", timeout=3)
                self.assertEqual(raised.exception.code, 500)
                raised.exception.close()
            finally:
                thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertNotIn(SENTINEL, captured.getvalue())
        self.assertIn('"event":"server_error"', captured.getvalue())
