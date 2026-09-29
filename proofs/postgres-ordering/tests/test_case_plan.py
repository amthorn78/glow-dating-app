"""The case plan and the controls, offline: what the job will run, pinned."""

import unittest

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
        plan = cases.plan()
        self.assertEqual(len(plan), 10 * 4 + 15)
        self.assertEqual(len({c["id"] for c in plan}), len(plan))
        self.assertTrue(all(c["guarantee"] and c["title"] for c in plan))

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
