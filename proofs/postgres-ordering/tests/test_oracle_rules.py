"""The commit-order oracle's rules on constructed rows, offline: the oracle's fetches
are replaced, so no database is opened (P06.DB-C1, the exact-head review's F2)."""

import unittest
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest import mock
from uuid import UUID, uuid4

from glow_ordering_proof import oracle
from tests.fakes import FakeConnection

T0 = datetime(2026, 9, 29, 4, 18, 0, tzinfo=UTC)


def ms(n: float) -> datetime:
    return T0 + timedelta(milliseconds=n)


class World:
    def __init__(self) -> None:
        self.low, self.high = sorted((uuid4(), uuid4()))
        self.match = uuid4()
        self.session = uuid4()
        self.other_session = uuid4()
        self.sessions: list[tuple[Any, ...]] = [
            (self.session, self.low, 1, ms(60_000)),
            (self.other_session, self.high, 1, ms(60_000)),
        ]

    def submission(
        self,
        committed: float,
        *,
        version: int = 1,
        key: str | None = None,
        epoch: int = 1,
        log_rows: int = 1,
        log_committed: float | None = None,
        session: UUID | None = None,
    ) -> tuple[Any, ...]:
        return (
            uuid4(),
            self.low,
            version,
            key or f"k-{uuid4().hex}",
            self.match,
            self.low,
            self.high,
            ms(committed),
            log_rows,
            ms(committed if log_committed is None else log_committed),
            session or self.session,
            epoch,
            "design:stress",
            "race.block_by_high",
            1,
        )

    def revocation(
        self,
        kind: str,
        committed: float,
        *,
        version: int | None = None,
        actor: UUID | None = None,
        session: UUID | None = None,
    ) -> tuple[Any, ...]:
        match = self.match if kind in ("block", "unmatch") else None
        return (kind, match, actor, session, version, ms(committed))


def run(
    world: World, submissions: list[tuple[Any, ...]], revocations: list[tuple[Any, ...]]
) -> oracle.OracleReport:
    """``oracle.evaluate`` for one run tag, with its fetches answered from constructed
    rows: the submissions, the revocations, the sessions and no other writer."""
    answers = iter([submissions, revocations, world.sessions, []])

    def fetch(cursor: Any, sql: str, params: list[object] | None = None) -> list[Any]:
        return list(next(answers))

    with (
        mock.patch.object(oracle, "_fetch", fetch),
        mock.patch.object(oracle, "connection", FakeConnection(object())),
    ):
        return oracle.evaluate(run_tag="design:stress", case_id="race.block_by_high")


def rules(report: oracle.OracleReport) -> list[str]:
    return sorted(v.rule for v in report.violations)


class O2Tests(unittest.TestCase):
    def test_a_send_at_the_new_version_after_the_block_is_a_violation(self) -> None:
        # The review's F2: the send stored the version the block set (v2) and committed
        # after it. The old rule compared versions and saw nothing.
        world = World()
        report = run(
            world,
            [world.submission(10, version=2)],
            [world.revocation("block", 5, version=2, actor=world.high)],
        )
        self.assertIn("O2", rules(report))

    def test_the_same_send_committed_before_the_block_is_not(self) -> None:
        world = World()
        report = run(
            world,
            [world.submission(5, version=1)],
            [world.revocation("block", 10, version=2, actor=world.high)],
        )
        self.assertEqual(rules(report), [])
        report = run(
            world,
            [world.submission(5, version=2)],
            [world.revocation("block", 10, version=2, actor=world.high)],
        )
        self.assertNotIn("O2", rules(report))

    def test_an_unmatch_at_any_version_before_the_send(self) -> None:
        world = World()
        report = run(
            world,
            [world.submission(10, version=3)],
            [world.revocation("unmatch", 5, version=2, actor=world.low)],
        )
        self.assertIn("O2", rules(report))

    def test_equal_commit_timestamps_are_a_violation(self) -> None:
        world = World()
        report = run(
            world,
            [world.submission(5, version=2)],
            [world.revocation("block", 5, version=2, actor=world.high)],
        )
        self.assertIn("O2", rules(report))

    def test_a_block_without_a_contact_version_is_not_a_contact_revocation(self) -> None:
        # A block of a match that is no longer active changes no contact version.
        world = World()
        report = run(
            world,
            [world.submission(10, version=1)],
            [world.revocation("block", 5, version=None, actor=world.high)],
        )
        self.assertEqual(rules(report), [])

    def test_another_match_is_not_this_match(self) -> None:
        world = World()
        other = World()
        report = run(
            world,
            [world.submission(10, version=1)],
            [other.revocation("block", 5, version=2, actor=other.high)],
        )
        self.assertEqual(rules(report), [])


class ExistingRulesTests(unittest.TestCase):
    """The rules still flag what they flagged before the correction."""

    def test_the_design_row_is_clean(self) -> None:
        world = World()
        self.assertEqual(rules(run(world, [world.submission(5)], [])), [])

    def test_o1(self) -> None:
        world = World()
        self.assertEqual(rules(run(world, [world.submission(5, log_rows=0)], [])), ["O1"])
        self.assertEqual(rules(run(world, [world.submission(5, log_committed=6)], [])), ["O1"])

    def test_o2_the_old_case(self) -> None:
        world = World()
        report = run(
            world,
            [world.submission(10, version=1)],
            [world.revocation("block", 5, version=2, actor=world.high)],
        )
        self.assertEqual(rules(report), ["O2", "O6"])

    def test_o3(self) -> None:
        world = World()
        for kind in ("sign_out", "expire"):
            report = run(
                world,
                [world.submission(10)],
                [world.revocation(kind, 5, session=world.session)],
            )
            self.assertEqual(rules(report), ["O3"], kind)
        report = run(
            world,
            [world.submission(10)],
            [world.revocation("sign_out", 5, session=world.other_session)],
        )
        self.assertEqual(rules(report), [])

    def test_o4(self) -> None:
        world = World()
        report = run(
            world, [world.submission(10)], [world.revocation("suspend", 5, actor=world.high)]
        )
        self.assertEqual(rules(report), ["O4"])
        # The actor's own suspension also makes its epoch stale (O7).
        report = run(
            world, [world.submission(10)], [world.revocation("delete", 5, actor=world.low)]
        )
        self.assertEqual(rules(report), ["O4", "O7"])
        report = run(
            world, [world.submission(5)], [world.revocation("suspend", 10, actor=world.high)]
        )
        self.assertEqual(rules(report), [])

    def test_o5(self) -> None:
        # Narrowed in P06.2 (CX2): a commit at or after the expiry alone is not a
        # violation; tests/test_oracle_p06_2.py shows what is.
        world = World()
        self.assertEqual(rules(run(world, [world.submission(60_000)], [])), [])
        report = run(world, [world.submission(5, session=uuid4())], [])
        self.assertIn("O5", rules(report))

    def test_o6(self) -> None:
        world = World()
        self.assertEqual(rules(run(world, [world.submission(5, version=2)], [])), ["O6"])

    def test_o7(self) -> None:
        world = World()
        self.assertEqual(rules(run(world, [world.submission(5, epoch=2)], [])), ["O7"])

    def test_o8(self) -> None:
        world = World()
        report = run(world, [world.submission(5, key="k1"), world.submission(6, key="k1")], [])
        self.assertEqual(rules(report), ["O8"])


if __name__ == "__main__":
    unittest.main()
