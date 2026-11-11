"""The profile suite's offline checks (SV2 Stage A; its brief's D12 and acceptance check 12).

No database: the profile settings' refusals and values; the job's secret check of the suite's
output and the upload gate; the workflow's SV2 steps; the case plan; the schema check against the
shared corpus; the value ledger; and the commands' refusals of each other's settings. The cases
themselves run in the Database proof checks job, on the third disposable database.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
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
from glow_ordering_proof.profile_support import ObservedObjects, ValueLedger, synthetic_png
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


# The suite's own result lines, as ``profile_suite.run`` prints them.
SUITE_LINES = {
    "profile secret scan: clean": (
        "profile secret scan: clean (1040 secrets held; 0 found in 650 log records, 112 writes"
        " and the results JSON)"
    ),
    "profile value scan: clean": (
        "profile value scan: clean (133 member values held: coordinates, birth dates, times and"
        " places, own words, sensitive values; 0 found in the same output)"
    ),
}


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
        lines = "".join(f"{SUITE_LINES[line]}\n" for line in clean)
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

    def test_the_verdict_reads_the_suites_own_result_lines(self) -> None:
        # C2 (finding 15): "clean" anywhere else in the log is not the suite's verdict.
        found_secret = (
            "profile secret scan: FOUND (1040 secrets held; 1 found in 650 log records, 112"
            " writes and the results JSON)"
        )
        found_value = (
            "profile value scan: FOUND (133 member values held: coordinates, birth dates, times"
            " and places, own words, sensitive values; 2 found in the same output)"
        )
        logs = {
            "a FOUND line, with clean words in a case's detail": (
                "[profile] PASS a.case: profile secret scan: clean, profile value scan: clean\n"
                + found_secret
                + "\n"
                + SUITE_LINES["profile value scan: clean"]
                + "\n"
            ),
            "a value FOUND line": SUITE_LINES["profile secret scan: clean"] + "\n" + found_value,
            "a clean line that found some": SUITE_LINES["profile secret scan: clean"].replace(
                "0 found", "3 found"
            )
            + "\n"
            + SUITE_LINES["profile value scan: clean"],
            "a clean line twice": "\n".join(
                (*SUITE_LINES.values(), SUITE_LINES["profile value scan: clean"])
            ),
            "a clean line not at a line's start": "x " + "\nx ".join(SUITE_LINES.values()),
        }
        for what, log in logs.items():
            with self.subTest(log=what):
                self.job.results.write_text("{}", encoding="utf-8")
                self.job.write("profile.log", "[profile] PASS a.case\n" + log + "\n")
                status, printed = self.job.run()
                self.assertEqual(status, profile_scan.REFUSED)
                self.assertIn("reported clean: False", printed)
                self.assertFalse(self.job.results.exists())

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
                "re",
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
    def test_the_plan_covers_every_acceptance_check(self) -> None:
        plan = profile_cases.plan()
        self.assertEqual(len(plan), len(set(plan)))
        covered = {check for entry in profile_cases.CASES for check in entry.checks}
        # Stage A's checks, 1 to 9, 11 and 12, and SV2 Stage B's, 10 (the photos) and 13 (one
        # pointer order).
        for check in (str(n) for n in range(1, 14)):
            with self.subTest(check=check):
                self.assertIn(check, covered)
        for decision in (
            "D2",
            "D3",
            "D4",
            "D5",
            "D6",
            "D7",
            "D8",
            "D9",
            "D10",
            "D17",
            "D18",
            "D19",
        ):
            with self.subTest(decision=decision):
                self.assertIn(decision, covered)
        stage_b = [
            entry
            for entry in profile_cases.CASES
            if entry.case_id.split(".")[0]
            in (
                "media",
                "pointers",
            )
        ]
        # Stage B's eleven, correction C1's three (DM-58 item 9: the purge in any account
        # state, and every other photo step refusing an inactive owner), and correction C2's
        # hold stopping the check's approval (F1).
        self.assertEqual(len(stage_b), 15)
        # Correction C2's two (F1 and F5), each under its own name.
        plan = profile_cases.plan()
        self.assertIn("media.a_hold_stops_the_checks_approval", plan)
        self.assertIn("constraints.malformed_media_writes_are_refused", plan)
        self.assertTrue(
            all("10" in e.checks or "13" in e.checks or "12" in e.checks for e in stage_b)
        )

    def test_the_case_count_is_pinned(self) -> None:
        # C2 (finding 15): 47 cases after C1, and C2's six; SV2 Stage B's eleven (DM-57 section 5:
        # the count changes with Stage B's cases); Stage B's correction C1's three (DM-58 item 9);
        # Stage B's correction C2's two (the exact-head review's F1 and F5).
        self.assertEqual(profile_cases.CASE_COUNT, 69)
        self.assertEqual(len(profile_cases.plan()), profile_cases.CASE_COUNT)

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


# C3 (finding 3): the names a check's label may interpolate. Each holds a code, a route, a setting,
# field or event name, a count, or another label, never a member's value; a new name here is
# read before it is added. A failing check's label is printed in the case's detail line.
LABEL_NAMES = {
    "bumps",
    "constraint",
    "decision",
    "demoted",
    "event",
    "expected",
    "field",
    "limit",
    "name",
    "path",
    "removal",
    "state",
    "stored.operation",
    "what",
    "when",
    "word",
    "writer",
}
# The label's position in each checking call: ``expect(ok, what)``, ``ctx.refused(reply, status,
# code, what)`` and ``ctx.data(reply, kind, what)``.
LABEL_ARGUMENT = {"expect": 1, "refused": 3, "data": 2}


def label_parts(label: ast.expr) -> list[str]:
    """What a label is built from, beyond its literal text: each interpolated expression. A choice
    between two literals is literal text."""
    if isinstance(label, ast.Constant) and isinstance(label.value, str):
        return []
    if isinstance(label, ast.IfExp) and all(
        isinstance(branch, ast.Constant) for branch in (label.body, label.orelse)
    ):
        return []
    if isinstance(label, ast.JoinedStr):
        return [
            part
            for value in label.values
            if isinstance(value, ast.FormattedValue)
            for part in label_parts(value.value)
        ]
    return [ast.unparse(label)]


def _bound(target: ast.expr) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, ast.Tuple | ast.List):
        return set().union(*(_bound(element) for element in target.elts))
    if isinstance(target, ast.Starred):
        return _bound(target.value)
    return set()


def label_bindings(tree: ast.Module) -> dict[str, set[str]]:
    """SV2 Stage B (the delta review's N5): every binding of a name in ``LABEL_NAMES`` in the
    cases, by name: its kind and what it binds, as text. A parameter is named by its function."""
    found: dict[str, set[str]] = {}

    def add(names: set[str], text: str) -> None:
        for name in names & LABEL_NAMES:
            found.setdefault(name, set()).add(text)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                add(_bound(target), "= " + ast.unparse(node.value))
        elif isinstance(node, ast.AnnAssign | ast.AugAssign):
            add(_bound(node.target), "op= " + ast.unparse(node.value or ast.Constant(None)))
        elif isinstance(node, ast.NamedExpr):
            add(_bound(node.target), ":= " + ast.unparse(node.value))
        elif isinstance(node, ast.For | ast.comprehension):
            add(_bound(node.target), "in " + ast.unparse(node.iter))
        elif isinstance(node, ast.withitem) and node.optional_vars is not None:
            add(_bound(node.optional_vars), "with " + ast.unparse(node.context_expr))
        elif isinstance(node, ast.ExceptHandler) and node.name:
            add({node.name}, "except")
        elif isinstance(node, ast.FunctionDef | ast.Lambda):
            arguments = node.args
            for argument in [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]:
                owner = node.name if isinstance(node, ast.FunctionDef) else "<lambda>"
                add({argument.arg}, f"parameter of {owner}")
    return found


def label_parameter_calls(tree: ast.Module) -> list[tuple[str, str, ast.expr]]:
    """Every argument a call in the cases passes to a parameter in ``LABEL_NAMES`` of a function
    the cases define: the function, the parameter and the argument."""
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    found = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        function = functions.get(node.func.id)
        if function is None:
            continue
        names = [argument.arg for argument in function.args.args]
        for index, value in enumerate(node.args):
            if index < len(names) and names[index] in LABEL_NAMES:
                found.append((function.name, names[index], value))
        for keyword in node.keywords:
            if keyword.arg in LABEL_NAMES:
                found.append((function.name, keyword.arg, keyword.value))
    return found


def literal_text(value: ast.expr) -> bool:
    """Literal text, a literal value (a code, a count, a list of codes), or a label built only
    from names in ``LABEL_NAMES``."""
    try:
        ast.literal_eval(value)
    except ValueError:
        return all(part in LABEL_NAMES for part in label_parts(value))
    return True


def pinned(text: str) -> str:
    """A binding as the pin holds it: its text, or a long one's start and its whole text's
    SHA-256."""
    if len(text) <= 64:
        return text
    return text[:48] + " ... sha256:" + hashlib.sha256(text.encode()).hexdigest()[:16]


# SV2 Stage B (the delta review's N5): every binding of a label name in the cases, pinned, so a
# name rebound to a member value fails until the binding is read and added here. A long
# binding is pinned by its start and the SHA-256 of its whole text (``pinned``).
LABEL_BINDINGS: dict[str, frozenset[str]] = {
    "bumps": frozenset(
        {
            "parameter of check",
        }
    ),
    "constraint": frozenset(
        {
            "in operation.options.get('constraints', [])",
            "in writes",
        }
    ),
    "decision": frozenset(
        {
            "in ('accepted', 'withdrawn', 'accepted')",
            "in ('accepted', 'withdrawn', 'accepted', 'withdrawn')",
        }
    ),
    "demoted": frozenset(
        {
            "= 0",
            "= _events(profile.pk, 'profile_demoted')",
            "op= 1",
            "parameter of check",
        }
    ),
    "event": frozenset(
        {
            "= events.first()",
            "in ((age.pk, 'age_state_changed', before['counts ... sha256:6216e5c770f68e7c",
            "in OutboxEvent.objects.filter(schema_version='glow-profiles-1')",
            "parameter of demoted",
        }
    ),
    "expected": frozenset(
        {
            "= ctx.get(member, ADULT, 'own_age_state')['version']",
            "= {(profile.pk, 'profile_edited'), (profile.pk,  ... sha256:8a73046be5538e1a",
            "parameter of adult_body",
            "parameter of stays",
        }
    ),
    "field": frozenset(
        {
            "= ProfileFieldChoice.objects.get(account_id=acco ... sha256:dc43bce42493ddd8",
            "in ('gender', 'orientation', 'looking_for', 'rel ... sha256:520d721d276b38e8",
            "in (('orientation', PreferenceSetEntry.objects.f ... sha256:a9285fb5cc7a41f9",
            "in PreferenceSetEntry.objects.filter(account_id= ... sha256:05ba411f1ba78c88",
            "in before.items()",
        }
    ),
    "limit": frozenset(
        {
            "= _media_policy()['max_bytes']",
            "in _crossing_publications()",
        }
    ),
    "name": frozenset(
        {
            "in ('gender', 'looking_for')",
            "in (('gender', ['man']), ('orientation', [ORIENT ... sha256:35c16ba9884a2e9f",
            "in (('gender', ['woman', 'man']), ('orientation' ... sha256:afe7f55ba30b7935",
            "in (('orientation', [ORIENTATION_VALUES[1]], Non ... sha256:612fa843d81f8e51",
            "in (ps.ONBOARDING_CONSENT, ps.SENSITIVE_CONSENT)",
            "in _crossing_publications()",
            "in holds",
            "in names",
            "in ps.ALL_SETTINGS",
            "parameter of holding",
        }
    ),
    "path": frozenset(
        {
            "in ('/api/v1/staff/approve', '/api/v1/settings', ... sha256:b67311ee30f90c2f",
            "in ((PROFILE, {'operation': 'profile', 'meta': s ... sha256:7d5562a0f17695f4",
            "in (PROFILE, FIELDS, PREFERENCES, FILTERS, AREA, ... sha256:76acaaa1e7d749e6",
            "in (PROFILE, VISIBILITY, FIELDS, PREFERENCES, FI ... sha256:c2ee2be28b3d8e9c",
            "in paths",
            "in plans",
        }
    ),
    "removal": frozenset(
        {
            "in ('consent', 'summary', 'birth_input', 'adult_ ... sha256:208dbd04f4850696",
            "parameter of prepared",
        }
    ),
    "state": frozenset(
        {
            "= _profile_row(account).state",
            "= _profile_row(member.account_id).state",
            "= pf.FieldState(tuple(row.value_ids), row.own_words, row.shown)",
            "in ((restricted, 'restricted'), (removed, 'removed'))",
        }
    ),
    "what": frozenset(
        {
            "= 'the birth input behind a lapsed onboarding consent'",
            "in ('an original that no longer matches its comp ... sha256:53bb77fe08ad52fb",
            "in ((future, 400, 'invalid_request', \"an unknown ... sha256:c23e75e7e35095e6",
            "in plans",
            "in saves",
            "parameter of _expect_reset",
            "parameter of check",
            "parameter of completed",
            "parameter of demoted",
            "parameter of incomplete",
            "parameter of stays",
        }
    ),
    "when": frozenset(
        {
            "parameter of all_refused",
        }
    ),
    "word": frozenset(
        {
            "in ('distance_miles', 'miles', 'kilometres', 'la ... sha256:7f02d4e727057488",
            "in ('staff', 'setting', 'approve', 'revoke', 're ... sha256:e7db6abad681fc16",
        }
    ),
    "writer": frozenset(
        {
            "in ('the eligibility step', 'the birth input')",
        }
    ),
}


class ProfileLabelTests(unittest.TestCase):
    def test_no_checks_label_holds_a_member_value(self) -> None:
        tree = ast.parse(Path(profile_cases.__file__).read_text(encoding="utf-8"))
        checked = 0
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            called = (
                func.id
                if isinstance(func, ast.Name)
                else func.attr
                if isinstance(func, ast.Attribute)
                else ""
            )
            position = LABEL_ARGUMENT.get(called)
            if position is None or len(node.args) <= position:
                continue
            checked += 1
            for part in label_parts(node.args[position]):
                if part not in LABEL_NAMES:
                    found.append(f"{node.lineno}: {called} labelled by {part}")
        self.assertEqual(found, [])
        self.assertGreater(checked, 450)

    def test_a_label_built_from_a_value_is_found(self) -> None:
        call = ast.parse('ctx.refused(reply, 400, "invalid_request", born)').body[0]
        assert isinstance(call, ast.Expr) and isinstance(call.value, ast.Call)
        self.assertEqual(label_parts(call.value.args[3]), ["born"])
        call = ast.parse('expect(found == years, f"whole years ({years})")').body[0]
        assert isinstance(call, ast.Expr) and isinstance(call.value, ast.Call)
        self.assertEqual(label_parts(call.value.args[1]), ["years"])
        self.assertNotIn("born", LABEL_NAMES)
        self.assertNotIn("years", LABEL_NAMES)


class LabelBindingTests(unittest.TestCase):
    """SV2 Stage B (the delta review's N5): a name in ``LABEL_NAMES`` is trusted only where it is
    bound as pinned, and a label parameter is passed only literal text or another label name."""

    def test_every_binding_of_a_label_name_is_pinned(self) -> None:
        tree = ast.parse(Path(profile_cases.__file__).read_text(encoding="utf-8"))
        found = {
            name: frozenset(pinned(text) for text in texts)
            for name, texts in label_bindings(tree).items()
        }
        self.assertEqual(found, LABEL_BINDINGS)
        self.assertLessEqual(set(LABEL_BINDINGS), LABEL_NAMES)

    def test_every_label_parameter_is_passed_a_label(self) -> None:
        tree = ast.parse(Path(profile_cases.__file__).read_text(encoding="utf-8"))
        calls = label_parameter_calls(tree)
        self.assertGreater(len(calls), 40)
        found = [
            f"{value.lineno}: {function}({parameter}=...)"
            for function, parameter, value in calls
            if not literal_text(value)
        ]
        self.assertEqual(found, [])

    def test_a_label_name_rebound_to_a_value_is_found(self) -> None:
        rebound = ast.parse("def case(ctx, member):\n    what = member.birth_date\n")
        self.assertEqual(
            label_bindings(rebound)["what"],
            {"= member.birth_date"},
        )
        passed = ast.parse(
            "def stays(member, expected, what):\n    pass\n"
            "def case(ctx, member, born):\n    stays(member, [], born)\n"
        )
        calls = label_parameter_calls(passed)
        self.assertEqual([literal_text(value) for _f, _p, value in calls], [True, False])


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
            # SV2 Stage B: F05's responses.
            "MediaLifecycle",
            "MediaCollection",
            "MediaUploadGrant",
        ):
            with self.subTest(definition=definition):
                self.assertIn(definition, decided)


class ValueLedgerTests(unittest.TestCase):
    def test_every_form_the_code_could_print_is_found(self) -> None:
        # C2 (finding 5): a date in Python's repr, compact, numeric or in prose; a time in
        # Python's repr; a coordinate without its sign, or rounded or truncated to three decimals.
        ledger = ValueLedger()
        ledger.add("2008-02-29")
        ledger.add("02:47:19")
        ledger.add("40.7123457")
        ledger.add("-74.0067891")
        for printed in (
            "datetime.date(2008, 2, 29)",
            "29 February 2008",
            "February 29, 2008",
            "20080229",
            "29/02/2008",
            "02/29/2008",
            "datetime.time(2, 47, 19)",
            "lat 40.7123",
            "lat 40.712",
            "lat 40.71235",
            "lon -74.0068",
            "lon -74.007",
            "lon 74.006",
            "Decimal('40.7123457')",
        ):
            with self.subTest(printed=printed):
                self.assertEqual(ledger.found_in(printed), 1)
        # Coarser than three decimals is not a precise location; nor is another value.
        for printed in ("lat 40.71", "lon -74.01", "1 March 2008", "02:47:18"):
            with self.subTest(printed=printed):
                self.assertEqual(ledger.found_in(printed), 0)

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

    def test_a_photos_bytes_are_found_as_their_hex_and_their_repr(self) -> None:
        # SV2 Stage B, correction C2 (the exact-head review's F4): a photo's bytes printed as
        # their hex or their ``repr``, whole or from their start, as a log record or JSON would
        # hold them; and the fixture variant's text, as itself or its ``repr``.
        photo = synthetic_png(3, 2)
        variant = b"fixture-variant:" + hashlib.sha256(photo).hexdigest().encode("ascii")
        ledger = ValueLedger()
        ledger.add_bytes(photo)
        ledger.add_bytes(variant)
        for printed in (
            f"photo {photo!r}",
            f"photo {photo[:30]!r}",
            json.dumps({"detail": repr(photo)}),
            f"photo {photo.hex()}",
            f"start {photo[:24].hex()}",
            f"variant {variant.decode()}",
            f"variant {variant!r}",
            f"variant {variant.hex()}",
        ):
            with self.subTest(printed=printed[:24]):
                # The variant's ``repr`` holds its text too: two held values in one print.
                self.assertGreaterEqual(ledger.found_in(printed), 1)
        # Another photo's bytes (other dimensions) and a photo's first few bytes are not held.
        for printed in (repr(synthetic_png(5, 5)), synthetic_png(5, 5).hex(), repr(photo[:12])):
            with self.subTest(printed=printed[:24]):
                self.assertEqual(ledger.found_in(printed), 0)

    def test_the_stores_objects_join_the_ledger_as_they_are_written(self) -> None:
        # A key and its bytes are held when they are set, and stay held after the object is
        # deleted (a purge within the case).
        ledger = ValueLedger()
        held = {"0" * 31 + "a": synthetic_png(2, 3)}
        objects = ObservedObjects(held, ledger)
        key = secrets.token_hex(16)
        photo = synthetic_png(4, 4)
        objects[key] = photo
        objects.pop(key)
        self.assertEqual(ledger.found_in(f"key {key}"), 1)
        self.assertEqual(ledger.found_in(f"bytes {photo!r}"), 1)
        self.assertEqual(ledger.found_in(f"key {'0' * 31}a"), 1)
        self.assertEqual(ledger.found_in(f"bytes {synthetic_png(2, 3)!r}"), 1)
        self.assertEqual(dict(objects), held)


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
