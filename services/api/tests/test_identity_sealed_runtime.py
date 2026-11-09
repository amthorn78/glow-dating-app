"""SV1 (its brief's D11): the runtime stays sealed from the identity slice.

``glow_identity`` lives in ``services/api`` but runs only under the disposable-database proof's
identity settings (``proofs/postgres-ordering``). This is a check, not a convention: the served
runtime's settings, URL configuration and WSGI application import none of ``glow_identity``,
allauth, ``jwt`` or ``cryptography`` (nor ``cryptography``'s own ``cffi`` and ``pycparser``);
the database backend is still Django's dummy one; no identity setting or route is served; the
connection refusal is unchanged; and ``glow_identity`` cannot even load under the runtime's
settings. ``glow_api/`` is not changed by SV1. P11 wires the identity routes and settings.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from glow_api.configuration import ConfigurationError, load_configuration
from glow_api.configuration_profiles import FORBIDDEN_CONNECTION_NAMES

API_ROOT = Path(__file__).resolve().parents[1]

SEALED_FROM = (
    "glow_identity",
    "allauth",
    "jwt",
    "cryptography",
    "cffi",
    "_cffi_backend",
    "pycparser",
)

# The connection refusal as it stood at SV1's start (dc3e551); any change fails here.
FORBIDDEN_AT_SV1 = frozenset(
    {
        "DATABASE_URL",
        "GLOW_DATABASE_URL",
        "DATABASE_PRIVATE_URL",
        "PGHOST",
        "PGPORT",
        "PGDATABASE",
        "PGUSER",
        "PGPASSWORD",
        "REDIS_URL",
        "REDIS_PRIVATE_URL",
        "BROKER_URL",
        "CELERY_BROKER_URL",
        "CELERY_RESULT_BACKEND",
        "GLOW_BROKER_URL",
        "HDE_API_URL",
        "HDE_API_TOKEN",
        "HD_API_BASE_URL",
        "HD_API_KEY",
        "GEO_API_KEY",
        "GLOW_HDE_API_URL",
        "GLOW_HDE_API_TOKEN",
    }
)

RUNTIME = """
import json, sys
import django
django.setup()
import glow_api.settings, glow_api.urls, glow_api.wsgi
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.urls import get_resolver

def walk(patterns, prefix=""):
    for pattern in patterns:
        if hasattr(pattern, "url_patterns"):
            yield from walk(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            yield prefix + str(pattern.pattern)

try:
    connections["default"].ensure_connection()
    refused = None
except ImproperlyConfigured as exc:
    refused = type(exc).__name__
print(json.dumps({
    "modules": sorted(name for name in sys.modules if name.split(".")[0] in SEALED_FROM),
    "engine": settings.DATABASES["default"]["ENGINE"],
    "installed": list(settings.INSTALLED_APPS),
    "routes": sorted(walk(get_resolver().url_patterns)),
    "identity_settings": sorted(
        name for name in dir(settings)
        if name.startswith(("ACCOUNT_", "HEADLESS_", "USERSESSIONS_", "GLOW_IDENTITY_"))
    ),
    "backends": list(settings.AUTHENTICATION_BACKENDS),
    "middleware": list(settings.MIDDLEWARE),
    "refused": refused,
}))
"""


def clean_environment(**extra: str) -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "LANG": "C.UTF-8",
        "DJANGO_SETTINGS_MODULE": "glow_api.settings",
        **extra,
    }


def run_python(code: str, **extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=API_ROOT,
        env=clean_environment(**extra),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


class IdentitySealedRuntimeTests(unittest.TestCase):
    def test_the_runtime_imports_none_of_the_identity_slice(self) -> None:
        result = run_python(f"SEALED_FROM = {SEALED_FROM!r}\n" + RUNTIME, GLOW_ENV="test")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(seen["modules"], [])
        self.assertEqual(seen["engine"], "django.db.backends.dummy")
        self.assertEqual(seen["installed"], ["rest_framework"])
        self.assertEqual(seen["refused"], "ImproperlyConfigured")
        self.assertEqual(seen["identity_settings"], [])
        self.assertEqual(seen["backends"], ["django.contrib.auth.backends.ModelBackend"])
        self.assertFalse(any("allauth" in name for name in seen["middleware"]))
        for route in seen["routes"]:
            with self.subTest(route=route):
                self.assertNotIn("_allauth", route)
                self.assertNotIn("account/access", route)

    def test_no_runtime_module_names_the_identity_slice(self) -> None:
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8").lower()
                for name in ("glow_identity", "allauth", "jwt", "cryptography"):
                    self.assertNotIn(name, source)

    def test_the_identity_slice_cannot_load_under_the_runtime_settings(self) -> None:
        # Neither allauth's apps nor the models they need are installed there, so the
        # identity slice's modules refuse to load.
        result = run_python(
            "import django; django.setup(); import glow_identity.revocation", GLOW_ENV="test"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr, r"INSTALLED_APPS|not installed")

    def test_the_connection_refusal_is_unchanged(self) -> None:
        self.assertEqual(FORBIDDEN_CONNECTION_NAMES, FORBIDDEN_AT_SV1)
        value = "synthetic-connection-value-not-a-secret"
        for name in sorted(FORBIDDEN_AT_SV1):
            with self.subTest(name=name):
                with self.assertRaises(ConfigurationError) as raised:
                    load_configuration({"GLOW_ENV": "test", name: value})
                self.assertNotIn(value, str(raised.exception))


if __name__ == "__main__":
    unittest.main()
