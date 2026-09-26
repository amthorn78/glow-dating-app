"""Fakes for driving a proof run offline: no network, no Stream, no Node.

``FakeServer`` stands in for :class:`~glow_stream_proof.server_api.ServerApi`
and keeps just enough state (app settings, the match type's features, AB's
overrides, users and channels) for the harness's restores, re-reads and final
configuration check. ``FakeSession`` stands in for a client session; tests
script it with ``behaviour`` callables.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import jwt

from glow_stream_proof import configuration, proof_run
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.credentials import ServerCredentials
from glow_stream_proof.proof_run import ProofRun
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import UsageLedger
from tests.test_configuration import configured, snapshot

SECRET = "simulation-secret-for-offline-tests-only"
PREFIX = "p061i1-simulated"

Handler = Callable[[str, str, Any, dict[str, str] | None], ApiResult | None]


def ok(method: str, path: str, body: Any, status: int = 201) -> ApiResult:
    return ApiResult(method, path, status, None, None, body)


def error(method: str, path: str, status: int, code: int, message: str = "no") -> ApiResult:
    return ApiResult(method, path, status, code, message, {"code": code, "message": message})


def configured_state() -> dict[str, Any]:
    """An application in the proof's target configuration (``configuration.verify`` is [])."""
    state = configured(snapshot())
    state["app"]["app"].update(configuration.REQUIRED_APP_SETTINGS)
    return state


@dataclass
class FakeServer:
    ledger: UsageLedger
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    members: dict[str, list[str]] = field(default_factory=dict)
    overrides: dict[str, dict[str, Any]] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=configured_state)
    calls: list[tuple[str, str, Any]] = field(default_factory=list)
    handlers: list[Handler] = field(default_factory=list)
    task_status: str = "completed"
    sent: int = 0
    # Called with (channel id, message id) for every server-side send.
    on_send: Callable[[str, str], None] | None = None
    # How a channel re-read looks: whether its config shows the channel's
    # overrides, and whether it carries grants at all.
    merge_overrides: bool = True
    config_has_grants: bool = True

    def __post_init__(self) -> None:
        self.sdk = SimpleNamespace(
            upsert_users=self._upsert,
            chat=SimpleNamespace(
                get_or_create_channel=self._channel, send_message=self._send_message
            ),
            create_token=self._token,
        )

    # -- the typed SDK calls the harness makes ------------------------------------

    def _count(self) -> None:
        self.ledger.reserve("api_calls")

    def _upsert(self, *users: Any) -> None:
        self._count()
        for u in users:
            self.users[u.id] = {"id": u.id, "role": u.role, "name": u.name, "created_at": 0}

    def _channel(self, type: str, id: str, data: Any) -> None:
        self._count()
        self.members[id] = [m.user_id for m in data.members]

    def _send_message(self, type: str, id: str, message: Any) -> Any:
        self._count()
        self.sent += 1
        if self.on_send is not None:
            self.on_send(id, f"m-{self.sent}")
        return SimpleNamespace(data=SimpleNamespace(message=SimpleNamespace(id=f"m-{self.sent}")))

    @staticmethod
    def _token(user_id: str, expiration: int) -> str:
        return jwt.encode({"user_id": user_id, "iat": 0, "exp": expiration}, SECRET, "HS256")

    # -- raw requests -------------------------------------------------------------

    @property
    def app(self) -> dict[str, Any]:
        app: dict[str, Any] = self.state["app"]["app"]
        return app

    @property
    def match_type(self) -> dict[str, Any]:
        types: dict[str, Any] = self.state["channel_types"]["channel_types"]
        match: dict[str, Any] = types[configuration.MATCH_TYPE]
        return match

    def effective_channel(self, channel_id: str) -> dict[str, Any]:
        config = {k: v for k, v in configuration.MATCH_FEATURES.items() if k != "commands"}
        grants = {"channel_member": list(configuration.MATCH_MEMBER_GRANTS)}
        for key, value in (
            self.overrides.get(channel_id, {}).items() if self.merge_overrides else ()
        ):
            if key == "grants":
                for role, extra in value.items():
                    grants[role] = sorted(set(grants.get(role, [])) | set(extra))
            else:
                config[key] = value
        if self.config_has_grants:
            config["grants"] = grants
        return {"cid": f"{configuration.MATCH_TYPE}:{channel_id}", "config": config}

    def raw(
        self, method: str, path: str, *, body: Any = None, params: dict[str, str] | None = None
    ) -> ApiResult:
        self._count()
        self.calls.append((method, path, body))
        for handler in self.handlers:
            result = handler(method, path, body, params)
            if result is not None:
                return result
        return self._default(method, path, body, params)

    def _default(
        self, method: str, path: str, body: Any, params: dict[str, str] | None
    ) -> ApiResult:
        match_path = f"/api/v2/chat/channeltypes/{configuration.MATCH_TYPE}"
        if path == "/api/v2/users" and method == "GET":
            payload = json.loads((params or {}).get("payload", "{}"))
            cond = payload.get("filter_conditions", {}).get("id", {})
            wanted = cond.get("$in") or ([cond["$eq"]] if "$eq" in cond else None)
            users = [u for uid, u in self.users.items() if wanted is None or uid in wanted]
            return ok(method, path, {"users": users}, 200)
        if path == "/api/v2/chat/members":
            payload = json.loads((params or {}).get("payload", "{}"))
            ids = self.members.get(payload["id"], [])
            return ok(method, path, {"members": [{"user_id": i} for i in ids]}, 200)
        if path == "/api/v2/chat/channels":
            cid = ((body or {}).get("filter_conditions") or {}).get("cid")
            if cid:
                channel = self.effective_channel(str(cid).split(":", 1)[1])
                return ok(method, path, {"channels": [{"channel": channel}]}, 201)
            return ok(method, path, {"channels": []}, 201)
        if path.startswith("/channels/glow-match/") and method == "PATCH" and "/member" not in path:
            channel_id = path.split("/")[3]
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if overrides is not None:
                self.overrides[channel_id] = dict(overrides)
            return ok(method, path, {"channel": self.effective_channel(channel_id)}, 200)
        if path.startswith("/api/v2/tasks/"):
            return ok(method, path, {"status": self.task_status}, 200)
        if path == "/api/v2/users/delete":
            for user_id in (body or {}).get("user_ids", []):
                self.users.pop(user_id, None)
            return ok(method, path, {"task_id": "t1"})
        if path.endswith("/delete"):
            return ok(method, path, {"task_id": "t1"})
        if path == "/polls" and method == "POST":
            return ok(method, path, {"poll": {"id": "p1", "options": [{"id": "o1"}]}})
        if path == "/api/v2/polls/query":
            return ok(method, path, {"polls": []}, 201)
        if path == "/api/v2/usergroups" and method == "GET":
            return ok(method, path, {"user_groups": []}, 200)
        if method == "DELETE":
            return ok(method, path, {}, 200)
        if path.endswith("/message"):
            return ok(method, path, {"message": {"id": "m-poll"}})
        if path == match_path and method == "GET":
            return ok(method, path, copy.deepcopy(self.match_type), 200)
        if path == match_path and method == "PUT":
            for key, value in (body or {}).items():
                if key in configuration.MATCH_FEATURES:
                    self.match_type[key] = value
            return ok(method, path, copy.deepcopy(self.match_type), 201)
        if path == "/api/v2/app" and method == "GET":
            return ok(method, path, {"app": copy.deepcopy(self.app)}, 200)
        if path == "/api/v2/app" and method == "PATCH":
            for key, value in (body or {}).items():
                if key != "grants":
                    self.app[key] = value
            return ok(method, path, {}, 201)
        if path == "/api/v2/chat/channeltypes":
            return ok(method, path, copy.deepcopy(self.state["channel_types"]), 200)
        if path == "/api/v2/roles":
            return ok(method, path, {"roles": []}, 200)
        return ok(method, path, {"file": "https://cdn.invalid/f"})

    def get(self, path: str, params: dict[str, str] | None = None) -> ApiResult:
        return self.raw("GET", path, params=params)

    @staticmethod
    def require(result: ApiResult) -> ApiResult:
        return result

    def user_token(self, user_id: str, ttl_seconds: int) -> str:
        return jwt.encode({"user_id": user_id, "iat": 0, "exp": ttl_seconds}, SECRET, "HS256")

    def expired_user_token(self, user_id: str) -> str:
        return jwt.encode({"user_id": user_id, "iat": 0, "exp": 1}, SECRET, "HS256")

    def raw_multipart(self, path: str, **_kwargs: Any) -> ApiResult:
        self._count()
        return ok("POST", path, {"file": "https://cdn.invalid/f"})


QUERY_PATH = "/channels/glow-match/x/query"


def record(
    status: int | None, response: Any = None, *, path: str = QUERY_PATH, method: str = "POST"
) -> dict[str, Any]:
    return {
        "method": method,
        "path": path,
        "params": {"user_id": "u", "api_key": "k"},
        "body": {"data": {"members": ["a"]}},
        "status": status,
        "response": response,
    }


def http_reply(
    status: int, code: int | None = None, response: Any = None, path: str = QUERY_PATH
) -> Reply:
    """A reply whose only request got ``status`` (and Stream ``code``) from Stream."""
    body = response if response is not None else ({"code": code} if code is not None else {})
    rec = record(status, body, path=path)
    if status < 300:
        return Reply(True, {}, None, [rec], api_calls=1)
    error = {"status": status, "code": code, "message": "denied", "kind": "api"}
    return Reply(False, None, error, [rec], api_calls=1)


def local_error(message: str = "local SDK error", status: int | None = 403) -> Reply:
    """The SDK failed locally: an error that looks like a refusal, but no request."""
    return Reply(False, None, {"status": status, "code": 17, "message": message, "kind": "error"})


def ws_refused(status: int = 403, code: int = 17, kind: str = "ws-api") -> Reply:
    return Reply(False, None, {"status": status, "code": code, "message": "ws no", "kind": kind})


Behaviour = Callable[["FakeSession", str, dict[str, Any]], Reply | None]


class FakeSession:
    """A client refused everything except connecting and reading its own events.

    ``X`` succeeds at every call (it is the authorized member of XD). A test's
    ``behaviour`` is asked first and may return a reply of its own.
    """

    def __init__(self, label: str, behaviour: Behaviour | None = None) -> None:
        self.label = label
        self.behaviour = behaviour
        self.pending_events: list[dict[str, Any]] = []
        self.sent: list[tuple[str, dict[str, Any]]] = []

    def send(self, op: str, **params: Any) -> Reply:
        self.sent.append((op, params))
        if self.behaviour is not None:
            scripted = self.behaviour(self, op, params)
            if scripted is not None:
                return scripted
        if op in ("connect", "disconnect", "set_rest_user", "anonymous"):
            user = params.get("user") or {"id": "anon"}
            return Reply(True, {"me": {"id": user["id"], "role": "user"}}, None)
        if op == "events":
            events, self.pending_events = self.pending_events, []
            return Reply(True, {"events": events}, None)
        if op == "guest":
            post_status = 201 if self.label == "guest" else 403
            stored = f"guest-0000-{params['user']['id']}"  # Stream prefixes guest IDs
            response: dict[str, Any] = (
                {"user": {"id": stored, "role": "guest"}}
                if post_status == 201
                else {"code": 17, "message": "guest user creation is disabled"}
            )
            guest_post = record(post_status, response, path="/guest")
            # The lockdown refuses the connect setGuestUser makes after its POST /guest
            # (the I1 review, finding 6), so the control's guest has no session.
            return Reply(
                False,
                None,
                {"status": 403, "code": 17, "message": "no", "kind": "ws-api"},
                [guest_post],
                api_calls=1,
            )
        if self.label == "X":
            return Reply(True, {}, None, [record(201, {"channels": []})], api_calls=1)
        return http_reply(403, 17)

    def close(self) -> None:
        pass


def make_run(
    server: FakeServer | None = None,
    behaviours: dict[str, Behaviour] | None = None,
    *,
    ledger: UsageLedger | None = None,
) -> tuple[ProofRun, FakeServer]:
    ledger = ledger or (server.ledger if server else UsageLedger())
    server = server or FakeServer(ledger)
    run = ProofRun(
        ServerCredentials("1729640", "k", SECRET),
        server,  # type: ignore[arg-type]
        ledger,
        Redactor([SECRET]),
        {},
        prefix=PREFIX,
        accept_dashboard_user=True,
    )
    sessions: dict[str, Any] = run.sessions
    behaviours = behaviours or {}

    def fake_session(label: str, token: str | None, **_: Any) -> Any:
        return sessions.setdefault(label, FakeSession(label, behaviours.get(label)))

    def deliver(channel_id: str, message_id: str) -> None:
        # Stream delivers a server-sent message to the channel's connected members.
        labels = ("A", "B") if channel_id.endswith("-ch-ab") else ("X",)
        for label in labels:
            session = sessions.get(label)
            if isinstance(session, FakeSession):
                session.pending_events.append(
                    {
                        "type": "message.new",
                        "cid": f"{configuration.MATCH_TYPE}:{channel_id}",
                        "message": {"id": message_id},
                    }
                )

    if server.on_send is None:
        server.on_send = deliver
    run._session = fake_session  # type: ignore[method-assign]
    return run, server


def set_up(run: ProofRun) -> None:
    """Setup and the authorized path, with the settle time removed."""
    run.setup()
    run.authorized_path()


class NoSettle:
    """Context manager: remove the harness's settle waits for a test."""

    def __enter__(self) -> None:
        self._saved = (
            proof_run.TYPE_CHANGE_SETTLE_SECONDS,
            proof_run.TASK_POLL_INTERVAL_SECONDS,
            proof_run.RESTORE_RETRY_SECONDS,
        )
        proof_run.TYPE_CHANGE_SETTLE_SECONDS = 0
        proof_run.TASK_POLL_INTERVAL_SECONDS = 0
        proof_run.RESTORE_RETRY_SECONDS = 0

    def __exit__(self, *_exc: object) -> None:
        (
            proof_run.TYPE_CHANGE_SETTLE_SECONDS,
            proof_run.TASK_POLL_INTERVAL_SECONDS,
            proof_run.RESTORE_RETRY_SECONDS,
        ) = self._saved
