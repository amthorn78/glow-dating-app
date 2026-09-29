"""The stress run (item 6.3): a seeded, randomized repeat of each race within a fixed
budget, with a measured overlap count.

An overlap is measured from the database: each writer's transaction interval is
[``now()`` inside its transaction, its commit timestamp] when it committed, or
[``now()``, ``clock_timestamp()`` read just before its rollback] when it was refused
(recorded afterwards as an attempt row). An iteration overlapped when the send's
interval and a revocation's interval intersect. A race whose iterations never
overlapped proves nothing, so the floors in ``budget`` apply.
"""

from __future__ import annotations

import random
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from django.db import connection

from glow_ordering_proof import budget, oracle
from glow_ordering_proof.cases import (
    REVOCATION_BY_ID,
    Context,
    Revocation,
    World,
    make_world,
    send_request,
)
from glow_ordering_proof.concurrency import Barrier
from glow_ordering_proof.dbreads import submissions_of
from glow_ordering_proof.interface import Result
from glow_ordering_proof.observe import LOG_TABLE


@dataclass(frozen=True)
class Race:
    id: str
    title: str
    guarantee: str
    kind: str  # "revocation", "duplicates" or "opposing"
    revocation: Revocation | None = None


RACES: tuple[Race, ...] = (
    *(
        Race(
            f"race.{rev.id}", f"a send against {rev.title}", "DB06/DB09 ordering", "revocation", rev
        )
        for rev in REVOCATION_BY_ID.values()
    ),
    Race("race.racing_duplicates", "two identical sends", "5.4 racing duplicates", "duplicates"),
    Race(
        "race.opposing_writers",
        "a send, a block by each side and a suspension",
        "5.3 no deadlock",
        "opposing",
    ),
)
RACE_BY_ID = {race.id: race for race in RACES}


@dataclass
class RaceResult:
    race_id: str
    title: str
    seed: int
    iterations: int = 0
    overlaps: int = 0
    elapsed_seconds: float = 0.0
    outcomes: Counter[str] = field(default_factory=Counter)
    harness_failures: list[str] = field(default_factory=list)
    violations: list[oracle.Violation] = field(default_factory=list)
    first_failing_iteration: int | None = None
    stopped_early: bool = False

    @property
    def floors_met(self) -> bool:
        return budget.floors_met(self.iterations, self.overlaps)

    @property
    def clean(self) -> bool:
        return not self.violations and not self.harness_failures and self.floors_met

    def to_dict(self) -> dict[str, object]:
        return {
            "race_id": self.race_id,
            "title": self.title,
            "seed": self.seed,
            "iterations": self.iterations,
            "overlaps": self.overlaps,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "outcomes": dict(sorted(self.outcomes.items())),
            "harness_failures": self.harness_failures,
            "violations": [v.to_dict() for v in self.violations],
            "first_failing_iteration": self.first_failing_iteration,
            "floors_met": self.floors_met,
            "stopped_early": self.stopped_early,
            "budget": {
                "max_iterations": budget.MAX_ITERATIONS,
                "max_seconds": budget.MAX_SECONDS,
                "min_iterations": budget.MIN_ITERATIONS,
                "min_overlaps": budget.MIN_OVERLAPS,
            },
        }


def _intervals(run_tag: str, iteration: int) -> list[tuple[str, datetime, datetime]]:
    """Each writer's [start, end] of this iteration, from the log."""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT kind,
                   coalesce(attempt_start, xact_start),
                   coalesce(ended_at, pg_xact_commit_timestamp(xmin))
            FROM {LOG_TABLE}
            WHERE run_tag = %s AND iteration = %s AND kind <> 'sign_in'
            """,
            [run_tag, iteration],
        )
        rows = cursor.fetchall()
    return [(str(k), s, e) for k, s, e in rows if s is not None and e is not None]


def _overlapped(intervals: list[tuple[str, datetime, datetime]]) -> bool:
    sends = [(s, e) for k, s, e in intervals if k.startswith("send")]
    others = [(s, e) for k, s, e in intervals if not k.startswith("send")]
    return any(s1 < e2 and s2 < e1 for s1, e1 in sends for s2, e2 in others)


def _gated(barrier: Barrier, delay: float, writer: Callable[[], Result]) -> Callable[[], Result]:
    def run() -> Result:
        barrier.wait()
        if delay:
            time.sleep(delay)
        return writer()

    return run


def _writers(
    race: Race, ctx: Context, world: World, rng: random.Random
) -> list[tuple[str, Callable[[], Result], dict[str, Any]]]:
    """The writers of one iteration: a label, the call, and what an attempt row records."""
    subject = ctx.subject
    if race.kind == "revocation":
        assert race.revocation is not None
        rev = race.revocation
        request = send_request(world, key=f"k-{rng.getrandbits(64):x}")
        return [
            (
                "send",
                lambda: subject.send(request),
                {
                    "kind": "send",
                    "match_id": world.match,
                    "actor_id": world.low,
                    "session_id": world.session_low,
                    "contact_version": 1,
                },
            ),
            (
                rev.id,
                lambda: rev.act(world, subject, None),
                {"kind": rev.kind, "match_id": world.match},
            ),
        ]
    if race.kind == "duplicates":
        request = send_request(world, key=f"k-{rng.getrandbits(64):x}")
        record = {
            "kind": "send",
            "match_id": world.match,
            "actor_id": world.low,
            "session_id": world.session_low,
            "contact_version": 1,
        }
        return [
            ("send_a", lambda: subject.send(request), record),
            ("send_b", lambda: subject.send(request), record),
        ]
    request = send_request(world, key=f"k-{rng.getrandbits(64):x}")
    return [
        (
            "send",
            lambda: subject.send(request),
            {
                "kind": "send",
                "match_id": world.match,
                "actor_id": world.low,
                "session_id": world.session_low,
                "contact_version": 1,
            },
        ),
        (
            "block_by_low",
            lambda: subject.block(world.low, world.high),
            {"kind": "block", "match_id": world.match},
        ),
        (
            "block_by_high",
            lambda: subject.block(world.high, world.low),
            {"kind": "block", "match_id": world.match},
        ),
        ("suspend_high", lambda: subject.suspend(world.high), {"kind": "suspend"}),
    ]


def _allowed(race: Race, label: str, result: Result) -> bool:
    if result.outcome in ("deadlock", "error"):
        return False
    if label.startswith("send"):
        return result.outcome in ("authorized", "refused", "replayed")
    return result.outcome == "applied"


def run_race(
    ctx: Context,
    race: Race,
    *,
    seed: int,
    run_tag: str,
    stop_at_first_violation: bool = False,
    max_iterations: int = budget.MAX_ITERATIONS,
    max_seconds: float = budget.MAX_SECONDS,
) -> RaceResult:
    rng = random.Random(f"{seed}:{race.id}")
    result = RaceResult(race.id, race.title, seed)
    started = time.monotonic()
    while result.iterations < max_iterations and time.monotonic() - started < max_seconds:
        iteration = result.iterations + 1
        ctx.log.context.case_id = race.id
        ctx.log.context.iteration = iteration
        world = make_world(ctx)
        writers = _writers(race, ctx, world, rng)
        barrier = Barrier(len(writers))
        order = list(range(len(writers)))
        rng.shuffle(order)
        delays = [0.0] * len(writers)
        # One writer may get a head start of up to 3 ms, chosen by the seed.
        delays[order[0]] = 0.0
        for index in order[1:]:
            delays[index] = rng.choice((0.0, rng.uniform(0.0, 0.003)))
        futures = []
        for (label, writer, record), delay, worker in zip(
            writers, delays, ctx.workers, strict=False
        ):

            def task(
                writer: Callable[[], Result] = writer, record: dict[str, Any] = record
            ) -> Result:
                outcome = writer()
                if not outcome.committed:
                    ctx.log.record_attempt(outcome, **record)
                return outcome

            futures.append((label, worker.submit(_gated(barrier, delay, task))))
        results = [(label, f.result(timeout=budget.HOLD_SECONDS)) for label, f in futures]
        result.iterations = iteration
        for label, outcome in results:
            result.outcomes[f"{label}={outcome.label()}"] += 1
            if not _allowed(race, label, outcome):
                result.harness_failures.append(f"iteration {iteration}: {label}: {outcome.label()}")
        if race.kind == "duplicates":
            rows = submissions_of(world.match)
            if len(rows) != 1:
                result.harness_failures.append(
                    f"iteration {iteration}: {len(rows)} rows for one key"
                )
        if _overlapped(_intervals(run_tag, iteration)):
            result.overlaps += 1
        if stop_at_first_violation:
            report = oracle.evaluate(run_tag=run_tag, iteration=iteration)
            if report.violations or result.harness_failures:
                result.violations.extend(report.violations)
                result.first_failing_iteration = iteration
                result.stopped_early = True
                break
    result.elapsed_seconds = time.monotonic() - started
    ctx.log.context.iteration = None
    ctx.log.context.case_id = None
    return result


def attach_oracle(result: RaceResult, report: oracle.OracleReport, run_tag: str) -> None:
    """After the whole run, the oracle's violations for this race (by its case_id)."""
    mine = [v for v in report.violations_for(run_tag) if v.case_id == result.race_id]
    result.violations = mine
    if mine and result.first_failing_iteration is None:
        iterations = [v.iteration for v in mine if v.iteration is not None]
        result.first_failing_iteration = min(iterations) if iterations else None
