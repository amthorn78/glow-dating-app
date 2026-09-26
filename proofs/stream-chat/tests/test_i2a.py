"""P06.1-I2a: the cases besides the families (glow_stream_proof.i2a), against the fakes.

Each verdict branch is driven by scripted client replies and server handlers; the
fakes stand for what the live run records, not for Stream's behaviour.
"""

from __future__ import annotations

import json
import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import i2a, matrix, proof_run
from glow_stream_proof.app_send import ProviderUnavailable
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.proof_run import CaseResult, ProofRun
from tests.fakes import (
    AB,
    PREFIX,
    FakeServer,
    FakeSession,
    NoSettle,
    error,
    http_reply,
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
    def expiry(self, reads: list[Reply], reconnect: Reply) -> CaseResult:
        connects: list[int] = []

        def device(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                connects.append(1)
                if len(connects) > 1:
                    return reconnect
                return Reply(True, {"me": {"id": A_ID}}, None)
            if op == "call" and params.get("method") == "query":
                return reads.pop(0)
            if op == "call" and params.get("method") == "watch":
                return http_reply(201)
            return None

        run, _ = matrix_run({"TD-expiry"}, {"A-expiring": device})
        return only(run, "TD-expiry")

    def test_the_expired_token_is_refused(self) -> None:
        case = self.expiry([http_reply(201), http_reply(401, 40)], ws_refused(401, 40))
        self.assertEqual(case.verdict, matrix.HOLDS)
        self.assertEqual(case.detail["after_expiry"]["reconnect"], "401 / code 40")
        self.assertEqual(case.detail["expiry"]["lifetime_s"], i2a.EXPIRY_TTL_SECONDS)
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

    def test_the_second_devices_session_is_closed(self) -> None:
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
                return ok(method, path, {"members": [dict(self.member)]}, 200)
            if method == "PATCH" and path.startswith(f"/channels/glow-match/{AB}/member"):
                self.server_writes.append(body)
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
            self.assertTrue(fields[name]["restored"].endswith("verified True"), name)
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
        self.assertTrue(any("member field pinned was not restored" in s for s in run.stops))

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

    def test_stored_and_not_shown_to_b_is_filtered(self) -> None:
        case = self.flag(MemberStore(applied={"pinned"}, refused=set()))
        self.assertEqual(case.verdict, matrix.HOLDS_FILTERED)
        self.assertTrue(case.detail["restored"].endswith("verified True"))

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
