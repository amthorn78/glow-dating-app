"""The forced cases' wait observation, offline (P06.DB-C1, the exact-head review's F4):
a wait counts as observed only when ``pg_blocking_pids`` names the holder's backend."""

import unittest
from typing import Any
from unittest import mock

from glow_ordering_proof import observe
from tests.fakes import FakeConnection, ScriptedCursor

ARRIVER = 101
HOLDER = 100
OTHER = 222


class DecisionTests(unittest.TestCase):
    def test_a_wait_on_the_holder_is_observed(self) -> None:
        self.assertTrue(observe.waits_on_holder("Lock", (HOLDER,), HOLDER))
        self.assertTrue(observe.waits_on_holder("Lock", (OTHER, HOLDER), HOLDER))

    def test_a_wait_whose_blockers_do_not_include_the_holder_is_not_observed(self) -> None:
        self.assertFalse(observe.waits_on_holder("Lock", (OTHER,), HOLDER))
        self.assertFalse(observe.waits_on_holder("Lock", (), HOLDER))

    def test_no_lock_wait_is_not_observed(self) -> None:
        self.assertFalse(observe.waits_on_holder(None, (HOLDER,), HOLDER))
        self.assertFalse(observe.waits_on_holder("LWLock", (HOLDER,), HOLDER))


def answer(blockers: tuple[int, ...]) -> Any:
    def reply(sql: str, params: list[object]) -> tuple[Any, ...] | None:
        if "pg_stat_activity" in sql:
            return ("Lock", "transactionid", list(blockers))
        if "pg_locks" in sql:
            return ("transactionid", "ShareLock")
        return None

    return reply


class ObservationTests(unittest.TestCase):
    def observe(self, blockers: tuple[int, ...], polls_until_done: int) -> observe.ObservedWait:
        cursor = ScriptedCursor(answer(blockers))
        calls = {"n": 0}

        def finished() -> bool:
            calls["n"] += 1
            return calls["n"] >= polls_until_done

        with (
            mock.patch.object(observe, "connection", FakeConnection(cursor)),
            mock.patch("glow_ordering_proof.observe.time.sleep", lambda _: None),
        ):
            return observe.observe_lock_wait(ARRIVER, holder_pid=HOLDER, finished=finished)

    def test_blocked_by_the_holder(self) -> None:
        seen = self.observe((HOLDER,), 5)
        self.assertTrue(seen.observed)
        self.assertEqual(seen.blocking_pids, (HOLDER,))
        self.assertEqual(seen.holder_pid, HOLDER)
        self.assertIn(f"pg_blocking_pids=[{HOLDER}] (holder pid {HOLDER})", seen.summary())

    def test_blocked_by_another_backend_is_not_observed(self) -> None:
        seen = self.observe((OTHER,), 3)
        self.assertFalse(seen.observed)
        self.assertEqual(seen.blocking_pids, (OTHER,))
        self.assertIn("not by the holder", seen.summary())


if __name__ == "__main__":
    unittest.main()
