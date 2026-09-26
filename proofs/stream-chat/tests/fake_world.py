"""A stand-in for Stream in P06.1-I2a's families: no network, no Stream, no Node.

``World`` answers the server requests the families send (on their own channels
only; anything else falls through to ``FakeServer``) and scripts the families'
client sessions. Its behaviour is a plausible model, not Stream's: each knob is a
behaviour the live run records, so tests can drive every branch of the rules.

``FakeClock`` replaces ``time`` in :mod:`glow_stream_proof.mechanisms`, so that
the revocation's wait costs nothing and token ``iat`` claims follow it.
"""

from __future__ import annotations

import calendar
import json
import time
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import jwt

from glow_stream_proof import configuration, mechanisms
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.proof_run import ProofRun
from tests.fakes import SECRET, FakeServer, FakeSession, error, ok, record, ws_refused

T = configuration.MATCH_TYPE


class FakeClock:
    """``time`` for the mechanisms module: ``sleep`` advances it at once."""

    def __init__(self) -> None:
        self.now = time.time()

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += max(0.0, seconds)

    def __enter__(self) -> FakeClock:
        self._saved = getattr(mechanisms, "time")  # noqa: B009
        setattr(mechanisms, "time", self)  # noqa: B010
        return self

    def __exit__(self, *_exc: object) -> None:
        setattr(mechanisms, "time", self._saved)  # noqa: B010


def token_for(user_id: str, now: float, ttl: int = 900) -> str:
    """As the server SDK issues it: ``iat`` back-dated by 5 s."""
    iat = int(now) - 5
    return jwt.encode({"user_id": user_id, "iat": iat, "exp": iat + 5 + ttl}, SECRET, "HS256")


@dataclass
class World:
    server: FakeServer
    run: ProofRun
    clock: FakeClock
    # Knobs: what "Stream" does. The defaults give each outcome at least once.
    removed_keeps_events: bool = False
    banned_can_read: bool = True
    revoked_connection_open: bool = True
    client_can_show: bool = True
    hard_delete_removes_conversations: bool = True
    server_send_refused_when_frozen: bool = False
    # State
    frozen: set[str] = field(default_factory=set)
    hidden: dict[str, set[str]] = field(default_factory=dict)
    banned: dict[str, set[str]] = field(default_factory=dict)
    revoked: dict[str, int] = field(default_factory=dict)
    deactivated: set[str] = field(default_factory=set)
    deleted: set[str] = field(default_factory=set)
    messages: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    member_custom: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    channel_custom: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Channel -> the session labels watching it.
    watching: dict[str, set[str]] = field(default_factory=dict)
    # Label -> the token the session started with.
    tokens: dict[str, str] = field(default_factory=dict)
    counter: int = 0

    def install(self) -> World:
        self.server.handlers.insert(0, self.handle)
        self.server.user_token = self.user_token  # type: ignore[method-assign]
        typed_send = self.server.sdk.chat.send_message

        def send_message(type: str, id: str, message: Any) -> Any:
            # A typed send to a family channel is stored like a raw one.
            if self.family_channel(id):
                body = {"message": {"text": message.text, "user_id": message.user_id}}
                result = self.server.raw("POST", f"/channels/{type}/{id}/message", body=body)
                if not result.ok:
                    raise RuntimeError(f"send refused: {result.status}")
                return SimpleNamespace(
                    data=SimpleNamespace(message=SimpleNamespace(id=result.body["message"]["id"]))
                )
            return typed_send(type=type, id=id, message=message)

        self.server.sdk.chat.send_message = send_message
        return self

    def user_token(self, user_id: str, ttl_seconds: int) -> str:
        return token_for(user_id, self.clock.time(), ttl_seconds)

    # -- helpers --

    @staticmethod
    def family_channel(channel_id: str) -> bool:
        return any(channel_id.endswith(f"-ch-{key}") for key in mechanisms.MECHANISMS)

    def members(self, channel_id: str) -> list[str]:
        return self.server.members.get(channel_id, [])

    def label_user(self, label: str) -> str | None:
        key = label.split("-", 1)[0]
        return self.run.ctx.get(key)

    def next_id(self, kind: str) -> str:
        self.counter += 1
        return f"{kind}-{self.counter}"

    def deliver(self, channel_id: str, event: dict[str, Any], *, only: str | None = None) -> None:
        """Deliver ``event`` to the sessions watching the channel that may receive it."""
        for label in sorted(self.watching.get(channel_id, set())):
            uid = self.label_user(label)
            if uid is None or (only is not None and uid != only):
                continue
            if not self.receives(label, uid, channel_id):
                continue
            session = self.run.sessions.get(label)
            if isinstance(session, FakeSession):
                session.pending_events.append(json.loads(json.dumps(event)))

    def receives(self, label: str, uid: str, channel_id: str) -> bool:
        if uid in self.deleted or uid in self.deactivated:
            return False
        if uid in self.revoked and not self.revoked_connection_open:
            return self.token_ok(label, uid)
        if uid not in self.members(channel_id):
            return self.removed_keeps_events
        return True

    def token_ok(self, label: str, uid: str) -> bool:
        token = self.tokens.get(label)
        if token is None:
            return True
        iat = jwt.decode(token, options={"verify_signature": False}).get("iat")
        return not (uid in self.revoked and isinstance(iat, int) and iat < self.revoked[uid])

    def auth_error(self, label: str, uid: str) -> Reply | None:
        if uid in self.deleted:
            return self.reply(401, 5)
        if uid in self.deactivated:
            return self.reply(401, 5)
        if not self.token_ok(label, uid):
            return self.reply(401, 40)
        return None

    @staticmethod
    def reply(status: int, code: int | None = None, response: Any = None, path: str = "") -> Reply:
        body = response if response is not None else ({"code": code} if code else {})
        rec = record(status, body, path=path or "/channels/x/query")
        if status < 300:
            return Reply(True, {}, None, [rec], api_calls=1)
        return Reply(
            False,
            None,
            {"status": status, "code": code, "message": "no", "kind": "api"},
            [rec],
            api_calls=1,
        )

    # -- the server side --

    def handle(self, method: str, path: str, body: Any, params: dict[str, str] | None) -> Any:
        parts = [p for p in path.split("?", 1)[0].strip("/").split("/") if p]
        for prefix in (["api", "v2", "chat"], ["api", "v2"]):
            if parts[: len(prefix)] == prefix:
                parts = parts[len(prefix) :]
                break
        body = body or {}
        if parts[:1] == ["channels"] and len(parts) >= 3 and self.family_channel(parts[2]):
            return self.channel_request(method, path, parts[2], parts[3:], body)
        if parts == ["channels"] and method == "POST":
            cid = str((body.get("filter_conditions") or {}).get("cid") or "")
            channel_id = cid.split(":", 1)[-1]
            if self.family_channel(channel_id):
                return self.channel_read(method, path, channel_id)
            return None
        if parts == ["members"] and method == "GET":
            payload = json.loads((params or {}).get("payload", "{}"))
            channel_id = str(payload.get("id"))
            if not self.family_channel(channel_id):
                return None
            if channel_id not in self.server.members:
                return error(method, path, 404, 16)
            return ok(method, path, {"members": self.member_list(channel_id)}, 200)
        if parts == ["moderation", "ban"] and method == "POST":
            channel_id = str(body.get("channel_cid", "")).split(":", 1)[-1]
            self.banned.setdefault(channel_id, set()).add(str(body.get("target_user_id")))
            self.deliver(
                channel_id,
                {
                    "type": "user.banned",
                    "cid": f"{T}:{channel_id}",
                    "user": {"id": body.get("target_user_id")},
                    "created_by": {"id": body.get("banned_by_id")},
                },
                only=str(body.get("target_user_id")),
            )
            return ok(method, path, {"duration": "1ms"})
        if parts == ["moderation", "ban"] and method == "DELETE":
            channel_id = str((params or {}).get("id", ""))
            self.banned.get(channel_id, set()).discard(str((params or {}).get("target_user_id")))
            return ok(method, path, {"duration": "1ms"}, 200)
        if parts == ["users"] and method == "PATCH":
            for user in body.get("users") or []:
                stamp = (user.get("set") or {}).get("revoke_tokens_issued_before")
                if isinstance(stamp, str):
                    parsed = time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
                    self.revoked[user["id"]] = calendar.timegm(parsed)
            return ok(method, path, {"users": {}}, 200)
        if parts[:1] == ["users"] and len(parts) == 3 and parts[2] == "deactivate":
            self.deactivated.add(parts[1])
            if parts[1] in self.server.users:
                self.server.users[parts[1]]["deactivated_at"] = "2026-09-26T00:00:00Z"
            return ok(method, path, {"user": {"id": parts[1]}})
        if parts == ["users", "delete"] and method == "POST":
            for uid in body.get("user_ids") or []:
                self.delete_user(str(uid), body)
            return ok(method, path, {"task_id": "t-delete"})
        return None

    def delete_user(self, uid: str, options: dict[str, Any]) -> None:
        if uid not in self.server.users and not uid.startswith("deleted-user-"):
            return
        self.server.users.pop(uid, None)
        self.deleted.add(uid)
        if self.hard_delete_removes_conversations and options.get("conversations") == "hard":
            for channel_id in [c for c, m in self.server.members.items() if uid in m]:
                if len(self.members(channel_id)) <= 2:
                    self.server.members.pop(channel_id, None)
                    self.messages.pop(channel_id, None)
        if not uid.startswith("deleted-user-"):
            # As Stream: a system user takes over what the deleted user owned.
            artifact = "deleted-user-1729640-0000"
            self.server.users.setdefault(
                artifact, {"id": artifact, "role": "user", "created_at": time.time_ns()}
            )

    def member_list(self, channel_id: str) -> list[dict[str, Any]]:
        return [
            {"user_id": uid, **self.member_custom.get((channel_id, uid), {})}
            for uid in self.members(channel_id)
        ]

    def channel_read(self, method: str, path: str, channel_id: str) -> Any:
        if channel_id not in self.server.members:
            return ok(method, path, {"channels": []}, 201)
        channel = {
            "channel": {"cid": f"{T}:{channel_id}", "frozen": channel_id in self.frozen},
            "messages": list(self.messages.get(channel_id, [])),
            "members": self.member_list(channel_id),
        }
        return ok(method, path, {"channels": [channel]}, 201)

    def channel_request(
        self, method: str, path: str, channel_id: str, rest: list[str], body: dict[str, Any]
    ) -> Any:
        cid = f"{T}:{channel_id}"
        if channel_id not in self.server.members and rest[:1] != ["query"]:
            return error(method, path, 404, 16)
        if method == "PATCH" and not rest:
            fields = body.get("set") or {}
            if "frozen" in fields:
                (self.frozen.add if fields["frozen"] else self.frozen.discard)(channel_id)
            self.channel_custom.setdefault(channel_id, {}).update(fields)
            self.deliver(
                channel_id,
                {"type": "channel.updated", "cid": cid, "channel": {"cid": cid, **fields}},
            )
            return ok(method, path, {"channel": {"cid": cid}}, 200)
        if method == "POST" and not rest:
            members = self.server.members.setdefault(channel_id, [])
            for uid in body.get("remove_members") or []:
                if uid in members:
                    members.remove(uid)
                    self.deliver(
                        channel_id,
                        {
                            "type": "member.removed",
                            "cid": cid,
                            "member": {"user_id": uid},
                            "user": {"id": body.get("user_id")},
                        },
                    )
            for uid in body.get("add_members") or []:
                uid = uid if isinstance(uid, str) else uid.get("user_id")
                if uid not in members:
                    members.append(uid)
            return ok(method, path, {"channel": {"cid": cid}})
        if rest == ["message"] and method == "POST":
            message = body.get("message") or {}
            uid = message.get("user_id")
            if channel_id in self.frozen and self.server_send_refused_when_frozen:
                return error(method, path, 403, 17, "channel is frozen")
            if uid in self.deleted:
                return error(method, path, 400, 4, "user does not exist")
            if uid in self.deactivated:
                return error(method, path, 403, 17, "user is deactivated")
            stored = {
                "id": self.next_id("m"),
                "text": message.get("text"),
                "user": {"id": uid},
                "type": "regular",
            }
            self.messages.setdefault(channel_id, []).append(stored)
            for hider in list(self.hidden.get(channel_id, set())):
                self.hidden[channel_id].discard(hider)  # a new message shows it again
            self.deliver(channel_id, {"type": "message.new", "cid": cid, "message": stored})
            return ok(method, path, {"message": stored})
        if rest == ["hide"] and method == "POST":
            uid = str(body.get("user_id"))
            self.hidden.setdefault(channel_id, set()).add(uid)
            self.deliver(channel_id, {"type": "channel.hidden", "cid": cid}, only=uid)
            return ok(method, path, {"duration": "1ms"})
        if rest == ["show"] and method == "POST":
            self.hidden.get(channel_id, set()).discard(str(body.get("user_id")))
            return ok(method, path, {"duration": "1ms"})
        return None

    # -- the client side --

    def behaviour(self, session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        label = session.label
        if label.split("-", 1)[0] not in mechanisms.FAMILY_LABELS:
            return None
        uid = self.label_user(label)
        if uid is None:
            return None
        if op == "connect":
            refused = self.auth_error(label, uid)
            if refused is not None:
                return ws_refused(refused.status or 401, refused.code or 5)
            return Reply(True, {"me": {"id": uid, "role": "user"}}, None)
        if op != "call":
            return None
        method = params.get("method")
        channel_id = str(params.get("id", ""))
        refused = self.auth_error(label, uid)
        if method == "queryChannels":
            if refused is not None:
                return refused
            cid = str((params.get("args") or [{}])[0].get("cid", ""))
            channel_id = cid.split(":", 1)[-1]
            listed = channel_id in self.server.members and uid not in self.hidden.get(
                channel_id, set()
            )
            channels = [{"channel": {"cid": cid, "id": channel_id}}] if listed else []
            return self.reply(201, response={"channels": channels}, path="/channels")
        if not self.family_channel(channel_id):
            return None
        if refused is not None:
            return refused
        path = f"/channels/{T}/{channel_id}"
        if channel_id not in self.server.members:
            return self.reply(404, 16, path=path)
        member = uid in self.members(channel_id)
        if method in ("watch", "query"):
            if not member and uid not in self.banned.get(channel_id, set()):
                return self.reply(403, 17, path=f"{path}/query")
            if uid in self.banned.get(channel_id, set()) and not self.banned_can_read:
                return self.reply(403, 17, path=f"{path}/query")
            if method == "watch":
                self.watching.setdefault(channel_id, set()).add(label)
            texts = [m.get("text") for m in self.messages.get(channel_id, [])]
            return self.reply(
                201,
                response={"channel": {"id": channel_id}, "messages": [{"text": t} for t in texts]},
                path=f"{path}/query",
            )
        if method == "updateMemberPartial":
            if not member:
                return self.reply(403, 17, path=f"{path}/member")
            note = ((params.get("args") or [{}])[0].get("set") or {}).get("glow_note")
            self.member_custom.setdefault((channel_id, uid), {})["glow_note"] = note
            return self.reply(200, response={"channel_member": {}}, path=f"{path}/member")
        args = params.get("args") or []
        if method == "show":
            status = 201 if self.client_can_show else 403
            if self.client_can_show:
                self.hidden.get(channel_id, set()).discard(uid)
            return self.request(status, "POST", f"{path}/show", {"user_id": None}, {})
        # addMembers, unbanUser and updatePartial: a member may do none of them. The
        # records carry the request the SDK sends, for the server's replay.
        if method == "addMembers":
            return self.request(403, "POST", path, {"add_members": args[0]}, {})
        if method == "unbanUser":
            query = {"target_user_id": args[0], "type": T, "id": channel_id}
            return self.request(403, "DELETE", "/moderation/ban", None, query)
        if method == "updatePartial":
            return self.request(403, "PATCH", path, args[0], {})
        return self.reply(403, 17, path=path)

    def request(
        self, status: int, method: str, path: str, body: Any, query: dict[str, Any]
    ) -> Reply:
        """A reply whose one recorded request is ``method path`` with ``body`` and ``query``."""
        response: dict[str, Any] = {} if status < 300 else {"code": 17, "message": "no"}
        rec = {
            "method": method,
            "path": path,
            "params": {"api_key": "k", "user_id": "client", **query},
            "body": body,
            "status": status,
            "response": response,
        }
        if status < 300:
            return Reply(True, {}, None, [rec], api_calls=1)
        error_info = {"status": status, "code": 17, "message": "no", "kind": "api"}
        return Reply(False, None, error_info, [rec], api_calls=1)


def family_run(
    world_knobs: dict[str, Any] | None = None,
) -> tuple[ProofRun, FakeServer, World, FakeClock]:
    """A run whose family sessions and requests are answered by a ``World``."""
    from tests.fakes import make_run

    clock = FakeClock()
    holder: dict[str, World] = {}

    def behaviour(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        return holder["world"].behaviour(session, op, params)

    run, server = make_run(default_behaviour=behaviour)
    world = World(server, run, clock, **(world_knobs or {})).install()
    holder["world"] = world
    original = run._session

    def session_with_token(label: str, token: str | None, **kwargs: Any) -> Any:
        if token is not None:
            world.tokens[label] = token
        return original(label, token, **kwargs)

    run._session = session_with_token  # type: ignore[method-assign]
    return run, server, world, clock
