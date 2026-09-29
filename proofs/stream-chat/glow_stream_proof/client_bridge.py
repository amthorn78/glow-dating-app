"""Client sessions: one Node process per client, started without the secret.

The environment of a client process is built from an explicit allowlist
(``PATH``, ``HOME``, ``LANG``, the proxy and CA variables) plus the client-safe
API key and that session's own user token. :func:`client_environment` refuses
to produce an environment that holds ``STREAM_API_SECRET`` or the secret's
value, and the runner itself refuses to start if the name is present.

Every reply must carry its command's ``id``. A reply that does not match, a
reply that is not JSON, a timeout or an exited runner ends the session: the
process is killed and every later command on it raises
:class:`ClientSessionEnded` without being sent, so no case is judged on another
command's reply.

Every request the client sends is checked for a charge or limit signal: the
command's own, a request the SDK sent between commands (the runner reports it
in the next reply, or in its exit reply when the session closes), and every
asynchronous SDK error (P06.1-I2a). A signal is recorded in the run's ledger as
its stop is raised (:meth:`UsageLedger.stop_at_once`). One found as the session
closes is recorded, and raised only when no other exception is in flight.
"""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .redaction import Redactor
from .usage import GuardrailStop, UsageLedger, charge_signal, is_rate_limit, mentions_billing
from .workdir import PROOF_ROOT

RUNNER = PROOF_ROOT / "client" / "runner.cjs"
PASSTHROUGH = ("PATH", "HOME", "LANG", "HTTPS_PROXY", "https_proxy", "NODE_EXTRA_CA_CERTS")
CONNECT_OPS = frozenset({"connect", "guest", "anonymous"})


class UnsafeClientEnvironment(RuntimeError):
    """A client environment would have carried the server secret."""


class ClientSessionEnded(RuntimeError):
    """The session was ended (timeout, mismatched reply or exit); nothing more is judged on it."""


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


def _async_text(error: Any) -> str:
    """An asynchronous error's text (the runner sends a structured entry since P06.1-I2a)."""
    if isinstance(error, Mapping):
        return str(error.get("text"))
    return str(error)


def record_signal(record: Mapping[str, Any]) -> tuple[str, bool, bool] | None:
    """A charge or limit signal in Stream's answer to one recorded request, whether it
    was a rate limit, and whether its wording mentions billing; ``None`` if none."""
    status = record.get("status")
    response = record.get("response")
    code = response.get("code") if isinstance(response, dict) else None
    message = response.get("message") if isinstance(response, dict) else None
    if not isinstance(status, int) or status < 400:
        return None
    stream_code = code if isinstance(code, int) else None
    text = message if isinstance(message, str) else None
    signal = charge_signal(status, stream_code, text)
    if signal is None:
        return None
    return signal, is_rate_limit(status, stream_code), mentions_billing(text)


def async_signal(error: Mapping[str, Any]) -> tuple[str, bool, bool] | None:
    """A charge or limit signal in an asynchronous SDK error, as for the command's own
    error: its status, Stream code and wording, except a request the runner refused
    before sending it (P06.1-I2a)."""
    if error.get("kind") == "budget":
        return None
    status = error.get("status") if isinstance(error.get("status"), int) else None
    code = error.get("code") if isinstance(error.get("code"), int) else None
    message = error.get("message") if isinstance(error.get("message"), str) else None
    text = message or str(error.get("text") or "")
    signal = charge_signal(status, code, text)
    if signal is None:
        return None
    return signal, is_rate_limit(status, code), mentions_billing(text)


@dataclass
class Reply:
    ok: bool
    data: Any
    error: dict[str, Any] | None
    requests: list[dict[str, Any]] = field(default_factory=list)
    api_calls: int = 0
    ws_attempts: int = 0
    async_errors: list[str] = field(default_factory=list)
    # Requests the SDK sent between commands, and a command's requests answered only
    # after it replied, reported once answered (P06.1-I2a).
    background_requests: list[dict[str, Any]] = field(default_factory=list)

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
        argv: Sequence[str] | None = None,
        note: Callable[[str], None] | None = None,
    ) -> None:
        self.label = label
        self._ledger = ledger
        self._redactor = redactor
        self._timeout = timeout_seconds
        # Where what the exit reply shows is noted (P06.1-I2a).
        self._note = note
        self._next_id = 0
        self._connected = False
        self._ended: str | None = None
        self._stderr: deque[str] = deque(maxlen=50)
        # Every stdout line is queued by a reader thread as it arrives, so a line
        # already buffered is never missed and never waits for new pipe data.
        self._lines: queue.Queue[str | None] = queue.Queue()
        self._proc = subprocess.Popen(
            list(argv) if argv is not None else [node, str(RUNNER)],
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
        self._stdout_thread = threading.Thread(target=self._drain_stdout, daemon=True)
        self._stdout_thread.start()

    def _drain_stderr(self) -> None:
        assert self._proc.stderr is not None
        for line in self._proc.stderr:
            self._stderr.append(self._redactor.text(line.rstrip()))

    def _drain_stdout(self) -> None:
        assert self._proc.stdout is not None
        for line in self._proc.stdout:
            self._lines.put(line)
        self._lines.put(None)

    def stderr_tail(self) -> list[str]:
        return list(self._stderr)

    @property
    def ended(self) -> str | None:
        """Why the session was ended, or ``None`` while it is usable."""
        return self._ended

    def _end(self, reason: str) -> ClientSessionEnded:
        self._ended = reason
        if self._proc.poll() is None:
            self._proc.kill()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        self._close_pipes()
        if self._connected:
            self._connected = False
            self._ledger.connection_closed()
        return ClientSessionEnded(f"client {self.label} ended: {reason}")

    def _close_pipes(self) -> None:
        for pipe in (self._proc.stdin,):
            try:
                if pipe is not None:
                    pipe.close()
            except OSError:
                pass
        for thread in (self._stdout_thread, self._stderr_thread):
            thread.join(timeout=5)
        for pipe in (self._proc.stdout, self._proc.stderr):
            if pipe is not None:
                pipe.close()

    def _read_line(self) -> str:
        try:
            line = self._lines.get(timeout=self._timeout)
        except queue.Empty:
            raise TimeoutError(f"no reply within {self._timeout}s") from None
        if line is None:
            raise EOFError(f"the runner exited; stderr: {' | '.join(self.stderr_tail())}")
        return line

    def _reply_for(self, command_id: int) -> dict[str, Any]:
        try:
            line = self._read_line()
        except (TimeoutError, EOFError) as exc:
            raise self._end(self._redactor.text(str(exc))) from None
        try:
            raw = json.loads(line)
        except ValueError:
            raise self._end("the reply was not JSON") from None
        reply_id = raw.get("id") if isinstance(raw, dict) else None
        if reply_id != command_id:
            raise self._end(f"reply id {reply_id!r} does not match command id {command_id}")
        return dict(raw)

    def send(self, op: str, *, max_calls: int = 10, **params: Any) -> Reply:
        if self._ended is not None:
            raise ClientSessionEnded(
                f"client {self.label} was ended earlier ({self._ended}); {op} not sent"
            )
        if self._ledger.remaining("api_calls") < max_calls:
            raise GuardrailStop("guardrail: api_calls would be passed; stopping before the call")
        opens_connection = op in CONNECT_OPS
        if opens_connection:
            self._ledger.connection_opened()
        self._next_id += 1
        # A channel's ID travels as ``channel_id``, and the command's own ID, which the
        # runner echoes in its reply, is set last, so no parameter can overwrite it
        # (P06.1-I2a: at its first live use, C1's reply matching ended the session at
        # the first channel command, whose ``id`` had replaced the command's).
        fields = dict(params)
        if "id" in fields:
            fields["channel_id"] = fields.pop("id")
        command = {**fields, "id": self._next_id, "op": op, "max_calls": max_calls}
        try:
            assert self._proc.stdin is not None
            self._proc.stdin.write(json.dumps(command) + "\n")
            self._proc.stdin.flush()
            raw = self._reply_for(self._next_id)
        except (ClientSessionEnded, OSError) as exc:
            if opens_connection:
                self._ledger.connection_closed()  # the connect never answered
            if isinstance(exc, OSError):
                raise self._end(f"could not send the command: {exc}") from None
            raise
        raw_async = raw.get("async_errors") or []
        reply = Reply(
            ok=bool(raw.get("ok")),
            data=self._redactor.value(raw.get("data")),
            error=self._redactor.value(raw.get("error")),
            requests=self._redactor.value(raw.get("requests") or []),
            api_calls=int(raw.get("api_calls") or 0),
            ws_attempts=int(raw.get("ws_attempts") or 0),
            async_errors=[self._redactor.text(_async_text(e)) for e in raw_async],
            background_requests=self._redactor.value(raw.get("background_requests") or []),
        )
        background_calls = int(raw.get("background_api_calls") or 0)
        if opens_connection:
            if reply.ok:
                self._connected = True
            else:
                self._ledger.connection_closed()
        if op == "disconnect" and reply.ok and self._connected:
            self._connected = False
            self._ledger.connection_closed()
        # Every charge or limit signal in the reply is recorded before anything raises,
        # and before its calls are counted: a charge must not hide behind a rate limit
        # met first, nor behind the budget (P06.1-I2a; the independent review, point 3).
        stops = self._reply_signals(reply, raw_async)

        def tally(amount: int) -> None:
            if stops:
                # Already sent: counted without a check that could raise over the signal.
                self._ledger.count("api_calls", amount, source="client")
            else:
                self._ledger.reserve("api_calls", amount, source="client")

        if reply.api_calls:
            tally(reply.api_calls)
        if background_calls:
            # Sent by the SDK between commands; counted like any client call (P06.1-I2a).
            tally(background_calls)
        if stops:
            raise stops[0]
        return reply

    def _reply_signals(self, reply: Reply, raw_async: Sequence[Any]) -> list[GuardrailStop]:
        """Record every charge or limit signal in ``reply`` in the run's ledger, in order,
        and return their stops (P06.1-I2a)."""
        stops: list[GuardrailStop] = []
        for record in reply.requests:
            status = record.get("status")
            response = record.get("response")
            code = response.get("code") if isinstance(response, dict) else None
            message = response.get("message") if isinstance(response, dict) else None
            if isinstance(status, int) and status >= 400:
                stream_code = code if isinstance(code, int) else None
                signal = charge_signal(status, stream_code, message)
                if signal is not None:
                    stops.append(
                        self._ledger.stop_at_once(
                            f"client {self.label}: {signal}; stopping at once",
                            rate_limited=is_rate_limit(status, stream_code),
                            billing=mentions_billing(message if isinstance(message, str) else None),
                        )
                    )
        # The command's own error, when none of its recorded requests carried a signal
        # (it usually repeats the answer to one of them).
        if reply.error is not None and not stops:
            signal = charge_signal(reply.status, reply.code, reply.message)
            if signal is not None and reply.error.get("kind") != "budget":
                stops.append(
                    self._ledger.stop_at_once(
                        f"client {self.label}: {signal}; stopping at once",
                        rate_limited=is_rate_limit(reply.status, reply.code),
                        billing=mentions_billing(reply.message),
                    )
                )
        # A request the SDK sent between commands, an answer that came after its
        # command replied, and every asynchronous SDK error (P06.1-I2a).
        stops += self._late_signals(reply.background_requests, self._redactor.value(raw_async))
        return stops

    def _late_signals(
        self, records: Sequence[Mapping[str, Any]], async_errors: Sequence[Any]
    ) -> list[GuardrailStop]:
        """Record every charge or limit signal in ``records`` (requests sent between
        commands, or answered after their command replied) and in ``async_errors``, and
        return their stops (P06.1-I2a; every one since the independent review, point 3)."""
        stops: list[GuardrailStop] = []
        for record in records:
            found = record_signal(record)
            if found is not None:
                where = "a request sent between commands"
                if record.get("late"):
                    where = "a request answered after its command replied"
                stops.append(
                    self._ledger.stop_at_once(
                        f"client {self.label}: {found[0]} ({where}); stopping at once",
                        rate_limited=found[1],
                        billing=found[2],
                    )
                )
        for error in async_errors:
            found = async_signal(error) if isinstance(error, Mapping) else None
            if found is not None:
                stops.append(
                    self._ledger.stop_at_once(
                        f"client {self.label}: {found[0]} (an asynchronous SDK error); "
                        "stopping at once",
                        rate_limited=found[1],
                        billing=found[2],
                    )
                )
        return stops

    def close(self, *, raise_signal: bool = True) -> None:
        """End the session. The runner's exit reply reports what the SDK sent after the
        last command and every asynchronous error still unreported; they are counted,
        noted and checked for a charge or limit signal (P06.1-I2a). A signal is always
        recorded in the run's ledger; its stop is raised only when ``raise_signal`` and
        no other exception is in flight (for example in a ``finally``), so it never
        replaces one. The end of the run closes its sessions with ``raise_signal=False``.
        """
        exited = False
        if self._ended is None and self._proc.poll() is None:
            try:
                assert self._proc.stdin is not None
                self._proc.stdin.write(json.dumps({"id": 0, "op": "exit"}) + "\n")
                self._proc.stdin.flush()
                self._proc.wait(timeout=15)
                exited = True
            except (OSError, subprocess.TimeoutExpired):
                self._proc.kill()
                self._proc.wait(timeout=5)
        if self._ended is None:
            if self._proc.poll() is None:
                self._proc.kill()
                self._proc.wait(timeout=5)
            self._close_pipes()
        if self._connected:
            self._connected = False
            self._ledger.connection_closed()
        stop = self._exit_signal() if exited else None
        if stop is not None and raise_signal and sys.exc_info()[1] is None:
            raise stop

    def _exit_signal(self) -> GuardrailStop | None:
        """What the exit reply reports: counted, noted, and its first signal recorded."""
        exit_reply: dict[str, Any] | None = None
        while True:
            try:
                line = self._lines.get_nowait()
            except queue.Empty:
                break
            if line is None:
                continue
            try:
                raw = json.loads(line)
            except ValueError:
                continue
            if isinstance(raw, dict) and raw.get("id") == 0:
                exit_reply = raw
        if exit_reply is None:
            return None
        calls = int(exit_reply.get("background_api_calls") or 0)
        if calls:
            # Already sent; counted without a check that could raise here.
            self._ledger.count("api_calls", calls, source="client")
        records = self._redactor.value(exit_reply.get("background_requests") or [])
        errors = self._redactor.value(exit_reply.get("async_errors") or [])
        if self._note is not None:
            for record in records:
                status = record.get("status")
                self._note(
                    f"client {self.label} at exit: {record.get('method')} {record.get('path')} "
                    f"-> {status if isinstance(status, int) else 'no response'}"
                )
            for error in errors:
                self._note(f"client {self.label} at exit: async error: {_async_text(error)}")
        stops = self._late_signals(records, errors)
        return stops[0] if stops else None
