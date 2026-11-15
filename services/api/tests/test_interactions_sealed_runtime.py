"""SV3 Stage B (its brief's D15): the runtime stays sealed from Stage B's modules.

``glow_discovery.interactions``, ``interaction_views`` and ``interaction_urls`` run only under the
disposable-database proof's discovery settings (``proofs/postgres-ordering``), as Stage A's
modules do (``tests/test_discovery_sealed_runtime.py``). This is a check, not a convention: the
served runtime's settings, URL configuration and WSGI application import none of them; none of
Stage B's routes is served, by its pattern or by a request path; the database backend is still
Django's dummy one; and each of the three cannot even load under the runtime's settings.
``glow_api/`` is not changed by SV3. P11 wires the routes.
"""

import json
import unittest

from tests.test_profiles_sealed_runtime import API_ROOT, run_python

STAGE_B_MODULES = ("interactions", "interaction_views", "interaction_urls")
STAGE_B_ROUTES = (
    "api/v1/discovery/interaction",
    "api/v1/discovery/interaction/undo",
    "api/v1/matches/unmatch",
    "api/v1/matches/<uuid:match_id>",
    "api/v1/blocks",
)
STAGE_B_PATHS = (
    "/api/v1/discovery/interaction",
    "/api/v1/discovery/interaction/undo",
    "/api/v1/matches/unmatch",
    "/api/v1/matches/2b3c4d5e-6f70-4182-93a4-b5c6d7e8f901",
    "/api/v1/blocks",
)

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
    "discovery": sorted(name for name in sys.modules if name.split(".")[0] == "glow_discovery"),
    "engine": settings.DATABASES["default"]["ENGINE"],
    "installed": list(settings.INSTALLED_APPS),
    "routes": sorted(walk(get_resolver().url_patterns)),
    "resolved": {path: resolves(path) for path in PATHS},
}))
"""


def runtime() -> dict[str, object]:
    result = run_python(f"PATHS = {list(STAGE_B_PATHS)!r}\n" + RUNTIME)
    assert result.returncode == 0, result.stdout + result.stderr
    seen: dict[str, object] = json.loads(result.stdout.strip().splitlines()[-1])
    return seen


class InteractionsSealedRuntimeTests(unittest.TestCase):
    def test_the_runtime_imports_none_of_stage_bs_modules(self) -> None:
        seen = runtime()
        discovery = seen["discovery"]
        assert isinstance(discovery, list)
        self.assertEqual(discovery, [])
        for module in STAGE_B_MODULES:
            with self.subTest(module=module):
                self.assertNotIn(f"glow_discovery.{module}", discovery)
        installed = seen["installed"]
        assert isinstance(installed, list)
        self.assertFalse(any(str(app).startswith("glow_discovery") for app in installed))

    def test_the_runtime_serves_none_of_stage_bs_routes(self) -> None:
        seen = runtime()
        routes = seen["routes"]
        assert isinstance(routes, list)
        for route in STAGE_B_ROUTES:
            with self.subTest(route=route):
                self.assertNotIn(route, routes)
        for prefix in ("api/v1/discovery", "api/v1/matches", "api/v1/blocks"):
            with self.subTest(prefix=prefix):
                self.assertFalse(any(str(route).startswith(prefix) for route in routes))
        # And no request path of Stage B's resolves to a view.
        self.assertEqual(seen["resolved"], dict.fromkeys(STAGE_B_PATHS, False))

    def test_the_runtime_database_backend_is_the_dummy_one(self) -> None:
        self.assertEqual(runtime()["engine"], "django.db.backends.dummy")

    def test_no_runtime_module_names_stage_bs_modules(self) -> None:
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("glow_discovery", source)
                for module in STAGE_B_MODULES:
                    self.assertNotIn(module, source)

    def test_stage_bs_modules_cannot_load_under_the_runtime_settings(self) -> None:
        # Each touches the models (through ``glow_chat``'s adapter and ``glow_persistence``),
        # which the runtime does not install.
        for module in STAGE_B_MODULES:
            with self.subTest(module=module):
                result = run_python(
                    f"import django; django.setup(); import glow_discovery.{module}"
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r"INSTALLED_APPS|not installed")


if __name__ == "__main__":
    unittest.main()
