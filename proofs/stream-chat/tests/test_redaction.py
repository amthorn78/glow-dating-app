import time
import unittest

import jwt

import tests  # noqa: F401
from glow_stream_proof.redaction import (
    REDACTED_JWT,
    REDACTED_SECRET,
    Redactor,
    describe_token,
    find_leaks,
    token_lifetime_seconds,
)

SECRET = "synthetic-test-secret-not-a-real-one"


def _token(claims: dict[str, object], secret: str = SECRET) -> str:
    return jwt.encode(claims, secret, algorithm="HS256")


class RedactionTest(unittest.TestCase):
    def test_secret_and_jwt_are_replaced(self) -> None:
        token = _token({"user_id": "u1", "iat": 1, "exp": 2})
        text = f"secret={SECRET} header Authorization: {token} end"
        out = Redactor([SECRET]).text(text)
        self.assertNotIn(SECRET, out)
        self.assertNotIn(token, out)
        self.assertIn(REDACTED_SECRET, out)
        self.assertIn(REDACTED_JWT, out)

    def test_dev_token_is_replaced(self) -> None:
        dev = _token({"user_id": "u1"}).rsplit(".", 1)[0] + ".devtoken"
        self.assertEqual(Redactor().text(dev), REDACTED_JWT)

    def test_nested_values_and_sensitive_keys(self) -> None:
        token = _token({"user_id": "guest"})
        body = {
            "access_token": token,
            "user": {"id": "u1", "notes": [f"has {SECRET}"]},
            "token": "opaque-not-jwt",
        }
        out = Redactor([SECRET]).value(body)
        self.assertEqual(out["access_token"], REDACTED_JWT)
        self.assertEqual(out["token"], REDACTED_SECRET)
        self.assertEqual(out["user"]["notes"], [f"has {REDACTED_SECRET}"])
        self.assertEqual(out["user"]["id"], "u1")

    def test_find_leaks(self) -> None:
        token = _token({"user_id": "u1"})
        self.assertEqual(find_leaks("nothing here", [SECRET]), [])
        self.assertEqual(find_leaks(f"x {SECRET}", [SECRET]), ["contains a known secret"])
        self.assertEqual(find_leaks(f"x {token}", [SECRET]), ["contains a JWT-shaped value"])

    def test_sensitive_keys_are_matched_by_pattern(self) -> None:
        # Nit 8: credential-bearing keys in app configuration, not only exact names.
        body = {
            "sqs_secret": "plain",
            "push": {"apn": {"auth_key": "-----key-----"}, "firebase_credentials": {"k": "v"}},
            "refresh_token": "opaque",
            "db_password": "pw",
            "revoke_tokens_issued_before": "2026-09-25T00:00:00Z",
            "api_key": "abcdefghijkl",
            "id": "u1",
        }
        out = Redactor().value(body)
        self.assertEqual(out["sqs_secret"], REDACTED_SECRET)
        self.assertEqual(out["push"]["apn"]["auth_key"], REDACTED_SECRET)
        self.assertEqual(out["push"]["firebase_credentials"], REDACTED_SECRET)
        self.assertEqual(out["refresh_token"], REDACTED_SECRET)
        self.assertEqual(out["db_password"], REDACTED_SECRET)
        self.assertEqual(out["revoke_tokens_issued_before"], "2026-09-25T00:00:00Z")
        self.assertEqual(out["api_key"], "abcdefghijkl")
        self.assertEqual(out["id"], "u1")

    def test_api_key_is_not_redacted(self) -> None:
        # The API key is client-safe and may appear in evidence.
        self.assertEqual(Redactor([SECRET]).text("api_key=abcdefghijkl"), "api_key=abcdefghijkl")


class TokenDescriptionTest(unittest.TestCase):
    def test_claims_without_token(self) -> None:
        now = int(time.time())
        token = _token({"user_id": "p061i1-x-ua", "iat": now - 5, "exp": now + 895})
        described = describe_token(token)
        self.assertEqual(described["alg"], "HS256")
        self.assertEqual(described["claims"]["user_id"], "p061i1-x-ua")
        self.assertTrue(str(described["signature"]).startswith("present"))
        self.assertNotIn(token, repr(described))
        self.assertEqual(token_lifetime_seconds(token), 900)

    def test_dev_and_malformed(self) -> None:
        dev = _token({"user_id": "u1"}).rsplit(".", 1)[0] + ".devtoken"
        self.assertEqual(describe_token(dev)["signature"], "literal-devtoken")
        self.assertEqual(describe_token("not.a.jwt")["form"], "undecodable-jwt")
        self.assertEqual(describe_token("plain")["form"], "not-a-jwt")
        self.assertIsNone(token_lifetime_seconds(_token({"user_id": "u1"})))


if __name__ == "__main__":
    unittest.main()
