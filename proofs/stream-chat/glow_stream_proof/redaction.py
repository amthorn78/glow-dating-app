"""Redaction of secrets and tokens, and token-claim description for evidence.

Evidence may show a token's claims, never the token. Every string the harness
prints or writes passes through :class:`Redactor`, and :func:`find_leaks` is
the final check before anything is written to disk.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
from collections.abc import Iterable, Mapping
from typing import Any

REDACTED_SECRET = "<redacted-secret>"
REDACTED_JWT = "<redacted-jwt>"

# A compact JWS: base64url header starting with '{"' (eyJ), payload, signature.
# The signature part may be empty or a literal such as Stream's "devtoken".
JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{2,}\.[A-Za-z0-9_-]*")
_SENSITIVE_KEYS = frozenset(
    {"authorization", "access_token", "token", "api_secret", "secret", "stream-auth"}
)


class Redactor:
    """Replaces known secrets and anything shaped like a JWT."""

    def __init__(self, secrets: Iterable[str] = ()) -> None:
        # Longest first so a secret that contains another is fully replaced.
        self._secrets = sorted({s for s in secrets if s}, key=len, reverse=True)

    def text(self, value: str) -> str:
        for secret in self._secrets:
            value = value.replace(secret, REDACTED_SECRET)
        return JWT_PATTERN.sub(REDACTED_JWT, value)

    def value(self, obj: Any) -> Any:
        if isinstance(obj, str):
            return self.text(obj)
        if isinstance(obj, Mapping):
            out: dict[str, Any] = {}
            for key, item in obj.items():
                key_text = self.text(str(key))
                if key_text.lower() in _SENSITIVE_KEYS and isinstance(item, str) and item:
                    out[key_text] = REDACTED_JWT if JWT_PATTERN.search(item) else REDACTED_SECRET
                else:
                    out[key_text] = self.value(item)
            return out
        if isinstance(obj, list | tuple):
            return [self.value(item) for item in obj]
        return obj


def find_leaks(text: str, secrets: Iterable[str] = ()) -> list[str]:
    """Reasons ``text`` must not be written: a known secret or a JWT-shaped value."""
    reasons = []
    for secret in secrets:
        if secret and secret in text:
            reasons.append("contains a known secret")
    if JWT_PATTERN.search(text):
        reasons.append("contains a JWT-shaped value")
    return reasons


def _b64url_json(segment: str) -> dict[str, Any]:
    padded = segment + "=" * (-len(segment) % 4)
    decoded = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    if not isinstance(decoded, dict):
        raise ValueError("JWT segment is not a JSON object")
    return decoded


def describe_token(token: str) -> dict[str, Any]:
    """Header algorithm, claims and signature kind of a JWT, without the token.

    Claims are decoded without verification; this is a description for evidence,
    not an authentication decision.
    """
    parts = token.split(".")
    if len(parts) != 3:
        return {"form": "not-a-jwt"}
    try:
        header = _b64url_json(parts[0])
        claims = _b64url_json(parts[1])
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return {"form": "undecodable-jwt"}
    signature = parts[2]
    if signature == "devtoken":
        signature_kind = "literal-devtoken"
    elif not signature:
        signature_kind = "empty"
    else:
        signature_kind = f"present ({len(signature)} chars)"
    return {
        "form": "jwt",
        "alg": header.get("alg"),
        "claims": dict(sorted(claims.items())),
        "signature": signature_kind,
    }


def token_lifetime_seconds(token: str) -> int | None:
    described = describe_token(token)
    claims = described.get("claims")
    if not isinstance(claims, dict):
        return None
    iat, exp = claims.get("iat"), claims.get("exp")
    if isinstance(iat, int) and isinstance(exp, int):
        return exp - iat
    return None
