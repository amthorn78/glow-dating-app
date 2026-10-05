"""Runs one proof command with Django's real connection path and a fake server.

Used by ``tests/test_marker_commands.py`` in a subprocess, so the proof's settings and
Django's setup stay out of the test process. Only the backend's driver-facing methods
are replaced (opening the driver connection, autocommit, session settings, cursor
creation and closing); Django's own ``connect()``, its ``connection_created`` signal,
the receiver the proof's settings register, ``cursor()`` and every command are real.

The fake server answers the marker query with the row in ``HARNESS_ROW`` (JSON: a
``[pid, comment]`` pair, or ``null`` for no row) and raises ``HarnessStop`` on any other
statement, so a command that passes the check stops at its first real statement. What
ran is written to ``HARNESS_RECORD`` as JSON before the command's outcome propagates::

    python -m tests.command_harness migrate
    python -m tests.command_harness makemigrations --check --dry-run
    python -m tests.command_harness proof facts
    python -m tests.command_harness proof run --seed 1
    python -m tests.command_harness dbshell

``dbshell`` would start ``psql`` through the backend's client; the harness replaces the
client's ``runshell`` and records whether it was reached (``shell_started``).
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from glow_ordering_proof import marker


class HarnessStop(Exception):
    """The fake server received a statement other than the marker query."""


STATEMENTS: list[str] = []
CLOSED: list[int] = []
SHELLS: list[int] = []


class FakeServerCursor:
    def __init__(self, row: tuple[Any, ...] | None) -> None:
        self.row = row

    def execute(self, sql: object, params: object = None) -> None:
        text = str(sql)
        STATEMENTS.append(text)
        if text != marker.QUERY:
            raise HarnessStop("the fake server stops at the first statement after the check")

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.row

    def close(self) -> None:
        pass


def install_fake_server(row: tuple[Any, ...] | None) -> None:
    from django.db.backends.postgresql.base import DatabaseWrapper

    def get_new_connection(self: Any, conn_params: object) -> object:
        return object()

    def set_autocommit(self: Any, autocommit: bool) -> None:
        pass

    def init_connection_state(self: Any) -> None:
        pass

    def create_cursor(self: Any, name: object = None) -> FakeServerCursor:
        return FakeServerCursor(row)

    def close(self: Any) -> None:
        CLOSED.append(1)

    def runshell(self: Any, parameters: object) -> None:
        # Django's own dbshell would start psql here; the harness records it instead.
        SHELLS.append(1)

    from django.db.backends.postgresql.client import DatabaseClient

    DatabaseClient.runshell = runshell
    DatabaseWrapper.get_new_connection = get_new_connection
    DatabaseWrapper._set_autocommit = set_autocommit
    DatabaseWrapper.init_connection_state = init_connection_state
    DatabaseWrapper.create_cursor = create_cursor
    DatabaseWrapper._close = close


def main(argv: list[str]) -> int:
    raw = json.loads(os.environ["HARNESS_ROW"])
    install_fake_server(None if raw is None else tuple(raw))
    record_path = os.environ["HARNESS_RECORD"]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glow_ordering_proof.settings")
    try:
        if argv[:1] == ["proof"]:
            from glow_ordering_proof.__main__ import main as proof_main

            return proof_main(argv[1:])
        from django.core.management import execute_from_command_line

        execute_from_command_line(["django", *argv])
        return 0
    finally:
        from django.db import connections

        with open(record_path, "w", encoding="utf-8") as record:
            json.dump(
                {
                    "statements": STATEMENTS,
                    "closed": len(CLOSED),
                    "kept": connections["default"].connection is not None,
                    "shell_started": bool(SHELLS),
                },
                record,
            )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
