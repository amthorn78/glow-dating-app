"""SV3 Stage A, the parts that need no database (its brief's D2, D3, D6, D7, D13, D17 and D19).

The page route the discovery URL configuration serves, and no action route; the keyed tie-break and
its SQL construction (Q2); the cursor's binding (Q4); the selection's settings and policy version
(Q3); the ranking's port states and bands (D6); the request check and the card's projection (D13);
no log line carrying a value; the account row first in each page's transaction; and every pointer
taken through ``settings_store`` in one call (D19).

Each Django-dependent check runs in a fresh process under ``tests.discovery_offline_settings`` (the
three fragments, Django's dummy backend and keys generated for that process). The cases themselves
run on a disposable PostgreSQL in ``proofs/postgres-ordering``'s discovery suite, through the HTTP
endpoints.
"""

import ast
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.test_profiles_offline import last_json

API_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = API_ROOT / "glow_discovery"


def under_discovery_settings(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import django\ndjango.setup()\n" + code],
        cwd=API_ROOT,
        env={
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "DJANGO_SETTINGS_MODULE": "tests.discovery_offline_settings",
        },
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def modules() -> dict[str, ast.Module]:
    return {
        path.name: ast.parse(path.read_text(encoding="utf-8"))
        for path in sorted(DISCOVERY.glob("*.py"))
    }


class DiscoveryRouteTests(unittest.TestCase):
    def test_the_page_route_is_served_and_no_action_route(self) -> None:
        seen = last_json(
            under_discovery_settings(
                "import json\nfrom glow_discovery import urls, views\n"
                "print(json.dumps({'routes': [str(p.pattern) for p in urls.urlpatterns],"
                " 'methods': views.PageView.http_method_names}))"
            )
        )
        self.assertEqual(seen["routes"], ["api/v1/discovery/page"])
        self.assertEqual(seen["methods"], ["post"])


class KeyTests(unittest.TestCase):
    def test_the_tie_break_is_salted_hmac_and_its_sql_construction_agrees(self) -> None:
        seen = last_json(
            under_discovery_settings(
                """
import hashlib, json
from uuid import uuid4
from django.utils.crypto import salted_hmac
from glow_discovery import keys
batch, profile = uuid4(), uuid4()
message = f"{batch}:{profile}".encode()
ipad, opad = keys.sql_pads()
inner = hashlib.sha256(ipad + message).digest()
sql_like = hashlib.sha256(opad + inner).digest()
expected = salted_hmac(keys.TIE_BREAK_SALT, f"{batch}:{profile}", algorithm="sha256").digest()
unkeyed = hashlib.sha256(message).digest()
print(json.dumps({
    "python": keys.tie_break(batch, profile) == expected,
    "sql": sql_like == expected,
    "unkeyed": unkeyed == expected,
    "pads": [len(ipad), len(opad)],
}))
"""
            )
        )
        self.assertTrue(seen["python"])
        self.assertTrue(seen["sql"])
        self.assertFalse(seen["unkeyed"])
        self.assertEqual(seen["pads"], [64, 64])

    def test_a_cursor_is_bound_to_its_viewer_collection_batch_and_offset(self) -> None:
        seen = last_json(
            under_discovery_settings(
                """
import json, re
from uuid import uuid4
from glow_discovery import keys
viewer, other, batch = uuid4(), uuid4(), uuid4()
cursor = keys.cursor(viewer, "recommendations", batch, 7)
head, offset, mac = cursor.split(".")
flipped = mac[:-1] + ("0" if mac[-1] != "0" else "1")
print(json.dumps({
    "length": len(cursor),
    "pattern": re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", cursor) is not None,
    "own": keys.read_cursor(cursor, viewer, "recommendations") == (batch, 7),
    "other_viewer": keys.read_cursor(cursor, other, "recommendations"),
    "other_collection": keys.read_cursor(cursor, viewer, "discovery"),
    "offset": keys.read_cursor(f"{head}.08.{mac}", viewer, "recommendations"),
    "mac": keys.read_cursor(f"{head}.{offset}.{flipped}", viewer, "recommendations"),
    "batch": keys.read_cursor(f"{uuid4().hex}.{offset}.{mac}", viewer, "recommendations"),
    "garbage": keys.read_cursor("not-a-cursor", viewer, "recommendations"),
}))
"""
            )
        )
        self.assertLessEqual(seen["length"], 100)
        self.assertTrue(seen["pattern"])
        self.assertTrue(seen["own"])
        for refused in ("other_viewer", "other_collection", "offset", "mac", "batch", "garbage"):
            with self.subTest(refused=refused):
                self.assertIsNone(seen[refused])


class PolicyTests(unittest.TestCase):
    def test_the_selection_settings_are_named_in_order_and_versioned_together(self) -> None:
        seen = last_json(
            under_discovery_settings(
                """
import json
from glow_discovery import policy
numbers = {name: 1 for name in policy.SELECTION_SETTINGS}
base = policy.policy_version(numbers)
changed = {name: policy.policy_version({**numbers, name: 2}) != base
           for name in policy.SELECTION_SETTINGS}
print(json.dumps({
    "settings": list(policy.SELECTION_SETTINGS),
    "changed": changed,
    "adult": list(policy.ACCEPTED_AGE_STATES),
    "bounds": [policy.BATCH_LIMIT, policy.PAGE_MAX, policy.BATCH_LIFETIME.total_seconds()],
    "port": policy.compatibility_port() is None,
}))
"""
            )
        )
        self.assertEqual(
            seen["settings"],
            [
                "consent.onboarding",
                "discovery.resurfacing",
                "profile.age_range",
                "profile.location",
                "profile.narrowing",
            ],
        )
        self.assertEqual(seen["settings"], sorted(seen["settings"]))
        self.assertTrue(all(seen["changed"].values()))
        self.assertEqual(seen["adult"], ["self_declared_adult"])
        self.assertEqual(seen["bounds"], [100, 50, 1800.0])
        # The offline settings, like the runtime, select no compatibility provider.
        self.assertTrue(seen["port"])

    def test_a_fixture_provider_is_refused_outside_development_and_test(self) -> None:
        seen = last_json(
            under_discovery_settings(
                """
import json
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from glow_discovery import policy
found = {}
with override_settings(GLOW_DISCOVERY_COMPATIBILITY_FIXTURE="explicitly-synthetic-ready",
                       GLOW_DISCOVERY_ENVIRONMENT="test"):
    policy.require_fixture_environment()
    found["test"] = type(policy.compatibility_port()).__name__
for environment in ("production", "staging", None):
    with override_settings(GLOW_DISCOVERY_COMPATIBILITY_FIXTURE="explicitly-synthetic-ready",
                           GLOW_DISCOVERY_ENVIRONMENT=environment):
        try:
            policy.require_fixture_environment()
            found[str(environment)] = "allowed"
        except ImproperlyConfigured:
            found[str(environment)] = "refused"
        try:
            policy.compatibility_port()
            found[f"port:{environment}"] = "built"
        except ValueError:
            found[f"port:{environment}"] = "refused"
print(json.dumps(found))
"""
            )
        )
        self.assertEqual(seen["test"], "FixtureCompatibilityProvider")
        for environment in ("production", "staging", "None"):
            with self.subTest(environment=environment):
                self.assertEqual(seen[environment], "refused")
                self.assertEqual(seen[f"port:{environment}"], "refused")


RANKING = """
import json
from unittest import mock
from uuid import uuid4
from glow_discovery import pages, policy
from glow_domain.compatibility import FixtureCase

def row(tie):
    return {"account_id": uuid4(), "chart": ("resolved", "fixture:ref", 1, 1), "tie_break": tie}

viewer = pages.Viewer(True, (1, 1, 1), ("resolved", "fixture:viewer", 1, 1))
selection = mock.Mock(version="discovery.1.1.1.1.1")
calls = []

class Port:
    def __init__(self, case):
        self.inner = policy.FixtureCompatibilityProvider(
            "test", FixtureCase(case), policy.PROVENANCE
        )
    def evaluate_pair(self, request):
        calls.append(1)
        return self.inner.evaluate_pair(request)

found = {}
with mock.patch.object(policy, "compatibility_port", lambda: Port("explicitly-synthetic-ready")):
    found["empty"] = pages._recommend(uuid4(), viewer, [], selection)[0]
    found["empty_calls"] = len(calls)
with mock.patch.object(policy, "compatibility_port", lambda: None):
    found["none"] = pages._recommend(uuid4(), viewer, [row(b"a")], selection)[0]
for case in ("pending-chart", "engine-unavailable", "unsupported-contract"):
    with mock.patch.object(policy, "compatibility_port", lambda case=case: Port(case)):
        state, entries = pages._recommend(uuid4(), viewer, [row(b"a"), row(b"b")], selection)
        found[case] = [state, len(entries)]
rows = [row(bytes([n])) for n in (5, 1, 4, 2, 3)]
with mock.patch.object(policy, "compatibility_port", lambda: Port("explicitly-synthetic-ready")):
    state, entries = pages._recommend(uuid4(), viewer, rows, selection)
    found["one_band"] = [e["tie_break"][0] for e in entries]
    with mock.patch.object(policy, "band", lambda result: None):
        found["no_band"] = pages._recommend(uuid4(), viewer, rows, selection)[0]
def banded(result):
    return next(banded.values)
banded.values = iter([0, 1, 0, 1, 0])
with mock.patch.object(policy, "compatibility_port", lambda: Port("explicitly-synthetic-ready")):
    with mock.patch.object(policy, "band", banded):
        state, entries = pages._recommend(uuid4(), viewer, rows, selection)
        found["two_bands"] = [e["tie_break"][0] for e in entries]
print(json.dumps(found))
"""


class RankingTests(unittest.TestCase):
    def test_the_ports_states_and_the_bands_order_recommendations(self) -> None:
        seen = last_json(under_discovery_settings(RANKING))
        # F07: no eligible candidate is an empty batch, with no provider call.
        self.assertEqual(seen["empty"], "empty")
        self.assertEqual(seen["empty_calls"], 0)
        # D6: no port is unavailable; the port's states are the batch's.
        self.assertEqual(seen["none"], "unavailable")
        self.assertEqual(seen["pending-chart"], ["pending", 0])
        self.assertEqual(seen["engine-unavailable"], ["unavailable", 0])
        self.assertEqual(seen["unsupported-contract"], ["empty", 0])
        # One band: the keyed tie-break orders it.
        self.assertEqual(seen["one_band"], [1, 2, 3, 4, 5])
        self.assertEqual(seen["no_band"], "empty")
        # Bands first, then the tie-break within each (rows 5, 1, 4, 2, 3 in bands 0, 1, 0, 1, 0).
        self.assertEqual(seen["two_bands"], [3, 4, 5, 1, 2])


CONTRACT = """
import json, sys
sys.path.insert(0, "../../packages/contracts")
from datetime import UTC, datetime
from uuid import uuid4
from glow_discovery import contract
from glow_profiles.contract import Invalid, app_response
from runtime import valid

def parses(body):
    try:
        contract.parse_page_request(body)
        return True
    except Invalid:
        return False

found = {"valid": parses(b'{"collection": "recommendations", "cursor": null, "limit": 50}'),
         "integral": parses(b'{"collection": "discovery", "cursor": null, "limit": 5.0}')}
for name, body in {
    "extra": b'{"collection": "discovery", "cursor": null, "limit": 5, "x": 1}',
    "missing": b'{"collection": "discovery", "limit": 5}',
    "zero": b'{"collection": "discovery", "cursor": null, "limit": 0}',
    "over": b'{"collection": "discovery", "cursor": null, "limit": 51}',
    "fraction": b'{"collection": "discovery", "cursor": null, "limit": 1.5}',
    "text": b'{"collection": "discovery", "cursor": null, "limit": "5"}',
    "collection": b'{"collection": "everyone", "cursor": null, "limit": 5}',
    "long": b'{"collection": "discovery", "cursor": "' + b"a" * 101 + b'", "limit": 5}',
    "newline": b'{"collection": "discovery", "cursor": "abc\\\\n", "limit": 5}',
    "nan": b'{"collection": "discovery", "cursor": null, "limit": NaN}',
    "array": b'[]',
    "bytes": b'\\xff',
}.items():
    found[name] = parses(body)
fields = {
    "gender": {"value_ids": ["woman"], "own_words": "Synthetic words", "shown": False},
    "orientation": {"value_ids": ["not-stated"], "own_words": None, "shown": True},
    "looking_for": {"value_ids": ["long-term", "casual"], "own_words": None, "shown": True},
    "relationship_status": {"value_ids": ["single"], "own_words": None, "shown": True},
}
details = contract.details(fields, "New York-Newark-Jersey City, NY-NJ Metro Area")
found["details"] = details
found["details_text"] = contract.details(json.dumps(fields), None)
found["no_looking_for"] = contract.details({"gender": fields["gender"]}, "x")
profile = str(uuid4())
row = {"profile_id": profile, "display_name": "Synthetic Member", "age": 30,
       "bio": "A synthetic member.", "details": details}
card = contract.card(row, ["delivery-0123456789abcdef0123456789abcdef"])
page = contract.page(
    collection="recommendations", batch_id=str(uuid4()), version=1, state="ready",
    items=[card], next_cursor=None,
    expires_at=datetime(2026, 11, 11, 20, 0, 1, 900, tzinfo=UTC),
)
envelope = app_response(page, str(uuid4()))
found["valid_page"] = valid("production", "AppResponse", envelope)
found["page_keys"] = sorted(page)
found["card_keys"] = sorted(card)
found["profile_keys"] = sorted(card["profile"])
found["expires_at"] = page["expires_at"]
empty = contract.page(collection="discovery", batch_id=str(uuid4()), version=1, state="empty",
                      items=[], next_cursor=None, expires_at=datetime(2026, 11, 11, tzinfo=UTC))
found["valid_empty"] = valid("production", "AppResponse", app_response(empty, str(uuid4())))
print(json.dumps(found))
"""


class ContractTests(unittest.TestCase):
    def test_the_request_is_a_closed_page_request(self) -> None:
        seen = last_json(under_discovery_settings(CONTRACT))
        self.assertTrue(seen["valid"])
        self.assertTrue(seen["integral"])
        for name in (
            "extra",
            "missing",
            "zero",
            "over",
            "fraction",
            "text",
            "collection",
            "long",
            "newline",
            "nan",
            "array",
            "bytes",
        ):
            with self.subTest(body=name):
                self.assertFalse(seen[name])

    def test_the_card_shows_only_what_display_allows(self) -> None:
        seen = last_json(under_discovery_settings(CONTRACT))
        details = seen["details"]
        # Gender's flag is off: not shown, own words included. Orientation is not stated: nothing
        # to show. "Looking for" always; relationship status while its flag is on.
        self.assertIsNone(details["gender"])
        self.assertIsNone(details["orientation"])
        self.assertEqual(details["looking_for"], ["long-term", "casual"])
        self.assertEqual(details["relationship_status"], {"value_ids": ["single"]})
        self.assertEqual(details["area_name"], "New York-Newark-Jersey City, NY-NJ Metro Area")
        self.assertEqual(seen["details_text"]["area_name"], None)
        # A card without "looking for" is left out (fails closed).
        self.assertIsNone(seen["no_looking_for"])

    def test_the_page_is_the_contracts_card_page(self) -> None:
        seen = last_json(under_discovery_settings(CONTRACT))
        self.assertTrue(seen["valid_page"])
        self.assertTrue(seen["valid_empty"])
        self.assertEqual(
            seen["page_keys"],
            [
                "batch_id",
                "collection",
                "expires_at",
                "items",
                "kind",
                "next_cursor",
                "state",
                "version",
            ],
        )
        self.assertEqual(seen["card_keys"], ["details", "profile", "profile_id"])
        self.assertEqual(
            seen["profile_keys"],
            [
                "age",
                "compatibility",
                "display_name",
                "media_delivery_refs",
                "profile_id",
                "summary",
            ],
        )
        # Whole seconds, a fraction dropped (never rounded up).
        self.assertEqual(seen["expires_at"], "2026-11-11T20:00:01Z")


class StructureTests(unittest.TestCase):
    def test_no_log_line_carries_a_value(self) -> None:
        for name, tree in modules().items():
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "logger"
                ):
                    with self.subTest(module=name, line=node.lineno):
                        self.assertIsInstance(node.args[0], ast.Constant)
                        for argument in node.args[1:]:
                            # Only a refusal's reason code, or a contract code's name.
                            self.assertIn(
                                ast.unparse(argument), ("result.reason", "INVALID_REQUEST")
                            )
        self.assertNotIn("print(", (DISCOVERY / "pages.py").read_text(encoding="utf-8"))

    def test_each_page_transaction_takes_the_account_row_first(self) -> None:
        tree = modules()["pages.py"]
        firsts: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in ("create", "continue_page"):
                body = next(item for item in node.body if isinstance(item, ast.FunctionDef))
                first = next(item for item in body.body if isinstance(item, ast.Expr))
                assert isinstance(first.value, ast.Call)
                firsts[node.name] = ast.unparse(first.value.func)
        self.assertEqual(firsts, {"create": "lock_account", "continue_page": "read_account_shared"})

    def test_every_pointer_is_taken_through_the_settings_store_once(self) -> None:
        # D19: glow_discovery locks no pointer itself (no code string names the pointer's table or
        # takes a row lock), and takes every setting it reads in one read_shared call, which each
        # page's transaction makes once, first after the account row.
        for name, tree in modules().items():
            docstrings = {
                id(node.body[0].value)
                for node in ast.walk(tree)
                if isinstance(node, ast.Module | ast.FunctionDef | ast.ClassDef)
                and node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
            }
            strings = [
                node.value.lower()
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and id(node) not in docstrings
            ]
            for word in ("policyrevision", "for share", "for update"):
                with self.subTest(module=name, word=word):
                    self.assertFalse(any(word in text for text in strings))
        calls = [
            node
            for node in ast.walk(modules()["pages.py"])
            if isinstance(node, ast.Call) and ast.unparse(node.func).endswith("read_shared")
        ]
        self.assertEqual(len(calls), 1)
        self.assertEqual(ast.unparse(calls[0].args[1]), "policy.SELECTION_SETTINGS")

    def test_the_statements_select_no_private_value(self) -> None:
        seen = last_json(
            under_discovery_settings(
                "import json\nfrom glow_discovery import predicates\n"
                "print(json.dumps({'card': predicates.CARD, 'names': list(predicates.CARD_NAMES)}))"
            )
        )
        for word in ("birth_date", "latitude", "longitude", "lat,", "lon,", "area_id", "miles"):
            with self.subTest(word=word):
                self.assertFalse(word in seen["card"])
        self.assertNotIn("area_id", seen["names"])
        self.assertNotIn("birth_date", seen["names"])

    def test_mypy_checks_the_discovery_slice(self) -> None:
        self.assertIn('"glow_discovery"', (API_ROOT / "pyproject.toml").read_text())


if __name__ == "__main__":
    unittest.main()
