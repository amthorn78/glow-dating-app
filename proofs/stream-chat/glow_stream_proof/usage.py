"""Usage counting and the P06.1 budget guardrails.

The brief sets guardrails per session: at most 20 synthetic users, 30 channels,
10 concurrent connections and 5,000 API calls. The harness reserves before it
acts, so a guardrail stops the run before it is passed. Counts are kept for the
current run and, through an ignored ledger file, for every run of the session.

A response that suggests a charge, an upgrade or an exceeded limit also stops
the run at once (:func:`charge_signal`).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .workdir import _replace

KINDS = ("users", "channels", "api_calls")


@dataclass(frozen=True)
class Limits:
    users: int = 20
    channels: int = 30
    connections: int = 10
    api_calls: int = 5000


GUARDRAILS = Limits()


class GuardrailStop(RuntimeError):
    """A guardrail would be passed, or a response suggested a charge or a limit.

    ``at_once`` is true when a response suggested a charge, an upgrade or an
    exceeded limit (:func:`charge_signal`: HTTP 402 or 429, Stream code 9 or
    99, or charge wording). Such a signal stops the run at once, wherever it is
    met, and the run then deletes none of its data (P06.1-C3). A budget
    guardrail is not such a signal.

    ``rate_limited`` is true only when the response was a rate limit (HTTP 429
    or Stream code 9; :func:`is_rate_limit`). Only then is a restore at the end
    of the run tried again after a pause. A rate limit also stops the run at once.
    """

    def __init__(self, message: str, *, rate_limited: bool = False, at_once: bool = False) -> None:
        super().__init__(message)
        self.rate_limited = rate_limited
        self.at_once = at_once or rate_limited


@dataclass
class Counts:
    users: int = 0
    channels: int = 0
    api_calls: int = 0
    server_api_calls: int = 0
    client_api_calls: int = 0
    peak_connections: int = 0
    connection_attempts: int = 0


@dataclass
class UsageLedger:
    limits: Limits = GUARDRAILS
    run: Counts = field(default_factory=Counts)
    session: Counts = field(default_factory=Counts)
    open_connections: int = 0
    path: Path | None = None
    # Every charge or limit signal met, recorded as its stop is raised
    # (:meth:`stop_at_once`). Kept in memory only (P06.1-C3).
    signals: list[GuardrailStop] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | None, limits: Limits = GUARDRAILS) -> UsageLedger:
        ledger = cls(limits=limits, path=path)
        if path is not None and path.exists():
            stored = json.loads(path.read_text(encoding="utf-8"))
            ledger.session = Counts(**stored.get("session", {}))
        return ledger

    def save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Through a temporary file, as every .work file is written, so an interrupted
        # save never leaves the ledger truncated (P06.1-C3).
        _replace(self.path, json.dumps({"session": asdict(self.session)}, indent=2) + "\n")

    def stop_at_once(self, message: str, *, rate_limited: bool) -> GuardrailStop:
        """Record a charge or limit signal where it is met, and return its stop to raise.

        The server client and every client session of a run share this ledger, so
        the signal stays recorded even if its stop is replaced in flight (for
        example by a Ctrl-C while a client session closes), and the end of the run
        still sees it (P06.1-C3).
        """
        stop = GuardrailStop(message, rate_limited=rate_limited, at_once=True)
        self.signals.append(stop)
        return stop

    def _check(self, kind: str, amount: int) -> None:
        limit = getattr(self.limits, kind)
        for scope, counts in (("run", self.run), ("session", self.session)):
            used = getattr(counts, kind)
            if used + amount > limit:
                raise GuardrailStop(
                    f"guardrail: {kind} would reach {used + amount} in this {scope} "
                    f"(limit {limit}); stopping before it is passed"
                )

    def reserve(self, kind: str, amount: int = 1, *, source: str = "server") -> None:
        if kind not in KINDS:
            raise ValueError(f"unknown usage kind {kind!r}")
        self._check(kind, amount)
        for counts in (self.run, self.session):
            setattr(counts, kind, getattr(counts, kind) + amount)
            if kind == "api_calls":
                attr = "server_api_calls" if source == "server" else "client_api_calls"
                setattr(counts, attr, getattr(counts, attr) + amount)
        self.save()

    def release(self, kind: str, amount: int = 1) -> None:
        """Return a reservation that was not used (for example, a refused creation)."""
        if kind not in KINDS:
            raise ValueError(f"unknown usage kind {kind!r}")
        for counts in (self.run, self.session):
            setattr(counts, kind, max(0, getattr(counts, kind) - amount))
        self.save()

    def remaining(self, kind: str) -> int:
        limit: int = getattr(self.limits, kind)
        return limit - max(int(getattr(self.run, kind)), int(getattr(self.session, kind)))

    def connection_opened(self) -> None:
        if self.open_connections + 1 > self.limits.connections:
            raise GuardrailStop(
                f"guardrail: concurrent connections would reach {self.open_connections + 1} "
                f"(limit {self.limits.connections})"
            )
        self.open_connections += 1
        for counts in (self.run, self.session):
            counts.connection_attempts += 1
            counts.peak_connections = max(counts.peak_connections, self.open_connections)
        self.save()

    def connection_closed(self) -> None:
        self.open_connections = max(0, self.open_connections - 1)

    def summary(self) -> dict[str, Any]:
        return {
            "limits": asdict(self.limits),
            "run": asdict(self.run),
            "session": asdict(self.session),
        }


_CHARGE_WORDS = re.compile(
    r"upgrade|billing|payment|overage|charge|quota|plan limit|limit exceeded|exceeded",
    re.IGNORECASE,
)
# Stream codes: 9 rate limit, 99 application suspended.
_CHARGE_CODES = frozenset({9, 99})
_CHARGE_STATUSES = frozenset({402, 429})


def is_rate_limit(status: int | None, code: int | None) -> bool:
    """HTTP 429 or Stream code 9, unless the status is 402 or the code 99.

    The response's wording is not consulted: a rate limit's own message may say
    "exceeded", which the charge-signal wording also matches.
    """
    return (status == 429 or code == 9) and status != 402 and code != 99


def charge_signal(status: int | None, code: int | None, message: str | None) -> str | None:
    """Why a response suggests a charge, an upgrade or an exceeded limit, if it does."""
    if status in _CHARGE_STATUSES:
        return f"HTTP {status}"
    if code in _CHARGE_CODES:
        return f"Stream error code {code}"
    if message and _CHARGE_WORDS.search(message):
        return "response text mentions a charge, upgrade or exceeded limit"
    return None
