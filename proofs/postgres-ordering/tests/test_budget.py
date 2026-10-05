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
        # P06.2 (DM-13 2.2): both subjects keep the budget. The reference design's twelve
        # races and two stress controls, and the adapter's twelve races and three D5
        # races, all at the wall-clock cap, take 14.5 minutes; the forced cases, the
        # controls and the delivery phase have the rest of the job's 20 minutes. A
        # measured run is far below the cap (C2's twelve races took 4 to 7 s each).
        from glow_ordering_proof import controls, stress

        stress_controls = sum(c.mode == "stress" for c in controls.CONTROLS)
        races = len(stress.races()) + stress_controls + len(stress.races(d5=True))
        self.assertEqual(races, 12 + 2 + 15)
        self.assertLess(races * budget.MAX_SECONDS, 15 * 60)


if __name__ == "__main__":
    unittest.main()
