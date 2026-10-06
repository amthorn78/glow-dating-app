"""Nits 7 and 11: the client runner, started offline with a placeholder API key.

Constructing the SDK client makes no request, and no command here connects.
"""

import json
import os
import subprocess
import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import matrix
from glow_stream_proof.client_bridge import RUNNER, ClientSession
from glow_stream_proof.redaction import Redactor
from glow_stream_proof.usage import UsageLedger


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
  refused: errorInfo(Object.assign(new Error('PROOF_REFUSED: denied path (join)'),
    { proofRefused: true })),
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
        # The product op's own refusal (P06.1-I2b): before anything is sent.
        self.assertEqual(
            (out["refused"]["kind"], out["refused"]["message"]),
            ("refused", "PROOF_REFUSED: denied path (join)"),
        )


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

    def test_a_channel_command_names_its_channel_as_channel_id(self) -> None:
        """P06.1-I2a: found by run 1's first live channel command. The channel is
        ``channel_id``; ``id`` stays the command's own. A development token is made
        locally, and the channel method fails before any request."""
        replies = run_runner(
            {"id": 1, "op": "set_rest_user", "user_id": "u", "token_source": "dev", "max_calls": 0},
            {
                "id": 2,
                "op": "call",
                "target": "channel",
                "method": "_checkInitialized",
                "args": [],
                "type": "glow-match",
                "channel_id": "proof-channel",
                "max_calls": 0,
            },
        )
        reply = replies[1]
        self.assertEqual(reply["id"], 2)
        self.assertIn("glow-match:proof-channel", reply["error"]["message"])
        self.assertEqual(reply["requests"], [])


class ChannelCommandSessionTest(unittest.TestCase):
    """P06.1-I2a: run 1 ended at A's first channel command, "reply id '<AB>' does not
    match command id 2": the channel's ``id`` had replaced the command's, and C1's reply
    matching (never run live before) ended the session. The real runner, offline."""

    def test_a_channel_command_keeps_its_own_id_end_to_end(self) -> None:
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin"),
            "PROOF_API_KEY": "offlinetestkey",
            "PROOF_MAX_API_CALLS": "5",
        }
        session = ClientSession("t", env, UsageLedger(), Redactor(), timeout_seconds=30)
        try:
            session.send("set_rest_user", max_calls=0, user_id="u", token_source="dev")
            reply = session.send(
                "call",
                max_calls=0,
                target="channel",
                method="_checkInitialized",
                args=[],
                type="glow-match",
                id="proof-channel",
            )
        finally:
            session.close()
        self.assertIsNone(session.ended)
        self.assertFalse(reply.ok)
        assert reply.error is not None
        self.assertIn("glow-match:proof-channel", str(reply.error.get("message")))


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


# Every reply to a command carries these keys (client_bridge.Reply reads them).
REPLY_KEYS = {
    "id",
    "ok",
    "data",
    "error",
    "requests",
    "api_calls",
    "api_calls_total",
    "ws_attempts",
    "background_requests",
    "background_api_calls",
    "async_errors",
}
# The proxy the WebSocket and HTTP requests would go through: a loopback port nothing
# listens on, so a connect fails at once and no request leaves the machine.
UNREACHABLE_PROXY = "http://127.0.0.1:1"


def run_runner_offline(*commands: dict[str, Any]) -> list[dict[str, Any]]:
    lines = "".join(json.dumps(c) + "\n" for c in (*commands, {"id": 99, "op": "exit"}))
    done = subprocess.run(
        ["node", str(RUNNER)],
        env={
            "PATH": os.environ.get("PATH", "/usr/bin"),
            "PROOF_API_KEY": "offlinetestkey",
            "PROOF_MAX_API_CALLS": "0",
            "HTTPS_PROXY": UNREACHABLE_PROXY,
        },
        cwd=RUNNER.parent.parent,
        input=lines,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return [json.loads(line) for line in done.stdout.splitlines()]


class EveryOpTest(unittest.TestCase):
    """P06.1-I2b, the I2a review's nit 5: the real runner, offline, answers each op the
    Python side uses with a reply of the protocol's shape. Nothing connects: the HTTP
    budget is zero, so the SDK's requests are refused before they are sent, and the
    WebSocket goes to a loopback proxy nothing listens on."""

    def test_each_op_replies_with_the_protocols_shape(self) -> None:
        dev = {"token_source": "dev"}
        replies = run_runner_offline(
            {"id": 1, "op": "ping"},
            {"id": 2, "op": "selfcheck"},
            {"id": 3, "op": "connect", "user": {"id": "u"}, **dev, "max_calls": 0},
            {"id": 4, "op": "disconnect", "max_calls": 0},
            {"id": 5, "op": "set_rest_user", "user_id": "u", **dev, "max_calls": 0},
            {
                "id": 6,
                "op": "call",
                "target": "channel",
                "method": "_checkInitialized",
                "args": [],
                "type": "glow-match",
                "channel_id": "proof-channel",
                "channel_data": {"members": ["u"]},
                "max_calls": 0,
            },
            {
                "id": 7,
                "op": "call",
                "target": "client",
                "method": "queryUsers",
                "args": [{"id": "u"}],
                "max_calls": 0,
            },
            {"id": 8, "op": "get", "path": "/channels/glow-match/proof-channel", "max_calls": 0},
            {"id": 9, "op": "guest", "user": {"id": "g"}, "max_calls": 0},
            {"id": 10, "op": "anonymous", "max_calls": 0},
            {"id": 11, "op": "events", "wait_ms": 10},
            # P06.1-I2b: the Video and Feeds op, refused by the budget before it is sent,
            # and one the op itself refuses (the deny-list) before the budget is asked.
            {
                "id": 12,
                "op": "product",
                "method": "POST",
                "path": "/api/v2/video/call/default/proof-call",
                "body": {"data": {"custom": {"glow_note": "x"}}},
                "max_calls": 0,
            },
            {
                "id": 13,
                "op": "product",
                "method": "POST",
                "path": "/api/v2/video/call/default/proof-call",
                "body": {"ring": True},
                "max_calls": 5,
            },
            {
                "id": 14,
                "op": "product",
                "method": "POST",
                "path": "/api/v2/video/call/default/proof-call/join",
                "body": {},
                "max_calls": 5,
            },
            # A refusal only the op's own check makes (P06.1-C4): the runner's request check
            # sees a clean path and a harmless query, so without the op's check this would
            # reach the budget.
            {
                "id": 15,
                "op": "product",
                "method": "GET",
                "path": "/api/v2/video/call/default/proof-call?x=1",
                "max_calls": 5,
            },
        )
        by_id = {r["id"]: r for r in replies}
        self.assertEqual(sorted(by_id), list(range(1, 16)) + [99])
        for command_id in range(1, 16):
            self.assertEqual(set(by_id[command_id]), REPLY_KEYS, command_id)
            self.assertEqual(by_id[command_id]["requests"], [], command_id)  # nothing sent
            self.assertEqual(by_id[command_id]["api_calls"], 0, command_id)
        self.assertEqual(by_id[1]["data"], {"pong": True})
        self.assertTrue(by_id[2]["data"]["isomorphic_ws_shared"])
        # The connect's WebSocket could not be opened: no answer from Stream (ws-failure),
        # and one attempt was made.
        self.assertFalse(by_id[3]["ok"])
        self.assertEqual(by_id[3]["error"]["kind"], "ws-failure")
        self.assertGreaterEqual(by_id[3]["ws_attempts"], 1)
        self.assertTrue(by_id[4]["ok"])
        self.assertEqual(by_id[5]["data"], {"user_id": "u"})
        # A channel command with channel_data opens the channel with that data.
        self.assertEqual(by_id[6]["error"]["kind"], "error")
        self.assertIn("glow-match:proof-channel", by_id[6]["error"]["message"])
        # A client call without a connection: the connect's failure rethrown locally, or
        # its HTTP request refused by the budget before it is sent. Nothing is sent.
        self.assertFalse(by_id[7]["ok"])
        self.assertIn(by_id[7]["error"]["kind"], ("ws-failure", "error", "budget"))
        # The GET and the guest's POST are refused by the budget before they are sent.
        self.assertEqual(by_id[8]["error"]["kind"], "budget")
        self.assertEqual(by_id[9]["error"]["kind"], "budget")
        self.assertEqual(by_id[10]["error"]["kind"], "ws-failure")
        self.assertEqual(by_id[11]["data"], {"events": []})
        self.assertEqual(by_id[12]["error"]["kind"], "budget")
        self.assertEqual(by_id[13]["error"]["kind"], "refused")
        self.assertEqual(by_id[13]["error"]["message"], "PROOF_REFUSED: denied field (ring)")
        self.assertEqual(by_id[14]["error"]["kind"], "refused")
        self.assertEqual(by_id[14]["error"]["message"], "PROOF_REFUSED: denied path (join)")
        self.assertEqual(by_id[15]["error"]["kind"], "refused")
        self.assertEqual(
            by_id[15]["error"]["message"],
            "PROOF_REFUSED: query parameters belong in params, not in the path",
        )
        exit_reply = by_id[99]
        self.assertTrue(exit_reply["ok"])
        self.assertEqual(
            set(exit_reply),
            {
                "id",
                "ok",
                "api_calls_total",
                "ws_attempts",
                "background_requests",
                "background_api_calls",
                "async_errors",
            },
        )


CHAT = "https://chat.stream-io-api.com"
REST_USER = {"op": "set_rest_user", "user_id": "u", "token_source": "dev", "max_calls": 0}


def client_call(command_id: int, method: str, *args: Any) -> dict[str, Any]:
    """A ``call`` of one of the client's own methods, with a zero budget."""
    return {
        "id": command_id,
        "op": "call",
        "target": "client",
        "method": method,
        "args": list(args),
        "max_calls": 0,
    }


class _NotSentTest(unittest.TestCase):
    """The runner's reply to a command it sent nothing for: its error kind and message."""

    def assert_not_sent(self, reply: dict[str, Any], kind: str, message: str | None = None) -> None:
        self.assertFalse(reply["ok"], reply)
        self.assertEqual(reply["error"]["kind"], kind, reply)
        if message is not None:
            self.assertEqual(reply["error"]["message"], message, reply)
        self.assertEqual(reply["requests"], [], reply)
        self.assertEqual(reply["api_calls"], 0, reply)


class ProductReachTest(_NotSentTest):
    """P06.1-C4, the I2b review's finding 1: nothing reaches Video or Feeds except through
    the product op's check, whatever op sent the request. Offline: the budget is zero and
    the proxy is a loopback port nothing listens on, so nothing can leave the machine; a
    request the check lets through is refused by the budget (kind ``budget``), one it
    refuses has kind ``refused``, and neither is counted or recorded."""

    def test_the_reviews_scenario_a_client_post_to_a_join_with_ring(self) -> None:
        """The review's reproduction: after a REST user is set, a ``call`` of the client's
        ``post`` to the chat host's join path with ``ring: true``. Without the fix the
        budget stopped it (kind ``budget``); with a budget it would have been sent."""
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            client_call(2, "post", CHAT + "/api/v2/video/call/default/x/join", {"ring": True}),
            client_call(3, "post", CHAT + "/api/v2/video/call/default/x", {"ring": True}),
            client_call(4, "post", "/api/v2/feeds/activities", {"feeds": ["user:x"]}),
        )
        by_id = {r["id"]: r for r in replies}
        self.assertTrue(by_id[1]["ok"], by_id[1])
        self.assert_not_sent(by_id[2], "refused", "PROOF_REFUSED: denied path (join)")
        self.assert_not_sent(by_id[3], "refused", "PROOF_REFUSED: denied field (ring)")
        # A relative URL (no base URL): still a product path, still the op's check; the
        # allowlist admits it, so only the budget stops it.
        self.assert_not_sent(by_id[4], "budget")
        self.assertEqual(by_id[99]["background_requests"], [])

    def test_a_product_path_not_in_its_normalized_form_is_refused_outright(self) -> None:
        not_normal = "PROOF_REFUSED: a Video or Feeds path not in its normalized form"
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            # An encoded slash and dot segments: the chat prefix, read as Video.
            client_call(2, "post", CHAT + "/api/v2/chat/..%2fvideo/call/default/x", {}),
            # An encoded letter.
            client_call(3, "post", CHAT + "/api/v2/%76ideo/call/default/x", {}),
            # A double encoding.
            client_call(4, "get", CHAT + "/api/v2/feeds/activities/a%252Fb", {}),
            # An empty segment.
            client_call(5, "post", CHAT + "/api/v2//video/call/default/x", {}),
            # Letter case is folded to find the path; the allowlist's fixed segments are
            # lower case, so the op's check refuses it.
            client_call(6, "post", CHAT + "/API/V2/VIDEO/call/default/x", {}),
            # A dot segment the URL parser resolves before sending: sent as the join path.
            client_call(7, "post", CHAT + "/api/v2/chat/../video/call/default/x/join", {}),
        )
        by_id = {r["id"]: r for r in replies}
        for command_id in (2, 3, 4, 5):
            self.assert_not_sent(by_id[command_id], "refused", not_normal)
        self.assert_not_sent(
            by_id[6], "refused", "PROOF_REFUSED: path outside the Video and Feeds allowlist"
        )
        self.assert_not_sent(by_id[7], "refused", "PROOF_REFUSED: denied path (join)")

    def test_a_product_host_is_checked_whatever_its_path(self) -> None:
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            client_call(2, "post", "https://video.stream-io-api.com/api/v2/chat/channels", {}),
            client_call(3, "post", "https://FEEDS.stream-io-api.com/channels/glow-match/x", {}),
            client_call(4, "get", "https://video.stream-io-api.com/api/v2/video/call/default/x"),
            client_call(
                5, "get", "https://video.stream-io-api.com/api/v2/video/call/default/x?ring=1"
            ),
            client_call(6, "delete", "https://feeds.stream-io-api.com/api/v2/feeds/activities/a"),
        )
        by_id = {r["id"]: r for r in replies}
        outside = "PROOF_REFUSED: path outside the Video and Feeds allowlist"
        self.assert_not_sent(by_id[2], "refused", outside)
        self.assert_not_sent(by_id[3], "refused", outside)
        self.assert_not_sent(by_id[4], "budget")  # on the allowlist: only the budget stops it
        self.assert_not_sent(by_id[5], "refused", "PROOF_REFUSED: denied field (ring)")
        self.assert_not_sent(
            by_id[6], "refused", "PROOF_REFUSED: method DELETE is not allowed on this path"
        )

    def test_a_product_body_the_check_cannot_read_is_refused(self) -> None:
        """A string body that is not JSON (axios sends it form-encoded) could carry a denied
        field the check cannot see; it is refused. A JSON string is read like an object."""
        cannot_read = "PROOF_REFUSED: a Video or Feeds body the check cannot read"
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            client_call(2, "post", CHAT + "/api/v2/video/call/default/x", "ring=true"),
            client_call(3, "post", CHAT + "/api/v2/video/call/default/x", '{"Ring": true}'),
            client_call(4, "post", CHAT + "/api/v2/video/call/default/x", '{"custom": {}}'),
            client_call(5, "post", CHAT + "/channels/glow-match/x/query", "not json"),
        )
        by_id = {r["id"]: r for r in replies}
        self.assert_not_sent(by_id[2], "refused", cannot_read)
        self.assert_not_sent(by_id[3], "refused", "PROOF_REFUSED: denied field (ring)")
        self.assert_not_sent(by_id[4], "budget")
        self.assert_not_sent(by_id[5], "budget")  # a chat path: the check does not apply

    def test_an_escape_that_is_not_utf8_does_not_switch_the_check_off(self) -> None:
        """C4's own review (blocking): %ff or %c0 made decodeURIComponent throw, so the path
        was left undecoded and a %76ideo path was not seen as Video. Decoding is now byte by
        byte."""
        not_normal = "PROOF_REFUSED: a Video or Feeds path not in its normalized form"
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            client_call(
                2, "post", CHAT + "/api/v2/%76ideo/call/default/abc%ff/join", {"ring": True}
            ),
            {
                "id": 3,
                "op": "get",
                "path": "/api/v2/%76ideo/call/default/abc%ff",
                "params": {"ring": "true"},
                "max_calls": 0,
            },
            {"id": 4, "op": "get", "path": "/api/v2/%66eeds/activities/a%c0", "max_calls": 0},
            # An escape that is not hex is left as it is, and the rest is still decoded.
            {"id": 5, "op": "get", "path": "/api/v2/%76ideo/%zz", "max_calls": 0},
            # An encoding that does not settle in eight rounds is refused, on any path.
            {"id": 6, "op": "get", "path": "/channels/x%" + "25" * 9 + "41", "max_calls": 0},
        )
        by_id = {r["id"]: r for r in replies}
        for command_id in (2, 3, 4, 5):
            self.assert_not_sent(by_id[command_id], "refused", not_normal)
        self.assert_not_sent(
            by_id[6], "refused", "PROOF_REFUSED: a path whose percent-encoding does not settle"
        )

    def test_only_streams_hosts_no_host_header_and_the_bare_product_forms(self) -> None:
        """C4's own review: a request goes only to Stream's chat, Video or Feeds host, never
        with a Host header of its own; the Video and Feeds clients' bare /video and /feeds
        forms are product paths; JSON inside a query value is read by the deny-list."""
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            client_call(2, "post", "https://example.com/api/v2/chat/x", {}),
            client_call(3, "post", "https://chat.stream-io-api.com.evil.test/x", {}),
            client_call(
                4,
                "post",
                CHAT + "/channels/glow-match/x/query",
                {},
                {"headers": {"Host": "video.stream-io-api.com"}},
            ),
            client_call(5, "post", CHAT + "/video/call/default/x/join", {}),
            client_call(6, "post", CHAT + "/feeds/activities", {}),
            {
                "id": 7,
                "op": "get",
                "path": "/api/v2/video/call/default/x",
                "params": {"payload": '{"Ring": true}'},
                "max_calls": 0,
            },
            client_call(8, "post", CHAT + "/channels/glow-match/x/query", {}),
            client_call(9, "post", "http://chat.stream-io-api.com/channels/glow-match/x", {}),
            client_call(
                10,
                "post",
                CHAT + "/channels/glow-match/x/query",
                {},
                {"headers": {"X-Forwarded-Host": "video.stream-io-api.com"}},
            ),
        )
        by_id = {r["id"]: r for r in replies}
        other_host = "PROOF_REFUSED: a host other than Stream's chat, Video or Feeds host"
        self.assert_not_sent(by_id[2], "refused", other_host)
        self.assert_not_sent(by_id[3], "refused", other_host)
        self.assert_not_sent(by_id[4], "refused", "PROOF_REFUSED: a Host header")
        self.assert_not_sent(by_id[5], "refused", "PROOF_REFUSED: denied path (join)")
        self.assert_not_sent(
            by_id[6], "refused", "PROOF_REFUSED: path outside the Video and Feeds allowlist"
        )
        self.assert_not_sent(by_id[7], "refused", "PROOF_REFUSED: denied field (ring)")
        self.assert_not_sent(by_id[8], "budget")  # an ordinary chat request
        self.assert_not_sent(by_id[9], "refused", "PROOF_REFUSED: a protocol other than https")
        self.assert_not_sent(by_id[10], "refused", "PROOF_REFUSED: a forwarding header")

    def test_the_get_op_is_checked_too(self) -> None:
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            {"id": 2, "op": "get", "path": "/../api/v2/video/call/default/x/join", "max_calls": 0},
            {"id": 3, "op": "get", "path": "/api/v2/video/call/default/x", "max_calls": 0},
            {"id": 4, "op": "get", "path": "/api/v2/feeds/%66eeds/query", "max_calls": 0},
            {"id": 5, "op": "get", "path": "/channels/glow-match/x", "max_calls": 0},
        )
        by_id = {r["id"]: r for r in replies}
        self.assert_not_sent(by_id[2], "refused", "PROOF_REFUSED: denied path (join)")
        self.assert_not_sent(by_id[3], "budget")
        self.assert_not_sent(
            by_id[4], "refused", "PROOF_REFUSED: a Video or Feeds path not in its normalized form"
        )
        self.assert_not_sent(by_id[5], "budget")  # a chat path: the check does not apply

    def test_the_18_product_cases_steps_are_not_refused_by_the_new_check(self) -> None:
        """Each product case's step, with the values a run gives its placeholders, goes
        through the product op and then the new check, and only the zero budget stops it.
        An activity ID with capitals passes too: letter case is kept in the comparison."""
        prefix = "p061i1-0927062935"
        flat = prefix.replace("-", "")
        ctx = {
            "A": f"{prefix}-ua",
            "B": f"{prefix}-ub",
            "CALL": f"{prefix}-call",
            "CALL_a": f"{prefix}-call-a",
            "CALL_dev": f"{prefix}-call-dev",
            "CALL_x": f"{prefix}-call-x",
            "FG": "user",
            "FGT": "timeline",
            "vd_text": f"vdmarker{flat}",
            "fd_text": f"fdmarker{flat}",
        }
        cases = [c for c in matrix.all_cases() if matrix.product_of(c) is not None]
        self.assertEqual(len(cases), 18)
        for act in ("0b6f7c1e-3a52-4d7e-9a1b-5c2d8e4f6a70", "0B6F7C1E-3A52-4D7E-9A1B-5C2D8E4F6A70"):
            commands = []
            for index, case in enumerate(cases, start=2):
                assert case.step is not None and case.step.op == "product"
                params = matrix.substitute(dict(case.step.params), {**ctx, "ACT": act})
                commands.append({"id": index, "op": "product", **params, "max_calls": 0})
            replies = run_runner_offline({"id": 1, **REST_USER}, *commands)
            by_id = {r["id"]: r for r in replies}
            for index, case in enumerate(cases, start=2):
                with self.subTest(case=case.id, act=act):
                    self.assert_not_sent(by_id[index], "budget")


REWRITING_HEADERS = (
    "X-HTTP-Method-Override",
    "X-HTTP-Method",
    "X-Method-Override",
    "X-Original-URL",
    "X-Rewrite-URL",
)


def with_headers(command_id: int, headers: dict[str, str]) -> dict[str, Any]:
    """An ordinary chat request (a client ``post`` to the chat host) whose request options,
    the SDK's third argument to ``post``, carry ``headers``."""
    return client_call(
        command_id, "post", CHAT + "/channels/glow-match/x/query", {}, {"headers": headers}
    )


class RequestHeaderTest(_NotSentTest):
    """P06.1-C5, the manager's addition to the C4 review's finding 1: the runner refuses a
    request carrying a request-rewriting header, in any letter case, whatever op sent it,
    before it is counted or sent (kind ``refused``), as it refuses the forwarding headers.
    Every header name is read as axios sends it, trimmed (C5 found that " Host" passed the
    check), with an underscore read as a hyphen (C5's own review). Offline: a zero budget and
    a loopback proxy nothing listens on."""

    def test_each_request_rewriting_header_is_refused(self) -> None:
        rewriting = "PROOF_REFUSED: a request-rewriting header"
        headers = [{name: "DELETE"} for name in REWRITING_HEADERS]
        # One in another letter case, and one with its name padded as axios would trim it.
        headers += [{"x-REWRITE-url": "/api/v2/video/call/default/x/join"}]
        headers += [{"  x-http-method-override\t": "DELETE"}]
        commands = [with_headers(n, h) for n, h in enumerate(headers, start=2)]
        # Whatever op sends it: the channel target's queryMembers and the client's queryUsers,
        # with their request options (their fourth argument).
        options = {"headers": {"X-HTTP-Method-Override": "DELETE"}}
        commands.append(
            {
                "id": 20,
                "op": "call",
                "target": "channel",
                "method": "queryMembers",
                "args": [{}, [], {}, options],
                "type": "glow-match",
                "channel_id": "x",
                "max_calls": 0,
            }
        )
        commands.append(client_call(21, "queryUsers", {}, [], {}, options))
        # An ordinary chat request: only the budget stops it.
        commands.append(client_call(22, "post", CHAT + "/channels/glow-match/x/query", {}))
        replies = run_runner_offline({"id": 1, **REST_USER}, *commands)
        by_id = {r["id"]: r for r in replies}
        for command in commands[:-1]:
            with self.subTest(command=command["id"]):
                self.assert_not_sent(by_id[command["id"]], "refused", rewriting)
        self.assert_not_sent(by_id[22], "budget")

    def test_a_header_name_is_read_as_axios_sends_it(self) -> None:
        """A name padded with whitespace is trimmed by axios before it is sent, so the check
        reads it trimmed: the Host and forwarding headers too."""
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            with_headers(2, {" Host": "video.stream-io-api.com"}),
            with_headers(3, {"X-Forwarded-Host\t": "video.stream-io-api.com"}),
            with_headers(4, {" X-Original-URL ": "/api/v2/video/call/default/x/join"}),
        )
        by_id = {r["id"]: r for r in replies}
        self.assert_not_sent(by_id[2], "refused", "PROOF_REFUSED: a Host header")
        self.assert_not_sent(by_id[3], "refused", "PROOF_REFUSED: a forwarding header")
        self.assert_not_sent(by_id[4], "refused", "PROOF_REFUSED: a request-rewriting header")

    def test_an_underscore_in_a_header_name_is_read_as_a_hyphen(self) -> None:
        """C5's own review: some servers read an underscore in a header name as a hyphen, so
        an underscore spelling of a refused header is refused too."""
        rewriting = "PROOF_REFUSED: a request-rewriting header"
        forwarding = "PROOF_REFUSED: a forwarding header"
        cases = [
            ({"X_HTTP_Method_Override": "DELETE"}, rewriting),
            ({"x_original_url": "/api/v2/video/call/default/x/join"}, rewriting),
            ({"X-HTTP_Method": "DELETE"}, rewriting),
            ({"x_method-override": "DELETE"}, rewriting),
            ({"X_Rewrite_URL": "/api/v2/feeds/activities"}, rewriting),
            ({"X_Forwarded_Host": "video.stream-io-api.com"}, forwarding),
            ({"x_original_host": "video.stream-io-api.com"}, forwarding),
        ]
        commands = [with_headers(n, h) for n, (h, _) in enumerate(cases, start=2)]
        replies = run_runner_offline({"id": 1, **REST_USER}, *commands)
        by_id = {r["id"]: r for r in replies}
        for command, (headers, message) in zip(commands, cases, strict=True):
            with self.subTest(headers=headers):
                self.assert_not_sent(by_id[command["id"]], "refused", message)

    def test_axios_trims_a_header_name_before_sending(self) -> None:
        """The premise of reading names trimmed: the axios stream-chat uses sends each header
        name trimmed (its http adapter's AxiosHeaders.normalize)."""
        script = (
            "const path = require('node:path');"
            "const at = [path.dirname(require.resolve('stream-chat'))];"
            "const { AxiosHeaders } = require(require.resolve('axios', { paths: at }));"
            "const h = AxiosHeaders.concat({}, {' Host': 'v', 'X-Original-URL\\t': '/x'});"
            "process.stdout.write(JSON.stringify({"
            " seen: Object.keys(h.toJSON()),"
            " sent: Object.keys(AxiosHeaders.from(h).normalize().toJSON()) }));"
        )
        done = subprocess.run(
            ["node", "-e", script],
            env={"PATH": os.environ.get("PATH", "/usr/bin")},
            cwd=RUNNER.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = json.loads(done.stdout)
        self.assertEqual(out["seen"], [" Host", "X-Original-URL\t"])
        self.assertEqual(out["sent"], ["Host", "X-Original-URL"])

    def test_neither_stream_chat_nor_axios_names_a_rewriting_header(self) -> None:
        """So no chat request carries one, and the refusal changes no chat case: no file of
        the installed stream-chat 9.53.0 or axios 1.20.0 names any of the five headers, nor,
        in its underscore spelling, any name the runner refuses (C5's own review)."""
        modules = RUNNER.parent.parent / "node_modules"
        versions = {
            name: json.loads((modules / name / "package.json").read_text())["version"]
            for name in ("stream-chat", "axios")
        }
        self.assertEqual(versions, {"stream-chat": "9.53.0", "axios": "1.20.0"})
        refused = [*REWRITING_HEADERS, "X-Forwarded-Host", "X-Original-Host", "X-Host"]
        names = [n.lower().encode() for n in REWRITING_HEADERS]
        names += [n.lower().replace("-", "_").encode() for n in refused]
        scanned = 0
        for package in ("stream-chat", "axios"):
            for path in sorted((modules / package).rglob("*")):
                if path.is_file():
                    scanned += 1
                    text = path.read_bytes().lower()
                    found = [n for n in names if n in text]
                    self.assertEqual(found, [], str(path))
        self.assertGreater(scanned, 100)


class HeaderAllowlistTest(_NotSentTest):
    """P06.2 B1 (the C5 review's advice): the runner refuses a request carrying any header
    name outside the allowlist of what stream-chat 9.53.0 and axios 1.20.0 set, whatever op
    sent it, before it is counted or sent. The routing headers the named deny-lists left
    (X-Forwarded-Prefix, X-Forwarded-Proto, X-Original-Method and their kin) are refused by
    it; a header the SDK sets passes; an ordinary request reaches the budget. Offline: a
    zero budget and a loopback proxy nothing listens on."""

    def test_a_header_outside_the_allowlist_is_refused_by_name(self) -> None:
        cases = [
            ({"X-Forwarded-Prefix": "/video"}, "x-forwarded-prefix"),
            ({"X-Forwarded-Proto": "http"}, "x-forwarded-proto"),
            ({"X-Original-Method": "DELETE"}, "x-original-method"),
            ({"X-Forwarded-For": "127.0.0.1"}, "x-forwarded-for"),
            ({"Via": "1.1 proxy"}, "via"),
            ({"X-Custom": "x"}, "x-custom"),
            # Read as sent: trimmed, lower case, an underscore for a hyphen.
            ({"  X_Forwarded_Prefix\t": "/feeds"}, "x-forwarded-prefix"),
        ]
        commands = [with_headers(n, h) for n, (h, _) in enumerate(cases, start=2)]
        # Through the channel target's queryMembers and the client's queryUsers too.
        options = {"headers": {"X-Forwarded-Prefix": "/video"}}
        commands.append(
            {
                "id": 20,
                "op": "call",
                "target": "channel",
                "method": "queryMembers",
                "args": [{}, [], {}, options],
                "type": "glow-match",
                "channel_id": "x",
                "max_calls": 0,
            }
        )
        commands.append(client_call(21, "queryUsers", {}, [], {}, options))
        replies = run_runner_offline({"id": 1, **REST_USER}, *commands)
        by_id = {r["id"]: r for r in replies}
        for command, (headers, name) in zip(commands, cases, strict=False):
            with self.subTest(headers=headers):
                self.assert_not_sent(
                    by_id[command["id"]],
                    "refused",
                    f"PROOF_REFUSED: a header name outside the allowlist ({name})",
                )
        for command_id in (20, 21):
            self.assert_not_sent(
                by_id[command_id],
                "refused",
                "PROOF_REFUSED: a header name outside the allowlist (x-forwarded-prefix)",
            )
        self.assertEqual(by_id[99]["background_requests"], [])

    def test_the_named_deny_lists_keep_their_own_refusals(self) -> None:
        """The Host, forwarding and request-rewriting checks come first and keep their
        messages; the allowlist refuses what they do not name."""
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            with_headers(2, {"Host": "video.stream-io-api.com"}),
            with_headers(3, {"X-Forwarded-Host": "video.stream-io-api.com"}),
            with_headers(4, {"X-HTTP-Method-Override": "DELETE"}),
        )
        by_id = {r["id"]: r for r in replies}
        self.assert_not_sent(by_id[2], "refused", "PROOF_REFUSED: a Host header")
        self.assert_not_sent(by_id[3], "refused", "PROOF_REFUSED: a forwarding header")
        self.assert_not_sent(by_id[4], "refused", "PROOF_REFUSED: a request-rewriting header")

    def test_a_header_the_sdk_sets_passes_and_only_the_budget_stops_the_request(self) -> None:
        replies = run_runner_offline(
            {"id": 1, **REST_USER},
            # The SDK's own names, through request options, in another letter case.
            with_headers(2, {"X-STREAM-CLIENT": "x", "Stream-Auth-Type": "jwt"}),
            with_headers(3, {"x-client-request-id": "abc", "Accept": "application/json"}),
            # An ordinary chat request with no option at all.
            client_call(4, "post", CHAT + "/channels/glow-match/x/query", {}),
            client_call(5, "get", CHAT + "/users", {}),
        )
        by_id = {r["id"]: r for r in replies}
        for command_id in (2, 3, 4, 5):
            self.assert_not_sent(by_id[command_id], "budget")

    def test_the_allowlist_is_what_the_sdk_and_axios_set(self) -> None:
        """The premise: stream-chat 9.53.0 sets Authorization, stream-auth-type,
        X-Stream-Client and x-client-request-id (and a form's Content-Type for a file), and
        axios 1.20.0 merges Accept and Content-Type before its interceptors; no other header
        name appears in either package's request path. The allowlist in the runner is
        exactly those names."""
        modules = RUNNER.parent.parent / "node_modules"
        sdk = (modules / "stream-chat" / "dist" / "cjs" / "index.node.js").read_text()
        for name in (
            "Authorization",
            '"stream-auth-type"',
            '"X-Stream-Client"',
            '"x-client-request-id"',
        ):
            self.assertIn(name, sdk)
        axios_defaults = (modules / "axios" / "lib" / "defaults" / "index.js").read_text()
        self.assertIn("Accept: 'application/json, text/plain, */*'", axios_defaults)
        self.assertIn("'Content-Type': undefined", axios_defaults)
        source = RUNNER.read_text()
        listed = source.split("const ALLOWED_HEADERS = [", 1)[1].split("];", 1)[0]
        names = sorted(n.strip().strip("'") for n in listed.split(",") if n.strip())
        self.assertEqual(
            names,
            [
                "accept",
                "authorization",
                "content-type",
                "stream-auth-type",
                "x-client-request-id",
                "x-stream-client",
            ],
        )


# The runner loaded with a stub stream-chat in require.cache, as the runner itself places its
# WebSocket for isomorphic-ws: the stub records the request interceptor the runner registers,
# and nothing is sent.
MAX_REDIRECTS_CASES = r"""
const path = require('node:path');
const interceptors = [];
class StreamChat {
  constructor() {
    this.baseURL = 'https://chat.stream-io-api.com';
    this.axiosInstance = {
      interceptors: {
        request: { use: (fn) => interceptors.push(fn) },
        response: { use: () => {} },
      },
    };
  }
  on() {}
}
const stubPath = require.resolve('stream-chat');
require.cache[stubPath] = {
  id: stubPath, filename: stubPath, loaded: true, exports: { StreamChat }, children: [], paths: [],
};
require(path.resolve('client/runner.cjs'));
const out = [];
for (const config of [
  { method: 'post', url: 'https://chat.stream-io-api.com/channels/glow-match/x/query', data: {} },
  { method: 'get', url: 'https://chat.stream-io-api.com/users', maxRedirects: 5, params: {} },
  { method: 'post', baseURL: 'https://chat.stream-io-api.com',
    url: '/channels/glow-match/x/message', data: { message: { text: 'x' } }, maxRedirects: 21 },
]) {
  const sent = interceptors[0](config);
  out.push(sent.maxRedirects === undefined ? 'unset' : sent.maxRedirects);
}
process.stdout.write(JSON.stringify({ interceptors: interceptors.length, maxRedirects: out }));
process.exit(0);
"""


class MaxRedirectsTest(unittest.TestCase):
    """P06.1-C5, the C4 review's nit 2: every request leaves the runner's request interceptor
    with ``maxRedirects`` 0, so axios follows no redirect (C4's own review). The runner is
    loaded with a stub stream-chat, so the interceptor is called directly and nothing is sent."""

    def test_every_request_leaves_the_interceptor_with_max_redirects_zero(self) -> None:
        done = subprocess.run(
            ["node", "-e", MAX_REDIRECTS_CASES],
            env={"PATH": os.environ.get("PATH", "/usr/bin"), "PROOF_API_KEY": "offlinetestkey"},
            cwd=RUNNER.parent.parent,
            input="",
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        out = json.loads(done.stdout)
        self.assertEqual(out["interceptors"], 1)
        self.assertEqual(out["maxRedirects"], [0, 0, 0])


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
