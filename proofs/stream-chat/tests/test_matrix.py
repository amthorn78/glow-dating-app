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
        # C13 deletes AB, so it is the last case that uses it. P06.1-I2a's families come
        # after it: each runs on users and a channel of its own.
        on_ab = [c.id for c in self.cases if c.phase < proof_run.FAMILY_PHASE]
        self.assertEqual(on_ab[-1], "C13")
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
