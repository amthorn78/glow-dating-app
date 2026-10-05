"""The proof package as an installed app, for one reason: its ``dbshell`` command
replaces Django's under the proof's settings (P06.DB's carried item 6; DM-12).

Django resolves a management command name to the installed app that provides it before
Django's own commands, so every way of reaching ``dbshell`` under these settings
(``python -m django dbshell``, ``django-admin dbshell``, ``call_command("dbshell")``)
loads the proof's command, which refuses. The app has no models and no migrations.
"""

from django.apps import AppConfig


class ProofConfig(AppConfig):  # type: ignore[misc]
    name = "glow_ordering_proof"
    verbose_name = "P06.DB ordering proof (management commands only; no models)"
