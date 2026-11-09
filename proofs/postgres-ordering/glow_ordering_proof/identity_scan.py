"""The job's secret check of the identity suite's output (SV1; its brief's D10 and acceptance
check 12; correction C1, DM-47 C1.4).

The Database proof checks job runs it after the suite::

    python -m glow_ordering_proof.identity_scan <directory> <log> <results JSON>

``<directory>`` is the job's protected temporary directory, which holds the run's secrets in
files (D2, D10). The check reads the job's own values from it: the identity settings'
``SECRET_KEY``, the identity database's marker, the ordering database's marker, the
PostgreSQL superuser's password, every password in the passfile and every line of the JWT
signing key. It looks for each in the suite's log and in its results JSON, the same values in
both, and it asks the log for the suite's own clean scan. It passes only when no value is found
in either file and the suite reported clean.

On a refusal it removes the results JSON, so nothing is left to upload; the job uploads the
JSON only after this check has passed. It prints counts and file names only, never a value or
a line of either file. It imports nothing outside the standard library and needs no settings,
database or network.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# The files of the job's directory whose whole content is one secret value.
VALUE_FILES = ("identity-secret-key", "identity-marker", "marker", "superuser-password")
PASSFILE = "passfile"
JWT_KEY_FILE = "identity-jwt-key.pem"
SUITE_CLEAN = "identity secret scan: clean"
PASSED = 0
REFUSED = 3


class ScanError(Exception):
    """The check could not read what it needs. The message names a file, never a value."""


def job_values(directory: Path) -> list[str]:
    """The job's own secret values, read from its directory: the same list the job's check of
    the log has used since SV1."""
    values: list[str] = []
    try:
        for name in VALUE_FILES:
            values.append((directory / name).read_text(encoding="ascii").strip())
        for line in (directory / PASSFILE).read_text(encoding="ascii").splitlines():
            if line.strip():
                values.append(line.rsplit(":", 1)[1])
        pem = (directory / JWT_KEY_FILE).read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError, IndexError):
        raise ScanError("a secret file of the job's directory could not be read") from None
    values += [line for line in pem.splitlines() if line and not line.startswith("-----")]
    return [value for value in values if value]


def _strings(value: Any) -> Iterable[str]:
    """Every string in a decoded JSON document, keys included."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def results_text(raw: str) -> str:
    """The results file as written, and its decoded strings, so a value that JSON escapes is
    found as well. A file that is not JSON is scanned as written."""
    try:
        decoded = json.loads(raw)
    except ValueError:
        return raw
    return raw + "\n" + "\n".join(_strings(decoded))


def found_in(values: Sequence[str], text: str) -> int:
    """How many of ``values`` appear in ``text``. The values are never returned."""
    return sum(1 for value in values if value and value in text)


@dataclass(frozen=True)
class Scan:
    found_in_log: int
    found_in_results: int
    results_present: bool
    suite_clean: bool

    def passed(self) -> bool:
        return self.found_in_log == 0 and self.found_in_results == 0 and self.suite_clean


def scan(directory: Path, log: Path, results: Path) -> Scan:
    values = job_values(directory)
    try:
        log_text = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        raise ScanError("the suite's log could not be read") from None
    present = results.exists()
    found_results = 0
    if present:
        try:
            raw = results.read_text(encoding="utf-8", errors="replace")
        except OSError:
            raise ScanError("the suite's results JSON could not be read") from None
        found_results = found_in(values, results_text(raw))
    return Scan(found_in(values, log_text), found_results, present, SUITE_CLEAN in log_text)


def withhold(results: Path) -> bool:
    """Removes the results JSON after a refusal. True if a file was removed."""
    try:
        results.unlink()
    except FileNotFoundError:
        return False
    return True


def main(argv: Sequence[str]) -> int:
    if len(argv) != 3:
        print("usage: python -m glow_ordering_proof.identity_scan <directory> <log> <results>")
        return 2
    directory, log, results = (Path(arg) for arg in argv)
    try:
        outcome = scan(directory, log, results)
    except ScanError as error:
        print(f"the job's secret check could not run: {error}")
        removed = withhold(results)
        print(f"the results JSON {'was removed' if removed else 'is absent'}; nothing to upload")
        return REFUSED
    print(f"the job's secrets found in the identity suite's output: {outcome.found_in_log}")
    if outcome.results_present:
        print(f"the job's secrets found in the identity results JSON: {outcome.found_in_results}")
    else:
        print("the identity results JSON is absent: nothing to scan or upload")
    print(f"the suite's own scan reported clean: {outcome.suite_clean}")
    if outcome.passed():
        return PASSED
    removed = withhold(results)
    print(f"the results JSON {'was removed' if removed else 'is absent'}; nothing to upload")
    return REFUSED


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
