"""Every command that uses the proof's settings runs the marker check first, and a wrong
or missing comment ends it with a non-zero status (DM-10 2.2), shown without a database.

Each command runs in a clean subprocess through ``tests/command_harness.py``: Django's
real connection path, the receiver the real settings register, and a fake server.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from glow_ordering_proof import environment, marker
from tests.test_settings_refusals import GOOD

PACKAGE = Path(__file__).resolve().parents[1]
MARKER_VALUE = GOOD[environment.MARKER]
EXPECTED = environment.MARKER_COMMENT_PREFIX + MARKER_VALUE

COMMANDS: dict[str, list[str]] = {
    "migrate": ["migrate", "--verbosity", "1"],
    "makemigrations --check --dry-run": ["makemigrations", "--check", "--dry-run"],
    "facts": ["proof", "facts"],
    "run": ["proof", "run", "--seed", "1"],
}


def run_command(argv: list[str], row: tuple[Any, ...] | None) -> tuple[int, str, dict[str, Any]]:
    with tempfile.TemporaryDirectory() as tmp:
        record = Path(tmp) / "record.json"
        environ = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": tmp,
            "LANG": "C.UTF-8",
            **GOOD,
            "DJANGO_SETTINGS_MODULE": "glow_ordering_proof.settings",
            "HARNESS_ROW": json.dumps(None if row is None else list(row)),
            "HARNESS_RECORD": str(record),
        }
        completed = subprocess.run(
            [sys.executable, "-m", "tests.command_harness", *argv],
            cwd=PACKAGE,
            env=environ,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        output = completed.stdout + completed.stderr
        if not record.exists():
            raise AssertionError(f"the harness wrote no record:\n{output}")
        return completed.returncode, output, json.loads(record.read_text(encoding="utf-8"))


class CommandRefusalTests(unittest.TestCase):
    def test_each_command_refuses_a_wrong_comment_before_any_other_statement(self) -> None:
        other = environment.MARKER_COMMENT_PREFIX + secrets.token_hex(16)
        rows: dict[str, tuple[Any, ...] | None] = {
            "a different marker": (4242, other),
            "the bare prefix": (4242, environment.MARKER_COMMENT_PREFIX),
            "something after": (4242, EXPECTED + " "),
            "a null comment": (4242, None),
            "no row": None,
        }
        for command, argv in COMMANDS.items():
            for label, row in rows.items():
                with self.subTest(command=command, comment=label):
                    status, output, record = run_command(argv, row)
                    self.assertNotEqual(status, 0, output)
                    self.assertIn(marker.REFUSAL, output)
                    self.assertIn("RefusedDatabase", output)
                    self.assertIn(environment.MARKER, output)
                    self.assertNotIn(MARKER_VALUE, output)
                    self.assertNotIn(other, output)
                    self.assertNotIn("HarnessStop", output)
                    # The check was the connection's only statement, and the connection
                    # was closed through Django and not kept.
                    self.assertEqual(record["statements"], [marker.QUERY])
                    self.assertGreaterEqual(record["closed"], 1)
                    self.assertFalse(record["kept"])

    def test_each_command_passes_a_matching_comment_and_goes_on(self) -> None:
        for command, argv in COMMANDS.items():
            with self.subTest(command=command):
                status, output, record = run_command(argv, (4242, EXPECTED))
                # The command passed the check and reached its own first statement, where
                # the fake server stops it.
                self.assertNotEqual(status, 0, output)
                self.assertIn("HarnessStop", output)
                self.assertNotIn(marker.REFUSAL, output)
                self.assertIn("database marker verified on a new connection", output)
                self.assertNotIn(MARKER_VALUE, output)
                self.assertEqual(record["statements"][0], marker.QUERY)
                self.assertGreaterEqual(len(record["statements"]), 2)
                self.assertNotEqual(record["statements"][1], marker.QUERY)


class DbshellRefusalTests(unittest.TestCase):
    """P06.DB's carried item 6 (DM-12): dbshell under the proof's settings refuses with
    the marker's refusal, opening no connection and starting no client, whatever the
    database's comment."""

    def test_dbshell_is_refused_before_any_connection(self) -> None:
        other = environment.MARKER_COMMENT_PREFIX + secrets.token_hex(16)
        rows: dict[str, tuple[Any, ...] | None] = {
            "the run's marker": (4242, EXPECTED),
            "a different marker": (4242, other),
            "no row": None,
        }
        for label, row in rows.items():
            for argv in (["dbshell"], ["dbshell", "--", "-c", "SELECT 1"]):
                with self.subTest(comment=label, argv=argv):
                    status, output, record = run_command(argv, row)
                    self.assertNotEqual(status, 0, output)
                    self.assertIn("RefusedDatabase", output)
                    self.assertIn(marker.DBSHELL_REFUSAL, output)
                    self.assertIn(environment.MARKER, output)
                    self.assertNotIn(MARKER_VALUE, output)
                    self.assertEqual(record["statements"], [])
                    self.assertFalse(record["shell_started"])
                    self.assertFalse(record["kept"])

    def test_the_proof_provides_the_dbshell_command(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "import django; django.setup();"
                " from django.core.management import get_commands;"
                " print(get_commands()['dbshell'])",
            ],
            cwd=PACKAGE,
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "LANG": "C.UTF-8",
                **GOOD,
                "DJANGO_SETTINGS_MODULE": "glow_ordering_proof.settings",
            },
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "glow_ordering_proof")


if __name__ == "__main__":
    unittest.main()
