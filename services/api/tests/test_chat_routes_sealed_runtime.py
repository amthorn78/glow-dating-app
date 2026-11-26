"""SV4 A2 (its brief's D15): the runtime stays sealed from chat's routes and the match list.

``glow_chat``'s route modules (``contract``, ``route_reads``, ``views``, ``urls``) and the match
list beside SV3's match read (``glow_discovery``'s ``interactions``, ``interaction_views``,
``interaction_urls`` and ``contract``) run only under the disposable-database proof's chat settings
(``proofs/postgres-ordering``). This is a check, not a convention, in the style of SV1's to SV3's:
the served runtime's settings, URL configuration and WSGI application import none of them; the
database backend is still Django's dummy one; none of A2's routes is served, by its pattern or by
a request path; the runtime names no text reader's factory (D8, "The provider"); no runtime module
names them; each cannot even load under the runtime's settings; and the production catalog's
paths map stays empty. ``glow_api/`` is not changed by A2. Integration wires the routes.
"""

import json
import unittest

from tests.test_profiles_sealed_runtime import API_ROOT, run_python

A2_MODULES = (
    "glow_chat.contract",
    "glow_chat.route_reads",
    "glow_chat.views",
    "glow_chat.urls",
    "glow_discovery.interactions",
    "glow_discovery.interaction_views",
    "glow_discovery.interaction_urls",
    "glow_discovery.contract",
)
A2_ROUTES = (
    "api/v1/chat/messages",
    "api/v1/chat/conversations",
    "api/v1/chat/history",
    "api/v1/chat/read-cursor",
    "api/v1/matches",
)
A2_PATHS = tuple(f"/{route}" for route in A2_ROUTES)

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
                      if name.split(".")[0] in ("glow_chat", "glow_discovery", "glow_persistence")),
    "engine": settings.DATABASES["default"]["ENGINE"],
    "installed": list(settings.INSTALLED_APPS),
    "routes": sorted(walk(get_resolver().url_patterns)),
    "resolved": {path: resolves(path) for path in PATHS},
    "reader": getattr(settings, "GLOW_CHAT_TEXT_READER", None),
}))
"""


def runtime() -> dict[str, object]:
    result = run_python(f"PATHS = {list(A2_PATHS)!r}\n" + RUNTIME)
    assert result.returncode == 0, result.stdout + result.stderr
    seen: dict[str, object] = json.loads(result.stdout.strip().splitlines()[-1])
    return seen


class ChatRoutesSealedRuntimeTests(unittest.TestCase):
    def test_the_runtime_imports_none_of_a2s_modules(self) -> None:
        seen = runtime()
        modules = seen["modules"]
        assert isinstance(modules, list)
        self.assertEqual(modules, [])
        for module in A2_MODULES:
            with self.subTest(module=module):
                self.assertNotIn(module, modules)
        self.assertEqual(seen["installed"], ["rest_framework"])

    def test_the_runtime_database_backend_is_the_dummy_one(self) -> None:
        self.assertEqual(runtime()["engine"], "django.db.backends.dummy")

    def test_the_runtime_serves_none_of_a2s_routes(self) -> None:
        seen = runtime()
        routes = seen["routes"]
        assert isinstance(routes, list)
        self.assertEqual(
            routes, ["api/v1/development/recommendations", "health/live", "health/ready"]
        )
        for route in A2_ROUTES:
            with self.subTest(route=route):
                self.assertNotIn(route, routes)
        self.assertFalse(
            any(str(route).startswith(("api/v1/chat", "api/v1/matches")) for route in routes)
        )
        self.assertEqual(seen["resolved"], dict.fromkeys(A2_PATHS, False))

    def test_the_runtime_names_no_text_reader(self) -> None:
        # D8, "The provider": only the proof's chat settings name the history read's factory.
        self.assertIsNone(runtime()["reader"])

    def test_no_runtime_module_names_a2s_modules_or_the_reader(self) -> None:
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("glow_chat", source)
                self.assertNotIn("glow_discovery", source)
                self.assertNotIn("GLOW_CHAT_TEXT_READER", source)
                self.assertNotIn("route_reads", source)

    def test_a2s_modules_cannot_load_under_the_runtime_settings(self) -> None:
        # Each touches the models (through glow_chat's adapter and glow_persistence), which the
        # runtime does not install; ``glow_chat.contract`` imports no model, so it is left out.
        for module in ("glow_chat.route_reads", "glow_chat.views", "glow_chat.urls"):
            with self.subTest(module=module):
                result = run_python(f"import django; django.setup(); import {module}")
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r"INSTALLED_APPS|not installed")

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
