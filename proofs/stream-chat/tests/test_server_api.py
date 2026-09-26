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
from glow_stream_proof.usage import GuardrailStop, UsageLedger

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


if __name__ == "__main__":
    unittest.main()
