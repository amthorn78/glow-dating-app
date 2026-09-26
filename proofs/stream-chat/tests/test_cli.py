"""The commands, against a fake server: nothing is sent to Stream or written to ``.work``.

- Finding 2 and nit 5: every run ends with the journal restored, cleanup and
  ``configuration.verify()``; any difference or cleanup problem makes the run
  exit non-zero, and so does Ctrl-C, after which the results are still written.
- Nit 8: ``baseline`` writes no other user's identifier or name.
- Nit 10: ``restore --apply`` re-reads and verifies.
"""

import json
import unittest
from collections.abc import Callable
from typing import Any
from unittest import mock

import tests  # noqa: F401
from glow_stream_proof import cli, configuration
from glow_stream_proof.credentials import ServerCredentials
from glow_stream_proof.proof_run import ProofRun, TemporaryChange
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import UsageLedger
from glow_stream_proof.workdir import PROOF_ROOT
from tests.fakes import SECRET, FakeServer, NoSettle, make_run
from tests.test_configuration import _type
from tests.test_preflight import dashboard_user


class FakeContext:
    def __init__(self, server: FakeServer) -> None:
        self.credentials = ServerCredentials("1729640", "k", SECRET)
        self.secrets = [SECRET]
        self.redactor = Redactor(self.secrets)
        self.ledger = server.ledger
        self.api = server
        self.lines: list[str] = []

    def say(self, text: str) -> None:
        self.lines.append(text)


class CommandTest(unittest.TestCase):
    def setUp(self) -> None:
        self.written: dict[str, Any] = {}

        def write_json(name: str, data: Any, secrets: Any) -> Any:
            self.written[name] = json.loads(json.dumps(data, default=str))
            return PROOF_ROOT / ".work" / name

        def write_text(name: str, text: str, secrets: Any) -> Any:
            self.written[name] = text
            return PROOF_ROOT / ".work" / name

        for name, fake in (("write_json", write_json), ("write_text", write_text)):
            patcher = mock.patch.object(cli, name, fake)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.settle = NoSettle()
        self.settle.__enter__()
        self.addCleanup(self.settle.__exit__)

    def run_command(self, adjust: Callable[[ProofRun, FakeServer], None] | None = None) -> int:
        """``cmd_run`` for case S1 only, with the run built on a fake server."""
        run, server = make_run()
        server.users["owner"] = dashboard_user("owner")  # as in the live application
        if adjust is not None:
            adjust(run, server)
        self.proof, self.server = run, server

        def factory(*_args: Any, **_kwargs: Any) -> ProofRun:
            return run

        with mock.patch.object(cli, "ProofRun", factory):
            return cli.cmd_run(FakeContext(server), True, {"S1"})  # type: ignore[arg-type]

    def results(self) -> dict[str, Any]:
        name = next(
            n
            for n in self.written
            if n.startswith("run-") and n.endswith(".json") and "progress" not in n
        )
        data: dict[str, Any] = self.written[name]
        return data

    def test_clean_run_exits_zero(self) -> None:
        self.assertEqual(self.run_command(), 0)
        self.assertEqual(self.results()["post_run_problems"], [])

    def test_configuration_difference_after_the_run_exits_non_zero(self) -> None:
        def drift(run: ProofRun, server: FakeServer) -> None:
            matrix_run = run.run_matrix

            def run_then_drift(*args: Any, **kwargs: Any) -> None:
                matrix_run(*args, **kwargs)
                server.app["member_custom_on_messages_enabled"] = True

            run.run_matrix = run_then_drift  # type: ignore[method-assign]

        self.assertEqual(self.run_command(drift), cli.EXIT_AFTER_RUN_PROBLEMS)
        problems = self.results()["post_run_problems"]
        self.assertIn(
            "configuration differs after the run: "
            "member_custom_on_messages_enabled is True, want False",
            problems,
        )

    def test_cleanup_problem_exits_non_zero(self) -> None:
        def keep_users(run: ProofRun, server: FakeServer) -> None:
            def refuse(
                method: str, path: str, body: Any, params: dict[str, str] | None
            ) -> ApiResult | None:
                if path == "/api/v2/users/delete":
                    return ApiResult(method, path, 500, -1, "internal", {})
                return None

            server.handlers.append(refuse)

        self.assertEqual(self.run_command(keep_users), cli.EXIT_AFTER_RUN_PROBLEMS)
        problems = " | ".join(self.results()["post_run_problems"])
        self.assertIn("users_delete got 500", problems)
        self.assertIn("remaining_proof_users", problems)

    def test_ctrl_c_restores_cleans_up_writes_results_and_exits_non_zero(self) -> None:
        def interrupt(run: ProofRun, server: FakeServer) -> None:
            def interrupted(*_args: Any, **_kwargs: Any) -> None:
                server.app["guest_user_creation_disabled"] = False
                run.journal.append(
                    TemporaryChange("guest user creation enabled", run._disable_guest_creation)
                )
                raise KeyboardInterrupt

            run.run_matrix = interrupted  # type: ignore[method-assign]

        self.assertEqual(self.run_command(interrupt), cli.EXIT_STOPPED)
        results = self.results()
        self.assertEqual(results["stop_reason"], "interrupted (Ctrl-C)")
        self.assertEqual(results["journal_not_restored"], [])
        self.assertIs(self.server.app["guest_user_creation_disabled"], True)
        self.assertIn("users_task", results["cleanup"])
        self.assertEqual(results["post_run_problems"], [])

    def test_baseline_writes_no_other_users_identifier_or_name(self) -> None:
        server = FakeServer(UsageLedger())
        server.users["private-user-id"] = {
            "id": "private-user-id",
            "name": "Private Person",
            "role": "admin",
            "custom": {"dashboard_user": True, "first_name": "Private"},
        }
        ctx = FakeContext(server)
        self.assertEqual(cli.cmd_baseline(ctx), 0)  # type: ignore[arg-type]
        name = next(n for n in self.written if n.startswith("snapshot-"))
        text = json.dumps(self.written[name])
        for private in ("private-user-id", "Private Person", "Private"):
            self.assertNotIn(private, text)
        written = self.written[name]
        self.assertEqual(written["users"]["dashboard_users"], 1)
        raw = {
            "app": {"app": server.app},
            "channel_types": server.state["channel_types"],
        }
        self.assertEqual(configuration.baseline_record(written), configuration.baseline_record(raw))

    def test_restore_apply_verifies_what_it_restored(self) -> None:
        server = FakeServer(UsageLedger())
        ctx = FakeContext(server)
        # The fake accepts every request but applies no grants: the check must see it.
        self.assertEqual(cli.cmd_restore(ctx, True, False), 1)  # type: ignore[arg-type]
        self.assertTrue(any("grants for user" in line for line in ctx.lines))

        applying = FakeServer(UsageLedger())

        def apply_grants(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            types = applying.state["channel_types"]["channel_types"]
            if path == "/api/v2/app" and method == "PATCH":
                applying.app["guest_user_creation_disabled"] = body["guest_user_creation_disabled"]
                applying.app["grants"].update(body["grants"])
                return ApiResult(method, path, 201, None, None, {})
            name = path.rsplit("/", 1)[-1]
            if method == "PUT" and name in configuration.DEFAULT_TYPES:
                types.setdefault(name, _type(name))["grants"] = body["grants"]
                return ApiResult(method, path, 201, None, None, {})
            return None

        applying.handlers.append(apply_grants)
        ctx = FakeContext(applying)
        self.assertEqual(cli.cmd_restore(ctx, True, False), 0)  # type: ignore[arg-type]
        self.assertIn("differences from the recorded baseline after restore: []", ctx.lines)

    def test_verify_clean_lists_polls_and_user_groups(self) -> None:
        server = FakeServer(UsageLedger())

        def leftover_poll(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if path == "/api/v2/polls/query":
                return ApiResult(method, path, 201, None, None, {"polls": [{"id": "left"}]})
            return None

        ctx = FakeContext(server)
        self.assertEqual(cli.cmd_verify_clean(ctx), 0)  # type: ignore[arg-type]
        server.handlers.append(leftover_poll)
        self.assertEqual(cli.cmd_verify_clean(ctx), 1)  # type: ignore[arg-type]
        self.assertIn("polls remaining: ['left']", ctx.lines)


if __name__ == "__main__":
    unittest.main()
