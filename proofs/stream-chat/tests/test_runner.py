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


if __name__ == "__main__":
    unittest.main()
