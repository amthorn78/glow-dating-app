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
        self.assertEqual(complete["cases"], 132)  # 114 at I2a, plus the 18 I2b cases
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
        self.assertTrue(self.plan["all_fit"], (self.plan["fits"], self.plan["i2b_fits"]))
        complete, reserve, caps = self.plan["complete_set"], self.plan["reserve"], self.plan["caps"]
        self.assertLessEqual(complete["users"] + reserve["users"], caps["users"])
        self.assertLessEqual(complete["channels"] + reserve["channels"], caps["channels"])

    def test_the_i2b_plan(self) -> None:
        """P06.1-I2b (its prompt, section 5; DM-05 finding 6): run 1, run V1, run V2 and
        the largest of them in reserve fit the session caps."""
        runs = self.plan["i2b_runs"]
        self.assertEqual(sorted(runs), ["run_1", "run_V1", "run_V2"])
        run_1 = runs["run_1"]
        self.assertEqual(run_1["cases"], len(load_script().matrix.RUN_1_CASES))
        self.assertEqual((run_1["users"], run_1["channels"]), (7, 4))
        for name in ("run_V1", "run_V2"):
            # The lean setup: users A and B, no channel, two connections.
            self.assertEqual(runs[name]["cases"], 18)
            self.assertEqual(
                (runs[name]["users"], runs[name]["channels"], runs[name]["peak_connections"]),
                (2, 0, 2),
            )
            self.assertEqual((runs[name]["problems"], runs[name]["harness_errors"]), ([], []))
        self.assertEqual(self.plan["i2b_largest_run"]["users"], 7)
        self.assertEqual(self.plan["i2b_total_with_reserve"], {"users": 18, "channels": 8})
        self.assertTrue(all(self.plan["i2b_fits"].values()), self.plan["i2b_fits"])

    def test_one_set_is_counted_on_its_own(self) -> None:
        script = load_script()
        only = script.measure({"VD-create", "FD-feed"})
        self.assertEqual((only["users"], only["channels"], only["cases"]), (2, 0, 2))
        mixed = script.measure({"VD-create", "S1"})
        self.assertEqual((mixed["users"], mixed["channels"]), (4, 2))  # not lean


if __name__ == "__main__":
    unittest.main()
