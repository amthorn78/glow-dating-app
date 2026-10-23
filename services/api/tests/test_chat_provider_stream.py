"""The Stream adapter and the client token's signer, offline (P06.2 Stage B2; the brief's
design points c to f, DM-16 4.1 to 4.5 and 3.1 to 3.3).

The adapter runs on a ``getstream`` client built here with explicit dummy values on a
*recorded* ``httpx`` transport: a hand-written model of Stream Chat's documented answers
(timestamps as Unix nanoseconds, as the SDK decodes them) that records every request's
method, path, query parameters and JSON body, without the ``api_key`` parameter and without
any header. Nothing here was captured with credentials, and no request leaves the process.

One port contract, two subjects: the same script runs against the fixture provider and
against the adapter on the recording, and the outcomes must agree row for row, except the
one row DM-16 4.7 names (a send by a removed member), where the fixture refuses and the
recording models Stream's server-side send accepting it; the live conformance run records
what Stream answers.
"""

from __future__ import annotations

import inspect
import json
import re
import time
import unittest
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import jwt
from getstream import Stream
from getstream.exceptions import StreamApiException, StreamTransportException

from glow_domain import chat_provider_stream as adapter_module
from glow_domain.chat_provider import (
    CHANNEL_UNAVAILABLE,
    MEMBER_UNAVAILABLE,
    OPERATIONS,
    PROVIDER_REJECTED,
    PROVIDER_UNAVAILABLE,
    ChatProviderError,
    ProviderReceipt,
)
from glow_domain.chat_provider_fixtures import FixtureChatProvider
from glow_domain.chat_provider_stream import (
    IAT_BACKDATE_SECONDS,
    StreamChatProvider,
    StreamProviderError,
    sign_chat_token,
    token_claims,
)
from glow_domain.chat_tokens import TokenGrant, revocation_cutoff_sent

# Dummy values for the client built here; neither is a credential.
API_KEY = "synthetic-api-key-for-offline-tests"
SECRET = "synthetic-signing-value-for-offline-tests-only"
BASE_URL = "https://chat.invalid/"
TYPE = "glow-match"
NOW = datetime(2026, 10, 23, 12, 0, 0, tzinfo=UTC)

# The harness's stop types, as the adapter must let them through (DM-16 4.1): each is a
# RuntimeError raised from the HTTP client's hooks, before or after a request.
STOP_TYPES: tuple[type[RuntimeError], ...] = (
    type("GuardRefused", (RuntimeError,), {}),
    type("RunStopped", (RuntimeError,), {}),
    type("GuardrailStop", (RuntimeError,), {}),
    RuntimeError,
)


def _ns(moment: datetime) -> int:
    return int(moment.timestamp() * 1_000_000_000)


def _error(status: int, code: int, message: str) -> tuple[int, dict[str, Any]]:
    # Stream's error envelope (its documented APIError shape).
    return status, {
        "code": code,
        "message": message,
        "StatusCode": status,
        "duration": "0.42ms",
        "more_info": "https://getstream.io/chat/docs/api_errors_response",
        "details": [],
    }


class RecordedStream:
    """A hand-written model of Stream Chat's answers to the SDK's requests, recording what
    the adapter sends. It holds users, channels and messages as Stream would, answers from
    Stream's documented response shapes, and refuses as Stream documents (404 code 16 for
    an object it does not have; 400 code 4 for an input error such as a message ID that
    already exists). Its server-side send does not check membership (DM-16 4.7)."""

    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}
        self.channels: dict[str, dict[str, Any]] = {}
        self.messages: dict[str, dict[str, Any]] = {}
        self.recording: list[dict[str, Any]] = []
        self.credentials_seen = 0
        self._scripted: list[Callable[[httpx.Request], httpx.Response | None]] = []
        self.clock = _ns(NOW)

    # -- scripting -------------------------------------------------------------------

    def refuse_next(self, status: int, code: int, message: str) -> None:
        def answer(request: httpx.Request) -> httpx.Response | None:
            status_, body = _error(status, code, message)
            return httpx.Response(status_, json=body)

        self._scripted.append(answer)

    def fail_next(self, exception: Callable[[httpx.Request], Exception]) -> None:
        def answer(request: httpx.Request) -> httpx.Response | None:
            raise exception(request)

        self._scripted.append(answer)

    def answer_next(self, status: int, body: Any) -> None:
        self._scripted.append(lambda request: httpx.Response(status, json=body))

    # -- the transport -----------------------------------------------------------------

    def handle(self, request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if "api_key" in params:
            self.credentials_seen += 1
            del params["api_key"]  # never recorded (DM-16 4.2)
        body = json.loads(request.content) if request.content else None
        self.recording.append(
            {"method": request.method, "path": request.url.path, "params": params, "body": body}
        )
        if self._scripted:
            scripted = self._scripted.pop(0)(request)
            if scripted is not None:
                return scripted
        status, answer = self._answer(request.method, request.url.path, params, body)
        return httpx.Response(status, json=answer)

    # -- Stream's documented behaviour -------------------------------------------------

    def _user_body(self, user: dict[str, Any]) -> dict[str, Any]:
        body = {
            "id": user["id"],
            "role": "user",
            "banned": False,
            "online": False,
            "invisible": False,
            "language": "",
            "shadow_banned": False,
            "created_at": user["created_at"],
            "updated_at": user["created_at"],
            "total_unread_count": 0,
            "unread_channels": 0,
            "unread_count": 0,
            "unread_threads": 0,
            "blocked_user_ids": [],
            "channel_mutes": [],
            "devices": [],
            "mutes": [],
            "teams": [],
            "custom": {},
        }
        for key in ("deactivated_at", "revoke_tokens_issued_before"):
            if user.get(key) is not None:
                body[key] = user[key]
        return body

    def _member_body(self, user_id: str) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "channel_role": "channel_member",
            "banned": False,
            "shadow_banned": False,
            "notifications_muted": False,
            "created_at": self.clock,
            "updated_at": self.clock,
            "custom": {},
            "user": self._user_body(self.users[user_id]),
        }

    def _channel_body(self, channel: dict[str, Any]) -> dict[str, Any]:
        return {
            "cid": channel["cid"],
            "id": channel["id"],
            "type": TYPE,
            "created_at": channel["created_at"],
            "updated_at": channel["created_at"],
            "disabled": False,
            "frozen": False,
            "member_count": len(channel["members"]),
            "custom": {},
        }

    def _state_body(self, channel: dict[str, Any]) -> dict[str, Any]:
        return {
            "duration": "0.42ms",
            "channel": self._channel_body(channel),
            "members": [self._member_body(m) for m in channel["members"]],
            "messages": [],
            "pinned_messages": [],
            "threads": [],
        }

    def _message_body(self, message: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": message["id"],
            "cid": message["cid"],
            "text": message["text"],
            "html": f"<p>{message['text']}</p>\n",
            "type": "regular",
            "created_at": message["created_at"],
            "updated_at": message["created_at"],
            "user": self._user_body(self.users[message["user_id"]])
            if message["user_id"] in self.users
            else {"id": message["user_id"], "role": "user"},
            "attachments": [],
            "latest_reactions": [],
            "own_reactions": [],
            "mentioned_users": [],
            "restricted_visibility": [],
            "custom": {},
            "reaction_counts": {},
            "reaction_scores": {},
            "reply_count": 0,
            "deleted_reply_count": 0,
            "pinned": False,
            "shadowed": False,
            "silent": False,
            "mentioned_channel": False,
            "mentioned_here": False,
        }

    def _answer(
        self, method: str, path: str, params: dict[str, str], body: Any
    ) -> tuple[int, dict[str, Any]]:
        self.clock += 1_000_000
        if method == "GET" and path == "/api/v2/users":
            payload = json.loads(params.get("payload", "{}"))
            wanted = payload.get("filter_conditions", {}).get("id", {}).get("$in", [])
            include_deactivated = payload.get("include_deactivated_users") is True
            users = [
                self._user_body(u)
                for uid, u in self.users.items()
                if uid in wanted and (include_deactivated or u.get("deactivated_at") is None)
            ]
            return 200, {"duration": "0.42ms", "users": users}
        if method == "POST" and path == "/api/v2/users":
            out = {}
            for uid, data in (body or {}).get("users", {}).items():
                user = self.users.setdefault(uid, {"id": uid, "created_at": self.clock})
                for key in ("name", "image", "role", "custom"):
                    if key in data:
                        user[key] = data[key]  # an upsert replaces what it names
                out[uid] = self._user_body(user)
            return 201, {"duration": "0.42ms", "membership_deletion_task_id": "", "users": out}
        if method == "PATCH" and path == "/api/v2/users":
            out = {}
            for entry in (body or {}).get("users", []):
                user = self.users.get(entry["id"])
                if user is None:
                    return _error(404, 16, f"user {entry['id']} does not exist")
                cut = entry.get("set", {}).get("revoke_tokens_issued_before")
                if cut is not None:
                    moment = datetime.fromisoformat(cut.replace("Z", "+00:00"))
                    user["revoke_tokens_issued_before"] = _ns(moment)
                out[entry["id"]] = self._user_body(user)
            return 201, {"duration": "0.42ms", "membership_deletion_task_id": "", "users": out}
        deactivate = re.fullmatch(r"/api/v2/users/([^/]+)/deactivate", path)
        if method == "POST" and deactivate:
            user = self.users.get(deactivate.group(1))
            if user is None:
                return _error(404, 16, f"user {deactivate.group(1)} does not exist")
            if user.get("deactivated_at") is not None:
                return _error(
                    400, 4, "DeactivateUser failed with error: user is already deactivated"
                )
            user["deactivated_at"] = self.clock
            return 201, {"duration": "0.42ms", "user": self._user_body(user)}
        if method == "POST" and path == "/api/v2/chat/channels":
            cid = (body or {}).get("filter_conditions", {}).get("cid")
            channels = [self._state_body(c) for c in self.channels.values() if c["cid"] == cid]
            return 201, {"duration": "0.42ms", "channels": channels}
        query = re.fullmatch(rf"/api/v2/chat/channels/{TYPE}/([^/]+)/query", path)
        if method == "POST" and query:
            channel_id = query.group(1)
            data = (body or {}).get("data", {})
            members = [m["user_id"] for m in data.get("members", [])]
            creator = data.get("created_by_id")
            if creator is None and "created_by" not in data:
                return _error(
                    400,
                    4,
                    'GetOrCreateChannel failed with error: "either data.created_by or '
                    'data.created_by_id must be provided when using server side auth."',
                )
            missing = [m for m in [*members, creator] if m and m not in self.users]
            if missing:
                return _error(
                    400, 4, f'GetOrCreateChannel failed with error: "users {missing} do not exist"'
                )
            channel = self.channels.get(channel_id)
            if channel is None:
                channel = {
                    "id": channel_id,
                    "cid": f"{TYPE}:{channel_id}",
                    "members": list(dict.fromkeys(members)),
                    "created_at": self.clock,
                }
                self.channels[channel_id] = channel
            else:
                # Stream's get-or-create on an existing channel adds the members named.
                for member in members:
                    if member not in channel["members"]:
                        channel["members"].append(member)
            return 201, self._state_body(channel)
        send = re.fullmatch(rf"/api/v2/chat/channels/{TYPE}/([^/]+)/message", path)
        if method == "POST" and send:
            channel = self.channels.get(send.group(1))
            if channel is None:
                return _error(404, 16, 'SendMessage failed with error: "channel not found"')
            message = (body or {}).get("message", {})
            sender = message.get("user_id")
            if sender not in self.users:
                return _error(
                    400, 4, f'SendMessage failed with error: "user {sender} does not exist"'
                )
            if self.users[sender].get("deactivated_at") is not None:
                return _error(
                    400, 4, f'SendMessage failed with error: "user {sender} is deactivated"'
                )
            message_id = message.get("id")
            if message_id in self.messages:
                exists = f'"a message with ID {message_id} already exists"'
                return _error(400, 4, f"SendMessage failed with error: {exists}")
            stored = {
                "id": message_id,
                "cid": channel["cid"],
                "text": message.get("text"),
                "user_id": sender,
                "created_at": self.clock,
            }
            self.messages[message_id] = stored
            return 201, {"duration": "0.42ms", "message": self._message_body(stored)}
        update = re.fullmatch(rf"/api/v2/chat/channels/{TYPE}/([^/]+)", path)
        if method == "POST" and update:
            channel = self.channels.get(update.group(1))
            if channel is None:
                return _error(404, 16, 'UpdateChannel failed with error: "channel not found"')
            for member in (body or {}).get("remove_members", []):
                if member in channel["members"]:
                    channel["members"].remove(member)
            return 201, {
                "duration": "0.42ms",
                "channel": self._channel_body(channel),
                "members": [self._member_body(m) for m in channel["members"]],
            }
        return _error(404, 16, "not modelled")


def make_client(model: RecordedStream, **options: Any) -> Stream:
    """A client with explicit dummy values; every knob given, so construction reads no
    environment variable (``getstream`` 6.1.0 would otherwise instantiate its settings)."""
    return Stream(
        api_key=API_KEY,
        api_secret=SECRET,
        base_url=BASE_URL,
        timeout=5.0,
        max_conns_per_host=1,
        idle_timeout=1.0,
        connect_timeout=1.0,
        **(
            {"transport": httpx.MockTransport(model.handle)} if "http_client" not in options else {}
        ),
        **options,
    )


def outcome(call: Callable[[], ProviderReceipt]) -> str:
    """A row's outcome: ``ok``, ``already`` or the Glow code."""
    try:
        receipt = call()
    except ChatProviderError as error:
        return error.code
    return "already" if receipt.already else "ok"


class World:
    """The identifiers one contract run uses (Glow's own random IDs; no shape enforced)."""

    def __init__(self, tag: str) -> None:
        self.a, self.b, self.d, self.e = (f"{tag}-u{i}" for i in "abde")
        self.unknown = f"{tag}-unknown"
        self.c, self.c_missing, self.c_mixed = f"{tag}-c1", f"{tag}-cx", f"{tag}-c2"
        self.m1, self.m2, self.m3, self.m4, self.m5 = (f"{tag}-m{i}" for i in range(1, 6))
        self.cut = datetime(2026, 10, 23, 12, 30, 0, tzinfo=UTC)


# The one row where the two subjects are expected to differ (DM-16 4.7).
REMOVED_MEMBER_SEND = "send by a removed member (4.7)"


def contract(provider: Any, w: World) -> dict[str, str]:
    """Each operation's outcomes: first call, repeat, an unknown member, channel or user,
    after a removal and after a deactivation (design point f)."""
    rows: dict[str, str] = {}
    rows["provision first"] = outcome(lambda: provider.provision_user(w.a))
    rows["provision repeat"] = outcome(lambda: provider.provision_user(w.a))
    rows["provision second member"] = outcome(lambda: provider.provision_user(w.b))
    rows["create first"] = outcome(lambda: provider.create_channel(w.c, (w.a, w.b)))
    rows["create repeat"] = outcome(lambda: provider.create_channel(w.c, (w.a, w.b)))
    rows["create with an unknown member"] = outcome(
        lambda: provider.create_channel(w.c_mixed, (w.a, w.unknown))
    )
    rows["send first"] = outcome(lambda: provider.send_message(w.c, w.a, w.m1, "hello"))
    rows["send repeat"] = outcome(lambda: provider.send_message(w.c, w.a, w.m1, "hello"))
    rows["send to an unknown channel"] = outcome(
        lambda: provider.send_message(w.c_missing, w.a, w.m3, "hello")
    )
    rows["send by an unknown user"] = outcome(
        lambda: provider.send_message(w.c, w.unknown, w.m4, "hello")
    )
    rows["remove first"] = outcome(lambda: provider.remove_members(w.c, (w.a, w.b)))
    rows["remove repeat"] = outcome(lambda: provider.remove_members(w.c, (w.a, w.b)))
    rows["create repeated after the removal"] = outcome(
        lambda: provider.create_channel(w.c, (w.a, w.b))
    )
    rows[REMOVED_MEMBER_SEND] = outcome(lambda: provider.send_message(w.c, w.a, w.m2, "later"))
    rows["remove from an unknown channel"] = outcome(
        lambda: provider.remove_members(w.c_missing, (w.a, w.b))
    )
    rows["provision for deactivation"] = outcome(lambda: provider.provision_user(w.d))
    rows["deactivate first"] = outcome(lambda: provider.deactivate_user(w.d))
    rows["deactivate repeat"] = outcome(lambda: provider.deactivate_user(w.d))
    rows["provision after deactivation"] = outcome(lambda: provider.provision_user(w.d))
    rows["create with a deactivated member"] = outcome(
        lambda: provider.create_channel(f"{w.c}-d", (w.d, w.b))
    )
    rows["send by a deactivated user"] = outcome(
        lambda: provider.send_message(w.c, w.d, w.m5, "hello")
    )
    rows["deactivate an unknown user"] = outcome(lambda: provider.deactivate_user(w.unknown))
    rows["provision for revocation"] = outcome(lambda: provider.provision_user(w.e))
    sent = revocation_cutoff_sent(w.cut)
    rows["revoke first"] = outcome(lambda: provider.revoke_user_tokens(w.e, sent))
    rows["revoke repeat"] = outcome(lambda: provider.revoke_user_tokens(w.e, sent))
    rows["revoke later cut-off"] = outcome(
        lambda: provider.revoke_user_tokens(w.e, sent + timedelta(seconds=30))
    )
    rows["provision after revocation"] = outcome(lambda: provider.provision_user(w.e))
    rows["revoke an unknown user"] = outcome(lambda: provider.revoke_user_tokens(w.unknown, sent))
    return rows


EXPECTED = {
    "provision first": "ok",
    "provision repeat": "already",
    "provision second member": "ok",
    "create first": "ok",
    "create repeat": "already",
    "create with an unknown member": MEMBER_UNAVAILABLE,
    "send first": "ok",
    "send repeat": "already",
    "send to an unknown channel": CHANNEL_UNAVAILABLE,
    "send by an unknown user": MEMBER_UNAVAILABLE,
    "remove first": "ok",
    "remove repeat": "already",
    "create repeated after the removal": "already",
    REMOVED_MEMBER_SEND: MEMBER_UNAVAILABLE,  # the fixture's; the recording accepts
    "remove from an unknown channel": CHANNEL_UNAVAILABLE,
    "provision for deactivation": "ok",
    "deactivate first": "ok",
    "deactivate repeat": "already",
    "provision after deactivation": "already",
    "create with a deactivated member": MEMBER_UNAVAILABLE,
    "send by a deactivated user": MEMBER_UNAVAILABLE,
    "deactivate an unknown user": MEMBER_UNAVAILABLE,
    "provision for revocation": "ok",
    "revoke first": "ok",
    "revoke repeat": "already",
    "revoke later cut-off": "ok",
    "provision after revocation": "already",
    "revoke an unknown user": MEMBER_UNAVAILABLE,
}


class ContractTests(unittest.TestCase):
    """One port contract, two subjects (design point f)."""

    def test_the_fixture_meets_the_stated_contract(self) -> None:
        rows = contract(FixtureChatProvider("test"), World("fx"))
        self.assertEqual(rows, EXPECTED)

    def test_the_adapter_on_the_recording_meets_the_contract_but_for_the_stated_row(self) -> None:
        model = RecordedStream()
        rows = contract(StreamChatProvider(make_client(model)), World("st"))
        differing = {k: (EXPECTED[k], v) for k, v in rows.items() if v != EXPECTED[k]}
        # DM-16 4.7: Stream's server-side send may not check membership; the recording
        # models an acceptance, which the live row records as a difference, not a failure.
        self.assertEqual(differing, {REMOVED_MEMBER_SEND: (MEMBER_UNAVAILABLE, "ok")})

    def test_the_contract_covers_every_operation(self) -> None:
        source = inspect.getsource(contract)
        for operation in OPERATIONS:
            self.assertIn(f"provider.{operation}(", source)


class WhatIsSentTests(unittest.TestCase):
    """DM-16 4.2: each operation's method, path and exact JSON keys, on the recording."""

    def setUp(self) -> None:
        self.model = RecordedStream()
        self.adapter = StreamChatProvider(make_client(self.model))
        self.w = World("ws")

    def requests(self) -> list[dict[str, Any]]:
        taken, self.model.recording = list(self.model.recording), []
        return taken

    def test_provisioning_sends_the_id_only_after_a_read(self) -> None:
        self.adapter.provision_user(self.w.a)
        read, write = self.requests()
        self.assertEqual((read["method"], read["path"]), ("GET", "/api/v2/users"))
        payload = json.loads(read["params"]["payload"])
        # The SDK serialises every field of the payload, the unset ones as null.
        self.assertEqual(
            {key: value for key, value in payload.items() if value is not None},
            {
                "filter_conditions": {"id": {"$in": [self.w.a]}},
                "include_deactivated_users": True,
                "limit": 1,
            },
        )
        self.assertEqual((write["method"], write["path"]), ("POST", "/api/v2/users"))
        self.assertEqual(write["body"], {"users": {self.w.a: {"id": self.w.a}}})
        # A repeat reads and writes nothing (4.4).
        self.adapter.provision_user(self.w.a)
        self.assertEqual([r["method"] for r in self.requests()], ["GET"])

    def test_creation_sends_the_type_the_two_members_and_their_creator_only(self) -> None:
        self.adapter.provision_user(self.w.a)
        self.adapter.provision_user(self.w.b)
        self.requests()
        self.adapter.create_channel(self.w.c, (self.w.a, self.w.b))
        users, channel, create = self.requests()
        self.assertEqual((users["method"], users["path"]), ("GET", "/api/v2/users"))
        self.assertEqual(
            json.loads(users["params"]["payload"])["filter_conditions"],
            {"id": {"$in": [self.w.a, self.w.b]}},
        )
        self.assertEqual((channel["method"], channel["path"]), ("POST", "/api/v2/chat/channels"))
        self.assertEqual(
            channel["body"],
            {"filter_conditions": {"cid": f"{TYPE}:{self.w.c}"}, "limit": 1, "member_limit": 10},
        )
        self.assertEqual(
            (create["method"], create["path"]),
            ("POST", f"/api/v2/chat/channels/{TYPE}/{self.w.c}/query"),
        )
        self.assertEqual(
            create["body"],
            {
                "data": {
                    "created_by_id": self.w.a,
                    "members": [{"user_id": self.w.a}, {"user_id": self.w.b}],
                }
            },
        )
        # A repeat reads and sends the members to no existing channel (4.4).
        self.adapter.create_channel(self.w.c, (self.w.a, self.w.b))
        self.assertEqual(
            [(r["method"], r["path"]) for r in self.requests()],
            [("GET", "/api/v2/users"), ("POST", "/api/v2/chat/channels")],
        )

    def test_a_send_carries_the_committed_id_the_text_and_the_sender(self) -> None:
        self._channel()
        self.adapter.send_message(self.w.c, self.w.a, self.w.m1, "hello")
        (send,) = self.requests()
        self.assertEqual(
            (send["method"], send["path"]),
            ("POST", f"/api/v2/chat/channels/{TYPE}/{self.w.c}/message"),
        )
        self.assertEqual(
            send["body"], {"message": {"id": self.w.m1, "text": "hello", "user_id": self.w.a}}
        )

    def test_a_removal_names_the_two_members_after_a_read(self) -> None:
        self._channel()
        self.adapter.remove_members(self.w.c, (self.w.a, self.w.b))
        read, remove = self.requests()
        self.assertEqual((read["method"], read["path"]), ("POST", "/api/v2/chat/channels"))
        self.assertEqual(
            (remove["method"], remove["path"]), ("POST", f"/api/v2/chat/channels/{TYPE}/{self.w.c}")
        )
        self.assertEqual(remove["body"], {"remove_members": [self.w.a, self.w.b]})
        self.adapter.remove_members(self.w.c, (self.w.a, self.w.b))
        self.assertEqual([r["method"] for r in self.requests()], ["POST"])  # the read only

    def test_a_deactivation_names_the_user_in_its_path_with_an_empty_body(self) -> None:
        self.adapter.provision_user(self.w.d)
        self.requests()
        self.adapter.deactivate_user(self.w.d)
        read, deactivate = self.requests()
        self.assertEqual((read["method"], read["path"]), ("GET", "/api/v2/users"))
        self.assertEqual(
            (deactivate["method"], deactivate["path"]),
            ("POST", f"/api/v2/users/{self.w.d}/deactivate"),
        )
        self.assertEqual(deactivate["body"], {})

    def test_a_revocation_carries_the_user_and_the_cut_off_as_given(self) -> None:
        self.adapter.provision_user(self.w.e)
        self.requests()
        sent = revocation_cutoff_sent(datetime(2026, 10, 23, 12, 30, 0, 250_000, tzinfo=UTC))
        self.adapter.revoke_user_tokens(self.w.e, sent)
        read, revoke = self.requests()
        self.assertEqual((read["method"], read["path"]), ("GET", "/api/v2/users"))
        self.assertEqual((revoke["method"], revoke["path"]), ("PATCH", "/api/v2/users"))
        self.assertEqual(
            revoke["body"],
            {
                "users": [
                    {"id": self.w.e, "set": {"revoke_tokens_issued_before": "2026-10-23T12:30:01Z"}}
                ]
            },
        )

    def test_no_request_carries_a_name_image_role_or_custom_field(self) -> None:
        contract(self.adapter, self.w)
        forbidden = {"name", "image", "role", "custom"}
        creations = 0
        for request in self.model.recording:
            keys = _keys_at_every_depth(request["body"])
            self.assertFalse(keys & forbidden, request)
            if "data" in keys:
                # Only the creation's envelope, holding the creator and the members.
                creations += 1
                self.assertTrue(request["path"].endswith("/query"), request)
                self.assertEqual(set(request["body"]), {"data"})
                self.assertEqual(set(request["body"]["data"]), {"created_by_id", "members"})
                for member in request["body"]["data"]["members"]:
                    self.assertEqual(set(member), {"user_id"})
        self.assertGreater(creations, 0)

    def test_the_recording_holds_no_api_key_parameter_and_no_auth_header(self) -> None:
        contract(self.adapter, self.w)
        text = json.dumps(self.model.recording)
        for forbidden in ("api_key", "Authorization", "authorization", "stream-auth-type"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn(SECRET, text)
        # The transport did authenticate every request; the recording left it out.
        self.assertEqual(self.model.credentials_seen, len(self.model.recording))

    def test_the_adapter_holds_only_the_client_it_is_given(self) -> None:
        client = make_client(self.model)
        adapter = StreamChatProvider(client)
        self.assertEqual(vars(adapter), {"_client": client})
        self.assertEqual(adapter.name, "stream")

    def _channel(self) -> None:
        self.adapter.provision_user(self.w.a)
        self.adapter.provision_user(self.w.b)
        self.adapter.create_channel(self.w.c, (self.w.a, self.w.b))
        self.requests()


def _keys_at_every_depth(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key))
            keys |= _keys_at_every_depth(item)
    elif isinstance(value, list):
        for item in value:
            keys |= _keys_at_every_depth(item)
    return keys


class ExceptionBoundaryTests(unittest.TestCase):
    """DM-16 4.1: only the SDK's own errors are mapped; the harness's stop types and every
    other exception propagate unchanged, from a hook before the request and after it."""

    def operations(self, adapter: StreamChatProvider, w: World) -> list[Callable[[], Any]]:
        return [
            lambda: adapter.provision_user(w.a),
            lambda: adapter.create_channel(w.c, (w.a, w.b)),
            lambda: adapter.send_message(w.c, w.a, w.m1, "hello"),
            lambda: adapter.remove_members(w.c, (w.a, w.b)),
            lambda: adapter.deactivate_user(w.a),
            lambda: adapter.revoke_user_tokens(w.a, revocation_cutoff_sent(NOW)),
        ]

    def test_each_stop_type_propagates_unchanged_from_a_request_hook(self) -> None:
        for stop_type in STOP_TYPES:
            for index, operation in enumerate(OPERATIONS):
                with self.subTest(stop=stop_type.__name__, operation=operation):
                    raised = stop_type("stopped before the request")

                    def hook(request: httpx.Request, raised: BaseException = raised) -> None:
                        raise raised

                    model = RecordedStream()
                    http = httpx.Client(
                        event_hooks={"request": [hook]}, transport=httpx.MockTransport(model.handle)
                    )
                    adapter = StreamChatProvider(make_client(model, http_client=http))
                    with self.assertRaises(stop_type) as seen:
                        self.operations(adapter, World("hook"))[index]()
                    self.assertIs(seen.exception, raised)
                    self.assertEqual(model.recording, [])  # nothing reached the transport

    def test_each_stop_type_propagates_unchanged_from_a_response_hook(self) -> None:
        for stop_type in STOP_TYPES:
            for index, operation in enumerate(OPERATIONS):
                with self.subTest(stop=stop_type.__name__, operation=operation):
                    raised = stop_type("stopped on the response")

                    def hook(response: httpx.Response, raised: BaseException = raised) -> None:
                        raise raised

                    model = RecordedStream()
                    http = httpx.Client(
                        event_hooks={"response": [hook]},
                        transport=httpx.MockTransport(model.handle),
                    )
                    adapter = StreamChatProvider(make_client(model, http_client=http))
                    with self.assertRaises(stop_type) as seen:
                        self.operations(adapter, World("hook"))[index]()
                    self.assertIs(seen.exception, raised)

    def test_a_transport_failure_and_a_timeout_are_provider_unavailable(self) -> None:
        """DM-16 5.2, offline: the code delivery retries."""
        w = World("tr")
        for make in (
            lambda request: httpx.ConnectError("refused", request=request),
            lambda request: httpx.ReadTimeout("slow", request=request),
            lambda request: httpx.RemoteProtocolError("closed", request=request),
        ):
            for index, operation in enumerate(OPERATIONS):
                with self.subTest(failure=make(None).__class__.__name__, operation=operation):
                    model = RecordedStream()
                    adapter = StreamChatProvider(make_client(model))
                    model.fail_next(make)
                    with self.assertRaises(StreamProviderError) as seen:
                        self.operations(adapter, w)[index]()
                    self.assertEqual(seen.exception.code, PROVIDER_UNAVAILABLE)
                    self.assertTrue(seen.exception.retryable)
                    self.assertIsNone(seen.exception.status)
                    self.assertIsNone(seen.exception.__cause__)  # no provider text travels

    def test_an_httpx_transport_error_raised_directly_is_mapped_too(self) -> None:
        class Raising:
            def query_users(self, payload: Any) -> Any:
                raise httpx.ConnectTimeout("slow")

        with self.assertRaises(StreamProviderError) as seen:
            StreamChatProvider(Raising()).provision_user("u")
        self.assertEqual(seen.exception.code, PROVIDER_UNAVAILABLE)


class CodesFromStatusAndNumberTests(unittest.TestCase):
    """DM-16 4.5: each mapping is decided by the HTTP status and Stream's numeric code."""

    def setUp(self) -> None:
        self.model = RecordedStream()
        self.adapter = StreamChatProvider(make_client(self.model))
        self.w = World("cd")
        self.adapter.provision_user(self.w.a)
        self.adapter.provision_user(self.w.b)
        self.adapter.create_channel(self.w.c, (self.w.a, self.w.b))

    def send(self) -> StreamProviderError:
        with self.assertRaises(StreamProviderError) as seen:
            self.adapter.send_message(self.w.c, self.w.a, self.w.m1, "hello")
        return seen.exception

    def test_a_5xx_a_429_and_an_unreadable_success_are_provider_unavailable(self) -> None:
        for status, code in ((500, 0), (502, 0), (429, 9)):
            with self.subTest(status=status):
                self.model.refuse_next(status, code, "server")
                error = self.send()
                self.assertEqual(
                    (error.code, error.status, error.number), (PROVIDER_UNAVAILABLE, status, code)
                )
        self.model.answer_next(
            201, {"duration": "1ms", "message": {"id": "another-id", "created_at": 1}}
        )
        self.assertEqual(self.send().code, PROVIDER_REJECTED)  # Stream answered with another ID
        # A success whose body the SDK cannot decode: getstream 6.1.0 re-parses the body as
        # its error envelope and raises its own KeyError, which is not one of the SDK's API
        # or transport errors, so it propagates unchanged (4.1); delivery maps it to
        # provider_unavailable and retries, and the retry meets the existing message.
        self.model.answer_next(201, {"duration": "1ms", "message": "not an object"})
        with self.assertRaises(KeyError):
            self.adapter.send_message(self.w.c, self.w.a, self.w.m1, "hello")

    def test_404_with_code_16_is_the_operations_missing_object(self) -> None:
        self.model.refuse_next(404, 16, 'SendMessage failed with error: "channel not found"')
        error = self.send()
        self.assertEqual((error.code, error.status, error.number), (CHANNEL_UNAVAILABLE, 404, 16))
        self.model.refuse_next(404, 16, 'UpdateChannel failed with error: "channel not found"')
        with self.assertRaises(StreamProviderError) as removal:
            # The read finds the channel; the write is refused.
            self.adapter.remove_members(self.w.c, (self.w.a, self.w.b))
        self.assertEqual(removal.exception.code, CHANNEL_UNAVAILABLE)
        self.model.recording.clear()
        self.model.refuse_next(404, 16, 'DeactivateUser failed with error: "user not found"')
        with self.assertRaises(StreamProviderError) as deactivation:
            self.adapter.deactivate_user(self.w.a)
        self.assertEqual(deactivation.exception.code, MEMBER_UNAVAILABLE)

    def test_other_4xx_answers_are_provider_rejected(self) -> None:
        for status, code in ((403, 17), (401, 5), (400, 4), (409, 4), (400, 99)):
            with self.subTest(status=status, code=code):
                self.model.refuse_next(status, code, "refused")
                error = self.send()
                self.assertEqual(
                    (error.code, error.status, error.number), (PROVIDER_REJECTED, status, code)
                )
                self.assertFalse(error.retryable)

    def test_the_text_of_a_sends_input_error_is_tested_in_memory_only(self) -> None:
        self.model.refuse_next(
            400, 4, 'SendMessage failed with error: "a message with ID x already exists"'
        )
        receipt = self.adapter.send_message(self.w.c, self.w.a, self.w.m1, "hello")
        self.assertEqual(receipt, ProviderReceipt(self.w.m1, already=True))
        self.model.refuse_next(400, 4, 'SendMessage failed with error: "user u does not exist"')
        self.assertEqual(self.send().code, MEMBER_UNAVAILABLE)
        self.model.refuse_next(404, 16, 'SendMessage failed with error: "user u is deactivated"')
        self.assertEqual(self.send().code, MEMBER_UNAVAILABLE)
        self.model.refuse_next(400, 4, 'SendMessage failed with error: "text is too long"')
        error = self.send()
        self.assertEqual(error.code, PROVIDER_REJECTED)
        # Nothing of Stream's text is kept: the error carries the code and two numbers.
        self.assertEqual(str(error), PROVIDER_REJECTED)
        self.assertEqual(
            {k: v for k, v in vars(error).items() if not k.startswith("_")},
            {"code": PROVIDER_REJECTED, "status": 400, "number": 4},
        )

    def test_the_error_is_a_chat_provider_error_with_a_glow_code_only(self) -> None:
        error = StreamProviderError(MEMBER_UNAVAILABLE, status=404, number=16)
        self.assertIsInstance(error, ChatProviderError)
        self.assertEqual(str(error), MEMBER_UNAVAILABLE)
        with self.assertRaises(ValueError):
            StreamProviderError("not a glow code")  # type: ignore[arg-type]


class RepeatNeverUndoesTests(unittest.TestCase):
    """DM-16 4.4, offline: the read-first paths on the recording."""

    def setUp(self) -> None:
        self.model = RecordedStream()
        self.adapter = StreamChatProvider(make_client(self.model))
        self.w = World("rp")

    def test_provisioning_never_changes_an_existing_user(self) -> None:
        self.adapter.provision_user(self.w.a)
        self.model.users[self.w.a]["deactivated_at"] = 7
        self.model.users[self.w.a]["revoke_tokens_issued_before"] = 9
        self.model.recording.clear()
        receipt = self.adapter.provision_user(self.w.a)
        self.assertTrue(receipt.already)
        self.assertEqual([r["method"] for r in self.model.recording], ["GET"])
        self.assertEqual(
            (
                self.model.users[self.w.a]["deactivated_at"],
                self.model.users[self.w.a]["revoke_tokens_issued_before"],
            ),
            (7, 9),
        )

    def test_a_repeated_creation_after_a_removal_does_not_re_add_the_members(self) -> None:
        self.adapter.provision_user(self.w.a)
        self.adapter.provision_user(self.w.b)
        self.adapter.create_channel(self.w.c, (self.w.a, self.w.b))
        self.adapter.remove_members(self.w.c, (self.w.a, self.w.b))
        self.model.recording.clear()
        receipt = self.adapter.create_channel(self.w.c, (self.w.a, self.w.b))
        self.assertTrue(receipt.already)
        self.assertEqual(self.model.channels[self.w.c]["members"], [])
        self.assertFalse(any(r["path"].endswith("/query") for r in self.model.recording))

    def test_deactivation_and_revocation_never_create_a_user(self) -> None:
        for call in (
            lambda: self.adapter.deactivate_user(self.w.unknown),
            lambda: self.adapter.revoke_user_tokens(self.w.unknown, revocation_cutoff_sent(NOW)),
        ):
            self.model.recording.clear()
            with self.assertRaises(StreamProviderError) as seen:
                call()
            self.assertEqual(seen.exception.code, MEMBER_UNAVAILABLE)
            self.assertEqual([r["method"] for r in self.model.recording], ["GET"])
        self.assertNotIn(self.w.unknown, self.model.users)

    def test_a_revocation_never_lowers_the_cut_off_stream_holds(self) -> None:
        self.adapter.provision_user(self.w.e)
        later = revocation_cutoff_sent(NOW + timedelta(minutes=5))
        earlier = revocation_cutoff_sent(NOW)
        self.assertFalse(self.adapter.revoke_user_tokens(self.w.e, later).already)
        self.model.recording.clear()
        self.assertTrue(self.adapter.revoke_user_tokens(self.w.e, earlier).already)
        self.assertTrue(self.adapter.revoke_user_tokens(self.w.e, later).already)
        self.assertEqual([r["method"] for r in self.model.recording], ["GET", "GET"])
        self.assertEqual(self.model.users[self.w.e]["revoke_tokens_issued_before"], _ns(later))

    def test_the_cut_off_is_sent_as_given_never_rounded_here(self) -> None:
        self.adapter.provision_user(self.w.e)
        exact = datetime(2026, 10, 23, 12, 30, 0, 123456, tzinfo=UTC)
        self.model.recording.clear()
        self.adapter.revoke_user_tokens(self.w.e, exact)
        sent = self.model.recording[-1]["body"]["users"][0]["set"]["revoke_tokens_issued_before"]
        self.assertEqual(sent, "2026-10-23T12:30:00.123456Z")
        with self.assertRaises(ValueError):
            self.adapter.revoke_user_tokens(self.w.e, exact.replace(tzinfo=None))


class SignerTests(unittest.TestCase):
    """DM-16 3.1 to 3.3: the pre-approved signer, against the SDK's own token."""

    def grant(self, issued_at: datetime) -> TokenGrant:
        return TokenGrant("user-ref", issued_at, issued_at + timedelta(hours=1))

    def test_iat_and_exp_are_the_grants_truncated_to_the_second_and_never_later(self) -> None:
        issued = datetime(2026, 10, 23, 12, 0, 0, 999_999, tzinfo=UTC)
        claims = token_claims(self.grant(issued))
        self.assertEqual(
            claims,
            {"user_id": "user-ref", "iat": 1792756800 - IAT_BACKDATE_SECONDS, "exp": 1792760400},
        )
        self.assertLessEqual(claims["iat"], int(issued.timestamp()))
        self.assertLessEqual(claims["exp"], int((issued + timedelta(hours=1)).timestamp()))
        self.assertEqual(claims["exp"] - claims["iat"], 3600 + IAT_BACKDATE_SECONDS)

    def test_the_backdate_is_fixed_and_at_most_five_seconds(self) -> None:
        self.assertIsInstance(IAT_BACKDATE_SECONDS, int)
        self.assertGreaterEqual(IAT_BACKDATE_SECONDS, 0)
        self.assertLessEqual(IAT_BACKDATE_SECONDS, 5)

    def test_a_naive_time_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            token_claims(self.grant(datetime(2026, 10, 23, 12, 0, 0)))

    def test_the_signers_token_matches_the_sdks_in_header_and_claim_names(self) -> None:
        client = make_client(RecordedStream())
        ours = sign_chat_token(self.grant(NOW), client)
        theirs = client.create_token("user-ref", expiration=3600)
        self.assertEqual(jwt.get_unverified_header(ours), {"alg": "HS256", "typ": "JWT"})
        self.assertEqual(jwt.get_unverified_header(ours), jwt.get_unverified_header(theirs))
        decoded = jwt.decode(ours, SECRET, algorithms=["HS256"], options={"verify_exp": False})
        self.assertEqual(set(decoded), {"user_id", "iat", "exp"})
        self.assertEqual(set(decoded), set(jwt.decode(theirs, SECRET, algorithms=["HS256"])))
        self.assertEqual(
            decoded,
            {
                "user_id": "user-ref",
                "iat": int(NOW.timestamp()) - IAT_BACKDATE_SECONDS,
                "exp": int(NOW.timestamp()) + 3600,
            },
        )
        # The SDK's own claims come from its clock: iat now - 5 and exp now + lifetime.
        sdk_claims = jwt.decode(theirs, SECRET, algorithms=["HS256"])
        self.assertAlmostEqual(sdk_claims["iat"], int(time.time()) - 5, delta=3)

    def test_a_token_signed_with_a_wrong_key_fails_verification(self) -> None:
        token = sign_chat_token(self.grant(NOW), make_client(RecordedStream()))
        with self.assertRaises(jwt.InvalidSignatureError):
            jwt.decode(
                token,
                "another-synthetic-value",
                algorithms=["HS256"],
                options={"verify_exp": False},
            )

    def test_the_signer_keeps_nothing(self) -> None:
        source = inspect.getsource(adapter_module)
        self.assertNotIn("os.environ", source)
        self.assertNotIn("getenv", source)
        self.assertNotIn("from_env", source.split('"""', 2)[2])  # outside the docstring
        self.assertNotIn("Stream(", source.split('"""', 2)[2])
        self.assertIn("client.api_secret", source)


class SealTests(unittest.TestCase):
    """DM-16 2.3, 2.4: the module imports only the port, the token module and the SDK."""

    def test_the_module_imports_nothing_from_django_glow_persistence_or_glow_chat(self) -> None:
        source = inspect.getsource(adapter_module)
        imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
        self.assertTrue(imports)
        for line in imports:
            self.assertNotRegex(line, r"django|glow_persistence|glow_chat|glow_api")
        own = [line for line in imports if line.startswith("from .")]
        self.assertEqual(
            sorted(own),
            sorted(["from .chat_provider import (", "from .chat_tokens import TokenGrant"]),
        )

    def test_the_sdks_errors_are_the_only_ones_mapped(self) -> None:
        source = inspect.getsource(adapter_module)
        caught = set(re.findall(r"except \(([^)]*)\)", source))
        self.assertEqual(
            caught, {"StreamApiException, StreamTransportException, httpx.TransportError"}
        )
        self.assertNotIn("except Exception", source)
        self.assertNotIn("except BaseException", source)
        self.assertIsInstance(StreamApiException(status_code=400), Exception)
        self.assertIsInstance(StreamTransportException("timeout"), Exception)


if __name__ == "__main__":
    unittest.main()
