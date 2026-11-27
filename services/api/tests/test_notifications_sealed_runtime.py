"""SV4 B1 (its brief's D31, with D15's pattern): the runtime stays sealed from F12's surface.

``glow_notifications`` (the ORM adapter, the factory hooks, the contract mapping, the views and the
URLs) runs only under the disposable-database proof's chat settings (``proofs/postgres-ordering``).
This is a check, not a convention, in the style of SV1's to SV4 A2's: the served runtime's settings,
URL configuration and WSGI application import none of it; the database backend is still Django's
dummy one; none of F12's routes is served, by its pattern or by a request path; the runtime names
neither the token store's nor the push transport's factory (D16; DM-101's AM1); no runtime module
names them; the package's modules that touch the models cannot even load under the runtime's
settings; and the production catalog's paths map stays empty. ``glow_api/`` is not changed by B1.

SV4 B2 (its brief's D31): the module list gains B2's modules (the deliverer, ``logout``, the
sweeps, G-04's read and the management command), every earlier assertion kept; B2's modules that
touch the models cannot load under the runtime's settings either; the runtime's command list holds
no ``glow_notifications`` command, since the runtime installs no ``glow_notifications``; and no
``glow_chat`` or ``glow_discovery`` module imports ``glow_notifications`` (the two writers take the
events' names from ``glow_domain.notifications``). ``glow_api/`` is not changed by B2.
"""

import ast
import json
import unittest

from tests.test_profiles_sealed_runtime import API_ROOT, run_python

B1_MODULES = (
    "glow_notifications",
    "glow_notifications.apps",
    "glow_notifications.conf",
    "glow_notifications.contract",
    "glow_notifications.persistence",
    "glow_notifications.providers",
    "glow_notifications.urls",
    "glow_notifications.views",
    # SV4 B2 (D31).
    "glow_notifications.delivery",
    "glow_notifications.logout",
    "glow_notifications.recipients",
    "glow_notifications.sweeps",
    "glow_notifications.management",
    "glow_notifications.management.commands",
    "glow_notifications.management.commands.notification_sweeps",
)
# G-04's read (``glow_notifications.recipients``) imports no model (one literal statement on the
# connection), so it is left out here, as the package's root is in B1's list below; the runtime
# imports it nowhere (``test_the_runtime_imports_none_of_b1s_modules``).
B2_MODULES_WITH_MODELS = (
    "glow_notifications.delivery",
    "glow_notifications.logout",
    "glow_notifications.sweeps",
    "glow_notifications.management.commands.notification_sweeps",
)
B2_COMMAND = "notification_sweeps"
B1_ROUTES = (
    "api/v1/notifications",
    "api/v1/notifications/device",
    "api/v1/notifications/settings",
)
B1_PATHS = tuple(f"/{route}" for route in B1_ROUTES)
FACTORIES = ("GLOW_NOTIFICATIONS_TOKEN_STORE", "GLOW_NOTIFICATIONS_PUSH_TRANSPORT")

RUNTIME = """
import json, sys
import django
django.setup()
import glow_api.settings, glow_api.urls, glow_api.wsgi
from django.conf import settings
from django.urls import Resolver404, get_resolver, resolve


def walk(patterns, prefix=""):
    for pattern in patterns:
        if hasattr(pattern, "url_patterns"):
            yield from walk(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            yield prefix + str(pattern.pattern)


def resolves(path):
    try:
        resolve(path)
    except Resolver404:
        return False
    return True


print(json.dumps({
    "modules": sorted(name for name in sys.modules
                      if name.split(".")[0] in ("glow_notifications", "glow_persistence")
                      or name.startswith(("glow_domain.notification", "glow_profiles"))),
    "engine": settings.DATABASES["default"]["ENGINE"],
    "installed": list(settings.INSTALLED_APPS),
    "routes": sorted(walk(get_resolver().url_patterns)),
    "resolved": {path: resolves(path) for path in PATHS},
    "factories": {name: getattr(settings, name, None) for name in FACTORIES},
}))
"""


def runtime() -> dict[str, object]:
    result = run_python(f"PATHS = {list(B1_PATHS)!r}\nFACTORIES = {list(FACTORIES)!r}\n" + RUNTIME)
    assert result.returncode == 0, result.stdout + result.stderr
    seen: dict[str, object] = json.loads(result.stdout.strip().splitlines()[-1])
    return seen


class NotificationsSealedRuntimeTests(unittest.TestCase):
    def test_the_runtime_imports_none_of_b1s_modules(self) -> None:
        seen = runtime()
        modules = seen["modules"]
        assert isinstance(modules, list)
        self.assertEqual(modules, [])
        for module in B1_MODULES:
            with self.subTest(module=module):
                self.assertNotIn(module, modules)
        self.assertEqual(seen["installed"], ["rest_framework"])

    def test_the_runtime_database_backend_is_the_dummy_one(self) -> None:
        self.assertEqual(runtime()["engine"], "django.db.backends.dummy")

    def test_the_runtime_serves_none_of_b1s_routes(self) -> None:
        seen = runtime()
        routes = seen["routes"]
        assert isinstance(routes, list)
        self.assertEqual(
            routes, ["api/v1/development/recommendations", "health/live", "health/ready"]
        )
        for route in B1_ROUTES:
            with self.subTest(route=route):
                self.assertNotIn(route, routes)
        self.assertFalse(any(str(route).startswith("api/v1/notifications") for route in routes))
        self.assertEqual(seen["resolved"], dict.fromkeys(B1_PATHS, False))

    def test_the_runtime_names_no_token_store_or_push_transport(self) -> None:
        # D16 (DM-101's AM1): only the proof's chat settings name the two factories.
        self.assertEqual(runtime()["factories"], dict.fromkeys(FACTORIES, None))

    def test_no_runtime_module_names_b1s_modules_or_the_factories(self) -> None:
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("glow_notifications", source)
                for name in FACTORIES:
                    self.assertNotIn(name, source)

    def test_b1s_modules_cannot_load_under_the_runtime_settings(self) -> None:
        # Each touches the models (through the adapter and glow_persistence), which the runtime does
        # not install; the package's root, its app config, its settings fragment, its factory hooks
        # and its contract mapping import no model, so they are left out (as A2's test leaves out
        # glow_chat.contract).
        for module in (
            "glow_notifications.persistence",
            "glow_notifications.views",
            "glow_notifications.urls",
        ):
            with self.subTest(module=module):
                result = run_python(f"import django; django.setup(); import {module}")
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r"INSTALLED_APPS|not installed")

    def test_b2s_modules_cannot_load_under_the_runtime_settings(self) -> None:
        # SV4 B2: each touches the models (through the deliverer, logout, the sweeps or the
        # adapter), which the runtime does not install.
        for module in B2_MODULES_WITH_MODELS:
            with self.subTest(module=module):
                result = run_python(f"import django; django.setup(); import {module}")
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r"INSTALLED_APPS|not installed")

    def test_the_runtime_lists_no_notification_command(self) -> None:
        # SV4 B2 (D24, D31): the command exists in the package, and the runtime, which installs
        # no glow_notifications, lists none of the package's commands.
        result = run_python(
            "import json\n"
            "import django\n"
            "django.setup()\n"
            "from django.core.management import find_commands, get_commands\n"
            "commands = get_commands()\n"
            "print(json.dumps({\n"
            "    'found': find_commands('glow_notifications/management'),\n"
            "    'listed': sorted(name for name, app in commands.items()\n"
            "                     if app.startswith('glow_notifications')),\n"
            f"    'named': {B2_COMMAND!r} in commands,\n"
            "}))\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(seen["found"], [B2_COMMAND])
        self.assertEqual(seen["listed"], [])
        self.assertFalse(seen["named"])

    def test_no_chat_or_discovery_module_imports_glow_notifications(self) -> None:
        # SV4 B2: the two writers (glow_discovery.interactions' like, glow_chat.delivery's
        # receipt) take the events' names from glow_domain.notifications only.
        for package in ("glow_chat", "glow_discovery"):
            for path in sorted((API_ROOT / package).rglob("*.py")):
                source = path.read_text(encoding="utf-8")
                with self.subTest(module=str(path.relative_to(API_ROOT))):
                    for node in ast.walk(ast.parse(source)):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            self.assertFalse(node.module.startswith("glow_notifications"))
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                self.assertFalse(alias.name.startswith("glow_notifications"))
                    self.assertNotIn("glow_notifications", source)

    def test_the_production_catalog_claims_no_route(self) -> None:
        catalog = json.loads(
            (API_ROOT.parents[1] / "packages/contracts/production/openapi.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(catalog["paths"], {})
        self.assertNotIn("servers", catalog)


if __name__ == "__main__":
    unittest.main()
