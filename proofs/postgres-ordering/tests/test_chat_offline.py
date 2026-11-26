"""The chat suite's offline checks (SV4 A2; its brief's D2 and D10), on the discovery suite's
pattern (``tests.test_discovery_offline``).

No database: the chat settings' refusals and values; the job's secret check of the suite's output
and the upload gate; the workflow's SV4 steps in the chat suite's own job, "Database proof checks
(chat)"; the case plan; the commands' refusals of each other's settings; the runner's row-lock
record and scans; and the suite's support (the provider the settings name, the routes it calls).
The cases themselves run in their own job, on their own disposable database.
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import io
import json
import os
import re
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
from glow_ordering_proof import chat_cases, chat_scan, chat_support, environment
from tests.test_identity_offline import (
    KeyFiles,
    credentials_prelude,
    job_databases,
    job_secret_files,
    pem,
    script_lines,
    workflow_job,
    workflow_step,
    writers,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
PROOF = Path(__file__).resolve().parents[1] / "glow_ordering_proof"
CHAT_SETTINGS = "glow_ordering_proof.chat_settings"
JOB = "database-chat"  # the chat suite's own job (SV4 A2, on A0's pattern)

GOOD = {
    environment.HOST: "127.0.0.1",
    environment.PORT: "5433",
    environment.NAME: "glow_chat_proof",
    environment.USER: "glow_proof",
    environment.PASSFILE: "/tmp/example/passfile",
    environment.MARKER: secrets.token_hex(16),
    "PATH": "/x",
    "HOME": "/h",
    "LANG": "C.UTF-8",
}


class ChatSettingsModuleTests(unittest.TestCase):
    """The chat settings refuse at import, as the proof's settings do, and then take SV1's, SV2's
    and SV3's fragments, the chat URL configuration, the suite's own two keys and the text
    reader's factory (D8, "The provider")."""

    def setUp(self) -> None:
        self.files = KeyFiles()

    def tearDown(self) -> None:
        self.files.close()

    def import_settings(self, environ: dict[str, str]) -> Any:
        saved = dict(os.environ)
        sys.modules.pop(CHAT_SETTINGS, None)
        try:
            os.environ.clear()
            os.environ.update(environ)
            return importlib.import_module(CHAT_SETTINGS)
        finally:
            os.environ.clear()
            os.environ.update(saved)
            sys.modules.pop(CHAT_SETTINGS, None)

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
        self.assertEqual(settings.ROOT_URLCONF, "glow_ordering_proof.chat_urls")
        database = settings.DATABASES["default"]
        self.assertIs(database["ATOMIC_REQUESTS"], False)
        self.assertEqual(database["NAME"], "glow_chat_proof")
        self.assertNotIn("PASSWORD", database)
        from psycopg import IsolationLevel

        self.assertIs(database["OPTIONS"]["isolation_level"], IsolationLevel.READ_COMMITTED)
        self.assertEqual(
            settings.GLOW_DISCOVERY_COMPATIBILITY_FIXTURE, "explicitly-synthetic-ready"
        )
        self.assertEqual(settings.GLOW_DISCOVERY_ENVIRONMENT, "test")
        # D8: these settings alone name the history read's text reader, the suite's fixture.
        self.assertEqual(
            settings.GLOW_CHAT_TEXT_READER, "glow_ordering_proof.chat_support.text_reader"
        )
        self.assertEqual(settings.LOGGING["root"], {"level": "DEBUG", "handlers": []})

    def test_the_settings_refuse_what_the_proofs_settings_refuse(self) -> None:
        files = self.files.environ()
        for extra in (
            {"PGPASSWORD": "x"},
            {"DATABASE_URL": "x"},
            {"HD_API_KEY": "x"},
            {"STREAM_API_SECRET": "x"},
        ):
            with self.subTest(name=next(iter(extra))):
                with self.assertRaises(environment.RefusedEnvironment):
                    self.import_settings({**GOOD, **files, **extra})
        with self.assertRaises(environment.RefusedConnection):
            self.import_settings({**GOOD, **files, environment.HOST: "db.example.internal"})

    def test_the_settings_never_import_the_api_settings(self) -> None:
        for name in ("chat_settings.py", "chat_urls.py"):
            path = PROOF / name
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ImportFrom) and node.module:
                    with self.subTest(module=name, imported=node.module):
                        self.assertFalse(node.module.startswith("glow_api"))
                        self.assertNotIn("static_settings", node.module)

    def test_the_url_configuration_serves_the_five_route_modules(self) -> None:
        tree = ast.parse((PROOF / "chat_urls.py").read_text(encoding="utf-8"))
        imported = sorted(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertEqual(
            imported,
            [
                "glow_chat.urls",
                "glow_discovery.interaction_urls",
                "glow_discovery.urls",
                "glow_identity.urls",
                "glow_profiles.urls",
            ],
        )


SUITE_LINES = {
    "chat secret scan: clean": (
        "chat secret scan: clean (1077 secrets held; 0 found in 814 log records, 50 writes"
        " and the results JSON)"
    ),
    "chat value scan: clean": (
        "chat value scan: clean (866 member values held: member values, message texts, provider"
        " identifiers; 0 found in the same output)"
    ),
}


class ChatJobDirectory:
    """A job directory as the chat job's credentials step writes it: every secret file it writes,
    read from the workflow (D2), with synthetic values only."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        files = job_secret_files(JOB)
        keys = sorted(name for name in files if name.endswith(".pem"))
        self.values: dict[str, str] = {}
        for name in sorted(files - {chat_scan.PASSFILE, *keys}):
            self.values[name] = secrets.token_hex(24)
            self.write(name, self.values[name] + "\n")
        self.role_password = secrets.token_hex(24)
        self.write(
            chat_scan.PASSFILE,
            "".join(
                f"127.0.0.1:5433:{database}:glow_proof:{self.role_password}\n"
                for database in job_databases(JOB)
            ),
        )
        self.pem_lines: list[str] = []
        for name in keys:
            text = pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
            self.write(name, text)
            self.pem_lines.append(
                [line for line in text.splitlines() if not line.startswith("---")][3]
            )
        self.log = self.write("chat.log", "[chat] PASS a.case\n")
        self.results = self.root / "chat-results.json"
        self.results.write_text(json.dumps({"cases": [{"detail": "ok"}]}), encoding="utf-8")

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="ascii")
        path.chmod(0o600)
        return path

    def clean_log(self, extra: str = "", clean: tuple[str, ...] = chat_scan.SUITE_CLEAN) -> None:
        lines = "".join(f"{SUITE_LINES[line]}\n" for line in clean)
        self.write("chat.log", "[chat] PASS a.case\n" + extra + lines)

    def run(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = chat_scan.main([str(self.root), str(self.log), str(self.results)])
        return status, out.getvalue()

    def every_value(self) -> list[str]:
        return [*self.values.values(), self.role_password, *self.pem_lines]

    def close(self) -> None:
        self.directory.cleanup()


class ChatScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.job = ChatJobDirectory()

    def tearDown(self) -> None:
        self.job.close()

    def test_the_values_are_every_secret_file_of_the_job(self) -> None:
        # D2: the check lists every secret file its own job writes (its keys, its marker, the
        # decoy database's marker, the passwords), and no other.
        self.assertEqual(
            set(chat_scan.VALUE_FILES),
            {"chat-secret-key", "chat-marker", "discovery-marker", "superuser-password"},
        )
        self.assertEqual(set(chat_scan.KEY_FILES), {"chat-jwt-key.pem"})
        self.assertEqual(
            {*chat_scan.VALUE_FILES, chat_scan.PASSFILE, *chat_scan.KEY_FILES},
            job_secret_files(JOB),
        )
        found = chat_scan.job_values(self.job.root)
        for value in self.job.every_value():
            self.assertIn(value, found)

    def test_the_docstring_names_the_chat_job(self) -> None:
        # D12, "Due at A2": the scan's docstring names its own job, not the shared one.
        docstring = chat_scan.__doc__ or ""
        self.assertIn('"Database proof checks (chat)"', docstring)
        self.assertNotIn("The Database proof checks job", docstring)

    def test_clean_output_passes_and_keeps_the_json(self) -> None:
        self.job.clean_log()
        status, printed = self.job.run()
        self.assertEqual(status, chat_scan.PASSED, printed)
        self.assertTrue(self.job.results.exists())

    def test_a_value_in_the_log_or_the_json_is_refused_and_the_json_removed(self) -> None:
        for name in sorted(self.job.values):
            for where in ("log", "json"):
                with self.subTest(file=name, where=where):
                    job = ChatJobDirectory()
                    try:
                        value = job.values[name]
                        job.clean_log(extra=f"{value}\n" if where == "log" else "")
                        if where == "json":
                            job.results.write_text(json.dumps({"x": value}), encoding="utf-8")
                        status, printed = job.run()
                        self.assertEqual(status, chat_scan.REFUSED)
                        self.assertFalse(job.results.exists())
                        for secret in job.every_value():
                            self.assertNotIn(secret, printed)
                    finally:
                        job.close()

    def test_the_role_password_and_a_key_line_are_refused_too(self) -> None:
        for which in ("role password", "a key line"):
            with self.subTest(which=which):
                job = ChatJobDirectory()
                try:
                    value = job.role_password if which == "role password" else job.pem_lines[0]
                    job.clean_log(extra=f"{value}\n")
                    status, _ = job.run()
                    self.assertEqual(status, chat_scan.REFUSED)
                finally:
                    job.close()

    def test_each_of_the_suites_clean_scans_is_required(self) -> None:
        for kept in chat_scan.SUITE_CLEAN:
            with self.subTest(kept=kept):
                job = ChatJobDirectory()
                try:
                    job.clean_log(clean=(kept,))
                    status, _ = job.run()
                    self.assertEqual(status, chat_scan.REFUSED)
                finally:
                    job.close()

    def test_the_suites_own_lines_match_what_the_suite_prints(self) -> None:
        self.assertTrue(chat_scan.suite_reported_clean("\n".join(SUITE_LINES.values())))
        source = (PROOF / "chat_suite.py").read_text(encoding="utf-8")
        for words in (
            "member values held: member values, message texts, provider",
            "identifiers; {report.values_found} found in the same output",
            "secrets held; {report.secrets_found} found in",
        ):
            with self.subTest(words=words):
                self.assertIn(words, source)


class ChatWorkflowTests(unittest.TestCase):
    """The chat suite's job's steps, "Database proof checks (chat)", read as the job runs them."""

    def test_the_credentials_step_makes_its_database_the_decoy_and_its_own_keys(self) -> None:
        step = workflow_step(JOB, "Generate the disposable database's credentials")
        for line in (
            'echo "::add-mask::$chat_marker"',
            'echo "::add-mask::$discovery_marker"',
            'echo "::add-mask::$chat_secret_key"',
            'printf \'%s\\n\' "$chat_marker" > "$dir/chat-marker"',
            'printf \'%s\\n\' "$discovery_marker" > "$dir/discovery-marker"',
            'printf \'%s\\n\' "$chat_secret_key" > "$dir/chat-secret-key"',
            "python - \"$dir/chat-jwt-key.pem\" <<'PYTHON'",
        ):
            with self.subTest(line=line):
                self.assertIn(line, step)
        self.assertIn("CREATE DATABASE glow_chat_proof OWNER glow_proof;", step)
        self.assertIn("COMMENT ON DATABASE glow_chat_proof IS 'glow-ordering-proof:%s';", step)
        # AG1: the decoy, in this job's PostgreSQL, carries the discovery database's name and a
        # marker of its own; the passfile names only the chat database.
        self.assertIn("CREATE DATABASE glow_discovery_proof OWNER glow_proof;", step)
        self.assertIn("COMMENT ON DATABASE glow_discovery_proof IS 'glow-ordering-proof:%s';", step)
        self.assertEqual(job_databases(JOB), ["glow_chat_proof"])
        self.assertIn('test "$chat_marker" != "$discovery_marker"', step)
        self.assertEqual(step.count("for path in sys.argv[1:]:"), 1)
        job = "\n".join(workflow_job(JOB))
        for other in (
            "discovery-secret-key",
            "discovery-jwt-key.pem",
            "profile-",
            "identity-",
            "wrong_marker",
            "discovery_settings",
        ):
            with self.subTest(other=other):
                self.assertNotIn(other, job)
        lines = script_lines(step.split("        run: |\n", 1)[1])
        self.assertEqual(lines[0], "set +x")
        values = [
            "superuser_password",
            "role_password",
            "chat_marker",
            "discovery_marker",
            "chat_secret_key",
        ]
        events = credentials_prelude(step)
        self.assertEqual([name for kind, name in events if kind == "generated"], values)
        self.assertEqual([name for kind, name in events if kind == "masked"], values)
        for name in values:
            with self.subTest(name=name):
                self.assertLess(events.index(("generated", name)), events.index(("masked", name)))
                self.assertEqual(len(re.findall(rf"^ *{name}=", step, flags=re.MULTILINE)), 1)
        self.assertEqual(step.count("::add-mask::"), len(values))
        role = (
            "printf \"CREATE ROLE glow_proof LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB"
            " NOCREATEROLE;\\n"
            "CREATE DATABASE glow_chat_proof OWNER glow_proof;\\n"
            "COMMENT ON DATABASE glow_chat_proof IS 'glow-ordering-proof:%s';\\n"
            "CREATE DATABASE glow_discovery_proof OWNER glow_proof;\\n"
            "COMMENT ON DATABASE glow_discovery_proof IS 'glow-ordering-proof:%s';\\n\""
            ' "$role_password" "$chat_marker" "$discovery_marker" > "$dir/create-role.sql"'
        )
        self.assertEqual(writers(step, "create-role.sql"), [role])
        distinct = (
            'test "$chat_marker" != "$discovery_marker"'
            ' || { echo "the markers are not distinct; refusing"; exit 1; }'
        )
        self.assertLess(lines.index(distinct), lines.index(role))
        self.assertEqual(
            writers(step, "chat-marker"),
            ['printf \'%s\\n\' "$chat_marker" > "$dir/chat-marker"'],
        )
        self.assertEqual(
            writers(step, "discovery-marker"),
            ['printf \'%s\\n\' "$discovery_marker" > "$dir/discovery-marker"'],
        )
        self.assertIn('echo "container=glow-proof-db-chat-${GITHUB_RUN_ID}-', step)

    def test_the_migrations_step_refuses_the_decoys_marker_first(self) -> None:
        step = workflow_step(JOB, "SV4: show the chat database refuses the decoy database's marker")
        self.assertIn("        shell: bash\n", step)
        lines = script_lines(step)
        self.assertEqual(step.count("PROOF_DB_MARKER="), 1)
        self.assertIn(
            'PROOF_DB_PASSFILE="$DIR/passfile" PROOF_DB_MARKER="$(cat "$DIR/$1")" \\', lines
        )
        self.assertIn(
            "PROOF_DB_HOST=127.0.0.1 PROOF_DB_PORT=5433 PROOF_DB_NAME=glow_chat_proof"
            " PROOF_DB_USER=glow_proof \\",
            lines,
        )
        refused_line = (
            "chat discovery-marker python -m django migrate --verbosity 1"
            ' > "$DIR/chat-wrong-marker.log" 2>&1'
        )
        migrate_line = "chat chat-marker python -m django migrate --verbosity 1"
        self.assertEqual(
            [line for line in lines if "python -m django migrate" in line],
            [refused_line, migrate_line],
        )
        sequence = [
            "docker exec \"$CONTAINER\" psql -X -q -At -F ' ' -v ON_ERROR_STOP=1 -U postgres"
            ' -d glow_chat_proof -c "$1"',
            'decoy=$(in_chat_db "SELECT count(*) FROM pg_catalog.pg_database WHERE datname ='
            " 'glow_discovery_proof' AND starts_with(shobj_description(oid, 'pg_database'),"
            " 'glow-ordering-proof:')\")",
            'distinct=$(in_chat_db "SELECT shobj_description((SELECT oid FROM'
            " pg_catalog.pg_database WHERE datname = 'glow_discovery_proof'), 'pg_database') IS"
            " DISTINCT FROM shobj_description((SELECT oid FROM pg_catalog.pg_database WHERE"
            " datname = 'glow_chat_proof'), 'pg_database')\")",
            'if [ "$decoy" != 1 ] || [ "$distinct" != t ]; then echo "FAIL: the decoy database'
            ' or its own marker is missing"; exit 1; fi',
            'in_chat_db "$per_schema" > "$DIR/chat-relations-before.txt"',
            'outside_before=$(in_chat_db "$outside_pg")',
            "set +e",
            refused_line,
            "status=$?",
            "set -e",
            'in_chat_db "$per_schema" > "$DIR/chat-relations-after.txt"',
            'outside_after=$(in_chat_db "$outside_pg")',
            "no_ledger=$(in_chat_db \"SELECT to_regclass('public.django_migrations') IS NULL\")",
            "refusal=$(grep -m 1 -F 'RefusedDatabase: refusing this database'"
            ' "$DIR/chat-wrong-marker.log" || true)',
            "fail=0",
            'if [ "$status" -eq 0 ]; then echo "FAIL: migrate with another database\'s marker'
            ' exited 0"; fail=1; fi',
            'if [ -n "$refusal" ]; then',
            'echo "FAIL: the refusal message is missing (diagnostics withheld)"; fail=1',
            'cmp -s "$DIR/chat-relations-before.txt" "$DIR/chat-relations-after.txt" \\',
            '|| { echo "FAIL: a schema\'s relation count changed"; fail=1; }',
            'if [ "$outside_before" != 0 ] || [ "$outside_after" != 0 ]; then',
            'echo "FAIL: a relation exists outside information_schema and the pg_ schemas"; fail=1',
            'if [ "$no_ledger" != t ]; then echo "FAIL: django_migrations exists"; fail=1; fi',
            'test "$fail" = 0',
            migrate_line,
            "chat chat-marker python -m django makemigrations --check --dry-run",
        ]
        self.assertEqual([line for line in sequence if line not in lines], [])
        at = [lines.index(line) for line in sequence]
        self.assertEqual(at, sorted(at))
        cmp = sequence.index('|| { echo "FAIL: a schema\'s relation count changed"; fail=1; }')
        self.assertEqual(at[cmp], at[cmp - 1] + 1)
        self.assertEqual(lines.count("set +e"), 1)
        self.assertEqual(lines.count("set -e"), 1)
        self.assertLess(step.index('test "$fail" = 0'), step.index(migrate_line))
        self.assertIn('PROOF_IDENTITY_SECRET_KEY_FILE="$DIR/chat-secret-key"', step)
        self.assertIn('PROOF_IDENTITY_JWT_KEY_FILE="$DIR/chat-jwt-key.pem"', step)
        self.assertIn("DJANGO_SETTINGS_MODULE=glow_ordering_proof.chat_settings", step)

    def test_the_dbshell_step_requires_a_failed_exit_and_the_refusal(self) -> None:
        step = workflow_step(JOB, "SV4: show that dbshell is refused")
        self.assertIn("        shell: bash\n", step)
        lines = script_lines(step)
        sequence = [
            "set +e",
            'env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 \\',
            "PROOF_DB_HOST=127.0.0.1 PROOF_DB_PORT=5433 PROOF_DB_NAME=glow_chat_proof"
            " PROOF_DB_USER=glow_proof \\",
            'PROOF_DB_PASSFILE="$DIR/passfile" PROOF_DB_MARKER="$(cat "$DIR/chat-marker")" \\',
            'PROOF_IDENTITY_SECRET_KEY_FILE="$DIR/chat-secret-key" \\',
            'PROOF_IDENTITY_JWT_KEY_FILE="$DIR/chat-jwt-key.pem" \\',
            "DJANGO_SETTINGS_MODULE=glow_ordering_proof.chat_settings \\",
            'python -m django dbshell < /dev/null > "$DIR/chat-dbshell.log" 2>&1',
            "status=$?",
            "set -e",
            "refusal=$(grep -m 1 -F 'RefusedDatabase: refusing dbshell'"
            ' "$DIR/chat-dbshell.log" || true)',
            'rm -f "$DIR/chat-dbshell.log"',
            'echo "chat dbshell exit status: $status"',
            'if [ "$status" -eq 0 ]; then echo "FAIL: dbshell exited 0"; exit 1; fi',
            'if [ -z "$refusal" ]; then echo "FAIL: the dbshell refusal is missing'
            ' (diagnostics withheld)"; exit 1; fi',
            'echo "refusal: $refusal"',
        ]
        self.assertEqual([line for line in sequence if line not in lines], [])
        at = [lines.index(line) for line in sequence]
        self.assertEqual(at, sorted(at))
        self.assertEqual(at[8], at[7] + 1)  # the exit status is the dbshell command's

    def test_the_suite_step_runs_the_check_and_sets_the_output_only_on_a_pass(self) -> None:
        step = workflow_step(JOB, "SV4: run the chat suite")
        self.assertIn("        id: chat\n", step)
        self.assertIn(
            'python -m glow_ordering_proof.chat_scan "$DIR" "$DIR/chat.log"'
            " .work/chat-results.json",
            step,
        )
        self.assertIn(
            "chat python -m glow_ordering_proof chat --results .work/chat-results.json", step
        )
        passed = step.index('if [ "$scan" -eq 0 ]; then')
        withheld = step.index("else", passed)
        output = step.index('echo "scan=passed" >> "$GITHUB_OUTPUT"')
        self.assertTrue(passed < output < withheld)
        self.assertEqual(step.count("scan=passed"), 1)
        self.assertIn('echo "chat phase: $((finished - started)) s', step)
        self.assertIn('if [ "$scan" -ne 0 ]; then echo "FAIL: the secret check did not pass"', step)
        self.assertIn('test "$status" -eq 0', step)

    def test_after_a_failed_check_the_step_prints_counts_only(self) -> None:
        step = workflow_step(JOB, "SV4: run the chat suite")
        lines = step.splitlines()
        start = lines.index('          if [ "$scan" -eq 0 ]; then')
        withheld = lines.index("          else", start)
        end = lines.index("          fi", withheld)
        branch = "\n".join(line[10:] for line in lines[withheld + 1 : end])
        log = [
            "[chat] PASS send.case (D8) 0.1 s: a detail line",
            "[chat] FAIL failed.case (D5) 0.3 s: FAILED: a reason",
            "[chat] cases: 1/2 passed in 0.4 s",
            "chat secret scan: FOUND (9 secrets held; 1 found in 3 log records)",
            "CHAT VERDICT: FAIL",
        ]
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "chat.log").write_text("\n".join(log) + "\n", encoding="utf-8")
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
        step = workflow_step(JOB, "SV4: show that a second chat run on the used database")
        self.assertIn("-d glow_chat_proof", step)
        for table in (
            "auth_user",
            "glow_persistence_appaccount",
            "glow_persistence_profile",
            "glow_persistence_match",
            "glow_persistence_messagesubmission",
            "glow_persistence_outboxevent",
        ):
            with self.subTest(table=table):
                self.assertIn(f"FROM {table})", step)
        self.assertIn("grep -m 1 -F 'refusing a used database'", step)
        self.assertIn('if [ "$before" != "$after" ]; then', step)
        self.assertIn("python -m glow_ordering_proof chat >", step)

    def test_the_upload_waits_for_the_check(self) -> None:
        step = workflow_step(JOB, "SV4: save the chat suite's results JSON")
        self.assertIn("        if: ${{ always() && steps.chat.outputs.scan == 'passed' }}\n", step)
        self.assertIn("name: sv4-chat-results", step)
        self.assertIn("path: proofs/postgres-ordering/.work/chat-results.json", step)

    def test_the_cleanup_removes_everything_whatever_happened(self) -> None:
        step = workflow_step(JOB, "Remove the disposable database")
        self.assertIn("        if: always()\n", step)
        self.assertIn('docker rm --force --volumes "$CONTAINER"', step)
        self.assertIn('rm -rf "$DIR"', step)
        self.assertIn('test -z "$remaining"', step)

    def test_the_job_prints_no_connection_value(self) -> None:
        # Its comments name what it never does; its commands do none of it.
        job = "\n".join(line for line in workflow_job(JOB) if not line.lstrip().startswith("#"))
        for word in ("docker inspect", "DATABASE_URL", "$GITHUB_ENV", "PGPASSWORD", "set -x"):
            with self.subTest(word=word):
                self.assertNotIn(word, job)


# -- the plan --------------------------------------------------------------------------------

PLAN = (
    "routes.refuse_what_is_not_their_dto",
    "send.replay_conflict_and_version",
    "reads.history_list_and_cursor_for_both",
    "send.five_refusals_one_code",
    "d5.each_cause_read_only",
    "ended.unmatch_block_deletion_hidden",
    "d4.block_and_unmatch_serve_the_same",
    "d3.retired_likes_make_no_conversation",
    "match_list.active_matches_newest_first",
    "wrong_member.every_route_not_found",
    "transactions.non_atomic_requests",
    "ar12.like_while_a_block_waits_and_a_match_after_unblock",
    "list.bounded_locks",
    "send.one_answer_for_every_version_and_session",
    "list.block_session_and_own_account_checks",
    "ar13.history_publication_during_a_read",
    "d5.each_cause_hidden",
    "reads.session_ended_in_locks_answers_as_hidden",
)


class ChatPlanTests(unittest.TestCase):
    def test_the_case_count_is_pinned(self) -> None:
        self.assertEqual(chat_cases.CASE_COUNT, 18)
        self.assertEqual(len(chat_cases.CASES), chat_cases.CASE_COUNT)
        self.assertEqual(chat_cases.plan(), PLAN)

    def test_the_cases_that_publish_hidden_run_last(self) -> None:
        # A cause published hidden cannot be made readable again under the launch consent
        # version (SV2's D2), so every read-only case comes first. A2-C1 adds the third, which
        # reads a conversation hidden by a cause (DM-99's AK2).
        self.assertEqual(
            chat_cases.plan()[-3:],
            (
                "ar13.history_publication_during_a_read",
                "d5.each_cause_hidden",
                "reads.session_ended_in_locks_answers_as_hidden",
            ),
        )
        for entry in chat_cases.CASES[:-3]:
            source = ast.unparse(_function(entry.run.__name__))
            with self.subTest(case=entry.case_id):
                self.assertNotIn("hidden", re.findall(r'(\w+)="hidden"', source))
                self.assertNotIn("_publish_history", source)
                self.assertNotIn("publish_setting", source)

    def test_each_d10_item_has_its_case(self) -> None:
        # D10's list, A1's review's AR-12 and AR-13 (D12, "Due at A2"), each by a case's checks.
        labels = {check for entry in chat_cases.CASES for check in entry.checks}
        for label in ("D3", "D4", "D5", "D6", "D8", "D9", "AR-12", "AR-13", "R4"):
            with self.subTest(label=label):
                self.assertIn(label, labels)

    def test_every_case_isolates_its_members(self) -> None:
        source = ast.unparse(_function("run_case"))
        for line in (
            "cache.clear()",
            "ctx.discovery.hide_everyone()",
            "profiles.watch_store()",
            "profiles.hold_media()",
            "ctx.hold_provider_ids()",
        ):
            with self.subTest(line=line):
                self.assertIn(line, source)


def _function(name: str) -> ast.FunctionDef:
    tree = ast.parse((PROOF / "chat_cases.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"no function {name}")


# -- the commands ----------------------------------------------------------------------------------


class ChatCommandTests(unittest.TestCase):
    """``chat`` runs only under the chat settings, and no other command runs under them; both
    refusals come before Django is set up."""

    def call(self, argv: list[str], settings_module: str) -> tuple[int, str]:
        out = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": settings_module}),
            mock.patch.object(commands, "_setup", side_effect=AssertionError("set up")),
            contextlib.redirect_stdout(out),
        ):
            status = commands.main(argv)
        return status, out.getvalue()

    def test_the_chat_command_refuses_every_other_settings_module(self) -> None:
        for module in (
            "glow_ordering_proof.settings",
            "glow_ordering_proof.identity_settings",
            "glow_ordering_proof.profile_settings",
            "glow_ordering_proof.discovery_settings",
            "glow_api.settings",
        ):
            with self.subTest(module=module):
                status, printed = self.call(["chat"], module)
                self.assertEqual(status, 1)
                self.assertIn("refusing: set DJANGO_SETTINGS_MODULE=" + CHAT_SETTINGS, printed)

    def test_no_other_command_runs_under_the_chat_settings(self) -> None:
        for argv in (["facts"], ["run", "--seed", "1"], ["identity"], ["profile"], ["discovery"]):
            with self.subTest(command=argv[0]):
                status, printed = self.call(argv, CHAT_SETTINGS)
                self.assertEqual(status, 1)
                self.assertIn("refusing: only the chat suite runs under the chat settings", printed)

    def test_the_commands_docstring_names_the_chat_command(self) -> None:
        docstring = commands.__doc__ or ""
        self.assertIn("python -m glow_ordering_proof chat --results chat.json", docstring)
        self.assertIn("``chat`` (SV4 A2) runs the chat suite", docstring)


# -- the runner ---------------------------------------------------------------------------------


class ChatRunnerTests(unittest.TestCase):
    """The chat suite installs D14's record before its first statement and checks it, and its
    scans, before its verdict, as the other Django suites do."""

    def source(self) -> str:
        return (PROOF / "chat_suite.py").read_text(encoding="utf-8")

    def test_the_record_is_installed_first_and_checked_before_the_verdict(self) -> None:
        text = self.source()
        install = text.index("lock_record = row_locks.install()")
        self.assertLess(install, text.index("reasons = used_database_reasons()"))
        self.assertLess(install, text.index("server_facts()"))
        check = text.index("summary = lock_record.check()")
        self.assertLess(check, text.index("body = report.to_json()"))
        lines = text.index('for line in summary.lines("chat"):')
        self.assertLess(lines, text.index('print(f"CHAT VERDICT: '))
        self.assertIn("and self.row_lock_failures == 0", text)

    def test_it_refuses_other_settings_a_changed_plan_and_a_superuser(self) -> None:
        text = self.source()
        for line in (
            'if settings.ROOT_URLCONF != "glow_ordering_proof.chat_urls":',
            "if len(chat_cases.CASES) != chat_cases.CASE_COUNT:",
            'if report.server.get("superuser") != "false":',
            "migration_times(migration_ledger())",
            "values.found_in(capture.text(), headers=headers)",
            'values.where(texts, headers="the response headers")',
        ):
            with self.subTest(line=line):
                self.assertIn(line, text)
        self.assertLess(
            text.index("if len(chat_cases.CASES) != chat_cases.CASE_COUNT:"),
            text.index("reasons = used_database_reasons()"),
        )

    def test_a_results_json_holding_a_value_is_not_written(self) -> None:
        text = self.source()
        withheld = text.index(
            "if results_path is not None and (secrets_in_results or values_in_results):"
        )
        written = text.index("results_path.write_text(body")
        self.assertLess(withheld, written)


# -- the support ----------------------------------------------------------------------------------


class ChatSupportTests(unittest.TestCase):
    def test_the_routes_are_the_apis(self) -> None:
        tree = ast.parse((API_ROOT / "glow_chat" / "urls.py").read_text(encoding="utf-8"))
        declared = {
            "/" + str(node.args[0].value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "path"
            and isinstance(node.args[0], ast.Constant)
        }
        self.assertEqual(declared, set(chat_support.CHAT_ROUTES))
        self.assertEqual(chat_support.MATCHES, "/api/v1/matches")

    def test_the_text_reader_is_the_suites_one_provider(self) -> None:
        with mock.patch.object(chat_support, "_PROVIDER", None):
            first = chat_support.text_reader()
            self.assertIs(chat_support.text_reader(), first)
            self.assertIs(chat_support.provider(), first)
            self.assertEqual(type(first).__name__, "FixtureChatProvider")

    def test_a_hold_holds_only_its_points(self) -> None:
        hold = chat_support.Hold("after_locks")
        self.assertIsNone(hold.after_first_lock)
        self.assertIsNone(hold.before_commit)
        self.assertIsNotNone(hold.after_locks)
        hold.on_begin(7)
        self.assertEqual(hold.wait_pid(), 7)
        hold.free()
        with self.assertRaises(ValueError):
            chat_support.Hold("on_commit")

    def test_the_message_texts_are_unique_and_held(self) -> None:
        held: list[str] = []

        class Values:
            def add(self, value: str) -> None:
                held.append(value)

        class Profiles:
            values = Values()

        ctx = chat_support.ChatContext(mock.Mock(profiles=Profiles()))
        texts = {ctx.text() for _ in range(50)}
        self.assertEqual(len(texts), 50)
        self.assertEqual(sorted(held), sorted(texts))


if __name__ == "__main__":
    unittest.main()
