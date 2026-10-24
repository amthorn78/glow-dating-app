"""P06.2 Stage B2: the ``conformance`` command, offline (DM-16 1.1, 4.1, 4.3, 4.4, 4.6).

The Stream adapter is imported from ``services/api`` by the command's own import route, in
this harness's environment (no Django here), and run against the fake server and fake
client sessions: no network, no Stream, no Node, no ``STREAM_*`` variable.
"""

from __future__ import annotations

import json
import sys
import unittest
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from unittest import mock

import httpx
import jwt

import tests  # noqa: F401
from glow_stream_proof import baseline, cli, configuration, conformance
from glow_stream_proof.client_bridge import Reply
from glow_stream_proof.conformance import ConformanceRun, load_api_modules, start_refusals
from glow_stream_proof.credentials import EnvironmentRefused, ServerCredentials
from glow_stream_proof.proof_run import RunStopped
from glow_stream_proof.redaction import JWT_PATTERN, Redactor
from glow_stream_proof.server_api import ServerApi
from glow_stream_proof.stops import GuardRefused
from glow_stream_proof.usage import GuardrailStop, Limits, UsageLedger
from glow_stream_proof.workdir import PROOF_ROOT
from tests.fakes import (
    PREFIX,
    SECRET,
    FakeServer,
    FakeSession,
    NoSettle,
    error,
    http_reply,
    make_run,
    ws_refused,
)
from tests.test_cli import FakeContext
from tests.test_preflight import dashboard_user

# The import route, in the harness's own environment (DM-16 4.6).
PORT, FIXTURES, ADAPTER, TOKENS = load_api_modules()
T = configuration.MATCH_TYPE
OPERATIONS = tuple(PORT.OPERATIONS)
NOW = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


@contextmanager
def no_revocation_wait() -> Iterator[None]:
    """The run waits for the wall clock to pass a signed token's iat; not here."""
    with mock.patch.object(conformance, "AFTER_REVOCATION_MARGIN_SECONDS", -2.0):
        yield


def stream_like(
    server: FakeServer, tokens: dict[str, str], session: FakeSession, op: str, params: Any
) -> Reply | None:
    """Stream's answers to a client session, as the harness's P06.1 runs recorded them: a
    token of a deactivated user or one issued before the user's cut-off is refused at the
    connect (401 with a token code); a channel read by a member succeeds and one by a
    non-member (a removed member) gets 404 code 16."""
    token = tokens.get(session.label)
    claims = jwt.decode(token, options={"verify_signature": False}) if token else {}
    user_id = str(claims.get("user_id"))
    if op == "connect":
        user = server.users.get(user_id)
        if user is None:
            return ws_refused(401, 5, message="user not found")
        if user.get("deactivated_at"):
            return ws_refused(401, 40, message="user deactivated")
        cut = user.get("revoke_tokens_issued_before")
        iat = claims.get("iat")
        if cut and isinstance(iat, int) and iat < cut / 1e9:
            return ws_refused(401, 40, message="token revoked")
        return None  # the fake session's own success
    if op == "call" and params.get("method") == "query":
        channel_id = params.get("id")
        members = server.members.get(channel_id)
        if members is None or user_id not in members:
            return http_reply(404, 16, path=f"/channels/{T}/{channel_id}/query")
        return http_reply(201, response={"channel": {"cid": f"{T}:{channel_id}"}, "members": []})
    return None


def conformance_run(
    server: FakeServer | None = None,
    behaviour: Callable[[FakeSession, str, dict[str, Any]], Reply | None] | None = None,
) -> tuple[ConformanceRun, FakeServer]:
    """A conformance run on the fakes, with the dashboard user the live application holds."""
    fake = server or FakeServer(UsageLedger())
    fake.users.setdefault("owner", dashboard_user("owner"))
    tokens: dict[str, str] = {}

    def answer(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
        if behaviour is not None:
            scripted = behaviour(session, op, params)
            if scripted is not None:
                return scripted
        return stream_like(fake, tokens, session, op, params)

    run, server = make_run(fake, default_behaviour=answer, run_class=ConformanceRun)
    assert isinstance(run, ConformanceRun)
    original = run._session

    def session_with_token(label: str, token: str | None, **kwargs: Any) -> Any:
        if token is not None:
            tokens[label] = token
        return original(label, token, **kwargs)

    run._session = session_with_token  # type: ignore[method-assign]
    return run, server


def complete(run: ConformanceRun) -> list[str]:
    with NoSettle(), no_revocation_wait():
        run.preflight()
        run.run_rows()
        return run.finish(cleanup=True)


class ImportRouteTest(unittest.TestCase):
    """DM-16 4.6: the adapter and the domain modules load here, without Django."""

    def test_the_modules_come_from_services_api_and_load_without_django(self) -> None:
        self.assertEqual(conformance.API_ROOT, PROOF_ROOT.parent.parent / "services" / "api")
        for module in (PORT, FIXTURES, ADAPTER, TOKENS):
            self.assertTrue(str(module.__file__).startswith(str(conformance.API_ROOT)))
        self.assertEqual(ADAPTER.StreamChatProvider.name, "stream")
        self.assertFalse(any(name.split(".")[0] == "django" for name in sys.modules))
        self.assertIn(str(conformance.API_ROOT), sys.path)

    def test_the_adapter_imports_only_the_port_the_token_module_and_the_sdk(self) -> None:
        source = (conformance.API_ROOT / "glow_domain" / "chat_provider_stream.py").read_text(
            encoding="utf-8"
        )
        imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
        for line in imports:
            self.assertNotRegex(line, r"django|glow_persistence|glow_chat|glow_api")
        self.assertIn("from getstream.exceptions import", source)


class StartRefusalTest(unittest.TestCase):
    """DM-16 1.1: both verifications before the first changing request."""

    def test_both_counts_are_zero_on_the_proofs_configuration(self) -> None:
        server = FakeServer(UsageLedger())
        snapshot = baseline.read_snapshot(server)  # type: ignore[arg-type]
        self.assertEqual(start_refusals(snapshot), ([], []))

    def test_a_chat_difference_refuses(self) -> None:
        server = FakeServer(UsageLedger())
        server.app["member_custom_on_messages_enabled"] = True
        snapshot = baseline.read_snapshot(server)  # type: ignore[arg-type]
        chat, locked = start_refusals(snapshot)
        self.assertEqual(chat, ["member_custom_on_messages_enabled is True, want False"])
        self.assertEqual(locked, [])
        self.assertEqual(self.command(server), cli.EXIT_REFUSED)

    def test_a_video_and_feeds_difference_refuses(self) -> None:
        server = FakeServer(UsageLedger())
        server.products.grant_before_lockdown()
        snapshot = baseline.read_snapshot(server)  # type: ignore[arg-type]
        chat, locked = start_refusals(snapshot)
        self.assertEqual(chat, [])
        self.assertTrue(locked)
        self.assertEqual(self.command(server), cli.EXIT_REFUSED)

    def command(self, server: FakeServer) -> int:
        """``cmd_conformance`` on a drifted application: refused before any run is built."""
        server.users["owner"] = dashboard_user("owner")
        ctx = FakeContext(server)
        never = mock.Mock(side_effect=AssertionError("a run was built"))
        with mock.patch.object(conformance, "ConformanceRun", never):
            code = cli.cmd_conformance(ctx, True)  # type: ignore[arg-type]
        self.assertIn(
            "refused: the application's configuration is not the proof's; nothing changed",
            ctx.lines,
        )
        self.assertEqual(
            [c for c in server.calls if c[0] != "GET" and c[1] != "/api/v2/chat/channels"], []
        )
        self.assertEqual(set(server.users), {"owner"})
        return code


def hooked_api(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    ledger: UsageLedger | None = None,
) -> tuple[ServerApi, list[str]]:
    """A real server client on a mock transport; what reached the transport is listed."""
    seen: list[str] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(f"{request.method} {request.url.path}")
        return handler(request)

    api = ServerApi(
        ServerCredentials("1729640", "synthetickey", SECRET),
        ledger or UsageLedger(),
        Redactor([SECRET]),
        transport=httpx.MockTransport(record),
    )
    return api, seen


def operations(adapter: Any) -> list[tuple[str, Callable[[], Any]]]:
    cut = TOKENS.revocation_cutoff_sent(NOW)
    return [
        ("provision_user", lambda: adapter.provision_user("u1")),
        ("create_channel", lambda: adapter.create_channel("c1", ("u1", "u2"))),
        ("send_message", lambda: adapter.send_message("c1", "u1", "m1", "hello")),
        ("remove_members", lambda: adapter.remove_members("c1", ("u1", "u2"))),
        ("deactivate_user", lambda: adapter.deactivate_user("u1")),
        ("revoke_user_tokens", lambda: adapter.revoke_user_tokens("u1", cut)),
    ]


class EveryRequestPassesTheGuardTest(unittest.TestCase):
    """DM-16 4.3: with a guard that refuses everything, each operation raises GuardRefused
    before the transport sees a request."""

    def test_refuse_all(self) -> None:
        api, seen = hooked_api(lambda request: httpx.Response(200, json={"duration": "1ms"}))
        api.guard = lambda method, path, body, params: "refused by this test"
        adapter = ADAPTER.StreamChatProvider(api.sdk)
        try:
            for name, call in operations(adapter):
                with self.subTest(operation=name):
                    with self.assertRaises(GuardRefused) as refused:
                        call()
                    self.assertEqual(str(refused.exception), "refused by this test")
        finally:
            api.close()
        self.assertEqual(seen, [])
        self.assertEqual(api._ledger.summary()["run"]["api_calls"], 0)
        self.assertEqual(set(name for name, _ in operations(adapter)), set(OPERATIONS))


class StopTypesPropagateTest(unittest.TestCase):
    """DM-16 4.1: the harness's own stop types pass through the adapter unchanged, from the
    places the harness raises them: the guard (GuardRefused, or a RunStopped raised by it),
    the budget ledger before a request (GuardrailStop) and a charge or limit signal on a
    response (GuardrailStop, at once)."""

    def test_a_run_stopped_raised_by_the_guard(self) -> None:
        api, seen = hooked_api(lambda request: httpx.Response(200, json={"duration": "1ms"}))
        stop = RunStopped("stopped by the run")

        def raising_guard(method: str, path: str, body: Any, params: Any) -> str | None:
            raise stop

        api.guard = raising_guard
        adapter = ADAPTER.StreamChatProvider(api.sdk)
        try:
            for name, call in operations(adapter):
                with self.subTest(operation=name):
                    with self.assertRaises(RunStopped) as seen_stop:
                        call()
                    self.assertIs(seen_stop.exception, stop)
        finally:
            api.close()
        self.assertEqual(seen, [])

    def test_the_budget_guardrail_before_the_request(self) -> None:
        ledger = UsageLedger(limits=Limits(api_calls=0))
        api, seen = hooked_api(
            lambda request: httpx.Response(200, json={"duration": "1ms"}), ledger=ledger
        )
        adapter = ADAPTER.StreamChatProvider(api.sdk)
        try:
            for name, call in operations(adapter):
                with self.subTest(operation=name):
                    with self.assertRaises(GuardrailStop) as stopped:
                        call()
                    self.assertFalse(stopped.exception.at_once)
                    self.assertIn("api_calls would reach", str(stopped.exception))
        finally:
            api.close()
        self.assertEqual(seen, [])

    def test_a_charge_or_limit_signal_on_the_response(self) -> None:
        api, seen = hooked_api(
            lambda request: httpx.Response(429, json={"code": 9, "message": "Too many requests"})
        )
        adapter = ADAPTER.StreamChatProvider(api.sdk)
        try:
            for name, call in operations(adapter):
                with self.subTest(operation=name):
                    with self.assertRaises(GuardrailStop) as stopped:
                        call()
                    self.assertTrue(stopped.exception.at_once)
                    self.assertTrue(stopped.exception.rate_limited)
        finally:
            api.close()
        self.assertEqual(len(seen), len(OPERATIONS))
        self.assertEqual(len(api._ledger.signals), len(OPERATIONS))

    def test_an_unrelated_runtime_error_from_a_hook(self) -> None:
        api, _seen = hooked_api(lambda request: httpx.Response(200, json={"duration": "1ms"}))
        error = RuntimeError("unrelated")

        def raising_guard(method: str, path: str, body: Any, params: Any) -> str | None:
            raise error

        api.guard = raising_guard
        adapter = ADAPTER.StreamChatProvider(api.sdk)
        try:
            for name, call in operations(adapter):
                with self.subTest(operation=name):
                    with self.assertRaises(RuntimeError) as seen_error:
                        call()
                    self.assertIs(seen_error.exception, error)
        finally:
            api.close()


class ConformanceRunTest(unittest.TestCase):
    """The rows against the fakes: every row made, the identifiers the run's own, the
    ledger counted, the run cleaned up, nothing secret in the record."""

    proof: ConformanceRun
    server: FakeServer
    problems: list[str]
    results: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.proof, cls.server = conformance_run()
        cls.problems = complete(cls.proof)
        cls.results = cls.proof.results()

    def test_every_row_passes_or_is_one_stated_as_recorded(self) -> None:
        verdicts = {row.row_id: row.verdict for row in self.proof.rows}
        not_passing = {k: v for k, v in verdicts.items() if v != conformance.PASS}
        self.assertEqual(
            not_passing,
            {"M5": conformance.RECORDED, "R7": conformance.RECORDED, "V7": conformance.RECORDED},
        )
        self.assertEqual(self.problems, [])
        self.assertEqual(len(self.proof.rows), 46)

    def test_the_recorded_rows(self) -> None:
        by_id = {row.row_id: row for row in self.proof.rows}
        # 4.7: the fixture refuses a removed member's send; this model of Stream accepts it.
        self.assertEqual((by_id["R7"].expected, by_id["R7"].observed), ("member_unavailable", "ok"))
        self.assertEqual(by_id["R7"].reason, "differs from the fixture")
        # DM-20 1.3: M5 is recorded whatever Stream answers, its expectation the fixture's;
        # these fakes refuse an unknown sender, as the fixture does.
        self.assertEqual(
            (by_id["M5"].expected, by_id["M5"].observed, by_id["M5"].reason),
            ("member_unavailable", "member_unavailable", "as the fixture"),
        )
        # The boundary token: this model compares strictly, so iat == cut-off is accepted.
        self.assertEqual(by_id["V7"].observed, "accepted")

    def test_the_codes_the_composition_needs_and_their_mappings(self) -> None:
        by_id = {row.row_id: row for row in self.proof.rows}
        for row_id, code in (
            ("C4", "member_unavailable"),
            ("R8", "channel_unavailable"),
            ("D10", "member_unavailable"),
            ("V13", "member_unavailable"),
        ):
            self.assertEqual((by_id[row_id].observed, by_id[row_id].expected), (code, code))
        mappings = {m["row"]: m for m in self.proof.mappings}
        self.assertEqual(
            mappings["C4"]["decided_by"], "the adapter's read: Stream does not hold the object"
        )
        self.assertEqual(
            (mappings["M4"]["code"], mappings["M4"]["status"], mappings["M4"]["number"]),
            ("channel_unavailable", 404, 16),
        )
        self.assertEqual(
            (mappings["M5"]["code"], mappings["M5"]["status"], mappings["M5"]["number"]),
            ("member_unavailable", 400, 4),
        )
        self.assertEqual(
            (mappings["D9"]["code"], mappings["D9"]["status"], mappings["D9"]["number"]),
            ("member_unavailable", 400, 4),
        )
        for m in self.proof.mappings:
            self.assertIn(m["code"], PORT.ERROR_CODES)

    def test_the_adapter_runs_on_the_harnesss_own_client(self) -> None:
        """DM-16 4.3: the adapter is built on ``ServerApi.sdk``, the one hooked client, so
        every request it makes passes the guard and the ledger."""
        self.assertIs(self.proof.adapter._client, self.server.sdk)
        self.assertEqual(vars(self.proof.adapter), {"_client": self.server.sdk})

    def test_the_identifiers_are_the_runs_prefix_plus_32_hexadecimal_characters(self) -> None:
        self.assertGreaterEqual(len(self.proof.ids), 14)
        for value in self.proof.ids.values():
            self.assertTrue(value.startswith(PREFIX))
            tail = value[len(PREFIX) :]
            self.assertEqual(len(tail), 32)
            int(tail, 16)
        self.assertTrue(all(self.proof.owns_user(u) for u in self.proof.users))
        self.assertTrue(all(self.proof.owns_channel(c) for c in self.proof.channels))

    def test_the_ledger_counted_the_users_the_channels_and_the_calls(self) -> None:
        counted = self.proof.ledger.summary()["run"]
        # Five users: U1 to U4, and M5's sender, reserved before its send (B2R3).
        self.assertEqual((counted["users"], counted["channels"]), (5, 2))
        self.assertEqual(counted["peak_connections"], 1)
        self.assertGreater(counted["api_calls"], 40)
        self.assertEqual(len(self.proof.users), 5)
        self.assertEqual(len(self.proof.channels), 2)

    def test_the_run_was_cleaned_up(self) -> None:
        self.assertEqual(set(self.server.users), {"owner"})
        self.assertEqual(self.proof.cleanup_result.get("users_task"), "completed")
        self.assertEqual(self.proof.cleanup_result.get("channels_task"), "completed")
        self.assertEqual(self.proof.cleanup_result.get("remaining_proof_users"), [])
        self.assertEqual(self.proof.cleanup_result.get("remaining_channels"), [])
        self.assertIn(self.proof.ids["U3"], self.proof.deactivated_users)

    def test_the_record_holds_no_token_and_no_secret(self) -> None:
        text = json.dumps(self.results, default=str) + conformance.render(self.results)
        self.assertIsNone(JWT_PATTERN.search(text))
        self.assertNotIn(SECRET, text)
        self.assertEqual(self.results["verdicts"], {"PASS": 43, "RECORDED": 3})
        self.assertEqual(
            self.results["api_calls_used"], self.proof.ledger.summary()["run"]["api_calls"]
        )

    def test_the_signer_rows(self) -> None:
        by_id = {row.row_id: row for row in self.proof.rows}
        self.assertEqual(by_id["T1"].detail["claim_names"], ["exp", "iat", "user_id"])
        self.assertEqual(
            by_id["T1"].detail["iat_minus_truncated_issue"], -ADAPTER.IAT_BACKDATE_SECONDS
        )
        self.assertEqual(by_id["T1"].detail["exp_minus_truncated_expiry"], 0)
        self.assertEqual(by_id["V4"].detail["sent_minus_exact_seconds"], 1)
        self.assertEqual(by_id["V4"].detail["held_minus_exact_seconds"], 1)


class ConformanceVerdictTest(unittest.TestCase):
    """What the rows say when Stream answers otherwise."""

    def test_a_read_that_still_succeeds_after_the_removal_fails_the_row(self) -> None:
        def reads_succeed(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                return http_reply(201, response={"channel": {}})
            return None

        run, _server = conformance_run(behaviour=reads_succeed)
        complete(run)
        by_id = {row.row_id: row for row in run.rows}
        self.assertEqual(by_id["R3"].verdict, conformance.FAIL)
        self.assertEqual(by_id["T2"].verdict, conformance.PASS)

    def test_a_connect_without_a_recorded_answer_is_inconclusive(self) -> None:
        def no_answer(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "connect":
                return Reply(False, None, {"kind": "error", "message": "local"})
            return None

        run, _server = conformance_run(behaviour=no_answer)
        complete(run)
        by_id = {row.row_id: row for row in run.rows}
        for row_id in ("T2", "R3", "D3", "V5", "V8"):
            self.assertEqual(by_id[row_id].verdict, conformance.INCONCLUSIVE, row_id)

    def test_a_contract_row_that_differs_is_a_difference_and_the_blocking_ones_say_so(self) -> None:
        run, _server = conformance_run()
        run.fixture = _FixtureSayingOtherwise(run.fixture)
        complete(run)
        by_id = {row.row_id: row for row in run.rows}
        self.assertEqual(by_id["M4"].verdict, conformance.DIFFERENCE)
        self.assertEqual(by_id["M4"].reason, "differs from the fixture: a finding")
        self.assertEqual(by_id["R8"].verdict, conformance.DIFFERENCE)
        self.assertEqual(by_id["R8"].reason, conformance.BLOCKING)


class _FixtureSayingOtherwise:
    """A fixture whose unknown-channel outcomes differ from the adapter's (test only)."""

    def __init__(self, fixture: Any) -> None:
        self._fixture = fixture

    def __getattr__(self, name: str) -> Any:
        return getattr(self._fixture, name)

    def send_message(self, channel_id: str, sender: str, message_id: str, text: str) -> Any:
        try:
            return self._fixture.send_message(channel_id, sender, message_id, text)
        except PORT.ChatProviderError as error:
            if error.code == "channel_unavailable":
                raise PORT.ChatProviderError("provider_rejected") from None
            raise

    def remove_members(self, channel_id: str, members: tuple[str, str]) -> Any:
        try:
            return self._fixture.remove_members(channel_id, members)
        except PORT.ChatProviderError as error:
            if error.code == "channel_unavailable":
                raise PORT.ChatProviderError("provider_rejected") from None
            raise


@dataclass
class SendCreatesItsSender(FakeServer):
    """As Stream answered M5 live (DM-20 item 2): a server-side send naming a sender it does
    not hold is accepted, and (by inference from B2-C3's reads, AM7-06) creates that user.
    ``seen_at_send`` holds each sender so created, with what ``on_unknown_sender`` returned
    at the moment of the send (``None`` without one)."""

    on_unknown_sender: Callable[[str], Any] | None = None
    seen_at_send: dict[str, Any] = field(default_factory=dict)

    def _send_message(self, type: str, id: str, message: Any) -> Any:
        sender = message.user_id
        if sender not in self.users and id in self.members:
            seen = self.on_unknown_sender
            self.seen_at_send[sender] = seen(sender) if seen is not None else None
            self.users[sender] = {"id": sender, "role": "user", "created_at": 0}
        return super()._send_message(type, id, message)


def spied(run: ConformanceRun) -> list[tuple[str, str, tuple[Any, ...]]]:
    """Each contract row's operation and arguments, in the order the run makes them."""
    made: list[tuple[str, str, tuple[Any, ...]]] = []
    original = run._both

    def both(row_id: str, description: str, operation: str, *args: Any, **kwargs: Any) -> Any:
        made.append((row_id, operation, args))
        return original(row_id, description, operation, *args, **kwargs)

    run._both = both  # type: ignore[method-assign]
    return made


def _names(args: Any) -> set[str]:
    if isinstance(args, str):
        return {args}
    if isinstance(args, tuple | list):
        return set().union(*(_names(a) for a in args)) if args else set()
    return set()


# The user each of the four rows names (DM-20 1.2): C4's absent member, M5's sender, and the
# user D10 deactivates and V13 revokes.
ABSENT_USER_ROWS: dict[str, Callable[[tuple[Any, ...]], Any]] = {
    "C4": lambda args: args[1][1],
    "M5": lambda args: args[1],
    "D10": lambda args: args[0],
    "V13": lambda args: args[0],
}


class RowIdentifiersTest(unittest.TestCase):
    """DM-20 1.2: C4, D10 and V13 each name a user no other row names, and M5 its own;
    C4's, D10's and V13's users are never created by the run."""

    def test_no_two_of_c4_m5_d10_and_v13_share_an_identifier(self) -> None:
        run, _server = conformance_run()
        made = spied(run)
        complete(run)
        by_row = {row_id: args for row_id, _operation, args in made}
        named = {row: pick(by_row[row]) for row, pick in ABSENT_USER_ROWS.items()}
        self.assertEqual(len(set(named.values())), 4, named)
        keys = {row: k for row, uid in named.items() for k, v in run.ids.items() if v == uid}
        self.assertEqual(keys, {"C4": "U5", "M5": "U6", "D10": "U7", "V13": "U8"})
        for row, user_id in named.items():
            with self.subTest(row=row):
                # No other row names it, before or after.
                others = [r for r, _op, args in made if r != row and user_id in _names(args)]
                self.assertEqual(others, [])
        for row in ("C4", "D10", "V13"):
            with self.subTest(row=row):
                # Never through _new_user: not a run user, nothing reserved for it.
                self.assertNotIn(named[row], run.users)

    def test_under_streams_send_d10_and_v13_still_name_a_user_stream_does_not_have(self) -> None:
        """With M5's send creating its sender (as live), D10 and V13 still exercise their
        cause and give the fixture's code, which B2-C3's shared identifier did not."""
        server = SendCreatesItsSender(UsageLedger())
        run, _ = conformance_run(server)
        complete(run)
        by_id = {row.row_id: row for row in run.rows}
        for row_id in ("C4", "D10", "V13"):
            with self.subTest(row=row_id):
                self.assertEqual(by_id[row_id].verdict, conformance.PASS)
                self.assertEqual(by_id[row_id].observed, "member_unavailable")
        self.assertEqual(set(server.seen_at_send), {run.ids["U6"]})


class RecordedSenderTest(unittest.TestCase):
    """DM-20 1.3 with B2R3: M5 is recorded whatever Stream answers; its sender is reserved
    in the ledger and recorded as a run user before the send, so cleanup deletes it by
    record, not only by the prefix search."""

    def stream_like_run(self) -> tuple[ConformanceRun, SendCreatesItsSender]:
        server = SendCreatesItsSender(UsageLedger())
        run, _ = conformance_run(server)
        server.on_unknown_sender = lambda sender: (
            sender in run.users,
            run.ledger.summary()["run"]["users"],
        )
        return run, server

    def test_m5_is_recorded_when_stream_accepts_the_send(self) -> None:
        run, _server = self.stream_like_run()
        complete(run)
        m5 = next(row for row in run.rows if row.row_id == "M5")
        self.assertEqual(
            (m5.expected, m5.observed, m5.verdict, m5.reason),
            ("member_unavailable", "ok", conformance.RECORDED, "differs from the fixture"),
        )
        self.assertEqual(run.verdict_counts(), {"PASS": 43, "RECORDED": 3})

    def test_the_sender_is_reserved_and_recorded_before_the_send(self) -> None:
        run, server = self.stream_like_run()
        complete(run)
        sender = run.ids["U6"]
        # At the send: already a run user, and the ledger had counted it with U1 and U2.
        self.assertEqual(server.seen_at_send, {sender: (True, 3)})
        self.assertIn(sender, run.users)

    def test_cleanup_deletes_the_created_sender_and_nothing_is_found_unrecorded(self) -> None:
        run, server = self.stream_like_run()
        problems = complete(run)
        self.assertEqual(problems, [])
        self.assertEqual(set(server.users), {"owner"})
        self.assertEqual(run.cleanup_result.get("users_found_by_prefix_not_recorded"), 0)
        deleted = [b for m, p, b in server.calls if p == "/api/v2/users/delete"]
        self.assertIn(run.ids["U6"], deleted[0]["user_ids"])

    def test_the_sender_is_deleted_by_record_when_the_prefix_search_finds_nothing(self) -> None:
        run, server = self.stream_like_run()

        def listing_fails(method: str, path: str, body: Any, params: Any) -> Any:
            payload = json.loads((params or {}).get("payload", "{}"))
            if method == "GET" and path == "/api/v2/users" and payload.get("limit") == 100:
                return error(method, path, 500, 0, "listing unavailable")
            return None

        with NoSettle(), no_revocation_wait():
            run.preflight()
            run.run_rows()
            # Only the cleanup's listing fails: the prefix search finds nothing.
            server.handlers.append(listing_fails)
            run.finish(cleanup=True)
        self.assertEqual(run.cleanup_result.get("users_found_by_prefix_not_recorded"), 0)
        deleted = [b for m, p, b in server.calls if p == "/api/v2/users/delete"]
        self.assertIn(run.ids["U6"], deleted[0]["user_ids"])
        self.assertNotIn(run.ids["U6"], server.users)

    def test_a_sender_stream_did_not_create_leaves_no_problem(self) -> None:
        """These fakes refuse the send: the recorded sender is absent from a complete
        listing, so cleanup does not name it again, and reports no problem."""
        run, server = conformance_run()
        problems = complete(run)
        self.assertEqual(problems, [])
        self.assertEqual(run.cleanup_result.get("recorded_users_already_gone"), 1)
        self.assertEqual(run.cleanup_result.get("users_found_by_prefix_not_recorded"), 0)


class ResultsIdentifiersTest(unittest.TestCase):
    """B2R2: the results replace every identifier of the run with its key, not only the
    prefix, so no row's detail and no note keeps an identifier's random part."""

    def test_no_detail_or_note_keeps_an_identifiers_random_part(self) -> None:
        run, _server = conformance_run(SendCreatesItsSender(UsageLedger()))
        complete(run)
        # A note and a stop that name identifiers, as a client note or a stop could.
        run.notes.append(f"client X note: {run.ids['U1']} in {T}:{run.ids['C1']}")
        run.stops.append(f"stopped at {run.ids['M1']}")
        randoms = {value[len(PREFIX) :] for value in run.ids.values()}
        self.assertEqual(len(randoms), len(run.ids))
        self.assertTrue(all(len(r) == 32 for r in randoms))
        raw = json.dumps([row.detail for row in run.rows], default=str)
        self.assertTrue(any(r in raw for r in randoms))  # the details do carry identifiers
        results = run.results()
        details = [json.dumps(row["detail"]) for row in results["rows"]]
        text = json.dumps(results, default=str) + conformance.render(results)
        for random_part in randoms:
            with self.subTest(random_part=random_part[:6]):
                self.assertFalse(any(random_part in d for d in details))
                self.assertFalse(any(random_part in n for n in results["notes"]))
                self.assertNotIn(random_part, text)
        c2 = next(row for row in results["rows"] if row["row_id"] == "C2")
        self.assertEqual(sorted(c2["detail"]["shape"]["member_user_ids"]), ["{U1}", "{U2}"])
        self.assertIn("client X note: {U1} in glow-match:{C1}", results["notes"])
        self.assertEqual(results["prefix"], PREFIX)


class CommandTest(unittest.TestCase):
    """``cmd_conformance``: its exit codes and its records, on the fakes."""

    def setUp(self) -> None:
        self.written: dict[str, Any] = {}

        def write_json(name: str, data: Any, secrets: Any) -> Any:
            self.written[name] = json.loads(json.dumps(data, default=str))
            return PROOF_ROOT / ".work" / name

        def write_text(name: str, text: str, secrets: Any) -> Any:
            self.written[name] = text
            return PROOF_ROOT / ".work" / name

        for name, fake in (("write_json", write_json), ("write_text", write_text)):
            patcher = mock.patch.object(cli, name, fake)
            patcher.start()
            self.addCleanup(patcher.stop)
        for context in (NoSettle(), no_revocation_wait()):
            context.__enter__()
            self.addCleanup(context.__exit__, None, None, None)

    def command(self, adjust: Callable[[ConformanceRun, FakeServer], None] | None = None) -> int:
        run, server = conformance_run()
        if adjust is not None:
            adjust(run, server)
        self.proof, self.server = run, server
        self.ctx = FakeContext(server)

        def factory(*_args: Any, **_kwargs: Any) -> ConformanceRun:
            return run

        with mock.patch.object(conformance, "ConformanceRun", factory):
            return cli.cmd_conformance(self.ctx, True)  # type: ignore[arg-type]

    def results(self) -> dict[str, Any]:
        name = next(
            n
            for n in self.written
            if n.startswith("conformance-") and n.endswith(".json") and "progress" not in n
        )
        data: dict[str, Any] = self.written[name]
        return data

    def test_a_clean_run_exits_zero_and_records_the_rows(self) -> None:
        self.assertEqual(self.command(), 0)
        results = self.results()
        self.assertEqual(results["verdicts"], {"PASS": 43, "RECORDED": 3})
        self.assertEqual(results["post_run_problems"], [])
        self.assertIsNone(results["stop_reason"])
        markdown = next(v for k, v in self.written.items() if k.endswith(".md"))
        self.assertIn("| R7 |", markdown)
        self.assertIn("API calls used by the run:", markdown)
        text = json.dumps(self.written, default=str) + "".join(self.ctx.lines)
        self.assertIsNone(JWT_PATTERN.search(text))
        self.assertNotIn(SECRET, text)
        self.assertTrue(
            any(
                line.startswith("configuration differences from the proof's target: 0")
                for line in self.ctx.lines
            )
        )
        self.assertTrue(
            any(
                line.startswith("video and feeds differences from the lockdown target: 0")
                for line in self.ctx.lines
            )
        )

    def test_a_failing_row_exits_one_after_cleanup(self) -> None:
        def reads_succeed(session: FakeSession, op: str, params: dict[str, Any]) -> Reply | None:
            if op == "call" and params.get("method") == "query":
                return http_reply(201, response={"channel": {}})
            return None

        run, server = conformance_run(behaviour=reads_succeed)
        self.proof, self.server, self.ctx = run, server, FakeContext(server)
        with mock.patch.object(conformance, "ConformanceRun", lambda *a, **k: run):
            code = cli.cmd_conformance(self.ctx, True)  # type: ignore[arg-type]
        self.assertEqual(code, cli.EXIT_ROWS_DIFFER)
        self.assertEqual(self.results()["verdicts"].get("FAIL"), 1)  # R3: the read succeeded
        self.assertEqual(self.results()["post_run_problems"], [])
        self.assertEqual(set(server.users), {"owner"})

    def test_a_stop_during_the_rows_exits_two_and_still_cleans_up(self) -> None:
        def stop_on_the_removal(run: ConformanceRun, server: FakeServer) -> None:
            original = server.sdk.chat.update_channel

            def refused(*args: Any, **kwargs: Any) -> Any:
                raise GuardRefused("guard refused POST channels/{type}/{id}: test")

            server.sdk.chat.update_channel = refused
            self.original = original

        self.assertEqual(self.command(stop_on_the_removal), cli.EXIT_STOPPED)
        results = self.results()
        self.assertEqual(
            results["stop_reason"], "stopped: guard refused POST channels/{type}/{id}: test"
        )
        self.assertLess(len(results["rows"]), 46)
        self.assertEqual(set(self.server.users), {"owner"})
        self.assertEqual(results["post_run_problems"], [])

    def test_a_charge_signal_exits_two_and_deletes_nothing(self) -> None:
        def charge_on_the_removal(run: ConformanceRun, server: FakeServer) -> None:
            def charged(*args: Any, **kwargs: Any) -> Any:
                raise server.ledger.stop_at_once(
                    "server POST x: HTTP 402; stopping at once", rate_limited=False
                )

            server.sdk.chat.update_channel = charged

        self.assertEqual(self.command(charge_on_the_removal), cli.EXIT_STOPPED)
        results = self.results()
        self.assertTrue(results["stop_reason"].startswith("guardrail: server POST x: HTTP 402"))
        self.assertTrue(
            any(
                p.startswith("cleanup skipped: a charge or limit signal")
                for p in results["post_run_problems"]
            )
        )
        self.assertTrue(set(self.server.users) - {"owner"})  # nothing deleted

    def test_a_cleanup_problem_exits_four(self) -> None:
        def task_fails(run: ConformanceRun, server: FakeServer) -> None:
            server.task_status = "failed"

        self.assertEqual(self.command(task_fails), cli.EXIT_AFTER_RUN_PROBLEMS)
        self.assertTrue(any("not 'completed'" in p for p in self.results()["post_run_problems"]))

    def test_the_command_is_registered(self) -> None:
        with mock.patch.object(cli, "Context") as context:
            context.side_effect = EnvironmentRefused("no credentials in this test")
            self.assertEqual(cli.main(["conformance", "--accept-dashboard-user"]), 2)


if __name__ == "__main__":
    unittest.main()
