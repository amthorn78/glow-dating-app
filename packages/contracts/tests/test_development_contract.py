"""Validate actual scaffold responses, never live providers or persistence."""

import copy
import json
import os
from pathlib import Path

os.environ["GLOW_ENV"] = "test"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glow_api.settings")

import django  # noqa: E402
from django.test import SimpleTestCase  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

django.setup()

from glow_api.fixtures import recommendations  # noqa: E402

CONTRACT_DIR = Path(__file__).resolve().parents[1] / "development"
SCHEMA = json.loads((CONTRACT_DIR / "gapp-dev-v1.schema.json").read_text())
OPENAPI = json.loads((CONTRACT_DIR / "openapi.json").read_text())


def validator(definition):
    schema = {**SCHEMA, "$ref": f"#/$defs/{definition}"}
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


class DevelopmentContractTests(SimpleTestCase):
    databases = set()

    def test_schema_is_valid_and_actual_get_responses_conform(self):
        expected = {
            "/health/live": (200, "Liveness"),
            "/health/ready": (503, "Readiness"),
            "/api/v1/development/recommendations": (200, "DevelopmentRecommendations"),
        }
        self.assertEqual(set(OPENAPI["paths"]), set(expected))
        self.assertEqual(OPENAPI["openapi"], "3.1.0")
        self.assertEqual(OPENAPI["info"]["version"], "gapp-dev-v1")
        for route, (status, definition) in expected.items():
            with self.subTest(route=route):
                documented = OPENAPI["paths"][route]["get"]["responses"][str(status)]
                self.assertEqual(
                    documented["content"]["application/json"]["schema"]["$ref"],
                    f"./gapp-dev-v1.schema.json#/$defs/{definition}",
                )
                response = self.client.get(route)
                self.assertEqual(response.status_code, status)
                self.assertEqual(response["Cache-Control"], "no-store")
                validator(definition).validate(response.json())

    def test_fixture_validates_and_profile_identifiers_are_distinct(self):
        body = recommendations()
        validator("DevelopmentRecommendations").validate(body)
        ids = [item["profile_id"] for item in body["items"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_empty_development_list_is_valid(self):
        validator("DevelopmentRecommendations").validate(
            {"mode": "fixture", "contract_version": "gapp-dev-v1", "items": []}
        )

    def test_private_fields_and_numeric_compatibility_are_rejected(self):
        schema = validator("DevelopmentRecommendations")
        cases = []
        root_extra = recommendations()
        root_extra["account_id"] = "private-account"
        cases.append(root_extra)
        private_birth = recommendations()
        private_birth["items"][0]["birth_time"] = "12:00"
        cases.append(private_birth)
        numeric_score = recommendations()
        numeric_score["items"][0]["compatibility"]["score"] = 98
        cases.append(numeric_score)
        for index, body in enumerate(cases):
            with self.subTest(case=index):
                self.assertFalse(schema.is_valid(body))

    def test_wrong_versions_markers_and_result_claims_are_rejected(self):
        schema = validator("DevelopmentRecommendations")
        cases = []
        for key, value in (("mode", "live"), ("contract_version", "gapp-dev-v2")):
            body = recommendations()
            body[key] = value
            cases.append(body)
        missing_mode = recommendations()
        del missing_mode["mode"]
        cases.append(missing_mode)
        for field, value in (("status", "ready"), ("source", "hde")):
            body = recommendations()
            body["items"][0]["compatibility"][field] = value
            cases.append(body)
        for index, body in enumerate(cases):
            with self.subTest(case=index):
                self.assertFalse(schema.is_valid(body))

    def test_malformed_primitives_and_development_bounds_are_rejected(self):
        schema = validator("DevelopmentRecommendations")
        for field, value in (
            ("age", True),
            ("age", 17),
            ("age", 121),
            ("age", 30.5),
            ("display_name", "   "),
            ("display_name", "x" * 81),
            ("profile_id", ""),
            ("summary", None),
        ):
            with self.subTest(field=field, value=value):
                body = recommendations()
                body["items"][0][field] = value
                self.assertFalse(schema.is_valid(body))
        oversized = recommendations()
        oversized["items"] = [copy.deepcopy(oversized["items"][0]) for _ in range(51)]
        self.assertFalse(schema.is_valid(oversized))

