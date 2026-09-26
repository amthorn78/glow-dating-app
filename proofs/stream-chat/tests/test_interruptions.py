"""P06.1-C2, finding 1: what a case observed survives an interruption of a later step.

Every way a case can end records its row: a guardrail stop, a failed restore, an
ended client session, any other exception or Ctrl-C. The row keeps what the
case had observed: a FAIL stays a FAIL, and anything else becomes INCONCLUSIVE
with the interruption as its reason. A client success whose undo was owed is
undone, or the row says why not.
"""

import unittest
from collections.abc import Callable
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix
from glow_stream_proof.client_bridge import ClientSessionEnded, Reply
from glow_stream_proof.proof_run import CaseResult, ProofRun, RunStopped
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import GuardrailStop
from tests.fakes import FakeServer, FakeSession, NoSettle, make_run, record, set_up

Behaviour = Callable[[FakeSession, str, dict[str, Any]], Reply | None]
ENDED = "client {} ended: no reply within 60s"


def ended(label: str) -> ClientSessionEnded:
    return ClientSessionEnded(ENDED.format(label))


def success(body: Any = None, path: str = "/channels/glow-match/x/query") -> Reply:
    return Reply(True, {}, None, [record(201, body or {}, path=path)], api_calls=1)


def only(run: ProofRun, case_id: str) -> CaseResult:
    rows = [c for c in run.case_results if c.case_id == case_id]
    assert len(rows) == 1, [c.case_id for c in run.case_results]
    return rows[0]


def matrix_run(
    cases: set[str],
    behaviours: dict[str, Behaviour] | None = None,
    *,
    after_setup: dict[str, Behaviour] | None = None,
    handler: Callable[[FakeServer, ProofRun], Any] | None = None,
    raises: type[BaseException] | None = None,
) -> tuple[ProofRun, FakeServer]:
    """Set up, then run ``cases``; ``after_setup`` behaviours apply to the matrix only."""
    run, server = make_run(behaviours=behaviours)
    with NoSettle():
        set_up(run)
        for label, behaviour in (after_setup or {}).items():
            session = run.sessions[label]
            assert isinstance(session, FakeSession)
            session.behaviour = behaviour
        if handler is not None:
            server.handlers.append(handler(server, run))
        if raises is None:
            run.run_matrix(cases)
        else:
            with unittest.TestCase().assertRaises(raises):
                run.run_matrix(cases)
    return run, server


class ReviewScenariosTest(unittest.TestCase):
    """The three scenarios of the C1 review's finding 1."""

    def test_s2_fail_survives_a_timeout_in_the_production_phase(self) -> None:
        # Replies on: A's thread reply succeeds (FAIL). The restore succeeds, then
        # the production-phase request times out.
        calls: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendMessage":
                calls.append(1)
                if len(calls) == 1:
                    return success({"message": {"id": "m-reply"}}, "/channels/glow-match/x/message")
                raise ended("A")
            return None

        run, server = matrix_run({"S2", "S3a"}, after_setup={"A": a})
        row = only(run, "S2")
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertEqual(row.reason, "the client action succeeded")
        self.assertIn("ClientSessionEnded", row.detail["interrupted"])
        self.assertEqual(row.detail["feature_override"]["features"], {"replies": True})
        self.assertEqual(server.overrides[run.ctx["AB"]], {})  # the override was removed
        self.assertEqual([c.case_id for c in run.case_results], ["S2", "S3a"])  # the run went on

    def test_s15_leak_survives_bs_session_ending_during_the_control(self) -> None:
        marker = "memberfreep061i1simulated"
        queries: list[int] = []

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                queries.append(1)
                if len(queries) == 1:  # B's production read carries A's member field
                    return success({"members": [{"user_id": "a", "glow_note": marker}]})
                raise ended("B")  # during the control
            return None

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "updateMemberPartial":
                return success({}, "/channels/glow-match/x/member")
            return None

        run, _server = matrix_run({"S15"}, after_setup={"A": a, "B": b})
        row = only(run, "S15")
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertIn("B read it via channel_query", row.reason)
        self.assertTrue(row.detail["production_b_views"]["channel_query_has_marker"])
        self.assertIn("ClientSessionEnded", row.detail["interrupted"])

    @staticmethod
    def _a_edits_its_message(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        if op == "call" and params.get("method") == "updateMessage":
            message_id = params["args"][0]["id"]
            return success({"message": {"id": message_id}}, f"/messages/{message_id}")
        return None

    @staticmethod
    def _replay_fails_with(
        exc: BaseException,
    ) -> Callable[[FakeServer, ProofRun], Any]:
        def install(server: FakeServer, run: ProofRun) -> Any:
            def handler(
                method: str, path: str, body: Any, params: dict[str, str] | None
            ) -> ApiResult | None:
                message = (body or {}).get("message") or {}
                if method == "POST" and path.startswith("/messages/") and "text" not in message:
                    raise exc  # the server replay of A's edit (the undo carries the text)
                return None

            return handler

        return install

    @staticmethod
    def _undo_posts(server: FakeServer, run: ProofRun) -> list[Any]:
        return [
            c
            for c in server.calls
            if c[0] == "POST"
            and c[1].startswith("/messages/")
            and ((c[2] or {}).get("message") or {}).get("text") == run.ctx["m_a_text"]
        ]

    def test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit(self) -> None:
        # The run stops at once; the client's success is recorded, and its undo is
        # not made, as the README's rule for a guardrail stop says.
        stop = GuardrailStop(
            "server POST /messages/x: HTTP 429; stopping at once", rate_limited=True
        )
        run, server = matrix_run(
            {"S3a", "S3b"},
            after_setup={"A": self._a_edits_its_message},
            handler=self._replay_fails_with(stop),
            raises=GuardrailStop,
        )
        row = only(run, "S3a")
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertEqual(row.control, "control not completed")
        self.assertIn("GuardrailStop", row.detail["interrupted"])
        self.assertTrue(
            row.detail["client_success_undo"].startswith("not made: a guardrail stopped the run")
        )
        self.assertEqual(self._undo_posts(server, run), [])
        self.assertEqual([c.case_id for c in run.case_results], ["S3a"])

    def test_s3a_client_success_is_undone_after_a_replay_error(self) -> None:
        # Not a stop: the undo is made, and the run goes on.
        run, server = matrix_run(
            {"S3a", "S3b"},
            after_setup={"A": self._a_edits_its_message},
            handler=self._replay_fails_with(RuntimeError("connection reset")),
        )
        row = only(run, "S3a")
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertIn("RuntimeError", row.detail["interrupted"])
        self.assertEqual(
            row.detail["client_success_undo"], "made after the interruption: undo POST 201"
        )
        self.assertEqual(len(self._undo_posts(server, run)), 1)
        self.assertEqual([c.case_id for c in run.case_results], ["S3a", "S3b"])

    def test_s3a_undo_is_not_made_after_ctrl_c(self) -> None:
        run, server = matrix_run(
            {"S3a"},
            after_setup={"A": self._a_edits_its_message},
            handler=self._replay_fails_with(KeyboardInterrupt()),
            raises=KeyboardInterrupt,
        )
        row = only(run, "S3a")
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertTrue(row.detail["client_success_undo"].startswith("not made: interrupted"))
        self.assertEqual(self._undo_posts(server, run), [])

    def test_undo_after_a_completed_control_is_recorded(self) -> None:
        run, server = matrix_run({"S3a"}, after_setup={"A": self._a_edits_its_message})
        row = only(run, "S3a")
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertEqual(row.detail["client_success_undo"], "undo POST 201")
        self.assertEqual(len(self._undo_posts(server, run)), 2)  # the replay's and the client's


class EveryWayACaseEndsTest(unittest.TestCase):
    def test_guardrail_stop_with_nothing_observed_records_an_inconclusive_row(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "watch":
                raise GuardrailStop("client A: HTTP 402; stopping at once")
            return None

        run, _server = matrix_run({"R1", "R2"}, after_setup={"A": a}, raises=GuardrailStop)
        row = only(run, "R1")
        self.assertEqual(row.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(row.reason, "the run stopped at a guardrail during this case")
        self.assertIn("HTTP 402", row.observed)
        self.assertEqual([c.case_id for c in run.case_results], ["R1"])

    def test_ctrl_c_with_nothing_observed_records_an_inconclusive_row(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "watch":
                raise KeyboardInterrupt
            return None

        run, _server = matrix_run({"R1"}, after_setup={"A": a}, raises=KeyboardInterrupt)
        row = only(run, "R1")
        self.assertEqual(row.verdict, matrix.INCONCLUSIVE)
        self.assertIn("Ctrl-C", row.reason)

    def test_an_observed_refusal_becomes_inconclusive_with_the_interruption_as_reason(
        self,
    ) -> None:
        # A's watch of XD is refused (403 / 17); X's control session then ends.
        def x(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call":
                raise ended("X")
            return None

        run, _server = matrix_run({"R1"}, after_setup={"X": x})
        row = only(run, "R1")
        self.assertEqual(row.observed, "403 / code 17")
        self.assertEqual(row.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(
            row.reason,
            "interrupted before the case finished: a client session ended "
            "(timeout, mismatched reply or exit)",
        )


class ProceduresKeepWhatTheyObservedTest(unittest.TestCase):
    """Each procedure keeps a FAIL it observed before a later step was interrupted."""

    def assert_kept_fail(self, run: ProofRun, case_id: str) -> CaseResult:
        row = only(run, case_id)
        self.assertEqual(row.verdict, matrix.FAIL, row.reason)
        self.assertIn("interrupted", row.detail)
        return row

    def test_t2_rest_success_survives_as_controls_session_ending(self) -> None:
        def bad(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            return success() if op == "call" else None

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call":
                raise ended("A")
            return None

        run, _ = matrix_run({"T2-rest"}, {"tok-T2-rest": bad}, after_setup={"A": a})
        self.assert_kept_fail(run, "T2-rest")

    def test_t4_ws_connection_as_b_survives_a_failed_disconnect(self) -> None:
        def t4(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                return Reply(True, {"me": {"id": params["user"]["id"], "role": "user"}}, None)
            if op == "disconnect":
                raise ended("tok-T4-ws")
            return None

        run, _ = matrix_run({"T4-ws"}, {"tok-T4-ws": t4})
        self.assertEqual(
            self.assert_kept_fail(run, "T4-ws").reason, "connected as B with A's token"
        )

    def test_t4_rest_xd_success_survives_xs_session_ending(self) -> None:
        def claimer(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            return success() if op == "call" else None

        def x(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call":
                raise ended("X")
            return None

        run, _ = matrix_run({"T4-rest-xd"}, {"claim-XD": claimer}, after_setup={"X": x})
        self.assert_kept_fail(run, "T4-rest-xd")

    def test_g1_created_guest_survives_a_failed_disconnect(self) -> None:
        def attempt(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "guest":
                stored = f"guest-1-{params['user']['id']}"
                created = record(201, {"user": {"id": stored, "role": "guest"}}, path="/guest")
                return Reply(True, {"me": {"id": stored}}, None, [created], api_calls=1)
            if op == "disconnect":
                raise ended("guest-attempt")
            return None

        run, _ = matrix_run({"G1-create"}, {"guest-attempt": attempt})
        self.assert_kept_fail(run, "G1-create")
        self.assertIn("guest-1-", " ".join(run.users))

    def test_g3_leak_survives_the_controls_session_ending(self) -> None:
        def anon(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                return success({"channel": {"cid": f"glow-match:{params['id']}"}})
            return None

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call":
                raise ended("A")
            return None

        run, _ = matrix_run({"G3-read-ab"}, {"anonymous": anon}, after_setup={"A": a})
        self.assert_kept_fail(run, "G3-read-ab")

    def test_s10_vote_success_survives_the_production_vote_ending(self) -> None:
        votes: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "castPollVote":
                votes.append(1)
                if len(votes) == 1:
                    return success({"vote": {}}, "/messages/m-poll/polls/p1/vote")
                raise ended("A")
            return None

        run, server = matrix_run({"S10"}, after_setup={"A": a})
        self.assert_kept_fail(run, "S10")
        self.assertIs(server.match_type["polls"], False)

    def test_s10_vote_success_survives_an_error_in_the_server_replay(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "castPollVote":
                return success({"vote": {}}, "/messages/m-poll/polls/p1/vote")
            return None

        def replay_error(server: FakeServer, run: ProofRun) -> Any:
            def handler(
                method: str, path: str, body: Any, params: dict[str, str] | None
            ) -> ApiResult | None:
                if path.endswith("/vote"):
                    raise RuntimeError("connection reset")
                return None

            return handler

        run, server = matrix_run({"S10"}, after_setup={"A": a}, handler=replay_error)
        self.assert_kept_fail(run, "S10")
        self.assertIs(server.match_type["polls"], False)  # restored all the same

    def test_s10_polls_on_control_survives_the_production_vote_ending(self) -> None:
        # A's vote is refused with polls on, and the server's vote succeeds; the
        # production vote is then interrupted: INCONCLUSIVE, with the control kept.
        votes: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "castPollVote":
                votes.append(1)
                if len(votes) == 1:
                    rec = record(403, {"code": 17}, path="/messages/m-poll/polls/p1/vote")
                    error = {"status": 403, "code": 17, "message": "no", "kind": "api"}
                    return Reply(False, None, error, [rec], api_calls=1)
                raise ended("A")
            return None

        run, _ = matrix_run({"S10"}, after_setup={"A": a})
        row = only(run, "S10")
        self.assertEqual(row.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(row.observed, "polls on: 403 / code 17")
        self.assertEqual(row.control, "server replay POST -> 201")
        self.assertIn("ClientSessionEnded", row.detail["interrupted"])

    def test_s14_stored_change_survives_an_error_in_the_control(self) -> None:
        run, server = make_run()
        name = "renamed on connect by A"

        def stored_and_failing_control(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if (
                method == "GET"
                and path == "/api/v2/users"
                and '"$eq"' in (params or {}).get("payload", "")
            ):
                user = {"id": run.ctx["A"], "role": "user", "name": name}
                return ApiResult(method, path, 200, None, None, {"users": [user]})
            if method == "PATCH" and path == "/users":
                raise RuntimeError("connection reset")
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(stored_and_failing_control)
            run.run_matrix({"S14"})
        row = self.assert_kept_fail(run, "S14")
        self.assertEqual(row.reason, "the change reached Stream's stored state")

    def test_s14_profile_on_the_connection_survives_a_failed_disconnect(self) -> None:
        def profile(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                user = params["user"]
                me = {"id": user["id"], "role": "user", "name": user["name"], "custom_keys": []}
                return Reply(True, {"me": me}, None)
            if op == "disconnect":
                raise ended("A-profile")
            return None

        run, _ = matrix_run({"S14"}, {"A-profile": profile})
        self.assert_kept_fail(run, "S14")

    def test_e5_role_on_the_connection_survives_a_failed_disconnect(self) -> None:
        def role(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                return Reply(True, {"me": {"id": params["user"]["id"], "role": "admin"}}, None)
            if op == "disconnect":
                raise ended("A-role")
            return None

        run, _ = matrix_run({"E5"}, {"A-role": role})
        self.assert_kept_fail(run, "E5")

    def test_rt1_xd_event_survives_xs_session_ending(self) -> None:
        drains: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "events" and params.get("wait_ms"):
                event = {"type": "message.new", "cid": "glow-match:p061i1-simulated-ch-xd"}
                return Reply(True, {"events": [event]}, None)
            return None

        def x(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "events":
                drains.append(1)
                if len(drains) > 1:
                    raise ended("X")
            return None

        run, _ = matrix_run({"RT1"}, after_setup={"A": a, "X": x})
        self.assert_kept_fail(run, "RT1")

    def test_rt2_marker_in_the_first_window_survives_bs_session_ending(self) -> None:
        marker = "typingfreep061i1simulated"
        windows: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                return success({"event": {}}, "/channels/glow-match/x/event")
            return None

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "events":
                windows.append(1)
                if len(windows) == 2:  # after A's request
                    event = {"type": "typing.start", "glow_text": marker}
                    return Reply(True, {"events": [event]}, None)
                if len(windows) == 3:  # after the probe
                    raise ended("B")
            return None

        run, _ = matrix_run({"RT2"}, after_setup={"A": a, "B": b})
        row = self.assert_kept_fail(run, "RT2")
        self.assertEqual(row.detail["marker_event_types"], ["typing.start"])


class ReviewOfC2Test(unittest.TestCase):
    """Points the independent review of these corrections raised (P06.1-C2)."""

    @staticmethod
    def e5_with_admin_stored(restore_error: BaseException) -> Callable[[FakeServer, ProofRun], Any]:
        def install(server: FakeServer, run: ProofRun) -> Any:
            def handler(
                method: str, path: str, body: Any, params: dict[str, str] | None
            ) -> ApiResult | None:
                payload = (params or {}).get("payload", "")
                if method == "GET" and path == "/api/v2/users" and '"$eq"' in payload:
                    user = {"id": run.ctx["A"], "role": "admin"}
                    return ApiResult(method, path, 200, None, None, {"users": [user]})
                if method == "PATCH" and path == "/users":
                    raise restore_error
                return None

            return handler

        return install

    def test_e5_stored_role_fail_survives_a_rate_limited_restore(self) -> None:
        stop = GuardrailStop("server PATCH /users: HTTP 429; stopping at once", rate_limited=True)
        run, _ = matrix_run({"E5"}, handler=self.e5_with_admin_stored(stop), raises=GuardrailStop)
        row = only(run, "E5")
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertEqual(row.detail["stored_role"], "admin")

    def test_e5_failed_restore_stops_the_run_after_its_row(self) -> None:
        run, _ = matrix_run(
            {"E5", "C1"},
            handler=self.e5_with_admin_stored(RuntimeError("connection reset")),
            raises=RunStopped,
        )
        self.assertEqual(only(run, "E5").verdict, matrix.FAIL)
        self.assertEqual([c.case_id for c in run.case_results], ["E5"])  # C1 never ran
        self.assertTrue(any("E5: restoring A's role raised" in s for s in run.stops))

    def test_a_failing_progress_write_never_replaces_a_guardrail_stop(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "watch":
                raise GuardrailStop("client A: HTTP 402; stopping at once")
            return None

        def failing_progress() -> None:
            raise OSError("disk full")

        run, _server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = a
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"R1"}, failing_progress)
        self.assertEqual([c.case_id for c in run.case_results], ["R1"])
        self.assertTrue(any(n.startswith("progress not written: OSError") for n in run.notes))

    def test_ctrl_c_is_kept_when_the_progress_write_fails(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "watch":
                raise KeyboardInterrupt
            return None

        def failing_progress() -> None:
            raise OSError("disk full")

        run, _server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = a
            with self.assertRaises(KeyboardInterrupt):
                run.run_matrix({"R1"}, failing_progress)

    def test_a_key_still_overridden_keeps_the_change_journalled(self) -> None:
        # Two keys: Stream keeps replies after the removal, and B's probe for the
        # grant is stopped by the budget. The change is not "restored".
        override = {"replies": True, "grants": {"channel_member": ["read-channel-members"]}}

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "queryMembers":
                raise GuardrailStop(
                    "guardrail: api_calls would be passed; stopping before the call"
                )
            return None

        run, server = make_run(behaviours={"B": b})
        server.config_has_grants = False

        def keep_replies(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                server.overrides[run.ctx["AB"]] = {"replies": True}
                return ApiResult(method, path, 200, None, None, {})
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(keep_replies)
            change = run._channel_override_change(override)
            with self.assertRaises(RunStopped), run._temporary(change):
                run._set_channel_override(change, override)
        self.assertEqual(run.journal, [change])
        self.assertEqual(run.unverified_restores, [])

    def test_finish_keeps_the_problems_found_before_a_second_ctrl_c(self) -> None:
        from glow_stream_proof.proof_run import TemporaryChange

        def stuck() -> str:
            raise RunStopped("still on")

        run, _server = make_run()
        run.journal.append(TemporaryChange("stuck change", stuck))

        def interrupted_cleanup() -> dict[str, Any]:
            raise KeyboardInterrupt

        run.cleanup = interrupted_cleanup  # type: ignore[method-assign]
        with NoSettle(), self.assertRaises(KeyboardInterrupt):
            run.finish(cleanup=True)
        self.assertTrue(any("not restored" in p for p in run.post_run_problems))


if __name__ == "__main__":
    unittest.main()
