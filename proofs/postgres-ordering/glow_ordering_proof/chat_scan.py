"""The job's secret check of the chat suite's output (SV4 A2; its brief's D2 and D10), as
``discovery_scan`` is for the discovery suite.

The chat suite's own job, "Database proof checks (chat)", runs it after the chat suite::

    python -m glow_ordering_proof.chat_scan <directory> <log> <results JSON>

``<directory>`` is the job's protected temporary directory. The check reads every secret value the
job holds there, from every secret file the job writes and no other (D2): the chat settings'
``SECRET_KEY`` and JWT signing key, the chat database's marker, the decoy database's marker (in
``discovery-marker``; DM-96 AG1), the PostgreSQL superuser's password and every password in the
passfile. Since SV4 B1 (its brief's D29; DM-101, section 11) it also holds the suite's synthetic
push tokens, which the suite derives from that ``SECRET_KEY`` (``push_tokens``) and registers
through F12's device route: so the job writes no file for them, and a token that reached the log
or the results JSON is found here too. It looks for each value in the suite's log and in its
results JSON, and it reads the suite's own result line for each of its scans (its secrets and its
member values), which must say clean with 0 found. It passes only when no value is found in either
file and the suite reported both scans clean. On a refusal it removes the results JSON, so nothing
is left to upload. It prints counts and file names only, never a value or a line of either file,
and imports nothing outside the standard library and ``identity_scan``.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from glow_ordering_proof.identity_scan import ScanError, found_in, results_text, withhold

VALUE_FILES = (
    "chat-secret-key",
    "chat-marker",
    "discovery-marker",
    "superuser-password",
)
PASSFILE = "passfile"
KEY_FILES = ("chat-jwt-key.pem",)
SUITE_CLEAN = ("chat secret scan: clean", "chat value scan: clean")
# The suite's own result lines, each read as a whole line: exactly one line for each scan, at the
# start of its line, clean, with 0 found. The word "clean" elsewhere in the log counts for nothing.
SUITE_RESULT_LINES = (
    (
        "chat secret scan: ",
        re.compile(
            r"chat secret scan: clean \(\d+ secrets held; 0 found in \d+ log records,"
            r" \d+ writes and the results JSON\)"
        ),
    ),
    (
        "chat value scan: ",
        re.compile(
            r"chat value scan: clean \(\d+ member values held: [a-z ,]+;"
            r" 0 found in the same output\)"
        ),
    ),
)


def suite_reported_clean(log_text: str) -> bool:
    """Whether the suite's own result line for each scan, and only that line, says clean."""
    lines = log_text.splitlines()
    for prefix, clean in SUITE_RESULT_LINES:
        own = [line for line in lines if line.startswith(prefix)]
        if len(own) != 1 or clean.fullmatch(own[0]) is None:
            return False
    return True


PASSED = 0
REFUSED = 3

# SV4 B1 (its brief's D29; DM-101, section 11): the suite's synthetic push tokens, a pool derived
# from the run's SECRET_KEY, so the suite and this check hold the same tokens with no file of their
# own. The pool bounds the tokens one run can register; the suite refuses a token past it.
SECRET_KEY_FILE = "chat-secret-key"
PUSH_TOKEN_LABEL = "glow-ordering-proof.chat.push-token"
PUSH_TOKEN_POOL = 160


def push_tokens(secret_key: str, count: int = PUSH_TOKEN_POOL) -> list[str]:
    """The run's synthetic push tokens: each the HMAC-SHA256 of its index under the run's
    ``SECRET_KEY``, so no one without the key can tell one. Test data, never a device's."""
    key = secret_key.encode("utf-8")
    return [
        "synthetic-push-token-"
        + hmac.new(key, f"{PUSH_TOKEN_LABEL}:{index}".encode("ascii"), hashlib.sha256).hexdigest()
        for index in range(count)
    ]


def job_values(directory: Path) -> list[str]:
    values: list[str] = []
    try:
        for name in VALUE_FILES:
            values.append((directory / name).read_text(encoding="ascii").strip())
        # The push tokens, from the SECRET_KEY the job wrote (D29, B1).
        values += push_tokens(values[VALUE_FILES.index(SECRET_KEY_FILE)])
        for line in (directory / PASSFILE).read_text(encoding="ascii").splitlines():
            if line.strip():
                values.append(line.rsplit(":", 1)[1])
        for name in KEY_FILES:
            pem = (directory / name).read_text(encoding="ascii")
            values += [line for line in pem.splitlines() if line and not line.startswith("-----")]
    except (OSError, UnicodeDecodeError, IndexError):
        raise ScanError("a secret file of the job's directory could not be read") from None
    return [value for value in values if value]


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
    clean = suite_reported_clean(log_text)
    return Scan(found_in(values, log_text), found_results, present, clean)


def main(argv: Sequence[str]) -> int:
    if len(argv) != 3:
        print("usage: python -m glow_ordering_proof.chat_scan <directory> <log> <results>")
        return 2
    directory, log, results = (Path(arg) for arg in argv)
    try:
        outcome = scan(directory, log, results)
    except ScanError as error:
        print(f"the job's secret check could not run: {error}")
        removed = withhold(results)
        print(f"the results JSON {'was removed' if removed else 'is absent'}; nothing to upload")
        return REFUSED
    print(f"the job's secrets found in the chat suite's output: {outcome.found_in_log}")
    if outcome.results_present:
        print(f"the job's secrets found in the chat results JSON: {outcome.found_in_results}")
    else:
        print("the chat results JSON is absent: nothing to scan or upload")
    print(f"the suite's own scans (secrets, member values) reported clean: {outcome.suite_clean}")
    if outcome.passed():
        return PASSED
    removed = withhold(results)
    print(f"the results JSON {'was removed' if removed else 'is absent'}; nothing to upload")
    return REFUSED


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
