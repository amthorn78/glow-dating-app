"""``notification_sweeps``: SV4 B2's sweeps, once (its brief's D24; ``glow_notifications.sweeps``).

Sealed until integration, as every command is until P11: it exists only where ``glow_notifications``
is installed, which only the disposable-database proof's chat settings do; the served runtime
installs no ``glow_notifications``, so its command list holds none of it (a seal test proves it). It
needs the token store's factory, which only those settings name, and refuses without it
(``provider_unavailable``). It prints counts only, never a token, a reference or an installation.
SV5 schedules it.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from glow_notifications.delivery import ProviderUnavailable
from glow_notifications.sweeps import SweepReport, run_sweeps


class Command(BaseCommand):  # type: ignore[misc]
    help = "Run SV4 B2's notification sweeps once (sealed; the proof's chat settings only)."

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            report: SweepReport = run_sweeps()
        except ProviderUnavailable as refused:
            raise CommandError(str(refused)) from None
        counts = ", ".join(f"{name} {value}" for name, value in asdict(report).items())
        self.stdout.write(f"notification sweeps: {counts}")
