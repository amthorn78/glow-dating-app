"""The profile suite's offline checks (SV2 Stage A; its brief's D12 and acceptance check 12).

No database: the profile settings' refusals and values; the job's secret check of the suite's
output and the upload gate; the workflow's SV2 steps; the case plan; the schema check against the
shared corpus; the value ledger; and the commands' refusals of each other's settings. The cases
themselves run in the Database proof checks job, on the third disposable database.
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import io
import json
import os
import secrets
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from cryptography.hazmat.primitives.asymmetric import rsa

from glow_ordering_proof import __main__ as commands
from glow_ordering_proof import (
    environment,
    identity_environment,
    profile_cases,
    profile_scan,
    schema_check,
)
from glow_ordering_proof.profile_support import ValueLedger
from tests.test_identity_offline import KeyFiles, pem, workflow_step

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
PROFILE_SETTINGS = "glow_ordering_proof.profile_settings"


def unquoted_step(name_prefix: str) -> str:
    """``workflow_step`` for a step whose name the workflow does not quote."""
    lines = (REPO_ROOT / ".github" / "workflows" / "foundation.yml").read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("      - ")]
    for index, start in enumerate(starts):
        if lines[start].startswith(f"      - name: {name_prefix}"):
            end = starts[index + 1] if index + 1 < len(starts) else len(lines)
            return "\n".join(lines[start:end])
    raise AssertionError(f"no step named {name_prefix!r}")


GOOD = {
    environment.HOST: "127.0.0.1",
    environment.PORT: "5433",
    environment.NAME: "glow_profile_proof",
    environment.USER: "glow_proof",
    environment.PASSFILE: "/tmp/example/passfile",
    environment.MARKER: secrets.token_hex(16),
    "PATH": "/x",
    "HOME": "/h",
    "LANG": "C.UTF-8",
}


class ProfileSettingsModuleTests(unittest.TestCase):
    """The profile settings refuse at import, as the proof's settings do, and then take SV1's
    fragment, SV2's app and the suite's own two keys from their files."""

    def setUp(self) -> None:
        self.files = KeyFiles()

    def tearDown(self) -> None:
        self.files.close()

    def import_settings(self, environ: dict[str, str]) -> Any:
        saved = dict(os.environ)
        sys.modules.pop(PROFILE_SETTINGS, None)
        try:
            os.environ.clear()
            os.environ.update(environ)
            return importlib.import_module(PROFILE_SETTINGS)
        finally:
            os.environ.clear()
            os.environ.update(saved)
            sys.modules.pop(PROFILE_SETTINGS, None)

    def test_the_settings_load_with_the_proof_variables_and_the_key_files(self) -> None:
        settings = self.import_settings({**GOOD, **self.files.environ()})
        self.assertEqual(settings.SECRET_KEY, self.files.secret_key)
        self.assertEqual(settings.HEADLESS_JWT_PRIVATE_KEY, self.files.jwt_key)
        self.assertEqual(settings.INSTALLED_APPS[-1], "glow_ordering_proof.apps.ProofConfig")
        for app in (
            "allauth.account",
            "allauth.headless",
            "glow_identity.apps.IdentityConfig",
            "glow_persistence.apps.PersistenceDesignConfig",
            "glow_profiles.apps.ProfilesConfig",
        ):
            self.assertIn(app, settings.INSTALLED_APPS)
        self.assertEqual(settings.ROOT_URLCONF, "glow_ordering_proof.profile_urls")
        database = settings.DATABASES["default"]
        # Two helpers refuse a transaction the caller opened (glow_chat's and SV1's).
        self.assertIs(database["ATOMIC_REQUESTS"], False)
        self.assertEqual(database["NAME"], "glow_profile_proof")
        self.assertNotIn("PASSWORD", database)
        from psycopg import IsolationLevel

        self.assertIs(database["OPTIONS"]["isolation_level"], IsolationLevel.READ_COMMITTED)
        self.assertEqual(settings.ALLOWED_HOSTS, ["testserver"])
        self.assertEqual(settings.LOGGING["root"], {"level": "DEBUG", "handlers": []})
        self.assertNotEqual(settings.SECRET_KEY, identity_environment.PLACEHOLDER_SECRET_KEY)

    def test_the_settings_refuse_what_the_proofs_settings_refuse(self) -> None:
        files = self.files.environ()
        with self.assertRaises(environment.RefusedEnvironment):
            self.import_settings({**GOOD, **files, "PGPASSWORD": "x"})
        with self.assertRaises(environment.RefusedEnvironment):
            self.import_settings({**GOOD, **files, "DATABASE_URL": "postgres://x"})
        with self.assertRaises(environment.RefusedEnvironment):
            self.import_settings({**GOOD, **files, "GEO_API_KEY": "x"})
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
        for name in ("profile_settings.py", "profile_urls.py"):
            path = REPO_ROOT / "proofs/postgres-ordering/glow_ordering_proof" / name
            imported: list[str] = []
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    imported.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.append(node.module)
            for module in imported:
                with self.subTest(module=name, imported=module):
                    self.assertFalse(module.startswith("glow_api"), module)
                    self.assertNotIn("static_settings", module)


class ProfileJobDirectory:
    """A job directory as the credentials step writes it, with synthetic values only."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.values: dict[str, str] = {}
        for name in profile_scan.VALUE_FILES:
            self.values[name] = secrets.token_hex(24)
            self.write(name, self.values[name] + "\n")
        self.role_password = secrets.token_hex(24)
        self.write(
            profile_scan.PASSFILE,
            "".join(
                f"127.0.0.1:5433:{database}:glow_proof:{self.role_password}\n"
                for database in ("glow_proof", "glow_identity_proof", "glow_profile_proof")
            ),
        )
        self.pem_lines: list[str] = []
        for name in profile_scan.KEY_FILES:
            text = pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
            self.write(name, text)
            self.pem_lines.append(
                [line for line in text.splitlines() if not line.startswith("---")][3]
            )
        self.log = self.write("profile.log", "[profile] PASS a.case\n")
        self.results = self.root / "profile-results.json"
        self.results.write_text(json.dumps({"cases": [{"detail": "ok"}]}), encoding="utf-8")

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="ascii")
        path.chmod(0o600)
        return path

    def clean_log(self, extra: str = "", clean: tuple[str, ...] = profile_scan.SUITE_CLEAN) -> None:
        lines = "".join(f"{line} (1 held)\n" for line in clean)
        self.write("profile.log", "[profile] PASS a.case\n" + extra + lines)

    def every_value(self) -> list[str]:
        return [*self.values.values(), self.role_password, *self.pem_lines]

    def run(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = profile_scan.main([str(self.root), str(self.log), str(self.results)])
        return status, out.getvalue()

    def close(self) -> None:
        self.directory.cleanup()


class ProfileScanTests(unittest.TestCase):
    """The job's check finds any of its own secrets in the profile suite's log or results JSON,
    requires both of the suite's own clean scans, and leaves nothing to upload after a refusal."""

    def setUp(self) -> None:
        self.job = ProfileJobDirectory()

    def tearDown(self) -> None:
        self.job.close()

    def assert_no_value_printed(self, printed: str) -> None:
        for value in self.job.every_value():
            self.assertNotIn(value, printed)

    def test_the_values_are_every_secret_file_of_the_job(self) -> None:
        self.assertEqual(
            set(profile_scan.VALUE_FILES),
            {
                "profile-secret-key",
                "profile-marker",
                "identity-secret-key",
                "identity-marker",
                "marker",
                "superuser-password",
            },
        )
        self.assertEqual(
            set(profile_scan.KEY_FILES), {"profile-jwt-key.pem", "identity-jwt-key.pem"}
        )
        values = profile_scan.job_values(self.job.root)
        for value in self.job.every_value():
            self.assertIn(value, values)
        self.assertNotIn("", values)
        self.assertFalse(any(value.startswith("-----") for value in values))

    def test_clean_output_passes_and_keeps_the_json(self) -> None:
        self.job.clean_log()
        status, printed = self.job.run()
        self.assertEqual(status, profile_scan.PASSED, printed)
        self.assertTrue(self.job.results.exists())
        self.assertIn("found in the profile results JSON: 0", printed)

    def test_a_value_in_the_json_only_is_refused_and_the_json_removed(self) -> None:
        self.job.clean_log()
        for value in self.job.every_value():
            with self.subTest(value=len(value)):
                self.job.results.write_text(
                    json.dumps({"server": {"planted": value}}), encoding="utf-8"
                )
                status, printed = self.job.run()
                self.assertEqual(status, profile_scan.REFUSED)
                self.assertFalse(self.job.results.exists())
                # The role's password is in the passfile three times, so it counts three times.
                self.assertRegex(printed, r"found in the profile results JSON: [13]\n")
                self.assertIn("removed; nothing to upload", printed)
                self.assert_no_value_printed(printed)

    def test_a_value_escaped_by_json_is_found(self) -> None:
        self.job.clean_log()
        value = self.job.values["profile-marker"]
        escaped = "".join(f"\\u{ord(c):04x}" for c in value)
        self.job.results.write_text('{"detail": "' + escaped + '"}', encoding="utf-8")
        status, printed = self.job.run()
        self.assertEqual(status, profile_scan.REFUSED)
        self.assertFalse(self.job.results.exists())

    def test_a_value_in_the_log_is_refused_and_the_json_removed(self) -> None:
        self.job.clean_log(extra=self.job.values["profile-secret-key"] + "\n")
        status, printed = self.job.run()
        self.assertEqual(status, profile_scan.REFUSED)
        self.assertFalse(self.job.results.exists())
        self.assertIn("found in the profile suite's output: 1", printed)
        self.assert_no_value_printed(printed)

    def test_each_of_the_suites_clean_scans_is_required(self) -> None:
        for only in profile_scan.SUITE_CLEAN:
            with self.subTest(only=only):
                self.job.results.write_text("{}", encoding="utf-8")
                self.job.clean_log(clean=(only,))
                status, printed = self.job.run()
                self.assertEqual(status, profile_scan.REFUSED)
                self.assertFalse(self.job.results.exists())
                self.assertIn("reported clean: False", printed)

    def test_an_absent_json_is_nothing_to_upload(self) -> None:
        self.job.clean_log()
        self.job.results.unlink()
        status, printed = self.job.run()
        self.assertEqual(status, profile_scan.PASSED)
        self.assertIn("absent: nothing to scan or upload", printed)

    def test_an_unreadable_secret_file_is_refused(self) -> None:
        for name in ("profile-secret-key", "profile-jwt-key.pem", profile_scan.PASSFILE):
            with self.subTest(name=name):
                job = ProfileJobDirectory()
                try:
                    job.clean_log()
                    (job.root / name).unlink()
                    status, printed = job.run()
                    self.assertEqual(status, profile_scan.REFUSED)
                    self.assertFalse(job.results.exists())
                    self.assertIn("could not run", printed)
                finally:
                    job.close()

    def test_the_module_imports_only_the_standard_library_and_the_identity_check(self) -> None:
        tree = ast.parse(Path(profile_scan.__file__).read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertLessEqual(
            imported,
            {
                "__future__",
                "collections.abc",
                "dataclasses",
                "pathlib",
                "sys",
                "glow_ordering_proof.identity_scan",
            },
        )


class ProfileWorkflowTests(unittest.TestCase):
    """The Database proof checks job's SV2 steps, read as the job runs them."""

    def test_the_credentials_step_makes_the_third_database_and_its_own_keys(self) -> None:
        step = unquoted_step("Generate the disposable database's credentials")
        for line in (
            'echo "::add-mask::$profile_marker"',
            'echo "::add-mask::$profile_secret_key"',
            'printf \'%s\\n\' "$profile_marker" > "$dir/profile-marker"',
            'printf \'%s\\n\' "$profile_secret_key" > "$dir/profile-secret-key"',
            'python - "$dir/identity-jwt-key.pem" "$dir/profile-jwt-key.pem" <<\'PYTHON\'',
        ):
            with self.subTest(line=line):
                self.assertIn(line, step)
        self.assertIn("CREATE DATABASE glow_profile_proof OWNER glow_proof;", step)
        self.assertIn("COMMENT ON DATABASE glow_profile_proof IS 'glow-ordering-proof:%s';", step)
        self.assertIn("127.0.0.1:5433:glow_profile_proof:glow_proof:%s", step)
        self.assertIn('test "$profile_marker" != "$identity_marker"', step)
        # Each key is generated, never copied: one key per path, in a loop.
        self.assertIn("for path in sys.argv[1:]:", step)

    def test_the_migrations_step_refuses_both_other_markers_first(self) -> None:
        step = workflow_step("SV2: show the profile database refuses the other markers")
        loop = step.index("for other in marker identity-marker; do")
        migrate = step.index("profile profile-marker python -m django migrate --verbosity 1")
        self.assertLess(loop, migrate)
        self.assertIn(
            "profile profile-marker python -m django makemigrations --check --dry-run", step
        )
        self.assertIn('PROOF_IDENTITY_SECRET_KEY_FILE="$DIR/profile-secret-key"', step)
        self.assertIn('PROOF_IDENTITY_JWT_KEY_FILE="$DIR/profile-jwt-key.pem"', step)
        self.assertIn("DJANGO_SETTINGS_MODULE=glow_ordering_proof.profile_settings", step)

    def test_the_suite_step_runs_the_check_and_sets_the_output_only_on_a_pass(self) -> None:
        step = workflow_step("SV2: run the profile suite")
        self.assertIn("        id: profile\n", step)
        self.assertIn(
            'python -m glow_ordering_proof.profile_scan "$DIR" "$DIR/profile.log"'
            " .work/profile-results.json",
            step,
        )
        passed = step.index('if [ "$scan" -eq 0 ]; then')
        withheld = step.index("else", passed)
        output = step.index('echo "scan=passed" >> "$GITHUB_OUTPUT"')
        self.assertTrue(passed < output < withheld)
        self.assertEqual(step.count("scan=passed"), 1)
        self.assertIn('echo "profile phase: $((finished - started)) s', step)

    def test_after_a_failed_check_the_step_prints_counts_only(self) -> None:
        step = workflow_step("SV2: run the profile suite")
        lines = step.splitlines()
        start = lines.index('          if [ "$scan" -eq 0 ]; then')
        withheld = lines.index("          else", start)
        end = lines.index("          fi", withheld)
        branch = "\n".join(line[10:] for line in lines[withheld + 1 : end])
        log = [
            "[profile] PASS settings.case (1, D2) 0.1 s: every launch default reads",
            "[profile] PASS other.case (5, D5) 0.2 s: a detail line",
            "[profile] FAIL failed.case (12) 0.3 s: FAILED: a reason",
            "[profile] cases: 2/3 passed in 0.6 s",
            "profile secret scan: FOUND (9 secrets held; 1 found in 3 log records)",
            "profile value scan: clean (4 member values held)",
            "PROFILE VERDICT: FAIL",
            "an unexpected line of output",
        ]
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "profile.log").write_text("\n".join(log) + "\n", encoding="utf-8")
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
        for fragment in ("[profile]", "settings.case", "failed.case", "VERDICT"):
            self.assertNotIn(fragment, printed)
        self.assertIn("counts only, never a line of the suite's output", printed)
        self.assertIn("lines in the suite's output: 8", printed)
        self.assertIn("case lines: 2 passed, 1 failed", printed)

    def test_the_second_run_step_counts_rows_and_requires_the_refusal(self) -> None:
        step = workflow_step("SV2: show that a second profile run on the used database")
        self.assertIn("-d glow_profile_proof", step)
        for table in (
            "auth_user",
            "glow_persistence_appaccount",
            "glow_persistence_profile",
            "glow_persistence_settingversion",
            "glow_persistence_outboxevent",
            "glow_persistence_idempotencyrecord",
        ):
            with self.subTest(table=table):
                self.assertIn(f"FROM {table})", step)
        self.assertIn("grep -m 1 -F 'refusing a used database'", step)
        self.assertIn('if [ "$before" != "$after" ]; then', step)

    def test_the_upload_waits_for_the_check(self) -> None:
        step = workflow_step("SV2: save the profile suite's results JSON")
        self.assertIn(
            "        if: ${{ always() && steps.profile.outputs.scan == 'passed' }}\n", step
        )
        self.assertNotIn("if: always()\n", step)
        self.assertIn("name: sv2-profile-results", step)
        self.assertIn("path: proofs/postgres-ordering/.work/profile-results.json", step)


class ProfilePlanTests(unittest.TestCase):
    def test_the_plan_covers_every_stage_a_acceptance_check(self) -> None:
        plan = profile_cases.plan()
        self.assertEqual(len(plan), len(set(plan)))
        covered = {check for entry in profile_cases.CASES for check in entry.checks}
        # Stage A's checks: 1 to 9, 11 and 12 (10, the photos, is Stage B's).
        for check in [*(str(n) for n in range(1, 10)), "11", "12"]:
            with self.subTest(check=check):
                self.assertIn(check, covered)
        self.assertNotIn("10", covered)
        for decision in ("D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D17", "D18"):
            with self.subTest(decision=decision):
                self.assertIn(decision, covered)

    def test_the_expected_routes_are_the_api_routes(self) -> None:
        # Read from services/api's URL configuration as text, without importing it.
        tree = ast.parse((API_ROOT / "glow_profiles" / "urls.py").read_text(encoding="utf-8"))
        declared = {
            node.args[0].value
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "path"
            and isinstance(node.args[0], ast.Constant)
        }
        self.assertEqual(declared, set(profile_cases.EXPECTED_PROFILE_ROUTES))


class SchemaCheckCorpusTests(unittest.TestCase):
    """The proof's schema check decides every production corpus case it supports as the
    contract's validators do, and refuses a schema it does not support rather than passing it."""

    def test_every_supported_production_case_is_decided_as_the_contract_does(self) -> None:
        corpus = json.loads(
            (REPO_ROOT / "packages/contracts/corpus/shared-v1.json").read_text(encoding="utf-8")
        )["cases"]
        root = schema_check.load_schema()
        disagreements: list[str] = []
        unsupported: set[str] = set()
        decided: set[str] = set()
        for row in corpus:
            if row["scope"] != "production":
                continue
            try:
                valid = not schema_check.check_body(row["definition"], row["value"], root)
            except schema_check.UnsupportedSchema:
                unsupported.add(row["definition"])
                continue
            decided.add(row["definition"])
            if valid != row["valid"]:
                disagreements.append(row["name"])
        self.assertEqual(disagreements, [])
        self.assertLessEqual(unsupported, {"AppIntent"})
        # Every response the profile routes serve is decided, not skipped.
        for definition in (
            "AppResponse",
            "Error",
            "OwnProfile",
            "OwnProfileFields",
            "OwnPreferences",
            "OwnFilters",
            "OwnArea",
            "NearestArea",
            "ProfileCatalog",
            "OwnCompletion",
            "OnboardingEligibility",
            "OwnSensitiveConsent",
            "OwnAgeState",
            "OwnBirthInput",
        ):
            with self.subTest(definition=definition):
                self.assertIn(definition, decided)


class ValueLedgerTests(unittest.TestCase):
    def test_a_value_is_found_as_sent_or_as_json_escapes_it(self) -> None:
        ledger = ValueLedger()
        words = "é" * 39 + "x"
        ledger.add(words)
        ledger.add(40.7123457)
        ledger.add("1990-06-15")
        ledger.add("abcd")  # too short to search for
        self.assertEqual(ledger.count(), 3)
        self.assertEqual(ledger.found_in("nothing here"), 0)
        self.assertEqual(ledger.found_in(json.dumps({"detail": words})), 1)
        self.assertEqual(ledger.found_in(json.dumps({"detail": words}, ensure_ascii=False)), 1)
        self.assertEqual(ledger.found_in("latitude 40.7123457"), 1)
        self.assertEqual(ledger.found_in("born 1990-06-15 abcd"), 1)


class ProfileCommandTests(unittest.TestCase):
    """``profile`` runs only under the profile settings, and no other command runs under them;
    both refusals come before Django is set up."""

    def call(self, argv: list[str], settings_module: str) -> tuple[int, str]:
        out = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": settings_module}),
            mock.patch.object(commands, "_setup", side_effect=AssertionError("set up")),
            contextlib.redirect_stdout(out),
        ):
            status = commands.main(argv)
        return status, out.getvalue()

    def test_the_profile_command_refuses_every_other_settings_module(self) -> None:
        for module in (
            "glow_ordering_proof.settings",
            "glow_ordering_proof.identity_settings",
            "glow_api.settings",
        ):
            with self.subTest(module=module):
                status, printed = self.call(["profile"], module)
                self.assertEqual(status, 1)
                self.assertIn("refusing: set DJANGO_SETTINGS_MODULE=" + PROFILE_SETTINGS, printed)

    def test_no_other_command_runs_under_the_profile_settings(self) -> None:
        for argv in (["facts"], ["run", "--seed", "1"], ["identity"]):
            with self.subTest(command=argv[0]):
                status, printed = self.call(argv, PROFILE_SETTINGS)
                self.assertEqual(status, 1)
                self.assertIn("refusing: only the profile suite runs under the profile", printed)


if __name__ == "__main__":
    unittest.main()
