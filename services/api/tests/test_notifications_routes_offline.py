"""SV4 B1, the parts of F12's surface that need no database (its brief's D16, D18, D19 and D31, with
DM-101's AM1 to AM7).

- **Requests** (D19): the domain's parsers take each ``DeviceIntent`` and ``NotificationIntent`` as
  the production schema decides, and the ``Glow-Installation-Id`` header as the contract's
  ``device_id`` pattern; a body naming an actor, an account or a session is refused like any field
  the DTO does not have.
- **Projections**: each served ``NotificationSettings`` validates as its DTO and inside
  ``AppResponse``, with no token, reference or installation.
- **The mapping is complete** (D19; DM-101's AM6; DM-99's AK2 pattern): every refusal reason the
  ORM adapter can answer, read from its source and from every helper it calls, SV2's included
  (``lock_account``, ``read_account_shared``, ``idempotency.decide``; A2-C1's delta review, F2's
  lesson), and every reason the port's in-memory fixture can answer, is pinned to one code; a
  reason added later fails here until it is mapped.
- **The routes** (D19), in a fresh process under ``tests.discovery_offline_settings`` (Django's
  dummy backend), each request through DRF's request factory with the actor forced as SV1's
  authentication would give it and the persistence replaced by the port's in-memory fixture
  (``NotificationService``): each route answers its DTO for the header's installation, refuses
  what is not its request, answers each refusal with its code (a 401 from inside the command with
  the challenge, AM6), caches nothing, echoes no value and logs codes only; the device route
  refuses without the token store's factory (D16), before any read.
- **The structure** (D18, D19): the three routes and no other, each ``non_atomic_requests`` with
  SV1's authentication only; the token store's ``put`` before the command's transaction; the lock
  order (the account row, the session row ``FOR SHARE``, then the registrations by primary key);
  the digest binding the requesting installation; no account lock but SV2's, no
  ``select_for_update``; the installation read from the header only.

The database cases run on a disposable PostgreSQL in ``proofs/postgres-ordering``'s chat suite,
through the HTTP endpoints with no enclosing transaction. All data is synthetic.
"""

import ast
import importlib
import json
import sys
import unittest
from pathlib import Path
from typing import Any
from uuid import uuid4

from glow_domain import chat
from glow_domain import notifications as n
from glow_notifications import contract
from tests.test_discovery_offline import under_discovery_settings
from tests.test_profiles_offline import last_json

API_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = API_ROOT / "glow_notifications"
ADAPTER = PACKAGE / "persistence.py"
DOMAIN = API_ROOT / "glow_domain" / "notifications.py"
sys.path.insert(0, str(API_ROOT.parents[1] / "packages" / "contracts"))
from runtime import valid  # noqa: E402

INSTALLATION = "4c5d6e7f-8091-4a2b-9c3d-4e5f60718293"
KEY = "synthetic-key-b1"
TOKEN = "SYNTHETIC-FIXTURE-PUSH-TOKEN-offline-b1-NOT-A-REAL-DEVICE-TOKEN"
REGISTER = {
    "operation": "device",
    "meta": {"idempotency_key": KEY, "expected_version": 0},
    "device_id": INSTALLATION,
    "action": "register",
    "provider_token": TOKEN,
}
REVOKE = {**REGISTER, "action": "revoke", "provider_token": None}
SETTINGS = {
    "operation": "notifications",
    "meta": {"idempotency_key": KEY, "expected_version": 1},
    "match_notifications": True,
    "message_notifications": False,
}


def parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def accepts(definition: str, value: object) -> bool:
    parse = n.parse_device_intent if definition == "DeviceIntent" else n.parse_settings_intent
    try:
        parse(json.loads(json.dumps(value)))
    except n.IntentError:
        return False
    return True


# -- requests (D19) ------------------------------------------------------------------------------


class RequestTests(unittest.TestCase):
    def bodies(self) -> list[tuple[str, object]]:
        meta = REGISTER["meta"]
        return [
            ("DeviceIntent", REGISTER),
            ("DeviceIntent", REVOKE),
            ("DeviceIntent", {**REGISTER, "provider_token": None}),
            ("DeviceIntent", {**REVOKE, "provider_token": TOKEN}),
            ("DeviceIntent", {**REGISTER, "provider_token": ""}),
            ("DeviceIntent", {**REGISTER, "provider_token": " \t\n"}),
            ("DeviceIntent", {**REGISTER, "provider_token": "x" * 4096}),
            ("DeviceIntent", {**REGISTER, "provider_token": "x" * 4097}),
            ("DeviceIntent", {**REGISTER, "provider_token": "a\ud800b"}),
            ("DeviceIntent", {**REGISTER, "provider_token": "a\x00b"}),
            ("DeviceIntent", {**REGISTER, "device_id": INSTALLATION.upper()}),
            ("DeviceIntent", {**REGISTER, "device_id": INSTALLATION + "\n"}),
            ("DeviceIntent", {**REGISTER, "device_id": "not-an-installation"}),
            ("DeviceIntent", {**REGISTER, "action": "rotate"}),
            ("DeviceIntent", {**REGISTER, "operation": "notifications"}),
            ("DeviceIntent", {**REGISTER, "platform": "ios"}),
            ("DeviceIntent", {k: v for k, v in REGISTER.items() if k != "device_id"}),
            ("DeviceIntent", {**REGISTER, "meta": {"idempotency_key": KEY}}),
            ("DeviceIntent", {**REGISTER, "meta": {**meta, "expected_version": -1}}),
            ("DeviceIntent", {**REGISTER, "meta": {**meta, "expected_version": 1.5}}),
            ("DeviceIntent", {**REGISTER, "meta": {**meta, "expected_version": True}}),
            ("DeviceIntent", {**REGISTER, "meta": {**meta, "expected_version": 2**53}}),
            ("DeviceIntent", {**REGISTER, "meta": {**meta, "idempotency_key": ""}}),
            ("DeviceIntent", {**REGISTER, "meta": {**meta, "idempotency_key": "-k"}}),
            ("DeviceIntent", {**REGISTER, "meta": {**meta, "idempotency_key": "k" * 101}}),
            ("NotificationIntent", SETTINGS),
            ("NotificationIntent", {**SETTINGS, "match_notifications": 1}),
            ("NotificationIntent", {**SETTINGS, "device_id": INSTALLATION}),
            ("NotificationIntent", {k: v for k, v in SETTINGS.items() if k != "meta"}),
            ("NotificationIntent", {**SETTINGS, "operation": "device"}),
        ]

    def test_each_intent_is_parsed_as_the_contract_decides(self) -> None:
        for definition, body in self.bodies():
            with self.subTest(definition=definition, body=json.dumps(body)[:80]):
                self.assertEqual(accepts(definition, body), valid("production", definition, body))
        self.assertTrue(accepts("DeviceIntent", REGISTER))
        self.assertTrue(accepts("DeviceIntent", REVOKE))
        self.assertTrue(accepts("NotificationIntent", SETTINGS))

    def test_a_body_naming_an_actor_or_its_installation_is_refused(self) -> None:
        # The actor is SV1's session, the installation the header's: never a field of the intent.
        for definition, body in (("DeviceIntent", REGISTER), ("NotificationIntent", SETTINGS)):
            fields = ["actor_id", "account_id", "session_id", "installation_id"]
            if definition == "NotificationIntent":
                fields.append("device_id")
            for field in fields:
                with self.subTest(definition=definition, field=field):
                    changed = {**body, field: str(uuid4())}
                    self.assertFalse(accepts(definition, changed))
                    self.assertFalse(valid("production", definition, changed))

    def test_the_installation_header_is_the_contracts_device_id(self) -> None:
        pattern_body = {**REGISTER}
        for value in (INSTALLATION, INSTALLATION.upper(), INSTALLATION + "\n", "x", "", None, 7):
            with self.subTest(value=value):
                try:
                    n.parse_installation(value)
                    ours = True
                except n.IntentError:
                    ours = False
                theirs = valid("production", "DeviceIntent", {**pattern_body, "device_id": value})
                self.assertEqual(ours, theirs)
        self.assertEqual(str(n.parse_installation(INSTALLATION)), INSTALLATION)

    def test_a_body_that_is_not_a_json_object_is_refused(self) -> None:
        for raw in (b"", b"{", b"[]", b"null", b'"x"', b"\xff", b'{"a": NaN}', b"[" * 100_000):
            with self.subTest(raw=raw[:10]):
                with self.assertRaises(contract.Invalid):
                    contract.parse(raw)
        self.assertEqual(contract.parse(json.dumps(REGISTER).encode()), REGISTER)


# -- projections ---------------------------------------------------------------------------------


def envelope(data: dict[str, object]) -> dict[str, object]:
    return {
        "contract_version": "gapp-api-v1",
        "request_id": str(uuid4()),
        "data": data,
    }


class ProjectionTests(unittest.TestCase):
    def test_the_settings_are_the_contracts_dto_and_nothing_more(self) -> None:
        for view in (
            n.NotificationSettingsView(1, False, False, "active"),
            n.NotificationSettingsView(9, True, False, "revoked"),
        ):
            with self.subTest(view=view):
                served = contract.settings(view)
                self.assertTrue(valid("production", "NotificationSettings", served))
                self.assertTrue(valid("production", "AppResponse", envelope(served)))
                self.assertEqual(
                    set(served),
                    {
                        "kind",
                        "version",
                        "match_notifications",
                        "message_notifications",
                        "device_state",
                    },
                )
        self.assertFalse(
            valid(
                "production",
                "NotificationSettings",
                {**contract.settings(n.NotificationSettingsView(1, 0, 0, "active")), "x": 1},  # type: ignore[arg-type]
            )
        )


# -- the mapping is complete (D19; AM6; DM-99's AK2 pattern) ------------------------------------

TX = API_ROOT / "glow_profiles" / "tx.py"
IDEMPOTENCY = API_ROOT / "glow_profiles" / "idempotency.py"
# The modules whose functions the walk follows into, by the module the adapter imports them from.
FOLLOWED = {"glow_profiles.tx": TX, "glow_profiles.idempotency": IDEMPOTENCY}
# A reason passed through from a caught refusal or a transaction's result: the walk reads the
# reasons where they are raised instead.
PASSED_THROUGH = {"refused.reason", "rollback.reason", "reason"}

# Every reason ``OrmNotificationPersistence``'s read, device command and settings command can answer
# refused, as their routes serve it (``contract.refusal``).
ADAPTER_SERVED = {
    contract.NO_TOKEN_STORE: ("provider_unavailable", False),
    n.INTENT_INVALID: ("invalid_request", False),
    n.WRONG_INSTALLATION: ("forbidden", False),
    n.TOKEN_STORE_REFUSED: ("provider_unavailable", True),
    "account_missing": ("unauthenticated", False),
    chat.ACCOUNT_NOT_ACTIVE: ("unauthenticated", False),
    contract.SESSION_ROW_MISSING: ("unauthenticated", False),
    n.SESSION_NOT_OWNER: ("unauthenticated", False),
    chat.SESSION_NOT_VALID: ("unauthenticated", False),
    chat.SESSION_EXPIRED: ("unauthenticated", False),
    chat.SESSION_EPOCH_STALE: ("unauthenticated", False),
    chat.IDEMPOTENCY_CONFLICT: ("idempotency_conflict", False),
    contract.TRANSFER_CHANGED: ("state_conflict", False),
    contract.REGISTRATION_MISSING: ("state_conflict", False),
    n.STALE_VERSION: ("stale_version", False),
    n.TRANSITION_FORBIDDEN: ("state_conflict", False),
    n.REGISTRATION_BOUND: ("state_conflict", False),
    n.REGISTRATION_NOT_ACTIVE: ("state_conflict", False),
}
# Every reason the port's in-memory fixture (``NotificationService``) can answer refused, as the
# routes serve it over the fixture.
FIXTURE_SERVED = {
    chat.SESSION_MISSING: ("unauthenticated", False),
    n.SESSION_NOT_OWNER: ("unauthenticated", False),
    chat.ACCOUNT_MISSING: ("unauthenticated", False),
    chat.ACCOUNT_NOT_ACTIVE: ("unauthenticated", False),
    chat.SESSION_NOT_VALID: ("unauthenticated", False),
    chat.SESSION_EXPIRED: ("unauthenticated", False),
    chat.SESSION_EPOCH_STALE: ("unauthenticated", False),
    n.INTENT_INVALID: ("invalid_request", False),
    n.WRONG_INSTALLATION: ("forbidden", False),
    chat.IDEMPOTENCY_CONFLICT: ("idempotency_conflict", False),
    n.FIXTURE_CAPACITY: ("state_conflict", False),
    n.STALE_VERSION: ("stale_version", False),
    n.TRANSITION_FORBIDDEN: ("state_conflict", False),
    n.TOKEN_STORE_REFUSED: ("provider_unavailable", True),
    n.REGISTRATION_BOUND: ("state_conflict", False),
    n.REGISTRATION_NOT_ACTIVE: ("state_conflict", False),
}


class _Module:
    def __init__(self, path: Path, source: str | None = None) -> None:
        self.path = path
        self.tree = ast.parse(source if source is not None else path.read_text(encoding="utf-8"))
        self.functions = {
            node.name: node for node in self.tree.body if isinstance(node, ast.FunctionDef)
        }
        self.classes = {
            node.name: node for node in self.tree.body if isinstance(node, ast.ClassDef)
        }
        self.constants = {
            target.id: node.value.value
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        # The names this module imports: ``from X import a as b`` is b -> (X, a), a relative
        # ``from . import a`` or ``from .m import a`` read from the module's own package.
        package = path.parent.name
        self.names: dict[str, tuple[str, str]] = {}
        for node in self.tree.body:
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level:
                base = package + (f".{node.module}" if node.module else "")
            elif node.module:
                base = node.module
            else:
                continue
            for alias in node.names:
                self.names[alias.asname or alias.name] = (base, alias.name)


class _Reasons:
    """The refusal reasons a set of entry points can answer, read from the source.

    From each entry point it reads every ``raise _Refused(X)`` (the adapter's), every
    ``raise Refused(code, X)`` (SV2's helpers'), every ``CommandResult("refused", X)`` and
    ``ReadResult("refused", X)``, and a reason a function returns into one of those (the fixture's
    ``_session_refusal``), in the function and in every function it calls, followed into the
    callees' own calls: the class's methods called as ``self.<name>``, the module's functions, and
    the functions of SV2's ``glow_profiles.tx`` and ``glow_profiles.idempotency`` the module imports
    (by name or through the module), with their own helpers. ``X`` must be a constant, a module
    constant, a ``chat.`` or ``n.`` name, a name imported from ``glow_notifications.contract``, or
    a pass-through of a refusal caught or a transaction's result (``PASSED_THROUGH``), whose
    reasons are read where they are raised; any other form is recorded as unresolved, and fails.
    Not seen: a reason raised by a function of another module, one built at runtime, a database
    error (served ``state_conflict``, never a reason), and the views' own refusals (the header,
    the body, the method; pinned by ``RouteTests``)."""

    def __init__(self, sources: dict[Path, str] | None = None) -> None:
        self.sources = sources or {}
        self.modules: dict[Path, _Module] = {}
        self.unresolved: list[str] = []
        self.seen: set[tuple[Path, str]] = set()

    def module(self, path: Path) -> _Module:
        if path not in self.modules:
            self.modules[path] = _Module(path, self.sources.get(path))
        return self.modules[path]

    def _value(self, module: _Module, node: ast.expr, where: str) -> set[str]:
        text = ast.unparse(node)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value} if node.value else set()
        if text in PASSED_THROUGH:
            return set()
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            imported = module.names.get(node.value.id)
            if imported is not None:
                found = importlib.import_module(f"{imported[0]}.{imported[1]}")
                return {getattr(found, node.attr)}
        if isinstance(node, ast.Name):
            if node.id in module.constants:
                return {module.constants[node.id]}
            imported = module.names.get(node.id)
            if imported is not None and imported[0].startswith(("glow_domain", "glow_notif")):
                return {getattr(importlib.import_module(imported[0]), imported[1])}
        self.unresolved.append(f"{where}: {text}")
        return set()

    def collect(
        self, path: Path, function: ast.FunctionDef, klass: ast.ClassDef | None
    ) -> set[str]:
        key = (path, f"{klass.name if klass else ''}.{function.name}")
        if key in self.seen:
            return set()
        self.seen.add(key)
        module = self.module(path)
        found: set[str] = set()
        returned_from = {
            node.targets[0].id: ast.unparse(node.value.func)
            for node in ast.walk(function)
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
        }
        for node in ast.walk(function):
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                raised = ast.unparse(node.exc.func)
                if raised == "_Refused":
                    found |= self._value(module, node.exc.args[0], function.name)
                elif raised == "Refused":
                    found |= self._value(module, node.exc.args[1], function.name)
            if not isinstance(node, ast.Call):
                continue
            called = ast.unparse(node.func)
            if called.endswith(("CommandResult", "ReadResult")) and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and first.value == "refused":
                    reason = node.args[1]
                    if isinstance(reason, ast.Name) and reason.id in returned_from:
                        found |= self._returns(path, returned_from[reason.id], klass)
                    else:
                        found |= self._value(module, reason, function.name)
            target = self._callee(path, called, klass)
            if target is not None:
                found |= self.collect(*target)
        return found

    def _returns(self, path: Path, called: str, klass: ast.ClassDef | None) -> set[str]:
        target = self._callee(path, called, klass)
        assert target is not None, called
        module = self.module(target[0])
        values: set[str] = set()
        for node in ast.walk(target[1]):
            if isinstance(node, ast.Return) and node.value is not None:
                values |= self._value(module, node.value, target[1].name)
        return values

    def _callee(
        self, path: Path, called: str, klass: ast.ClassDef | None
    ) -> tuple[Path, ast.FunctionDef, ast.ClassDef | None] | None:
        module = self.module(path)
        if called.startswith("self.") and klass is not None:
            name = called.removeprefix("self.")
            for node in klass.body:
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    return path, node, klass
            return None
        if called in module.functions:
            return path, module.functions[called], None
        head, _, tail = called.partition(".")
        imported = module.names.get(head)
        if imported is None:
            return None
        if not tail and imported[0] in FOLLOWED:
            other = self.module(FOLLOWED[imported[0]])
            if imported[1] in other.functions:
                return FOLLOWED[imported[0]], other.functions[imported[1]], None
            return None
        dotted = f"{imported[0]}.{imported[1]}"
        if tail and dotted in FOLLOWED and "." not in tail:
            other = self.module(FOLLOWED[dotted])
            if tail in other.functions:
                return FOLLOWED[dotted], other.functions[tail], None
        return None

    def entry_points(self, path: Path, klass_name: str, names: tuple[str, ...]) -> set[str]:
        klass = self.module(path).classes[klass_name]
        found: set[str] = set()
        for node in klass.body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                found |= self.collect(path, node, klass)
        return found


PORT = ("read", "device", "settings")


class MappingCompletenessTests(unittest.TestCase):
    """DM-99's AK2 pattern, for D19 (AM6): every refusal reason the ORM adapter and the port's
    fixture can answer is pinned to the code and retryability its route serves; a reason added
    later, in the adapter or in any helper it calls, fails here until it is mapped."""

    def test_every_reason_the_adapter_can_answer_is_pinned(self) -> None:
        reading = _Reasons()
        found = reading.entry_points(ADAPTER, "OrmNotificationPersistence", PORT)
        self.assertEqual(reading.unresolved, [])
        self.assertEqual(found, set(ADAPTER_SERVED))
        for reason, expected in ADAPTER_SERVED.items():
            with self.subTest(reason=reason):
                self.assertEqual(contract.refusal("refused", reason), expected)

    def test_every_reason_the_fixture_can_answer_is_pinned(self) -> None:
        reading = _Reasons()
        found = reading.entry_points(DOMAIN, "NotificationService", PORT)
        self.assertEqual(reading.unresolved, [])
        self.assertEqual(found, set(FIXTURE_SERVED))
        for reason, expected in FIXTURE_SERVED.items():
            with self.subTest(reason=reason):
                self.assertEqual(contract.refusal("refused", reason), expected)

    def test_the_table_holds_no_other_reason(self) -> None:
        self.assertEqual(
            set(contract.REFUSALS),
            set(ADAPTER_SERVED) | set(FIXTURE_SERVED) | {contract.REGISTRATION_ABSENT},
        )
        self.assertEqual(contract.refusal("absent", ""), ("not_found", False))
        self.assertEqual(contract.refusal("deadlock", "DeadlockDetected"), ("state_conflict", True))
        self.assertEqual(contract.refusal("error", "transaction_open"), ("state_conflict", False))
        self.assertEqual(contract.refusal("refused", "no_such_reason"), ("state_conflict", False))
        codes = {
            "invalid_request",
            "unauthenticated",
            "forbidden",
            "not_found",
            "state_conflict",
            "stale_version",
            "idempotency_conflict",
            "provider_unavailable",
        }
        self.assertLessEqual({code for code, _ in contract.REFUSALS.values()}, codes)

    def test_each_session_reason_is_unauthenticated(self) -> None:
        # D19 (AM6): these routes concern only the member's own account and installation.
        for reason in (
            chat.SESSION_MISSING,
            n.SESSION_NOT_OWNER,
            chat.ACCOUNT_MISSING,
            "account_missing",
            chat.ACCOUNT_NOT_ACTIVE,
            chat.SESSION_NOT_VALID,
            chat.SESSION_EXPIRED,
            chat.SESSION_EPOCH_STALE,
            contract.SESSION_ROW_MISSING,
        ):
            with self.subTest(reason=reason):
                self.assertEqual(contract.refusal("refused", reason), ("unauthenticated", False))

    def test_a_reason_added_in_the_adapter_or_a_helper_is_found(self) -> None:
        # The reading itself, on modified copies: a raise in one of the adapter's helpers, and one
        # in SV2's lock helper the adapter calls (F2's lesson: a helper's raises are read).
        source = ADAPTER.read_text(encoding="utf-8")
        marker = "        account_id, state, expires_at, session_epoch = session\n"
        self.assertEqual(source.count(marker), 1)
        planted = source.replace(marker, marker + "        raise _Refused(n.FIXTURE_CAPACITY)\n")
        found = _Reasons({ADAPTER: planted}).entry_points(
            ADAPTER, "OrmNotificationPersistence", PORT
        )
        self.assertEqual(found - set(ADAPTER_SERVED), {n.FIXTURE_CAPACITY})
        helper = TX.read_text(encoding="utf-8")
        marker = '    signal(tx.probe, "after_first_lock")\n    if account.state != "active":\n'
        self.assertEqual(helper.count(marker), 1)
        planted = helper.replace(
            marker,
            marker.replace("    signal", '    raise Refused(NOT_FOUND, "planted")\n    signal'),
        )
        found = _Reasons({TX: planted}).entry_points(ADAPTER, "OrmNotificationPersistence", PORT)
        self.assertEqual(found - set(ADAPTER_SERVED), {"planted"})


# -- the routes, in a fresh process (D19) ----------------------------------------------------------

ROUTES = r"""
import json, logging, sys, types
from unittest import mock
from uuid import UUID, uuid4
sys.path.insert(0, "../../packages/contracts")
from django.test import override_settings
from rest_framework.test import APIRequestFactory, force_authenticate
from glow_domain import notifications as n
from glow_domain.notification_fixtures import notification_fixture, synthetic_token
from glow_identity.authentication import Actor
from glow_notifications import providers, views
from runtime import valid

records = []


class Capture(logging.Handler):
    def emit(self, record):
        records.append([record.name, record.getMessage()])


root = logging.getLogger()
root.addHandler(Capture(level=logging.DEBUG))
root.setLevel(logging.DEBUG)

fx = notification_fixture("test")
account = fx.world.add_account()
session = fx.world.open_session(account)
actor = Actor(account, 1, "active", session, "valid")
INSTALLATION = str(uuid4())
OTHER = str(uuid4())
TOKEN = synthetic_token("ROUTES-CANARY-b1")
KEY = "synthetic-key-b1"
VALUES = (INSTALLATION, OTHER, TOKEN, str(account), str(session), KEY)


class Signed:
    is_authenticated = True


factory = APIRequestFactory()


def send(view, body, *, installation=INSTALLATION, method="post", content_type="application/json",
         signed=True, path="/x", headers=None):
    data = body if body is None or isinstance(body, (str, bytes)) else json.dumps(body)
    extra = dict(headers or {})
    if installation is not None:
        extra["HTTP_GLOW_INSTALLATION_ID"] = installation
    request = factory.generic(method.upper(), path, data=data or "", content_type=content_type,
                              **extra)
    if signed:
        force_authenticate(request, user=Signed(), token=actor)
    response = view.as_view()(request)
    response.render()
    return response


def answer(response):
    text = response.content.decode("utf-8")
    body = json.loads(text)
    served = (body.get("data") or {}) if isinstance(body, dict) else {}
    return {
        "status": response.status_code,
        "cache": response.get("Cache-Control"),
        "challenge": response.get("WWW-Authenticate"),
        "code": body.get("code"),
        "retryable": body.get("retryable"),
        "kind": served.get("kind"),
        "data": served or None,
        "valid": valid("production", "AppResponse" if "data" in body else "Error", body),
        "echo": any(value in text for value in VALUES),
    }


def device(action, version, key, *, token=TOKEN, device_id=INSTALLATION):
    return {"operation": "device", "meta": {"idempotency_key": key, "expected_version": version},
            "device_id": device_id, "action": action,
            "provider_token": token if action == "register" else None}


def notifications(match, message, version, key):
    return {"operation": "notifications",
            "meta": {"idempotency_key": key, "expected_version": version},
            "match_notifications": match, "message_notifications": message}


made = []


def persistence(**kwargs):
    made.append(sorted(kwargs))
    return fx.service


store = object()
module = types.ModuleType("synthetic_store")
module.make = lambda: store
module.transport = lambda: "a transport"
sys.modules["synthetic_store"] = module

cases = {}
# Without the token store's factory, the device route refuses before any read (D16): the real
# adapter, with no store, never reaches a transaction or a connection.
cases["no_store"] = answer(send(views.DeviceView, device("register", 0, "k0")))
cases["no_store_hook"] = [providers.token_store() is None, providers.push_transport() is None]
with override_settings(GLOW_NOTIFICATIONS_TOKEN_STORE="synthetic_store.make",
                       GLOW_NOTIFICATIONS_PUSH_TRANSPORT="synthetic_store.transport"):
    cases["hooks"] = [providers.token_store() is store,
                      providers.push_transport() == "a transport"]
    with mock.patch.object(views, "OrmNotificationPersistence", persistence):
        cases["register"] = answer(send(views.DeviceView, device("register", 0, "k1")))
        cases["read"] = answer(send(views.NotificationsView, None, method="get"))
        cases["settings"] = answer(send(views.SettingsView, notifications(True, False, 1, "k2")))
        cases["replay"] = answer(send(views.DeviceView, device("register", 0, "k1")))
        cases["conflict"] = answer(send(views.DeviceView,
                                        device("register", 0, "k1", token=TOKEN + "-other")))
        cases["stale"] = answer(send(views.DeviceView, device("register", 9, "k3")))
        cases["forbidden"] = answer(send(views.DeviceView,
                                         device("register", 0, "k4", device_id=OTHER)))
        cases["absent"] = answer(send(views.NotificationsView, None, method="get",
                                      installation=OTHER))
        cases["revoke_none"] = answer(send(views.DeviceView,
                                           device("revoke", 0, "k5", device_id=OTHER),
                                           installation=OTHER))
        cases["settings_none"] = answer(send(views.SettingsView,
                                             notifications(True, True, 0, "k6"),
                                             installation=OTHER))
        fx.tokens.refuse_next_put()
        cases["store_refused"] = answer(send(views.DeviceView,
                                             device("register", 0, "k7", device_id=OTHER),
                                             installation=OTHER))
        cases["intent_invalid"] = answer(send(views.DeviceView,
                                              {**device("register", 0, "k8"), "x": 1}))
        for name, header in (("missing", None), ("upper", INSTALLATION.upper()),
                             ("not_uuid", "not-an-installation"),
                             ("two", INSTALLATION + ", " + INSTALLATION)):
            cases[f"header:{name}"] = [
                answer(send(views.DeviceView, device("revoke", 1, "k9"), installation=header)),
                answer(send(views.SettingsView, notifications(True, True, 1, "k9"),
                            installation=header)),
                answer(send(views.NotificationsView, None, method="get", installation=header)),
            ]
        for name, view, body in (("device", views.DeviceView, device("revoke", 2, "k10")),
                                 ("settings", views.SettingsView,
                                  notifications(False, False, 2, "k10"))):
            cases[f"{name}:query"] = answer(send(view, body, path="/x?a=1"))
            cases[f"{name}:type"] = answer(send(view, body, content_type="text/plain"))
            cases[f"{name}:not_json"] = answer(send(view, "{"))
            cases[f"{name}:not_object"] = answer(send(view, "[]"))
            cases[f"{name}:get"] = answer(send(view, None, method="get"))
            cases[f"{name}:put"] = answer(send(view, body, method="put"))
            cases[f"{name}:unsigned"] = answer(send(view, body, signed=False))
            cases[f"{name}:format"] = answer(send(view, body, path="/x?format=xml"))
        # Accept is not read: a refusal by the command's state is the contract's Error in JSON.
        cases["device:html"] = answer(send(views.DeviceView, device("revoke", 99, "k10"),
                                           headers={"HTTP_ACCEPT": "text/html"}))
        cases["settings:html"] = answer(send(views.SettingsView,
                                             notifications(False, False, 99, "k10"),
                                             headers={"HTTP_ACCEPT": "text/html"}))
        cases["read:html"] = answer(send(views.NotificationsView, None, method="get",
                                         headers={"HTTP_ACCEPT": "text/html"}))
        cases["read:body"] = answer(send(views.NotificationsView, json.dumps({"x": 1}),
                                         method="get"))
        cases["read:query"] = answer(send(views.NotificationsView, None, method="get",
                                          path="/x?a=1"))
        cases["read:post"] = answer(send(views.NotificationsView, None))
        cases["read:unsigned"] = answer(send(views.NotificationsView, None, method="get",
                                             signed=False))
        # The bound (D25): ten active registrations of the account (the first one's and nine
        # more), then an eleventh refused.
        for index in range(9):
            installation = str(uuid4())
            send(views.DeviceView, device("register", 0, f"bound-{index}",
                                          device_id=installation), installation=installation)
        eleventh = str(uuid4())
        cases["bound"] = answer(send(views.DeviceView,
                                     device("register", 0, "bound-11", device_id=eleventh),
                                     installation=eleventh))
        # A session that ended once the command holds its locks: 401 with the challenge (AM6).
        fx.world.end_session(session)
        cases["ended"] = [
            answer(send(views.DeviceView, device("revoke", 2, "k11"))),
            answer(send(views.SettingsView, notifications(True, True, 2, "k12"))),
            answer(send(views.NotificationsView, None, method="get")),
        ]
cases["made"] = made
print(json.dumps({
    "cases": cases,
    "records": records,
    "record_echo": any(value in line for _, line in records for value in VALUES),
}))
"""


def routes() -> dict[str, object]:
    return last_json(under_discovery_settings(ROUTES))


class RouteTests(unittest.TestCase):
    seen: dict[str, object] = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls.seen = routes()
        cls.cases = cls.seen["cases"]

    def case(self, name: str) -> Any:
        return self.cases[name]  # type: ignore[index]

    def assert_served(self, found: dict[str, object], data: dict[str, object]) -> None:
        self.assertEqual(
            (found["status"], found["kind"], found["valid"], found["echo"]),
            (200, "notifications", True, False),
            found,
        )
        self.assertEqual(found["data"], data)
        self.assertEqual(found["cache"], "no-store")

    def assert_refused(
        self, found: dict[str, object], status: int, code: str, *, retryable: bool = False
    ) -> None:
        self.assertEqual(
            (found["status"], found["code"], found["valid"], found["echo"], found["retryable"]),
            (status, code, True, False, retryable),
            found,
        )
        self.assertEqual(found["cache"], "no-store")
        self.assertEqual(found["challenge"], "Bearer" if status == 401 else None)

    @staticmethod
    def settings(version: int, state: str = "active", match: bool = False) -> dict[str, object]:
        return {
            "kind": "notifications",
            "version": version,
            "match_notifications": match,
            "message_notifications": False,
            "device_state": state,
        }

    def test_each_route_answers_its_dto_for_the_headers_installation(self) -> None:
        self.assert_served(self.case("register"), self.settings(1))
        self.assert_served(self.case("read"), self.settings(1))
        self.assert_served(self.case("settings"), self.settings(2, match=True))
        self.assert_served(self.case("replay"), self.settings(2, match=True))

    def test_each_refusal_answers_its_code(self) -> None:
        self.assert_refused(self.case("conflict"), 409, "idempotency_conflict")
        self.assert_refused(self.case("stale"), 409, "stale_version")
        self.assert_refused(self.case("forbidden"), 403, "forbidden")
        self.assert_refused(self.case("absent"), 404, "not_found")
        self.assert_refused(self.case("revoke_none"), 409, "state_conflict")
        self.assert_refused(self.case("settings_none"), 409, "state_conflict")
        self.assert_refused(self.case("store_refused"), 503, "provider_unavailable", retryable=True)
        self.assert_refused(self.case("intent_invalid"), 400, "invalid_request")
        self.assert_refused(self.case("bound"), 409, "state_conflict")

    def test_a_session_ended_in_the_command_is_unauthenticated_with_the_challenge(self) -> None:
        # AM6: a 401 from inside the command carries WWW-Authenticate, as the door's does.
        for found in self.case("ended"):
            with self.subTest(found=found["code"]):
                self.assert_refused(found, 401, "unauthenticated")

    def test_the_installation_comes_from_the_header_only(self) -> None:
        for name in ("missing", "upper", "not_uuid", "two"):
            for found in self.case(f"header:{name}"):
                with self.subTest(header=name):
                    self.assert_refused(found, 400, "invalid_request")

    def test_each_route_refuses_what_is_not_its_request(self) -> None:
        for name in ("device", "settings"):
            with self.subTest(route=name):
                for kind in ("query", "type", "not_json", "not_object", "format"):
                    self.assert_refused(self.case(f"{name}:{kind}"), 400, "invalid_request")
                for kind in ("get", "put"):
                    self.assert_refused(self.case(f"{name}:{kind}"), 405, "invalid_request")
                self.assert_refused(self.case(f"{name}:unsigned"), 401, "unauthenticated")
                # Accept is not read (A2-C1's negotiation): the state's refusal, in JSON.
                self.assert_refused(self.case(f"{name}:html"), 409, "stale_version")
        self.assert_refused(self.case("read:body"), 400, "invalid_request")
        self.assert_refused(self.case("read:query"), 400, "invalid_request")
        self.assert_refused(self.case("read:post"), 405, "invalid_request")
        self.assert_refused(self.case("read:unsigned"), 401, "unauthenticated")
        self.assert_served(self.case("read:html"), self.settings(2, match=True))

    def test_the_device_route_refuses_without_the_token_stores_factory(self) -> None:
        # D16 (AM1): no factory named, no store: provider_unavailable, before any read or write.
        self.assert_refused(self.case("no_store"), 503, "provider_unavailable")
        self.assertEqual(self.case("no_store_hook"), [True, True])
        self.assertEqual(self.case("hooks"), [True, True])

    def test_only_the_device_route_takes_the_token_store(self) -> None:
        made = self.case("made")
        self.assertEqual(made[0], ["tokens"])  # the register
        self.assertEqual(made[1], [])  # the read
        self.assertEqual(made[2], [])  # the settings
        self.assertEqual({tuple(kwargs) for kwargs in made}, {("tokens",), ()})

    def test_the_routes_log_codes_only(self) -> None:
        self.assertFalse(self.seen["record_echo"])
        mine = [line for name, line in self.seen["records"] if name == "glow_notifications.views"]
        self.assertTrue(mine)
        for line in mine:
            with self.subTest(line=line):
                self.assertRegex(line, r"^notifications route refused: [a-z_]+$")


# -- the structure (D18, D19) ------------------------------------------------------------------


def _function(tree: ast.Module, klass: str, name: str) -> ast.FunctionDef:
    found = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == klass
    )
    return next(n for n in found.body if isinstance(n, ast.FunctionDef) and n.name == name)


def _called_lines(function: ast.AST) -> list[tuple[int, str]]:
    return sorted(
        (node.lineno, ast.unparse(node.func))
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
    )


def _first(calls: list[tuple[int, str]], name: str, after: int = 0) -> int:
    return next(line for line, called in calls if called == name and line > after)


class StructureTests(unittest.TestCase):
    def test_the_three_routes_and_no_other(self) -> None:
        seen = last_json(
            under_discovery_settings(
                "import json\n"
                "from glow_notifications import urls, views\n"
                "from glow_identity.authentication import GlowActorAuthentication\n"
                "from rest_framework.permissions import IsAuthenticated\n"
                "print(json.dumps([[str(p.pattern), p.callback.view_class.__name__,"
                " sorted(getattr(p.callback, '_non_atomic_requests', ())),"
                " p.callback.view_class.authentication_classes == [GlowActorAuthentication],"
                " p.callback.view_class.permission_classes == [IsAuthenticated],"
                " p.callback.view_class.content_negotiation_class is views.JsonOnlyNegotiation,"
                " p.callback.view_class.http_method_names]"
                " for p in urls.urlpatterns]))\n"
            )
        )
        self.assertEqual(
            seen,
            [
                [
                    "api/v1/notifications",
                    "NotificationsView",
                    ["default"],
                    True,
                    True,
                    True,
                    ["get"],
                ],
                [
                    "api/v1/notifications/device",
                    "DeviceView",
                    ["default"],
                    True,
                    True,
                    True,
                    ["post"],
                ],
                [
                    "api/v1/notifications/settings",
                    "SettingsView",
                    ["default"],
                    True,
                    True,
                    True,
                    ["post"],
                ],
            ],
        )

    def test_the_store_takes_the_token_before_the_commands_transaction(self) -> None:
        # AM4: the put runs before the transaction, never inside it.
        tree = parsed(ADAPTER)
        command = _function(tree, "OrmNotificationPersistence", "device")
        calls = _called_lines(command)
        self.assertLess(_first(calls, "self._tokens.put"), _first(calls, "self._run"))
        # In the command's own body: never in a function or a lambda it could hand to the
        # transaction, which a line order alone would not show.
        for node in ast.walk(command):
            if node is not command and isinstance(node, ast.FunctionDef | ast.Lambda):
                with self.subTest(nested=node.lineno):
                    self.assertNotIn(".put(", ast.unparse(node))
        for name in ("_device", "_register", "_revoke", "settings", "read", "_run"):
            source = ast.unparse(_function(tree, "OrmNotificationPersistence", name))
            with self.subTest(function=name):
                self.assertNotIn(".put(", source)
        device = ast.unparse(_function(tree, "OrmNotificationPersistence", "device"))
        self.assertIn("if fresh is not None and (done is None or not done.saved):", device)
        self.assertIn("self._park(fresh)", device)

    def test_the_lock_order_is_the_account_the_session_then_the_registrations(self) -> None:
        tree = parsed(ADAPTER)
        calls = _called_lines(_function(tree, "OrmNotificationPersistence", "_device"))
        pre = _first(calls, "_holder")
        account = _first(calls, "self._lock_own_account")
        session = _first(calls, "self._lock_session")
        check = _first(calls, "self._check_session")
        decide = _first(calls, "self._decide")
        again = _first(calls, "_holder", after=decide)
        registrations = _first(calls, "self._lock_registrations")
        self.assertEqual(
            sorted([pre, account, session, check, decide, again, registrations]),
            [pre, account, session, check, decide, again, registrations],
        )
        self.assertLess(_first(calls, "self._lock_other_account"), session)
        body = next(
            node
            for node in ast.walk(_function(tree, "OrmNotificationPersistence", "settings"))
            if isinstance(node, ast.FunctionDef) and node.name == "body"
        )
        calls = _called_lines(body)
        order = [
            _first(calls, name)
            for name in (
                "self._lock_own_account",
                "self._lock_session",
                "self._check_session",
                "self._decide",
                "self._lock_registrations",
            )
        ]
        self.assertEqual(order, sorted(order))
        body = next(
            node
            for node in ast.walk(_function(tree, "OrmNotificationPersistence", "read"))
            if isinstance(node, ast.FunctionDef) and node.name == "body"
        )
        calls = _called_lines(body)
        order = [
            _first(calls, name)
            for name in ("read_account_shared", "self._lock_session", "self._check_session")
        ]
        self.assertEqual(order, sorted(order))

    def test_the_locks_are_sv2s_and_two_literal_statements(self) -> None:
        source = ADAPTER.read_text(encoding="utf-8")
        self.assertNotIn("select_for_update", source)
        self.assertNotIn("lock_account_any_state", source)
        self.assertNotIn("glow_persistence_appaccount", source)
        tree = parsed(ADAPTER)
        statements = {
            target.id: node.value.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and " FOR " in node.value.value
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        self.assertEqual(set(statements), {"SESSION_SHARED", "REGISTRATIONS_FOR_UPDATE"})
        self.assertTrue(statements["SESSION_SHARED"].endswith("WHERE id = %s FOR SHARE"))
        self.assertIn("FROM glow_persistence_accountsession", statements["SESSION_SHARED"])
        self.assertTrue(
            statements["REGISTRATIONS_FOR_UPDATE"].endswith(
                "WHERE id = ANY(%s) ORDER BY id FOR UPDATE"
            )
        )
        self.assertIn(
            "FROM glow_persistence_deviceregistration", statements["REGISTRATIONS_FOR_UPDATE"]
        )

    def test_the_digest_binds_the_requesting_installation(self) -> None:
        # AM5: the canonical intent and the header's installation, under SV2's keyed digest.
        tree = parsed(ADAPTER)
        digest = next(
            n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_digest"
        )
        self.assertEqual(
            ast.unparse(digest.body[-1]),
            "return idempotency.digest(operation, {**intent, INSTALLATION_FIELD: "
            "str(caller.device_id)})",
        )
        for name in ("device", "settings"):
            source = ast.unparse(_function(tree, "OrmNotificationPersistence", name))
            with self.subTest(command=name):
                self.assertIn("_digest(", source)
                self.assertIn("intent, caller)", source)

    def test_the_views_read_the_installation_from_the_header_only(self) -> None:
        tree = parsed(PACKAGE / "views.py")
        for node in ast.walk(tree):
            # The code, not its docstrings, which name the intent's field.
            body = getattr(node, "body", None)
            if (
                isinstance(body, list)
                and body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
            ):
                body[0] = ast.Pass()
        text = ast.unparse(tree)
        self.assertNotIn("device_id", text)
        self.assertIn("n.parse_installation(request.META.get(contract.INSTALLATION_HEADER))", text)
        self.assertEqual(contract.INSTALLATION_HEADER, "HTTP_GLOW_INSTALLATION_ID")
        for path in sorted(PACKAGE.glob("*.py")):
            source = path.read_text(encoding="utf-8")
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, ast.Call) and ast.unparse(node.func).startswith("logger."):
                    with self.subTest(module=path.name, line=node.lineno):
                        self.assertIsInstance(node.args[0], ast.Constant)
                        self.assertLessEqual(len(node.args), 2)
                        if len(node.args) == 2:
                            self.assertEqual(ast.unparse(node.args[1]), "reason")

    def test_no_module_imports_the_runtime_or_another_slices_routes(self) -> None:
        for path in sorted(PACKAGE.glob("*.py")):
            for node in ast.walk(parsed(path)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    with self.subTest(module=path.name, imported=node.module):
                        self.assertFalse(node.module.startswith(("glow_api", "glow_chat")))
                        self.assertFalse(node.module.startswith("glow_discovery"))


if __name__ == "__main__":
    unittest.main()
