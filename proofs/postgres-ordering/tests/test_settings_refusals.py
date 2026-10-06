"""The settings' refusals (acceptance check 4), shown without a database."""

from __future__ import annotations

import ast
import importlib
import secrets
import sys
import unittest
from pathlib import Path
from typing import Any

from glow_ordering_proof import environment

REPO_ROOT = Path(__file__).resolve().parents[3]
API_PROFILES = REPO_ROOT / "services" / "api" / "glow_api" / "configuration_profiles.py"

GOOD = {
    environment.HOST: "127.0.0.1",
    environment.PORT: "5433",
    environment.NAME: "glow_proof",
    environment.USER: "glow_proof",
    environment.PASSFILE: "/tmp/example/passfile",
    # A marker made for the test run, never a literal in the source.
    environment.MARKER: secrets.token_hex(16),
}


def api_forbidden_names() -> frozenset[str]:
    """The API's FORBIDDEN_CONNECTION_NAMES, read from its source without importing it."""
    module = ast.parse(API_PROFILES.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "FORBIDDEN_CONNECTION_NAMES" for t in node.targets
        ):
            names = ast.literal_eval(node.value.args[0])  # type: ignore[attr-defined]
            return frozenset(names)
    raise AssertionError("FORBIDDEN_CONNECTION_NAMES not found in the API's source")


class ForbiddenNameTests(unittest.TestCase):
    def test_copy_matches_the_api(self) -> None:
        self.assertEqual(environment.API_FORBIDDEN_CONNECTION_NAMES, api_forbidden_names())

    def test_each_api_name_refuses(self) -> None:
        for name in sorted(environment.API_FORBIDDEN_CONNECTION_NAMES):
            with self.subTest(name=name):
                with self.assertRaises(environment.RefusedEnvironment) as ctx:
                    environment.require_clean_environment({**GOOD, name: "x"})
                self.assertIn(name, str(ctx.exception))
                self.assertNotIn("x", str(ctx.exception).split(":")[-1].replace(name, ""))

    def test_the_named_three_refuse_even_when_empty(self) -> None:
        for name in ("DATABASE_URL", "HD_API_KEY", "GEO_API_KEY"):
            with self.subTest(name=name):
                with self.assertRaises(environment.RefusedEnvironment):
                    environment.require_clean_environment({**GOOD, name: ""})

    def test_any_pg_name_refuses(self) -> None:
        for name in ("PGPASSFILE", "PGSERVICE", "PGSERVICEFILE", "PGSSLMODE", "PGOPTIONS", "PGX"):
            with self.subTest(name=name):
                with self.assertRaises(environment.RefusedEnvironment) as ctx:
                    environment.require_clean_environment({**GOOD, name: "value"})
                self.assertIn(name, str(ctx.exception))
                self.assertNotIn("value", str(ctx.exception))

    def test_refusal_names_every_offender_and_no_value(self) -> None:
        present = environment.refused_names(
            {**GOOD, "PGHOST": "h", "DATABASE_URL": "u", "PGZ": "z"}
        )
        self.assertEqual(present, ("DATABASE_URL", "PGHOST", "PGZ"))

    def test_clean_environment_passes(self) -> None:
        environment.require_clean_environment({**GOOD, "PATH": "/x", "HOME": "/h", "LANG": "C"})
        # The proof's own names are not PG*, DATABASE_URL or GLOW_* names.
        for name in environment.PROOF_NAMES:
            self.assertFalse(name.startswith("PG"))
            self.assertFalse(name.startswith("GLOW_"))
            self.assertNotIn("DATABASE_URL", name)


class ConnectionOptionTests(unittest.TestCase):
    def test_loopback_and_socket_hosts_accepted(self) -> None:
        for host in ("127.0.0.1", "localhost", "::1", "/run/proof/sockets"):
            with self.subTest(host=host):
                options = environment.connection_options({**GOOD, environment.HOST: host})
                self.assertEqual(options.host, host)
                self.assertEqual(options.unix_socket, host.startswith("/"))

    def test_other_hosts_refused(self) -> None:
        for host in ("10.0.0.5", "db.internal", "example.com", "0.0.0.0", "", "127.0.0.2"):
            with self.subTest(host=host):
                with self.assertRaises(environment.RefusedConnection) as ctx:
                    environment.connection_options({**GOOD, environment.HOST: host})
                self.assertNotIn(host or "<empty>", str(ctx.exception))

    def test_missing_options_refused(self) -> None:
        for name in environment.PROOF_NAMES:
            with self.subTest(name=name):
                bad = dict(GOOD)
                del bad[name]
                with self.assertRaises(environment.RefusedConnection) as ctx:
                    environment.connection_options(bad)
                self.assertIn(name, str(ctx.exception))

    def test_bad_port_passfile_and_identifiers_refused(self) -> None:
        for name, value in (
            (environment.PORT, "abc"),
            (environment.PORT, "0"),
            (environment.PORT, "70000"),
            (environment.PASSFILE, "relative/passfile"),
            (environment.NAME, "glow;drop"),
            (environment.USER, ""),
        ):
            with self.subTest(name=name, value=value):
                with self.assertRaises(environment.RefusedConnection):
                    environment.connection_options({**GOOD, name: value})

    def test_django_database_is_explicit_with_passfile_and_no_service(self) -> None:
        database = environment.django_database(environment.connection_options(GOOD))
        self.assertEqual(database["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(database["HOST"], "127.0.0.1")
        self.assertEqual(database["PORT"], "5433")
        self.assertEqual(database["NAME"], "glow_proof")
        self.assertEqual(database["USER"], "glow_proof")
        options = database["OPTIONS"]
        assert isinstance(options, dict)
        self.assertEqual(options["passfile"], "/tmp/example/passfile")
        self.assertEqual(options["sslmode"], "disable")
        self.assertNotIn("service", options)
        self.assertNotIn("PASSWORD", database)
        self.assertNotIn("password", options)


class SettingsModuleTests(unittest.TestCase):
    """The settings module itself refuses at import; imported in a subprocess-free way by
    controlling os.environ around a fresh import."""

    def import_settings(self, environ: dict[str, str]) -> Any:
        import os

        saved = dict(os.environ)
        sys.modules.pop("glow_ordering_proof.settings", None)
        try:
            os.environ.clear()
            os.environ.update(environ)
            return importlib.import_module("glow_ordering_proof.settings")
        finally:
            os.environ.clear()
            os.environ.update(saved)
            sys.modules.pop("glow_ordering_proof.settings", None)

    def test_settings_refuse_a_pg_name(self) -> None:
        with self.assertRaises(environment.RefusedEnvironment):
            self.import_settings({**GOOD, "PGPASSWORD": "x", "PATH": "/x"})

    def test_settings_refuse_database_url(self) -> None:
        with self.assertRaises(environment.RefusedEnvironment):
            self.import_settings({**GOOD, "DATABASE_URL": "postgres://x", "PATH": "/x"})

    def test_settings_refuse_a_remote_host(self) -> None:
        with self.assertRaises(environment.RefusedConnection):
            self.import_settings({**GOOD, environment.HOST: "db.example.internal", "PATH": "/x"})

    def test_settings_load_with_the_proof_variables_only(self) -> None:
        settings = self.import_settings({**GOOD, "PATH": "/x", "HOME": "/h", "LANG": "C.UTF-8"})
        apps = settings.INSTALLED_APPS
        self.assertEqual(
            apps,
            [
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "glow_persistence.apps.PersistenceDesignConfig",
                "glow_ordering_proof.apps.ProofConfig",
            ],
        )
        database = settings.DATABASES["default"]
        self.assertEqual(database["OPTIONS"]["passfile"], "/tmp/example/passfile")
        from psycopg import IsolationLevel

        self.assertIs(database["OPTIONS"]["isolation_level"], IsolationLevel.READ_COMMITTED)
        self.assertEqual(settings.AUTH_USER_MODEL, "auth.User")

    def test_settings_never_import_the_api_settings(self) -> None:
        source = (REPO_ROOT / "proofs/postgres-ordering/glow_ordering_proof/settings.py").read_text(
            encoding="utf-8"
        )
        imported: list[str] = []
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertTrue(imported)
        for module in imported:
            self.assertFalse(module.startswith("glow_api"), module)
            self.assertNotIn("static_settings", module)
        self.assertNotIn("from glow_api", source)
        self.assertNotIn("import glow_api", source)


if __name__ == "__main__":
    unittest.main()
