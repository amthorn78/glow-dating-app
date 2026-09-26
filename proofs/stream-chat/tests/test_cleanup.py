"""Nits 5, 12 and 13: cleanup is guarded and judged, has enough budget, and
removes the polls and user groups a client managed to create."""

import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix, proof_run
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.proof_run import TemporaryChange, cleanup_problems
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import UsageLedger
from tests.fakes import FakeSession, NoSettle, error, make_run, ok, record, set_up

CLEAN: dict[str, Any] = {
    "errors": [],
    "polls": [200],
    "user_groups": [200],
    "channels_delete": 201,
    "channels_task": "completed",
    "users_delete": 201,
    "users_task": "completed",
    "remaining_proof_users": [],
    "remaining_channels": [],
    "remaining_polls": [],
    "remaining_user_groups": [],
    "deleted_user_artifacts_remaining": 0,
}


class CleanupProblemsTest(unittest.TestCase):
    def test_clean(self) -> None:
        self.assertEqual(cleanup_problems(CLEAN), [])

    def test_each_problem_is_reported(self) -> None:
        cases = {
            "errors": (["users: RuntimeError: boom"], "cleanup error"),
            "polls": ([200, 404], "polls delete statuses [404]"),
            "channels_task": ("running", "channels_task is 'running'"),
            "users_delete": (500, "users_delete got 500"),
            "remaining_proof_users": (["p061i1-x-ua"], "remaining_proof_users"),
            "remaining_polls": (["poll-1"], "remaining_polls"),
            "deleted_user_artifacts_remaining": (1, "deleted-user artifacts remaining"),
        }
        for key, (value, expected) in cases.items():
            problems = cleanup_problems({**CLEAN, key: value})
            self.assertTrue(any(expected in p for p in problems), (key, problems))

    def test_unlisted_or_unchecked_leftovers_are_problems(self) -> None:
        listing = {**CLEAN, "remaining_polls": None, "polls_listing": "not verified: HTTP 400"}
        self.assertIn("remaining_polls: not verified: HTTP 400", cleanup_problems(listing))
        unchecked = {k: v for k, v in CLEAN.items() if k != "remaining_channels"}
        self.assertIn("remaining_channels: not checked", cleanup_problems(unchecked))


class GuardedCleanupTest(unittest.TestCase):
    def test_a_failing_step_does_not_stop_the_others(self) -> None:
        run, server = make_run()
        with NoSettle():
            set_up(run)
        run.polls.append(("p-1", run.ctx["B"]))

        def broken_poll_delete(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "DELETE" and path.startswith("/polls/"):
                raise RuntimeError("connection reset")
            return None

        server.handlers.append(broken_poll_delete)
        with NoSettle():
            out = run.cleanup()
        self.assertEqual(out["users_task"], "completed")
        self.assertEqual(out["remaining_proof_users"], [])
        self.assertTrue(any("polls: RuntimeError" in e for e in out["errors"]))
        self.assertTrue(any("cleanup error" in p for p in cleanup_problems(out)))

    def test_task_that_does_not_complete_is_a_problem(self) -> None:
        run, server = make_run()
        with NoSettle():
            set_up(run)
        server.task_status = "failed"
        with NoSettle():
            problems = cleanup_problems(run.cleanup())
        self.assertIn("channels_task is 'failed', not 'completed'", problems)


class CleanupReserveTest(unittest.TestCase):
    def test_reserve_covers_the_worst_case_end_of_run(self) -> None:
        """Every delete task polled to its limit, polls, groups and a journal restore."""
        ledger = UsageLedger()
        run, server = make_run(ledger=ledger)
        with NoSettle():
            set_up(run)
        run.polls += [("p-1", run.ctx["B"]), ("p-2", run.ctx["A"])]
        run.ctx["ctl_poll"] = "p-3"
        run.groups.append("g-1")
        run.ctx["ctl_group"] = "g-2"
        run.journal.append(
            TemporaryChange("guest user creation enabled", run._disable_guest_creation)
        )
        server.task_status = "running"
        artifact = f"deleted-user-{run.credentials.app_id}-abc"

        def artifact_user(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "GET" and path == "/api/v2/users":
                user = {"id": artifact, "created_at": run.started_ns + 1}
                return ok(method, path, {"users": list(server.users.values()) + [user]}, 200)
            return None

        server.handlers.append(artifact_user)
        before = ledger.run.api_calls
        with NoSettle():
            run.finish(cleanup=True)
        used = ledger.run.api_calls - before
        self.assertGreater(used, 100)
        self.assertLessEqual(used, proof_run.CLEANUP_RESERVE)


class ClientCreatedDataTest(unittest.TestCase):
    def test_client_created_poll_and_group_are_deleted(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            method = params.get("method")
            if op == "call" and method == "createPoll":
                body = {"poll": {"id": "client-poll", "created_by_id": "a-id"}}
                return Reply(True, {}, None, [record(201, body, path="/polls")], api_calls=1)
            if op == "call" and method == "createUserGroup":
                body = {"user_group": {"id": "client-group"}}
                return Reply(True, {}, None, [record(201, body, path="/usergroups")], api_calls=1)
            return None

        run, server = make_run(behaviours={"A": a})
        with NoSettle():
            set_up(run)
            run.run_matrix({"S9", "S16"})
            run.cleanup()
        verdicts = {c.case_id: c.verdict for c in run.case_results}
        self.assertEqual(verdicts, {"S9": matrix.FAIL, "S16": matrix.FAIL})
        deleted = {path for method, path, _ in server.calls if method == "DELETE"}
        self.assertIn("/polls/client-poll", deleted)
        self.assertIn("/api/v2/usergroups/client-group", deleted)

    def test_verify_clean_lists_polls_and_user_groups(self) -> None:
        run, server = make_run()

        def leftovers(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if path == "/api/v2/polls/query":
                return ok(method, path, {"polls": [{"id": "left-poll"}]}, 201)
            if path == "/api/v2/usergroups" and method == "GET":
                return error(method, path, 400, 4, "not supported")
            return None

        server.handlers.append(leftovers)
        out = run.verify_clean()
        self.assertEqual(out["remaining_polls"], ["left-poll"])
        self.assertIsNone(out["remaining_user_groups"])
        problems = cleanup_problems({**CLEAN, **out})
        self.assertIn("remaining_polls: ['left-poll']", problems)
        self.assertIn("remaining_user_groups: not verified: HTTP 400 code 4", problems)


if __name__ == "__main__":
    unittest.main()
