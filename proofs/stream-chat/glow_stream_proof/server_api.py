"""The harness's server side: Stream's Python server SDK (``getstream``).

All server HTTP traffic goes through one ``httpx.Client`` owned by the SDK
client. A request hook first asks the run's guard, when one is installed,
whether the request may be sent (:mod:`glow_stream_proof.guard`; P06.1-I2a):
a refused request raises :class:`~glow_stream_proof.stops.GuardRefused` and is
neither sent nor counted. The hook then reserves one API call in the usage
ledger before the request is sent, so the guardrail stops a call before it
happens. A response hook checks every error response for a charge signal, so
typed SDK calls (``upsert_users``, ``send_message`` and the rest) stop the run
as raw requests do. Raw requests
(:meth:`ServerApi.raw`) use the same SDK-authenticated client; they exist so
that a positive control can replay exactly the method, path and body a client
sent, and so that JSON ``null`` (which the SDK's typed methods strip) can be
sent when restoring defaults.

Nothing here prints, logs or returns the API secret or a server token.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from getstream import Stream

from .credentials import ServerCredentials
from .redaction import Redactor
from .stops import GuardRefused
from .usage import UsageLedger, charge_signal, is_rate_limit, mentions_billing

# A guard: (method, path, JSON body or None, query parameters) -> why the request is
# refused, or None when it may be sent (glow_stream_proof.guard.refusal).
Guard = Callable[[str, str, Any, Mapping[str, str]], str | None]

BASE_URL = "https://chat.stream-io-api.com/"

# The SDK logs at DEBUG through the "getstream" logger; keep it quiet.
logging.getLogger("getstream").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


@dataclass(frozen=True)
class ApiResult:
    method: str
    path: str
    status: int
    code: int | None
    message: str | None
    body: Any

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


def _parse(response: httpx.Response) -> tuple[Any, int | None, str | None]:
    try:
        body: Any = response.json() if response.content else {}
    except ValueError:
        body = {"unparsed_body_chars": len(response.content)}
    code = None
    message = None
    if response.status_code >= 400 and isinstance(body, dict):
        raw_code = body.get("code")
        code = raw_code if isinstance(raw_code, int) else None
        raw_message = body.get("message")
        message = raw_message if isinstance(raw_message, str) else None
    return body, code, message


def _json_body(request: httpx.Request) -> Any:
    """The request's JSON body, or ``None`` (no body, a multipart upload, not JSON)."""
    if request.headers.get("content-type", "").startswith("multipart/"):
        return None
    try:
        content = request.content
    except httpx.RequestNotRead:
        return None
    if not content:
        return None
    try:
        return json.loads(content)
    except ValueError:
        return None


def _rate_limit_reset(response: httpx.Response) -> str:
    """The reset a rate-limited answer gives, for the stop's message (P06.1-I2a)."""
    reset = response.headers.get("x-ratelimit-reset")
    return f" (x-ratelimit-reset {reset})" if reset else ""


class ServerApi:
    def __init__(
        self,
        credentials: ServerCredentials,
        ledger: UsageLedger,
        redactor: Redactor,
        *,
        base_url: str = BASE_URL,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._credentials = credentials
        self._ledger = ledger
        self._redactor = redactor
        # Installed by a run or by cleanup --apply (P06.1-I2a); None sends everything.
        self.guard: Guard | None = None
        self._http = httpx.Client(
            timeout=30.0,
            event_hooks={"request": [self._before_request], "response": [self._after_response]},
            transport=transport,
        )
        self.sdk: Any = Stream(
            api_key=credentials.api_key,
            api_secret=credentials.secret(),
            base_url=base_url,
            http_client=self._http,
        )

    def _before_request(self, request: httpx.Request) -> None:
        if self.guard is not None:
            # Before anything is counted or sent (DM-04 finding 1).
            refused = self.guard(
                request.method, request.url.path, _json_body(request), dict(request.url.params)
            )
            if refused is not None:
                raise GuardRefused(refused)
        self._ledger.reserve("api_calls", source="server")

    def _after_response(self, response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        response.read()
        _, code, message = _parse(response)
        signal = charge_signal(
            response.status_code, code, None if message is None else self._redactor.text(message)
        )
        if signal is not None:
            method, path = response.request.method, response.request.url.path
            raise self._ledger.stop_at_once(
                f"server {method} {path}: {signal}{_rate_limit_reset(response)}; stopping at once",
                rate_limited=is_rate_limit(response.status_code, code),
                billing=mentions_billing(message),
            )

    def close(self) -> None:
        self._http.close()

    # -- requests -------------------------------------------------------------

    def raw(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        params: dict[str, str] | None = None,
    ) -> ApiResult:
        """Send one request with server authentication and return it redacted.

        ``path`` is relative to the chat API base URL (for example
        ``/channels/glow-match/x/query`` or ``/api/v2/app``).
        """
        content = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"} if content is not None else {}
        response = self._http.request(
            method, path.lstrip("/"), content=content, params=params, headers=headers
        )
        return self._result(method, path, response)

    def _result(self, method: str, path: str, response: httpx.Response) -> ApiResult:
        parsed, code, message = _parse(response)
        result = ApiResult(
            method=method,
            path=path,
            status=response.status_code,
            code=code,
            message=None if message is None else self._redactor.text(message),
            body=self._redactor.value(parsed),
        )
        signal = charge_signal(result.status, result.code, result.message)
        if signal is not None:
            raise self._ledger.stop_at_once(
                f"server {method} {path}: {signal}{_rate_limit_reset(response)}; stopping at once",
                rate_limited=is_rate_limit(result.status, result.code),
                billing=mentions_billing(result.message),
            )
        return result

    def raw_multipart(
        self,
        path: str,
        *,
        fields: dict[str, str],
        file_name: str,
        content: bytes,
        mime: str,
    ) -> ApiResult:
        """A multipart upload with server authentication (same form as the client's)."""
        response = self._http.request(
            "POST", path.lstrip("/"), data=fields, files={"file": (file_name, content, mime)}
        )
        return self._result("POST", path, response)

    def create_guest(self, user: dict[str, Any]) -> tuple[ApiResult, str | None]:
        """Server-side guest creation. The access token is returned separately and is
        never part of the (redacted) result."""
        path = "/guest"
        content = json.dumps({"user": user}).encode("utf-8")
        response = self._http.request(
            "POST", path.lstrip("/"), content=content, headers={"Content-Type": "application/json"}
        )
        token = None
        if response.status_code < 300:
            try:
                body = response.json()
            except ValueError:
                body = {}
            candidate = body.get("access_token") if isinstance(body, dict) else None
            token = candidate if isinstance(candidate, str) else None
        return self._result("POST", path, response), token

    def get(self, path: str, params: dict[str, str] | None = None) -> ApiResult:
        return self.raw("GET", path, params=params)

    def require(self, result: ApiResult) -> ApiResult:
        if not result.ok:
            raise RuntimeError(
                f"server {result.method} {result.path} failed: HTTP {result.status} "
                f"code {result.code}: {result.message}"
            )
        return result

    # -- tokens ---------------------------------------------------------------

    def user_token(self, user_id: str, ttl_seconds: int) -> str:
        """A user token from the SDK: ``user_id``, ``iat`` and ``exp`` claims."""
        token = self.sdk.create_token(user_id, expiration=ttl_seconds)
        if not isinstance(token, str):
            raise TypeError("SDK returned a non-string token")
        return token

    def expired_user_token(self, user_id: str, expired_seconds_ago: int = 600) -> str:
        """A correctly signed token whose ``exp`` is already in the past."""
        now = int(time.time())
        claims = {
            "user_id": user_id,
            "iat": now - expired_seconds_ago - 300,
            "exp": now - expired_seconds_ago,
        }
        return jwt.encode(claims, self._credentials.secret(), algorithm="HS256")

    @staticmethod
    def wrong_secret_token(user_id: str, wrong_secret: str, ttl_seconds: int) -> str:
        """A well-formed token for ``user_id`` signed with a secret Stream does not know."""
        now = int(time.time())
        claims = {"user_id": user_id, "iat": now - 5, "exp": now + ttl_seconds}
        return jwt.encode(claims, wrong_secret, algorithm="HS256")
