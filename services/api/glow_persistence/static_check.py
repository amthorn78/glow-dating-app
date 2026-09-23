"""Inspect migration state with no connection, schema editor or executor.

Run with GLOW_ENV=test python -m glow_persistence.static_check. This intentionally
avoids makemigrations: its history checks can ask a database about migration state.
"""

import os
from contextlib import ExitStack, contextmanager
from unittest.mock import patch


@contextmanager
def no_database_access():
    """Allow dummy backend metadata, reject connection/cursor/schema operations."""
    with ExitStack() as stack:
        for method in ("connect", "ensure_connection", "cursor", "schema_editor"):
            stack.enter_context(
                patch(
                    f"django.db.backends.base.base.BaseDatabaseWrapper.{method}",
                    side_effect=AssertionError("P02 static review cannot access a database"),
                )
            )
        stack.enter_context(
            patch(
                "socket.create_connection",
                side_effect=AssertionError("Static review cannot use network"),
            )
        )
        yield


def setup_static_registry():
    import django
    from django.conf import settings

    if settings.configured:
        raise RuntimeError("Use a fresh process for the isolated static model registry")
    os.environ["DJANGO_SETTINGS_MODULE"] = "glow_persistence.static_settings"
    django.setup()


def inspect_definitions():
    from django.apps import apps
    from django.db.migrations.autodetector import MigrationAutodetector
    from django.db.migrations.loader import MigrationLoader
    from django.db.migrations.state import ProjectState

    config = apps.get_app_config("glow_persistence")
    problems = [error for model in config.get_models() for error in model.check(databases=[])]
    if problems:
        raise AssertionError(
            "Model definition errors: " + ", ".join(str(item) for item in problems)
        )
    # Pinned Django source inspected: None skips the MigrationRecorder entirely.
    loader = MigrationLoader(connection=None)
    target = ProjectState.from_apps(apps)
    changes = MigrationAutodetector(loader.project_state(), target).changes(
        graph=loader.graph, trim_to_apps={"glow_persistence"}
    )
    if changes:
        raise AssertionError("Committed migration state differs from model definitions")
    return loader, target


def main():
    with no_database_access():
        setup_static_registry()
        loader, target = inspect_definitions()
        model_count = sum(label == "glow_persistence" for label, _ in target.models)
        migrations = sorted(
            name for label, name in loader.disk_migrations if label == "glow_persistence"
        )
        print(
            f"Static definitions agree: {model_count} app models; migrations={','.join(migrations)}"
        )
        print("No SQL, connection, migration execution, authentication or concurrency proof.")


if __name__ == "__main__":
    main()
