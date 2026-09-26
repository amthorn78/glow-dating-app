"""Finding 1: verdicts come from Stream's recorded answer to the request under test.

An SDK error that looks like a refusal, a local throw, or a call that returned
without sending a request is never a HOLDS.
"""

import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix
from glow_stream_proof.client_bridge import ClientSessionEnded, Reply
from glow_stream_proof.proof_run import CaseResult, ProofRun, _http_answer, _ws_answer
from tests.fakes import (
    FakeSession,
    NoSettle,
    http_reply,
    local_error,
    make_run,
    record,
    set_up,
    ws_refused,
)


def case_of(run: ProofRun, case_id: str) -> CaseResult:
    return next(c for c in run.case_results if c.case_id == case_id)


class AnswerTest(unittest.TestCase):
    def test_sdk_error_without_a_request_has_no_answer(self) -> None:
        answer = _http_answer(local_error())
        self.assertEqual(answer.outcome, "no-response")
        self.assertIsNone(answer.status)

    def test_status_and_code_come_from_the_record_not_the_sdk_error(self) -> None:
        error = {"status": 403, "code": 17, "message": "x", "kind": "error"}
        self.assertEqual(
            _http_answer(Reply(False, None, error, [record(201, {})])).outcome, "success"
        )
        answer = _http_answer(Reply(False, None, error, [record(400, {"code": 4})]))
        self.assertEqual((answer.outcome, answer.status, answer.code), ("input", 400, 4))

    def test_a_request_without_a_response_has_no_answer(self) -> None:
        self.assertEqual(
            _http_answer(Reply(False, None, None, [record(None)])).outcome, "no-response"
        )

    def test_null_return_without_a_request_has_no_answer(self) -> None:
        self.assertEqual(_http_answer(Reply(True, {}, None, [])).outcome, "no-response")

    def test_ws_answer_trusts_only_streams_error_frame(self) -> None:
        self.assertEqual(_ws_answer(ws_refused(401, 5)).outcome, "auth")
        self.assertEqual(_ws_answer(ws_refused(401, 5, kind="ws-failure")).outcome, "no-response")
        self.assertEqual(_ws_answer(local_error()).outcome, "no-response")
        self.assertEqual(_ws_answer(Reply(True, {"me": {"id": "a"}}, None)).outcome, "success")
        self.assertEqual(_ws_answer(Reply(True, {}, None)).outcome, "no-response")

    def test_no_verdict_holds_without_an_answer(self) -> None:
        for control in (True, False):
            verdict = matrix.refused_verdict("no-response", control)
            self.assertEqual(verdict.label, matrix.INCONCLUSIVE)
        self.assertEqual(
            matrix.no_leak_verdict("no-response", [], True, True).label, matrix.INCONCLUSIVE
        )
        self.assertEqual(
            matrix.not_effective_verdict(False, "no-response", True).label, matrix.INCONCLUSIVE
        )


class RequestUnderTestInCasesTest(unittest.TestCase):
    def run_cases(self, only: set[str], behaviours: dict[str, Any]) -> ProofRun:
        run, _server = make_run(behaviours=behaviours)
        with NoSettle():
            set_up(run)
            run.run_matrix(only)
        return run

    def test_generic_case_uses_the_record_not_the_sdk_error(self) -> None:
        # The SDK reports 403 / 17, but Stream's recorded answer to A's watch of XD is 201.
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if (
                op == "call"
                and params.get("method") == "watch"
                and params.get("id", "").endswith("-ch-xd")
            ):
                error = {"status": 403, "code": 17, "message": "x", "kind": "error"}
                return Reply(False, None, error, [record(201, {"channel": {}})], api_calls=1)
            return None

        run = self.run_cases({"R1"}, {"A": a})
        self.assertEqual(case_of(run, "R1").verdict, matrix.FAIL)

    def test_generic_case_without_a_request_is_inconclusive(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "watch":
                return local_error()
            return None

        run = self.run_cases({"R1"}, {"A": a})
        case = case_of(run, "R1")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, matrix.NO_RESPONSE_REASON)

    def test_g1_fails_whenever_the_clients_post_guest_created_a_guest(self) -> None:
        # POST /guest 201 created a guest; the lockdown then refused its connect.
        def attempt(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "guest":
                stored = f"guest-1-{params['user']['id']}"
                created = record(201, {"user": {"id": stored, "role": "guest"}}, path="/guest")
                return Reply(False, None, ws_refused().error, [created], api_calls=1)
            return None

        run = self.run_cases({"G1-create"}, {"guest-attempt": attempt})
        case = case_of(run, "G1-create")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertTrue(case.detail["client_guest_user_exists_after"])
        self.assertIn("guest-1-", " ".join(run.users))

    def test_g1_judges_the_post_guest_answer(self) -> None:
        run = self.run_cases({"G1-create"}, {})
        case = case_of(run, "G1-create")
        self.assertEqual(case.observed, "403 / code 17")
        self.assertEqual(case.verdict, matrix.HOLDS)

    def test_g3_is_inconclusive_unless_the_anonymous_connect_succeeded(self) -> None:
        # A failed anonymous connect makes the SDK rethrow it for every probe.
        def anon(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "anonymous":
                return ws_refused(403, 17)
            if op == "call":
                return local_error("rethrown connect error")
            return None

        g3 = {"G3-read-ab", "G3-channels", "G3-users", "G3-message"}
        run = self.run_cases(g3, {"anonymous": anon})
        for case_id in g3:
            case = case_of(run, case_id)
            self.assertEqual(case.verdict, matrix.INCONCLUSIVE, case_id)
            self.assertIn("anonymous connect", case.observed)
        anonymous = run.sessions["anonymous"]
        assert isinstance(anonymous, FakeSession)
        self.assertEqual([op for op, _ in anonymous.sent], ["anonymous"])

    def test_g3_probe_without_a_request_is_inconclusive(self) -> None:
        def anon(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            return local_error() if op == "call" else None

        run = self.run_cases({"G3-users"}, {"anonymous": anon})
        self.assertEqual(case_of(run, "G3-users").verdict, matrix.INCONCLUSIVE)

    def test_rt2_local_throw_is_inconclusive(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                return local_error("channel is not initialized")
            return None

        run = self.run_cases({"RT2"}, {"A": a})
        case = case_of(run, "RT2")
        self.assertEqual(case.control, "B listening (received a probe message): True")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_rt3_null_return_without_a_request_is_inconclusive(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "markRead":
                return Reply(True, {}, None, [])  # read events off: null, no request
            return None

        run = self.run_cases({"RT3"}, {"A": a})
        self.assertEqual(case_of(run, "RT3").verdict, matrix.INCONCLUSIVE)

    def test_rt2_refused_by_stream_with_nothing_delivered_holds(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                return http_reply(400, 18)
            return None

        run = self.run_cases({"RT2"}, {"A": a})
        case = case_of(run, "RT2")
        self.assertEqual(case.verdict, matrix.HOLDS)
        self.assertIn("refused (feature)", case.reason)


class AnonymousConnectWithoutAnswerTest(unittest.TestCase):
    """The review's nit: an anonymous connect that never answered is not a KeyError."""

    def test_later_probes_are_inconclusive(self) -> None:
        def anon(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "anonymous":
                raise ClientSessionEnded("client anonymous ended: no reply within 60s")
            return None

        run, _server = make_run(behaviours={"anonymous": anon})
        with NoSettle():
            set_up(run)
            run.run_matrix({"G3-read-ab", "G3-users"})
        first, second = run.case_results
        self.assertIn("client session ended", first.reason)
        self.assertEqual(second.verdict, matrix.INCONCLUSIVE)
        self.assertIn("the anonymous connect did not answer", second.observed)


if __name__ == "__main__":
    unittest.main()
