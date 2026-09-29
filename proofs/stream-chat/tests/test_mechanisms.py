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
from tests.fakes import FakeServer, NoSettle, error, record

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
        # A connection that closed or recovered could explain the miss (the independent
        # review, point 2).
        dropped = ws(True, False, True, True, "closed and recovered")
        self.assertEqual(dropped["status"], mechanisms.NOT_SHOWN)
        self.assertIn("not attributable", dropped["why"])
        self.assertEqual(ws(True, True, True, True, "closed")["status"], mechanisms.NOT_ENDED)

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

    def test_the_hide_is_made_again_before_the_members_own_show(self) -> None:
        run, _, _, _ = run_families({"RV-hide"})
        case = row(run, "RV-hide")
        # The probe's message showed the channel again; it is hidden again first.
        self.assertEqual(case.detail["listed_after_a_new_message"], "listed")
        self.assertEqual(
            case.detail["hidden_again_before_undo"], {"answer": "201", "listed": "not listed"}
        )
        self.assertTrue(case.detail["client_undo"]["verdict"].startswith("FAIL"))

    def test_a_hide_that_is_not_made_again_leaves_the_undo_unjudged(self) -> None:
        run, server, _, clock = family_run()
        hides: list[int] = []

        def refuse_second_hide(method: str, path: str, body: Any, params: Any) -> Any:
            if method == "POST" and path.endswith("-ch-hide/hide"):
                hides.append(1)
                if len(hides) == 2:
                    return error(method, path, 500, -1, "internal")
            return None

        server.handlers.insert(0, refuse_second_hide)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"RV-hide"})
            run.finish(cleanup=True)
        case = row(run, "RV-hide")
        self.assertTrue(case.detail["client_undo"]["verdict"].startswith(matrix.INCONCLUSIVE))
        self.assertEqual(case.detail["client_undo"]["request"], "not sent")
        session = run.sessions.get("M1")
        sent = [p.get("method") for op, p in getattr(session, "sent", []) if op == "call"]
        self.assertNotIn("show", sent)

    def test_a_mechanism_refused_with_the_actor_named_is_applied_without_it(self) -> None:
        run, server, _, clock = family_run()

        def refuse_actor(method: str, path: str, body: Any, params: Any) -> Any:
            if body and "remove_members" in body and "user_id" in body:
                return error(method, path, 403, 17, "user may not remove members")
            return None

        server.handlers.insert(0, refuse_actor)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"RV-remove"})
        case = row(run, "RV-remove")
        apply = case.detail["apply"]
        self.assertEqual(
            apply["refused_with_the_actor_named"], "403 / code 17: user may not remove members"
        )
        self.assertIsNone(apply["actor_named"])
        self.assertEqual(apply["body"], {"remove_members": ["{M1}"]})
        self.assertEqual(case.detail["on_apply"]["M2"]["names_actor"], "no actor named")
        self.assertEqual(case.verdict, mechanisms.MEETS)

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
            # A token issued past the back-dating connects and reads: the revocation
            # alone does not end the member's access (the independent review, point 4).
            self.assertEqual(table[label]["token_issued_after"]["status"], mechanisms.NOT_ENDED)
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertEqual(
            case.reason, "does not end token_issued_after for R, token_issued_after for R-2"
        )
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
        self.assertEqual(
            case.reason,
            "does not end ws for R, token_issued_after for R, ws for R-2, "
            "token_issued_after for R-2",
        )

    def test_deactivation_and_the_hard_delete(self) -> None:
        run, _, _, _ = run_families({"SD-deactivate", "SD-delete"})
        deactivate = row(run, "SD-deactivate")
        self.assertEqual(deactivate.verdict, mechanisms.MEETS)
        # A token issued after the deactivation is refused too.
        self.assertEqual(
            deactivate.detail["table"]["S"]["token_issued_after"]["status"], mechanisms.ENDED
        )
        self.assertEqual(deactivate.detail["token_issued_after"]["connect"], "401 / code 5")
        self.assertIn("a token issued after it", deactivate.reason)
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

    def test_a_connect_that_creates_the_deleted_user_again_is_cleaned_up(self) -> None:
        run, server, _, problems = run_families({"SD-delete"}, connect_recreates_deleted=True)
        case = row(run, "SD-delete")
        self.assertEqual(case.detail["connected_after_the_delete"], ["H", "H-new"])
        h = f"{run.prefix}-uh"
        self.assertIn(h, run.users)  # named at cleanup again
        self.assertNotIn(h, server.users)  # and deleted
        self.assertEqual(problems, [])

    def test_the_policy_requires_every_dimension_of_the_mechanism(self) -> None:
        ended = {d: {"status": mechanisms.ENDED} for d in mechanisms.DIMENSIONS}
        verdict = mechanisms.policy_verdict({"S": ended}, None, True, mechanisms.ACCOUNT_DIMENSIONS)
        self.assertEqual(verdict.label, matrix.INCONCLUSIVE)
        self.assertEqual(verdict.reason, "not shown: token_issued_after for S")

    def test_the_cleanup_names_no_user_or_channel_that_is_gone(self) -> None:
        # The hard delete's task is reported late and the channel is still there when
        # the run looks; both are gone by the cleanup (P06.1-I2a).
        run, server, world, clock = family_run({"hard_delete_removes_conversations": False})
        server.task_status = "running"
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"SD-delete"})
            h, cid = f"{run.prefix}-uh", f"glow-match:{run.prefix}-ch-delete"
            self.assertIn(h, run.users)  # the task never reported completion
            self.assertIn(cid, run.maybe_gone_channels)
            server.members.pop(f"{run.prefix}-ch-delete")  # the conversation goes later
            server.task_status = "completed"
            problems = run.finish(cleanup=True)
        out = run.cleanup_result
        self.assertEqual(out["recorded_users_already_gone"], 1)
        self.assertEqual(out["channels_already_gone"], ["glow-match:{CH_delete}"])
        deleted = [b for m, p, b in server.calls if p == "/api/v2/chat/channels/delete"]
        self.assertNotIn(cid, deleted[-1]["cids"])
        self.assertEqual(out["users_delete"], 201)  # the batch named only existing users
        self.assertEqual(problems, [])
        # What was observed may predate the delete: not judged.
        delete = row(run, "SD-delete")
        self.assertEqual(delete.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(
            delete.reason, "the hard delete's task did not report completion (running)"
        )

    def test_a_stop_during_the_hard_deletes_task_leaves_the_channel_checked_first(self) -> None:
        # The independent review, point 8: the run stops while it waits for the task.
        run, server, _, clock = family_run()

        def limited(method: str, path: str, body: Any, params: Any) -> Any:
            if path.startswith("/api/v2/tasks/"):
                raise run.ledger.stop_at_once(
                    "server GET: HTTP 429; stopping at once", rate_limited=True
                )
            return None

        server.handlers.insert(0, limited)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"SD-delete"})
        self.assertIn(f"glow-match:{run.prefix}-ch-delete", run.maybe_gone_channels)

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


CLOSED = {"type": "connection.changed", "online": False}
RECOVERED = {"type": "connection.recovered"}


class WindowTest(unittest.TestCase):
    """The open subscription's window (the independent review, point 2)."""

    def test_a_late_delivery_is_not_taken_for_an_ended_subscription(self) -> None:
        run, _, _, _ = run_families({"RV-remove"}, removed_keeps_events=True, late={"M1"})
        case = row(run, "RV-remove")
        probe = case.detail["after_probe"]
        self.assertEqual(probe["order"], ["M2", "M1"])  # the listener first
        self.assertEqual(probe["second_window"], ["M1"])
        self.assertTrue(probe["received"]["M1"]["message"])
        self.assertEqual(case.detail["table"]["M1"]["ws"]["status"], mechanisms.NOT_ENDED)
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)

    def test_a_member_that_misses_the_probe_twice_is_ended(self) -> None:
        run, _, _, _ = run_families({"RV-remove"})
        case = row(run, "RV-remove")
        self.assertEqual(case.detail["after_probe"]["second_window"], ["M1"])
        self.assertEqual(case.detail["table"]["M1"]["ws"]["status"], mechanisms.ENDED)

    def test_a_closed_or_recovered_connection_leaves_a_channel_level_miss_not_shown(
        self,
    ) -> None:
        run, _, _, _ = run_families({"RV-remove"}, after_window_local={"M1": [CLOSED, RECOVERED]})
        case = row(run, "RV-remove")
        ws = case.detail["table"]["M1"]["ws"]
        self.assertEqual(ws["status"], mechanisms.NOT_SHOWN)
        self.assertIn("closed and recovered", ws["why"])
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_a_close_in_the_mechanisms_own_window_counts_too(self) -> None:
        run, _, _, _ = run_families({"RV-remove"}, apply_window_local={"M1": [CLOSED]})
        case = row(run, "RV-remove")
        self.assertTrue(case.detail["on_apply"]["M1"]["connection_closed"])
        self.assertEqual(case.detail["table"]["M1"]["ws"]["status"], mechanisms.NOT_SHOWN)

    def test_an_account_level_close_may_end_the_subscription_a_recovery_may_not(self) -> None:
        run, _, _, _ = run_families({"SD-deactivate"}, after_window_local={"S": [CLOSED]})
        ws = row(run, "SD-deactivate").detail["table"]["S"]["ws"]
        self.assertEqual(ws["status"], mechanisms.ENDED)
        self.assertIn("the connection closed after the mechanism", ws["why"])
        run, _, _, _ = run_families(
            {"SD-deactivate"}, after_window_local={"S": [CLOSED, RECOVERED]}
        )
        ws = row(run, "SD-deactivate").detail["table"]["S"]["ws"]
        self.assertEqual(ws["status"], mechanisms.NOT_SHOWN)
        self.assertIn("recovered", ws["why"])


class TokenLifetimeTest(unittest.TestCase):
    """No refusal is judged that could be a token's own expiry (the independent review,
    a nit). The margins are raised past the tokens' 900 s to drive each rule."""

    def setUp(self) -> None:
        self.saved = (
            proof_run.CASE_TOKEN_MARGIN_SECONDS,
            mechanisms.FAMILY_TOKEN_MARGIN_SECONDS,
            mechanisms.TOKEN_EXPIRY_MARGIN_SECONDS,
        )

    def tearDown(self) -> None:
        (
            proof_run.CASE_TOKEN_MARGIN_SECONDS,
            mechanisms.FAMILY_TOKEN_MARGIN_SECONDS,
            mechanisms.TOKEN_EXPIRY_MARGIN_SECONDS,
        ) = self.saved

    def test_a_case_is_not_run_while_the_setup_tokens_are_close_to_expiry(self) -> None:
        proof_run.CASE_TOKEN_MARGIN_SECONDS = 10_000
        run, _, _, _ = run_families({"R1"})
        case = row(run, "R1")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.request, "-")
        self.assertIn("not run: the setup tokens are close to their expiry", case.observed)
        ap11 = next(c for c in run.checks if c.check_id == "AP11")
        self.assertEqual(ap11.result, "FAIL")
        self.assertIn("not made", ap11.evidence)

    def test_a_family_is_not_run_while_the_shared_tokens_are_close_to_expiry(self) -> None:
        mechanisms.FAMILY_TOKEN_MARGIN_SECONDS = 10_000
        run, _, _, _ = run_families({"RV-remove", "RV-ban"})
        # M1's and M2's tokens are issued by the first family; the second finds them old.
        self.assertEqual(row(run, "RV-remove").verdict, mechanisms.MEETS)
        ban = row(run, "RV-ban")
        self.assertEqual(ban.verdict, matrix.INCONCLUSIVE)
        self.assertIn("not run: the members' tokens are close to their expiry", ban.observed)
        self.assertNotIn("apply", ban.detail)

    def test_a_refusal_near_the_members_own_expiry_is_not_an_ended_dimension(self) -> None:
        mechanisms.TOKEN_EXPIRY_MARGIN_SECONDS = 10_000
        run, _, _, _ = run_families({"RV-remove"})
        case = row(run, "RV-remove")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        rest = case.detail["table"]["M1"]["rest"]
        self.assertEqual(rest["status"], mechanisms.NOT_SHOWN)
        self.assertIn("the refusal could be its expiry", rest["why"])
        self.assertGreater(case.detail["token_seconds_left_after"]["M1"], 800)

    def test_the_margin_applies_to_every_dimension(self) -> None:
        # The I2a review's nit 3 (P06.1-I2b): not only the REST read.
        mechanisms.TOKEN_EXPIRY_MARGIN_SECONDS = 10_000
        run, _, _, _ = run_families({"RV-remove"})
        table = row(run, "RV-remove").detail["table"]["M1"]
        for dim in mechanisms.DIMENSIONS:
            self.assertEqual(table[dim]["status"], mechanisms.NOT_SHOWN, dim)
            self.assertIn("the refusal could be its expiry", table[dim]["why"], dim)


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
        # What the family had observed before the stop is kept in the row: the REST
        # reads, S15 writes and token reuse made after the mechanism (the independent
        # review, point 7).
        self.assertIn("M1: rest ended", case.observed)
        self.assertEqual(case.detail["apply"]["answer"], "201")
        self.assertEqual(case.detail["table"]["M1"]["token_reuse"]["status"], mechanisms.ENDED)
        self.assertIn("only a rate limit", " ".join(problems))

    def test_an_ended_client_session_ends_only_its_case(self) -> None:
        run, server, world, clock = family_run()
        original = world.behaviour
        calls = {"n": 0}

        def ends(session: Any, op: str, params: dict[str, Any]) -> Any:
            # As ClientSession: once ended, the session sends nothing more.
            if getattr(session, "ended", None):
                raise ClientSessionEnded(f"client M1 was ended earlier; {op} not sent")
            if session.label == "M1" and params.get("method") == "updateMemberPartial":
                calls["n"] += 1
                if calls["n"] == 2:  # the write after the mechanism
                    session.ended = "no reply within 60s"
                    session.close()  # as ClientSession's end: its connection is closed
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
        # M1's session ended at its S15 write: that dimension and its subscription are
        # not shown; its REST read and token reuse were still judged, and the case was
        # interrupted at the undo, which needs M1's session (the independent review,
        # point 7).
        m1 = removal.detail["table"]["M1"]
        self.assertEqual(m1["s15"]["status"], mechanisms.NOT_SHOWN)
        self.assertIn("session ended", m1["s15"]["why"])
        self.assertEqual(m1["ws"]["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(m1["rest"]["status"], mechanisms.ENDED)
        self.assertEqual(m1["token_reuse"]["status"], mechanisms.ENDED)
        self.assertIn("ClientSessionEnded", removal.detail["interrupted"])
        # The family went on past the probe to the retention read.
        self.assertIn("after_probe", removal.detail)
        self.assertIn("retention", removal.detail)
        # The run went on to the next family, with a new M1 session, and cleaned up.
        self.assertNotEqual(row(run, "RV-ban").verdict, matrix.INCONCLUSIVE)
        self.assertEqual(problems, [])

    def test_an_interrupted_family_keeps_what_does_not_meet_the_policy(self) -> None:
        # The independent review, point 7: M1's read after the ban succeeds (not
        # ended), then a rate limit stops the run in the probe.
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
                run.run_matrix({"RV-ban"})
            run.finish(cleanup=True)
        case = row(run, "RV-ban")
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertIn("does not end rest for M1", case.reason)
        self.assertIn("GuardrailStop", case.detail["interrupted"])

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


class KeptStepsTest(unittest.TestCase):
    """P06.1-I2b, the I2a review's finding 1: an interruption inside a family step keeps
    that step's observations, so a member's "not ended" read seen before a stop stays in
    the row as DOES NOT MEET (never as a pass)."""

    ledger: UsageLedger

    def test_a_stop_inside_a_step_keeps_the_other_members_observation(self) -> None:
        # The review's scenario: RV-ban; M1's REST read after the ban succeeds (not
        # ended); a 402 then arrives on M2's read, in the same step.
        run, server, world, clock = family_run()
        self.ledger = run.ledger
        original = world.behaviour
        queries = {"M2": 0}

        def charge(session: Any, op: str, params: dict[str, Any]) -> Any:
            if session.label == "M2" and op == "call" and params.get("method") == "query":
                queries["M2"] += 1
                if queries["M2"] == 2:  # the read after the mechanism
                    raise self.ledger.stop_at_once(
                        "client M2: HTTP 402; stopping at once", rate_limited=False
                    )
            return original(session, op, params)

        world.behaviour = charge  # type: ignore[method-assign]
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"RV-ban"})
            run.finish(cleanup=True)
        case = row(run, "RV-ban")
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertIn("does not end rest for M1", case.reason)
        self.assertEqual(case.detail["table"]["M1"]["rest"]["status"], mechanisms.NOT_ENDED)
        self.assertEqual(case.detail["after"]["M1"]["rest"], "201 (succeeded)")
        self.assertIn("GuardrailStop", case.detail["interrupted"])

    def test_a_stop_after_the_mechanisms_request_keeps_the_row_as_applied(self) -> None:
        # A rate limit on the channel read right after the ban was applied: the row
        # says the mechanism was applied, not "controls made; not yet applied".
        reads = {"n": 0}

        def limited(method: str, path: str, body: Any, params: Any) -> Any:
            if method == "POST" and path == "/api/v2/chat/channels":
                cid = str(((body or {}).get("filter_conditions") or {}).get("cid", ""))
                if cid.endswith("-ch-ban"):
                    reads["n"] += 1
                    if reads["n"] == 2:  # the read after the mechanism was applied
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
                run.run_matrix({"RV-ban"})
            run.finish(cleanup=True)
        case = row(run, "RV-ban")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertTrue(case.observed.startswith("applied: 201"), case.observed)
        self.assertEqual(case.detail["apply"]["answer"], "201")
        self.assertIn("GuardrailStop", case.detail["interrupted"])

    def test_a_stop_in_the_retention_read_keeps_what_the_channel_showed(self) -> None:
        # The channel's first message is gone; a rate limit then stops the run in the
        # members read that follows the retention read. DOES NOT MEET is kept.
        def limited(method: str, path: str, body: Any, params: Any) -> Any:
            if method == "GET" and path == "/api/v2/chat/members" and "-ch-remove" in str(params):
                raise self.ledger.stop_at_once(
                    "server GET: HTTP 429; stopping at once", rate_limited=True
                )
            return None

        run, server, _, clock = family_run({"history_lost": True})
        self.ledger = run.ledger
        server.handlers.insert(0, limited)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"RV-remove"})
            run.finish(cleanup=True)
        case = row(run, "RV-remove")
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertIn("not retained", case.reason)
        self.assertIn("GuardrailStop", case.detail["interrupted"])


class Missing404Test(unittest.TestCase):
    """P06.1-I2b: a 404 code 16 counts as ended only under the three conditions the
    manager decided and the I2a review refined."""

    def test_the_rule(self) -> None:
        gone = Answer("not-found", 404, 16, record(404, {"code": 16, "message": "u1 was removed"}))
        ended = mechanisms.dimension(OK, gone, other_ok=True, missing="membership", uid="u1")
        self.assertEqual(ended["status"], mechanisms.ENDED)
        self.assertIn("u1 was removed", ended["why"])
        self.assertIn("the other member's identical request still succeeded", ended["why"])
        # Each condition on its own is not enough: the other member's request did not
        # succeed (or was not collected), the mechanism removes nothing the request
        # needs, the message names neither the membership nor the user, no control before.
        for kwargs in (
            {"other_ok": False, "missing": "membership", "uid": "u1"},
            {"other_ok": None, "missing": "membership", "uid": "u1"},
            {"other_ok": True, "missing": None, "uid": "u1"},
        ):
            shown = mechanisms.dimension(OK, gone, **kwargs)
            self.assertEqual(shown["status"], mechanisms.NOT_SHOWN, kwargs)
            self.assertIn("u1 was removed", shown["why"], kwargs)  # the message is kept
        unnamed = Answer("not-found", 404, 16, record(404, {"code": 16, "message": "nope"}))
        shown = mechanisms.dimension(OK, unnamed, other_ok=True, missing="membership", uid="u1")
        self.assertEqual(shown["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(
            mechanisms.dimension(DENIED, gone, other_ok=True, missing="user", uid="u1")["status"],
            mechanisms.NOT_SHOWN,
        )
        # Only Stream code 16, and only a 404.
        other_code = Answer("not-found", 404, 4, record(404, {"code": 4, "message": "u1 gone"}))
        self.assertEqual(
            mechanisms.dimension(OK, other_code, other_ok=True, missing="user", uid="u1")["status"],
            mechanisms.NOT_SHOWN,
        )
        # The message may name the missing thing by its noun instead of the ID.
        named = Answer(
            "not-found", 404, 16, record(404, {"code": 16, "message": "the user x was deactivated"})
        )
        self.assertEqual(
            mechanisms.dimension(OK, named, other_ok=True, missing="user", uid="u1")["status"],
            mechanisms.ENDED,
        )
        self.assertEqual(
            mechanisms.dimension(OK, named, other_ok=True, missing="membership", uid="u1")[
                "status"
            ],
            mechanisms.NOT_SHOWN,
        )
        # The token dimensions follow the same rule, on the connect and on the read.
        token = mechanisms.token_dimension(
            OK, OK, gone, None, other_ok=True, missing="user", uid="u1"
        )
        self.assertEqual(token["status"], mechanisms.ENDED)
        token = mechanisms.token_dimension(
            OK, OK, OK, gone, other_ok=True, missing="user", uid="u1"
        )
        self.assertEqual(token["status"], mechanisms.ENDED)
        self.assertEqual(
            mechanisms.token_dimension(
                OK, OK, gone, None, other_ok=False, missing="user", uid="u1"
            )["status"],
            mechanisms.NOT_SHOWN,
        )
        # The mechanisms it applies to: removal (the membership) and deactivation (the user).
        self.assertEqual(mechanisms.REMOVES, {"remove": "membership", "deactivate": "user"})

    def test_a_removed_members_own_write_404_ends_the_dimension(self) -> None:
        run, _, _, _ = run_families({"RV-remove"}, removed_member_write_404=True)
        case = row(run, "RV-remove")
        s15 = case.detail["table"]["M1"]["s15"]
        self.assertEqual(s15["status"], mechanisms.ENDED)
        self.assertIn("404 / code 16 after the membership was removed", s15["why"])
        self.assertIn("{M1} was removed: not a member of glow-match:{CH_remove}", s15["why"])
        # Stream's message is kept in the row, with the run's identifiers generalized.
        self.assertEqual(
            case.detail["after"]["M1"]["messages"]["s15"],
            "{M1} was removed: not a member of glow-match:{CH_remove}",
        )
        self.assertEqual(case.verdict, mechanisms.MEETS)

    def test_a_404_without_the_other_members_success_stays_not_shown(self) -> None:
        run, _, world, clock = family_run({"removed_member_write_404": True})
        original = world.behaviour
        writes = {"M2": 0}

        def other_fails(session: Any, op: str, params: dict[str, Any]) -> Any:
            if (
                session.label == "M2"
                and op == "call"
                and params.get("method") == "updateMemberPartial"
            ):
                writes["M2"] += 1
                if writes["M2"] == 2:  # M2's write after the mechanism
                    return world.reply(500, 0, response={"message": "internal"})
            return original(session, op, params)

        world.behaviour = other_fails  # type: ignore[method-assign]
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"RV-remove"})
            run.finish(cleanup=True)
        case = row(run, "RV-remove")
        s15 = case.detail["table"]["M1"]["s15"]
        self.assertEqual(s15["status"], mechanisms.NOT_SHOWN)
        self.assertIn("refusal not attributable (not-found)", s15["why"])
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_a_404_whose_message_names_nothing_stays_not_shown(self) -> None:
        run, _, _, _ = run_families(
            {"RV-remove"}, removed_member_write_404=True, missing_message="does not exist"
        )
        case = row(run, "RV-remove")
        s15 = case.detail["table"]["M1"]["s15"]
        self.assertEqual(s15["status"], mechanisms.NOT_SHOWN)
        self.assertIn("'does not exist'", s15["why"])
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_a_deactivated_users_404s_end_its_dimensions(self) -> None:
        run, _, _, _ = run_families({"SD-deactivate"}, deactivated_answers_404=True)
        case = row(run, "SD-deactivate")
        table = case.detail["table"]["S"]
        for dim in ("rest", "s15", "token_reuse", "token_issued_after"):
            self.assertEqual(table[dim]["status"], mechanisms.ENDED, dim)
            self.assertIn("404 / code 16 after the user was removed", table[dim]["why"], dim)
            self.assertIn("the user {S} was deactivated", table[dim]["why"], dim)
        messages = case.detail["after"]["S"]["messages"]
        self.assertEqual(messages["rest"], "the user {S} was deactivated")
        self.assertEqual(messages["token_reuse.connect"], "the user {S} was deactivated")
        self.assertEqual(messages["token_issued_after.connect"], "the user {S} was deactivated")
        self.assertEqual(case.detail["token_issued_after"]["connect"], "404 / code 16")
        self.assertEqual(case.verdict, mechanisms.MEETS)

    def test_a_404_after_another_mechanism_stays_not_shown(self) -> None:
        # The same 404 with the same message after a ban: the ban removes nothing the
        # write needs, so the rule does not apply.
        run, _, world, clock = family_run({"removed_member_write_404": True})
        original = world.behaviour

        def banned_404(session: Any, op: str, params: dict[str, Any]) -> Any:
            if (
                session.label == "M1"
                and op == "call"
                and params.get("method") == "updateMemberPartial"
                and world.banned.get(f"{run.prefix}-ch-ban")
            ):
                message = world.missing_message.format(uid=run.ctx["M1"], cid="x")
                return world.reply(404, 16, response={"code": 16, "message": message})
            return original(session, op, params)

        world.behaviour = banned_404  # type: ignore[method-assign]
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            run.run_matrix({"RV-ban"})
            run.finish(cleanup=True)
        s15 = row(run, "RV-ban").detail["table"]["M1"]["s15"]
        self.assertEqual(s15["status"], mechanisms.NOT_SHOWN)
        self.assertIn("refusal not attributable", s15["why"])


class KeptAfterTheIndependentCheckTest(unittest.TestCase):
    """P06.1-I2b, the independent check's findings 1 and 2: what a family observed is kept
    when a stop falls inside the member's own undo or inside the probe's collection."""

    def test_the_members_own_undo_is_kept_when_the_replay_stops(self) -> None:
        run, server, _world, clock = family_run()

        def charged_replay(method: str, path: str, body: Any, params: dict[str, str] | None) -> Any:
            # The server's replay of the member's own show (its body names the user).
            if method == "POST" and path.endswith("/show") and (body or {}).get("user_id"):
                raise server.ledger.stop_at_once(
                    "server POST show: HTTP 402; stopping at once", rate_limited=False, billing=True
                )
            return None

        server.handlers.insert(0, charged_replay)
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"RV-hide"})
        kept = row(run, "RV-hide")
        undo = kept.detail["client_undo"]
        self.assertTrue(undo["verdict"].startswith(matrix.FAIL), undo)
        self.assertEqual(undo["control"], "not completed")
        self.assertEqual(undo["answer"], "201 (succeeded)")
        self.assertEqual(kept.verdict, matrix.FALLS_SHORT)
        self.assertIn("client undo: FAIL", kept.observed)

    def test_an_earlier_sessions_probe_is_kept_when_a_later_collection_stops(self) -> None:
        run, server, _world, clock = family_run()
        original = run._session
        seen_after: list[str] = []

        def stopping_second(label: str, token: str | None, **kwargs: Any) -> Any:
            session: Any = original(label, token, **kwargs)  # a FakeSession
            inner = session.behaviour

            def behaviour(sess: Any, op: str, params: dict[str, Any]) -> Any:
                if op == "events" and any(World.is_after_probe(e) for e in sess.pending_events):
                    seen_after.append(sess.label)
                    if len(seen_after) == 2:
                        # The second session's collection of the after-probe window: a
                        # signal in a background request's answer.
                        raise server.ledger.stop_at_once(
                            f"client {sess.label}: HTTP 402; stopping at once",
                            rate_limited=False,
                            billing=True,
                        )
                return inner(sess, op, params) if inner is not None else None

            session.behaviour = behaviour
            return session

        run._session = stopping_second  # type: ignore[method-assign]
        with NoSettle(), clock:
            run.setup()
            run.authorized_path()
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"RV-freeze"})
        kept = row(run, "RV-freeze")
        first, second = seen_after
        table = kept.detail["table"]
        # The first session's window was collected and shows the probe received: its
        # subscription is "not ended"; the second's could not be collected.
        self.assertEqual(table[first]["ws"]["status"], mechanisms.NOT_ENDED, table[first]["ws"])
        self.assertEqual(table[second]["ws"]["status"], mechanisms.NOT_SHOWN)
        self.assertEqual(kept.verdict, matrix.FALLS_SHORT)


class ListenerAndRetentionTest(unittest.TestCase):
    """P06.1-I2b, the I2a review's nit 3: the listener and the retention read."""

    def test_a_probe_that_reaches_no_session_leaves_the_subscription_not_shown(self) -> None:
        run, _, _, _ = run_families({"RV-remove"}, after_probe_lost=True)
        case = row(run, "RV-remove")
        ws = case.detail["table"]["M1"]["ws"]
        self.assertEqual(ws["status"], mechanisms.NOT_SHOWN)
        self.assertIn("no listener received the probe after the mechanism", ws["why"])
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("ws for M1", case.reason)

    def test_a_channel_whose_first_message_is_gone_does_not_meet_the_policy(self) -> None:
        run, _, _, _ = run_families({"RV-remove"}, history_lost=True)
        case = row(run, "RV-remove")
        retention = case.detail["retention"]
        self.assertTrue(retention["channel_exists"])
        self.assertFalse(retention["history_retained"])
        self.assertEqual(case.verdict, mechanisms.FALLS_SHORT)
        self.assertIn("the channel's messages are not retained", case.reason)


if __name__ == "__main__":
    unittest.main()
