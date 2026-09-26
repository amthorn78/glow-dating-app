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

import jwt

import tests  # noqa: F401
from glow_stream_proof import cli, configuration
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.credentials import ServerCredentials
from glow_stream_proof.proof_run import ProofRun, RunStopped, TemporaryChange
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import GuardrailStop, UsageLedger
from glow_stream_proof.workdir import PROOF_ROOT
from tests.fakes import SECRET, FakeServer, FakeSession, NoSettle, make_run
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
                run.journal.append(run._guest_creation_change())
                raise KeyboardInterrupt

            run.run_matrix = interrupted  # type: ignore[method-assign]

        self.assertEqual(self.run_command(interrupt), cli.EXIT_STOPPED)
        results = self.results()
        self.assertEqual(results["stop_reason"], "interrupted (Ctrl-C)")
        self.assertEqual(results["journal_not_restored"], [])
        self.assertIs(self.server.app["guest_user_creation_disabled"], True)
        self.assertIn("users_task", results["cleanup"])
        self.assertEqual(results["post_run_problems"], [])

    def test_second_ctrl_c_inside_finish_keeps_the_results_file(self) -> None:
        # P06.1-C2, the C1 review's nit 8: the first Ctrl-C stops the matrix with a
        # temporary change journalled; a second one interrupts finish().
        def interrupt_twice(run: ProofRun, server: FakeServer) -> None:
            def interrupted(*_args: Any, **_kwargs: Any) -> None:
                server.app["guest_user_creation_disabled"] = False
                run.journal.append(run._guest_creation_change())
                raise KeyboardInterrupt

            def finish_interrupted(**_kwargs: Any) -> list[str]:
                raise KeyboardInterrupt

            run.run_matrix = interrupted  # type: ignore[method-assign]
            run.finish = finish_interrupted  # type: ignore[method-assign]

        self.assertEqual(self.run_command(interrupt_twice), cli.EXIT_STOPPED)
        results = self.results()
        self.assertEqual(results["stop_reason"], "interrupted (Ctrl-C)")
        self.assertEqual(results["journal_not_restored"], ["guest user creation enabled"])
        self.assertTrue(
            results["post_run_problems"][0].startswith("the end of the run was interrupted")
        )
        self.assertNotIn("end_of_run", results)  # the final write replaced the early one

    def test_results_are_written_before_the_end_of_the_run(self) -> None:
        def record_early_write(run: ProofRun, server: FakeServer) -> None:
            finish = run.finish

            def finish_after_checking(**kwargs: Any) -> list[str]:
                early = self.results()
                self.assertIn("end_of_run", early)
                self.assertEqual(len(early["cases"]), 1)  # S1's row is already there
                return finish(**kwargs)

            run.finish = finish_after_checking  # type: ignore[method-assign]

        self.assertEqual(self.run_command(record_early_write), 0)

    def test_ctrl_c_during_the_early_write_still_restores(self) -> None:
        writes = vars(cli)["write_json"]  # the fixture's fake

        def interrupt_first_run_write(name: str, data: Any, secrets: Any) -> Any:
            if name.startswith("run-") and "progress" not in name and "end_of_run" in data:
                raise KeyboardInterrupt
            return writes(name, data, secrets)

        def interrupted(run: ProofRun, server: FakeServer) -> None:
            def matrix(*_args: Any, **_kwargs: Any) -> None:
                server.app["guest_user_creation_disabled"] = False
                run.journal.append(run._guest_creation_change())
                raise KeyboardInterrupt

            run.run_matrix = matrix  # type: ignore[method-assign]

        with mock.patch.object(cli, "write_json", interrupt_first_run_write):
            self.assertEqual(self.run_command(interrupted), cli.EXIT_STOPPED)
        self.assertIs(self.server.app["guest_user_creation_disabled"], True)
        self.assertEqual(self.results()["journal_not_restored"], [])

    def test_second_ctrl_c_keeps_the_problems_finish_found(self) -> None:
        # The C2 review's nit 4: finish() had found a restore it could not make before
        # the second Ctrl-C (during the cleanup); the results keep that problem.
        def interrupt_twice(run: ProofRun, server: FakeServer) -> None:
            def stuck() -> str:
                raise RunStopped("still on")

            def interrupted(*_args: Any, **_kwargs: Any) -> None:
                run.journal.append(TemporaryChange("stuck change", stuck))
                raise KeyboardInterrupt

            def cleanup_interrupted() -> dict[str, Any]:
                raise KeyboardInterrupt

            run.run_matrix = interrupted  # type: ignore[method-assign]
            run.cleanup = cleanup_interrupted  # type: ignore[method-assign]

        self.assertEqual(self.run_command(interrupt_twice), cli.EXIT_STOPPED)
        problems = self.results()["post_run_problems"]
        self.assertTrue(problems[0].startswith("the end of the run was interrupted"))
        self.assertIn("temporary change not restored: still on", problems)

    def test_second_ctrl_c_closes_the_client_sessions(self) -> None:
        # The C2 review's nit 4: the client processes are closed after a second Ctrl-C.
        def interrupt_twice(run: ProofRun, server: FakeServer) -> None:
            def interrupted(*_args: Any, **_kwargs: Any) -> None:
                raise KeyboardInterrupt

            def finish_interrupted(**_kwargs: Any) -> list[str]:
                raise KeyboardInterrupt

            run.run_matrix = interrupted  # type: ignore[method-assign]
            run.finish = finish_interrupted  # type: ignore[method-assign]

        self.assertEqual(self.run_command(interrupt_twice), cli.EXIT_STOPPED)
        self.assertEqual(self.proof.sessions, {})

    def test_the_early_write_failure_note_is_redacted(self) -> None:
        # P06.1-C3, the C2 review's nit 10.
        token = jwt.encode({"user_id": "x"}, SECRET, "HS256")
        writes = vars(cli)["write_json"]  # the fixture's fake

        def failing_early_write(name: str, data: Any, secrets: Any) -> Any:
            if name.startswith("run-") and "progress" not in name and "end_of_run" in data:
                raise RuntimeError(f"refused near {token} and {SECRET}")
            return writes(name, data, secrets)

        with mock.patch.object(cli, "write_json", failing_early_write):
            self.assertEqual(self.run_command(), 0)
        notes = [n for n in self.results()["notes"] if n.startswith("results not written")]
        self.assertEqual(len(notes), 1)
        self.assertIn("RuntimeError: refused near <redacted-jwt> and <redacted-secret>", notes[0])
        self.assertNotIn(token, notes[0])
        self.assertNotIn(SECRET, notes[0])

    # -- P06.1-C3, the C2 review's finding 2: a charge or limit signal met anywhere in
    # the run means nothing of the run's is deleted.

    def test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup(self) -> None:
        # The review's reproduction: the run stopped on a failed restore, and the end
        # of the run's retry got HTTP 402.
        def stopped_on_a_failed_restore(run: ProofRun, server: FakeServer) -> None:
            attempts: list[int] = []

            def restore() -> str:
                attempts.append(1)
                if len(attempts) == 1:
                    raise RunStopped("could not restore glow-match features: PUT 500")
                raise GuardrailStop("server PUT /x: HTTP 402; stopping at once", at_once=True)

            def matrix(*_args: Any, **_kwargs: Any) -> None:
                change = TemporaryChange("glow-match features ['custom_events']", restore)
                run.journal.append(change)
                run._restore(change)  # the case's own restore fails: the run stops

            run.run_matrix = matrix  # type: ignore[method-assign]

        self.assertEqual(self.run_command(stopped_on_a_failed_restore), cli.EXIT_STOPPED)
        results = self.results()
        self.assertTrue(results["stop_reason"].startswith("stopped: could not restore"))
        self.assert_nothing_deleted(results)
        self.assertEqual(results["stop_signals"], ["server PUT /x: HTTP 402; stopping at once"])
        # The configuration was still re-read at the end (preflight read it once before).
        reads = [
            p for m, p, _b in self.server.calls if m == "GET" and p == "/api/v2/chat/channeltypes"
        ]
        self.assertEqual(len(reads), 2)

    def test_rate_limited_restores_at_the_end_skip_the_cleanup(self) -> None:
        # The review: three rate-limited retries also ended in a cleanup.
        attempts: list[int] = []

        def rate_limited_at_the_end(run: ProofRun, server: FakeServer) -> None:
            def restore() -> str:
                attempts.append(1)
                raise GuardrailStop("server PUT /x: HTTP 429; stopping at once", rate_limited=True)

            def matrix(*_args: Any, **_kwargs: Any) -> None:
                run.journal.append(TemporaryChange("a change", restore))
                raise KeyboardInterrupt

            run.run_matrix = matrix  # type: ignore[method-assign]

        self.assertEqual(self.run_command(rate_limited_at_the_end), cli.EXIT_STOPPED)
        self.assertEqual(len(attempts), 3)  # a rate limit is still retried
        self.assert_nothing_deleted(self.results())

    def test_a_signal_as_the_runs_own_stop_skips_the_cleanup(self) -> None:
        # cmd_run adds its own stop to the run's record; finish() decides from it.
        def charged(run: ProofRun, server: FakeServer) -> None:
            def matrix(*_args: Any, **_kwargs: Any) -> None:
                raise GuardrailStop("client A: HTTP 402; stopping at once", at_once=True)

            run.run_matrix = matrix  # type: ignore[method-assign]

        self.assertEqual(self.run_command(charged), cli.EXIT_STOPPED)
        results = self.results()
        self.assert_nothing_deleted(results)
        self.assertEqual(results["stop_signals"], ["client A: HTTP 402; stopping at once"])

    def test_a_signal_whose_stop_a_ctrl_c_replaced_skips_the_cleanup(self) -> None:
        # The independent review of P06.1-C3: E5's own client session met a charge
        # signal, and a Ctrl-C arrived while E5's `finally` closed that session. The
        # Ctrl-C became the run's stop; the signal was recorded where it was met.
        interrupted: list[int] = []
        real_close = FakeSession.close

        def close(session: FakeSession, **_kwargs: Any) -> None:
            if session.label == "A-role" and not interrupted:
                interrupted.append(1)
                raise KeyboardInterrupt
            real_close(session)

        def e5_charged_on_connect(run: ProofRun, server: FakeServer) -> None:
            make_session, matrix_run = run._session, run.run_matrix

            def charged(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
                if op == "connect":
                    raise run.ledger.stop_at_once(
                        "client A-role: HTTP 402; stopping at once", rate_limited=False
                    )
                return None

            def session(label: str, token: str | None, **kwargs: Any) -> Any:
                created: Any = make_session(label, token, **kwargs)
                if label == "A-role":
                    created.behaviour = charged
                return created

            def e5_only(
                only: set[str] | None = None, progress: Callable[[], None] | None = None
            ) -> None:
                matrix_run({"E5"}, progress)

            run._session = session  # type: ignore[method-assign]
            run.run_matrix = e5_only  # type: ignore[method-assign]

        with mock.patch.object(FakeSession, "close", close):
            self.assertEqual(self.run_command(e5_charged_on_connect), cli.EXIT_STOPPED)
        results = self.results()
        self.assertEqual(results["stop_reason"], "interrupted (Ctrl-C)")
        self.assertEqual(results["stop_signals"], ["client A-role: HTTP 402; stopping at once"])
        self.assert_nothing_deleted(results)

    def test_a_budget_stop_still_cleans_up(self) -> None:
        def budget(run: ProofRun, server: FakeServer) -> None:
            def matrix(*_args: Any, **_kwargs: Any) -> None:
                raise GuardrailStop(
                    "guardrail: api_calls would be passed; stopping before the call"
                )

            run.run_matrix = matrix  # type: ignore[method-assign]

        self.assertEqual(self.run_command(budget), cli.EXIT_STOPPED)
        results = self.results()
        self.assertEqual(results["stop_signals"], [])
        self.assertIn("users_task", results["cleanup"])
        self.assertEqual(results["post_run_problems"], [])

    def assert_nothing_deleted(self, results: dict[str, Any]) -> None:
        self.assertEqual(results["cleanup"], {})
        self.assertEqual([p for _m, p, _b in self.server.calls if p.endswith("/delete")], [])
        skipped = [p for p in results["post_run_problems"] if p.startswith("cleanup skipped")]
        self.assertEqual(len(skipped), 1, results["post_run_problems"])
        self.assertIn("a charge or limit signal stopped the run at once", skipped[0])
        self.assertEqual(self.proof.sessions, {})  # the client processes are still closed

    def test_preflight_stop_exits_non_zero_without_cleanup(self) -> None:
        def second_dashboard_user(run: ProofRun, server: FakeServer) -> None:
            server.users["second"] = dashboard_user("second")

        self.assertEqual(self.run_command(second_dashboard_user), cli.EXIT_STOPPED)
        results = self.results()
        self.assertIn("exactly one is accepted", results["stop_reason"])
        self.assertEqual(results["post_run_problems"], [])
        self.assertEqual(results["cleanup"], {})
        self.assertEqual(results["checks"], [])

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
                types.setdefault(name, _type(name)).update(body)
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


class AtomicWriteTest(unittest.TestCase):
    """P06.1-C2: an interrupted write never leaves a results file truncated."""

    def test_a_failed_write_leaves_the_previous_file_whole(self) -> None:
        import tempfile
        from pathlib import Path

        from glow_stream_proof import workdir

        with (
            tempfile.TemporaryDirectory() as scratch,
            mock.patch.object(workdir, "WORK_DIR", Path(scratch)),
        ):
            workdir.write_json("run-x.json", {"cases": [1]}, [SECRET])
            with mock.patch.object(Path, "replace", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    workdir.write_json("run-x.json", {"cases": [1, 2]}, [SECRET])
            self.assertEqual(json.loads((Path(scratch) / "run-x.json").read_text()), {"cases": [1]})


if __name__ == "__main__":
    unittest.main()
