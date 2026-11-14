"""SV3 Stage A (its brief's D15): the runtime stays sealed from the discovery slice.

``glow_discovery`` runs only under the disposable-database proof's discovery settings
(``proofs/postgres-ordering``). This is a check, not a convention: the served runtime's settings,
URL configuration and WSGI application import none of it; the database backend is still Django's
dummy one; no discovery route is served; the runtime's settings select no compatibility provider for
discovery (D6; PF01 section 5), and ``glow_discovery`` cannot even load under them. ``glow_api/`` is
not changed by SV3. P11 wires the discovery route and its provider.
"""

import json
import unittest

from tests.test_profiles_sealed_runtime import API_ROOT, run_python

RUNTIME = """
import json, sys
import django
django.setup()
import glow_api.settings, glow_api.urls, glow_api.wsgi
from django.conf import settings
from django.urls import get_resolver

def walk(patterns, prefix=""):
    for pattern in patterns:
        if hasattr(pattern, "url_patterns"):
            yield from walk(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            yield prefix + str(pattern.pattern)

print(json.dumps({
    "discovery": sorted(name for name in sys.modules if name.split(".")[0] == "glow_discovery"),
    "engine": settings.DATABASES["default"]["ENGINE"],
    "fixture": getattr(settings, "GLOW_DISCOVERY_COMPATIBILITY_FIXTURE", None),
    "environment": getattr(settings, "GLOW_DISCOVERY_ENVIRONMENT", None),
    "installed": list(settings.INSTALLED_APPS),
    "routes": sorted(walk(get_resolver().url_patterns)),
}))
"""


class DiscoverySealedRuntimeTests(unittest.TestCase):
    def test_the_runtime_imports_none_of_the_discovery_slice(self) -> None:
        result = run_python(RUNTIME)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(seen["discovery"], [])
        self.assertEqual(seen["engine"], "django.db.backends.dummy")
        self.assertEqual(seen["installed"], ["rest_framework"])
        self.assertNotIn("api/v1/discovery/page", seen["routes"])
        self.assertEqual(
            seen["routes"], ["api/v1/development/recommendations", "health/live", "health/ready"]
        )

    def test_the_runtime_selects_no_compatibility_provider_for_discovery(self) -> None:
        result = run_python(RUNTIME)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertIsNone(seen["fixture"])
        self.assertIsNone(seen["environment"])

    def test_no_runtime_module_names_the_discovery_slice(self) -> None:
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("glow_discovery", source)
                self.assertNotIn("GLOW_DISCOVERY", source)

    def test_the_discovery_slice_cannot_load_under_the_runtime_settings(self) -> None:
        # The modules that touch the models (``eligibility`` reads rows through the cursor only, so
        # it imports none at load; the runtime imports it no more than the rest, above).
        for module in ("pages", "views", "urls"):
            with self.subTest(module=module):
                result = run_python(
                    f"import django; django.setup(); import glow_discovery.{module}"
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r"INSTALLED_APPS|not installed")


if __name__ == "__main__":
    unittest.main()
