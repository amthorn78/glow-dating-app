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


ACCOUNT = "glow_persistence_appaccount"
# Correction B-C2's item 4 (the exact-head review of Stage B, #4; DM-75): texts of the review's
# kinds (a literal, a dollar-quoted string, an ``E''`` string, a quoted alias, a nested comment, a
# ``U&`` identifier and a ``DO`` block with dynamic SQL), with DM-75 section 2's forms. Each passed
# 470d97a's rule though PostgreSQL takes ``FOR UPDATE`` on account rows (the evidence record's
# table, "Stage B, correction B-C2"); each is refused now, and passes with ``FOR NO KEY UPDATE``.
MASKED_FORMS = (
    f"SELECT id, '--' FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f"SELECT id, '/*' FROM {ACCOUNT} WHERE id = %s FOR UPDATE /* a comment */",
    f"SELECT id, 'it''s -- a note' FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f"SELECT id, $$--$$ FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f"SELECT id, $tag$--$tag$ FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f"SELECT id, E'\\'--' FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f"SELECT id, U&'--' FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f'SELECT id AS "--" FROM {ACCOUNT} WHERE id = %s FOR UPDATE',
    f"SELECT id FROM {ACCOUNT} WHERE id = %s /* a /* nested */ comment -- */ FOR UPDATE",
    'SELECT id FROM U&"glow\\005fpersistence\\005fappaccount" WHERE id = %s FOR UPDATE',
)
# Statements that fail by rule, whatever their lock: a ``DO`` statement (its body runs as code;
# the plain one was refused at 470d97a too, the dynamic one passed) and an unterminated span.
BY_RULE = (
    "DO $$BEGIN EXECUTE 'SELECT id FROM glow_persistence_' || 'appaccount LIMIT 1 FOR UPDATE';"
    " END$$",
    f"DO $$BEGIN PERFORM id FROM {ACCOUNT} LIMIT 1 FOR UPDATE; END$$",
    "do $body$ BEGIN PERFORM 1; END $body$",
    "SELECT 1; DO $$BEGIN PERFORM 1; END$$",
    f"SELECT id, '-- FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f'SELECT id AS "-- FROM {ACCOUNT} WHERE id = %s FOR UPDATE',
    f"SELECT id FROM {ACCOUNT} WHERE id = %s /* a /* b */ -- FOR UPDATE",
    f"SELECT id, E'\\' -- FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    f"SELECT id, $q$ -- FROM {ACCOUNT} WHERE id = %s FOR UPDATE",
    'SELECT id FROM U&"unterminated',
)
# Correction B-C2's item 5 (the exact-head review of Stage B, #5; DM-75): one planted example of
# each form an ``OF`` name or the account table may not take, and the review's scope example.
SCOPE_FORMS = (
    # The review's scope example: a comma item whose alias an EXISTS sub-query binds again.
    f"SELECT x.id FROM glow_persistence_match m, {ACCOUNT} x WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match x WHERE x.id = m.id) FOR UPDATE OF x",
    # A name bound twice.
    f"SELECT x.id FROM {ACCOUNT} a JOIN glow_persistence_match x ON x.account_low_id = a.id"
    " WHERE EXISTS (SELECT 1 FROM glow_persistence_block x) FOR UPDATE OF x",
    # A sub-query's alias bound twice.
    f"SELECT s.id FROM (SELECT id FROM {ACCOUNT}) s JOIN glow_persistence_match m"
    " ON m.account_low_id = s.id WHERE EXISTS (SELECT 1 FROM glow_persistence_match s)"
    " FOR UPDATE OF s",
    # A comma item.
    f"SELECT m.id FROM glow_persistence_match m, {ACCOUNT} a WHERE a.id = m.account_low_id"
    " FOR UPDATE OF m",
    # A comma item as the OF target, the first of its list, the account table only a column's
    # qualifier (only the comma rule refuses it).
    f"SELECT m.id FROM glow_persistence_match m, glow_persistence_block b WHERE {ACCOUNT}.id"
    " = m.account_low_id FOR UPDATE OF m",
    # A schema-qualified name: the account table, and the OF target.
    f"SELECT x.id FROM public.{ACCOUNT} x WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match x) FOR UPDATE OF x",
    f"SELECT m.id FROM public.glow_persistence_match m JOIN {ACCOUNT} a"
    " ON a.id = m.account_low_id FOR UPDATE OF m",
    # ONLY: the account table, and the OF target.
    f"SELECT x.id FROM ONLY ({ACCOUNT}) x WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match x) FOR UPDATE OF x",
    f"SELECT m.id FROM ONLY glow_persistence_match m JOIN {ACCOUNT} a"
    " ON a.id = m.account_low_id FOR UPDATE OF m",
    # *: the account table, and the OF target.
    f"SELECT x.id FROM {ACCOUNT} * x WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match x) FOR UPDATE OF x",
    f"SELECT m.id FROM glow_persistence_match * m JOIN {ACCOUNT} a"
    " ON a.id = m.account_low_id FOR UPDATE OF m",
    # A sub-query's alias.
    f"SELECT s.id FROM (SELECT id FROM {ACCOUNT}) s FOR UPDATE OF s",
    # A function's alias, alone and bound again in a sub-query.
    f"SELECT f.n FROM {ACCOUNT} a JOIN generate_series(1, 2) f(n) ON f.n = 1 FOR UPDATE OF f",
    f"SELECT f.n FROM {ACCOUNT} a JOIN generate_series(1, 2) f ON true WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match f) FOR UPDATE OF f",
    # The account table inside a sub-query.
    f"SELECT m.id FROM glow_persistence_match m WHERE m.account_low_id IN"
    f" (SELECT a.id FROM {ACCOUNT} a) FOR UPDATE OF m",
    # A WITH query's name bound to a plain item's alias too.
    f"WITH acc AS (SELECT 1) SELECT m.id FROM glow_persistence_match m JOIN {ACCOUNT} a"
    " ON a.id = m.account_low_id JOIN glow_persistence_block acc ON true FOR UPDATE OF acc",
)


class PostgresReadingTests(unittest.TestCase):
    """Correction B-C2's item 4: the rule reads a statement as PostgreSQL does. Every comment and
    every string constant is masked before it judges; a quoted identifier stays a name; an
    unterminated span and a ``DO`` statement fail, and a ``U&`` quoted identifier fails with
    ``FOR UPDATE``."""

    def refused(self, statement: str) -> str | None:
        return row_locks.refusal(statement, TABLES)

    def test_each_masked_form_is_refused_and_passes_with_no_key(self) -> None:
        for statement in MASKED_FORMS:
            with self.subTest(statement=statement):
                self.assertIsNotNone(self.refused(statement))
                self.assertIsNone(
                    self.refused(statement.replace("FOR UPDATE", "FOR NO KEY UPDATE"))
                )

    def test_a_do_statement_and_an_unterminated_span_fail_whatever_their_lock(self) -> None:
        for statement in BY_RULE:
            with self.subTest(statement=statement):
                self.assertIsNotNone(self.refused(statement))
                self.assertIsNotNone(
                    self.refused(statement.replace("FOR UPDATE", "FOR NO KEY UPDATE"))
                )
        self.assertEqual(self.refused(BY_RULE[0]), row_locks.DO_STATEMENT)
        self.assertEqual(self.refused(BY_RULE[-1]), row_locks.UNTERMINATED)

    def test_a_quoted_identifier_stays_a_name(self) -> None:
        self.assertIsNotNone(
            self.refused(f'SELECT "id" FROM "{ACCOUNT}" WHERE "id" = %s FOR UPDATE')
        )
        # Comment markers inside a quoted identifier are not comments.
        self.assertIsNotNone(
            self.refused(f'SELECT "a--b", "c/*d" FROM "{ACCOUNT}" WHERE "id" = %s FOR UPDATE')
        )
        # A doubled quote inside one does not end it.
        self.assertIsNotNone(
            self.refused(f'SELECT "x"" -- y" FROM "{ACCOUNT}" WHERE "id" = %s FOR UPDATE')
        )

    def test_what_a_constant_or_a_comment_holds_is_not_read(self) -> None:
        for statement in (
            # The account table named only in a constant or a comment.
            f"SELECT id, '{ACCOUNT}' FROM glow_persistence_match FOR UPDATE",
            f"SELECT id, $${ACCOUNT}$$ FROM glow_persistence_match FOR UPDATE",
            f"SELECT id FROM glow_persistence_match /* {ACCOUNT} */ FOR UPDATE",
            f"SELECT id FROM glow_persistence_match -- {ACCOUNT}\n FOR UPDATE",
            # A lock named only in a constant.
            f"SELECT id, 'FOR UPDATE' FROM {ACCOUNT} WHERE id = %s FOR NO KEY UPDATE",
            f"SELECT id, E'\\' FOR UPDATE' FROM {ACCOUNT} WHERE id = %s",
            # ON CONFLICT DO is not a DO statement.
            f"INSERT INTO {ACCOUNT} (id) VALUES (%s) ON CONFLICT DO NOTHING",
            # A plain backslash in a standard string ends nothing.
            "SELECT id FROM glow_persistence_match WHERE id LIKE 'pg\\_%' FOR UPDATE",
        ):
            with self.subTest(statement=statement):
                self.assertIsNone(self.refused(statement))

    def test_a_u_and_identifier_fails_only_with_for_update(self) -> None:
        name = 'U&"glow\\005fpersistence\\005fmatch"'
        self.assertEqual(
            self.refused(f"SELECT id FROM {name} FOR UPDATE OF {name}"), row_locks.U_AND_NAME
        )
        self.assertIsNone(self.refused(f"SELECT id FROM {name} FOR NO KEY UPDATE"))
        self.assertIsNone(self.refused(f"SELECT id FROM {name}"))

    def test_the_fast_path_and_the_full_reading_agree(self) -> None:
        # A statement with no constant, comment or dollar sign is judged without being read; the
        # same statement with an empty comment added is read in full, and its verdict is the same.
        statements = [
            ORM_ACCOUNT.format(lock=lock)
            for lock in ("FOR UPDATE", "FOR NO KEY UPDATE", "FOR SHARE", "", "For Update")
        ] + [
            JOINED.format(alias="T2 ", ref="T2", lock=lock)
            for lock in ('FOR UPDATE OF "glow_persistence_match"', "FOR UPDATE OF T2", "")
        ]
        # Correction B-C3's item 9 (B-C2's delta re-review, N7): a ``--`` comment between the
        # lock's words, which the fast path must not pass unread.
        statements.append(f"SELECT id FROM {ACCOUNT} WHERE id = %s FOR -- c\nUPDATE")
        for statement in statements:
            with self.subTest(statement=statement):
                fast = row_locks.judge(statement, TABLES)
                full = row_locks.judge(statement + " /* */", TABLES)
                self.assertEqual(
                    (fast.reason is None, fast.writer, fast.for_update),
                    (full.reason is None, full.writer, full.for_update),
                )


class ResolutionTests(unittest.TestCase):
    """Correction B-C2's item 5: an ``OF`` name counts only where the statement binds it once, in
    any scope, as a plain ``FROM`` or ``JOIN`` item's table or alias, and the account table
    appears only as such an item's table or a column's qualifier; any other form fails."""

    def refused(self, statement: str) -> str | None:
        return row_locks.refusal(statement, TABLES)

    def test_each_form_and_the_reviews_scope_example_are_refused(self) -> None:
        for statement in SCOPE_FORMS:
            with self.subTest(statement=statement):
                self.assertIsNotNone(self.refused(statement))
                self.assertIsNone(
                    self.refused(statement.replace("FOR UPDATE", "FOR NO KEY UPDATE"))
                )

    def test_a_qualifier_and_a_reference_in_a_lock_clause_are_read_as_references(self) -> None:
        for statement in (
            # The account table plainly joined, its alias a qualifier in a sub-query.
            f"SELECT m.id FROM glow_persistence_match m JOIN {ACCOUNT} a"
            " ON a.id = m.account_low_id WHERE EXISTS (SELECT 1 FROM glow_persistence_block b"
            " WHERE b.blocker_id = a.id) FOR UPDATE OF m",
            # The account table's own name as a qualifier, and in another clause's OF list.
            f'SELECT "glow_persistence_match"."id" FROM "glow_persistence_match" INNER JOIN'
            f' "{ACCOUNT}" ON ("glow_persistence_match"."account_low_id" = "{ACCOUNT}"."id")'
            f' FOR UPDATE OF "glow_persistence_match" FOR SHARE OF "{ACCOUNT}"',
        ):
            with self.subTest(statement=statement):
                self.assertIsNone(self.refused(statement))


LONG = "a" * 63
# Forms an independent read of B-C2's rule found passing before they were closed: each is one of
# the forms items 4 and 5 name, read as PostgreSQL reads it (PostgreSQL 17's scanner and grammar).
LEXICAL_FORMS = (
    # Only ASCII spaces, tabs, line ends, form feeds and vertical tabs are whitespace; any other
    # character, and a dollar sign after it, continues an identifier (no dollar quote begins).
    f"SELECT 1 AS  $a$ FROM {ACCOUNT} FOR UPDATE --$a$",
    f"SELECT 1 AS  $$ FROM {ACCOUNT} FOR UPDATE --$$",
    f"SELECT 1 AS \u0085$q$ FROM {ACCOUNT} FOR UPDATE --$q$",
    f"SELECT 1 AS 　$q$ FROM {ACCOUNT} FOR UPDATE --$q$",
    f'SELECT "{ACCOUNT}"."id" AS  $x$ FROM "{ACCOUNT}" FOR UPDATE --$x$',
    # An E'' constant continued across a newline keeps its backslash escapes.
    f"SELECT 1 FROM {ACCOUNT} WHERE '' = E''\n'\\', ' FOR UPDATE --'",
    f"SELECT 1 FROM {ACCOUNT} WHERE '' = E''\r'\\', ' FOR UPDATE --'",
    f"SELECT 1 FROM {ACCOUNT} WHERE '' = E'' -- c\n'\\', ' FOR UPDATE --'",
    f"SELECT 1 FROM {ACCOUNT} WHERE email IN (E'x'\n'\\', ') FOR UPDATE --'",
)
BINDING_FORMS = (
    # An unreserved keyword is a bare alias, so the name is bound twice.
    f"SELECT 1 FROM {ACCOUNT} set WHERE EXISTS (SELECT 1 FROM glow_persistence_match AS set)"
    " FOR UPDATE OF set",
    f"SELECT 1 FROM {ACCOUNT} update WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match AS update) FOR UPDATE OF update",
    f"SELECT 1 FROM {ACCOUNT} values WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match AS values) FOR UPDATE OF values",
    f"SELECT 1 FROM {ACCOUNT} between WHERE EXISTS"
    " (SELECT 1 FROM glow_persistence_match AS between) FOR UPDATE OF between",
    f"SELECT 1 FROM glow_persistence_match AS set; SELECT 1 FROM {ACCOUNT} set FOR UPDATE OF set",
    # IS DISTINCT FROM is no FROM list: it binds nothing and leaves the real list's comma read.
    f"SELECT NULL IS DISTINCT FROM glow_persistence_match AS set FROM {ACCOUNT} set"
    " JOIN glow_persistence_match ON true FOR UPDATE OF set",
    f"SELECT 1 FROM {ACCOUNT} a JOIN glow_persistence_match m ON a.id IS DISTINCT FROM m.id,"
    " glow_persistence_block b FOR UPDATE OF m",
    # Names are truncated to 63 bytes, so these two aliases are one name.
    f"SELECT 1 FROM {ACCOUNT} AS {LONG}1 WHERE EXISTS"
    f" (SELECT 1 FROM glow_persistence_match AS {LONG}2) FOR UPDATE OF {LONG}2",
    f"SELECT 1 FROM {ACCOUNT} AS {LONG} WHERE EXISTS"
    f" (SELECT 1 FROM glow_persistence_match AS {LONG}x) FOR UPDATE OF {LONG}x",
)


class PostgresLexicalEdgeTests(unittest.TestCase):
    """Correction B-C2's items 4 and 5, at PostgreSQL's lexical and naming edges: its whitespace,
    a continued string constant's kind, unreserved keywords as aliases, a FROM that opens no list,
    names truncated to 63 bytes, and an alias hiding its table's name."""

    def refused(self, statement: str) -> str | None:
        return row_locks.refusal(statement, TABLES)

    def test_each_form_is_refused_and_passes_with_no_key(self) -> None:
        for statement in LEXICAL_FORMS + BINDING_FORMS:
            with self.subTest(statement=statement):
                self.assertIsNotNone(self.refused(statement))
                self.assertIsNone(
                    self.refused(statement.replace("FOR UPDATE", "FOR NO KEY UPDATE"))
                )

    def test_a_hidden_do_statement_is_found(self) -> None:
        statement = (
            f"SELECT 1 AS  $a$; DO $$BEGIN PERFORM 1 FROM {ACCOUNT} FOR UPDATE; END$$; --$a$"
        )
        self.assertEqual(self.refused(statement), row_locks.DO_STATEMENT)

    def test_an_alias_hides_its_tables_name_and_a_functions_from_opens_no_list(self) -> None:
        for statement in (
            # Django's FOR UPDATE OF self on a table joined to itself under an alias.
            'SELECT "glow_persistence_block"."id" FROM "glow_persistence_block" INNER JOIN'
            f' "{ACCOUNT}" ON ("glow_persistence_block"."actor_id" = "{ACCOUNT}"."id") INNER JOIN'
            f' "glow_persistence_block" T3 ON ("{ACCOUNT}"."id" = T3."target_id") WHERE'
            ' T3."state" = %s ORDER BY "glow_persistence_block"."id" ASC LIMIT 1'
            ' FOR UPDATE OF "glow_persistence_block"',
            f"SELECT m.id FROM glow_persistence_match m JOIN {ACCOUNT} a ON a.id = m.account_low_id"
            " WHERE EXTRACT(YEAR FROM a.created_at) = %s FOR UPDATE OF m",
            # A plain constant continued across a newline is still masked whole.
            f"SELECT 'a'\n'FOR UPDATE' FROM {ACCOUNT} WHERE id = %s FOR NO KEY UPDATE",
        ):
            with self.subTest(statement=statement):
                self.assertIsNone(self.refused(statement))
        # The aliased table's own name binds nothing.
        self.assertIsNotNone(
            self.refused(
                f"SELECT 1 FROM glow_persistence_match m JOIN {ACCOUNT} a ON true"
                " FOR UPDATE OF glow_persistence_match"
            )
        )


# Correction B-C3's item 3 (B-C2's delta re-review, S1; DM-77): a function's or a procedure's body,
# a string constant, runs as code, so a statement that creates one fails whatever its lock. Each
# passed 4860b56's rule (its body masked); each is refused now, with FOR NO KEY UPDATE too.
ROUTINE_BODIES = (
    # The review's planted form.
    "CREATE FUNCTION pg_temp.f() RETURNS SETOF bigint LANGUAGE sql AS"
    f" $$ SELECT id FROM {ACCOUNT} FOR UPDATE $$",
    f"CREATE FUNCTION pg_temp.f() RETURNS SETOF bigint LANGUAGE sql AS 'SELECT id FROM {ACCOUNT}"
    " FOR UPDATE'",
    f"CREATE FUNCTION pg_temp.f() RETURNS SETOF bigint LANGUAGE sql AS E'SELECT id FROM {ACCOUNT}"
    " FOR UPDATE'",
    "CREATE OR REPLACE PROCEDURE pg_temp.p() LANGUAGE sql AS"
    f" $body$ SELECT id FROM {ACCOUNT} FOR UPDATE $body$",
    "create /* a comment */ or\nreplace function pg_temp.f() returns setof bigint language sql"
    f" as $$ SELECT id FROM {ACCOUNT} FOR UPDATE $$",
    # Codex on b67d9e3 (P2, "Reject executable routine definitions before masking their bodies").
    "CREATE FUNCTION public.d14_lock() RETURNS void LANGUAGE plpgsql AS"
    f" $$ BEGIN PERFORM id FROM {ACCOUNT} FOR UPDATE; END $$",
)
# Codex's sequence on b67d9e3: the creation fails; the call and the drop are judged as they are.
CODEX_SEQUENCE = (
    ROUTINE_BODIES[-1],
    "SELECT public.d14_lock()",
    "DROP FUNCTION public.d14_lock()",
)
# Correction B-C3's item 5 (B-C2's delta re-review, F5; DM-77): an OF name bound again inside a
# parenthesised join, or in a DELETE or MERGE statement's USING list. Each passed 4860b56's rule
# (the binding unread); each is refused now, as bound twice.
UNREAD_BINDINGS = (
    # The review's two planted texts.
    f"SELECT 1 FROM {ACCOUNT} a JOIN (glow_persistence_block x JOIN glow_persistence_block y"
    " ON true) j ON true JOIN glow_persistence_match x ON true FOR UPDATE OF x",
    "WITH q AS (DELETE FROM glow_persistence_block z USING glow_persistence_block x WHERE"
    f" z.id = x.id RETURNING z.id) SELECT 1 FROM {ACCOUNT} a JOIN glow_persistence_match x"
    " ON true FOR UPDATE OF x",
    # A MERGE statement's USING list.
    "WITH q AS (MERGE INTO glow_persistence_block z USING glow_persistence_block x ON"
    " z.id = x.id WHEN MATCHED THEN DO NOTHING RETURNING z.id) SELECT 1 FROM"
    f" {ACCOUNT} a JOIN glow_persistence_match x ON true FOR UPDATE OF x",
    # A later item of a USING list, and a JOIN item in one.
    "WITH q AS (DELETE FROM glow_persistence_block z USING glow_persistence_block w,"
    f" glow_persistence_block x RETURNING z.id) SELECT 1 FROM {ACCOUNT} a JOIN"
    " glow_persistence_match x ON true FOR UPDATE OF x",
    "WITH q AS (DELETE FROM glow_persistence_block z USING glow_persistence_block w JOIN"
    f" glow_persistence_block x ON true RETURNING z.id) SELECT 1 FROM {ACCOUNT} a JOIN"
    " glow_persistence_match x ON true FOR UPDATE OF x",
    # Nested parenthesised joins, and one whose first item is a sub-query.
    f"SELECT 1 FROM {ACCOUNT} a JOIN ((glow_persistence_block w JOIN glow_persistence_block x"
    " ON true) JOIN glow_persistence_block y ON true) ON true JOIN glow_persistence_match x"
    " ON true FOR UPDATE OF x",
    f"SELECT 1 FROM {ACCOUNT} a JOIN ((SELECT 1) s JOIN glow_persistence_block x ON true)"
    " ON true JOIN glow_persistence_match x ON true FOR UPDATE OF x",
    # The OF target itself inside a parenthesised join: not plain.
    f"SELECT 1 FROM ({ACCOUNT} a JOIN glow_persistence_match m ON true) FOR UPDATE OF m",
)
# Correction B-C3's item 6 (B-C2's delta re-review, S2; DM-77): psycopg writes a value where the
# placeholder stands, and a number, true, false or NULL can complete a dollar-quote tag.
GLUED = (
    # The review's text, and the placeholder inside the tag.
    f"SELECT id, $q%s$ $q1$ FROM {ACCOUNT} FOR UPDATE --$q1$",
    f"SELECT id, $q%sx$ $q1x$ FROM {ACCOUNT} FOR UPDATE --$q1x$",
    # A placeholder glued to a name character on either side, of each kind, the word UPDATE
    # anywhere (a comment included), with no span at all.
    "UPDATE glow_persistence_match SET version = version%s",
    "UPDATE glow_persistence_match SET version = %bversion",
    "SELECT 1 FROM glow_persistence_match WHERE id = x%t -- update",
    "SELECT 1 FROM glow_persistence_match WHERE id = x%(name)s /* UPDATE */",
    "SELECT 1 FROM glow_persistence_match WHERE id = é%s FOR UPDATE",
)


class FunctionBodyTests(unittest.TestCase):
    """Correction B-C3's item 3: a statement that creates a function or a procedure fails
    whatever its lock, as a ``DO`` statement does."""

    def refused(self, statement: str) -> str | None:
        return row_locks.refusal(statement, TABLES)

    def test_each_routine_body_is_refused_with_either_lock(self) -> None:
        for statement in ROUTINE_BODIES:
            with self.subTest(statement=statement):
                self.assertEqual(self.refused(statement), row_locks.CREATES_ROUTINE)
                self.assertEqual(
                    self.refused(statement.replace("FOR UPDATE", "FOR NO KEY UPDATE")),
                    row_locks.CREATES_ROUTINE,
                )

    def test_a_routine_with_no_constant_is_refused_and_not_passed_unread(self) -> None:
        # A SQL-standard body is no string constant: the fast path must still read it.
        statement = (
            "CREATE FUNCTION pg_temp.f() RETURNS SETOF bigint LANGUAGE sql BEGIN ATOMIC"
            f" SELECT id FROM {ACCOUNT} FOR SHARE; END"
        )
        self.assertEqual(self.refused(statement), row_locks.CREATES_ROUTINE)

    def test_codexs_sequence_the_creation_fails_the_call_and_drop_are_judged(self) -> None:
        verdicts = [self.refused(statement) for statement in CODEX_SEQUENCE]
        self.assertEqual(verdicts, [row_locks.CREATES_ROUTINE, None, None])

    def test_the_words_are_read_as_postgresql_reads_them(self) -> None:
        for statement in (
            "SELECT 'CREATE FUNCTION f() RETURNS int' FROM glow_persistence_match",
            "SELECT 1 /* CREATE FUNCTION */ FROM glow_persistence_match",
            'SELECT "create", "function" FROM glow_persistence_match',
            "CREATE TABLE glow_scratch (procedure int)",
        ):
            with self.subTest(statement=statement):
                self.assertIsNone(self.refused(statement))


class OwnObjectsFilterTests(unittest.TestCase):
    """Correction B-C3's item 3 (F3): ``OWN_OBJECTS`` excludes only ``pg_catalog``,
    ``information_schema``, the TOAST schemas and extensions, so a temporary schema's functions,
    procedures, views and rules count."""

    def test_each_count_excludes_only_the_system_and_toast_schemas(self) -> None:
        query = row_locks.OWN_OBJECTS
        self.assertEqual(query.count("SELECT count(*)"), 3)
        self.assertEqual(
            query.count("n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')"), 3
        )
        self.assertEqual(query.count("n.nspname NOT LIKE 'pg\\_toast\\_temp\\_%'"), 3)
        self.assertEqual(query.count("nspname"), 6)
        self.assertNotIn("'pg\\_%'", query)
        # The functions' count leaves out an extension's own.
        self.assertEqual(query.count("d.deptype = 'e'"), 1)


class UnreadBindingTests(unittest.TestCase):
    """Correction B-C3's item 5: an item inside a parenthesised join, and an item of a ``DELETE``
    or ``MERGE`` statement's ``USING`` list, are read as bindings, none of them plain; a join's
    ``USING (…)`` column list binds nothing."""

    def refused(self, statement: str) -> str | None:
        return row_locks.refusal(statement, TABLES)

    def test_each_binding_is_read_and_the_name_bound_twice_or_not_plain_fails(self) -> None:
        for statement in UNREAD_BINDINGS:
            with self.subTest(statement=statement):
                self.assertIsNotNone(self.refused(statement))
                self.assertIsNone(
                    self.refused(statement.replace("FOR UPDATE", "FOR NO KEY UPDATE"))
                )

    def test_a_joins_using_column_list_binds_nothing(self) -> None:
        statement = (
            "SELECT m.id FROM glow_persistence_match m JOIN glow_persistence_block b USING (id)"
            f" JOIN {ACCOUNT} a ON a.id = m.account_low_id FOR UPDATE OF {{of}}"
        )
        self.assertIsNone(self.refused(statement.format(of="m")))
        self.assertIsNotNone(self.refused(statement.format(of="a")))
        inside = (
            "WITH q AS (DELETE FROM glow_persistence_block z USING glow_persistence_block w JOIN"
            " glow_persistence_block v USING (id) RETURNING z.id) SELECT 1 FROM"
            f" {ACCOUNT} a JOIN glow_persistence_match x ON true FOR UPDATE OF x"
        )
        self.assertIsNone(self.refused(inside))


class GluedPlaceholderTests(unittest.TestCase):
    """Correction B-C3's item 6: a statement whose text holds the word ``UPDATE`` anywhere and a
    placeholder glued to a name character or a dollar sign fails, whatever D14 reads in it."""

    def refused(self, statement: str) -> str | None:
        return row_locks.refusal(statement, TABLES)

    def test_each_glued_placeholder_fails_with_either_lock(self) -> None:
        for statement in GLUED:
            with self.subTest(statement=statement):
                self.assertEqual(self.refused(statement), row_locks.GLUED_PLACEHOLDER)
                self.assertEqual(
                    self.refused(statement.replace("FOR UPDATE", "FOR NO KEY UPDATE")),
                    row_locks.GLUED_PLACEHOLDER,
                )

    def test_a_placeholder_apart_from_names_a_literal_percent_or_no_update_passes(self) -> None:
        for statement in (
            f"SELECT id FROM {ACCOUNT} WHERE id = %s FOR NO KEY UPDATE",
            "UPDATE glow_persistence_match SET decided_at = %(name)s::timestamptz WHERE id = %s",
            ORM_ACCOUNT.format(lock="FOR NO KEY UPDATE"),
            "UPDATE glow_persistence_match SET version = (version + %s) WHERE id IN (%s, %s)",
            # ``%%`` is a literal percent sign, not a placeholder.
            "UPDATE glow_persistence_match SET note = 'a%%sb' WHERE id = %s",
            # No word UPDATE: a placeholder glued to a name does not matter.
            "SELECT x%s FROM glow_persistence_match FOR SHARE",
            # UPDATE only as part of a longer word.
            "SELECT 1 FROM glow_persistence_match WHERE updated_at = x%s",
        ):
            with self.subTest(statement=statement):
                self.assertIsNone(self.refused(statement))


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
