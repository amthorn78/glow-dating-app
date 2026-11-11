"""SV2 Stage A (its brief's D13): the runtime stays sealed from the profile slice.

``glow_profiles``, its domain modules (``glow_domain.profile_fields``, ``profile_settings`` and
``identity_verification``) and the models they write run only under the disposable-database
proof's profile settings (``proofs/postgres-ordering``). This is a check, not a convention: the
served runtime's settings, URL configuration and WSGI application import none of them; the
database backend is still Django's dummy one; no profile route is served; and ``glow_profiles``
cannot even load under the runtime's settings. ``glow_api/`` is not changed by SV2. P11 wires the
profile routes and settings.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]

# Whole packages the runtime must not import (the models are in ``glow_persistence``).
SEALED_PACKAGES = ("glow_profiles", "glow_persistence", "glow_identity", "glow_chat")
# SV2's new domain modules, beside the ones the runtime does import.
SEALED_MODULES = (
    "glow_domain.profile_fields",
    "glow_domain.profile_settings",
    "glow_domain.identity_verification",
    # SV2 Stage B: the photo ports (D10).
    "glow_domain.media",
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
    "packages": sorted(name for name in sys.modules if name.split(".")[0] in SEALED_PACKAGES),
    "modules": sorted(name for name in sys.modules if name in SEALED_MODULES),
    "engine": settings.DATABASES["default"]["ENGINE"],
    "refused": refused,
    "installed": list(settings.INSTALLED_APPS),
    "routes": sorted(walk(get_resolver().url_patterns)),
}))
"""


def run_python(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=API_ROOT,
        env={
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "DJANGO_SETTINGS_MODULE": "glow_api.settings",
            "GLOW_ENV": "test",
        },
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


class ProfilesSealedRuntimeTests(unittest.TestCase):
    def test_the_runtime_imports_none_of_the_profile_slice(self) -> None:
        result = run_python(
            f"SEALED_PACKAGES = {SEALED_PACKAGES!r}\nSEALED_MODULES = {SEALED_MODULES!r}\n"
            + RUNTIME
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(seen["packages"], [])
        self.assertEqual(seen["modules"], [])
        self.assertEqual(seen["engine"], "django.db.backends.dummy")
        # The dummy backend refuses a connection: nothing can reach a database (C2, finding 15).
        self.assertEqual(seen["refused"], "ImproperlyConfigured")
        self.assertEqual(seen["installed"], ["rest_framework"])
        # The runtime's routes as they stood at SV2's start: no profile, consent, eligibility or
        # birth-input route is served.
        self.assertEqual(
            seen["routes"], ["api/v1/development/recommendations", "health/live", "health/ready"]
        )

    def test_no_runtime_module_names_the_profile_slice(self) -> None:
        names = ("glow_profiles", "glow_persistence", *SEALED_MODULES)
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                for name in names:
                    self.assertNotIn(name, source)
                for name in ("profile_fields", "profile_settings", "identity_verification"):
                    self.assertNotIn(name, source)

    def test_the_profile_slice_cannot_load_under_the_runtime_settings(self) -> None:
        # Neither the models' app nor the apps they need are installed there, so the profile
        # slice's modules refuse to load.
        for module in ("operations", "staff", "views", "urls", "settings_store"):
            with self.subTest(module=module):
                result = run_python(f"import django; django.setup(); import glow_profiles.{module}")
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r"INSTALLED_APPS|not installed")

    def test_the_age_section_imports_nothing_new(self) -> None:
        # ``glow_domain.identity`` is the one module the runtime imports that SV2 changes (D7's
        # date and transition, in its age section): it still imports the standard library only.
        source = (API_ROOT / "glow_domain" / "identity.py").read_text(encoding="utf-8")
        imports = sorted(
            line.strip()
            for line in source.splitlines()
            if line.startswith(("import ", "from ")) and "__future__" not in line
        )
        self.assertEqual(
            imports,
            [
                "from dataclasses import dataclass",
                "from datetime import date, datetime",
                "from enum import Enum",
                "from typing import Protocol",
            ],
        )


if __name__ == "__main__":
    unittest.main()
