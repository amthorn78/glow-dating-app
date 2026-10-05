"""The stress run's overlap measure, offline (P06.DB-C1, the exact-head review's F1).

Each race measures its own overlaps: its per-iteration reads select its own rows by
run tag, race (``case_id``) and iteration, and an iteration overlaps only when two of
its own writers' database intervals intersect."""

import unittest
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest import mock

from glow_ordering_proof import oracle, stress
from tests.fakes import FakeConnection, FilteringCursor

T0 = datetime(2026, 9, 29, 4, 18, 0, tzinfo=UTC)


def ms(n: float) -> datetime:
    return T0 + timedelta(milliseconds=n)


def row(run_tag: str, case_id: str, iteration: int, kind: str, start: float, end: float) -> Any:
    return {
        "run_tag": run_tag,
        "case_id": case_id,
        "iteration": iteration,
        "kind": kind,
        "start": ms(start),
        "end": ms(end),
    }


class OverlapDecisionTests(unittest.TestCase):
    def test_two_writer_race(self) -> None:
        self.assertTrue(
            stress._overlapped("revocation", [("send", ms(0), ms(5)), ("block", ms(2), ms(8))])
        )
        self.assertTrue(
            stress._overlapped(
                "revocation", [("send_attempt", ms(3), ms(9)), ("unmatch", ms(0), ms(4))]
            )
        )
        self.assertFalse(
            stress._overlapped("revocation", [("send", ms(0), ms(5)), ("block", ms(5), ms(8))])
        )
        self.assertFalse(
            stress._overlapped("revocation", [("send", ms(0), ms(2)), ("suspend", ms(3), ms(8))])
        )

    def test_the_duplicates_race_intersecting(self) -> None:
        # Both writers are sends: the first committed, the second replayed (an attempt row).
        intervals = [("send", ms(0), ms(6)), ("send_attempt", ms(1), ms(7))]
        self.assertTrue(stress._overlapped("duplicates", intervals))

    def test_the_duplicates_race_disjoint(self) -> None:
        intervals = [("send", ms(0), ms(3)), ("send_attempt", ms(4), ms(7))]
        self.assertFalse(stress._overlapped("duplicates", intervals))
        self.assertFalse(stress._overlapped("duplicates", [("send", ms(0), ms(3))]))

    def test_the_opposing_race(self) -> None:
        # The send's interval against any revocation's.
        self.assertTrue(
            stress._overlapped(
                "opposing",
                [
                    ("send_attempt", ms(0), ms(4)),
                    ("block", ms(5), ms(6)),
                    ("block", ms(7), ms(8)),
                    ("suspend", ms(3), ms(9)),
                ],
            )
        )
        # Revocations that overlap only each other do not count: the send is apart.
        self.assertFalse(
            stress._overlapped(
                "opposing",
                [
                    ("send_attempt", ms(0), ms(2)),
                    ("block", ms(3), ms(6)),
                    ("block", ms(4), ms(8)),
                    ("suspend", ms(5), ms(9)),
                ],
            )
        )

    def test_revocations_alone_never_overlap_a_two_writer_race(self) -> None:
        self.assertFalse(
            stress._overlapped("revocation", [("block", ms(0), ms(5)), ("block", ms(1), ms(6))])
        )


class PerRaceSelectionTests(unittest.TestCase):
    """Rows of two races at the same iteration count only for their own race."""

    ROWS = [
        # race.block_by_low, iteration 1: the send and the block overlap.
        row("design:stress", "race.block_by_low", 1, "send", 0, 5),
        row("design:stress", "race.block_by_low", 1, "block", 2, 8),
        row("design:stress", "race.block_by_low", 1, "sign_in", 0, 1),
        # race.block_by_high, iteration 1: disjoint.
        row("design:stress", "race.block_by_high", 1, "send_attempt", 20, 22),
        row("design:stress", "race.block_by_high", 1, "block", 23, 25),
        # race.racing_duplicates, iteration 1: disjoint sends.
        row("design:stress", "race.racing_duplicates", 1, "send", 40, 42),
        row("design:stress", "race.racing_duplicates", 1, "send_attempt", 43, 45),
        # race.racing_duplicates, iteration 2: intersecting sends.
        row("design:stress", "race.racing_duplicates", 2, "send", 60, 64),
        row("design:stress", "race.racing_duplicates", 2, "send_attempt", 61, 66),
        # Another run tag at the same race and iteration.
        row("control:no_locks.stress", "race.block_by_high", 1, "send", 100, 110),
        row("control:no_locks.stress", "race.block_by_high", 1, "block", 101, 105),
    ]

    def intervals(self, run_tag: str, race_id: str, iteration: int) -> list[Any]:
        cursor = FilteringCursor(self.ROWS, ("kind", "start", "end"))
        with mock.patch.object(stress, "connection", FakeConnection(cursor)):
            result = stress._intervals(run_tag, race_id, iteration)
        sql, params = cursor.executed[0]
        self.assertIn("case_id = %s", sql)
        self.assertIn(race_id, params)
        return result

    def overlapped(self, race_id: str, iteration: int) -> bool:
        race = stress.RACE_BY_ID[race_id]
        return stress._overlapped(race.kind, self.intervals("design:stress", race_id, iteration))

    def test_each_race_reads_only_its_own_rows(self) -> None:
        own = self.intervals("design:stress", "race.block_by_high", 1)
        self.assertEqual(sorted(k for k, _, _ in own), ["block", "send_attempt"])

    def test_an_earlier_race_does_not_lend_its_overlap(self) -> None:
        self.assertTrue(self.overlapped("race.block_by_low", 1))
        self.assertFalse(self.overlapped("race.block_by_high", 1))
        self.assertFalse(self.overlapped("race.racing_duplicates", 1))
        self.assertTrue(self.overlapped("race.racing_duplicates", 2))

    def test_the_per_iteration_oracle_check_names_the_race(self) -> None:
        captured: list[tuple[str, list[object]]] = []

        def fetch(cursor: Any, sql: str, params: list[object] | None = None) -> list[Any]:
            captured.append((sql, list(params or [])))
            return []

        with (
            mock.patch.object(oracle, "_fetch", fetch),
            mock.patch.object(oracle, "connection", FakeConnection(object())),
        ):
            oracle.evaluate(run_tag="design:stress", case_id="race.block_by_high", iteration=3)
        sql, params = captured[0]
        self.assertIn("l.case_id = %s", sql)
        # The reference design's rows only (its bindings' provider), then the filters.
        self.assertEqual(params, ["proof", "design:stress", "race.block_by_high", 3])


if __name__ == "__main__":
    unittest.main()
