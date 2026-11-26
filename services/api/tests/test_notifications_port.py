"""SV4 B1 (its brief's D18 and D25): F12's persistence port, ``NotificationPersistence``.

The domain keeps the pure parts and its in-memory ``NotificationService`` becomes the port's
fixture, still guarded to development and test (P06.3's tests, ``tests/test_notifications.py``,
keep every assertion against it); ``glow_notifications.persistence.OrmNotificationPersistence`` is
the port's ORM adapter. Here, with no Django and no database: both take the port's three methods
the same way, with the trusted ``Caller`` first and never an actor in the intent; the fixture keeps
D25's bound as the adapter does (an eleventh active registration refused, with no token stored,
a rotation at the bound served, a registration again once one ends); and the bound is the one
constant both read.
"""

import ast
import inspect
import unittest
import uuid
from pathlib import Path

from glow_domain import notifications as n
from glow_domain.notification_fixtures import notification_fixture, synthetic_token

API_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = API_ROOT / "glow_notifications" / "persistence.py"
PORT = ("read", "device", "settings")


def register(device: uuid.UUID, version: int, key: str, label: str) -> dict[str, object]:
    return {
        "operation": "device",
        "meta": {"idempotency_key": key, "expected_version": version},
        "device_id": str(device),
        "action": "register",
        "provider_token": synthetic_token(label),
    }


class PortShapeTests(unittest.TestCase):
    def test_the_port_has_the_three_methods_and_the_fixture_takes_them(self) -> None:
        declared = {
            name
            for name, member in vars(n.NotificationPersistence).items()
            if callable(member) and not name.startswith("_")
        }
        self.assertEqual(declared, set(PORT))
        for name in PORT:
            with self.subTest(method=name):
                port = list(inspect.signature(getattr(n.NotificationPersistence, name)).parameters)
                fixture = list(inspect.signature(getattr(n.NotificationService, name)).parameters)
                self.assertEqual(fixture, port)

    def test_the_adapter_takes_them_the_same_way_with_a_probe_only_beside(self) -> None:
        # Read from the source: the adapter imports the models, which need a configured registry.
        tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
        klass = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "OrmNotificationPersistence"
        )
        methods = {node.name: node for node in klass.body if isinstance(node, ast.FunctionDef)}
        for name in PORT:
            with self.subTest(method=name):
                port = list(inspect.signature(getattr(n.NotificationPersistence, name)).parameters)
                arguments = methods[name].args
                self.assertEqual([arg.arg for arg in arguments.args], port)
                self.assertEqual([arg.arg for arg in arguments.kwonlyargs], ["probe"])
                self.assertEqual(len(arguments.kw_defaults), 1)
        constructor = methods["__init__"].args
        self.assertEqual([arg.arg for arg in constructor.kwonlyargs], ["tokens"])


class FixtureBoundTests(unittest.TestCase):
    """D25 at fixture scope, as the ORM adapter keeps it (``n.MAX_ACTIVE_REGISTRATIONS``)."""

    def test_the_bound_is_ten_and_one_constant(self) -> None:
        self.assertEqual(n.MAX_ACTIVE_REGISTRATIONS, 10)
        self.assertEqual(n.REGISTRATION_BOUND, "registration_bound")
        source = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("if active >= n.MAX_ACTIVE_REGISTRATIONS:", source)
        self.assertIn("raise _Refused(n.REGISTRATION_BOUND)", source)

    def test_an_eleventh_active_registration_is_refused_with_no_token_stored(self) -> None:
        fx = notification_fixture()
        account = fx.world.add_account()
        session = fx.world.open_session(account)
        devices = [uuid.uuid4() for _ in range(n.MAX_ACTIVE_REGISTRATIONS)]
        for index, device in enumerate(devices):
            caller = n.Caller(account, session, device)
            result = fx.service.device(caller, register(device, 0, f"k{index}", f"b{index}"))
            self.assertEqual(result.outcome, "applied")
        eleventh = uuid.uuid4()
        held = fx.tokens.held
        refused = fx.service.device(
            n.Caller(account, session, eleventh), register(eleventh, 0, "k11", "b11")
        )
        self.assertEqual((refused.outcome, refused.reason), ("refused", n.REGISTRATION_BOUND))
        self.assertIsNone(fx.service.registration(account, eleventh))
        self.assertEqual(fx.tokens.held, held)
        rotated = fx.service.device(
            n.Caller(account, session, devices[0]), register(devices[0], 1, "k12", "b12")
        )
        self.assertEqual((rotated.outcome, rotated.transition), ("applied", "rotate"))
        revoke = {
            "operation": "device",
            "meta": {"idempotency_key": "k13", "expected_version": 1},
            "device_id": str(devices[1]),
            "action": "revoke",
            "provider_token": None,
        }
        self.assertEqual(
            fx.service.device(n.Caller(account, session, devices[1]), revoke).outcome, "applied"
        )
        again = fx.service.device(
            n.Caller(account, session, eleventh), register(eleventh, 0, "k14", "b14")
        )
        self.assertEqual((again.outcome, again.transition), ("applied", "register"))

    def test_another_accounts_registrations_do_not_count(self) -> None:
        fx = notification_fixture()
        first, second = fx.world.add_account(), fx.world.add_account()
        first_session, second_session = fx.world.open_session(first), fx.world.open_session(second)
        for index in range(n.MAX_ACTIVE_REGISTRATIONS):
            device = uuid.uuid4()
            fx.service.device(
                n.Caller(first, first_session, device), register(device, 0, f"a{index}", "a")
            )
        device = uuid.uuid4()
        result = fx.service.device(
            n.Caller(second, second_session, device), register(device, 0, "b", "b")
        )
        self.assertEqual(result.outcome, "applied")


class InstallationTests(unittest.TestCase):
    def test_the_installation_is_a_lower_case_uuid(self) -> None:
        value = str(uuid.uuid4())
        self.assertEqual(n.parse_installation(value), uuid.UUID(value))
        for bad in (value.upper(), value + "\n", "x", "", None, 7, value.replace("-", "")):
            with self.subTest(value=bad):
                with self.assertRaises(n.IntentError) as raised:
                    n.parse_installation(bad)
                self.assertEqual(str(raised.exception), n.INTENT_INVALID)


if __name__ == "__main__":
    unittest.main()
