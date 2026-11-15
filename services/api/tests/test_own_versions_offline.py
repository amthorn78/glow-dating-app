"""SV3 Stage B's correction B-C1 (its brief's section "Stage B, correction B-C1", item 1; D13's
"The actor's own versions"; DM-74): the parts of the own-versions read that need no database.

- **The answer** (D13): ``contract.own_versions`` is D13's ``OwnInteractionVersions`` for every
  state of the actor's own directional row and own block, served inside ``AppResponse``, each
  ``none`` with ``0`` and each row with its own version, and nothing else.
- **What it reads** (DM-74 section 3.4): one transaction whose first statement holds the actor's
  account row ``FOR SHARE`` (``read_account_shared``), as the match read does; then only the
  profile's account ID, the actor's own directional row and the actor's own block, each keyed by
  the actor as ``actor_id`` and the profile's account as ``target_id``; never a refusal of its
  own (no ``not_found`` for a profile), never the profile's state, and never a row whose actor is
  the other member.
- **The route** (owner-only): an unauthenticated request is ``unauthenticated`` (401), another
  method ``invalid_request`` (405), a query string or a body ``invalid_request`` (400), each
  ``Cache-Control: no-store``; an answer is the actor's read, by the actor's account and the
  path's profile ID only, served ``no-store``.

Each Django-dependent check runs in a fresh process under ``tests.discovery_offline_settings``
(Django's dummy backend), as ``test_interactions_offline`` does. The cases that need the database
(each state after its command, the alike answers byte-identical, the other member's rows never
shown, the account lock held and the three recoveries) run on a disposable PostgreSQL in
``proofs/postgres-ordering``'s discovery suite (``interaction_cases``' ``own_versions.*``). All data
is synthetic.
"""

import ast
import unittest
from pathlib import Path

from tests.test_discovery_offline import under_discovery_settings
from tests.test_profiles_offline import last_json

API_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = API_ROOT / "glow_discovery"
KEYS = [
    "block_state",
    "block_version",
    "interaction_state",
    "interaction_version",
    "kind",
    "target_profile_id",
]

# -- the answer (D13) ---------------------------------------------------------------------------

ANSWERS = """
import json, sys
sys.path.insert(0, "../../packages/contracts")
from glow_discovery import contract
from runtime import valid

TARGET = "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f"
ROWS = {"none": None, "liked": ("liked", 1), "passed": ("passed", 1),
        "withdrawn": ("withdrawn", 2), "resurfaced": ("liked", 3)}
BLOCKS = {"none": None, "active": ("active", 1), "removed": ("removed", 2)}
found = {}
for row_name, row in ROWS.items():
    for block_name, block in BLOCKS.items():
        value = contract.own_versions(TARGET, row, block)
        envelope = {"contract_version": "gapp-api-v1",
                    "request_id": "44444444-4444-4444-8444-444444444444", "data": value}
        found[f"{row_name}/{block_name}"] = {
            "value": value,
            "dto": valid("production", "OwnInteractionVersions", value),
            "served": valid("production", "AppResponse", envelope),
        }
print(json.dumps({"answers": found, "kind": contract.OWN_VERSIONS}))
"""

ROW_EXPECTED = {
    "none": ("none", 0),
    "liked": ("liked", 1),
    "passed": ("passed", 1),
    "withdrawn": ("withdrawn", 2),
    "resurfaced": ("liked", 3),
}
BLOCK_EXPECTED = {"none": ("none", 0), "active": ("active", 1), "removed": ("removed", 2)}


class OwnVersionsAnswerTests(unittest.TestCase):
    """D13: the read's answer for each state of the actor's own rows."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = last_json(under_discovery_settings(ANSWERS))

    def test_each_state_and_version_is_the_dto_and_served_in_app_response(self) -> None:
        answers = self.seen["answers"]
        self.assertEqual(len(answers), len(ROW_EXPECTED) * len(BLOCK_EXPECTED))
        for row_name, (row_state, row_version) in ROW_EXPECTED.items():
            for block_name, (block_state, block_version) in BLOCK_EXPECTED.items():
                with self.subTest(row=row_name, block=block_name):
                    answer = answers[f"{row_name}/{block_name}"]
                    self.assertTrue(answer["dto"])
                    self.assertTrue(answer["served"])
                    self.assertEqual(
                        answer["value"],
                        {
                            "kind": "own_interaction_versions",
                            "target_profile_id": "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f",
                            "interaction_state": row_state,
                            "interaction_version": row_version,
                            "block_state": block_state,
                            "block_version": block_version,
                        },
                    )
                    self.assertEqual(sorted(answer["value"]), KEYS)
        self.assertEqual(self.seen["kind"], "own_interaction_versions")


# -- what it reads (DM-74 section 3.4) ---------------------------------------------------------


def _read_function() -> ast.FunctionDef:
    tree = ast.parse((DISCOVERY / "interactions.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "read_own_versions":
            return node
    raise AssertionError("no read_own_versions")


def _body(function: ast.FunctionDef) -> ast.FunctionDef:
    found = [n for n in function.body if isinstance(n, ast.FunctionDef) and n.name == "body"]
    assert len(found) == 1
    return found[0]


def _calls(node: ast.AST) -> list[str]:
    return [ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)]


class OwnVersionsStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.function = _read_function()
        self.body = _body(self.function)

    def test_the_actors_account_is_held_for_share_first_in_one_transaction(self) -> None:
        # As the match read: the account row FOR SHARE, the transaction's first statement, so the
        # read waits for a command of the actor's in flight (every writer of a directional row or
        # a block takes it FOR NO KEY UPDATE first).
        self.assertEqual(ast.unparse(self.body.body[0]), "read_account_shared(tx, account_id)")
        outside = [s for s in self.function.body if not isinstance(s, ast.FunctionDef)]
        self.assertEqual([ast.unparse(s) for s in outside[1:]], ["return run(body, probe)"])

    def test_it_reads_only_the_actors_own_rows(self) -> None:
        # The profile's account ID through ``_account_of_profile`` (its ID only, pinned by
        # ``test_interactions_offline``), then the actor's own directional row and own block, each
        # keyed by the actor as actor_id and the profile's account as target_id: never the other
        # direction, never a combination, an exclusion or another model.
        filters = [
            n
            for n in ast.walk(self.body)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            if n.func.attr in ("filter", "get", "exclude", "all", "raw", "extra")
        ]
        self.assertEqual(
            sorted(ast.unparse(n) for n in filters),
            [
                "Block.objects.filter(actor_id=account_id, target_id=target_id)",
                "DirectionalInteraction.objects.filter(actor_id=account_id, target_id=target_id)",
            ],
        )
        names = {n.id for n in ast.walk(self.body) if isinstance(n, ast.Name)}
        self.assertNotIn("Q", names)
        self.assertNotIn("Profile", names)
        self.assertNotIn("Match", names)
        self.assertEqual(
            ast.unparse(self.body.body[1]),
            "target_id = _account_of_profile(str(profile_id))",
        )
        self.assertEqual(
            [c for c in _calls(self.body) if c.startswith("_")], ["_account_of_profile"]
        )
        self.assertFalse(any(isinstance(n, ast.BinOp) for n in ast.walk(self.body)))

    def test_it_never_refuses_a_profile(self) -> None:
        # No not_found for a missing profile, no answer that depends on its state: the read has no
        # refusal of its own; only SV2's ``read_account_shared`` refuses, for the actor's own
        # account.
        for node in ast.walk(self.function):
            with self.subTest(line=getattr(node, "lineno", 0)):
                self.assertNotIsInstance(node, ast.Raise)
        names = {n.id for n in ast.walk(self.function) if isinstance(n, ast.Name)}
        self.assertTrue({"Refused", "NOT_FOUND", "FORBIDDEN"}.isdisjoint(names))
        returns = [n for n in ast.walk(self.body) if isinstance(n, ast.Return)]
        self.assertEqual(
            [ast.unparse(n) for n in returns],
            ["return Result('read', data=contract.own_versions(str(profile_id), row, own_block))"],
        )
        self.assertFalse(any(isinstance(n, ast.If) for n in ast.walk(self.body)))


# -- the route (owner-only) ---------------------------------------------------------------------

ROUTE = """
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

PROFILE = "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f"
actor = Actor(uuid4(), 1, "active", uuid4(), "valid")


class Signed:
    is_authenticated = True


factory = APIRequestFactory()
calls = []


def read(account_id, profile_id):
    calls.append([str(account_id), str(profile_id)])
    return Result("read", data=contract.own_versions(str(profile_id), ("passed", 1), None))


def send(method, *, path="/x", body=None, signed=True):
    request = factory.generic(method, path, data=body or b"", content_type="application/json")
    if signed:
        force_authenticate(request, user=Signed(), token=actor)
    response = views.OwnVersionsView.as_view()(request, profile_id=UUID(PROFILE))
    response.render()
    payload = json.loads(response.content.decode("utf-8"))
    return {
        "status": response.status_code,
        "cache": response.get("Cache-Control"),
        "authenticate": response.get("WWW-Authenticate"),
        "body": payload,
        "valid": valid("production", "AppResponse", payload),
        "error": valid("production", "Error", payload),
    }


cases = {}
with mock.patch.object(views.interactions, "read_own_versions", read):
    cases["read"] = send("GET")
    cases["unauthenticated"] = send("GET", signed=False)
    for method in ("POST", "PUT", "PATCH", "DELETE"):
        cases[method] = send(method, body=b"{}")
    cases["query"] = send("GET", path="/x?profile_id=" + PROFILE)
    cases["body"] = send("GET", body=b'{"profile_id": "' + PROFILE.encode() + b'"}')
print(json.dumps({"cases": cases, "calls": calls, "records": records,
                  "actor": str(actor.account_id)}))
"""

ROUTE_ANSWERS = {
    "unauthenticated": (401, "unauthenticated"),
    "POST": (405, "invalid_request"),
    "PUT": (405, "invalid_request"),
    "PATCH": (405, "invalid_request"),
    "DELETE": (405, "invalid_request"),
    "query": (400, "invalid_request"),
    "body": (400, "invalid_request"),
}


class OwnVersionsRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = last_json(under_discovery_settings(ROUTE))

    def test_only_the_signed_in_actors_bodyless_get_is_answered(self) -> None:
        cases = self.seen["cases"]
        self.assertEqual(set(cases), {"read", *ROUTE_ANSWERS})
        for case, (status, code) in ROUTE_ANSWERS.items():
            with self.subTest(case=case):
                answer = cases[case]
                self.assertEqual(answer["status"], status)
                self.assertTrue(answer["error"])
                self.assertEqual(answer["body"]["code"], code)
                self.assertEqual(answer["cache"], "no-store")
        self.assertEqual(cases["unauthenticated"]["authenticate"], "Bearer")
        # Only the signed-in actor's bodyless GET reaches the read, by the actor's account and the
        # path's profile ID, nothing else.
        self.assertEqual(
            self.seen["calls"], [[self.seen["actor"], "6f1c2a3e-8b4d-4c5e-9f60-7a8b9c0d1e2f"]]
        )

    def test_the_answer_is_the_read_served_no_store(self) -> None:
        answer = self.seen["cases"]["read"]
        self.assertEqual(answer["status"], 200)
        self.assertTrue(answer["valid"])
        self.assertEqual(answer["cache"], "no-store")
        self.assertEqual(answer["body"]["data"]["kind"], "own_interaction_versions")
        self.assertEqual(sorted(answer["body"]["data"]), KEYS)

    def test_the_route_logs_reason_codes_only(self) -> None:
        # The answer logs nothing; each refused query or body logs the route's one reason code.
        lines = [line for name, line in self.seen["records"] if name.startswith("glow_discovery")]
        self.assertEqual(lines, ["interaction route refused: invalid_request"] * 2)


if __name__ == "__main__":
    unittest.main()
