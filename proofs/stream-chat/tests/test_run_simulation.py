"""Drive a whole proof run against fakes: no network, no Stream, no Node.

This does not test Stream. It checks that the orchestration reaches every
case, records a result for each, never reports a harness error, restores every
temporary change, cleans up and ends with a configuration check.
"""

import unittest

import tests  # noqa: F401
from glow_stream_proof import matrix
from tests.fakes import PREFIX, NoSettle, make_run


class SimulationTest(unittest.TestCase):
    def test_full_orchestration_against_fakes(self) -> None:
        run, server = make_run()
        with NoSettle():
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

    def test_guest_reach_is_not_run_when_the_guest_connect_is_refused(self) -> None:
        """Finding 6: as in the live lockdown, setGuestUser's connect is refused.

        G1's control creates the guest (POST /guest 201), but its connect gets
        403 / 17, so there is no guest session and every G2 case is "not run".
        """
        run, _server = make_run()
        with NoSettle():
            run.setup()
            run.authorized_path()
            run.run_matrix({"G1-create", "G2-read-ab", "G2-channels", "G2-users", "G2-message"})
        cases = {c.case_id: c for c in run.case_results}
        self.assertIn("POST /guest 201", cases["G1-create"].control)
        self.assertIn("guest connect 403 / code 17", cases["G1-create"].control)
        self.assertNotIn("guest", run.sessions)
        for suffix in ("read-ab", "channels", "users", "message"):
            case = cases[f"G2-{suffix}"]
            self.assertEqual(case.observed, "not run: no guest session")
            self.assertEqual(case.verdict, matrix.INCONCLUSIVE)


if __name__ == "__main__":
    unittest.main()
