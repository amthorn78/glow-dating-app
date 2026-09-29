"""The negative controls (item 6.3): a deliberately broken variant for each guarantee,
run in the same job and required to fail there.

A forced control runs one named case under a broken ``Design`` and must fail it
deterministically. A stress control runs one race under a broken design and must
produce at least one violation within the budget; its first failing iteration is
recorded. A control that never fails fails the job.

Each control declares the signal its broken switch must produce (P06.DB-C1, F3): the
case signals it must show (``cases.WAIT_NOT_OBSERVED`` and the others) and the oracle
rules one of whose violations must appear under its run tag. It counts as failed as
intended only when that signal is present. A harness error, a database error the
design does not expect, a stress harness failure, or any other failure without the
declared signal counts as a control that did not fail as intended, which fails the job.
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import Literal

from glow_ordering_proof import oracle, stress
from glow_ordering_proof.cases import (
    CASE_BY_ID,
    COMMIT_AFTER_REVOCATION,
    DATABASE_ERROR,
    DEADLOCK,
    HARNESS_ERROR,
    REFUSAL_MISSING,
    WAIT_NOT_OBSERVED,
    CaseResult,
    Context,
    run_case,
)
from glow_ordering_proof.concurrency import Worker
from glow_ordering_proof.design import Design
from glow_ordering_proof.observe import LogContext, ProofLog

# A failure of these kinds means the demonstration did not run cleanly; it never
# counts as a control's signal.
DISQUALIFYING = frozenset({HARNESS_ERROR, DATABASE_ERROR})


@dataclass(frozen=True)
class Signal:
    """What a control's broken switch must produce. Every case signal in ``case`` must
    be among the target case's signals, and, when ``oracle`` is not empty, at least one
    oracle violation under the control's run tag must have one of its rules."""

    case: frozenset[str] = frozenset()
    oracle: frozenset[str] = frozenset()

    def met(
        self,
        case_signals: Collection[str],
        oracle_rules: Collection[str],
        *,
        harness_failed: bool = False,
    ) -> bool:
        if not self.case and not self.oracle:
            return False
        if harness_failed or DISQUALIFYING & set(case_signals):
            return False
        if not self.case <= set(case_signals):
            return False
        return not self.oracle or bool(self.oracle & set(oracle_rules))

    def describe(self) -> str:
        parts = sorted(self.case)
        if self.oracle:
            parts.append("oracle " + "/".join(sorted(self.oracle)))
        return " + ".join(parts)


def _signal(*case: str, oracle: Collection[str] = ()) -> Signal:
    return Signal(frozenset(case), frozenset(oracle))


@dataclass(frozen=True)
class Control:
    id: str
    guarantee: str
    design: Design
    mode: Literal["forced", "stress"]
    target: str  # a case id or a race id
    expectation: str
    signal: Signal

    @property
    def run_tag(self) -> str:
        return f"control:{self.id}"


CONTROLS: tuple[Control, ...] = (
    Control(
        "no_locks.forced",
        "D5 row locks order a send against an unmatch",
        Design(lock_accounts=False, lock_match=False, lock_session=False),
        "forced",
        "unmatch_by_high.send_holds",
        "the unmatch never waits; the send commits after the revocation (O2/O6)",
        _signal(WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION, oracle={"O2", "O6"}),
    ),
    Control(
        "no_locks.stress",
        "D5 row locks, under randomized races",
        Design(lock_accounts=False, lock_match=False, lock_session=False),
        "stress",
        "race.block_by_high",
        "at least one send commits after the block within the budget",
        _signal(oracle={"O2", "O6"}),
    ),
    Control(
        "no_version_check",
        "DB06 stale contact version",
        Design(check_contact_version=False),
        "forced",
        "named.stale_contact_version",
        "a send with a stale contact version is authorized (the case's expected refusal;"
        " the oracle cannot see a stale client version)",
        _signal(REFUSAL_MISSING),
    ),
    Control(
        "no_session_lock",
        "5.1 sign-out joins the lock protocol",
        Design(lock_session=False),
        "forced",
        "sign_out_sender.send_holds",
        "the sign-out never waits; the send commits after it (O3)",
        _signal(WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION, oracle={"O3"}),
    ),
    Control(
        "transaction_start_time",
        "5.2 time is read after the locks",
        Design(time_source="transaction_start"),
        "forced",
        "named.session_expires_during_wait",
        "the send whose session expired while it waited is authorized (O5)",
        _signal(REFUSAL_MISSING, oracle={"O5"}),
    ),
    Control(
        "dedup_before_authorize",
        "5.4 authorize first, then deduplicate",
        Design(authorize_before_dedup=False),
        "forced",
        "named.retry_after_revocation",
        "a retry after the revocation gets the old receipt as if current",
        _signal(REFUSAL_MISSING),
    ),
    Control(
        "inverted_lock_order",
        "5.3 one canonical lock order for every writer",
        Design(canonical_order=False),
        "forced",
        "named.opposing_first_lock_block_high_vs_send",
        "a block by the higher account locking its own account first deadlocks against a send",
        _signal(DEADLOCK),
    ),
    Control(
        "no_account_lock.forced",
        "5.3 account-wide revocations are ordered by the account locks",
        Design(lock_accounts=False),
        "forced",
        "suspend_high.send_holds",
        "the suspension never waits; the send commits after it (O4)",
        _signal(WAIT_NOT_OBSERVED, COMMIT_AFTER_REVOCATION, oracle={"O4"}),
    ),
    Control(
        "no_account_lock.stress",
        "5.3 account locks, under randomized races",
        Design(lock_accounts=False),
        "stress",
        "race.suspend_high",
        "at least one send commits after the suspension within the budget",
        _signal(oracle={"O4"}),
    ),
    Control(
        "filter_state_in_lock",
        "5.5 an empty locked read is a refusal",
        Design(filter_state_in_lock=True),
        "forced",
        "unmatch_by_high.revocation_holds",
        "the locked read filtered on state returns nothing after the unmatch, and the send"
        " proceeds (O2/O6)",
        _signal(REFUSAL_MISSING, oracle={"O2", "O6"}),
    ),
)
CONTROL_BY_ID = {control.id: control for control in CONTROLS}


@dataclass
class ControlResult:
    control_id: str
    guarantee: str
    mode: str
    target: str
    variant: str
    failed_as_intended: bool
    signal: str
    first_failing_iteration: int | None = None
    oracle_violations: int = 0
    case: CaseResult | None = None
    race: stress.RaceResult | None = None
    declared: str = ""  # the signal the control declares; failed_as_intended says if met

    def to_dict(self) -> dict[str, object]:
        return {
            "control_id": self.control_id,
            "guarantee": self.guarantee,
            "mode": self.mode,
            "target": self.target,
            "variant": self.variant,
            "declared_signal": self.declared,
            "failed_as_intended": self.failed_as_intended,
            "signal": self.signal,
            "first_failing_iteration": self.first_failing_iteration,
            "oracle_violations": self.oracle_violations,
            "case": self.case.to_dict() if self.case else None,
            "race": self.race.to_dict() if self.race else None,
        }


def judge_forced(
    control: Control, case_result: CaseResult, violations: list[oracle.Violation]
) -> tuple[bool, str]:
    """Whether a forced control failed as intended, by its declared signal only, and
    what the run showed."""
    rules = sorted({v.rule for v in violations})
    met = control.signal.met(case_result.signals, rules)
    signal = "; ".join(case_result.failures) or "the case passed under the broken design"
    # The oracle's part first, so the printed table's truncation never hides it.
    signal = f"oracle: {len(violations)} violation(s) ({', '.join(rules) or '-'}) | {signal}"
    if not case_result.passed and not met:
        signal = (
            f"not the declared signal (case signals {sorted(case_result.signals)},"
            f" oracle rules {rules}): {signal}"
        )
    return met, signal


def judge_stress(control: Control, race_result: stress.RaceResult) -> tuple[bool, str]:
    """Whether a stress control failed as intended: an oracle violation of a declared
    rule at its first failing iteration, with no harness failure."""
    rules = sorted({v.rule for v in race_result.violations})
    met = control.signal.met((), rules, harness_failed=bool(race_result.harness_failures))
    if race_result.violations or race_result.harness_failures:
        signal = (
            f"first failing iteration {race_result.first_failing_iteration}"
            f" (oracle rules {', '.join(rules) or 'none'}): "
            + "; ".join([v.detail for v in race_result.violations] + race_result.harness_failures)[
                :300
            ]
        )
        if not met:
            signal = "not the declared signal: " + signal
    else:
        signal = (
            f"no violation in {race_result.iterations} iterations"
            f" ({race_result.overlaps} overlaps, {race_result.elapsed_seconds:.1f} s)"
        )
    return met, signal


def run_control(
    control: Control, *, log: ProofLog, workers: list[Worker], seed: int
) -> ControlResult:
    from glow_ordering_proof.fixtures import DjangoFixtures
    from glow_ordering_proof.reference import ReferenceSubject

    log.context = LogContext(run_tag=control.run_tag, variant=control.design.describe())
    ctx = Context(ReferenceSubject(log, control.design), DjangoFixtures(), log, workers)
    if control.mode == "forced":
        case_result = run_case(ctx, CASE_BY_ID[control.target])
        report = oracle.evaluate(run_tag=control.run_tag)
        failed, signal = judge_forced(control, case_result, report.violations)
        return ControlResult(
            control.id,
            control.guarantee,
            control.mode,
            control.target,
            control.design.describe(),
            failed,
            signal,
            None,
            len(report.violations),
            case=case_result,
            declared=control.signal.describe(),
        )
    race_result = stress.run_race(
        ctx,
        stress.RACE_BY_ID[control.target],
        seed=seed,
        run_tag=control.run_tag,
        stop_at_first_violation=True,
    )
    failed, signal = judge_stress(control, race_result)
    return ControlResult(
        control.id,
        control.guarantee,
        control.mode,
        control.target,
        control.design.describe(),
        failed,
        signal,
        race_result.first_failing_iteration,
        len(race_result.violations),
        race=race_result,
        declared=control.signal.describe(),
    )


def plan() -> list[dict[str, str]]:
    return [
        {
            "id": c.id,
            "guarantee": c.guarantee,
            "mode": c.mode,
            "target": c.target,
            "variant": c.design.describe(),
            "signal": c.signal.describe(),
        }
        for c in CONTROLS
    ]
