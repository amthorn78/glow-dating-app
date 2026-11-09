"""The identity suite's offline checks (SV1; its brief's D2, D10 and acceptance checks 4 and 12).

No database: the key files' refusals, the identity settings' refusals and values, the schema
check on constructed bodies, the case plan, the secret ledger and the output capture. The cases
themselves run in the Database proof checks job, on the second disposable database.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import importlib
import io
import json
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

from glow_ordering_proof import (
    environment,
    identity_cases,
    identity_environment,
    identity_scan,
    schema_check,
)
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
        # Acceptance checks 1 to 11, and 13 (correction C1).
        for check in [*(str(n) for n in range(1, 12)), "13"]:
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


class JobDirectory:
    """A job directory as the credentials step writes it, with synthetic values only."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.values: dict[str, str] = {}
        for name in identity_scan.VALUE_FILES:
            self.values[name] = secrets.token_hex(24)
            self.write(name, self.values[name] + "\n")
        self.role_password = secrets.token_hex(24)
        self.write(
            identity_scan.PASSFILE,
            f"127.0.0.1:5433:glow_proof:glow_proof:{self.role_password}\n"
            f"127.0.0.1:5433:glow_identity_proof:glow_proof:{self.role_password}\n",
        )
        self.pem = pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
        self.write(identity_scan.JWT_KEY_FILE, self.pem)
        self.pem_line = [line for line in self.pem.splitlines() if not line.startswith("---")][3]
        self.log = self.write("identity.log", "[identity] PASS a.case\n")
        self.results = self.root / "identity-results.json"
        self.results.write_text(json.dumps({"cases": [{"detail": "ok"}]}), encoding="utf-8")

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="ascii")
        path.chmod(0o600)
        return path

    def clean_log(self, extra: str = "") -> None:
        self.write(
            "identity.log",
            "[identity] PASS a.case\n" + extra + "identity secret scan: clean (1 secrets held)\n",
        )

    def every_value(self) -> list[str]:
        return [*self.values.values(), self.role_password, self.pem_line]

    def run(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = identity_scan.main([str(self.root), str(self.log), str(self.results)])
        return status, out.getvalue()

    def close(self) -> None:
        self.directory.cleanup()


class IdentityScanTests(unittest.TestCase):
    """Correction C1 (DM-47 C1.4): the job's check scans the log and the results JSON with the
    same values, and leaves nothing to upload after a refusal."""

    def setUp(self) -> None:
        self.job = JobDirectory()

    def tearDown(self) -> None:
        self.job.close()

    def assert_no_value_printed(self, printed: str) -> None:
        for value in self.job.every_value():
            self.assertNotIn(value, printed)

    def test_the_values_are_the_job_files(self) -> None:
        values = identity_scan.job_values(self.job.root)
        for value in self.job.every_value():
            self.assertIn(value, values)
        self.assertNotIn("", values)
        self.assertFalse(any(value.startswith("-----") for value in values))

    def test_clean_output_passes_and_keeps_the_json(self) -> None:
        self.job.clean_log()
        status, printed = self.job.run()
        self.assertEqual(status, identity_scan.PASSED, printed)
        self.assertTrue(self.job.results.exists())
        self.assertIn("found in the identity results JSON: 0", printed)

    def test_a_value_in_the_json_only_is_refused_and_the_json_removed(self) -> None:
        self.job.clean_log()
        for value in self.job.every_value():
            with self.subTest(value=len(value)):
                self.job.results.write_text(
                    json.dumps({"server": {"planted": value}}), encoding="utf-8"
                )
                status, printed = self.job.run()
                self.assertEqual(status, identity_scan.REFUSED)
                self.assertFalse(self.job.results.exists())
                # The role's password is in the passfile twice, so it counts twice.
                self.assertRegex(printed, r"found in the identity results JSON: [12]\n")
                self.assertIn("removed; nothing to upload", printed)
                self.assert_no_value_printed(printed)

    def test_a_value_escaped_by_json_is_found(self) -> None:
        self.job.clean_log()
        value = self.job.values["marker"]
        escaped = "".join(f"\\u{ord(c):04x}" for c in value)
        self.job.results.write_text('{"detail": "' + escaped + '"}', encoding="utf-8")
        self.assertNotIn(value, self.job.results.read_text(encoding="utf-8"))
        status, printed = self.job.run()
        self.assertEqual(status, identity_scan.REFUSED)
        self.assertFalse(self.job.results.exists())

    def test_a_value_in_the_log_is_refused_and_the_json_removed(self) -> None:
        self.job.clean_log(extra=self.job.values["identity-secret-key"] + "\n")
        status, printed = self.job.run()
        self.assertEqual(status, identity_scan.REFUSED)
        self.assertFalse(self.job.results.exists())
        self.assertIn("found in the identity suite's output: 1", printed)
        self.assert_no_value_printed(printed)

    def test_no_clean_line_from_the_suite_is_refused(self) -> None:
        status, printed = self.job.run()  # the log has no "identity secret scan: clean"
        self.assertEqual(status, identity_scan.REFUSED)
        self.assertFalse(self.job.results.exists())
        self.assertIn("reported clean: False", printed)

    def test_an_absent_json_is_nothing_to_upload(self) -> None:
        self.job.clean_log()
        self.job.results.unlink()
        status, printed = self.job.run()
        self.assertEqual(status, identity_scan.PASSED)
        self.assertIn("absent: nothing to scan or upload", printed)

    def test_an_unreadable_secret_file_is_refused(self) -> None:
        self.job.clean_log()
        (self.job.root / identity_scan.PASSFILE).unlink()
        status, printed = self.job.run()
        self.assertEqual(status, identity_scan.REFUSED)
        self.assertFalse(self.job.results.exists())
        self.assertIn("could not run", printed)

    def test_the_module_imports_only_the_standard_library(self) -> None:
        tree = ast.parse(Path(identity_scan.__file__).read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertLessEqual(
            imported,
            {"__future__", "collections", "dataclasses", "json", "pathlib", "sys", "typing"},
        )


def workflow_step(name_prefix: str) -> str:
    """The text of the Database proof checks job's step whose name starts with the prefix."""
    lines = (REPO_ROOT / ".github" / "workflows" / "foundation.yml").read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("      - ")]
    for index, start in enumerate(starts):
        if f'name: "{name_prefix}' in lines[start]:
            end = starts[index + 1] if index + 1 < len(starts) else len(lines)
            return "\n".join(lines[start:end])
    raise AssertionError(f"no step named {name_prefix!r}")


class IdentityUploadGateTests(unittest.TestCase):
    """Correction C1: the results JSON is uploaded only after the job's check has passed."""

    def test_the_suite_step_runs_the_check_and_sets_the_output_only_on_a_pass(self) -> None:
        step = workflow_step("SV1: run the identity suite")
        self.assertIn("        id: identity\n", step)
        self.assertIn(
            'python -m glow_ordering_proof.identity_scan "$DIR" "$DIR/identity.log"'
            " .work/identity-results.json",
            step,
        )
        passed = step.index('if [ "$scan" -eq 0 ]; then')
        withheld = step.index("else", passed)
        output = step.index('echo "scan=passed" >> "$GITHUB_OUTPUT"')
        self.assertTrue(passed < output < withheld)
        self.assertEqual(step.count("scan=passed"), 1)

    def test_the_upload_waits_for_the_check(self) -> None:
        step = workflow_step("SV1: save the identity suite's results JSON")
        self.assertIn(
            "        if: ${{ always() && steps.identity.outputs.scan == 'passed' }}\n", step
        )
        self.assertNotIn("if: always()\n", step)
        self.assertIn("path: proofs/postgres-ordering/.work/identity-results.json", step)


if __name__ == "__main__":
    unittest.main()
