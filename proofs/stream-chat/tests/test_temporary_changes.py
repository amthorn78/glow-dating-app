"""Finding 2 and nit 4: temporary changes are journalled, restored and verified.

A failed restore stops the run; a restore failure never hides a guardrail stop
already in flight; undos and override removals are checked, and each removal is
re-read.
"""

import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import configuration
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.proof_run import (
    RunStopped,
    TemporaryChange,
    override_removal_problems,
)
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import GuardrailStop
from tests.fakes import FakeSession, NoSettle, error, make_run, set_up

MATCH_PATH = f"/api/v2/chat/channeltypes/{configuration.MATCH_TYPE}"


def is_restore_put(method: str, path: str, body: Any, feature: str) -> bool:
    return method == "PUT" and path == MATCH_PATH and (body or {}).get(feature) is False


class TypeFeatureRestoreTest(unittest.TestCase):
    def test_failed_restore_stops_the_run(self) -> None:
        run, server = make_run()

        def refuse_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if is_restore_put(method, path, body, "custom_events"):
                return error(method, path, 500, -1, "internal")
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_restore)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S12", "S13"})
        ids = [c.case_id for c in run.case_results]
        self.assertEqual(ids, ["S12"])  # S13 never ran
        self.assertIn("run stopped", run.case_results[0].observed)
        self.assertTrue(any("restore failed" in s for s in run.stops))
        self.assertEqual(len(run.journal), 1)  # still owed; finish() tries again

    def test_restore_that_reads_back_wrong_stops_the_run(self) -> None:
        run, server = make_run()

        def ignore_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if is_restore_put(method, path, body, "custom_events"):
                return ApiResult(method, path, 201, None, None, {})  # accepted, not applied
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(ignore_restore)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S12"})
        self.assertIs(server.match_type["custom_events"], True)

    def test_journal_entry_exists_before_the_enabling_request(self) -> None:
        # Ctrl-C arrives while the enabling PUT is in flight (after Stream applied it).
        run, server = make_run()

        def interrupt_enable(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "PUT" and path == MATCH_PATH and (body or {}).get("custom_events"):
                server.match_type["custom_events"] = True
                raise KeyboardInterrupt
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(interrupt_enable)
            with self.assertRaises(KeyboardInterrupt):
                run.run_matrix({"S12"})
        self.assertIs(server.match_type["custom_events"], False)
        self.assertEqual(run.journal, [])

    def test_guest_creation_is_restored_after_an_interrupt_before_the_control(self) -> None:
        run, server = make_run()
        base_session = run._session

        def interrupting_session(label: str, token: str | None, **kwargs: Any) -> Any:
            if label == "guest":
                raise KeyboardInterrupt  # during the settle wait or the session start
            return base_session(label, token, **kwargs)

        with NoSettle():
            set_up(run)
            run._session = interrupting_session  # type: ignore[method-assign]
            with self.assertRaises(KeyboardInterrupt):
                run.run_matrix({"G1-create"})
        self.assertIs(server.app["guest_user_creation_disabled"], True)
        self.assertEqual(run.journal, [])

    def test_restore_failure_does_not_hide_a_guardrail_stop_in_flight(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                raise GuardrailStop("client A: HTTP 429; stopping at once")
            return None

        run, server = make_run(behaviours={"A": a})

        def refuse_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if is_restore_put(method, path, body, "custom_events"):
                return error(method, path, 500, -1, "internal")
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_restore)
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"S12"})
        text = " | ".join(run.stops)
        self.assertIn("restore failed", text)
        self.assertIn("GuardrailStop", text)
        self.assertIn("HTTP 429", text)


class ChannelOverrideRemovalTest(unittest.TestCase):
    def test_removal_that_did_not_apply_stops_the_run(self) -> None:
        run, server = make_run()

        def keep_override(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                return ApiResult(method, path, 200, None, None, {})  # accepted, not applied
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(keep_override)
            with self.assertRaises(RunStopped) as stopped:
                run.run_matrix({"S2", "S3a"})
        self.assertIn("replies is True", str(stopped.exception))
        self.assertEqual([c.case_id for c in run.case_results], ["S2"])

    def test_removal_refused_stops_the_run(self) -> None:
        run, server = make_run()

        def refuse_removal(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                return error(method, path, 500, -1)
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_removal)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S5"})

    def test_removal_is_re_read(self) -> None:
        run, server = make_run()
        with NoSettle():
            set_up(run)
            run.run_matrix({"S2"})
        reads = [
            c
            for c in server.calls
            if c[1] == "/api/v2/chat/channels" and c[2].get("filter_conditions")
        ]
        self.assertEqual(len(reads), 1)
        self.assertIn("re-read", run.case_results[0].detail["feature_override"]["restored"])
        self.assertEqual(server.overrides[run.ctx["AB"]], {})

    def test_override_removal_problems(self) -> None:
        replies = {"replies": True}
        grant = {"grants": {"channel_member": ["read-channel-members"]}}
        self.assertEqual(override_removal_problems({"config_overrides": {}}, replies), ([], []))
        self.assertEqual(
            override_removal_problems({"config": {"replies": False}}, replies), ([], [])
        )
        problems, _ = override_removal_problems({"config": {"replies": True}}, replies)
        self.assertEqual(problems, ["replies is True, want False"])
        self.assertEqual(override_removal_problems({"config": {}}, replies), ([], ["replies"]))
        member_grants = {"channel_member": ["read-channel", "read-channel-members"]}
        problems, _ = override_removal_problems({"config": {"grants": member_grants}}, grant)
        self.assertEqual(problems, ["channel_member still has ['read-channel-members']"])
        self.assertEqual(override_removal_problems({"config": {}}, grant), ([], ["grants"]))
        self.assertEqual(override_removal_problems(None, grant)[0], ["AB could not be re-read"])


class UndoCheckTest(unittest.TestCase):
    def test_failed_undo_stops_the_run_after_its_case(self) -> None:
        run, server = make_run()

        def refuse_undo(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            text = ((body or {}).get("message") or {}).get("text")
            if method == "POST" and path.startswith("/messages/") and text == run.ctx["m_a_text"]:
                return error(method, path, 500, -1)
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_undo)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S3a", "S3b"})
        self.assertEqual([c.case_id for c in run.case_results], ["S3a"])
        self.assertIn("undo POST 500", run.case_results[0].control)
        self.assertTrue(any("undo POST" in s for s in run.stops))

    def test_member_field_unset_is_checked(self) -> None:
        run, server = make_run()

        def refuse_unset(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "PATCH" and path.endswith("/member") and (body or {}).get("unset"):
                return error(method, path, 500, -1)
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_unset)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S15", "S16"})
        self.assertEqual([c.case_id for c in run.case_results], ["S15"])


class FinishTest(unittest.TestCase):
    def test_finish_restores_the_journal_and_verifies_the_configuration(self) -> None:
        run, server = make_run()
        restored: list[str] = []

        def restore() -> str:
            restored.append("x")
            return "done"

        change = TemporaryChange("a leftover change", restore)
        run.journal.append(change)
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertEqual(restored, ["x"])
        self.assertEqual(run.journal, [])
        self.assertEqual(
            problems, ["cleanup skipped (a charge or limit signal stopped the run at once)"]
        )
        server.app["guest_user_creation_disabled"] = False
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertIn(
            "configuration differs after the run: guest_user_creation_disabled is not true",
            problems,
        )

    def test_finish_reports_a_restore_it_cannot_make(self) -> None:
        run, _server = make_run()

        def fail() -> str:
            raise RunStopped("still on")

        run.journal.append(TemporaryChange("stuck change", fail))
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertTrue(any(p.startswith("temporary change not restored") for p in problems))
        self.assertEqual(run.results()["journal_not_restored"], ["stuck change"])


if __name__ == "__main__":
    unittest.main()
