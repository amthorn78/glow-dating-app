"""SV2 Stage A, correction C1: D9's one shared recompute (DM-54, Y3 to Y5), the parts that need no
database.

- the rule: ``incomplete`` with nothing missing becomes ``visible``, ``visible`` with anything
  missing becomes ``incomplete``, and ``paused``, ``restricted`` and ``removed`` stay;
- the registry entry each change is, and that each is in ``flows-v1.json``'s F04 with its role;
- every writer of D9's Stage A list ends with the recompute, with its own kind of writer, and no
  other operation calls it;
- only the recompute writes a profile's state (``glow_chat``'s pause, resume and restriction
  aside), so nothing else can make a profile ``visible``.

The profile suite on the disposable PostgreSQL shows each writer doing it through the routes.
"""

import ast
import json
import unittest

from tests.test_profiles_offline import API_ROOT, last_json, modules, under_profile_settings

FLOWS = API_ROOT.parents[1] / "packages" / "contracts" / "production" / "flows-v1.json"

# D9's writers for Stage A (DM-54, Y3), each with the kind of writer that decides the registry
# entry of its change.
WRITERS = {
    ("operations.py", "save_profile"): "PROFILE_EDIT",
    ("operations.py", "set_field"): "F04_OWNER",
    ("operations.py", "set_area"): "F04_OWNER",
    ("operations.py", "decide_onboarding_consent"): "OTHER_FLOW",
    ("operations.py", "adult_check"): "OTHER_FLOW",
    ("operations.py", "save_birth_input"): "OTHER_FLOW",
    ("staff.py", "approve_without_id"): "OTHER_FLOW",
    ("staff.py", "revoke_approval"): "OTHER_FLOW",
}
# The operations that write no completion requirement, so never recompute.
NOT_WRITERS = {
    ("operations.py", "read"),
    ("operations.py", "set_preferences"),
    ("operations.py", "set_filters"),
    ("operations.py", "nearest_area"),
    ("operations.py", "decide_sensitive_consent"),
    ("operations.py", "set_visibility"),
    ("staff.py", "publish_setting"),
    ("staff.py", "restrict_profile"),
}


def _recompute_calls(node: ast.AST) -> list[str]:
    """The ``writer=`` of every ``recompute.recompute(...)`` call under ``node``."""
    found = []
    for call in ast.walk(node):
        if (
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "recompute"
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "recompute"
        ):
            writer = next(k.value for k in call.keywords if k.arg == "writer")
            found.append(ast.unparse(writer))
    return found


def _helpers(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    return {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}


def _calls_of(writer: ast.FunctionDef, helpers: dict[str, ast.FunctionDef]) -> list[str]:
    """The recompute calls a writer makes itself or through a module helper it calls."""
    found = _recompute_calls(writer)
    for call in ast.walk(writer):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
            helper = helpers.get(call.func.id)
            if helper is not None and helper is not writer:
                found += _recompute_calls(helper)
    return found


class RuleTests(unittest.TestCase):
    def test_the_rule_and_the_registry_entries(self) -> None:
        seen = last_json(
            under_profile_settings(
                """
import json
from glow_profiles import recompute as r

states = ("incomplete", "visible", "paused", "restricted", "removed")
rule = {f"{s}|{bool(m)}": r.next_state(s, m) for s in states for m in ((), ("chart",))}
entries = {
    f"{w}|{b}|{a}": r.entry(w, b, a)
    for w in r.WRITERS
    for b, a in (("incomplete", "visible"), ("visible", "incomplete"), ("paused", "paused"))
}
cleared = {
    f"{b}|{a}": r.entry(r.PROFILE_EDIT, b, a, clears_summary=True)
    for b, a in (("incomplete", "visible"), ("visible", "incomplete"), ("paused", "paused"))
}
rides = {
    f"{w}|{c}": r.rides_on_the_edit(w, c)
    for w in r.WRITERS
    for c in ("complete", "edit", "requirement_removed", "requirements_met")
}
others = []
for w in (r.F04_OWNER, r.OTHER_FLOW):
    try:
        r.entry(w, "visible", "incomplete", clears_summary=True)
    except ValueError:
        others.append(w)
print(json.dumps({"rule": rule, "entries": entries, "cleared": cleared, "rides": rides,
                  "others": others}))
"""
            )
        )
        self.assertEqual(
            seen["rule"],
            {
                "incomplete|False": "visible",
                "incomplete|True": "incomplete",
                "visible|False": "visible",
                "visible|True": "incomplete",
                "paused|False": "paused",
                "paused|True": "paused",
                "restricted|False": "restricted",
                "restricted|True": "restricted",
                "removed|False": "removed",
                "removed|True": "removed",
            },
        )
        self.assertEqual(
            seen["entries"],
            {
                "profile_edit|incomplete|visible": "complete",
                # C2 (DM-55, section 6): a lapse the edit finds but did not cause.
                "profile_edit|visible|incomplete": "requirement_removed",
                "profile_edit|paused|paused": None,
                "f04_owner|incomplete|visible": "complete",
                "f04_owner|visible|incomplete": "requirement_removed",
                "f04_owner|paused|paused": None,
                "other_flow|incomplete|visible": "requirements_met",
                "other_flow|visible|incomplete": "requirement_removed",
                "other_flow|paused|paused": None,
            },
        )
        # The edit that clears the summary itself is the owner's edit, whatever else is missing.
        self.assertEqual(
            seen["cleared"],
            {"incomplete|visible": "complete", "visible|incomplete": "edit", "paused|paused": None},
        )
        # Only the profile edit's complete and its owner edit ride on the edit's own write; every
        # other change is a transition of its own, with its bumps and event.
        self.assertEqual(
            {key for key, rides in seen["rides"].items() if rides},
            {"profile_edit|complete", "profile_edit|edit"},
        )
        self.assertEqual(seen["others"], ["f04_owner", "other_flow"])

    def test_every_entry_the_recompute_names_is_in_the_registry(self) -> None:
        flows = json.loads(FLOWS.read_text(encoding="utf-8"))["flows"]
        f04 = next(flow for flow in flows if flow["id"] == "F04")["transitions"]
        rules = {(t["event"], t["from"], t["to"]): t for t in f04}
        for event, before, after, role in (
            ("complete", "incomplete", "visible", "owner"),
            ("requirements_met", "incomplete", "visible", "system"),
            ("edit", "visible", "incomplete", "owner"),
            ("requirement_removed", "visible", "incomplete", "system"),
        ):
            with self.subTest(event=event):
                rule = rules[(event, before, after)]
                self.assertEqual(rule["role"], role)
                self.assertEqual(rule["eligible"], after == "visible")


class CallSiteTests(unittest.TestCase):
    def test_every_requirement_writer_ends_with_the_recompute(self) -> None:
        trees = modules()
        for (name, function), writer in WRITERS.items():
            with self.subTest(writer=function):
                helpers = _helpers(trees[name])
                calls = _calls_of(helpers[function], helpers)
                self.assertTrue(calls, f"{function} does not recompute")
                self.assertEqual(set(calls), {f"recompute.{writer}"})
        for name, function in NOT_WRITERS:
            with self.subTest(other=function):
                helpers = _helpers(trees[name])
                self.assertEqual(_calls_of(helpers[function], helpers), [])

    def test_only_the_recompute_writes_a_profiles_state(self) -> None:
        writes = []
        for name, tree in modules().items():
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and target.attr == "state"
                            and ast.unparse(target.value) == "profile"
                        ):
                            writes.append((name, ast.unparse(node.value)))
        self.assertEqual(writes, [("recompute.py", "after")])
        # C2 (finding 7): nor a queryset ``.update(state=...)`` on a profile, anywhere.
        updates = [
            (name, node.lineno)
            for name, tree in modules().items()
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "update"
            and "Profile" in ast.unparse(node.func.value)
            and any(k.arg in ("state", None) for k in node.keywords)
        ]
        self.assertEqual(updates, [])
        created = [
            ast.unparse(keyword.value)
            for node in ast.walk(modules()["operations.py"])
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "Profile.objects.create"
            for keyword in node.keywords
            if keyword.arg == "state"
        ]
        self.assertEqual(created, ["'incomplete'"])

    def test_a_failing_date_returns_its_refusal_at_both_writers(self) -> None:
        # DM-54, Y6 to Y8; DM-55, Z2: at both writers a date under 18 from a self-declared adult
        # resets the account and returns the refusal, so tx.run commits the reset, and nothing of
        # the date is written: the reset creates no revision and stores no idempotency record.
        helpers = _helpers(modules()["operations.py"])
        reset = helpers["_reset_failing_date"]
        # Its one raise is the age port's own refusal (a state conflict), never the date's.
        self.assertEqual(
            [ast.unparse(node) for node in ast.walk(reset) if isinstance(node, ast.Raise)],
            ["raise Refused(STATE_CONFLICT, f'age:{refused}') from None"],
        )
        called = {ast.unparse(node.func) for node in ast.walk(reset) if isinstance(node, ast.Call)}
        self.assertFalse(called & {"BirthInput.objects.create", "idempotency.store"})
        self.assertIn("recompute.recompute", called)
        self.assertFalse([n for n in ast.walk(reset) if isinstance(n, ast.Return)])
        for writer, reason in (
            ("adult_check", "ADULT_CHECK_UNDER_AGE"),
            ("save_birth_input", "BIRTH_DATE_FAILS_ADULT_RULE"),
        ):
            with self.subTest(writer=writer):
                body = next(
                    node
                    for node in ast.walk(helpers[writer])
                    if isinstance(node, ast.FunctionDef) and node.name == "body"
                )
                found = [
                    (ast.unparse(block[index]), ast.unparse(block[index + 1]))
                    for node in ast.walk(body)
                    for block in [getattr(node, "body", None)]
                    if isinstance(block, list)
                    for index in range(len(block) - 1)
                    if ast.unparse(block[index]).startswith("_reset_failing_date(")
                ]
                self.assertEqual(
                    found,
                    [
                        (
                            "_reset_failing_date(tx, account_id, now)",
                            f"return Result('refused', FORBIDDEN, {reason})",
                        )
                    ],
                )
