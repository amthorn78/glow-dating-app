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
from uuid import UUID, uuid4

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
        self.assertEqual(discovery_cases.CASE_COUNT, 40)
        self.assertEqual(len(discovery_cases.plan()), discovery_cases.CASE_COUNT)
        # C2's two new cases (the exact-head review's F1 and F2).
        for case_id in ("pages.one_snapshot_statements", "distance.choice_no_longer_offered"):
            self.assertIn(case_id, discovery_cases.plan())

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
# C2 (DM-65; the exact-head review's F3): a lock of another model's queryset that joins a table
# locks the joined rows FOR UPDATE too, a joined account included, unless it takes no_key=True or
# names in of= no path to AppAccount.
PLANTED_JOINS = {
    "select_related_account": (
        "from glow_persistence.models import Profile\n\n\n"
        "def lock(account_id):\n"
        "    return (\n"
        "        Profile.objects.select_related('account')\n"
        "        .select_for_update()\n"
        "        .filter(account_id=account_id)\n"
        "        .first()\n"
        "    )\n"
    ),
    "lookup_through_candidate": (
        "from glow_persistence.models import RecommendationEntry\n\n\n"
        "def lock(batch_id):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update()\n"
        "        .filter(batch_id=batch_id, candidate__state='active')\n"
        "    )\n"
    ),
    "lookup_through_another_model": (
        "from glow_persistence.models import RecommendationEntry\n\n\n"
        "def lock(account_id):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update()\n"
        "        .filter(batch__account__state='active', batch__account_id=account_id)\n"
        "    )\n"
    ),
}
# Further joins the rule covers: a Q, an F, an order_by and a values path, a queryset held in a
# variable, a generic lock with a join, and a path the scan cannot read.
PLANTED_JOINS_MORE = {
    "q": (
        "from django.db.models import Q\n"
        "from glow_persistence.models import Block\n\n\n"
        "def lock(pk):\n"
        "    return Block.objects.select_for_update().filter(Q(target__state='active')).first()\n"
    ),
    "f": (
        "from django.db.models import F\n"
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    rows = Match.objects.select_for_update()\n"
        "    return rows.filter(pk=pk, state=F('account_low__state')).first()\n"
    ),
    "order_by": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock():\n"
        "    rows = Match.objects.select_for_update()\n"
        "    return rows.order_by('-account_high__created_at').first()\n"
    ),
    "values": (
        "from glow_persistence.models import DirectionalInteraction\n\n\n"
        "def lock(pk):\n"
        "    return list(\n"
        "        DirectionalInteraction.objects.select_for_update()\n"
        "        .filter(pk=pk)\n"
        "        .values('actor__state')\n"
        "    )\n"
    ),
    "held_in_a_variable": (
        "from glow_persistence.models import ChatIdentity\n\n\n"
        "def lock(pk):\n"
        "    rows = ChatIdentity.objects.select_for_update()\n"
        "    return rows.filter(binding__match__account_low__state='active').first()\n"
    ),
    "generic_with_a_join": (
        "from glow_persistence.models import AppAccount\n\n\n"
        "def _lock(model, pk):\n"
        "    rows = model.objects.select_for_update(no_key=model is AppAccount)\n"
        "    return rows.select_related('account').filter(pk=pk).first()\n"
    ),
    "unreadable_path": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock(name, value):\n"
        "    return Match.objects.select_for_update().filter(**{name: value}).first()\n"
    ),
}
ACCEPTED_JOINS = {
    "of_self": (
        "from glow_persistence.models import RecommendationEntry\n\n\n"
        "def lock(account_id):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update(of=('self',))\n"
        "        .filter(batch__account__state='active', candidate__state='active')\n"
        "    )\n"
    ),
    "no_key": (
        "from glow_persistence.models import Profile\n\n\n"
        "def lock(account_id):\n"
        "    return (\n"
        "        Profile.objects.select_related('account')\n"
        "        .select_for_update(no_key=True)\n"
        "        .filter(account_id=account_id)\n"
        "        .first()\n"
        "    )\n"
    ),
    "of_another_model": (
        "from glow_persistence.models import RecommendationEntry\n\n\n"
        "def lock(account_id):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update(of=('self', 'batch'))\n"
        "        .filter(batch__account_id=account_id, batch__state='ready')\n"
        "    )\n"
    ),
    "lookups_only": (
        "from glow_persistence.models import MediaObject\n\n\n"
        "def lock(asset_id):\n"
        "    return (\n"
        "        MediaObject.objects.select_for_update()\n"
        "        .filter(asset_id=asset_id, adopted_at__isnull=False, role__in=['original'])\n"
        "        .order_by('-created_at')\n"
        "        .first()\n"
        "    )\n"
    ),
}
# Each of these names a path to AppAccount in of=, so the joined account is still locked FOR
# UPDATE.
PLANTED_OF = {
    "of_the_candidate": (
        "from glow_persistence.models import RecommendationEntry\n\n\n"
        "def lock(batch_id):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update(of=('self', 'candidate'))\n"
        "        .filter(batch_id=batch_id, candidate__state='active')\n"
        "    )\n"
    ),
    "of_the_batch_account": (
        "from glow_persistence.models import RecommendationEntry\n\n\n"
        "def lock(batch_id):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update(of=('batch__account',))\n"
        "        .filter(batch__account__state='active')\n"
        "    )\n"
    ),
}


# C3 (DM-67; C2's delta re-review's L1): a generic lock with a join passes only with no_key=True;
# an of= does not make it pass, since the model can be AppAccount. The review's helper.
L1_HELPER = (
    "def _lock(model, pk):\n"
    "    return (\n"
    "        model.objects.select_related('account')\n"
    "        .select_for_update({mode})\n"
    "        .filter(pk=pk)\n"
    "        .first()\n"
    "    )\n"
)
# C3 (L2): the joins C2's scan did not see; each locks a joined account row FOR UPDATE.
PLANTED_L2 = {
    "q_in_a_variable": (
        "from django.db.models import Q\n"
        "from glow_persistence.models import Block\n\n\n"
        "def lock(pk):\n"
        "    condition = Q(target__state='active')\n"
        "    return Block.objects.select_for_update().filter(condition).first()\n"
    ),
    "f_in_a_variable": (
        "from django.db.models import F\n"
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    state = F('account_low__state')\n"
        "    return Match.objects.select_for_update().filter(pk=pk, state=state).first()\n"
    ),
    "q_from_a_helper": (
        "from django.db.models import Q\n"
        "from glow_persistence.models import RecommendationEntry\n\n\n"
        "def _active():\n"
        "    return Q(candidate__state='active')\n\n\n"
        "def lock(batch_id):\n"
        "    rows = RecommendationEntry.objects.select_for_update()\n"
        "    return list(rows.filter(_active(), batch_id=batch_id))\n"
    ),
    "latest_through_the_account": (
        "from glow_persistence.models import Profile\n\n\n"
        "def lock():\n"
        "    return (\n"
        "        Profile.objects.select_for_update()\n"
        "        .filter(state='visible')\n"
        "        .latest('account__created_at')\n"
        "    )\n"
    ),
    "extra_tables": (
        "from glow_persistence.models import Profile\n\n\n"
        "def lock(pk):\n"
        "    return (\n"
        "        Profile.objects.select_for_update()\n"
        "        .extra(tables=['glow_persistence_appaccount'])\n"
        "        .filter(pk=pk)\n"
        "        .first()\n"
        "    )\n"
    ),
    "a_join_two_variables_after_the_lock": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    rows = Match.objects.select_for_update()\n"
        "    narrowed = rows.filter(pk=pk)\n"
        "    ordered = narrowed.order_by('account_low__created_at')\n"
        "    return ordered.first()\n"
    ),
    "a_reverse_path_to_the_account": (
        "from django.contrib.auth.models import User\n\n\n"
        "def lock(account_id):\n"
        "    return User.objects.select_for_update().filter(appaccount=account_id).first()\n"
    ),
    "sql_join_placeholder": (
        "def lock(cursor, table, pk):\n"
        "    cursor.execute(\n"
        "        f'SELECT m.id FROM glow_persistence_match m JOIN {table} a'\n"
        "        ' ON a.id = m.account_low_id WHERE m.id = %s FOR UPDATE',\n"
        "        [pk],\n"
        "    )\n"
    ),
    "sql_named_format_field": (
        "def lock(cursor, table, pk):\n"
        "    cursor.execute(\n"
        "        'SELECT id FROM {table} WHERE id = %s FOR UPDATE'.format(table=table), [pk]\n"
        "    )\n"
    ),
    "sql_a_clause_of_its_own": (
        "LOCK = ' FOR UPDATE'\n\n\n"
        "def lock(cursor, table, pk):\n"
        "    cursor.execute('SELECT id FROM ' + table + ' WHERE id = %s' + LOCK, [pk])\n"
    ),
}
# Further forms C3's rules refuse: a path method's argument that is not a string literal, an
# expression method's argument, * arguments, a Q combined with another given positionally, a
# chain followed back through the variables it was assigned from, and SQL formatted with % or
# joined to another string.
PLANTED_L2_MORE = {
    "a_path_held_in_a_variable": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock(field):\n"
        "    return Match.objects.select_for_update().order_by(field).first()\n"
    ),
    "annotate": (
        "from django.db.models import Count\n"
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    rows = Match.objects.select_for_update().annotate(n=Count('pk'))\n"
        "    return rows.filter(pk=pk).first()\n"
    ),
    "starred": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock(conditions):\n"
        "    return Match.objects.select_for_update().filter(*conditions).first()\n"
    ),
    "combined_qs": (
        "from django.db.models import Q\n"
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    rows = Match.objects.select_for_update()\n"
        "    return rows.filter(Q(pk=pk) | Q(state='active')).first()\n"
    ),
    "assigned_before_the_lock": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    first = Match.objects.filter(account_high__state='active')\n"
        "    second = first.filter(pk=pk)\n"
        "    return second.select_for_update().first()\n"
    ),
    "a_q_in_a_q_in_a_variable": (
        "from django.db.models import Q\n"
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    inner = Q(account_low__state='active')\n"
        "    outer = Q(inner, pk=pk)\n"
        "    return Match.objects.select_for_update().filter(outer).first()\n"
    ),
    "sql_percent": (
        "def lock(cursor, table, pk):\n"
        "    cursor.execute('SELECT id FROM %s WHERE id = 1 FOR UPDATE' % table)\n"
    ),
    "sql_joined": (
        "def lock(cursor, more, pk):\n"
        "    cursor.execute(\n"
        "        'SELECT id FROM glow_persistence_match WHERE id = %s FOR UPDATE' + more, [pk]\n"
        "    )\n"
    ),
    "sql_a_subquery_after_from": (
        "def lock(cursor, pk):\n"
        "    cursor.execute(\n"
        "        'SELECT id FROM (SELECT id FROM glow_persistence_match) m'\n"
        "        ' WHERE id = %s FOR UPDATE',\n"
        "        [pk],\n"
        "    )\n"
    ),
}
# What C3's rules still pass: a keyword's value that is a value, a Q held in a variable that
# follows no relation, string paths that follow none, and complete SQL naming its own tables.
ACCEPTED_L2 = {
    "a_keyword_value": (
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk, state):\n"
        "    rows = Match.objects.select_for_update()\n"
        "    found = rows.filter(pk=pk, state=state)\n"
        "    return found.order_by('-created_at').first()\n"
    ),
    "a_q_in_a_variable_with_no_join": (
        "from django.db.models import Q\n"
        "from glow_persistence.models import Match\n\n\n"
        "def lock(pk):\n"
        "    condition = Q(pk=pk, state__in=['active'])\n"
        "    return Match.objects.select_for_update().filter(condition).latest('created_at')\n"
    ),
    "complete_sql": (
        "def lock(cursor, pk):\n"
        "    cursor.execute(\n"
        "        'SELECT m.id FROM glow_persistence_match m'\n"
        "        ' JOIN glow_persistence_chatbinding b ON b.match_id = m.id'\n"
        "        ' WHERE m.id = %s FOR UPDATE',\n"
        "        [pk],\n"
        "    )\n"
    ),
    "no_key_with_a_reverse_path": (
        "from django.contrib.auth.models import User\n\n\n"
        "def lock(account_id):\n"
        "    rows = User.objects.select_for_update(no_key=True)\n"
        "    return rows.filter(appaccount=account_id).first()\n"
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
        # C2 (DM-65): services/api's 47 select_for_update calls and the reference design's 5; none
        # locks a queryset that joins another table.
        self.assertEqual(account_lock_scan.calls([API_ROOT]), (47, 0))
        self.assertEqual(account_lock_scan.calls([account_lock_scan.REFERENCE]), (5, 0))

    def test_the_account_foreign_keys_are_read_from_the_models(self) -> None:
        model = account_lock_scan.read_models()
        self.assertEqual(
            model.account_fields,
            {
                "account",
                "actor",
                "target",
                "candidate",
                "viewer",
                "account_low",
                "account_high",
                "reporter",
                "subject",
                "appellant",
            },
        )
        self.assertLessEqual(model.account_fields | {"batch", "binding", "match"}, model.relations)

    def test_a_lock_of_a_queryset_that_joins_fails_the_scan(self) -> None:
        # C2's three planted joins (the brief's item 3), with the further forms the rule covers.
        for name, text in {**PLANTED_JOINS, **PLANTED_JOINS_MORE, **PLANTED_OF}.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual(len(locks), 1)
                self.assertEqual(
                    [lock.mode for lock in account_lock_scan.violations(locks)], ["FOR UPDATE"]
                )
                self.assertTrue(locks[0].joins)

    def test_a_joining_lock_passes_with_no_key_or_an_of_naming_no_account(self) -> None:
        for name, text in ACCEPTED_JOINS.items():
            with self.subTest(accepted=name):
                locks = self.scan_source(text)
                self.assertEqual(account_lock_scan.violations(locks), [])
        self.assertEqual(
            [lock.mode for lock in self.scan_source(ACCEPTED_JOINS["of_self"])],
            ["FOR UPDATE OF self"],
        )
        self.assertEqual(
            [lock.mode for lock in self.scan_source(ACCEPTED_JOINS["no_key"])],
            ["FOR NO KEY UPDATE"],
        )
        self.assertEqual(self.scan_source(ACCEPTED_JOINS["lookups_only"]), [])

    def test_the_command_exits_non_zero_on_a_planted_join(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(PLANTED_JOINS["lookup_through_another_model"], encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = account_lock_scan.main([str(path)])
        self.assertEqual(code, 1)
        self.assertIn("joins through filter: batch__account__state", out.getvalue())
        self.assertIn("locking a queryset that joins: 1", out.getvalue())
        self.assertIn("not FOR NO KEY UPDATE: 1", out.getvalue())

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

    def test_the_reverse_names_of_the_accounts_own_relations_are_read(self) -> None:
        # C3 (L2): AppAccount's one relation field, auth_user, has no related name.
        self.assertEqual(account_lock_scan.read_models().reverse, {"appaccount"})

    def test_a_generic_lock_with_a_join_passes_only_with_no_key(self) -> None:
        # C3 (L1): the review's helper, refused with of=('self',), passes with no_key=True.
        refused = self.scan_source(L1_HELPER.format(mode="of=('self',)"))
        self.assertEqual([(lock.kind, lock.mode) for lock in refused], [("generic", "FOR UPDATE")])
        self.assertEqual(len(account_lock_scan.violations(refused)), 1)
        self.assertTrue(refused[0].joins)
        passed = self.scan_source(L1_HELPER.format(mode="no_key=True"))
        self.assertEqual([lock.mode for lock in passed], ["FOR NO KEY UPDATE"])
        self.assertEqual(account_lock_scan.violations(passed), [])

    def test_the_joins_c2_did_not_see_fail_the_scan(self) -> None:
        # C3 (L2): each form the delta re-review planted, and the further forms the rules cover.
        for name, text in {**PLANTED_L2, **PLANTED_L2_MORE}.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual(len(locks), 1)
                self.assertEqual(
                    [lock.mode for lock in account_lock_scan.violations(locks)], ["FOR UPDATE"]
                )
                if locks[0].kind != "sql":
                    self.assertTrue(locks[0].joins)

    def test_values_paths_with_no_join_and_complete_sql_still_pass(self) -> None:
        for name, text in ACCEPTED_L2.items():
            with self.subTest(accepted=name):
                self.assertEqual(account_lock_scan.violations(self.scan_source(text)), [])
        self.assertEqual(self.scan_source(ACCEPTED_L2["a_keyword_value"]), [])
        self.assertEqual(self.scan_source(ACCEPTED_L2["complete_sql"]), [])

    def test_the_sql_rule_reads_each_from_and_join(self) -> None:
        names = account_lock_scan.names_its_tables
        self.assertTrue(names("SELECT id FROM glow_persistence_match WHERE id = %s FOR UPDATE"))
        self.assertTrue(names('SELECT 1 FROM "glow_persistence_match" m JOIN x.y ON true'))
        for text in (
            "SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR UPDATE",
            "SELECT 1 FROM glow_persistence_match m JOIN {} a ON true FOR UPDATE",
            "SELECT 1 FROM {table} FOR UPDATE",
            "SELECT 1 FROM t JOIN {0} a ON true FOR UPDATE",
            " FOR UPDATE",
            "SELECT 1 FROM %s FOR UPDATE",
            "SELECT 1 FROM fn (1) FOR UPDATE",
            "SELECT 1 FROM t JOIN (SELECT 1) s ON true FOR UPDATE",
        ):
            with self.subTest(text=text):
                self.assertFalse(names(text))


# C3 (S1; DM-67): the three reads of the viewer's own account row the pages make before the probe
# point, as Django and ``tx.read_account_shared`` send them (seen in a local run).
_COLUMNS = ", ".join(
    f'"glow_persistence_appaccount"."{name}"'
    for name in (
        "id",
        "created_at",
        "updated_at",
        "version",
        "auth_user_id",
        "state",
        "eligibility_version",
        "preferences_version",
        "blocks_version",
        "session_epoch",
    )
)
_BY_KEY = (
    ' FROM "glow_persistence_appaccount" WHERE "glow_persistence_appaccount"."id" = %s'
    ' ORDER BY "glow_persistence_appaccount"."id" ASC LIMIT 1'
)
OWN_ACCOUNT_READS = {
    "the_lock": f"SELECT {_COLUMNS}{_BY_KEY} FOR NO KEY UPDATE",
    "the_shared_read": "SELECT state FROM glow_persistence_appaccount WHERE id = %s FOR SHARE",
    "the_versions": (
        'SELECT "glow_persistence_appaccount"."eligibility_version" AS "eligibility_version",'
        ' "glow_persistence_appaccount"."preferences_version" AS "preferences_version",'
        ' "glow_persistence_appaccount"."blocks_version" AS "blocks_version"' + _BY_KEY
    ),
}
VIEWER_STATEMENT = "WITH v AS (SELECT ... WHERE a.id = %(viewer)s) SELECT ..."


class PreProbeListTests(unittest.TestCase):
    """C3's list (S1; DM-67): before the probe point, a statement that reads a member table passes
    only as ``VIEWER`` bound to the viewer, or as one read of the viewer's own account row."""

    def setUp(self) -> None:
        self.viewer = str(uuid4())
        self.other = str(uuid4())

    def listed(self, sql: str, params: Any) -> bool:
        return discovery_cases.listed(sql, params, self.viewer, VIEWER_STATEMENT)

    def test_the_three_account_reads_pass(self) -> None:
        for name, sql in OWN_ACCOUNT_READS.items():
            with self.subTest(read=name):
                self.assertTrue(self.listed(sql, (UUID(self.viewer),)))
                self.assertTrue(self.listed(sql, [UUID(self.viewer)]))

    def test_viewer_passes_only_for_the_viewer(self) -> None:
        self.assertTrue(self.listed(VIEWER_STATEMENT, {"viewer": UUID(self.viewer), "today": 1}))
        self.assertFalse(self.listed(VIEWER_STATEMENT, {"viewer": UUID(self.other), "today": 1}))
        self.assertFalse(self.listed(VIEWER_STATEMENT, [UUID(self.viewer)]))

    def test_other_reads_fail(self) -> None:
        shared = OWN_ACCOUNT_READS["the_shared_read"]
        cases: dict[str, tuple[str, Any]] = {
            "another_id": (shared, [UUID(self.other)]),
            "the_viewer_and_another": (shared, [UUID(self.viewer), UUID(self.other)]),
            "an_in_list": (
                "SELECT state FROM glow_persistence_appaccount WHERE id IN (%s, %s)",
                [UUID(self.viewer), UUID(self.other)],
            ),
            "a_join": (
                "SELECT a.state FROM glow_persistence_appaccount a"
                " JOIN glow_persistence_profile p ON p.account_id = a.id WHERE a.id = %s",
                [UUID(self.viewer)],
            ),
            "a_subquery": (
                "SELECT state FROM glow_persistence_appaccount WHERE id = %s"
                " OR id IN (SELECT candidate_id FROM glow_persistence_recommendationentry)",
                [UUID(self.viewer)],
            ),
            "a_subquery_in_the_columns": (
                "SELECT (SELECT count(*) FROM glow_persistence_appaccount) FROM"
                " glow_persistence_appaccount WHERE id = %s",
                [UUID(self.viewer)],
            ),
            # C4 (N2; DM-68): an OR condition, and a join without an alias.
            "an_or_condition": (
                "SELECT state FROM glow_persistence_appaccount WHERE id = %s OR state = 'active'",
                [UUID(self.viewer)],
            ),
            "a_join_without_an_alias": (
                "SELECT glow_persistence_appaccount.state FROM glow_persistence_appaccount"
                " JOIN glow_persistence_profile"
                " ON glow_persistence_profile.account_id = glow_persistence_appaccount.id"
                " WHERE glow_persistence_appaccount.id = %s",
                [UUID(self.viewer)],
            ),
            "every_other_account": (
                "SELECT state FROM glow_persistence_appaccount WHERE id <> %s",
                [UUID(self.viewer)],
            ),
            "another_condition": (
                "SELECT state FROM glow_persistence_appaccount WHERE id = %s AND state = 'active'",
                [UUID(self.viewer)],
            ),
            "another_lock": (shared.replace("FOR SHARE", "FOR UPDATE"), [UUID(self.viewer)]),
            "a_named_parameter": (
                "SELECT state FROM glow_persistence_appaccount WHERE id = %(viewer)s",
                {"viewer": UUID(self.viewer)},
            ),
        }
        for name, (sql, params) in cases.items():
            with self.subTest(read=name):
                self.assertFalse(self.listed(sql, params))


# C4 (DM-68; C3's delta re-review's F1 to F5): the forms C3's scan passed, each locking a joined
# or an explicit account row FOR UPDATE, with the controls the rules must still pass.
_C4_IMPORTS = (
    "from django.db.models import Q, Value\n"
    "from django.db.models.functions import Coalesce, Lower\n"
    "from django.utils import timezone\n"
    "from glow_persistence.models import AppAccount, Match, Profile, RecommendationEntry\n\n\n"
)
# Item 1 (F1): a call to a capitalised name that takes a string literal, in a keyword's value.
PLANTED_F1 = {
    "lower_in_the_value": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower('account__state')).first()\n"
    ),
    "lower_assigned_to_a_name_first": (
        "def lock(pk):\n"
        "    expression = Lower('account__state')\n"
        "    return Profile.objects.select_for_update().filter(display_name=expression).first()\n"
    ),
    "coalesce": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Coalesce('account__state', Value(''))).first()\n"
    ),
}
ACCEPTED_F1 = {
    "a_value_from_a_lower_case_call": (
        "def lock(pk):\n"
        "    account = find_account(pk)\n"
        "    return Profile.objects.select_for_update().filter(pk=account.pk).first()\n"
    ),
    "now": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(pk=pk, expires_at__gt=timezone.now()).first()\n"
    ),
}
# Item 2 (F2, with DM-68's forms): a queryset that is not a plain chain.
PLANTED_F2 = {
    "and_assigned": (
        "def lock(pk):\n"
        "    locked = Match.objects.select_for_update().filter(pk=pk)\n"
        "    rows = locked & Profile.objects.filter(account__state='active')\n"
        "    return rows.first()\n"
    ),
    "and_inline": (
        "def lock(pk):\n"
        "    locked = Match.objects.select_for_update().filter(pk=pk)\n"
        "    return (locked & Profile.objects.filter(account__state='active')).first()\n"
    ),
    "xor": (
        "def lock(pk):\n"
        "    locked = Match.objects.select_for_update().filter(pk=pk)\n"
        "    return (locked ^ Profile.objects.filter(account__state='active')).first()\n"
    ),
    "an_account_lock_on_a_combination": (
        "def lock(a, b):\n"
        "    return (\n"
        "        (AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b))\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n"
    ),
    "an_account_lock_on_a_conditional": (
        "def lock(a, b, flag):\n"
        "    return (\n"
        "        (AppAccount.objects.filter(pk=a) if flag else AppAccount.objects.filter(pk=b))\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n"
    ),
    "an_account_lock_on_an_or": (
        "def lock(a):\n"
        "    return (\n"
        "        (AppAccount.objects.filter(pk=a) or AppAccount.objects.none())\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n"
    ),
    "an_account_lock_on_an_assignment_expression": (
        "def lock(a):\n"
        "    return (rows := AppAccount.objects.filter(pk=a)).select_for_update().first()\n"
    ),
}
# Further forms item 2's words name: the whole combination inline, the other part held in a name,
# a combination assigned in place, and a join in one branch of a conditional receiver.
PLANTED_F2_MORE = {
    "or_inline_with_no_name": (
        "def lock(pk):\n"
        "    return (\n"
        "        Match.objects.select_for_update().filter(pk=pk)\n"
        "        | Match.objects.filter(account_low__state='active')\n"
        "    ).first()\n"
    ),
    "the_other_part_held_in_a_name": (
        "def lock(pk):\n"
        "    joined = Profile.objects.filter(account__state='active')\n"
        "    locked = Match.objects.select_for_update().filter(pk=pk)\n"
        "    return (locked & joined).first()\n"
    ),
    "combined_in_place": (
        "def lock(pk):\n"
        "    locked = Match.objects.select_for_update().filter(pk=pk)\n"
        "    locked &= Profile.objects.filter(account__state='active')\n"
        "    return locked.first()\n"
    ),
    "a_join_in_one_branch_of_a_conditional_receiver": (
        "def lock(pk, flag):\n"
        "    return (\n"
        "        (Match.objects.filter(account_low__state='x') if flag else Match.objects.all())\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n"
    ),
}
# Item 3 (F3): complex_filter.
PLANTED_F3 = (
    "def lock(pk):\n"
    "    rows = Match.objects.select_for_update()\n"
    "    return rows.complex_filter({'account_low__state': 'active'}).first()\n"
)
ACCEPTED_F3 = (
    "def lock(pk):\n    return Match.objects.select_for_update().complex_filter(Q(pk=pk)).first()\n"
)
# Item 4 (F4): of= read only as literals.
PLANTED_F4 = {
    "an_f_string": (
        "def lock(batch_id, name):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update(of=(f'{name}',))\n"
        "        .filter(batch_id=batch_id, candidate__state='active')\n"
        "    )\n"
    ),
    "a_call": (
        "def lock(batch_id, name):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update(of=(str(name),))\n"
        "        .filter(batch_id=batch_id, candidate__state='active')\n"
        "    )\n"
    ),
    "a_starred_entry": (
        "def lock(batch_id, names):\n"
        "    return list(\n"
        "        RecommendationEntry.objects.select_for_update(of=('self', *names))\n"
        "        .filter(batch_id=batch_id, candidate__state='active')\n"
        "    )\n"
    ),
}
# Item 5 (F5): a generic lock's no_key, read by its syntax.
F5_HELPER = (
    "def _lock(model, other, flag, pk):\n"
    "    rows = model.objects.select_for_update(no_key={no_key})\n"
    "    return rows.filter(pk=pk).first()\n"
)
PLANTED_F5 = {
    "is_not": "model is not AppAccount",
    "not": "not (model is AppAccount)",
    "another_variable": "other is AppAccount",
    "inside_an_and": "model is AppAccount and flag",
    "reversed": "AppAccount is model",
    "inside_an_or": "model is AppAccount or flag",
}
F5_ASSIGNED = (
    "def _lock(model, pk):\n"
    "    flag = model is AppAccount\n"
    "    return model.objects.select_for_update(no_key=flag).filter(pk=pk).first()\n"
)


class LockScanC4Tests(unittest.TestCase):
    """C4's rules (DM-68; the brief's "Stage A, correction C4", items 1 to 5): each planted form is
    refused as ``FOR UPDATE``, and each control passes."""

    def scan_source(self, text: str) -> list[account_lock_scan.Lock]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(_C4_IMPORTS + text, encoding="utf-8")
            return account_lock_scan.scan([path])

    def assert_refused(self, text: str, kind: str, joins: bool = True) -> None:
        locks = self.scan_source(text)
        self.assertEqual(len(locks), 1)
        self.assertEqual([(lock.kind, lock.mode) for lock in locks], [(kind, "FOR UPDATE")])
        self.assertEqual(len(account_lock_scan.violations(locks)), 1)
        self.assertEqual(bool(locks[0].joins), joins)

    def test_a_function_given_a_path_in_a_keywords_value_is_a_join(self) -> None:
        # Item 1 (F1).
        for name, text in PLANTED_F1.items():
            with self.subTest(planted=name):
                self.assert_refused(text, "join")
                self.assertIn(
                    "filter: an argument the scan cannot read", self.scan_source(text)[0].joins
                )
        for name, text in ACCEPTED_F1.items():
            with self.subTest(accepted=name):
                self.assertEqual(self.scan_source(text), [])

    def test_a_queryset_that_is_not_a_plain_chain_is_read_through(self) -> None:
        # Item 2 (F2, with DM-68's forms): the joins of every part count, and an account lock on
        # a combination, a conditional, an or or an assignment expression is an account lock.
        for name, text in {**PLANTED_F2, **PLANTED_F2_MORE}.items():
            with self.subTest(planted=name):
                kind = "orm" if name.startswith("an_account_lock") else "join"
                self.assert_refused(text, kind, joins=kind == "join")

    def test_an_account_lock_on_a_combination_passes_with_no_key(self) -> None:
        text = PLANTED_F2["an_account_lock_on_a_combination"].replace(
            ".select_for_update()", ".select_for_update(no_key=True)"
        )
        locks = self.scan_source(text)
        self.assertEqual([(lock.kind, lock.mode) for lock in locks], [("orm", "FOR NO KEY UPDATE")])
        self.assertEqual(account_lock_scan.violations(locks), [])

    def test_complex_filter_takes_only_a_q(self) -> None:
        # Item 3 (F3).
        self.assert_refused(PLANTED_F3, "join")
        self.assertEqual(self.scan_source(ACCEPTED_F3), [])

    def test_of_is_read_only_as_literals(self) -> None:
        # Item 4 (F4).
        for name, text in PLANTED_F4.items():
            with self.subTest(planted=name):
                self.assert_refused(text, "join")
        literal = PLANTED_F4["an_f_string"].replace("(f'{name}',)", "('self',)")
        self.assertEqual([lock.mode for lock in self.scan_source(literal)], ["FOR UPDATE OF self"])

    def test_a_generic_locks_no_key_is_read_by_its_syntax(self) -> None:
        # Item 5 (F5): only True, or exactly `<the lock's own variable> is AppAccount`.
        for name, no_key in PLANTED_F5.items():
            with self.subTest(planted=name):
                self.assert_refused(F5_HELPER.format(no_key=no_key), "generic", joins=False)
        self.assert_refused(F5_ASSIGNED, "generic", joins=False)
        for no_key in ("model is AppAccount", "True", "(model is AppAccount)"):
            with self.subTest(accepted=no_key):
                locks = self.scan_source(F5_HELPER.format(no_key=no_key))
                self.assertEqual([lock.mode for lock in locks], ["FOR NO KEY UPDATE"])


# C4 (F6; DM-68): the statements a page by cursor sends, as the local run recorded them (their
# text, never a parameter), with the real VIEWER and RECHECK; and the writes the check must see.
def _predicates() -> Any:
    if str(API_ROOT) not in sys.path:
        sys.path.insert(0, str(API_ROOT))
    return importlib.import_module("glow_discovery.predicates")


CURSOR_PAGE_READS = {
    "the_backend_read": "SELECT pg_backend_pid(), now()",
    "the_clock": "SELECT clock_timestamp()",
    "the_shared_account_read": OWN_ACCOUNT_READS["the_shared_read"],
    "the_versions": OWN_ACCOUNT_READS["the_versions"],
    "a_pointer_read": (
        "SELECT id, policy_version, artifact_ref FROM glow_persistence_policyrevision"
        " WHERE name = %s FOR SHARE"
    ),
    "a_batch_read": (
        'SELECT "glow_persistence_recommendationbatch"."id",'
        ' "glow_persistence_recommendationbatch"."updated_at"'
        ' FROM "glow_persistence_recommendationbatch"'
        ' WHERE "glow_persistence_recommendationbatch"."id" = %s'
        ' ORDER BY "glow_persistence_recommendationbatch"."id" ASC LIMIT 1'
    ),
    "a_photo_owner_read": (
        'SELECT "glow_persistence_mediaasset"."account_id" AS "account_id"'
        ' FROM "glow_persistence_mediaasset" WHERE "glow_persistence_mediaasset"."id" = %s'
        ' ORDER BY "glow_persistence_mediaasset"."id" ASC LIMIT 1'
    ),
    "a_lower_case_read": "  select 1 from glow_persistence_match where id = %s for share",
}
WRITES = {
    "update_auth_user": "UPDATE auth_user SET is_active = is_active WHERE id = -1",
    "update_only": 'UPDATE ONLY "glow_persistence_recommendationbatch" SET "state" = %s',
    "a_schema_qualified_update": "UPDATE public.glow_persistence_match SET state = state",
    "insert_into": 'INSERT INTO "glow_persistence_recommendationbatch" ("id") VALUES (%s)',
    "delete_from": "DELETE FROM glow_persistence_block WHERE id = %s",
    "a_with_holding_an_update": (
        "WITH t AS (UPDATE glow_persistence_match SET state = state RETURNING id) SELECT * FROM t"
    ),
    "select_into": "SELECT * INTO scratch FROM glow_persistence_match",
    "a_writers_row_lock": (
        "SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR NO KEY UPDATE"
    ),
    "for_update": "SELECT id FROM glow_persistence_match WHERE id = %s FOR UPDATE",
    "call": "CALL refresh_everything()",
    "truncate": "TRUNCATE glow_persistence_block",
    "merge": "MERGE INTO glow_persistence_match m USING t ON true WHEN MATCHED THEN DO NOTHING",
    "copy": "COPY glow_persistence_match FROM STDIN",
    "a_savepoint": 'SAVEPOINT "s1"',
    "set": "SET search_path TO public",
}


class WriteCheckTests(unittest.TestCase):
    """C4's write check (F6; DM-68): a statement is a read only if it begins with ``SELECT`` or
    ``WITH`` and holds none of ``INSERT``, ``UPDATE``, ``DELETE``, ``MERGE``, ``INTO``,
    ``TRUNCATE`` or ``COPY``; anything else is a write."""

    def test_the_statements_a_page_by_cursor_sends_are_reads(self) -> None:
        predicates = _predicates()
        reads = {**CURSOR_PAGE_READS, "viewer": predicates.VIEWER, "recheck": predicates.RECHECK}
        for name, sql in reads.items():
            with self.subTest(read=name):
                self.assertFalse(discovery_cases.is_write(sql))

    def test_anything_but_a_read_is_a_write(self) -> None:
        for name, sql in WRITES.items():
            with self.subTest(write=name):
                self.assertTrue(discovery_cases.is_write(sql))

    def test_the_words_are_whole_words(self) -> None:
        # A column such as updated_at or a table such as glow_persistence_copy... is not a word.
        self.assertFalse(
            discovery_cases.is_write('SELECT "t"."updated_at", "t"."into_x" FROM "t" WHERE id = %s')
        )
        self.assertTrue(discovery_cases.is_write("SELECTED FROM t"))
