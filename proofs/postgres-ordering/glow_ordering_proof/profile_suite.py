"""The profile suite's run (SV2 Stage A; D12): ``python -m glow_ordering_proof profile``.

On the third disposable database, after ``migrate`` and ``makemigrations --check --dry-run``: it
refuses a database an earlier run used, records the server and the migration ledger, runs every
case in ``profile_cases`` in order, then checks that no secret the run handled (the identity
suite's ``SecretLedger``: passwords, codes, tokens, session keys, the run's keys) and no member
value it sent (``ValueLedger``: coordinates, birth dates, times and places, own words, sensitive
field values) appears in any log record (captured at DEBUG), in anything the process wrote, or in
the results JSON it would write (acceptance check 12). A results JSON that holds one is not
written. It prints one line per case and ``PROFILE VERDICT: PASS`` or ``FAIL``, and exits 0 only
on a pass. The job's own check (``profile_scan``) then scans the log and the JSON with the job's
values before the JSON is uploaded.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

USED_DATABASE = "refusing a used database"
SCAN_CLEAN = "profile secret scan: clean"
SCAN_FOUND = "profile secret scan: FOUND"
VALUES_CLEAN = "profile value scan: clean"
VALUES_FOUND = "profile value scan: FOUND"


@dataclass
class CaseRecord:
    case_id: str
    checks: list[str]
    passed: bool
    seconds: float
    detail: str


@dataclass
class ProfileReport:
    server: dict[str, str]
    ledger: list[tuple[str, str, str]]
    cases: list[CaseRecord] = field(default_factory=list)
    seconds: float = 0.0
    secrets_held: int = 0
    secrets_found: int = -1
    values_held: int = 0
    values_found: int = -1

    def passed(self) -> bool:
        return (
            bool(self.cases)
            and all(c.passed for c in self.cases)
            and self.secrets_found == 0
            and self.values_found == 0
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def used_database_reasons() -> list[str]:
    from django.contrib.auth import get_user_model
    from glow_persistence.models import AppAccount, OutboxEvent, SettingVersion

    reasons = []
    if get_user_model().objects.exists():
        reasons.append("auth users exist")
    if AppAccount.objects.exists():
        reasons.append("app accounts exist")
    if OutboxEvent.objects.exists():
        reasons.append("outbox events exist")
    if SettingVersion.objects.filter(number__gt=1).exists():
        reasons.append("a setting was published beyond its launch default")
    return reasons


def _file_secrets() -> list[str]:
    from django.conf import settings

    from glow_ordering_proof import identity_environment

    values = [
        settings.SECRET_KEY,
        *identity_environment.pem_body_lines(settings.HEADLESS_JWT_PRIVATE_KEY),
    ]
    return [value for value in values if isinstance(value, str)]


def run(results_path: Path | None) -> int:
    from django.conf import settings

    from glow_ordering_proof import profile_cases
    from glow_ordering_proof.identity_scan import results_text
    from glow_ordering_proof.identity_support import Context, OutputCapture, SecretLedger
    from glow_ordering_proof.observe import migration_ledger, server_facts
    from glow_ordering_proof.profile_support import ProfileContext, ValueLedger

    if settings.ROOT_URLCONF != "glow_ordering_proof.profile_urls":
        print("refusing: the profile suite runs only under glow_ordering_proof.profile_settings")
        return 1
    reasons = used_database_reasons()
    if reasons:
        print(
            f"{USED_DATABASE}: {'; '.join(reasons)}. The profile suite runs once per new database."
        )
        return 1
    ledger = SecretLedger()
    for value in _file_secrets():
        ledger.add(value)
    values = ValueLedger()
    capture = OutputCapture()
    capture.install()
    report = ProfileReport(server_facts(), migration_ledger())
    ctx: ProfileContext | None = None
    started = time.monotonic()
    try:
        if report.server.get("superuser") != "false":
            print("refusing: the profile suite connects as a non-superuser role")
            return 1
        ctx = ProfileContext(Context(ledger), values)
        for entry in profile_cases.CASES:
            case_started = time.monotonic()
            passed, detail = profile_cases.run_case(ctx, entry)
            record = CaseRecord(
                entry.case_id, list(entry.checks), passed, time.monotonic() - case_started, detail
            )
            report.cases.append(record)
            verdict = "PASS" if passed else "FAIL"
            print(
                f"[profile] {verdict} {entry.case_id} ({', '.join(entry.checks)})"
                f" {record.seconds:.1f} s: {detail}",
                flush=True,
            )
    finally:
        report.seconds = time.monotonic() - started
        capture.uninstall()
        # Everything the process wrote and logged, and every response header the routes sent.
        text = capture.text() + "\n" + "\n".join(ctx.headers if ctx is not None else [])
        report.secrets_held = ledger.count()
        report.secrets_found = ledger.found_in(text)
        report.values_held = values.count()
        report.values_found = values.found_in(text)
    # The results JSON is output too: a secret or a member value in it fails the run, and the
    # file is not written. It is searched as written and as its decoded strings, because JSON
    # escapes a non-ASCII value (the own words' case sends one).
    body = report.to_json()
    scanned = results_text(body)
    secrets_in_results = ledger.found_in(scanned)
    values_in_results = values.found_in(scanned)
    report.secrets_found += secrets_in_results
    report.values_found += values_in_results
    passed_cases = sum(c.passed for c in report.cases)
    print(
        f"[profile] cases: {passed_cases}/{len(report.cases)} passed in {report.seconds:.1f} s",
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
        f" ({report.values_held} member values held: coordinates, birth dates, times and places,"
        f" own words, sensitive values; {report.values_found} found in the same output)",
        flush=True,
    )
    print(f"PROFILE VERDICT: {'PASS' if report.passed() else 'FAIL'}", flush=True)
    if results_path is not None and (secrets_in_results or values_in_results):
        print("results withheld: the results JSON held a secret or a member value")
    elif results_path is not None:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(body, encoding="utf-8")
        print(f"results written: {results_path}")
    return 0 if report.passed() else 1


def plan() -> tuple[str, ...]:
    from glow_ordering_proof import profile_cases

    return profile_cases.plan()
