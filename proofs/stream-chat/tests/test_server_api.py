"""Nit 6: a charge signal stops the run on typed SDK calls too, not only raw requests.

The server client runs on an ``httpx.MockTransport``: nothing leaves the process.
"""

import unittest

import httpx
from getstream.models import MessageRequest, UserRequest

import tests  # noqa: F401
from glow_stream_proof.credentials import ServerCredentials
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.server_api import ServerApi
from glow_stream_proof.usage import GuardrailStop, Limits, UsageLedger

SECRET = "synthetic-test-secret-for-the-mock-transport"


def api_answering(status: int, body: dict[str, object]) -> tuple[ServerApi, list[str]]:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(f"{request.method} {request.url.path}")
        return httpx.Response(status, json=body)

    api = ServerApi(
        ServerCredentials("1729640", "synthetickey", SECRET),
        UsageLedger(),
        Redactor([SECRET]),
        transport=httpx.MockTransport(handler),
    )
    return api, seen


class TypedCallChargeSignalTest(unittest.TestCase):
    def test_typed_calls_stop_on_a_charge_signal(self) -> None:
        api, seen = api_answering(429, {"code": 9, "message": "Too many requests"})
        try:
            with self.assertRaises(GuardrailStop) as stopped:
                api.sdk.upsert_users(UserRequest(id="u1", role="user"))
            self.assertIn("HTTP 429", str(stopped.exception))
            with self.assertRaises(GuardrailStop):
                api.sdk.chat.send_message(
                    type="glow-match", id="c1", message=MessageRequest(text="t", user_id="u1")
                )
        finally:
            api.close()
        self.assertEqual(len(seen), 2)

    def test_billing_wording_in_an_error_stops_the_run(self) -> None:
        api, _seen = api_answering(400, {"code": 4, "message": "please upgrade your plan"})
        try:
            with self.assertRaises(GuardrailStop):
                api.sdk.upsert_users(UserRequest(id="u1", role="user"))
        finally:
            api.close()

    def test_an_ordinary_refusal_is_not_a_charge_signal(self) -> None:
        api, _seen = api_answering(403, {"code": 17, "message": "not allowed"})
        try:
            with self.assertRaises(Exception) as raised:
                api.sdk.upsert_users(UserRequest(id="u1", role="user"))
            self.assertNotIsInstance(raised.exception, GuardrailStop)
            self.assertEqual(api.raw("GET", "/api/v2/app").status, 403)
        finally:
            api.close()


class RateLimitFlagTest(unittest.TestCase):
    """P06.1-C2, nit 4: a stop says whether it was a rate limit (HTTP 429 or Stream code 9)."""

    def stop_for(self, status: int, body: dict[str, object]) -> GuardrailStop:
        api, _seen = api_answering(status, body)
        try:
            with self.assertRaises(GuardrailStop) as raw:
                api.raw("GET", "/api/v2/app")
            with self.assertRaises(GuardrailStop) as typed:
                api.sdk.upsert_users(UserRequest(id="u1", role="user"))
        finally:
            api.close()
        self.assertEqual(raw.exception.rate_limited, typed.exception.rate_limited)
        return raw.exception

    def test_rate_limits(self) -> None:
        self.assertTrue(
            self.stop_for(429, {"code": 9, "message": "Too many requests"}).rate_limited
        )
        self.assertTrue(self.stop_for(429, {"message": "slow down"}).rate_limited)
        self.assertTrue(self.stop_for(400, {"code": 9, "message": "rate limited"}).rate_limited)

    def test_the_result_check_flags_a_rate_limit(self) -> None:
        # The response hook raises first for every live response; the second check
        # in ServerApi._result must flag a rate limit the same way.
        api, _seen = api_answering(200, {})
        try:
            for status, body, limited in (
                (429, {"code": 9, "message": "x"}, True),
                (402, {"code": 9, "message": "x"}, False),
            ):
                response = httpx.Response(status, json=body)
                with self.assertRaises(GuardrailStop) as stopped:
                    api._result("GET", "/api/v2/app", response)
                self.assertEqual(stopped.exception.rate_limited, limited, status)
        finally:
            api.close()

    def test_charge_signals_are_not_rate_limits(self) -> None:
        self.assertFalse(self.stop_for(402, {"code": 9, "message": "x"}).rate_limited)
        self.assertFalse(self.stop_for(403, {"code": 99, "message": "suspended"}).rate_limited)
        self.assertFalse(self.stop_for(400, {"code": 4, "message": "upgrade"}).rate_limited)


class StopAtOnceFlagTest(unittest.TestCase):
    """P06.1-C3, finding 2: every charge or limit signal says it stops the run at once,
    and is recorded in the run's ledger as it is raised, so the run's record holds it
    wherever it is met, even if its stop is replaced later. A budget guardrail is not."""

    SIGNALS = (
        (402, {"code": 4, "message": "x"}),
        (403, {"code": 99, "message": "suspended"}),
        (400, {"code": 4, "message": "please upgrade your plan"}),
        (429, {"code": 9, "message": "Too many requests"}),
    )

    def test_typed_and_raw_calls_mark_the_signal(self) -> None:
        # The response hook raises for typed and raw calls alike.
        for status, body in self.SIGNALS:
            api, _seen = api_answering(status, body)
            try:
                with self.assertRaises(GuardrailStop) as typed:
                    api.sdk.upsert_users(UserRequest(id="u1", role="user"))
                with self.assertRaises(GuardrailStop) as raw:
                    api.raw("GET", "/api/v2/app")
            finally:
                api.close()
            self.assertTrue(typed.exception.at_once, status)
            self.assertTrue(raw.exception.at_once, status)
            self.assertEqual(api._ledger.signals, [typed.exception, raw.exception], status)

    def test_the_result_check_marks_the_signal(self) -> None:
        api, _seen = api_answering(200, {})
        stops: list[GuardrailStop] = []
        try:
            for status, body in self.SIGNALS:
                with self.assertRaises(GuardrailStop) as stopped:
                    api._result("GET", "/api/v2/app", httpx.Response(status, json=body))
                self.assertTrue(stopped.exception.at_once, status)
                stops.append(stopped.exception)
        finally:
            api.close()
        self.assertEqual(api._ledger.signals, stops)

    def test_a_budget_guardrail_is_not_a_signal(self) -> None:
        ledger = UsageLedger(limits=Limits(api_calls=0))
        with self.assertRaises(GuardrailStop) as stopped:
            ledger.reserve("api_calls")
        self.assertFalse(stopped.exception.at_once)
        self.assertEqual(ledger.signals, [])


def api_with_headers(status: int, body: dict[str, object], headers: dict[str, str]) -> ServerApi:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=body, headers=headers)

    return ServerApi(
        ServerCredentials("1729640", "synthetickey", SECRET),
        UsageLedger(),
        Redactor([SECRET]),
        transport=httpx.MockTransport(handler),
    )


class SignalKindAtTheServerTest(unittest.TestCase):
    """P06.1-I2a, "Signals, by kind": a rate limit whose wording mentions a quota,
    billing or an upgrade is not only a rate limit; a stop names the reset."""

    def stops(self, status: int, body: dict[str, object]) -> list[GuardrailStop]:
        api = api_with_headers(status, body, {"x-ratelimit-reset": "1790309999"})
        try:
            with self.assertRaises(GuardrailStop) as typed:
                api.sdk.upsert_users(UserRequest(id="u1", role="user"))
            with self.assertRaises(GuardrailStop) as raw:
                api.raw("GET", "/api/v2/app")
            response = httpx.Response(status, json=body, headers={"x-ratelimit-reset": "1"})
            with self.assertRaises(GuardrailStop) as result:
                api._result("GET", "/api/v2/app", response)
        finally:
            api.close()
        return [typed.exception, raw.exception, result.exception]

    def test_only_a_rate_limit(self) -> None:
        for stop in self.stops(429, {"code": 9, "message": "Too many requests"}):
            self.assertTrue(stop.only_rate_limit)

    def test_a_rate_limit_with_quota_wording_is_a_charge_signal(self) -> None:
        for stop in self.stops(429, {"code": 9, "message": "monthly quota exceeded"}):
            self.assertTrue(stop.rate_limited)
            self.assertTrue(stop.billing)
            self.assertFalse(stop.only_rate_limit)

    def test_the_stop_names_the_reset(self) -> None:
        typed, raw, result = self.stops(429, {"code": 9, "message": "Too many requests"})
        self.assertIn("HTTP 429 (x-ratelimit-reset 1790309999); stopping at once", str(typed))
        self.assertIn("HTTP 429 (x-ratelimit-reset 1790309999); stopping at once", str(raw))
        self.assertIn("HTTP 429 (x-ratelimit-reset 1); stopping at once", str(result))


if __name__ == "__main__":
    unittest.main()
