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

from tests.test_profiles_offline import (
    API_ROOT,
    last_json,
    modules,
    scanned_modules,
    under_profile_settings,
)

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
    # SV2 Stage B (D9): the check's approval, and the removal or restriction of a photo.
    ("media.py", "run_check"): "OTHER_FLOW",
    ("media.py", "remove_photo"): "OTHER_FLOW",
    ("staff.py", "restrict_media"): "OTHER_FLOW",
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
    # SV2 Stage B: photo steps that meet or remove no requirement.
    ("media.py", "request_upload"),
    ("media.py", "reorder_photos"),
    ("media.py", "record_upload"),
    ("media.py", "acknowledge_deletion"),
    ("media.py", "review"),
    ("media.py", "request_purge"),
    ("media.py", "delivery_reference"),
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


# C3 (finding 1 (c)): the one write of a profile's state, and every other state write in
# ``glow_profiles`` and the age port, named by its file, line, function and model. Each is a write
# of another model's state; ``_binds`` checks that the variable written holds that model.
RECOMPUTE_WRITE = ("glow_profiles/recompute.py", 138, "recompute", "profile.state = after")
NOT_A_PROFILES_STATE = {
    (
        "glow_profiles/identity_verification.py",
        82,
        "approve_without_id",
        "row.state = VerificationState.STAFF_APPROVED.value",
    ): "IdentityVerification",
    (
        "glow_profiles/identity_verification.py",
        96,
        "revoke_approval",
        "row.state = VerificationState.UNVERIFIED.value",
    ): "IdentityVerification",
    # SV2 Stage B moved these two lines (operations.py gained D19's pointer reads and the owner's
    # approved photos), so their numbers move with them (the carried-items file, "Carried to SV2").
    (
        "glow_profiles/operations.py",
        927,
        "_invalidate_birth_input",
        "current.state = 'missing'",
    ): "BirthInput",
    (
        "glow_profiles/operations.py",
        947,
        "_mapping_to_pending",
        "mapping.state = 'pending'",
    ): "EngineIdentity",
    # SV2 Stage B (D10): a photo's one state write, another model's (F05's registry table).
    (
        "glow_profiles/media.py",
        128,
        "transition",
        "asset.state = after",
    ): "MediaAsset",
    (
        "glow_identity/age.py",
        98,
        "transition",
        "row.state = change.state.value",
    ): "AccountAgeState",
}


def _writes_state(node: ast.Call) -> bool:
    """SV2 Stage B (the delta review's N2): a ``bulk_create`` writes a state when it upserts
    (``update_conflicts``, ``update_fields`` or ``unique_fields``), unpacks ``**``, or builds any
    object with a ``state`` keyword, whatever the receiver."""
    keywords = {keyword.arg for keyword in node.keywords}
    if keywords & {"update_conflicts", "update_fields", "unique_fields", None}:
        return True
    return any(
        isinstance(inner, ast.Call)
        and any(keyword.arg in ("state", None) for keyword in inner.keywords)
        for argument in node.args
        for inner in ast.walk(argument)
    )


def _state_writes(tree: ast.Module) -> list[tuple[int, str, str]]:
    """Every way the static guard sees a state written, by line, function and statement: an
    assignment to any ``.state``; any ``setattr``, ``__setattr__``, ``__dict__`` or ``vars``;
    any ``bulk_update``; any ``update``, ``update_or_create`` or ``get_or_create`` whose
    keywords name ``state`` or ``defaults``, or are unpacked with ``**``; and (SV2 Stage B, N2)
    any ``bulk_create`` that writes a state (``_writes_state``), whatever the receiver."""
    found = []
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    def owner(node: ast.AST) -> str:
        line = getattr(node, "lineno", 0)
        holding = [
            function.name
            for function in functions
            if function.lineno <= line <= (function.end_lineno or line)
        ]
        return holding[-1] if holding else "<module>"

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign | ast.AugAssign | ast.AnnAssign):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if any(
                    isinstance(part, ast.Attribute) and part.attr == "state"
                    for part in ast.walk(target)
                ):
                    found.append((node.lineno, owner(node), ast.unparse(node)))
        if isinstance(node, ast.Attribute) and node.attr in {"__setattr__", "__dict__"}:
            found.append((node.lineno, owner(node), ast.unparse(node)))
        if isinstance(node, ast.Call):
            called = ast.unparse(node.func)
            attr = node.func.attr if isinstance(node.func, ast.Attribute) else called
            keywords = {keyword.arg for keyword in node.keywords}
            if (
                called in {"setattr", "vars"}
                or attr == "bulk_update"
                or attr in {"update", "update_or_create", "get_or_create"}
                and keywords & {"state", "defaults", "create_defaults", None}
                or attr == "bulk_create"
                and _writes_state(node)
            ):
                found.append((node.lineno, owner(node), ast.unparse(node)))
    return found


def _bound_names(target: ast.expr) -> set[str]:
    """The names a target binds: a name, or each name of a tuple, list or starred target (not an
    attribute or a subscript, which bind nothing)."""
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, ast.Tuple | ast.List):
        return set().union(*(_bound_names(element) for element in target.elts))
    if isinstance(target, ast.Starred):
        return _bound_names(target.value)
    return set()


def _other_bindings(function: ast.FunctionDef, variable: str) -> list[str]:
    """SV2 Stage B (the delta review's N3): every way ``function`` binds ``variable`` other than
    a plain ``variable = value``: tuple or starred unpacking, an annotated or augmented
    assignment, the walrus, a ``for`` or comprehension target, a ``with`` target, an ``except``
    name, a parameter, an import, or ``global`` and ``nonlocal``."""
    found: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name) and variable in _bound_names(target):
                    found.append(f"unpacking:{node.lineno}")
        elif isinstance(node, ast.AnnAssign | ast.AugAssign):
            if variable in _bound_names(node.target):
                found.append(f"annotated_or_augmented:{node.lineno}")
        elif isinstance(node, ast.NamedExpr):
            if variable in _bound_names(node.target):
                found.append(f"walrus:{node.lineno}")
        elif isinstance(node, ast.For | ast.AsyncFor | ast.comprehension):
            if variable in _bound_names(node.target):
                found.append(f"for:{getattr(node, 'lineno', 0)}")
        elif isinstance(node, ast.withitem):
            if node.optional_vars is not None and variable in _bound_names(node.optional_vars):
                found.append("with")
        elif isinstance(node, ast.ExceptHandler):
            if node.name == variable:
                found.append(f"except:{node.lineno}")
        elif isinstance(node, ast.arg):
            if node.arg == variable:
                found.append(f"parameter:{node.lineno}")
        elif isinstance(node, ast.Import | ast.ImportFrom):
            if any((alias.asname or alias.name).split(".")[0] == variable for alias in node.names):
                found.append(f"import:{node.lineno}")
        elif isinstance(node, ast.Global | ast.Nonlocal):
            if variable in node.names:
                found.append(f"global:{node.lineno}")
    return found


def _binds(function: ast.FunctionDef, variable: str, model: str, module: ast.Module) -> bool:
    """Whether every value ``function`` binds to ``variable`` is ``model``'s: an expression naming
    the model, or a call of a helper of the same module whose every return names it. Any other
    form of binding (``_other_bindings``; N3) is not seen to hold the model, so it fails."""
    helpers = {
        node.name: node
        for node in ast.walk(module)
        if isinstance(node, ast.FunctionDef) and node is not function
    }
    if _other_bindings(function, variable):
        return False
    values = [
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == variable for t in node.targets)
    ]
    if not values:
        return False
    for value in values:
        if model in ast.unparse(value).split("(")[0].split("."):
            continue
        called = value.func if isinstance(value, ast.Call) else None
        name = (
            called.attr
            if isinstance(called, ast.Attribute)
            else called.id
            if isinstance(called, ast.Name)
            else ""
        )
        helper = helpers.get(name)
        returns = (
            [r.value for r in ast.walk(helper) if isinstance(r, ast.Return) and r.value]
            if helper is not None
            else []
        )
        if not returns or not all(model in ast.unparse(r) for r in returns):
            return False
    return True


# The one creation of a profile (the profile edit's), by file, function and statement.
PROFILE_CREATE = (
    "glow_profiles/operations.py",
    "body",
    "Profile.objects.create(account_id=account_id, display_name=intent['display_name'],"
    " bio=intent['summary'], state='incomplete')",
)


def _profile_creations(trees: dict[str, ast.Module]) -> list[tuple[str, str, str]]:
    """Every ``create``, ``get_or_create``, ``update_or_create`` or ``bulk_create`` on a receiver
    naming ``Profile``, and every ``Profile(...)`` built, in the scanned modules (N2)."""
    found = []
    for name, tree in trees.items():
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            creates = (
                isinstance(func, ast.Attribute)
                and func.attr in {"create", "get_or_create", "update_or_create", "bulk_create"}
                and "Profile" in ast.unparse(func.value).replace("(", ".").split(".")
            )
            builds = isinstance(func, ast.Name) and func.id == "Profile"
            if creates or builds:
                holding = [
                    function.name
                    for function in functions
                    if function.lineno <= node.lineno <= (function.end_lineno or node.lineno)
                ]
                found.append((name, holding[-1] if holding else "<module>", ast.unparse(node)))
    return found


# SV2 Stage B, correction C2 (the exact-head review's F3): the one creation of a photo, the
# grant's new asset ``upload_pending``, by file, enclosing definitions and statement. Every other
# state a photo reaches is ``transition``'s (``NOT_A_PROFILES_STATE``).
ASSET_CREATE = (
    "glow_profiles/media.py",
    "request_upload.body",
    "MediaAsset.objects.create(account_id=account_id, provider=adapters.storage.name,"
    " storage_ref=key, position=position, state=md.UPLOAD_PENDING)",
)
# Every creation in ``glow_profiles`` and the age port that sets a ``state``, whatever its
# receiver is named, by file, enclosing definitions, the call and the state it sets: a
# ``create``, ``get_or_create`` or ``update_or_create``, or a class built with ``state=`` (or
# ``**``). Each sets its own model's initial state, and only the photo's is ``MediaAsset``'s.
CREATIONS_WITH_STATE = {
    ("glow_identity/age.py", "OrmAgeAssurance.record", "AccountAgeState.objects.create")
    + ("assurance.state.value",),
    ("glow_profiles/events.py", "emit", "OutboxEvent.objects.create", "'pending'"),
    ("glow_profiles/idempotency.py", "store", "IdempotencyRecord.objects.create", "'completed'"),
    ("glow_profiles/media.py", "request_upload.body", "MediaAsset.objects.create")
    + ("md.UPLOAD_PENDING",),
    ("glow_profiles/operations.py", "save_birth_input.body", "BirthInput.objects.create")
    + ("'pending'",),
    ("glow_profiles/operations.py", "save_profile.body", "Profile.objects.create")
    + ("'incomplete'",),
    ("glow_profiles/operations.py", "decide_sensitive_consent.body")
    + ("ConsentDecision.objects.create", "'accepted' if accepting else 'withdrawn'"),
}
CREATING = {"create", "get_or_create", "update_or_create", "bulk_create"}


def _enclosing(tree: ast.Module, line: int) -> str:
    """The classes and functions that enclose ``line``, outermost first, dotted."""
    holding = sorted(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
            and node.lineno <= line <= (node.end_lineno or line)
        ),
        key=lambda node: node.lineno,
    )
    return ".".join(node.name for node in holding) or "<module>"


def _asset_creations(trees: dict[str, ast.Module]) -> list[tuple[str, str, str]]:
    """Every ``create``, ``get_or_create``, ``update_or_create`` or ``bulk_create`` on a receiver
    naming ``MediaAsset``, and every ``MediaAsset(...)`` built, in the scanned modules (F3)."""
    found = []
    for name, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            creates = (
                isinstance(func, ast.Attribute)
                and func.attr in CREATING
                and "MediaAsset" in ast.unparse(func.value).replace("(", ".").split(".")
            )
            builds = ast.unparse(func).split(".")[-1] == "MediaAsset"
            if creates or builds:
                found.append((name, _enclosing(tree, node.lineno), ast.unparse(node)))
    return found


def _creations_with_state(trees: dict[str, ast.Module]) -> set[tuple[str, ...]]:
    """Every creation that sets a ``state`` (or unpacks ``**``), whatever its receiver: a
    ``create``, ``get_or_create`` or ``update_or_create``, or a call of a name that starts with
    a capital (a class built), by file, enclosing definitions, call and the state it sets (F3)."""
    found = set()
    for name, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            last = ast.unparse(node.func).split(".")[-1]
            if not (last in CREATING - {"bulk_create"} or last[:1].isupper()):
                continue
            for keyword in node.keywords:
                if keyword.arg in ("state", None):
                    found.add(
                        (
                            name,
                            _enclosing(tree, node.lineno),
                            ast.unparse(node.func),
                            ast.unparse(keyword.value),
                        )
                    )
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
        # C3 (finding 1 (c)): every state write the guard can see, under any name, in
        # ``glow_profiles`` and the age port, is the recompute's or on the allowlist of writes
        # that are not a profile's; and each allowlisted write holds the model it names.
        trees = scanned_modules()
        seen = {
            (name, line, function, statement)
            for name, tree in trees.items()
            for line, function, statement in _state_writes(tree)
        }
        self.assertEqual(seen, {RECOMPUTE_WRITE, *NOT_A_PROFILES_STATE})
        for (name, _line, function, statement), model in NOT_A_PROFILES_STATE.items():
            with self.subTest(write=statement, model=model):
                tree = trees[name]
                defined = next(
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef) and node.name == function
                )
                variable = statement.split(".")[0]
                self.assertTrue(_binds(defined, variable, model, tree), (variable, model))
                self.assertNotEqual(model, "Profile")
        recompute_tree = trees[RECOMPUTE_WRITE[0]]
        recompute_function = next(
            node
            for node in ast.walk(recompute_tree)
            if isinstance(node, ast.FunctionDef) and node.name == RECOMPUTE_WRITE[2]
        )
        self.assertTrue(_binds(recompute_function, "profile", "Profile", recompute_tree))
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
        # SV2 Stage B (the delta review's N2): no profile is created, built or bulk-created
        # anywhere else in ``glow_profiles`` or the age port, whatever the receiver is named.
        self.assertEqual(_profile_creations(trees), [PROFILE_CREATE])

    def test_a_photo_is_created_only_upload_pending(self) -> None:
        # SV2 Stage B, correction C2 (the exact-head review's F3): the state-write guard above
        # reads assignments and updates, so a ``MediaAsset.objects.create(state=...)`` or a
        # ``MediaAsset(state=...)`` outside ``transition`` passed it. A photo is created once,
        # by the grant, ``upload_pending``; and no creation anywhere in ``glow_profiles`` or the
        # age port sets a state but the allowlist's, whatever its receiver is named.
        trees = scanned_modules()
        self.assertEqual(_asset_creations(trees), [ASSET_CREATE])
        self.assertEqual(_creations_with_state(trees), CREATIONS_WITH_STATE)
        photos = [entry for entry in CREATIONS_WITH_STATE if "MediaAsset" in entry[2]]
        self.assertEqual(
            photos, [(*ASSET_CREATE[:2], "MediaAsset.objects.create", "md.UPLOAD_PENDING")]
        )

    def test_the_creation_guard_sees_each_spelling(self) -> None:
        # Each spelling F3 names, as ``_asset_creations`` and ``_creations_with_state`` see it.
        tree = ast.parse(
            "def restrict(asset_id):\n"
            "    MediaAsset.objects.create(state='approved')\n"
            "    models.MediaAsset(state='approved').save()\n"
            "    MediaAsset.objects.get_or_create(pk=asset_id, state='approved')\n"
            "    MediaAsset.objects.update_or_create(pk=asset_id, state='approved')\n"
            "    model = MediaAsset\n"
            "    model.objects.create(state='approved')\n"
            "    Asset(**fields)\n"
        )
        trees = {"glow_profiles/staff.py": tree}
        self.assertEqual(len(_asset_creations(trees)), 4)
        self.assertEqual(
            {(entry[2], entry[3]) for entry in _creations_with_state(trees)},
            {
                ("MediaAsset.objects.create", "'approved'"),
                ("models.MediaAsset", "'approved'"),
                ("MediaAsset.objects.get_or_create", "'approved'"),
                ("MediaAsset.objects.update_or_create", "'approved'"),
                ("model.objects.create", "'approved'"),
                ("Asset", "fields"),
            },
        )

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
