"""Drive a whole proof run against fakes: no network, no Stream, no Node.

This does not test Stream. It checks that the orchestration reaches every
case, records a result for each, never reports a harness error, and cleans up.
"""

import json
import unittest
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import jwt

import tests  # noqa: F401
from glow_stream_proof import configuration, matrix, proof_run
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.credentials import ServerCredentials
from glow_stream_proof.proof_run import ProofRun
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import UsageLedger

SECRET = "simulation-secret-for-offline-tests-only"


def ok(method: str, path: str, body: Any, status: int = 201) -> ApiResult:
    return ApiResult(method, path, status, None, None, body)


@dataclass
class FakeServer:
    ledger: UsageLedger
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    members: dict[str, list[str]] = field(default_factory=dict)
    sent: int = 0

    def __post_init__(self) -> None:
        self.sdk = SimpleNamespace(
            upsert_users=self._upsert,
            chat=SimpleNamespace(
                get_or_create_channel=self._channel, send_message=self._send_message
            ),
            create_token=self._token,
        )

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
        return SimpleNamespace(data=SimpleNamespace(message=SimpleNamespace(id=f"m-{self.sent}")))

    @staticmethod
    def _token(user_id: str, expiration: int) -> str:
        return jwt.encode({"user_id": user_id, "iat": 0, "exp": expiration}, SECRET, "HS256")

    def raw(
        self, method: str, path: str, *, body: Any = None, params: dict[str, str] | None = None
    ) -> ApiResult:
        self._count()
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
            return ok(method, path, {"channels": []}, 200)
        if path.startswith("/api/v2/tasks/"):
            return ok(method, path, {"status": "completed"}, 200)
        if path.endswith("/delete"):
            return ok(method, path, {"task_id": "t1"})
        if path == "/polls":
            return ok(method, path, {"poll": {"id": "p1", "options": [{"id": "o1"}]}})
        if path.endswith("/message"):
            return ok(method, path, {"message": {"id": "m-poll"}})
        if path == "/api/v2/chat/channeltypes/glow-match" and method == "GET":
            return ok(method, path, dict(configuration.MATCH_FEATURES), 200)
        if path == "/api/v2/app" and method == "GET":
            return ok(method, path, {"app": {"guest_user_creation_disabled": True}}, 200)
        if path in ("/api/v2/app", "/api/v2/chat/channeltypes", "/api/v2/roles"):
            return ok(method, path, {"app": {}, "channel_types": {}, "roles": []}, 200)
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

    def create_guest(self, user: dict[str, Any]) -> tuple[ApiResult, str]:
        self._count()
        self.users[user["id"]] = {"id": user["id"], "role": "guest", "created_at": 0}
        return ok("POST", "/guest", {"user": {"id": user["id"], "role": "guest"}}), "guest-token"

    def raw_multipart(self, path: str, **_kwargs: Any) -> ApiResult:
        self._count()
        return ok("POST", path, {"file": "https://cdn.invalid/f"})


class FakeSession:
    """A client that is refused everything except connecting and reading its own events."""

    def __init__(self, label: str) -> None:
        self.label = label

    def send(self, op: str, **params: Any) -> Reply:
        if op in ("connect", "disconnect", "set_rest_user", "anonymous"):
            user = params.get("user") or {"id": "anon"}
            return Reply(True, {"me": {"id": user["id"], "role": "user"}}, None)
        if op == "events":
            return Reply(True, {"events": []}, None)
        if op == "guest":
            if self.label == "guest":
                return Reply(True, {"me": {"id": params["user"]["id"], "role": "guest"}}, None)
            return Reply(False, None, {"status": 403, "code": 17, "message": "no"})
        record: dict[str, Any] = {
            "method": "POST",
            "path": "/channels/glow-match/x/query",
            "params": {"payload": {"filter_conditions": {}}, "user_id": "u", "api_key": "k"},
            "body": {"data": {"members": ["a"]}},
            "status": 403 if self.label != "X" else 201,
            "response": {"code": 17} if self.label != "X" else {"channels": []},
        }
        if self.label == "X":
            return Reply(True, {}, None, [record], api_calls=1)
        return Reply(False, None, {"status": 403, "code": 17, "message": "denied"}, [record], 1)

    def close(self) -> None:
        pass


class SimulationTest(unittest.TestCase):
    def setUp(self) -> None:
        self._settle = proof_run.TYPE_CHANGE_SETTLE_SECONDS
        proof_run.TYPE_CHANGE_SETTLE_SECONDS = 0

    def tearDown(self) -> None:
        proof_run.TYPE_CHANGE_SETTLE_SECONDS = self._settle

    def test_full_orchestration_against_fakes(self) -> None:
        ledger = UsageLedger()
        server = FakeServer(ledger)
        creds = ServerCredentials("1729640", "k", SECRET)
        run = ProofRun(
            creds,
            server,  # type: ignore[arg-type]
            ledger,
            Redactor([SECRET]),
            {},
            prefix="p061i1-simulated",
            accept_dashboard_user=True,
        )
        sessions: dict[str, Any] = run.sessions

        def fake_session(label: str, token: str | None, **_: Any) -> Any:
            return sessions.setdefault(label, FakeSession(label))

        run._session = fake_session  # type: ignore[method-assign]
        run._events = lambda key, wait_ms=0: []  # type: ignore[method-assign]
        run.verify_clean = lambda: {"remaining_proof_users": []}  # type: ignore[method-assign]
        run.setup()
        run.authorized_path()
        run.run_matrix()
        run.cleanup()
        results = run.results()
        self.assertEqual(len(results["cases"]), len(matrix.all_cases()))
        errors = [c["case_id"] for c in results["cases"] if "harness error" in c["observed"]]
        self.assertEqual(errors, [])
        self.assertIn("AP11", {c["check_id"] for c in results["checks"]})
        self.assertIn("users_task", results["cleanup"])
        self.assertLessEqual(ledger.run.users, 20)
        self.assertIn("guest_id", run.ctx)


if __name__ == "__main__":
    unittest.main()
