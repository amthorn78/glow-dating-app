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
PROOF = Path(__file__).resolve().parents[1] / "glow_ordering_proof"
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
    def test_the_plan_covers_stage_as_and_stage_bs_acceptance_checks(self) -> None:
        # Rewritten by SV3 Stage B's item 6 (DM-73): Stage B's checks 7 to 11 are now covered by
        # its cases, and Stage A's still are.
        plan = discovery_cases.plan()
        self.assertEqual(len(plan), len(set(plan)))
        covered = {check for entry in discovery_cases.CASES for check in entry.checks}
        for check in ("1", "2", "3", "4", "5", "6", "12", "13", "14"):
            with self.subTest(check=check):
                self.assertIn(check, covered)
        for decision in ("D2", "D3", "D4", "D5", "D6", "D7", "D8", "D13", "D14", "D19", "DB04"):
            with self.subTest(decision=decision):
                self.assertIn(decision, covered)
        stage_b = {
            check
            for entry in discovery_cases.CASES
            if entry.case_id in STAGE_B_CASES
            for check in entry.checks
        }
        for check in ("7", "8", "9", "10", "11", "12", "13", "14", "15"):
            with self.subTest(stage_b_check=check):
                self.assertIn(check, stage_b)
        for decision in ("D9", "D10", "D11", "D12", "D13", "D14", "D19", "DB04", "DB05", "DB10"):
            with self.subTest(stage_b_decision=decision):
                self.assertIn(decision, stage_b)
        # Stage A's cases cover none of Stage B's checks 7 to 11.
        stage_a = {
            check
            for entry in discovery_cases.CASES
            if entry.case_id not in STAGE_B_CASES
            for check in entry.checks
        }
        for check in ("7", "8", "9", "10", "11"):
            self.assertNotIn(check, stage_a)

    def test_the_case_count_is_pinned(self) -> None:
        # Re-pinned by SV3 Stage B's item 6 (DM-73): Stage A's 40, and Stage B's 19 named below.
        self.assertEqual(discovery_cases.CASE_COUNT, 59)
        self.assertEqual(len(discovery_cases.plan()), discovery_cases.CASE_COUNT)
        # C2's two new cases (the exact-head review's F1 and F2).
        for case_id in ("pages.one_snapshot_statements", "distance.choice_no_longer_offered"):
            self.assertIn(case_id, discovery_cases.plan())
        self.assertEqual(discovery_cases.plan()[40:], STAGE_B_CASES)

    def test_the_routes_are_the_apis(self) -> None:
        # Rewritten by SV3 Stage B's item 6 (DM-73): the exact routes Stage A's and Stage B's URL
        # modules declare, and the suite's URL configuration serves both.
        declared: dict[str, set[str]] = {}
        for module in ("urls.py", "interaction_urls.py"):
            tree = ast.parse((API_ROOT / "glow_discovery" / module).read_text(encoding="utf-8"))
            declared[module] = {
                str(node.args[0].value)
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "path"
                and isinstance(node.args[0], ast.Constant)
            }
        self.assertEqual(
            declared,
            {
                "urls.py": {"api/v1/discovery/page"},
                "interaction_urls.py": {
                    "api/v1/discovery/interaction",
                    "api/v1/discovery/interaction/undo",
                    "api/v1/matches/unmatch",
                    "api/v1/matches/<uuid:match_id>",
                    "api/v1/blocks",
                },
            },
        )
        from glow_ordering_proof import discovery_support, interaction_cases

        self.assertEqual(discovery_support.PAGE, "/api/v1/discovery/page")
        self.assertEqual(
            (
                interaction_cases.INTERACTION,
                interaction_cases.UNDO,
                interaction_cases.UNMATCH,
                interaction_cases.BLOCKS,
                interaction_cases.MATCHES,
            ),
            (
                "/api/v1/discovery/interaction",
                "/api/v1/discovery/interaction/undo",
                "/api/v1/matches/unmatch",
                "/api/v1/blocks",
                "/api/v1/matches",
            ),
        )
        served = ast.parse((PROOF / "discovery_urls.py").read_text(encoding="utf-8"))
        names = {
            node.value.id
            for node in ast.walk(served)
            if isinstance(node, ast.Starred) and isinstance(node.value, ast.Name)
        }
        self.assertEqual(
            names, {"identity_routes", "profile_routes", "discovery_routes", "interaction_routes"}
        )


# SV3 Stage B's cases, in the order the suite runs them, after Stage A's 40.
STAGE_B_CASES = (
    "row_locks.driver_forms_are_seen",
    "interactions.like_and_pass_are_idempotent",
    "interactions.stale_and_ineligible_are_refused",
    "interactions.unreciprocated_like_is_hidden",
    "interactions.pass_over_like_is_refused",
    "match.reciprocal_likes_make_one_match",
    "match.no_route_creates_a_match",
    "match.activate_reciprocal_refuses_what_activate_match_refuses",
    "concurrency.reciprocal_likes_at_once",
    "concurrency.changes_during_a_like_are_seen",
    "unmatch.revokes_contact_and_never_rematches",
    "block.works_after_unmatch_and_while_paused",
    "settings.resurfacing_off_and_on",
    "settings.undo_off_and_on",
    "settings.rematch_cannot_be_switched_on",
    "routes.interaction_refusals_and_ownership",
    "constraints.interaction_writes_are_refused",
    "interactions.logs_no_private_value",
    "interactions.pointer_order",
)


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
# Found by C4's own probes (forms item 2's and item 5's words name, which C3's scan and C4's first
# commit passed): a combination assigned in place with the lock on its right; a lock on a name
# that holds an account combination, conditional or in-place combination; and a model held in a
# variable whose name begins with an underscore.
PLANTED_C4_PROBES = {
    "combined_in_place_the_lock_on_the_right": (
        "join",
        "def lock(pk):\n"
        "    rows = Match.objects.filter(account_low__state='active')\n"
        "    rows |= Match.objects.select_for_update().filter(pk=pk)\n"
        "    return rows.first()\n",
    ),
    "combined_in_place_the_lock_on_the_right_a_join_after": (
        "join",
        "def lock(pk):\n"
        "    rows = Match.objects.none()\n"
        "    rows |= Match.objects.select_for_update().filter(pk=pk)\n"
        "    return rows.filter(account_low__state='active').first()\n",
    ),
    "a_name_holding_an_account_combination": (
        "orm",
        "def lock(a, b):\n"
        "    rows = AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)\n"
        "    return rows.select_for_update(no_key=rows is AppAccount).first()\n",
    ),
    "a_name_holding_an_account_conditional": (
        "orm",
        "def lock(a, b, flag):\n"
        "    rows = AppAccount.objects.filter(pk=a) if flag else AppAccount.objects.filter(pk=b)\n"
        "    return rows.select_for_update(no_key=rows is AppAccount).first()\n",
    ),
    "a_name_holding_an_account_combination_in_place": (
        "orm",
        "def lock(a, b):\n"
        "    rows = AppAccount.objects.filter(pk=a)\n"
        "    rows |= AppAccount.objects.filter(pk=b)\n"
        "    return rows.select_for_update(no_key=rows is AppAccount).first()\n",
    ),
    "an_underscore_variable_is_not": (
        "generic",
        "def _lock(_model, pk):\n"
        "    rows = _model.objects.select_for_update(no_key=_model is not AppAccount)\n"
        "    return rows.filter(pk=pk).first()\n",
    ),
    "an_underscore_variable_with_no_no_key": (
        "generic",
        "def _lock(_model, pk):\n"
        "    return _model.objects.select_for_update().filter(pk=pk).first()\n",
    ),
    "an_underscore_variable_with_a_join_and_of": (
        "generic",
        "def _lock(_model, pk):\n"
        "    return (\n"
        "        _model.objects.select_related('account')\n"
        "        .select_for_update(of=('self',))\n"
        "        .filter(pk=pk)\n"
        "        .first()\n"
        "    )\n",
    ),
}
ACCEPTED_C4_PROBES = {
    "an_underscore_helper": (
        "def _lock(_model, pk):\n"
        "    rows = _model.objects.select_for_update(no_key=_model is AppAccount)\n"
        "    return rows.filter(pk=pk).first()\n"
    ),
    "a_name_holding_an_account_combination_with_no_key": (
        "def lock(a, b):\n"
        "    rows = AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)\n"
        "    return rows.select_for_update(no_key=True).first()\n"
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

    def test_the_forms_c4s_probes_found_are_refused(self) -> None:
        # Item 2 (in place, the lock on the right; a receiver held in a name) and item 5 (a
        # variable whose name begins with an underscore).
        for name, (kind, text) in PLANTED_C4_PROBES.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual(len(locks), 1)
                self.assertEqual((locks[0].kind, locks[0].mode), (kind, "FOR UPDATE"))
                self.assertEqual(len(account_lock_scan.violations(locks)), 1)
        for name, text in ACCEPTED_C4_PROBES.items():
            with self.subTest(accepted=name):
                locks = self.scan_source(text)
                self.assertEqual(len(locks), 1)
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


# C5 (DM-69; C4's delta re-review's F1): a lock's receiver name, followed through every plain
# assignment. Each form locks account rows FOR UPDATE at run time: its name holds a queryset, so
# `x is AppAccount` is false.
_C5_IMPORTS = _C4_IMPORTS.replace("import Q, Value", "import F, Q, Value")
_C5_COMBINATION = "    c = AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)\n"
_C5_LOCK = "    return {name}.select_for_update(no_key={name} is AppAccount).first()\n"
PLANTED_C5_RECEIVERS = {
    "d_is_c": "def lock(a, b):\n" + _C5_COMBINATION + "    d = c\n" + _C5_LOCK.format(name="d"),
    "d_is_c_filtered": (
        "def lock(a, b):\n"
        + _C5_COMBINATION
        + "    d = c.filter(pk=a)\n"
        + _C5_LOCK.format(name="d")
    ),
    "d_is_c_sliced": (
        "def lock(a, b):\n" + _C5_COMBINATION + "    d = c[:5]\n" + _C5_LOCK.format(name="d")
    ),
    "d_is_rows_all_after_rows_combined_in_place": (
        "def lock(a, b):\n"
        "    rows = AppAccount.objects.filter(pk=a)\n"
        "    rows |= AppAccount.objects.filter(pk=b)\n"
        "    d = rows.all()\n" + _C5_LOCK.format(name="d")
    ),
    "three_hops": (
        "def lock(a, b):\n"
        + _C5_COMBINATION
        + "    d = c\n    e = d\n    f = e\n"
        + _C5_LOCK.format(name="f")
    ),
    "two_hops_from_an_account_conditional": (
        "def lock(a, b, flag):\n"
        "    c = AppAccount.objects.filter(pk=a) if flag else AppAccount.objects.filter(pk=b)\n"
        "    d = c\n" + _C5_LOCK.format(name="d")
    ),
    "two_hops_from_an_assignment_expression": (
        "def lock(a):\n"
        "    c = (rows := AppAccount.objects.filter(pk=a))\n"
        "    d = c\n" + _C5_LOCK.format(name="d")
    ),
}
# Forms beyond the brief's examples that item 1's words name: an annotated assignment and a `:=`
# as the plain assignment that passes the name on, and a hop through a combination in place.
PLANTED_C5_RECEIVERS_MORE = {
    "an_annotated_assignment": (
        "def lock(a, b):\n" + _C5_COMBINATION + "    d: object = c\n" + _C5_LOCK.format(name="d")
    ),
    "an_assignment_expression_passes_it_on": (
        "def lock(a, b):\n"
        + _C5_COMBINATION
        + "    if (d := c) is None:\n        return None\n"
        + _C5_LOCK.format(name="d")
    ),
    "a_name_combined_in_place_two_hops_back": (
        "def lock(a, b):\n"
        "    rows = AppAccount.objects.filter(pk=a)\n"
        "    rows &= AppAccount.objects.filter(pk=b)\n"
        "    d = rows\n    e = d.order_by('pk')\n" + _C5_LOCK.format(name="e")
    ),
    "a_chain_starting_from_a_combination": (
        "def lock(a, b):\n"
        "    c = (AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)).filter(pk=a)\n"
        "    d = c\n" + _C5_LOCK.format(name="d")
    ),
    "the_combination_in_a_later_assignment": (
        "def lock(a, b, flag):\n"
        "    c = Match.objects.none()\n"
        "    if flag:\n"
        "        c = AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)\n"
        "    d = c\n" + _C5_LOCK.format(name="d")
    ),
    "a_name_re_assigned_from_itself": (
        "def lock(a, b):\n"
        + _C5_COMBINATION
        + "    c = c.filter(pk=a)\n    d = c\n"
        + _C5_LOCK.format(name="d")
    ),
    "a_composite_receiver_whose_later_part_holds_one": (
        "def lock(a, b, flag):\n"
        + _C5_COMBINATION
        + "    return (Match.objects.all() if flag else c).select_for_update(\n"
        "        no_key=c is AppAccount\n"
        "    ).first()\n"
    ),
}


class LockScanC5Tests(unittest.TestCase):
    """C5's rule (DM-69; the brief's "Stage A, correction C5", item 1): a lock's receiver name is
    followed through every plain assignment, transitively, to an account combination,
    conditional, boolean or assignment expression; each chain it holds is judged as the
    receiver."""

    def scan_source(self, text: str) -> list[account_lock_scan.Lock]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(_C5_IMPORTS + text, encoding="utf-8")
            return account_lock_scan.scan([path])

    def test_a_receiver_name_is_followed_through_every_plain_assignment(self) -> None:
        for name, text in {**PLANTED_C5_RECEIVERS, **PLANTED_C5_RECEIVERS_MORE}.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual(
                    [(lock.kind, lock.mode) for lock in locks], [("orm", "FOR UPDATE")]
                )
                self.assertEqual(len(account_lock_scan.violations(locks)), 1)

    def test_a_variable_models_combination_held_in_a_name_is_a_generic_lock(self) -> None:
        # The model can be AppAccount, and no_key names another variable, so the lock fails.
        text = (
            "def lock(model, a, b):\n"
            "    c = model.objects.filter(pk=a) | model.objects.filter(pk=b)\n"
            "    d = c\n" + _C5_LOCK.format(name="d")
        )
        locks = self.scan_source(text)
        self.assertEqual([(lock.kind, lock.mode) for lock in locks], [("generic", "FOR UPDATE")])

    def test_the_receivers_own_chain_is_reported_first(self) -> None:
        # Where the receiver's own chain fails too (no no_key), it is the chain reported.
        text = PLANTED_C5_RECEIVERS["d_is_c"].replace("no_key=d is AppAccount", "")
        locks = self.scan_source(text)
        self.assertEqual([(lock.kind, lock.mode) for lock in locks], [("generic", "FOR UPDATE")])

    def test_chains_are_kept_once_by_what_judges_them(self) -> None:
        # _distinct keeps one chain per (AppAccount among its names, a capitalised name, a
        # variable, that variable), in written order; each of these must stay apart or in order.
        cases = {
            "a_capitalised_attribute_beside_a_variable_model": (
                "def lock(model, a, b):\n"
                "    return (\n"
                "        (model.Foo.objects.filter(pk=a) | model.objects.filter(pk=b))\n"
                "        .select_for_update()\n"
                "        .first()\n"
                "    )\n",
                ("generic", "FOR UPDATE"),
            ),
            "the_account_beside_another_model_on_one_variable": (
                "def lock(models, a, b):\n"
                "    return (\n"
                "        (\n"
                "            models.Match.objects.filter(pk=a)\n"
                "            | models.AppAccount.objects.filter(pk=b)\n"
                "        )\n"
                "        .select_for_update(no_key=models is AppAccount)\n"
                "        .first()\n"
                "    )\n",
                ("orm", "FOR UPDATE"),
            ),
            "the_first_failing_chain_in_written_order": (
                "def lock(model, other, a, b, c):\n"
                "    return (\n"
                "        (\n"
                "            AppAccount.objects.filter(pk=a)\n"
                "            | model.objects.filter(pk=b)\n"
                "            | AppAccount.objects.filter(pk=c)\n"
                "        )\n"
                "        .select_for_update(no_key=other is AppAccount)\n"
                "        .first()\n"
                "    )\n",
                ("orm", "FOR UPDATE"),
            ),
            "a_capitalised_name_holding_a_variable_models_combination": (
                "def lock(model, a, b):\n"
                "    Rows = model.objects.filter(pk=a) | model.objects.filter(pk=b)\n"
                "    return Rows.select_for_update().first()\n",
                ("generic", "FOR UPDATE"),
            ),
        }
        for name, (text, verdict) in cases.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual([(lock.kind, lock.mode) for lock in locks], [verdict])

    def test_a_followed_receiver_passes_with_no_key_true(self) -> None:
        text = PLANTED_C5_RECEIVERS["d_is_c"].replace("no_key=d is AppAccount", "no_key=True")
        locks = self.scan_source(text)
        self.assertEqual(len(locks), 1)
        self.assertEqual(account_lock_scan.violations(locks), [])

    def test_a_plain_chain_held_in_a_name_stays_a_generic_lock(self) -> None:
        # The stated limit (the README's further forms): no combination, conditional, boolean or
        # assignment expression is reached, so the lock is judged as before, as a generic lock.
        for hops in ("", "    d = c\n"):
            with self.subTest(hops=hops or "none"):
                name = "d" if hops else "c"
                text = (
                    "def lock(a):\n    c = AppAccount.objects.filter(pk=a)\n"
                    + hops
                    + _C5_LOCK.format(name=name)
                )
                locks = self.scan_source(text)
                self.assertEqual(
                    [(lock.kind, lock.mode) for lock in locks], [("generic", "FOR NO KEY UPDATE")]
                )


# C5 (N3; DM-69): tests that pin C4's branches, each failing against a mutant of C4's code that
# C4's tests left passing (C4's delta re-review's N3; the evidence record lists each mutant).
PINNED_C4_ITEM_1 = {
    "an_f_string": (
        "def lock(pk, name):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower(f'account__{name}')).first()\n"
    ),
    "an_f_string_of_fields_only": (
        "def lock(pk, name):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower(f'{name}')).first()\n"
    ),
    "a_keyword_argument": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower(expression='account__state')).first()\n"
    ),
    "an_f_string_starting_with_a_field": (
        "def lock(pk, name):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower(f'{name}__state')).first()\n"
    ),
    "an_f_string_by_keyword": (
        "def lock(pk, name):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower(expression=f'account__{name}')).first()\n"
    ),
    "a_literal_of_one_segment": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower('account')).first()\n"
    ),
    "a_class_with_an_inner_capital": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=OuterRef('account__state')).first()\n"
    ),
    "raw_sql": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=RawSQL('select 1', [])).first()\n"
    ),
    "two_keywords": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    value = Lower(expression='account__state', output_field=None)\n"
        "    return rows.filter(display_name=value).first()\n"
    ),
    "a_path_second": (
        "def lock(pk):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Coalesce(None, 'account__state')).first()\n"
    ),
    "a_star_second": (
        "def lock(pk, parts):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Coalesce(None, *parts)).first()\n"
    ),
    "a_double_star_after_a_keyword": (
        "def lock(pk, parts):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Coalesce(output_field=None, **parts)).first()\n"
    ),
    "a_double_star_after_a_positional": (
        "def lock(pk, parts):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Coalesce(None, **parts)).first()\n"
    ),
    "a_starred_argument": (
        "def lock(pk, parts):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Lower(*parts)).first()\n"
    ),
    "a_double_starred_argument": (
        "def lock(pk, parts):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    return rows.filter(display_name=Coalesce(**parts)).first()\n"
    ),
}
PINNED_C4_ITEM_2 = {
    "the_lock_in_a_conditional": (
        "join",
        "def lock(pk, flag):\n"
        "    return (\n"
        "        Match.objects.select_for_update().filter(pk=pk)\n"
        "        if flag\n"
        "        else Profile.objects.filter(account__state='active')\n"
        "    ).first()\n",
    ),
    "the_lock_in_an_or": (
        "join",
        "def lock(pk):\n"
        "    return (\n"
        "        Match.objects.select_for_update().filter(pk=pk)\n"
        "        or Profile.objects.filter(account__state='active')\n"
        "    ).first()\n",
    ),
    "a_combination_inside_the_receivers_chain": (
        "orm",
        "def lock(a, b):\n"
        "    return (\n"
        "        (AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b))\n"
        "        .filter(pk=a)\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_lock_in_the_else_branch": (
        "join",
        "def lock(pk, flag):\n"
        "    return (\n"
        "        Profile.objects.filter(account__state='active')\n"
        "        if flag\n"
        "        else Match.objects.select_for_update().filter(pk=pk)\n"
        "    ).first()\n",
    ),
    "a_join_after_the_conditional": (
        "join",
        "def lock(pk, flag):\n"
        "    return (\n"
        "        Match.objects.select_for_update().filter(pk=pk)\n"
        "        if flag\n"
        "        else Match.objects.none()\n"
        "    ).filter(account_low__state='active').first()\n",
    ),
    "a_join_after_the_conditional_held_in_a_name": (
        "join",
        "def lock(pk, flag):\n"
        "    rows = Match.objects.select_for_update() if flag else Match.objects.none()\n"
        "    return rows.filter(account_low__state='active').first()\n",
    ),
    "the_lock_in_a_later_operand": (
        "join",
        "def lock(pk):\n"
        "    return (\n"
        "        Profile.objects.filter(account__state='active')\n"
        "        or Match.objects.select_for_update().filter(pk=pk)\n"
        "    ).first()\n",
    ),
    "a_join_after_the_or": (
        "join",
        "def lock(pk):\n"
        "    return (\n"
        "        Match.objects.select_for_update().filter(pk=pk) or Match.objects.none()\n"
        "    ).filter(account_low__state='active').first()\n",
    ),
    "a_conditional_inside_the_receivers_chain": (
        "orm",
        "def lock(a, flag):\n"
        "    return (\n"
        "        (AppAccount.objects.filter(pk=a) if flag else AppAccount.objects.none())\n"
        "        .filter(pk=a)\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "an_or_inside_the_receivers_chain": (
        "orm",
        "def lock(a):\n"
        "    return (\n"
        "        (AppAccount.objects.filter(pk=a) or AppAccount.objects.none())\n"
        "        .filter(pk=a)\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "an_assignment_expression_inside_the_receivers_chain": (
        "orm",
        "def lock(a):\n"
        "    return (\n"
        "        (rows := AppAccount.objects.filter(pk=a))\n"
        "        .filter(pk=a)\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_account_second_in_a_combination_inside_the_chain": (
        "orm",
        "def lock(a, b, model):\n"
        "    return (\n"
        "        (model.objects.filter(pk=a) | AppAccount.objects.filter(pk=b))\n"
        "        .filter(pk=a)\n"
        "        .select_for_update(no_key=model is AppAccount)\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_account_first_in_a_combination_inside_the_chain": (
        "orm",
        "def lock(a, b, model):\n"
        "    return (\n"
        "        (AppAccount.objects.filter(pk=a) | model.objects.filter(pk=b))\n"
        "        .filter(pk=a)\n"
        "        .select_for_update(no_key=model is AppAccount)\n"
        "        .first()\n"
        "    )\n",
    ),
    "a_join_in_a_conditional_receivers_else_branch": (
        "join",
        "def lock(flag):\n"
        "    return (\n"
        "        (Match.objects.all() if flag else Match.objects.filter(account_low__state='x'))\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_account_in_a_conditional_receivers_else_branch": (
        "orm",
        "def lock(model, flag):\n"
        "    return (\n"
        "        (model.objects.all() if flag else AppAccount.objects.all())\n"
        "        .select_for_update(no_key=model is AppAccount)\n"
        "        .first()\n"
        "    )\n",
    ),
    "a_join_in_an_or_receivers_later_operand": (
        "join",
        "def lock():\n"
        "    return (\n"
        "        (Match.objects.all() or Match.objects.filter(account_low__state='x'))\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "a_join_in_an_or_receivers_first_operand": (
        "join",
        "def lock():\n"
        "    return (\n"
        "        (Match.objects.filter(account_low__state='x') or Match.objects.all())\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_account_in_an_or_receivers_later_operand": (
        "orm",
        "def lock(model):\n"
        "    return (\n"
        "        (model.objects.all() or AppAccount.objects.all())\n"
        "        .select_for_update(no_key=model is AppAccount)\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_account_in_an_or_receivers_first_operand": (
        "orm",
        "def lock(model):\n"
        "    return (\n"
        "        (AppAccount.objects.all() or model.objects.all())\n"
        "        .select_for_update(no_key=model is AppAccount)\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_lock_in_an_and": (
        "join",
        "def lock(pk):\n"
        "    return (\n"
        "        Match.objects.select_for_update().filter(pk=pk)\n"
        "        and Profile.objects.filter(account__state='active')\n"
        "    ).first()\n",
    ),
    "the_lock_in_an_or_of_three": (
        "join",
        "def lock(pk):\n"
        "    return (\n"
        "        Match.objects.select_for_update().filter(pk=pk)\n"
        "        or Match.objects.none()\n"
        "        or Profile.objects.filter(account__state='active')\n"
        "    ).first()\n",
    ),
    "a_variable_models_combination_inside_the_chain": (
        "generic",
        "def lock(model, a, b):\n"
        "    return (\n"
        "        (model.objects.filter(pk=a) | model.objects.filter(pk=b))\n"
        "        .filter(pk=a)\n"
        "        .select_for_update()\n"
        "        .first()\n"
        "    )\n",
    ),
    "the_account_through_an_attribute_inside_a_combination_in_the_chain": (
        "orm",
        "def lock(models, a):\n"
        "    return (\n"
        "        (models.AppAccount.objects.filter(pk=a) | Match.objects.all())\n"
        "        .filter(pk=a)\n"
        "        .select_for_update(no_key=models is AppAccount)\n"
        "        .first()\n"
        "    )\n",
    ),
    "and_in_place_the_lock_on_the_right": (
        "join",
        "def lock(pk):\n"
        "    rows = Match.objects.filter(account_low__state='active')\n"
        "    rows &= Match.objects.select_for_update().filter(pk=pk)\n"
        "    return rows.first()\n",
    ),
    "xor_in_place_the_lock_on_the_right": (
        "join",
        "def lock(pk):\n"
        "    rows = Match.objects.filter(account_low__state='active')\n"
        "    rows ^= Match.objects.select_for_update().filter(pk=pk)\n"
        "    return rows.first()\n",
    ),
    "an_account_name_xor_in_place": (
        "orm",
        "def lock(a, b):\n"
        "    rows = AppAccount.objects.filter(pk=a)\n"
        "    rows ^= AppAccount.objects.filter(pk=b)\n"
        "    return rows.select_for_update(no_key=rows is AppAccount).first()\n",
    ),
    "combined_in_place_the_lock_on_the_right_read_after": (
        "join",
        "def lock(pk):\n"
        "    rows = Match.objects.none()\n"
        "    rows |= Match.objects.select_for_update().filter(pk=pk)\n"
        "    later = rows\n"
        "    return later.filter(account_low__state='active').first()\n",
    ),
    "combined_in_place_read_back_through_the_other_part": (
        "join",
        "def lock(pk):\n"
        "    locked = Match.objects.select_for_update().filter(pk=pk)\n"
        "    rows = Match.objects.filter(pk=pk)\n"
        "    rows |= Profile.objects.filter(account__state='active')\n"
        "    return (locked & rows).first()\n",
    ),
}
PINNED_C4_ITEM_3 = {
    "an_f": (
        "def lock(pk):\n"
        "    return Match.objects.select_for_update().complex_filter(F('pk')).first()\n"
    ),
    "an_f_by_keyword": (
        "def lock(pk):\n"
        "    return Match.objects.select_for_update().complex_filter(filter_obj=F('pk')).first()\n"
    ),
    "a_name_assigned_an_f": (
        "def lock(pk):\n"
        "    cond = F('pk')\n"
        "    return Match.objects.select_for_update().complex_filter(cond).first()\n"
    ),
    "a_name_assigned_a_q_and_a_dict": (
        "def lock(pk, flag):\n"
        "    cond = Q(pk=pk)\n"
        "    if flag:\n"
        "        cond = {'account_low__state': 'active'}\n"
        "    return Match.objects.select_for_update().complex_filter(cond).first()\n"
    ),
    "a_name_assigned_a_q_and_an_f": (
        "def lock(pk, flag):\n"
        "    cond = Q(pk=pk)\n"
        "    if flag:\n"
        "        cond = F('pk')\n"
        "    return Match.objects.select_for_update().complex_filter(cond).first()\n"
    ),
    "a_keyword_dict": (
        "def lock(pk):\n"
        "    rows = Match.objects.select_for_update()\n"
        "    return rows.complex_filter(filter_obj={'account_low__state': 'active'}).first()\n"
    ),
}
PINNED_C4_ITEM_4 = {
    "a_name_as_an_entry": "of=('self', name)",
    "a_name_as_the_whole_of": "of=names",
    "a_name_first": "of=(name, 'self')",
    "a_list_with_a_name": "of=['self', name]",
    "a_constant": "of=('self', OF_PATH)",
    "a_constant_as_the_whole_of": "of=LOCKED",
    "a_call_wrapping_a_name": "of=tuple(names)",
}
_PINNED_OF = (
    "def lock(batch_id, name, names):\n"
    "    return list(\n"
    "        RecommendationEntry.objects.select_for_update({of})\n"
    "        .filter(batch_id=batch_id, candidate__state='active')\n"
    "    )\n"
)
# Item 6: each of the seven words alone after a read's start (a text a page could send, read as
# the words say, whether or not PostgreSQL would accept it), a statement that holds a SELECT but
# does not begin with one, and the words in lower case.
PINNED_C4_ITEM_6 = {
    "insert_alone": (
        "WITH t AS (INSERT glow_persistence_block DEFAULT VALUES RETURNING id) SELECT id FROM t"
    ),
    "update_alone": "WITH t AS (UPDATE glow_persistence_match SET state = state) SELECT 1",
    "delete_alone": (
        "WITH t AS (DELETE FROM glow_persistence_block WHERE id = %s RETURNING id) SELECT id FROM t"
    ),
    "merge_alone": (
        "WITH t AS (SELECT 1 AS id) MERGE glow_persistence_match m USING t ON true"
        " WHEN MATCHED THEN DO NOTHING"
    ),
    "into_alone": "SELECT * INTO scratch FROM glow_persistence_match",
    "truncate_alone": "SELECT 1; TRUNCATE glow_persistence_block",
    "copy_alone": "SELECT 1; COPY glow_persistence_match TO STDOUT",
    "a_select_not_at_the_start": "PREPARE p AS SELECT id FROM glow_persistence_match",
    "explain": "EXPLAIN SELECT id FROM glow_persistence_match",
    "a_lower_case_delete": (
        "with t as (delete from glow_persistence_block returning id) select id from t"
    ),
    "a_lower_case_into": "select * into scratch from glow_persistence_match",
    "a_mixed_case_delete": (
        "With t AS (Delete FROM glow_persistence_block RETURNING id) SELECT id FROM t"
    ),
    "a_lower_case_truncate": "select 1; truncate glow_persistence_block",
    "a_lower_case_copy": "select 1; copy glow_persistence_match to stdout",
    "a_lower_case_merge": (
        "with t as (select 1 as id) merge glow_persistence_match m using t on true"
        " when matched then do nothing"
    ),
    "a_lower_case_insert": (
        "with t as (insert glow_persistence_block default values returning id) select id from t"
    ),
    "table": "TABLE glow_persistence_match",
    "values": "VALUES (1)",
    "prepare_on_two_lines": "PREPARE p AS\nSELECT id FROM glow_persistence_match",
    "explain_on_two_lines": "EXPLAIN\nSELECT id FROM glow_persistence_match",
    "a_write_after_quoted_text": (
        "SELECT E'it\\'s', 1; DELETE FROM glow_persistence_block; SELECT 'x'"
    ),
    "a_lower_case_write_with_a_non_ascii_value": (
        "with t as (delete from glow_persistence_block where name = '\u00e9' returning id)"
        " select id from t"
    ),
    "on_several_lines": (
        "WITH t AS (\n"
        "  UPDATE glow_persistence_match SET state = state RETURNING id\n"
        ")\nSELECT * FROM t"
    ),
}


PINNED_C4_ITEM_6_READS = {
    "a_lower_case_with": "with t as (select 1 as id) select id from t",
    "a_word_with_a_prefix": 'SELECT "t"."last_update", "t"."auto_insert" FROM "t"',
    "a_word_with_a_non_ascii_prefix": "SELECT \u00e9into FROM glow_persistence_match",
}


class PinnedC4BranchTests(unittest.TestCase):
    """C5 (N3; DM-69): C4's items 1 to 4 and 6, pinned branch by branch. No rule changes."""

    def scan_source(self, text: str) -> list[account_lock_scan.Lock]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(_C5_IMPORTS + text, encoding="utf-8")
            return account_lock_scan.scan([path])

    def assert_refused(self, text: str, kind: str) -> None:
        locks = self.scan_source(text)
        self.assertEqual([(lock.kind, lock.mode) for lock in locks], [(kind, "FOR UPDATE")])
        self.assertEqual(len(account_lock_scan.violations(locks)), 1)

    def test_item_1_each_argument_form_given_a_path_is_a_join(self) -> None:
        for name, text in PINNED_C4_ITEM_1.items():
            with self.subTest(planted=name):
                self.assert_refused(text, "join")
                self.assertIn(
                    "filter: an argument the scan cannot read", self.scan_source(text)[0].joins
                )

    def test_item_2_each_composite_branch_is_read(self) -> None:
        for name, (kind, text) in PINNED_C4_ITEM_2.items():
            with self.subTest(planted=name):
                self.assert_refused(text, kind)

    def test_item_3_complex_filter_reads_only_a_q_given_either_way(self) -> None:
        for name, text in PINNED_C4_ITEM_3.items():
            with self.subTest(planted=name):
                self.assert_refused(text, "join")
                self.assertIn(
                    "complex_filter: an argument the scan cannot read",
                    self.scan_source(text)[0].joins,
                )

    def test_item_4_a_name_in_of_fails_closed(self) -> None:
        for name, of in PINNED_C4_ITEM_4.items():
            with self.subTest(planted=name):
                self.assert_refused(_PINNED_OF.format(of=of), "join")

    def test_item_6_each_write_word_and_the_reads_start(self) -> None:
        for name, sql in PINNED_C4_ITEM_6.items():
            with self.subTest(write=name):
                self.assertTrue(discovery_cases.is_write(sql))
        # The words are whole words with their case ignored, so these stay reads.
        for name, sql in PINNED_C4_ITEM_6_READS.items():
            with self.subTest(read=name):
                self.assertFalse(discovery_cases.is_write(sql))


# SV3 Stage B, B0 (DM-70; the design DM-71 read; the brief's "Stage B, B0", items 1, 4 and 8).
_B0_IMPORTS = "from glow_persistence.models import AppAccount, Match, Profile\n\n\n"
_B0_COMBINATION = "AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)"


def names_each_assigned_from_every_other(count: int, no_key: str = "True") -> str:
    """``count`` names, the first assigned an account combination, then each assigned from every
    other (``count * (count - 1)`` assignments); the last name locked."""
    lines = ["def lock(a, b):", f"    n0 = {_B0_COMBINATION}"]
    lines += [f"    n{i} = n{j}" for i in range(count) for j in range(count) if i != j]
    lines.append(f"    return n{count - 1}.select_for_update(no_key={no_key}).first()")
    return _B0_IMPORTS + "\n".join(lines) + "\n"


def plain_hops(hops: int, no_key: str = "True") -> str:
    """An account combination, then ``hops`` plain assignments (``x1 = x0``, ...), the last name
    locked: ``hops + 1`` names followed (``AppAccount``, a model's name, counts toward neither)."""
    lines = ["def lock(a, b):", f"    x0 = {_B0_COMBINATION}"]
    lines += [f"    x{i} = x{i - 1}" for i in range(1, hops + 1)]
    lines.append(f"    return x{hops}.select_for_update(no_key={no_key}).first()")
    return _B0_IMPORTS + "\n".join(lines) + "\n"


def combination_of_parts(parts: int) -> str:
    """One account lock whose receiver is a combination of ``parts`` querysets."""
    body = " | ".join(f"AppAccount.objects.filter(pk={i})" for i in range(parts))
    return (
        _B0_IMPORTS + f"def lock():\n    return ({body}).select_for_update(no_key=True).first()\n"
    )


class LockScanBoundTests(unittest.TestCase):
    """B0's item 1: for each lock, the receiver rule follows at most 100 names along one chain and
    visits at most 1,000 states; beyond either the lock is refused, its line naming the limit, the
    function and the lock's line. No test asserts a time (the evidence record states each)."""

    def scan_source(self, text: str) -> list[account_lock_scan.Lock]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(text, encoding="utf-8")
            return account_lock_scan.scan([path])

    def printed(self, text: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(text, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                status = account_lock_scan.main([str(path)])
            return status, out.getvalue()

    def test_the_limits_are_module_constants(self) -> None:
        self.assertEqual(account_lock_scan.MAX_NAMES_FOLLOWED, 100)
        self.assertEqual(account_lock_scan.MAX_STATES, 1000)

    def test_fourteen_names_each_assigned_from_every_other_are_refused_by_the_states_limit(
        self,
    ) -> None:
        text = names_each_assigned_from_every_other(14)
        locks = self.scan_source(text)
        self.assertEqual(
            [(lock.kind, lock.mode) for lock in locks],
            [("bound: more than 1000 states", "FOR UPDATE")],
        )
        self.assertEqual(len(account_lock_scan.violations(locks)), 1)
        status, printed = self.printed(text)
        self.assertEqual(status, 1)
        line = f"planted.py:{locks[0].line} (lock, bound: more than 1000 states): FOR UPDATE"
        self.assertIn(line, printed)
        self.assertTrue(printed.startswith("BAD "))
        self.assertIn("account locks found: 1; not FOR NO KEY UPDATE: 1", printed)

    def test_five_hundred_plain_hops_are_refused_by_the_names_limit_not_a_recursion_error(
        self,
    ) -> None:
        text = plain_hops(500)
        locks = self.scan_source(text)  # raises RecursionError as at 8d83474 (the reversal)
        self.assertEqual(
            [(lock.kind, lock.mode) for lock in locks],
            [("bound: more than 100 names followed", "FOR UPDATE")],
        )
        status, printed = self.printed(text)
        self.assertEqual(status, 1)
        self.assertIn(
            "(lock, bound: more than 100 names followed): FOR UPDATE", printed.splitlines()[0]
        )

    def test_just_inside_each_limit_the_lock_passes_as_before(self) -> None:
        # With no_key=True: 8 names each assigned from every other (257 states), and 99 hops (100
        # names followed; AppAccount is not counted), each judged as at 8d83474.
        for name, text in {
            "eight names": names_each_assigned_from_every_other(8),
            "99 hops": plain_hops(99),
        }.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual(
                    [(lock.kind, lock.mode) for lock in locks], [("generic", "FOR NO KEY UPDATE")]
                )
                self.assertEqual(account_lock_scan.violations(locks), [])

    def test_just_beyond_each_limit_the_lock_is_refused(self) -> None:
        # 100 hops: 101 names followed. Eight names visit 257 states: at a limit of 257 they pass,
        # at 256 they are refused.
        locks = self.scan_source(plain_hops(100))
        self.assertEqual(
            [(lock.kind, lock.mode) for lock in locks],
            [("bound: more than 100 names followed", "FOR UPDATE")],
        )
        eight = names_each_assigned_from_every_other(8)
        with mock.patch.object(account_lock_scan, "MAX_STATES", 257):
            locks = self.scan_source(eight)
        self.assertEqual(account_lock_scan.violations(locks), [])
        with mock.patch.object(account_lock_scan, "MAX_STATES", 256):
            locks = self.scan_source(eight)
        self.assertEqual(
            [(lock.kind, lock.mode) for lock in locks],
            [("bound: more than 256 states", "FOR UPDATE")],
        )

    def test_beyond_a_limit_a_lock_never_passes_whatever_its_no_key_or_model(self) -> None:
        # The lock is refused even with no_key=True, and on a model other than AppAccount.
        other = plain_hops(500).replace("AppAccount.objects", "Match.objects")
        for name, text in {"no_key=True": plain_hops(500), "Match": other}.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual(len(account_lock_scan.violations(locks)), 1)
                self.assertTrue(locks[0].kind.startswith("bound: "))

    def test_the_tree_is_unchanged(self) -> None:
        # 52 calls, 0 joining, 7 account locks, none refused by the bound (the output is compared
        # byte for byte with 8d83474's in the evidence record).
        locks = account_lock_scan.scan()
        self.assertEqual(len(locks), 7)
        self.assertEqual(account_lock_scan.violations(locks), [])
        self.assertFalse(any(lock.kind.startswith("bound") for lock in locks))
        self.assertEqual(account_lock_scan.calls(), (52, 0))


class LockScanStatedLimitB0Tests(unittest.TestCase):
    """B0's item 8, a stated limit (DM-71): a combination of 1,000 parts exceeds Python's recursion
    limit in the reading of combinations (``_parts``), so the scan stops and exits 1, failing
    closed; one of 300 parts does not."""

    def scan_source(self, text: str) -> list[account_lock_scan.Lock]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(text, encoding="utf-8")
            return account_lock_scan.scan([path])

    def test_a_combination_of_1000_parts_raises_and_300_parts_do_not(self) -> None:
        with self.assertRaises(RecursionError):
            self.scan_source(combination_of_parts(1000))
        locks = self.scan_source(combination_of_parts(300))
        self.assertEqual([(lock.kind, lock.mode) for lock in locks], [("orm", "FOR NO KEY UPDATE")])


# B0's item 4 (DM-70; C5's delta re-review's F3 and F12): tests that pin C5's memo key and two of
# C4's branches, each failing against its mutant (the evidence record lists each).
PINNED_C5_REVIEW = {
    # F3: the memo key's seen. Keyed on the name alone, x is first followed under {y} (where it
    # reaches nothing), and that answer is reused for x's own chain, so the account is lost.
    "the_memo_keys_seen": (
        "def lock(a, b):\n"
        "    Y = X | Match.objects.filter(pk=b)\n"
        "    X = Y\n"
        "    X = AppAccount.objects.filter(pk=a)\n"
        "    return (Y | X).select_for_update().first()\n",
        "orm",
    ),
    # SV3 Stage B, item 4 (DM-72; B0's delta re-review's F6): the memo key's seen, not its size.
    # Keyed on (name, len(seen)), x is first followed under {y} (where it reaches nothing), and
    # that answer is reused under {z}, another seen of the same size, so the account is lost.
    "the_memo_keys_seen_not_its_size": (
        "def lock(a, b):\n"
        "    Y = X | Match.objects.filter(pk=b)\n"
        "    Z = X | Match.objects.filter(pk=b)\n"
        "    X = Y\n"
        "    X = AppAccount.objects.filter(pk=a)\n"
        "    return (Y | Z).select_for_update().first()\n",
        "orm",
    ),
    # F12: _climb's NamedExpr branch, climbing through an assignment expression to the calls made
    # on it, and the name it assigns.
    "a_call_on_an_assignment_expression": (
        "def lock(pk, state):\n"
        "    return (rows := Profile.objects.select_for_update()).filter(account__state=state)\n",
        "join",
    ),
    "a_use_of_the_name_an_assignment_expression_assigns": (
        "def lock(pk, state):\n"
        "    if (rows := Profile.objects.select_for_update()) is None:\n"
        "        return None\n"
        "    return rows.filter(account__state=state).first()\n",
        "join",
    ),
    # F12: a field path in a later keyword argument of a capitalised call.
    "a_path_in_a_later_keyword_argument": (
        "def lock(pk, field):\n"
        "    rows = Profile.objects.select_for_update()\n"
        "    expression = Lower(output_field=field, expression='account__state')\n"
        "    return rows.filter(display_name=expression).first()\n",
        "join",
    ),
}


class PinnedC5ReviewTests(unittest.TestCase):
    """B0's item 4: F3's and F12's forms, each refused; no rule changes."""

    def scan_source(self, text: str) -> list[account_lock_scan.Lock]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planted.py"
            path.write_text(_C5_IMPORTS + text, encoding="utf-8")
            return account_lock_scan.scan([path])

    def test_each_form_is_refused(self) -> None:
        for name, (text, kind) in PINNED_C5_REVIEW.items():
            with self.subTest(planted=name):
                locks = self.scan_source(text)
                self.assertEqual([(lock.kind, lock.mode) for lock in locks], [(kind, "FOR UPDATE")])
                self.assertEqual(len(account_lock_scan.violations(locks)), 1)


if __name__ == "__main__":
    unittest.main()
