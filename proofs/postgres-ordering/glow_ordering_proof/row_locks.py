"""D14's record of the row locks the suites send (the SV3 brief's D14 and acceptance check 15;
DM-68, DM-70, DM-71, DM-73; SV3 Stage B).

The lock scan (``account_lock_scan``) reads the source and cannot be complete, so each of the four
suites (the ordering suite's ``run``, ``identity``, ``profile`` and ``discovery``) also checks what
it sends. Before its first statement it installs one ``RowLockRecord``, which records the text of
every statement the process sends while the suite runs:

- **through Django** (``DJANGO``): an execute wrapper on every connection the process opens, the
  ones its concurrency cases open in other threads included (each new connection is given the
  wrapper as it connects, through Django's ``connection_created`` signal, and the connections
  already open are given it at install). It is the outermost wrapper, so it records every
  statement Django's ``execute`` and ``executemany`` send, as Django's ``execute`` receives them;
- **through the driver itself** (``DRIVER``; Stage B's item 2, DM-70 and DM-73): psycopg's own
  ``Cursor.execute``, ``executemany``, ``stream`` and ``copy``, and ``ServerCursor.execute``, are
  wrapped in the suite's process, and a statement they send outside Django's ``execute`` is
  recorded too. That is every statement sent through a method of the driver's cursor that Django's
  cursor passes through unwrapped (``stream``, ``copy``), through ``callproc`` (Django's cursor
  calls it without its execute wrappers, and Django's own psycopg 3 cursor class sends it as
  ``SELECT * FROM "name"(...)`` through the driver cursor's ``execute``), and through the driver's
  own connection (``connection.connection``: its ``cursor()`` and its ``execute``, which make a
  cursor of Django's cursor class, a subclass of psycopg's ``Cursor``), and through a connection
  opened with ``psycopg.connect``, whose cursors are psycopg's ``Cursor``. Nothing is refused:
  Django's own use of the driver's connection (creating cursors, the health check's
  ``SELECT 1``, configuring a new connection) is recorded and judged like any other statement.

**How it reads a statement** (``_read``; the exact-head review of Stage B, #4; DM-75; B-C2's delta
re-review, F4; DM-77): as PostgreSQL reads the text the record receives, before psycopg writes its
parameters into it, with ``standard_conforming_strings`` on. Every comment (``--`` to the line's
end, and ``/* … */``, nested block comments included) and every string constant (``'…'`` with
``''``, ``E'…'`` with backslash escapes, ``U&'…'``, and dollar-quoted strings, the tag empty or an
identifier) is masked before it judges; a quoted identifier (``"…"`` with ``""``) is kept as a
name, so Django's ``"glow_persistence_appaccount"`` is still the account table. An unterminated
span (a string constant, a quoted identifier or a block comment), a ``DO`` statement, a statement
that creates a function or a procedure (``CREATE [OR REPLACE] FUNCTION`` or ``PROCEDURE``; the last
two run a string as code) and a statement that creates a view (``CREATE [OR REPLACE] [TEMP |
TEMPORARY] [RECURSIVE] VIEW`` or ``CREATE MATERIALIZED VIEW``, with ``LOCAL``, ``GLOBAL`` and
``UNLOGGED`` read among those words too; a lock through a view reaches a table it does not name;
B-C3's delta re-review, F4; DM-78) fail whatever their lock, the words read as PostgreSQL reads
them; a statement holding a ``U&`` quoted identifier, whose escapes can spell any name, fails if it
takes ``FOR UPDATE``. Each placeholder is read as psycopg 3.3.6 reads one: ``%s``, ``%b`` or
``%t``, or ``%(name)s``, ``%(name)b`` or ``%(name)t`` with a name of one or more characters other
than ``)`` (a name holding ``(`` included; B-C3's delta re-review, F1; DM-78), the text scanned in
order, and ``%%`` a literal percent sign. Before anything else, two placeholder tests run: a
statement whose text holds the word ``UPDATE`` anywhere (spans and comments included) and a
placeholder whose neighbour on either side is a name character (a letter, digit, underscore, dollar
sign or non-ASCII character) fails, since the value psycopg writes there can complete a
dollar-quote tag (B-C2's delta re-review, S2; DM-77); and a statement with a placeholder any part
of which lies inside a string constant (dollar-quoted ones included), a quoted identifier or a
comment fails whatever its lock or text, since the quotes and text psycopg writes there can end
that span (B-C3's delta re-review, F5; DM-78). Only PostgreSQL's whitespace separates tokens: a
space, a tab, a line end, a form feed or a vertical tab. Every non-ASCII character, a non-ASCII
space included, is an identifier character, and a dollar sign after an identifier character
continues the identifier rather than opening a dollar quote. A string constant continued across a
line end keeps its kind (an ``E'…'`` constant's continuation still takes backslash escapes), and a
name is cut to 63 bytes, as PostgreSQL cuts it. Unquoted words are read without regard to case, and
the account table's name in any case counts as the account table. After the placeholder tests, a
statement with no single quote, comment, dollar sign or ampersand, every quoted identifier ended,
no ``DO``, no ``CREATE`` with ``FUNCTION``, ``PROCEDURE`` or ``VIEW``, and no writer's lock in its
text passes without being read further (``judge``'s fast path).

**The rule** (``refusal``): a statement fails if it takes a writer's row lock ``FOR UPDATE``, not
``FOR NO KEY UPDATE``, and names ``glow_persistence_appaccount``, unless each of its ``FOR UPDATE``
clauses is ``FOR UPDATE OF`` a list of names none of which is that table or an alias the statement
gives it. A lock clause it cannot read that way fails too: ``FOR UPDATE`` with no ``OF`` list it
can read; an ``OF`` name the resolution below does not bind once to a plain ``FROM`` or ``JOIN``
item, or binds to a table that is not one of the models' tables (a view); or text after the clause
that is not another lock clause. With the models' tables given (``RowLockRecord`` reads them from
Django's registry once it is ready), a statement that takes ``FOR UPDATE`` and does not name the
account table fails too unless every relation name its reading binds (``_relations``), in any
scope (each ``FROM``, ``JOIN``, ``USING``-list, ``INTO``, ``UPDATE`` and ``DELETE FROM`` item, a
``WITH`` query's name read as one included, but not an item after a ``set`` or ``values`` that
the reading takes as the end of the ``FROM`` list; the proof README's "Limits"), is one of those
tables, written without a schema; a ``TABLE`` command, or parentheses it cannot read, fail it as
well. So a ``FOR UPDATE`` through a name that is not one of the models' tables, in a position its
reading binds, fails, whatever else the statement names (Codex on ``4c2f918``; DM-78; B-C4's
delta re-review, F1; DM-79). A sub-query's and a function's own relations are read in turn; a
function is not a relation.

**How it resolves ``FOR UPDATE OF``** (``_resolve``; the exact-head review of Stage B, #5; DM-75):
an ``OF`` name counts only where the statement binds it once, in any scope, as a table named in a
plain ``FROM`` or ``JOIN`` item or that item's alias, and the account table appears only as such an
item's table or a column's qualifier (a name in a lock clause's ``OF`` list is read as a reference,
as a qualifier is). An item binds its alias where it has one (an unreserved keyword such as
``set`` can be one), and its table's name only where it has none, as PostgreSQL binds them; a
``FROM`` after ``IS DISTINCT`` or among a function's arguments (``EXTRACT(… FROM …)``) opens no
list. Any other form fails: a name bound twice; a comma item (every item of a
``FROM`` list that holds a comma); a schema-qualified name; ``ONLY``; ``*``; a sub-query's or a
function's alias; or the account table inside a sub-query. The other binding forms it reads (a
``WITH`` query's name, an ``UPDATE``, ``INTO`` or ``DELETE FROM`` target, a ``MERGE INTO``
target's alias with or without ``AS``, a column alias list, ``TABLESAMPLE``, an item inside a
parenthesised join, an item of a ``DELETE`` or ``MERGE`` statement's ``USING`` list, and a join's
``USING (…) AS`` alias; B-C2's delta re-review, F5; DM-77; B-C3's delta re-review, F2 and F3;
DM-78) count as bindings too, and none of them is plain. A join's ``USING (…)`` column list itself
binds nothing.

**The database's own objects:** a lock taken inside a database function, a view or a rule is not in
any statement's text, so a statement that creates a function or a procedure fails whatever its
lock (its body, a string constant, runs as code; DM-77), as does a statement that creates a view
(DM-78), and the check counts the functions,
procedures, views and rules that exist when it runs outside ``pg_catalog``,
``information_schema``, the TOAST schemas and extensions, temporary schemas included; the suite
fails unless each is zero (no migration defines one).

The check runs before the suite's verdict. It prints counts, and each failing statement's text with
its reason, never a parameter: Django sends parameters apart from the text, and a ``callproc``
argument is rendered as ``%s``.

**The windows** (Stage B's item 1, DM-69): ``window`` lets a case read every statement the record
saw while it ran, with its source, thread and connection, so ``pages.one_snapshot_statements``
checks that no statement went out on another connection, from another thread or through the
driver itself while a page ran.

**What it does not see** (the proof README's "Limits"): a statement a case's own execute wrapper
sends through the driver while Django's ``execute`` runs on that thread (the driver's record skips
that thread until ``execute`` returns), and it judges a statement such a wrapper rewrites on the
text before the rewrite (no case's wrapper sends or rewrites one today); a statement sent below
psycopg's cursors (libpq's own connection object, ``connection.connection.pgconn.exec_(...)``), or
through an asynchronous cursor; a statement read with ``standard_conforming_strings`` off (S3);
a parameter's value where its placeholder stands outside every span and is glued to no name
character or dollar sign, which psycopg writes as a constant, and a string constant after such a
placeholder, which a value holding a backslash can change (S4; the proof README's "Limits"); a
lock through a model table's name that refers to another relation when the lock runs (a view of
that name a path the record does not see created, the account table renamed to that name, or a
table of that name of which the account table was made a child), since it judges each statement
on its own text and follows no change to the schema; a statement sent before Django's registry
is ready, judged without the models' tables; the name ``excluded`` as a binding; and a statement
a case never runs.

**Its counts** of connections and threads are of distinct identities, which a closed connection's
or an ended thread's successor may reuse, and it counts a connection's Django wrapper and its
psycopg connection as two. Neither count bounds the other: a thread that opens connections in turn
adds an identity for each (DM-77).
"""

from __future__ import annotations

import re
import threading
from bisect import bisect_left
from collections import Counter
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, NamedTuple

ACCOUNT_TABLE = "glow_persistence_appaccount"
DJANGO = "django"
DRIVER = "driver"

# How D14 reads a statement (the exact-head review of Stage B, #4; DM-75): PostgreSQL's lexical
# rules, with ``standard_conforming_strings`` on (its default), so a backslash escapes only in
# ``E'…'``.
_LEX = re.compile(
    r"""
    (?P<space>[ \t\n\r\f\v]+)
    | (?P<line>--[^\n\r]*+)
    | (?P<block>/\*)
    | (?P<escape>[eE]'(?:[^'\\]|\\.|'')*+')
    | (?P<unicode>[uU]&'(?:[^']|'')*+')
    | (?P<uname>[uU]&"(?:[^"]|"")*+")
    | (?P<string>'(?:[^']|'')*+')
    | (?P<name>"(?:[^"]|"")*+")
    | (?P<dollar>\$(?:[A-Za-z_\x80-\U0010ffff][A-Za-z0-9_\x80-\U0010ffff]*+)?\$)
    | (?P<word>[A-Za-z_\x80-\U0010ffff][A-Za-z0-9_$\x80-\U0010ffff]*+)
    | (?P<number>[0-9][0-9_]*+(?:\.[0-9_]*+)?(?:[eE][+-]?[0-9]++)?|\.[0-9][0-9_]*+)
    | (?P<other>.)
    """,
    re.S | re.X,
)
_BLOCK = re.compile(r"/\*|\*/")
# A string constant continues across whitespace that holds a newline (``--`` comments allowed,
# block comments not), keeping its kind: an ``E'…'`` constant's continuation still takes backslash
# escapes.
_CONTINUE = re.compile(
    r"(?:[ \t\f\v]|--[^\n\r]*+)*+[\n\r](?:[ \t\n\r\f\v]++|--[^\n\r]*+[\n\r])*+(?=')"
)
_ESCAPE_BODY = re.compile(r"'(?:[^'\\]|\\.|'')*+'", re.S)
_PLAIN_BODY = re.compile(r"'(?:[^']|'')*+'")
# PostgreSQL truncates every identifier to NAMEDATALEN - 1 bytes.
_NAME_BYTES = 63
_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
# The fast path: a statement with no quote mark but double quotes, no comment, dollar sign or
# ampersand (so no ``U&``), an even count of double quotes (so every quoted identifier ends), no
# ``DO`` and no writer's lock in its text cannot fail the rule and takes no writer's lock.
_SPAN_MARKS = ("'", "$", "--", "/*", "&")
_MAYBE_DO = re.compile(r"(?:\A|;)\s*DO\b", re.I)
_MAYBE_CREATE = re.compile(r"\bCREATE\b", re.I)
# Correction B-C4's item 3 (B-C3's delta re-review, F4; DM-78): the fast path reads ``VIEW`` as it
# reads ``FUNCTION`` and ``PROCEDURE``, so a text that may create a view is read in full.
_MAYBE_CREATED = re.compile(r"\b(?:FUNCTION|PROCEDURE|VIEW)\b", re.I)
_TEXT_WRITER = re.compile(r"\bFOR\s+(?:NO\s+KEY\s+)?UPDATE\b", re.I)
_TEXT_FOR_UPDATE = re.compile(r"\bFOR\s+UPDATE\b", re.I)
_TEXT_ACCOUNT = re.compile(r"glow_persistence_appaccount", re.I)
# Correction B-C3's item 6 (B-C2's delta re-review, S2; DM-77): psycopg writes each parameter's
# value into the text before sending it, so a placeholder glued to a name character or a dollar
# sign can complete a dollar-quote tag (``$q%s$`` with ``1`` is ``$q1$``). ``%%`` is a literal
# percent sign, not a placeholder; the word ``UPDATE`` is matched as the other words are (whole
# word, any case), anywhere in the text, spans and comments included.
_TEXT_UPDATE = re.compile(r"\bUPDATE\b", re.I)
# Correction B-C4's item 1 (B-C3's delta re-review, F1; DM-78): a placeholder as psycopg 3.3.6
# reads one (``_re_placeholder`` and ``_split_query``): ``%s``, ``%b`` or ``%t``, or a name of one
# or more characters other than ``)`` in parentheses followed by one of them; ``%%`` is a literal
# percent sign. The text is scanned in order, as psycopg scans it, so ``%%`` is read first.
_PLACEHOLDER = re.compile(r"%%|%\([^)]+\)[sbt]|%[sbt]")
_NAME_CHARACTER = re.compile(r"[A-Za-z0-9_$\x80-\U0010ffff]")
# A text that may hold a span (a string constant, a quoted identifier or a comment): the span test
# reads only such a text.
_SPAN_STARTS = ("'", '"', "$", "--", "/*")
# A text whose only span mark is the double quote, with an even count of them, holds only quoted
# identifiers, each ended, which the lexer reads left to right, a doubled quote inside one kept in
# it; so a position lies inside one exactly where an odd count of double quotes stands before it,
# and that is read without reading the text in full (Django's statements are all of this kind).
_OTHER_SPAN_STARTS = ("'", "$", "--", "/*")

UNTERMINATED = "an unterminated string constant, quoted identifier or block comment"
DO_STATEMENT = "a DO statement, whose body runs as code"
CREATES_ROUTINE = "a statement that creates a function or a procedure, whose body runs as code"
CREATES_VIEW = (
    "a statement that creates a view, through which a lock reaches a table it does not name"
)
U_AND_NAME = "a U& quoted identifier, whose escapes can spell any name, with FOR UPDATE"
GLUED_PLACEHOLDER = (
    "a placeholder glued to a name character or a dollar sign, in a statement whose text holds"
    " UPDATE"
)
PLACEHOLDER_IN_SPAN = (
    "a placeholder inside a string constant, a quoted identifier or a comment, which the value"
    " psycopg writes there can end"
)
OUTSIDE_THE_MODELS = (
    "FOR UPDATE in a statement that reads a relation name that is not one of the models' tables"
    " written without a schema"
)
TABLE_COMMAND = "FOR UPDATE in a statement that holds a TABLE command, whose relation is not read"
# The words PostgreSQL reads between ``CREATE [OR REPLACE]`` and ``VIEW``: the temporary and
# unlogged options (``LOCAL`` and ``GLOBAL`` before ``TEMP`` or ``TEMPORARY``), ``RECURSIVE`` and
# ``MATERIALIZED``.
_VIEW_OPTIONS = frozenset(
    {"temp", "temporary", "local", "global", "unlogged", "recursive", "materialized"}
)
_SUB_QUERY_STARTS = frozenset({"select", "with", "values", "table"})
_STRENGTHS = (("update",), ("no", "key", "update"), ("share",), ("key", "share"))
# Words that end a FROM list at its own depth.
_ENDS_FROM = frozenset(
    {
        "except",
        "fetch",
        "for",
        "group",
        "having",
        "intersect",
        "limit",
        "offset",
        "order",
        "returning",
        "select",
        "set",
        "union",
        "values",
        "where",
        "window",
    }
)
# PostgreSQL's reserved and type_func_name keywords: never a table's name, and never a bare alias
# (an unreserved keyword such as ``set`` or ``values`` can be one).
_KEYWORDS = frozenset(
    {
        "all",
        "analyse",
        "analyze",
        "and",
        "any",
        "array",
        "as",
        "asc",
        "asymmetric",
        "authorization",
        "binary",
        "both",
        "case",
        "cast",
        "check",
        "collate",
        "collation",
        "column",
        "concurrently",
        "constraint",
        "create",
        "cross",
        "current_catalog",
        "current_date",
        "current_role",
        "current_schema",
        "current_time",
        "current_timestamp",
        "current_user",
        "default",
        "deferrable",
        "desc",
        "distinct",
        "do",
        "else",
        "end",
        "except",
        "false",
        "fetch",
        "for",
        "foreign",
        "freeze",
        "from",
        "full",
        "grant",
        "group",
        "having",
        "ilike",
        "in",
        "initially",
        "inner",
        "intersect",
        "into",
        "is",
        "isnull",
        "join",
        "lateral",
        "leading",
        "left",
        "like",
        "limit",
        "localtime",
        "localtimestamp",
        "natural",
        "not",
        "notnull",
        "null",
        "offset",
        "on",
        "only",
        "or",
        "order",
        "outer",
        "overlaps",
        "placing",
        "primary",
        "references",
        "returning",
        "right",
        "select",
        "session_user",
        "similar",
        "some",
        "symmetric",
        "system_user",
        "table",
        "tablesample",
        "then",
        "to",
        "trailing",
        "true",
        "union",
        "unique",
        "user",
        "using",
        "variadic",
        "verbose",
        "when",
        "where",
        "window",
        "with",
    }
)

# The functions and procedures, views and materialized views, and rules that exist when the check
# runs, outside ``pg_catalog``, ``information_schema``, the TOAST schemas (``pg_toast`` and each
# ``pg_toast_temp_N``) and extensions: a temporary schema's (``pg_temp_N``) count (correction
# B-C3's item 3; B-C2's delta re-review, F3; DM-77).
OWN_OBJECTS = """
SELECT
  (SELECT count(*) FROM pg_catalog.pg_proc p
     JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
      AND n.nspname NOT LIKE 'pg\\_toast\\_temp\\_%'
      AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend d
                       WHERE d.classid = 'pg_catalog.pg_proc'::regclass
                         AND d.objid = p.oid AND d.deptype = 'e')),
  (SELECT count(*) FROM pg_catalog.pg_class c
     JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('v', 'm')
      AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
      AND n.nspname NOT LIKE 'pg\\_toast\\_temp\\_%'),
  (SELECT count(*) FROM pg_catalog.pg_rewrite r
     JOIN pg_catalog.pg_class c ON c.oid = r.ev_class
     JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE r.rulename <> '_RETURN'
      AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
      AND n.nspname NOT LIKE 'pg\\_toast\\_temp\\_%')
"""


class _Token(NamedTuple):
    """One token as PostgreSQL reads it: ``word`` (an unquoted word, in lower case), ``name`` (a
    quoted identifier, as written, unquoted), ``uname`` (a ``U&`` quoted identifier), ``string``
    (a masked string constant), ``number`` or ``other`` (one character)."""

    kind: str
    text: str


_OPEN = _Token("other", "(")
_CLOSE = _Token("other", ")")
_COMMA = _Token("other", ",")
_DOT = _Token("other", ".")
_STAR = _Token("other", "*")
_SEMI = _Token("other", ";")
_MASKED = _Token("string", "")


def _read(sql: str, spans: list[tuple[int, int]] | None = None) -> list[_Token] | str:
    """The statement's tokens, every comment dropped and every string constant masked, or why it
    cannot be read (an unterminated span). Where ``spans`` is given, each comment's, string
    constant's (its continuations included) and quoted identifier's start and end in ``sql`` are
    added to it, in order."""
    found: list[_Token] = []
    position, size = 0, len(sql)
    # With no block comment or dollar quote, no token needs a scan of its own: one pass reads all.
    matches = None if "/*" in sql or "$" in sql else _LEX.finditer(sql)
    while position < size:
        match = next(matches) if matches is not None else _LEX.match(sql, position)
        assert match is not None  # ``other`` matches any one character
        kind, text, position = str(match.lastgroup), match.group(), match.end()
        start = match.start()
        if kind == "space":
            continue
        if kind == "line":
            if spans is not None:
                spans.append((start, position))
            continue
        if kind == "block":
            depth = 1
            while depth:
                edge = _BLOCK.search(sql, position)
                if edge is None:
                    return UNTERMINATED
                depth += 1 if edge.group() == "/*" else -1
                position = edge.end()
            if spans is not None:
                spans.append((start, position))
            continue
        if kind == "dollar":
            close = sql.find(text, position)
            if close < 0:
                return UNTERMINATED
            position = close + len(text)
            found.append(_MASKED)
            if spans is not None:
                spans.append((start, position))
        elif kind in ("escape", "unicode", "string"):
            body = _ESCAPE_BODY if kind == "escape" else _PLAIN_BODY
            gap = _CONTINUE.match(sql, position)
            if gap is not None:
                matches = None  # the scan moves past the continuation itself: read on by position
            while gap is not None:
                part = body.match(sql, gap.end())
                if part is None:
                    return UNTERMINATED
                position = part.end()
                gap = _CONTINUE.match(sql, position)
            found.append(_MASKED)
            if spans is not None:
                spans.append((start, position))
        elif kind == "name":
            found.append(_Token("name", _truncated(text[1:-1].replace('""', '"'))))
            if spans is not None:
                spans.append((start, position))
        elif kind == "uname":
            found.append(_Token("uname", ""))
            if spans is not None:
                spans.append((start, position))
        elif kind == "word":
            # A lone E or U at a token's start that did not begin a whole constant or identifier
            # begins one that never ends.
            if text in ("e", "E") and sql.startswith("'", position):
                return UNTERMINATED
            if text in ("u", "U") and sql.startswith(("&'", '&"'), position):
                return UNTERMINATED
            found.append(_Token("word", _truncated(text.translate(_ASCII_LOWER))))
        elif kind == "other" and text in ("'", '"'):
            return UNTERMINATED
        else:
            found.append(_Token(kind, text))
    return found


def _truncated(name: str) -> str:
    """A name as PostgreSQL keeps it: at most 63 bytes, cut on a character's boundary."""
    data = name.encode("utf-8")
    if len(data) <= _NAME_BYTES:
        return name
    return data[:_NAME_BYTES].decode("utf-8", "ignore")


def _word(token: _Token, *words: str) -> bool:
    return token.kind == "word" and token.text in words


def _is_account(token: _Token) -> bool:
    return token.kind in ("word", "name") and token.text.lower() == ACCOUNT_TABLE


class _Clause(NamedTuple):
    """One lock clause: its strength, its ``OF`` list's token positions (``None`` for no list or
    one it cannot read), and the positions of its first token and of the token after it."""

    strength: str
    names: tuple[int, ...] | None
    start: int
    end: int


def _clauses(tokens: list[_Token]) -> list[_Clause]:
    found: list[_Clause] = []
    size = len(tokens)
    for start, token in enumerate(tokens):
        if not _word(token, "for"):
            continue
        for words in _STRENGTHS:
            if not all(
                start + 1 + k < size and _word(tokens[start + 1 + k], word)
                for k, word in enumerate(words)
            ):
                continue
            at = start + 1 + len(words)
            names: list[int] | None = None
            if at < size and _word(tokens[at], "of"):
                at += 1
                names = []
                while True:
                    if at < size and tokens[at].kind in ("word", "name"):
                        names.append(at)
                        at += 1
                    else:
                        names = None
                        break
                    if at < size and tokens[at] == _COMMA:
                        at += 1
                        continue
                    break
            if at < size and _word(tokens[at], "nowait"):
                at += 1
            elif at + 1 < size and _word(tokens[at], "skip") and _word(tokens[at + 1], "locked"):
                at += 2
            listed = None if names is None else tuple(names)
            found.append(_Clause(" ".join(words), listed, start, at))
            break
    return found


@dataclass(frozen=True)
class Verdict:
    """D14's judgement of one statement: why it fails (``None`` if it passes), whether it takes a
    writer's row lock, whether it names the account table (read only for a statement that takes
    one, or one read in full), and whether it takes ``FOR UPDATE``."""

    reason: str | None
    writer: bool
    account: bool
    for_update: bool


def _placeholders(sql: str) -> Iterator[tuple[int, int]]:
    """Each placeholder's start and end in ``sql``, read as psycopg 3.3.6 reads them (``%%``, a
    literal percent sign, skipped)."""
    if "%" not in sql:
        return
    for match in _PLACEHOLDER.finditer(sql):
        if match.group() != "%%":
            yield match.span()


def _glued_placeholder(sql: str) -> bool:
    """Whether ``sql`` holds the word ``UPDATE`` anywhere and a placeholder (``%s``, ``%b``,
    ``%t`` or a named one such as ``%(name)s``) whose neighbour on either side is a name character
    (a letter, digit, underscore, dollar sign or non-ASCII character)."""
    if "%" not in sql or _TEXT_UPDATE.search(sql) is None:
        return False
    for start, end in _placeholders(sql):
        if (start > 0 and _NAME_CHARACTER.match(sql, start - 1)) or (
            end < len(sql) and _NAME_CHARACTER.match(sql, end)
        ):
            return True
    return False


def _in_quoted_name(sql: str, placeholders: list[tuple[int, int]]) -> bool:
    """Whether any part of one of ``placeholders`` lies inside a quoted identifier, in a text whose
    only spans are quoted identifiers, each ended: an odd count of double quotes before its start,
    or a double quote in it."""
    count, at = 0, 0
    for start, end in placeholders:
        count += sql.count('"', at, start)
        if count % 2 or '"' in sql[start:end]:
            return True
        at = start
    return False


def _in_span(placeholders: list[tuple[int, int]], spans: list[tuple[int, int]]) -> bool:
    """Whether any part of one of ``placeholders`` lies inside one of ``spans`` (each a string
    constant's, a quoted identifier's or a comment's start and end, in order, none overlapping)."""
    starts = [start for start, _ in spans]
    for start, end in placeholders:
        # The last span that starts before the placeholder ends; an earlier one ends before it.
        at = bisect_left(starts, end) - 1
        if at >= 0 and spans[at][1] > start:
            return True
    return False


def _creates(tokens: list[_Token]) -> str | None:
    """Why the statement fails as a creation, as PostgreSQL reads it: it creates a function or a
    procedure (``CREATE [OR REPLACE] FUNCTION`` or ``PROCEDURE``), or a view (``CREATE [OR
    REPLACE] [TEMP | TEMPORARY] [RECURSIVE] VIEW`` or ``CREATE MATERIALIZED VIEW``, with
    ``LOCAL``, ``GLOBAL`` and ``UNLOGGED`` read among the options as PostgreSQL reads them)."""
    size = len(tokens)
    for i, token in enumerate(tokens):
        if not _word(token, "create"):
            continue
        k = i + 1
        if k + 1 < size and _word(tokens[k], "or") and _word(tokens[k + 1], "replace"):
            k += 2
        if k < size and _word(tokens[k], "function", "procedure"):
            return CREATES_ROUTINE
        while k < size and _word(tokens[k], *_VIEW_OPTIONS):
            k += 1
        if k < size and _word(tokens[k], "view"):
            return CREATES_VIEW
    return None


def judge(sql: str, tables: frozenset[str] = frozenset()) -> Verdict:
    """D14's judgement of ``sql`` as PostgreSQL reads the text the record receives, before psycopg
    writes its parameters into it, with ``standard_conforming_strings`` on. ``tables`` is the
    models' tables; when it is given, an ``OF`` name must resolve to one of them, and a statement
    that takes ``FOR UPDATE`` without naming the account table must read only them, in the
    positions its reading binds (the module docstring's rule)."""

    def by_text(reason: str) -> Verdict:
        return Verdict(
            reason,
            _TEXT_WRITER.search(sql) is not None,
            _TEXT_ACCOUNT.search(sql) is not None,
            _TEXT_FOR_UPDATE.search(sql) is not None,
        )

    if _glued_placeholder(sql):
        return by_text(GLUED_PLACEHOLDER)
    # Correction B-C4's item 2 (B-C3's delta re-review, F5; DM-78): a placeholder any part of which
    # lies inside a span fails, whatever the statement holds, before the fast path.
    tokens: list[_Token] | str | None = None
    placeholders = list(_placeholders(sql))
    if placeholders and any(mark in sql for mark in _SPAN_STARTS):
        if not any(mark in sql for mark in _OTHER_SPAN_STARTS) and sql.count('"') % 2 == 0:
            inside = _in_quoted_name(sql, placeholders)
        else:
            spans: list[tuple[int, int]] = []
            tokens = _read(sql, spans)
            if isinstance(tokens, str):
                return by_text(tokens)
            inside = _in_span(placeholders, spans)
        if inside:
            return by_text(PLACEHOLDER_IN_SPAN)
    if not any(mark in sql for mark in _SPAN_MARKS) and sql.count('"') % 2 == 0:
        lowered = sql.lower()
        no_writer = "update" not in lowered or _TEXT_WRITER.search(sql) is None
        no_do = (";" not in sql and not lowered.lstrip().startswith("do")) or (
            _MAYBE_DO.search(sql) is None
        )
        no_create = (
            "create" not in lowered
            or _MAYBE_CREATE.search(sql) is None
            or _MAYBE_CREATED.search(sql) is None
        )
        if no_writer and no_do and no_create:
            return Verdict(None, False, False, False)
    if tokens is None:
        tokens = _read(sql)
    if isinstance(tokens, str):
        return by_text(tokens)
    clauses = _clauses(tokens)
    writer = any(clause.strength in ("update", "no key update") for clause in clauses)
    for_update = any(clause.strength == "update" for clause in clauses)
    account = any(_is_account(token) for token in tokens)
    starts = [0] + [i + 1 for i, token in enumerate(tokens) if token == _SEMI]
    if any(i < len(tokens) and _word(tokens[i], "do") for i in starts):
        return Verdict(DO_STATEMENT, writer, account, for_update)
    created = _creates(tokens)
    if created is not None:
        return Verdict(created, writer, account, for_update)
    if not for_update:
        return Verdict(None, writer, account, for_update)
    if any(token.kind == "uname" for token in tokens):
        return Verdict(U_AND_NAME, writer, account, for_update)
    if not account:
        # Correction B-C4's item 3 (Codex on 4c2f918; DM-78): with the models' tables given, a
        # FOR UPDATE that names no account table reads only those tables.
        if not tables:
            return Verdict(None, writer, account, for_update)
        return Verdict(_relations(tokens, tables), writer, account, for_update)
    return Verdict(_resolve(tokens, clauses, tables), writer, account, for_update)


def refusal(sql: str, tables: frozenset[str] = frozenset()) -> str | None:
    """Why ``sql`` fails D14's rule, or ``None``. ``tables`` is the models' tables; when it is
    given, an ``OF`` name must resolve to one of them."""
    return judge(sql, tables).reason


@dataclass
class _Item:
    """One relation a statement binds: whether it is a plain ``FROM`` or ``JOIN`` item, its table
    (``None`` for a sub-query, a function, a join's ``USING (…) AS`` alias or a ``WITH`` query)
    and that table's token position, the ``FROM`` list it belongs to, whether it is a ``WITH``
    query (``table`` then its name), and whether its table's name is schema-qualified."""

    plain: bool
    table: str | None
    position: int | None
    clause: int | None
    query: bool = False
    qualified: bool = False


@dataclass
class _Reading:
    """What ``_bindings`` reads in a statement: its items, the items each name binds, and whether
    a sub-query encloses each token."""

    items: list[_Item]
    bound: dict[str, set[int]]
    in_sub: list[bool]


def _resolve(tokens: list[_Token], clauses: list[_Clause], tables: frozenset[str]) -> str | None:
    """The rule for a statement that takes ``FOR UPDATE`` and names the account table: each such
    clause's ``OF`` names, each bound once, in any scope, by a plain ``FROM`` or ``JOIN`` item
    whose table is a model's and not the account table, and the account table appearing only as
    such an item's table, a column's qualifier or a name in a lock clause's ``OF`` list."""
    reading = _bindings(tokens)
    if isinstance(reading, str):
        return reading
    return _account_rule(tokens, clauses, tables, reading)


def _relations(tokens: list[_Token], tables: frozenset[str]) -> str | None:
    """The relations check (correction B-C4's item 3; Codex on 4c2f918; DM-78), for a statement
    that takes ``FOR UPDATE`` and does not name the account table, the models' tables given: every
    relation name its reading binds, in any scope (each ``FROM``, ``JOIN``, ``USING``-list,
    ``INTO``, ``UPDATE`` and ``DELETE FROM`` item, a ``WITH`` query's name read as one; not an
    item after a ``set`` or ``values`` read as the end of the ``FROM`` list, a stated limit:
    B-C4's delta re-review, F1; DM-79), is one of ``tables``, written without a schema; a
    ``TABLE`` command, or parentheses it cannot read, fail it. A sub-query's and a function's
    own relations are read in turn; a function is not a relation."""
    if any(_word(token, "table") for token in tokens):
        return TABLE_COMMAND
    reading = _bindings(tokens)
    if isinstance(reading, str):
        return reading
    for item in reading.items:
        if item.table is None:
            continue
        if item.qualified or item.table not in tables:
            return OUTSIDE_THE_MODELS
    return None


def _bindings(tokens: list[_Token]) -> _Reading | str:
    """Every relation the statement binds, in any scope, or why it cannot be read (parentheses it
    cannot read)."""
    size = len(tokens)
    # Each token's depth, whether a sub-query encloses it, and each parenthesis's partner.
    depth = [0] * size
    in_sub = [False] * size
    enclosing: list[int | None] = [None] * size
    innermost_sub = [False] * size
    partner: dict[int, int] = {}
    stack: list[tuple[int, bool]] = []
    for i, token in enumerate(tokens):
        if token == _CLOSE:
            if not stack:
                return "parentheses it cannot read"
            opened, _ = stack.pop()
            partner[opened] = i
        depth[i] = len(stack)
        in_sub[i] = any(sub for _, sub in stack)
        enclosing[i] = stack[-1][0] if stack else None
        innermost_sub[i] = bool(stack) and stack[-1][1]
        if token == _OPEN:
            k = i + 1
            while k < size and tokens[k] == _OPEN:
                k += 1
            stack.append((i, k < size and _word(tokens[k], *_SUB_QUERY_STARTS)))
    if stack:
        return "parentheses it cannot read"

    items: list[_Item] = []
    bound: dict[str, set[int]] = {}
    consumed: set[int] = set()  # alias tokens a relation read, which the scan steps over
    # Correction B-C3's item 5 (B-C2's delta re-review, F5; DM-77): the depths inside a
    # parenthesised join, where every item is read as a binding, none of them plain, and the
    # tokens where such a join's first item starts.
    joined: set[int] = set()
    item_starts: set[int] = set()
    # Each depth's open FROM list (the position of the word that opened it), or ``None``.
    open_list: dict[int, int | None] = {}
    # The lists none of whose items is plain: a DELETE or MERGE statement's USING list.
    not_plain_lists: set[int] = set()

    def bind(name: str | None, item: int) -> None:
        if name is not None:
            bound.setdefault(name, set()).add(item)

    # The parentheses that directly hold a SELECT, VALUES, TABLE or WITH: sub-queries.
    queries = {
        opened
        for k, opened in enumerate(enclosing)
        if opened is not None and _word(tokens[k], *_SUB_QUERY_STARTS)
    }

    def joins_in(opened: int) -> bool:
        """Whether the parenthesis at ``opened``, where a FROM item stands, holds a joined table
        rather than a sub-query: no ``SELECT``, ``VALUES``, ``TABLE`` or ``WITH`` at its own
        depth, and more than one token inside it (``ONLY (name)`` is read apart)."""
        return partner[opened] != opened + 2 and opened not in queries

    def relation(at: int, clause: int | None, plain: bool, aliases: str = "any") -> int:
        """Reads the item at ``at``; returns where the scan goes on (inside a parenthesis it
        opens, so a sub-query's own items are read too). ``aliases`` is how an alias may follow:
        ``any`` (a FROM item: ``AS`` or a bare name that is not a reserved keyword), ``update``
        (an ``UPDATE`` target, where a bare ``SET`` is the keyword) or ``as`` (an ``INSERT`` or
        ``SELECT`` ``INTO`` target: only after ``AS``; a ``MERGE INTO`` target's is read as a FROM
        item's, since B-C4)."""
        resume: int | None = None
        table: str | None = None
        position: int | None = None
        opened_join: int | None = None
        qualified = False
        while at < size and _word(tokens[at], "lateral", "only"):
            plain, at = False, at + 1
        if at < size and tokens[at] == _OPEN:
            plain, resume, k = False, at, partner[at] + 1
            if partner[at] == at + 2 and tokens[at + 1].kind in ("word", "name"):
                position = at + 1  # ``ONLY (name)``
                table = tokens[position].text
            elif joins_in(at):
                opened_join = at
        elif at < size and (
            tokens[at].kind == "name"
            or (tokens[at].kind == "word" and tokens[at].text not in _KEYWORDS)
        ):
            parts, k = [at], at + 1
            while k + 1 < size and tokens[k] == _DOT and tokens[k + 1].kind in ("word", "name"):
                parts.append(k + 1)
                k += 2
            plain = plain and len(parts) == 1
            qualified = len(parts) > 1
            position = parts[-1]
            table = tokens[position].text
            if k < size and tokens[k] == _OPEN:  # a function
                plain, resume, table, position = False, k, None, None
                k = partner[k] + 1
            elif k < size and tokens[k] == _STAR:
                plain, k = False, k + 1
        else:
            return at
        alias: str | None = None
        if k < size and _word(tokens[k], "as"):
            if k + 1 < size and tokens[k + 1].kind in ("word", "name"):
                alias, k = tokens[k + 1].text, k + 2
                consumed.update((k - 2, k - 1))
        elif (
            aliases != "as"
            and k < size
            and (
                tokens[k].kind == "name"
                or (
                    tokens[k].kind == "word"
                    and tokens[k].text not in _KEYWORDS
                    and not (aliases == "update" and tokens[k].text == "set")
                )
            )
        ):
            alias, k = tokens[k].text, k + 1
            consumed.add(k - 1)
        if k < size and (tokens[k] == _OPEN or _word(tokens[k], "tablesample")):
            plain = False  # a column alias list, or a sample
        items.append(_Item(plain, table, position, clause, qualified=qualified))
        # As PostgreSQL reads it, an alias hides its table's name: the item binds one name.
        bind(alias if alias is not None else table, len(items) - 1)
        if opened_join is not None:
            # A parenthesised join: its items are read as a FROM list's, none of them plain.
            inner = depth[opened_join] + 1
            open_list[inner] = clause if clause is not None else opened_join
            joined.add(inner)
            item_starts.add(opened_join + 1)
            return opened_join + 1
        return resume if resume is not None else k

    # Every FROM list's items, its JOIN and comma items included, and each other binding form.
    commas: set[int] = set()
    # At each depth, where the last DELETE or MERGE and the last JOIN stand: a USING after a JOIN
    # is the join's column list, which binds nothing; one after a DELETE or MERGE opens a list.
    last_dml: dict[int, int] = {}
    last_join: dict[int, int] = {}
    i = 0
    while i < size:
        token, level = tokens[i], depth[i]
        if i in item_starts:
            item_starts.discard(i)
            i = relation(i, open_list.get(level), False)
            continue
        if i in consumed:
            i += 1
            continue
        if _word(token, "delete", "merge"):
            last_dml[level] = i
        elif _word(token, "join"):
            last_join[level] = i
        elif token == _SEMI:
            last_dml.clear()
            last_join.clear()
        if _word(token, "using") and last_dml.get(level, -1) > last_join.get(level, -1):
            # A DELETE or MERGE statement's USING list: every item a binding, none plain.
            open_list[level] = i
            not_plain_lists.add(i)
            last_dml.pop(level)
            i = relation(i + 1, i, False)
            continue
        if _word(token, "using") and i + 1 < size and tokens[i + 1] == _OPEN:
            # Correction B-C4's item 4 (B-C3's delta re-review, F3; DM-78): a join's
            # ``USING (…) AS name`` binds that name, to no table, and it is not plain.
            k = partner[i + 1] + 1
            if k + 1 < size and _word(tokens[k], "as") and tokens[k + 1].kind in ("word", "name"):
                items.append(_Item(False, None, None, open_list.get(level)))
                bind(tokens[k + 1].text, len(items) - 1)
                consumed.update((k, k + 1))
        opener = enclosing[i]
        if _word(token, "from") and (
            (i > 0 and _word(tokens[i - 1], "distinct"))
            or (
                opener is not None
                and not innermost_sub[i]
                and opener > 0
                and tokens[opener - 1].kind in ("word", "name")
                and not _word(tokens[opener - 1], *_KEYWORDS)
            )
        ):
            # ``IS DISTINCT FROM``, or a FROM among a function's arguments (``EXTRACT(… FROM …)``,
            # ``SUBSTRING``, ``TRIM``, ``OVERLAY``): no FROM list.
            i += 1
            continue
        if _word(token, "from"):
            open_list[level] = i
            i = relation(i + 1, i, not (i > 0 and _word(tokens[i - 1], "delete")))
            continue
        if _word(token, "join") and open_list.get(level) is not None:
            i = relation(i + 1, open_list[level], level not in joined)
            continue
        if token == _COMMA and open_list.get(level) is not None:
            commas.add(open_list[level] or 0)
            i = relation(i + 1, open_list[level], False)
            continue
        if _word(token, "into"):
            # Correction B-C4's item 4 (B-C3's delta re-review, F2; DM-78): a ``MERGE INTO``
            # target's alias may be written without ``AS`` (``USING``, a reserved word, ends it).
            merge = i > 0 and _word(tokens[i - 1], "merge")
            i = relation(i + 1, None, False, "any" if merge else "as")
            continue
        if _word(token, "update") and not (
            i > 0 and _word(tokens[i - 1], "for", "key", "do", "on")
        ):
            i = relation(i + 1, None, False, "update")
            continue
        if token == _CLOSE:
            open_list[level + 1] = None
            joined.discard(level + 1)
        elif token.kind == "word" and token.text in _ENDS_FROM:
            open_list[level] = None
        i += 1
    for item in items:
        if item.clause in commas or item.clause in not_plain_lists:
            item.plain = False
    for i, token in enumerate(tokens):
        if (_word(token, "with", "recursive") or token == _COMMA) and i + 1 < size:
            if tokens[i + 1].kind not in ("word", "name"):
                continue
            k = i + 2
            if k < size and tokens[k] == _OPEN:
                k = partner[k] + 1
            if not (k < size and _word(tokens[k], "as")):
                continue
            k += 1
            while k < size and _word(tokens[k], "not", "materialized"):
                k += 1
            if k < size and tokens[k] == _OPEN:
                items.append(_Item(False, tokens[i + 1].text, None, None, query=True))
                bind(tokens[i + 1].text, len(items) - 1)
    return _Reading(items, bound, in_sub)


def _account_rule(
    tokens: list[_Token], clauses: list[_Clause], tables: frozenset[str], reading: _Reading
) -> str | None:
    """The account table only as a plain item's table outside any sub-query, a column's
    qualifier, or a name in a lock clause's OF list; and each ``FOR UPDATE`` clause's ``OF``
    names, each bound once to a plain item whose table is a model's and not the account
    table."""
    size = len(tokens)
    items, bound, in_sub = reading.items, reading.bound, reading.in_sub
    # The account table appears only as a plain item's table outside any sub-query, a column's
    # qualifier, or a name in a lock clause's OF list.
    listed = {k for clause in clauses for k in clause.names or ()}
    plain_tables = {
        item.position
        for item in items
        if item.plain and item.position is not None and not in_sub[item.position]
    }
    for i, token in enumerate(tokens):
        if not _is_account(token) or i in listed or i in plain_tables:
            continue
        if i + 1 < size and tokens[i + 1] == _DOT and not (i > 0 and tokens[i - 1] == _DOT):
            continue
        return (
            "the account table appears other than as a plain FROM or JOIN item's table outside"
            " any sub-query, or a column's qualifier"
        )

    starts = {clause.start for clause in clauses}
    for clause in clauses:
        if clause.strength != "update":
            continue
        if clause.names is None:
            return "FOR UPDATE with no OF list it can read"
        rest = tokens[clause.end :]
        while rest and rest[-1] == _SEMI:
            rest.pop()
        if rest and clause.end not in starts:
            return "text after the lock clause that is not another lock clause"
        for k in clause.names:
            found = sorted(bound.get(tokens[k].text, set()))
            if any(items[f].query for f in found):
                return "FOR UPDATE OF a WITH query"
            if not found:
                return "FOR UPDATE OF a name the statement gives no table"
            if len(found) > 1:
                return "FOR UPDATE OF a name the statement binds more than once"
            item = items[found[0]]
            if not item.plain or item.table is None:
                return (
                    "FOR UPDATE OF a name bound other than as a plain FROM or JOIN item (a comma"
                    " item, a schema-qualified name, ONLY, *, a sub-query or a function)"
                )
            if item.table.lower() == ACCOUNT_TABLE:
                return "FOR UPDATE OF the account table or an alias it is given"
            if tables and item.table not in tables:
                return "FOR UPDATE OF a relation that is not a model's table"
    return None


def query_text(query: Any) -> str:
    """A statement's text as the record keeps it: a string as it is; psycopg's composed SQL with
    each literal and placeholder written as ``%s``, so no parameter is kept."""
    if isinstance(query, str):
        return query
    if isinstance(query, bytes | bytearray | memoryview):
        return bytes(query).decode("utf-8", "replace")
    from psycopg import sql

    if isinstance(query, sql.Composed):
        return "".join(query_text(part) for part in query)
    if isinstance(query, sql.Literal | sql.Placeholder):
        return "%s"
    if isinstance(query, sql.SQL | sql.Identifier):
        return str(query.as_string(None))
    return f"<{type(query).__name__}>"


@dataclass(frozen=True)
class Seen:
    """One statement a window saw: its source, thread, connection and text."""

    source: str
    thread: int
    connection: int
    text: str


@dataclass
class Summary:
    statements: int = 0
    through_django: int = 0
    through_driver: int = 0
    connections: int = 0
    threads: int = 0
    writer_locks: int = 0
    account_writer_locks: int = 0
    account_no_key: int = 0
    account_update_of_others: int = 0
    refused: int = 0
    functions: int = -1
    views: int = -1
    rules: int = -1
    refusals: list[tuple[str, str, int]] = field(default_factory=list)

    def failures(self) -> int:
        """Refused statements, the database's own objects, and a record that saw nothing (it was
        not installed) each count as a failure."""
        own = sum(max(n, 0) for n in (self.functions, self.views, self.rules))
        unread = sum(1 for n in (self.functions, self.views, self.rules) if n < 0)
        return self.refused + own + unread + (1 if self.statements == 0 else 0)

    def passed(self) -> bool:
        return self.failures() == 0

    def lines(self, suite: str) -> list[str]:
        found = [
            f"[{suite}] row locks sent (D14): {self.statements} statements"
            f" ({self.through_django} through Django's execute or executemany,"
            f" {self.through_driver} through the driver itself) on {self.connections}"
            f" connections in {self.threads} threads; {self.writer_locks} take a writer's row"
            f" lock, {self.account_writer_locks} of them naming the account table"
            f" ({self.account_no_key} FOR NO KEY UPDATE, {self.account_update_of_others}"
            f" FOR UPDATE OF other tables only); {self.refused} refused; the database's own"
            f" functions {self.functions}, views {self.views}, rules {self.rules}",
        ]
        for reason, text, count in self.refusals:
            found.append(f"[{suite}] row lock refused (D14): {reason} ({count}x): {text}")
        found.append(f"ROW LOCKS (D14): {'PASS' if self.passed() else 'FAIL'}")
        return found

    def as_dict(self) -> dict[str, Any]:
        return {
            "statements": self.statements,
            "through_django": self.through_django,
            "through_driver": self.through_driver,
            "connections": self.connections,
            "threads": self.threads,
            "writer_locks": self.writer_locks,
            "account_writer_locks": self.account_writer_locks,
            "account_no_key": self.account_no_key,
            "account_update_of_others": self.account_update_of_others,
            "refused": self.refused,
            "functions": self.functions,
            "views": self.views,
            "rules": self.rules,
            "failures": self.failures(),
        }


class RowLockRecord:
    """The record one suite's process keeps: counts, each refused statement's text, and the
    windows a case opens. It is thread-safe; it keeps no parameter and no accepted text."""

    def __init__(self, tables: frozenset[str] | None = None) -> None:
        # The models' tables, read from Django's registry the first time a statement needs them
        # (``None`` until then): the record is installed before the suite's first statement, and
        # may be installed before the registry is ready.
        self.tables = tables
        self._lock = threading.Lock()
        self._local = threading.local()
        self._counts: Counter[str] = Counter()
        self._connections: set[tuple[int, int]] = set()
        self._threads: set[int] = set()
        self._refused: Counter[tuple[str, str]] = Counter()
        self._windows: list[list[Seen]] = []
        self._installed = False
        self._originals: list[tuple[type, str, Any]] = []

    # -- recording ------------------------------------------------------------------------

    def _model_tables(self) -> frozenset[str]:
        if self.tables is None:
            from django.apps import apps

            if not apps.ready:
                return frozenset()
            self.tables = model_tables()
        return self.tables

    def note(self, sql: Any, source: str, connection: object) -> None:
        text = query_text(sql)
        thread = threading.get_ident()
        verdict = judge(text, self._model_tables())
        reason, writer = verdict.reason, verdict.writer
        account = writer and verdict.account
        with self._lock:
            self._counts["statements"] += 1
            self._counts[source] += 1
            self._connections.add((thread, id(connection)))
            self._threads.add(thread)
            if writer:
                self._counts["writer_locks"] += 1
            if account:
                self._counts["account_writer_locks"] += 1
                if reason is None and not verdict.for_update:
                    self._counts["account_no_key"] += 1
                elif reason is None:
                    self._counts["account_update_of_others"] += 1
            if reason is not None:
                self._refused[(reason, " ".join(text.split()))] += 1
            for window in self._windows:
                window.append(Seen(source, thread, id(connection), text))

    def wrapper(
        self, execute: Callable[..., Any], sql: Any, params: Any, many: bool, context: Any
    ) -> Any:
        """Django's execute wrapper: it records the statement, then marks the thread as inside
        Django's ``execute`` while the statement goes down, so the driver's record skips it."""
        self.note(sql, DJANGO, context.get("connection"))
        self._local.depth = getattr(self._local, "depth", 0) + 1
        try:
            return execute(sql, params, many, context)
        finally:
            self._local.depth -= 1

    def _inside_django(self) -> bool:
        return bool(getattr(self._local, "depth", 0))

    # -- installing ---------------------------------------------------------------------

    def _give(self, connection: Any) -> None:
        if self.wrapper not in connection.execute_wrappers:
            # First, so that a case's own ``execute_wrapper``, which appends and then pops the
            # last wrapper, never removes this one.
            connection.execute_wrappers.insert(0, self.wrapper)

    def _on_created(self, sender: Any, connection: Any, **kwargs: Any) -> None:
        self._give(connection)

    def _driver_method(self, original: Callable[..., Any]) -> Callable[..., Any]:
        record = self

        def method(cursor: Any, query: Any, *args: Any, **kwargs: Any) -> Any:
            if not record._inside_django():
                record.note(query, DRIVER, getattr(cursor, "connection", None))
            return original(cursor, query, *args, **kwargs)

        method.__name__ = getattr(original, "__name__", "method")
        method.__doc__ = getattr(original, "__doc__", None)
        return method

    def install(self) -> RowLockRecord:
        from django.db import connections
        from django.db.backends.signals import connection_created
        from psycopg import Cursor, ServerCursor

        if self._installed:
            return self
        connection_created.connect(self._on_created, weak=False, dispatch_uid=id(self))
        for connection in _open_connections(connections):
            self._give(connection)
        for owner, name in (
            (Cursor, "execute"),
            (Cursor, "executemany"),
            (Cursor, "stream"),
            (Cursor, "copy"),
            (ServerCursor, "execute"),
        ):
            original = owner.__dict__[name]
            self._originals.append((owner, name, original))
            setattr(owner, name, self._driver_method(original))
        self._installed = True
        return self

    def uninstall(self) -> None:
        from django.db import connections
        from django.db.backends.signals import connection_created

        if not self._installed:
            return
        connection_created.disconnect(dispatch_uid=id(self))
        for connection in _open_connections(connections):
            if self.wrapper in connection.execute_wrappers:
                connection.execute_wrappers.remove(self.wrapper)
        for owner, name, original in reversed(self._originals):
            setattr(owner, name, original)
        self._originals.clear()
        self._installed = False

    # -- reading --------------------------------------------------------------------------

    @contextmanager
    def window(self) -> Iterator[list[Seen]]:
        """Every statement the record sees while the block runs, from any thread."""
        seen: list[Seen] = []
        with self._lock:
            self._windows.append(seen)
        try:
            yield seen
        finally:
            with self._lock:
                self._windows.remove(seen)

    def summary(self, own: tuple[int, int, int] | None = None) -> Summary:
        with self._lock:
            counts = Counter(self._counts)
            refused = sorted(self._refused.items())
            connections = len(self._connections)
            threads = len(self._threads)
        functions, views, rules = own if own is not None else (-1, -1, -1)
        return Summary(
            statements=counts["statements"],
            through_django=counts[DJANGO],
            through_driver=counts[DRIVER],
            connections=connections,
            threads=threads,
            writer_locks=counts["writer_locks"],
            account_writer_locks=counts["account_writer_locks"],
            account_no_key=counts["account_no_key"],
            account_update_of_others=counts["account_update_of_others"],
            refused=sum(count for _, count in refused),
            functions=functions,
            views=views,
            rules=rules,
            refusals=[(reason, text, count) for (reason, text), count in refused],
        )

    def check(self) -> Summary:
        """The verdict, before the suite's: the counts, the refused statements and the
        database's own objects, read on the suite's connection."""
        from django.db import connection

        own: tuple[int, int, int] | None = None
        try:
            with connection.cursor() as cursor:
                cursor.execute(OWN_OBJECTS)
                row = cursor.fetchone()
            if row is not None:
                own = (int(row[0]), int(row[1]), int(row[2]))
        except Exception:  # noqa: BLE001 - unread counts fail the check, by type only
            own = None
        return self.summary(own)


_ACTIVE: RowLockRecord | None = None


def _open_connections(connections: Any) -> list[Any]:
    """This thread's connections, or none where Django has no settings yet (each connection made
    later is given the wrapper as it connects)."""
    from django.core.exceptions import ImproperlyConfigured

    try:
        return list(connections.all())
    except ImproperlyConfigured:
        return []


def model_tables() -> frozenset[str]:
    """Every table the installed models (and their many-to-many tables) define."""
    from django.apps import apps

    found: set[str] = set()
    for model in apps.get_models(include_auto_created=True):
        found.add(str(model._meta.db_table))
    return frozenset(found)


def install() -> RowLockRecord:
    """The suite's record, installed before its first statement; one per process."""
    global _ACTIVE
    if _ACTIVE is None:
        _ACTIVE = RowLockRecord().install()
    return _ACTIVE


def uninstall() -> None:
    """The record taken out, once its suite has checked it."""
    global _ACTIVE
    if _ACTIVE is not None:
        _ACTIVE.uninstall()
        _ACTIVE = None


def active() -> RowLockRecord | None:
    return _ACTIVE
