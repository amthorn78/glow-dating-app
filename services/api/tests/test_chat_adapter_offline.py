"""P06.2 Stage B1's offline tests of the persistence adapter (F4, F5): the adapter's
modules load under the static model registry in a fresh process, and its transaction
plumbing runs against a fake connection, so no database is opened.

The adapter's locks, checks and writes are proven by the disposable-database proof
(``proofs/postgres-ordering``); these tests cover what needs no database: the mapping of
a deadlock by its SQLSTATE in ``_run`` (F4), and the refusal of a self-block before any
lock or write (F5).
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]

PRELUDE = """
import sys
from datetime import UTC, datetime
from unittest import mock
from uuid import uuid4
from glow_persistence.static_check import no_database_access, setup_static_registry
with no_database_access():
    setup_static_registry()
    from django.db import IntegrityError
    from glow_chat import contact
    from glow_domain import chat

    T0 = datetime(2026, 10, 6, 12, 0, tzinfo=UTC)

    class FakeCursor:
        # The statements _run makes itself: the backend and start, and the clock.
        def __init__(self):
            self.statements = []
        def execute(self, sql, params=None):
            self.statements.append(sql)
            if "pg_backend_pid" in sql:
                self.row = (4242, T0)
            elif "clock_timestamp" in sql:
                self.row = (T0,)
            else:
                raise AssertionError("an unexpected statement: " + sql)
        def fetchone(self):
            return self.row

    class FakeConnection:
        def __init__(self):
            self.cursors = []
        def cursor(self):
            cursor = FakeCursor()
            self.cursors.append(cursor)
            return cursor

    class Atomic:
        def __enter__(self):
            return self
        def __exit__(self, *exc):
            return False

    adapter = contact.OrmContactPersistence(provider="fixture")
    fake = FakeConnection()
    patches = [
        mock.patch.object(contact, "connection", fake),
        mock.patch.object(contact.transaction, "atomic", lambda: Atomic()),
    ]
    for patch in patches:
        patch.start()
"""


class OfflineAdapterTests(unittest.TestCase):
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

    def test_f4_a_deadlock_is_mapped_by_its_sqlstate(self) -> None:
        """F4: the driver's DeadlockDetected is recognized by SQLSTATE 40P01 on the
        exception's cause, without importing the driver; any other SQLSTATE, an
        IntegrityError and an unrelated error are results of outcome ``error``."""
        self.check_script("""
class DriverError(Exception):
    def __init__(self, sqlstate):
        super().__init__("driver text that must not matter")
        self.sqlstate = sqlstate

def failing(cause):
    def body(tx):
        raise RuntimeError("wrapped") from cause
    return body

deadlock = adapter._run(failing(DriverError("40P01")), None)
assert deadlock.outcome == "deadlock" and deadlock.reason == "DeadlockDetected", deadlock
assert deadlock.trace is not None and deadlock.trace.backend_pid == 4242
assert "driver text" not in deadlock.reason
other = adapter._run(failing(DriverError("40001")), None)  # serialization_failure
assert other.outcome == "error" and other.reason == "RuntimeError", other
plain = adapter._run(failing(None), None)
assert plain.outcome == "error" and plain.reason == "RuntimeError", plain

def integrity(tx):
    raise IntegrityError("constraint text") from DriverError("23514")
broken = adapter._run(integrity, None)
assert broken.outcome == "error" and broken.reason == "IntegrityError:DriverError", broken

def refused(tx):
    raise contact._Refused("some_reason")
result = adapter._run(refused, None)
assert result.outcome == "refused" and result.reason == "some_reason", result
assert result.trace is not None and result.trace.ended_at == T0
""")

    def test_f5_a_self_block_is_refused_before_any_lock_or_write(self) -> None:
        """F5: a block whose actor is its target is refused with a Glow code before the
        adapter locks or writes anything; the no-self constraint is never reached."""
        self.check_script("""
untouched = mock.Mock()
untouched.objects.select_for_update.side_effect = AssertionError("a lock was taken")
untouched.objects.create.side_effect = AssertionError("a row was written")
account = uuid4()
with (
    mock.patch.object(contact, "AppAccount", untouched),
    mock.patch.object(contact, "Match", untouched),
    mock.patch.object(contact, "Block", untouched),
):
    result = adapter.block(account, account)
assert result.outcome == "refused" and result.reason == chat.SELF_TARGET, result
assert result.reason == "self_target"
untouched.objects.select_for_update.assert_not_called()
untouched.objects.create.assert_not_called()
# Only _run's own statements ran: the backend and start, and the clock before the rollback.
statements = [s for cursor in fake.cursors for s in cursor.statements]
assert statements == ["SELECT pg_backend_pid(), now()", "SELECT clock_timestamp()"], statements
""")

    def test_the_adapter_has_no_switch_and_the_grant_is_on_the_port(self) -> None:
        """DM-13 2.1 still holds after B1, and the new grant is a port method the
        adapter implements with the same signature."""
        self.check_script("""
import inspect
assert vars(adapter) == {"provider": "fixture"}
source = inspect.getsource(contact)
for word in ("Design(", "design.", "lock_accounts", "check_contact_version", "filter_state"):
    assert word not in source, word
assert "FOR SHARE" in source and "clock_timestamp()" in source
port = inspect.signature(chat.ContactPersistence.grant_token)
mine = inspect.signature(contact.OrmContactPersistence.grant_token)
assert list(port.parameters) == list(mine.parameters) == ["self", "session_id", "probe"]
""")


if __name__ == "__main__":
    unittest.main()
