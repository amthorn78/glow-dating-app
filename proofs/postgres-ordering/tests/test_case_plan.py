"""The case plan and the controls, offline: what the job will run, pinned."""

import unittest
from datetime import timedelta

from glow_ordering_proof import cases, controls, stress
from glow_ordering_proof.design import REFERENCE, Design


class CasePlanTests(unittest.TestCase):
    def test_every_revocation_has_its_four_interleavings(self) -> None:
        ids = {c["id"] for c in cases.plan()}
        expected = {
            "block_by_low",
            "block_by_high",
            "unmatch_by_low",
            "unmatch_by_high",
            "suspend_low",
            "suspend_high",
            "delete_low",
            "delete_high",
            "sign_out_sender",
            "expire_sender",
        }
        self.assertEqual({r.id for r in cases.REVOCATIONS}, expected)
        for rev in expected:
            for interleaving in (
                "sequential_send_first",
                "sequential_revocation_first",
                "send_holds",
                "revocation_holds",
            ):
                self.assertIn(f"{rev}.{interleaving}", ids)

    def test_named_cases_cover_the_brief(self) -> None:
        ids = {c["id"] for c in cases.plan()}
        for name in (
            "named.positive_send",
            "named.stale_contact_version",
            "named.retry_identical",
            "named.retry_different_request",
            "named.retry_after_revocation",
            "named.racing_duplicates",
            "named.unblock_no_resurrect",
            "named.session_expires_during_wait",
            "named.opposing_first_lock_block_high_vs_send",
            "named.opposing_first_lock_suspend_high_vs_block_low",
            "named.opposing_blocks_both_sides",
            "named.opposing_four_writers",
            "named.sign_in_revocations",
            "named.deletion_keeps_authorization",
            "named.unmatch_repeat_is_safe",
        ):
            self.assertIn(name, ids)

    def test_plan_count_and_uniqueness(self) -> None:
        # P06.DB's 55 cases and CX2's boundary (P06.2, item 4), for both subjects.
        plan = cases.plan()
        self.assertEqual(len(plan), 10 * 4 + 15 + 1)
        self.assertEqual(len({c["id"] for c in plan}), len(plan))
        self.assertTrue(all(c["guarantee"] and c["title"] for c in plan))
        self.assertIn("named.session_expires_after_check", {c["id"] for c in plan})

    def test_the_adapter_plan_adds_d5(self) -> None:
        # P06.2 D5 (DM-13 4.1): each writer's four interleavings, both ways, for the
        # sender's and the other member's account, and the positive case; the adapter
        # only, since the reference design excludes D5. B1 adds its own cases (below).
        reference = {c["id"] for c in cases.plan()}
        adapter = {c["id"] for c in cases.plan(d5=True)}
        self.assertTrue(reference < adapter)
        added = adapter - reference
        self.assertEqual(len(added), 6 * 4 + 1 + len(cases.B1_CASES))
        for writer in ("pause", "restrict", "withdraw"):
            for which in ("low", "high"):
                for interleaving in (
                    "sequential_send_first",
                    "sequential_revocation_first",
                    "send_holds",
                    "revocation_holds",
                ):
                    self.assertIn(f"{writer}_{which}.{interleaving}", added)
        self.assertIn("named.d5_restored", added)

    def test_the_adapter_plan_adds_b1(self) -> None:
        # P06.2 B1: activation against each D5 writer both ways (DM-15 6.1), the token
        # grant against the bump and a sign-out (F1), and the F2 and F5 nits; the
        # adapter only. The reference design's 56 cases are unchanged (6.3).
        self.assertEqual(len(cases.plan()), 56)
        self.assertEqual(len(cases.plan(d5=True)), 56 + 25 + 34)
        ids = {c["id"] for c in cases.plan(d5=True)}
        self.assertFalse({c.id for c in cases.B1_CASES} & {c["id"] for c in cases.plan()})
        self.assertEqual(len(cases.B1_ACTIVATION_CASES), 6 * 4)
        for writer in ("pause", "restrict", "withdraw"):
            for which in ("low", "high"):
                for interleaving in (
                    "sequential_writer_first",
                    "sequential_activation_first",
                    "activation_holds",
                    "writer_holds",
                ):
                    self.assertIn(f"activation.{writer}_{which}.{interleaving}", ids)
        for name in (
            "token.pending_identity_refused",
            "token.sequential_grant_first",
            "token.sequential_grant_first_long_skew",
            "token.sequential_bump_first",
            "token.grant_holds",
            "token.bump_holds",
            "token.sign_out_holds",
            "named.f2_session_account_changed_under_wait",
            "named.f2_match_pair_changed_under_wait",
            "named.f5_self_block_refused",
        ):
            self.assertIn(name, ids)
        self.assertEqual(len(ids), len(cases.plan(d5=True)))

    def test_the_token_cases_skew_is_shorter_than_their_sessions(self) -> None:
        # B1-C1 R5: under the token cases' skew a grant timed by the app clock still
        # passes the session's expiry check, so it fails on its issue time against the
        # bump's cut-off; the long-skew case's hour is longer than the session, so a check
        # of the expiry against the app clock refuses there instead.
        session = timedelta(seconds=cases.SESSION_TTL)
        self.assertLess(cases.APP_CLOCK_SKEW, session / 2)
        self.assertGreater(cases.APP_CLOCK_SKEW, timedelta(seconds=30))
        self.assertGreater(cases.APP_CLOCK_SKEW_LONG, session)

    def test_restriction_shares_the_pause_writer(self) -> None:
        # DM-15 6.1: the pause and the restriction are one writer in the adapter
        # (``_set_profile``, read from its source: the adapter is not importable without
        # Django's settings), and activation checks one profile state for both; the
        # restriction still gets its own activation cases above.
        import ast
        from pathlib import Path

        source = (
            Path(__file__).resolve().parents[3] / "services" / "api" / "glow_chat" / "contact.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        adapter = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "OrmContactPersistence"
        )
        methods = {node.name: node for node in adapter.body if isinstance(node, ast.FunctionDef)}
        for name in ("pause_profile", "restrict_profile", "resume_profile"):
            calls = {
                node.func.attr
                for node in ast.walk(methods[name])
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            self.assertEqual(calls, {"_set_profile"}, name)
        self.assertIn("_set_profile", methods)
        self.assertIn("_contact_state_checks", methods)
        for name in ("activate_match", "send"):
            calls = {
                node.func.attr
                for node in ast.walk(methods[name])
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            self.assertIn("_contact_state_checks", calls, name)

    def test_races(self) -> None:
        ids = {r.id for r in stress.RACES}
        self.assertEqual(len(ids), 12)
        for rev in cases.REVOCATIONS:
            self.assertIn(f"race.{rev.id}", ids)
        self.assertIn("race.racing_duplicates", ids)
        self.assertIn("race.opposing_writers", ids)


class ControlPlanTests(unittest.TestCase):
    def test_each_control_breaks_exactly_one_switch_group(self) -> None:
        for control in controls.CONTROLS:
            with self.subTest(control=control.id):
                self.assertNotEqual(control.design, REFERENCE)
                self.assertTrue(control.design.describe().startswith("broken:"))

    def test_each_control_targets_a_case_or_race(self) -> None:
        for control in controls.CONTROLS:
            with self.subTest(control=control.id):
                if control.mode == "forced":
                    self.assertIn(control.target, cases.CASE_BY_ID)
                else:
                    self.assertIn(control.target, stress.RACE_BY_ID)
                self.assertTrue(control.run_tag.startswith("control:"))

    def test_the_guarantees_have_controls(self) -> None:
        designs = [c.design for c in controls.CONTROLS]
        self.assertIn(Design(lock_accounts=False, lock_match=False, lock_session=False), designs)
        self.assertIn(Design(check_contact_version=False), designs)
        self.assertIn(Design(lock_session=False), designs)
        self.assertIn(Design(time_source="transaction_start"), designs)
        self.assertIn(Design(authorize_before_dedup=False), designs)
        self.assertIn(Design(canonical_order=False), designs)
        self.assertIn(Design(lock_accounts=False), designs)
        self.assertIn(Design(filter_state_in_lock=True), designs)
        self.assertEqual(sum(c.mode == "stress" for c in controls.CONTROLS), 2)

    def test_reference_describes_itself(self) -> None:
        self.assertEqual(REFERENCE.describe(), "reference")
        self.assertEqual(Design(lock_session=False).describe(), "broken:lock_session")


if __name__ == "__main__":
    unittest.main()
