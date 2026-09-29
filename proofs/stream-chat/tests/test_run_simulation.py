"""Drive a whole proof run against fakes: no network, no Stream, no Node.

This does not test Stream. It checks that the orchestration reaches every
case, records a result for each, never reports a harness error, restores every
temporary change, cleans up and ends with a configuration check.
"""

import unittest

import tests  # noqa: F401
from glow_stream_proof import matrix
from tests.fake_world import FakeClock
from tests.fakes import PREFIX, NoSettle, make_run


class SimulationTest(unittest.TestCase):
    def test_full_orchestration_against_fakes(self) -> None:
        run, server = make_run()
        with NoSettle(), FakeClock():
            run.setup()
            run.authorized_path()
            run.run_matrix()
            problems = run.finish(cleanup=True)
        results = run.results()
        self.assertEqual(len(results["cases"]), len(matrix.all_cases()))
        errors = [c["case_id"] for c in results["cases"] if "harness error" in c["observed"]]
        self.assertEqual(errors, [])
        self.assertIn("AP11", {c["check_id"] for c in results["checks"]})
        self.assertIn("users_task", results["cleanup"])
        self.assertLessEqual(run.ledger.run.users, 20)
        self.assertTrue(run.ctx["guest_id"].startswith(f"guest-0000-{PREFIX}"))
        self.assertIn(run.ctx["guest_id"], run.users)
        self.assertEqual(run.journal, [])
        self.assertEqual(results["journal_not_restored"], [])
        self.assertEqual(problems, [])
        self.assertEqual(results["stops"], [])

    def test_guest_reach_runs_on_a_guest_created_server_side(self) -> None:
        """Finding 6, as P06.1-I2a sets G2 up.

        As in the live lockdown, setGuestUser's connect is refused: G1's control
        creates its guest (POST /guest 201), but its connect gets 403 / 17, so it has
        no session. G2 creates its own guest server-side instead (with guest creation
        enabled for that moment, journalled and disabled again) and connects it with
        its ID only.
        """
        run, server = make_run()
        with NoSettle():
            run.setup()
            run.authorized_path()
            run.run_matrix({"G1-create", "G2-read-ab", "G2-channels", "G2-users", "G2-message"})
        cases = {c.case_id: c for c in run.case_results}
        self.assertIn("POST /guest 201", cases["G1-create"].control)
        self.assertIn("guest connect 403 / code 17", cases["G1-create"].control)
        self.assertNotIn("guest", run.sessions)
        setup = run.g2_setup
        self.assertIsNotNone(setup, "G2's server-side setup was not made")
        assert setup is not None
        self.assertEqual(setup["server_create"], "403 / code 17")
        self.assertEqual(setup["with_guest_creation_enabled"]["server_create"], "201")
        self.assertIn("verified", setup["with_guest_creation_enabled"]["restored"])
        self.assertEqual(setup["connect"], "ok (succeeded)")
        self.assertEqual(setup["stored_form"], "guest-<id>-{prefix}-g2")
        guest = run.sessions["g2"]
        connects = [p for op, p in guest.sent if op == "connect"]  # type: ignore[attr-defined]
        self.assertEqual(connects, [{"max_calls": 3, "user": {"id": run.ctx["g2_id"]}}])
        self.assertIn(run.ctx["g2_id"], run.users)
        self.assertEqual(run.journal, [])
        self.assertIs(server.app["guest_user_creation_disabled"], True)
        for suffix in ("read-ab", "channels", "users", "message"):
            case = cases[f"G2-{suffix}"]
            self.assertNotIn("not run", case.observed, suffix)
            self.assertEqual(case.detail["g2_setup"]["connect"], "ok (succeeded)")


if __name__ == "__main__":
    unittest.main()
