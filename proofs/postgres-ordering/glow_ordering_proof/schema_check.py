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

SV2 Stage A extends the keywords to those its profile responses use, with JSON Schema 2020-12's
meanings: ``anyOf``, ``allOf``, ``if``/``then``/``else``, ``items``, ``minItems``, ``maxItems``,
``uniqueItems``, the ``array``, ``number`` and ``null`` types, and ``format`` for ``date`` and
``date-time`` (as ``runtime.py`` checks them). Every other keyword is still an error.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
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
        # SV2 Stage A:
        "anyOf",
        "allOf",
        "if",
        "then",
        "else",
        "items",
        "minItems",
        "maxItems",
        "uniqueItems",
        "format",
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
    # SV2 Stage A:
    if expected == "array":
        return isinstance(value, list)
    if expected == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    raise UnsupportedSchema(f"type {expected}")


def _format_ok(name: str, value: str) -> bool:
    """``date`` and ``date-time`` as ``packages/contracts/runtime.py`` checks them: a real
    calendar date; UTC whole seconds."""
    try:
        if name == "date":
            date.fromisoformat(value)
            return True
        if name == "date-time":
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            return True
    except ValueError:
        return False
    raise UnsupportedSchema(f"format {name}")


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
    if isinstance(value, int | float) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            found.append(f"{at}: minimum")
        if "maximum" in schema and value > schema["maximum"]:
            found.append(f"{at}: maximum")
    if isinstance(value, str) and "format" in schema and not _format_ok(schema["format"], value):
        found.append(f"{at}: format")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            found.append(f"{at}: minItems")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            found.append(f"{at}: maxItems")
        if schema.get("uniqueItems"):
            seen = [json.dumps(item, sort_keys=True) for item in value]
            if len(set(seen)) != len(seen):
                found.append(f"{at}: uniqueItems")
        if "items" in schema:
            for index, item in enumerate(value):
                found += errors(root, schema["items"], item, f"{at}[{index}]")
    if "anyOf" in schema and not any(
        not errors(root, branch, value, at) for branch in schema["anyOf"]
    ):
        found.append(f"{at}: anyOf")
    for branch in schema.get("allOf", ()):
        found += errors(root, branch, value, at)
    if "if" in schema:
        if not errors(root, schema["if"], value, at):
            if "then" in schema:
                found += errors(root, schema["then"], value, at)
        elif "else" in schema:
            found += errors(root, schema["else"], value, at)
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


def unique_keys(value: Any) -> bool:
    """The contract's key-uniqueness rule, applied after the schema (``runtime.py``'s
    ``unique_keys`` and mobile ``validation.ts``): ``items`` by ``profile_id`` (by ``asset_id``
    in a media collection) and ``selections`` by ``dimension`` hold no repeated key."""
    if isinstance(value, dict):
        item_key = "asset_id" if value.get("kind") == "media_collection" else "profile_id"
        for collection, key in (("items", item_key), ("selections", "dimension")):
            items = value.get(collection)
            if isinstance(items, list):
                keys = [item.get(key) if isinstance(item, dict) else None for item in items]
                if len(keys) != len(set(map(str, keys))):
                    return False
        return all(unique_keys(item) for item in value.values())
    if isinstance(value, list):
        return all(unique_keys(item) for item in value)
    return True


def check_body(definition: str, value: Any, root: dict[str, Any] | None = None) -> list[str]:
    """SV2: the schema's errors and the key-uniqueness rule, as the contract's validators apply
    them; empty when ``value`` is valid."""
    found = check(definition, value, root)
    if not found and not unique_keys(value):
        found.append("$: unique keys")
    return found
