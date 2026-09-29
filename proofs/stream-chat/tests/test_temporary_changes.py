"""Finding 2 and nit 4: temporary changes are journalled, restored and verified.

A failed restore stops the run; a restore failure never hides a guardrail stop
already in flight; undos and override removals are checked, and each removal is
re-read.
"""

import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import configuration, matrix
from glow_stream_proof.client_bridge import ClientSessionEnded, Reply
from glow_stream_proof.proof_run import (
    RunStopped,
    TemporaryChange,
    channel_shape,
    override_state,
)
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import GuardrailStop, UsageLedger
from tests.fakes import FakeSession, NoSettle, error, make_run, record, set_up

MATCH_PATH = f"/api/v2/chat/channeltypes/{configuration.MATCH_TYPE}"


def is_restore_put(method: str, path: str, body: Any, feature: str) -> bool:
    return method == "PUT" and path == MATCH_PATH and (body or {}).get(feature) is False


class TypeFeatureRestoreTest(unittest.TestCase):
    def test_failed_restore_stops_the_run(self) -> None:
        run, server = make_run()

        def refuse_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if is_restore_put(method, path, body, "custom_events"):
                return error(method, path, 500, -1, "internal")
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_restore)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S12", "S13"})
        ids = [c.case_id for c in run.case_results]
        self.assertEqual(ids, ["S12"])  # S13 never ran
        row = run.case_results[0]
        self.assertEqual(row.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(row.reason, "the restore failed before the production phase")
        self.assertEqual(row.observed, "403 / code 17")  # what the case observed is kept
        self.assertIn("could not restore glow-match features", row.detail["run_stopped"])
        self.assertTrue(any("restore failed" in s for s in run.stops))
        self.assertEqual(len(run.journal), 1)  # still owed; finish() tries again

    def test_restore_that_reads_back_wrong_stops_the_run(self) -> None:
        run, server = make_run()

        def ignore_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if is_restore_put(method, path, body, "custom_events"):
                return ApiResult(method, path, 201, None, None, {})  # accepted, not applied
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(ignore_restore)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S12"})
        self.assertIs(server.match_type["custom_events"], True)

    def test_journal_entry_exists_before_the_enabling_request(self) -> None:
        # Ctrl-C arrives while the enabling PUT is in flight (after Stream applied it).
        run, server = make_run()

        def interrupt_enable(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "PUT" and path == MATCH_PATH and (body or {}).get("custom_events"):
                server.match_type["custom_events"] = True
                raise KeyboardInterrupt
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(interrupt_enable)
            with self.assertRaises(KeyboardInterrupt):
                run.run_matrix({"S12"})
        self.assertIs(server.match_type["custom_events"], False)
        self.assertEqual(run.journal, [])

    def test_guest_creation_is_restored_after_an_interrupt_before_the_control(self) -> None:
        run, server = make_run()
        base_session = run._session

        def interrupting_session(label: str, token: str | None, **kwargs: Any) -> Any:
            if label == "guest":
                raise KeyboardInterrupt  # during the settle wait or the session start
            return base_session(label, token, **kwargs)

        with NoSettle():
            set_up(run)
            run._session = interrupting_session  # type: ignore[method-assign]
            with self.assertRaises(KeyboardInterrupt):
                run.run_matrix({"G1-create"})
        self.assertIs(server.app["guest_user_creation_disabled"], True)
        self.assertEqual(run.journal, [])

    def test_restore_failure_does_not_hide_a_guardrail_stop_in_flight(self) -> None:
        ledger = UsageLedger()  # the stop is raised through it (P06.1-I2a; nit 6)

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                raise ledger.stop_at_once("client A: HTTP 429; stopping at once", rate_limited=True)
            return None

        run, server = make_run(behaviours={"A": a}, ledger=ledger)

        def refuse_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if is_restore_put(method, path, body, "custom_events"):
                return error(method, path, 500, -1, "internal")
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_restore)
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"S12"})
        text = " | ".join(run.stops)
        self.assertIn("restore failed", text)
        self.assertIn("GuardrailStop", text)
        self.assertIn("HTTP 429", text)


class ChannelOverrideRemovalTest(unittest.TestCase):
    def test_removal_that_did_not_apply_stops_the_run(self) -> None:
        run, server = make_run()

        def keep_override(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                return ApiResult(method, path, 200, None, None, {})  # accepted, not applied
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(keep_override)
            with self.assertRaises(RunStopped) as stopped:
                run.run_matrix({"S2", "S3a"})
        self.assertIn("replies still reads as overridden", str(stopped.exception))
        self.assertEqual([c.case_id for c in run.case_results], ["S2"])

    def test_removal_refused_stops_the_run(self) -> None:
        run, server = make_run()

        def refuse_removal(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                server.overrides[run.ctx["AB"]] = {}  # applied, but answered with an error
                return error(method, path, 500, -1)
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_removal)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S5"})

    def test_removal_is_re_read(self) -> None:
        run, server = make_run()
        with NoSettle():
            set_up(run)
            run.run_matrix({"S2"})
        reads = [
            c
            for c in server.calls
            if c[1] == "/api/v2/chat/channels" and c[2].get("filter_conditions")
        ]
        self.assertEqual(len(reads), 2)  # while set, and after the removal
        self.assertIn("re-read", run.case_results[0].detail["feature_override"]["restored"])
        self.assertEqual(server.overrides[run.ctx["AB"]], {})

    def test_override_state(self) -> None:
        replies = ("replies", True)
        grant = ("grants", {"channel_member": ["read-channel-members"]})
        self.assertEqual(override_state({"config_overrides": {"replies": True}}, *replies), "set")
        self.assertEqual(override_state({"config_overrides": {}}, *replies), "clear")
        self.assertEqual(override_state({"config": {"replies": True}}, *replies), "set")
        self.assertEqual(override_state({"config": {"replies": False}}, *replies), "clear")
        self.assertEqual(override_state({"config": {}}, *replies), "unknown")
        self.assertEqual(override_state(None, *replies), "unknown")
        members = {"channel_member": ["read-channel", "read-channel-members"]}
        self.assertEqual(override_state({"config": {"grants": members}}, *grant), "set")
        plain = {"channel_member": ["read-channel"]}
        self.assertEqual(override_state({"config": {"grants": plain}}, *grant), "clear")
        self.assertEqual(override_state({"config": {}}, *grant), "unknown")
        shape = channel_shape({"cid": "x", "config": {"replies": False}})
        self.assertEqual(
            shape,
            {
                "read": True,
                "keys": ["cid", "config"],
                "config_keys": ["replies"],
                "has_config_overrides": False,
            },
        )


class OverrideReReadShapeTest(unittest.TestCase):
    """The I1 review's point 1: a re-read proves a removal only if it showed the override."""

    def test_re_read_that_never_shows_the_override_is_recorded_not_verified(self) -> None:
        run, server = make_run()
        server.merge_overrides = False  # the re-read shows the type's values only
        with NoSettle():
            set_up(run)
            run.run_matrix({"S2", "S3a"})  # the run goes on
            problems = run.finish(cleanup=False)
        self.assertEqual([c.case_id for c in run.case_results], ["S2", "S3a"])
        restored = run.case_results[0].detail["feature_override"]
        self.assertIn("not verified: ['replies']", restored["restored"])
        self.assertEqual(restored["reread"]["shown_while_set"], [])
        self.assertTrue(restored["reread"]["while_set"]["read"])
        self.assertEqual(len(run.unverified_restores), 1)
        self.assertTrue(any(p.startswith("temporary change not verified") for p in problems))

    def test_grant_not_shown_is_checked_by_b_being_refused_again(self) -> None:
        run, server = make_run()
        server.config_has_grants = False
        with NoSettle():
            set_up(run)
            run.run_matrix({"S15"})
        case = run.case_results[0]
        self.assertIn("B's members query refused again", case.control)
        self.assertEqual(run.unverified_restores, [])

    def test_grant_still_in_effect_stops_the_run(self) -> None:
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "queryMembers":
                return Reply(True, {}, None, [record(200, {"members": []})], api_calls=1)
            return None

        run, server = make_run(behaviours={"B": b})
        server.config_has_grants = False
        with NoSettle():
            set_up(run)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S15"})

    def test_grant_unverifiable_when_bs_session_has_ended(self) -> None:
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "queryMembers":
                raise ClientSessionEnded("client B ended: no reply within 60s")
            return None

        run, server = make_run(behaviours={"B": b})
        server.config_has_grants = False
        grant = {"grants": {"channel_member": ["read-channel-members"]}}
        with NoSettle():
            set_up(run)
            change = run._channel_override_change(grant)
            with run._temporary(change):
                run._set_channel_override(change, grant)
        self.assertIn("B's session had ended", change.note)
        self.assertEqual(len(run.unverified_restores), 1)


class UndoCheckTest(unittest.TestCase):
    def test_failed_undo_stops_the_run_after_its_case(self) -> None:
        run, server = make_run()

        def refuse_undo(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            text = ((body or {}).get("message") or {}).get("text")
            if method == "POST" and path.startswith("/messages/") and text == run.ctx["m_a_text"]:
                return error(method, path, 500, -1)
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_undo)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S3a", "S3b"})
        self.assertEqual([c.case_id for c in run.case_results], ["S3a"])
        self.assertIn("undo POST 500", run.case_results[0].control)
        self.assertTrue(any("undo POST" in s for s in run.stops))

    def test_member_field_unset_is_checked(self) -> None:
        run, server = make_run()

        def refuse_unset(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "PATCH" and path.endswith("/member") and (body or {}).get("unset"):
                return error(method, path, 500, -1)
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_unset)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S15", "S16"})
        self.assertEqual([c.case_id for c in run.case_results], ["S15"])


class FinishTest(unittest.TestCase):
    def test_finish_restores_the_journal_and_verifies_the_configuration(self) -> None:
        # After a charge signal (since P06.1-C3 from the run's record, not a reason
        # passed in) the journal is restored and nothing is deleted.
        run, server = make_run()
        restored: list[str] = []

        def restore() -> str:
            restored.append("x")
            return "done"

        change = TemporaryChange("a leftover change", restore)
        run.journal.append(change)
        run.record_signal(GuardrailStop("client A: HTTP 402; stopping at once", at_once=True))
        with NoSettle():
            problems = run.finish(cleanup=True)
        self.assertEqual(restored, ["x"])
        self.assertEqual(run.journal, [])
        self.assertEqual(
            problems,
            [
                "cleanup skipped: a charge or limit signal stopped the run at once (client A: "
                "HTTP 402; stopping at once); a charge signal: make no further live call, "
                "and report it"
            ],
        )
        self.assertFalse(any(path.endswith("/delete") for _m, path, _b in server.calls))
        server.app["guest_user_creation_disabled"] = False
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertIn(
            "configuration differs after the run: guest_user_creation_disabled is not true",
            problems,
        )

    def test_finish_reports_a_restore_it_cannot_make(self) -> None:
        run, _server = make_run()

        def fail() -> str:
            raise RunStopped("still on")

        run.journal.append(TemporaryChange("stuck change", fail))
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertTrue(any(p.startswith("temporary change not restored") for p in problems))
        self.assertEqual(run.results()["journal_not_restored"], ["stuck change"])


class KeptRowTest(unittest.TestCase):
    """The review's point 2: a failed restore keeps what the case had observed."""

    def test_fail_observed_before_a_failed_restore_stays_fail(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                return Reply(True, {}, None, [record(201, {"event": {}})], api_calls=1)
            return None

        run, server = make_run(behaviours={"A": a})

        def refuse_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if is_restore_put(method, path, body, "custom_events"):
                return error(method, path, 500, -1, "internal")
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_restore)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S12"})
        row = run.case_results[0]
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertIn("run_stopped", row.detail)

    def test_s15_leak_observed_before_a_failed_control_restore_stays_fail(self) -> None:
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                body = {"members": [{"glow_note": "memberfreep061i1simulated"}]}
                return Reply(True, {}, None, [record(201, body)], api_calls=1)
            return None

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "updateMemberPartial":
                return Reply(True, {}, None, [record(200, {})], api_calls=1)
            return None

        run, server = make_run(behaviours={"A": a, "B": b})

        def refuse_removal(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                return error(method, path, 500, -1)
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(refuse_removal)
            with self.assertRaises(RunStopped):
                run.run_matrix({"S15"})
        row = run.case_results[0]
        self.assertEqual(row.verdict, matrix.FAIL)
        self.assertIn("B read it via channel_query", row.reason)
        self.assertTrue(row.detail["production_b_views"]["channel_query_has_marker"])


class GuardedUnsetTest(unittest.TestCase):
    """The review's point 3: S15's unset never hides a guardrail stop in flight.

    Since P06.1-C3 no unset is sent after a guardrail stop, so the failing unset here
    is the production phase's, sent before the control's guardrail stop; its
    deferred stop must not replace that guardrail stop.
    """

    def test_guardrail_stop_survives_a_failing_unset(self) -> None:
        writes: list[int] = []
        ledger = UsageLedger()  # the stop is raised through it (P06.1-I2a; nit 6)

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "updateMemberPartial":
                writes.append(1)
                if len(writes) == 2:  # the control's write
                    raise ledger.stop_at_once(
                        "client A: HTTP 429; stopping at once", rate_limited=True
                    )
                return Reply(True, {}, None, [record(200, {})], api_calls=1)
            return None

        run, server = make_run(behaviours={"A": a}, ledger=ledger)

        def broken_unset(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "PATCH" and path.endswith("/member") and (body or {}).get("unset"):
                raise RuntimeError("connection reset")
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(broken_unset)
            with self.assertRaises(GuardrailStop):
                run.run_matrix({"S15", "S16"})
        # Since P06.1-C2 the stopped case keeps its row (S16 never ran).
        self.assertEqual([c.case_id for c in run.case_results], ["S15"])
        self.assertEqual(run.case_results[0].verdict, matrix.INCONCLUSIVE)
        self.assertTrue(any("unsetting A's member field raised" in s for s in run.stops))


class FinishRetryTest(unittest.TestCase):
    """The review's point 5: the end of the run tries a failed restore again."""

    def test_restore_is_retried(self) -> None:
        run, _server = make_run()
        attempts: list[int] = []

        def flaky() -> str:
            attempts.append(1)
            if len(attempts) < 3:
                raise RunStopped("HTTP 500")
            return "restored"

        run.journal.append(TemporaryChange("flaky change", flaky))
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertEqual(len(attempts), 3)
        self.assertEqual(run.journal, [])
        self.assertEqual(problems, [])

    def test_budget_stop_is_not_retried(self) -> None:
        run, _server = make_run()
        attempts: list[int] = []

        def budget() -> str:
            attempts.append(1)
            raise GuardrailStop("guardrail: api_calls would reach 5001 in this session")

        run.journal.append(TemporaryChange("budget change", budget))
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertEqual(len(attempts), 1)
        self.assertTrue(any("not restored" in p for p in problems))


class RateLimitRetryTest(unittest.TestCase):
    """P06.1-C2, the C1 review's nit 4: among stop signals, only a rate limit is retried."""

    def attempts_for(
        self, stop: GuardrailStop, ledger: UsageLedger | None = None
    ) -> tuple[int, list[str]]:
        run, _server = make_run(ledger=ledger)
        attempts: list[int] = []

        def stopped() -> str:
            attempts.append(1)
            raise stop

        run.journal.append(TemporaryChange("a change", stopped))
        with NoSettle():
            problems = run.finish(cleanup=False)
        return len(attempts), problems

    def test_a_charge_signal_is_not_retried(self) -> None:
        for message in ("HTTP 402", "Stream error code 99", "response text mentions a charge"):
            # Raised as production raises it, through the run's ledger (P06.1-I2a; nit 6).
            ledger = UsageLedger()
            stop = ledger.stop_at_once(
                f"server PATCH /x: {message}; stopping at once", rate_limited=False
            )
            count, problems = self.attempts_for(stop, ledger)
            self.assertEqual(count, 1, message)
            self.assertTrue(any("not restored" in p for p in problems))

    def test_a_rate_limit_is_retried(self) -> None:
        stop = GuardrailStop("server PATCH /x: HTTP 429; stopping at once", rate_limited=True)
        count, problems = self.attempts_for(stop)
        self.assertEqual(count, 3)
        self.assertTrue(any("not restored" in p for p in problems))

    def test_a_failure_that_is_not_a_stop_signal_is_still_retried(self) -> None:
        count, _problems = self.attempts_for_error(RunStopped("PUT 500"))
        self.assertEqual(count, 3)

    def attempts_for_error(self, exc: Exception) -> tuple[int, list[str]]:
        run, _server = make_run()
        attempts: list[int] = []

        def failing() -> str:
            attempts.append(1)
            raise exc

        run.journal.append(TemporaryChange("a change", failing))
        with NoSettle():
            problems = run.finish(cleanup=False)
        return len(attempts), problems


class UnverifiedRemovalTest(unittest.TestCase):
    """P06.1-C2, the C1 review's nit 9: an accepted removal that could not be verified
    is reported "not verified", not "not restored"."""

    GRANT = {"grants": {"channel_member": ["read-channel-members"]}}

    def run_with_budget_stopped_probe(self) -> tuple[Any, Any]:
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "queryMembers":
                raise GuardrailStop(
                    "guardrail: api_calls would be passed; stopping before the call"
                )
            return None

        run, server = make_run(behaviours={"B": b})
        server.config_has_grants = False  # the re-read cannot show the grant
        return run, server

    def test_at_the_end_of_the_run(self) -> None:
        run, server = self.run_with_budget_stopped_probe()
        with NoSettle():
            set_up(run)
            change = run._channel_override_change(self.GRANT)
            run.journal.append(change)
            run._set_channel_override(change, self.GRANT)  # then the run was stopped
            problems = run.finish(cleanup=False)
        self.assertEqual(server.overrides[run.ctx["AB"]], {})  # the removal was made
        self.assertEqual(run.journal, [])
        self.assertFalse(any("not restored" in p for p in problems), problems)
        verified = [p for p in problems if p.startswith("temporary change not verified")]
        self.assertEqual(len(verified), 1, problems)
        self.assertIn("B's members query could not be made", verified[0])
        self.assertTrue(any(s.startswith("restore made but not verified") for s in run.stops))

    def test_during_a_case(self) -> None:
        run, server = self.run_with_budget_stopped_probe()
        with NoSettle():
            set_up(run)
            change = run._channel_override_change(self.GRANT)
            with self.assertRaises(GuardrailStop), run._temporary(change):
                run._set_channel_override(change, self.GRANT)
            problems = run.finish(cleanup=False)
        self.assertEqual(run.journal, [])
        self.assertFalse(any("not restored" in p for p in problems), problems)
        self.assertTrue(any(p.startswith("temporary change not verified") for p in problems))


if __name__ == "__main__":
    unittest.main()
