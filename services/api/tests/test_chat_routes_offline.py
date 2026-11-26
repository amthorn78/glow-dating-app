"""SV4 A2, the parts of chat's routes that need no database (its brief's D8, D9 and D15).

- **Requests** (D8): ``glow_chat.contract.parse`` accepts each route's closed intent and refuses
  what the production schema refuses, so the server and the contract agree; a body naming an
  actor, an account or a session is refused like any other field the DTO does not have.
- **Projections** (D9): each served body validates as its DTO and inside ``AppResponse``; a
  conversation is ``open`` or ``read_only``, never a state naming a cause, with its count and
  marker kept either way; the match list holds at most 200 entries.
- **The send's refusals** (D8; DM-96 AG13): the five that come from either member's state or the
  end of contact, and their missing forms, answer one code, ``not_found``, the same for each.
- **The routes** (D8), in a fresh process under ``tests.discovery_offline_settings`` (Django's
  dummy backend; keys generated for that process), each request through DRF's request factory
  with the actor forced as SV1's authentication would give it and ``glow_chat``'s persistence
  replaced by a recorder: each route answers its DTO, refuses a body that is not its DTO, a query
  string, another content type and another method, takes its session from the actor only, caches
  nothing, echoes no value and logs codes only; the reads' views refuse to run without the text
  reader's factory, before any read (D8, "The provider").
- **The structure** (D8): the four routes and no other (no ``ChannelIntent`` route), each
  ``non_atomic_requests``, each with SV1's authentication only; the list's candidates are read
  before its first lock, and each table is locked in one statement; no new module takes a
  writer's lock or imports ``glow_discovery``.

The routes' database cases run on a disposable PostgreSQL in ``proofs/postgres-ordering``'s chat
suite, through the HTTP endpoints with no enclosing transaction (the reads refuse a Django test
case's atomic block, so no ``TestCase`` tests them; the P11 plan's R4). All data is synthetic.
"""

import ast
import json
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from glow_chat import contract
from glow_domain import chat
from glow_domain.chat_reads import ConversationEntry, LatestMarker
from tests.test_discovery_offline import under_discovery_settings
from tests.test_profiles_offline import last_json

API_ROOT = Path(__file__).resolve().parents[1]
CHAT = API_ROOT / "glow_chat"
NEW_MODULES = ("contract.py", "route_reads.py", "urls.py", "views.py")
sys.path.insert(0, str(API_ROOT.parents[1] / "packages" / "contracts"))
from runtime import valid  # noqa: E402

MATCH = "2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901"
SUBMISSION = "3c4d5e6f-7081-4293-a4b5-c6d7e8f90a1b"
KEY = "synthetic-key-zq7"
MESSAGE = {
    "operation": "message",
    "meta": {"idempotency_key": KEY, "expected_version": 1},
    "match_id": MATCH,
    "text": "A synthetic message for the offline tests.",
}
PAGE = {"match_id": MATCH, "cursor": None, "limit": 50}
CURSOR = {"operation": "read_cursor", "match_id": MATCH, "submission_id": SUBMISSION}


def parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def accepts(definition: str, value: object) -> bool:
    try:
        contract.parse(definition, json.dumps(value).encode("utf-8"))
    except contract.Invalid:
        return False
    return True


# -- requests (D8) -------------------------------------------------------------------------------


class RequestTests(unittest.TestCase):
    def bodies(self) -> list[tuple[str, object]]:
        message, page, cursor = MESSAGE, PAGE, CURSOR
        return [
            ("MessageIntent", message),
            ("MessageIntent", {**message, "text": "x" * 4000}),
            ("MessageIntent", {**message, "text": "x" * 4001}),
            ("MessageIntent", {**message, "text": ""}),
            ("MessageIntent", {**message, "text": " \t\n"}),
            ("MessageIntent", {**message, "text": "\ud800"}),
            ("MessageIntent", {**message, "text": 7}),
            ("MessageIntent", {**message, "operation": "channel"}),
            ("MessageIntent", {**message, "match_id": MATCH.upper()}),
            ("MessageIntent", {**message, "match_id": MATCH + "\n"}),
            ("MessageIntent", {**message, "meta": {"idempotency_key": KEY}}),
            ("MessageIntent", {**message, "meta": {**message["meta"], "expected_version": -1}}),
            ("MessageIntent", {**message, "meta": {**message["meta"], "expected_version": 1.5}}),
            ("MessageIntent", {**message, "meta": {**message["meta"], "idempotency_key": ""}}),
            ("MessageIntent", {k: v for k, v in message.items() if k != "text"}),
            ("MessagePageRequest", page),
            ("MessagePageRequest", {**page, "cursor": "c" + "A" * 46}),
            ("MessagePageRequest", {**page, "limit": 0}),
            ("MessagePageRequest", {**page, "limit": 51}),
            ("MessagePageRequest", {**page, "cursor": ""}),
            ("MessagePageRequest", {**page, "cursor": "-x"}),
            ("MessagePageRequest", {**page, "cursor": "c" * 101}),
            ("MessagePageRequest", {k: v for k, v in page.items() if k != "cursor"}),
            ("ReadCursorIntent", cursor),
            ("ReadCursorIntent", {**cursor, "operation": "read"}),
            ("ReadCursorIntent", {**cursor, "submission_id": "not-a-uuid"}),
            ("ReadCursorIntent", {**cursor, "meta": message["meta"]}),
        ]

    def test_each_intent_is_parsed_as_the_contract_decides(self) -> None:
        for definition, body in self.bodies():
            with self.subTest(definition=definition, body=json.dumps(body)[:80]):
                self.assertEqual(accepts(definition, body), valid("production", definition, body))
        self.assertTrue(accepts("MessageIntent", MESSAGE))
        self.assertTrue(accepts("MessagePageRequest", PAGE))
        self.assertTrue(accepts("ReadCursorIntent", CURSOR))

    def test_a_body_naming_an_actor_is_refused(self) -> None:
        # D8: the actor is SV1's authenticated session, never a field; such a field is refused as
        # the contract refuses it.
        for definition, body in (
            ("MessageIntent", MESSAGE),
            ("MessagePageRequest", PAGE),
            ("ReadCursorIntent", CURSOR),
        ):
            for field in ("actor_id", "account_id", "session_id", "member_id", "other_id"):
                with self.subTest(definition=definition, field=field):
                    changed = {**body, field: str(uuid4())}
                    self.assertFalse(accepts(definition, changed))
                    self.assertFalse(valid("production", definition, changed))

    def test_only_the_server_refuses_a_nul(self) -> None:
        # The database cannot store U+0000 (SV2's rule); the contract's schema allows it.
        body = {**MESSAGE, "text": "a\x00b"}
        self.assertTrue(valid("production", "MessageIntent", body))
        self.assertFalse(accepts("MessageIntent", body))

    def test_a_body_that_is_not_json_or_not_an_object_is_refused(self) -> None:
        for raw in (b"", b"{", b"[]", b"null", b'"x"', b"\xff", b'{"a": NaN}', b"[" * 100_000):
            with self.subTest(raw=raw[:10]):
                with self.assertRaises(contract.Invalid):
                    contract.parse("MessageIntent", raw)


# -- projections (D9) -------------------------------------------------------------------------


def entry(unread: int = 2, latest: bool = True) -> ConversationEntry:
    marker = LatestMarker(UUID(SUBMISSION), datetime(2026, 11, 22, 9, 30, tzinfo=UTC))
    return ConversationEntry(UUID(MATCH), unread, marker if latest else None)


def envelope(data: dict[str, object]) -> dict[str, object]:
    return {
        "contract_version": "gapp-api-v1",
        "request_id": "44444444-4444-4444-8444-444444444444",
        "data": data,
    }


class ProjectionTests(unittest.TestCase):
    def test_a_conversation_is_open_or_read_only_with_its_count_and_marker(self) -> None:
        for read_only, state in ((False, "open"), (True, "read_only")):
            for unread, latest in ((2, True), (0, False)):
                with self.subTest(state=state, unread=unread):
                    summary = contract.conversation_summary(
                        entry(unread, latest), read_only=read_only
                    )
                    self.assertEqual(summary["state"], state)
                    self.assertEqual(summary["unread_count"], unread)
                    self.assertEqual(summary["latest"] is not None, latest)
                    self.assertEqual(
                        set(summary), {"kind", "match_id", "state", "unread_count", "latest"}
                    )
                    self.assertTrue(valid("production", "ConversationSummary", summary))
                    self.assertTrue(valid("production", "AppResponse", envelope(summary)))
        with self.assertRaises(ValueError):
            contract.conversation_summary(entry(-1), read_only=True)

    def test_the_list_serves_each_entrys_mark(self) -> None:
        other = ConversationEntry(UUID(int=7, version=4), 0, None)
        listed = contract.conversation_list([(entry(), True), (other, False)])
        self.assertEqual(
            [summary["state"] for summary in listed["conversations"]], ["read_only", "open"]
        )
        self.assertTrue(valid("production", "ConversationList", listed))
        self.assertTrue(valid("production", "AppResponse", envelope(listed)))

    def test_a_state_naming_a_cause_is_not_the_contract(self) -> None:
        summary = contract.conversation_summary(entry(), read_only=True)
        for state in ("hidden", "paused", "restricted", "suspended", "blocked", "unmatched"):
            with self.subTest(state=state):
                self.assertFalse(
                    valid("production", "ConversationSummary", {**summary, "state": state})
                )

    def test_the_submission_carries_no_text(self) -> None:
        for state in ("pending", "accepted", "failed"):
            with self.subTest(state=state):
                served = contract.message_submission(SUBMISSION, 1, state)
                self.assertEqual(set(served), {"kind", "submission_id", "version", "state"})
                self.assertTrue(valid("production", "MessageSubmission", served))
                self.assertTrue(valid("production", "AppResponse", envelope(served)))


# -- the send's refusals (D8) ----------------------------------------------------------------------


class SendRefusalTests(unittest.TestCase):
    FIVE = (
        chat.MATCH_NOT_ACTIVE,
        chat.BLOCKED,
        chat.ACCOUNT_NOT_ACTIVE,
        chat.PROFILE_UNAVAILABLE,
        chat.CONSENT_NOT_CURRENT,
    )

    def test_the_five_answer_one_code_the_same_for_each(self) -> None:
        answers = {reason: contract.send_error("refused", reason) for reason in self.FIVE}
        self.assertEqual(set(answers.values()), {("not_found", False)})
        # Their missing forms too.
        for reason in (chat.PROFILE_MISSING, chat.NO_CONSENT):
            with self.subTest(reason=reason):
                self.assertEqual(contract.send_error("refused", reason), ("not_found", False))
        self.assertEqual(contract.SEND_STOPPED, "not_found")
        self.assertLessEqual(set(self.FIVE), contract.STOPPED_REASONS)

    def test_the_stopped_code_is_the_one_the_reads_answer_for_the_conversation(self) -> None:
        from glow_domain.chat_projections import error_for

        for reason in (chat.MATCH_NOT_ACTIVE, chat.BLOCKED, chat.ACCOUNT_NOT_ACTIVE):
            with self.subTest(reason=reason):
                self.assertEqual(
                    contract.send_error("refused", reason), error_for("refused", reason)
                )

    def test_the_other_refusals_keep_their_codes(self) -> None:
        cases = {
            # A2-C1 (A2R-1, A2R-2; DM-99): a wrong version and the session's reasons inside the
            # send answer the one code; the session missing before the locks stays 401.
            chat.STALE_CONTACT_VERSION: ("not_found", False),
            chat.IDEMPOTENCY_CONFLICT: ("idempotency_conflict", False),
            chat.SESSION_MISSING: ("unauthenticated", False),
            chat.SESSION_NOT_VALID: ("not_found", False),
            chat.SESSION_EXPIRED: ("not_found", False),
            chat.SESSION_EPOCH_STALE: ("not_found", False),
            chat.SESSION_CHANGED: ("not_found", False),
            chat.MATCH_MISSING: ("not_found", False),
            chat.NOT_A_MEMBER: ("not_found", False),
            chat.MATCH_CHANGED: ("not_found", False),
            chat.BINDING_NOT_ACTIVE: ("not_found", False),
        }
        for reason, expected in cases.items():
            with self.subTest(reason=reason):
                self.assertEqual(contract.send_error("refused", reason), expected)
        self.assertEqual(
            contract.send_error("deadlock", "DeadlockDetected"), ("state_conflict", True)
        )
        self.assertEqual(
            contract.send_error("error", "OperationalError"), ("state_conflict", False)
        )


# -- the mapping is complete (A2-C1; DM-99's AK2) -------------------------------------------------

CONTACT = CHAT / "contact.py"
READS = CHAT / "reads.py"
SETTINGS_STORE = API_ROOT / "glow_profiles" / "settings_store.py"

# Every reason ``OrmContactPersistence.send`` can raise from its first lock on, as the send route
# serves it (``contract.send_error``): the one code for every stopped cause, a wrong version and a
# session ended once the send holds its locks; ``unauthenticated`` only for the session's row
# missing at its lock; ``idempotency_conflict`` for the same key with another intent.
SEND_SERVED = {
    "appaccount_missing": ("not_found", False),
    "match_missing": ("not_found", False),
    "accountsession_missing": ("unauthenticated", False),
    chat.MATCH_NOT_ACTIVE: ("not_found", False),
    chat.MATCH_CHANGED: ("not_found", False),
    chat.SESSION_CHANGED: ("not_found", False),
    chat.ACCOUNT_NOT_ACTIVE: ("not_found", False),
    chat.SESSION_NOT_VALID: ("not_found", False),
    chat.SESSION_EXPIRED: ("not_found", False),
    chat.SESSION_EPOCH_STALE: ("not_found", False),
    chat.BLOCKED: ("not_found", False),
    chat.STALE_CONTACT_VERSION: ("not_found", False),
    chat.PROFILE_UNAVAILABLE: ("not_found", False),
    chat.CONSENT_NOT_CURRENT: ("not_found", False),
    chat.IDEMPOTENCY_CONFLICT: ("idempotency_conflict", False),
    chat.BINDING_NOT_ACTIVE: ("not_found", False),
}
# Every reason ``reads._authorize`` can raise from its first lock on, as the history read and the
# read cursor serve it (``contract.read_error(..., conversation=True)``): ``not_found``, the code a
# hidden conversation answers, but for the session's row missing at its lock.
CONVERSATION_SERVED = {
    "appaccount_missing": ("not_found", False),
    "match_missing": ("not_found", False),
    "accountsession_missing": ("unauthenticated", False),
    "setting_unresolved": ("not_found", False),
    chat.MATCH_NOT_ACTIVE: ("not_found", False),
    chat.MATCH_CHANGED: ("not_found", False),
    chat.SESSION_CHANGED: ("not_found", False),
    chat.ACCOUNT_NOT_ACTIVE: ("not_found", False),
    chat.SESSION_NOT_VALID: ("not_found", False),
    chat.SESSION_EXPIRED: ("not_found", False),
    chat.SESSION_EPOCH_STALE: ("not_found", False),
    chat.BLOCKED: ("not_found", False),
    "conversation_hidden": ("not_found", False),
}
SESSION_IN_LOCKS = (
    chat.SESSION_CHANGED,
    chat.SESSION_NOT_VALID,
    chat.SESSION_EXPIRED,
    chat.SESSION_EPOCH_STALE,
)


class _Reasons:
    """The refusals a function can raise from its first lock on, read from the source.

    From the line of the function's first lock call, it reads every ``raise _Refused(X)``, and
    each lock call's ``<table>_missing`` form, in the function and in every helper it calls from
    there, followed into the helpers' own calls: the class's methods called as ``self.<name>`` and
    the module's functions (an alias ``name = OrmContactPersistence.<name>`` followed to the
    method). ``X`` must be a ``chat.<NAME>`` constant, a module constant, a name imported from
    ``glow_domain``, or ``_history``'s pass-through of ``settings_store.read_shared``'s reasons,
    which are read from that function; any other form fails the test. Not seen: a reason raised
    by a function of another module (but ``read_shared``), one returned as a result instead of
    raised, a database error (served ``state_conflict`` as a deadlock or an error, never a reason),
    and the reasons before the first lock (``session_missing``, ``match_missing``,
    ``not_a_member``), pinned by the tests above."""

    LOCKS = {"self._lock", "_lock_shared"}

    def __init__(self, path: Path) -> None:
        self.path = path
        self.tree = parsed(path)
        self.functions = {n.name: n for n in self.tree.body if isinstance(n, ast.FunctionDef)}
        self.constants = {
            t.id: n.value.value
            for n in self.tree.body
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
            for t in n.targets
            if isinstance(t, ast.Name) and isinstance(n.value.value, str)
        }
        self.imported = {
            alias.asname or alias.name: node.module
            for node in self.tree.body
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("glow_domain")
            for alias in node.names
        }
        self.aliases = {
            t.id: n.value.attr
            for n in self.tree.body
            if isinstance(n, ast.Assign)
            and isinstance(n.value, ast.Attribute)
            and ast.unparse(n.value.value) == "OrmContactPersistence"
            for t in n.targets
            if isinstance(t, ast.Name)
        }
        self.unresolved: list[str] = []

    def method(self, klass: str, name: str) -> ast.FunctionDef:
        found = next(n for n in self.tree.body if isinstance(n, ast.ClassDef) and n.name == klass)
        return next(n for n in found.body if isinstance(n, ast.FunctionDef) and n.name == name)

    def _value(self, node: ast.expr, helper: str) -> set[str]:
        import importlib

        text = ast.unparse(node)
        if text.startswith("chat."):
            return {getattr(chat, text.removeprefix("chat."))}
        if isinstance(node, ast.Name) and node.id in self.constants:
            return {self.constants[node.id]}
        if isinstance(node, ast.Name) and node.id in self.imported:
            return {getattr(importlib.import_module(self.imported[node.id]), node.id)}
        if helper == "_history" and text == "refused.reason":
            store = parsed(SETTINGS_STORE)
            read_shared = next(
                n for n in store.body if isinstance(n, ast.FunctionDef) and n.name == "read_shared"
            )
            return {
                raised.exc.args[1].value
                for raised in ast.walk(read_shared)
                if isinstance(raised, ast.Raise)
                and isinstance(raised.exc, ast.Call)
                and isinstance(raised.exc.args[1], ast.Constant)
            }
        self.unresolved.append(f"{helper}: {text}")
        return set()

    def collect(self, function: ast.FunctionDef, klass: ast.ClassDef | None) -> set[str]:
        calls = [n for n in ast.walk(function) if isinstance(n, ast.Call)]
        first = min(n.lineno for n in calls if ast.unparse(n.func) in self.LOCKS)
        return self._from(function, klass, first, set())

    def _from(
        self, function: ast.FunctionDef, klass: ast.ClassDef | None, first: int, seen: set[str]
    ) -> set[str]:
        found: set[str] = set()
        for node in ast.walk(function):
            if getattr(node, "lineno", first) < first:
                continue
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                if ast.unparse(node.exc.func) == "_Refused":
                    found |= self._value(node.exc.args[0], function.name)
            if not isinstance(node, ast.Call):
                continue
            called = ast.unparse(node.func)
            if called == "self._lock":
                found.add(f"{ast.unparse(node.args[0]).lower()}_missing")
            elif called == "_lock_shared":
                table = node.args[0]
                assert isinstance(table, ast.Constant), ast.unparse(table)
                found.add(f"{str(table.value).removeprefix('glow_persistence_')}_missing")
            else:
                helper = self._helper(called, klass)
                if helper is not None and helper[0].name not in seen:
                    seen.add(helper[0].name)
                    inner = klass if helper[1] is self else None
                    found |= helper[1]._from(helper[0], inner, 0, seen)
        return found

    def _helper(
        self, called: str, klass: ast.ClassDef | None
    ) -> tuple[ast.FunctionDef, Any] | None:
        if called.startswith("self.") and klass is not None:
            name = called.removeprefix("self.")
            for node in klass.body:
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    return node, self
        if called in self.functions:
            return self.functions[called], self
        if called in self.aliases:
            contact = _Reasons(CONTACT)
            return contact.method("OrmContactPersistence", self.aliases[called]), contact
        return None


def _send_reasons() -> tuple[set[str], list[str]]:
    reading = _Reasons(CONTACT)
    klass = next(
        n
        for n in reading.tree.body
        if isinstance(n, ast.ClassDef) and n.name == "OrmContactPersistence"
    )
    send = reading.method("OrmContactPersistence", "send")
    body = next(n for n in send.body if isinstance(n, ast.FunctionDef) and n.name == "body")
    return reading.collect(body, klass), reading.unresolved


def _authorize_reasons() -> tuple[set[str], list[str]]:
    reading = _Reasons(READS)
    authorize = reading.method("OrmConversationReads", "_authorize")
    return reading.collect(authorize, None), reading.unresolved


class MappingCompletenessTests(unittest.TestCase):
    """DM-99's AK2: every reason the send and a conversation's read can raise once they hold
    their first lock is pinned to the code and status its route serves; a reason added later
    fails here until it is pinned."""

    def test_every_reason_the_send_raises_after_its_first_lock_is_pinned(self) -> None:
        found, unresolved = _send_reasons()
        self.assertEqual(unresolved, [])
        self.assertEqual(found, set(SEND_SERVED))
        for reason, expected in SEND_SERVED.items():
            with self.subTest(reason=reason):
                self.assertEqual(contract.send_error("refused", reason), expected)
        # Each one's status, through the route itself: RouteTests.test_every_pinned_reason_...

    def test_every_reason_a_conversations_read_raises_after_its_first_lock_is_pinned(self) -> None:
        found, unresolved = _authorize_reasons()
        self.assertEqual(unresolved, [])
        self.assertEqual(found, set(CONVERSATION_SERVED))
        for reason, expected in CONVERSATION_SERVED.items():
            with self.subTest(reason=reason):
                self.assertEqual(
                    contract.read_error("refused", reason, conversation=True), expected
                )

    def test_the_session_found_ended_in_the_locks_answers_one_code_but_on_the_list(self) -> None:
        for reason in SESSION_IN_LOCKS:
            with self.subTest(reason=reason):
                self.assertEqual(contract.send_error("refused", reason), ("not_found", False))
                self.assertEqual(
                    contract.read_error("refused", reason, conversation=True),
                    ("not_found", False),
                )
                # The list refuses as a whole and names no conversation (DM-99's AK1).
                self.assertEqual(contract.read_error("refused", reason), ("unauthenticated", False))
        for reason in (chat.SESSION_MISSING, "accountsession_missing"):
            with self.subTest(reason=reason):
                self.assertEqual(contract.send_error("refused", reason), ("unauthenticated", False))
                for conversation in (True, False):
                    self.assertEqual(
                        contract.read_error("refused", reason, conversation=conversation),
                        ("unauthenticated", False),
                    )
        # A deadlock and a database error are no reason: state_conflict, as before.
        self.assertEqual(
            contract.read_error("deadlock", "DeadlockDetected", conversation=True),
            ("state_conflict", True),
        )

    def test_a_reason_added_after_the_locks_is_found(self) -> None:
        # The reading itself: a raise added after the first lock, in a copy of the send's source,
        # is found, and is no pinned reason.
        source = CONTACT.read_text(encoding="utf-8")
        marker = '            if match.state != "active":\n'
        self.assertEqual(source.count(marker), 1)
        tree = ast.parse(
            source.replace(marker, "            raise _Refused(chat.NO_CONSENT)\n" + marker)
        )
        reading = _Reasons(CONTACT)
        reading.tree = tree
        klass = next(
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "OrmContactPersistence"
        )
        send = reading.method("OrmContactPersistence", "send")
        body = next(n for n in send.body if isinstance(n, ast.FunctionDef) and n.name == "body")
        self.assertEqual(reading.collect(body, klass) - set(SEND_SERVED), {chat.NO_CONSENT})


# -- the routes, in a fresh process (D8) ----------------------------------------------------------

ROUTES = r"""
import json, logging, sys, types
from datetime import UTC, datetime
from unittest import mock
from uuid import UUID, uuid4
sys.path.insert(0, "../../packages/contracts")
from django.test import override_settings
from rest_framework.test import APIRequestFactory, force_authenticate
from glow_chat import views
from glow_discovery import contract as discovery_contract, interaction_views
from glow_domain.chat import ContactResult, SendReceipt
from glow_domain.chat_reads import (
    ConversationEntry, CursorResult, HistoryPage, LatestMarker, ListResult, ReadResult,
    Reconciliation,
)
from glow_chat.route_reads import ServedEntry
from glow_identity.authentication import Actor
from glow_profiles.tx import Result
from runtime import valid

records = []


class Capture(logging.Handler):
    def emit(self, record):
        records.append([record.name, record.getMessage()])


root = logging.getLogger()
root.addHandler(Capture(level=logging.DEBUG))
root.setLevel(logging.DEBUG)

MATCH = "2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901"
SUBMISSION = "3c4d5e6f-7081-4293-a4b5-c6d7e8f90a1b"
OTHER_SESSION = "5e6f7081-92a3-4b4c-8d6e-7f8091a2b3c4"
KEY = "synthetic-key-zq7"
TEXT = "A synthetic message for the offline tests."
actor = Actor(uuid4(), 1, "active", uuid4(), "valid")
VALUES = (MATCH, SUBMISSION, KEY, TEXT, OTHER_SESSION, str(actor.account_id), str(actor.session_id))
message = {"operation": "message", "meta": {"idempotency_key": KEY, "expected_version": 1},
           "match_id": MATCH, "text": TEXT}
page = {"match_id": MATCH, "cursor": None, "limit": 50}
cursor = {"operation": "read_cursor", "match_id": MATCH, "submission_id": SUBMISSION}


class Signed:
    is_authenticated = True


factory = APIRequestFactory()


def send(view, body, *, path="/x", content_type="application/json", method="post",
         signed=True, headers=None, **kwargs):
    data = body if body is None or isinstance(body, (str, bytes)) else json.dumps(body)
    extra = dict(headers or {})
    request = factory.generic(method.upper(), path, data=data or "", content_type=content_type,
                              **extra)
    if signed:
        force_authenticate(request, user=Signed(), token=actor)
    response = view.as_view()(request, **kwargs)
    response.render()
    return response


def answer(response, kind=None):
    text = response.content.decode("utf-8")
    body = json.loads(text)
    served = (body.get("data") or {}) if isinstance(body, dict) else {}
    return {
        "status": response.status_code,
        "cache": response.get("Cache-Control"),
        "body": body,
        "code": body.get("code"),
        "retryable": body.get("retryable"),
        "kind": served.get("kind"),
        "valid": valid("production", "AppResponse" if "data" in body else "Error", body),
        # A served answer names its own match and submission; a refusal names nothing.
        "echo": any(value in text for value in VALUES
                    if "data" not in body or value not in (MATCH, SUBMISSION)),
    }


class Sent:
    def __init__(self, result):
        self.result = result
        self.commands = []
        self.providers = []

    def __call__(self, *, provider):
        self.providers.append(provider)
        return self

    def send(self, command, *, probe=None):
        self.commands.append(command)
        return self.result


class Submissions:
    class objects:
        @staticmethod
        def filter(**kwargs):
            class Rows:
                @staticmethod
                def values_list(*names):
                    class First:
                        @staticmethod
                        def first():
                            return (1, "pending")
                    return First
            return Rows


marker = LatestMarker(UUID(SUBMISSION), datetime(2026, 11, 22, 9, 30, tzinfo=UTC))
listed = ListResult("listed", conversations=(
    ServedEntry(UUID(MATCH), 2, marker, True),
    ServedEntry(UUID(int=7, version=4), 0, None, False),
))
history = ReadResult("read", page=HistoryPage(UUID(MATCH), (), None, None, False, Reconciliation()))
moved = CursorResult("moved", entry=ServedEntry(UUID(MATCH), 0, marker, True))


class Reads:
    made = []
    calls = []
    answers = {"list": listed, "history": history, "cursor": moved}

    def __init__(self, texts):
        Reads.made.append(texts)

    def list_conversations(self, session_id, *, probe=None):
        Reads.calls.append(["list", str(session_id)])
        return Reads.answers["list"]

    def read_history(self, request, *, probe=None):
        Reads.calls.append(["history", str(request.session_id), str(request.match_id)])
        return Reads.answers["history"]

    def move_read_cursor(self, command, *, probe=None):
        Reads.calls.append(["cursor", str(command.session_id), str(command.match_id)])
        return Reads.answers["cursor"]


reader = object()
module = types.ModuleType("synthetic_reader")
module.make = lambda: reader
sys.modules["synthetic_reader"] = module
READER = override_settings(GLOW_CHAT_TEXT_READER="synthetic_reader.make")

POSTS = ((views.MessageView, message), (views.HistoryView, page), (views.ReadCursorView, cursor))
cases = {}
receipt = SendReceipt(UUID(SUBMISSION), 1, "d" * 64)
sent = Sent(ContactResult("authorized", receipt=receipt))
with (
    mock.patch.object(views, "OrmContactPersistence", sent),
    mock.patch.object(views, "MessageSubmission", Submissions),
    mock.patch.object(views, "RouteConversationReads", Reads),
):
    # Without the factory the reads' views refuse to run, before any read (D8, "The provider").
    for name, view, body, method in (
        ("list", views.ConversationListView, None, "get"),
        ("history", views.HistoryView, page, "post"),
        ("cursor", views.ReadCursorView, cursor, "post"),
    ):
        cases[f"no_reader_{name}"] = answer(send(view, body, method=method))
    cases["no_reader_made"] = len(Reads.made)
    cases["no_reader_calls"] = list(Reads.calls)
    cases["send_without_reader"] = answer(send(views.MessageView, message))
    with READER:
        cases["send"] = answer(send(views.MessageView, message))
        # A header naming another session changes nothing: the actor is the authentication's.
        cases["send_header"] = answer(send(views.MessageView, message,
                                           headers={"HTTP_X_SESSION_TOKEN": OTHER_SESSION}))
        cases["list"] = answer(send(views.ConversationListView, None, method="get"))
        cases["history"] = answer(send(views.HistoryView, page))
        cases["cursor"] = answer(send(views.ReadCursorView, cursor))
        cases["bad_cursor"] = answer(send(views.HistoryView, {**page, "cursor": "cAAAA"}))
        cases["made"] = [texts is reader for texts in Reads.made]
        cases["calls"] = list(Reads.calls)
        cases["commands"] = [
            [str(c.session_id), str(c.match_id), c.contact_version, c.idempotency_key,
             c.text == TEXT] for c in sent.commands
        ]
        cases["providers"] = sent.providers
        for index, (view, body) in enumerate(POSTS):
            name = view.__name__
            cases[f"{name}:extra"] = answer(send(view, {**body, "x": KEY}))
            cases[f"{name}:actor"] = answer(send(view, {**body, "session_id": OTHER_SESSION}))
            cases[f"{name}:query"] = answer(send(view, body, path="/x?match=" + MATCH))
            cases[f"{name}:type"] = answer(send(view, body, content_type="text/plain"))
            cases[f"{name}:method"] = answer(send(view, None, method="get"))
            cases[f"{name}:put"] = answer(send(view, body, method="put"))
            cases[f"{name}:unsigned"] = answer(send(view, body, signed=False))
            cases[f"{name}:not_json"] = answer(send(view, "{"))
        cases["list:body"] = answer(send(views.ConversationListView, json.dumps(page),
                                         method="get"))
        cases["list:query"] = answer(send(views.ConversationListView, None, method="get",
                                          path="/x?match=" + MATCH))
        cases["list:method"] = answer(send(views.ConversationListView, None))
        cases["list:unsigned"] = answer(send(views.ConversationListView, None, method="get",
                                             signed=False))
        # The send's refusals, each as its code; the five answer one code (D8).
        for reason in ("match_not_active", "blocked", "account_not_active",
                       "profile_unavailable", "consent_not_current", "stale_contact_version",
                       "idempotency_conflict", "session_not_valid", "match_missing",
                       "not_a_member"):
            sent.result = ContactResult("refused", reason)
            cases[f"send:{reason}"] = answer(send(views.MessageView, message))
        sent.result = ContactResult("deadlock", "DeadlockDetected")
        cases["send:deadlock"] = answer(send(views.MessageView, message))
        cases["all_commands"] = [str(c.session_id) for c in sent.commands]
        # A2-C1 (A2R-4; DM-99 item 2): neither the format override nor Accept is read.
        sent.result = ContactResult("authorized", receipt=receipt)
        Reads.answers = {"list": listed, "history": history, "cursor": moved}
        for view, body, method in (*((v, b, "post") for v, b in POSTS),
                                   (views.ConversationListView, None, "get")):
            name = view.__name__
            cases[f"{name}:format"] = answer(send(view, body, method=method,
                                                  path="/x?format=xml"))
            cases[f"{name}:format_unsigned"] = answer(send(view, body, method=method,
                                                           path="/x?format=xml", signed=False))
            cases[f"{name}:html"] = answer(send(view, body, method=method,
                                                headers={"HTTP_ACCEPT": "text/html"}))
        # A2-C1 (DM-99's AK2): every reason the send and a conversation's read raise once they
        # hold their first lock, through its route.
        for reason in __SEND_REASONS__:
            sent.result = ContactResult("refused", reason)
            cases[f"complete:send:{reason}"] = answer(send(views.MessageView, message))
        for reason in __CONVERSATION_REASONS__:
            Reads.answers = {"list": ListResult("refused", reason),
                             "history": ReadResult("refused", reason),
                             "cursor": CursorResult("refused", reason)}
            cases[f"complete:reads:{reason}"] = [
                answer(send(views.ConversationListView, None, method="get")),
                answer(send(views.HistoryView, page)),
                answer(send(views.ReadCursorView, cursor)),
            ]
        # The reads' refusals, each as error_for maps it, but the session's reasons in the locks
        # on a conversation's own reads (A2-C1; DM-99's AK1).
        for reason in ("match_not_active", "conversation_hidden", "blocked", "session_expired",
                       "message_unavailable", "session_not_valid", "session_epoch_stale",
                       "session_changed", "session_missing", "accountsession_missing"):
            Reads.answers = {"list": ListResult("refused", reason),
                             "history": ReadResult("refused", reason),
                             "cursor": CursorResult("refused", reason)}
            cases[f"reads:{reason}"] = [
                answer(send(views.ConversationListView, None, method="get")),
                answer(send(views.HistoryView, page)),
                answer(send(views.ReadCursorView, cursor)),
            ]
        Reads.answers = {"list": ListResult("error", "transaction_open"),
                         "history": ReadResult("error", "transaction_open"),
                         "cursor": CursorResult("error", "transaction_open")}
        cases["reads:transaction_open"] = [
            answer(send(views.ConversationListView, None, method="get")),
            answer(send(views.HistoryView, page)),
            answer(send(views.ReadCursorView, cursor)),
        ]

# The match list (D9).
entries = [discovery_contract.match_projection(str(uuid4()), 1, str(uuid4()), "active")]
listing = Result("read", data=discovery_contract.match_list(entries))
with mock.patch.object(interaction_views.interactions, "read_matches",
                       lambda account_id: listing):
    cases["matches"] = answer(send(interaction_views.MatchListView, None, method="get"))
    cases["matches:body"] = answer(send(interaction_views.MatchListView, json.dumps(page),
                                        method="get"))
    cases["matches:query"] = answer(send(interaction_views.MatchListView, None, method="get",
                                         path="/x?state=active"))
    cases["matches:method"] = answer(send(interaction_views.MatchListView, None))
    cases["matches:format"] = answer(send(interaction_views.MatchListView, None, method="get",
                                          path="/x?format=xml"))
    cases["matches:format_unsigned"] = answer(send(interaction_views.MatchListView, None,
                                                   method="get", path="/x?format=xml",
                                                   signed=False))
    cases["matches:html"] = answer(send(interaction_views.MatchListView, None, method="get",
                                        headers={"HTTP_ACCEPT": "text/html"}))
# SV3's other views keep DRF's negotiation (DM-99 item 2: carried to P10): the framework still
# answers the format override on the match read, as before.
from rest_framework.settings import api_settings
cases["sv3_negotiation"] = {
    view.__name__: view.content_negotiation_class is api_settings.DEFAULT_CONTENT_NEGOTIATION_CLASS
    for view in (interaction_views.InteractionView, interaction_views.UndoView,
                 interaction_views.UnmatchView, interaction_views.BlockView,
                 interaction_views.MatchView, interaction_views.OwnVersionsView)
}
framework = send(interaction_views.MatchView, None, method="get", path="/x?format=xml",
                 match_id=UUID(MATCH))
cases["MatchView:format"] = [framework.status_code, json.loads(framework.content),
                             framework.has_header("Cache-Control")]
print(json.dumps({
    "cases": cases,
    "actor_session": str(actor.session_id),
    "records": records,
    "record_echo": any(value in line for _, line in records for value in VALUES),
}))
"""


def routes() -> dict[str, object]:
    script = ROUTES.replace("__SEND_REASONS__", json.dumps(sorted(SEND_SERVED))).replace(
        "__CONVERSATION_REASONS__", json.dumps(sorted(CONVERSATION_SERVED))
    )
    return last_json(under_discovery_settings(script))


class RouteTests(unittest.TestCase):
    seen: dict[str, object] = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = routes()
        cls.cases = cls.seen["cases"]

    def case(self, name: str) -> dict[str, object]:
        found = self.cases[name]  # type: ignore[index]
        assert isinstance(found, dict)
        return found

    def assert_served(self, name: str, kind: str) -> None:
        found = self.case(name)
        self.assertEqual(
            (found["status"], found["kind"], found["valid"], found["echo"]),
            (200, kind, True, False),
        )
        self.assertEqual(found["cache"], "no-store")

    def assert_refused(self, name: str, status: int, code: str) -> None:
        found = self.case(name)
        self.assertEqual(
            (found["status"], found["code"], found["valid"], found["echo"]),
            (status, code, True, False),
            name,
        )
        self.assertEqual(found["cache"], "no-store")

    def test_each_route_answers_its_dto(self) -> None:
        self.assert_served("send", "message")
        self.assert_served("send_without_reader", "message")
        self.assert_served("list", "conversation_list")
        self.assert_served("history", "message_page")
        self.assert_served("cursor", "conversation")
        self.assert_served("matches", "match_list")
        body = self.case("list")["body"]
        assert isinstance(body, dict)
        self.assertEqual([c["state"] for c in body["data"]["conversations"]], ["read_only", "open"])
        cursor = self.case("cursor")["body"]
        assert isinstance(cursor, dict)
        self.assertEqual(cursor["data"]["state"], "read_only")
        self.assertEqual(cursor["data"]["unread_count"], 0)
        self.assertIsNotNone(cursor["data"]["latest"])

    def test_the_session_is_the_actors_only(self) -> None:
        session = self.seen["actor_session"]
        commands = self.case_list("commands")
        # Without the factory, with it, and with a header naming another session.
        self.assertEqual(len(commands), 3)
        # And every refused send after them: ten refusals and a deadlock.
        self.assertEqual(self.case_list("all_commands"), [session] * (3 + 11))
        for command in commands:
            self.assertEqual(command[0], session)
            self.assertEqual(
                command[1:], ["2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901", 1, "synthetic-key-zq7", True]
            )
        for call in self.case_list("calls"):
            self.assertEqual(call[1], session)
        self.assertEqual(set(self.case_list("providers")), {"fixture"})

    def case_list(self, name: str) -> list[object]:
        found = self.cases[name]  # type: ignore[index]
        assert isinstance(found, list)
        return found

    def test_the_reads_refuse_to_run_without_the_text_reader(self) -> None:
        for name in ("list", "history", "cursor"):
            with self.subTest(route=name):
                self.assert_refused(f"no_reader_{name}", 503, "provider_unavailable")
                self.assertFalse(self.case(f"no_reader_{name}")["retryable"])
        self.assertEqual(self.cases["no_reader_made"], 0)  # type: ignore[index]
        self.assertEqual(self.cases["no_reader_calls"], [])  # type: ignore[index]
        # With the factory, each read is made with the reader it returns.
        self.assertTrue(self.case_list("made"))
        self.assertTrue(all(self.case_list("made")))

    def test_each_route_refuses_what_is_not_its_request(self) -> None:
        for name in ("MessageView", "HistoryView", "ReadCursorView"):
            with self.subTest(route=name):
                for suffix in ("extra", "actor", "query", "type", "not_json"):
                    self.assert_refused(f"{name}:{suffix}", 400, "invalid_request")
                self.assert_refused(f"{name}:method", 405, "invalid_request")
                self.assert_refused(f"{name}:put", 405, "invalid_request")
                self.assert_refused(f"{name}:unsigned", 401, "unauthenticated")
        self.assert_refused("list:body", 400, "invalid_request")
        self.assert_refused("list:query", 400, "invalid_request")
        self.assert_refused("list:method", 405, "invalid_request")
        self.assert_refused("list:unsigned", 401, "unauthenticated")
        self.assert_refused("bad_cursor", 409, "stale_version")
        self.assert_refused("matches:body", 400, "invalid_request")
        self.assert_refused("matches:query", 400, "invalid_request")
        self.assert_refused("matches:method", 405, "invalid_request")

    def test_the_sends_five_refusals_answer_one_code(self) -> None:
        five = (
            "match_not_active",
            "blocked",
            "account_not_active",
            "profile_unavailable",
            "consent_not_current",
        )
        bodies = []
        for reason in five:
            with self.subTest(reason=reason):
                self.assert_refused(f"send:{reason}", 404, "not_found")
                body = self.case(f"send:{reason}")["body"]
                assert isinstance(body, dict)
                bodies.append({k: v for k, v in body.items() if k != "request_id"})
        self.assertEqual(len({json.dumps(b, sort_keys=True) for b in bodies}), 1)
        # A2-C1 (A2R-1, A2R-2; DM-99): a wrong version and a session found ended in the send's
        # locks answer the one code, with the same body.
        self.assert_refused("send:stale_contact_version", 404, "not_found")
        self.assert_refused("send:idempotency_conflict", 409, "idempotency_conflict")
        self.assert_refused("send:session_not_valid", 404, "not_found")
        for name in ("send:stale_contact_version", "send:session_not_valid"):
            body = self.case(name)["body"]
            assert isinstance(body, dict)
            self.assertIn({k: v for k, v in body.items() if k != "request_id"}, bodies, name)
        self.assert_refused("send:match_missing", 404, "not_found")
        self.assert_refused("send:not_a_member", 404, "not_found")
        self.assert_refused("send:deadlock", 409, "state_conflict")
        self.assertTrue(self.case("send:deadlock")["retryable"])

    def test_the_reads_refusals_are_error_fors(self) -> None:
        # Each as (the list, the history read, the read cursor). A2-C1 (DM-99's AK1): the
        # session's reasons in the locks answer the history and the cursor as a hidden
        # conversation (not_found); the list, session_missing and accountsession_missing keep 401.
        unauthenticated, not_found = (401, "unauthenticated"), (404, "not_found")
        in_locks = (unauthenticated, not_found, not_found)
        expected = {
            "match_not_active": (not_found,) * 3,
            "conversation_hidden": (not_found,) * 3,
            "blocked": (not_found,) * 3,
            "session_expired": in_locks,
            "message_unavailable": (not_found,) * 3,
            "transaction_open": ((409, "state_conflict"),) * 3,
            "session_not_valid": in_locks,
            "session_epoch_stale": in_locks,
            "session_changed": in_locks,
            "session_missing": (unauthenticated,) * 3,
            "accountsession_missing": (unauthenticated,) * 3,
        }
        for reason, answers in expected.items():
            founds = self.case_list(f"reads:{reason}")
            self.assertEqual(len(founds), 3)
            for found, (status, code) in zip(founds, answers, strict=True):
                with self.subTest(reason=reason):
                    assert isinstance(found, dict)
                    self.assertEqual(
                        (found["status"], found["code"], found["valid"], found["echo"]),
                        (status, code, True, False),
                    )

    def test_every_pinned_reason_is_served_with_its_code_and_status(self) -> None:
        # DM-99's AK2, through the routes: each reason MappingCompletenessTests reads from the
        # source, as the route serves it; every not_found has one body on the three routes.
        status = {"not_found": 404, "unauthenticated": 401, "idempotency_conflict": 409}
        bodies = set()
        answered: list[tuple[str, dict[str, object], tuple[str, bool]]] = []
        for reason, expected in SEND_SERVED.items():
            answered.append((f"send {reason}", self.case(f"complete:send:{reason}"), expected))
        for reason, expected in CONVERSATION_SERVED.items():
            listed, read, moved = self.case_list(f"complete:reads:{reason}")
            for route, found in (("history", read), ("cursor", moved)):
                assert isinstance(found, dict)
                answered.append((f"{route} {reason}", found, expected))
            assert isinstance(listed, dict)
            if reason in SESSION_IN_LOCKS:
                self.assertEqual((listed["status"], listed["code"]), (401, "unauthenticated"))
        for name, found, (code, retryable) in answered:
            with self.subTest(route=name):
                self.assertEqual(
                    (found["status"], found["code"], found["retryable"], found["valid"]),
                    (status[code], code, retryable, True),
                )
                self.assertFalse(found["echo"])
                self.assertEqual(found["cache"], "no-store")
                if code == "not_found":
                    body = found["body"]
                    assert isinstance(body, dict)
                    bodies.add(json.dumps({k: v for k, v in body.items() if k != "request_id"}))
        self.assertEqual(len(bodies), 1)

    def test_the_negotiation_reads_neither_accept_nor_format(self) -> None:
        # A2-C1 (A2R-4; DM-99 item 2), on the five routes: ?format=xml meets the routes' own
        # query-string refusal (400, or 401 unsigned), and Accept: text/html is served as JSON.
        served = {
            "MessageView": "message",
            "HistoryView": "message_page",
            "ReadCursorView": "conversation",
            "ConversationListView": "conversation_list",
            "matches": "match_list",
        }
        for name, kind in served.items():
            with self.subTest(route=name):
                self.assert_refused(f"{name}:format", 400, "invalid_request")
                self.assert_refused(f"{name}:format_unsigned", 401, "unauthenticated")
                self.assert_served(f"{name}:html", kind)

    def test_sv3s_other_views_keep_their_negotiation(self) -> None:
        self.assertEqual(
            self.cases["sv3_negotiation"],  # type: ignore[index]
            {
                name: True
                for name in (
                    "InteractionView",
                    "UndoView",
                    "UnmatchView",
                    "BlockView",
                    "MatchView",
                    "OwnVersionsView",
                )
            },
        )
        # The framework still answers the format override there, before authentication, with no
        # Cache-Control (carried to P10).
        self.assertEqual(
            self.cases["MatchView:format"],  # type: ignore[index]
            [404, {"detail": "Not found."}, False],
        )

    def test_the_routes_log_codes_only(self) -> None:
        self.assertFalse(self.seen["record_echo"])
        chat_records = [
            line
            for name, line in self.seen["records"]  # type: ignore[attr-defined]
            if name == "glow_chat.views"
        ]
        self.assertTrue(chat_records)
        for line in chat_records:
            with self.subTest(line=line):
                # A reason is a code: one of Glow's, or a database error's type name.
                self.assertRegex(line, r"^chat route refused: [A-Za-z_]+(:[A-Za-z_]+)?$")


# -- the structure (D8, D15) -----------------------------------------------------------------------

URLS = """
import json
from glow_chat import route_reads, urls, views
from glow_identity.authentication import GlowActorAuthentication
from rest_framework.permissions import IsAuthenticated
print(json.dumps({"routes": [
    [str(p.pattern), p.callback.view_class.__name__, p.callback.view_class.http_method_names,
     sorted(getattr(p.callback, "_non_atomic_requests", [])),
     p.callback.view_class.authentication_classes == [GlowActorAuthentication],
     p.callback.view_class.permission_classes == [IsAuthenticated]]
    for p in urls.urlpatterns
], "candidates": route_reads.CANDIDATES, "bound": route_reads.LIST_BOUND}))
"""


class StructureTests(unittest.TestCase):
    def test_the_four_routes_and_no_other(self) -> None:
        seen = last_json(under_discovery_settings(URLS))
        self.assertEqual(
            seen["routes"],
            [
                ["api/v1/chat/messages", "MessageView", ["post"], ["default"], True, True],
                [
                    "api/v1/chat/conversations",
                    "ConversationListView",
                    ["get"],
                    ["default"],
                    True,
                    True,
                ],
                ["api/v1/chat/history", "HistoryView", ["post"], ["default"], True, True],
                ["api/v1/chat/read-cursor", "ReadCursorView", ["post"], ["default"], True, True],
            ],
        )
        declaring = sorted(
            path.name
            for path in CHAT.glob("*.py")
            if any(
                isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "urlpatterns" for t in node.targets)
                for node in parsed(path).body
            )
        )
        self.assertEqual(declaring, ["urls.py"])

    def test_no_channel_intent_route(self) -> None:
        # OD-45: the client needs no channel entitlement; ChannelEntitlement stays unserved.
        for name in NEW_MODULES:
            tree = parsed(CHAT / name)
            strings = [
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            ]
            code = [text for text in strings if "ChannelIntent" in text and "``" not in text]
            names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            with self.subTest(module=name):
                self.assertEqual(code, [])
                self.assertFalse({"ChannelIntent", "ChannelEntitlement"} & names)

    def test_no_new_module_takes_a_writers_lock_or_imports_discovery(self) -> None:
        for name in NEW_MODULES:
            tree = parsed(CHAT / name)
            calls = {
                node.func.attr
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            strings = [
                node.value.upper()
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            ]
            with self.subTest(module=name):
                self.assertNotIn("select_for_update", calls)
                self.assertFalse(any("FOR UPDATE" in s or "FOR NO KEY" in s for s in strings))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        self.assertFalse((node.module or "").startswith("glow_discovery"))

    def test_the_list_bounds_its_candidates_before_its_first_lock(self) -> None:
        # D8 (the P11 plan's C1 finding 4): the candidates, with no lock, first; then each table
        # in one statement, accounts then matches then the session; then the setting's pointer.
        seen = last_json(under_discovery_settings(URLS))
        candidates = str(seen["candidates"])
        tree = parsed(CHAT / "route_reads.py")
        klass = next(
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "RouteConversationReads"
        )
        listing = next(
            n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == "_list"
        )
        order = [
            ast.unparse(node.func)
            for node in ast.walk(listing)
            if isinstance(node, ast.Call)
            and ast.unparse(node.func)
            in ("self.candidates", "_lock_many", "_lock_shared", "_history", "_clock")
        ]
        lines = {
            name: [
                node.lineno
                for node in ast.walk(listing)
                if isinstance(node, ast.Call) and ast.unparse(node.func) == name
            ]
            for name in ("self.candidates", "_lock_many", "_lock_shared", "_history", "_clock")
        }
        self.assertEqual(
            sorted(order),
            sorted(
                [
                    "self.candidates",
                    "_lock_many",
                    "_lock_many",
                    "_lock_shared",
                    "_history",
                    "_clock",
                ]
            ),
        )
        self.assertLess(max(lines["self.candidates"]), min(lines["_lock_many"]))
        self.assertLess(max(lines["_lock_many"]), min(lines["_lock_shared"]))
        self.assertLess(max(lines["_lock_shared"]), min(lines["_history"]))
        self.assertNotRegex(candidates.upper(), r"\bFOR\s+(UPDATE|SHARE|NO|KEY)\b")
        self.assertTrue(
            candidates.endswith("ORDER BY latest_at DESC NULLS LAST, m.id DESC LIMIT %s")
        )
        self.assertEqual(seen["bound"], 200)
        many = next(
            n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_lock_many"
        )
        sql = [node for node in ast.walk(many) if isinstance(node, ast.JoinedStr)]
        self.assertEqual(len(sql), 1)
        tail = sql[0].values[-1]
        assert isinstance(tail, ast.Constant)
        self.assertEqual(tail.value, " WHERE id = ANY(%s) ORDER BY id FOR SHARE")

    def test_the_views_log_a_constant_and_a_reason_only(self) -> None:
        tree = parsed(CHAT / "views.py")
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
        ]
        self.assertEqual(len(calls), 1)
        for node in calls:
            self.assertEqual(ast.unparse(node.args[0]), "'chat route refused: %s'")
            self.assertEqual(ast.unparse(node.args[1]), "reason")
            self.assertEqual(node.keywords, [])
        for name in NEW_MODULES:
            with self.subTest(module=name):
                called = {
                    ast.unparse(node.func)
                    for node in ast.walk(parsed(CHAT / name))
                    if isinstance(node, ast.Call)
                }
                self.assertNotIn("print", called)

    def test_the_views_read_the_body_only_through_the_contract(self) -> None:
        tree = parsed(CHAT / "views.py")
        reads = [
            ast.unparse(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute) and node.attr in ("data", "body", "POST", "GET")
        ]
        self.assertEqual(sorted(reads), ["request._request.body", "request._request.body"])


if __name__ == "__main__":
    unittest.main()
