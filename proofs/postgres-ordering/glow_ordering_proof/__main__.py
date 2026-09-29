"""The proof's commands, run with the proof's settings in a clean environment::

    python -m glow_ordering_proof facts       # SELECT version(), settings, the applied ledger
    python -m glow_ordering_proof run --seed 20260929 --results results.json

``run`` executes the suite: the forced and named cases, the stress races, the negative
controls and the commit-order oracle over every row, then prints the results table.
It exits 0 only on a PASS. Django's own ``migrate`` and ``makemigrations --check
--dry-run`` run separately (``python -m django ...``).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from glow_ordering_proof import budget


def _setup() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glow_ordering_proof.settings")
    import django

    django.setup()


def facts() -> int:
    from glow_ordering_proof.observe import migration_ledger, server_facts
    from glow_ordering_proof.results import table

    print(table(("fact", "value"), sorted(server_facts().items())))
    print(table(("app", "name", "applied"), migration_ledger()))
    return 0


def run(seed: int, results_path: Path | None) -> int:
    from django.db import connection, transaction

    from glow_ordering_proof import oracle, stress
    from glow_ordering_proof.cases import Context, run_all
    from glow_ordering_proof.concurrency import Worker
    from glow_ordering_proof.controls import CONTROLS, run_control
    from glow_ordering_proof.fixtures import DjangoFixtures
    from glow_ordering_proof.observe import LogContext, ProofLog, migration_ledger, server_facts
    from glow_ordering_proof.reference import ReferenceSubject
    from glow_ordering_proof.results import Report, render

    server = server_facts()
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SHOW transaction_isolation")
        isolation = str(cursor.fetchone()[0])
    report = Report(seed, server, isolation, migration_ledger())
    if server.get("superuser") != "false":
        report.problems.append("the proof must connect as a non-superuser role")
    if server.get("track_commit_timestamp") != "on":
        report.problems.append("track_commit_timestamp is not on; the oracle needs it")
    if isolation != "read committed":
        report.problems.append(f"transaction isolation is {isolation}, not read committed")
    if report.problems:
        print(render(report))
        return 1

    log = ProofLog()
    log.ensure_table()
    workers = [Worker(f"proof-writer-{i}") for i in range(4)]
    try:
        ctx = Context(ReferenceSubject(log), DjangoFixtures(), log, workers)
        log.context = LogContext(run_tag="design:forced", variant="reference")
        report.cases = run_all(ctx)
        print(
            f"cases: {sum(c.passed for c in report.cases)}/{len(report.cases)} passed", flush=True
        )
        log.context = LogContext(run_tag="design:stress", variant="reference")
        for race in stress.RACES:
            result = stress.run_race(ctx, race, seed=seed, run_tag="design:stress")
            report.races.append(result)
            print(
                f"race {race.id}: {result.iterations} iterations, {result.overlaps} overlaps,"
                f" {result.elapsed_seconds:.1f} s",
                flush=True,
            )
        for control in CONTROLS:
            outcome = run_control(control, log=log, workers=workers, seed=seed)
            report.controls.append(outcome)
            verdict = (
                "failed as intended" if outcome.failed_as_intended else "DID NOT FAIL AS INTENDED"
            )
            print(
                f"control {control.id}: declared signal {outcome.declared}: {verdict}", flush=True
            )
        report.oracle = oracle.evaluate()
        for race_result in report.races:
            stress.attach_oracle(race_result, report.oracle, "design:stress")
    finally:
        for worker in workers:
            worker.close()
    text = render(report)
    print(text)
    if results_path is not None:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(report.to_json(), encoding="utf-8")
        print(f"results written: {results_path}")
    ok, _ = report.verdict()
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m glow_ordering_proof")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("facts")
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--seed", type=int, default=budget.DEFAULT_SEED)
    run_parser.add_argument("--results", type=Path, default=None)
    args = parser.parse_args(argv)
    _setup()
    if args.command == "facts":
        return facts()
    return run(args.seed, args.results)


if __name__ == "__main__":
    sys.exit(main())
