"""Result recording and the printed table, offline, with synthetic results."""

import json
import unittest
from collections import Counter
from uuid import uuid4

from glow_ordering_proof import budget
from glow_ordering_proof.cases import CaseResult
from glow_ordering_proof.controls import ControlResult
from glow_ordering_proof.observe import ObservedWait
from glow_ordering_proof.oracle import OracleReport, Violation
from glow_ordering_proof.results import Report, render, table
from glow_ordering_proof.stress import RaceResult

FACTS = {
    "version": "PostgreSQL 17.11 (example)",
    "track_commit_timestamp": "on",
    "superuser": "false",
    "current_user": "glow_proof",
}


def wait(observed: bool = True) -> ObservedWait:
    return ObservedWait(
        4242,
        observed,
        "Lock" if observed else None,
        "transactionid" if observed else None,
        "transactionid" if observed else None,
        "ShareLock" if observed else None,
        7,
        12,
    )


def passing_report() -> Report:
    report = Report(
        20260929, FACTS, "read committed", [("auth", "0001_initial", "2026-09-29T00:00:00")]
    )
    report.cases = [CaseResult("block_by_low.send_holds", "DB06", "t", True, [wait()], ["ok"], [])]
    race = RaceResult(
        "race.block_by_low",
        "t",
        20260929,
        iterations=120,
        overlaps=115,
        elapsed_seconds=9.5,
        outcomes=Counter({"send=authorized": 60, "send=refused:match_not_active": 60}),
    )
    report.races = [race]
    report.controls = [
        ControlResult(
            "no_locks.forced",
            "D5",
            "forced",
            "block_by_high.send_holds",
            "broken:lock_accounts",
            True,
            "the second connection was not observed waiting",
            None,
            1,
        ),
        ControlResult(
            "no_locks.stress",
            "D5",
            "stress",
            "race.block_by_high",
            "broken:lock_accounts",
            True,
            "first failing iteration 3",
            3,
            1,
        ),
    ]
    report.oracle = OracleReport(
        200,
        300,
        [
            Violation(
                "O2", "control:no_locks.forced", "block_by_high.send_holds", None, uuid4(), "late"
            )
        ],
        {"design:forced": 100, "design:stress": 99, "control:no_locks.forced": 1},
    )
    return report


class ReportTests(unittest.TestCase):
    def test_passing_report(self) -> None:
        report = passing_report()
        ok, reasons = report.verdict()
        self.assertTrue(ok, reasons)
        text = render(report)
        self.assertIn("VERDICT: PASS", text)
        self.assertIn("pid 4242 wait_event_type=Lock", text)
        self.assertIn("failed as intended", text)
        data = json.loads(report.to_json())
        self.assertEqual(data["verdict"], "PASS")
        self.assertEqual(data["budget"]["min_overlaps"], budget.MIN_OVERLAPS)

    def test_failed_case_fails(self) -> None:
        report = passing_report()
        report.cases.append(CaseResult("x", "g", "t", False, [wait(False)], [], ["boom"]))
        ok, reasons = report.verdict()
        self.assertFalse(ok)
        self.assertTrue(any("cases failed: x" in r for r in reasons))
        self.assertIn("no wait observed", render(report))

    def test_floors_fail_the_run(self) -> None:
        report = passing_report()
        report.races[0].iterations = 49
        self.assertFalse(report.verdict()[0])
        report.races[0].iterations = 60
        report.races[0].overlaps = 9
        self.assertFalse(report.verdict()[0])
        self.assertIn("NOT MET", render(report))

    def test_a_control_that_never_fails_fails_the_run(self) -> None:
        report = passing_report()
        report.controls[1].failed_as_intended = False
        ok, reasons = report.verdict()
        self.assertFalse(ok)
        self.assertTrue(
            any(
                "did not fail as intended (declared signal absent): no_locks.stress" in r
                for r in reasons
            )
        )

    def test_design_violation_fails_and_control_violation_does_not(self) -> None:
        report = passing_report()
        self.assertTrue(report.verdict()[0])
        report.oracle.violations.append(
            Violation("O3", "design:stress", "race.x", 5, uuid4(), "late")
        )
        ok, reasons = report.verdict()
        self.assertFalse(ok)
        self.assertTrue(any("oracle violations in the design's rows: 1" in r for r in reasons))

    def test_untagged_rows_count_as_design_rows(self) -> None:
        report = passing_report()
        report.oracle.violations.append(
            Violation("O1", "untagged", None, None, uuid4(), "no log row")
        )
        self.assertFalse(report.verdict()[0])

    def test_missing_oracle_fails(self) -> None:
        report = passing_report()
        report.oracle = None
        self.assertFalse(report.verdict()[0])

    def test_render_has_no_connection_material(self) -> None:
        text = render(passing_report()).lower()
        for word in ("password", "passfile", "proof_db_", "postgres://", "postgresql://"):
            self.assertNotIn(word, text)

    def test_table(self) -> None:
        text = table(("a", "bb"), [("1", "22"), ("333", "4")])
        self.assertEqual(text.splitlines()[0], "a    bb")
        self.assertEqual(text.splitlines()[1], "---  --")


if __name__ == "__main__":
    unittest.main()
