"""Finding 7 and nits 3, 15 and 16: individual procedures, against fakes."""

import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.proof_run import CaseResult, ProofRun
from tests.fakes import FakeSession, NoSettle, http_reply, make_run, record, set_up


def run_cases(only: set[str], behaviours: dict[str, Any]) -> ProofRun:
    run, _server = make_run(behaviours=behaviours)
    with NoSettle():
        set_up(run)
        run.run_matrix(only)
    return run


def case_of(run: ProofRun, case_id: str) -> CaseResult:
    return next(c for c in run.case_results if c.case_id == case_id)


class LeakTermsTest(unittest.TestCase):
    """Finding 7: the guest and anonymous probes look for more than message text."""

    def test_terms(self) -> None:
        cases = {c.id: c for c in matrix.all_cases()}
        for gid in ("G2", "G3"):
            read_ab = set(cases[f"{gid}-read-ab"].leak_terms)
            for term in ("{AB}", "{A}", "{B}", "{A_name}", "{B_name}", "{m_a}", "{m_b}"):
                self.assertIn(term, read_ab)
            message = set(cases[f"{gid}-message"].leak_terms)
            for term in ("{m_x}", "{X}", "{XD}", "{xd_text}"):
                self.assertIn(term, message)
            self.assertEqual(
                cases[f"{gid}-channels"].action, "query channels whose members include A"
            )

    def test_channel_object_without_text_is_a_leak(self) -> None:
        def anon(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                cid = f"glow-match:{params['id']}"
                body = {"channel": {"cid": cid}, "messages": []}
                return Reply(True, {}, None, [record(201, body)], api_calls=1)
            return None

        run = run_cases({"G3-read-ab"}, {"anonymous": anon})
        case = case_of(run, "G3-read-ab")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn(run.ctx["AB"], case.reason)


class ClaimRequestLineTest(unittest.TestCase):
    """Nit 3: the user_id shown is the one the client actually sent."""

    def claim(self, params: dict[str, str]) -> CaseResult:
        def claimer(session: FakeSession, op: str, p: dict[str, Any]) -> Reply | None:
            if op == "call":
                rec = record(403, {"code": 17}, path=f"/channels/glow-match/{p['id']}/query")
                rec["params"] = dict(params)
                error = {"status": 403, "code": 17, "message": "no", "kind": "api"}
                return Reply(False, None, error, [rec], api_calls=1)
            return None

        return case_of(run_cases({"T4-rest-xd"}, {"claim-XD": claimer}), "T4-rest-xd")

    def test_user_id_from_the_recorded_request(self) -> None:
        run, _ = make_run()
        with NoSettle():
            set_up(run)
        case = self.claim({"user_id": run.ctx["X"], "api_key": "k"})
        self.assertTrue(case.request.endswith("?user_id={X}"), case.request)

    def test_no_user_id_is_not_invented(self) -> None:
        case = self.claim({"api_key": "k"})
        self.assertNotIn("user_id", case.request)


class CheckRedactionTest(unittest.TestCase):
    """Nit 15: check evidence is redacted before it is stored."""

    def test_check_evidence_is_redacted(self) -> None:
        run, _ = make_run()
        token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoieCJ9.c2lnbmF0dXJl"
        run._check("X1", "a check", True, f"got {token}")
        self.assertNotIn(token, run.checks[0].evidence)
        self.assertIn("<redacted-jwt>", run.checks[0].evidence)


class NotEffectiveTest(unittest.TestCase):
    """Nit 16: E5 and S14 also judge the connection; T4-rest-unread needs its controls."""

    def test_e5_role_carried_by_the_connection_fails(self) -> None:
        def a_role(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                return Reply(True, {"me": {"id": params["user"]["id"], "role": "admin"}}, None)
            return None

        run = run_cases({"E1", "E5"}, {"A-role": a_role})
        case = case_of(run, "E5")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertEqual(case.detail["connect_me_role"], "admin")

    def test_e5_role_kept_holds(self) -> None:
        self.assertEqual(case_of(run_cases({"E1", "E5"}, {}), "E5").verdict, matrix.HOLDS_IGNORED)

    def test_s14_profile_carried_by_the_connection_fails(self) -> None:
        def a_profile(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                user = params["user"]
                me = {"id": user["id"], "role": "user", "name": user["name"], "custom_keys": []}
                return Reply(True, {"me": me}, None)
            return None

        case = case_of(run_cases({"S14"}, {"A-profile": a_profile}), "S14")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertTrue(case.detail["connection_carried_new_fields"])

    def test_unread_refusal_without_its_controls_is_inconclusive(self) -> None:
        def refuse_unread(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "getUnreadCount":
                return http_reply(403, 17, path="/unread")
            return None

        behaviours = {"A": refuse_unread, "B": refuse_unread, "claim-unread": refuse_unread}
        case = case_of(run_cases({"T4-rest-unread"}, behaviours), "T4-rest-unread")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_unread_refusal_with_its_controls_holds(self) -> None:
        def own(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "getUnreadCount":
                total = 0 if session.label == "A" else 1
                body = {"total_unread_count": total}
                return Reply(True, {}, None, [record(200, body, path="/unread")], api_calls=1)
            return None

        def claimer(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "getUnreadCount":
                return http_reply(403, 17, path="/unread")
            return None

        behaviours = {"A": own, "B": own, "claim-unread": claimer}
        case = case_of(run_cases({"T4-rest-unread"}, behaviours), "T4-rest-unread")
        self.assertEqual(case.verdict, matrix.HOLDS)


if __name__ == "__main__":
    unittest.main()
