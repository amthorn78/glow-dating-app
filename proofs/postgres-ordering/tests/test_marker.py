"""The run's marker (brief D1; DM-10 2.1 and 2.2), shown without a database: the marker's
form, the settings' refusal at import, and the connection check against a fake
connection and cursor."""

from __future__ import annotations

import importlib
import io
import os
import secrets
import sys
import unittest
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stdout
from typing import Any

from django.db import DatabaseError
from django.db.backends.signals import connection_created

from glow_ordering_proof import environment, marker
from tests.test_settings_refusals import GOOD

MARKER_VALUE = GOOD[environment.MARKER]
EXPECTED = environment.MARKER_COMMENT_PREFIX + MARKER_VALUE


class FakeCursor:
    """Answers the marker query with one scripted row, and records every statement."""

    def __init__(self, row: tuple[Any, ...] | None) -> None:
        self.row = row
        self.executed: list[str] = []

    def execute(self, sql: str, params: object = None) -> None:
        self.executed.append(sql)

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.row


class FakeDjangoConnection:
    """A stand-in for a Django database wrapper that has just connected."""

    def __init__(self, row: tuple[Any, ...] | None) -> None:
        self.cursor_ = FakeCursor(row)
        self.closed = 0

    @contextmanager
    def cursor(self) -> Iterator[FakeCursor]:
        yield self.cursor_

    def close(self) -> None:
        self.closed += 1


@contextmanager
def installed(expected: str | None) -> Iterator[None]:
    saved = marker._expected
    marker._expected = expected
    try:
        yield
    finally:
        marker._expected = saved


def values_in(text: str) -> list[str]:
    """Any value a refusal must never carry."""
    return [v for v in (MARKER_VALUE, EXPECTED) if v in text]


class MarkerFormTests(unittest.TestCase):
    def test_a_token_hex_16_marker_is_accepted(self) -> None:
        for _ in range(20):
            value = secrets.token_hex(16)
            self.assertEqual(environment.database_marker({environment.MARKER: value}), value)

    def test_the_expected_comment_is_the_prefix_and_the_marker(self) -> None:
        self.assertEqual(environment.MARKER_COMMENT_PREFIX, "glow-ordering-proof:")
        self.assertEqual(environment.expected_comment(MARKER_VALUE), EXPECTED)

    def test_the_marker_is_one_of_the_proofs_own_names(self) -> None:
        self.assertEqual(environment.MARKER, "PROOF_DB_MARKER")
        self.assertIn(environment.MARKER, environment.PROOF_NAMES)

    def test_a_missing_marker_is_refused(self) -> None:
        with self.assertRaises(environment.RefusedConnection) as ctx:
            environment.database_marker({})
        self.assertIn(environment.MARKER, str(ctx.exception))
        bad = dict(GOOD)
        del bad[environment.MARKER]
        with self.assertRaises(environment.RefusedConnection) as ctx:
            environment.connection_options(bad)
        self.assertIn(environment.MARKER, str(ctx.exception))

    def test_malformed_markers_are_refused_by_name_never_by_value(self) -> None:
        cases = {
            "empty": "",
            "short": MARKER_VALUE[:31],
            "long": MARKER_VALUE + "0",
            "upper case": "A" + MARKER_VALUE[1:].upper(),
            "non-hex": "g" * 32,
            "leading space": " " + MARKER_VALUE,
            "trailing space": MARKER_VALUE + " ",
            "trailing newline": MARKER_VALUE + "\n",
            "prefixed with 0x": "0x" + MARKER_VALUE[:30],
            "prefixed with the comment prefix": environment.MARKER_COMMENT_PREFIX + MARKER_VALUE,
            "the bare prefix": environment.MARKER_COMMENT_PREFIX,
        }
        for label, value in cases.items():
            with self.subTest(label):
                with self.assertRaises(environment.RefusedConnection) as ctx:
                    environment.database_marker({environment.MARKER: value})
                message = str(ctx.exception)
                self.assertIn(environment.MARKER, message)
                if value.strip():
                    self.assertNotIn(value.strip(), message)
                self.assertEqual(values_in(message), [])


class SettingsMarkerTests(unittest.TestCase):
    def import_settings(self, environ: dict[str, str]) -> Any:
        saved = dict(os.environ)
        sys.modules.pop("glow_ordering_proof.settings", None)
        try:
            os.environ.clear()
            os.environ.update(environ)
            return importlib.import_module("glow_ordering_proof.settings")
        finally:
            os.environ.clear()
            os.environ.update(saved)
            sys.modules.pop("glow_ordering_proof.settings", None)

    def test_settings_refuse_a_missing_or_malformed_marker_at_import(self) -> None:
        without = {k: v for k, v in GOOD.items() if k != environment.MARKER}
        for label, environ in (
            ("missing", without),
            ("empty", {**GOOD, environment.MARKER: ""}),
            ("short", {**GOOD, environment.MARKER: MARKER_VALUE[:16]}),
            ("padded", {**GOOD, environment.MARKER: MARKER_VALUE + " "}),
        ):
            with self.subTest(label):
                with self.assertRaises(environment.RefusedConnection) as ctx:
                    self.import_settings({**environ, "PATH": "/x"})
                self.assertIn(environment.MARKER, str(ctx.exception))
                self.assertEqual(values_in(str(ctx.exception)), [])

    def test_settings_register_the_check_with_the_runs_comment(self) -> None:
        connection_created.disconnect(dispatch_uid=marker.DISPATCH_UID)
        with installed(None):
            self.import_settings({**GOOD, "PATH": "/x"})
            self.assertEqual(marker._expected, EXPECTED)
            # disconnect() reports whether a receiver was registered under the uid.
            self.assertTrue(connection_created.disconnect(dispatch_uid=marker.DISPATCH_UID))

    def test_the_check_is_registered_by_the_settings_not_by_main(self) -> None:
        from pathlib import Path

        package = Path(marker.__file__).parent
        self.assertIn("marker.install(", (package / "settings.py").read_text(encoding="utf-8"))
        self.assertNotIn("marker", (package / "__main__.py").read_text(encoding="utf-8"))


class ConnectionCheckTests(unittest.TestCase):
    def check(self, row: tuple[Any, ...] | None) -> tuple[FakeDjangoConnection, Exception | None]:
        connection = FakeDjangoConnection(row)
        error: Exception | None = None
        with installed(EXPECTED), redirect_stdout(io.StringIO()):
            try:
                marker.verify_new_connection(sender=object, connection=connection)
            except Exception as exc:  # noqa: BLE001 - the test inspects it
                error = exc
        return connection, error

    def test_the_query_reads_the_current_databases_comment(self) -> None:
        self.assertIn("shobj_description(d.oid, 'pg_database')", marker.QUERY)
        self.assertIn("d.datname = pg_catalog.current_database()", marker.QUERY)
        self.assertTrue(marker.QUERY.startswith("SELECT "))
        for word in ("UPDATE", "INSERT", "DELETE", "FOR UPDATE", "LOCK", "BEGIN", "SET "):
            self.assertNotIn(word, marker.QUERY.upper())

    def test_a_matching_comment_passes_with_one_statement(self) -> None:
        connection, error = self.check((97, EXPECTED))
        self.assertIsNone(error)
        self.assertEqual(connection.closed, 0)
        self.assertEqual(connection.cursor_.executed, [marker.QUERY])

    def test_every_other_comment_refuses_closes_and_names_only_the_variable(self) -> None:
        other = secrets.token_hex(16)
        while other == MARKER_VALUE:
            other = secrets.token_hex(16)
        rows: dict[str, tuple[Any, ...] | None] = {
            "a different marker": (97, environment.MARKER_COMMENT_PREFIX + other),
            "the bare prefix": (97, environment.MARKER_COMMENT_PREFIX),
            "the marker alone": (97, MARKER_VALUE),
            "something before": (97, " " + EXPECTED),
            "a prefix before": (97, "x" + EXPECTED),
            "something after": (97, EXPECTED + " "),
            "a newline after": (97, EXPECTED + "\n"),
            "a character after": (97, EXPECTED + "0"),
            "upper case": (97, EXPECTED.upper()),
            "an empty comment": (97, ""),
            "a null comment": (97, None),
            "no row": None,
        }
        for label, row in rows.items():
            with self.subTest(label):
                connection, error = self.check(row)
                self.assertIsInstance(error, marker.RefusedDatabase)
                self.assertEqual(connection.closed, 1)
                self.assertEqual(connection.cursor_.executed, [marker.QUERY])
                message = str(error)
                self.assertIn(marker.REFUSAL, message)
                self.assertIn(environment.MARKER, message)
                self.assertEqual(values_in(message), [])
                self.assertNotIn(other, message)

    def test_no_installed_marker_refuses_without_a_statement(self) -> None:
        connection = FakeDjangoConnection((97, EXPECTED))
        with installed(None), self.assertRaises(marker.RefusedDatabase):
            marker.verify_new_connection(sender=object, connection=connection)
        self.assertEqual(connection.closed, 1)
        self.assertEqual(connection.cursor_.executed, [])

    def test_a_failing_query_closes_the_connection_and_propagates(self) -> None:
        class Boom(Exception):
            pass

        class FailingCursor(FakeCursor):
            def execute(self, sql: str, params: object = None) -> None:
                raise Boom("server gone")

        connection = FakeDjangoConnection(None)
        connection.cursor_ = FailingCursor(None)
        with installed(EXPECTED), self.assertRaises(Boom):
            marker.verify_new_connection(sender=object, connection=connection)
        self.assertEqual(connection.closed, 1)

    def test_the_refusal_is_not_a_database_error(self) -> None:
        # makemigrations turns an OperationalError into a warning; this must not be one.
        self.assertFalse(issubclass(marker.RefusedDatabase, DatabaseError))


if __name__ == "__main__":
    unittest.main()
