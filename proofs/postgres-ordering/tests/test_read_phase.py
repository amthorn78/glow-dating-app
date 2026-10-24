"""The read phase, offline (P06.2 Stage C1; no database): its plan, its planted controls'
declared signals, and the run's verdict with it.

The read phase's cases run against PostgreSQL in the database job; here the plan is
pinned (each revocation's three forced cases and the named cases DM-22 asks for), the
controls must target the forced case "committed while the read waits" and declare a
missing refusal (3.3), and a run without the read phase, or with a failing read case or a
control that did not fail, does not pass.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[3] / "services" / "api"
if str(API_ROOT) not in sys.path:
    # The read phase's domain types are Django-free (``glow_domain``); its adapter
    # (``glow_chat``) is imported only when a case runs.
    sys.path.insert(0, str(API_ROOT))

from glow_ordering_proof import cases, read_phase  # noqa: E402
from glow_ordering_proof.cases import REFUSAL_MISSING, CaseResult  # noqa: E402
from glow_ordering_proof.controls import ControlResult  # noqa: E402
from glow_ordering_proof.interface import Result  # noqa: E402
from glow_ordering_proof.results import ReadReport  # noqa: E402


def passing_reads() -> ReadReport:
    report = ReadReport()
    report.cases.append(CaseResult("read.x", "g", "t", True))
    report.controls.append(
        ControlResult("read.final_check_skipped", "g", "planted", "t", "v", True, "signal")
    )
    return report


class ReadPlanTests(unittest.TestCase):
    def test_each_revocation_has_its_three_forced_read_cases(self) -> None:
        ids = {c["id"] for c in read_phase.plan()}
        revocations = {r.id for r in (*cases.REVOCATIONS, *cases.D5_REVOCATIONS)}
        # The nine kinds C1 names: block, unmatch, suspension, deletion, sign-out, session
        # expiry, pause, restriction and consent withdrawal, each with either member.
        self.assertEqual(
            {cases.REVOCATION_BY_ID[r].kind for r in revocations},
            {
                "block",
                "unmatch",
                "suspend",
                "delete",
                "sign_out",
                "expire",
                "pause",
                "restrict",
                "withdraw",
            },
        )
        self.assertEqual(len(revocations), 16)
        for rev in revocations:
            for name in ("read_waits", "check_holds", "revocation_holds"):
                self.assertIn(f"read.{rev}.{name}", ids)

    def test_the_named_cases_cover_dm_22(self) -> None:
        ids = {c["id"] for c in read_phase.plan()}
        for name in (
            "read.block_during_provider_call",  # 3.2
            "read.order_follows_acceptance",  # 2.2
            "read.pages_and_cursors",
            "read.only_text_glow_sent",  # 2.1
            "read.provider_error_fails_the_read",  # 2.4
            "read.cursor_bound_to_match",  # 6.4
            "read.reads_write_nothing",  # 2.3
            "read.no_text_in_logs",  # 2.5
            "read.unread_and_read_cursor",  # point e, 6.3
            "read.conversation_list",  # item 4, 6.1
        ):
            self.assertIn(name, ids)

    def test_plan_count_and_uniqueness(self) -> None:
        plan = read_phase.plan()
        self.assertEqual(len(plan), 16 * 3 + 10)
        self.assertEqual(len({c["id"] for c in plan}), len(plan))
        self.assertTrue(all(c["guarantee"] and c["title"] for c in plan))
        # The reads are not the suite's: the reference design's 56 cases are unchanged.
        self.assertEqual(len(cases.plan()), 56)
        self.assertFalse({c["id"] for c in plan} & {c["id"] for c in cases.plan(d5=True)})


class ReadControlTests(unittest.TestCase):
    def test_the_controls_target_the_forced_case_and_declare_a_missing_refusal(self) -> None:
        ids = {c["id"] for c in read_phase.plan()}
        self.assertIn(read_phase.CONTROL_TARGET, ids)
        self.assertEqual(read_phase.CONTROL_TARGET, "read.block_by_high.read_waits")
        self.assertEqual(
            {c.id for c in read_phase.READ_CONTROLS},
            {"read.final_check_skipped", "read.final_check_before_call"},
        )
        for control in read_phase.READ_CONTROLS:
            with self.subTest(control=control.id):
                self.assertEqual(control.signal.case, frozenset({REFUSAL_MISSING}))
                self.assertTrue(control.signal.met({REFUSAL_MISSING}, ()))
                self.assertFalse(control.signal.met({cases.OTHER}, ()))
                self.assertFalse(control.signal.met({REFUSAL_MISSING, cases.HARNESS_ERROR}, ()))

    def test_a_page_where_a_refusal_was_expected_is_a_missing_refusal(self) -> None:
        for outcome in ("read", "listed", "moved"):
            self.assertEqual(cases.outcome_signal(Result(outcome), ("refused",)), REFUSAL_MISSING)


class ReadReportTests(unittest.TestCase):
    def test_the_report_passes_only_with_cases_and_failing_controls(self) -> None:
        self.assertTrue(passing_reads().ok)
        self.assertFalse(ReadReport().ok)
        failing_case = passing_reads()
        failing_case.cases.append(CaseResult("read.y", "g", "t", False))
        self.assertFalse(failing_case.ok)
        self.assertIn("read cases failed: read.y", failing_case.reasons())
        quiet_control = passing_reads()
        quiet_control.controls.append(
            ControlResult("read.final_check_before_call", "g", "planted", "t", "v", False, "s")
        )
        self.assertFalse(quiet_control.ok)
        no_controls = passing_reads()
        no_controls.controls.clear()
        self.assertFalse(no_controls.ok)


if __name__ == "__main__":
    unittest.main()
