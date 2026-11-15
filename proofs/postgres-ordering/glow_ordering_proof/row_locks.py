"""D14's record of the row locks the suites send (the SV3 brief's D14 and acceptance check 15;
DM-68, DM-70, DM-71, DM-73; SV3 Stage B).

The lock scan (``account_lock_scan``) reads the source and cannot be complete, so each of the four
suites (the ordering suite's ``run``, ``identity``, ``profile`` and ``discovery``) also checks what
it sends. Before its first statement it installs one ``RowLockRecord``, which records the text of
every statement the process sends while the suite runs:

- **through Django** (``DJANGO``): an execute wrapper on every connection the process opens, the
  ones its concurrency cases open in other threads included (each new connection is given the
  wrapper as it connects, through Django's ``connection_created`` signal, and the connections
  already open are given it at install). It is the outermost wrapper, so it sees every statement
  Django's ``execute`` and ``executemany`` send, whatever wrapper a case adds inside it;
- **through the driver itself** (``DRIVER``; Stage B's item 2, DM-70 and DM-73): psycopg's own
  ``Cursor.execute``, ``executemany``, ``stream`` and ``copy``, and ``ServerCursor.execute``, are
  wrapped in the suite's process, and a statement they send outside Django's ``execute`` is
  recorded too. That is every statement sent through a method of the driver's cursor that Django's
  cursor passes through unwrapped (``stream``, ``copy``), through ``callproc`` (Django's cursor
  calls it without its execute wrappers, and Django's own psycopg 3 cursor class sends it as
  ``SELECT * FROM "name"(...)`` through the driver cursor's ``execute``), and through the driver's
  own connection (``connection.connection``: its ``cursor()`` and its ``execute``, which make a
  cursor of Django's cursor class, a subclass of psycopg's ``Cursor``). Nothing is refused: Django's
  own use of the driver's connection (creating cursors, the health check's ``SELECT 1``, configuring
  a new connection) is recorded and judged like any other statement.

**The rule** (``refusal``): a statement fails if it takes a writer's row lock ``FOR UPDATE``, not
``FOR NO KEY UPDATE``, and names ``glow_persistence_appaccount``, unless each of its ``FOR UPDATE``
clauses is ``FOR UPDATE OF`` a list of names none of which is that table or an alias the statement
gives it. A lock clause it cannot read that way fails too: ``FOR UPDATE`` with no ``OF``; an ``OF``
name that is not a table the statement names after ``FROM`` or ``JOIN``, or that table's alias
(a sub-query's alias, a ``WITH`` query's name, a schema-qualified name), or a table that is not one
of the models' tables (a view); or text after the clause that is not another lock clause. Comments
are read as spaces, and case is ignored.

**The database's own objects:** a lock taken inside a database function, a view or a rule is not in
any statement's text, so the check also counts the functions, procedures, views and rules the
migrated database defines outside the system schemas and extensions; the suite fails unless each is
zero (no migration defines one).

The check runs before the suite's verdict. It prints counts, and each failing statement's text with
its reason, never a parameter: Django sends parameters apart from the text, and a ``callproc``
argument is rendered as ``%s``.

**The windows** (Stage B's item 1, DM-69): ``window`` lets a case read every statement the record
saw while it ran, with its source, thread and connection, so ``pages.one_snapshot_statements``
checks that no statement went out on another connection, from another thread or through the
driver itself while a page ran.

**What it does not see** (the proof README's "Limits"): a statement sent below psycopg's cursors
(libpq's own connection object, ``connection.connection.pgconn.exec_(...)``), on a connection the
process opens without Django (``psycopg.connect``), or through an asynchronous cursor; and a
statement a case never runs.
"""

from __future__ import annotations

import re
import threading
from collections import Counter
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

ACCOUNT_TABLE = "glow_persistence_appaccount"
DJANGO = "django"
DRIVER = "driver"

_COMMENT = re.compile(r"/\*.*?\*/|--[^\n]*", re.S)
_FOR_UPDATE = re.compile(r"\bFOR\s+UPDATE\b", re.I)
_WRITER_LOCK = re.compile(r"\bFOR\s+(?:NO\s+KEY\s+)?UPDATE\b", re.I)
_NO_KEY = re.compile(r"\bFOR\s+NO\s+KEY\s+UPDATE\b", re.I)
_NAMES_ACCOUNT = re.compile(r"\bglow_persistence_appaccount\b", re.I)
_LOCK_CLAUSE = re.compile(r"FOR\s+(?:UPDATE|NO\s+KEY\s+UPDATE|SHARE|KEY\s+SHARE)\b", re.I)
_IDENT = r'(?:"(?:[^"]|"")+"|[A-Za-z_][A-Za-z0-9_$]*)'
_OF_LIST = re.compile(
    rf"\s+OF\s+({_IDENT}(?:\s*,\s*{_IDENT})*)(?:\s+(?:NOWAIT|SKIP\s+LOCKED))?(?=\s|;|$)", re.I
)
_ONE_IDENT = re.compile(_IDENT)
_FROM_ITEM = re.compile(
    rf"\b(?:FROM|JOIN)\s+(?:ONLY\s+)?({_IDENT})(?!\s*\.)(?:\s+(?:AS\s+)?({_IDENT}))?", re.I
)
_CTE = re.compile(
    rf"(?:\bWITH(?:\s+RECURSIVE)?|,)\s*({_IDENT})\s*(?:\([^)]*\)\s*)?AS\s+"
    r"(?:NOT\s+)?(?:MATERIALIZED\s+)?\(",
    re.I,
)
_KEYWORDS = frozenset(
    {
        "and",
        "as",
        "cross",
        "except",
        "fetch",
        "for",
        "from",
        "full",
        "group",
        "having",
        "inner",
        "intersect",
        "join",
        "lateral",
        "left",
        "limit",
        "natural",
        "offset",
        "on",
        "or",
        "order",
        "outer",
        "returning",
        "right",
        "set",
        "tablesample",
        "union",
        "using",
        "values",
        "where",
        "window",
    }
)

OWN_OBJECTS = """
SELECT
  (SELECT count(*) FROM pg_catalog.pg_proc p
     JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname <> 'information_schema' AND n.nspname NOT LIKE 'pg\\_%'
      AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend d
                       WHERE d.classid = 'pg_catalog.pg_proc'::regclass
                         AND d.objid = p.oid AND d.deptype = 'e')),
  (SELECT count(*) FROM pg_catalog.pg_class c
     JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('v', 'm')
      AND n.nspname <> 'information_schema' AND n.nspname NOT LIKE 'pg\\_%'),
  (SELECT count(*) FROM pg_catalog.pg_rewrite r
     JOIN pg_catalog.pg_class c ON c.oid = r.ev_class
     JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE r.rulename <> '_RETURN'
      AND n.nspname <> 'information_schema' AND n.nspname NOT LIKE 'pg\\_%')
"""


def _name(identifier: str) -> str:
    """An identifier as PostgreSQL reads it: a quoted one as written, an unquoted one in lower
    case."""
    if identifier.startswith('"'):
        return identifier[1:-1].replace('""', '"')
    return identifier.lower()


def refusal(sql: str, tables: frozenset[str] = frozenset()) -> str | None:
    """Why ``sql`` fails D14's rule, or ``None``. ``tables`` is the models' tables; when it is
    given, an ``OF`` name must resolve to one of them."""
    text = _COMMENT.sub(" ", sql)
    if _FOR_UPDATE.search(text) is None or _NAMES_ACCOUNT.search(text) is None:
        return None
    relations: dict[str, set[str]] = {}
    for item in _FROM_ITEM.finditer(text):
        relation = _name(item.group(1))
        relations.setdefault(relation, set()).add(relation)
        alias = item.group(2)
        if alias is not None and _name(alias) not in _KEYWORDS:
            relations.setdefault(_name(alias), set()).add(relation)
    queries = {_name(found.group(1)) for found in _CTE.finditer(text)}
    for clause in _FOR_UPDATE.finditer(text):
        rest = text[clause.end() :]
        listed = _OF_LIST.match(rest)
        if listed is None:
            return "FOR UPDATE with no OF list it can read"
        after = rest[listed.end() :].strip().rstrip(";").strip()
        if after and _LOCK_CLAUSE.match(after) is None:
            return "text after the lock clause that is not another lock clause"
        for name in (_name(found) for found in _ONE_IDENT.findall(listed.group(1))):
            if name in queries:
                return "FOR UPDATE OF a WITH query"
            named = relations.get(name)
            if not named:
                return "FOR UPDATE OF a name the statement gives no table"
            if ACCOUNT_TABLE in named:
                return "FOR UPDATE OF the account table or an alias it is given"
            if tables and not named <= tables:
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
        reason = refusal(text, self._model_tables())
        clean = _COMMENT.sub(" ", text)
        writer = _WRITER_LOCK.search(clean) is not None
        account = writer and _NAMES_ACCOUNT.search(clean) is not None
        with self._lock:
            self._counts["statements"] += 1
            self._counts[source] += 1
            self._connections.add((thread, id(connection)))
            self._threads.add(thread)
            if writer:
                self._counts["writer_locks"] += 1
            if account:
                self._counts["account_writer_locks"] += 1
                if reason is None and _FOR_UPDATE.search(clean) is None:
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
