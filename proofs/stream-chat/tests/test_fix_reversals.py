"""P06.1-C3, the C2 review's nit 3: ``checks/fix_reversals.py`` proves what it claims.

A pattern counts only where it starts a line, so a pattern with the wrong
indentation cannot land inside a longer line (C1's "F2 end of run" reversal did,
and made ``cli.py`` fail to compile), and a reversal whose edited file does not
compile or import is "not demonstrated".
"""

import importlib.util
import sys
import tempfile
import unittest
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType
from unittest import mock

import jwt

import tests  # noqa: F401
from tests.fakes import SECRET

PROOF_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROOF_ROOT / "checks" / "fix_reversals.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("fix_reversals", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class FixReversalsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.script = load_script()

    def test_a_pattern_matches_only_at_a_line_start(self) -> None:
        # C1's pattern had 8 spaces; the line it meant has 12.
        text = "    try:\n            problems = run.finish()\n"
        self.assertEqual(self.script.anchored(text, "        problems = run.finish()\n"), [])
        self.assertEqual(self.script.anchored(text, "            problems = run.finish()\n"), [9])

    def test_every_pattern_starts_a_line_once(self) -> None:
        for name, edits, _tests in self.script.R:
            for path, old, _new in edits:
                text = (PROOF_ROOT / path).read_text(encoding="utf-8")
                self.assertEqual(len(self.script.anchored(text, old)), 1, (name, path))

    def test_failure_reasons(self) -> None:
        token = jwt.encode({"user_id": "x"}, SECRET, "HS256")
        separator = "=" * 70 + "\n"
        report = (
            separator
            + "FAIL: test_a (tests.x.T.test_a)\n"
            + "-" * 70
            + "\nTraceback (most recent call last):\n"
            + '  File "x.py", line 1, in test_a\n'
            + f"AssertionError: 'HOLDS' != 'FAIL' near {token}\n"
            + "- HOLDS\n+ FAIL\n\n"
            + separator
            + "ERROR: test_b (unittest.loader._FailedTest.test_b)\n"
            + "-" * 70
            + "\nAttributeError: type object 'T' has no attribute 'test_b'\n\n"
            + "-" * 70
            + "\nRan 2 tests in 0.001s\n\nFAILED (failures=1, errors=1)\n"
        )
        self.assertEqual(
            self.script.failure_reasons(report),
            [
                "FAIL: test_a: AssertionError: 'HOLDS' != 'FAIL' near <jwt>",
                "ERROR: test_b: AttributeError: type object 'T' has no attribute 'test_b'",
            ],
        )
        aborted = 'Traceback (most recent call last):\n  File "x.py"\nKeyboardInterrupt\n'
        self.assertEqual(
            self.script.failure_reasons(aborted),
            ["the test process stopped before reporting: KeyboardInterrupt"],
        )

    def test_every_named_test_exists(self) -> None:
        # A name that does not resolve would make both runs of its reversal fail.
        loader = unittest.TestLoader()
        for name, _edits, test_names in self.script.R:
            for test in test_names:
                cases = list(flatten(loader.loadTestsFromName(test)))
                self.assertTrue(cases, (name, test))
                failed = [c for c in cases if type(c).__name__ == "_FailedTest"]
                self.assertEqual(failed, [], (name, test))

    def test_an_edit_that_does_not_compile_or_import_is_reported(self) -> None:
        # With the interpreter running these tests: a scratch copy of this directory, as
        # the script makes, has no .venv of its own.
        with (
            mock.patch.object(self.script, "PY", sys.executable),
            tempfile.TemporaryDirectory() as tmp,
        ):
            root = Path(tmp)
            (root / "broken.py").write_text("try:\n    x = 1\n", encoding="utf-8")
            (root / "fails.py").write_text("raise RuntimeError('at import')\n", encoding="utf-8")
            (root / "fine.py").write_text("x = 1\n", encoding="utf-8")
            (root / "broken.cjs").write_text("function (\n", encoding="utf-8")
            for path, expected in (
                ("broken.py", "SyntaxError"),
                ("fails.py", "RuntimeError: at import"),
                ("broken.cjs", "SyntaxError"),
            ):
                reason = self.script.loads(root, path)
                self.assertIsNotNone(reason, path)
                self.assertIn(expected, reason)
            self.assertIsNone(self.script.loads(root, "fine.py"))


if __name__ == "__main__":
    unittest.main()
