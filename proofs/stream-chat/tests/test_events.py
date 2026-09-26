"""Finding 4 and nit 1: event views count only what Stream delivered.

The SDK's local events (a client's own query raises ``channels.queried`` with
the full queried state) are dropped, the event type that carried a marker is
recorded, and RT2 and RT3 search every event window they collect.
"""

import re
import subprocess
import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix
from glow_stream_proof.client_bridge import RUNNER, Reply
from glow_stream_proof.proof_run import CaseResult, ProofRun
from tests.fakes import FakeSession, NoSettle, make_run, record, set_up

SDK = RUNNER.parent.parent / "node_modules" / "stream-chat" / "dist" / "cjs" / "index.node.js"


def case_of(run: ProofRun, case_id: str) -> CaseResult:
    return next(c for c in run.case_results if c.case_id == case_id)


def member_custom_run(*, deliver_member_updated: bool) -> ProofRun:
    note: dict[str, str] = {}
    sessions: dict[str, FakeSession] = {}

    def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        if op == "call" and params.get("method") == "updateMemberPartial":
            value = params["args"][0]["set"].get("glow_note")
            if isinstance(value, str):
                note["value"] = value
                if deliver_member_updated:
                    sessions["B"].pending_events.append(
                        {"type": "member.updated", "member": {"custom": {"glow_note": value}}}
                    )
            return Reply(True, {}, None, [record(200, {"channel_member": {}})], api_calls=1)
        return None

    def b(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        sessions["B"] = session
        if op == "call" and params.get("method") == "query":
            state = {"members": [{"user_id": "a", "glow_note": note.get("value")}]}
            # The SDK's own local event, with the queried state (and so the marker).
            session.pending_events.append({"type": "channels.queried", "queriedChannels": state})
            session.pending_events.append({"type": "capabilities.changed", "cid": "x"})
            return Reply(True, {}, None, [record(201, {"channel": {}, **state})], api_calls=1)
        return None

    run, _server = make_run(behaviours={"A": a, "B": b})
    with NoSettle():
        set_up(run)
        run.run_matrix({"S15"})
    return run


class MemberCustomEventsTest(unittest.TestCase):
    def test_local_query_event_is_not_counted_as_delivered(self) -> None:
        case = case_of(member_custom_run(deliver_member_updated=False), "S15")
        views = case.detail["production_b_views"]
        self.assertTrue(views["channel_query_has_marker"])
        self.assertFalse(views["events_have_marker"])
        self.assertEqual(views["marker_event_types"], [])
        self.assertEqual(
            views["local_event_types_dropped"], ["capabilities.changed", "channels.queried"]
        )
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertEqual(case.reason, "response disclosed: B read it via channel_query")

    def test_the_event_type_that_carried_the_marker_is_recorded(self) -> None:
        case = case_of(member_custom_run(deliver_member_updated=True), "S15")
        views = case.detail["production_b_views"]
        self.assertEqual(views["marker_event_types"], ["member.updated"])
        self.assertIn("B read it via events (member.updated)", case.reason)


class PayloadWindowsTest(unittest.TestCase):
    def run_rt2(self, extra_event: dict[str, Any]) -> CaseResult:
        """A's typing event is accepted; ``extra_event`` reaches B only after the probe."""
        run, server = make_run()
        delivered = server.on_send
        assert delivered is not None
        armed: list[bool] = []

        def on_send(channel_id: str, message_id: str) -> None:
            # The next server send after A's request is the listener probe.
            delivered(channel_id, message_id)
            session = run.sessions.get("B")
            if armed and isinstance(session, FakeSession):
                session.pending_events.append(dict(extra_event))
                armed.clear()

        def a(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "sendEvent":
                extra_event["glow_text"] = params["args"][0]["glow_text"]
                armed.append(True)
                return Reply(True, {}, None, [record(201, {"event": {}})], api_calls=1)
            return None

        run.sessions["A"] = FakeSession("A", a)  # type: ignore[assignment]
        server.on_send = on_send
        with NoSettle():
            set_up(run)
            run.run_matrix({"RT2"})
        return case_of(run, "RT2")

    def test_marker_in_another_event_type_in_the_second_window_fails(self) -> None:
        case = self.run_rt2({"type": "channel.updated"})
        self.assertEqual(case.verdict, matrix.FAIL)
        self.assertIn("channel.updated", case.reason)

    def test_marker_only_in_a_local_event_is_not_delivered(self) -> None:
        case = self.run_rt2({"type": "channels.queried"})
        self.assertNotEqual(case.verdict, matrix.FAIL)
        self.assertEqual(case.detail["local_event_types_dropped"], ["channels.queried"])


class LocalEventTypesTest(unittest.TestCase):
    def test_every_local_event_the_sdk_declares_is_dropped(self) -> None:
        """The SDK's EVENT_MAP marks its local events; the harness drops each of them."""
        source = SDK.read_text(encoding="utf-8")
        block = source.split("var EVENT_MAP = {", 1)[1].split("};", 1)[0]
        local = block.split("// local events", 1)[1]
        declared = set(re.findall(r'"([a-z_.]+)": true', local))
        self.assertTrue(declared)
        self.assertLessEqual(declared, set(matrix.LOCAL_EVENT_TYPES))
        self.assertIn("health.check", matrix.LOCAL_EVENT_TYPES)
        version = subprocess.run(
            ["node", "-p", "require('./node_modules/stream-chat/package.json').version"],
            cwd=RUNNER.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
        self.assertEqual(version, "9.53.0")


if __name__ == "__main__":
    unittest.main()
