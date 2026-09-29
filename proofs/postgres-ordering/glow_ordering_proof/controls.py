"""The negative controls (item 6.3): a deliberately broken variant for each guarantee,
run in the same job and required to fail there.

A forced control runs one named case under a broken ``Design`` and must fail it
deterministically. A stress control runs one race under a broken design and must
produce at least one violation within the budget; its first failing iteration is
recorded. A control that never fails fails the job.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from glow_ordering_proof import oracle, stress
from glow_ordering_proof.cases import CASE_BY_ID, CaseResult, Context, run_case
from glow_ordering_proof.concurrency import Worker
from glow_ordering_proof.design import Design
from glow_ordering_proof.observe import LogContext, ProofLog


@dataclass(frozen=True)
class Control:
    id: str
    guarantee: str
    design: Design
    mode: Literal["forced", "stress"]
    target: str  # a case id or a race id
    expectation: str

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
    ),
    Control(
        "no_locks.stress",
        "D5 row locks, under randomized races",
        Design(lock_accounts=False, lock_match=False, lock_session=False),
        "stress",
        "race.block_by_high",
        "at least one send commits after the block within the budget",
    ),
    Control(
        "no_version_check",
        "DB06 stale contact version",
        Design(check_contact_version=False),
        "forced",
        "named.stale_contact_version",
        "a send with a stale contact version is authorized (O6)",
    ),
    Control(
        "no_session_lock",
        "5.1 sign-out joins the lock protocol",
        Design(lock_session=False),
        "forced",
        "sign_out_sender.send_holds",
        "the sign-out never waits; the send commits after it (O3)",
    ),
    Control(
        "transaction_start_time",
        "5.2 time is read after the locks",
        Design(time_source="transaction_start"),
        "forced",
        "named.session_expires_during_wait",
        "the send whose session expired while it waited is authorized (O5)",
    ),
    Control(
        "dedup_before_authorize",
        "5.4 authorize first, then deduplicate",
        Design(authorize_before_dedup=False),
        "forced",
        "named.retry_after_revocation",
        "a retry after the revocation gets the old receipt as if current",
    ),
    Control(
        "inverted_lock_order",
        "5.3 one canonical lock order for every writer",
        Design(canonical_order=False),
        "forced",
        "named.opposing_first_lock_block_high_vs_send",
        "a block by the higher account locking its own account first deadlocks against a send",
    ),
    Control(
        "no_account_lock.forced",
        "5.3 account-wide revocations are ordered by the account locks",
        Design(lock_accounts=False),
        "forced",
        "suspend_high.send_holds",
        "the suspension never waits; the send commits after it (O4)",
    ),
    Control(
        "no_account_lock.stress",
        "5.3 account locks, under randomized races",
        Design(lock_accounts=False),
        "stress",
        "race.suspend_high",
        "at least one send commits after the suspension within the budget",
    ),
    Control(
        "filter_state_in_lock",
        "5.5 an empty locked read is a refusal",
        Design(filter_state_in_lock=True),
        "forced",
        "unmatch_by_high.revocation_holds",
        "the locked read filtered on state returns nothing after the unmatch, and the send"
        " proceeds (O2/O6)",
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

    def to_dict(self) -> dict[str, object]:
        return {
            "control_id": self.control_id,
            "guarantee": self.guarantee,
            "mode": self.mode,
            "target": self.target,
            "variant": self.variant,
            "failed_as_intended": self.failed_as_intended,
            "signal": self.signal,
            "first_failing_iteration": self.first_failing_iteration,
            "oracle_violations": self.oracle_violations,
            "case": self.case.to_dict() if self.case else None,
            "race": self.race.to_dict() if self.race else None,
        }


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
        failed = not case_result.passed
        signal = "; ".join(case_result.failures) or "the case passed under the broken design"
        if report.violations:
            signal += f" | oracle: {len(report.violations)} violation(s)"
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
        )
    race_result = stress.run_race(
        ctx,
        stress.RACE_BY_ID[control.target],
        seed=seed,
        run_tag=control.run_tag,
        stop_at_first_violation=True,
    )
    failed = bool(race_result.violations or race_result.harness_failures)
    if failed:
        signal = (
            f"first failing iteration {race_result.first_failing_iteration}: "
            + "; ".join([v.detail for v in race_result.violations] + race_result.harness_failures)[
                :300
            ]
        )
    else:
        signal = (
            f"no violation in {race_result.iterations} iterations"
            f" ({race_result.overlaps} overlaps, {race_result.elapsed_seconds:.1f} s)"
        )
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
    )


def plan() -> list[dict[str, str]]:
    return [
        {
            "id": c.id,
            "guarantee": c.guarantee,
            "mode": c.mode,
            "target": c.target,
            "variant": c.design.describe(),
        }
        for c in CONTROLS
    ]
