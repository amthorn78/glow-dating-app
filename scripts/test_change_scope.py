"""Exercise real Git histories and the exemption's safety boundaries."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from change_scope import classify


class ChangeScopeTests(unittest.TestCase):
    def setUp(self):
        self.old = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.write("app.py", "baseline\n")
        self.write("docs/notes.md", "notes\n")
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

    def test_docs_add_edit_delete_and_readme(self):
        self.write("docs/new.md", "new\n")
        self.write("README.md", "readme\n")
        Path("docs/notes.md").unlink()
        self.assertFalse(classify(self.base, self.commit())["full"])

    def test_code_hidden_behind_later_docs_commit(self):
        self.write("app.py", "code\n")
        self.commit()
        self.write("docs/notes.md", "docs\n")
        self.assertTrue(classify(self.base, self.commit(), merge_base=True)["full"])

    def test_code_renamed_into_documentation(self):
        Path("app.py").rename("docs/app.md")
        self.assertTrue(classify(self.base, self.commit())["full"])

    def test_behavior_markdown_and_configuration(self):
        for path in ["AGENTS.md", "docs/nested/AGENTS.md", "CLAUDE.md", "docs/rules.instructions.md", "docs/pf-canon/policy.md", "docs/ephemeral/prompt.md", "docs/continuity/current-handoff.md", "docs/planning/manager-workflow.md", ".env.example", ".github/workflows/ci.yml", "docs/code.py", "unknown.md"]:
            with self.subTest(path=path):
                self.write(path, "changed\n")
                self.assertTrue(classify(self.base, self.commit())["full"])
                self.git("reset", "--hard", self.base)

    def test_symlink_and_executable_docs_are_not_exempt(self):
        Path("docs/notes.md").unlink()
        Path("docs/notes.md").symlink_to("../app.py")
        self.assertTrue(classify(self.base, self.commit())["full"])
        self.git("reset", "--hard", self.base)
        Path("docs/notes.md").chmod(0o755)
        self.assertTrue(classify(self.base, self.commit())["full"])

    def test_unknown_base_empty_and_zero_fail_closed(self):
        for base in ["0" * 40, "a" * 40, "--help", self.base]:
            self.assertTrue(classify(base, self.base)["full"])

    def test_pr_compares_merge_base(self):
        self.git("checkout", "-qb", "feature")
        self.write("docs/notes.md", "feature docs\n")
        head = self.commit()
        self.git("checkout", "--detach", self.base)
        self.write("app.py", "base branch changed\n")
        advanced_base = self.commit()
        self.assertFalse(classify(advanced_base, head, merge_base=True)["full"])


if __name__ == "__main__":
    unittest.main()
