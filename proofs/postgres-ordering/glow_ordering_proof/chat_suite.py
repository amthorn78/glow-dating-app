"""The chat suite's run (SV4 A2; its brief's D10): ``python -m glow_ordering_proof chat``.

On the chat suite's own disposable database (``glow_chat_proof``, in its own job), after
``migrate`` and ``makemigrations --check --dry-run``: it refuses a database an earlier run used,
records the server and the migration ledger, runs every case in ``chat_cases`` in order, then
checks that no secret the run handled (the identity suite's ``SecretLedger``: passwords, codes,
tokens, session keys, the run's keys and the values derived from its ``SECRET_KEY``) and no member
value it sent (``ValueLedger``: SV2's member values, every message's text, and the provider's own
identifiers of channels, users and messages) appears in any log record (captured at DEBUG), in
anything the process wrote, in a response header, or in the results JSON it would write. A
results JSON that holds one is not written. It prints one line per case and ``CHAT VERDICT: PASS``
or ``FAIL``, and exits 0 only on a pass. The job's own check (``chat_scan``) then scans the log and
the JSON with the job's values before the JSON is uploaded.

Before its first statement it installs D14's record of every row lock the process sends
(``row_locks``), and checks it before the verdict, as the other suites do.
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
    migration_times,
    output_texts,
    used_database_reasons,
)

SCAN_CLEAN = "chat secret scan: clean"
SCAN_FOUND = "chat secret scan: FOUND"
VALUES_CLEAN = "chat value scan: clean"
VALUES_FOUND = "chat value scan: FOUND"


@dataclass
class ChatReport:
    server: dict[str, str]
    ledger: list[tuple[str, str, str]]
    cases: list[CaseRecord] = field(default_factory=list)
    seconds: float = 0.0
    secrets_held: int = 0
    secrets_found: int = -1
    values_held: int = 0
    values_found: int = -1
    # D14 (SV3 Stage B): the row locks the suite sent, checked before its verdict.
    row_locks: dict[str, Any] = field(default_factory=dict)
    row_lock_failures: int = 0

    def passed(self) -> bool:
        return (
            bool(self.cases)
            and all(c.passed for c in self.cases)
            and self.secrets_found == 0
            and self.values_found == 0
            and self.row_lock_failures == 0
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _file_secrets() -> list[str]:
    """The run's keys, and every value derived from ``SECRET_KEY`` the discovery suite looks for
    (its pages' cursors are keyed by it, and the cases page through them)."""
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

    from glow_ordering_proof import chat_cases
    from glow_ordering_proof.chat_support import ChatContext
    from glow_ordering_proof.discovery_support import DiscoveryContext
    from glow_ordering_proof.identity_scan import results_text
    from glow_ordering_proof.identity_support import Context, OutputCapture, SecretLedger
    from glow_ordering_proof.observe import migration_ledger, server_facts
    from glow_ordering_proof.profile_support import ProfileContext, ValueLedger

    if settings.ROOT_URLCONF != "glow_ordering_proof.chat_urls":
        print("refusing: the chat suite runs only under glow_ordering_proof.chat_settings")
        return 1
    # D14 (SV3 Stage B): the record of every row lock the suite sends, before its first
    # statement (``row_locks``).
    from glow_ordering_proof import row_locks

    lock_record = row_locks.install()
    if len(chat_cases.CASES) != chat_cases.CASE_COUNT:
        print(
            f"refusing: the suite holds {len(chat_cases.CASES)} cases, not the"
            f" {chat_cases.CASE_COUNT} pinned"
        )
        return 1
    reasons = used_database_reasons()
    if reasons:
        print(
            f"refusing a used database: {'; '.join(reasons)}. The chat suite runs once per new"
            " database."
        )
        return 1
    ledger = SecretLedger()
    for value in _file_secrets():
        ledger.add(value)
    values = ValueLedger()
    capture = OutputCapture()
    capture.install()
    report = ChatReport(server_facts(), migration_times(migration_ledger()))
    ctx: ChatContext | None = None
    started = time.monotonic()
    try:
        if report.server.get("superuser") != "false":
            print("refusing: the chat suite connects as a non-superuser role")
            return 1
        ctx = ChatContext(DiscoveryContext(ProfileContext(Context(ledger), values)))
        for entry in chat_cases.CASES:
            case_started = time.monotonic()
            passed, detail = chat_cases.run_case(ctx, entry)
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
                f"[chat] {verdict} {entry.case_id} ({', '.join(entry.checks)})"
                f" {record.seconds:.1f} s: {detail}",
                flush=True,
            )
    finally:
        report.seconds = duration(time.monotonic() - started)
        capture.uninstall()
        # Everything the process wrote and logged, and every response header the routes sent.
        headers = "\n".join(ctx.profiles.headers if ctx is not None else [])
        text = capture.text() + "\n" + headers
        report.secrets_held = ledger.count()
        report.secrets_found = ledger.found_in(text)
        report.values_held = values.count()
        report.values_found = values.found_in(capture.text(), headers=headers)
    # D14 (SV3 Stage B): checked before the verdict, and before the results JSON is written;
    # counts, and each refused statement's text, never a parameter.
    summary = lock_record.check()
    report.row_locks = summary.as_dict()
    report.row_lock_failures = summary.failures()
    body = report.to_json()
    scanned = results_text(body)
    secrets_in_results = ledger.found_in(scanned)
    values_in_results = values.found_in(scanned)
    report.secrets_found += secrets_in_results
    report.values_found += values_in_results
    passed_cases = sum(c.passed for c in report.cases)
    print(
        f"[chat] cases: {passed_cases}/{len(report.cases)} passed in {report.seconds:.1f} s",
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
        f" ({report.values_held} member values held: member values, message texts, provider"
        f" identifiers; {report.values_found} found in the same output)",
        flush=True,
    )
    texts = output_texts(capture, headers, scanned)
    for where in values.where(texts, headers="the response headers") if report.values_found else []:
        # The kind of value and the text it was found in, never the value.
        print(f"{VALUES_FOUND}: {where}", flush=True)
    for line in summary.lines("chat"):
        print(line, flush=True)
    print(f"CHAT VERDICT: {'PASS' if report.passed() else 'FAIL'}", flush=True)
    if results_path is not None and (secrets_in_results or values_in_results):
        print("results withheld: the results JSON held a secret or a member value")
    elif results_path is not None:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(body, encoding="utf-8")
        print(f"results written: {results_path}")
    return 0 if report.passed() else 1


def plan() -> tuple[str, ...]:
    from glow_ordering_proof import chat_cases

    return chat_cases.plan()
