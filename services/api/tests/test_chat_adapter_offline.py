"""P06.2 Stage B1's offline tests of the persistence adapter (F4, F5) and of the
delivery's dead-letter plans (B1-C1): the modules load under the static model registry in
a fresh process, and the transaction plumbing runs against a fake connection, so no
database is opened.

The adapter's locks, checks and writes are proven by the disposable-database proof
(``proofs/postgres-ordering``); these tests cover what needs no database: the mapping of
a deadlock by its SQLSTATE in ``_run`` (F4), the refusal of a self-block before any lock
or write (F5), the grant's single ``before_commit`` signal (B1-C1 R2), and the mark of
every dead letter that concerns a row (B1-C1 R3).
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

    def test_r2_the_grant_signals_before_commit_once(self) -> None:
        """B1-C1 R2: the grant's body no longer signals ``before_commit``; ``_run`` does,
        once, after the body, as for every other writer. A refused grant commits nothing
        and is not signalled, also as for every other writer."""
        self.check_script("""
from datetime import timedelta
session_id, account_id = uuid4(), uuid4()

class GrantCursor(FakeCursor):
    # The grant's two shared locks, by primary key, answered as the locked rows.
    def execute(self, sql, params=None):
        if "FOR SHARE" in sql and "glow_persistence_appaccount" in sql:
            self.statements.append(sql)
            self.row = ("active", 1)
        elif "FOR SHARE" in sql and "glow_persistence_accountsession" in sql:
            self.statements.append(sql)
            self.row = (account_id, "valid", 1, T0 + timedelta(minutes=5))
        else:
            super().execute(sql, params)

def grant_cursor():
    cursor = GrantCursor()
    fake.cursors.append(cursor)
    return cursor

fake.cursor = grant_cursor
sessions = mock.Mock()
sessions.objects.filter.return_value.values_list.return_value.first.return_value = account_id
identities = mock.Mock()

def grant(identity_state):
    identities.objects.filter.return_value.values_list.return_value.first.return_value = (
        "a" * 32,
        identity_state,
    )
    signals = []
    probe = chat.TransactionProbe(
        after_locks=lambda: signals.append("after_locks"),
        before_commit=lambda: signals.append("before_commit"),
    )
    with (
        mock.patch.object(contact, "AccountSession", sessions),
        mock.patch.object(contact, "ChatIdentity", identities),
    ):
        return adapter.grant_token(session_id, probe=probe), signals

granted, signals = grant("active")
assert granted.outcome == "granted", granted
assert granted.grant is not None and granted.grant.issued_at == T0, granted.grant
assert signals == ["after_locks", "before_commit"], signals
refused, signals = grant("pending")
assert refused.outcome == "refused" and refused.reason == "no_chat_identity", refused
assert signals == ["after_locks"], signals
""")

    def test_r3_every_dead_letter_that_concerns_a_row_marks_it(self) -> None:
        """B1-C1 R3 (F3's rule): the dead letters made without a call, a provisioning or
        a channel's creation for another provider's row, and a removal for another
        provider's binding or one whose members or channel reference are missing, mark
        their identity or binding through the dead-letter path; an event whose row does
        not exist has nothing to mark, and a contact revocation with no binding is no
        dead letter at all."""
        self.check_script("""
from glow_chat import delivery, events
from glow_domain.chat_provider import MEMBER_UNAVAILABLE, PROVIDER_REJECTED
from glow_domain.chat_provider_fixtures import FixtureChatProvider

marks = []

def mark_binding(binding_id, code, *, fail_pending):
    marks.append(("binding", binding_id, code, fail_pending))

def mark_identity(identity_id, code):
    marks.append(("identity", identity_id, code))

def model(first=None, values=None):
    rows = mock.Mock()
    rows.objects.filter.return_value.first.return_value = first
    rows.objects.filter.return_value.values_list.return_value.first.return_value = values
    return rows

deliverer = delivery.OutboxDelivery(FixtureChatProvider(environment="test"))

def dead_letter(kind, *, identity=None, binding=None, pair=None, submission=None):
    # One event of ``kind``: its plan, then the dead-letter path of ``_settle``.
    del marks[:]
    event = mock.Mock(
        event_type=kind, payload_ref=uuid4(), aggregate_id=uuid4(), attempts=1, version=1
    )
    with (
        mock.patch.object(delivery, "ChatIdentity", model(first=identity)),
        mock.patch.object(delivery, "ChatBinding", model(first=binding)),
        mock.patch.object(delivery, "Match", model(values=pair)),
        mock.patch.object(delivery, "MessageSubmission", model(first=submission)),
        mock.patch.object(delivery, "_mark_binding", mark_binding),
        mock.patch.object(delivery, "_mark_identity", mark_identity),
    ):
        plan = deliverer._plan(event)
        assert plan.call is None, kind
        if plan.code is None:
            return plan, None
        done = deliverer._settle(event, plan, None, plan.code, T0, provider_called=False)
    assert done.outcome == "dead_letter" and event.state == "dead_letter", done
    return plan, done

elsewhere = mock.Mock(id=uuid4(), provider="elsewhere", user_ref="b" * 32, state="pending")
plan, done = dead_letter(events.IDENTITY_CREATED, identity=elsewhere)
assert done.code == PROVIDER_REJECTED
assert marks == [("identity", elsewhere.id, PROVIDER_REJECTED)], marks

other_binding = mock.Mock(id=uuid4(), provider="elsewhere", match_id=uuid4(), channel_ref="c" * 32)
plan, done = dead_letter(events.MATCH_ACTIVATED, binding=other_binding)
assert done.code == PROVIDER_REJECTED
assert marks == [("binding", other_binding.id, PROVIDER_REJECTED, True)], marks
plan, done = dead_letter(events.CONTACT_REVOKED, binding=other_binding)
assert done.code == PROVIDER_REJECTED
assert marks == [("binding", other_binding.id, PROVIDER_REJECTED, False)], marks

bound = mock.Mock(id=uuid4(), provider="fixture", match_id=uuid4(), channel_ref="d" * 32)
plan, done = dead_letter(events.CONTACT_REVOKED, binding=bound, pair=None)  # no match
assert done.code == MEMBER_UNAVAILABLE
assert marks == [("binding", bound.id, MEMBER_UNAVAILABLE, False)], marks
plan, done = dead_letter(events.CONTACT_REVOKED, binding=bound, pair=(uuid4(), uuid4()))
assert done.code == MEMBER_UNAVAILABLE  # the match, but no identity
assert marks == [("binding", bound.id, MEMBER_UNAVAILABLE, False)], marks
member = mock.Mock(user_ref="e" * 32, state="active")
unbound = mock.Mock(id=uuid4(), provider="fixture", match_id=uuid4(), channel_ref=None)
plan, done = dead_letter(
    events.CONTACT_REVOKED, binding=unbound, identity=member, pair=(uuid4(), uuid4())
)
assert done.code == MEMBER_UNAVAILABLE  # both identities, no channel reference
assert marks == [("binding", unbound.id, MEMBER_UNAVAILABLE, False)], marks

# No row to mark: the event's own row does not exist, or the kind is unknown.
for kind in (events.IDENTITY_CREATED, events.MATCH_ACTIVATED, events.MESSAGE_SUBMITTED):
    plan, done = dead_letter(kind)
    assert done.code == PROVIDER_REJECTED and plan.on_dead_letter is delivery._nothing, kind
    assert marks == [], (kind, marks)
plan, done = dead_letter("an_unknown_kind")
assert done.code == PROVIDER_REJECTED and plan.on_dead_letter is delivery._nothing
assert marks == []
# A contact revocation for a match that never had a binding is no dead letter.
plan, done = dead_letter(events.CONTACT_REVOKED)
assert done is None and plan.on_dead_letter is delivery._nothing and marks == []
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
