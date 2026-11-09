"""A strict check of a served body against the contract's own schema (the SV1 brief's Outcome 5
and acceptance check 4), with no new dependency.

The proof's lock takes only SV1's pins (D12), so the JSON Schema library the API's tests use is
not installed here. This module reads ``packages/contracts/production/gapp-api-v1.schema.json``
and applies exactly the keywords the definitions it checks use (``description`` is an
annotation); **any other keyword is an error**, so a schema change cannot pass unchecked. A
``oneOf`` is decided by the ``kind`` every branch requires, as a ``const`` or an ``enum``: the
one branch whose values hold the body's ``kind`` is checked in full, and the others cannot
match, since each requires values the body's ``kind`` is not. The API's tests validate the same
builders with the contract's own validator (``packages/contracts/runtime.py``).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "packages"
    / "contracts"
    / "production"
    / "gapp-api-v1.schema.json"
)

_KEYWORDS = frozenset(
    {
        "type",
        "additionalProperties",
        "required",
        "properties",
        "const",
        "enum",
        "pattern",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "not",
        "oneOf",
        "$ref",
        "description",
    }
)


class UnsupportedSchema(Exception):
    """The schema uses a keyword this check does not apply."""


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(schema, dict)
    return schema


def _resolve(root: dict[str, Any], ref: str) -> dict[str, Any]:
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        raise UnsupportedSchema(f"reference {ref}")
    definition = root["$defs"][ref.removeprefix(prefix)]
    assert isinstance(definition, dict)
    return definition


def _type_ok(expected: str, value: Any) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    raise UnsupportedSchema(f"type {expected}")


def _kind_values(root: dict[str, Any], branch: dict[str, Any]) -> frozenset[str]:
    if set(branch) != {"$ref"}:
        raise UnsupportedSchema("a oneOf branch that is not a reference")
    definition = _resolve(root, branch["$ref"])
    kind = definition.get("properties", {}).get("kind", {})
    if "kind" not in definition.get("required", ()):
        raise UnsupportedSchema("a oneOf branch without a required kind")
    if "const" in kind:
        return frozenset({str(kind["const"])})
    if "enum" in kind:
        return frozenset(str(value) for value in kind["enum"])
    raise UnsupportedSchema("a oneOf branch whose kind is neither a const nor an enum")


def errors(root: dict[str, Any], schema: dict[str, Any], value: Any, at: str = "$") -> list[str]:
    """Every way ``value`` fails ``schema``, as paths and keywords (no value is echoed)."""
    unknown = set(schema) - _KEYWORDS
    if unknown:
        raise UnsupportedSchema(f"{at}: keywords {sorted(unknown)}")
    found: list[str] = []
    if "$ref" in schema:
        found += errors(root, _resolve(root, schema["$ref"]), value, at)
    if "type" in schema and not _type_ok(schema["type"], value):
        return found + [f"{at}: type"]
    if "const" in schema and value != schema["const"]:
        found.append(f"{at}: const")
    if "enum" in schema and value not in schema["enum"]:
        found.append(f"{at}: enum")
    if isinstance(value, str):
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            found.append(f"{at}: pattern")
        if "minLength" in schema and len(value) < schema["minLength"]:
            found.append(f"{at}: minLength")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            found.append(f"{at}: maxLength")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            found.append(f"{at}: minimum")
        if "maximum" in schema and value > schema["maximum"]:
            found.append(f"{at}: maximum")
    if "not" in schema and not errors(root, schema["not"], value, at):
        found.append(f"{at}: not")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", ()):
            if name not in value:
                found.append(f"{at}.{name}: required")
        if schema.get("additionalProperties") is False:
            for name in value:
                if name not in properties:
                    found.append(f"{at}.{name}: additionalProperties")
        elif "additionalProperties" in schema:
            raise UnsupportedSchema(f"{at}: additionalProperties other than false")
        for name, subschema in properties.items():
            if name in value:
                found += errors(root, subschema, value[name], f"{at}.{name}")
    if "oneOf" in schema:
        kind = value.get("kind") if isinstance(value, dict) else None
        matching = [b for b in schema["oneOf"] if kind in _kind_values(root, b)]
        if len(matching) != 1:
            found.append(f"{at}: oneOf ({len(matching)} branches by kind)")
        else:
            found += errors(root, matching[0], value, at)
    return found


def check(definition: str, value: Any, root: dict[str, Any] | None = None) -> list[str]:
    """The errors of ``value`` against ``#/$defs/<definition>``; empty when it is valid."""
    schema_root = root if root is not None else load_schema()
    return errors(schema_root, {"$ref": f"#/$defs/{definition}"}, value)
