"""The discovery suite's offline checks (SV3 Stage A; its brief's D14 and acceptance check 13).

No database: the discovery settings' refusals and values; the job's secret check of the suite's
output and the upload gate; the workflow's SV3 steps; the case plan; the commands' refusals of
each other's settings; and the scan of account locks (C1; DM-61 K3), with its planted reversals.
The cases themselves run in the Database proof checks job, on the fourth disposable database.
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
from glow_ordering_proof import account_lock_scan, discovery_cases, discovery_scan, environment
from tests.test_identity_offline import KeyFiles, pem, workflow_step
from tests.test_profile_offline import unquoted_step

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
DISCOVERY_SETTINGS = "glow_ordering_proof.discovery_settings"

GOOD = {
    environment.HOST: "127.0.0.1",
    environment.PORT: "5433",
    environment.NAME: "glow_discovery_proof",
    environment.USER: "glow_proof",
    environment.PASSFILE: "/tmp/example/passfile",
    environment.MARKER: secrets.token_hex(16),
    "PATH": "/x",
    "HOME": "/h",
    "LANG": "C.UTF-8",
}


class DiscoverySettingsModuleTests(unittest.TestCase):
    """The discovery settings refuse at import, as the proof's settings do, and then take SV1's and
    SV2's fragments, SV3's app, the fixture compatibility adapter and the suite's own two keys."""

    def setUp(self) -> None:
        self.files = KeyFiles()

    def tearDown(self) -> None:
        self.files.close()

    def import_settings(self, environ: dict[str, str]) -> Any:
        saved = dict(os.environ)
        sys.modules.pop(DISCOVERY_SETTINGS, None)
        try:
            os.environ.clear()
            os.environ.update(environ)
            return importlib.import_module(DISCOVERY_SETTINGS)
        finally:
            os.environ.clear()
            os.environ.update(saved)
            sys.modules.pop(DISCOVERY_SETTINGS, None)

    def test_the_settings_load_with_the_proof_variables_and_the_key_files(self) -> None:
        settings = self.import_settings({**GOOD, **self.files.environ()})
        self.assertEqual(settings.SECRET_KEY, self.files.secret_key)
        self.assertEqual(settings.HEADLESS_JWT_PRIVATE_KEY, self.files.jwt_key)
        self.assertEqual(settings.INSTALLED_APPS[-1], "glow_ordering_proof.apps.ProofConfig")
        for app in (
            "glow_identity.apps.IdentityConfig",
            "glow_persistence.apps.PersistenceDesignConfig",
            "glow_profiles.apps.ProfilesConfig",
            "glow_discovery.apps.DiscoveryConfig",
        ):
            self.assertIn(app, settings.INSTALLED_APPS)
        self.assertEqual(settings.ROOT_URLCONF, "glow_ordering_proof.discovery_urls")
        database = settings.DATABASES["default"]
        self.assertIs(database["ATOMIC_REQUESTS"], False)
        self.assertEqual(database["NAME"], "glow_discovery_proof")
        self.assertNotIn("PASSWORD", database)
        from psycopg import IsolationLevel

        self.assertIs(database["OPTIONS"]["isolation_level"], IsolationLevel.READ_COMMITTED)
        # D6: the fixture adapter, selected here only, in the test environment.
        self.assertEqual(
            settings.GLOW_DISCOVERY_COMPATIBILITY_FIXTURE, "explicitly-synthetic-ready"
        )
        self.assertEqual(settings.GLOW_DISCOVERY_ENVIRONMENT, "test")
        self.assertEqual(settings.LOGGING["root"], {"level": "DEBUG", "handlers": []})

    def test_the_settings_refuse_what_the_proofs_settings_refuse(self) -> None:
        files = self.files.environ()
        for extra in ({"PGPASSWORD": "x"}, {"DATABASE_URL": "x"}, {"HD_API_KEY": "x"}):
            with self.subTest(name=next(iter(extra))):
                with self.assertRaises(environment.RefusedEnvironment):
                    self.import_settings({**GOOD, **files, **extra})
        with self.assertRaises(environment.RefusedConnection):
            self.import_settings({**GOOD, **files, environment.HOST: "db.example.internal"})

    def test_the_settings_never_import_the_api_settings(self) -> None:
        for name in ("discovery_settings.py", "discovery_urls.py"):
            path = REPO_ROOT / "proofs/postgres-ordering/glow_ordering_proof" / name
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ImportFrom) and node.module:
                    with self.subTest(module=name, imported=node.module):
                        self.assertFalse(node.module.startswith("glow_api"))
                        self.assertNotIn("static_settings", node.module)


SUITE_LINES = {
    "discovery secret scan: clean": (
        "discovery secret scan: clean (1044 secrets held; 0 found in 631 log records, 64 writes"
        " and the results JSON)"
    ),
    "discovery value scan: clean": (
        "discovery value scan: clean (591 member values held: coordinates, internal points,"
        " distances, birth dates, times and places, own words, sensitive values, photo keys and"
        " references; 0 found in the same output)"
    ),
}


class DiscoveryJobDirectory:
    """A job directory as the credentials step writes it, with synthetic values only."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.values: dict[str, str] = {}
        for name in discovery_scan.VALUE_FILES:
            self.values[name] = secrets.token_hex(24)
            self.write(name, self.values[name] + "\n")
        self.role_password = secrets.token_hex(24)
        databases = ("glow_proof", "glow_identity_proof", "glow_profile_proof")
        self.write(
            discovery_scan.PASSFILE,
            "".join(
                f"127.0.0.1:5433:{database}:glow_proof:{self.role_password}\n"
                for database in (*databases, "glow_discovery_proof")
            ),
        )
        self.pem_lines: list[str] = []
        for name in discovery_scan.KEY_FILES:
            text = pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
            self.write(name, text)
            self.pem_lines.append(
                [line for line in text.splitlines() if not line.startswith("---")][3]
            )
        self.log = self.write("discovery.log", "[discovery] PASS a.case\n")
        self.results = self.root / "discovery-results.json"
        self.results.write_text(json.dumps({"cases": [{"detail": "ok"}]}), encoding="utf-8")

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="ascii")
        path.chmod(0o600)
        return path

    def clean_log(
        self, extra: str = "", clean: tuple[str, ...] = discovery_scan.SUITE_CLEAN
    ) -> None:
        lines = "".join(f"{SUITE_LINES[line]}\n" for line in clean)
        self.write("discovery.log", "[discovery] PASS a.case\n" + extra + lines)

    def run(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = discovery_scan.main([str(self.root), str(self.log), str(self.results)])
        return status, out.getvalue()

    def every_value(self) -> list[str]:
        return [*self.values.values(), self.role_password, *self.pem_lines]

    def close(self) -> None:
        self.directory.cleanup()


class DiscoveryScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.job = DiscoveryJobDirectory()

    def tearDown(self) -> None:
        self.job.close()

    def test_the_values_are_every_secret_file_of_the_job(self) -> None:
        self.assertEqual(
            set(discovery_scan.VALUE_FILES),
            {
                "discovery-secret-key",
                "discovery-marker",
                "profile-secret-key",
                "profile-marker",
                "identity-secret-key",
                "identity-marker",
                "marker",
                "superuser-password",
            },
        )
        self.assertEqual(
            set(discovery_scan.KEY_FILES),
            {"discovery-jwt-key.pem", "profile-jwt-key.pem", "identity-jwt-key.pem"},
        )
        found = discovery_scan.job_values(self.job.root)
        for value in self.job.every_value():
            self.assertIn(value, found)

    def test_clean_output_passes_and_keeps_the_json(self) -> None:
        self.job.clean_log()
        status, printed = self.job.run()
        self.assertEqual(status, discovery_scan.PASSED, printed)
        self.assertTrue(self.job.results.exists())

    def test_a_value_in_the_log_or_the_json_is_refused_and_the_json_removed(self) -> None:
        for where in ("log", "json"):
            with self.subTest(where=where):
                job = DiscoveryJobDirectory()
                try:
                    value = job.values["discovery-secret-key"]
                    job.clean_log(extra=f"{value}\n" if where == "log" else "")
                    if where == "json":
                        job.results.write_text(json.dumps({"x": value}), encoding="utf-8")
                    status, printed = job.run()
                    self.assertEqual(status, discovery_scan.REFUSED)
                    self.assertFalse(job.results.exists())
                    for secret in job.every_value():
                        self.assertNotIn(secret, printed)
                finally:
                    job.close()

    def test_each_of_the_suites_clean_scans_is_required(self) -> None:
        for kept in discovery_scan.SUITE_CLEAN:
            with self.subTest(kept=kept):
                job = DiscoveryJobDirectory()
                try:
                    job.clean_log(clean=(kept,))
                    status, _ = job.run()
                    self.assertEqual(status, discovery_scan.REFUSED)
                finally:
                    job.close()

    def test_the_suites_own_lines_match_what_the_suite_prints(self) -> None:
        # The suite's lines, as discovery_suite.run formats them, pass the check's patterns.
        self.assertTrue(discovery_scan.suite_reported_clean("\n".join(SUITE_LINES.values())))


class DiscoveryWorkflowTests(unittest.TestCase):
    """The Database proof checks job's SV3 steps, read as the job runs them."""

    def test_the_credentials_step_makes_the_fourth_database_and_its_own_keys(self) -> None:
        step = unquoted_step("Generate the disposable database's credentials")
        for line in (
            'echo "::add-mask::$discovery_marker"',
            'echo "::add-mask::$discovery_secret_key"',
            'printf \'%s\\n\' "$discovery_marker" > "$dir/discovery-marker"',
            'printf \'%s\\n\' "$discovery_secret_key" > "$dir/discovery-secret-key"',
            "python - \"$dir/discovery-jwt-key.pem\" <<'PYTHON'",
        ):
            with self.subTest(line=line):
                self.assertIn(line, step)
        self.assertIn("CREATE DATABASE glow_discovery_proof OWNER glow_proof;", step)
        self.assertIn("COMMENT ON DATABASE glow_discovery_proof IS 'glow-ordering-proof:%s';", step)
        self.assertIn("127.0.0.1:5433:glow_discovery_proof:glow_proof:%s", step)
        self.assertIn('test "$discovery_marker" != "$profile_marker"', step)
        self.assertEqual(step.count("for path in sys.argv[1:]:"), 2)

    def test_the_migrations_step_refuses_the_three_other_markers_first(self) -> None:
        step = workflow_step("SV3: show the discovery database refuses the other markers")
        loop = step.index("for other in marker identity-marker profile-marker; do")
        migrate = step.index("discovery discovery-marker python -m django migrate --verbosity 1")
        self.assertLess(loop, migrate)
        self.assertIn(
            "discovery discovery-marker python -m django makemigrations --check --dry-run", step
        )
        self.assertIn('PROOF_IDENTITY_SECRET_KEY_FILE="$DIR/discovery-secret-key"', step)
        self.assertIn('PROOF_IDENTITY_JWT_KEY_FILE="$DIR/discovery-jwt-key.pem"', step)
        self.assertIn("DJANGO_SETTINGS_MODULE=glow_ordering_proof.discovery_settings", step)

    def test_the_suite_step_runs_the_check_and_sets_the_output_only_on_a_pass(self) -> None:
        step = workflow_step("SV3: run the discovery suite")
        self.assertIn("        id: discovery\n", step)
        self.assertIn(
            'python -m glow_ordering_proof.discovery_scan "$DIR" "$DIR/discovery.log"'
            " .work/discovery-results.json",
            step,
        )
        passed = step.index('if [ "$scan" -eq 0 ]; then')
        withheld = step.index("else", passed)
        output = step.index('echo "scan=passed" >> "$GITHUB_OUTPUT"')
        self.assertTrue(passed < output < withheld)
        self.assertEqual(step.count("scan=passed"), 1)
        self.assertIn('echo "discovery phase: $((finished - started)) s', step)

    def test_after_a_failed_check_the_step_prints_counts_only(self) -> None:
        step = workflow_step("SV3: run the discovery suite")
        lines = step.splitlines()
        start = lines.index('          if [ "$scan" -eq 0 ]; then')
        withheld = lines.index("          else", start)
        end = lines.index("          fi", withheld)
        branch = "\n".join(line[10:] for line in lines[withheld + 1 : end])
        log = [
            "[discovery] PASS settings.case (1, D3) 0.1 s: a detail line",
            "[discovery] FAIL failed.case (5) 0.3 s: FAILED: a reason",
            "[discovery] cases: 1/2 passed in 0.4 s",
            "discovery secret scan: FOUND (9 secrets held; 1 found in 3 log records)",
            "DISCOVERY VERDICT: FAIL",
        ]
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "discovery.log").write_text("\n".join(log) + "\n", encoding="utf-8")
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
        self.assertIn("lines in the suite's output: 5", printed)
        self.assertIn("case lines: 1 passed, 1 failed", printed)

    def test_the_second_run_step_counts_rows_and_requires_the_refusal(self) -> None:
        step = workflow_step("SV3: show that a second discovery run on the used database")
        self.assertIn("-d glow_discovery_proof", step)
        for table in (
            "auth_user",
            "glow_persistence_appaccount",
            "glow_persistence_profile",
            "glow_persistence_recommendationbatch",
            "glow_persistence_recommendationentry",
            "glow_persistence_outboxevent",
        ):
            with self.subTest(table=table):
                self.assertIn(f"FROM {table})", step)
        self.assertIn("grep -m 1 -F 'refusing a used database'", step)
        self.assertIn('if [ "$before" != "$after" ]; then', step)

    def test_the_upload_waits_for_the_check(self) -> None:
        step = workflow_step("SV3: save the discovery suite's results JSON")
        self.assertIn(
            "        if: ${{ always() && steps.discovery.outputs.scan == 'passed' }}\n", step
        )
        self.assertIn("name: sv3-discovery-results", step)
        self.assertIn("path: proofs/postgres-ordering/.work/discovery-results.json", step)

    def test_the_suite_runs_after_the_profile_suite(self) -> None:
        text = (REPO_ROOT / ".github/workflows/foundation.yml").read_text(encoding="utf-8")
        self.assertLess(
            text.index("SV2: save the profile suite's results JSON"),
            text.index("SV3: show the discovery database refuses the other markers"),
        )
        self.assertLess(
            text.index("SV3: save the discovery suite's results JSON"),
            text.index("Remove the disposable database, its credential files"),
        )


class DiscoveryPlanTests(unittest.TestCase):
    def test_the_plan_covers_stage_as_acceptance_checks(self) -> None:
        plan = discovery_cases.plan()
        self.assertEqual(len(plan), len(set(plan)))
        covered = {check for entry in discovery_cases.CASES for check in entry.checks}
        for check in ("1", "2", "3", "4", "5", "6", "12", "13", "14"):
            with self.subTest(check=check):
                self.assertIn(check, covered)
        for decision in ("D2", "D3", "D4", "D5", "D6", "D7", "D8", "D13", "D14", "D19", "DB04"):
            with self.subTest(decision=decision):
                self.assertIn(decision, covered)
        # Stage B's checks (7 to 11) are not Stage A's.
        for check in ("7", "8", "9", "10", "11"):
            self.assertNotIn(check, covered)

    def test_the_case_count_is_pinned(self) -> None:
        self.assertEqual(discovery_cases.CASE_COUNT, 38)
        self.assertEqual(len(discovery_cases.plan()), discovery_cases.CASE_COUNT)

    def test_the_page_route_is_the_apis(self) -> None:
        tree = ast.parse((API_ROOT / "glow_discovery" / "urls.py").read_text(encoding="utf-8"))
        declared = {
            node.args[0].value
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "path"
            and isinstance(node.args[0], ast.Constant)
        }
        self.assertEqual(declared, {"api/v1/discovery/page"})
        from glow_ordering_proof import discovery_support

        self.assertEqual(discovery_support.PAGE, "/api/v1/discovery/page")


class DiscoveryCommandTests(unittest.TestCase):
    """``discovery`` runs only under the discovery settings, and no other command runs under them;
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

    def test_the_discovery_command_refuses_every_other_settings_module(self) -> None:
        for module in (
            "glow_ordering_proof.settings",
            "glow_ordering_proof.identity_settings",
            "glow_ordering_proof.profile_settings",
            "glow_api.settings",
        ):
            with self.subTest(module=module):
                status, printed = self.call(["discovery"], module)
                self.assertEqual(status, 1)
                self.assertIn("refusing: set DJANGO_SETTINGS_MODULE=" + DISCOVERY_SETTINGS, printed)

    def test_no_other_command_runs_under_the_discovery_settings(self) -> None:
        for argv in (["facts"], ["run", "--seed", "1"], ["identity"], ["profile"]):
            with self.subTest(command=argv[0]):
                status, printed = self.call(argv, DISCOVERY_SETTINGS)
                self.assertEqual(status, 1)
                self.assertIn("refusing:", printed)


if __name__ == "__main__":
    unittest.main()


PLANTED = {
    "orm": (
        "from glow_persistence.models import AppAccount\n\n\n"
        "def lock(account_id):\n"
        "    return AppAccount.objects.select_for_update().filter(pk=account_id).first()\n"
    ),
    "generic": (
        "def _lock(model, pk):\n"
        "    return model.objects.select_for_update().filter(pk=pk).first()\n"
    ),
    "sql": (
        "def lock(cursor, account_id):\n"
        "    cursor.execute(\n"
        "        'SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR UPDATE',\n"
        "        [account_id],\n"
        "    )\n"
    ),
    "sql_table_placeholder": (
        "def lock(cursor, table, pk):\n"
        "    cursor.execute(f'SELECT id FROM {table} WHERE id = %s FOR UPDATE', [pk])\n"
    ),
}
ACCEPTED = {
    "orm": (
        "from glow_persistence.models import AppAccount\n\n\n"
        "def lock(account_id):\n"
        "    rows = AppAccount.objects.select_for_update(no_key=True)\n"
        "    return rows.filter(pk=account_id).first()\n"
    ),
    "generic": (
        "from glow_persistence.models import AppAccount\n\n\n"
        "def _lock(model, pk):\n"
        "    rows = model.objects.select_for_update(no_key=model is AppAccount)\n"
        "    return rows.filter(pk=pk).first()\n"
    ),
    "other_model": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    return Match.objects.select_for_update().filter(pk=pk).first()\n"
    ),
    "shared_read": (
        "def read(cursor, account_id):\n"
        "    cursor.execute(\n"
        "        'SELECT state FROM glow_persistence_appaccount WHERE id = %s FOR SHARE',\n"
        "        [account_id],\n"
        "    )\n"
    ),
    "docstring": (
        'def lock():\n    """Takes glow_persistence_appaccount FOR UPDATE, in words only."""\n'
    ),
}


class AccountLockScanTests(unittest.TestCase):
    """C1's scan (DM-61 K1, K3): every explicit lock of an ``AppAccount`` row in ``services/api``
    and the reference design is ``FOR NO KEY UPDATE``; a planted ``FOR UPDATE`` lock fails it."""

    def scan_source(self, text: str) -> list[account_lock_scan.Lock]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(text, encoding="utf-8")
            return account_lock_scan.scan([path])

    def test_the_tree_has_only_no_key_account_locks_at_the_seven_sites(self) -> None:
        locks = account_lock_scan.scan()
        self.assertEqual(account_lock_scan.violations(locks), [])
        self.assertEqual(account_lock_scan.sites(locks), account_lock_scan.EXPECTED_SITES)
        self.assertEqual(len(locks), 7)

    def test_the_scan_reads_services_api_without_its_tests_and_the_reference(self) -> None:
        scanned = {path.resolve() for path in account_lock_scan.sources()}
        self.assertIn((API_ROOT / "glow_profiles" / "tx.py").resolve(), scanned)
        self.assertIn(account_lock_scan.REFERENCE.resolve(), scanned)
        self.assertFalse(any("tests" in path.relative_to(REPO_ROOT).parts for path in scanned))
        self.assertFalse(any(".venv" in path.parts for path in scanned))

    def test_a_planted_for_update_lock_fails_the_scan(self) -> None:
        # The reversal (DM-61 K3): each planted lock is found and refused.
        for name, text in PLANTED.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual(len(locks), 1)
                self.assertEqual(
                    [lock.mode for lock in account_lock_scan.violations(locks)], ["FOR UPDATE"]
                )

    def test_no_key_locks_reads_and_other_models_pass(self) -> None:
        for name, text in ACCEPTED.items():
            with self.subTest(accepted=name):
                self.assertEqual(account_lock_scan.violations(self.scan_source(text)), [])

    def test_the_command_exits_non_zero_on_a_planted_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(PLANTED["orm"], encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = account_lock_scan.main([str(path)])
        self.assertEqual(code, 1)
        self.assertIn("not FOR NO KEY UPDATE: 1", out.getvalue())
