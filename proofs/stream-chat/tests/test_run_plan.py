"""P06.1-I2a's run plan (checks/run_plan.py): the complete set, counted offline, fits the
session's caps with one rerun of the largest case family in reserve.

The numbers are pinned, so a change that makes the set larger is seen here first.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any

import tests  # noqa: F401

SCRIPT = Path(__file__).resolve().parent.parent / "checks" / "run_plan.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_plan", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunPlanTest(unittest.TestCase):
    plan: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        # Without a usage ledger: the count is the plan's own.
        cls.plan = load_script().plan(ledger=None)

    def test_the_complete_set_runs_every_case_cleanly(self) -> None:
        complete = self.plan["complete_set"]
        self.assertEqual(complete["cases"], 114)
        self.assertEqual(complete["problems"], [])
        self.assertEqual(complete["harness_errors"], [])

    def test_the_count(self) -> None:
        complete = self.plan["complete_set"]
        self.assertEqual(
            {k: complete[k] for k in ("users", "channels", "peak_connections")},
            {"users": 11, "channels": 18, "peak_connections": 6},
        )
        base = self.plan["base_setup"]
        self.assertEqual((base["users"], base["channels"], base["cases"]), (4, 2, 0))
        self.assertEqual(self.plan["reserve"], {"users": 7, "channels": 8, "peak_connections": 5})

    def test_what_the_session_already_used_is_counted(self) -> None:
        # The independent review, a nit: the caps are per session, and the checkout's
        # ledger holds what earlier live commands used.
        script = load_script()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "usage-ledger.json"
            ledger.write_text(json.dumps({"session": {"users": 5, "api_calls": 10}}))
            self.assertEqual(
                script.session_used(ledger), {"users": 5, "channels": 0, "api_calls": 10}
            )
            planned = script.plan(ledger=ledger)
        self.assertEqual(planned["session_used_before"]["users"], 5)
        self.assertFalse(planned["fits"]["users"])  # 5 + 11 + 7 > 20
        self.assertFalse(planned["all_fit"])

    def test_it_fits_with_one_rerun_in_reserve(self) -> None:
        self.assertTrue(self.plan["all_fit"], self.plan["fits"])
        complete, reserve, caps = self.plan["complete_set"], self.plan["reserve"], self.plan["caps"]
        self.assertLessEqual(complete["users"] + reserve["users"], caps["users"])
        self.assertLessEqual(complete["channels"] + reserve["channels"], caps["channels"])


if __name__ == "__main__":
    unittest.main()
