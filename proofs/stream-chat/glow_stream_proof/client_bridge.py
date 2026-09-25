"""Client sessions: one Node process per client, started without the secret.

The environment of a client process is built from an explicit allowlist
(``PATH``, ``HOME``, ``LANG``, the proxy and CA variables) plus the client-safe
API key and that session's own user token. :func:`client_environment` refuses
to produce an environment that holds ``STREAM_API_SECRET`` or the secret's
value, and the runner itself refuses to start if the name is present.
"""

from __future__ import annotations

import json
import selectors
import subprocess
import threading
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .redaction import Redactor
from .usage import GuardrailStop, UsageLedger, charge_signal
from .workdir import PROOF_ROOT

RUNNER = PROOF_ROOT / "client" / "runner.cjs"
PASSTHROUGH = ("PATH", "HOME", "LANG", "HTTPS_PROXY", "https_proxy", "NODE_EXTRA_CA_CERTS")
CONNECT_OPS = frozenset({"connect", "guest", "anonymous"})


class UnsafeClientEnvironment(RuntimeError):
    """A client environment would have carried the server secret."""


def client_environment(
    parent: Mapping[str, str],
    *,
    api_key: str,
    user_token: str | None,
    max_api_calls: int,
    secret: str,
) -> dict[str, str]:
    env = {name: parent[name] for name in PASSTHROUGH if name in parent}
    env["PROOF_API_KEY"] = api_key
    if user_token is not None:
        env["PROOF_USER_TOKEN"] = user_token
    env["PROOF_MAX_API_CALLS"] = str(max_api_calls)
    if "STREAM_API_SECRET" in env or (secret and any(secret in v for v in env.values())):
        raise UnsafeClientEnvironment("client environment would carry the API secret")
    return env


@dataclass
class Reply:
    ok: bool
    data: Any
    error: dict[str, Any] | None
    requests: list[dict[str, Any]] = field(default_factory=list)
    api_calls: int = 0
    ws_attempts: int = 0
    async_errors: list[str] = field(default_factory=list)

    @property
    def status(self) -> int | None:
        if self.error and isinstance(self.error.get("status"), int):
            return int(self.error["status"])
        if self.requests and isinstance(self.requests[-1].get("status"), int):
            return int(self.requests[-1]["status"])
        return None

    @property
    def code(self) -> int | None:
        if self.error and isinstance(self.error.get("code"), int):
            return int(self.error["code"])
        return None

    @property
    def message(self) -> str | None:
        if self.error and isinstance(self.error.get("message"), str):
            return str(self.error["message"])
        return None

    @property
    def last_request(self) -> dict[str, Any] | None:
        return self.requests[-1] if self.requests else None


class ClientSession:
    """A running client process and the commands sent to it."""

    def __init__(
        self,
        label: str,
        env: dict[str, str],
        ledger: UsageLedger,
        redactor: Redactor,
        *,
        node: str = "node",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.label = label
        self._ledger = ledger
        self._redactor = redactor
        self._timeout = timeout_seconds
        self._next_id = 0
        self._connected = False
        self._stderr: deque[str] = deque(maxlen=50)
        self._proc = subprocess.Popen(
            [node, str(RUNNER)],
            env=env,
            cwd=str(PROOF_ROOT),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr_thread.start()

    def _drain_stderr(self) -> None:
        assert self._proc.stderr is not None
        for line in self._proc.stderr:
            self._stderr.append(self._redactor.text(line.rstrip()))

    def stderr_tail(self) -> list[str]:
        return list(self._stderr)

    def _read_line(self) -> str:
        assert self._proc.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(self._proc.stdout, selectors.EVENT_READ)
        try:
            if not selector.select(self._timeout):
                raise TimeoutError(f"client {self.label}: no reply within {self._timeout}s")
        finally:
            selector.close()
        line = self._proc.stdout.readline()
        if not line:
            raise RuntimeError(
                f"client {self.label} exited; stderr: {' | '.join(self.stderr_tail())}"
            )
        return str(line)

    def send(self, op: str, *, max_calls: int = 10, **params: Any) -> Reply:
        if self._ledger.remaining("api_calls") < max_calls:
            raise GuardrailStop("guardrail: api_calls would be passed; stopping before the call")
        opens_connection = op in CONNECT_OPS
        if opens_connection:
            self._ledger.connection_opened()
        self._next_id += 1
        command = {"id": self._next_id, "op": op, "max_calls": max_calls, **params}
        assert self._proc.stdin is not None
        self._proc.stdin.write(json.dumps(command) + "\n")
        self._proc.stdin.flush()
        raw = json.loads(self._read_line())
        reply = Reply(
            ok=bool(raw.get("ok")),
            data=self._redactor.value(raw.get("data")),
            error=self._redactor.value(raw.get("error")),
            requests=self._redactor.value(raw.get("requests") or []),
            api_calls=int(raw.get("api_calls") or 0),
            ws_attempts=int(raw.get("ws_attempts") or 0),
            async_errors=[self._redactor.text(str(e)) for e in raw.get("async_errors") or []],
        )
        if reply.api_calls:
            self._ledger.reserve("api_calls", reply.api_calls, source="client")
        if opens_connection:
            if reply.ok:
                self._connected = True
            else:
                self._ledger.connection_closed()
        if op == "disconnect" and reply.ok and self._connected:
            self._connected = False
            self._ledger.connection_closed()
        for record in reply.requests:
            status = record.get("status")
            response = record.get("response")
            code = response.get("code") if isinstance(response, dict) else None
            message = response.get("message") if isinstance(response, dict) else None
            if isinstance(status, int) and status >= 400:
                signal = charge_signal(status, code if isinstance(code, int) else None, message)
                if signal is not None:
                    raise GuardrailStop(f"client {self.label}: {signal}; stopping at once")
        if reply.error is not None:
            signal = charge_signal(reply.status, reply.code, reply.message)
            if signal is not None and reply.error.get("kind") != "budget":
                raise GuardrailStop(f"client {self.label}: {signal}; stopping at once")
        return reply

    def close(self) -> None:
        if self._proc.poll() is None:
            try:
                assert self._proc.stdin is not None
                self._proc.stdin.write(json.dumps({"id": 0, "op": "exit"}) + "\n")
                self._proc.stdin.flush()
                self._proc.wait(timeout=15)
            except (OSError, subprocess.TimeoutExpired):
                self._proc.kill()
                self._proc.wait(timeout=5)
        if self._connected:
            self._connected = False
            self._ledger.connection_closed()
