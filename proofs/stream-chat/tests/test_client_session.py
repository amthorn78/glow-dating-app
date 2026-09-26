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


class ClientRateLimitFlagTest(unittest.TestCase):
    """P06.1-C2, nit 4: a client's charge signal says whether it was a rate limit."""

    def stop_for(self, status: int, code: int) -> GuardrailStop:
        s = session(answering(status, code), UsageLedger())
        try:
            with self.assertRaises(GuardrailStop) as stopped:
                s.send("call")
        finally:
            s.close()
        return stopped.exception

    def test_flags(self) -> None:
        self.assertTrue(self.stop_for(429, 9).rate_limited)
        self.assertFalse(self.stop_for(402, 4).rate_limited)
        self.assertFalse(self.stop_for(403, 99).rate_limited)


if __name__ == "__main__":
    unittest.main()
