"""Pure Stream Chat authentication; no registered callback or business admission.

The provider signs exact body bytes with HMAC-SHA256, not a timestamp envelope.
Authentication alone cannot establish freshness, ownership or replay safety.
P11 must replace the refusing admission boundary with a durable inbox transaction.
"""

import hashlib
import hmac
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Never

# Application admission limits, not claimed Stream service limits.
MAX_BODY_BYTES = 1_048_576
MAX_API_KEY_BYTES = 256
MAX_SECRET_BYTES = 4096
_HEX_SIGNATURE = re.compile(r"[0-9a-f]{64}")


def _bounded_header(value: object, limit: int) -> bool:
    return (
        isinstance(value, str)
        and 0 < len(value) <= limit
        and all(32 < ord(character) < 127 for character in value)
    )


@dataclass(frozen=True)
class StreamWebhookCredentials:
    """One explicitly selected application key/secret; no retired-key fallback."""

    api_key: str = field(repr=False)
    secret: bytes = field(repr=False)

    def __post_init__(self) -> None:
        if not _bounded_header(self.api_key, MAX_API_KEY_BYTES):
            raise ValueError("Invalid Stream webhook application key configuration.")
        if not isinstance(self.secret, bytes) or not 1 <= len(self.secret) <= MAX_SECRET_BYTES:
            raise ValueError("Invalid Stream webhook secret configuration.")


class SignatureStatus(Enum):
    DISABLED = "disabled"
    CONFIGURATION_REQUIRED = "configuration_required"
    MALFORMED = "malformed"
    UNSUPPORTED_ENCODING = "unsupported_encoding"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHENTICATED = "authenticated"


@dataclass(frozen=True)
class StreamSignatureResult:
    """No private payload, signature, key, event ID or secret is retained."""

    status: SignatureStatus

    def __post_init__(self) -> None:
        if not isinstance(self.status, SignatureStatus):
            raise TypeError("Webhook verification requires a declared status.")


def verify_stream_signature(
    raw_body: bytes,
    signature: str,
    api_key: str,
    credentials: StreamWebhookCredentials | None,
    *,
    enabled: bool = False,
    content_encoding: str = "identity",
) -> StreamSignatureResult:
    """Verify identity-encoded Stream bytes without parsing or executing them.

    `enabled` permits this pure check only; it never activates a callback route.
    Pass Django request.body and exactly one value of X-Signature and X-Api-Key.
    Future HTTP code must reject duplicated headers before calling this function.
    Compressed deliveries are unsupported here, even if a vendor SDK supports them.
    No timestamp or replay protection is claimed; identical bytes can verify twice.
    """
    if type(enabled) is not bool:
        return StreamSignatureResult(SignatureStatus.MALFORMED)
    if not enabled:
        return StreamSignatureResult(SignatureStatus.DISABLED)
    if not isinstance(credentials, StreamWebhookCredentials):
        return StreamSignatureResult(SignatureStatus.CONFIGURATION_REQUIRED)
    if (
        not isinstance(raw_body, bytes)
        or not 1 <= len(raw_body) <= MAX_BODY_BYTES
        or not _bounded_header(signature, 64)
        or _HEX_SIGNATURE.fullmatch(signature) is None
        or not _bounded_header(api_key, MAX_API_KEY_BYTES)
    ):
        return StreamSignatureResult(SignatureStatus.MALFORMED)
    if content_encoding != "identity":
        return StreamSignatureResult(SignatureStatus.UNSUPPORTED_ENCODING)
    if not hmac.compare_digest(credentials.api_key, api_key):
        return StreamSignatureResult(SignatureStatus.AUTHENTICATION_FAILED)
    expected = hmac.new(credentials.secret, raw_body, hashlib.sha256).hexdigest()
    status = (
        SignatureStatus.AUTHENTICATED
        if hmac.compare_digest(expected, signature)
        else SignatureStatus.AUTHENTICATION_FAILED
    )
    return StreamSignatureResult(status)


class WebhookAdmissionUnavailable(RuntimeError):
    """Fixed error codes only; never retain submitted/provider text."""


def require_durable_webhook_admission(result: StreamSignatureResult) -> Never:
    """Fail closed for both verified and unverified input until P11 admission.

    The future boundary must atomically persist a verified, schema/identity-bound
    event with replay/order controls before any domain side effect. A caller-made
    result, valid signature or delivery-ID header cannot grant that permission.
    """
    if not isinstance(result, StreamSignatureResult) or (
        result.status is not SignatureStatus.AUTHENTICATED
    ):
        raise WebhookAdmissionUnavailable("unverified_event")
    raise WebhookAdmissionUnavailable("durable_inbox_unavailable")
