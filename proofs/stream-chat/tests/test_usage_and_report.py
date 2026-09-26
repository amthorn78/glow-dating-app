import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import tests  # noqa: F401
from glow_stream_proof import report
from glow_stream_proof.usage import GuardrailStop, Limits, UsageLedger, charge_signal


class UsageTest(unittest.TestCase):
    def test_stops_before_passing(self) -> None:
        ledger = UsageLedger(limits=Limits(users=3, channels=2, connections=1, api_calls=5))
        ledger.reserve("users", 3)
        with self.assertRaises(GuardrailStop):
            ledger.reserve("users")
        self.assertEqual(ledger.run.users, 3)
        ledger.reserve("api_calls", 5, source="client")
        with self.assertRaises(GuardrailStop):
            ledger.reserve("api_calls")
        self.assertEqual(ledger.run.client_api_calls, 5)
        ledger.connection_opened()
        with self.assertRaises(GuardrailStop):
            ledger.connection_opened()
        ledger.connection_closed()
        ledger.connection_opened()
        self.assertEqual(ledger.run.peak_connections, 1)

    def test_session_totals_persist_across_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
            first = UsageLedger.load(path, Limits(users=5, channels=5, connections=5, api_calls=5))
            first.reserve("users", 4)
            second = UsageLedger.load(path, Limits(users=5, channels=5, connections=5, api_calls=5))
            self.assertEqual(second.run.users, 0)
            self.assertEqual(second.session.users, 4)
            with self.assertRaises(GuardrailStop):
                second.reserve("users", 2)
            self.assertEqual(second.remaining("users"), 1)

    def test_an_interrupted_save_leaves_the_previous_ledger_whole(self) -> None:
        # P06.1-C3, the C2 review's nit 9: the ledger is written through a temporary
        # file, like every .work file, so a save interrupted mid-write loses nothing.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage-ledger.json"
            ledger = UsageLedger.load(path)
            ledger.reserve("users")
            real_write = Path.write_text

            def interrupted(target: Path, data: str, *args: Any, **kwargs: Any) -> int:
                real_write(target, "", *args, **kwargs)  # opened and truncated, then stopped
                raise KeyboardInterrupt

            with (
                mock.patch.object(Path, "write_text", interrupted),
                self.assertRaises(KeyboardInterrupt),
            ):
                ledger.reserve("users")
            self.assertEqual(UsageLedger.load(path).session.users, 1)

    def test_unknown_kind(self) -> None:
        with self.assertRaises(ValueError):
            UsageLedger().reserve("dollars")

    def test_charge_signal(self) -> None:
        self.assertIsNone(charge_signal(403, 17, "ReadChannel failed"))
        self.assertIsNone(charge_signal(200, None, None))
        self.assertIsNotNone(charge_signal(429, 9, "Too many requests"))
        self.assertIsNotNone(charge_signal(402, None, None))
        self.assertIsNotNone(charge_signal(403, 99, "app suspended"))
        self.assertIsNotNone(charge_signal(400, 4, "please upgrade your plan"))
        self.assertIsNotNone(charge_signal(400, 4, "monthly quota exceeded"))


class ReportTest(unittest.TestCase):
    def test_table_escapes_pipes_and_newlines(self) -> None:
        out = report.table(("a", "b"), [("x|y", "line1\nline2"), (None, "")])
        self.assertIn("x\\|y", out)
        self.assertIn("line1 line2", out)
        self.assertIn("| - | - |", out)

    def test_verdict_counts(self) -> None:
        cases = [{"verdict": "HOLDS"}, {"verdict": "HOLDS"}, {"verdict": "FAIL"}]
        self.assertEqual(report.verdict_counts(cases), {"FAIL": 1, "HOLDS": 2})


if __name__ == "__main__":
    unittest.main()
