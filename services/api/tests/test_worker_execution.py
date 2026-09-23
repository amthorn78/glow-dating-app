from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch

from glow_domain.provider_contracts import ExpectedProviderFailure, FailureCode
from glow_domain.worker_execution import (
    ExecutionState,
    RetryBudget,
    WorkerExecutionError,
    execute_with_retry,
)


class Clock:
    def __init__(self):
        self.time = 100.0
        self.sleeps = []

    def now(self):
        return self.time

    def sleep(self, delay):
        self.sleeps.append(delay)
        self.time += delay


class WorkerTests(TestCase):
    def setUp(self):
        self.network = patch("socket.socket", side_effect=AssertionError("No network allowed"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.clock = Clock()
        self.budget = RetryBudget(3, 10, 2, 0.2, 1)
        self.observations = []
        self.calls = []

    def execute(self, operation, **kwargs):
        arguments = {
            "idempotency_key": "synthetic-operation-1",
            "budget": self.budget,
            "monotonic": self.clock.now,
            "sleep": self.clock.sleep,
            "observer": self.observations.append,
        }
        arguments.update(kwargs)
        return execute_with_retry(operation, **arguments)

    def scripted(self, failures):
        def operation(context):
            self.calls.append(context)
            if len(self.calls) <= len(failures):
                raise ExpectedProviderFailure(failures[len(self.calls) - 1])
            return "synthetic-output"

        return operation

    def test_eventual_success_has_bounded_exponential_delay_and_one_stable_key(self):
        result = self.execute(self.scripted([FailureCode.TIMEOUT, FailureCode.OUTAGE]))
        self.assertEqual(result.state, ExecutionState.SUCCESS)
        self.assertEqual(result.attempts, 3)
        self.assertEqual(result.value, "synthetic-output")
        self.assertEqual([c.idempotency_key for c in self.calls], ["synthetic-operation-1"] * 3)
        self.assertEqual([c.timeout_seconds for c in self.calls], [2, 2, 2])
        self.assertEqual([o.delay_ms for o in self.observations if o.kind == "retry"], [200, 400])
        self.assertAlmostEqual(sum(self.clock.sleeps), 0.6)
        self.assertTrue(all(0 < delay <= 0.1 for delay in self.clock.sleeps))

    def test_repeated_transient_failure_stops_at_attempt_budget(self):
        result = self.execute(self.scripted([FailureCode.OUTAGE] * 10))
        self.assertEqual(result.state, ExecutionState.EXHAUSTED)
        self.assertEqual(result.failure, FailureCode.OUTAGE)
        self.assertEqual(len(self.calls), 3)

    def test_every_permanent_code_stops_without_sleep(self):
        for failure in set(FailureCode) - {FailureCode.TIMEOUT, FailureCode.OUTAGE}:
            self.calls.clear()
            with self.subTest(failure=failure):
                result = self.execute(self.scripted([failure]))
                self.assertEqual(result.state, ExecutionState.PERMANENT_FAILURE)
                self.assertEqual(result.failure, failure)
                self.assertEqual(len(self.calls), 1)
                self.assertEqual(self.clock.sleeps, [])

    def test_unknown_error_raises_safe_defect_without_retry_or_exception_chain(self):
        sentinel = "SYNTHETIC_PRIVATE_BIRTH_LOCATION_TOKEN"

        def operation(context):
            self.calls.append(context)
            raise RuntimeError(sentinel)

        with self.assertRaises(WorkerExecutionError) as raised:
            self.execute(operation)
        self.assertNotIn(sentinel, str(raised.exception))
        self.assertTrue(raised.exception.__suppress_context__)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.clock.sleeps, [])
        self.assertEqual(self.observations[-1].outcome, "unexpected_failure")

    def test_deadline_prevents_an_unaffordable_retry(self):
        result = self.execute(
            self.scripted([FailureCode.TIMEOUT]),
            budget=RetryBudget(3, 0.2, 0.2, 0.2, 1),
        )
        self.assertEqual(result.state, ExecutionState.DEADLINE_EXCEEDED)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.clock.sleeps, [])

    def test_attempt_timeout_late_success_is_not_accepted_or_retried(self):
        def operation(context):
            self.calls.append(context)
            self.clock.time = context.deadline
            return "uncertain external effect"

        result = self.execute(operation)
        self.assertEqual(result.state, ExecutionState.DEADLINE_EXCEEDED)
        self.assertIsNone(result.value)
        self.assertEqual(len(self.calls), 1)

    def test_late_failure_uses_total_deadline(self):
        def operation(context):
            self.clock.time += 11
            raise ExpectedProviderFailure(FailureCode.TIMEOUT)

        result = self.execute(operation)
        self.assertEqual(result.state, ExecutionState.DEADLINE_EXCEEDED)
        self.assertEqual(result.attempts, 1)

    def test_cancellation_before_attempt_during_backoff_and_after_call(self):
        before = self.execute(self.scripted([]), cancelled=lambda: True)
        self.assertEqual(before.state, ExecutionState.CANCELLED)
        self.assertEqual(before.attempts, 0)
        during = self.execute(
            self.scripted([FailureCode.OUTAGE]),
            cancelled=lambda: len(self.clock.sleeps) >= 1,
        )
        self.assertEqual(during.state, ExecutionState.CANCELLED)
        self.assertEqual(during.attempts, 1)
        after = self.execute(self.scripted([]), cancelled=lambda: len(self.calls) >= 2)
        self.assertEqual(after.state, ExecutionState.CANCELLED)
        self.assertIsNone(after.value)

    def test_remaining_deadline_caps_timeout_for_later_attempt(self):
        def operation(context):
            self.calls.append(context)
            if context.attempt == 1:
                self.clock.time += 1.5
                raise ExpectedProviderFailure(FailureCode.TIMEOUT)
            return None

        result = self.execute(operation, budget=RetryBudget(3, 2, 2, 0.2, 0.2))
        self.assertEqual(result.state, ExecutionState.SUCCESS)
        self.assertAlmostEqual(self.calls[1].timeout_seconds, 0.3)

    def test_advancing_clock_cannot_send_negative_duration_to_sleep(self):
        def advancing_clock():
            self.clock.time += 0.11
            return self.clock.time

        def checked_sleep(duration):
            self.assertGreater(duration, 0)
            self.clock.sleep(duration)

        result = self.execute(
            self.scripted([FailureCode.TIMEOUT]),
            monotonic=advancing_clock,
            sleep=checked_sleep,
        )
        self.assertEqual(result.state, ExecutionState.SUCCESS)

    def test_nonfinite_backward_clocks_fail_loudly(self):
        for value in (float("inf"), float("nan"), True, "private"):
            with self.subTest(value=value), self.assertRaises(WorkerExecutionError):
                self.execute(self.scripted([]), monotonic=lambda value=value: value)
        times = iter([100, 99])
        with self.assertRaises(WorkerExecutionError):
            self.execute(self.scripted([]), monotonic=lambda: next(times))

    def test_malformed_budgets_and_keys_reject_before_any_work(self):
        for field in (
            "max_attempts",
            "total_seconds",
            "attempt_seconds",
            "initial_backoff_seconds",
            "max_backoff_seconds",
        ):
            for value in (True, float("nan"), float("inf"), -1, 0, 301, "private"):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    replace(self.budget, **{field: value})
        for key in ("", " ", "x" * 129, "invalid\nkey", "é", None):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.execute(self.scripted([]), idempotency_key=key)
        self.assertEqual(self.calls, [])

    def test_duplicate_work_substitute_reuses_effect_and_rechecks_authorization(self):
        # One tiny test substitute, not a persistence implementation or production ledger.
        receipts = {}
        effects = []
        consent = [True]
        payload = ["fixed-synthetic-payload"]

        def operation(context):
            if not consent[0]:
                raise ExpectedProviderFailure(FailureCode.CONSENT_REQUIRED)
            if context.idempotency_key not in receipts:
                effects.append(payload[0])
                receipts[context.idempotency_key] = payload[0]
            elif receipts[context.idempotency_key] != payload[0]:
                raise ExpectedProviderFailure(FailureCode.IDEMPOTENCY_CONFLICT)
            return receipts[context.idempotency_key]

        first = self.execute(operation)
        replay = self.execute(operation)
        self.assertEqual(first.value, replay.value)
        self.assertEqual(len(effects), 1)
        payload[0] = "changed-synthetic-payload"
        conflict = self.execute(operation)
        self.assertEqual(conflict.failure, FailureCode.IDEMPOTENCY_CONFLICT)
        self.assertEqual(len(effects), 1)
        consent[0] = False
        rejected = self.execute(operation)
        self.assertEqual(rejected.state, ExecutionState.PERMANENT_FAILURE)
        self.assertEqual(rejected.failure, FailureCode.CONSENT_REQUIRED)
        self.assertEqual(len(effects), 1)

    def test_context_and_result_repr_hide_keys_and_payloads(self):
        sentinel = "SYNTHETIC_SECRET"
        result = self.execute(self.scripted([]), idempotency_key=sentinel)
        self.assertNotIn(sentinel, repr(self.calls[0]))
        self.assertNotIn("synthetic-output", repr(result))
