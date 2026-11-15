"""SV3 Stage B, the parts that need no database (its brief's D9 to D13, D17 and D19, and the review
plan's D10 bullet).

- **Requests** (D9, D11, D12; D13): ``contract.parse`` accepts each of Stage B's four closed
  intents and refuses what the production schema refuses, so the server and the contract agree.
- **Projections and receipts** (D13): each projection validates as its DTO and inside
  ``AppResponse``; the internal command result keeps only the projection its receipt allows, and
  its receipt never changes with the projection.
- **Policy** (D12): resurfacing's cutoff and undo's window follow their settings, off at launch.
- **Predicates** (D7, D12; Stage B's item 3): one consumption clause for the selection, every
  recheck and the like's own check; ``VIEWER`` selects no distance choice.
- **Rematch** (D12): ``discovery.rematch`` cannot be switched on (``rematch_not_built``).
- **Structure** (D2, D9 to D11, D17, D19): each command locks both accounts first, reads its
  settings in one call, names no lock or pointer table, and logs codes only; ``glow_chat`` imports
  nothing from ``glow_discovery``; ``activate_reciprocal`` is called only from the like.
- **D10's writer** (the review plan): every function and method of ``glow_chat/contact.py`` at
  main's base is unchanged at the working tree, by AST; ``activate_reciprocal`` is the only new
  one, and its body is ``activate_match``'s with exactly one statement inserted.

Each Django-dependent check runs in a fresh process under ``tests.discovery_offline_settings``
(Django's dummy backend; keys generated for that process), as ``test_discovery_offline`` does. The
cases themselves run on a disposable PostgreSQL in ``proofs/postgres-ordering``'s discovery suite.
All data is synthetic.
"""

import ast
import copy
import difflib
import hashlib
import os
import re
import subprocess
import unittest
from pathlib import Path

from glow_domain import profile_settings as ps
from tests.test_discovery_offline import under_discovery_settings
from tests.test_profiles_offline import last_json

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = API_ROOT.parents[1]
DISCOVERY = API_ROOT / "glow_discovery"
CHAT = API_ROOT / "glow_chat"
CONTACT = CHAT / "contact.py"
CONTACT_IN_REPO = "services/api/glow_chat/contact.py"
COMMANDS = ("interact", "undo", "unmatch", "block")
INTENTS = ("InteractionIntent", "InteractionUndoIntent", "UnmatchIntent", "BlockIntent")


def parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def top_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"no function {name}")


def inner_body(function: ast.FunctionDef) -> ast.FunctionDef:
    """The command's transaction body: its nested ``def body(tx)``."""
    found = [n for n in function.body if isinstance(n, ast.FunctionDef) and n.name == "body"]
    assert len(found) == 1, function.name
    return found[0]


def called(node: ast.AST) -> list[str]:
    return [ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)]


def docstring_ids(tree: ast.AST) -> set[int]:
    return {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    }


def code_strings(tree: ast.AST) -> list[str]:
    """Every string constant outside docstrings (f-strings' literal parts included)."""
    skip = docstring_ids(tree)
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in skip
    ]


# -- requests (D9, D11, D12; D13) --------------------------------------------------------------

REQUESTS = """
import json, sys
sys.path.insert(0, "../../packages/contracts")
from glow_discovery import contract
from glow_profiles.contract import Invalid
from runtime import valid

TARGET = "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f"
BATCH = "1d2e3f40-5a6b-4c7d-8e9f-0a1b2c3d4e5f"
MATCH = "2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901"
META = {"idempotency_key": "synthetic-key-1", "expected_version": 0}
VALID = {
    "InteractionIntent": {"operation": "interaction", "meta": META, "target_profile_id": TARGET,
                          "batch_id": BATCH, "batch_version": 1, "action": "like"},
    "InteractionUndoIntent": {"operation": "interaction_undo", "meta": META,
                              "target_profile_id": TARGET},
    "UnmatchIntent": {"operation": "unmatch", "meta": META, "match_id": MATCH},
    "BlockIntent": {"operation": "block", "meta": META, "target_profile_id": TARGET,
                    "action": "block"},
}
OTHER_OPERATION = {"InteractionIntent": "interaction_undo", "InteractionUndoIntent": "interaction",
                   "UnmatchIntent": "block", "BlockIntent": "unmatch"}
UUID_FIELD = {"InteractionIntent": "target_profile_id",
              "InteractionUndoIntent": "target_profile_id",
              "UnmatchIntent": "match_id", "BlockIntent": "target_profile_id"}


def bodies(name):
    base = json.dumps(VALID[name])

    def changed(change):
        value = json.loads(base)
        change(value)
        return json.dumps(value).encode()

    def meta(key, value):
        return lambda v: v["meta"].__setitem__(key, value)

    out = {
        "valid": base.encode(),
        "integral": base.replace('"expected_version": 0', '"expected_version": 0.0').encode(),
        "extra": changed(lambda v: v.__setitem__("extra", 1)),
        "actor_in_body": changed(lambda v: v.__setitem__("actor_id", TARGET)),
        "meta_extra": changed(meta("actor_id", TARGET)),
        "wrong_operation": changed(lambda v: v.__setitem__("operation", OTHER_OPERATION[name])),
        "missing_meta": changed(lambda v: v.pop("meta")),
        "missing_key": changed(lambda v: v["meta"].pop("idempotency_key")),
        "uppercase_uuid": changed(
            lambda v: v.__setitem__(UUID_FIELD[name], v[UUID_FIELD[name]].upper())),
        "negative_expected_version": changed(meta("expected_version", -1)),
        "over_max_expected_version": changed(meta("expected_version", 2 ** 53)),
        "text_expected_version": changed(meta("expected_version", "0")),
        "long_key": changed(meta("idempotency_key", "k" * 101)),
        "key_newline": changed(meta("idempotency_key", "synthetic-key\\n")),
        "not_json": b'{"operation": ',
        "nan": base.replace('"expected_version": 0', '"expected_version": NaN').encode(),
        "array": b"[]",
        "bytes": b"\\xff",
    }
    if name == "InteractionIntent":
        out["action_match"] = changed(lambda v: v.__setitem__("action", "match"))
        out["action_undo"] = changed(lambda v: v.__setitem__("action", "undo"))
        out["batch_version_zero"] = changed(lambda v: v.__setitem__("batch_version", 0))
        out["uppercase_batch"] = changed(lambda v: v.__setitem__("batch_id", BATCH.upper()))
    if name == "InteractionUndoIntent":
        out["with_batch"] = changed(lambda v: v.__setitem__("batch_id", BATCH))
        out["with_action"] = changed(lambda v: v.__setitem__("action", "pass"))
    if name == "BlockIntent":
        out["action_report"] = changed(lambda v: v.__setitem__("action", "report"))
    return out


found = {}
for name in VALID:
    for case, body in bodies(name).items():
        try:
            value = contract.parse(name, body)
            accepted, schema_parsed = True, valid("production", name, value)
            same = value == json.loads(body)
        except Invalid:
            accepted, schema_parsed, same = False, None, None
        try:
            decoded = json.loads(body)
        except (UnicodeDecodeError, ValueError):
            schema = None
        else:
            schema = valid("production", name, decoded)
        found[f"{name}/{case}"] = {"accepted": accepted, "schema": schema,
                                   "schema_parsed": schema_parsed, "same": same}
    found[f"{name}/app_intent"] = valid("production", "AppIntent", VALID[name])
found["requests"] = sorted(contract.REQUESTS)
print(json.dumps(found))
"""


class RequestTests(unittest.TestCase):
    """D13: Stage B's four intents, closed, parsed as ``PageRequest`` is, agreeing with the
    production schema on every body."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = last_json(under_discovery_settings(REQUESTS))

    def test_each_intent_accepts_its_valid_body_and_the_schema_agrees(self) -> None:
        self.assertEqual(
            self.seen["requests"],
            sorted(["PageRequest", *INTENTS]),
        )
        for name in INTENTS:
            for case in ("valid", "integral"):
                with self.subTest(intent=name, body=case):
                    answer = self.seen[f"{name}/{case}"]
                    self.assertTrue(answer["accepted"])
                    self.assertTrue(answer["schema"])
                    # The parsed DTO is the production schema's, unchanged from the body.
                    self.assertTrue(answer["schema_parsed"])
                    self.assertTrue(answer["same"])
            with self.subTest(intent=name, body="app_intent"):
                self.assertTrue(self.seen[f"{name}/app_intent"])

    def test_each_refused_body_is_invalid_in_the_production_schema_too(self) -> None:
        refused = [
            key
            for key, answer in self.seen.items()
            if isinstance(answer, dict) and key.split("/")[1] not in ("valid", "integral")
        ]
        for name in INTENTS:
            for case in (
                "extra",
                "actor_in_body",
                "meta_extra",
                "wrong_operation",
                "missing_meta",
                "missing_key",
                "uppercase_uuid",
                "negative_expected_version",
                "over_max_expected_version",
                "text_expected_version",
                "long_key",
                "key_newline",
                "not_json",
                "nan",
                "array",
                "bytes",
            ):
                self.assertIn(f"{name}/{case}", refused)
        for case in ("action_match", "action_undo", "batch_version_zero", "uppercase_batch"):
            self.assertIn(f"InteractionIntent/{case}", refused)
        for case in ("with_batch", "with_action"):
            self.assertIn(f"InteractionUndoIntent/{case}", refused)
        self.assertIn("BlockIntent/action_report", refused)
        for key in refused:
            with self.subTest(body=key):
                answer = self.seen[key]
                self.assertFalse(answer["accepted"])
                # A body JSON can decode is invalid in the schema as well (never accepted by one
                # and refused by the other); one it cannot decode has nothing to validate.
                if key.split("/")[1] in ("not_json", "bytes"):
                    self.assertIsNone(answer["schema"])
                else:
                    self.assertIs(answer["schema"], False)


# -- projections and receipts (D13) -------------------------------------------------------------

PROJECTIONS = """
import json, sys
sys.path.insert(0, "../../packages/contracts")
from glow_discovery import contract
from glow_profiles.contract import app_response
from runtime import valid

TARGET = "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f"
MATCH = "2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901"
REF = "3c4d5e6f-7081-4293-a4b5-c6d7e8f90a1b"
REQUEST = "4d5e6f70-8192-43a4-b5c6-d7e8f90a1b2c"


def both(definition, value):
    return [valid("production", definition, value),
            valid("production", "AppResponse", app_response(value, REQUEST))]


liked_match = contract.interaction_outcome(TARGET, 2, "liked", MATCH)
liked = contract.interaction_outcome(TARGET, 1, "liked", None)
passed = contract.interaction_outcome(TARGET, 1, "passed", MATCH)
undone = contract.undo_outcome(TARGET, 3)
matches = {s: contract.match_projection(MATCH, 2, TARGET, s)
           for s in ("active", "unmatched", "restricted")}
blocks = {s: contract.block_outcome(TARGET, 1, s) for s in ("active", "removed")}
found = {
    "liked_match": both("InteractionOutcome", liked_match),
    "liked": both("InteractionOutcome", liked),
    "passed": both("InteractionOutcome", passed),
    "passed_match_id": passed["match_id"],
    "liked_match_id": liked_match["match_id"],
    "raw_passed_with_match": valid("production", "InteractionOutcome",
                                   {**passed, "match_id": MATCH}),
    "undo": both("InteractionUndoOutcome", undone),
    "undo_as_interaction": valid("production", "InteractionOutcome", undone),
    "matches": {s: both("MatchProjection", p) for s, p in matches.items()},
    "blocks": {s: both("BlockOutcome", p) for s, p in blocks.items()},
    "keys": {
        "interaction": sorted(liked), "undo": sorted(undone),
        "match": sorted(matches["active"]), "block": sorted(blocks["active"]),
    },
}
projections = {"none": None, "liked": liked_match, "passed": passed, "undo": undone,
               "match": matches["active"], "block": blocks["active"]}
results = {}
receipts = {}
for code in ("liked", "passed", "unmatched", "blocked", "unblocked", "withdrawn"):
    receipt = contract.receipt(code, REF, 4)
    snapshot = json.dumps(receipt, sort_keys=True)
    receipts[code] = {
        "CommandReceipt": valid("production", "CommandReceipt", receipt),
        "InteractionUndoReceipt": valid("production", "InteractionUndoReceipt", receipt),
        "keys": sorted(receipt),
    }
    dto = "InteractionUndoCommandResult" if code == "withdrawn" else "InteractionCommandResult"
    for name, projection in projections.items():
        for replayed in (False, True):
            result = contract.command_result(receipt, replayed, projection)
            current = result["current_projection"]
            results[f"{code}/{name}/{replayed}"] = {
                "dto": dto,
                "kind": result["kind"],
                "valid": valid("production", dto, result),
                "kept": None if current is None else current["kind"],
                "identical": current is None or current == projection,
                "receipt": json.dumps(result["receipt"], sort_keys=True) == snapshot,
                "receipt_untouched": json.dumps(receipt, sort_keys=True) == snapshot,
                "replayed": result["replayed"],
                "served": valid("production", "AppResponse", app_response(result, REQUEST)),
                "keys": sorted(result),
            }
found["results"] = results
found["receipts"] = receipts
# What the server's filter prevents: the schema refuses a projection its receipt does not allow.
found["raw_liked_with_match"] = valid("production", "InteractionCommandResult", {
    "kind": "interaction_command_result", "receipt": contract.receipt("liked", REF, 1),
    "replayed": False, "current_projection": matches["active"]})
found["raw_withdrawn_with_block"] = valid("production", "InteractionUndoCommandResult", {
    "kind": "interaction_undo_command_result", "receipt": contract.receipt("withdrawn", REF, 1),
    "replayed": False, "current_projection": blocks["active"]})
print(json.dumps(found))
"""

KEPT = {
    "liked": {"liked": "interaction", "passed": "interaction"},
    "passed": {"liked": "interaction", "passed": "interaction"},
    "unmatched": {"match": "match"},
    "blocked": {"block": "block"},
    "unblocked": {"block": "block"},
    "withdrawn": {"undo": "interaction_undo", "liked": "interaction", "passed": "interaction"},
}


class ProjectionTests(unittest.TestCase):
    """D13: the served projections and the internal command result."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = last_json(under_discovery_settings(PROJECTIONS))

    def test_each_projection_is_its_dto_and_served_in_app_response(self) -> None:
        seen = self.seen
        for name in ("liked_match", "liked", "passed", "undo"):
            with self.subTest(projection=name):
                self.assertEqual(seen[name], [True, True])
        for state, answer in seen["matches"].items():
            with self.subTest(match=state):
                self.assertEqual(answer, [True, True])
        for state, answer in seen["blocks"].items():
            with self.subTest(block=state):
                self.assertEqual(answer, [True, True])
        # A pass never carries a match (the schema holds it to null; the projection forces it).
        self.assertIsNone(seen["passed_match_id"])
        self.assertFalse(seen["raw_passed_with_match"])
        self.assertEqual(seen["liked_match_id"], "2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901")
        self.assertFalse(seen["undo_as_interaction"])
        self.assertEqual(
            seen["keys"],
            {
                "interaction": ["kind", "match_id", "state", "target_profile_id", "version"],
                "undo": ["kind", "state", "target_profile_id", "version"],
                "match": ["kind", "match_id", "other_profile_id", "state", "version"],
                "block": ["kind", "state", "target_profile_id", "version"],
            },
        )

    def test_each_receipt_is_its_dto(self) -> None:
        for code, answer in self.seen["receipts"].items():
            with self.subTest(code=code):
                undo = code == "withdrawn"
                self.assertEqual(answer["CommandReceipt"], not undo)
                self.assertEqual(answer["InteractionUndoReceipt"], undo)
                self.assertEqual(
                    answer["keys"], ["committed_version", "object_ref", "outcome_code"]
                )

    def test_the_command_result_keeps_only_an_allowed_projection_and_its_receipt(self) -> None:
        results = self.seen["results"]
        self.assertEqual(len(results), 6 * 6 * 2)
        for key, answer in results.items():
            code, name, replayed = key.split("/")
            with self.subTest(result=key):
                self.assertTrue(answer["valid"])
                self.assertEqual(
                    answer["kind"],
                    "interaction_undo_command_result"
                    if code == "withdrawn"
                    else "interaction_command_result",
                )
                # Kept unchanged where the DTO's rule allows it; null otherwise (a MatchProjection
                # given for a liked receipt becomes null).
                self.assertEqual(answer["kept"], KEPT[code].get(name))
                self.assertTrue(answer["identical"])
                # The receipt is the original, whatever the projection, and is not mutated.
                self.assertTrue(answer["receipt"])
                self.assertTrue(answer["receipt_untouched"])
                self.assertEqual(answer["replayed"], replayed == "True")
                # Internal only: never a served response.
                self.assertFalse(answer["served"])
                self.assertEqual(
                    answer["keys"], ["current_projection", "kind", "receipt", "replayed"]
                )
        self.assertFalse(self.seen["raw_liked_with_match"])
        self.assertFalse(self.seen["raw_withdrawn_with_block"])


# -- policy (D12) -------------------------------------------------------------------------------

POLICY = """
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest import mock
from glow_discovery import policy
from glow_domain import profile_settings as ps

now = datetime(2026, 11, 15, 12, 0, 0, tzinfo=UTC)


def attempt(function, *args):
    try:
        value = function(*args)
    except Exception as exc:
        return "error:" + type(exc).__name__
    if value is None:
        return None
    if isinstance(value, timedelta):
        return value.total_seconds()
    return value.isoformat()


def settings(resurfacing):
    found = {}
    for number, name in enumerate(policy.SELECTION_SETTINGS, start=1):
        content = resurfacing if name == ps.RESURFACING else ps.LAUNCH_DEFAULTS[name]
        found[name] = SimpleNamespace(
            name=name, number=number, policy_version=f"{name}.v{number}", content=content)
    return found


on = {"enabled": True, "waiting_days": 7}
off = ps.LAUNCH_DEFAULTS[ps.RESURFACING]
found = {
    "resurfacing_off_default": attempt(policy.resurfaced_before, off, now),
    "resurfacing_off_with_days": attempt(
        policy.resurfaced_before, {"enabled": False, "waiting_days": 7}, now),
    "resurfacing_on": attempt(policy.resurfaced_before, on, now),
    "resurfacing_on_no_clock": attempt(policy.resurfaced_before, on, None),
    "resurfacing_truthy": attempt(policy.resurfaced_before, {"enabled": 1, "waiting_days": 7}, now),
    "undo_off_default": attempt(policy.undo_window, ps.LAUNCH_DEFAULTS[ps.UNDO]),
    "undo_off_with_days": attempt(policy.undo_window, {"enabled": False, "waiting_days": 3}),
    "undo_on": attempt(policy.undo_window, {"enabled": True, "waiting_days": 3}),
    "undo_truthy": attempt(policy.undo_window, {"enabled": "true", "waiting_days": 3}),
    "selection_on": attempt(lambda: policy.selection(settings(on), now.date(), now)
                            .resurfaced_before),
    "selection_on_no_clock": attempt(lambda: policy.selection(settings(on), now.date())
                                     .resurfaced_before),
    "selection_off": attempt(lambda: policy.selection(settings(off), now.date(), now)
                             .resurfaced_before),
    "now": now.isoformat(),
    "undo_settings": list(policy.UNDO_SETTINGS),
    "undo_name": ps.UNDO,
    "undo_in_selection": ps.UNDO in policy.SELECTION_SETTINGS,
}
calls = []
with mock.patch.object(policy, "resurfaced_before",
                       lambda content, clock: calls.append([content, attempt(lambda: clock)])):
    policy.selection(settings(on), now.date(), now)
found["passed_to_resurfaced_before"] = calls
print(json.dumps(found))
"""


class PolicyTests(unittest.TestCase):
    """D12: resurfacing and undo follow their settings, off at launch (every pass excludes; no
    pass can be withdrawn)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = last_json(under_discovery_settings(POLICY))

    def test_resurfacing_has_a_cutoff_only_while_on_with_a_clock(self) -> None:
        seen = self.seen
        self.assertIsNone(seen["resurfacing_off_default"])
        self.assertIsNone(seen["resurfacing_off_with_days"])
        self.assertEqual(seen["resurfacing_on"], "2026-11-08T12:00:00+00:00")
        self.assertIsNone(seen["resurfacing_on_no_clock"])
        # Only ``true`` switches it on.
        self.assertIsNone(seen["resurfacing_truthy"])

    def test_undo_has_a_window_only_while_on(self) -> None:
        seen = self.seen
        self.assertIsNone(seen["undo_off_default"])
        self.assertIsNone(seen["undo_off_with_days"])
        self.assertEqual(seen["undo_on"], 3 * 86400.0)
        self.assertIsNone(seen["undo_truthy"])

    def test_the_selection_passes_its_clock_to_resurfacing(self) -> None:
        seen = self.seen
        self.assertEqual(seen["selection_on"], "2026-11-08T12:00:00+00:00")
        self.assertIsNone(seen["selection_on_no_clock"])
        self.assertIsNone(seen["selection_off"])
        self.assertEqual(
            seen["passed_to_resurfaced_before"],
            [[{"enabled": True, "waiting_days": 7}, seen["now"]]],
        )

    def test_undo_reads_discovery_undo_alone(self) -> None:
        self.assertEqual(self.seen["undo_settings"], [ps.UNDO])
        self.assertEqual(self.seen["undo_name"], "discovery.undo")
        self.assertFalse(self.seen["undo_in_selection"])


# -- predicates (D7, D12; Stage B's item 3) ------------------------------------------------------

PREDICATES = """
import json
from glow_discovery import predicates

clause = predicates.unconsumed()
outer = predicates.VIEWER.replace(predicates.MEMBER, "")
start, end = outer.index("SELECT "), outer.index("\\nFROM v")
print(json.dumps({
    "clause": clause,
    "counts": {name: getattr(predicates, name).count(clause)
               for name in ("UNCONSUMED", "SELECTION", "RECHECK", "PAIR", "VIEWER")},
    "viewer_member": predicates.VIEWER.count(predicates.MEMBER),
    "viewer_outer": outer,
    "viewer_columns": [c.strip() for c in outer[start + len("SELECT "):end].split(",")],
    "chart_columns": [c.strip() for c in predicates.CHART_COLUMNS.format(name="chart").split(",")],
    "member_states": predicates.member_states("v"),
}))
"""

DIRECTIONAL = (
    "(i.state = 'liked' OR (i.state = 'passed'"
    " AND (%(resurfaced_before)s::timestamptz IS NULL"
    " OR i.decided_at > %(resurfaced_before)s::timestamptz)))"
)


class PredicateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = last_json(under_discovery_settings(PREDICATES))

    def test_consumption_is_liked_always_passed_unless_resurfaced_never_withdrawn(self) -> None:
        clause = self.seen["clause"]
        # 'liked' excludes always; 'passed' unless resurfaced (decided at or before the cutoff,
        # with the cutoff set); a 'withdrawn' row, or any other state, excludes nothing.
        self.assertIn(DIRECTIONAL, clause)
        self.assertNotIn("withdrawn", clause)
        self.assertIn("m.state IN ('active', 'restricted', 'unmatched')", clause)
        self.assertEqual(
            set(re.findall(r"'([a-z_]+)'", clause)),
            {"liked", "passed", "active", "restricted", "unmatched"},
        )

    def test_one_consumption_text_for_the_selection_every_recheck_and_the_like(self) -> None:
        # The same clause, once each, in the like's own check, the selection and every recheck;
        # the trusted adapter's pair read and the viewer's read do not apply it (D7).
        self.assertEqual(
            self.seen["counts"],
            {"UNCONSUMED": 1, "SELECTION": 1, "RECHECK": 1, "PAIR": 0, "VIEWER": 0},
        )

    def test_the_viewer_selects_no_distance_choice_and_pages_reads_its_columns(self) -> None:
        seen = self.seen
        self.assertEqual(seen["viewer_member"], 1)
        self.assertNotIn("distance_choice", seen["viewer_outer"])
        columns = seen["viewer_columns"]
        self.assertEqual(
            columns,
            [
                seen["member_states"],
                "v.eligibility_version",
                "v.preferences_version",
                "v.blocks_version",
                *seen["chart_columns"],
            ],
        )
        self.assertEqual(len(columns), 8)
        # ``pages._viewer`` reads the versions from 1 to 3 and the chart from 4 to 8.
        viewer = top_function(parsed(DISCOVERY / "pages.py"), "_viewer")
        returned = [n for n in viewer.body if isinstance(n, ast.Return)][-1]
        assert returned.value is not None
        self.assertEqual(
            ast.unparse(returned.value),
            "Viewer(row[0] is True, (int(row[1]), int(row[2]), int(row[3])), tuple(row[4:8]))",
        )
        self.assertEqual(columns[4:8], seen["chart_columns"])


# -- rematch (D12) ------------------------------------------------------------------------------


class RematchTests(unittest.TestCase):
    """D12 (DM-60): rematch is not built, so ``discovery.rematch`` refuses ``enabled`` on
    (``rematch_not_built``); resurfacing and undo, which are built, may be switched on."""

    def rematch(self, **change: object) -> tuple[str, ...]:
        content = {**ps.LAUNCH_DEFAULTS[ps.REMATCH], **change}
        return ps.publication_refusals(ps.REMATCH, content, ps.LAUNCH_DEFAULTS[ps.REMATCH])

    def test_rematch_enabled_is_refused_naming_rematch_not_built(self) -> None:
        self.assertEqual(ps.REMATCH, "discovery.rematch")
        self.assertEqual(ps.REMATCH_NOT_BUILT, "rematch_not_built")
        self.assertIn(ps.REMATCH_NOT_BUILT, ps.FIXED_LIMITS)
        for days in (1, 30, ps.WAITING_DAYS_MAX):
            with self.subTest(waiting_days=days):
                self.assertEqual(
                    self.rematch(enabled=True, waiting_days=days), (ps.REMATCH_NOT_BUILT,)
                )
        # With no current version (the launch default's publication) as well.
        content = {**ps.LAUNCH_DEFAULTS[ps.REMATCH], "enabled": True, "waiting_days": 30}
        self.assertEqual(ps.publication_refusals(ps.REMATCH, content), (ps.REMATCH_NOT_BUILT,))

    def test_rematch_after_a_block_or_report_names_both_limits(self) -> None:
        both = {ps.REMATCH_NEVER_AFTER_BLOCK_OR_REPORT, ps.REMATCH_NOT_BUILT}
        for change in (
            {"after_block": True},
            {"after_report": True},
            {"after_block": True, "after_report": True},
        ):
            with self.subTest(change=change):
                found = self.rematch(enabled=True, waiting_days=30, **change)
                self.assertEqual(set(found), both)
                self.assertEqual(len(found), 2)

    def test_rematch_off_is_accepted(self) -> None:
        self.assertEqual(self.rematch(), ())
        self.assertEqual(self.rematch(enabled=False, waiting_days=30), ())
        self.assertEqual(
            self.rematch(enabled=False, waiting_days=None, after_block=False, after_report=False),
            (),
        )

    def test_resurfacing_and_undo_may_be_switched_on(self) -> None:
        for name in (ps.RESURFACING, ps.UNDO):
            with self.subTest(setting=name):
                content = {"enabled": True, "waiting_days": 7}
                self.assertEqual(
                    ps.publication_refusals(name, content, ps.LAUNCH_DEFAULTS[name]), ()
                )
                self.assertNotIn(ps.REMATCH_NOT_BUILT, ps.publication_refusals(name, content, None))


# -- structure (D2, D9 to D11, D17, D19) ---------------------------------------------------------

IDENTIFIER_READS = {
    "interact": "target_id = _account_of_profile(intent['target_profile_id'])",
    "undo": "target_id = _account_of_profile(intent['target_profile_id'])",
    "block": "target_id = _account_of_profile(intent['target_profile_id'])",
    "unmatch": (
        "pair = Match.objects.filter(pk=intent['match_id'])"
        ".values_list('account_low_id', 'account_high_id').first()"
    ),
}
LOCKS = {
    "interact": "_lock_pair(tx, account_id, target_id)",
    "undo": "_lock_pair(tx, account_id, target_id)",
    "block": "_lock_pair(tx, account_id, target_id)",
    "unmatch": "_lock_pair(tx, account_id, UUID(str(other_id)))",
}
SETTINGS_READS = {
    "interact": ["pages._selection"],
    "undo": ["settings_store.read_shared"],
    "unmatch": [],
    "block": [],
}


def python_sources(root: Path) -> list[Path]:
    """Every Python source under ``root``, without virtual environments and caches."""
    pruned = {".venv", "__pycache__", "node_modules", ".mypy_cache", ".ruff_cache"}
    found: list[Path] = []
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = sorted(d for d in subdirectories if d not in pruned)
        found.extend(Path(directory) / name for name in sorted(files) if name.endswith(".py"))
    return found


def lock_index(statements: list[ast.stmt]) -> int:
    for index, statement in enumerate(statements):
        if (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)
            and ast.unparse(statement.value.func) == "_lock_pair"
        ):
            return index
    raise AssertionError("no _lock_pair call")


def settings_reads(node: ast.AST) -> list[str]:
    return [
        name
        for name in called(node)
        if name.endswith("read_shared") or name.split(".")[-1] == "_selection"
    ]


class StructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = parsed(DISCOVERY / "interactions.py")

    def test_each_command_locks_both_accounts_before_any_other_row(self) -> None:
        # D2 (DM-60 section 11): the one read before the locks is an identifier that never
        # changes (the target's account, or the match's pair); then ``_lock_pair``; anything else
        # before it only judges that identifier and refuses.
        for command in COMMANDS:
            with self.subTest(command=command):
                function = top_function(self.tree, command)
                # Outside the transaction: the request's keyed digest only (no row).
                outside = [s for s in function.body if not isinstance(s, ast.FunctionDef)]
                for statement in outside[1:]:
                    self.assertLessEqual(
                        set(called(statement)), {"idempotency.digest", "run"}, command
                    )
                statements = inner_body(function).body
                at = lock_index(statements)
                self.assertEqual(ast.unparse(statements[0]), IDENTIFIER_READS[command])
                self.assertEqual(ast.unparse(statements[at]), LOCKS[command])
                for statement in statements[1:at]:
                    self.assertLessEqual(set(called(statement)), {"Refused"})
                    self.assertNotIn("objects", ast.unparse(statement))
                    self.assertNotIn("_account_of_profile", ast.unparse(statement))
        # The identifier read selects the account's ID only.
        helper = top_function(self.tree, "_account_of_profile")
        self.assertIn(
            "Profile.objects.filter(pk=profile_id).values_list('account_id', flat=True).first()",
            ast.unparse(helper),
        )
        # ``_lock_pair`` takes the accounts in canonical order through SV2's ``lock_account``.
        lock = top_function(self.tree, "_lock_pair")
        loop = next(n for n in lock.body if isinstance(n, ast.For))
        self.assertEqual(ast.unparse(loop.iter), "sorted(accounts)")
        self.assertIn("lock_account", called(loop))
        # The match read holds the actor's account FOR SHARE first.
        read = inner_body(top_function(self.tree, "read_match")).body
        self.assertEqual(ast.unparse(read[0]), "read_account_shared(tx, account_id)")

    def test_each_command_reads_its_settings_in_one_call_right_after_the_locks(self) -> None:
        # D19: at most one ``read_shared`` per transaction, its first, right after the locks;
        # the like's is ``pages._selection`` (the selection's settings); undo's is
        # ``discovery.undo``'s.
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef):
                with self.subTest(function=node.name):
                    self.assertEqual(settings_reads(node), SETTINGS_READS.get(node.name, []))
        for command in ("interact", "undo"):
            with self.subTest(command=command):
                statements = inner_body(top_function(self.tree, command)).body
                at = lock_index(statements)
                self.assertEqual(settings_reads(statements[at + 1]), SETTINGS_READS[command])
        undo_read = next(
            n
            for n in ast.walk(top_function(self.tree, "undo"))
            if isinstance(n, ast.Call) and ast.unparse(n.func) == "settings_store.read_shared"
        )
        self.assertEqual(ast.unparse(undo_read.args[1]), "policy.UNDO_SETTINGS")
        # ``pages._selection`` makes its one call first, of the selection's settings.
        selection = top_function(parsed(DISCOVERY / "pages.py"), "_selection")
        self.assertEqual(settings_reads(selection), ["settings_store.read_shared"])
        first = selection.body[0]
        self.assertEqual(
            ast.unparse(first),
            "found = settings_store.read_shared(tx, policy.SELECTION_SETTINGS)",
        )
        # No other module of the slice reads a setting.
        for path in sorted(DISCOVERY.glob("*.py")):
            if path.name in ("pages.py", "interactions.py"):
                continue
            with self.subTest(module=path.name):
                self.assertEqual(settings_reads(parsed(path)), [])

    def test_no_code_string_takes_a_lock_or_names_the_pointer_table(self) -> None:
        for name in ("interactions.py", "interaction_views.py", "interaction_urls.py"):
            tree = parsed(DISCOVERY / name)
            strings = [text.lower() for text in code_strings(tree)]
            for word in ("for update", "for share", "for no key", "policyrevision"):
                with self.subTest(module=name, word=word):
                    self.assertFalse(any(word in text for text in strings))
            with self.subTest(module=name, word="select_for_update"):
                self.assertNotIn("select_for_update", called(tree))
                self.assertNotIn(
                    "PolicyRevision",
                    {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
                    | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)},
                )

    def test_the_action_routes_log_only_a_reason_code(self) -> None:
        tree = parsed(DISCOVERY / "interaction_views.py")
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
        ]
        self.assertEqual(len(calls), 2)
        for node in calls:
            with self.subTest(line=node.lineno):
                self.assertIsInstance(node.args[0], ast.Constant)
                self.assertEqual(node.keywords, [])
                self.assertEqual(len(node.args), 2)
                self.assertIn(ast.unparse(node.args[1]), ("result.reason", "INVALID_REQUEST"))

    def test_glow_chat_imports_nothing_from_glow_discovery(self) -> None:
        for path in sorted(CHAT.glob("*.py")):
            tree = parsed(path)
            with self.subTest(module=path.name):
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertFalse(alias.name.startswith("glow_discovery"))
                    if isinstance(node, ast.ImportFrom):
                        self.assertFalse((node.module or "").startswith("glow_discovery"))
                # No dynamic import by name either.
                self.assertFalse(any("glow_discovery" in text for text in code_strings(tree)))

    def test_activate_reciprocal_is_called_only_from_the_like_after_its_recheck(self) -> None:
        sources = python_sources(API_ROOT)
        callers = []
        texts = []
        for path in sources:
            text = path.read_text(encoding="utf-8")
            relative = path.relative_to(API_ROOT).as_posix()
            if path != Path(__file__).resolve() and ".activate_reciprocal(" in text:
                texts.append(relative)
            for node in ast.walk(ast.parse(text)):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "activate_reciprocal"
                ):
                    callers.append(relative)
        self.assertEqual(texts, ["glow_discovery/interactions.py"])
        self.assertEqual(callers, ["glow_discovery/interactions.py"])
        statements = inner_body(top_function(self.tree, "interact")).body

        def index(word: str) -> int:
            found = [i for i, s in enumerate(statements) if word in ast.unparse(s)]
            self.assertEqual(len(found), 1, word)
            return found[0]

        # Inside the like's transaction, after the locks and the pair's recheck (D10 (a)).
        self.assertLess(lock_index(statements), index("_eligible(tx, selection, pair)"))
        self.assertLess(index("_eligible(tx, selection, pair)"), index(".activate_reciprocal("))


# -- log capture (check 13; D17) -----------------------------------------------------------------

REASON = r"^[a-z_]+(:[a-z_]+)?$"


class LogCaptureTests(unittest.TestCase):
    """Check 13 (D8, D17): no log line carries a value. Every logger call in ``glow_discovery``,
    Stage B's modules included, logs a constant format with only a reason code; every reason the
    commands refuse with is a code; and the routes' lines, captured, hold no body value."""

    def test_every_logger_call_logs_a_constant_and_reason_codes_only(self) -> None:
        names = {path.name for path in DISCOVERY.glob("*.py")}
        self.assertLessEqual(
            {"interactions.py", "interaction_views.py", "interaction_urls.py"}, names
        )
        for path in sorted(DISCOVERY.glob("*.py")):
            tree = parsed(path)
            calls = called(tree)
            with self.subTest(module=path.name):
                self.assertNotIn("print", calls)
                # The standard library's logging only names the module's own logger.
                for name in calls:
                    if name.startswith("logging."):
                        self.assertEqual(name, "logging.getLogger")
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and ast.unparse(node.func) == "logging.getLogger":
                        self.assertEqual(
                            [ast.unparse(a) for a in node.args],
                            [repr(f"glow_discovery.{path.stem}")],
                        )
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "logger"
                ):
                    with self.subTest(module=path.name, line=node.lineno):
                        self.assertIsInstance(node.args[0], ast.Constant)
                        self.assertEqual(node.keywords, [])
                        for argument in node.args[1:]:
                            self.assertIn(
                                ast.unparse(argument), ("result.reason", "INVALID_REQUEST")
                            )

    def test_every_refusal_reason_in_the_commands_is_a_code(self) -> None:
        # What ``result.reason`` can carry from Stage B's commands: a constant code, or a code
        # joined with ``glow_chat``'s own result codes, never a value.
        tree = parsed(DISCOVERY / "interactions.py")
        allowed = {"STALE", "result.reason", "result.outcome", "activated.reason"}
        refusals = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "Refused"
        ]
        self.assertGreaterEqual(len(refusals), 15)
        for node in refusals:
            with self.subTest(line=node.lineno):
                self.assertEqual(len(node.args), 2)
                self.assertIn(
                    ast.unparse(node.args[0]),
                    ("FORBIDDEN", "NOT_FOUND", "STALE_VERSION", "STATE_CONFLICT", "code"),
                )
                reason = node.args[1]
                if isinstance(reason, ast.Constant):
                    self.assertRegex(reason.value, REASON)
                else:
                    self.assertIsInstance(reason, ast.JoinedStr)
                    assert isinstance(reason, ast.JoinedStr)
                    for part in reason.values:
                        if isinstance(part, ast.FormattedValue):
                            self.assertIn(ast.unparse(part.value), allowed)
                        else:
                            assert isinstance(part, ast.Constant)
                            self.assertRegex(str(part.value), r"^[a-z_:]*$")

    def test_the_routes_log_lines_hold_no_body_value(self) -> None:
        seen = last_json(under_discovery_settings(ROUTE_LOGS))
        self.assertEqual(set(seen["cases"]), set(ROUTE_STATUS))
        for case, answer in seen["cases"].items():
            with self.subTest(case=case):
                self.assertEqual(answer["status"], ROUTE_STATUS[case])
                self.assertEqual(answer["cache"], "no-store")
                self.assertFalse(answer["echo"])
                if answer["status"] == 200:
                    self.assertTrue(answer["valid"])
                else:
                    self.assertEqual(
                        set(answer["body"]), {"contract_version", "request_id", "code", "retryable"}
                    )
                    self.assertEqual(answer["body"]["code"], ROUTE_CODE[case])
        # Every line is the route's, holding a reason code and nothing else: four invalid
        # requests (the 405 logs nothing) and the three refusals, each by its internal code.
        self.assertEqual(
            {name for name, _ in seen["records"]}, {"glow_discovery.interaction_views"}
        )
        lines = [line for _, line in seen["records"]]
        for line in lines:
            with self.subTest(line=line):
                self.assertRegex(line, r"^interaction route refused: [a-z_]+(:[a-z_]+)?$")
        self.assertEqual(
            sorted(lines),
            sorted(
                ["interaction route refused: invalid_request"] * 3
                + [
                    "interaction route refused: stale:batch",
                    "interaction route refused: undo_off",
                    "interaction route refused: match_not_found",
                ]
            ),
        )
        self.assertFalse(seen["record_echo"])


ROUTE_STATUS = {
    "extra_field": 400,
    "query_string": 400,
    "content_type": 400,
    "method": 405,
    "stale": 409,
    "applied": 200,
    "undo_off": 403,
    "match_not_found": 404,
}
ROUTE_CODE = {
    "extra_field": "invalid_request",
    "query_string": "invalid_request",
    "content_type": "invalid_request",
    "method": "invalid_request",
    "stale": "stale_version",
    "undo_off": "forbidden",
    "match_not_found": "not_found",
}

ROUTE_LOGS = """
import json, logging, sys
from unittest import mock
from uuid import UUID, uuid4
sys.path.insert(0, "../../packages/contracts")
from rest_framework.test import APIRequestFactory, force_authenticate
from glow_discovery import contract, interaction_views as views
from glow_identity.authentication import Actor
from glow_profiles.tx import Result
from runtime import valid

records = []


class Capture(logging.Handler):
    def emit(self, record):
        records.append([record.name, record.getMessage()])


root = logging.getLogger()
root.addHandler(Capture(level=logging.DEBUG))
root.setLevel(logging.DEBUG)
logging.getLogger("glow_discovery").setLevel(logging.DEBUG)

TARGET = "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f"
BATCH = "1d2e3f40-5a6b-4c7d-8e9f-0a1b2c3d4e5f"
MATCH = "2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901"
KEY = "synthetic-key-zq7"
actor = Actor(uuid4(), 1, "active", uuid4(), "valid")
VALUES = (TARGET, BATCH, MATCH, KEY, str(actor.account_id), str(actor.session_id))


class Signed:
    is_authenticated = True


factory = APIRequestFactory()
like = {"operation": "interaction", "meta": {"idempotency_key": KEY, "expected_version": 0},
        "target_profile_id": TARGET, "batch_id": BATCH, "batch_version": 1, "action": "like"}
undo = {"operation": "interaction_undo", "meta": {"idempotency_key": KEY, "expected_version": 1},
        "target_profile_id": TARGET}


def send(view, body, *, path="/x", content_type="application/json", method="post", **kwargs):
    if method == "post":
        request = factory.post(path, data=body, content_type=content_type)
    else:
        request = factory.get(path)
    force_authenticate(request, user=Signed(), token=actor)
    response = view.as_view()(request, **kwargs)
    response.render()
    return response


def answer(response, served=False):
    text = response.content.decode("utf-8")
    body = json.loads(text)
    return {
        "status": response.status_code,
        "cache": response["Cache-Control"],
        "body": body,
        "valid": valid("production", "AppResponse", body),
        # The served projection is the actor's own, which names its target; nothing else may.
        "echo": any(value in text for value in VALUES if not (served and value == TARGET)),
    }


def fixed(result):
    return staticmethod(lambda account_id, intent: result)


cases = {}
cases["extra_field"] = answer(send(views.InteractionView, json.dumps({**like, "x": KEY})))
cases["query_string"] = answer(
    send(views.InteractionView, json.dumps(like), path="/x?target=" + TARGET))
cases["content_type"] = answer(
    send(views.InteractionView, json.dumps(like), content_type="text/plain"))
cases["method"] = answer(send(views.InteractionView, None, method="get"))
with mock.patch.object(views.InteractionView, "command",
                       fixed(Result("refused", "stale_version", "stale:batch"))):
    cases["stale"] = answer(send(views.InteractionView, json.dumps(like)))
outcome = contract.interaction_outcome(TARGET, 1, "liked", None)
with mock.patch.object(views.InteractionView, "command", fixed(Result("applied", data=outcome))):
    cases["applied"] = answer(send(views.InteractionView, json.dumps(like)), served=True)
with mock.patch.object(views.UndoView, "command",
                       fixed(Result("refused", "forbidden", "undo_off"))):
    cases["undo_off"] = answer(send(views.UndoView, json.dumps(undo)))
with mock.patch.object(views.interactions, "read_match",
                       lambda account_id, match_id: Result("refused", "not_found",
                                                           "match_not_found")):
    cases["match_not_found"] = answer(
        send(views.MatchView, None, method="get", match_id=UUID(MATCH)))
print(json.dumps({
    "cases": cases,
    "records": records,
    "record_echo": any(value in line for _, line in records for value in VALUES),
}))
"""


# -- D10's writer, by AST (the review plan) -----------------------------------------------------

INSERTED = (
    "for actor_id, target_id in ((low_id, high_id), (high_id, low_id)):\n"
    "    if not DirectionalInteraction.objects.filter(actor_id=actor_id, target_id=target_id,"
    " state='liked').exists():\n"
    "        raise _Refused('not_reciprocal')"
)


def definitions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    """The module's functions and its classes' methods, by name (``Class.method``)."""
    found: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        assert not isinstance(node, ast.AsyncFunctionDef)
        if isinstance(node, ast.FunctionDef):
            found[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                assert not isinstance(item, ast.AsyncFunctionDef)
                if isinstance(item, ast.FunctionDef):
                    found[f"{node.name}.{item.name}"] = item
    return found


def every_definition(tree: ast.Module) -> set[str]:
    """Every function, method and nested function, by its qualified path."""
    found: set[str] = set()

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                name = f"{prefix}{child.name}"
                if not isinstance(child, ast.ClassDef):
                    found.add(name)
                visit(child, name + ".")
            else:
                visit(child, prefix)

    visit(tree, "")
    return found


def without_reciprocal(tree: ast.Module) -> str:
    """The module's dump with ``activate_reciprocal`` taken out of its class."""
    copied = copy.deepcopy(tree)
    for node in copied.body:
        if isinstance(node, ast.ClassDef):
            node.body = [
                item
                for item in node.body
                if not (isinstance(item, ast.FunctionDef) and item.name == "activate_reciprocal")
            ]
    return ast.dump(copied)


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        env={
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "GIT_TERMINAL_PROMPT": "0",
        },
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def main_base() -> str | None:
    """Main as this branch's base: the newest merge base of ``HEAD`` with ``main`` or
    ``origin/main`` (a local ``main`` can be stale), or ``None`` where the checkout holds neither
    (CI's shallow clone)."""
    try:
        if git("rev-parse", "--is-inside-work-tree").returncode != 0:
            return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    bases = []
    for ref in ("main", "origin/main"):
        if git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").returncode != 0:
            continue
        found = git("merge-base", "HEAD", ref)
        if found.returncode == 0 and found.stdout.strip():
            bases.append(found.stdout.strip())
    for base in bases:
        if all(git("merge-base", "--is-ancestor", other, base).returncode == 0 for other in bases):
            return base
    return None


# D10 (a): the sha256 of ``ast.dump`` (Python 3.12, the pinned toolchain) of every function and
# method in ``glow_chat/contact.py`` at main's 947576d (PR46's merge, Stage B's base), and of the
# whole module there, so the comparison runs without main's history (CI's shallow clone).
MAIN_DEFINITION_DIGESTS = {
    "OrmContactPersistence.__init__": (
        "d29c433a6d01332500a406beb971ebe25fa91f4ea2d83179492136978135518a"
    ),
    "OrmContactPersistence._bump_eligibility": (
        "7586d0c65d5a7d597a3cda44ae45ddaa2893242418af962b083151f0991de609"
    ),
    "OrmContactPersistence._clock": (
        "f1f2aaf6f792d7f120b3ec9c74bdd1458c1e02ad6d8df7ddbd8d0e6c7a9c18bb"
    ),
    "OrmContactPersistence._contact_state_checks": (
        "6dc7cbcd43dce52b0f166473de71db1987f6ebdcad81606661fdf02380ac7217"
    ),
    "OrmContactPersistence._decide_consent": (
        "bd62733fba050aa94701fbf0f51d0ec4ace1225d20f41b2c8a0c92e2a3d36320"
    ),
    "OrmContactPersistence._end_session": (
        "883f399a205663384d8bfba6eb6ed8089cab1f6fc6cc4a031fc5b47fa9793914"
    ),
    "OrmContactPersistence._event": (
        "ae5168036bf5c6aa0eb59d94e2a4277ceb34fcbda4344139145da2a3634f091e"
    ),
    "OrmContactPersistence._lock": (
        "86121c4a53566e91b31bb39ee504a9e64d96b08e69955e4c2897814aebc3faf5"
    ),
    "OrmContactPersistence._lock_shared": (
        "17a861502b400f405183b4e2316e72a81d46ef008aae3ab4f425c2baf55cf890"
    ),
    "OrmContactPersistence._revoke_account": (
        "192ebc353a01fe42ba6956e435cd23f6f02d839d700bcfaeb2c6838f0d9b11a9"
    ),
    "OrmContactPersistence._run": (
        "a278f6f2121b36788756eb67d9f99fb903eac07a601535b8c6261ae5cb2e44ab"
    ),
    "OrmContactPersistence._set_profile": (
        "cd38d099181e7a5773537c31fff5d2539ea55757bc9a039ca7ab8ef89dd6c7e0"
    ),
    "OrmContactPersistence._signal": (
        "5ad513d912f859f98a0e7224b0cdc733dcce13072c55ec97ae453049c30102b2"
    ),
    "OrmContactPersistence.accept_consent": (
        "77507bc060da28d19cb98099e3ffbe0c96951cca0e852205191f22c1fc2c3021"
    ),
    "OrmContactPersistence.activate_match": (
        "0dd4f363fc5914cc6519bf2c6230c8568f2f37b74573ad8954b8bcad5c37603b"
    ),
    "OrmContactPersistence.block": (
        "210c71e44f87b165b12dbb2f18a7ecb7e4b8276cb42143ab59d77382909c34ff"
    ),
    "OrmContactPersistence.delete": (
        "98c132fe94ec641a8dba771c5fb44dab2b497041fab2ce78daf9552da93f7c68"
    ),
    "OrmContactPersistence.expire_session": (
        "5e4b2d153ff78191864f1884bea878878b0890d137240dcdf9a20ba9282db55c"
    ),
    "OrmContactPersistence.grant_token": (
        "3b7f63837ad8e4ad7f224a80e56297ed68a529f1d8198547df81ec3a74eca0f3"
    ),
    "OrmContactPersistence.open_session": (
        "6770e36ac83b146756fc23f42a9e9440df8ac4497af14d5e4a96ab6420f1702b"
    ),
    "OrmContactPersistence.pause_profile": (
        "202e173dd9d8cc32d38df776ca979a16ecfe080b73a75e12e90f314d1a447b1a"
    ),
    "OrmContactPersistence.restrict_profile": (
        "b5551af534444afab7a90d6188853cbcf59443ff78dd1c758d5b1c14faa914ce"
    ),
    "OrmContactPersistence.resume_profile": (
        "1b9db7346663faa27c15b8a0642d2482848030e79829ba93aad82929c1500a18"
    ),
    "OrmContactPersistence.send": (
        "b39e7884d0466d389d4593570cc439ba5d76d4c7e1951ddd95fe939ed15325cb"
    ),
    "OrmContactPersistence.sign_out": (
        "d9a7b38f987fbf7779b3dfa736ba293b4fdce24bc34782b58bb19d07df2c0cbe"
    ),
    "OrmContactPersistence.suspend": (
        "9ec8f066926a25cb1c37fd8d188e60b5988687b2c465817cd8d9ca7e4ebf9b77"
    ),
    "OrmContactPersistence.unblock": (
        "41ba9fa84bfaf22fda7d96256bd8ff9f14c030147ee82c0e111837c346844482"
    ),
    "OrmContactPersistence.unmatch": (
        "00d1286741645db16fb4b14508ab5d74fa998391de381792f3fa6d58410fd973"
    ),
    "OrmContactPersistence.withdraw_consent": (
        "9bcc30fcb80d3a804a399495c7206f4d41586c3859aafeaa1ad078f76fca22d7"
    ),
    "_Refused.__init__": ("bbfd56379b9f21651934d6d4dd59e32243602968d40c368bd66daa01b29c0c36"),
    "_Rollback.__init__": ("a5454323019cd11e3cad67e07bfa091c10c8de694f72a187331065dd31fb87eb"),
    "new_provider_ref": ("c9330b760a05ca5ea99499229004b5d8034f32a4c79a9f5ab9bab24c4c38145f"),
}
MAIN_MODULE_DIGEST = "b1d45a7f611487b7caa030b13bfcd26a8dba80882235c8f549482eb1318e97c7"


class ReciprocalWriterTests(unittest.TestCase):
    """D10 (a), as the review plan reads it: every existing function and method in
    ``glow_chat/contact.py`` unchanged from main's (by AST), ``activate_reciprocal`` the only new
    one, and its body ``activate_match``'s with the one check added under the account locks."""

    def setUp(self) -> None:
        self.head = parsed(CONTACT)
        methods = definitions(self.head)
        self.match = methods["OrmContactPersistence.activate_match"]
        self.reciprocal = methods["OrmContactPersistence.activate_reciprocal"]

    def test_every_writer_at_mains_base_is_unchanged_and_one_is_new(self) -> None:
        base = main_base()
        if base is None:
            self.skipTest(
                "neither main nor origin/main is in this checkout (CI's shallow clone); the "
                "comparison runs wherever main's history is present"
            )
        shown = git("show", f"{base}:{CONTACT_IN_REPO}")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        main = ast.parse(shown.stdout)
        before, after = definitions(main), definitions(self.head)
        self.assertGreater(len(before), 20)
        for name, node in before.items():
            with self.subTest(definition=name):
                self.assertIn(name, after)
                self.assertEqual(ast.dump(after[name]), ast.dump(node))
        self.assertLessEqual(
            set(after) - set(before), {"OrmContactPersistence.activate_reciprocal"}
        )
        new = every_definition(self.head) - every_definition(main)
        self.assertTrue(
            all(name.startswith("OrmContactPersistence.activate_reciprocal") for name in new), new
        )
        # The whole module, the new method aside, is main's: no import, constant or class
        # attribute changed either.
        self.assertEqual(without_reciprocal(self.head), without_reciprocal(main))

    def test_every_writer_is_mains_by_its_pinned_digest_and_one_is_new(self) -> None:
        # The same comparison as the test above, against digests pinned from main's 947576d, so it
        # runs in CI too.
        after = definitions(self.head)
        self.assertEqual(len(MAIN_DEFINITION_DIGESTS), 32)
        for name, digest in MAIN_DEFINITION_DIGESTS.items():
            with self.subTest(definition=name):
                self.assertIn(name, after)
                found = hashlib.sha256(ast.dump(after[name]).encode()).hexdigest()
                self.assertEqual(found, digest)
        self.assertEqual(
            set(after) - set(MAIN_DEFINITION_DIGESTS), {"OrmContactPersistence.activate_reciprocal"}
        )
        module = hashlib.sha256(without_reciprocal(self.head).encode()).hexdigest()
        self.assertEqual(module, MAIN_MODULE_DIGEST)

    def test_activate_reciprocal_is_activate_match_with_one_statement_inserted(self) -> None:
        match_body = inner_body(self.match).body
        reciprocal_body = inner_body(self.reciprocal).body
        before = [ast.dump(s) for s in match_body]
        after = [ast.dump(s) for s in reciprocal_body]
        operations = [
            (tag, i1, i2, j1, j2)
            for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
                a=before, b=after, autojunk=False
            ).get_opcodes()
            if tag != "equal"
        ]
        self.assertEqual(len(operations), 1, operations)
        tag, i1, i2, j1, j2 = operations[0]
        self.assertEqual((tag, i2 - i1, j2 - j1), ("insert", 0, 1))
        inserted = reciprocal_body[j1]
        self.assertIsInstance(inserted, ast.For)
        self.assertEqual(ast.unparse(inserted), INSERTED)
        # Under both account locks, after the existing pair's refusal, before the contact checks.
        self.assertIn("raise _Refused(chat.MATCH_EXISTS)", ast.unparse(match_body[i1 - 1]))
        self.assertEqual(ast.unparse(match_body[i1]), "self._contact_state_checks(low_id, high_id)")
        locks = [i for i, s in enumerate(match_body) if "self._lock(AppAccount" in ast.unparse(s)]
        self.assertEqual(len(locks), 2)
        self.assertLess(max(locks), i1)

    def test_the_method_around_the_body_is_activate_matchs_with_one_import(self) -> None:
        self.assertEqual(ast.dump(self.reciprocal.args), ast.dump(self.match.args))
        self.assertEqual(ast.dump(self.reciprocal.returns), ast.dump(self.match.returns))
        self.assertEqual(self.reciprocal.decorator_list, [])
        self.assertEqual(self.match.decorator_list, [])
        skip = docstring_ids(self.head)
        outer_match = [s for s in self.match.body if id(getattr(s, "value", None)) not in skip]
        outer = [s for s in self.reciprocal.body if id(getattr(s, "value", None)) not in skip]
        self.assertEqual(len(outer), len(outer_match) + 1)
        self.assertIsInstance(outer[0], ast.ImportFrom)
        for mine, theirs in zip(outer[1:], outer_match, strict=True):
            if isinstance(theirs, ast.FunctionDef):
                assert isinstance(mine, ast.FunctionDef)
                self.assertEqual(mine.name, theirs.name)
                self.assertEqual(ast.dump(mine.args), ast.dump(theirs.args))
                self.assertEqual(ast.dump(mine.returns), ast.dump(theirs.returns))
                # The nested body's decorators too (the exact-head review's #14; DM-75): a
                # decorator on ``body`` could bypass its checks.
                self.assertEqual(
                    [ast.dump(d) for d in mine.decorator_list],
                    [ast.dump(d) for d in theirs.decorator_list],
                )
            else:
                self.assertEqual(ast.dump(mine), ast.dump(theirs))
        imports = [
            ast.unparse(node)
            for node in ast.walk(self.reciprocal)
            if isinstance(node, ast.Import | ast.ImportFrom)
        ]
        self.assertEqual(imports, ["from glow_persistence.models import DirectionalInteraction"])
        # ``glow_chat`` does not import the directional model at module level.
        module_imports = [
            ast.unparse(node) for node in self.head.body if isinstance(node, ast.ImportFrom)
        ]
        self.assertFalse(any("DirectionalInteraction" in line for line in module_imports))


if __name__ == "__main__":
    unittest.main()
