"""The proof's commands, run with the proof's settings in a clean environment::

    python -m glow_ordering_proof facts       # SELECT version(), settings, the applied ledger
    python -m glow_ordering_proof run --seed 20260929 --results results.json

``run`` executes the suite on two subjects (P06.2, D3): the reference design, then the
app's adapter (``services/api``'s ``glow_chat``), each with the forced and named cases,
the stress races, its controls and the commit-order oracle over every row of its own,
reported separately; then the delivery phase, the app's outbox against the fixture
provider. It refuses a database an earlier run used (P06.DB's carried item 1). It exits
0 only on a PASS. Django's own ``migrate`` and ``makemigrations --check --dry-run`` run
separately (``python -m django ...``); Django's ``dbshell`` is refused under these
settings (the proof's own command, P06.DB's carried item 6).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

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


def refuse_used_database() -> bool:
    """P06.DB's carried item 1 (R2): a database an earlier run wrote to is refused before
    anything is written, so no run reads another run's rows as its own."""
    from django.db import connection

    from glow_ordering_proof.observe import USED_DATABASE, used_database_reasons

    with connection.cursor() as cursor:
        reasons = used_database_reasons(cursor)
    if reasons:
        print(
            f"{USED_DATABASE}: {'; '.join(reasons)}. The proof runs once per new disposable"
            " database.",
            flush=True,
        )
        return True
    return False


def run_subject(ctx: Any, seed: int, report: Any, *, reference: bool) -> None:
    """One subject: every case, the stress races, its controls, then the oracle over
    every row of the subject, each printed with the subject's name."""
    from glow_ordering_proof import stress
    from glow_ordering_proof.cases import all_cases, run_all
    from glow_ordering_proof.controls import CONTROLS, run_control
    from glow_ordering_proof.observe import LogContext
    from glow_ordering_proof.planted import (
        AdapterPlanter,
        ReferencePlanter,
        planted_for,
        run_planted,
    )

    name = ctx.name
    log = ctx.log
    log.context = LogContext(run_tag="design:forced", variant=name)
    report.cases = run_all(ctx, all_cases(d5=ctx.d5))
    passed = sum(c.passed for c in report.cases)
    print(f"[{name}] cases: {passed}/{len(report.cases)} passed", flush=True)
    log.context = LogContext(run_tag="design:stress", variant=name)
    for race in stress.races(d5=ctx.d5):
        result = stress.run_race(ctx, race, seed=seed, run_tag="design:stress")
        report.races.append(result)
        orders = ", ".join(f"{k} {v}" for k, v in sorted(result.orders.items()))
        print(
            f"[{name}] race {race.id}: {result.iterations} iterations, {result.overlaps} overlaps,"
            f" {result.elapsed_seconds:.1f} s; orders: {orders}",
            flush=True,
        )
    if reference:
        for control in CONTROLS:
            outcome = run_control(control, log=log, workers=ctx.workers, seed=seed)
            report.controls.append(outcome)
            verdict = (
                "failed as intended" if outcome.failed_as_intended else "DID NOT FAIL AS INTENDED"
            )
            print(
                f"[{name}] control {control.id}: declared signal {outcome.declared}: {verdict}",
                flush=True,
            )
    planter = ReferencePlanter(log) if reference else AdapterPlanter(log)
    for planted in planted_for(d5=ctx.d5):
        outcome = run_planted(planted, ctx, planter)
        report.controls.append(outcome)
        verdict = "flagged as intended" if outcome.failed_as_intended else "NOT FLAGGED"
        print(f"[{name}] planted {planted.id}: declared {outcome.declared}: {verdict}", flush=True)
    report.oracle = ctx.evidence.evaluate()
    for race_result in report.races:
        stress.attach_oracle(race_result, report.oracle, "design:stress")
    design = len(report.design_violations())
    print(
        f"[{name}] oracle: {report.oracle.submissions} submissions,"
        f" {report.oracle.revocations} revocation witnesses, {design} violations in the"
        " design's rows",
        flush=True,
    )


def run(seed: int, results_path: Path | None) -> int:
    from django.db import connection, transaction

    from glow_ordering_proof.observe import migration_ledger, server_facts
    from glow_ordering_proof.results import Report, render

    server = server_facts()
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SHOW transaction_isolation")
        isolation = str(cursor.fetchone()[0])
    ledger = migration_ledger()
    reference_report = Report(seed, server, isolation, ledger, subject="reference")
    if server.get("superuser") != "false":
        reference_report.problems.append("the proof must connect as a non-superuser role")
    if server.get("track_commit_timestamp") != "on":
        reference_report.problems.append("track_commit_timestamp is not on; the oracle needs it")
    if isolation != "read committed":
        reference_report.problems.append(
            f"transaction isolation is {isolation}, not read committed"
        )
    if reference_report.problems:
        print(render(reference_report))
        return 1
    if refuse_used_database():
        return 1
    adapter_report = Report(seed, server, isolation, ledger, subject="adapter")
    return run_suite(seed, results_path, reference_report, adapter_report)


def run_suite(
    seed: int, results_path: Path | None, reference_report: Any, adapter_report: Any
) -> int:
    """Both subjects, then the delivery phase, on a database ``run`` has accepted."""
    from glow_chat.contact import OrmContactPersistence

    from glow_ordering_proof.adapter import PROVIDER, AdapterFixtures, AdapterSubject
    from glow_ordering_proof.cases import Context
    from glow_ordering_proof.concurrency import Worker
    from glow_ordering_proof.delivery_phase import run_delivery_phase
    from glow_ordering_proof.evidence import AdapterEvidence, ReferenceEvidence
    from glow_ordering_proof.fixtures import DjangoFixtures
    from glow_ordering_proof.observe import ProofLog
    from glow_ordering_proof.reference import ReferenceSubject
    from glow_ordering_proof.results import RunReport, render_run

    log = ProofLog()
    log.ensure_table()
    workers = [Worker(f"proof-writer-{i}") for i in range(4)]
    adapter = OrmContactPersistence(provider=PROVIDER)
    run_report = RunReport([reference_report, adapter_report])
    try:
        reference_ctx = Context(
            ReferenceSubject(log), DjangoFixtures(), log, workers, ReferenceEvidence(log)
        )
        run_subject(reference_ctx, seed, reference_report, reference=True)
        adapter_ctx = Context(
            AdapterSubject(adapter, log),
            AdapterFixtures(adapter),
            log,
            workers,
            AdapterEvidence(),
            name="adapter",
            d5=True,
        )
        run_subject(adapter_ctx, seed, adapter_report, reference=False)
        # Delivery changes the rows whose commit times the oracle read, so it runs only
        # after both subjects' oracles.
        run_report.delivery = run_delivery_phase(adapter_ctx)
        passed = sum(c.passed for c in run_report.delivery.checks)
        print(
            f"[delivery] {run_report.delivery.drained} events drained;"
            f" checks {passed}/{len(run_report.delivery.checks)} passed",
            flush=True,
        )
    finally:
        for worker in workers:
            worker.close()
    print(render_run(run_report))
    if results_path is not None:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(run_report.to_json(), encoding="utf-8")
        print(f"results written: {results_path}")
    ok, _ = run_report.verdict()
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
