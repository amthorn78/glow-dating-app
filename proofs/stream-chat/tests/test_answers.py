"""Finding 1: verdicts come from Stream's recorded answer to the request under test.

An SDK error that looks like a refusal, a local throw, or a call that returned
without sending a request is never a HOLDS.
"""

import dataclasses
import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix
from glow_stream_proof.client_bridge import ClientSessionEnded, Reply
from glow_stream_proof.proof_run import (
    PRODUCTION_NO_RESPONSE_REASON,
    CaseResult,
    ProofRun,
    _http_answer,
    _ws_answer,
)
from glow_stream_proof.server_api import ApiResult
from tests.fakes import (
    Behaviour,
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
        self.assertEqual(case.reason, matrix.NO_RESPONSE_REASON)

    def test_rt3_null_return_without_a_request_is_inconclusive(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "markRead":
                return Reply(True, {}, None, [])  # read events off: null, no request
            return None

        run = self.run_cases({"RT3"}, {"A": a})
        self.assertEqual(case_of(run, "RT3").verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case_of(run, "RT3").reason, matrix.NO_RESPONSE_REASON)

    def test_rt2_feature_refusal_is_refused_feature_not_holds(self) -> None:
        # I1's recorded RT2 (400 code 18, nothing delivered) was HOLDS; since P06.1-C3
        # the same observation is "REFUSED (feature off; not a permission error)".
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                return http_reply(400, 18)
            return None

        run = self.run_cases({"RT2"}, {"A": a})
        case = case_of(run, "RT2")
        self.assertEqual(case.verdict, matrix.REFUSED_FEATURE)
        self.assertIn("400 feature error (code 18)", case.reason)


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


def at_the_sdk_path(reply: Reply, params: dict[str, Any]) -> Reply:
    """``reply`` with its recorded requests at the path stream-chat 9.53.0 sends RT2's
    ``sendEvent`` or RT3's ``markRead`` to."""
    suffix = "read" if params["method"] == "markRead" else "event"
    path = f"/channels/{params['type']}/{params['id']}/{suffix}"
    return dataclasses.replace(reply, requests=[{**r, "path": path} for r in reply.requests])


def b_reads(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
    """B's own markRead, RT3's control, succeeds."""
    if op == "call" and params.get("method") == "markRead":
        succeeded = Reply(True, {}, None, [record(201, {"event": {}})], api_calls=1)
        return at_the_sdk_path(succeeded, params)
    return None


class PayloadRefusalAttributionTest(unittest.TestCase):
    """RT2 and RT3 count a refusal only as the matrix quality rule allows.

    P06.1-C2, finding 3: an input, not-found or other refusal is INCONCLUSIVE.
    P06.1-C3, the manager's decision on C2: a feature refusal is REFUSED (feature
    off), not HOLDS, and an authentication or permission refusal HOLDS only when
    the same request by a member allowed to make it succeeded: B's own markRead
    for RT3; RT2 has no such control while typing events are off.
    """

    def payload_run(self, case_id: str, reply: Reply, b: Behaviour | None = None) -> ProofRun:
        method = "sendEvent" if case_id == "RT2" else "markRead"

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == method:
                return at_the_sdk_path(reply, params)
            return None

        run, _server = make_run(behaviours={"A": a})
        with NoSettle():
            set_up(run)
            session = run.sessions["B"]
            assert isinstance(session, FakeSession)
            session.behaviour = b
            run.run_matrix({case_id})
        return run

    def payload_case(self, case_id: str, reply: Reply) -> CaseResult:
        return case_of(self.payload_run(case_id, reply), case_id)

    @staticmethod
    def sent(run: ProofRun, label: str, method: str) -> list[dict[str, Any]]:
        session = run.sessions[label]
        assert isinstance(session, FakeSession)
        return [p for op, p in session.sent if op == "call" and p.get("method") == method]

    def test_input_not_found_and_other_refusals_are_inconclusive(self) -> None:
        for case_id in ("RT2", "RT3"):
            for status, code, outcome in (
                (400, 4, "input"),
                (404, 16, "not-found"),
                (503, None, "other"),
            ):
                case = self.payload_case(case_id, http_reply(status, code))
                self.assertEqual(case.verdict, matrix.INCONCLUSIVE, (case_id, status))
                self.assertEqual(case.reason, f"refusal not attributable ({outcome})")

    def test_feature_refusals_are_refused_feature_not_holds(self) -> None:
        for case_id in ("RT2", "RT3"):
            for code in (18, 19):
                case = self.payload_case(case_id, http_reply(400, code))
                self.assertEqual(case.verdict, matrix.REFUSED_FEATURE, (case_id, code))
                self.assertIn(f"400 feature error (code {code})", case.reason)

    def test_rt2_auth_or_permission_refusal_has_no_positive_control(self) -> None:
        for status, code, outcome in ((403, 17, "permission"), (401, 5, "auth")):
            run = self.payload_run("RT2", http_reply(status, code))
            case = case_of(run, "RT2")
            self.assertEqual(case.verdict, matrix.INCONCLUSIVE, status)
            self.assertIn(f"{outcome} error, but no positive control", case.reason)
            self.assertTrue(case.control.endswith("; no positive control"), case.control)
            self.assertEqual(self.sent(run, "B", "sendEvent"), [])  # no member can send it

    def test_rt3_auth_or_permission_refusal_holds_with_bs_own_request(self) -> None:
        for status, code, outcome in ((403, 17, "permission"), (401, 5, "auth")):
            run = self.payload_run("RT3", http_reply(status, code), b_reads)
            case = case_of(run, "RT3")
            self.assertEqual(case.verdict, matrix.HOLDS, (status, case.reason))
            self.assertIn(f"{outcome} error; the same request by B succeeded", case.reason)
            self.assertIn("B's own identical request: 201 (succeeded)", case.control)
            # The control is the same request, with the same body, made by B.
            self.assertEqual(self.sent(run, "B", "markRead"), self.sent(run, "A", "markRead"))

    def test_rt3_refusal_without_a_successful_control_is_inconclusive(self) -> None:
        # B's own markRead is refused as well (the fakes refuse B's calls).
        case = self.payload_case("RT3", http_reply(403, 17))
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, "permission error, but the positive control did not succeed")
        self.assertIn("B's own identical request: 403 / code 17", case.control)

    def test_rt3_control_that_was_another_request_is_inconclusive(self) -> None:
        # The independent review of P06.1-C3: the control counts only if it was the same
        # request, by method and path, not merely the same SDK call.
        def b_reads_elsewhere(
            session: FakeSession, op: str, params: dict[str, Any]
        ) -> Reply | None:
            if op == "call" and params.get("method") == "markRead":
                path = "/channels/glow-match/other/read"
                return http_reply(201, response={"event": {}}, path=path)
            return None

        case = case_of(self.payload_run("RT3", http_reply(403, 17), b_reads_elsewhere), "RT3")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(
            case.reason,
            "permission error, but the positive control was another request "
            "(POST /channels/glow-match/other/read)",
        )

    def test_rt3_controls_own_events_are_not_searched(self) -> None:
        # B's own markRead raises B's own message.read. Were Stream to echo B's custom
        # fields in it, the marker would be B's own, not something A put before B.
        def b_reads_and_echoes(
            session: FakeSession, op: str, params: dict[str, Any]
        ) -> Reply | None:
            if op == "call" and params.get("method") == "markRead":
                marker = params["args"][0]["glow_text"]
                echo = {"type": "message.read", "user": {"id": "b"}, "glow_text": marker}
                session.pending_events.append(echo)
            return b_reads(session, op, params)

        run = self.payload_run("RT3", http_reply(403, 17), b_reads_and_echoes)
        case = case_of(run, "RT3")
        self.assertEqual(case.verdict, matrix.HOLDS, case.reason)
        self.assertEqual(case.detail["marker_event_types"], [])
        self.assertEqual(case.detail["control_event_types"], ["message.read"])

    def test_a_refusal_while_b_is_not_listening_is_inconclusive(self) -> None:
        # The C2 review's nit 4: this C1 rule had no test of its own. Unless B's
        # listener saw the probe, no refusal shows that nothing reached B.
        def b_not_listening(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "events":
                session.pending_events.clear()
                return Reply(True, {"events": []}, None)
            return b_reads(session, op, params)

        for case_id, reply in (("RT3", http_reply(403, 17)), ("RT2", http_reply(400, 18))):
            case = case_of(self.payload_run(case_id, reply, b_not_listening), case_id)
            self.assertEqual(case.verdict, matrix.INCONCLUSIVE, case_id)
            self.assertEqual(case.reason, "B's listener did not see the probe")

    def test_named_events_after_an_unattributable_refusal_are_inconclusive(self) -> None:
        # Events of the named type arrived, but Stream refused A's request with an
        # input error: that says nothing about what A's event delivers.
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "events" and session.pending_events:
                session.pending_events.append({"type": "message.read", "cid": "x"})
            return None

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "markRead":
                return http_reply(400, 4)
            return None

        run, _server = make_run(behaviours={"A": a, "B": b})
        with NoSettle():
            set_up(run)
            run.run_matrix({"RT3"})
        self.assertEqual(case_of(run, "RT3").verdict, matrix.INCONCLUSIVE)


class ProductionPhaseAnswerTest(unittest.TestCase):
    """P06.1-C2, the C1 review's nit 5: the production-phase request must have an answer."""

    @staticmethod
    def second_call_throws(method: str) -> Any:
        calls: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == method:
                calls.append(1)
                if len(calls) == 2:  # the production phase
                    return local_error("thrown locally")
            return None

        return a

    def test_feature_gated_case_without_a_production_answer_is_inconclusive(self) -> None:
        run, _server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = self.second_call_throws("sendMessage")
            run.run_matrix({"S2"})
        case = case_of(run, "S2")
        self.assertIn("feature off (production): no answer recorded", case.observed)
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, PRODUCTION_NO_RESPONSE_REASON)

    def test_feature_gated_case_with_a_production_refusal_holds(self) -> None:
        run, _server = make_run()
        with NoSettle():
            set_up(run)
            run.run_matrix({"S2"})
        self.assertEqual(case_of(run, "S2").verdict, matrix.HOLDS)

    def test_a_production_command_with_several_requests(self) -> None:
        # The independent review of P06.1-C3: S5's production command recorded a 201
        # and then a 403. The row lists both (it was built before the production
        # phase), the case is INCONCLUSIVE (the command has no answer), and the 201 is
        # undone like any client success.
        calls: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendReaction":
                calls.append(1)
                path = f"/messages/{params['args'][0]}/reaction"
                if len(calls) == 1:  # the feature-on phase: refused
                    return http_reply(403, 17, path=path)
                error = {"status": 403, "code": 17, "message": "x", "kind": "api"}
                requests = [
                    record(201, {"reaction": {}}, path=path),
                    record(403, {"code": 17}, path=path),
                ]
                return Reply(False, None, error, requests, api_calls=2)
            return None

        run, server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = a
            run.run_matrix({"S5"})
        case = case_of(run, "S5")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, PRODUCTION_NO_RESPONSE_REASON)
        self.assertEqual(
            case.detail["requests"],
            [
                "client A call sendReaction: POST /messages/{m_b}/reaction -> 201, "
                "POST /messages/{m_b}/reaction -> 403"
            ],
        )
        undo_path = f"/messages/{run.ctx['m_b']}/reaction/love"
        undos = [c for c in server.calls if c[0] == "DELETE" and c[1] == undo_path]
        # The server replay's own undo in the feature-on phase, then the production 201's.
        self.assertEqual(len(undos), 2)
        self.assertTrue(case.detail["client_success_undo"].startswith("undo DELETE"))

    def test_poll_vote_without_a_production_answer_is_inconclusive(self) -> None:
        run, _server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = self.second_call_throws("castPollVote")
            run.run_matrix({"S10"})
        case = case_of(run, "S10")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, PRODUCTION_NO_RESPONSE_REASON)

    @staticmethod
    def first_call_succeeds_second_throws(method: str, path: str) -> Behaviour:
        calls: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == method:
                calls.append(1)
                if len(calls) == 1:  # the feature-on (or polls-on) phase: a bypass
                    return Reply(True, {}, None, [record(201, {}, path=path)], api_calls=1)
                return local_error("thrown locally")  # the production phase: no answer
            return None

        return a

    def test_feature_on_fail_survives_a_production_request_without_an_answer(self) -> None:
        # The C2 review's nit 4: a FAIL seen with the feature on stays a FAIL.
        run, _server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = self.first_call_succeeds_second_throws("sendMessage", "/x/message")
            run.run_matrix({"S2"})
        case = case_of(run, "S2")
        self.assertIn("feature off (production): no answer recorded", case.observed)
        self.assertEqual(case.verdict, matrix.FAIL)

    def test_polls_on_fail_survives_a_production_vote_without_an_answer(self) -> None:
        run, _server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = self.first_call_succeeds_second_throws("castPollVote", "/x/vote")
            run.run_matrix({"S10"})
        case = case_of(run, "S10")
        self.assertIn("polls off (production): no answer recorded", case.observed)
        self.assertEqual(case.verdict, matrix.FAIL)


class FeatureOnFailTest(unittest.TestCase):
    """P06.1-C3, the C2 review's finding 1: an observed FAIL survives a failed enabling
    request. "Could not enable" applies only when no FAIL was observed."""

    @staticmethod
    def enable_refused(case_id: str, sdk_method: str | None) -> CaseResult:
        """``case_id`` with its enabling request answered 500; A's first ``sdk_method``
        call (the feature-on phase) gets 201 when it is given."""
        run, server = make_run()
        calls: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == sdk_method:
                calls.append(1)
                if len(calls) == 1:
                    return Reply(True, {}, None, [record(201, {})], api_calls=1)
            return None

        def refuse_enable(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if (method == "PATCH" and overrides) or (
                method == "PUT" and (body or {}).get("custom_events") is True
            ):
                return ApiResult(method, path, 500, -1, "internal", {})
            return None

        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = a
            server.handlers.append(refuse_enable)
            run.run_matrix({case_id})
        return case_of(run, case_id)

    def test_fail_survives_a_failed_enabling_request(self) -> None:
        # The review's reproduction (S2): the PATCH enabling replies got 500, and A's
        # thread reply got 201. The same with a type-level feature (S12).
        for case_id, sdk_method in (("S2", "sendMessage"), ("S12", "sendEvent")):
            case = self.enable_refused(case_id, sdk_method)
            self.assertEqual(case.verdict, matrix.FAIL, (case_id, case.reason))
            self.assertEqual(case.reason, "the client action succeeded")
            self.assertEqual(case.detail["feature_override"]["set_status"], 500)
            self.assertTrue(case.observed.startswith("feature on: 201 (succeeded)"), case.observed)

    def test_without_an_observed_fail_the_case_is_inconclusive(self) -> None:
        case = self.enable_refused("S2", None)
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, "could not enable {'replies': True} (channel AB, 500)")


class OneRequestTest(unittest.TestCase):
    """P06.1-C2, the C1 review's nit 6: a command that must send one request sent one."""

    def test_two_recorded_requests_have_no_answer(self) -> None:
        reply = Reply(False, None, None, [record(403, {"code": 17}), record(403, {"code": 17})])
        answer = _http_answer(reply)
        self.assertEqual(answer.outcome, "no-response")
        self.assertIn("2 requests recorded", answer.note)

    def test_generic_case_with_two_requests_is_inconclusive(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "watch":
                first = record(201, {"channel": {}})
                second = record(403, {"code": 17})
                error = {"status": 403, "code": 17, "message": "x", "kind": "api"}
                return Reply(False, None, error, [first, second], api_calls=2)
            return None

        run, _server = make_run(behaviours={"A": a})
        with NoSettle():
            set_up(run)
            run.run_matrix({"R1"})
        case = case_of(run, "R1")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.request, "-")

    def test_each_request_of_a_command_is_kept_and_a_success_is_undone(self) -> None:
        # P06.1-C3, the C2 review's nit 5: S3a's edit got 201, then a second request
        # 403. The row keeps both, and the 201 is undone like any client success.
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "updateMessage":
                path = f"/messages/{params['args'][0]['id']}"
                first = record(201, {"message": {}}, path=path)
                second = record(403, {"code": 17}, path=path)
                error = {"status": 403, "code": 17, "message": "x", "kind": "api"}
                return Reply(False, None, error, [first, second], api_calls=2)
            return None

        run, server = make_run(behaviours={"A": a})
        with NoSettle():
            set_up(run)
            run.run_matrix({"S3a", "S3b"})
        case = case_of(run, "S3a")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(
            case.detail["requests"],
            [
                "client A call updateMessage: "
                "POST /messages/{m_a} -> 201, POST /messages/{m_a} -> 403"
            ],
        )
        self.assertEqual(case.detail["client_success_undo"], "undo POST 201")
        undo = [
            c
            for c in server.calls
            if c[1] == f"/messages/{run.ctx['m_a']}"
            and ((c[2] or {}).get("message") or {}).get("text") == run.ctx["m_a_text"]
        ]
        self.assertEqual(len(undo), 1)
        # Each row lists only its own case's commands, and none that sent one request.
        self.assertEqual(
            case_of(run, "S3b").detail["requests"],
            [
                "client A call updateMessage: "
                "POST /messages/{m_b} -> 201, POST /messages/{m_b} -> 403"
            ],
        )

    def test_a_row_without_such_a_command_lists_no_requests(self) -> None:
        run, _server = make_run()
        with NoSettle():
            set_up(run)
            run.run_matrix({"R1"})
        self.assertNotIn("requests", case_of(run, "R1").detail)

    def test_a_poll_created_among_several_requests_is_deleted_at_cleanup(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "createPoll":
                created = record(201, {"poll": {"id": "client-poll"}}, path="/polls")
                refused = record(403, {"code": 17}, path="/polls")
                error = {"status": 403, "code": 17, "message": "x", "kind": "api"}
                return Reply(False, None, error, [created, refused], api_calls=2)
            return None

        run, _server = make_run(behaviours={"A": a})
        with NoSettle():
            set_up(run)
            run.run_matrix({"S9"})
        self.assertEqual(case_of(run, "S9").verdict, matrix.INCONCLUSIVE)
        self.assertIn("client-poll", [poll_id for poll_id, _owner in run.polls])

    def test_guest_attempt_with_another_request_has_no_answer(self) -> None:
        def attempt(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "guest":
                refused = record(403, {"code": 17}, path="/guest")
                other = record(403, {"code": 17}, path="/users")
                error = {"status": 403, "code": 17, "message": "x", "kind": "api"}
                return Reply(False, None, error, [refused, other], api_calls=2)
            return None

        run, _server = make_run(behaviours={"guest-attempt": attempt})
        with NoSettle():
            set_up(run)
            run.run_matrix({"G1-create"})
        self.assertEqual(case_of(run, "G1-create").verdict, matrix.INCONCLUSIVE)


if __name__ == "__main__":
    unittest.main()
