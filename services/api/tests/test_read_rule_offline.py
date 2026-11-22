"""SV4 A1 (its brief's D5; OD-60, H; DM-96): the read rule's decision, offline. ``readable``
serves a conversation read-only only while ``chat.history`` names the launch onboarding version
and every cause present reads ``read_only``: one hidden cause hides the conversation whatever the
others read, and a missing key, another value or another version reads hidden (fail-closed). A
setting that cannot be resolved refuses the read. The database cases are the ordering suite's
``read.d5_*`` cases; this module loads ``glow_chat.reads`` under the static model registry in a
fresh process, as ``test_chat_reads_offline`` does, so no database is opened.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]

PRELUDE = """
from unittest import mock
from glow_persistence.static_check import no_database_access, setup_static_registry
with no_database_access():
    setup_static_registry()
    from glow_chat import reads
    from glow_domain import profile_settings as ps
    from glow_profiles.tx import POLICY_UNRESOLVED, Refused

    LAUNCH = dict(ps.LAUNCH_DEFAULTS[ps.HISTORY])
    CAUSES = ps.HISTORY_CAUSES
"""


class ReadRuleTests(unittest.TestCase):
    def check_script(self, assertions: str) -> None:
        body = "\n".join("    " + line for line in assertions.splitlines())
        result = subprocess.run(
            [sys.executable, "-c", PRELUDE + body],
            cwd=API_ROOT,
            env={**os.environ, "GLOW_ENV": "test"},
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_launch_default_reads_every_cause_read_only(self) -> None:
        self.check_script("""
assert reads.LAUNCH_CONSENT_POLICY_VERSION == "consent.onboarding.v1"
assert set(CAUSES) == {"own_pause", "other_pause", "restriction", "suspension",
                       "withdrawn_consent"}
assert reads.readable((), LAUNCH)
for cause in CAUSES:
    assert reads.readable((cause,), LAUNCH), cause
assert reads.readable(CAUSES, LAUNCH)
""")

    def test_one_hidden_cause_hides_the_conversation_whatever_the_others_read(self) -> None:
        self.check_script("""
for hidden in CAUSES:
    content = {**LAUNCH, hidden: "hidden"}
    assert not reads.readable((hidden,), content), hidden
    for other in CAUSES:
        if other != hidden:
            # The other cause alone is still read-only; together with the hidden one, hidden.
            assert reads.readable((other,), content), (hidden, other)
            assert not reads.readable((hidden, other), content), (hidden, other)
            assert not reads.readable((other, hidden), content), (hidden, other)
    assert not reads.readable(CAUSES, content), hidden
""")

    def test_another_version_a_missing_key_or_another_value_reads_hidden(self) -> None:
        self.check_script("""
other_version = {**LAUNCH, "consent_policy_version": "consent.onboarding.v2"}
for cause in CAUSES:
    assert not reads.readable((cause,), other_version), cause
    missing = {k: v for k, v in LAUNCH.items() if k != cause}
    assert not reads.readable((cause,), missing), cause
    for value in ("", "Read_Only", "visible", None, True):
        assert not reads.readable((cause,), {**LAUNCH, cause: value}), (cause, value)
no_version = {k: v for k, v in LAUNCH.items() if k != "consent_policy_version"}
assert not reads.readable(("own_pause",), no_version)
# With no cause, the setting decides nothing: the conversation is served.
assert reads.readable((), other_version) and reads.readable((), {})
""")

    def test_an_unresolved_setting_refuses_the_read(self) -> None:
        self.check_script("""
for reason in ("setting_unresolved", "setting_version_missing", "setting_pointer_mismatch"):
    with mock.patch.object(
        reads.settings_store, "read_shared", side_effect=Refused(POLICY_UNRESOLVED, reason)
    ):
        try:
            reads._history(object())
        except reads._Refused as refused:
            assert refused.reason == reason, refused.reason
        else:
            raise AssertionError("an unresolved setting was read as readable")
""")

    def test_the_setting_is_read_through_the_store_only_after_the_row_locks(self) -> None:
        # D5 (SV2's D19): ``chat.history``'s pointer through ``settings_store.read_shared``,
        # after every row lock and before the clock, in the history read's check and the list.
        import ast

        source = (API_ROOT / "glow_chat" / "reads.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        bodies = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name in ("_authorize", "_list")
        }
        self.assertEqual(set(bodies), {"_authorize", "_list"})
        for name, function in bodies.items():
            with self.subTest(function=name):
                lines = [ast.unparse(statement) for statement in function.body]
                history = [
                    i for i, line in enumerate(lines) if line == "history = _history(cursor)"
                ]
                self.assertEqual(len(history), 1, lines)
                locks = [i for i, line in enumerate(lines) if "_lock_shared(" in line]
                self.assertTrue(locks)
                self.assertLess(max(locks), history[0])
                clock = lines.index("now = _clock(cursor)")
                self.assertLess(history[0], clock)
        self.assertIn("settings_store.read_shared(", source)
        self.assertNotIn("policyrevision", source.lower())
