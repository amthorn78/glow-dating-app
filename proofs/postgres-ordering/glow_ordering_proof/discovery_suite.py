"""The discovery suite's run (SV3 Stage A; D14): ``python -m glow_ordering_proof discovery``.

On the fourth disposable database, after ``migrate`` and ``makemigrations --check --dry-run``: it
refuses a database an earlier run used, records the server and the migration ledger, runs every
case in ``discovery_cases`` in order, then checks that no secret the run handled (the identity
suite's ``SecretLedger``: passwords, codes, tokens, session keys, the run's keys, the cursors'
derived key, and the derived keys and pads the keyed tie-break DM-61 removed would have used) and
no member value it sent (``ValueLedger``: coordinates, the
areas' internal points, distances, birth dates, times and places, own words, sensitive field
values, the photos' keys and references) appears in any log record (captured at DEBUG), in anything
the process wrote, or in the results JSON it would write (acceptance check 13). A results JSON that
holds one is not written. It prints one line per case and ``DISCOVERY VERDICT: PASS`` or ``FAIL``,
and exits 0 only on a pass. The job's own check (``discovery_scan``) then scans the log and the JSON
with the job's values before the JSON is uploaded.

The results JSON also holds the recorded query plans (D14; DB11), labelled as the disposable
setup's measurement at the stated population, the statements per page request (D7) and D8's
population-of-one record.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from glow_ordering_proof.profile_suite import (
    CaseRecord,
    duration,
    output_texts,
    used_database_reasons,
)

SCAN_CLEAN = "discovery secret scan: clean"
SCAN_FOUND = "discovery secret scan: FOUND"
VALUES_CLEAN = "discovery value scan: clean"
VALUES_FOUND = "discovery value scan: FOUND"
MEASUREMENT = (
    "The disposable setup's measurement (PF01 P09: no extrapolation): PostgreSQL 17.11 in the CI"
    " job's container, one run, at the population each plan states; not a capacity claim."
)


@dataclass
class DiscoveryReport:
    server: dict[str, str]
    ledger: list[tuple[str, str, str]]
    cases: list[CaseRecord] = field(default_factory=list)
    seconds: float = 0.0
    secrets_held: int = 0
    secrets_found: int = -1
    values_held: int = 0
    values_found: int = -1
    plans: dict[str, Any] = field(default_factory=dict)
    statements_per_page: dict[str, int] = field(default_factory=dict)
    disclosure: dict[str, Any] = field(default_factory=dict)

    def passed(self) -> bool:
        return (
            bool(self.cases)
            and all(c.passed for c in self.cases)
            and self.secrets_found == 0
            and self.values_found == 0
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _file_secrets() -> list[str]:
    """The run's keys, the cursors' derived key (D7), and every value derived from ``SECRET_KEY``
    the tie-break check looks for (``discovery_support.derived_from_secret_key``: the keyed
    tie-break's derived key and pads DM-61 removed, which no statement may carry)."""
    from django.conf import settings

    from glow_ordering_proof import identity_environment
    from glow_ordering_proof.discovery_support import derived_from_secret_key

    values = [
        settings.SECRET_KEY,
        *identity_environment.pem_body_lines(settings.HEADLESS_JWT_PRIVATE_KEY),
        *derived_from_secret_key(),
    ]
    return [value for value in values if isinstance(value, str)]


def run(results_path: Path | None) -> int:
    from django.conf import settings

    from glow_ordering_proof import discovery_cases
    from glow_ordering_proof.discovery_support import DiscoveryContext
    from glow_ordering_proof.identity_scan import results_text
    from glow_ordering_proof.identity_support import Context, OutputCapture, SecretLedger
    from glow_ordering_proof.observe import migration_ledger, server_facts
    from glow_ordering_proof.profile_support import ProfileContext, ValueLedger

    if settings.ROOT_URLCONF != "glow_ordering_proof.discovery_urls":
        print(
            "refusing: the discovery suite runs only under glow_ordering_proof.discovery_settings"
        )
        return 1
    if len(discovery_cases.CASES) != discovery_cases.CASE_COUNT:
        print(
            f"refusing: the suite holds {len(discovery_cases.CASES)} cases, not the"
            f" {discovery_cases.CASE_COUNT} pinned"
        )
        return 1
    reasons = used_database_reasons()
    if reasons:
        print(
            f"refusing a used database: {'; '.join(reasons)}. The discovery suite runs once per"
            " new database."
        )
        return 1
    ledger = SecretLedger()
    for value in _file_secrets():
        ledger.add(value)
    values = ValueLedger()
    capture = OutputCapture()
    capture.install()
    report = DiscoveryReport(server_facts(), migration_ledger())
    ctx: DiscoveryContext | None = None
    started = time.monotonic()
    try:
        if report.server.get("superuser") != "false":
            print("refusing: the discovery suite connects as a non-superuser role")
            return 1
        ctx = DiscoveryContext(ProfileContext(Context(ledger), values))
        for entry in discovery_cases.CASES:
            case_started = time.monotonic()
            passed, detail = discovery_cases.run_case(ctx, entry)
            record = CaseRecord(
                entry.case_id,
                list(entry.checks),
                passed,
                duration(time.monotonic() - case_started),
                detail,
            )
            report.cases.append(record)
            verdict = "PASS" if passed else "FAIL"
            print(
                f"[discovery] {verdict} {entry.case_id} ({', '.join(entry.checks)})"
                f" {record.seconds:.1f} s: {detail}",
                flush=True,
            )
        report.plans = {"measurement": MEASUREMENT, "population": 1000, "queries": ctx.plans}
        report.statements_per_page = dict(ctx.statements)
        report.disclosure = dict(ctx.disclosure)
    finally:
        report.seconds = duration(time.monotonic() - started)
        capture.uninstall()
        # Everything the process wrote and logged, and every response header the routes sent.
        headers = "\n".join(ctx.profiles.headers if ctx is not None else [])
        text = capture.text() + "\n" + headers
        report.secrets_held = ledger.count()
        report.secrets_found = ledger.found_in(text)
        report.values_held = values.count()
        # DM-64 T4: a match inside a timing PostgreSQL wrote into a plan is not counted.
        report.values_found = values.found_in(text, plan_timings=True)
    body = report.to_json()
    scanned = results_text(body)
    secrets_in_results = ledger.found_in(scanned)
    values_in_results = values.found_in(scanned, plan_timings=True)
    report.secrets_found += secrets_in_results
    report.values_found += values_in_results
    passed_cases = sum(c.passed for c in report.cases)
    print(
        f"[discovery] cases: {passed_cases}/{len(report.cases)} passed in {report.seconds:.1f} s",
        flush=True,
    )
    print(
        f"{SCAN_CLEAN if report.secrets_found == 0 else SCAN_FOUND}"
        f" ({report.secrets_held} secrets held; {report.secrets_found} found in"
        f" {len(capture.records)} log records, {len(capture.written)} writes and the results"
        " JSON)",
        flush=True,
    )
    print(
        f"{VALUES_CLEAN if report.values_found == 0 else VALUES_FOUND}"
        f" ({report.values_held} member values held: coordinates, internal points, distances,"
        f" birth dates, times and places, own words, sensitive values, photo keys and references;"
        f" {report.values_found} found in the same output)",
        flush=True,
    )
    texts = output_texts(capture, headers, scanned)
    for where in values.where(texts, plan_timings=True) if report.values_found else []:
        # DM-64 T7: the kind of value and the text it was found in, never the value.
        print(f"{VALUES_FOUND}: {where}", flush=True)
    for name, number in sorted(report.statements_per_page.items()):
        print(f"[discovery] statements per page request: {name}: {number}", flush=True)
    for name, plan in sorted((report.plans.get("queries") or {}).items()):
        print(
            f"[discovery] plan at 1,000 members: {name}: {plan.get('execution', '')};"
            f" nodes {', '.join(plan.get('nodes', []))}",
            flush=True,
        )
    print(f"DISCOVERY VERDICT: {'PASS' if report.passed() else 'FAIL'}", flush=True)
    if results_path is not None and (secrets_in_results or values_in_results):
        print("results withheld: the results JSON held a secret or a member value")
    elif results_path is not None:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(body, encoding="utf-8")
        print(f"results written: {results_path}")
    return 0 if report.passed() else 1


def plan() -> tuple[str, ...]:
    from glow_ordering_proof import discovery_cases

    return discovery_cases.plan()
