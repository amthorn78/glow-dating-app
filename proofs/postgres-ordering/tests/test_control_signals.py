"""The negative controls' declared signals, offline (P06.DB-C1, the exact-head review's
F3): a control fails as intended only by its own signal."""

import unittest
from collections import Counter
from uuid import uuid4

from glow_ordering_proof import cases, controls, stress
from glow_ordering_proof.cases import (
    CASE_SIGNALS,
    COMMIT_AFTER_REVOCATION,
    DATABASE_ERROR,
    DEADLOCK,
    HARNESS_ERROR,
    OTHER,
    REFUSAL_MISSING,
    WAIT_NOT_OBSERVED,
    CaseResult,
)
from glow_ordering_proof.design import REFERENCE
from glow_ordering_proof.interface import Result
from glow_ordering_proof.oracle import Violation

# What each broken switch can make the suite show, derived from the reference design:
# the case signals and the oracle rules. A declared signal outside this is one the
# broken switch cannot produce. The oracle cannot see a stale client version (the
# send stores the locked match's version), so the version check has no oracle rule.
PRODUCIBLE: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    # Without the send's locks a revocation does not wait, and the send can commit
    # after it: contact (O2, O6), session (O3) or account (O4, O7) revocations.
    "lock_accounts": (
        frozenset({WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION, REFUSAL_MISSING}),
        frozenset({"O2", "O4", "O6", "O7"}),
    ),
    "lock_match": (
        frozenset({WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION, REFUSAL_MISSING}),
        frozenset({"O2", "O6"}),
    ),
    "lock_session": (
        frozenset({WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION, REFUSAL_MISSING}),
        frozenset({"O3", "O5"}),
    ),
    "check_contact_version": (frozenset({REFUSAL_MISSING}), frozenset()),
    "time_source": (frozenset({REFUSAL_MISSING}), frozenset({"O5"})),
    "authorize_before_dedup": (frozenset({REFUSAL_MISSING}), frozenset()),
    "filter_state_in_lock": (frozenset({REFUSAL_MISSING}), frozenset({"O2", "O3", "O4", "O6"})),
    "canonical_order": (frozenset({DEADLOCK}), frozenset()),
}


def flipped(control: controls.Control) -> list[str]:
    return [
        name for name in PRODUCIBLE if getattr(control.design, name) != getattr(REFERENCE, name)
    ]


def case_result(passed: bool, signals: set[str], failures: list[str] | None = None) -> CaseResult:
    return CaseResult(
        "t", "g", "t", passed, [], [], failures or ["a failure"] * (not passed), frozenset(signals)
    )


def violation(rule: str, tag: str = "control:x") -> Violation:
    return Violation(rule, tag, "c", 1, uuid4(), "late")


def race_result(violations: list[Violation], harness: list[str]) -> stress.RaceResult:
    return stress.RaceResult(
        "race.block_by_high",
        "t",
        1,
        iterations=1,
        overlaps=1,
        outcomes=Counter(),
        harness_failures=harness,
        violations=violations,
        first_failing_iteration=1,
    )


class DeclaredSignalTests(unittest.TestCase):
    def test_each_control_declares_a_signal_its_switch_can_produce(self) -> None:
        for control in controls.CONTROLS:
            with self.subTest(control=control.id):
                names = flipped(control)
                self.assertTrue(names)
                case_ok = frozenset().union(*(PRODUCIBLE[n][0] for n in names))
                oracle_ok = frozenset().union(*(PRODUCIBLE[n][1] for n in names))
                signal = control.signal
                self.assertTrue(signal.case or signal.oracle, "no declared signal")
                self.assertLessEqual(signal.case, case_ok)
                self.assertLessEqual(signal.oracle, oracle_ok)
                self.assertLessEqual(signal.case, CASE_SIGNALS - {HARNESS_ERROR, OTHER})

    def test_signals_fit_the_target(self) -> None:
        for control in controls.CONTROLS:
            with self.subTest(control=control.id):
                if control.mode == "stress":
                    # A race has no case judge: its signal is an oracle violation.
                    self.assertEqual(control.signal.case, frozenset())
                    self.assertTrue(control.signal.oracle)
                else:
                    # A forced control must fail its case, with the case's own signal.
                    self.assertTrue(control.signal.case)
                if COMMIT_AFTER_REVOCATION in control.signal.case:
                    # Only the send_holds interleaving compares the commit timestamps.
                    self.assertTrue(control.target.endswith(".send_holds"))
                if WAIT_NOT_OBSERVED in control.signal.case:
                    self.assertTrue(control.target.endswith((".send_holds", ".revocation_holds")))

    def test_no_version_check_declares_no_oracle_rule(self) -> None:
        # The manager's observation 3: the oracle cannot see a stale client version.
        self.assertEqual(controls.CONTROL_BY_ID["no_version_check"].signal.oracle, frozenset())


class ForcedJudgementTests(unittest.TestCase):
    no_locks = controls.CONTROL_BY_ID["no_locks.forced"]
    deadlock = controls.CONTROL_BY_ID["inverted_lock_order"]
    refusal = controls.CONTROL_BY_ID["dedup_before_authorize"]

    def test_the_declared_signal_counts(self) -> None:
        result = case_result(False, {WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION, OTHER})
        met, _ = controls.judge_forced(self.no_locks, result, [violation("O2"), violation("O6")])
        self.assertTrue(met)
        met, _ = controls.judge_forced(self.deadlock, case_result(False, {DEADLOCK}), [])
        self.assertTrue(met)

    def test_a_case_failing_for_another_reason_is_not_counted(self) -> None:
        for signals in ({HARNESS_ERROR}, {OTHER}, {DATABASE_ERROR}, {REFUSAL_MISSING}):
            with self.subTest(signals=signals):
                met, text = controls.judge_forced(self.deadlock, case_result(False, signals), [])
                self.assertFalse(met)
                self.assertIn("not the declared signal", text)

    def test_a_harness_error_disqualifies_even_beside_the_signal(self) -> None:
        met, _ = controls.judge_forced(
            self.refusal, case_result(False, {REFUSAL_MISSING, HARNESS_ERROR}), []
        )
        self.assertFalse(met)

    def test_every_part_of_the_signal_is_required(self) -> None:
        # The case's part without the oracle's, and the oracle's without the case's.
        both = case_result(False, {WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION})
        self.assertFalse(controls.judge_forced(self.no_locks, both, [])[0])
        self.assertFalse(controls.judge_forced(self.no_locks, both, [violation("O3")])[0])
        wait_only = case_result(False, {WAIT_NOT_OBSERVED})
        self.assertFalse(controls.judge_forced(self.no_locks, wait_only, [violation("O2")])[0])

    def test_a_passing_case_is_not_counted(self) -> None:
        met, text = controls.judge_forced(self.deadlock, case_result(True, set()), [])
        self.assertFalse(met)
        self.assertIn("the case passed", text)


class StressJudgementTests(unittest.TestCase):
    control = controls.CONTROL_BY_ID["no_locks.stress"]

    def test_an_oracle_violation_of_a_declared_rule_counts(self) -> None:
        self.assertTrue(controls.judge_stress(self.control, race_result([violation("O2")], []))[0])

    def test_a_harness_failure_is_not_counted(self) -> None:
        met, text = controls.judge_stress(
            self.control, race_result([], ["iteration 1: send: error:OperationalError"])
        )
        self.assertFalse(met)
        self.assertIn("not the declared signal", text)
        met, _ = controls.judge_stress(
            self.control, race_result([violation("O2")], ["iteration 1: block: deadlock"])
        )
        self.assertFalse(met)

    def test_another_rule_is_not_counted(self) -> None:
        self.assertFalse(controls.judge_stress(self.control, race_result([violation("O3")], []))[0])

    def test_no_violation_is_not_counted(self) -> None:
        met, text = controls.judge_stress(self.control, race_result([], []))
        self.assertFalse(met)
        self.assertIn("no violation", text)


class CaseSignalTests(unittest.TestCase):
    def test_outcome_signals(self) -> None:
        self.assertEqual(cases.outcome_signal(Result("authorized"), ("refused",)), REFUSAL_MISSING)
        self.assertEqual(cases.outcome_signal(Result("replayed"), ("refused",)), REFUSAL_MISSING)
        self.assertEqual(cases.outcome_signal(Result("deadlock"), ("refused",)), DEADLOCK)
        self.assertEqual(cases.outcome_signal(Result("error"), ("applied",)), DATABASE_ERROR)
        self.assertEqual(cases.outcome_signal(Result("refused"), ("authorized",)), OTHER)

    def test_a_harness_error_is_its_own_signal(self) -> None:
        def boom(ctx: cases.Context, judge: cases.Judge) -> None:
            raise RuntimeError("boom")

        class Log:
            class context:  # noqa: N801 - a stand-in for LogContext
                case_id: str | None = None

        ctx = cases.Context(None, None, Log(), [])  # type: ignore[arg-type]
        result = cases.run_case(ctx, cases.Case("x", "g", "t", boom))
        self.assertFalse(result.passed)
        self.assertEqual(result.signals, frozenset({HARNESS_ERROR}))


if __name__ == "__main__":
    unittest.main()
