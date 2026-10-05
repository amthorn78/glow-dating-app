"""The stress budget's floors are fixed in code (item 6.3)."""

import unittest

from glow_ordering_proof import budget


class BudgetTests(unittest.TestCase):
    def test_caps_and_floors(self) -> None:
        self.assertEqual(budget.MAX_ITERATIONS, 200)
        self.assertEqual(budget.MAX_SECONDS, 30.0)
        self.assertEqual(budget.MIN_ITERATIONS, 50)
        self.assertEqual(budget.MIN_OVERLAPS, 10)
        self.assertGreaterEqual(budget.MAX_ITERATIONS, budget.MIN_ITERATIONS)

    def test_floors(self) -> None:
        self.assertTrue(budget.floors_met(50, 10))
        self.assertTrue(budget.floors_met(200, 200))
        self.assertFalse(budget.floors_met(49, 10))
        self.assertFalse(budget.floors_met(50, 9))
        self.assertFalse(budget.floors_met(0, 0))

    def test_whole_database_step_fits_the_job(self) -> None:
        # Twelve design races and two stress controls at the wall-clock cap, plus the
        # forced cases and the forced controls, stay well under the job's 20 minutes.
        from glow_ordering_proof import controls, stress

        stress_controls = sum(c.mode == "stress" for c in controls.CONTROLS)
        worst = (len(stress.RACES) + stress_controls) * budget.MAX_SECONDS
        self.assertLess(worst, 12 * 60)


if __name__ == "__main__":
    unittest.main()
