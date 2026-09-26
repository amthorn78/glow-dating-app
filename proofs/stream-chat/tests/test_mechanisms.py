"""P06.1-I2a: the revocation, suspension and deletion families (glow_stream_proof.mechanisms).

The rules are tested as pure functions; each family is driven against
``tests.fake_world.World``, whose knobs stand for the behaviours the live run
records. The fake's defaults are a model, not Stream's behaviour.
"""

from __future__ import annotations

import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix, mechanisms, proof_run
from glow_stream_proof.client_bridge import ClientSessionEnded
from glow_stream_proof.proof_run import Answer, ProofRun
from glow_stream_proof.usage import GuardrailStop, UsageLedger
from tests.fake_world import World, family_run
from tests.fakes import FakeServer, NoSettle, error

FAMILIES = [c.id for c in matrix.all_cases() if c.phase >= proof_run.FAMILY_PHASE]


def answer(outcome: str, status: int | None = None, code: int | None = None) -> Answer:
    return Answer(outcome, status, code, None)  # type: ignore[arg-type]


OK = answer("success", 201)
DENIED = answer("permission", 403, 17)
EXPIRED = answer("auth", 401, 40)
MISSING = answer("not-found", 404, 16)


def run_families(case_ids: set[str], **knobs: Any) -> tuple[ProofRun, FakeServer, World, list[str]]:
    run, server, world, clock = family_run(knobs)
    with NoSettle(), clock:
        run.setup()
        run.authorized_path()
        run.run_matrix(case_ids)
        problems = run.finish(cleanup=True)
    return run, server, world, problems


def row(run: ProofRun, case_id: str) -> proof_run.CaseResult:
    return next(c for c in run.case_results if c.case_id == case_id)


class RulesTest(unittest.TestCase):
    def test_a_dimension_ends_only_on_an_attributable_refusal_after_a_control(self) -> None:
        self.assertEqual(mechanisms.dimension(OK, DENIED)["status"], mechanisms.ENDED)
        self.assertEqual(mechanisms.dimension(OK, EXPIRED)["status"], mechanisms.ENDED)
        self.assertEqual(mechanisms.dimension(OK, OK)["status"], mechanisms.NOT_ENDED)
        # A 404 or no answer is not attributable; nor is anything without a control.
        self.assertEqual(mechanisms.dimension(OK, MISSING)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(mechanisms.dimension(OK, None)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(mechanisms.dimension(DENIED, DENIED)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(mechanisms.dimension(None, DENIED)["status"], mechanisms.NOT_SHOWN)

    def test_the_subscription_ends_only_with_a_listener_that_received_it(self) -> None:
        ws = mechanisms.ws_dimension
        self.assertEqual(ws(True, False, True, True)["status"], mechanisms.ENDED)
        self.assertEqual(ws(True, True, True, True)["status"], mechanisms.NOT_ENDED)
        # Nothing arrived anywhere: a slow delivery is not an ended subscription.
        self.assertEqual(ws(True, False, False, True)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(ws(True, False, True, False)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(ws(False, False, True, True)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(ws(True, None, True, True)["status"], mechanisms.NOT_SHOWN)

    def test_token_reuse(self) -> None:
        token = mechanisms.token_dimension
        self.assertEqual(token(OK, OK, EXPIRED, None)["status"], mechanisms.ENDED)
        self.assertEqual(token(OK, OK, OK, DENIED)["status"], mechanisms.ENDED)
        self.assertEqual(token(OK, OK, OK, OK)["status"], mechanisms.NOT_ENDED)
        self.assertEqual(token(OK, OK, OK, MISSING)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(token(OK, OK, MISSING, None)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(token(OK, DENIED, EXPIRED, None)["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(token(None, OK, EXPIRED, None)["status"], mechanisms.NOT_SHOWN)

    def test_the_policy_verdict(self) -> None:
        ended = {d: {"status": mechanisms.ENDED} for d in mechanisms.DIMENSIONS}
        holds = matrix.Verdict(matrix.HOLDS, "refused")
        verdict = mechanisms.policy_verdict({"M1": ended}, holds, True)
        self.assertEqual(verdict.label, mechanisms.MEETS)
        # Without a client undo (an account-level mechanism) the undo is not required.
        self.assertEqual(
            mechanisms.policy_verdict({"S": ended}, None, True).label, mechanisms.MEETS
        )
        open_ws = {**ended, "ws": {"status": mechanisms.NOT_ENDED}}
        verdict = mechanisms.policy_verdict({"M1": open_ws}, holds, True)
        self.assertEqual(verdict.label, mechanisms.FALLS_SHORT)
        self.assertIn("does not end ws for M1", verdict.reason)
        undone = matrix.Verdict(matrix.FAIL, "the client action succeeded")
        verdict = mechanisms.policy_verdict({"M1": ended}, undone, True)
        self.assertEqual(verdict.label, mechanisms.FALLS_SHORT)
        self.assertIn("the member's own client undid it", verdict.reason)
        verdict = mechanisms.policy_verdict({"M1": ended}, holds, False)
        self.assertEqual(verdict.label, mechanisms.FALLS_SHORT)
        self.assertIn("not retained", verdict.reason)
        # A dimension not shown, an undo not judged or an unknown retention: INCONCLUSIVE.
        unknown = {**ended, "rest": {"status": mechanisms.NOT_SHOWN}}
        for judged, undo, retained in (
            ({"M1": unknown}, holds, True),
            ({"M1": ended}, matrix.Verdict(matrix.INCONCLUSIVE, "x"), True),
            ({"M1": ended}, matrix.Verdict(matrix.REFUSED_FEATURE, "x"), True),
            ({"M1": ended}, holds, None),
            ({"M1": {}}, holds, True),
        ):
            verdict = mechanisms.policy_verdict(judged, undo, retained)
            self.assertEqual(verdict.label, matrix.INCONCLUSIVE, (judged, undo, retained))

    def test_actor_paths(self) -> None:
        event = {
            "type": "member.removed",
            "user": {"id": "u-m2", "name": "Synthetic M2"},
            "channel": {"members": [{"user_id": "u-m2"}]},
        }
        paths = mechanisms.value_paths(event, {"u-m2": "{M2}", "Synthetic M2": "{M2_name}"})
        self.assertEqual(
            paths,
            ["channel.members[].user_id={M2}", "user.id={M2}", "user.name={M2_name}"],
        )
        # A member list names every member; it does not name who acted.
        self.assertEqual(mechanisms.actor_paths(paths), ["user.id={M2}", "user.name={M2_name}"])

    def test_the_table_names_cover_every_familys_channel(self) -> None:
        # proof_run writes them out, because mechanisms imports it.
        for key in mechanisms.MECHANISMS:
            self.assertIn(f"CH_{key}", proof_run._TABLE_NAMES)
        for key in mechanisms.FAMILY_LABELS:
            self.assertIn(key, proof_run._TABLE_NAMES)


class FamiliesTest(unittest.TestCase):
    def test_every_family_records_a_row_and_the_run_cleans_up(self) -> None:
        run, server, world, problems = run_families(set(FAMILIES))
        self.assertEqual([c.case_id for c in run.case_results], FAMILIES)
        self.assertEqual(problems, [])
        self.assertEqual(run.stops, [])
        for case in run.case_results:
            self.assertNotIn("harness error", case.observed, case.case_id)
            self.assertIn(
                case.verdict,
                (mechanisms.MEETS, mechanisms.FALLS_SHORT, matrix.INCONCLUSIVE),
                case.case_id,
            )
        checks = {c.check_id: c.result for c in run.checks}
        for key in mechanisms.MECHANISMS:
            self.assertEqual(checks[f"AP12-{key}"], "PASS", key)
        # Every new state is gone: the deactivated user, the frozen, hidden and banned
        # channels, and the deleted-user artifact the hard delete made.
        self.assertEqual(run.cleanup_result["remaining_proof_users"], [])
        self.assertEqual(run.cleanup_result["remaining_channels"], [])
        self.assertEqual(run.cleanup_result["deleted_user_artifacts_remaining"], 0)
        self.assertEqual([u for u in server.users if "simulated" in u], [])

    def test_member_removal(self) -> None:
        run, _, _, _ = run_families({"RV-remove"})
        case = row(run, "RV-remove")
        self.assertEqual(case.verdict, mechanisms.MEETS)
        detail = case.detail
        self.assertEqual(detail["apply"]["request"], "POST /channels/glow-match/{CH_remove}")
        self.assertEqual(detail["apply"]["body"], {"remove_members": ["{M1}"], "user_id": "{M2}"})
        self.assertEqual(detail["client_undo"]["answer"], "403 / code 17")
        self.assertEqual(detail["client_undo"]["control"], "server replay POST -> 201")
        self.assertTrue(detail["client_undo"]["verdict"].startswith("HOLDS"))
        # Member custom data across removal and re-adding (the S15 mapping).
        self.assertEqual(detail["member_custom_after"]["M1"], "not a member")
        self.assertIn("beforenote", detail["member_custom_after_readd"])
        # The other member's event names the acting user.
        self.assertEqual(detail["on_apply"]["M2"]["names_actor"], ["member.removed: user.id={M2}"])
        self.assertEqual(detail["table"]["M2"]["rest"]["status"], mechanisms.NOT_ENDED)

    def test_an_open_subscription_that_keeps_receiving_is_not_ended(self) -> None:
        run, _, _, _ = run_families({"RV-remove"}, removed_keeps_events=True)
        case = row(run, "RV-remove")
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertEqual(case.reason, "does not end ws for M1")

    def test_a_client_that_can_show_its_hidden_channel(self) -> None:
        run, _, _, _ = run_families({"RV-hide"})
        case = row(run, "RV-hide")
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertIn("the member's own client undid it", case.reason)
        self.assertEqual(case.detail["hidden_in_channel_list"], "not listed")
        self.assertEqual(case.detail["listed_after_a_new_message"], "listed")

    def test_a_freeze_is_judged_for_both_members(self) -> None:
        run, _, _, _ = run_families({"RV-freeze"})
        case = row(run, "RV-freeze")
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertIn("rest for M1", case.reason)
        self.assertIn("rest for M2", case.reason)

    def test_token_revocation_on_two_devices(self) -> None:
        run, _, _, _ = run_families({"RV-revoke"}, revoked_connection_open=False)
        case = row(run, "RV-revoke")
        table = case.detail["table"]
        for label in ("R", "R-2"):
            for dim in mechanisms.DIMENSIONS:
                self.assertEqual(table[label][dim]["status"], mechanisms.ENDED, (label, dim))
        self.assertEqual(case.verdict, mechanisms.MEETS)
        tokens = case.detail["tokens_after_revocation"]
        # Issued at once, its back-dated iat is before the revocation time: refused.
        self.assertLess(tokens["early"]["iat_minus_revocation_s"], 0)
        self.assertEqual(tokens["early"]["connect"], "401 / code 40")
        # Issued past the back-dating: accepted, and the member reads the channel again.
        self.assertGreater(tokens["late"]["iat_minus_revocation_s"], 0)
        self.assertEqual(tokens["late"]["read"], "201 (succeeded)")
        # The revocation is per user, never application-wide.
        self.assertEqual(case.detail["apply"]["request"], "PATCH /api/v2/users")

    def test_an_open_connection_that_outlives_the_revocation(self) -> None:
        run, _, _, _ = run_families({"RV-revoke"})
        case = row(run, "RV-revoke")
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertEqual(case.reason, "does not end ws for R, ws for R-2")

    def test_deactivation_and_the_hard_delete(self) -> None:
        run, _, _, _ = run_families({"SD-deactivate", "SD-delete"})
        deactivate = row(run, "SD-deactivate")
        self.assertEqual(deactivate.verdict, mechanisms.MEETS)
        self.assertEqual(deactivate.detail["retention"]["affected_member_message"]["author"], "{S}")
        delete = row(run, "SD-delete")
        self.assertEqual(delete.verdict, mechanisms.FALLS_SHORT)
        self.assertIn("not retained", delete.reason)
        self.assertEqual(
            delete.detail["apply"]["body"],
            {"user_ids": ["{H}"], "user": "hard", "messages": "hard", "conversations": "hard"},
        )
        self.assertEqual(delete.detail["apply"]["task"], "completed")
        self.assertTrue(delete.detail["channel_deleted_by_the_mechanism"])
        # Neither the deleted user nor its deleted channel is named again at cleanup.
        self.assertNotIn(f"{run.prefix}-uh", run.users)
        self.assertNotIn(f"glow-match:{run.prefix}-ch-delete", run.channels)

    def test_a_channel_the_hard_delete_keeps_is_deleted_by_the_cleanup(self) -> None:
        run, _, _, problems = run_families({"SD-delete"}, hard_delete_removes_conversations=False)
        self.assertIn(f"glow-match:{run.prefix}-ch-delete", run.channels)
        self.assertEqual(problems, [])
        self.assertEqual(run.cleanup_result["remaining_channels"], [])

    def test_a_mechanism_stream_does_not_apply_ends_only_its_case(self) -> None:
        run, server, _, clock = family_run()

        def refuse_ban(method: str, path: str, body: Any, params: Any) -> Any:
            if path == "/api/v2/moderation/ban" and method == "POST":
                return error(method, path, 400, 4, "bad ban")
            return None

        server.handlers.insert(0, refuse_ban)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"RV-ban", "RV-hide"})
            run.finish(cleanup=True)
        ban = row(run, "RV-ban")
        self.assertEqual(ban.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(ban.reason, "Stream did not apply the mechanism (400 / code 4)")
        self.assertNotEqual(row(run, "RV-hide").verdict, matrix.INCONCLUSIVE)


class BudgetAndSessionsTest(unittest.TestCase):
    def test_a_family_starts_only_with_the_calls_it_declared(self) -> None:
        run, _, _, clock = family_run()
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            # Enough left for an I1 case (30 beyond the 130 kept for the end), not for
            # a family (120).
            spent = (
                run.ledger.limits.api_calls
                - run.ledger.run.api_calls
                - (proof_run.CLEANUP_RESERVE + proof_run.CASE_CALL_MARGIN + 10)
            )
            run.ledger.reserve("api_calls", spent)
            run.run_matrix({"R1", "RV-remove"})
        self.assertEqual([c.case_id for c in run.case_results], ["R1"])
        self.assertTrue(any("matrix stopped before RV-remove" in n for n in run.notes))

    def test_a_familys_own_sessions_are_closed_at_its_end(self) -> None:
        run, _, _, clock = family_run()
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"RV-revoke", "SD-delete"})
            left = set(run.sessions)
            run.finish(cleanup=True)
        # The shared M2 stays for the next family; R, its second device, H and every
        # token-reuse session are closed.
        self.assertEqual(left, {"M2"})
        self.assertEqual(run.ledger.open_connections, 0)

    def test_the_server_side_send_is_an_observation_only(self) -> None:
        verdicts = []
        for refuse in (False, True):
            run, server, _, clock = family_run()

            def handler(
                method: str, path: str, body: Any, params: Any, refuse: bool = refuse
            ) -> Any:
                text = str(((body or {}).get("message") or {}).get("text", ""))
                if refuse and text.startswith("server send as the affected member"):
                    return error(method, path, 403, 17, "user is not a member")
                return None

            server.handlers.insert(0, handler)
            with NoSettle(), clock:
                run.setup()
                run.authorized_path()
                run.run_matrix({"RV-remove"})
            case = row(run, "RV-remove")
            verdicts.append((case.verdict, case.reason))
            expected = "403 / code 17" if refuse else "201"
            self.assertEqual(case.detail["server_send_as_affected"]["answer"], expected)
        self.assertEqual(verdicts[0], verdicts[1])


class StopsTest(unittest.TestCase):
    ledger: UsageLedger

    def test_a_charge_signal_on_the_mechanism_stops_the_run_and_skips_the_cleanup(self) -> None:
        def charge(method: str, path: str, body: Any, params: Any) -> Any:
            if method == "POST" and body and "remove_members" in body:
                raise self.ledger.stop_at_once(
                    "server POST: HTTP 402; stopping at once", rate_limited=False
                )
            return None

        run, server, _, clock = family_run()
        self.ledger = run.ledger
        server.handlers.insert(0, charge)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"RV-remove", "RV-ban"})
            problems = run.finish(cleanup=True)
        case = row(run, "RV-remove")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("guardrail", case.reason)
        self.assertEqual([c.case_id for c in run.case_results], ["RV-remove"])  # stopped
        self.assertTrue(any(p.startswith("cleanup skipped") for p in problems))
        self.assertEqual(run.cleanup_result, {})

    def test_a_rate_limit_in_a_probe_keeps_what_was_observed(self) -> None:
        def limited(method: str, path: str, body: Any, params: Any) -> Any:
            text = str((body or {}).get("message", {}).get("text", ""))
            if method == "POST" and text.startswith("after probe"):
                raise self.ledger.stop_at_once(
                    "server POST: HTTP 429; stopping at once", rate_limited=True
                )
            return None

        run, server, _, clock = family_run()
        self.ledger = run.ledger
        server.handlers.insert(0, limited)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"RV-remove"})
            problems = run.finish(cleanup=True)
        case = row(run, "RV-remove")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        # What the family had observed before the stop is kept in the row.
        self.assertIn("applied", case.observed)
        self.assertEqual(case.detail["apply"]["answer"], "201")
        self.assertIn("only a rate limit", " ".join(problems))

    def test_an_ended_client_session_ends_only_its_case(self) -> None:
        run, server, world, clock = family_run()
        original = world.behaviour
        calls = {"n": 0}

        def ends(session: Any, op: str, params: dict[str, Any]) -> Any:
            if session.label == "M1" and params.get("method") == "updateMemberPartial":
                calls["n"] += 1
                if calls["n"] == 2:  # the write after the mechanism
                    raise ClientSessionEnded("client M1 ended: no reply within 60s")
            return original(session, op, params)

        world.behaviour = ends  # type: ignore[method-assign]
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"RV-remove", "RV-ban"})
            problems = run.finish(cleanup=True)
        removal = row(run, "RV-remove")
        self.assertEqual(removal.verdict, matrix.INCONCLUSIVE)
        self.assertIn("ClientSessionEnded", removal.detail["interrupted"])
        # The run went on to the next family, and cleaned up.
        self.assertNotEqual(row(run, "RV-ban").verdict, matrix.INCONCLUSIVE)
        self.assertEqual(problems, [])

    def test_the_i1_sessions_close_before_the_families_only_when_one_runs(self) -> None:
        run, _, _, clock = family_run()
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"R1"})
            self.assertIn("A", run.sessions)
            run.run_matrix({"RV-hide"})
            self.assertNotIn("A", run.sessions)
            self.assertIn("M1", run.sessions)
            run.finish(cleanup=True)


if __name__ == "__main__":
    unittest.main()
