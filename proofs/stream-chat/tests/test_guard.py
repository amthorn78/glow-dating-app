"""P06.1-I2a, DM-04 finding 1: one guard for every server call that changes something.

Before a server request is sent, the guard refuses it when it acts on a user,
channel, message, poll or group the run did not create, when it changes an
application setting outside the run's journal, or when it is not a kind of
request the proof makes. The guard runs in the server client's request hook, so
a refused request is neither sent nor counted: the hook tests drive the real
``ServerApi`` on an ``httpx.MockTransport``. The fakes ask the same guard, so every
offline run is guarded as a live one is.
"""

import unittest
from datetime import UTC, datetime
from typing import Any

import httpx
from getstream.models import UserRequest

import tests  # noqa: F401
from glow_stream_proof import cli, guard, matrix
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.credentials import ServerCredentials
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.server_api import ServerApi
from glow_stream_proof.stops import GuardRefused, RunStopped
from glow_stream_proof.usage import UsageLedger
from tests.fakes import PREFIX, FakeServer, FakeSession, NoSettle, make_run, record, set_up

RUN = "p061i1-0926000000"
A, B = f"{RUN}-ua", f"{RUN}-ub"
AB = f"glow-match:{RUN}-ch-ab"
# Stand-ins for what the run did not create: the dashboard user and another channel.
FOREIGN_USER = "dashboard-owner-7f3a"
FOREIGN_CHANNEL = "messaging:someone-elses-channel"
T = "glow-match"


class Scope(guard.PrefixScope):
    """A run's scope: its prefix, and a journal the test sets."""

    app_settings: frozenset[str] = frozenset()
    type_features: frozenset[str] = frozenset()
    messages: frozenset[str] = frozenset({"m-recorded"})

    def owns_message(self, message_id: str) -> bool:
        return message_id in self.messages

    def owns_poll(self, poll_id: str) -> bool:
        return poll_id == "poll-recorded"

    def owns_group(self, group_id: str) -> bool:
        return group_id == "group-recorded"

    def journalled_app_settings(self) -> frozenset[str]:
        return self.app_settings

    def journalled_type_features(self) -> frozenset[str]:
        return self.type_features


def refusal(
    method: str,
    path: str,
    body: Any = None,
    params: dict[str, str] | None = None,
    scope: guard.Scope | None = None,
) -> str | None:
    return guard.refusal(method, path, body, params, scope or Scope(RUN))


def user_calls(user: str, channel: str = AB) -> list[tuple[str, str, Any, dict[str, str]]]:
    """Every kind of server call that acts on ``user``: one each for ban, deactivate,
    delete, token revocation, hide, member removal, and user and member updates."""
    ch_type, ch_id = channel.split(":")
    return [
        ("POST", "/api/v2/users/delete", {"user_ids": [user], "user": "hard"}, {}),
        ("POST", "/api/v2/users/deactivate", {"user_ids": [user]}, {}),
        ("POST", f"/api/v2/users/{user}/deactivate", {"mark_messages_deleted": False}, {}),
        ("POST", "/api/v2/users/reactivate", {"user_ids": [user]}, {}),
        (
            "PATCH",
            "/api/v2/users",
            {"users": [{"id": user, "set": {"revoke_tokens_issued_before": "2026-09-26"}}]},
            {},
        ),
        ("POST", "/api/v2/users", {"users": {user: {"id": user, "role": "user"}}}, {}),
        ("PATCH", "/users", {"users": [{"id": user, "set": {"name": "x"}}]}, {}),
        ("POST", "/api/v2/moderation/ban", {"target_user_id": user, "channel_cid": channel}, {}),
        ("POST", "/api/v2/moderation/unban", None, {"target_user_id": user}),
        ("POST", "/moderation/ban", {"target_user_id": user, "type": ch_type, "id": ch_id}, {}),
        ("DELETE", "/moderation/ban", None, {"target_user_id": user}),
        ("POST", f"/api/v2/chat/channels/{ch_type}/{ch_id}/hide", {"user_id": user}, {}),
        ("POST", f"/api/v2/chat/channels/{ch_type}/{ch_id}/show", {"user_id": user}, {}),
        ("POST", f"/channels/{ch_type}/{ch_id}", {"remove_members": [user]}, {}),
        ("POST", f"/channels/{ch_type}/{ch_id}", {"add_members": [{"user_id": user}]}, {}),
        ("PATCH", f"/api/v2/chat/channels/{ch_type}/{ch_id}/member", {}, {"user_id": user}),
        # The deprecated member path names the member in the path (P06.1-I2a, step 2).
        ("PATCH", f"/channels/{ch_type}/{ch_id}/member/{user}", {"set": {"x": 1}}, {}),
        ("POST", "/api/v2/users/block", {"blocked_user_id": user, "user_id": A}, {}),
        ("POST", "/api/v2/guest", {"user": {"id": user}}, {}),
        # The muted user is the target (P06.1-I2a; the independent review).
        ("POST", "/api/v2/moderation/mute", {"target_id": user, "user_id": A}, {}),
    ]


def channel_calls(channel: str) -> list[tuple[str, str, Any, dict[str, str]]]:
    """Every kind of server call that acts on ``channel`` (for the run's own user A)."""
    ch_type, ch_id = channel.split(":")
    return [
        ("DELETE", f"/api/v2/chat/channels/{ch_type}/{ch_id}", None, {"hard_delete": "true"}),
        ("POST", "/api/v2/chat/channels/delete", {"cids": [channel], "hard_delete": True}, {}),
        ("PATCH", f"/channels/{ch_type}/{ch_id}", {"set": {"frozen": True}}, {}),
        ("POST", f"/channels/{ch_type}/{ch_id}/truncate", {}, {}),
        ("POST", f"/api/v2/chat/channels/{ch_type}/{ch_id}/hide", {"user_id": A}, {}),
        ("POST", f"/channels/{ch_type}/{ch_id}", {"remove_members": [A]}, {}),
        ("PATCH", f"/channels/{ch_type}/{ch_id}/member", {"set": {"x": 1}}, {"user_id": A}),
        ("POST", f"/channels/{ch_type}/{ch_id}/message", {"message": {"user_id": A}}, {}),
        ("POST", "/api/v2/moderation/ban", {"target_user_id": A, "channel_cid": channel}, {}),
        ("POST", "/moderation/ban", {"target_user_id": A, "type": ch_type, "id": ch_id}, {}),
        ("DELETE", "/moderation/ban", None, {"target_user_id": A, "type": ch_type, "id": ch_id}),
    ]


class RefusalTest(unittest.TestCase):
    def test_reads_are_never_refused(self) -> None:
        for method, path in (
            ("GET", "/api/v2/users"),
            ("GET", f"/api/v2/users/{FOREIGN_USER}/export"),
            ("GET", "/api/v2/app"),
            ("POST", "/api/v2/chat/channels"),
            ("POST", "/api/v2/polls/query"),
            ("POST", "/api/v2/chat/messages/history"),
            ("HEAD", "/api/v2/chat/channels"),
        ):
            self.assertIsNone(refusal(method, path, {"user_ids": [FOREIGN_USER]}), path)

    def test_the_runs_own_users_and_channels_pass(self) -> None:
        for method, path, body, params in user_calls(A) + channel_calls(AB):
            self.assertIsNone(refusal(method, path, body, params), (method, path))
        recorded = Scope(RUN, users={"guest-1234-requested"}, channels={"commerce:recorded"})
        self.assertIsNone(
            refusal(
                "POST",
                "/api/v2/users/delete",
                {"user_ids": ["guest-1234-requested"]},
                None,
                recorded,
            )
        )
        self.assertIsNone(
            refusal(
                "POST",
                "/api/v2/chat/channels/delete",
                {"cids": ["commerce:recorded"]},
                None,
                recorded,
            )
        )

    def test_a_user_the_run_did_not_create_is_refused(self) -> None:
        for method, path, body, params in user_calls(FOREIGN_USER):
            refused = refusal(method, path, body, params)
            self.assertIsNotNone(refused, (method, path))
            assert refused is not None
            self.assertIn("a user ID this run did not create", refused)
            self.assertNotIn(FOREIGN_USER, refused)  # never names the identifier

    def test_a_channel_the_run_did_not_create_is_refused(self) -> None:
        for method, path, body, params in channel_calls(FOREIGN_CHANNEL):
            refused = refusal(method, path, body, params)
            self.assertIsNotNone(refused, (method, path))
            assert refused is not None
            self.assertIn("a channel this run did not create", refused)
            self.assertNotIn("someone-elses-channel", refused)

    def test_application_changes_outside_the_journal_are_refused(self) -> None:
        revoke_all = {"revoke_tokens_issued_before": "2026-09-26T12:00:00Z"}
        guest = {"guest_user_creation_disabled": False}
        for method, body in (
            ("PATCH", revoke_all),  # an application-wide token revocation
            ("PATCH", guest),  # guest creation, with nothing in the journal
            ("PATCH", {"webhook_url": "https://hooks.invalid/x"}),
            ("PATCH", {}),
            ("POST", guest),
            ("PUT", guest),
        ):
            for path in ("/api/v2/app", "/app"):
                refused = refusal(method, path, body)
                self.assertIsNotNone(refused, (method, path, body))
                assert refused is not None
                self.assertIn("not a journalled temporary setting", refused)
        journalled = Scope(RUN)
        journalled.app_settings = frozenset({"guest_user_creation_disabled"})
        self.assertIsNone(refusal("PATCH", "/api/v2/app", guest, None, journalled))
        both = {**guest, **revoke_all}
        self.assertIsNotNone(refusal("PATCH", "/api/v2/app", both, None, journalled))
        self.assertIsNotNone(refusal("PATCH", "/api/v2/app", revoke_all, None, journalled))

    def test_match_type_changes_outside_the_journal_are_refused(self) -> None:
        on = {"automod": "disabled", "custom_events": True}
        path = f"/api/v2/chat/channeltypes/{T}"
        self.assertIsNotNone(refusal("PUT", path, on))
        journalled = Scope(RUN)
        journalled.type_features = frozenset({"custom_events"})
        self.assertIsNone(refusal("PUT", path, on, None, journalled))
        for method, other_path, body in (
            ("PUT", path, {"custom_events": True, "reactions": True}),  # not journalled
            ("PUT", path, {"automod": "AI", "custom_events": True}),  # a lasting change
            ("PUT", "/api/v2/chat/channeltypes/messaging", {"custom_events": True}),
            ("POST", "/api/v2/chat/channeltypes", {"name": "other"}),
            ("DELETE", path, None),
        ):
            self.assertIsNotNone(refusal(method, other_path, body, None, journalled), body)

    def test_other_kinds_of_change_are_refused(self) -> None:
        for method, path, body in (
            ("PUT", "/api/v2/chat/channels/batch", {"operation": "hide", "filter": {}}),
            ("POST", "/api/v2/chat/retention_policy", {"policy": "old"}),
            ("POST", "/api/v2/roles", {"name": "r"}),
            ("DELETE", "/api/v2/roles/r", None),
            ("POST", "/api/v2/chat/channels/read", {"user_id": A}),
            ("POST", "/api/v2/chat/segments/query-x/addtargets", {}),
            ("POST", "/api/v2/moderation/flag", {"entity_id": A}),
        ):
            refused = refusal(method, path, body)
            self.assertIsNotNone(refused, path)
            assert refused is not None
            self.assertIn("not a kind of request this proof makes", refused)

    def test_a_message_poll_or_group_must_be_the_runs(self) -> None:
        self.assertIsNone(refusal("DELETE", "/messages/m-recorded"))
        self.assertIn("a message this run did not record", str(refusal("DELETE", "/messages/m-x")))
        self.assertIsNone(refusal("POST", "/messages/m-x", {"message": {"user_id": A}}))
        self.assertIsNotNone(
            refusal("POST", "/messages/m-x", {"message": {"user_id": FOREIGN_USER}})
        )
        self.assertIsNone(refusal("DELETE", "/polls/poll-recorded", None, {"user_id": A}))
        self.assertIn("a poll this run did not record", str(refusal("DELETE", "/polls/other")))
        # A poll update names its poll in the body.
        update = {"name": "x", "user_id": A}
        self.assertIsNone(refusal("PUT", "/api/v2/polls", {"id": "poll-recorded", **update}))
        for body in ({"id": "other", **update}, update):
            self.assertIn(
                "a poll this run did not record", str(refusal("PUT", "/api/v2/polls", body))
            )
        self.assertIsNone(refusal("POST", "/polls", {"name": "server poll", "user_id": A}))
        self.assertIsNone(refusal("DELETE", "/api/v2/usergroups/group-recorded"))
        self.assertIn(
            "a user group this run did not record", str(refusal("DELETE", "/api/v2/usergroups/g"))
        )

    def test_a_refusal_names_the_requests_shape_only(self) -> None:
        refused = refusal("POST", f"/api/v2/users/{FOREIGN_USER}/deactivate", {})
        self.assertEqual(
            refused,
            "guard refused POST users/{id}/deactivate: a user ID this run did not create",
        )
        refused = refusal("PATCH", "/channels/messaging/someone-elses-channel", {"set": {}})
        self.assertEqual(
            refused,
            "guard refused PATCH channels/{type}/{id}: a channel this run did not create",
        )


def api_answering() -> tuple[ServerApi, list[str]]:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(f"{request.method} {request.url.path}")
        body = {"duration": "1ms", "users": {}, "membership_deletion_task_id": ""}
        return httpx.Response(200, json=body)

    api = ServerApi(
        ServerCredentials("1729640", "synthetickey", "synthetic-secret-for-the-guard-hook"),
        UsageLedger(),
        Redactor(),
        transport=httpx.MockTransport(handler),
    )
    return api, seen


class ServerHookTest(unittest.TestCase):
    """The hook asks the guard before a request is counted or sent, typed calls too."""

    def test_a_refused_request_is_neither_sent_nor_counted(self) -> None:
        api, seen = api_answering()
        scope = Scope(RUN)
        api.guard = lambda method, path, body, params: guard.refusal(
            method, path, body, params, scope
        )
        try:
            refused_calls = (
                lambda: api.raw("POST", "/api/v2/users/delete", body={"user_ids": [FOREIGN_USER]}),
                lambda: api.sdk.delete_users(user_ids=[FOREIGN_USER], user="hard"),
                lambda: api.sdk.update_app(revoke_tokens_issued_before=datetime.now(UTC)),
                lambda: api.sdk.moderation.ban(target_user_id=FOREIGN_USER, channel_cid=AB),
                lambda: api.sdk.chat.hide_channel(type="messaging", id="other", user_id=A),
                lambda: api.sdk.upsert_users(UserRequest(id=FOREIGN_USER, role="user")),
            )
            for call in refused_calls:
                with self.assertRaises(GuardRefused):
                    call()
            self.assertEqual(seen, [])
            self.assertEqual(api._ledger.run.api_calls, 0)
            api.sdk.update_users_partial(users=[{"id": A, "set": {"name": "n"}}])
            api.raw("GET", "/api/v2/users")
        finally:
            api.close()
        self.assertEqual(seen, ["PATCH /api/v2/users", "GET /api/v2/users"])
        self.assertEqual(api._ledger.run.api_calls, 2)

    def test_a_refusal_stops_the_run(self) -> None:
        self.assertTrue(issubclass(GuardRefused, RunStopped))


class GuardedRunTest(unittest.TestCase):
    """A run installs the guard on its server client, with itself as the scope."""

    def test_the_run_is_the_guards_scope(self) -> None:
        run, server = make_run()
        self.assertIsNotNone(server.guard)
        with NoSettle():
            set_up(run)
        with self.assertRaises(GuardRefused):
            server.raw("POST", "/api/v2/users/delete", body={"user_ids": ["dashboard-owner"]})
        with self.assertRaises(GuardRefused):
            server.raw("PATCH", "/api/v2/app", body={"guest_user_creation_disabled": False})
        server.raw("POST", "/api/v2/users/delete", body={"user_ids": [run.ctx["A"]]})
        change = run._guest_creation_change()
        run.journal.append(change)
        server.raw("PATCH", "/api/v2/app", body={"guest_user_creation_disabled": False})
        run.journal.remove(change)
        with self.assertRaises(GuardRefused):
            server.raw("PATCH", "/api/v2/app", body={"guest_user_creation_disabled": True})

    def test_a_refusal_in_a_case_stops_the_run_after_its_row(self) -> None:
        # A's request, as recorded, names another channel; the server replay (the
        # control) would act on it, so the guard refuses it and the run stops.
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendMessage":
                rec = record(403, {"code": 17}, path="/channels/messaging/someone-else/message")
                error = {"status": 403, "code": 17, "message": "no", "kind": "api"}
                return Reply(False, None, error, [rec], api_calls=1)
            return None

        run, server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = a
            with self.assertRaises(GuardRefused):
                run.run_matrix({"S1", "S3a"})
        self.assertEqual([c.case_id for c in run.case_results], ["S1"])
        row = run.case_results[0]
        self.assertEqual(row.verdict, matrix.INCONCLUSIVE)
        self.assertIn("guard refused POST channels/{type}/{id}/message", row.detail["interrupted"])
        sent = [p for _m, p, _b in server.calls if "someone-else" in p]
        self.assertEqual(sent, [])

    def test_the_artifact_the_runs_cleanup_creates_may_be_deleted(self) -> None:
        run, server = make_run()
        with NoSettle():
            set_up(run)
        artifact = f"deleted-user-{run.credentials.app_id}-abc"
        server.users[artifact] = {"id": artifact, "created_at": run.started_ns + 1}
        with NoSettle():
            out = run.cleanup()
        self.assertEqual(out["artifact_users_delete"], 201)
        self.assertNotIn(artifact, server.users)
        self.assertEqual(out["errors"], [])


class CleanupCommandTest(unittest.TestCase):
    def test_cleanup_apply_is_guarded_by_the_prefix(self) -> None:
        server = FakeServer(UsageLedger())
        server.users[f"{PREFIX}-ua"] = {"id": f"{PREFIX}-ua"}

        class Context:
            api = server
            redactor = Redactor()
            lines: list[str] = []

            def say(self, text: str) -> None:
                self.lines.append(text)

        self.assertEqual(cli.cmd_cleanup(Context(), apply=True), 0)  # type: ignore[arg-type]
        self.assertIsNotNone(server.guard)
        with self.assertRaises(GuardRefused):
            server.raw("POST", "/api/v2/users/delete", body={"user_ids": ["dashboard-owner"]})


if __name__ == "__main__":
    unittest.main()
