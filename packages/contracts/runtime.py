"""JSON Schema validation plus documented collection-key invariants. No I/O adapters."""

import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

FORMATS = FormatChecker()


@FORMATS.checks("date-time", raises=ValueError)
def utc_seconds(value):
    if not isinstance(value, str):
        return True
    datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return True


ROOT = Path(__file__).resolve().parent
SCHEMAS = {
    "development": json.loads((ROOT / "development/gapp-dev-v1.schema.json").read_text()),
    "production": json.loads((ROOT / "production/gapp-api-v1.schema.json").read_text()),
}


def valid(scope, definition, value):
    schema = {**SCHEMAS[scope], "$ref": f"#/$defs/{definition}"}
    if not Draft202012Validator(schema, format_checker=FORMATS).is_valid(value):
        return False
    return unique_keys(value)


def unique_keys(value):
    """Schemas close shape; these collections additionally have unique keys."""
    if isinstance(value, dict):
        for collection, key in (("items", "profile_id"), ("selections", "dimension")):
            items = value.get(collection)
            if isinstance(items, list):
                keys = [item[key] for item in items]
                if len(keys) != len(set(keys)):
                    return False
        return all(unique_keys(item) for item in value.values())
    if isinstance(value, list):
        return all(unique_keys(item) for item in value)
    return True
