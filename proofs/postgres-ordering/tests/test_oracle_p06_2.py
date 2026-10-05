"""The oracle's P06.2 rules on constructed rows, offline: O5 narrowed (CX2), O9 (CX1),
O10 (D5) and O0 (every revocation has its witness)."""

import unittest
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from glow_ordering_proof import oracle
from glow_ordering_proof.oracle import Census, RevocationRow, SubmissionRow, WriterRow

T0 = datetime(2026, 10, 5, 12, 0, 0, tzinfo=UTC)
EXPIRY = 1_000.0


def ms(n: float) -> datetime:
    return T0 + timedelta(milliseconds=n)


class World:
    def __init__(self) -> None:
        self.low, self.high = sorted((uuid4(), uuid4()))
        self.match = uuid4()
        self.session = uuid4()
        self.sessions: dict[UUID, tuple[UUID, int, datetime]] = {
            self.session: (self.low, 1, ms(EXPIRY))
        }

    def submission(
        self,
        committed: float,
        *,
        started: float | None = 0,
        actor: UUID | None = None,
        claims: int = 1,
    ) -> SubmissionRow:
        return SubmissionRow(
            uuid4(),
            actor or self.low,
            1,
            f"k-{uuid4().hex}",
            self.match,
            self.low,
            self.high,
            ms(committed),
            1,
            ms(committed),
            self.session,
            1,
            "design:forced",
            "c",
            None,
            None if started is None else ms(started),
            claims,
        )

    def consent(self, account: UUID, state: str, committed: float) -> RevocationRow:
        return RevocationRow(f"consent_{state}", None, account, None, 1, ms(committed))

    def accepted(self) -> list[RevocationRow]:
        return [self.consent(self.low, "accepted", -10), self.consent(self.high, "accepted", -10)]


def rules(report: oracle.OracleReport) -> list[str]:
    return sorted(v.rule for v in report.violations)


def judge(world: World, submissions: list[SubmissionRow], **kwargs: Any) -> list[str]:
    revocations = kwargs.pop("revocations", [])
    return rules(oracle.judge(submissions, revocations, world.sessions, **kwargs))


class NarrowedO5Tests(unittest.TestCase):
    """CX2 (the brief's D4, confirmed by DM-13): the design checks expiry at a time read
    after its locks, so a commit after the expiry is a violation only when the checks
    must have run after it."""

    def test_checked_before_and_committed_after_is_not_a_violation(self) -> None:
        world = World()
        # The forced boundary: began before the expiry, a delay, committed after it.
        self.assertEqual(judge(world, [world.submission(EXPIRY + 50, started=EXPIRY - 500)]), [])

    def test_began_after_the_expiry_is_a_violation(self) -> None:
        world = World()
        self.assertEqual(judge(world, [world.submission(EXPIRY + 50, started=EXPIRY + 10)]), ["O5"])

    def test_waited_past_the_expiry_on_a_writer_of_its_rows_is_a_violation(self) -> None:
        # The transaction_start_time control: the send began before the expiry, waited on
        # the other member's send, which committed after the expiry, then committed.
        world = World()
        holder = WriterRow("send", frozenset({world.match, world.low, world.high}), ms(EXPIRY + 20))
        submission = world.submission(EXPIRY + 40, started=EXPIRY - 500)
        self.assertEqual(judge(world, [submission], writers=[holder]), ["O5"])

    def test_a_writer_of_other_rows_or_ended_before_the_expiry_is_not(self) -> None:
        world = World()
        submission = world.submission(EXPIRY + 40, started=EXPIRY - 500)
        elsewhere = WriterRow("send", frozenset({uuid4()}), ms(EXPIRY + 20))
        before = WriterRow("block", frozenset({world.low}), ms(EXPIRY - 100))
        after_commit = WriterRow("block", frozenset({world.low}), ms(EXPIRY + 60))
        self.assertEqual(judge(world, [submission], writers=[elsewhere, before, after_commit]), [])

    def test_a_writer_that_ended_before_the_send_began_is_not_a_wait(self) -> None:
        world = World()
        submission = world.submission(EXPIRY + 40, started=EXPIRY + 30)
        # It began after the expiry anyway: that alone is the violation.
        self.assertEqual(judge(world, [submission]), ["O5"])
        unknown_start = world.submission(EXPIRY + 40, started=None)
        writer = WriterRow("unmatch", frozenset({world.match}), ms(EXPIRY + 5))
        self.assertEqual(judge(world, [unknown_start], writers=[writer]), ["O5"])

    def test_committed_before_the_expiry_is_never_a_violation(self) -> None:
        world = World()
        writer = WriterRow("send", frozenset({world.match}), ms(EXPIRY - 20))
        self.assertEqual(judge(world, [world.submission(EXPIRY - 10)], writers=[writer]), [])


class SenderRuleO9Tests(unittest.TestCase):
    """CX1: the submission's actor is its session's account and a member of its match."""

    def test_the_sessions_own_account_is_clean(self) -> None:
        world = World()
        self.assertEqual(judge(world, [world.submission(5)]), [])

    def test_the_other_member_with_the_senders_session(self) -> None:
        world = World()
        self.assertEqual(judge(world, [world.submission(5, actor=world.high)]), ["O9"])

    def test_a_non_member(self) -> None:
        world = World()
        self.assertEqual(judge(world, [world.submission(5, actor=uuid4())]), ["O9", "O9"])

    def test_two_claims_are_an_o1_violation(self) -> None:
        world = World()
        self.assertEqual(judge(world, [world.submission(5, claims=2)]), ["O1"])
        self.assertEqual(judge(world, [world.submission(5, claims=0)]), ["O1"])


class D5RuleO10Tests(unittest.TestCase):
    def test_accepted_and_visible_is_clean(self) -> None:
        world = World()
        self.assertEqual(
            judge(world, [world.submission(5)], revocations=world.accepted(), d5=True), []
        )

    def test_o10_needs_d5(self) -> None:
        world = World()
        # The reference design carries no consent rows: O10 does not apply to it.
        self.assertEqual(judge(world, [world.submission(5)]), [])
        self.assertEqual(judge(world, [world.submission(5)], d5=True), ["O10", "O10"])

    def test_a_pause_before_the_send(self) -> None:
        world = World()
        pause = RevocationRow("profile_paused", None, world.high, None, 2, ms(2))
        revocations = [*world.accepted(), pause]
        self.assertEqual(
            judge(world, [world.submission(5)], revocations=revocations, d5=True), ["O10"]
        )
        resume = RevocationRow("profile_resumed", None, world.high, None, 3, ms(3))
        self.assertEqual(
            judge(world, [world.submission(5)], revocations=[*revocations, resume], d5=True), []
        )
        self.assertEqual(judge(world, [world.submission(1)], revocations=revocations, d5=True), [])

    def test_a_restriction_committed_with_the_send(self) -> None:
        world = World()
        restriction = RevocationRow("profile_restricted", None, world.low, None, 2, ms(5))
        self.assertEqual(
            judge(
                world,
                [world.submission(5)],
                revocations=[*world.accepted(), restriction],
                d5=True,
            ),
            ["O10"],
        )

    def test_a_withdrawal_before_the_send(self) -> None:
        world = World()
        withdrawn = world.consent(world.low, "withdrawn", 2)
        revocations = [*world.accepted(), withdrawn]
        self.assertEqual(
            judge(world, [world.submission(5)], revocations=revocations, d5=True), ["O10"]
        )
        again = world.consent(world.low, "accepted", 3)
        self.assertEqual(
            judge(world, [world.submission(5)], revocations=[*revocations, again], d5=True), []
        )


class WitnessRuleO0Tests(unittest.TestCase):
    def census(self, world: World, **changes: Any) -> Census:
        census = Census(
            matches={world.match: 1},
            accounts={world.low: 1, world.high: 1},
            sessions={world.session: (world.low, "valid")},
            tags={world.match: ("design:forced", "c", None)},
        )
        for name, value in changes.items():
            setattr(census, name, value)
        return census

    def o0(self, world: World, census: Census, revocations: list[RevocationRow]) -> list[str]:
        report = oracle.judge([], revocations, world.sessions, census=census)
        return [f"{v.rule}:{v.run_tag}" for v in report.violations]

    def test_a_consistent_world(self) -> None:
        world = World()
        self.assertEqual(self.o0(world, self.census(world), []), [])
        unmatch = RevocationRow("unmatch", world.match, world.low, None, 2, ms(1))
        census = self.census(world, matches={world.match: 2})
        self.assertEqual(self.o0(world, census, [unmatch]), [])

    def test_a_bumped_match_without_its_witness(self) -> None:
        world = World()
        census = self.census(world, matches={world.match: 2})
        self.assertEqual(self.o0(world, census, []), ["O0:design:forced"])

    def test_an_account_and_a_session_without_their_witnesses(self) -> None:
        world = World()
        census = self.census(
            world,
            accounts={world.low: 2, world.high: 1},
            sessions={world.session: (world.low, "revoked")},
        )
        self.assertEqual(len(self.o0(world, census, [])), 2)
        witnessed = [
            RevocationRow("access_revoked", None, world.low, None, None, ms(1)),
            RevocationRow("session_revoked", None, None, world.session, None, ms(2)),
        ]
        self.assertEqual(self.o0(world, census, witnessed), [])

    def test_the_adapters_token_revocation_witness(self) -> None:
        world = World()
        census = self.census(world, accounts={world.low: 2, world.high: 1}, epoch_witnesses=True)
        access = RevocationRow("access_revoked", None, world.low, None, None, ms(1))
        self.assertEqual(len(self.o0(world, census, [access])), 1)
        tokens = RevocationRow("session_epoch_bumped", None, world.low, None, None, ms(1))
        self.assertEqual(self.o0(world, census, [access, tokens]), [])

    def test_a_profile_without_its_witness(self) -> None:
        world = World()
        census = self.census(world, profiles={world.low: (2, "paused")})
        self.assertEqual(len(self.o0(world, census, [])), 1)
        pause = RevocationRow("profile_paused", None, world.low, None, 2, ms(1))
        self.assertEqual(self.o0(world, census, [pause]), [])

    def test_an_untagged_entity_counts_as_the_designs(self) -> None:
        world = World()
        census = self.census(world, matches={world.match: 2}, tags={})
        self.assertEqual(self.o0(world, census, []), ["O0:untagged"])

    def test_a_scoped_evaluation_keeps_its_own_tag(self) -> None:
        world = World()
        census = self.census(world, matches={world.match: 2})
        report = oracle.judge([], [], world.sessions, census=census, scope="control:x")
        self.assertEqual(report.violations, [])


if __name__ == "__main__":
    unittest.main()
