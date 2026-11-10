"""SV2 Stage A, the parts that need no database (its brief's D1, D11, D17 and D18).

The routes the profile URL configuration serves, and no staff route; no log line or refusal
reason carrying a submitted value; no SV2 code writing ``verified`` or a resolved mapping; every
member and staff operation taking the account row lock first (DM-13 4.1); and a stored
idempotency digest that cannot be reproduced without the key (D17).

Each Django-dependent check runs in a fresh process under ``tests.profiles_offline_settings``
(SV1's identity fragment and SV2's, Django's dummy backend and keys generated for that process).
The profile cases themselves run on a disposable PostgreSQL in ``proofs/postgres-ordering``'s
profile suite, through the HTTP endpoints.
"""

import ast
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

API_ROOT = Path(__file__).resolve().parents[1]
PROFILES = API_ROOT / "glow_profiles"

PROFILE_ROUTES = {
    "api/v1/profile",
    "api/v1/profile/completion",
    "api/v1/profile/visibility",
    "api/v1/profile/fields",
    "api/v1/profile/preferences",
    "api/v1/profile/filters",
    "api/v1/profile/area",
    "api/v1/profile/area/nearest",
    "api/v1/profile/catalog",
    "api/v1/profile/<uuid:profile_id>",
    "api/v1/consent",
    "api/v1/consent/sensitive",
    "api/v1/eligibility/adult",
    "api/v1/birth-input",
    "api/v1/birth-input/<uuid:input_id>",
}

# The member operations (commands take the account row lock; reads take it shared) and the staff
# operations that act on one account.
COMMANDS = {
    "save_profile",
    "set_field",
    "set_preferences",
    "set_filters",
    "set_area",
    "decide_onboarding_consent",
    "decide_sensitive_consent",
    "adult_check",
    "save_birth_input",
    "set_visibility",
}
READS = {"read", "nearest_area"}
STAFF = {"approve_without_id", "revoke_approval", "restrict_profile"}

# A refusal reason is a code. Its only interpolations are other closed codes: glow_chat's result
# reason and outcome, a field rule's refusal, the age transition's refusal and the adult outcome;
# the identity verification port's reason; and a publication's fixed-limit codes.
REASON = re.compile(r"[a-z_]+")
# A whole reason: a lowercase code, with one ``:``-qualified part at most (``tx.run``'s one
# exception type, ``DeadlockDetected``, is the only other).
REASON_CODE = re.compile(r"[a-z_]+(:[a-z_]+)?|DeadlockDetected")
REASON_PARTS = {
    "result.reason",
    "result.outcome",
    "refusal",
    "refused",
    "outcome.value",
    # ``tx.run``'s integrity error, reported by the driver's exception type only.
    "type(cause).__name__",
}
REASON_EXPRESSIONS = {
    "outcome.reason",
    "'refused:' + ','.join(refusals)",
    # ``tx.run``: a refusal's own reason, and an exception reported by its type only.
    "rollback.refused.reason",
    "type(exc).__name__",
}

# The static logging guard's other module: SV2's age section in SV1's age port (D4, D7).
AGE_PORT = API_ROOT / "glow_identity" / "age.py"


def module_constants(tree: ast.Module) -> dict[str, str]:
    """A module's upper-case string constants, by name."""
    return {
        target.id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id.isupper()
    }


def under_profile_settings(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import django\ndjango.setup()\n" + code],
        cwd=API_ROOT,
        env={
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "DJANGO_SETTINGS_MODULE": "tests.profiles_offline_settings",
        },
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def last_json(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    assert result.returncode == 0, result.stdout + result.stderr
    value: dict[str, Any] = json.loads(result.stdout.strip().splitlines()[-1])
    return value


def modules() -> dict[str, ast.Module]:
    return {
        path.name: ast.parse(path.read_text(encoding="utf-8"))
        for path in sorted(PROFILES.glob("*.py"))
    }


class ProfileRoutesTests(unittest.TestCase):
    def test_the_member_routes_are_served_and_no_staff_route(self) -> None:
        seen = last_json(
            under_profile_settings(
                """
import json
from django.conf import settings
from django.urls import get_resolver
from glow_identity.urls import urlpatterns as identity

def walk(patterns, prefix=""):
    for pattern in patterns:
        if hasattr(pattern, "url_patterns"):
            yield from walk(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            yield prefix + str(pattern.pattern)

served = set(walk(get_resolver().url_patterns))
print(json.dumps({
    "profile": sorted(served - set(walk(identity))),
    "all": sorted(served),
    "atomic": settings.DATABASES["default"].get("ATOMIC_REQUESTS", False),
    "engine": settings.DATABASES["default"]["ENGINE"],
}))
"""
            )
        )
        self.assertEqual(set(seen["profile"]), PROFILE_ROUTES)
        # Two helpers refuse a transaction the caller opened, so requests are not atomic.
        self.assertIs(seen["atomic"], False)
        self.assertEqual(seen["engine"], "django.db.backends.dummy")
        for route in seen["all"]:
            with self.subTest(route=route):
                for word in ("staff", "approve", "revoke", "restrict", "publish", "setting"):
                    self.assertNotIn(word, route)

    def test_no_view_reaches_a_staff_operation(self) -> None:
        for name in ("views.py", "urls.py"):
            tree = modules()[name]
            with self.subTest(module=name):
                imported = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        imported.add(node.module or "")
                        imported.update(f"{node.module}.{alias.name}" for alias in node.names)
                    elif isinstance(node, ast.Import):
                        imported.update(alias.name for alias in node.names)
                    elif isinstance(node, ast.Name):
                        self.assertNotEqual(node.id, "staff")
                self.assertFalse(any("staff" in module for module in imported), imported)


class NoValueInLogsTests(unittest.TestCase):
    """D17: a refusal names a code, never a field's value."""

    def test_only_the_views_log_and_only_a_code(self) -> None:
        for name, tree in modules().items():
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                    continue
                if not (isinstance(node.func.value, ast.Name) and node.func.value.id == "logger"):
                    continue
                with self.subTest(module=name, line=node.lineno):
                    self.assertEqual(name, "views.py")
                    self.assertEqual(node.func.attr, "info")
                    self.assertEqual(
                        [ast.unparse(argument) for argument in node.args][0],
                        "'profile route refused: %s'",
                    )
                    self.assertIn(ast.unparse(node.args[1]), {"result.reason", "INVALID_REQUEST"})
                    self.assertEqual(len(node.args), 2)

    def test_nothing_but_the_views_reaches_logging_or_imports_by_name(self) -> None:
        # A logger reached any other way (an import of logging, getLogger, an import by name)
        # would escape the check above.
        found = []
        for name, tree in modules().items():
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom):
                    roots = {(node.module or "").split(".")[0]}
                else:
                    roots = set()
                if "logging" in roots and name != "views.py":
                    found.append(f"{name}:{getattr(node, 'lineno', 0)} imports logging")
                if isinstance(node, ast.Call):
                    func = node.func
                    called = (
                        func.id
                        if isinstance(func, ast.Name)
                        else func.attr
                        if isinstance(func, ast.Attribute)
                        else ""
                    )
                    if called in {"__import__", "import_module"}:
                        found.append(f"{name}:{node.lineno} imports by name")
                    if called == "getLogger" and name != "views.py":
                        found.append(f"{name}:{node.lineno} gets a logger")
        self.assertEqual(found, [])

    def test_the_age_port_logs_and_prints_nothing(self) -> None:
        # C2 (finding 5): the age state's date passes through SV1's age port (D7's transition,
        # D4's ``age_years``), so the guard covers ``glow_identity/age.py`` too: no logging
        # import, no logger, no print, no import by name.
        tree = ast.parse(AGE_PORT.read_text(encoding="utf-8"))
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                if any(name.split(".")[0] in {"logging", "warnings"} for name in names):
                    found.append(f"{node.lineno} imports logging")
            if isinstance(node, ast.Name) and node.id in {"logger", "logging", "log", "print"}:
                found.append(f"{node.lineno} names {node.id}")
            if isinstance(node, ast.Attribute) and node.attr in {"getLogger", "warning", "debug"}:
                found.append(f"{node.lineno} reaches {node.attr}")
            if isinstance(node, ast.Call) and ast.unparse(node.func) in {
                "__import__",
                "importlib.import_module",
                "import_module",
            }:
                found.append(f"{node.lineno} imports by name")
        self.assertEqual(found, [])

    def _assert_reason_is_a_code(self, reason: ast.expr, constants: dict[str, str]) -> None:
        if isinstance(reason, ast.Constant):
            self.assertIsNotNone(REASON_CODE.fullmatch(str(reason.value)), reason.value)
        elif isinstance(reason, ast.Name) and reason.id in constants:
            # A module constant holding a code (``BIRTH_DATE_FAILS_ADULT_RULE``).
            self.assertIsNotNone(REASON_CODE.fullmatch(constants[reason.id]), reason.id)
        elif isinstance(reason, ast.JoinedStr):
            for part in reason.values:
                if isinstance(part, ast.FormattedValue):
                    self.assertIn(ast.unparse(part.value), REASON_PARTS)
                else:
                    assert isinstance(part, ast.Constant)
                    self.assertRegex(str(part.value), r"[a-z_]*[:_]")
        else:
            self.assertIn(ast.unparse(reason), REASON_EXPRESSIONS)

    def test_every_refusal_reason_is_a_code(self) -> None:
        # ``Refused(code, reason)`` and ``Result(outcome, code, reason)`` alike (C2, finding 7):
        # a reason is a code, a module constant holding one, or a closed interpolation; never a
        # value. A ``Result`` whose outcome is not a literal carries no reason at all.
        checked = 0
        for name, tree in modules().items():
            constants = module_constants(tree)
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                    continue
                if node.func.id == "Refused":
                    reason: ast.expr | None = node.args[1]
                elif node.func.id == "Result":
                    reason = next((k.value for k in node.keywords if k.arg == "reason"), None)
                    if reason is None and len(node.args) > 2:
                        reason = node.args[2]
                    if not (node.args and isinstance(node.args[0], ast.Constant)):
                        with self.subTest(module=name, line=node.lineno):
                            self.assertIsNone(reason, "a computed outcome carries no reason")
                        continue
                    if reason is None:
                        continue
                else:
                    continue
                with self.subTest(module=name, line=node.lineno):
                    self._assert_reason_is_a_code(reason, constants)
                    checked += 1
        self.assertGreater(checked, 60)

    def test_nothing_prints_but_the_area_steps_command(self) -> None:
        for name, tree in modules().items():
            prints = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ]
            with self.subTest(module=name):
                # The step's two results and its usage line; nothing else prints.
                self.assertEqual(len(prints), 3 if name == "areas_source.py" else 0)


class WritesTests(unittest.TestCase):
    def test_no_sv2_code_writes_verified_or_a_resolved_mapping(self) -> None:
        # D18: SV2 builds the seam and no provider, so nothing writes ``verified``; D8: the chart
        # mapping is resolved only by P05's worker, so nothing writes ``resolved``.
        written = set()
        for tree in modules().values():
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Attribute) and target.attr == "state":
                            written.add(ast.unparse(node.value))
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr
                    in {"create", "update", "update_or_create", "get_or_create", "bulk_create"}
                ):
                    for keyword in node.keywords:
                        if keyword.arg in {"state", "defaults"}:
                            written.add(ast.unparse(keyword.value))
                if isinstance(node, ast.Attribute) and node.attr in {"VERIFIED", "RESOLVED"}:
                    written.add(ast.unparse(node))
        # The check sees the states SV2 does write, so it is looking at the writes.
        self.assertTrue({"'pending'", "VerificationState.STAFF_APPROVED.value"} <= written)
        for value in written:
            with self.subTest(value=value):
                self.assertNotRegex(value, r"(?i)\bverified\b|\bresolved\b")

    def test_the_port_refuses_a_passed_check(self) -> None:
        seen = last_json(
            under_profile_settings(
                """
import json
from datetime import UTC, datetime
from uuid import uuid4
from glow_profiles.identity_verification import OrmIdentityVerification

outcome = OrmIdentityVerification(datetime.now(UTC)).record_check_passed(
    uuid4(), "fixture-reference"
)
print(json.dumps({"outcome": outcome.outcome, "reason": outcome.reason}))
"""
            )
        )
        self.assertEqual(seen, {"outcome": "refused", "reason": "no_provider"})


class LockOrderTests(unittest.TestCase):
    """DM-13 4.1: each operation's transaction starts with the account row: locked for a command
    or a staff operation, shared for a read."""

    def test_every_operation_takes_the_account_row_first(self) -> None:
        found: dict[str, str] = {}
        for name in ("operations.py", "staff.py"):
            for function in modules()[name].body:
                if not isinstance(function, ast.FunctionDef):
                    continue
                for inner in function.body:
                    if isinstance(inner, ast.FunctionDef) and inner.name == "body":
                        found[function.name] = ast.unparse(inner.body[0])
        self.assertEqual(set(found), COMMANDS | READS | STAFF)
        for operation, first in found.items():
            with self.subTest(operation=operation):
                expected = "read_account_shared" if operation in READS else "lock_account"
                self.assertEqual(first, f"{expected}(tx, account_id)")


class KeyedDigestTests(unittest.TestCase):
    """D17: a stored digest is keyed by the settings' ``SECRET_KEY`` and names its purpose."""

    def test_a_stored_digest_cannot_be_reproduced_without_the_key(self) -> None:
        seen = last_json(
            under_profile_settings(
                """
import hashlib, json
from django.conf import settings
from django.utils.crypto import salted_hmac
from glow_profiles import idempotency

def intent(values, key="fixture-key-1"):
    return {
        "operation": "profile_field",
        "meta": {"idempotency_key": key, "expected_version": 0},
        "policy_version": "catalog.1.1.1.1.1.1.1",
        "field": "orientation",
        "value_ids": values,
        "own_words": None,
        "shown": False,
    }

operation = "profile_field.orientation"
stored = idempotency.digest(operation, intent(["fixture-a"]))
candidates = [["fixture-a"], ["fixture-b"], ["not-stated"], ["fixture-a", "fixture-b"]]
unkeyed = {
    hashlib.sha256(idempotency.canonical(intent(values)).encode()).hexdigest()
    for values in candidates
}
canonical = idempotency.canonical(intent(["fixture-a"]))
print(json.dumps({
    "length": len(stored),
    "hex": all(character in "0123456789abcdef" for character in stored),
    "named": stored == salted_hmac(
        idempotency.SALT_PREFIX + operation, canonical, algorithm="sha256"
    ).hexdigest(),
    "keyed_by_settings": stored == salted_hmac(
        idempotency.SALT_PREFIX + operation,
        canonical,
        secret=settings.SECRET_KEY,
        algorithm="sha256",
    ).hexdigest(),
    "unkeyed_match": stored in unkeyed,
    "another_key": stored == salted_hmac(
        idempotency.SALT_PREFIX + operation,
        canonical,
        secret="synthetic-other-key-not-a-secret",
        algorithm="sha256",
    ).hexdigest(),
    "another_operation": (
        stored == idempotency.digest("profile_field.gender", intent(["fixture-a"]))
    ),
    "key_left_out": (
        stored == idempotency.digest(operation, intent(["fixture-a"], "fixture-key-2"))
    ),
    "sha1_default": (
        stored == salted_hmac(idempotency.SALT_PREFIX + operation, canonical).hexdigest()
    ),
}))
"""
            )
        )
        self.assertEqual(seen["length"], 64)
        self.assertTrue(seen["hex"])
        self.assertTrue(seen["named"])
        self.assertTrue(seen["keyed_by_settings"])
        self.assertFalse(seen["unkeyed_match"])
        self.assertFalse(seen["another_key"])
        self.assertFalse(seen["another_operation"])
        # The record binds every field but the key; the key itself deduplicates.
        self.assertTrue(seen["key_left_out"])
        self.assertFalse(seen["sha1_default"])


if __name__ == "__main__":
    unittest.main()


class BodiesTheParserCannotHoldTests(unittest.TestCase):
    """C2, item 6 (finding 11; DM-55, section 8): a body the parser cannot hold, such as an integer
    too large for its number check or nesting deeper than the parser allows, and a text holding
    U+0000, which the database cannot store, are refused ``invalid_request`` (400) with the
    contract's ``Error``, like any other invalid body. No value is echoed. Each runs through the
    route's own view, with the actor forced (the request is refused before any database read),
    and each body is within the request size limit (16 KiB), so the parser, not the limit,
    decides."""

    def test_each_answers_400_with_the_contracts_error_and_no_value(self) -> None:
        seen = last_json(
            under_profile_settings(
                """
import json
from uuid import uuid4
from rest_framework.test import APIRequestFactory, force_authenticate
from glow_identity.authentication import Actor
from glow_profiles import views

actor = Actor(uuid4(), 1, "active", uuid4(), "valid")


class Signed:
    is_authenticated = True


factory = APIRequestFactory()
from django.conf import settings

digits = "7" * 321
# 10,000 nested arrays, as the parser meets them (its depth is passed long before the body
# ends), and 5,000 closed ones: each body within the request size limit, so the parser decides.
opened = "[" * 10000
closed = "[" * 5000 + "]" * 5000
bodies = {
    "a_321_digit_coordinate": ("NearestAreaView", '{"latitude": %s, "longitude": 1}' % digits),
    "10000_nested_arrays": ("NearestAreaView", '{"latitude": %s' % opened),
    "5000_closed_nested_arrays": (
        "NearestAreaView", '{"latitude": %s, "longitude": 1}' % closed
    ),
    "u0000_in_a_stored_text": (
        "ProfileView",
        json.dumps({
            "operation": "profile",
            "meta": {"idempotency_key": "nul-key", "expected_version": 0},
            "display_name": "Synthetic\\u0000Nul",
            "summary": "A synthetic member.",
        }),
    ),
}
out = {}
limit = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
for case, (view, body) in bodies.items():
    assert len(body.encode("utf-8")) < limit, case
    request = factory.post("/x", data=body, content_type="application/json")
    force_authenticate(request, user=Signed(), token=actor)
    response = views.__dict__[view].as_view()(request)
    response.render()
    text = response.content.decode("utf-8")
    out[case] = {
        "status": response.status_code,
        "type": response["Content-Type"],
        "body": json.loads(text),
        "echo": any(part in text for part in (digits[:40], "[[[", "Synthetic", "Nul", "nul-key")),
    }
print(json.dumps(out))
"""
            )
        )
        self.assertEqual(
            set(seen),
            {
                "a_321_digit_coordinate",
                "10000_nested_arrays",
                "5000_closed_nested_arrays",
                "u0000_in_a_stored_text",
            },
        )
        for case, answer in seen.items():
            with self.subTest(case=case):
                self.assertEqual(answer["status"], 400)
                self.assertTrue(answer["type"].startswith("application/json"))
                self.assertEqual(answer["body"]["code"], "invalid_request")
                self.assertEqual(
                    set(answer["body"]), {"contract_version", "request_id", "code", "retryable"}
                )
                self.assertIs(answer["body"]["retryable"], False)
                self.assertFalse(answer["echo"])
