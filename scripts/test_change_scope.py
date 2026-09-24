"""Exercise real Git histories and the exemption's safety boundaries."""

import os
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest

from change_scope import classify


class ChangeScopeTests(unittest.TestCase):
    def setUp(self):
        self.policy_source = Path(__file__).with_name("change_scope.py").read_text()
        self.old = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.write("app.py", "baseline\n")
        self.write("docs/testing/evidence/notes.md", "notes\n")
        self.base = self.commit()

    def tearDown(self):
        os.chdir(self.old)
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL).decode().strip()

    def write(self, path, value):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(value)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "change")
        return self.git("rev-parse", "HEAD")

    def test_inert_docs_add_edit_delete_and_license(self):
        self.write("docs/continuity/history/new.md", "new\n")
        self.write("apps/mobile/EXPO-TEMPLATE-LICENSE.md", "license\n")
        Path("docs/testing/evidence/notes.md").unlink()
        self.assertFalse(classify(self.base, self.commit())["full"])

    def test_code_hidden_behind_later_docs_commit(self):
        self.write("app.py", "code\n")
        self.commit()
        self.write("docs/testing/evidence/notes.md", "docs\n")
        self.assertTrue(classify(self.base, self.commit(), merge_base=True)["full"])

    def test_code_renamed_into_documentation(self):
        Path("app.py").rename("docs/testing/evidence/app.md")
        self.assertTrue(classify(self.base, self.commit())["full"])

    def test_behavior_markdown_and_configuration(self):
        for path in ["README.md", "services/api/README.md", "docs/operations/build-and-deploy.md", "docs/operations/operational-runbooks.md", "docs/architecture/privacy-and-safety-rules.md", "docs/adr/new-policy.md", "docs/testing/p11-deferred-acceptance.md", "AGENTS.md", "docs/continuity/history/AGENTS.md", "CLAUDE.md", "docs/rules.instructions.md", "docs/pf-canon/policy.md", "docs/ephemeral/prompt.md", "docs/continuity/current-handoff.md", "docs/planning/manager-workflow.md", "docs/planning/new-implementation-brief.md", "docs/planning/nested/assignment.md", ".env.example", ".github/workflows/ci.yml", "docs/code.py", "unknown.md"]:
            with self.subTest(path=path):
                self.write(path, "changed\n")
                self.assertTrue(classify(self.base, self.commit())["full"])
                self.git("reset", "--hard", self.base)

    def test_symlink_and_executable_docs_are_not_exempt(self):
        Path("docs/testing/evidence/notes.md").unlink()
        Path("docs/testing/evidence/notes.md").symlink_to("../../../app.py")
        self.assertTrue(classify(self.base, self.commit())["full"])
        self.git("reset", "--hard", self.base)
        Path("docs/testing/evidence/notes.md").chmod(0o755)
        self.assertTrue(classify(self.base, self.commit())["full"])

    def test_trusted_base_policy_ignores_candidate_substitution(self):
        self.write("scripts/change_scope.py", self.policy_source)
        trusted_base = self.commit()
        # This head would self-exempt if its classifier or tests ran first.
        self.write("scripts/change_scope.py", "import json; print(json.dumps({'full': False}))\n")
        self.write("scripts/test_change_scope.py", 'raise RuntimeError("must not run before classification")\n')
        self.write("argparse.py", 'raise RuntimeError("candidate import shadow")\n')
        head = self.commit()
        with tempfile.TemporaryDirectory() as policy_dir:
            trusted = Path(policy_dir) / "change_scope.py"
            trusted.write_bytes(subprocess.check_output(["git", "show", f"{trusted_base}:scripts/change_scope.py"]))
            import json
            result = json.loads(subprocess.check_output([
                sys.executable, "-I", str(trusted), "--base", trusted_base,
                "--head", head, "--merge-base",
            ]))
        self.assertTrue(result["full"])
        self.assertIn("scripts/test_change_scope.py", result["paths"])

    def test_unknown_base_empty_and_zero_fail_closed(self):
        for base in ["0" * 40, "a" * 40, "--help", self.base]:
            self.assertTrue(classify(base, self.base)["full"])

    def test_pr_compares_merge_base(self):
        self.git("checkout", "-qb", "feature")
        self.write("docs/testing/evidence/notes.md", "feature docs\n")
        head = self.commit()
        self.git("checkout", "--detach", self.base)
        self.write("app.py", "base branch changed\n")
        advanced_base = self.commit()
        self.assertFalse(classify(advanced_base, head, merge_base=True)["full"])


if __name__ == "__main__":
    unittest.main()
