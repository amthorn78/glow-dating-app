import unittest

import tests  # noqa: F401
from glow_stream_proof import matrix, proof_run
from glow_stream_proof.configuration import DEFAULT_TYPES


class MatrixDefinitionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = matrix.all_cases()
        self.ids = {c.id for c in self.cases}

    def test_structurally_valid(self) -> None:
        self.assertEqual(matrix.validate(self.cases), [])

    def test_every_case_has_a_positive_control(self) -> None:
        for case in self.cases:
            self.assertNotEqual(case.control.kind, "none", case.id)

    def test_required_coverage(self) -> None:
        required = {
            # tokens: dev, wrong secret, expired (REST and WebSocket), A acting as B/X
            "T1-rest",
            "T1-ws",
            "T2-rest",
            "T2-ws",
            "T3-rest",
            "T3-ws",
            "T4-ws",
            "T4-rest-xd",
            "T4-rest-unread",
            # guest and anonymous access
            "G1-create",
            "G2-read-ab",
            "G2-channels",
            "G2-users",
            "G2-message",
            "G3-read-ab",
            "G3-channels",
            "G3-users",
            "G3-message",
            # creating, joining and changing
            "C1",
            "C7",
            "C8",
            "C9",
            "C10a",
            "C10b",
            "C11",
            "C12",
            "C13",
            # reading outside the match
            "R1",
            "R2",
            "R3",
            "R4",
            "R5",
            "R6",
            "R7a",
            "R7b",
            "R8a",
            "R8b",
            "R9",
            # content in front of B
            "S1",
            "S2",
            "S3a",
            "S3b",
            "S4a",
            "S4b",
            "S5",
            "S6",
            "S7",
            "S8",
            "S9",
            "S10",
            "S11",
            "S12",
            "S13",
            "S14",
            "S15",
            # self-escalation
            "E1",
            "E2",
            "E3",
            "E4",
            "E5",
            "E6",
            # realtime
            "RT1",
            "RT2",
            "RT3",
        }
        self.assertEqual(required - self.ids, set())

    def test_every_default_type_is_covered(self) -> None:
        for n, ctype in enumerate(DEFAULT_TYPES, start=2):
            for verb in ("create", "read", "send", "join"):
                case = next(c for c in self.cases if c.id == f"C{n}-{verb}")
                self.assertIn(ctype, case.action)

    def test_destructive_cases_run_last(self) -> None:
        order = [c.id for c in self.cases]
        for destructive in ("S4a", "S4b", "C12", "C13"):
            for earlier in ("S3a", "S5", "S8", "R6", "C11"):
                self.assertLess(order.index(earlier), order.index(destructive))
        # C13 deletes AB, so it is the last case that uses it. P06.1-I2b's Video and Feeds
        # cases come after it, on objects of their own, and P06.1-I2a's families after
        # them: each runs on users and a channel of its own.
        on_ab = [
            c.id
            for c in self.cases
            if c.phase < proof_run.FAMILY_PHASE and matrix.product_of(c) is None
        ]
        self.assertEqual(on_ab[-1], "C13")
        product_cases = [c.id for c in self.cases if matrix.product_of(c) is not None]
        self.assertEqual(product_cases, matrix.product_case_ids())
        self.assertLess(order.index("C13"), order.index(product_cases[0]))
        self.assertLess(order.index(product_cases[-1]), order.index("RV-remove"))
        families = [c for c in self.cases if c.phase >= proof_run.FAMILY_PHASE]
        self.assertEqual(
            [c.id for c in families],
            [
                "RV-remove",
                "RV-ban",
                "RV-hide",
                "RV-freeze",
                "RV-revoke",
                "SD-deactivate",
                "SD-delete",
            ],
        )
        self.assertEqual(order[-len(families) :], [c.id for c in families])

    def test_no_case_acts_as_a_privileged_role(self) -> None:
        for case in self.cases:
            if case.step is not None:
                self.assertIn(case.step.session, ("A", "B", "X"))

    def test_placeholders_resolve_with_a_full_context(self) -> None:
        ctx = {
            k: f"v-{k}"
            for k in (
                "A",
                "B",
                "X",
                "D",
                "AB",
                "XD",
                "AB_cid",
                "XD_cid",
                "m_a",
                "m_b",
                "m_x",
                "m_a_text",
                "member_marker",
                "m_b_text",
                "xd_text",
                "prefix",
                "A_name",
                "B_name",
                "X_name",
                "D_name",
                "run_start",  # P06.1-I2a: F9-sync
                # P06.1-I2b: the Video and Feeds cases' objects and markers.
                "CALL",
                "CALL_a",
                "CALL_dev",
                "CALL_x",
                "ACT",
                "FG",
                "FGT",
                "vd_text",
                "fd_text",
            )
        }
        for case in self.cases:
            if case.step is not None:
                matrix.substitute(dict(case.step.params), ctx)
            matrix.substitute(list(case.leak_terms), ctx)
            matrix.substitute(dict(case.control.body_patch), ctx)
            for undo in case.control.undo:
                matrix.substitute(undo.path, ctx)
                if undo.body is not None:
                    matrix.substitute(dict(undo.body), ctx)


class SubstituteAndMergeTest(unittest.TestCase):
    def test_substitute(self) -> None:
        ctx = {"A": "ua", "AB": "ch"}
        out = matrix.substitute({"{A}": ["{AB}", {"k": "x{A}y"}], "n": 1}, ctx)
        self.assertEqual(out, {"ua": ["ch", {"k": "xuay"}], "n": 1})
        with self.assertRaises(matrix.MissingPlaceholder):
            matrix.substitute("{nope}", ctx)

    def test_deep_merge(self) -> None:
        base = {"message": {"text": "t"}, "keep": 1}
        self.assertEqual(
            matrix.deep_merge(base, {"message": {"user_id": "u"}}),
            {"message": {"text": "t", "user_id": "u"}, "keep": 1},
        )
        self.assertEqual(base, {"message": {"text": "t"}, "keep": 1})
        self.assertEqual(matrix.deep_merge(None, {"a": 1}), {"a": 1})


class ClassificationTest(unittest.TestCase):
    def test_classify(self) -> None:
        self.assertEqual(matrix.classify(200, None), "success")
        self.assertEqual(matrix.classify(201, None), "success")
        for code in (5, 40, 41, 42, 43):
            self.assertEqual(matrix.classify(401, code), "auth")
        self.assertEqual(matrix.classify(403, 17), "permission")
        self.assertEqual(matrix.classify(403, 70), "permission")
        self.assertEqual(matrix.classify(400, 19), "feature")
        self.assertEqual(matrix.classify(400, 4), "input")
        self.assertEqual(matrix.classify(404, 16), "not-found")
        self.assertEqual(matrix.classify(401, 99), "other")
        self.assertEqual(matrix.classify(403, 60), "other")
        self.assertEqual(matrix.classify(None, 17), "no-response")

    def test_api_key_error_is_not_a_token_refusal(self) -> None:
        # Nit 2: Stream's code 2 is an API-key error, not attributable to the token.
        self.assertEqual(matrix.classify(401, 2), "other")
        self.assertEqual(matrix.refused_verdict("other", True).label, matrix.INCONCLUSIVE)

    def test_refused_verdict_requires_attributable_error_and_control(self) -> None:
        self.assertEqual(matrix.refused_verdict("permission", True).label, matrix.HOLDS)
        self.assertEqual(matrix.refused_verdict("auth", True).label, matrix.HOLDS)
        self.assertEqual(matrix.refused_verdict("permission", False).label, matrix.INCONCLUSIVE)
        self.assertEqual(matrix.refused_verdict("success", True).label, matrix.FAIL)
        self.assertEqual(matrix.refused_verdict("input", True).label, matrix.INCONCLUSIVE)
        self.assertEqual(matrix.refused_verdict("not-found", True).label, matrix.INCONCLUSIVE)
        self.assertEqual(matrix.refused_verdict("feature", True).label, matrix.REFUSED_FEATURE)

    def test_no_leak_verdict(self) -> None:
        self.assertEqual(matrix.no_leak_verdict("success", ["x"], True, True).label, matrix.FAIL)
        self.assertEqual(
            matrix.no_leak_verdict("success", [], True, True).label, matrix.HOLDS_FILTERED
        )
        self.assertEqual(
            matrix.no_leak_verdict("success", [], True, False).label, matrix.INCONCLUSIVE
        )
        self.assertEqual(matrix.no_leak_verdict("permission", [], True, False).label, matrix.HOLDS)

    def test_no_leak_verdict_with_nothing_scanned(self) -> None:
        """P06.1-C4, the I2b review's nit 4: a success with nothing left to scan is
        INCONCLUSIVE; a refusal keeps its own rule."""
        verdict = matrix.no_leak_verdict("success", [], True, True, nothing_scanned=True)
        self.assertEqual(
            (verdict.label, verdict.reason), (matrix.INCONCLUSIVE, matrix.NOTHING_SCANNED_REASON)
        )
        self.assertEqual(
            matrix.no_leak_verdict("permission", [], True, True, nothing_scanned=True).label,
            matrix.HOLDS,
        )
        self.assertEqual(
            matrix.no_leak_verdict("permission", [], False, True, nothing_scanned=True).label,
            matrix.INCONCLUSIVE,
        )

    def test_not_effective_verdict(self) -> None:
        self.assertEqual(matrix.not_effective_verdict(True, "success", True).label, matrix.FAIL)
        self.assertEqual(
            matrix.not_effective_verdict(False, "success", True).label, matrix.HOLDS_IGNORED
        )
        self.assertEqual(
            matrix.not_effective_verdict(False, "permission", True).label, matrix.HOLDS
        )
        self.assertEqual(
            matrix.not_effective_verdict(False, "success", False).label, matrix.INCONCLUSIVE
        )

    def test_find_terms(self) -> None:
        body = {"channels": [{"cid": "glow-match:p-ch-xd"}]}
        self.assertEqual(matrix.find_terms(body, ["p-ch-xd", "absent"]), ["p-ch-xd"])


if __name__ == "__main__":
    unittest.main()


class ProductStepValidationTest(unittest.TestCase):
    """P06.1-I2b: a product case's step must be one the runner's op would send."""

    def test_a_product_step_the_op_would_refuse_fails_validation(self) -> None:
        good = next(c for c in matrix.all_cases() if c.id == "VD-create")
        bad = matrix.Case(
            id="VD-bad",
            group="video",
            actor="A",
            token="A's valid token",
            action="ring B",
            expect="refused",
            control=good.control,
            step=matrix.SdkStep(
                session="A",
                op="product",
                params={
                    "method": "POST",
                    "path": "/api/v2/video/call/default/x",
                    "body": {"ring": True},
                },
            ),
            phase=91,
        )
        problems = matrix.validate([good, bad])
        self.assertEqual(
            problems, ["VD-bad: the product op would refuse its step: denied field (ring)"]
        )
        self.assertEqual(matrix.validate([good]), [])


class ProductReachValidationTest(unittest.TestCase):
    """P06.1-C4, the I2b review's finding 1: a step that could reach Video or Feeds through
    any op but ``product`` fails validation."""

    def case(self, op: str, params: dict[str, object]) -> matrix.Case:
        control = next(c for c in matrix.all_cases() if c.id == "VD-create").control
        return matrix.Case(
            id=f"X-{op}",
            group="content",
            actor="A",
            token="A's valid token",
            action="reach a product another way",
            expect="refused",
            control=control,
            step=matrix.SdkStep(session="A", op=op, params=params),  # type: ignore[arg-type]
            phase=40,
        )

    def test_a_call_of_a_client_url_method_fails_validation(self) -> None:
        for method in sorted(matrix.CLIENT_URL_METHODS):
            case = self.case(
                "call",
                {
                    "target": "client",
                    "method": method,
                    "args": ["https://chat.stream-io-api.com/api/v2/video/call/default/x/join"],
                },
            )
            self.assertEqual(
                matrix.validate([case]),
                [
                    f"X-call: a call of the client's {method}, which takes a URL, could reach "
                    "Video or Feeds; only the product op may reach them"
                ],
            )

    def test_a_get_of_a_product_path_fails_validation(self) -> None:
        for path in (
            "/api/v2/video/call/default/x",
            "/api/v2/FEEDS/activities",
            "/api/v2/chat/..%2Fvideo/calls",
            "/channels/../api/v2/feeds/feeds/query",
            "/api/v2/%76ideo",
        ):
            self.assertEqual(
                matrix.validate([self.case("get", {"path": path})]),
                ["X-get: a get of a Video or Feeds path; only the product op may reach them"],
                path,
            )

    def test_what_stays_valid(self) -> None:
        self.assertEqual(
            matrix.validate([self.case("get", {"path": "/channels/glow-match/x"})]), []
        )
        self.assertEqual(matrix.validate([self.case("get", {"path": "/api/v2/videos"})]), [])
        channel_call = self.case(
            "call", {"target": "channel", "method": "query", "args": [{}], "type": "glow-match"}
        )
        self.assertEqual(matrix.validate([channel_call]), [])
        client_call = self.case("call", {"target": "client", "method": "queryUsers", "args": [{}]})
        self.assertEqual(matrix.validate([client_call]), [])
        # And every case in the matrix: no step reaches a product but through the op.
        self.assertEqual(matrix.validate(matrix.all_cases()), [])
