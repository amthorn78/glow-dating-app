"""P06.2 Stage A's changes to the suite, offline (no database).

- P06.DB's carried item 1 (R2): a used database is refused before anything is written.
- Carried item 3 (R3, R4): the per-iteration oracle check names its race at its call
  site; an empty signal is never met; sign-ins never count as a race's writers.
- Carried item 2 (R1): each iteration's commit order is counted, and the session races
  give the revocation a seeded extra delay.
- DM-13 2.1: the oracle-level controls, planted in either subject's rows.
- D3: the run passes only when both subjects and the delivery phase pass.
"""

from __future__ import annotations

import random
import unittest
from collections import Counter
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import nullcontext
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest import mock
from uuid import UUID, uuid4

from glow_ordering_proof import __main__ as cli
from glow_ordering_proof import cases, controls, evidence, observe, oracle, planted, stress
from glow_ordering_proof.interface import Result
from glow_ordering_proof.results import Report, RunReport
from tests.fakes import FakeConnection, FilteringCursor, ScriptedCursor

T0 = datetime(2026, 10, 5, 12, 0, 0, tzinfo=UTC)


def ms(n: float) -> datetime:
    return T0 + timedelta(milliseconds=n)


class UsedDatabaseTests(unittest.TestCase):
    def reasons(self, tables: dict[str, bool], accounts: bool) -> list[str]:
        """``tables`` maps each proof table that exists to whether it holds a row."""

        def answer(sql: str, params: list[object]) -> tuple[Any, ...]:
            if sql.startswith("SELECT to_regclass"):
                return (params[0] in tables,)
            if "glow_persistence_appaccount" in sql:
                return (accounts,)
            for table, rows in tables.items():
                if table in sql:
                    return (rows,)
            raise AssertionError(sql)

        return observe.used_database_reasons(ScriptedCursor(answer))

    def test_a_new_database_is_accepted(self) -> None:
        self.assertEqual(self.reasons({}, False), [])
        empty = {table: False for table in observe.PROOF_TABLES}
        self.assertEqual(self.reasons(empty, False), [])

    def test_any_proof_row_or_app_account_refuses(self) -> None:
        for table in observe.PROOF_TABLES:
            with self.subTest(table=table):
                self.assertEqual(
                    self.reasons({table: True}, False), [f"{table} already holds rows"]
                )
        self.assertEqual(self.reasons({}, True), ["glow_persistence_appaccount already holds rows"])

    def test_run_refuses_before_it_writes_anything(self) -> None:
        facts = {"superuser": "false", "track_commit_timestamp": "on"}
        isolation = ScriptedCursor(lambda sql, params: ("read committed",))
        used = ScriptedCursor(lambda sql, params: (True,))
        connections = iter([FakeConnection(isolation), FakeConnection(used)])

        class Switching:
            def cursor(self) -> Any:
                return next(connections).cursor()

        suite = mock.Mock(side_effect=AssertionError("the suite ran on a used database"))
        with (
            mock.patch("django.db.connection", Switching()),
            mock.patch("django.db.transaction.atomic", lambda: nullcontext()),
            mock.patch.object(observe, "server_facts", lambda: facts),
            mock.patch.object(observe, "migration_ledger", lambda: []),
            mock.patch.object(cli, "run_suite", suite),
            mock.patch("builtins.print") as printed,
        ):
            self.assertEqual(cli.run(1, None), 1)
        suite.assert_not_called()
        text = " ".join(str(call.args[0]) for call in printed.call_args_list)
        self.assertIn(observe.USED_DATABASE, text)


class ThreadWorker:
    """A worker with no database connection: its own thread, for the race's barrier."""

    def __init__(self) -> None:
        self.pool = ThreadPoolExecutor(max_workers=1)

    def submit(self, task: Callable[[], Any]) -> Future[Any]:
        return self.pool.submit(task)


class FakeLog:
    def __init__(self) -> None:
        self.context = observe.LogContext(run_tag="design:stress", variant="fake")

    def record_world(self, *args: object) -> None:
        return None


class FakeSubject:
    """Every writer applies or authorizes at once; nothing touches a database."""

    def sign_in(self, account_id: UUID, *, ttl_seconds: float, hooks: Any = None) -> Result:
        return Result("applied", session_id=uuid4())

    def __getattr__(self, name: str) -> Callable[..., Result]:
        def writer(*args: object, **kwargs: object) -> Result:
            return Result("authorized" if name == "send" else "applied")

        return writer


class FakeFixtures:
    def create_account(self) -> UUID:
        return uuid4()

    def create_match(self, first: UUID, second: UUID) -> UUID:
        return uuid4()


class FakeEvidence:
    name = "fake"

    def __init__(self) -> None:
        self.evaluations: list[dict[str, object]] = []

    def revocation_commit(self, world: object, rev: object) -> None:
        return None

    def intervals(self, run_tag: str, case_id: str, iteration: int) -> list[Any]:
        return []

    def evaluate(self, **filters: object) -> oracle.OracleReport:
        self.evaluations.append(filters)
        return oracle.OracleReport(0, 0)

    def record_attempt(self, result: Result, **record: object) -> None:
        return None


def fake_context(evidence_reader: FakeEvidence) -> cases.Context:
    return cases.Context(
        FakeSubject(),
        FakeFixtures(),
        FakeLog(),  # type: ignore[arg-type]
        [ThreadWorker() for _ in range(4)],  # type: ignore[misc]
        evidence_reader,
    )


class PerIterationCallSiteTests(unittest.TestCase):
    """R3: the per-iteration oracle check names the race (``case_id``) at its call site,
    since every race of a run tag numbers its iterations from 1."""

    def test_the_stress_control_check_names_its_race_and_iteration(self) -> None:
        reader = FakeEvidence()
        race = stress.RACE_BY_ID["race.block_by_high"]
        stress.run_race(
            fake_context(reader),
            race,
            seed=1,
            run_tag="control:no_locks.stress",
            stop_at_first_violation=True,
            max_iterations=2,
        )
        self.assertEqual(
            reader.evaluations,
            [
                {"run_tag": "control:no_locks.stress", "case_id": race.id, "iteration": 1},
                {"run_tag": "control:no_locks.stress", "case_id": race.id, "iteration": 2},
            ],
        )


class EmptySignalTests(unittest.TestCase):
    """R4: a control that declares no signal can never count as failed as intended."""

    def test_an_empty_signal_is_never_met(self) -> None:
        empty = controls.Signal()
        self.assertFalse(empty.met({cases.WAIT_NOT_OBSERVED, cases.REFUSAL_MISSING}, {"O2"}))
        self.assertFalse(empty.met((), ()))


SIGN_IN_ROWS: list[dict[str, Any]] = [
    # The send and the revocation never overlap; only a sign-in overlaps the send.
    {
        "run_tag": "design:stress",
        "case_id": "race.block_by_low",
        "iteration": 1,
        "kind": k,
        "start": ms(a),
        "end": ms(b),
    }
    for k, a, b in (("send", 0, 5), ("sign_in", 1, 3), ("block", 10, 12))
]


class SignInExclusionTests(unittest.TestCase):
    """R4: a sign-in is the world's setup, never one of the race's writers."""

    def overlapped(self, read: Callable[[], list[Any]], target: Any) -> bool:
        cursor = FilteringCursor(SIGN_IN_ROWS, ("kind", "start", "end"))
        with mock.patch.object(target, "connection", FakeConnection(cursor)):
            intervals = read()
        sql = cursor.executed[0][0]
        self.assertIn("kind <> 'sign_in'", sql)
        return stress._overlapped("revocation", intervals)

    def test_the_reference_reader(self) -> None:
        self.assertFalse(
            self.overlapped(
                lambda: stress._intervals("design:stress", "race.block_by_low", 1), stress
            )
        )

    def test_the_adapter_reader(self) -> None:
        self.assertFalse(
            self.overlapped(
                lambda: evidence.adapter_intervals("design:stress", "race.block_by_low", 1),
                evidence,
            )
        )

    def test_without_the_exclusion_the_sign_in_would_count(self) -> None:
        intervals = [(str(r["kind"]), r["start"], r["end"]) for r in SIGN_IN_ROWS]
        self.assertTrue(stress._overlapped("revocation", intervals))


class CommitOrderTests(unittest.TestCase):
    def test_two_writers(self) -> None:
        self.assertEqual(
            stress.commit_order(
                "revocation", [("send", ms(0), ms(5)), ("block", ms(1), ms(8))], []
            ),
            "send first",
        )
        self.assertEqual(
            stress.commit_order(
                "revocation", [("send_attempt", ms(0), ms(9)), ("sign_out", ms(1), ms(4))], []
            ),
            "revocation first",
        )

    def test_opposing_writers(self) -> None:
        intervals = [
            ("send_attempt", ms(0), ms(9)),
            ("block", ms(1), ms(4)),
            ("block", ms(2), ms(10)),
            ("suspend", ms(1), ms(11)),
        ]
        self.assertEqual(stress.commit_order("opposing", intervals, []), "revocation first")

    def test_duplicates_by_the_authorization(self) -> None:
        results = [("send_a", Result("replayed")), ("send_b", Result("authorized"))]
        self.assertEqual(stress.commit_order("duplicates", [], results), "send_b first")

    def test_unmeasured(self) -> None:
        self.assertEqual(stress.commit_order("revocation", [], []), "not measured")


class SeededDelayTests(unittest.TestCase):
    """R1, carried item 2: in the session races, and only there, the revocation gets a
    seeded extra delay on about half the iterations."""

    def delays(self, race_id: str, iterations: int = 60) -> list[tuple[float, float]]:
        seen: list[float] = []
        real = stress._gated

        def gated(barrier: Any, delay: float, writer: Callable[[], Result]) -> Callable[[], Result]:
            seen.append(delay)
            return real(barrier, delay, writer)

        with mock.patch.object(stress, "_gated", gated):
            stress.run_race(
                fake_context(FakeEvidence()),
                stress.RACE_BY_ID[race_id],
                seed=20260929,
                run_tag="design:stress",
                max_iterations=iterations,
            )
        return list(zip(seen[0::2], seen[1::2], strict=True))

    def test_the_session_races_delay_the_revocation(self) -> None:
        for race_id in ("race.sign_out_sender", "race.expire_sender"):
            with self.subTest(race=race_id):
                pairs = self.delays(race_id)
                self.assertTrue(any(rev > 0.003 for _, rev in pairs))
                self.assertTrue(all(send <= 0.003 for send, _ in pairs))
                self.assertTrue(all(rev <= 0.003 + stress.MAX_REVOCATION_DELAY for _, rev in pairs))

    def test_the_other_races_keep_p06_dbs_head_start(self) -> None:
        for race_id in ("race.block_by_low", "race.suspend_high", "race.pause_high"):
            with self.subTest(race=race_id):
                self.assertTrue(all(max(pair) <= 0.003 for pair in self.delays(race_id, 30)))

    def test_the_seed_decides_the_delays(self) -> None:
        self.assertEqual(
            self.delays("race.sign_out_sender", 20), self.delays("race.sign_out_sender", 20)
        )
        random.seed(0)  # the module's own generator is per race; this changes nothing
        self.assertEqual(
            self.delays("race.expire_sender", 20), self.delays("race.expire_sender", 20)
        )


class PlantedPlanTests(unittest.TestCase):
    def test_every_rule_has_a_planted_control(self) -> None:
        rules = Counter(control.rule for control in planted.PLANTED)
        for rule in ("O0", "O1", "O2", "O3", "O4", "O5", "O6", "O9", "O10"):
            self.assertIn(rule, rules)
        self.assertEqual(rules["O9"], 2)  # CX1: the other member, and a non-member
        self.assertEqual(len(planted.PLANTED_BY_ID), len(planted.PLANTED))

    def test_d5_controls_run_for_the_adapter_only(self) -> None:
        reference = planted.planted_for(d5=False)
        adapter = planted.planted_for(d5=True)
        self.assertTrue(all(not c.d5 for c in reference))
        self.assertEqual(
            {c.id for c in adapter} - {c.id for c in reference},
            {"oracle.send_while_paused", "oracle.send_after_consent_withdrawn"},
        )
        self.assertTrue(all(c.run_tag.startswith("control:") for c in adapter))

    def test_each_control_plants_what_it_declares(self) -> None:
        calls: list[tuple[str, dict[str, object]]] = []

        class Recorder:
            def __getattr__(self, name: str) -> Callable[..., None]:
                def record(*args: object, **kwargs: object) -> None:
                    calls.append((name, kwargs))

                return record

        world = cases.World(uuid4(), uuid4(), uuid4(), uuid4(), uuid4())
        ctx = fake_context(FakeEvidence())
        expected = {
            "oracle.misattributed_actor": ["submission"],
            "oracle.non_member_actor": ["submission"],
            "oracle.send_after_contact_revocation": ["contact_revocation", "submission"],
            "oracle.send_after_session_end": ["session_end", "submission"],
            "oracle.send_after_account_revocation": ["account_revocation", "submission"],
            "oracle.wrong_contact_version": ["submission"],
            "oracle.witness_in_another_transaction": ["submission"],
            "oracle.unwitnessed_revocation": ["contact_revocation"],
            "oracle.send_while_paused": ["pause", "submission"],
            "oracle.send_after_consent_withdrawn": ["withdraw", "submission"],
        }
        for control_id, names in expected.items():
            with self.subTest(control=control_id):
                calls.clear()
                planted._plant(planted.PLANTED_BY_ID[control_id], ctx, world, Recorder())  # type: ignore[arg-type]
                self.assertEqual([name for name, _ in calls], names)
        calls.clear()
        planted._plant(planted.PLANTED_BY_ID["oracle.misattributed_actor"], ctx, world, Recorder())  # type: ignore[arg-type]
        self.assertEqual(calls[0][1]["actor"], world.high)
        self.assertEqual(calls[0][1]["session"], world.session_low)


class RunVerdictTests(unittest.TestCase):
    def passing(self, subject: str) -> Report:
        report = Report(1, {}, "read committed", [], subject=subject)
        report.oracle = oracle.OracleReport(0, 0)
        return report

    def test_both_subjects_and_the_delivery_phase(self) -> None:
        from glow_ordering_proof.results import DeliveryReport

        delivery = DeliveryReport()
        delivery.check("drain", True, "ok")
        run = RunReport([self.passing("reference"), self.passing("adapter")], delivery)
        self.assertTrue(run.verdict()[0])
        delivery.check("end state", False, "a channel kept its members")
        self.assertFalse(run.verdict()[0])
        self.assertFalse(
            RunReport([self.passing("reference"), self.passing("adapter")]).verdict()[0]
        )
        failing = self.passing("adapter")
        failing.oracle.violations.append(
            oracle.Violation("O9", "design:forced", "c", None, uuid4(), "misattributed")
        )
        ok_delivery = DeliveryReport()
        ok_delivery.check("drain", True, "ok")
        run = RunReport([self.passing("reference"), failing], ok_delivery)
        ok, reasons = run.verdict()
        self.assertFalse(ok)
        self.assertTrue(any(r.startswith("adapter:") for r in reasons))
        self.assertFalse(DeliveryReport().ok)


if __name__ == "__main__":
    unittest.main()
