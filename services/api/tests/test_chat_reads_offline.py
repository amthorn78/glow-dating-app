"""P06.2 Stage C1-C1's offline tests of the conversation reads' adapter
(``glow_chat.reads``): the module loads under the static model registry in a fresh
process, and no database is opened.

The reads' locks, checks and their order against revocations are proven by the
disposable-database proof (``proofs/postgres-ordering``, the read phase); these tests
cover what needs no database:

- C1-C2 (C1-C1's re-review, R1): a read refuses before any statement while its caller has
  a transaction open, an atomic block or autocommit off, and its body never runs; the
  history read's second line before the provider call refuses both, with no provider
  call;
- finding 1 (DM-22 3.2): a read's transaction is durable, so inside an enclosing atomic
  block it is an ``error`` result before any statement and its body never runs; and the
  history read's assertion before the provider call refuses an open atomic block with no
  provider call;
- finding 10: the reason ``_lock_shared`` gives for a missing session row is the one the
  projection maps to ``unauthenticated``.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]

PRELUDE = """
from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4
from glow_persistence.static_check import no_database_access, setup_static_registry
with no_database_access():
    setup_static_registry()
    from django.db import connections
    from glow_chat import reads
    from glow_domain import chat_projections as projections
    from glow_domain.chat_reads import AcceptedRow, HistoryRequest
    from glow_persistence.models import AccountSession

    T0 = datetime(2026, 10, 24, 12, 0, tzinfo=UTC)

    class RecordingTexts:
        # The text read, recording each call; it answers every asked ID.
        def __init__(self):
            self.calls = []
        def read_message_texts(self, channel_id, message_ids):
            self.calls.append((channel_id, message_ids))
            return {ref: "a text" for ref in message_ids}
"""


class OfflineReadsTests(unittest.TestCase):
    def check_script(self, assertions: str) -> None:
        body = "\n".join("    " + line for line in assertions.splitlines())
        result = subprocess.run(
            [sys.executable, "-c", PRELUDE + body],
            cwd=API_ROOT,
            env={**os.environ, "GLOW_ENV": "test"},
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_read_refuses_a_callers_open_transaction_before_any_statement(self) -> None:
        """C1-C2, R1: with autocommit off, or with an atomic block open (a Django test
        case's included), ``_run`` returns ``error``, ``transaction_open``, with no trace,
        before it enters its block; the body never runs. The checks need no connection:
        no statement is made."""
        self.check_script("""
default = connections["default"]
for in_block, autocommit in ((False, False), (True, False), (True, True)):
    ran = []
    with (
        mock.patch.object(default, "in_atomic_block", in_block),
        mock.patch.object(default, "get_autocommit", return_value=autocommit),
        mock.patch.object(default, "cursor", side_effect=AssertionError("a statement")),
    ):
        result = reads._run(lambda cursor, probe: ran.append(1), None)
    assert result == (None, "error", reads.TRANSACTION_OPEN, None), (in_block, autocommit, result)
    assert reads.TRANSACTION_OPEN == "transaction_open"
    assert ran == [], (in_block, autocommit)
    assert projections.error_for("error", reads.TRANSACTION_OPEN) == ("state_conflict", False)
# A connection that cannot be opened while autocommit is read is an ``error`` result,
# as any other database error is, never an exception out of the read.
with mock.patch.object(default, "get_autocommit", side_effect=RuntimeError("no database")):
    result = reads._run(lambda cursor, probe: ran.append(1), None)
assert result == (None, "error", "RuntimeError", None), result
""")

    def test_a_read_inside_an_open_atomic_block_is_an_error_before_any_statement(
        self,
    ) -> None:
        """Finding 1: ``_run``'s block is durable. With an atomic block already open on
        the connection (not a Django test case's), entering it raises before any
        statement; the result is ``error``, with no trace, and the body never runs. The
        caller-transaction check is held passing here, so the durable flag is what refuses
        (C1-C2 keeps it behind that check)."""
        self.check_script("""
class Outer:
    _from_testcase = False

ran = []
default = connections["default"]
with (
    mock.patch.object(default, "atomic_blocks", [Outer()]),
    mock.patch.object(reads, "_caller_transaction_open", return_value=False),
):
    value, outcome, reason, trace = reads._run(lambda cursor, probe: ran.append(1), None)
assert (value, outcome, reason, trace) == (None, "error", "RuntimeError", None), (
    value, outcome, reason, trace)
assert ran == [], "the body ran inside an enclosing atomic block"
""")

    def test_the_history_read_refuses_an_open_atomic_block_before_the_provider_call(
        self,
    ) -> None:
        """Finding 1: with the first check passed and an atomic block open, the history
        read returns ``error`` and calls no provider; with none open, the same read calls
        the provider once and returns its page."""
        self.check_script("""
match_id, submission_id = uuid4(), uuid4()
row = AcceptedRow(submission_id, False, T0, 1, "digest", "provider-message-1")
selected = reads._Selected("channel-1", (row,), (), None, None)
request = HistoryRequest(uuid4(), match_id, None, 50)

def read(in_atomic_block, autocommit=True):
    texts = RecordingTexts()
    adapter = reads.OrmConversationReads(texts)
    open_block = mock.Mock(in_atomic_block=in_atomic_block)
    open_block.get_autocommit.return_value = autocommit
    with (
        mock.patch.object(reads, "connection", open_block),
        mock.patch.object(adapter, "_first_check", return_value=(selected, None, None)),
        mock.patch.object(adapter, "_final_check", return_value=("ok", "", None)),
    ):
        return adapter.read_history(request), texts.calls

refused, calls = read(True)
assert refused.outcome == "error" and refused.reason == reads.ATOMIC_BLOCK_OPEN, refused
assert refused.reason == "atomic_block_open"
assert refused.page is None and calls == [], (refused, calls)
assert projections.error_for(refused.outcome, refused.reason) == ("state_conflict", False)
served, calls = read(False)
assert served.outcome == "read" and served.page is not None, served
assert calls == [("channel-1", ("provider-message-1",))], calls
""")

    def test_the_history_read_refuses_autocommit_off_before_the_provider_call(self) -> None:
        """C1-C2, R1: the second line before the provider call also refuses a connection
        with autocommit off and no atomic block (``transaction.set_autocommit(False)``),
        with ``error``, ``transaction_open`` and no provider call. ``_run``'s own check is
        the first line; the first check is replaced here, so this line is what refuses."""
        self.check_script("""
match_id, submission_id = uuid4(), uuid4()
row = AcceptedRow(submission_id, False, T0, 1, "digest", "provider-message-1")
selected = reads._Selected("channel-1", (row,), (), None, None)
request = HistoryRequest(uuid4(), match_id, None, 50)
texts = RecordingTexts()
adapter = reads.OrmConversationReads(texts)
autocommit_off = mock.Mock(in_atomic_block=False)
autocommit_off.get_autocommit.return_value = False
with (
    mock.patch.object(reads, "connection", autocommit_off),
    mock.patch.object(adapter, "_first_check", return_value=(selected, None, None)),
    mock.patch.object(adapter, "_final_check", return_value=("ok", "", None)),
):
    refused = adapter.read_history(request)
assert refused.outcome == "error" and refused.reason == reads.TRANSACTION_OPEN, refused
assert refused.page is None and texts.calls == [], (refused, texts.calls)
assert projections.error_for(refused.outcome, refused.reason) == ("state_conflict", False)
""")

    def test_a_missing_session_row_maps_to_unauthenticated(self) -> None:
        """Finding 10: the projection's ``accountsession_missing`` is the reason
        ``_lock_shared`` (``glow_chat.contact``, shared by the reads) gives when the
        session's row is gone, for the table the model names."""
        self.check_script("""
class EmptyCursor:
    def execute(self, sql, params=None):
        assert sql.endswith("FOR SHARE"), sql
    def fetchone(self):
        return None

try:
    reads._lock_shared(
        AccountSession._meta.db_table, uuid4(), ("account_id", "state"), EmptyCursor()
    )
except reads._Refused as refused:
    reason = refused.reason
else:
    raise AssertionError("a missing session row was not refused")
assert projections.error_for("refused", reason) == ("unauthenticated", False), reason
""")


if __name__ == "__main__":
    unittest.main()
