"""Finding 7 and nits 3, 15 and 16: individual procedures, against fakes."""

import unittest
from typing import Any

import jwt

import tests  # noqa: F401
from glow_stream_proof import matrix
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.proof_run import CaseResult, ProofRun
from glow_stream_proof.server_api import ApiResult
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
        token = jwt.encode({"user_id": "x"}, "synthetic-offline-secret", "HS256")
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


def unread(total: int | None, status: int = 200) -> Reply:
    body: dict[str, Any] = {} if total is None else {"total_unread_count": total}
    if status >= 300:
        return http_reply(status, 17, path="/unread")
    return Reply(True, {}, None, [record(status, body, path="/unread")], api_calls=1)


class UnreadControlsTest(unittest.TestCase):
    """P06.1-C2, finding 2: T4-rest-unread HOLDS only with both controls and all totals."""

    def unread_case(self, a: Reply, b: Reply, claim: Reply) -> CaseResult:
        def answering(reply: Reply) -> Any:
            def behaviour(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
                if op == "call" and params.get("method") == "getUnreadCount":
                    return reply
                return None

            return behaviour

        behaviours = {"A": answering(a), "B": answering(b), "claim-unread": answering(claim)}
        return case_of(run_cases({"T4-rest-unread"}, behaviours), "T4-rest-unread")

    def test_as_own_control_refused_is_inconclusive(self) -> None:
        # The review's reproduction: A's own request refused, B's answered 1, and the
        # claim answered 2xx without the field.
        case = self.unread_case(unread(None, 403), unread(1), unread(None))
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.control, "A's own total None; B's own total 1")

    def test_a_missing_total_is_inconclusive(self) -> None:
        # Both controls answered 2xx, but A's carried no total, and nor did the claim.
        case = self.unread_case(unread(None), unread(1), unread(None))
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_b_count_with_as_control_failed_is_inconclusive(self) -> None:
        case = self.unread_case(unread(None, 403), unread(1), unread(1))
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_claim_ignored_with_both_controls_holds(self) -> None:
        case = self.unread_case(unread(0), unread(1), unread(0))
        self.assertEqual(case.verdict, matrix.HOLDS_IGNORED)

    def test_bs_count_returned_fails(self) -> None:
        case = self.unread_case(unread(0), unread(1), unread(1))
        self.assertEqual(case.verdict, matrix.FAIL)


class StoredUserUnreadableTest(unittest.TestCase):
    """P06.1-C2, the C1 review's nit 7: an unreadable stored user is not a result."""

    @staticmethod
    def run_with_unreadable_first_read(cases: set[str], behaviours: dict[str, Any]) -> ProofRun:
        run, server = make_run(behaviours=behaviours)
        reads: list[int] = []

        def listing(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if (
                method == "GET"
                and path == "/api/v2/users"
                and '"$eq"' in (params or {}).get("payload", "")
            ):
                reads.append(1)
                if len(reads) == 1:  # the read of A's stored user after the connect
                    return ApiResult(method, path, 200, None, None, {"users": []})
                user = {"id": run.ctx["A"], "role": "user", "name": "renamed on connect by A"}
                return ApiResult(method, path, 200, None, None, {"users": [user]})
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(listing)
            run.run_matrix(cases)
        return run

    def test_e5_is_inconclusive_when_as_stored_user_cannot_be_read(self) -> None:
        run = self.run_with_unreadable_first_read({"E1", "E5"}, {})
        case = case_of(run, "E5")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, "A's stored user could not be read")
        self.assertFalse(case.detail["stored_user_read"])
        self.assertFalse(any("E5" in n for n in run.notes))  # no role "restored"

    def test_s14_is_inconclusive_when_as_stored_user_cannot_be_read(self) -> None:
        run = self.run_with_unreadable_first_read({"S14"}, {})
        case = case_of(run, "S14")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, "A's stored user could not be read")

    def test_server_user_matches_the_id(self) -> None:
        run, server = make_run()
        server.users["someone-else"] = {"id": "someone-else", "role": "admin"}

        def everyone(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "GET" and path == "/api/v2/users":
                return ApiResult(
                    method, path, 200, None, None, {"users": list(server.users.values())}
                )
            return None

        server.handlers.append(everyone)
        self.assertIsNone(run._server_user("p061i1-simulated-ua"))
        self.assertEqual(run._server_user("someone-else"), {"id": "someone-else", "role": "admin"})


if __name__ == "__main__":
    unittest.main()
