"""The identity suite's run (SV1; its brief's D10): ``python -m glow_ordering_proof identity``.

On the second disposable database, after ``migrate`` and ``makemigrations --check --dry-run``:
it refuses a database an earlier run used, records the server and the migration ledger, runs
every case in ``identity_cases`` in order, then checks that no secret the run handled appears in
any log record (captured at DEBUG) or in anything the process wrote (acceptance check 12). It
prints one line per case and ``IDENTITY VERDICT: PASS`` or ``FAIL``, and exits 0 only on a pass.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

USED_DATABASE = "refusing a used database"
SCAN_CLEAN = "identity secret scan: clean"
SCAN_FOUND = "identity secret scan: FOUND"


@dataclass
class CaseRecord:
    case_id: str
    checks: list[str]
    passed: bool
    seconds: float
    detail: str


@dataclass
class IdentityReport:
    server: dict[str, str]
    ledger: list[tuple[str, str, str]]
    cases: list[CaseRecord] = field(default_factory=list)
    seconds: float = 0.0
    secrets_held: int = 0
    secrets_found: int = -1

    def passed(self) -> bool:
        return bool(self.cases) and all(c.passed for c in self.cases) and self.secrets_found == 0

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def used_database_reasons() -> list[str]:
    from django.contrib.auth import get_user_model
    from glow_persistence.models import AppAccount, OutboxEvent

    reasons = []
    if get_user_model().objects.exists():
        reasons.append("auth users exist")
    if AppAccount.objects.exists():
        reasons.append("app accounts exist")
    if OutboxEvent.objects.exists():
        reasons.append("outbox events exist")
    return reasons


def _file_secrets() -> list[str]:
    """The run's own keys, read back from the identity settings, for the scan only."""
    from django.conf import settings

    from glow_ordering_proof import identity_environment

    values = [
        settings.SECRET_KEY,
        *identity_environment.pem_body_lines(settings.HEADLESS_JWT_PRIVATE_KEY),
    ]
    return [value for value in values if isinstance(value, str)]


def run(results_path: Path | None) -> int:
    from django.conf import settings

    from glow_ordering_proof import identity_cases
    from glow_ordering_proof.identity_support import Context, OutputCapture, SecretLedger
    from glow_ordering_proof.observe import migration_ledger, server_facts

    if settings.ROOT_URLCONF != "glow_identity.urls":
        print("refusing: the identity suite runs only under glow_ordering_proof.identity_settings")
        return 1
    reasons = used_database_reasons()
    if reasons:
        print(
            f"{USED_DATABASE}: {'; '.join(reasons)}. The identity suite runs once per new database."
        )
        return 1
    ledger = SecretLedger()
    for value in _file_secrets():
        ledger.add(value)
    capture = OutputCapture()
    capture.install()
    report = IdentityReport(server_facts(), migration_ledger())
    started = time.monotonic()
    try:
        if report.server.get("superuser") != "false":
            print("refusing: the identity suite connects as a non-superuser role")
            return 1
        ctx = Context(ledger)
        for entry in identity_cases.CASES:
            case_started = time.monotonic()
            passed, detail = identity_cases.run_case(ctx, entry)
            record = CaseRecord(
                entry.case_id, list(entry.checks), passed, time.monotonic() - case_started, detail
            )
            report.cases.append(record)
            verdict = "PASS" if passed else "FAIL"
            print(
                f"[identity] {verdict} {entry.case_id} ({', '.join(entry.checks)})"
                f" {record.seconds:.1f} s: {detail}",
                flush=True,
            )
    finally:
        report.seconds = time.monotonic() - started
        capture.uninstall()
        report.secrets_held = ledger.count()
        report.secrets_found = ledger.found_in(capture.text())
    passed_cases = sum(c.passed for c in report.cases)
    print(
        f"[identity] cases: {passed_cases}/{len(report.cases)} passed in {report.seconds:.1f} s",
        flush=True,
    )
    print(
        f"{SCAN_CLEAN if report.secrets_found == 0 else SCAN_FOUND}"
        f" ({report.secrets_held} secrets held; {report.secrets_found} found in"
        f" {len(capture.records)} log records and {len(capture.written)} writes)",
        flush=True,
    )
    print(f"IDENTITY VERDICT: {'PASS' if report.passed() else 'FAIL'}", flush=True)
    if results_path is not None:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(report.to_json(), encoding="utf-8")
        print(f"results written: {results_path}")
    return 0 if report.passed() else 1


def plan() -> tuple[str, ...]:
    from glow_ordering_proof import identity_cases

    return identity_cases.plan()


_: Any = os  # the command's environment is the caller's clean one
