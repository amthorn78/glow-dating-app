"""P06.1-I2a: the cases besides the families (glow_stream_proof.i2a), against the fakes.

Each verdict branch is driven by scripted client replies and server handlers; the
fakes stand for what the live run records, not for Stream's behaviour.
"""

from __future__ import annotations

import json
import unittest
from typing import Any

import jwt

import tests  # noqa: F401
from glow_stream_proof import i2a, matrix, proof_run
from glow_stream_proof.app_send import ProviderUnavailable
from glow_stream_proof.client_bridge import ClientSessionEnded, Reply
from glow_stream_proof.proof_run import CaseResult, ProofRun
from glow_stream_proof.usage import GuardrailStop
from tests.fake_world import FakeClock, token_for
from tests.fakes import (
    AB,
    PREFIX,
    SECRET,
    FakeServer,
    FakeSession,
    NoSettle,
    error,
    http_reply,
    local_error,
    make_run,
    ok,
    record,
    set_up,
    ws_refused,
)
from tests.test_interruptions import matrix_run

A_ID, B_ID = f"{PREFIX}-ua", f"{PREFIX}-ub"


def only(run: ProofRun, case_id: str) -> CaseResult:
    return next(c for c in run.case_results if c.case_id == case_id)


def calls_to(method: str) -> Any:
    """A behaviour that counts the SDK calls to ``method`` and answers by count."""

    def make(answers: list[Reply]) -> Any:
        seen: list[int] = []

        def behaviour(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == method:
                seen.append(1)
                return answers[min(len(seen), len(answers)) - 1]
            return None

        return behaviour

    return make


class TokenExpiryTest(unittest.TestCase):
    def expiry(
        self,
        reads: list[Reply],
        reconnect: Reply,
        *,
        slow_watch_s: float = 0,
        token: Any = None,
    ) -> CaseResult:
        """TD-expiry on a fake clock: the case's token is issued at the clock's time and
        its wait for the expiry costs nothing."""
        connects: list[int] = []
        clock = FakeClock()

        def device(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                connects.append(1)
                if len(connects) > 1:
                    return reconnect
                return Reply(True, {"me": {"id": A_ID}}, None)
            if op == "call" and params.get("method") == "query":
                return reads.pop(0)
            if op == "call" and params.get("method") == "watch":
                clock.sleep(slow_watch_s)
                return http_reply(201)
            return None

        run, server = make_run(behaviours={"A-expiring": device})
        with NoSettle(), clock:
            set_up(run)
            server.user_token = token or (  # type: ignore[method-assign]
                lambda uid, ttl: token_for(uid, clock.time(), ttl)
            )
            run.run_matrix({"TD-expiry"})
        return only(run, "TD-expiry")

    def test_the_expired_token_is_refused(self) -> None:
        case = self.expiry([http_reply(201), http_reply(401, 40)], ws_refused(401, 40))
        self.assertEqual(case.verdict, matrix.HOLDS)
        self.assertEqual(case.detail["after_expiry"]["reconnect"], "401 / code 40")
        # The server SDK back-dates iat by 5 s.
        self.assertEqual(case.detail["expiry"]["exp_minus_iat_s"], i2a.EXPIRY_TTL_SECONDS + 5)
        self.assertIn("first device read", case.observed)

    def test_a_read_or_a_reconnect_after_expiry_is_a_fail(self) -> None:
        case = self.expiry([http_reply(201), http_reply(201)], ws_refused(401, 40))
        self.assertEqual(
            (case.verdict, case.reason), (matrix.FAIL, "the REST read succeeded after expiry")
        )
        case = self.expiry(
            [http_reply(201), http_reply(401, 40)], Reply(True, {"me": {"id": A_ID}}, None)
        )
        self.assertEqual(
            (case.verdict, case.reason), (matrix.FAIL, "the reconnection succeeded after expiry")
        )

    def test_no_control_or_no_attributable_refusal_is_inconclusive(self) -> None:
        case = self.expiry([http_reply(403, 17), http_reply(401, 40)], ws_refused(401, 40))
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        case = self.expiry([http_reply(201), http_reply(404, 16)], ws_refused(401, 40))
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("not attributable", case.reason)

    def test_controls_that_finish_too_close_to_the_expiry_are_inconclusive(self) -> None:
        # The independent review, a nit: the token's lifetime is 25 s; the watch takes 23.
        case = self.expiry(
            [http_reply(201), http_reply(401, 40)], ws_refused(401, 40), slow_watch_s=23
        )
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("within 3 s of the token's expiry", case.reason)
        self.assertLess(case.detail["before_expiry"]["read_done_s_before_exp"], 3)

    def test_a_token_without_an_expiry_is_inconclusive(self) -> None:
        def no_exp(uid: str, ttl: int) -> str:
            return jwt.encode({"user_id": uid, "iat": 0}, SECRET, "HS256")

        case = self.expiry(
            [http_reply(201), http_reply(401, 40)], ws_refused(401, 40), token=no_exp
        )
        self.assertEqual(
            (case.verdict, case.reason), (matrix.INCONCLUSIVE, "the token carries no expiry claim")
        )

    def test_the_second_devices_session_is_closed(self) -> None:
        with FakeClock():  # the wait for the expiry costs nothing
            run, _ = matrix_run({"TD-expiry"})
        self.assertNotIn("A-expiring", run.sessions)


class OutageTest(unittest.TestCase):
    def test_the_send_is_refused_and_nothing_is_kept(self) -> None:
        run, server = matrix_run({"OUT-send"})
        case = only(run, "OUT-send")
        self.assertEqual(case.verdict, matrix.HOLDS)
        detail = case.detail
        # The real server SDK ran its error path; the one request never left the process.
        self.assertEqual(
            detail["transport_attempts"], [f"POST /api/v2/chat/channels/glow-match/{AB}/message"]
        )
        self.assertIn("StreamTransportException", detail["app_send"]["provider_error"])
        self.assertIsNone(detail["app_send"]["message_id"])
        self.assertTrue(detail["state_unchanged"])
        self.assertIs(detail["message_found_server_side"], False)
        self.assertEqual(case.control, "the same send with the provider reachable: sent True")

    def test_a_message_found_server_side_is_a_fail(self) -> None:
        def found(_server: FakeServer, run: ProofRun) -> Any:
            def handler(method: str, path: str, body: Any, params: Any) -> Any:
                if path == "/api/v2/chat/channels" and "message_limit" in (body or {}):
                    return ok(
                        method, path, {"channels": [{"messages": [f"outage probe {PREFIX}"]}]}
                    )
                return None

            return handler

        run, _ = matrix_run({"OUT-send"}, handler=found)
        case = only(run, "OUT-send")
        self.assertEqual(
            (case.verdict, case.reason), (matrix.FAIL, "the refused send left state behind")
        )

    def test_a_path_that_raises_is_a_fail(self) -> None:
        saved = i2a._Sender.send_as

        def broken(self: Any, *args: Any) -> Any:
            raise ValueError("not a refusal")

        setattr(i2a._Sender, "send_as", broken)  # noqa: B010
        try:
            run, _ = matrix_run({"OUT-send"})
        finally:
            setattr(i2a._Sender, "send_as", saved)  # noqa: B010
        case = only(run, "OUT-send")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn("raised: ValueError", case.reason)

    def test_a_control_that_fails_is_inconclusive(self) -> None:
        def refused_control(server: FakeServer, run: ProofRun) -> Any:
            def send(type: str, id: str, message: Any) -> Any:
                raise ProviderUnavailable("the control could not reach it either")

            server.sdk.chat.send_message = send
            return lambda *_: None

        run, _ = matrix_run({"OUT-send"}, handler=refused_control)
        case = only(run, "OUT-send")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("control sent False", case.reason)


class MemberStore:
    """A's member record in AB, as the server stores it, for the S15 mapping and F9."""

    def __init__(self, applied: set[str], refused: set[str]) -> None:
        self.member: dict[str, Any] = {"user_id": A_ID, "channel_role": "channel_member"}
        self.applied = applied
        self.refused = refused
        self.server_writes: list[Any] = []
        self.restore_fails: set[str] = set()
        # How many server reads of the member record succeed; None: every one.
        self.reads_ok: int | None = None
        self.reads = 0
        # Every server write of the member record is refused (a reserved field).
        self.patch_refused = False

    def write(self, fields: dict[str, Any]) -> None:
        for key, value in fields.items():
            if key in ("pinned", "archived"):
                self.member[f"{key}_at"] = "2026-09-26T00:00:00Z" if value else None
            else:
                self.member[key] = value

    def client(self, session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        method = params.get("method")
        path = f"/channels/glow-match/{AB}/member"
        if op == "call" and method == "updateMemberPartial":
            fields = params["args"][0]["set"]
            field = next(iter(fields))
            if field in self.refused:
                return http_reply(403, 17, path=path)
            if field in self.applied:
                self.write(fields)
            return http_reply(200, response={"channel_member": {}}, path=path)
        if op == "call" and method in ("pin", "archive"):
            flag = "pinned" if method == "pin" else "archived"
            member_path = f"{path}/{A_ID}"
            if flag in self.refused:
                rec = record(403, {"code": 17}, path=member_path, method="PATCH")
                rec["body"] = {"set": {flag: True}}
                return Reply(
                    False, None, {"status": 403, "code": 17, "kind": "api"}, [rec], api_calls=1
                )
            if flag in self.applied:
                self.write({flag: True})
            return http_reply(200, response={"channel_member": {}}, path=member_path)
        return None

    def server(self, _server: FakeServer, _run: ProofRun) -> Any:
        def handler(method: str, path: str, body: Any, params: Any) -> Any:
            if path == "/api/v2/chat/members" and AB in str(params):
                self.reads += 1
                if self.reads_ok is not None and self.reads > self.reads_ok:
                    return error(method, path, 500, -1, "internal")
                return ok(method, path, {"members": [dict(self.member)]}, 200)
            if method == "PATCH" and path.startswith(f"/channels/glow-match/{AB}/member"):
                self.server_writes.append(body)
                if self.patch_refused:
                    return error(method, path, 400, 4, "reserved field")
                fields = dict((body or {}).get("set") or {})
                if any(k in self.restore_fails for k in fields):
                    return ok(method, path, {}, 200)  # accepted, never stored
                self.write(fields)
                for key in (body or {}).get("unset") or []:
                    self.member.pop(key, None)
                return ok(method, path, {"channel_member": {}}, 200)
            return None

        return handler


class S15MapTest(unittest.TestCase):
    def mapped(self, store: MemberStore, b: Any = None) -> tuple[ProofRun, CaseResult]:
        run, _ = matrix_run(
            {"S15-map"},
            after_setup={"A": store.client, **({"B": b} if b else {})},
            handler=store.server,
        )
        return run, only(run, "S15-map")

    def test_the_mapping_records_what_a_member_can_set(self) -> None:
        store = MemberStore(applied={"glow_note", "pinned", "archived"}, refused={"channel_role"})
        _, case = self.mapped(store)
        self.assertEqual(case.verdict, i2a.RECORDED)
        fields = case.detail["fields"]
        self.assertTrue(fields["glow_note"]["applied"])
        self.assertTrue(fields["pinned"]["applied"])
        self.assertFalse(fields["banned"]["applied"])  # accepted, not stored
        self.assertEqual(fields["channel_role"]["member_write"], "403 / code 17")
        # A refused write is replayed by the server: its control.
        self.assertEqual(fields["channel_role"]["server_control"], "200")
        self.assertTrue(fields["channel_role"]["applied_by_control"])
        # Every change is put back and verified.
        for name in ("glow_note", "pinned", "archived", "channel_role"):
            self.assertTrue(fields[name]["restored"].startswith("PATCH 200"), name)
            self.assertTrue(fields[name]["restored"].endswith("verified True"), name)
        # A write accepted but not stored needs nothing put back; the record is verified.
        self.assertEqual(fields["banned"]["restored"], "nothing to put back; verified True")
        self.assertEqual(store.member.get("channel_role"), "channel_member")
        self.assertIsNone(store.member.get("pinned_at"))
        self.assertNotIn("glow_note", store.member)
        self.assertIn("banned", case.observed)
        self.assertEqual(case.detail["server_overwrite"]["stored"], True)
        self.assertEqual(case.detail["server_clear"]["absent_after"], True)

    def test_a_restore_that_fails_stops_the_run_after_the_case(self) -> None:
        store = MemberStore(applied={"pinned"}, refused=set())
        store.restore_fails = {"pinned"}
        run, _ = matrix_run(
            {"S15-map", "F9-pin"},
            after_setup={"A": store.client},
            handler=store.server,
            raises=proof_run.RunStopped,
        )
        self.assertEqual([c.case_id for c in run.case_results], ["S15-map"])
        self.assertTrue(any("A's member record in AB is not as it was" in s for s in run.stops))
        self.assertIn("verified False", only(run, "S15-map").detail["fields"]["pinned"]["restored"])

    def test_nothing_is_put_back_for_a_field_that_was_never_changed(self) -> None:
        # A write accepted but ignored needs no restore, which Stream might refuse; the
        # record is still verified, and the run goes on.
        store = MemberStore(applied=set(), refused=set())
        store.patch_refused = True
        run, _ = matrix_run(
            {"S15-map", "F9-pin"}, after_setup={"A": store.client}, handler=store.server
        )
        self.assertEqual([c.case_id for c in run.case_results], ["S15-map", "F9-pin"])
        self.assertEqual(run.stops, [])
        self.assertEqual(len(store.server_writes), 2)  # only the server's overwrite and clear
        fields = only(run, "S15-map").detail["fields"]
        self.assertEqual(fields["is_moderator"]["restored"], "nothing to put back; verified True")

    def test_a_record_that_cannot_be_read_after_restoring_stops_the_run(self) -> None:
        store = MemberStore(applied={"glow_note"}, refused=set())
        store.reads_ok = 2  # the original record and the read after A's write
        run, _ = matrix_run(
            {"S15-map", "F9-pin"},
            after_setup={"A": store.client},
            handler=store.server,
            raises=proof_run.RunStopped,
        )
        self.assertEqual([c.case_id for c in run.case_results], ["S15-map"])
        self.assertTrue(any("could not be read after restoring" in s for s in run.stops))

    def test_a_field_the_control_set_is_restored_when_bs_session_ends(self) -> None:
        # The independent review's point 1: the control's replay set channel_role, then
        # B's session ended before the field was done; the field is still put back.
        store = MemberStore(applied=set(), refused={"channel_role"})

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "events" and store.member.get("channel_role") == "channel_moderator":
                raise ClientSessionEnded("client B ended: no reply within 60s")
            return None

        run, case = self.mapped(store, b)
        self.assertEqual(store.member.get("channel_role"), "channel_member")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("ClientSessionEnded", case.detail["interrupted"])
        entry = case.detail["fields"]["channel_role"]
        self.assertTrue(entry["applied_by_control"])
        self.assertTrue(entry["restored"].endswith("verified True"))
        self.assertEqual(run.stops, [])

    def test_nothing_is_sent_to_restore_after_a_guardrail_stop(self) -> None:
        store = MemberStore(applied={"glow_note"}, refused=set())

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                raise GuardrailStop("per-session budget reached: api_calls")
            return None

        run, _ = matrix_run(
            {"S15-map"},
            after_setup={"A": store.client, "B": b},
            handler=store.server,
            raises=GuardrailStop,
        )
        self.assertEqual(store.server_writes, [])  # no restore was sent
        entry = only(run, "S15-map").detail["fields"]["glow_note"]
        self.assertTrue(entry["restored"].startswith("not sent: a guardrail stopped the run"))

    def test_what_b_receives_is_recorded(self) -> None:
        store = MemberStore(applied={"glow_note"}, refused=set())

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "events":
                marker = f"s15map{PREFIX.replace('-', '')}"
                events = [
                    {"type": "member.updated", "member": {"user_id": A_ID, "glow_note": marker}}
                ]
                return Reply(True, {"events": events}, None)
            return None

        _, case = self.mapped(store, b)
        self.assertEqual(case.detail["fields"]["glow_note"]["b_event_types"], ["member.updated"])
        self.assertTrue(case.detail["fields"]["glow_note"]["b_events_carry_value"])


class OwnMemberFlagTest(unittest.TestCase):
    def flag(self, store: MemberStore, b: Any = None, case_id: str = "F9-pin") -> CaseResult:
        run, _ = matrix_run(
            {case_id},
            after_setup={"A": store.client, **({"B": b} if b else {})},
            handler=store.server,
        )
        return only(run, case_id)

    @staticmethod
    def b_reads(members: list[dict[str, Any]]) -> Any:
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                return http_reply(201, response={"members": members})
            return None

        return b

    def test_stored_and_not_shown_to_b_is_filtered(self) -> None:
        store = MemberStore(applied={"pinned"}, refused=set())
        case = self.flag(store, self.b_reads([{"user_id": A_ID}]))
        self.assertEqual(case.verdict, matrix.HOLDS_FILTERED)
        self.assertTrue(case.detail["restored"].endswith("verified True"))
        self.assertIsNone(store.member.get("pinned_at"))

    def test_a_b_read_without_as_member_record_is_inconclusive(self) -> None:
        # The independent review's point 5: a read that could not show the flag.
        case = self.flag(MemberStore(applied={"pinned"}, refused=set()), self.b_reads([]))
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("did not return A's member record", case.reason)

    def test_a_refused_b_read_is_inconclusive(self) -> None:
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                return http_reply(403, 17)
            return None

        case = self.flag(MemberStore(applied={"pinned"}, refused=set()), b)
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_a_stored_record_that_cannot_be_read_is_inconclusive(self) -> None:
        store = MemberStore(applied={"pinned"}, refused=set())
        store.reads_ok = 1  # only the original record
        run, _ = matrix_run(
            {"F9-pin"},
            after_setup={"A": store.client, "B": self.b_reads([{"user_id": A_ID}])},
            handler=store.server,
            raises=proof_run.RunStopped,
        )
        case = only(run, "F9-pin")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertEqual(case.reason, "A's member record could not be read after the write")
        self.assertTrue(any("could not be read after restoring" in s for s in run.stops))

    def test_a_leak_stays_a_fail_when_the_control_is_interrupted(self) -> None:
        # The independent review's point 7: the row keeps the FAIL and the restore's note.
        store = MemberStore(applied=set(), refused={"pinned"})
        leaked = self.b_reads([{"user_id": A_ID, "pinned_at": "2026-09-26T00:00:00Z"}])

        def server(fake: FakeServer, run: ProofRun) -> Any:
            inner = store.server(fake, run)

            def handler(method: str, path: str, body: Any, params: Any) -> Any:
                if method == "PATCH" and path.endswith(f"/member/{A_ID}"):
                    raise RuntimeError("the control could not be sent")
                return inner(method, path, body, params)

            return handler

        run, _ = matrix_run(
            {"F9-pin"}, after_setup={"A": store.client, "B": leaked}, handler=server
        )
        case = only(run, "F9-pin")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn("RuntimeError", case.detail["interrupted"])
        self.assertTrue(case.detail["restored"].endswith("verified True"))

    def test_an_unreadable_record_writes_nothing(self) -> None:
        store = MemberStore(applied={"pinned"}, refused=set())
        store.reads_ok = 0
        case = self.flag(store)
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("nothing was written", case.reason)
        self.assertIsNone(store.member.get("pinned_at"))

    def test_shown_to_b_is_a_fail(self) -> None:
        store = MemberStore(applied={"archived"}, refused=set())

        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                members = [{"user_id": A_ID, "archived_at": "2026-09-26T00:00:00Z"}]
                return http_reply(201, response={"members": members})
            return None

        case = self.flag(store, b, "F9-archive")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertEqual(case.reason, "B reads that A archived AB: B's channel query")

    def test_accepted_but_not_stored(self) -> None:
        case = self.flag(MemberStore(applied=set(), refused=set()))
        self.assertEqual(case.verdict, matrix.HOLDS_IGNORED)

    def test_a_refusal_holds_with_the_servers_replay(self) -> None:
        case = self.flag(MemberStore(applied=set(), refused={"pinned"}))
        self.assertEqual(case.verdict, matrix.HOLDS)
        self.assertEqual(case.control, "server replay PATCH -> 200")


class InviteTest(unittest.TestCase):
    def invite(self, b_reply: Reply, a_events: list[dict[str, Any]] | None = None) -> CaseResult:
        def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") in ("acceptInvite", "rejectInvite"):
                return b_reply
            return None

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "watch":
                return http_reply(201)
            if op == "events" and a_events is not None:
                return Reply(True, {"events": a_events}, None)
            return None

        run, _ = matrix_run({"F9-invite-accept"}, after_setup={"A": a, "B": b})
        return only(run, "F9-invite-accept")

    def test_a_refusal_holds_with_the_servers_replay(self) -> None:
        refused = http_reply(403, 17, path=f"/channels/glow-match/{PREFIX}-ch-in-accept")
        case = self.invite(refused)
        self.assertEqual(case.verdict, matrix.HOLDS)
        self.assertEqual(case.control, "server replay POST -> 201")

    def test_an_accepted_invite_with_a_message_is_a_fail(self) -> None:
        case = self.invite(http_reply(201))
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn("B's accept with a message succeeded", case.reason)

    def test_text_that_reaches_a_is_a_fail(self) -> None:
        text = f"invite accept text {PREFIX}"
        event = {"type": "message.new", "message": {"text": text}}
        case = self.invite(http_reply(403, 17), [event])
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn("the text reached A in message.new", case.reason)


class OracleTest(unittest.TestCase):
    def test_identical_refusals_hold(self) -> None:
        run, _ = matrix_run({"EO-message", "EO-channel", "EO-user"})
        for case_id in ("EO-message", "EO-channel", "EO-user"):
            case = only(run, case_id)
            self.assertEqual(case.verdict, matrix.HOLDS, case_id)

    def test_a_different_refusal_for_a_missing_id_is_an_oracle(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            args = params.get("args") or []
            if op == "call" and params.get("method") == "getMessage" and "none" in str(args):
                return http_reply(404, 16)
            return None

        run, _ = matrix_run({"EO-message"}, after_setup={"A": a})
        case = only(run, "EO-message")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn("an existence oracle: getMessage", case.reason)

    def test_the_ids_in_a_message_do_not_make_it_differ(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "getMessage":
                message_id = params["args"][0]
                return http_reply(403, 17, {"code": 17, "message": f"no access to {message_id}"})
            return None

        run, _ = matrix_run({"EO-message"}, after_setup={"A": a})
        self.assertEqual(only(run, "EO-message").verdict, matrix.HOLDS)

    def test_identical_input_errors_are_inconclusive(self) -> None:
        # The independent review, point 6: an input error may come before any
        # existence check, so identical ones show nothing.
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "getMessage":
                return http_reply(400, 4)
            return None

        run, _ = matrix_run({"EO-message"}, after_setup={"A": a})
        case = only(run, "EO-message")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("identical input errors", case.reason)

    def test_a_pair_without_an_answer_is_inconclusive(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "getMessage":
                return local_error()
            return None

        run, _ = matrix_run({"EO-message"}, after_setup={"A": a})
        case = only(run, "EO-message")
        self.assertEqual(case.verdict, matrix.INCONCLUSIVE)
        self.assertIn("not attributable", case.reason)

    def test_identical_404s_hold(self) -> None:
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "getMessage":
                return http_reply(404, 16)
            return None

        run, _ = matrix_run({"EO-message"}, after_setup={"A": a})
        self.assertEqual(only(run, "EO-message").verdict, matrix.HOLDS)

    def test_an_oracle_seen_before_an_interruption_stays_a_fail(self) -> None:
        # The independent review, point 7: the query pair differs; the run is then
        # stopped in the watch pair.
        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            method = params.get("method")
            if (
                op == "call"
                and method == "query"
                and params.get("id", "").endswith("-none-channel")
            ):
                return http_reply(404, 16)
            if op == "call" and method == "watch":
                raise GuardrailStop("per-session budget reached: api_calls")
            return None

        run, _ = matrix_run({"EO-channel"}, after_setup={"A": a}, raises=GuardrailStop)
        case = only(run, "EO-channel")
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn("an existence oracle: query", case.reason)

    def test_a_missing_channel_that_a_probe_created_is_counted_and_cleaned_up(self) -> None:
        def created(_server: FakeServer, run: ProofRun) -> Any:
            def handler(method: str, path: str, body: Any, params: Any) -> Any:
                cid = str(((body or {}).get("filter_conditions") or {}).get("cid"))
                if path == "/api/v2/chat/channels" and cid.endswith("-none-channel"):
                    return ok(method, path, {"channels": [{"channel": {"cid": cid}}]})
                return None

            return handler

        run, _ = matrix_run({"EO-channel"}, handler=created)
        cid = f"glow-match:{PREFIX}-none-channel"
        self.assertIn(cid, run.channels)
        self.assertEqual(run.ledger.run.channels, 3)
        self.assertIn("deleted at cleanup", json.dumps(only(run, "EO-channel").detail))


class S10SetupTest(unittest.TestCase):
    def s10(self, answers: list[Any]) -> tuple[ProofRun, FakeServer]:
        def factory(_server: FakeServer, _run: ProofRun) -> Any:
            def handler(method: str, path: str, body: Any, params: Any) -> Any:
                if path == f"/channels/glow-match/{PREFIX}-ch-s10/message":
                    return answers.pop(0) if len(answers) > 1 else answers[0]
                return None

            return handler

        return matrix_run({"S10"}, handler=factory)

    def test_the_poll_message_is_retried_until_polls_reach_the_channel(self) -> None:
        not_yet = error(
            "POST", "p", 403, 17, 'SendMessage failed: "polls not enabled for this channel"'
        )
        accepted = ok("POST", "p", {"message": {"id": "m-poll"}})
        run, server = self.s10([not_yet, not_yet, accepted])
        case = only(run, "S10")
        self.assertIn(f"glow-match:{PREFIX}-ch-s10", run.channels)
        self.assertEqual(run.ledger.run.channels, 3)
        sends = [c for c in server.calls if c[1].endswith("-ch-s10/message")]
        self.assertEqual(len(sends), 3)
        self.assertNotEqual(case.verdict, matrix.INCONCLUSIVE)

    def test_another_refusal_is_not_retried(self) -> None:
        run, server = self.s10([error("POST", "p", 400, 4, "bad poll")])
        sends = [c for c in server.calls if c[1].endswith("-ch-s10/message")]
        self.assertEqual(len(sends), 1)
        self.assertIn("after 1 attempt(s)", only(run, "S10").control)

    def test_the_retries_stop(self) -> None:
        not_yet = error("POST", "p", 403, 17, "polls not enabled for this channel")
        run, server = self.s10([not_yet])
        sends = [c for c in server.calls if c[1].endswith("-ch-s10/message")]
        self.assertEqual(len(sends), proof_run.S10_ATTEMPTS)
        self.assertEqual(only(run, "S10").verdict, matrix.INCONCLUSIVE)


class G2SetupTest(unittest.TestCase):
    def test_a_guest_the_application_will_not_create_is_not_run(self) -> None:
        run, server = make_run()

        def refuse(user: dict[str, Any]) -> Any:
            server._count("POST", "/guest", {"user": user})
            return error("POST", "/guest", 403, 17, "guest user creation is disabled"), None

        server.create_guest = refuse  # type: ignore[method-assign]
        with NoSettle():
            set_up(run)
            run.run_matrix({"G2-read-ab", "G2-users"})
        for case_id in ("G2-read-ab", "G2-users"):
            case = only(run, case_id)
            self.assertEqual(case.observed, "not run: no guest session")
            self.assertEqual(case.detail["g2_setup"]["result"], "no guest was created")
        # Tried once, with guest creation enabled for that moment, and restored.
        self.assertIn("verified", run.g2_setup["with_guest_creation_enabled"]["restored"])  # type: ignore[index]
        self.assertEqual(run.journal, [])
        self.assertEqual(run.ledger.run.users, 4)

    def test_any_refusal_is_tried_again_with_guest_creation_enabled(self) -> None:
        # Stream does not document which status it gives (the independent review, a nit).
        run, server = make_run()
        original = server.create_guest

        def refuse_with_400(user: dict[str, Any]) -> Any:
            if server.app.get("guest_user_creation_disabled") is True:
                server._count("POST", "/guest", {"user": user})
                return error("POST", "/guest", 400, 4, "guest user creation is disabled"), None
            return original(user)

        server.create_guest = refuse_with_400  # type: ignore[method-assign]
        with NoSettle():
            set_up(run)
            run.run_matrix({"G2-read-ab"})
        setup = run.g2_setup or {}
        self.assertEqual(setup["server_create"], "400 / code 4")
        self.assertEqual(setup["with_guest_creation_enabled"]["server_create"], "201")
        self.assertIn("verified", setup["with_guest_creation_enabled"]["restored"])
        self.assertEqual(run.journal, [])

    def test_a_guest_whose_connect_is_refused_is_not_run(self) -> None:
        def g2(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            return ws_refused(403, 17) if op == "connect" else None

        run, _ = matrix_run({"G2-read-ab"}, {"g2": g2})
        case = only(run, "G2-read-ab")
        self.assertEqual(case.observed, "not run: no guest session")
        self.assertEqual(case.detail["g2_setup"]["connect"], "403 / code 17")
        self.assertNotIn("g2", run.sessions)


class RunnerGetTest(unittest.TestCase):
    def test_the_get_op_goes_through_the_request_budget(self) -> None:
        from tests.test_runner import run_runner

        replies = run_runner(
            # A development token is made locally; nothing here is sent.
            {"id": 1, "op": "set_rest_user", "user_id": "u", "token_source": "dev", "max_calls": 0},
            {"id": 2, "op": "get", "path": "/channels/glow-match/x", "max_calls": 0},
        )
        reply = next(r for r in replies if r.get("id") == 2)
        self.assertFalse(reply["ok"])
        self.assertEqual(reply["error"]["kind"], "budget")
        self.assertEqual(reply["requests"], [])  # refused before sending


if __name__ == "__main__":
    unittest.main()
