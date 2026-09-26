"""Nits 7 and 11: the client runner, started offline with a placeholder API key.

Constructing the SDK client makes no request, and no command here connects.
"""

import json
import os
import subprocess
import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof.client_bridge import RUNNER


def run_runner(*commands: dict[str, Any]) -> list[dict[str, Any]]:
    lines = "".join(json.dumps(c) + "\n" for c in (*commands, {"id": 99, "op": "exit"}))
    done = subprocess.run(
        ["node", str(RUNNER)],
        env={"PATH": os.environ.get("PATH", "/usr/bin"), "PROOF_API_KEY": "offlinetestkey"},
        cwd=RUNNER.parent.parent,
        input=lines,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return [json.loads(line) for line in done.stdout.splitlines()]


ERROR_CASES = r"""
const { errorInfo } = require('./client/error-info.cjs');
const json = (o) => new Error(JSON.stringify(o));
const api = Object.assign(new Error('x'), { name: 'ErrorFromResponse', status: 403, code: 17,
  response: { data: { message: 'not allowed' } } });
const out = {
  streamFrame: errorInfo(json({ code: 5, StatusCode: 401, message: 'bad', isWSFailure: false })),
  wsFailure: errorInfo(json({ code: 1006, StatusCode: 'n/a', message: 'x', isWSFailure: true })),
  noFlag: errorInfo(json({ code: 17, StatusCode: 403, message: 'local' })),
  api: errorInfo(api),
  local: errorInfo(new Error('channel is not initialized')),
  budget: errorInfo(Object.assign(new Error('PROOF_BUDGET'), { proofBudget: true })),
};
process.stdout.write(JSON.stringify(out));
"""


class ErrorInfoTest(unittest.TestCase):
    """Finding 1, runner side: only Stream's own WebSocket error frame is kind ``ws-api``."""

    def test_kinds(self) -> None:
        done = subprocess.run(
            ["node", "-e", ERROR_CASES],
            env={"PATH": os.environ.get("PATH", "/usr/bin")},
            cwd=RUNNER.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = json.loads(done.stdout)
        self.assertEqual(
            (out["streamFrame"]["kind"], out["streamFrame"]["status"], out["streamFrame"]["code"]),
            ("ws-api", 401, 5),
        )
        self.assertEqual(out["wsFailure"]["kind"], "ws-failure")
        self.assertEqual(out["noFlag"]["kind"], "ws-failure")  # not Stream's frame
        self.assertEqual((out["api"]["kind"], out["api"]["status"]), ("api", 403))
        self.assertEqual((out["local"]["kind"], out["local"]["status"]), ("error", None))
        self.assertEqual(out["budget"]["kind"], "budget")


class RunnerTest(unittest.TestCase):
    def test_stream_chat_uses_the_runners_websocket(self) -> None:
        """Nit 11: stream-chat resolves and keeps the runner's isomorphic-ws module."""
        reply = run_runner({"id": 1, "op": "selfcheck"})[0]
        self.assertTrue(reply["ok"], reply)
        self.assertEqual(
            reply["data"], {"isomorphic_ws_shared": True, "proxied_websocket_installed": True}
        )

    def test_unused_request_op_is_gone(self) -> None:
        """Nit 7: the raw ``request`` op, which overwrote the SDK's parameters, is removed."""
        reply = run_runner({"id": 1, "op": "request", "method": "POST", "path": "/x"})[0]
        self.assertFalse(reply["ok"])
        self.assertEqual(reply["error"]["message"], "unknown op request")
        self.assertEqual(reply["requests"], [])

    def test_every_reply_carries_its_command_id(self) -> None:
        replies = run_runner({"id": 7, "op": "ping"}, {"id": 8, "op": "nope"})
        self.assertEqual([r["id"] for r in replies], [7, 8, 99])


REQUEST_LOG_CASES = r"""
const { RequestLog, rateLimitOf } = require('./client/request-log.cjs');
const log = new RequestLog();
const between = log.start({ path: '/between', status: null });
log.beginCommand();
const own = log.start({ path: '/own', status: null });
const late = log.start({ path: '/late', status: null });
log.finish(own, 201, {});
const commandRequests = log.endCommand().map((r) => r.path);
const beforeAnswers = log.takeKept(false);
log.finish(between, 402, { code: 4, message: 'no' });
const headers = { 'x-ratelimit-reset': '1790', 'x-ratelimit-limit': '60', authorization: 'held' };
log.finish(late, 429, { code: 9 }, rateLimitOf(429, headers));
const afterAnswers = log.takeKept(false);
log.start({ path: '/never-answered', status: null });
const atExit = log.takeKept(true);
const out = {
  commandRequests, beforeAnswers, afterAnswers, atExit,
  rateLimit429: rateLimitOf(429, headers), rateLimit200: rateLimitOf(200, headers),
};
process.stdout.write(JSON.stringify(out));
"""


class RequestLogTest(unittest.TestCase):
    """P06.1-I2a, the C3 review's gap: a request the SDK sends between commands, and a
    command's request answered only after the command replied, are kept and reported
    in a later reply, so that every answer is checked for a charge or limit signal."""

    def test_every_request_is_reported_once_answered(self) -> None:
        done = subprocess.run(
            ["node", "-e", REQUEST_LOG_CASES],
            env={"PATH": os.environ.get("PATH", "/usr/bin")},
            cwd=RUNNER.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = json.loads(done.stdout)
        self.assertEqual(out["commandRequests"], ["/own", "/late"])
        # Nothing answered yet: nothing to report, but the call made between commands
        # is counted.
        self.assertEqual(out["beforeAnswers"]["background_requests"], [])
        self.assertEqual(out["beforeAnswers"]["background_api_calls"], 1)
        after = out["afterAnswers"]["background_requests"]
        self.assertEqual(
            [(r["path"], r["status"]) for r in after], [("/between", 402), ("/late", 429)]
        )
        self.assertTrue(after[0]["background"])
        self.assertTrue(after[1]["late"])
        self.assertEqual(out["afterAnswers"]["background_api_calls"], 0)  # "late" was counted
        exit_report = out["atExit"]["background_requests"]
        self.assertEqual(
            [(r["path"], r["status"]) for r in exit_report], [("/never-answered", None)]
        )
        self.assertEqual(out["atExit"]["background_api_calls"], 1)

    def test_only_a_rate_limits_own_headers_are_kept(self) -> None:
        done = subprocess.run(
            ["node", "-e", REQUEST_LOG_CASES],
            env={"PATH": os.environ.get("PATH", "/usr/bin")},
            cwd=RUNNER.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = json.loads(done.stdout)
        self.assertEqual(out["rateLimit429"], {"limit": "60", "remaining": None, "reset": "1790"})
        self.assertIsNone(out["rateLimit200"])
        self.assertEqual(
            out["afterAnswers"]["background_requests"][1]["ratelimit"]["reset"], "1790"
        )


class RunnerReportsTest(unittest.TestCase):
    def test_replies_and_the_exit_reply_carry_what_was_sent_outside_commands(self) -> None:
        ping, exit_reply = run_runner({"id": 1, "op": "ping"})
        self.assertEqual((ping["background_requests"], ping["background_api_calls"]), ([], 0))
        self.assertEqual(ping["async_errors"], [])
        self.assertEqual(exit_reply["id"], 99)
        self.assertEqual(exit_reply["background_requests"], [])
        self.assertEqual(exit_reply["background_api_calls"], 0)
        self.assertEqual(exit_reply["async_errors"], [])


if __name__ == "__main__":
    unittest.main()
