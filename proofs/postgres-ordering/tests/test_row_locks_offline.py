"""D14's record of the row locks the suites send, offline (SV3 Stage B; acceptance check 15).

No database: the rule (``row_locks.refusal``) on the statements the app and the harness send and on
the forms it must refuse; the record's counting, its windows and its two sources; the driver's
record skipping what Django's execute already recorded; the install patching psycopg's cursor
classes and restoring them; and each of the four runners installing the record before its first
statement and printing its lines before its verdict. The cases run in the Database proof checks
job, where each suite's own check is the evidence.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from typing import Any

from psycopg import sql

from glow_ordering_proof import row_locks

PROOF = Path(__file__).resolve().parents[1] / "glow_ordering_proof"
TABLES = frozenset(
    {
        "glow_persistence_appaccount",
        "glow_persistence_match",
        "glow_persistence_accountsession",
        "glow_persistence_block",
    }
)
ACCOUNT_COLUMNS = (
    '"glow_persistence_appaccount"."id", "glow_persistence_appaccount"."state",'
    ' "glow_persistence_appaccount"."version"'
)
# What Django sends for ``AppAccount.objects.select_for_update(...).filter(pk=...).first()``.
ORM_ACCOUNT = (
    f'SELECT {ACCOUNT_COLUMNS} FROM "glow_persistence_appaccount" WHERE'
    ' "glow_persistence_appaccount"."id" = %s ORDER BY "glow_persistence_appaccount"."id" ASC'
    " LIMIT 1 {lock}"
)
JOINED = (
    'SELECT "glow_persistence_match"."id" FROM "glow_persistence_match" INNER JOIN'
    ' "glow_persistence_appaccount" {alias}ON ("glow_persistence_match"."account_low_id" ='
    ' {ref}."id") WHERE {ref}."state" = %s {lock}'
)


class RuleTests(unittest.TestCase):
    """The rule's words: a writer's row lock ``FOR UPDATE`` naming the account table fails unless
    every such clause is ``FOR UPDATE OF`` names none of which is that table or its alias; a lock
    clause it cannot read that way fails too."""

    def refused(self, statement: str) -> str | None:
        return row_locks.refusal(statement, TABLES)

    def test_an_account_lock_for_update_is_refused_and_no_key_passes(self) -> None:
        self.assertIsNotNone(self.refused(ORM_ACCOUNT.format(lock="FOR UPDATE")))
        self.assertIsNone(self.refused(ORM_ACCOUNT.format(lock="FOR NO KEY UPDATE")))

    def test_the_two_harness_locks_before_and_after_item_5(self) -> None:
        # DM-73: cases.py's ``_harness_holder`` and planted.py's ``_suspend``.
        before = "SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR UPDATE"
        after = "SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR NO KEY UPDATE"
        self.assertIsNotNone(self.refused(before))
        self.assertIsNone(self.refused(after))
        self.assertIsNotNone(self.refused(ORM_ACCOUNT.format(lock="FOR UPDATE")))

    def test_readers_and_other_tables_pass(self) -> None:
        for statement in (
            ORM_ACCOUNT.format(lock="FOR SHARE"),
            ORM_ACCOUNT.format(lock="FOR KEY SHARE"),
            ORM_ACCOUNT.format(lock=""),
            'SELECT "glow_persistence_match"."id" FROM "glow_persistence_match" WHERE'
            ' "glow_persistence_match"."id" = %s LIMIT 1 FOR UPDATE',
            # A column whose name begins with the table's name is not the table.
            'SELECT "x"."glow_persistence_appaccount_id" FROM "glow_persistence_block" "x"'
            " FOR UPDATE",
            "SELECT state FROM glow_persistence_appaccount WHERE id = %s FOR SHARE",
        ):
            with self.subTest(statement=statement):
                self.assertIsNone(self.refused(statement))

    def test_an_of_naming_only_other_tables_passes(self) -> None:
        for lock in (
            'FOR UPDATE OF "glow_persistence_match"',
            'FOR UPDATE OF "glow_persistence_match" NOWAIT',
            'FOR UPDATE OF "glow_persistence_match" SKIP LOCKED',
            "FOR UPDATE OF glow_persistence_match",
            'FOR UPDATE OF "glow_persistence_match" FOR SHARE OF "glow_persistence_appaccount"',
            'FOR UPDATE OF "glow_persistence_match" FOR KEY SHARE OF T2',
        ):
            with self.subTest(lock=lock):
                statement = JOINED.format(alias="T2 ", ref="T2", lock=lock)
                self.assertIsNone(self.refused(statement))
        aliased = (
            'SELECT m."id" FROM "glow_persistence_match" m JOIN "glow_persistence_appaccount" a'
            ' ON m."account_low_id" = a."id" FOR UPDATE OF m'
        )
        self.assertIsNone(self.refused(aliased))

    def test_an_of_naming_the_account_table_or_its_alias_is_refused(self) -> None:
        for alias, ref, lock in (
            ("", '"glow_persistence_appaccount"', 'FOR UPDATE OF "glow_persistence_appaccount"'),
            ("T2 ", "T2", "FOR UPDATE OF T2"),
            ("AS acc ", "acc", "FOR UPDATE OF acc"),
            ("T2 ", "T2", 'FOR UPDATE OF "glow_persistence_match", T2'),
            ("T2 ", "T2", 'FOR UPDATE OF "T2"'),
            ("", '"glow_persistence_appaccount"', "for update of glow_persistence_appaccount"),
        ):
            with self.subTest(lock=lock):
                self.assertIsNotNone(self.refused(JOINED.format(alias=alias, ref=ref, lock=lock)))

    def test_a_lock_clause_it_cannot_read_is_refused(self) -> None:
        for lock in (
            "FOR UPDATE",
            "for update",
            "FOR\n  UPDATE",
            "FOR /* a comment */ UPDATE",
            "FOR UPDATE -- a comment\n",
            'FOR UPDATE OF "glow_persistence_match" FOR UPDATE',
            'FOR UPDATE OF "glow_persistence_match" WAIT',
            'FOR UPDATE OF "glow_persistence_match", ',
            'FOR UPDATE OF public."glow_persistence_match"',
            "FOR UPDATE OF unknown_name",
            'FOR UPDATE OF "Glow_persistence_match"',
        ):
            with self.subTest(lock=lock):
                self.assertIsNotNone(self.refused(JOINED.format(alias="T2 ", ref="T2", lock=lock)))

    def test_a_sub_query_a_with_query_and_a_relation_outside_the_models_are_refused(self) -> None:
        for statement in (
            "SELECT sub.id FROM (SELECT id FROM glow_persistence_appaccount) sub FOR UPDATE OF sub",
            "WITH acc AS (SELECT id FROM glow_persistence_appaccount) SELECT m.id FROM"
            " glow_persistence_match m JOIN acc ON acc.id = m.account_low_id FOR UPDATE OF acc",
            "SELECT v.id FROM some_view v JOIN glow_persistence_appaccount a ON a.id = v.id"
            " FOR UPDATE OF v",
            "SELECT a.id FROM public.glow_persistence_appaccount a FOR UPDATE OF a",
            "SELECT m.id FROM glow_persistence_match m, glow_persistence_appaccount a"
            " WHERE a.id = m.account_low_id FOR UPDATE",
        ):
            with self.subTest(statement=statement):
                self.assertIsNotNone(self.refused(statement))

    def test_without_the_models_tables_an_of_is_read_by_the_statement_alone(self) -> None:
        statement = (
            "SELECT v.id FROM some_view v JOIN glow_persistence_appaccount a ON a.id = v.id"
            " FOR UPDATE OF v"
        )
        self.assertIsNone(row_locks.refusal(statement))
        self.assertIsNotNone(row_locks.refusal(statement, TABLES))

    def test_the_words_are_whole_words_and_case_is_ignored(self) -> None:
        self.assertIsNotNone(self.refused(ORM_ACCOUNT.format(lock="For Update").upper()))
        self.assertIsNone(self.refused(ORM_ACCOUNT.format(lock="FOR UPDATED_AT")))


class QueryTextTests(unittest.TestCase):
    def test_a_composed_statement_keeps_no_parameter(self) -> None:
        # What Django's psycopg 3 cursor class sends for ``callproc("planted", [<a value>])``.
        statement = sql.Composed(
            [sql.SQL("SELECT * FROM "), sql.Identifier("planted"), sql.SQL("("), sql.Literal(7)]
            + [sql.SQL(")")]
        )
        self.assertEqual(row_locks.query_text(statement), 'SELECT * FROM "planted"(%s)')
        self.assertEqual(row_locks.query_text(b"SELECT 1"), "SELECT 1")
        self.assertEqual(row_locks.query_text("SELECT 2"), "SELECT 2")
        self.assertEqual(row_locks.query_text(sql.Placeholder("x")), "%s")


class Connection:
    """A stand-in for one connection object; only its identity is read."""


class RecordTests(unittest.TestCase):
    def test_counts_and_refusals_are_kept_without_parameters(self) -> None:
        record = row_locks.RowLockRecord(TABLES)
        first = Connection()
        record.note(ORM_ACCOUNT.format(lock="FOR NO KEY UPDATE"), row_locks.DJANGO, first)
        record.note(ORM_ACCOUNT.format(lock="FOR UPDATE"), row_locks.DJANGO, first)
        record.note(ORM_ACCOUNT.format(lock="FOR UPDATE"), row_locks.DRIVER, first)
        record.note(
            JOINED.format(alias="T2 ", ref="T2", lock='FOR UPDATE OF "glow_persistence_match"'),
            row_locks.DJANGO,
            first,
        )
        record.note("SELECT 1", row_locks.DRIVER, Connection())
        summary = record.summary((0, 0, 0))
        self.assertEqual(summary.statements, 5)
        self.assertEqual((summary.through_django, summary.through_driver), (3, 2))
        self.assertEqual(summary.writer_locks, 4)
        self.assertEqual(summary.account_writer_locks, 4)
        self.assertEqual((summary.account_no_key, summary.account_update_of_others), (1, 1))
        self.assertEqual(summary.refused, 2)
        self.assertEqual(len(summary.refusals), 1)
        self.assertEqual(summary.refusals[0][2], 2)
        self.assertNotIn("%s'", summary.refusals[0][1])
        self.assertEqual(summary.failures(), 2)
        self.assertFalse(summary.passed())
        lines = summary.lines("discovery")
        self.assertTrue(lines[0].startswith("[discovery] row locks sent (D14): 5 statements"))
        self.assertIn("2 refused", lines[0])
        self.assertTrue(lines[1].startswith("[discovery] row lock refused (D14): "))
        self.assertEqual(lines[-1], "ROW LOCKS (D14): FAIL")

    def test_a_clean_record_passes_and_an_empty_or_unread_one_fails(self) -> None:
        record = row_locks.RowLockRecord(TABLES)
        self.assertFalse(record.summary((0, 0, 0)).passed())  # it saw nothing
        record.note(ORM_ACCOUNT.format(lock="FOR NO KEY UPDATE"), row_locks.DJANGO, Connection())
        self.assertTrue(record.summary((0, 0, 0)).passed())
        self.assertEqual(record.summary((0, 0, 0)).lines("x")[-1], "ROW LOCKS (D14): PASS")
        self.assertFalse(record.summary(None).passed())  # the database's objects unread
        for own in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            with self.subTest(own=own):
                self.assertEqual(record.summary(own).failures(), 1)

    def test_a_window_sees_every_thread_connection_and_source(self) -> None:
        record = row_locks.RowLockRecord(TABLES)
        mine = Connection()
        theirs = Connection()
        record.note("SELECT 0", row_locks.DJANGO, mine)
        with record.window() as seen:
            record.note("SELECT 1", row_locks.DJANGO, mine)
            other = threading.Thread(
                target=record.note, args=("UPDATE x SET y = y", row_locks.DJANGO, theirs)
            )
            other.start()
            other.join()
            record.note("SELECT 2", row_locks.DRIVER, mine)
        record.note("SELECT 3", row_locks.DJANGO, mine)
        self.assertEqual([s.text for s in seen], ["SELECT 1", "UPDATE x SET y = y", "SELECT 2"])
        self.assertEqual(seen[0].thread, threading.get_ident())
        self.assertNotEqual(seen[1].thread, threading.get_ident())
        self.assertEqual(seen[0].connection, id(mine))
        self.assertNotEqual(seen[1].connection, id(mine))
        self.assertEqual([s.source for s in seen], ["django", "django", "driver"])
        self.assertEqual(record.summary((0, 0, 0)).threads, 2)

    def test_the_driver_record_skips_what_djangos_execute_recorded(self) -> None:
        record = row_locks.RowLockRecord(TABLES)
        sent: list[str] = []

        def original(cursor: Any, query: Any, *args: Any, **kwargs: Any) -> str:
            sent.append(row_locks.query_text(query))
            return "done"

        driver = record._driver_method(original)
        cursor = type("C", (), {"connection": Connection()})()

        def execute(statement: str, params: Any, many: bool, context: Any) -> Any:
            return driver(cursor, statement, params)

        context = {"connection": Connection()}
        self.assertEqual(record.wrapper(execute, "SELECT 1", None, False, context), "done")
        self.assertEqual(driver(cursor, "SELECT 2"), "done")
        summary = record.summary((0, 0, 0))
        self.assertEqual((summary.through_django, summary.through_driver), (1, 1))
        self.assertEqual(sent, ["SELECT 1", "SELECT 2"])


INSTALL = """
import django
from django.conf import settings
settings.configure(
    DATABASES={"default": {"ENGINE": "django.db.backends.postgresql", "NAME": "unused"}},
    INSTALLED_APPS=[], USE_TZ=True,
)
django.setup()
import psycopg
from django.db import connection
from glow_ordering_proof import row_locks
names = ("execute", "executemany", "stream", "copy")
before = {name: psycopg.Cursor.__dict__[name] for name in names}
server = psycopg.ServerCursor.__dict__["execute"]
record = row_locks.install()
assert row_locks.active() is record
assert row_locks.install() is record
assert connection.execute_wrappers[0] == record.wrapper
for name, original in before.items():
    assert psycopg.Cursor.__dict__[name] is not original, name
assert psycopg.ServerCursor.__dict__["execute"] is not server
with connection.execute_wrapper(lambda *a: None):
    pass
assert connection.execute_wrappers == [record.wrapper]
record.uninstall()
for name, original in before.items():
    assert psycopg.Cursor.__dict__[name] is original, name
assert psycopg.ServerCursor.__dict__["execute"] is server
assert connection.execute_wrappers == []
print("installed and restored")
"""


class InstallTests(unittest.TestCase):
    def test_install_wraps_every_connection_and_psycopgs_cursors_and_restores_them(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", INSTALL],
            cwd=PROOF.parent,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8"},
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("installed and restored", result.stdout)


def _source(name: str) -> str:
    return (PROOF / name).read_text(encoding="utf-8")


class RunnerTests(unittest.TestCase):
    """Each of the four suites installs the record before its first statement and prints the
    check's lines, which fold into its result, before its verdict."""

    def test_the_three_django_suites_install_first_and_check_before_the_verdict(self) -> None:
        for name, first, verdict in (
            ("identity_suite.py", "used_database_reasons()", "IDENTITY VERDICT"),
            ("profile_suite.py", "used_database_reasons()", "PROFILE VERDICT"),
            ("discovery_suite.py", "used_database_reasons()", "DISCOVERY VERDICT"),
        ):
            with self.subTest(suite=name):
                text = _source(name)
                install = text.index("lock_record = row_locks.install()")
                self.assertLess(install, text.index(f"reasons = {first}"))
                self.assertLess(install, text.index("server_facts()"))
                check = text.index("summary = lock_record.check()")
                self.assertLess(check, text.index("body = report.to_json()"))
                lines = text.index("for line in summary.lines(")
                self.assertLess(lines, text.index(f'print(f"{verdict}: '))
                self.assertIn("and self.row_lock_failures == 0", text)

    def test_the_ordering_suite_installs_first_and_its_failure_is_a_problem(self) -> None:
        text = _source("__main__.py")
        tree = ast.parse(text)
        run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
        calls = [ast.unparse(n) for n in ast.walk(run) if isinstance(n, ast.Call)]
        self.assertIn("row_locks.install()", calls)
        self.assertLess(text.index("row_locks.install()"), text.index("server = server_facts()"))
        self.assertLess(
            text.index("print_row_locks(run_report)"), text.index("print(render_run(run_report))")
        )
        self.assertIn("run_report.problems.append(", text)


if __name__ == "__main__":
    unittest.main()
