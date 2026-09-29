"""Result recording: the report, its JSON and the table printed in the job's log.

Nothing here ever sees a connection option, a password or a passfile path: the report
holds what the database answered and what the cases judged, and the renderer prints
only that.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from glow_ordering_proof import budget

DESIGN_TAG_PREFIX = "design:"


@dataclass
class Report:
    seed: int
    facts: dict[str, str]
    isolation_observed: str
    ledger: list[tuple[str, str, str]]
    cases: list[Any] = field(default_factory=list)  # CaseResult
    races: list[Any] = field(default_factory=list)  # RaceResult
    controls: list[Any] = field(default_factory=list)  # ControlResult
    oracle: Any = None  # OracleReport over every row
    problems: list[str] = field(default_factory=list)

    def design_violations(self) -> list[Any]:
        if self.oracle is None:
            return []
        return [
            v
            for v in self.oracle.violations
            if v.run_tag.startswith(DESIGN_TAG_PREFIX) or v.run_tag in ("untagged", "any")
        ]

    def verdict(self) -> tuple[bool, list[str]]:
        reasons = list(self.problems)
        failed_cases = [c.case_id for c in self.cases if not c.passed]
        if failed_cases:
            reasons.append(f"cases failed: {', '.join(failed_cases)}")
        for race in self.races:
            if not race.clean:
                reasons.append(
                    f"race {race.race_id}: violations={len(race.violations)}"
                    f" harness_failures={len(race.harness_failures)} iterations={race.iterations}"
                    f" overlaps={race.overlaps} floors_met={race.floors_met}"
                )
        not_failing = [c.control_id for c in self.controls if not c.failed_as_intended]
        if not_failing:
            reasons.append(
                "controls that did not fail as intended (declared signal absent):"
                f" {', '.join(not_failing)}"
            )
        if self.design_violations():
            reasons.append(
                f"oracle violations in the design's rows: {len(self.design_violations())}"
            )
        if self.oracle is None:
            reasons.append("the oracle did not run")
        return (not reasons, reasons)

    def to_dict(self) -> dict[str, object]:
        ok, reasons = self.verdict()
        return {
            "verdict": "PASS" if ok else "FAIL",
            "reasons": reasons,
            "seed": self.seed,
            "server": self.facts,
            "transaction_isolation_observed": self.isolation_observed,
            "migrations_applied": [list(row) for row in self.ledger],
            "cases": [c.to_dict() for c in self.cases],
            "races": [r.to_dict() for r in self.races],
            "controls": [c.to_dict() for c in self.controls],
            "oracle": self.oracle.to_dict() if self.oracle is not None else None,
            "budget": {
                "max_iterations": budget.MAX_ITERATIONS,
                "max_seconds": budget.MAX_SECONDS,
                "min_iterations": budget.MIN_ITERATIONS,
                "min_overlaps": budget.MIN_OVERLAPS,
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True, default=str)


def table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    cells = [[str(h) for h in headers]] + [[str(c) for c in row] for row in rows]
    widths = [max(len(r[i]) for r in cells) for i in range(len(headers))]
    lines = []
    for index, row in enumerate(cells):
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
        if index == 0:
            lines.append("  ".join("-" * w for w in widths))
    return "\n".join(lines)


def render(report: Report) -> str:
    ok, reasons = report.verdict()
    out: list[str] = []
    out.append("== P06.DB disposable-PostgreSQL proof ==")
    out.append("")
    out.append("-- Server (from the database) --")
    out.append(table(("fact", "value"), sorted(report.facts.items())))
    out.append(
        f"transaction_isolation (inside a writer's transaction): {report.isolation_observed}"
    )
    out.append("")
    out.append("-- Migrations applied (django_migrations) --")
    out.append(table(("app", "name", "applied"), report.ledger))
    out.append("")
    out.append("-- Cases (the reference design) --")
    out.append(
        table(
            ("case", "result", "waits observed", "notes"),
            (
                (
                    c.case_id,
                    "PASS" if c.passed else "FAIL",
                    "; ".join(w.summary() for w in c.waits) or "-",
                    "; ".join(c.failures) if c.failures else "; ".join(c.notes)[:160],
                )
                for c in report.cases
            ),
        )
    )
    out.append("")
    out.append(
        f"-- Stress races (seed {report.seed}; budget {budget.MAX_ITERATIONS} iterations or"
        f" {budget.MAX_SECONDS:g} s per race; floors {budget.MIN_ITERATIONS} iterations and"
        f" {budget.MIN_OVERLAPS} overlaps) --"
    )
    out.append(
        table(
            (
                "race",
                "iterations",
                "overlaps",
                "violations",
                "harness failures",
                "seconds",
                "floors",
                "outcomes",
            ),
            (
                (
                    r.race_id,
                    r.iterations,
                    r.overlaps,
                    len(r.violations),
                    len(r.harness_failures),
                    f"{r.elapsed_seconds:.1f}",
                    "met" if r.floors_met else "NOT MET",
                    ", ".join(f"{k}:{v}" for k, v in sorted(r.outcomes.items())),
                )
                for r in report.races
            ),
        )
    )
    out.append("")
    out.append("-- Negative controls (each must fail by its declared signal) --")
    out.append(
        table(
            (
                "control",
                "variant",
                "mode",
                "target",
                "declared signal",
                "failed as intended",
                "first failing iteration",
                "signal",
            ),
            (
                (
                    c.control_id,
                    c.variant,
                    c.mode,
                    c.target,
                    c.declared or "-",
                    "yes" if c.failed_as_intended else "NO",
                    c.first_failing_iteration if c.first_failing_iteration is not None else "-",
                    c.signal[:200],
                )
                for c in report.controls
            ),
        )
    )
    out.append("")
    out.append("-- Commit-order oracle (every row) --")
    if report.oracle is not None:
        out.append(
            f"submissions examined: {report.oracle.submissions};"
            f" revocation rows: {report.oracle.revocations}"
        )
        out.append(table(("run_tag", "submissions"), sorted(report.oracle.by_tag.items())))
        counts: dict[str, int] = {}
        for v in report.oracle.violations:
            counts[v.run_tag] = counts.get(v.run_tag, 0) + 1
        out.append(
            table(("run_tag", "violations"), sorted(counts.items())) if counts else "no violations"
        )
        design = report.design_violations()
        out.append(f"violations in the design's rows: {len(design)}")
        for v in design[:20]:
            out.append(
                f"  {v.rule} {v.run_tag} {v.case_id} it={v.iteration} {v.submission_id}: {v.detail}"
            )
    out.append("")
    out.append(f"== VERDICT: {'PASS' if ok else 'FAIL'} ==")
    for reason in reasons:
        out.append(f"  - {reason}")
    return "\n".join(out)
