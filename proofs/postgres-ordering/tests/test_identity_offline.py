"""The identity suite's offline checks (SV1; its brief's D2, D10 and acceptance checks 4 and 12).

No database: the key files' refusals, the identity settings' refusals and values, the schema
check on constructed bodies, the case plan, the secret ledger and the output capture. The cases
themselves run in the Database proof checks job, on the second disposable database.
"""

from __future__ import annotations

import ast
import copy
import importlib
import logging
import os
import secrets
import stat
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from glow_ordering_proof import environment, identity_cases, identity_environment, schema_check
from glow_ordering_proof.identity_support import OutputCapture, SecretLedger

REPO_ROOT = Path(__file__).resolve().parents[3]


def pem(key: Any) -> str:
    return str(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode("ascii")
    )


class KeyFiles:
    """Two key files made for the test, readable only by their owner, removed afterwards."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.secret_key = secrets.token_hex(32)
        self.jwt_key = pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
        self.secret_path = self.write("secret-key", self.secret_key)
        self.jwt_path = self.write("jwt-private-key.pem", self.jwt_key)

    def write(self, name: str, text: str, mode: int = 0o600) -> str:
        path = self.root / name
        path.write_text(text, encoding="ascii")
        path.chmod(mode)
        return str(path)

    def environ(self) -> dict[str, str]:
        return {
            identity_environment.SECRET_KEY_FILE: self.secret_path,
            identity_environment.JWT_KEY_FILE: self.jwt_path,
        }

    def close(self) -> None:
        self.directory.cleanup()


class IdentityKeyFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = KeyFiles()

    def tearDown(self) -> None:
        self.files.close()

    def test_generated_keys_are_read(self) -> None:
        environ = self.files.environ()
        self.assertEqual(identity_environment.secret_key(environ), self.files.secret_key)
        self.assertEqual(identity_environment.jwt_private_key(environ), self.files.jwt_key)

    def test_each_refusal_names_the_variable_and_no_value(self) -> None:
        name_secret = identity_environment.SECRET_KEY_FILE
        name_jwt = identity_environment.JWT_KEY_FILE
        weak_rsa = pem(rsa.generate_private_key(public_exponent=65537, key_size=1024))
        ec_key = pem(ec.generate_private_key(ec.SECP256R1()))
        cases = [
            ({}, name_secret, identity_environment.secret_key),
            ({name_secret: "relative/secret"}, name_secret, identity_environment.secret_key),
            (
                {name_secret: str(self.files.root / "absent")},
                name_secret,
                identity_environment.secret_key,
            ),
            ({name_secret: str(self.files.root)}, name_secret, identity_environment.secret_key),
            (
                {name_secret: self.files.write("readable", secrets.token_hex(32), 0o644)},
                name_secret,
                identity_environment.secret_key,
            ),
            (
                {name_secret: self.files.write("short", "x" * 20)},
                name_secret,
                identity_environment.secret_key,
            ),
            (
                {
                    name_secret: self.files.write(
                        "placeholder", identity_environment.PLACEHOLDER_SECRET_KEY * 2
                    )
                },
                name_secret,
                identity_environment.secret_key,
            ),
            (
                {name_secret: self.files.write("spaced", "ab cd " * 20)},
                name_secret,
                identity_environment.secret_key,
            ),
            (
                {name_jwt: self.files.write("weak.pem", weak_rsa)},
                name_jwt,
                identity_environment.jwt_private_key,
            ),
            (
                {name_jwt: self.files.write("ec.pem", ec_key)},
                name_jwt,
                identity_environment.jwt_private_key,
            ),
            (
                {name_jwt: self.files.write("junk.pem", "not a key " * 10)},
                name_jwt,
                identity_environment.jwt_private_key,
            ),
            ({}, name_jwt, identity_environment.jwt_private_key),
        ]
        for environ, name, read in cases:
            with self.subTest(name=name, environ=sorted(environ)):
                with self.assertRaises(identity_environment.RefusedSecret) as raised:
                    read(environ)
                message = str(raised.exception)
                self.assertIn(name, message)
                for value in environ.values():
                    self.assertNotIn(value, message)

    def test_pem_body_lines_are_the_base64_lines(self) -> None:
        lines = identity_environment.pem_body_lines(self.files.jwt_key)
        self.assertTrue(lines)
        for line in lines:
            self.assertNotIn("-----", line)
            self.assertIn(line, self.files.jwt_key)


GOOD = {
    environment.HOST: "127.0.0.1",
    environment.PORT: "5433",
    environment.NAME: "glow_identity_proof",
    environment.USER: "glow_proof",
    environment.PASSFILE: "/tmp/example/passfile",
    environment.MARKER: secrets.token_hex(16),
    "PATH": "/x",
    "HOME": "/h",
    "LANG": "C.UTF-8",
}


class IdentitySettingsModuleTests(unittest.TestCase):
    """The identity settings refuse at import, as the proof's settings do, and then take the
    identity fragment and the two keys from their files."""

    def setUp(self) -> None:
        self.files = KeyFiles()

    def tearDown(self) -> None:
        self.files.close()

    def import_settings(self, environ: dict[str, str]) -> Any:
        saved = dict(os.environ)
        sys.modules.pop("glow_ordering_proof.identity_settings", None)
        try:
            os.environ.clear()
            os.environ.update(environ)
            return importlib.import_module("glow_ordering_proof.identity_settings")
        finally:
            os.environ.clear()
            os.environ.update(saved)
            sys.modules.pop("glow_ordering_proof.identity_settings", None)

    def test_the_settings_load_with_the_proof_variables_and_the_key_files(self) -> None:
        settings = self.import_settings({**GOOD, **self.files.environ()})
        self.assertEqual(settings.SECRET_KEY, self.files.secret_key)
        self.assertEqual(settings.HEADLESS_JWT_PRIVATE_KEY, self.files.jwt_key)
        self.assertEqual(settings.INSTALLED_APPS[-1], "glow_ordering_proof.apps.ProofConfig")
        for app in (
            "django.contrib.sessions",
            "allauth",
            "allauth.account",
            "allauth.headless",
            "allauth.usersessions",
            "glow_identity.apps.IdentityConfig",
            "glow_persistence.apps.PersistenceDesignConfig",
        ):
            self.assertIn(app, settings.INSTALLED_APPS)
        self.assertEqual(settings.ROOT_URLCONF, "glow_identity.urls")
        database = settings.DATABASES["default"]
        self.assertIs(database["ATOMIC_REQUESTS"], False)
        self.assertEqual(database["NAME"], "glow_identity_proof")
        self.assertNotIn("PASSWORD", database)
        from psycopg import IsolationLevel

        self.assertIs(database["OPTIONS"]["isolation_level"], IsolationLevel.READ_COMMITTED)
        self.assertEqual(settings.ALLOWED_HOSTS, ["testserver"])
        self.assertNotEqual(settings.SECRET_KEY, identity_environment.PLACEHOLDER_SECRET_KEY)

    def test_the_settings_refuse_what_the_proofs_settings_refuse(self) -> None:
        files = self.files.environ()
        with self.assertRaises(environment.RefusedEnvironment):
            self.import_settings({**GOOD, **files, "PGPASSWORD": "x"})
        with self.assertRaises(environment.RefusedEnvironment):
            self.import_settings({**GOOD, **files, "DATABASE_URL": "postgres://x"})
        with self.assertRaises(environment.RefusedConnection):
            self.import_settings({**GOOD, **files, environment.HOST: "db.example.internal"})
        bad_marker = {**GOOD, **files}
        bad_marker[environment.MARKER] = "short"
        with self.assertRaises(environment.RefusedConnection):
            self.import_settings(bad_marker)

    def test_the_settings_refuse_a_missing_key_file(self) -> None:
        for name in identity_environment.IDENTITY_NAMES:
            with self.subTest(name=name):
                environ = {**GOOD, **self.files.environ()}
                del environ[name]
                with self.assertRaises(identity_environment.RefusedSecret):
                    self.import_settings(environ)

    def test_the_settings_never_import_the_api_settings(self) -> None:
        path = REPO_ROOT / "proofs/postgres-ordering/glow_ordering_proof/identity_settings.py"
        source = path.read_text(encoding="utf-8")
        imported: list[str] = []
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        for module in imported:
            self.assertFalse(module.startswith("glow_api"), module)
            self.assertNotIn("static_settings", module)


def account_access_body() -> dict[str, Any]:
    return {
        "contract_version": "gapp-api-v1",
        "request_id": str(uuid.uuid4()),
        "data": {
            "kind": "account_access",
            "account_id": str(uuid.uuid4()),
            "version": 2,
            "state": "active",
            "session_state": "valid",
        },
    }


class SchemaCheckTests(unittest.TestCase):
    def test_a_served_body_validates(self) -> None:
        self.assertEqual(schema_check.check("AppResponse", account_access_body()), [])
        error = {
            "contract_version": "gapp-api-v1",
            "request_id": str(uuid.uuid4()),
            "code": "unauthenticated",
            "retryable": False,
        }
        self.assertEqual(schema_check.check("Error", error), [])

    def test_each_defect_is_found(self) -> None:
        defects: list[tuple[str, Any]] = [
            ("data.version", 0),
            ("data.version", True),
            ("data.version", 9007199254740992),
            ("data.state", "verified"),
            ("data.session_state", "current"),
            ("data.account_id", "not-a-uuid"),
            ("data.account_id", str(uuid.uuid4()).upper()),
            ("data.account_id", str(uuid.uuid4()) + "\n"),
            ("data.kind", "account"),
            ("contract_version", "gapp-api-v2"),
            ("request_id", "x"),
        ]
        for path, value in defects:
            with self.subTest(path=path, value=value):
                body = account_access_body()
                parent: Any = body
                *parents, leaf = path.split(".")
                for key in parents:
                    parent = parent[key]
                parent[leaf] = value
                self.assertTrue(schema_check.check("AppResponse", body))
        missing = account_access_body()
        del missing["data"]["session_state"]
        self.assertTrue(schema_check.check("AppResponse", missing))
        extra = account_access_body()
        extra["data"]["email"] = "someone@example.invalid"
        self.assertTrue(schema_check.check("AppResponse", extra))
        surrogate = account_access_body()
        surrogate["data"]["state"] = "active\ud800"
        self.assertTrue(schema_check.check("AppResponse", surrogate))

    def test_an_unknown_keyword_is_an_error_not_a_pass(self) -> None:
        root = copy.deepcopy(schema_check.load_schema())
        root["$defs"]["AccountAccess"]["properties"]["version"]["multipleOf"] = 2
        with self.assertRaises(schema_check.UnsupportedSchema):
            schema_check.check("AppResponse", account_access_body(), root)


class IdentityPlanTests(unittest.TestCase):
    def test_the_plan_covers_every_acceptance_check(self) -> None:
        plan = identity_cases.plan()
        self.assertEqual(len(plan), len(set(plan)))
        covered = {check for case in identity_cases.CASES for check in case.checks}
        for check in [str(n) for n in range(1, 12)]:
            with self.subTest(check=check):
                self.assertIn(check, covered)
        # Acceptance check 12 is the run's own scan, after every case (identity_suite).
        self.assertEqual(plan[-1], "mail.no_link_no_stranger")
        self.assertEqual(len(identity_cases.EXPECTED_ROUTES), 18)

    def test_the_unauthenticated_table_has_each_route(self) -> None:
        paths = {path for _, path, _, _ in identity_cases.UNAUTHENTICATED}
        served = {"/" + route for route in identity_cases.EXPECTED_ROUTES}
        self.assertEqual(paths, served)


class LedgerAndCaptureTests(unittest.TestCase):
    def test_the_ledger_holds_tokens_their_parts_and_codes(self) -> None:
        ledger = SecretLedger()
        token = "aaaaaaaaaaaaaaaaaaaa.bbbbbbbbbbbbbbbbbbbbbbbb.cccccccccccccccccccc"
        ledger.add(token)
        ledger.add("BCDF-GHJK")
        ledger.add("short")
        self.assertEqual(ledger.found_in("x bbbbbbbbbbbbbbbbbbbbbbbb x"), 1)
        self.assertEqual(ledger.found_in("code BCDFGHJK"), 1)
        self.assertEqual(ledger.found_in("short"), 0)
        self.assertEqual(ledger.found_in("nothing here"), 0)

    def test_the_capture_reads_debug_records_and_writes(self) -> None:
        capture = OutputCapture()
        capture.install()
        try:
            logging.getLogger("glow_identity.test").debug("a debug line")
            print("a printed line")
        finally:
            capture.uninstall()
        self.assertIn("a debug line", capture.text())
        self.assertIn("a printed line", capture.text())
        self.assertNotIn(capture._handler, logging.getLogger().handlers)
        self.assertEqual(stat.S_IMODE(0o600), 0o600)


if __name__ == "__main__":
    unittest.main()
