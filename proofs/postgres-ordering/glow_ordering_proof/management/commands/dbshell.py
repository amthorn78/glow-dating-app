"""``dbshell`` under the proof's settings: refused (P06.DB's carried item 6; DM-12).

Django's own ``dbshell`` starts ``psql`` as a separate program with the proof's
connection options, outside Django's connection path, so the run's marker is never
checked for it. This command replaces it and refuses before anything connects: it opens
no connection and starts no client, so no command under the proof's settings reaches a
database unchecked. The refusal is the marker's ``RefusedDatabase``, naming
``PROOF_DB_MARKER`` and no value.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from glow_ordering_proof import marker


class Command(BaseCommand):  # type: ignore[misc]
    help = "Refused under the proof's settings: dbshell bypasses the run's marker check."
    requires_system_checks: list[str] = []

    def add_arguments(self, parser: ArgumentParser) -> None:
        # Django's own options, accepted so that any invocation reaches the refusal.
        parser.add_argument("--database", default="default")
        parser.add_argument("parameters", nargs="*")

    def handle(self, *args: Any, **options: Any) -> None:
        raise marker.refuse_dbshell()
