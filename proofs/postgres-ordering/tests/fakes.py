"""Offline stand-ins for Django's connection: no database is opened."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from typing import Any

_EQUALS = re.compile(r"\b(?:\w+\.)?(\w+) = %s")


class FilteringCursor:
    """Answers a SELECT over constructed rows by applying the query's own ``column = %s``
    conditions, in order, with its parameters. A condition the query leaves out is not
    applied, so a query that forgets a filter returns the rows it would have read."""

    def __init__(self, rows: Sequence[dict[str, Any]], columns: Sequence[str]) -> None:
        self.rows = rows
        self.columns = columns
        self.executed: list[tuple[str, list[object]]] = []
        self._result: list[tuple[Any, ...]] = []

    def execute(self, sql: str, params: Sequence[object] | None = None) -> None:
        params = list(params or [])
        self.executed.append((sql, params))
        where = sql.split("WHERE", 1)[1] if "WHERE" in sql else ""
        names = _EQUALS.findall(where)
        if len(names) != len(params):
            raise AssertionError(f"{len(names)} conditions for {len(params)} parameters")
        conditions = dict(zip(names, params, strict=True))
        self._result = [
            tuple(row[c] for c in self.columns)
            for row in self.rows
            if all(row.get(name) == value for name, value in conditions.items())
            and not ("kind <> 'sign_in'" in where and row.get("kind") == "sign_in")
        ]

    def fetchall(self) -> list[tuple[Any, ...]]:
        return list(self._result)


class ScriptedCursor:
    """Returns one scripted row per ``execute``, from a callable given the SQL."""

    def __init__(self, answer: Callable[[str, list[object]], tuple[Any, ...] | None]) -> None:
        self.answer = answer
        self.executed: list[tuple[str, list[object]]] = []
        self._row: tuple[Any, ...] | None = None

    def execute(self, sql: str, params: Sequence[object] | None = None) -> None:
        self.executed.append((sql, list(params or [])))
        self._row = self.answer(sql, list(params or []))

    def fetchone(self) -> tuple[Any, ...] | None:
        return self._row


class FakeConnection:
    """A stand-in for ``django.db.connection`` whose cursor is the given object."""

    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor

    @contextmanager
    def _context(self) -> Iterator[Any]:
        yield self._cursor

    def cursor(self) -> Any:
        return self._context()
