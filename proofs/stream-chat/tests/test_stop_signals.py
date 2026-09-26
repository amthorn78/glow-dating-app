"""P06.1-C3: a charge or limit signal met anywhere in the run stops the cleanup.

The C2 review's finding 2: the run records every charge or limit signal it meets
(HTTP 402 or 429, Stream code 9 or 99, or charge wording), wherever it meets it,
and ``finish()`` then restores and re-reads the configuration but deletes nothing.
Nit 6: B's probe stop is kept when a key still reads as overridden. Nit 7: after
a guardrail stop, S15 sends no unset of A's member field. The independent review
of P06.1-C3: a signal whose stop is replaced in flight is still recorded, because
the server client and every client session record it in the run's ledger as they
raise it.
"""

import unittest
from typing import Any
from unittest import mock

import tests  # noqa: F401
from glow_stream_proof import configuration
from glow_stream_proof.client_bridge import ClientSessionEnded, Reply
from glow_stream_proof.proof_run import ProofRun, RunStopped
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import GuardrailStop, UsageLedger
from tests.fakes import Behaviour, FakeServer, FakeSession, NoSettle, make_run, set_up
from tests.test_interruptions import matrix_run, only, success

MATCH_PATH = f"/api/v2/chat/channeltypes/{configuration.MATCH_TYPE}"
BUDGET = "guardrail: api_calls would be passed; stopping before the call"


def charge(where: str = "server PUT /x") -> GuardrailStop:
    return GuardrailStop(f"{where}: HTTP 402; stopping at once", at_once=True)


def rate_limit(where: str = "server PUT /x") -> GuardrailStop:
    return GuardrailStop(f"{where}: HTTP 429; stopping at once", rate_limited=True)


def deletes(server: FakeServer) -> list[str]:
    return [path for _method, path, _body in server.calls if path.endswith("/delete")]


def charged_on_connect(ledger: UsageLedger, label: str) -> Behaviour:
    """A client session that meets HTTP 402 on connect, and raises its stop as the real
    session does: through the run's ledger, which records it first."""

    def behaviour(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        if op == "connect":
            raise ledger.stop_at_once(
                f"client {label}: HTTP 402; stopping at once", rate_limited=False
            )
        return None

    return behaviour


class SignalRecordTest(unittest.TestCase):
    def test_a_signal_behind_another_stop_skips_the_cleanup(self) -> None:
        # The review's variant: a budget stop is in flight when S12's restore meets a
        # charge signal. _temporary keeps the budget stop as the run's stop; the
        # signal is recorded all the same, and nothing of the run's is deleted.
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                raise GuardrailStop(BUDGET)
            return None

        def charge_on_restore(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if (
                method == "PUT"
                and path == MATCH_PATH
                and (body or {}).get("custom_events") is False
            ):
                raise charge(f"server PUT {MATCH_PATH}")
            return None

        run, server = make_run()
        with NoSettle():
            set_up(run)
            session = run.sessions["A"]
            assert isinstance(session, FakeSession)
            session.behaviour = a
            server.handlers.append(charge_on_restore)
            with self.assertRaises(GuardrailStop) as stopped:
                run.run_matrix({"S12"})
            self.assertFalse(stopped.exception.at_once)  # the budget stop is the run's stop
            problems = run.finish(cleanup=True)
        self.assertEqual(deletes(server), [])
        self.assertEqual(run.cleanup_result, {})
        self.assertTrue(
            any(p.startswith("cleanup skipped: a charge or limit signal") for p in problems)
        )
        self.assertEqual(len(run.stop_signals), 1)
        self.assertIn("HTTP 402", run.stop_signals[0])
        # The restore was still tried at the end, and the configuration re-read.
        self.assertFalse(any(p.startswith("configuration not verified") for p in problems))

    def test_a_signal_met_during_cleanup_ends_it_and_is_recorded(self) -> None:
        run, server = make_run()
        with NoSettle():
            set_up(run)

        def rate_limited_delete(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if path == "/api/v2/chat/channels/delete":
                raise rate_limit("server POST /api/v2/chat/channels/delete")
            return None

        server.handlers.append(rate_limited_delete)
        with NoSettle():
            out = run.cleanup()
        self.assertNotIn("users_delete", out)  # nothing more is sent after the signal
        self.assertEqual(deletes(server), ["/api/v2/chat/channels/delete"])
        self.assertEqual(len(run.stop_signals), 1)
        self.assertIn("HTTP 429", run.stop_signals[0])

    def test_a_signal_met_by_the_final_configuration_read_is_recorded(self) -> None:
        run, server = make_run()

        def rate_limited_read(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            if method == "GET" and path == "/api/v2/app":
                raise rate_limit("server GET /api/v2/app")
            return None

        server.handlers.append(rate_limited_read)
        with NoSettle():
            problems = run.finish(cleanup=False)
        self.assertTrue(any(p.startswith("configuration not verified") for p in problems))
        self.assertEqual(len(run.stop_signals), 1)

    def test_a_budget_stop_is_not_a_charge_or_limit_signal(self) -> None:
        run, _server = make_run()
        run.record_signal(GuardrailStop(BUDGET))
        run.record_signal(RuntimeError("HTTP 402"))
        self.assertEqual(run.stop_signals, [])
        run.record_signal(charge())
        run.record_signal(charge())  # the same signal is recorded once
        self.assertEqual(run.stop_signals, ["server PUT /x: HTTP 402; stopping at once"])


class SignalReplacedInFlightTest(unittest.TestCase):
    """The independent review of P06.1-C3: E5's own client session meets a charge
    signal, and its stop is replaced while E5's ``finally`` closes that session."""

    def e5_run(self, replacement: BaseException) -> tuple[ProofRun, FakeServer]:
        ledger = UsageLedger()
        run, server = make_run(
            behaviours={"A-role": charged_on_connect(ledger, "A-role")}, ledger=ledger
        )
        real_close = FakeSession.close
        replaced: list[BaseException] = []

        def close(session: FakeSession) -> None:
            if session.label == "A-role" and not replaced:
                replaced.append(replacement)
                raise replacement
            real_close(session)

        patcher = mock.patch.object(FakeSession, "close", close)
        patcher.start()
        self.addCleanup(patcher.stop)
        return run, server

    def test_a_ctrl_c_that_replaces_the_stop_still_skips_the_cleanup(self) -> None:
        run, server = self.e5_run(KeyboardInterrupt())
        with NoSettle():
            set_up(run)
            with self.assertRaises(KeyboardInterrupt):
                run.run_matrix({"E5", "C1"})
            problems = run.finish(cleanup=True)
        self.assertEqual(run.stop_signals, ["client A-role: HTTP 402; stopping at once"])
        self.assertEqual(deletes(server), [])
        self.assertEqual(run.cleanup_result, {})
        self.assertTrue(
            any(p.startswith("cleanup skipped: a charge or limit signal") for p in problems)
        )

    def test_an_error_that_replaces_the_stop_still_stops_the_run(self) -> None:
        # After an ordinary error the run goes on to the next case; after a signal it
        # must not, so the run stops once E5's row is recorded.
        run, server = self.e5_run(ValueError("I/O operation on closed file"))
        with NoSettle():
            set_up(run)
            with self.assertRaises(RunStopped) as stopped:
                run.run_matrix({"E5", "C1"})
            problems = run.finish(cleanup=True)
        self.assertEqual(
            str(stopped.exception),
            "after E5: a charge or limit signal was met "
            "(client A-role: HTTP 402; stopping at once)",
        )
        self.assertEqual([c.case_id for c in run.case_results], ["E5"])  # C1 not started
        self.assertEqual(deletes(server), [])
        self.assertTrue(
            any(p.startswith("cleanup skipped: a charge or limit signal") for p in problems)
        )


class ProbeStopKeptTest(unittest.TestCase):
    """The C2 review's nit 6: B's probe stop is kept when a key still reads as overridden."""

    def test_a_probe_stop_is_kept_and_its_signal_recorded(self) -> None:
        # Two keys: Stream keeps replies after the removal, and B's probe for the grant
        # meets a rate limit. Until P06.1-C3 the rate limit appeared nowhere.
        override = {"replies": True, "grants": {"channel_member": ["read-channel-members"]}}

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "queryMembers":
                raise rate_limit("client B")
            return None

        run, server = make_run(behaviours={"B": b})
        server.config_has_grants = False

        def keep_replies(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                server.overrides[run.ctx["AB"]] = {"replies": True}
                return ApiResult(method, path, 200, None, None, {})
            return None

        with NoSettle():
            set_up(run)
            server.handlers.append(keep_replies)
            change = run._channel_override_change(override)
            with self.assertRaises(RunStopped), run._temporary(change):
                run._set_channel_override(change, override)
        self.assertEqual(run.journal, [change])  # still owed
        self.assertIn(
            "B's members query after AB's override removal: client B: HTTP 429; stopping at once",
            run.stops,
        )
        self.assertEqual(run.stop_signals, ["client B: HTTP 429; stopping at once"])


class MemberFieldUnsetTest(unittest.TestCase):
    """The C2 review's nit 7: after a guardrail stop, S15 sends no unset of A's member
    field; cleanup (after a charge or limit signal, cleanup --apply) deletes A."""

    @staticmethod
    def unsets(server: FakeServer) -> list[Any]:
        return [
            c
            for c in server.calls
            if c[0] == "PATCH" and c[1].endswith("/member") and (c[2] or {}).get("unset")
        ]

    @staticmethod
    def a_writes(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        if op == "call" and params.get("method") == "updateMemberPartial":
            return success({}, "/channels/glow-match/x/member")
        return None

    def test_no_unset_after_a_guardrail_stop_in_bs_reads(self) -> None:
        # The review's reproduction: B's query answered 402.
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                raise charge("client B")
            return None

        run, server = matrix_run(
            {"S15", "S16"},
            after_setup={"A": self.a_writes, "B": b},
            raises=GuardrailStop,
        )
        self.assertEqual(self.unsets(server), [])
        self.assertEqual([c.case_id for c in run.case_results], ["S15"])
        self.assertTrue(
            any(n.startswith("S15: A's member field not unset: not sent") for n in run.notes)
        )

    def test_no_unset_after_a_guardrail_stop_in_the_control(self) -> None:
        # A's control write meets a rate limit: the grant, a journalled change, is still
        # restored, but A's member field is not unset again.
        writes: list[int] = []

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "updateMemberPartial":
                writes.append(1)
                if len(writes) == 2:
                    raise rate_limit("client A")
            return self.a_writes(session, op, params)

        run, server = matrix_run({"S15"}, after_setup={"A": a}, raises=GuardrailStop)
        self.assertEqual(len(self.unsets(server)), 1)  # after the production reads only
        self.assertEqual(server.overrides[run.ctx["AB"]], {})  # the grant was removed
        self.assertTrue(only(run, "S15").detail["member_field_unset"].startswith("not sent"))

    def test_no_unset_after_a_signal_whose_stop_is_not_in_flight(self) -> None:
        # The independent review of P06.1-C3 (latent: S15's override has one key
        # today). B's probe after the removal meets a rate limit while another key
        # still reads as overridden, so RunStopped is in flight, not the signal's
        # stop. The signal was recorded where it was met; nothing more is sent.
        override = {"replies": True, "grants": {"channel_member": ["read-channel-members"]}}
        member_queries: list[int] = []
        ledger = UsageLedger()

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "queryMembers":
                member_queries.append(1)
                if len(member_queries) == 2:  # the probe after the removal
                    raise ledger.stop_at_once(
                        "client B: HTTP 429; stopping at once", rate_limited=True
                    )
            return None

        run, server = make_run(behaviours={"B": b}, ledger=ledger)
        server.config_has_grants = False

        def keep_replies(
            method: str, path: str, body: Any, params: dict[str, str] | None
        ) -> ApiResult | None:
            overrides = ((body or {}).get("set") or {}).get("config_overrides")
            if method == "PATCH" and overrides == {}:
                server.overrides[run.ctx["AB"]] = {"replies": True}
                return ApiResult(method, path, 200, None, None, {})
            return None

        out: dict[str, Any] = {}
        with NoSettle():
            set_up(run)
            server.handlers.append(keep_replies)
            change = run._channel_override_change(override)
            with self.assertRaises(RunStopped):
                run._member_control(change, override, "memberfreesimulated", out)
        self.assertEqual(len(member_queries), 2)
        self.assertEqual(run.stop_signals, ["client B: HTTP 429; stopping at once"])
        self.assertEqual(self.unsets(server), [])
        self.assertEqual(
            out["unset"],
            "not sent: a charge or limit signal was met (client B: HTTP 429; stopping at "
            "once); cleanup (after a charge or limit signal, cleanup --apply) deletes A",
        )

    def test_the_unset_is_still_sent_after_other_interruptions(self) -> None:
        # B's session ends during the control: not a guardrail stop, so the field is unset.
        queries: list[int] = []

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                queries.append(1)
                if len(queries) == 2:
                    raise ClientSessionEnded("client B ended: no reply within 60s")
            return None

        _run, server = matrix_run({"S15"}, after_setup={"A": self.a_writes, "B": b})
        self.assertEqual(len(self.unsets(server)), 2)


if __name__ == "__main__":
    unittest.main()
