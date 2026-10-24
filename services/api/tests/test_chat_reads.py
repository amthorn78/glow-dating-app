"""The conversation reads' offline parts (P06.2 Stage C1; the brief's "Stage C under
OD-45", points b and f, with DM-22's conditions).

No database: the page cursor (6.4), the page's assembly with the digest check (2.1),
the fixture provider's text read (point b), and the server's projections, each output
validated against the production schema (point f, 6.1, 6.2). The history read, the list
and the read-cursor command run against PostgreSQL in the database job's read phase
(``proofs/postgres-ordering``, ``read_phase.py``).
"""

from __future__ import annotations

import importlib.util
import logging
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from glow_domain import chat_projections as projections
from glow_domain.chat import SendCommand, request_digest
from glow_domain.chat_provider import (
    CHANNEL_UNAVAILABLE,
    OPERATIONS,
    PROVIDER_REJECTED,
    PROVIDER_UNAVAILABLE,
    TEXT_READ_LIMIT,
    ChatProviderError,
)
from glow_domain.chat_provider_fixtures import FixtureChatProvider
from glow_domain.chat_reads import (
    CURSOR_INVALID,
    PAGE_LIMIT,
    AcceptedRow,
    ConversationEntry,
    CursorError,
    HistoryMessage,
    HistoryPage,
    HistoryRequest,
    LatestMarker,
    ListResult,
    PageCursor,
    Reconciliation,
    UnsentRow,
    page_messages,
)

CONTRACTS = Path(__file__).resolve().parents[3] / "packages" / "contracts"
NOW = datetime(2026, 10, 24, 12, 0, 0, 750000, tzinfo=UTC)
MATCH = UUID("11111111-1111-4111-8111-111111111111")


def _runtime() -> Any:
    """The contracts package's own validator (``packages/contracts/runtime.py``)."""
    spec = importlib.util.spec_from_file_location(
        "glow_contracts_runtime", CONTRACTS / "runtime.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNTIME = _runtime()


def valid(definition: str, value: Any) -> bool:
    return bool(RUNTIME.valid("production", definition, value))


# Field names a provider's objects carry; none may reach a DTO (point f).
PROVIDER_KEYS = frozenset(
    {
        "provider_message_ref",
        "channel_ref",
        "cid",
        "user_id",
        "user",
        "member",
        "custom",
        "created_at",
        "updated_at",
        "deleted_at",
        "type",
        "event",
        "message",
        "html",
        "attachments",
    }
)


def keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        found = set(value)
        for item in value.values():
            found |= keys(item)
        return found
    if isinstance(value, list):
        return set().union(*(keys(item) for item in value)) if value else set()
    return set()


class RequestDigestTests(unittest.TestCase):
    def test_the_send_and_the_read_share_one_digest(self) -> None:
        command = SendCommand(uuid4(), MATCH, 3, "key", "hello")
        self.assertEqual(command.request_digest, request_digest(MATCH, 3, "hello"))
        self.assertNotEqual(request_digest(MATCH, 3, "hello"), request_digest(MATCH, 4, "hello"))


class PageCursorTests(unittest.TestCase):
    """DM-22 6.4: opaque, bound to its match, and never a provider ID."""

    def test_round_trip_and_form(self) -> None:
        for direction in ("older", "newer"):
            cursor = PageCursor(direction, MATCH, uuid4())  # type: ignore[arg-type]
            text = cursor.encode()
            self.assertEqual(PageCursor.decode(text), cursor)
            self.assertEqual(len(text), 47)
            self.assertRegex(text, r"^c[A-Za-z0-9_-]+$")
            self.assertNotIn(str(MATCH), text)
            self.assertTrue(
                valid("MessagePageRequest", {"match_id": str(MATCH), "cursor": text, "limit": 1})
            )

    def test_a_changed_or_foreign_text_is_refused(self) -> None:
        text = PageCursor("newer", MATCH, uuid4()).encode()
        flipped = text[:10] + ("A" if text[10] != "A" else "B") + text[11:]
        for bad in (
            "",
            text[:-1],
            text + "A",
            "x" + text[1:],
            text.replace("c", "d", 1),
            "c" + "_" * 46,
            "0123456789abcdef0123456789abcdef",  # a provider-shaped ID
            f"glow-match:{MATCH}",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(CursorError):
                    PageCursor.decode(bad)
        try:
            decoded = PageCursor.decode(flipped)
        except CursorError:
            return
        self.assertNotEqual(decoded, PageCursor.decode(text))

    def test_one_cursor_has_one_text(self) -> None:
        """A text whose last character differs only in the bits base64 leaves unused
        decodes to the same cursor; it is refused, so no two texts name one cursor."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        text = PageCursor("older", MATCH, uuid4()).encode()
        last = alphabet.index(text[-1])
        self.assertEqual(last % 4, 0)  # 34 bytes: the last character's two low bits unused
        variant = text[:-1] + alphabet[last + 1]
        with self.assertRaises(CursorError):
            PageCursor.decode(variant)

    def test_a_request_limit_outside_the_page_is_refused(self) -> None:
        for limit in (0, PAGE_LIMIT + 1):
            with self.assertRaises(ValueError):
                HistoryRequest(uuid4(), MATCH, None, limit)
        self.assertEqual(PAGE_LIMIT, TEXT_READ_LIMIT)
        self.assertEqual(PAGE_LIMIT, 50)


def accepted_row(
    text: str, *, version: int = 1, own: bool = False, ref: str | None = None
) -> AcceptedRow:
    return AcceptedRow(
        uuid4(), own, NOW, version, request_digest(MATCH, version, text), ref or uuid4().hex
    )


class PageAssemblyTests(unittest.TestCase):
    """DM-22 2.1: only text Glow sent is shown; anything else is unavailable and counted."""

    def test_exact_text_is_shown(self) -> None:
        row = accepted_row("hello")
        messages, counted = page_messages(MATCH, [row], [], {row.provider_message_ref: "hello"})
        self.assertEqual(messages[0].text, "hello")
        self.assertEqual(counted, Reconciliation())

    def test_a_text_altered_by_one_character_is_unavailable(self) -> None:
        row = accepted_row("hello")
        for altered in ("hellp", "hello ", " hello", "Hello", "helló", "hel​lo"):
            with self.subTest(altered=altered):
                messages, counted = page_messages(
                    MATCH, [row], [], {row.provider_message_ref: altered}
                )
                self.assertIsNone(messages[0].text)
                self.assertEqual(counted, Reconciliation(mismatched=1))

    def test_another_match_or_contact_version_is_unavailable(self) -> None:
        row = accepted_row("hello", version=2)
        other = AcceptedRow(
            row.submission_id, False, NOW, 2, request_digest(uuid4(), 2, "hello"), "r"
        )
        messages, counted = page_messages(MATCH, [other], [], {"r": "hello"})
        self.assertIsNone(messages[0].text)
        self.assertEqual(counted.mismatched, 1)

    def test_a_missing_message_is_unavailable_and_counted(self) -> None:
        rows = [accepted_row("one"), accepted_row("two")]
        texts: dict[str, object] = {rows[0].provider_message_ref: "one", "not-asked": "planted"}
        messages, counted = page_messages(MATCH, rows, [], texts)
        self.assertEqual([m.text for m in messages], ["one", None])
        self.assertEqual(counted, Reconciliation(missing=1, unrequested=1))
        bad: dict[str, object] = {rows[0].provider_message_ref: 7}
        _, counted = page_messages(MATCH, rows[:1], [], bad)
        self.assertEqual(counted.missing, 1)

    def test_the_members_unsent_follow_with_their_spool_text(self) -> None:
        row = accepted_row("one", own=True)
        pending = UnsentRow(uuid4(), NOW + timedelta(seconds=1), "pending", "on its way")
        failed = UnsentRow(uuid4(), NOW + timedelta(seconds=2), "failed", None)
        messages, _ = page_messages(
            MATCH, [row], [pending, failed], {row.provider_message_ref: "one"}
        )
        self.assertEqual(
            [(m.delivery, m.own, m.text) for m in messages],
            [("accepted", True, "one"), ("pending", True, "on its way"), ("failed", True, None)],
        )


class FixtureTextReadTests(unittest.TestCase):
    """Point b: the fixture answers from the messages it was sent, by the Stream adapter's
    rule; a test can plant, edit, retype or delete what it holds."""

    def setUp(self) -> None:
        self.provider = FixtureChatProvider("test")
        for user in ("ua", "ub"):
            self.provider.provision_user(user)
        self.provider.create_channel("c1", ("ua", "ub"))
        self.texts = {"m1": "first", "m2": "second", "m3": "third", "m4": "fourth"}
        for message_id, text in self.texts.items():
            self.provider.send_message("c1", "ua", message_id, text)

    def rows(self) -> list[AcceptedRow]:
        return [accepted_row(text, ref=ref) for ref, text in self.texts.items()]

    def test_answers_from_the_messages_it_was_sent(self) -> None:
        returned = self.provider.read_message_texts("c1", ("m1", "m2", "never-sent"))
        self.assertEqual(returned, {"m1": "first", "m2": "second"})
        call = self.provider.calls[-1]
        self.assertEqual(call.operation, "read_message_texts")
        self.assertEqual(call.arguments, OPERATIONS["read_message_texts"])

    def test_a_planted_message_glow_never_sent_never_reaches_a_page(self) -> None:
        self.provider.plant_message("c1", "planted", "a provider notice")
        self.assertEqual(
            self.provider.read_message_texts("c1", ("planted",)), {"planted": "a provider notice"}
        )
        refs = tuple(self.texts)
        returned = self.provider.read_message_texts("c1", refs)
        self.assertNotIn("planted", returned)  # Glow asks only for the IDs it committed
        messages, counted = page_messages(MATCH, self.rows(), [], returned)
        self.assertNotIn("a provider notice", [m.text for m in messages])
        self.assertEqual(counted, Reconciliation())

    def test_altered_deleted_system_and_error_messages_are_unavailable(self) -> None:
        self.provider.edit_message("c1", "m1", text="firsT")
        self.provider.delete_message("c1", "m2")
        self.provider.edit_message("c1", "m3", kind="system")
        self.provider.edit_message("c1", "m4", kind="error")
        returned = self.provider.read_message_texts("c1", tuple(self.texts))
        self.assertEqual(returned, {"m1": "firsT"})
        messages, counted = page_messages(MATCH, self.rows(), [], returned)
        self.assertEqual([m.text for m in messages], [None, None, None, None])
        self.assertEqual(counted, Reconciliation(missing=3, mismatched=1))

    def test_an_unknown_channel_and_failures_are_glow_codes(self) -> None:
        with self.assertRaises(ChatProviderError) as missing:
            self.provider.read_message_texts("no-such-channel", ("m1",))
        self.assertEqual(missing.exception.code, CHANNEL_UNAVAILABLE)
        self.provider.fail_next("read_message_texts")
        with self.assertRaises(ChatProviderError) as outage:
            self.provider.read_message_texts("c1", ("m1",))
        self.assertEqual(outage.exception.code, PROVIDER_UNAVAILABLE)
        self.provider.fail_next("read_message_texts", code=PROVIDER_REJECTED)
        with self.assertRaises(ChatProviderError) as rejected:
            self.provider.read_message_texts("c1", ("m1",))
        self.assertFalse(rejected.exception.retryable)

    def test_the_argument_rule(self) -> None:
        too_many = tuple(f"m{i}" for i in range(TEXT_READ_LIMIT + 1))
        calls = len(self.provider.calls)
        for bad in ((), too_many, ("m1", "m1"), ("",)):
            with self.subTest(count=len(bad)):
                with self.assertRaises(ValueError):
                    self.provider.read_message_texts("c1", bad)
        self.assertEqual(len(self.provider.calls), calls)  # refused before any call


def history_page(*messages: HistoryMessage, older: bool = True) -> HistoryPage:
    return HistoryPage(
        MATCH,
        messages,
        PageCursor("older", MATCH, messages[0].submission_id) if older and messages else None,
        PageCursor("newer", MATCH, messages[-1].submission_id) if messages else None,
        True,
        Reconciliation(),
    )


class ProjectionTests(unittest.TestCase):
    """Point f: every output validates against the production schema, and no provider ID
    or field can reach one."""

    def test_a_page_validates_and_carries_glows_fields_only(self) -> None:
        page = history_page(
            HistoryMessage(uuid4(), False, NOW, "accepted", "hello"),
            HistoryMessage(uuid4(), False, NOW, "accepted", None),
            HistoryMessage(uuid4(), True, NOW, "accepted", "mine"),
            HistoryMessage(uuid4(), True, NOW, "pending", "on its way"),
            HistoryMessage(uuid4(), True, NOW, "failed", None),
        )
        dto = projections.message_page(page)
        self.assertTrue(valid("MessagePage", dto))
        self.assertTrue(valid("AppResponse", projections.response(dto, uuid4())))
        self.assertFalse(keys(dto) & PROVIDER_KEYS)
        self.assertEqual(
            [(m["author"], m["content"], m["delivery"]) for m in dto["messages"]],
            [
                ("other", "text", None),
                ("other", "unavailable", None),
                ("own", "text", "accepted"),
                ("own", "text", "pending"),
                ("own", "unavailable", "failed"),
            ],
        )
        self.assertEqual(dto["messages"][0]["at"], "2026-10-24T12:00:00Z")  # truncated
        self.assertEqual(PageCursor.decode(dto["older_cursor"]).match_id, MATCH)

    def test_unavailable_is_one_state_with_no_reason(self) -> None:
        dto = projections.conversation_message(
            HistoryMessage(uuid4(), False, NOW, "accepted", None)
        )
        self.assertEqual(set(dto), {"submission_id", "author", "at", "content", "text", "delivery"})
        self.assertEqual((dto["content"], dto["text"]), ("unavailable", None))

    def test_another_members_unsent_submission_is_never_projected(self) -> None:
        for state in ("pending", "failed"):
            with self.assertRaises(ValueError):
                projections.conversation_message(HistoryMessage(uuid4(), False, NOW, state, "x"))  # type: ignore[arg-type]

    def test_the_list_and_a_summary_validate(self) -> None:
        marker = LatestMarker(uuid4(), NOW)
        result = ListResult(
            "listed",
            conversations=(
                ConversationEntry(MATCH, 3, marker),
                ConversationEntry(uuid4(), 0, None),
            ),
        )
        dto = projections.conversation_list(result)
        self.assertTrue(valid("ConversationList", dto))
        self.assertTrue(valid("AppResponse", projections.response(dto, uuid4())))
        self.assertEqual({c["state"] for c in dto["conversations"]}, {"open"})
        self.assertEqual(set(dto["conversations"][0]["latest"]), {"submission_id", "at"})
        self.assertFalse(keys(dto) & PROVIDER_KEYS)
        summary = projections.conversation_summary(ConversationEntry(MATCH, 1, None))
        self.assertTrue(valid("ConversationSummary", summary))
        with self.assertRaises(ValueError):
            projections.conversation_list(ListResult("refused", "blocked"))

    def test_refusals_map_to_glows_generic_codes(self) -> None:
        cases = {
            ("refused", "blocked"): ("not_found", False),
            ("refused", "match_not_active"): ("not_found", False),
            ("refused", "account_not_active"): ("not_found", False),
            ("refused", "profile_unavailable"): ("not_found", False),
            ("refused", "consent_not_current"): ("not_found", False),
            ("refused", "message_unavailable"): ("not_found", False),
            ("refused", "session_not_valid"): ("unauthenticated", False),
            ("refused", "session_epoch_stale"): ("unauthenticated", False),
            ("refused", CURSOR_INVALID): ("stale_version", False),
            ("refused", "provider_unavailable"): ("provider_unavailable", True),
            ("refused", "channel_unavailable"): ("provider_unavailable", False),
            ("deadlock", "DeadlockDetected"): ("state_conflict", True),
            ("error", "OperationalError"): ("state_conflict", False),
        }
        for (outcome, reason), wanted in cases.items():
            with self.subTest(reason=reason):
                self.assertEqual(projections.error_for(outcome, reason), wanted)
                dto = projections.error(outcome, reason, uuid4())
                self.assertTrue(valid("Error", dto))
                # The Glow code only: never the read's own reason or any other detail.
                self.assertEqual(set(dto), {"contract_version", "request_id", "code", "retryable"})
                self.assertEqual(dto["code"], wanted[0])

    def test_requests_name_the_session_never_an_actor_field(self) -> None:
        session = uuid4()
        cursor = PageCursor("newer", MATCH, uuid4())
        request = projections.page_request(
            {"match_id": str(MATCH), "cursor": cursor.encode(), "limit": 20}, session
        )
        self.assertEqual(request, HistoryRequest(session, MATCH, cursor, 20))
        with self.assertRaises(CursorError):
            projections.page_request(
                {"match_id": str(MATCH), "cursor": "cAAAA", "limit": 1}, session
            )
        target = uuid4()
        command = projections.read_cursor_command(
            {"operation": "read_cursor", "match_id": str(MATCH), "submission_id": str(target)},
            session,
        )
        self.assertEqual((command.session_id, command.submission_id), (session, target))

    def test_no_text_in_any_log_line(self) -> None:
        """DM-22 2.5: the projections log nothing, at any level."""
        records: list[logging.LogRecord] = []

        class Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record)

        root = logging.getLogger()
        handler = Capture(level=logging.DEBUG)
        saved = root.level
        root.addHandler(handler)
        root.setLevel(logging.DEBUG)
        try:
            projections.message_page(
                history_page(HistoryMessage(uuid4(), True, NOW, "pending", "a private text"))
            )
            projections.error("refused", "blocked", uuid4())
        finally:
            root.removeHandler(handler)
            root.setLevel(saved)
        self.assertFalse([r for r in records if "a private text" in r.getMessage()])
        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
