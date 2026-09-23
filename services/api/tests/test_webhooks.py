"""Synthetic byte authentication only; no account, endpoint, SDK or database."""

import hashlib
import hmac
from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch

from glow_domain.webhooks import (
    MAX_API_KEY_BYTES,
    MAX_BODY_BYTES,
    MAX_SECRET_BYTES,
    SignatureStatus,
    StreamSignatureResult,
    StreamWebhookCredentials,
    WebhookAdmissionUnavailable,
    require_durable_webhook_admission,
    verify_stream_signature,
)


class StreamWebhookTests(TestCase):
    def setUp(self):
        guard = patch("socket.socket", side_effect=AssertionError("Network is forbidden."))
        guard.start()
        self.addCleanup(guard.stop)
        self.credentials = StreamWebhookCredentials("synthetic-app", b"SYNTHETIC-SECRET-SENTINEL")
        self.body = b'{"type":"message.new","text":"PRIVATE-SENTINEL"}\n'
        self.signature = hmac.new(self.credentials.secret, self.body, hashlib.sha256).hexdigest()

    def verify(self, **changes):
        arguments = {
            "raw_body": self.body,
            "signature": self.signature,
            "api_key": self.credentials.api_key,
            "credentials": self.credentials,
            "enabled": True,
        }
        arguments.update(changes)
        return verify_stream_signature(**arguments)

    def test_known_hmac_sha256_vector(self):
        # RFC 4231 test case 1; pure authentication does not parse event JSON.
        credentials = StreamWebhookCredentials("synthetic-app", b"\x0b" * 20)
        result = verify_stream_signature(
            b"Hi There",
            "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7",
            "synthetic-app",
            credentials,
            enabled=True,
        )
        self.assertEqual(result.status, SignatureStatus.AUTHENTICATED)

    def test_exact_bytes_required_including_whitespace_and_utf8(self):
        self.assertEqual(self.verify().status, SignatureStatus.AUTHENTICATED)
        for body in (
            self.body.rstrip(),
            self.body.replace(b'"type":', b'"type": '),
            self.body.replace(b"PRIVATE-SENTINEL", "synthetic-é".encode()),
        ):
            with self.subTest(body_length=len(body)):
                self.assertEqual(
                    self.verify(raw_body=body).status, SignatureStatus.AUTHENTICATION_FAILED
                )
        unicode_body = '{"text":"synthetic-é"}\n'.encode()
        signature = hmac.new(self.credentials.secret, unicode_body, hashlib.sha256).hexdigest()
        self.assertEqual(
            self.verify(raw_body=unicode_body, signature=signature).status,
            SignatureStatus.AUTHENTICATED,
        )

    def test_missing_malformed_and_combined_signatures_rejected(self):
        for signature in (None, "", b"0" * 64, "a" * 63, "g" * 64, "a" * 65, "a,b", "\n" * 64):
            with self.subTest(signature_type=type(signature).__name__):
                self.assertEqual(self.verify(signature=signature).status, SignatureStatus.MALFORMED)
        self.assertEqual(
            self.verify(signature="0" * 64).status, SignatureStatus.AUTHENTICATION_FAILED
        )

    def test_api_key_bound_to_explicit_configuration(self):
        self.assertEqual(
            self.verify(api_key="different-app").status, SignatureStatus.AUTHENTICATION_FAILED
        )
        for key in (None, "", "a" * (MAX_API_KEY_BYTES + 1), "header\rinjection", "é"):
            self.assertEqual(self.verify(api_key=key).status, SignatureStatus.MALFORMED)

    def test_body_is_bounded_bytes_not_parsed_or_normalized(self):
        for body in (
            None,
            self.body.decode(),
            {},
            bytearray(self.body),
            b"",
            b"a" * (MAX_BODY_BYTES + 1),
        ):
            self.assertEqual(self.verify(raw_body=body).status, SignatureStatus.MALFORMED)

    def test_disabled_and_missing_configuration_never_accept_valid_signature(self):
        self.assertEqual(self.verify(enabled=False).status, SignatureStatus.DISABLED)
        self.assertEqual(self.verify(enabled="true").status, SignatureStatus.MALFORMED)
        self.assertEqual(
            self.verify(credentials=None).status, SignatureStatus.CONFIGURATION_REQUIRED
        )
        self.assertEqual(
            verify_stream_signature(
                self.body, self.signature, self.credentials.api_key, self.credentials
            ).status,
            SignatureStatus.DISABLED,
        )

    def test_unsupported_encoding_is_not_silently_decompressed(self):
        for encoding in ("gzip", "br", "identity,gzip", None):
            self.assertEqual(
                self.verify(content_encoding=encoding).status, SignatureStatus.UNSUPPORTED_ENCODING
            )

    def test_rotated_configuration_does_not_accept_retired_secret(self):
        current = replace(self.credentials, secret=b"SYNTHETIC-REPLACEMENT")
        self.assertEqual(
            self.verify(credentials=current).status, SignatureStatus.AUTHENTICATION_FAILED
        )
        current_signature = hmac.new(current.secret, self.body, hashlib.sha256).hexdigest()
        self.assertEqual(
            self.verify(credentials=current, signature=current_signature).status,
            SignatureStatus.AUTHENTICATED,
        )

    def test_replay_is_authenticated_but_cannot_reach_domain_admission(self):
        for _ in range(2):
            result = self.verify()
            self.assertEqual(result.status, SignatureStatus.AUTHENTICATED)
            with self.assertRaisesRegex(WebhookAdmissionUnavailable, "^durable_inbox_unavailable$"):
                require_durable_webhook_admission(result)
        with self.assertRaisesRegex(WebhookAdmissionUnavailable, "^unverified_event$"):
            require_durable_webhook_admission(self.verify(signature="0" * 64))

    def test_caller_constructed_proof_cannot_bypass_admission(self):
        with self.assertRaises(WebhookAdmissionUnavailable):
            require_durable_webhook_admission(StreamSignatureResult(SignatureStatus.AUTHENTICATED))
        with self.assertRaises(WebhookAdmissionUnavailable):
            require_durable_webhook_admission(True)
        with self.assertRaises(TypeError):
            StreamSignatureResult("authenticated")

    def test_credentials_errors_and_results_exclude_private_values(self):
        results = (self.verify(), self.verify(signature="0" * 64), self.verify(enabled=False))
        rendered = repr((self.credentials, results))
        for sentinel in ("PRIVATE-SENTINEL", "SYNTHETIC-SECRET-SENTINEL", self.signature):
            self.assertNotIn(sentinel, rendered)
        invalid = (
            {"api_key": "PRIVATE-SENTINEL\n"},
            {"secret": b""},
            {"secret": "SYNTHETIC-SECRET-SENTINEL"},
            {"secret": b"a" * (MAX_SECRET_BYTES + 1)},
        )
        for changes in invalid:
            with self.assertRaises(ValueError) as raised:
                replace(self.credentials, **changes)
            self.assertNotIn("PRIVATE-SENTINEL", str(raised.exception))
            self.assertNotIn("SYNTHETIC-SECRET-SENTINEL", str(raised.exception))
