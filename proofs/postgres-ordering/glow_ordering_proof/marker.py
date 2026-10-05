"""The run's marker, checked on every new connection (brief D1; DM-10 2.2).

A loopback host names a route, not a database. So the proof's settings register
``verify_new_connection`` on Django's ``connection_created`` signal, which every
management command and the proof's own commands load with the settings. Django sends
the signal once a new connection exists and has run only its own session settings (its
time zone, and a role if one were configured; the proof configures none). The check's
single ``SELECT`` is the connection's first statement after them: in autocommit, with
no transaction that writes and no row lock. It reads the comment of the connection's
own database and refuses, closing the connection through Django so that nothing keeps
it, unless the comment is exactly ``glow-ordering-proof:`` followed by the run's marker.

A refusal names ``PROOF_DB_MARKER`` and never a value: not the marker, not the expected
comment, not the comment found.
"""

from __future__ import annotations

import threading
from typing import Any

from django.db.backends.signals import connection_created

from glow_ordering_proof.environment import MARKER

DISPATCH_UID = "glow_ordering_proof.marker.verify_new_connection"

# The comment of the connection's own database, and the backend's pid for the log.
QUERY = (
    "SELECT pg_catalog.pg_backend_pid(),"
    " pg_catalog.shobj_description(d.oid, 'pg_database')"
    " FROM pg_catalog.pg_database AS d"
    " WHERE d.datname = pg_catalog.current_database()"
)

REFUSAL = "refusing this database: its comment is not the run's marker"
# DM-12: dbshell starts psql outside Django, where this check never runs.
DBSHELL_REFUSAL = "refusing dbshell under the proof's settings"


class RefusedDatabase(Exception):
    """The connected database does not carry the run's marker.

    Deliberately not a ``django.db.DatabaseError``: Django handles some of those itself
    (``makemigrations`` turns an ``OperationalError`` into a warning and carries on), and
    this refusal must end every command with a non-zero status.
    """


_expected: str | None = None


def install(expected_comment: str) -> None:
    """Called by the proof's settings: every new connection is checked from now on."""
    global _expected
    _expected = expected_comment
    connection_created.connect(verify_new_connection, weak=False, dispatch_uid=DISPATCH_UID)


def _refuse(connection: Any, reason: str) -> RefusedDatabase:
    connection.close()
    return RefusedDatabase(
        f"{REFUSAL} ({MARKER}): {reason}. The proof runs only against the disposable"
        " database created for this run, whose comment the creator set with that run's"
        f" {MARKER}; the connection is closed"
    )


def refuse_dbshell() -> RefusedDatabase:
    """The refusal of ``dbshell``, before any connection: ``psql`` would connect with
    the proof's options outside Django, so the marker could not be checked."""
    return RefusedDatabase(
        f"{DBSHELL_REFUSAL} ({MARKER}): it starts psql outside Django, where the run's"
        " marker is never checked; no connection was opened and no client was started"
    )


def verify_new_connection(sender: object, connection: Any, **kwargs: object) -> None:
    """The ``connection_created`` receiver: pass, or close the connection and raise."""
    expected = _expected
    if expected is None:
        raise _refuse(connection, "no marker is installed")
    try:
        with connection.cursor() as cursor:
            cursor.execute(QUERY)
            row = cursor.fetchone()
    except BaseException:
        connection.close()
        raise
    if row is None:
        raise _refuse(connection, "no row describes the current database")
    pid, comment = row
    if comment is None:
        raise _refuse(connection, "the database has no comment")
    if not isinstance(comment, str) or comment != expected:
        raise _refuse(connection, "the database's comment is different")
    print(
        f"database marker verified on a new connection: backend pid {pid},"
        f" thread {threading.current_thread().name}",
        flush=True,
    )
