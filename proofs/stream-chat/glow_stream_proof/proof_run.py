"""One live proof run against the development application.

Order: preflight (configuration and data checks) -> setup (synthetic users,
tokens, the two match channels, client sessions) -> authorized path ->
bypass matrix -> finish: restore every journalled temporary change, cleanup
(hard delete of this run's users, channels, polls and user groups, then a
check that none remain) and a final configuration check.

Verdicts are taken from Stream's recorded answer to the request under test
(:func:`_http_answer`, :func:`_ws_answer`), never from an error the SDK raised.
Every temporary change is journalled before its enabling request and restored
and verified when its case ends; a restore that fails stops the run.
"""

from __future__ import annotations

import base64
import json
import re
import secrets
import time
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from getstream.models import ChannelInput, ChannelMemberRequest, MessageRequest, UserRequest

from . import baseline, configuration, matrix
from .app_send import AppSendService
from .client_bridge import ClientSession, ClientSessionEnded, Reply, client_environment
from .configuration import MATCH_MEMBER_GRANTS, MATCH_TYPE
from .credentials import ServerCredentials
from .policy import MatchState
from .redaction import Redactor, describe_token, token_lifetime_seconds
from .server_api import ApiResult, ServerApi
from .usage import GuardrailStop, UsageLedger

PREFIX_ROOT = "p061i1-"
TOKEN_TTL_SECONDS = 900
TASK_POLL_ATTEMPTS = 30
TASK_POLL_INTERVAL_SECONDS = 2
# API calls kept back for the end of the run. The worst case, with every delete
# task polled TASK_POLL_ATTEMPTS times, is about 115 server calls: up to 5 poll
# and group deletes, 3 deletes with their task polls (93), 3 user listings, the
# verify-clean reads (7), the journal restores (6) and the final configuration
# read (2). tests/test_finish.py measures it against a fake server.
CLEANUP_RESERVE = 130
# The most one case can use before the next reserve check.
CASE_CALL_MARGIN = 30
EVENT_WAIT_MS = 2500
TYPE_CHANGE_SETTLE_SECONDS = 3
DESTRUCTIVE_PHASE = 70
T = MATCH_TYPE
# Nathan's confirmed dashboard administrator user was created at this minute
# (UTC), as recorded in the P06.1 evidence. Preflight compares only the minute;
# no identifier is read into the record.
DASHBOARD_USER_CREATED_MINUTE = "2026-09-24T13:07"


class RunStopped(RuntimeError):
    """The run stopped on a stop condition; the reason is reported."""


@dataclass
class TemporaryChange:
    """A change the run makes for a few seconds and must undo before going on."""

    description: str
    restore: Callable[[], str]
    note: str = ""


@dataclass(frozen=True)
class Answer:
    """Stream's recorded answer to the request under test."""

    outcome: matrix.Outcome
    status: int | None
    code: int | None
    record: dict[str, Any] | None
    note: str = ""


@dataclass
class CaseResult:
    case_id: str
    group: str
    actor: str
    token: str
    action: str
    expected: str
    request: str
    observed: str
    control: str
    verdict: str
    reason: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    check_id: str
    description: str
    result: str
    evidence: str


def _local_note(reply: Reply) -> str:
    if reply.error is not None:
        return f"{reply.error.get('kind')}: {reply.message}"
    return "the SDK returned without sending a request"


def _answer_of(record: dict[str, Any] | None, reply: Reply) -> Answer:
    """Stream's answer as recorded for ``record``; ``no-response`` if it has none."""
    if record is None:
        return Answer("no-response", None, None, None, _local_note(reply))
    status = record.get("status")
    if not isinstance(status, int):
        return Answer("no-response", None, None, record, _local_note(reply))
    response = record.get("response")
    raw_code = response.get("code") if isinstance(response, dict) else None
    code = raw_code if isinstance(raw_code, int) and status >= 400 else None
    return Answer(matrix.classify(status, code), status, code, record)


def _http_answer(reply: Reply) -> Answer:
    """The request under test is the last HTTP request the command sent.

    Every SDK call in the matrix sends one request. The SDK's own error
    (``reply.error``) is never used: a local throw, or a call that returned
    without a request, has no recorded answer.
    """
    return _answer_of(reply.last_request, reply)


def _ws_answer(reply: Reply) -> Answer:
    """Stream's answer to a WebSocket connect.

    Success is the handshake Stream sent (the SDK resolves with it). A refusal
    counts only when the SDK built the error from Stream's own error frame
    (runner kind ``ws-api``); any other failure has no recorded answer.
    """
    if reply.ok:
        data = reply.data if isinstance(reply.data, dict) else {}
        if data.get("me") or data.get("connection_id_present"):
            return Answer("success", None, None, None)
        return Answer("no-response", None, None, None, "the connect returned without a handshake")
    error = reply.error or {}
    status, code = error.get("status"), error.get("code")
    if error.get("kind") == "ws-api" and isinstance(status, int):
        code = code if isinstance(code, int) else None
        return Answer(matrix.classify(status, code), status, code, None)
    return Answer("no-response", None, None, None, _local_note(reply))


def _observed(answer: Answer) -> str:
    if answer.outcome == "success":
        return f"{answer.status if answer.status is not None else 'ok'} (succeeded)"
    if answer.outcome == "no-response":
        return f"no answer recorded ({answer.note})"
    return f"{answer.status} / code {answer.code}"


def _answer_message(answer: Answer, reply: Reply) -> str | None:
    response = answer.record.get("response") if answer.record else None
    if isinstance(response, dict) and isinstance(response.get("message"), str):
        return str(response["message"])
    return reply.message


def _utc_minute(value: Any) -> str | None:
    """A Stream timestamp (Unix nanoseconds, or ISO 8601) as ``YYYY-MM-DDTHH:MM`` in UTC."""
    if isinstance(value, str) and value.isdigit():
        value = int(value)
    if isinstance(value, int | float) and not isinstance(value, bool):
        # Stream's v2 API sends nanoseconds; milliseconds and seconds are accepted too.
        seconds = value / 1e9 if value > 1e15 else value / 1e3 if value > 1e12 else value
        return datetime.fromtimestamp(float(seconds), UTC).strftime("%Y-%m-%dT%H:%M")
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})[^+-]*(Z|\+00:00)$", value)
            return match.group(1) if match else None
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(UTC).strftime("%Y-%m-%dT%H:%M")
    return None


def override_removal_problems(
    channel: Mapping[str, Any] | None, override: Mapping[str, Any]
) -> tuple[list[str], list[str]]:
    """What a re-read of AB shows after an override was removed.

    Returns the differences, and the overridden keys the re-read cannot show.
    An empty ``config_overrides`` shows every key removed; otherwise the
    channel's effective ``config`` must hold the production value of each key.
    """
    if not isinstance(channel, Mapping):
        return ["AB could not be re-read"], []
    problems: list[str] = []
    unreadable: list[str] = []
    has_overrides = "config_overrides" in channel
    if channel.get("config_overrides"):
        problems.append(f"config_overrides still set: {sorted(channel['config_overrides'])}")
    raw_config = channel.get("config")
    config: Mapping[str, Any] = raw_config if isinstance(raw_config, Mapping) else {}
    for key, value in override.items():
        if key == "grants":
            grants = config.get("grants")
            if isinstance(grants, Mapping):
                for role, added in value.items():
                    production = set(MATCH_MEMBER_GRANTS) if role == "channel_member" else set()
                    extra = (set(added) - production) & set(grants.get(role) or [])
                    if extra:
                        problems.append(f"{role} still has {sorted(extra)}")
            elif not has_overrides:
                unreadable.append(key)
            continue
        want = configuration.MATCH_FEATURES.get(key)
        if key in config:
            if config[key] != want:
                problems.append(f"{key} is {config[key]!r}, want {want!r}")
        elif not has_overrides:
            unreadable.append(key)
    return problems, unreadable


def _request_line(record: Mapping[str, Any] | None, ctx: Mapping[str, str]) -> str:
    if not record:
        return "-"
    path = str(record.get("path") or "")
    return f"{record.get('method')} {_generic(path, ctx)}"


def _generic(text: str, ctx: Mapping[str, str]) -> str:
    """Replace run-specific identifiers with their placeholder names for the table."""
    pairs = sorted(
        ((v, k) for k, v in ctx.items() if v and k in _TABLE_NAMES), key=lambda p: -len(p[0])
    )
    for value, name in pairs:
        text = text.replace(value, "{" + name + "}")
    return text


_TABLE_NAMES = frozenset(
    {"A", "B", "X", "D", "AB", "XD", "m_a", "m_b", "m_x", "m_ctl", "prefix", "guest_id", "ctl_poll"}
)


def _dig(obj: Any, dotted: str) -> Any:
    for part in dotted.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def _responses(reply: Reply) -> list[Any]:
    return [r.get("response") for r in reply.requests]


class ProofRun:
    def __init__(
        self,
        credentials: ServerCredentials,
        api: ServerApi,
        ledger: UsageLedger,
        redactor: Redactor,
        environ: Mapping[str, str],
        *,
        prefix: str,
        accept_dashboard_user: bool,
    ) -> None:
        if not prefix.startswith(PREFIX_ROOT):
            raise ValueError(f"run prefix must start with {PREFIX_ROOT}")
        self.credentials = credentials
        self.api = api
        self.ledger = ledger
        self.redactor = redactor
        self.environ = environ
        self.prefix = prefix
        self.accept_dashboard_user = accept_dashboard_user
        self.ctx: dict[str, str] = {"prefix": prefix, "T": T}
        self.sessions: dict[str, ClientSession] = {}
        self._tokens: dict[str, str] = {}
        self.users: list[str] = []
        self.channels: list[str] = []
        self.polls: list[tuple[str, str]] = []
        self.groups: list[str] = []
        self.case_results: list[CaseResult] = []
        self.checks: list[CheckResult] = []
        self.notes: list[str] = []
        self.token_claims: dict[str, Any] = {}
        self.settings: dict[str, Any] = {}
        self.cleanup_result: dict[str, Any] = {}
        self.state = MatchState()
        self.connect_replies: dict[str, Reply] = {}
        self.control_ok: dict[str, bool] = {}
        self.ws_attempts = 0
        self.started_ns = time.time_ns()
        # Temporary changes not yet restored; each is added before its enabling request.
        self.journal: list[TemporaryChange] = []
        # Every stop condition and restore failure, in order, so none hides another.
        self.stops: list[str] = []
        self._pending_stop: str | None = None
        self.post_run_problems: list[str] = []

    # -- helpers ----------------------------------------------------------------

    def _check(self, check_id: str, description: str, ok: bool | None, evidence: str) -> None:
        result = "PASS" if ok else ("UNVERIFIED" if ok is None else "FAIL")
        text = self.redactor.text(_generic(evidence, self.ctx))
        self.checks.append(CheckResult(check_id, description, result, text))

    def _text(self, exc: BaseException) -> str:
        return self.redactor.text(_generic(str(exc), self.ctx))

    def _session(self, label: str, token: str | None, *, max_api_calls: int = 150) -> ClientSession:
        env = client_environment(
            self.environ,
            api_key=self.credentials.api_key,
            user_token=token,
            max_api_calls=max_api_calls,
            secret=self.credentials.secret(),
        )
        session = ClientSession(label, env, self.ledger, self.redactor)
        self.sessions[label] = session
        return session

    def _send(self, session: ClientSession, op: str, **params: Any) -> Reply:
        reply = session.send(op, **params)
        self.ws_attempts += reply.ws_attempts
        for error in reply.async_errors:
            self.notes.append(f"client {session.label} async error: {_generic(error, self.ctx)}")
        return reply

    def _step(self, step: matrix.SdkStep, session_label: str | None = None) -> Reply:
        session = self.sessions[session_label or step.session]
        params = matrix.substitute(dict(step.params), self.ctx)
        return self._send(session, step.op, max_calls=step.max_calls, **params)

    def _server(self, request: matrix.ServerRequest) -> ApiResult:
        body = matrix.substitute(dict(request.body), self.ctx) if request.body is not None else None
        params = (
            matrix.substitute(dict(request.params), self.ctx)
            if request.params is not None
            else None
        )
        return self.api.raw(
            request.method, matrix.substitute(request.path, self.ctx), body=body, params=params
        )

    def _remaining_ok(self) -> bool:
        return self.ledger.remaining("api_calls") > CLEANUP_RESERVE + CASE_CALL_MARGIN

    # -- temporary changes and undos ----------------------------------------------

    @contextmanager
    def _temporary(self, change: TemporaryChange) -> Iterator[TemporaryChange]:
        """Journal ``change`` before its enabling request; restore and verify it on exit.

        A restore that fails stops the run (:class:`RunStopped`). If an exception
        was already in flight, both are recorded in :attr:`stops`; a guardrail
        stop in flight stays the run's stop.
        """
        self.journal.append(change)
        try:
            yield change
        except BaseException as exc:
            try:
                self._restore(change)
            except BaseException:
                self.stops.append(
                    f"in flight when that restore failed: {type(exc).__name__}: {self._text(exc)}"
                )
                if isinstance(exc, GuardrailStop):
                    raise exc from None
                raise
            raise
        self._restore(change)

    def _restore(self, change: TemporaryChange) -> str:
        try:
            note = change.restore()
        except (RunStopped, GuardrailStop) as exc:
            self.stops.append(f"restore failed: {change.description}: {self._text(exc)}")
            raise
        except Exception as exc:
            message = (
                f"restore failed: {change.description}: {type(exc).__name__}: {self._text(exc)}"
            )
            self.stops.append(message)
            raise RunStopped(message) from exc
        change.note = note
        if change in self.journal:
            self.journal.remove(change)
        return note

    def _defer_stop(self, reason: str) -> None:
        """Stop the run once the current case's row is recorded."""
        reason = self.redactor.text(_generic(reason, self.ctx))
        self.stops.append(reason)
        if self._pending_stop is None:
            self._pending_stop = reason

    def _undo(self, undo: matrix.ServerRequest, case_id: str) -> str:
        """Send one undo request; a failed undo stops the run after this case."""
        done = self._server(undo)
        if not done.ok:
            self._defer_stop(
                f"{case_id}: undo {undo.method} {matrix.substitute(undo.path, self.ctx)} got "
                f"{done.status} code {done.code}: {done.message}"
            )
        return f"undo {undo.method} {done.status}"

    def _channel_override_change(self, override: Mapping[str, Any]) -> TemporaryChange:
        return TemporaryChange(
            f"config_overrides {sorted(override)} on AB",
            lambda: self._remove_channel_override(override),
        )

    def _server_channel(self, cid: str) -> Mapping[str, Any] | None:
        result = self.api.raw(
            "POST", "/api/v2/chat/channels", body={"filter_conditions": {"cid": cid}, "limit": 1}
        )
        channels = result.body.get("channels") if isinstance(result.body, dict) else None
        if not result.ok or not isinstance(channels, list) or not channels:
            return None
        channel = channels[0].get("channel") if isinstance(channels[0], dict) else None
        return channel if isinstance(channel, dict) else None

    def _remove_channel_override(self, override: Mapping[str, Any]) -> str:
        """Remove AB's overrides, then re-read AB and verify the removal."""
        path = f"/channels/{T}/{self.ctx['AB']}"
        off = self.api.raw("PATCH", path, body={"set": {"config_overrides": {}}})
        if not off.ok:
            raise RunStopped(
                f"removing AB's config_overrides got {off.status} code {off.code}: {off.message}"
            )
        problems, unreadable = override_removal_problems(
            self._server_channel(self.ctx["AB_cid"]), override
        )
        checked = "re-read"
        if unreadable == ["grants"] and "read-channel-members" in (
            override.get("grants", {}).get("channel_member") or []
        ):
            # The re-read does not show grants: B's members query must be refused again.
            probe = self._send(
                self.sessions["B"],
                "call",
                target="channel",
                method="queryMembers",
                args=[{}],
                type=T,
                id=self.ctx["AB"],
            )
            answer = _http_answer(probe)
            if answer.outcome != "permission":
                problems.append(f"B's members query afterwards got {_observed(answer)}")
            checked = f"re-read; B's members query refused again ({_observed(answer)})"
        elif unreadable:
            problems.append(f"the re-read of AB does not show {unreadable}")
        if problems:
            raise RunStopped(f"AB's override removal not verified: {'; '.join(problems)}")
        return f"override removed ({off.status}; {checked})"

    def _type_features_change(self, features: Mapping[str, Any]) -> TemporaryChange:
        return TemporaryChange(
            f"{T} features {sorted(features)}", lambda: self._type_features_restore(features)
        )

    def _guest_creation_change(self) -> TemporaryChange:
        return TemporaryChange("guest user creation enabled", self._disable_guest_creation)

    def _disable_guest_creation(self) -> str:
        off = self._set_guest_creation_disabled(True)
        time.sleep(TYPE_CHANGE_SETTLE_SECONDS)
        app = self.api.get("/api/v2/app")
        disabled = _dig(app.body, "app.guest_user_creation_disabled")
        if not off.ok or not app.ok or disabled is not True:
            raise RunStopped(
                f"guest creation could not be disabled again: PATCH {off.status}, "
                f"re-read {app.status}: {disabled!r}"
            )
        return f"disabled again ({off.status}) and verified"

    # -- preflight -------------------------------------------------------------

    def preflight(self) -> dict[str, Any]:
        snapshot = baseline.read_snapshot(self.api)
        problems = configuration.verify(snapshot)
        if problems:
            raise RunStopped("configuration is not in place: " + "; ".join(problems))
        app = snapshot["app"]["app"]
        self.settings = {k: app.get(k) for k in configuration.APP_SETTING_KEYS if k in app}
        foreign_users = []
        dashboard: list[Mapping[str, Any]] = []
        for user in snapshot["users"].get("users", []):
            uid = str(user.get("id"))
            if PREFIX_ROOT in uid:
                foreign_users.append(f"leftover proof user {uid}")
                continue
            custom = user.get("custom") or {}
            if user.get("role") == "admin" and custom.get("dashboard_user") is True:
                dashboard.append(user)
                continue
            foreign_users.append("a user this proof did not create")
        if not self.accept_dashboard_user:
            foreign_users += ["a user this proof did not create"] * len(dashboard)
        elif len(dashboard) != 1:
            # Nathan accepted exactly one dashboard administrator (25 September 2026).
            foreign_users.append(
                f"{len(dashboard)} dashboard administrator users; exactly one is accepted"
            )
        elif _utc_minute(dashboard[0].get("created_at")) != DASHBOARD_USER_CREATED_MINUTE:
            foreign_users.append(
                "a dashboard administrator user whose creation time is not that of the "
                "user Nathan confirmed"
            )
        channels = snapshot["channels"].get("channels", [])
        foreign_channels = [str(c.get("channel", {}).get("cid")) for c in channels]
        if foreign_users or foreign_channels:
            raise RunStopped(
                "application holds data this run did not create: "
                + "; ".join(foreign_users + [f"channel {c}" for c in foreign_channels])
            )
        return {"dashboard_users_present": len(dashboard), "configuration_problems": problems}

    # -- setup -----------------------------------------------------------------

    def setup(self) -> None:
        names = {"A": "ua", "B": "ub", "X": "ux", "D": "ud"}
        for key, suffix in names.items():
            self.ctx[key] = f"{self.prefix}-{suffix}"
            self.ctx[f"{key}_name"] = f"Synthetic {key} {self.prefix[-6:]}"
        self.ctx["AB"] = f"{self.prefix}-ch-ab"
        self.ctx["XD"] = f"{self.prefix}-ch-xd"
        self.ctx["AB_cid"] = f"{T}:{self.ctx['AB']}"
        self.ctx["XD_cid"] = f"{T}:{self.ctx['XD']}"
        self.ctx["m_a_text"] = f"authorized message from A {self.prefix}"
        self.ctx["m_b_text"] = f"authorized message from B {self.prefix}"
        self.ctx["xd_text"] = f"xdmarker{self.prefix.replace('-', '')}"

        self.ledger.reserve("users", 4)
        users = [
            UserRequest(id=self.ctx[k], name=self.ctx[f"{k}_name"], role="user") for k in names
        ]
        self.users.extend(self.ctx[k] for k in names)
        self.api.sdk.upsert_users(*users)
        stored = self.api.require(
            self.api.get(
                "/api/v2/users",
                params={
                    "payload": json.dumps(
                        {"filter_conditions": {"id": {"$in": [self.ctx[k] for k in names]}}}
                    )
                },
            )
        ).body.get("users", [])
        roles = sorted({u.get("role") for u in stored})
        self._check(
            "AP1",
            "server creates four synthetic users with the ordinary user role",
            len(stored) == 4 and roles == ["user"],
            f"{len(stored)} users, roles {roles}",
        )

        for key in names:
            token = self.api.user_token(self.ctx[key], TOKEN_TTL_SECONDS)
            self._tokens[key] = token
            self.token_claims[key] = describe_token(token)
        lifetimes = {k: token_lifetime_seconds(t) for k, t in self._tokens.items()}
        self._check(
            "AP2",
            f"server issues each user a token with user_id, iat and exp "
            f"(lifetime {TOKEN_TTL_SECONDS} s)",
            all(v is not None and v <= TOKEN_TTL_SECONDS + 10 for v in lifetimes.values()),
            f"lifetimes (exp - iat) {lifetimes}",
        )

        self.ledger.reserve("channels", 2)
        for cid_key, owner, other in (("AB", "A", "B"), ("XD", "X", "D")):
            self.channels.append(f"{T}:{self.ctx[cid_key]}")
            self.api.sdk.chat.get_or_create_channel(
                type=T,
                id=self.ctx[cid_key],
                data=ChannelInput(
                    created_by_id=self.ctx[owner],
                    members=[
                        ChannelMemberRequest(user_id=self.ctx[owner]),
                        ChannelMemberRequest(user_id=self.ctx[other]),
                    ],
                ),
            )
            self.state.add_match(self.ctx[owner], self.ctx[other], self.ctx[cid_key])
            members = self._server_members(self.ctx[cid_key])
            want = sorted([self.ctx[owner], self.ctx[other]])
            self._check(
                f"AP3-{cid_key}",
                f"server creates {cid_key} ({T}) with exactly its two members",
                members == want,
                f"members {members}",
            )

        for key in ("A", "B", "X"):
            session = self._session(key, self._tokens[key])
            reply = self._send(session, "connect", max_calls=3, user={"id": self.ctx[key]})
            self.connect_replies[key] = reply
            own = "AB" if key in ("A", "B") else "XD"
            watch = self._send(
                session,
                "call",
                target="channel",
                method="watch",
                args=[],
                type=T,
                id=self.ctx[own],
            )
            connected, watched = _ws_answer(reply), _http_answer(watch)
            self._check(
                f"AP4-{key}",
                f"client {key} connects over Stream's WebSocket and watches its own channel",
                connected.outcome == "success" and watched.outcome == "success",
                f"connect {_observed(connected)}; watch {_observed(watched)}; "
                f"role {(reply.data or {}).get('me', {}).get('role') if reply.ok else '-'}",
            )

    def _server_members(self, channel_id: str) -> list[str]:
        result = self.api.require(
            self.api.get(
                "/api/v2/chat/members",
                params={
                    "payload": json.dumps(
                        {"type": T, "id": channel_id, "filter_conditions": {}, "limit": 10}
                    )
                },
            )
        )
        return sorted(str(m.get("user_id")) for m in result.body.get("members", []))

    # -- authorized path -----------------------------------------------------------

    def send_as(self, channel_type: str, channel_id: str, user_id: str, text: str) -> ApiResult:
        response = self.api.sdk.chat.send_message(
            type=channel_type,
            id=channel_id,
            message=MessageRequest(text=text, user_id=user_id),
        )
        message_id = response.data.message.id
        return ApiResult("POST", "send_message", 201, None, None, {"message": {"id": message_id}})

    def authorized_path(self) -> None:
        service = AppSendService(self.state, self, T)
        for key, text_key, channel in (("A", "m_a", "AB"), ("B", "m_b", "AB"), ("X", "m_x", "XD")):
            text = self.ctx.get(f"{text_key}_text") or self.ctx["xd_text"]
            outcome = service.send(self.ctx[key], self.ctx[channel], text)
            if outcome.message_id:
                self.ctx[text_key] = outcome.message_id
            self._check(
                f"AP5-{key}",
                f"app send path: {key}'s message to {channel} passes the match/block check "
                "and is sent server-side",
                outcome.decision.allowed and outcome.stream_called and bool(outcome.message_id),
                f"decision {outcome.decision.reason}; Stream called {outcome.stream_called}",
            )
        refused_cases: list[tuple[str, str, str, str | None, str | None]] = [
            ("AP6", "A to XD (not a participant)", "A", "XD", None),
            ("AP7", "A to an unmatched pair's channel id", "A", None, f"{self.prefix}-ch-ax"),
        ]
        for check_id, desc, sender_key, target_key, raw_target in refused_cases:
            before = self.ledger.run.api_calls
            outcome = service.send(
                self.ctx[sender_key],
                raw_target or self.ctx[str(target_key)],
                "should never be sent",
            )
            after = self.ledger.run.api_calls
            self._check(
                check_id,
                f"app send path refuses {desc} without calling Stream",
                (not outcome.decision.allowed) and not outcome.stream_called and before == after,
                f"decision {outcome.decision.reason}; Stream called {outcome.stream_called}; "
                f"API calls before {before}, after {after}",
            )
        blocked_state = MatchState()
        blocked_state.add_match(self.ctx["A"], self.ctx["B"], self.ctx["AB"])
        blocked_state.block(self.ctx["B"], self.ctx["A"])
        before = self.ledger.run.api_calls
        outcome = AppSendService(blocked_state, self, T).send(self.ctx["A"], self.ctx["AB"], "x")
        after = self.ledger.run.api_calls
        self._check(
            "AP8",
            "app send path refuses a send after a block (fixture state) without calling Stream",
            (not outcome.decision.allowed) and not outcome.stream_called and before == after,
            f"decision {outcome.decision.reason}; API calls before {before}, after {after}",
        )
        for key, want_key in (("A", "m_b_text"), ("B", "m_a_text")):
            reply = self._send(
                self.sessions[key],
                "call",
                target="channel",
                method="query",
                args=[matrix.READ_OPTIONS],
                type=T,
                id=self.ctx["AB"],
            )
            found = bool(matrix.find_terms(_responses(reply), [self.ctx[want_key]]))
            other = "B" if key == "A" else "A"
            answer = _http_answer(reply)
            self._check(
                f"AP9-{key}",
                f"client {key} reads AB over REST and sees {other}'s server-sent message",
                answer.outcome == "success" and found,
                f"query {_observed(answer)}; {other}'s text present {found}",
            )
        for key, want_key in (("A", "m_b"), ("B", "m_a")):
            events = self._events(key)
            got = [
                e
                for e in events
                if e.get("type") == "message.new" and _dig(e, "message.id") == self.ctx[want_key]
            ]
            self._check(
                f"AP10-{key}",
                f"client {key} receives the other member's server-sent message over the WebSocket",
                bool(got),
                f"{len(events)} events; message.new for the other's message {len(got)}",
            )
        self._events("X")

    def _events_split(
        self, key: str, wait_ms: int = EVENT_WAIT_MS
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Events Stream delivered to ``key``, and the types of the SDK's local events dropped."""
        reply = self._send(self.sessions[key], "events", max_calls=0, wait_ms=wait_ms)
        events = [e for e in (reply.data or {}).get("events") or [] if isinstance(e, dict)]
        delivered = [e for e in events if e.get("type") not in matrix.LOCAL_EVENT_TYPES]
        local = sorted(
            {str(e.get("type")) for e in events if e.get("type") in matrix.LOCAL_EVENT_TYPES}
        )
        return delivered, local

    def _events(self, key: str, wait_ms: int = EVENT_WAIT_MS) -> list[dict[str, Any]]:
        return self._events_split(key, wait_ms)[0]

    def reconnect_check(self) -> None:
        try:
            self._reconnect_check()
        except (GuardrailStop, RunStopped):
            raise
        except Exception as exc:  # recorded as it happened
            self._check(
                "AP11",
                "client A disconnects, reconnects over the WebSocket and receives the next message",
                False,
                f"harness error: {type(exc).__name__}: {exc}",
            )

    def _reconnect_check(self) -> None:
        session = self.sessions["A"]
        dis = self._send(session, "disconnect", max_calls=2)
        con = self._send(session, "connect", max_calls=3, user={"id": self.ctx["A"]})
        watch = self._send(
            session, "call", target="channel", method="watch", args=[], type=T, id=self.ctx["AB"]
        )
        self._events("A", wait_ms=500)
        service = AppSendService(self.state, self, T)
        outcome = service.send(self.ctx["B"], self.ctx["AB"], f"after reconnect {self.prefix}")
        events = self._events("A")
        got = [
            e
            for e in events
            if e.get("type") == "message.new" and _dig(e, "message.id") == outcome.message_id
        ]
        reconnected, watched = _ws_answer(con), _http_answer(watch)
        self._check(
            "AP11",
            "client A disconnects, reconnects over the WebSocket and receives the next message",
            dis.ok
            and reconnected.outcome == "success"
            and watched.outcome == "success"
            and bool(got),
            f"disconnect {'ok' if dis.ok else 'failed'}; reconnect {_observed(reconnected)}; "
            f"watch {_observed(watched)}; message.new received {bool(got)}",
        )

    # -- temporary type-level features ------------------------------------------------

    def _put_match_type(self, features: Mapping[str, Any]) -> ApiResult:
        body = {
            "automod": configuration.MATCH_FEATURES["automod"],
            "automod_behavior": configuration.MATCH_FEATURES["automod_behavior"],
            "max_message_length": configuration.MATCH_FEATURES["max_message_length"],
            **features,
        }
        return self.api.raw("PUT", f"/api/v2/chat/channeltypes/{T}", body=body)

    def _type_features_on(self, features: Mapping[str, Any]) -> ApiResult:
        result = self._put_match_type(features)
        time.sleep(TYPE_CHANGE_SETTLE_SECONDS)
        return result

    def _type_features_restore(self, features: Mapping[str, Any]) -> str:
        """Put the production values back and verify them; stop the run if that fails."""
        restore = {k: configuration.MATCH_FEATURES[k] for k in features}
        result = self._put_match_type(restore)
        time.sleep(TYPE_CHANGE_SETTLE_SECONDS)
        reread = self.api.get(f"/api/v2/chat/channeltypes/{T}")
        current = reread.body
        wrong = {
            k: current.get(k) if isinstance(current, dict) else None
            for k, v in restore.items()
            if not isinstance(current, dict) or current.get(k) != v
        }
        if not result.ok or not reread.ok or wrong:
            raise RunStopped(
                f"could not restore {T} features {restore}: PUT {result.status}, "
                f"re-read {reread.status}, differing {wrong}"
            )
        return f"restored {restore} ({result.status}, verified)"

    # -- matrix --------------------------------------------------------------------

    def run_matrix(
        self, only: set[str] | None = None, progress: Callable[[], None] | None = None
    ) -> None:
        reconnected = False
        for case in matrix.all_cases():
            if case.phase >= DESTRUCTIVE_PHASE and not reconnected:
                # The reconnect check needs AB; the destructive cases come after it.
                self.reconnect_check()
                reconnected = True
            if only and case.id not in only:
                continue
            if not self._remaining_ok():
                self.notes.append(
                    f"matrix stopped before {case.id}: API-call budget reserved for cleanup"
                )
                break
            try:
                if case.procedure is not None:
                    result = self._procedure(case)
                else:
                    result = self._generic_case(case)
            except GuardrailStop:
                raise
            except RunStopped as exc:
                # Record the case, then stop: a failed restore ends the run.
                self.case_results.append(
                    self._result(
                        case,
                        "-",
                        f"run stopped: {self._text(exc)}",
                        "-",
                        matrix.Verdict(matrix.INCONCLUSIVE, "the run stopped during this case"),
                    )
                )
                if progress is not None:
                    progress()
                raise
            except ClientSessionEnded as exc:
                result = self._result(
                    case,
                    "-",
                    f"not judged: {self._text(exc)}",
                    "-",
                    matrix.Verdict(
                        matrix.INCONCLUSIVE,
                        "a client session ended (timeout, mismatched reply or exit)",
                    ),
                )
            except Exception as exc:  # recorded as it happened, never hidden
                result = self._result(
                    case,
                    "-",
                    f"harness error: {type(exc).__name__}: {self._text(exc)}",
                    "-",
                    matrix.Verdict(matrix.INCONCLUSIVE, "harness error"),
                )
            self.case_results.append(result)
            if progress is not None:
                progress()
            if self._pending_stop is not None:
                raise RunStopped(f"after {case.id}: {self._pending_stop}")
        if not reconnected:
            self.reconnect_check()

    def _result(
        self,
        case: matrix.Case,
        request: str,
        observed: str,
        control: str,
        verdict: matrix.Verdict,
        detail: dict[str, Any] | None = None,
    ) -> CaseResult:
        return CaseResult(
            case_id=case.id,
            group=case.group,
            actor=case.actor,
            token=case.token,
            action=case.action,
            expected=case.expect,
            request=request,
            observed=self.redactor.text(observed),
            control=self.redactor.text(_generic(control, self.ctx)),
            verdict=verdict.label,
            reason=verdict.reason,
            detail=self.redactor.value(detail or {}),
        )

    def _replay(self, case: matrix.Case, answer: Answer) -> tuple[bool, str, Any]:
        record = answer.record
        if record is None:
            return False, "no client request to replay", None
        control = case.control
        path = "/" + str(record.get("path") or "").lstrip("/")
        params = {
            k: v if isinstance(v, str) else json.dumps(v)
            for k, v in (record.get("params") or {}).items()
            if k in control.keep_params or k == "payload"
        }
        params.update(matrix.substitute(dict(control.add_params), self.ctx))
        body = record.get("body")
        if control.body_patch:
            body = matrix.deep_merge(body, matrix.substitute(dict(control.body_patch), self.ctx))
        if control.creates_channel:
            self.ledger.reserve("channels")
            cid = path.split("/")[2] + ":" + path.split("/")[3]
            self.channels.append(cid)
        method = str(record.get("method"))
        result = self.api.raw(
            method,
            path,
            body=body if method not in ("GET", "DELETE") else None,
            params=params or None,
        )
        for name, dotted in control.capture.items():
            value = _dig(result.body, dotted)
            if isinstance(value, str):
                self.ctx[name] = value
        undo_notes = []
        if result.ok:
            for undo in control.undo:
                undo_notes.append(self._undo(undo, case.id))
        summary = f"server replay {method} -> {result.status}" + (
            f" / code {result.code} ({result.message})" if result.code is not None else ""
        )
        if undo_notes:
            summary += " (" + ", ".join(undo_notes) + ")"
        return result.ok, summary, result.body

    def _generic_case(self, case: matrix.Case) -> CaseResult:
        """Run a case; for a feature-gated case, first with the feature enabled on AB.

        With the feature on (a channel-level override), a refusal can only come
        from the permission layer, and the server control shows the request is
        well formed. The override is then removed and the same request is sent
        under the production configuration, where it must also fail.
        """
        if not case.feature_override and not case.type_override:
            return self._evaluate_case(case)
        assert case.step is not None
        path = f"/channels/{T}/{self.ctx['AB']}"
        if case.feature_override:
            override = dict(case.feature_override)
            change = self._channel_override_change(override)
            scope = "channel AB"
        else:
            override = dict(case.type_override)
            change = self._type_features_change(override)
            scope = f"type {T}"
        # The journal entry exists before the enabling request is sent.
        with self._temporary(change):
            if case.feature_override:
                on = self.api.raw("PATCH", path, body={"set": {"config_overrides": override}})
            else:
                on = self._type_features_on(override)
            result = self._evaluate_case(case)
        production = _http_answer(self._step(case.step))
        result.detail["feature_override"] = {
            "scope": scope,
            "features": override,
            "set_status": on.status,
            "restored": change.note,
        }
        result.detail["production_config_observed"] = _observed(production)
        result.observed = (
            f"feature on: {result.observed}; feature off (production): {_observed(production)}"
        )
        if not on.ok:
            result.verdict = matrix.INCONCLUSIVE
            result.reason = f"could not enable {override} ({scope}, {on.status})"
        if production.outcome == "success":
            result.verdict = matrix.FAIL
            result.reason = "succeeded under the production configuration"
            self._undo_client_success(case)
        return result

    def _evaluate_case(self, case: matrix.Case) -> CaseResult:
        assert case.step is not None
        reply = self._step(case.step)
        answer = _http_answer(reply)
        outcome = answer.outcome
        request = _request_line(answer.record, self.ctx)
        leaks = matrix.find_terms(
            _responses(reply) + [reply.data], matrix.substitute(list(case.leak_terms), self.ctx)
        )
        control_ok: bool
        control_desc: str
        control_body: Any = None
        control = case.control
        if control.kind == "server-replay":
            control_ok, control_desc, control_body = self._replay(case, answer)
        elif control.kind == "session":
            assert control.session is not None
            creply = self._step(case.step, control.session)
            canswer = _http_answer(creply)
            control_ok = canswer.outcome == "success"
            control_body = _responses(creply)
            control_desc = f"{control.session}: {_observed(canswer)}"
        elif control.kind == "server-upload":
            control_ok, control_desc = self._upload_control(case)
        else:
            control_ok, control_desc = False, "no control"
        self.control_ok[case.id] = control_ok
        detail: dict[str, Any] = {"stream_message": _answer_message(answer, reply)}
        if case.expect == "no-leak":
            terms = matrix.substitute(list(control.expect_terms), self.ctx)
            found = bool(terms) and len(matrix.find_terms(control_body, terms)) == len(terms)
            detail["learned"] = self._learned(reply)
            verdict = matrix.no_leak_verdict(outcome, leaks, control_ok, found)
            control_desc += f"; control found target data {found}"
        else:
            verdict = matrix.refused_verdict(outcome, control_ok)
            if leaks:
                verdict = matrix.Verdict(matrix.FAIL, "response disclosed: " + ", ".join(leaks))
        if outcome == "success":
            self._track_client_created(reply)
            if case.expect == "refused":
                detail["client_success_note"] = "client action succeeded; see verdict"
                self._undo_client_success(case)
        return self._result(case, request, _observed(answer), control_desc, verdict, detail)

    def _undo_client_success(self, case: matrix.Case) -> None:
        # A bypass that changed state is reversed with the case's own undo requests.
        for undo in case.control.undo:
            self._undo(undo, case.id)

    def _track_client_created(self, reply: Reply) -> None:
        """A poll or user group a client managed to create is deleted at cleanup."""
        for response in _responses(reply):
            poll_id = _dig(response, "poll.id")
            if isinstance(poll_id, str) and poll_id:
                owner = _dig(response, "poll.created_by_id") or self.ctx.get("A", "")
                self.polls.append((poll_id, str(owner)))
            group_id = _dig(response, "user_group.id")
            if isinstance(group_id, str) and group_id:
                self.groups.append(group_id)

    def _learned(self, reply: Reply) -> dict[str, Any]:
        """What the response revealed, with non-synthetic identifiers withheld."""
        learned: dict[str, Any] = {"channels": [], "users": [], "messages": 0}
        for response in _responses(reply):
            if not isinstance(response, dict):
                continue
            for ch in response.get("channels") or []:
                cid = _dig(ch, "channel.cid")
                learned["channels"].append(self._synthetic(str(cid)))
            for user in response.get("users") or []:
                learned["users"].append(self._synthetic(str(user.get("id"))))
            learned["messages"] += len(response.get("results") or [])
            if isinstance(response.get("message"), dict):
                learned["messages"] += 1
        return learned

    def _synthetic(self, identifier: str) -> str:
        if self.prefix in identifier:
            return _generic(identifier, self.ctx)
        return "<non-synthetic identifier withheld>"

    def _upload_control(self, case: matrix.Case) -> tuple[bool, str]:
        assert case.step is not None
        args = case.step.params["args"]
        content = base64.b64decode(args[0]["__buffer_b64"])
        kind = "file" if case.step.params["method"] == "sendFile" else "image"
        result = self.api.raw_multipart(
            f"/channels/{T}/{self.ctx['AB']}/{kind}",
            fields={"user": json.dumps({"id": self.ctx["A"]})},
            file_name=str(args[1]),
            content=content,
            mime=str(args[2]),
        )
        note = f"server upload -> {result.status}" + (
            f" / code {result.code}" if result.code is not None else ""
        )
        url = result.body.get("file") if isinstance(result.body, dict) else None
        if result.ok and isinstance(url, str):
            undone = self.api.raw(
                "DELETE", f"/channels/{T}/{self.ctx['AB']}/{kind}", params={"url": url}
            )
            note += f" (undo DELETE {undone.status})"
            if not undone.ok:
                self._defer_stop(
                    f"{case.id}: deleting the control's upload got {undone.status} "
                    f"code {undone.code}: {undone.message}"
                )
        return result.ok, note

    # -- procedures ------------------------------------------------------------------

    def _procedure(self, case: matrix.Case) -> CaseResult:
        assert case.procedure is not None
        name, _, arg = case.procedure.partition(":")
        handler = {
            "token-rest": self._proc_token_rest,
            "token-ws": self._proc_token_ws,
            "token-rest-claim": self._proc_token_claim,
            "guest-create": self._proc_guest_create,
            "guest-role": self._proc_guest_role,
            "anonymous": self._proc_anonymous,
            "poll-vote": self._proc_poll_vote,
            "member-custom": self._proc_member_custom,
            "profile-on-connect": self._proc_profile_on_connect,
            "role-on-connect": self._proc_role_on_connect,
            "typing-payload": self._proc_typing,
            "read-payload": self._proc_read,
            "realtime-isolation": self._proc_realtime_isolation,
        }[name]
        return handler(case, arg)

    def _bad_token(self, kind: str) -> tuple[str | None, str]:
        a = self.ctx["A"]
        if kind == "T1":
            return None, "dev"
        if kind == "T2":
            return ServerApi.wrong_secret_token(a, secrets.token_urlsafe(32), 600), "env"
        if kind == "T3":
            return self.api.expired_user_token(a), "env"
        return self._tokens["A"], "env"

    def _query_ab_step(self) -> dict[str, Any]:
        return {
            "target": "channel",
            "method": "query",
            "args": [matrix.READ_OPTIONS],
            "type": T,
            "id": self.ctx["AB"],
        }

    def _proc_token_rest(self, case: matrix.Case, kind: str) -> CaseResult:
        token, source = self._bad_token(kind)
        session = self._session(f"tok-{kind}-rest", token, max_api_calls=10)
        try:
            set_reply = self._send(
                session, "set_rest_user", max_calls=1, user_id=self.ctx["A"], token_source=source
            )
            reply = self._send(session, "call", max_calls=2, **self._query_ab_step())
        finally:
            session.close()
        control = _http_answer(
            self._send(self.sessions["A"], "call", max_calls=2, **self._query_ab_step())
        )
        answer = _http_answer(reply)
        verdict = matrix.refused_verdict(answer.outcome, control.outcome == "success")
        detail = {"token_used": self._describe_bad(kind, token), "set_user": set_reply.ok}
        return self._result(
            case,
            _request_line(answer.record, self.ctx),
            _observed(answer),
            f"A valid token: {_observed(control)}",
            verdict,
            detail,
        )

    def _describe_bad(self, kind: str, token: str | None) -> dict[str, Any]:
        if kind == "T1":
            return {"form": "development token generated client-side by StreamChat.devToken"}
        return describe_token(token or "")

    def _proc_token_ws(self, case: matrix.Case, kind: str) -> CaseResult:
        token: str | None
        if kind == "T4":
            token, source = self._tokens["A"], "env"
            user = {"id": self.ctx["B"]}
            control_reply = self.connect_replies.get("B")
            control_label = "B's own token as B"
        else:
            token, source = self._bad_token(kind)
            user = {"id": self.ctx["A"]}
            control_reply = self.connect_replies.get("A")
            control_label = "A's valid token"
        session = self._session(f"tok-{kind}-ws", token, max_api_calls=10)
        try:
            reply = self._send(
                session,
                "connect",
                max_calls=2,
                user=user,
                token_source=source,
                skip_validation=(kind == "T4"),
            )
            if reply.ok:
                self._send(session, "disconnect", max_calls=2)
        finally:
            session.close()
        answer = _ws_answer(reply)
        control_answer = _ws_answer(control_reply) if control_reply else None
        control_ok = control_answer is not None and control_answer.outcome == "success"
        verdict = matrix.refused_verdict(answer.outcome, control_ok)
        me = ((reply.data or {}).get("me") or {}) if reply.ok else {}
        connected_as = me.get("id") if isinstance(me, dict) else None
        if kind == "T4" and answer.outcome == "success":
            if connected_as == self.ctx["A"]:
                verdict = matrix.Verdict(
                    matrix.HOLDS_IGNORED,
                    "claim ignored: Stream authenticated the connection as A (the token's user)",
                )
            elif connected_as == self.ctx["B"]:
                verdict = matrix.Verdict(matrix.FAIL, "connected as B with A's token")
            else:
                verdict = matrix.Verdict(matrix.INCONCLUSIVE, "connected identity unknown")
        detail = {
            "token_used": self._describe_bad(kind, token) if kind != "T4" else "A's valid token",
            "error_kind": (reply.error or {}).get("kind"),
            "error_message": reply.message,
            "connected_as": _generic(str(connected_as), self.ctx) if connected_as else None,
            "ws_attempts": reply.ws_attempts,
        }
        return self._result(
            case,
            "WebSocket /connect",
            _observed(answer),
            f"{control_label}: {_observed(control_answer) if control_answer else 'not run'}",
            verdict,
            detail,
        )

    def _proc_token_claim(self, case: matrix.Case, kind: str) -> CaseResult:
        session = self._session(f"claim-{kind}", self._tokens["A"], max_api_calls=10)
        try:
            if kind == "XD":
                self._send(
                    session,
                    "set_rest_user",
                    max_calls=1,
                    user_id=self.ctx["X"],
                    token_source="env",
                    skip_validation=True,
                )
                step = dict(self._query_ab_step(), id=self.ctx["XD"])
                reply = self._send(session, "call", max_calls=2, **step)
                control = _http_answer(self._send(self.sessions["X"], "call", max_calls=2, **step))
                answer = _http_answer(reply)
                verdict = matrix.refused_verdict(answer.outcome, control.outcome == "success")
                leaks = matrix.find_terms(_responses(reply), [self.ctx["xd_text"]])
                if leaks:
                    verdict = matrix.Verdict(matrix.FAIL, "response disclosed XD's message")
                return self._result(
                    case,
                    self._claim_request_line(answer.record),
                    _observed(answer),
                    f"X: {_observed(control)}",
                    verdict,
                )
            # unread: A has marked AB read, B has not; the claim must not return B's counts.
            self._send(
                self.sessions["A"],
                "call",
                target="channel",
                method="markRead",
                args=[{}],
                type=T,
                id=self.ctx["AB"],
            )
            own_a = self._send(
                self.sessions["A"], "call", target="client", method="getUnreadCount", args=[]
            )
            own_b = self._send(
                self.sessions["B"], "call", target="client", method="getUnreadCount", args=[]
            )
            self._send(
                session,
                "set_rest_user",
                max_calls=1,
                user_id=self.ctx["B"],
                token_source="env",
                skip_validation=True,
            )
            reply = self._send(session, "call", target="client", method="getUnreadCount", args=[])
        finally:
            session.close()

        def total(r: Reply) -> Any:
            responses = _responses(r)
            return (
                responses[-1].get("total_unread_count")
                if responses and isinstance(responses[-1], dict)
                else None
            )

        a_total, b_total, claim_total = total(own_a), total(own_b), total(reply)
        answer = _http_answer(reply)
        outcome = answer.outcome
        # The controls: A's and B's own identical requests succeed.
        controls_ok = (
            _http_answer(own_a).outcome == "success" and _http_answer(own_b).outcome == "success"
        )
        if outcome in ("auth", "permission", "no-response"):
            verdict = matrix.refused_verdict(outcome, controls_ok)
        elif outcome == "success" and a_total != b_total:
            if claim_total == a_total:
                verdict = matrix.Verdict(
                    matrix.HOLDS_IGNORED, "claim ignored: the response is A's own unread count"
                )
            elif claim_total == b_total:
                verdict = matrix.Verdict(matrix.FAIL, "the response is B's unread count")
            else:
                verdict = matrix.Verdict(matrix.INCONCLUSIVE, "count matches neither user")
        elif outcome == "success":
            verdict = matrix.Verdict(matrix.INCONCLUSIVE, "A's and B's counts do not differ")
        else:
            verdict = matrix.Verdict(matrix.INCONCLUSIVE, f"refusal not attributable ({outcome})")
        return self._result(
            case,
            self._claim_request_line(answer.record),
            _observed(answer),
            f"A's own total {a_total}; B's own total {b_total}",
            verdict,
            {"claimed_total": claim_total},
        )

    def _claim_request_line(self, record: dict[str, Any] | None) -> str:
        """The request line, with the user_id the client actually sent (if any)."""
        params = record.get("params") if record else None
        claimed = params.get("user_id") if isinstance(params, dict) else None
        suffix = f" ?user_id={_generic(str(claimed), self.ctx)}" if claimed else ""
        return _request_line(record, self.ctx) + suffix

    def _set_guest_creation_disabled(self, disabled: bool) -> ApiResult:
        return self.api.raw("PATCH", "/api/v2/app", body={"guest_user_creation_disabled": disabled})

    def _proc_guest_create(self, case: matrix.Case, _arg: str) -> CaseResult:
        guest_id = f"{self.prefix}-guest"
        user = {"id": guest_id, "name": "Synthetic guest"}
        self.ledger.reserve("users")
        session = self._session("guest-attempt", None, max_api_calls=10)
        try:
            reply = self._send(session, "guest", max_calls=3, user=user)
            if reply.ok:
                self._send(session, "disconnect", max_calls=2)
        finally:
            session.close()
        # The request under test is the client's POST /guest. setGuestUser then
        # also connects; that connect is not what G1 tests.
        post = self._guest_post(reply)
        answer = _answer_of(post, reply)
        # Stream stores guests as "guest-<uuid>-<requested id>"; read the ID it returned.
        created_id = self._guest_created(reply)
        exists_after = created_id is not None
        if exists_after:
            self.users.append(str(created_id))
        else:
            self.ledger.release("users")  # refused: no user was created
        control_ok = False
        control_desc = "not run (the client's POST /guest was not refused)"
        guest_role = None
        if created_id is None and answer.outcome not in ("success", "no-response"):
            # Positive control: the identical client request with guest creation
            # enabled for a moment, then disabled again and verified. The journal
            # entry exists before guest creation is enabled.
            self.ledger.reserve("users")
            change = self._guest_creation_change()
            with self._temporary(change):
                on = self._set_guest_creation_disabled(False)
                time.sleep(TYPE_CHANGE_SETTLE_SECONDS)
                guest = self._session("guest", None, max_api_calls=30)
                creply = self._send(guest, "guest", max_calls=3, user=user)
            cpost = self._guest_post(creply)
            post_status = cpost.get("status") if cpost else None
            control_ok = isinstance(post_status, int) and 200 <= post_status < 300
            control_created = self._guest_created(creply)
            if control_created is not None:
                self.ctx["guest_id"] = control_created
                self.users.append(control_created)
                guest_role = _dig(cpost.get("response") if cpost else None, "user.role")
            else:
                self.ledger.release("users")
            connected = _ws_answer(creply)
            if connected.outcome != "success":
                guest.close()
                self.sessions.pop("guest", None)
            control_desc = (
                f"identical request with guest creation enabled ({on.status}): POST /guest "
                f"{post_status}; guest connect {_observed(connected)}; {change.note}"
            )
        if created_id is not None:
            verdict = matrix.Verdict(matrix.FAIL, "the client's POST /guest created a guest user")
        else:
            verdict = matrix.refused_verdict(answer.outcome, control_ok)
        return self._result(
            case,
            _request_line(post or reply.last_request, self.ctx),
            _observed(answer),
            control_desc,
            verdict,
            {
                "stream_message": _answer_message(answer, reply),
                "client_guest_user_exists_after": exists_after,
                "client_connect": _observed(_ws_answer(reply)) if exists_after else None,
                "control_guest_role": guest_role,
            },
        )

    @staticmethod
    def _guest_post(reply: Reply) -> dict[str, Any] | None:
        return next((r for r in reply.requests if r.get("path") == "/guest"), None)

    @staticmethod
    def _guest_created(reply: Reply) -> str | None:
        for record in reply.requests:
            status = record.get("status")
            if record.get("path") == "/guest" and isinstance(status, int) and status < 300:
                created = _dig(record.get("response"), "user.id")
                return str(created) if created else None
        return None

    def _read_probe(self, suffix: str) -> tuple[dict[str, Any], str | None]:
        """The request a guest or anonymous client makes, and the session that controls it."""
        if suffix == "read-ab":
            return self._query_ab_step(), "A"
        if suffix == "channels":
            return {
                "target": "client",
                "method": "queryChannels",
                "args": [{"members": {"$in": [self.ctx["A"]]}}, [], matrix.READ_OPTIONS],
            }, "A"
        if suffix == "users":
            return {
                "target": "client",
                "method": "queryUsers",
                "args": [{"id": {"$in": [self.ctx[k] for k in ("A", "B", "X", "D")]}}],
            }, None
        return {"target": "client", "method": "getMessage", "args": [self.ctx["m_x"]]}, "X"

    def _proc_guest_role(self, case: matrix.Case, suffix: str) -> CaseResult:
        session = self.sessions.get("guest")
        if session is None:
            return self._result(
                case,
                "-",
                "not run: no guest session",
                "-",
                matrix.Verdict(matrix.INCONCLUSIVE, "the guest control did not create a guest"),
            )
        return self._probe_case(case, session, suffix)

    def _proc_anonymous(self, case: matrix.Case, suffix: str) -> CaseResult:
        session = self.sessions.get("anonymous")
        if session is None:
            session = self._session("anonymous", None, max_api_calls=20)
            connect = self._send(session, "anonymous", max_calls=3)
            self.connect_replies["anonymous"] = connect
            self.notes.append(f"anonymous connect: {_observed(_ws_answer(connect))}")
        connected = _ws_answer(self.connect_replies["anonymous"])
        if connected.outcome != "success":
            # A failed anonymous connect makes the SDK rethrow it for every probe
            # without sending a request, so nothing could be judged.
            return self._result(
                case,
                "-",
                f"not run: the anonymous connect got {_observed(connected)}",
                "-",
                matrix.Verdict(matrix.INCONCLUSIVE, "the anonymous connect did not succeed"),
            )
        return self._probe_case(case, session, suffix)

    def _probe_case(self, case: matrix.Case, session: ClientSession, suffix: str) -> CaseResult:
        step, control_session = self._read_probe(suffix)
        reply = self._send(session, "call", max_calls=2, **step)
        answer = _http_answer(reply)
        outcome = answer.outcome
        leaks = matrix.find_terms(
            _responses(reply), matrix.substitute(list(case.leak_terms), self.ctx)
        )
        if control_session is not None:
            control = self._send(self.sessions[control_session], "call", max_calls=2, **step)
            canswer = _http_answer(control)
            control_ok, control_body = canswer.outcome == "success", _responses(control)
            control_desc = f"{control_session}: {_observed(canswer)}"
        else:
            result = self.api.raw(
                "GET",
                "/users",
                params={"payload": json.dumps({"filter_conditions": step["args"][0]})},
            )
            control_ok, control_body = result.ok, result.body
            control_desc = f"server GET /users -> {result.status}"
        terms = matrix.substitute(list(case.leak_terms), self.ctx)
        found = bool(matrix.find_terms(control_body, terms))
        verdict = matrix.no_leak_verdict(outcome, leaks, control_ok, found)
        return self._result(
            case,
            _request_line(answer.record, self.ctx),
            _observed(answer),
            control_desc + f"; control found target data {found}",
            verdict,
            {"learned": self._learned(reply), "stream_message": _answer_message(answer, reply)},
        )

    def _proc_poll_vote(self, case: matrix.Case, _arg: str) -> CaseResult:
        """Polls cannot be overridden per channel, so they are enabled on the type
        briefly: B's poll message is created, A's vote must still be refused by the
        permission layer, the server's identical vote succeeds; then polls go off
        again (verified) and A's vote is repeated under the production config."""
        change = self._type_features_change({"polls": True})
        vote_args: list[Any] = []
        reply: Reply | None = None
        control_ok, control_desc = False, "no control"
        setup_note = ""
        # The journal entry exists before polls are enabled.
        with self._temporary(change):
            on = self._type_features_on({"polls": True})
            poll = self.api.raw(
                "POST",
                "/polls",
                body={
                    "name": "server poll",
                    "options": [{"text": "yes"}],
                    "user_id": self.ctx["B"],
                },
            )
            poll_id = _dig(poll.body, "poll.id")
            options = _dig(poll.body, "poll.options")
            option_id = (
                options[0].get("id")
                if isinstance(options, list) and options and isinstance(options[0], dict)
                else None
            )
            if poll.ok and poll_id:
                self.polls.append((str(poll_id), self.ctx["B"]))
            msg = self.api.raw(
                "POST",
                f"/channels/{T}/{self.ctx['AB']}/message",
                body={"message": {"text": "poll", "poll_id": poll_id, "user_id": self.ctx["B"]}},
            )
            message_id = _dig(msg.body, "message.id")
            setup_note = (
                f"polls on ({on.status}); poll {poll.status}; poll message {msg.status} / "
                f"code {msg.code} ({msg.message})"
            )
            if poll.ok and msg.ok and message_id:
                vote_args = [message_id, poll_id, {"option_id": option_id}]
                reply = self._send(
                    self.sessions["A"],
                    "call",
                    target="client",
                    method="castPollVote",
                    args=vote_args,
                )
                record = _http_answer(reply).record
                if record is not None:
                    body = matrix.deep_merge(record.get("body"), {"user_id": self.ctx["A"]})
                    path = "/" + str(record.get("path")).lstrip("/")
                    result = self.api.raw("POST", path, body=body)
                    control_ok = result.ok
                    control_desc = f"server replay POST -> {result.status}"
        if reply is None:
            return self._result(
                case,
                "-",
                "not set up",
                f"{setup_note}; {change.note}",
                matrix.Verdict(matrix.INCONCLUSIVE, "no poll message could be created in AB"),
            )
        production = _http_answer(
            self._send(
                self.sessions["A"], "call", target="client", method="castPollVote", args=vote_args
            )
        )
        answer = _http_answer(reply)
        verdict = matrix.refused_verdict(answer.outcome, control_ok)
        if production.outcome == "success":
            verdict = matrix.Verdict(matrix.FAIL, "succeeded under the production configuration")
        return self._result(
            case,
            _request_line(answer.record, self.ctx),
            f"polls on: {_observed(answer)}; polls off (production): {_observed(production)}",
            control_desc,
            verdict,
            {
                "stream_message": _answer_message(answer, reply),
                "production_message": production.record.get("response", {}).get("message")
                if production.record and isinstance(production.record.get("response"), dict)
                else None,
                "feature_override": {
                    "scope": f"type {T}",
                    "features": {"polls": True},
                    "set_status": on.status,
                    "restored": change.note,
                },
            },
        )

    def _b_member_views(self, marker: str) -> dict[str, Any]:
        """Whether B can read ``marker`` from A's membership, by each read B has.

        The events view counts only events Stream delivered: the SDK's local
        events (B's own query raises ``channels.queried`` with the queried state)
        are dropped, and the types of the events that carried the marker are
        recorded.
        """
        b = self.sessions["B"]
        query = self._send(
            b,
            "call",
            target="channel",
            method="query",
            args=[matrix.READ_OPTIONS],
            type=T,
            id=self.ctx["AB"],
        )
        members = self._send(
            b,
            "call",
            target="channel",
            method="queryMembers",
            args=[{}],
            type=T,
            id=self.ctx["AB"],
        )
        events, local = self._events_split("B")
        carriers = sorted({str(e.get("type")) for e in events if matrix.find_terms(e, [marker])})
        return {
            "channel_query": _observed(_http_answer(query)),
            "channel_query_has_marker": bool(matrix.find_terms(_responses(query), [marker])),
            "query_members": _observed(_http_answer(members)),
            "query_members_has_marker": bool(matrix.find_terms(_responses(members), [marker])),
            "event_types": sorted({str(e.get("type")) for e in events}),
            "local_event_types_dropped": local,
            "events_have_marker": bool(carriers),
            "marker_event_types": carriers,
        }

    def _unset_member_note(self) -> str:
        undone = self.api.raw(
            "PATCH",
            f"/channels/{T}/{self.ctx['AB']}/member",
            body={"unset": ["glow_note"]},
            params={"user_id": self.ctx["A"]},
        )
        if not undone.ok:
            self._defer_stop(
                f"S15: unsetting A's member field got {undone.status} code {undone.code}: "
                f"{undone.message}"
            )
        return str(undone.status)

    @staticmethod
    def _member_leaks(views: Mapping[str, Any]) -> list[str]:
        found = [n for n in ("channel_query", "query_members") if views.get(f"{n}_has_marker")]
        if views.get("events_have_marker"):
            found.append(f"events ({', '.join(views.get('marker_event_types') or [])})")
        return found

    def _proc_member_custom(self, case: matrix.Case, _arg: str) -> CaseResult:
        flat = self.prefix.replace("-", "")
        marker = f"memberfree{flat}"
        self.ctx["member_marker"] = marker
        path = f"/channels/{T}/{self.ctx['AB']}"
        self._events("B", wait_ms=0)
        reply = self._send(
            self.sessions["A"],
            "call",
            target="channel",
            method="updateMemberPartial",
            args=[{"set": {"glow_note": marker}}],
            type=T,
            id=self.ctx["AB"],
        )
        answer = _http_answer(reply)
        try:
            production = self._b_member_views(marker)
        finally:
            unset_first = self._unset_member_note()
        # Control: grant read-channel-members on AB (the first configuration) and
        # repeat A's identical write; B's same reads must now find it. The journal
        # entry exists before the grant is set.
        marker2 = f"memberctl{flat}"
        grant = {"grants": {"channel_member": ["read-channel-members"]}}
        change = self._channel_override_change(grant)
        granted: dict[str, Any] = {}
        control_answer: Answer | None = None
        try:
            with self._temporary(change):
                on = self.api.raw("PATCH", path, body={"set": {"config_overrides": grant}})
                self._events("B", wait_ms=0)
                creply = self._send(
                    self.sessions["A"],
                    "call",
                    target="channel",
                    method="updateMemberPartial",
                    args=[{"set": {"glow_note": marker2}}],
                    type=T,
                    id=self.ctx["AB"],
                )
                control_answer = _http_answer(creply)
                granted = self._b_member_views(marker2)
        finally:
            unset_second = self._unset_member_note()
        leaks = self._member_leaks(production)
        found = self._member_leaks(granted)
        control_ok = on.ok and control_answer is not None and control_answer.outcome == "success"
        verdict = matrix.no_leak_verdict(
            answer.outcome, [f"B read it via {n}" for n in leaks], control_ok, bool(found)
        )
        if verdict.label == matrix.HOLDS_FILTERED:
            verdict = matrix.Verdict(
                matrix.HOLDS_FILTERED,
                "A's write is accepted and stored, but B cannot read it without "
                f"read-channel-members; with that grant B reads it via {', '.join(found)}",
            )
        return self._result(
            case,
            _request_line(answer.record, self.ctx),
            _observed(answer),
            f"with read-channel-members granted on AB ({on.status}): A's write "
            f"{_observed(control_answer) if control_answer else 'not sent'}; B found it via "
            f"{found or 'nothing'}; {change.note}; member field unset "
            f"({unset_first}, {unset_second})",
            verdict,
            {"production_b_views": production, "granted_b_views": granted},
        )

    def _server_user(self, user_id: str) -> dict[str, Any]:
        result = self.api.require(
            self.api.get(
                "/api/v2/users",
                params={"payload": json.dumps({"filter_conditions": {"id": {"$eq": user_id}}})},
            )
        )
        users = result.body.get("users") or [{}]
        user = users[0]
        return user if isinstance(user, dict) else {}

    def _proc_profile_on_connect(self, case: matrix.Case, _arg: str) -> CaseResult:
        fields = {
            "name": "renamed on connect by A",
            "image": "https://example.invalid/a.png",
            "glow_bio": "connect free text",
        }
        session = self._session("A-profile", self._tokens["A"], max_api_calls=10)
        try:
            reply = self._send(
                session, "connect", max_calls=3, user={"id": self.ctx["A"], **fields}
            )
            if reply.ok:
                self._send(session, "disconnect", max_calls=2)
        finally:
            session.close()
        answer = _ws_answer(reply)
        # What Stream answered in the handshake: the connection's own user object.
        me = ((reply.data or {}).get("me") or {}) if answer.outcome == "success" else {}
        me_applied = isinstance(me, dict) and (
            me.get("name") == fields["name"]
            or me.get("image") == fields["image"]
            or "glow_bio" in (me.get("custom_keys") or [])
        )
        stored = self._server_user(self.ctx["A"])
        custom = stored.get("custom") or {}
        stored_applied = (
            stored.get("name") == fields["name"]
            or stored.get("image") == fields["image"]
            or custom.get("glow_bio") == fields["glow_bio"]
            or stored.get("glow_bio") == fields["glow_bio"]
        )
        control = self.api.raw(
            "PATCH",
            "/users",
            body={"users": [{"id": self.ctx["A"], "set": {"name": fields["name"]}}]},
        )
        after = self._server_user(self.ctx["A"]) if control.ok else {}
        control_ok = control.ok and after.get("name") == fields["name"]
        restore = self.api.raw(
            "PATCH",
            "/users",
            body={
                "users": [
                    {
                        "id": self.ctx["A"],
                        "set": {"name": self.ctx["A_name"]},
                        "unset": ["image", "glow_bio"],
                    }
                ]
            },
        )
        if not restore.ok:
            self._defer_stop(f"S14: restoring A's profile got {restore.status} code {restore.code}")
        if stored_applied:
            self.notes.append("S14: profile fields set on connect reached stored state; restored")
        verdict = matrix.not_effective_verdict(stored_applied, answer.outcome, control_ok)
        if me_applied and not stored_applied:
            verdict = matrix.Verdict(
                matrix.FAIL, "the connection's user object carried the new profile fields"
            )
        return self._result(
            case,
            "WebSocket /connect (user object with name, image, custom field)",
            _observed(answer),
            f"server PATCH /users -> {control.status}; name applied {control_ok}",
            verdict,
            {
                "stored_name_is_original": stored.get("name") == self.ctx["A_name"],
                "stored_has_image": bool(stored.get("image")),
                "stored_custom_keys": sorted(custom.keys()),
                "connection_carried_new_fields": me_applied,
                "restore_status": restore.status,
            },
        )

    def _proc_role_on_connect(self, case: matrix.Case, _arg: str) -> CaseResult:
        session = self._session("A-role", self._tokens["A"], max_api_calls=10)
        try:
            reply = self._send(
                session, "connect", max_calls=3, user={"id": self.ctx["A"], "role": "admin"}
            )
            if reply.ok:
                self._send(session, "disconnect", max_calls=2)
        finally:
            session.close()
        answer = _ws_answer(reply)
        me = ((reply.data or {}).get("me") or {}) if answer.outcome == "success" else {}
        connect_me_role = me.get("role") if isinstance(me, dict) else None
        stored = self._server_user(self.ctx["A"])
        stored_applied = stored.get("role") != "user"
        if stored_applied:
            restored = self.api.raw(
                "PATCH", "/users", body={"users": [{"id": self.ctx["A"], "set": {"role": "user"}}]}
            )
            if not restored.ok:
                self._defer_stop(f"E5: restoring A's role got {restored.status}")
            self.notes.append("E5: role on connect reached stored state; restored to user")
        control_ok = self.control_ok.get("E1", False)
        verdict = matrix.not_effective_verdict(stored_applied, answer.outcome, control_ok)
        if connect_me_role not in (None, "user") and not stored_applied:
            verdict = matrix.Verdict(
                matrix.FAIL, f"the connection's user object carried role {connect_me_role}"
            )
        return self._result(
            case,
            "WebSocket /connect (user object with role admin)",
            _observed(answer),
            f"E1 server replay succeeded: {control_ok}",
            verdict,
            {
                "stored_role": stored.get("role"),
                "connect_me_role": connect_me_role,
            },
        )

    def _payload_case(
        self, case: matrix.Case, step: dict[str, Any], event_types: tuple[str, ...], marker: str
    ) -> CaseResult:
        """What B receives when A sends ``step``; every window is searched for the marker."""
        self._events("B", wait_ms=0)
        reply = self._send(self.sessions["A"], "call", max_calls=2, **step)
        answer = _http_answer(reply)
        after_request, local_first = self._events_split("B")
        service = AppSendService(self.state, self, T)
        probe = service.send(self.ctx["A"], self.ctx["AB"], f"listener probe {self.prefix}")
        after_probe, local_second = self._events_split("B")
        windows = after_request + after_probe
        listening = any(
            e.get("type") == "message.new" and _dig(e, "message.id") == probe.message_id
            for e in after_probe
        )
        events = [e for e in windows if e.get("type") in event_types]
        carriers = sorted({str(e.get("type")) for e in windows if matrix.find_terms(e, [marker])})
        outcome = answer.outcome
        keys = sorted({k for e in events for k in e.keys()})
        if carriers:
            verdict = matrix.Verdict(
                matrix.FAIL, f"B received the free-text field in {', '.join(carriers)}"
            )
        elif outcome == "no-response":
            verdict = matrix.Verdict(matrix.INCONCLUSIVE, matrix.NO_RESPONSE_REASON)
        elif not listening:
            verdict = matrix.Verdict(matrix.INCONCLUSIVE, "B's listener did not see the probe")
        elif events:
            verdict = matrix.Verdict(matrix.HOLDS, "delivered without the free-text field")
        elif outcome == "success":
            verdict = matrix.Verdict(matrix.HOLDS_IGNORED, "accepted; B received no such event")
        else:
            # This case asks what reaches B: nothing did, and Stream refused the request.
            verdict = matrix.Verdict(
                matrix.HOLDS, f"refused ({outcome}); nothing delivered to B, who was listening"
            )
        return self._result(
            case,
            _request_line(answer.record, self.ctx),
            _observed(answer),
            f"B listening (received a probe message): {listening}",
            verdict,
            {
                "event_types": sorted({str(e.get("type")) for e in events}),
                "all_event_types": sorted({str(e.get("type")) for e in windows}),
                "marker_event_types": carriers,
                "local_event_types_dropped": sorted(set(local_first) | set(local_second)),
                "event_keys": keys,
                "sample": self._event_sample(events),
                "no_answer_note": answer.note or None,
            },
        )

    def _event_sample(self, events: list[dict[str, Any]]) -> Any:
        if not events:
            return None
        sample = dict(events[0])
        for key in ("user", "me", "channel"):
            if isinstance(sample.get(key), dict):
                sample[key] = {"id": _generic(str(sample[key].get("id")), self.ctx)}
        return json.loads(_generic(json.dumps(sample, default=str), self.ctx))

    def _proc_typing(self, case: matrix.Case, _arg: str) -> CaseResult:
        marker = f"typingfree{self.prefix.replace('-', '')}"
        step = {
            "target": "channel",
            "method": "sendEvent",
            "type": T,
            "id": self.ctx["AB"],
            "args": [{"type": "typing.start", "glow_text": marker, "text": marker}],
        }
        return self._payload_case(case, step, ("typing.start", "typing.stop"), marker)

    def _proc_read(self, case: matrix.Case, _arg: str) -> CaseResult:
        marker = f"readfree{self.prefix.replace('-', '')}"
        step = {
            "target": "channel",
            "method": "markRead",
            "type": T,
            "id": self.ctx["AB"],
            "args": [{"glow_text": marker, "text": marker}],
        }
        return self._payload_case(case, step, ("message.read", "notification.mark_read"), marker)

    def _proc_realtime_isolation(self, case: matrix.Case, _arg: str) -> CaseResult:
        for key in ("A", "X"):
            self._events(key, wait_ms=0)
        service = AppSendService(self.state, self, T)
        ab = service.send(self.ctx["B"], self.ctx["AB"], f"rt ab {self.prefix}")
        xd = service.send(self.ctx["D"], self.ctx["XD"], f"rt xd {self.ctx['xd_text']}")
        a_events = self._events("A")
        x_events = self._events("X", wait_ms=0)
        a_got_ab = any(_dig(e, "message.id") == ab.message_id for e in a_events)
        leaks = [
            str(e.get("type"))
            for e in a_events
            if matrix.find_terms(e, [self.ctx["XD"], self.ctx["xd_text"]])
        ]
        x_got_xd = any(_dig(e, "message.id") == xd.message_id for e in x_events)
        if leaks:
            verdict = matrix.Verdict(matrix.FAIL, "A received XD events: " + ", ".join(leaks))
        elif a_got_ab and x_got_xd:
            verdict = matrix.Verdict(matrix.HOLDS, "A received AB's event and nothing for XD")
        else:
            verdict = matrix.Verdict(
                matrix.INCONCLUSIVE, f"A got AB event {a_got_ab}; X got XD event {x_got_xd}"
            )
        return self._result(
            case,
            "WebSocket events",
            f"A: {len(a_events)} events, AB message.new {a_got_ab}",
            f"X received XD message.new {x_got_xd}",
            verdict,
            {"a_event_types": sorted({str(e.get("type")) for e in a_events})},
        )

    # -- cleanup ---------------------------------------------------------------------

    def close_sessions(self) -> None:
        for session in list(self.sessions.values()):
            session.close()
        self.sessions.clear()

    def _wait_task(self, task_id: str | None) -> str:
        if not task_id:
            return "no task"
        status = "unknown"
        for _ in range(TASK_POLL_ATTEMPTS):
            result = self.api.get(f"/api/v2/tasks/{task_id}")
            status = str(result.body.get("status")) if isinstance(result.body, dict) else "?"
            if status in ("completed", "failed"):
                return status
            time.sleep(TASK_POLL_INTERVAL_SECONDS)
        return status

    def cleanup(self) -> dict[str, Any]:
        """Delete everything this run created; each step is guarded and recorded.

        A charge signal ends the cleanup at once; any other failure is recorded
        and the next step still runs. :func:`cleanup_problems` judges the result.
        """
        self.close_sessions()
        out: dict[str, Any] = {"errors": []}
        steps: list[tuple[str, Callable[[], None]]] = [
            ("polls", lambda: self._delete_polls(out)),
            ("user groups", lambda: self._delete_groups(out)),
            ("channels", lambda: self._delete_channels(out)),
            ("users", lambda: self._delete_users(out)),
            ("deleted-user artifacts", lambda: self._delete_artifacts(out)),
            ("verify-clean", lambda: out.update(self.verify_clean())),
        ]
        for name, step in steps:
            try:
                step()
            except GuardrailStop as exc:
                out["errors"].append(f"{name}: {self._text(exc)}")
                if "stopping at once" in str(exc):
                    break
            except Exception as exc:  # recorded, and the next step still runs
                out["errors"].append(f"{name}: {type(exc).__name__}: {self._text(exc)}")
        self.cleanup_result = out
        return out

    def _delete_polls(self, out: dict[str, Any]) -> None:
        polls = list(self.polls)
        if "ctl_poll" in self.ctx:
            polls.append((self.ctx["ctl_poll"], self.ctx["A"]))
        for poll_id, owner in dict.fromkeys(polls):
            deleted = self.api.raw("DELETE", f"/polls/{poll_id}", params={"user_id": owner})
            out.setdefault("polls", []).append(deleted.status)

    def _delete_groups(self, out: dict[str, Any]) -> None:
        groups = list(self.groups) + ([self.ctx["ctl_group"]] if "ctl_group" in self.ctx else [])
        for group_id in dict.fromkeys(groups):
            deleted = self.api.raw("DELETE", f"/api/v2/usergroups/{group_id}")
            out.setdefault("user_groups", []).append(deleted.status)

    def _delete_channels(self, out: dict[str, Any]) -> None:
        cids = sorted(set(self.channels))
        if cids:
            res = self.api.raw(
                "POST", "/api/v2/chat/channels/delete", body={"cids": cids, "hard_delete": True}
            )
            out["channels_delete"] = res.status
            out["channels_task"] = self._wait_task(_dig(res.body, "task_id"))

    def _delete_users(self, out: dict[str, Any]) -> None:
        # Include any user whose ID contains this run's prefix (Stream prefixes
        # guest IDs with "guest-<uuid>-"), not only the IDs recorded here.
        listed = self.api.get(
            "/api/v2/users",
            params={"payload": json.dumps({"filter_conditions": {}, "limit": 100})},
        ).body
        found = [
            str(u.get("id"))
            for u in (listed.get("users", []) if isinstance(listed, dict) else [])
            if self.prefix in str(u.get("id"))
        ]
        out["users_found_by_prefix_not_recorded"] = len(set(found) - set(self.users))
        users = sorted(set(self.users) | set(found))
        if users:
            res = self.api.raw(
                "POST",
                "/api/v2/users/delete",
                body={
                    "user_ids": users,
                    "user": "hard",
                    "messages": "hard",
                    "conversations": "hard",
                    "calls": "hard",
                    "files": True,
                },
            )
            out["users_delete"] = res.status
            out["users_task"] = self._wait_task(_dig(res.body, "task_id"))

    def _delete_artifacts(self, out: dict[str, Any]) -> None:
        # Hard-deleting a user makes Stream create a system user
        # ("deleted-user-<app>-<hash>") that takes over references; it is an
        # artifact of this run's cleanup, so it is removed too.
        artifacts = self._artifact_users()
        out["artifact_users_found"] = len(artifacts)
        if artifacts:
            res = self.api.raw(
                "POST",
                "/api/v2/users/delete",
                body={
                    "user_ids": artifacts,
                    "user": "hard",
                    "messages": "hard",
                    "conversations": "hard",
                },
            )
            out["artifact_users_delete"] = res.status
            out["artifact_users_task"] = self._wait_task(_dig(res.body, "task_id"))

    def _artifact_users(self) -> list[str]:
        result = self.api.get(
            "/api/v2/users",
            params={"payload": json.dumps({"filter_conditions": {}, "limit": 100})},
        )
        marker = f"deleted-user-{self.credentials.app_id}-"
        found = []
        for user in result.body.get("users", []) if isinstance(result.body, dict) else []:
            created = user.get("created_at")
            if (
                str(user.get("id")).startswith(marker)
                and isinstance(created, int)
                and created >= self.started_ns
            ):
                found.append(str(user["id"]))
        return found

    def verify_clean(self) -> dict[str, Any]:
        snapshot = baseline.read_snapshot(self.api)
        users = [
            str(u.get("id"))
            for u in snapshot["users"].get("users", [])
            if PREFIX_ROOT in str(u.get("id"))
        ]
        channels = [
            str(c.get("channel", {}).get("cid")) for c in snapshot["channels"].get("channels", [])
        ]
        return {
            "remaining_proof_users": users,
            "remaining_channels": channels,
            "other_users_present": sum(
                1 for u in snapshot["users"].get("users", []) if PREFIX_ROOT not in str(u.get("id"))
            ),
            "dashboard_users_present": sum(
                1
                for u in snapshot["users"].get("users", [])
                if (u.get("custom") or {}).get("dashboard_user") is True
            ),
            "deleted_user_artifacts_remaining": sum(
                1
                for u in snapshot["users"].get("users", [])
                if str(u.get("id")).startswith(f"deleted-user-{self.credentials.app_id}-")
            ),
            **list_polls_and_groups(self.api),
        }

    def finish(self, *, cleanup: bool) -> list[str]:
        """End every run: restore journalled changes, clean up, verify the configuration.

        It runs after any stop, error, timeout or Ctrl-C. Nothing here raises
        except a second Ctrl-C; every problem is returned and kept in
        :attr:`post_run_problems`.
        """
        problems: list[str] = []
        for change in list(reversed(self.journal)):
            try:
                self._restore(change)
            except (RunStopped, GuardrailStop, Exception) as exc:
                problems.append(f"temporary change not restored: {self._text(exc)}")
        if cleanup:
            problems += cleanup_problems(self.cleanup())
        else:
            self.close_sessions()
            problems.append("cleanup skipped (a charge or limit signal stopped the run at once)")
        try:
            differences = configuration.verify(baseline.read_configuration(self.api))
        except (GuardrailStop, Exception) as exc:
            problems.append(f"configuration not verified after the run: {self._text(exc)}")
        else:
            problems += [f"configuration differs after the run: {d}" for d in differences]
        self.post_run_problems = problems
        return problems

    def results(self) -> dict[str, Any]:
        return {
            "prefix": self.prefix,
            "settings": self.settings,
            "token_claims": {k: self.redactor.value(v) for k, v in self.token_claims.items()},
            "checks": [asdict(c) for c in self.checks],
            "cases": [asdict(c) for c in self.case_results],
            "notes": self.notes,
            "stops": self.stops,
            "journal_not_restored": [c.description for c in self.journal],
            "post_run_problems": self.post_run_problems,
            "cleanup": self.cleanup_result,
            "usage": self.ledger.summary(),
            "ws_attempts": self.ws_attempts,
        }


def list_polls_and_groups(api: ServerApi) -> dict[str, Any]:
    """Polls and user groups present in the application (the proof's are the only ones).

    A listing Stream does not answer with 2xx is reported as not verified.
    """
    out: dict[str, Any] = {}
    polls = api.raw("POST", "/api/v2/polls/query", body={"filter": {}, "limit": 100})
    groups = api.get("/api/v2/usergroups", params={"limit": "100"})
    for key, result, items_key in (
        ("polls", polls, "polls"),
        ("user_groups", groups, "user_groups"),
    ):
        items = result.body.get(items_key) if isinstance(result.body, dict) else None
        if result.ok and isinstance(items, list):
            out[f"remaining_{key}"] = [str(i.get("id")) for i in items if isinstance(i, dict)]
        else:
            out[f"remaining_{key}"] = None
            out[f"{key}_listing"] = f"not verified: HTTP {result.status} code {result.code}"
    return out


def cleanup_problems(out: Mapping[str, Any]) -> list[str]:
    """Everything in a cleanup result that is not a verified, complete cleanup."""
    problems = [f"cleanup error: {e}" for e in out.get("errors") or []]
    for key in ("polls", "user_groups"):
        failed = [s for s in out.get(key) or [] if not (isinstance(s, int) and 200 <= s < 300)]
        if failed:
            problems.append(f"{key} delete statuses {failed}")
    for delete, task in (
        ("channels_delete", "channels_task"),
        ("users_delete", "users_task"),
        ("artifact_users_delete", "artifact_users_task"),
    ):
        if delete in out:
            status = out[delete]
            if not (isinstance(status, int) and 200 <= status < 300):
                problems.append(f"{delete} got {status}")
            if out.get(task) != "completed":
                problems.append(f"{task} is {out.get(task)!r}, not 'completed'")
    for key in (
        "remaining_proof_users",
        "remaining_channels",
        "remaining_polls",
        "remaining_user_groups",
    ):
        if key not in out:
            problems.append(f"{key}: not checked")
        elif out[key] is None:
            problems.append(f"{key}: {out.get(key.replace('remaining_', '') + '_listing')}")
        elif out[key]:
            problems.append(f"{key}: {out[key]}")
    if out.get("deleted_user_artifacts_remaining"):
        problems.append(
            f"deleted-user artifacts remaining: {out['deleted_user_artifacts_remaining']}"
        )
    return problems
