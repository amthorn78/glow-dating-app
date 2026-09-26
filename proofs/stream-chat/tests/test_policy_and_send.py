import unittest
from dataclasses import dataclass, field
from typing import Any

import tests  # noqa: F401
from glow_stream_proof.app_send import AppSendService, ProviderUnavailable
from glow_stream_proof.policy import MatchState


@dataclass
class FakeResult:
    status: int
    body: dict[str, Any]


@dataclass
class FakeSender:
    calls: list[tuple[str, str, str, str]] = field(default_factory=list)

    def send_as(self, channel_type: str, channel_id: str, user_id: str, text: str) -> FakeResult:
        self.calls.append((channel_type, channel_id, user_id, text))
        return FakeResult(201, {"message": {"id": f"m{len(self.calls)}"}})


def state() -> MatchState:
    s = MatchState()
    s.add_match("a", "b", "ab")
    s.add_match("x", "d", "xd")
    return s


class PolicyTest(unittest.TestCase):
    def test_authorized_for_both_members(self) -> None:
        s = state()
        self.assertEqual(s.send_decision("a", "ab", "hi").reason, "authorized")
        self.assertEqual(s.send_decision("b", "ab", "hi").recipient, "a")

    def test_refusals(self) -> None:
        s = state()
        self.assertEqual(s.send_decision("a", "xd", "hi").reason, "not_a_participant")
        self.assertEqual(s.send_decision("a", "ax", "hi").reason, "no_current_match")
        self.assertEqual(s.send_decision("a", "ab", "  ").reason, "empty_text")
        s.block("b", "a")
        self.assertEqual(s.send_decision("a", "ab", "hi").reason, "blocked")
        self.assertEqual(s.send_decision("b", "ab", "hi").reason, "blocked")
        s.unmatch("xd")
        self.assertEqual(s.send_decision("x", "xd", "hi").reason, "no_current_match")

    def test_self_match_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MatchState().add_match("a", "a", "aa")


class AppSendTest(unittest.TestCase):
    def test_authorized_send_calls_stream_as_the_user(self) -> None:
        sender = FakeSender()
        outcome = AppSendService(state(), sender, "glow-match").send("a", "ab", "hello")
        self.assertTrue(outcome.stream_called)
        self.assertEqual(outcome.message_id, "m1")
        self.assertEqual(sender.calls, [("glow-match", "ab", "a", "hello")])

    def test_refused_send_never_calls_stream(self) -> None:
        sender = FakeSender()
        service = AppSendService(state(), sender, "glow-match")
        for sender_id, channel in (("a", "xd"), ("a", "ax"), ("d", "ab")):
            outcome = service.send(sender_id, channel, "hello")
            self.assertFalse(outcome.decision.allowed)
            self.assertFalse(outcome.stream_called)
        blocked = state()
        blocked.block("a", "b")
        outcome = AppSendService(blocked, sender, "glow-match").send("a", "ab", "hello")
        self.assertEqual(outcome.decision.reason, "blocked")
        self.assertEqual(sender.calls, [])

    def test_an_unreachable_provider_refuses_the_send_and_keeps_nothing(self) -> None:
        # P06.1-I2a, the outage injection: no answer at all is a refusal, not an error
        # that escapes, and the app keeps no message ID and no change of state.
        class Unreachable:
            def send_as(self, *_args: Any) -> Any:
                raise ProviderUnavailable("ConnectError: injected outage")

        s = state()
        before = (dict(s._channels), set(s._blocks))
        outcome = AppSendService(s, Unreachable(), "glow-match").send("a", "ab", "hello")
        self.assertTrue(outcome.decision.allowed)
        self.assertTrue(outcome.stream_called)
        self.assertIsNone(outcome.message_id)
        self.assertEqual(outcome.provider_error, "ConnectError: injected outage")
        self.assertFalse(outcome.sent)
        self.assertEqual((dict(s._channels), set(s._blocks)), before)


if __name__ == "__main__":
    unittest.main()
