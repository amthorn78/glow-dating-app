"""Schema, projections and cross-language corpus; no DB or auth integration."""

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime import SCHEMAS, valid  # noqa: E402
from transition_contract import FLOWS  # noqa: E402


class ProductionContractTests(unittest.TestCase):
    def test_shared_valid_invalid_corpus(self):
        corpus = json.loads((ROOT / "corpus/shared-v1.json").read_text())
        for row in corpus["cases"]:
            with self.subTest(case=row["name"]):
                self.assertEqual(
                    valid(row["scope"], row["definition"], row["value"]), row["valid"]
                )

    def test_schemas_and_flow_references(self):
        for schema in SCHEMAS.values():
            Draft202012Validator.check_schema(schema)
        self.assertEqual(list(FLOWS), [f"F{i:02}" for i in range(1, 21)])
        for flow in FLOWS.values():
            for definition in flow["request_contracts"] + flow["response_contracts"]:
                if definition != "allauth-headless":
                    self.assertIn(definition, SCHEMAS["production"]["$defs"])
            self.assertEqual(
                set(flow["projection_roles"]), set(flow["response_contracts"])
            )
            for item in flow["transitions"]:
                self.assertNotEqual(item["from"], "deleted")
                self.assertNotEqual(item["from"], "completed")

    def test_production_openapi_catalog_does_not_claim_implemented_routes(self):
        catalog = json.loads((ROOT / "production/openapi.json").read_text())
        self.assertEqual(catalog["openapi"], "3.1.0")
        self.assertEqual(catalog["paths"], {})
        self.assertNotIn("servers", catalog)
        self.assertEqual(
            set(catalog["components"]["schemas"]), set(SCHEMAS["production"]["$defs"])
        )
        for name, reference in catalog["components"]["schemas"].items():
            self.assertEqual(
                reference, {"$ref": f"./gapp-api-v1.schema.json#/$defs/{name}"}
            )

    def test_fixture_identity_bridge_preserves_production_identity_boundary(self):
        fixture = json.loads((ROOT / "fixtures/interactions-v1.json").read_text())
        discovery = json.loads((ROOT / "fixtures/discovery-v1.json").read_text())
        identities = fixture["identities"]
        expected_accounts = {discovery["viewer"]["facts"]["account_id"]} | {
            candidate["account_id"] for candidate in discovery["candidates"]
        }
        self.assertEqual({row["account_id"] for row in identities}, expected_accounts)
        for field in ("account_id", "profile_id", "account_uuid", "profile_uuid"):
            self.assertEqual(len({row[field] for row in identities}), len(identities))
        self.assertFalse(
            {row["account_uuid"] for row in identities}
            & {row["profile_uuid"] for row in identities}
        )
        for row in identities:
            for field in ("account_uuid", "profile_uuid"):
                self.assertTrue(valid("production", "Identifier", row[field]))
            self.assertFalse(valid("production", "Identifier", row["profile_id"]))
            self.assertEqual(
                set(row), {"account_id", "profile_id", "account_uuid", "profile_uuid"}
            )
        self.assertFalse(fixture["policy"]["allow_pass_to_like"])
        self.assertFalse(fixture["policy"]["allow_rematch"])
        self.assertFalse(fixture["policy"]["allow_history"])

    def test_user_intents_do_not_accept_authority_fields(self):
        rows = json.loads((ROOT / "corpus/shared-v1.json").read_text())["cases"]
        for row in rows:
            if (
                row["valid"]
                and row["scope"] == "production"
                and isinstance(row["value"], dict)
                and "operation" in row["value"]
            ):
                for field in (
                    "actor_id",
                    "eligible",
                    "is_staff",
                    "consent_granted",
                    "active_match",
                ):
                    with self.subTest(schema=row["definition"], field=field):
                        self.assertFalse(
                            valid(
                                "production",
                                row["definition"],
                                {**row["value"], field: True},
                            )
                        )
