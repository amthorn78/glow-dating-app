"""The identity suite's offline checks (SV1; its brief's D2, D10 and acceptance checks 4 and 12).

No database: the key files' refusals, the identity settings' refusals and values, the schema
check on constructed bodies, the case plan, the secret ledger and the output capture. The cases
themselves run in their own suite's job, "Database proof checks (identity)", on its own
disposable database.
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
import re
import secrets
import stat
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from glow_ordering_proof import (
    environment,
    identity_cases,
    identity_environment,
    identity_scan,
    schema_check,
)
from glow_ordering_proof.identity_support import (
    MAIL_FORBIDDEN,
    OutputCapture,
    SecretLedger,
    clock_ahead,
    mail_forbidden_found,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"


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
        # Acceptance check 11's two sentences (correction C2, DM-48 C2.3).
        self.assertIn("ratelimit.failed_sign_ins", plan)
        self.assertIn("ratelimit.password_change", plan)
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


def glow_message(template_prefix: str, code: str) -> str:
    """One of Glow's own code messages (``glow_identity.messages``), subject and body, rendered
    with the code given and allauth's timeouts, with no Django settings."""
    if str(API_ROOT) not in sys.path:
        sys.path.insert(0, str(API_ROOT))
    from glow_identity import messages

    timeouts = SimpleNamespace(
        EMAIL_VERIFICATION_BY_CODE_TIMEOUT=900, PASSWORD_RESET_BY_CODE_TIMEOUT=180
    )
    with mock.patch.object(messages, "account_settings", timeouts):
        message = messages.render(template_prefix, {"code": code})
    return str(message.subject) + "\n" + str(message.body)


CODE_MESSAGES = (
    "account/email/email_confirmation_signup",
    "account/email/email_confirmation",
    "account/email/password_reset_code",
)


class MailNoLinkCheckTests(unittest.TestCase):
    """Correction C2 (F-1; DM-48 C2.5): the no-link check removes the exact code issued, every
    occurrence, before it looks for ``http`` and ``www.``; nothing else, and no pattern."""

    def test_a_code_spelling_http_passes(self) -> None:
        for prefix in CODE_MESSAGES:
            with self.subTest(message=prefix):
                text = glow_message(prefix, "HTTP-BCDF")
                self.assertIn("HTTP-BCDF", text)
                self.assertEqual(mail_forbidden_found(text, ["HTTP-BCDF"]), [])

    def test_a_code_ending_www_before_its_full_stop_passes(self) -> None:
        for prefix in CODE_MESSAGES:
            with self.subTest(message=prefix):
                text = glow_message(prefix, "BCDF-GWWW")
                self.assertIn("BCDF-GWWW.", text)
                self.assertEqual(mail_forbidden_found(text, ["BCDF-GWWW"]), [])

    def test_a_real_link_fails(self) -> None:
        issued = ["HTTP-BCDF"]
        message = glow_message("account/email/email_confirmation_signup", "HTTP-BCDF")
        cases = {
            "an https link": (message + "\nhttps://glow.invalid/verify", ["http", "://"]),
            "a www. address": (message + "\nVisit www.glow.invalid today.", ["www."]),
            "a link holding the code": (
                message + "\nhttps://glow.invalid/HTTP-BCDF",
                ["http", "://"],
            ),
            "a code-shaped word that was not issued": (message + " HTTP-BCDG", ["http"]),
        }
        for name, (text, expected) in cases.items():
            with self.subTest(case=name):
                self.assertEqual(mail_forbidden_found(text, issued), expected)

    def test_the_forbidden_list_is_unchanged(self) -> None:
        self.assertEqual(
            MAIL_FORBIDDEN,
            ("http", "://", "www.", "href", "<a", "allauth", "django", "example.com"),
        )


class ClockAheadTests(unittest.TestCase):
    """Correction C2 (DM-48 section 3): the moved clock keeps ``monotonic`` and ``sleep``, which
    allauth's ``cache_lock`` calls, unmoved."""

    def test_only_time_moves(self) -> None:
        module = SimpleNamespace(time=time)
        with clock_ahead(module, 120):
            moved = module.time.time() - time.time()
            self.assertGreater(moved, 119)
            self.assertLess(moved, 121)
            self.assertIs(module.time.monotonic, time.monotonic)
            self.assertIs(module.time.sleep, time.sleep)
        self.assertIs(module.time, time)

    def test_allauths_limiter_runs_on_the_moved_clock(self) -> None:
        from allauth.core.internal import ratelimit

        with clock_ahead(ratelimit, 120):
            self.assertGreater(ratelimit.time.time() - time.time(), 119)
            self.assertIs(ratelimit.time.monotonic, time.monotonic)
            self.assertIs(ratelimit.time.sleep, time.sleep)
        self.assertIs(ratelimit.time, time)


WORKFLOW = REPO_ROOT / ".github" / "workflows" / "foundation.yml"


def workflow_job(job: str) -> list[str]:
    """The lines of the workflow's job with this ID, from its key to the next job's (SV4 A0: one
    database job per suite)."""
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    keys = [i for i, line in enumerate(lines) if re.fullmatch(r"  [a-z][a-z0-9-]*:", line)]
    for index, start in enumerate(keys):
        if lines[start] == f"  {job}:":
            end = keys[index + 1] if index + 1 < len(keys) else len(lines)
            return lines[start:end]
    raise AssertionError(f"no job {job!r}")


def workflow_steps(job: str) -> list[str]:
    """The text of each of the job's steps, in order, without the comment lines between steps."""
    lines = workflow_job(job)
    starts = [i for i, line in enumerate(lines) if line.startswith("      - ")]
    steps = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        steps.append("\n".join(line for line in lines[start:end] if not line.startswith("      #")))
    return steps


def step_name(step: str) -> str:
    """A step's name as the workflow writes it, unquoted; empty for a step with no name."""
    found = re.search(r"^      [- ] name: (.*)$", step, flags=re.MULTILINE)
    return found.group(1).strip('"') if found else ""


def workflow_step(job: str, name_prefix: str) -> str:
    """The text of the job's step whose name, quoted or not, starts with the prefix."""
    for step in workflow_steps(job):
        if step_name(step).startswith(name_prefix):
            return step
    raise AssertionError(f"no step named {name_prefix!r} in {job!r}")


def job_secret_files(job: str) -> set[str]:
    """Every file the job's credentials step writes into its protected directory (SV4 A0, D2),
    but the role statement, which the next step removes once it has run; its values are the
    passfile's password and the marker files'."""
    step = workflow_step(job, "Generate the disposable database's credentials")
    return set(re.findall(r'"\$dir/([A-Za-z0-9._-]+)"', step)) - {"create-role.sql"}


def job_databases(job: str) -> list[str]:
    """The databases the job's passfile names, as its credentials step writes it."""
    step = workflow_step(job, "Generate the disposable database's credentials")
    return re.findall(r"127\.0\.0\.1:5433:(\w+):glow_proof:%s", step)


def script_lines(step: str) -> list[str]:
    """A step's lines without their indentation, so that a whole line of its script is found."""
    return [line.strip() for line in step.splitlines()]


def writers(step: str, name: str) -> list[str]:
    """Each line of a credentials step that writes or appends to the file in its directory."""
    return [line for line in script_lines(step) if f'> "$dir/{name}"' in line]


PRELUDE = re.compile(
    r"(?P<generated>[a-z_]+)=\$\(python -c 'import secrets; print\(secrets\.token_hex\(\d+\)\)'\)"
    r'|echo "::add-mask::\$(?P<masked>[a-z_]+)"'
    r"|set \+x|umask 077|#.*"
)


def credentials_prelude(step: str) -> list[tuple[str, str]]:
    """What a credentials step does before its first line that can print or write: each value it
    generates ("generated", name) and each value it masks ("masked", name), in order (SV4 A0-C1).
    Only `set +x`, `umask 077`, comments, the values' generation and their masks may come first."""
    script = step.split("        run: |\n", 1)[1]
    events: list[tuple[str, str]] = []
    for line in script_lines(script):
        found = PRELUDE.fullmatch(line)
        if found is None:
            break
        for kind in ("generated", "masked"):
            if found[kind]:
                events.append((kind, found[kind]))
    return events


class JobDirectory:
    """A job directory as the identity job's credentials step writes it: every secret file it
    writes, read from the workflow (SV4 A0, D2), with synthetic values only."""

    JOB = "database-identity"

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        files = job_secret_files(self.JOB)
        keys = sorted(name for name in files if name.endswith(".pem"))
        self.values: dict[str, str] = {}
        for name in sorted(files - {identity_scan.PASSFILE, *keys}):
            self.values[name] = secrets.token_hex(24)
            self.write(name, self.values[name] + "\n")
        self.role_password = secrets.token_hex(24)
        self.write(
            identity_scan.PASSFILE,
            "".join(
                f"127.0.0.1:5433:{database}:glow_proof:{self.role_password}\n"
                for database in job_databases(self.JOB)
            ),
        )
        (key,) = keys
        self.pem = pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
        self.write(key, self.pem)
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
        # SV4 A0 (D2): the check lists every secret file its own job writes, and no other.
        listed = {*identity_scan.VALUE_FILES, identity_scan.PASSFILE, identity_scan.JWT_KEY_FILE}
        self.assertEqual(
            listed,
            {
                "identity-secret-key",
                "identity-marker",
                "marker",
                "superuser-password",
                "passfile",
                "identity-jwt-key.pem",
            },
        )
        self.assertEqual(listed, job_secret_files(JobDirectory.JOB))
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


class IdentityUploadGateTests(unittest.TestCase):
    """Correction C1: the results JSON is uploaded only after the job's check has passed, in the
    identity suite's own job since SV4 A0."""

    def test_the_suite_step_runs_the_check_and_sets_the_output_only_on_a_pass(self) -> None:
        step = workflow_step(JobDirectory.JOB, "SV1: run the identity suite")
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

    def test_after_a_failed_check_the_step_prints_counts_only(self) -> None:
        # Correction C2 (F-4; D10, DM-48 C2.6): the failed branch shows counts only, never a
        # line of the suite's output. The branch is run as the step has it, on a synthetic log.
        step = workflow_step(JobDirectory.JOB, "SV1: run the identity suite")
        lines = step.splitlines()
        start = lines.index('          if [ "$scan" -eq 0 ]; then')
        withheld = lines.index("          else", start)
        end = lines.index("          fi", withheld)
        branch = "\n".join(line[10:] for line in lines[withheld + 1 : end])
        log = [
            "[identity] PASS config.case (D2) 0.1 s: every briefed value holds",
            "[identity] PASS other.case (4) 0.2 s: a detail line",
            "[identity] FAIL failed.case (11) 0.3 s: FAILED: a reason",
            "[identity] cases: 2/3 passed in 0.6 s",
            "identity secret scan: FOUND (9 secrets held; 1 found in 3 log records)",
            "IDENTITY VERDICT: FAIL",
            "refusing: a refusal line",
            "an unexpected line of output",
        ]
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "identity.log").write_text("\n".join(log) + "\n", encoding="utf-8")
            result = subprocess.run(
                ["bash", "-c", "set -e\n" + branch],
                env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "DIR": directory},
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        printed = result.stdout + result.stderr
        for line in log:
            with self.subTest(line=line):
                self.assertNotIn(line, printed)
        for fragment in ("[identity]", "config.case", "failed.case", "VERDICT", "refusing"):
            self.assertNotIn(fragment, printed)
        self.assertIn("counts only, never a line of the suite's output", printed)
        self.assertIn("lines in the suite's output: 8", printed)
        self.assertIn("case lines: 2 passed, 1 failed", printed)

    def test_the_upload_waits_for_the_check(self) -> None:
        step = workflow_step(JobDirectory.JOB, "SV1: save the identity suite's results JSON")
        self.assertIn(
            "        if: ${{ always() && steps.identity.outputs.scan == 'passed' }}\n", step
        )
        self.assertNotIn("if: always()\n", step)
        self.assertIn("path: proofs/postgres-ordering/.work/identity-results.json", step)


class IdentityWorkflowTests(unittest.TestCase):
    """The identity suite's job's own steps (Database proof checks (identity), since SV4 A0), read
    as the job runs them: its credentials, the decoy (DM-96 AG1), its dbshell refusal and its
    refusal of the decoy's marker (SV4 A0-C1, the exact-head review's F1 and F2)."""

    def test_the_credentials_step_makes_its_database_the_decoy_and_its_own_keys(self) -> None:
        step = workflow_step(JobDirectory.JOB, "Generate the disposable database's credentials")
        lines = script_lines(step.split("        run: |\n", 1)[1])
        self.assertEqual(lines[0], "set +x")
        # Every value is masked once it is generated and before any line that can print or write.
        values = [
            "superuser_password",
            "role_password",
            "identity_marker",
            "marker",
            "identity_secret_key",
        ]
        events = credentials_prelude(step)
        self.assertEqual([name for kind, name in events if kind == "generated"], values)
        self.assertEqual([name for kind, name in events if kind == "masked"], values)
        for name in values:
            with self.subTest(name=name):
                self.assertLess(events.index(("generated", name)), events.index(("masked", name)))
        self.assertEqual(step.count("::add-mask::"), len(values))
        for name in values:
            with self.subTest(name=name):
                self.assertEqual(len(re.findall(rf"^ *{name}=", step, flags=re.MULTILINE)), 1)
        # The markers are distinct before the role statement is written.
        distinct = (
            'test "$identity_marker" != "$marker"'
            ' || { echo "the markers are not distinct; refusing"; exit 1; }'
        )
        self.assertIn(distinct, lines)
        # F1: the identity database's comment takes the identity marker, and the decoy's (AG1:
        # glow_proof, the ordering suite's name) the decoy's, in exactly this argument list.
        role = (
            "printf \"CREATE ROLE glow_proof LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB"
            " NOCREATEROLE;\\n"
            "CREATE DATABASE glow_identity_proof OWNER glow_proof;\\n"
            "COMMENT ON DATABASE glow_identity_proof IS 'glow-ordering-proof:%s';\\n"
            "CREATE DATABASE glow_proof OWNER glow_proof;\\n"
            "COMMENT ON DATABASE glow_proof IS 'glow-ordering-proof:%s';\\n\""
            ' "$role_password" "$identity_marker" "$marker" > "$dir/create-role.sql"'
        )
        self.assertEqual(writers(step, "create-role.sql"), [role])
        self.assertLess(lines.index(distinct), lines.index(role))
        # Each marker file is written once, from its own database's marker.
        self.assertEqual(
            writers(step, "identity-marker"),
            ['printf \'%s\\n\' "$identity_marker" > "$dir/identity-marker"'],
        )
        self.assertEqual(writers(step, "marker"), ['printf \'%s\\n\' "$marker" > "$dir/marker"'])
        self.assertEqual(
            writers(step, "identity-secret-key"),
            ['printf \'%s\\n\' "$identity_secret_key" > "$dir/identity-secret-key"'],
        )
        self.assertIn("python - \"$dir/identity-jwt-key.pem\" <<'PYTHON'", lines)
        self.assertEqual(job_databases(JobDirectory.JOB), ["glow_identity_proof"])
        self.assertEqual(step.count("for path in sys.argv[1:]:"), 1)
        # No other suite's key, marker or settings is in this job.
        job = "\n".join(workflow_job(JobDirectory.JOB))
        for other in ("profile", "discovery", "wrong_marker"):
            with self.subTest(other=other):
                self.assertNotIn(other, job)

    def test_the_dbshell_step_requires_a_failed_exit_and_the_refusal(self) -> None:
        step = workflow_step(JobDirectory.JOB, "SV1: show that dbshell is refused")
        self.assertIn("        shell: bash\n", step)
        lines = script_lines(step)
        sequence = [
            "set +e",
            'env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 \\',
            "PROOF_DB_HOST=127.0.0.1 PROOF_DB_PORT=5433 PROOF_DB_NAME=glow_identity_proof"
            " PROOF_DB_USER=glow_proof \\",
            'PROOF_DB_PASSFILE="$DIR/passfile" PROOF_DB_MARKER="$(cat "$DIR/identity-marker")" \\',
            'PROOF_IDENTITY_SECRET_KEY_FILE="$DIR/identity-secret-key" \\',
            'PROOF_IDENTITY_JWT_KEY_FILE="$DIR/identity-jwt-key.pem" \\',
            "DJANGO_SETTINGS_MODULE=glow_ordering_proof.identity_settings \\",
            'python -m django dbshell < /dev/null > "$DIR/identity-dbshell.log" 2>&1',
            "status=$?",
            "set -e",
            "refusal=$(grep -m 1 -F 'RefusedDatabase: refusing dbshell'"
            ' "$DIR/identity-dbshell.log" || true)',
            'rm -f "$DIR/identity-dbshell.log"',
            'echo "identity dbshell exit status: $status"',
            'if [ "$status" -eq 0 ]; then echo "FAIL: dbshell exited 0"; exit 1; fi',
            'if [ -z "$refusal" ]; then echo "FAIL: the dbshell refusal is missing'
            ' (diagnostics withheld)"; exit 1; fi',
            'echo "refusal: $refusal"',
        ]
        self.assertEqual([line for line in sequence if line not in lines], [])
        at = [lines.index(line) for line in sequence]
        self.assertEqual(at, sorted(at))
        self.assertEqual(at[8], at[7] + 1)  # the exit status is the dbshell command's

    def test_the_migrations_step_refuses_the_decoys_marker_first(self) -> None:
        step = workflow_step(
            JobDirectory.JOB, "SV1: show the identity database refuses the decoy database's marker"
        )
        self.assertIn("        shell: bash\n", step)
        lines = script_lines(step)
        # F1: the function reads the marker file it is named, and the refused migrate is named
        # the decoy's (marker), before the identity database's own migrate.
        self.assertEqual(step.count("PROOF_DB_MARKER="), 1)
        self.assertIn(
            'PROOF_DB_PASSFILE="$DIR/passfile" PROOF_DB_MARKER="$(cat "$DIR/$1")" \\', lines
        )
        self.assertIn(
            "PROOF_DB_HOST=127.0.0.1 PROOF_DB_PORT=5433 PROOF_DB_NAME=glow_identity_proof"
            " PROOF_DB_USER=glow_proof \\",
            lines,
        )
        refused = (
            "identity marker python -m django migrate --verbosity 1"
            ' > "$DIR/identity-wrong-marker.log" 2>&1'
        )
        migrate = "identity identity-marker python -m django migrate --verbosity 1"
        self.assertEqual(
            [line for line in lines if "python -m django migrate" in line], [refused, migrate]
        )
        # F2: the decoy's existence and distinctness, the counts before and after and their
        # comparison, the refusal, and the step's failure, all before the migrations.
        sequence = [
            "docker exec \"$CONTAINER\" psql -X -q -At -F ' ' -v ON_ERROR_STOP=1 -U postgres"
            ' -d glow_identity_proof -c "$1"',
            'decoy=$(in_identity_db "SELECT count(*) FROM pg_catalog.pg_database WHERE datname ='
            " 'glow_proof' AND starts_with(shobj_description(oid, 'pg_database'),"
            " 'glow-ordering-proof:')\")",
            'distinct=$(in_identity_db "SELECT shobj_description((SELECT oid FROM'
            " pg_catalog.pg_database WHERE datname = 'glow_proof'), 'pg_database') IS DISTINCT"
            " FROM shobj_description((SELECT oid FROM pg_catalog.pg_database WHERE datname ="
            " 'glow_identity_proof'), 'pg_database')\")",
            'if [ "$decoy" != 1 ] || [ "$distinct" != t ]; then echo "FAIL: the decoy database'
            ' or its own marker is missing"; exit 1; fi',
            'in_identity_db "$per_schema" > "$DIR/identity-relations-before.txt"',
            'outside_before=$(in_identity_db "$outside_pg")',
            "set +e",
            refused,
            "status=$?",
            "set -e",
            'in_identity_db "$per_schema" > "$DIR/identity-relations-after.txt"',
            'outside_after=$(in_identity_db "$outside_pg")',
            "no_ledger=$(in_identity_db \"SELECT to_regclass('public.django_migrations') IS"
            ' NULL")',
            "refusal=$(grep -m 1 -F 'RefusedDatabase: refusing this database'"
            ' "$DIR/identity-wrong-marker.log" || true)',
            "fail=0",
            'if [ "$status" -eq 0 ]; then echo "FAIL: migrate with another database\'s marker'
            ' exited 0"; fail=1; fi',
            'if [ -n "$refusal" ]; then',
            'echo "FAIL: the refusal message is missing (diagnostics withheld)"; fail=1',
            'cmp -s "$DIR/identity-relations-before.txt" "$DIR/identity-relations-after.txt" \\',
            '|| { echo "FAIL: a schema\'s relation count changed"; fail=1; }',
            'if [ "$outside_before" != 0 ] || [ "$outside_after" != 0 ]; then',
            'echo "FAIL: a relation exists outside information_schema and the pg_ schemas"; fail=1',
            'if [ "$no_ledger" != t ]; then echo "FAIL: django_migrations exists"; fail=1; fi',
            'test "$fail" = 0',
            migrate,
            "identity identity-marker python -m django makemigrations --check --dry-run",
        ]
        self.assertEqual([line for line in sequence if line not in lines], [])
        at = [lines.index(line) for line in sequence]
        self.assertEqual(at, sorted(at))
        cmp = sequence.index('|| { echo "FAIL: a schema\'s relation count changed"; fail=1; }')
        self.assertEqual(at[cmp], at[cmp - 1] + 1)
        # The step fails under set -e at `test "$fail" = 0`: errors are not ignored again.
        self.assertEqual(lines.count("set +e"), 1)
        self.assertEqual(lines.count("set -e"), 1)


if __name__ == "__main__":
    unittest.main()
