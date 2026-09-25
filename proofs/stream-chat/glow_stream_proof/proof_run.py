"""One live proof run against the development application.

Order: preflight (configuration and data checks) -> setup (synthetic users,
tokens, the two match channels, client sessions) -> authorized path ->
bypass matrix -> cleanup (hard delete of this run's users and channels, then
a check that none remain).
"""

from __future__ import annotations

import base64
import json
import secrets
import time
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

from getstream.models import ChannelInput, ChannelMemberRequest, MessageRequest, UserRequest

from . import baseline, configuration, matrix
from .app_send import AppSendService
from .client_bridge import ClientSession, Reply, client_environment
from .configuration import DEFAULT_TYPES, MATCH_TYPE
from .credentials import ServerCredentials
from .policy import MatchState
from .redaction import Redactor, describe_token, token_lifetime_seconds
from .server_api import ApiResult, ServerApi
from .usage import GuardrailStop, UsageLedger

PREFIX_ROOT = "p061i1-"
TOKEN_TTL_SECONDS = 900
CLEANUP_RESERVE = 60
EVENT_WAIT_MS = 2500
DESTRUCTIVE_PHASE = 70
T = MATCH_TYPE


class RunStopped(RuntimeError):
    """The run stopped on a stop condition; the reason is reported."""


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


def _status_code(reply: Reply) -> tuple[int | None, int | None]:
    status, code = reply.status, reply.code
    if code is None:
        for record in reversed(reply.requests):
            response = record.get("response")
            if isinstance(response, dict) and isinstance(response.get("code"), int):
                code = int(response["code"])
                break
    return status, code


def _observed(reply: Reply) -> str:
    status, code = _status_code(reply)
    if reply.ok:
        return f"{status if status is not None else 'ok'} (succeeded)"
    if status is None and code is None:
        return f"no HTTP status ({(reply.error or {}).get('kind')}: {reply.message})"
    return f"{status} / code {code}"


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

    # -- helpers ----------------------------------------------------------------

    def _check(self, check_id: str, description: str, ok: bool | None, evidence: str) -> None:
        result = "PASS" if ok else ("UNVERIFIED" if ok is None else "FAIL")
        self.checks.append(CheckResult(check_id, description, result, _generic(evidence, self.ctx)))

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
        return self.ledger.remaining("api_calls") > CLEANUP_RESERVE

    # -- preflight -------------------------------------------------------------

    def preflight(self) -> dict[str, Any]:
        snapshot = baseline.read_snapshot(self.api)
        problems = configuration.verify(snapshot)
        if problems:
            raise RunStopped("configuration is not in place: " + "; ".join(problems))
        app = snapshot["app"]["app"]
        self.settings = {k: app.get(k) for k in configuration.APP_SETTING_KEYS if k in app}
        foreign_users = []
        dashboard_users = 0
        for user in snapshot["users"].get("users", []):
            uid = str(user.get("id"))
            if uid.startswith(PREFIX_ROOT):
                foreign_users.append(f"leftover proof user {uid}")
                continue
            custom = user.get("custom") or {}
            if user.get("role") == "admin" and custom.get("dashboard_user") is True:
                dashboard_users += 1
                if self.accept_dashboard_user:
                    continue
            foreign_users.append("a user this proof did not create")
        channels = snapshot["channels"].get("channels", [])
        foreign_channels = [str(c.get("channel", {}).get("cid")) for c in channels]
        if foreign_users or foreign_channels:
            raise RunStopped(
                "application holds data this run did not create: "
                + "; ".join(foreign_users + [f"channel {c}" for c in foreign_channels])
            )
        return {"dashboard_users_present": dashboard_users, "configuration_problems": problems}

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
            self._check(
                f"AP4-{key}",
                f"client {key} connects over Stream's WebSocket and watches its own channel",
                reply.ok and watch.ok,
                f"connect {_observed(reply)}; watch {_observed(watch)}; "
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
            self._check(
                f"AP9-{key}",
                f"client {key} reads AB over REST and sees {other}'s server-sent message",
                reply.ok and found,
                f"query {_observed(reply)}; {other}'s text present {found}",
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

    def _events(self, key: str, wait_ms: int = EVENT_WAIT_MS) -> list[dict[str, Any]]:
        reply = self._send(self.sessions[key], "events", max_calls=0, wait_ms=wait_ms)
        events = (reply.data or {}).get("events") or []
        return [e for e in events if isinstance(e, dict)]

    def reconnect_check(self) -> None:
        try:
            self._reconnect_check()
        except GuardrailStop:
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
        self._check(
            "AP11",
            "client A disconnects, reconnects over the WebSocket and receives the next message",
            dis.ok and con.ok and watch.ok and bool(got),
            f"disconnect {_observed(dis)}; reconnect {_observed(con)}; watch {_observed(watch)}; "
            f"message.new received {bool(got)}",
        )

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
            except Exception as exc:  # recorded as it happened, never hidden
                result = self._result(
                    case,
                    "-",
                    f"harness error: {type(exc).__name__}: {exc}",
                    "-",
                    matrix.Verdict(matrix.INCONCLUSIVE, "harness error"),
                )
            self.case_results.append(result)
            if progress is not None:
                progress()
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

    def _failing_record(self, reply: Reply) -> dict[str, Any] | None:
        for record in reversed(reply.requests):
            status = record.get("status")
            if isinstance(status, int) and status >= 400:
                return record
        return reply.last_request

    def _replay(self, case: matrix.Case, reply: Reply) -> tuple[bool, str, Any]:
        record = self._failing_record(reply)
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
                undone = self._server(undo)
                undo_notes.append(f"undo {undo.method} {undone.status}")
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
        if not case.feature_override:
            return self._evaluate_case(case)
        assert case.step is not None
        path = f"/channels/{T}/{self.ctx['AB']}"
        override = dict(case.feature_override)
        on = self.api.raw("PATCH", path, body={"set": {"config_overrides": override}})
        try:
            result = self._evaluate_case(case)
        finally:
            off = self.api.raw("PATCH", path, body={"set": {"config_overrides": {}}})
        production = self._step(case.step)
        result.detail["feature_override"] = {
            "features": override,
            "set_status": on.status,
            "removed_status": off.status,
        }
        result.detail["production_config_observed"] = _observed(production)
        result.observed = (
            f"feature on: {result.observed}; feature off (production): {_observed(production)}"
        )
        if not on.ok:
            result.verdict = matrix.INCONCLUSIVE
            result.reason = f"could not enable {override} on AB ({on.status})"
        if production.ok:
            result.verdict = matrix.FAIL
            result.reason = "succeeded under the production configuration"
            self._undo_client_success(case)
        return result

    def _evaluate_case(self, case: matrix.Case) -> CaseResult:
        assert case.step is not None
        reply = self._step(case.step)
        status, code = _status_code(reply)
        outcome = matrix.classify(status, code) if not reply.ok else "success"
        request = _request_line(self._failing_record(reply), self.ctx)
        leaks = matrix.find_terms(
            _responses(reply) + [reply.data], matrix.substitute(list(case.leak_terms), self.ctx)
        )
        control_ok: bool
        control_desc: str
        control_body: Any = None
        control = case.control
        if control.kind == "server-replay":
            control_ok, control_desc, control_body = self._replay(case, reply)
        elif control.kind == "session":
            assert control.session is not None
            creply = self._step(case.step, control.session)
            control_ok = creply.ok
            control_body = _responses(creply)
            control_desc = f"{control.session}: {_observed(creply)}"
        elif control.kind == "server-upload":
            control_ok, control_desc = self._upload_control(case)
        else:
            control_ok, control_desc = False, "no control"
        self.control_ok[case.id] = control_ok
        detail: dict[str, Any] = {}
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
        if reply.ok and case.expect == "refused":
            detail["client_success_note"] = "client action succeeded; see verdict"
            self._undo_client_success(case)
        return self._result(case, request, _observed(reply), control_desc, verdict, detail)

    def _undo_client_success(self, case: matrix.Case) -> None:
        # A bypass that changed state is reversed with the case's own undo requests.
        for undo in case.control.undo:
            self._server(undo)

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
        control = self._send(self.sessions["A"], "call", max_calls=2, **self._query_ab_step())
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        verdict = matrix.refused_verdict(outcome, control.ok)
        detail = {"token_used": self._describe_bad(kind, token), "set_user": set_reply.ok}
        return self._result(
            case,
            _request_line(reply.last_request, self.ctx),
            _observed(reply),
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
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        control_ok = bool(control_reply and control_reply.ok)
        verdict = matrix.refused_verdict(outcome, control_ok)
        me = ((reply.data or {}).get("me") or {}) if reply.ok else {}
        connected_as = me.get("id") if isinstance(me, dict) else None
        if kind == "T4" and reply.ok:
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
            _observed(reply),
            f"{control_label}: {_observed(control_reply) if control_reply else 'not run'}",
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
                control = self._send(self.sessions["X"], "call", max_calls=2, **step)
                status, code = _status_code(reply)
                outcome = "success" if reply.ok else matrix.classify(status, code)
                verdict = matrix.refused_verdict(outcome, control.ok)
                leaks = matrix.find_terms(_responses(reply), [self.ctx["xd_text"]])
                if leaks:
                    verdict = matrix.Verdict(matrix.FAIL, "response disclosed XD's message")
                return self._result(
                    case,
                    _request_line(reply.last_request, self.ctx) + " ?user_id={X}",
                    _observed(reply),
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
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        if outcome in ("auth", "permission"):
            verdict = matrix.Verdict(matrix.HOLDS, f"{outcome} error")
        elif outcome == "success" and a_total != b_total:
            if claim_total == a_total:
                verdict = matrix.Verdict(
                    matrix.HOLDS_IGNORED, "claim ignored: the response is A's own unread count"
                )
            elif claim_total == b_total:
                verdict = matrix.Verdict(matrix.FAIL, "the response is B's unread count")
            else:
                verdict = matrix.Verdict(matrix.INCONCLUSIVE, "count matches neither user")
        else:
            verdict = matrix.Verdict(matrix.INCONCLUSIVE, "A's and B's counts do not differ")
        return self._result(
            case,
            _request_line(reply.last_request, self.ctx) + " ?user_id={B}",
            _observed(reply),
            f"A's own total {a_total}; B's own total {b_total}",
            verdict,
            {"claimed_total": claim_total},
        )

    def _proc_guest_create(self, case: matrix.Case, _arg: str) -> CaseResult:
        guest_id = f"{self.prefix}-guest"
        self.ledger.reserve("users")
        session = self._session("guest-create", None, max_api_calls=10)
        try:
            reply = self._send(
                session, "guest", max_calls=3, user={"id": guest_id, "name": "Synthetic guest"}
            )
            if reply.ok:
                self.users.append(guest_id)
                self._send(session, "disconnect", max_calls=2)
        finally:
            session.close()
        created = (reply.data or {}).get("me", {}) if reply.ok else {}
        if isinstance(created, dict) and created.get("id"):
            self.users.append(str(created["id"]))
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        exists_after = bool(self._server_user(guest_id).get("id"))
        if not reply.ok and not exists_after:
            self.ledger.release("users")  # refused: no user was created
        elif exists_after and guest_id not in self.users:
            self.users.append(guest_id)
        self.ledger.reserve("users")
        server_guest = f"{self.prefix}-sguest"
        result, token = self.api.create_guest({"id": server_guest, "name": "Synthetic guest"})
        if not result.ok:
            self.ledger.release("users")
        if result.ok:
            gid = _dig(result.body, "user.id")
            self.ctx["guest_id"] = str(gid) if gid else server_guest
            self.users.append(self.ctx["guest_id"])
            if token:
                self._tokens["guest"] = token
                self.token_claims["guest"] = describe_token(token)
        verdict = matrix.refused_verdict(outcome, result.ok)
        return self._result(
            case,
            _request_line(reply.last_request, self.ctx),
            _observed(reply),
            f"server POST /guest -> {result.status}",
            verdict,
            {
                "server_guest_role": _dig(result.body, "user.role"),
                "client_guest_user_exists_after": exists_after,
                "client_error_message": reply.message,
            },
        )

    def _read_probe(self, suffix: str) -> tuple[dict[str, Any], str | None]:
        """The request a guest or anonymous client makes, and the session that controls it."""
        if suffix == "read-ab":
            return self._query_ab_step(), "A"
        if suffix == "channels":
            return {
                "target": "client",
                "method": "queryChannels",
                "args": [{"type": {"$in": [T, *DEFAULT_TYPES]}}, [], matrix.READ_OPTIONS],
            }, "A"
        if suffix == "users":
            return {
                "target": "client",
                "method": "queryUsers",
                "args": [{"id": {"$in": [self.ctx[k] for k in ("A", "B", "X", "D")]}}],
            }, None
        return {"target": "client", "method": "getMessage", "args": [self.ctx["m_x"]]}, "X"

    def _proc_guest_role(self, case: matrix.Case, suffix: str) -> CaseResult:
        token = self._tokens.get("guest")
        if token is None:
            return self._result(
                case,
                "-",
                "not run: no server-issued guest token",
                "-",
                matrix.Verdict(matrix.INCONCLUSIVE, "guest control did not produce a token"),
            )
        session = self.sessions.get("guest")
        if session is None:
            session = self._session("guest", token, max_api_calls=20)
            self._send(session, "set_rest_user", max_calls=1, user_id=self.ctx["guest_id"])
        return self._probe_case(case, session, suffix)

    def _proc_anonymous(self, case: matrix.Case, suffix: str) -> CaseResult:
        session = self.sessions.get("anonymous")
        if session is None:
            session = self._session("anonymous", None, max_api_calls=20)
            connect = self._send(session, "anonymous", max_calls=3)
            self.connect_replies["anonymous"] = connect
            self.notes.append(f"anonymous connect: {_observed(connect)}")
        return self._probe_case(case, session, suffix)

    def _probe_case(self, case: matrix.Case, session: ClientSession, suffix: str) -> CaseResult:
        step, control_session = self._read_probe(suffix)
        reply = self._send(session, "call", max_calls=2, **step)
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        leaks = matrix.find_terms(
            _responses(reply), matrix.substitute(list(case.leak_terms), self.ctx)
        )
        if control_session is not None:
            control = self._send(self.sessions[control_session], "call", max_calls=2, **step)
            control_ok, control_body = control.ok, _responses(control)
            control_desc = f"{control_session}: {_observed(control)}"
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
            _request_line(self._failing_record(reply), self.ctx),
            _observed(reply),
            control_desc + f"; control found target data {found}",
            verdict,
            {"learned": self._learned(reply)},
        )

    def _proc_poll_vote(self, case: matrix.Case, _arg: str) -> CaseResult:
        poll = self.api.raw(
            "POST",
            "/polls",
            body={"name": "server poll", "options": [{"text": "yes"}], "user_id": self.ctx["B"]},
        )
        poll_id = _dig(poll.body, "poll.id")
        option_id = None
        options = _dig(poll.body, "poll.options")
        if isinstance(options, list) and options and isinstance(options[0], dict):
            option_id = options[0].get("id")
        if not poll.ok or not poll_id:
            return self._result(
                case,
                "-",
                "not set up",
                f"server POST /polls -> {poll.status}/{poll.code}",
                matrix.Verdict(matrix.INCONCLUSIVE, "server could not create a poll"),
            )
        self.polls.append((str(poll_id), self.ctx["B"]))
        msg = self.api.raw(
            "POST",
            f"/channels/{T}/{self.ctx['AB']}/message",
            body={"message": {"text": "poll", "poll_id": poll_id, "user_id": self.ctx["B"]}},
        )
        message_id = _dig(msg.body, "message.id")
        if not msg.ok or not message_id:
            return self._result(
                case,
                "-",
                "not set up",
                f"server poll message -> {msg.status} / code {msg.code} ({msg.message})",
                matrix.Verdict(
                    matrix.INCONCLUSIVE,
                    "server could not attach the poll to a message in AB (polls are off)",
                ),
            )
        reply = self._send(
            self.sessions["A"],
            "call",
            target="client",
            method="castPollVote",
            args=[message_id, poll_id, {"option_id": option_id}],
        )
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        record = self._failing_record(reply)
        control_ok = False
        control_desc = "no control"
        if record is not None:
            body = matrix.deep_merge(record.get("body"), {"user_id": self.ctx["A"]})
            result = self.api.raw("POST", "/" + str(record.get("path")).lstrip("/"), body=body)
            control_ok = result.ok
            control_desc = f"server replay POST -> {result.status}"
        return self._result(
            case,
            _request_line(record, self.ctx),
            _observed(reply),
            control_desc,
            matrix.refused_verdict(outcome, control_ok),
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
        stored = self._server_user(self.ctx["A"])
        custom = stored.get("custom") or {}
        applied = (
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
        self.api.raw(
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
        if applied:
            self.notes.append("S14: profile fields set on connect reached stored state; restored")
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        verdict = matrix.not_effective_verdict(applied, outcome, control_ok)
        return self._result(
            case,
            "WebSocket /connect (user object with name, image, custom field)",
            _observed(reply),
            f"server PATCH /users -> {control.status}; name applied {control_ok}",
            verdict,
            {
                "stored_name_is_original": stored.get("name") == self.ctx["A_name"],
                "stored_has_image": bool(stored.get("image")),
                "stored_custom_keys": sorted(custom.keys()),
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
        stored = self._server_user(self.ctx["A"])
        applied = stored.get("role") != "user"
        if applied:
            self.api.raw(
                "PATCH", "/users", body={"users": [{"id": self.ctx["A"], "set": {"role": "user"}}]}
            )
            self.notes.append("E5: role on connect reached stored state; restored to user")
        control_ok = self.control_ok.get("E1", False)
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        verdict = matrix.not_effective_verdict(applied, outcome, control_ok)
        return self._result(
            case,
            "WebSocket /connect (user object with role admin)",
            _observed(reply),
            f"E1 server replay succeeded: {control_ok}",
            verdict,
            {
                "stored_role": stored.get("role"),
                "connect_me_role": ((reply.data or {}).get("me") or {}).get("role"),
            },
        )

    def _payload_case(
        self, case: matrix.Case, step: dict[str, Any], event_types: tuple[str, ...], marker: str
    ) -> CaseResult:
        self._events("B", wait_ms=0)
        reply = self._send(self.sessions["A"], "call", max_calls=2, **step)
        events = [e for e in self._events("B") if e.get("type") in event_types]
        carried = [e for e in events if matrix.find_terms(e, [marker])]
        service = AppSendService(self.state, self, T)
        probe = service.send(self.ctx["A"], self.ctx["AB"], f"listener probe {self.prefix}")
        listening = any(
            e.get("type") == "message.new" and _dig(e, "message.id") == probe.message_id
            for e in self._events("B")
        )
        status, code = _status_code(reply)
        outcome = "success" if reply.ok else matrix.classify(status, code)
        keys = sorted({k for e in events for k in e.keys()})
        if carried:
            verdict = matrix.Verdict(matrix.FAIL, "B received the free-text field")
        elif not listening:
            verdict = matrix.Verdict(matrix.INCONCLUSIVE, "B's listener did not see the probe")
        elif events:
            verdict = matrix.Verdict(matrix.HOLDS, "delivered without the free-text field")
        elif outcome == "success":
            verdict = matrix.Verdict(matrix.HOLDS_IGNORED, "accepted; B received no such event")
        else:
            # This case asks what reaches B: nothing did, whatever the refusal code.
            verdict = matrix.Verdict(
                matrix.HOLDS, f"refused ({outcome}); nothing delivered to B, who was listening"
            )
        return self._result(
            case,
            _request_line(reply.last_request, self.ctx),
            _observed(reply),
            f"B listening (received a probe message): {listening}",
            verdict,
            {
                "event_types": sorted({str(e.get("type")) for e in events}),
                "event_keys": keys,
                "sample": self._event_sample(events),
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
        for _ in range(30):
            result = self.api.get(f"/api/v2/tasks/{task_id}")
            status = str(result.body.get("status")) if isinstance(result.body, dict) else "?"
            if status in ("completed", "failed"):
                return status
            time.sleep(2)
        return status

    def cleanup(self) -> dict[str, Any]:
        self.close_sessions()
        out: dict[str, Any] = {}
        for poll_id, owner in self.polls + (
            [(self.ctx["ctl_poll"], self.ctx["A"])] if "ctl_poll" in self.ctx else []
        ):
            deleted = self.api.raw("DELETE", f"/polls/{poll_id}", params={"user_id": owner})
            out.setdefault("polls", []).append(deleted.status)
        if "ctl_group" in self.ctx:
            deleted = self.api.raw("DELETE", f"/api/v2/usergroups/{self.ctx['ctl_group']}")
            out["user_group"] = deleted.status
        cids = sorted(set(self.channels))
        if cids:
            res = self.api.raw(
                "POST", "/api/v2/chat/channels/delete", body={"cids": cids, "hard_delete": True}
            )
            out["channels_delete"] = res.status
            out["channels_task"] = self._wait_task(_dig(res.body, "task_id"))
        users = sorted(set(self.users))
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
        out.update(self.verify_clean())
        self.cleanup_result = out
        return out

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
            if str(u.get("id")).startswith(PREFIX_ROOT)
        ]
        channels = [
            str(c.get("channel", {}).get("cid")) for c in snapshot["channels"].get("channels", [])
        ]
        return {
            "remaining_proof_users": users,
            "remaining_channels": channels,
            "other_users_present": sum(
                1
                for u in snapshot["users"].get("users", [])
                if not str(u.get("id")).startswith(PREFIX_ROOT)
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
        }

    def results(self) -> dict[str, Any]:
        return {
            "prefix": self.prefix,
            "settings": self.settings,
            "token_claims": {k: self.redactor.value(v) for k, v in self.token_claims.items()},
            "checks": [asdict(c) for c in self.checks],
            "cases": [asdict(c) for c in self.case_results],
            "notes": self.notes,
            "cleanup": self.cleanup_result,
            "usage": self.ledger.summary(),
            "ws_attempts": self.ws_attempts,
        }
