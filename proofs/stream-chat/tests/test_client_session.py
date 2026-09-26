"""Finding 5: replies are matched to their commands.

A fake runner (a short Python script) stands in for ``client/runner.cjs``. A
mismatched reply, a timeout or an exit ends the session, and nothing more is
sent on it. A line the reader has already buffered is neither missed nor the
cause of a false timeout.
"""

import os
import sys
import time
import unittest

import tests  # noqa: F401
from glow_stream_proof.client_bridge import ClientSession, ClientSessionEnded
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.usage import GuardrailStop, UsageLedger

READ = "import json, sys\n"
EXIT = "    if json.loads(line).get('op') == 'exit':\n        break\n"
MISMATCH = READ + (
    "for line in sys.stdin:\n"
    "    cmd = json.loads(line)\n"
    "    print(json.dumps({'id': cmd['id'] + 100, 'ok': True}), flush=True)\n"
)
SILENT = READ + "for line in sys.stdin:\n" + EXIT
# The first command's reply and the second's arrive in one write.
BUFFERED = READ + (
    "line = sys.stdin.readline()\n"
    "sys.stdout.write(json.dumps({'id': 1, 'ok': True, 'data': 'first'}) + '\\n'"
    " + json.dumps({'id': 2, 'ok': True, 'data': 'second'}) + '\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n" + EXIT
)
EXITS = READ + "sys.stdin.readline()\nsys.exit(0)\n"
ECHO = READ + (
    "for line in sys.stdin:\n" + EXIT + "    cmd = json.loads(line)\n"
    "    print(json.dumps({'id': cmd['id'], 'ok': True}), flush=True)\n"
)


def session(script: str, ledger: UsageLedger, timeout: float = 5.0) -> ClientSession:
    return ClientSession(
        "fake",
        {"PATH": os.environ.get("PATH", "/usr/bin")},
        ledger,
        Redactor(),
        timeout_seconds=timeout,
        argv=[sys.executable, "-c", script],
    )


class ReplyMatchingTest(unittest.TestCase):
    def test_matching_reply_is_accepted(self) -> None:
        s = session(ECHO, UsageLedger())
        try:
            self.assertTrue(s.send("ping").ok)
            self.assertTrue(s.send("ping").ok)
        finally:
            s.close()

    def test_mismatched_reply_ends_the_session(self) -> None:
        s = session(MISMATCH, UsageLedger())
        try:
            with self.assertRaises(ClientSessionEnded) as ended:
                s.send("ping")
            self.assertIn("does not match command id 1", str(ended.exception))
            self.assertIsNotNone(s.ended)
            with self.assertRaises(ClientSessionEnded):
                s.send("ping")  # never sent: the session is over
        finally:
            s.close()

    def test_timeout_ends_the_session_and_releases_the_connection(self) -> None:
        ledger = UsageLedger()
        s = session(SILENT, ledger, timeout=0.5)
        try:
            with self.assertRaises(ClientSessionEnded) as ended:
                s.send("connect", user={"id": "u"})
            self.assertIn("no reply within", str(ended.exception))
            self.assertEqual(ledger.open_connections, 0)
            with self.assertRaises(ClientSessionEnded):
                s.send("ping")
        finally:
            s.close()

    def test_buffered_line_is_read_without_a_timeout(self) -> None:
        s = session(BUFFERED, UsageLedger(), timeout=1.0)
        try:
            self.assertEqual(s.send("ping").data, "first")
            started = time.monotonic()
            self.assertEqual(s.send("ping").data, "second")
            self.assertLess(time.monotonic() - started, 0.5)
        finally:
            s.close()

    def test_exited_runner_ends_the_session(self) -> None:
        s = session(EXITS, UsageLedger())
        try:
            with self.assertRaises(ClientSessionEnded) as ended:
                s.send("ping")
            self.assertIn("exited", str(ended.exception))
        finally:
            s.close()


def answering(status: int, code: int) -> str:
    """A fake runner whose every command records one request answered ``status`` / ``code``."""
    return READ + (
        "for line in sys.stdin:\n" + EXIT + "    cmd = json.loads(line)\n"
        "    request = {'method': 'GET', 'path': '/x', 'status': "
        + str(status)
        + ", 'response': {'code': "
        + str(code)
        + ", 'message': 'no'}}\n"
        "    print(json.dumps({'id': cmd['id'], 'ok': False, 'requests': [request],"
        " 'api_calls': 1, 'error': {'kind': 'api', 'status': "
        + str(status)
        + ", 'code': "
        + str(code)
        + "}}), flush=True)\n"
    )


def answering_without_a_request(status: int, code: int) -> str:
    """A fake runner whose every command fails with ``status`` / ``code`` and records no
    request (the check of the runner's error, not of a recorded request, raises)."""
    return READ + (
        "for line in sys.stdin:\n" + EXIT + "    cmd = json.loads(line)\n"
        "    print(json.dumps({'id': cmd['id'], 'ok': False, 'requests': [], 'api_calls': 0,"
        " 'error': {'kind': 'api', 'status': "
        + str(status)
        + ", 'code': "
        + str(code)
        + ", 'message': 'no'}}), flush=True)\n"
    )


class ClientRateLimitFlagTest(unittest.TestCase):
    """P06.1-C2, nit 4: a client's charge signal says whether it was a rate limit."""

    def stop_for(self, script: str, ledger: UsageLedger | None = None) -> GuardrailStop:
        s = session(script, ledger or UsageLedger())
        try:
            with self.assertRaises(GuardrailStop) as stopped:
                s.send("call")
        finally:
            s.close()
        return stopped.exception

    def test_flags(self) -> None:
        self.assertTrue(self.stop_for(answering(429, 9)).rate_limited)
        self.assertFalse(self.stop_for(answering(402, 4)).rate_limited)
        self.assertFalse(self.stop_for(answering(403, 99)).rate_limited)

    def test_the_error_only_check_flags_a_rate_limit(self) -> None:
        # P06.1-C3, the C2 review's nit 4: the second raise site had no test.
        self.assertTrue(self.stop_for(answering_without_a_request(429, 9)).rate_limited)
        self.assertFalse(self.stop_for(answering_without_a_request(402, 4)).rate_limited)

    def test_every_client_signal_stops_at_once(self) -> None:
        # P06.1-C3, finding 2: both raise sites mark the signal (402 is not a rate
        # limit) and record it in the run's ledger as they raise it.
        for script in (answering(402, 4), answering_without_a_request(402, 4)):
            ledger = UsageLedger()
            stop = self.stop_for(script, ledger)
            self.assertTrue(stop.at_once)
            self.assertEqual(ledger.signals, [stop])


def replying(extra: str) -> str:
    """A fake runner whose every command succeeds, its reply extended by ``extra`` (a
    Python dict literal), and whose exit is answered like the runner's (P06.1-I2a)."""
    return READ + (
        "for line in sys.stdin:\n"
        "    cmd = json.loads(line)\n"
        "    if cmd.get('op') == 'exit':\n"
        "        print(json.dumps({'id': 0, 'ok': True, 'background_requests': [],"
        " 'async_errors': []}), flush=True)\n"
        "        break\n"
        "    reply = {'id': cmd['id'], 'ok': True, 'requests': [], 'api_calls': 0}\n"
        "    reply.update(" + extra + ")\n"
        "    print(json.dumps(reply), flush=True)\n"
    )


def exiting_with(extra: str) -> str:
    """A fake runner whose exit reply is extended by ``extra``."""
    return READ + (
        "for line in sys.stdin:\n"
        "    cmd = json.loads(line)\n"
        "    if cmd.get('op') == 'exit':\n"
        "        reply = {'id': 0, 'ok': True, 'background_requests': [], 'async_errors': []}\n"
        "        reply.update(" + extra + ")\n"
        "        print(json.dumps(reply), flush=True)\n"
        "        break\n"
        "    print(json.dumps({'id': cmd['id'], 'ok': True}), flush=True)\n"
    )


BETWEEN_402 = (
    "{'background_requests': [{'method': 'POST', 'path': '/channels/delivered', 'status': 402,"
    " 'response': {'code': 4, 'message': 'no'}, 'background': True}], 'background_api_calls': 1}"
)
LATE_429 = (
    "{'background_requests': [{'method': 'GET', 'path': '/x', 'status': 429,"
    " 'response': {'code': 9, 'message': 'Too many requests'}, 'late': True}]}"
)
ASYNC_429_QUOTA = (
    "{'async_errors': [{'text': 'unhandledRejection: quota', 'kind': 'api', 'status': 429,"
    " 'code': 9, 'message': 'monthly quota exceeded'}]}"
)
ASYNC_BUDGET = (
    "{'async_errors': [{'text': 'unhandledRejection: PROOF_BUDGET', 'kind': 'budget',"
    " 'status': None, 'code': None,"
    " 'message': 'PROOF_BUDGET: request refused before sending (budget limit exceeded)'}]}"
)


class LateRequestsTest(unittest.TestCase):
    """P06.1-I2a, the C3 review's gap: every request a client session sends, between
    commands too, and every asynchronous SDK error, are checked for a charge or limit
    signal; a signal is recorded in the run's ledger and stops the run at once."""

    def stop_for(self, extra: str, ledger: UsageLedger) -> GuardrailStop:
        s = session(replying(extra), ledger)
        try:
            with self.assertRaises(GuardrailStop) as stopped:
                s.send("ping")
        finally:
            s.close()
        return stopped.exception

    def test_a_request_sent_between_commands(self) -> None:
        ledger = UsageLedger()
        stop = self.stop_for(BETWEEN_402, ledger)
        self.assertEqual(
            str(stop), "client fake: HTTP 402 (a request sent between commands); stopping at once"
        )
        self.assertTrue(stop.at_once)
        self.assertFalse(stop.rate_limited)
        self.assertEqual(ledger.signals, [stop])
        self.assertEqual(ledger.run.client_api_calls, 1)  # counted like any client call

    def test_an_answer_that_came_after_its_command_replied(self) -> None:
        ledger = UsageLedger()
        stop = self.stop_for(LATE_429, ledger)
        self.assertIn("(a request answered after its command replied)", str(stop))
        self.assertTrue(stop.only_rate_limit)
        self.assertEqual(ledger.signals, [stop])

    def test_an_asynchronous_sdk_error(self) -> None:
        ledger = UsageLedger()
        stop = self.stop_for(ASYNC_429_QUOTA, ledger)
        self.assertIn("(an asynchronous SDK error)", str(stop))
        self.assertTrue(stop.rate_limited)
        self.assertTrue(stop.billing)  # quota wording: not only a rate limit
        self.assertFalse(stop.only_rate_limit)

    def test_a_request_the_runner_refused_is_not_a_signal(self) -> None:
        ledger = UsageLedger()
        s = session(replying(ASYNC_BUDGET), ledger)
        try:
            reply = s.send("ping")
        finally:
            s.close()
        self.assertEqual(reply.async_errors, ["unhandledRejection: PROOF_BUDGET"])
        self.assertEqual(ledger.signals, [])


class ClosingSignalTest(unittest.TestCase):
    """What the exit reply reports is counted, noted and checked as the session closes."""

    def test_a_signal_at_exit_is_raised_when_nothing_else_is_in_flight(self) -> None:
        ledger = UsageLedger()
        notes: list[str] = []
        s = session(exiting_with(BETWEEN_402), ledger)
        s._note = notes.append
        s.send("ping")
        with self.assertRaises(GuardrailStop) as stopped:
            s.close()
        self.assertEqual(ledger.signals, [stopped.exception])
        self.assertEqual(ledger.run.client_api_calls, 1)
        self.assertEqual(notes, ["client fake at exit: POST /channels/delivered -> 402"])

    def test_a_signal_at_exit_never_replaces_an_exception_in_flight(self) -> None:
        ledger = UsageLedger()
        s = session(exiting_with(BETWEEN_402), ledger)
        s.send("ping")
        with self.assertRaises(ValueError):
            try:
                raise ValueError("in flight")
            finally:
                s.close()
        self.assertEqual(len(ledger.signals), 1)  # recorded all the same

    def test_the_end_of_the_run_closes_without_raising(self) -> None:
        ledger = UsageLedger()
        s = session(exiting_with(ASYNC_429_QUOTA), ledger)
        s.send("ping")
        s.close(raise_signal=False)
        self.assertEqual(len(ledger.signals), 1)
        self.assertIn("(an asynchronous SDK error)", str(ledger.signals[0]))


class ClientSignalKindTest(unittest.TestCase):
    """P06.1-I2a: at both of a command's raise sites, quota or billing wording makes a
    rate limit a charge signal."""

    def test_record_and_error_sites(self) -> None:
        for script in (answering(429, 9), answering_without_a_request(429, 9)):
            quota = script.replace("'message': 'no'", "'message': 'daily quota exceeded'")
            plain = ClientRateLimitFlagTest.stop_for(self, script)  # type: ignore[arg-type]
            charged = ClientRateLimitFlagTest.stop_for(self, quota)  # type: ignore[arg-type]
            self.assertTrue(plain.only_rate_limit)
            self.assertTrue(charged.billing)
            self.assertFalse(charged.only_rate_limit)


if __name__ == "__main__":
    unittest.main()
