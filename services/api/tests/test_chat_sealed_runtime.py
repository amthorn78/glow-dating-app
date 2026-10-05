"""P06.2 D2, condition 2.3 (DM-13): the runtime stays sealed.

The chat adapter (``glow_chat``) lives in ``services/api`` but runs only under the
disposable-database proof's settings. This is a check, not a convention: the runtime
settings, URL configuration and WSGI application import none of the adapter's modules
(nor the model registry or a database driver), the database backend is still Django's
dummy one, and the connection refusal is unchanged.
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

# The connection refusal as it stood at P06.2's start (2f982ae); any change fails here.
FORBIDDEN_AT_P06_2 = frozenset(
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
patterns = [str(p.pattern) for p in get_resolver().url_patterns]
try:
    connections["default"].ensure_connection()
    refused = None
except ImproperlyConfigured as exc:
    refused = type(exc).__name__
print(json.dumps({
    "modules": sorted(name for name in sys.modules if name.split(".")[0] in
                      ("glow_chat", "glow_persistence", "psycopg", "psycopg_binary")),
    "engine": settings.DATABASES["default"]["ENGINE"],
    "installed": list(settings.INSTALLED_APPS),
    "patterns": patterns,
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


class SealedRuntimeTests(unittest.TestCase):
    def test_the_runtime_imports_none_of_the_adapter(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", RUNTIME],
            cwd=API_ROOT,
            env=clean_environment(GLOW_ENV="test"),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(seen["modules"], [])
        self.assertEqual(seen["engine"], "django.db.backends.dummy")
        self.assertEqual(seen["installed"], ["rest_framework"])
        self.assertEqual(seen["refused"], "ImproperlyConfigured")
        self.assertFalse(any("chat" in pattern for pattern in seen["patterns"]))

    def test_no_runtime_module_names_the_adapter(self) -> None:
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("glow_chat", source)
                self.assertNotIn("glow_persistence", source)

    def test_the_connection_refusal_is_unchanged(self) -> None:
        self.assertEqual(FORBIDDEN_CONNECTION_NAMES, FORBIDDEN_AT_P06_2)
        value = "synthetic-connection-value-not-a-secret"
        for name in sorted(FORBIDDEN_AT_P06_2):
            with self.subTest(name=name):
                with self.assertRaises(ConfigurationError) as raised:
                    load_configuration({"GLOW_ENV": "test", name: value})
                self.assertNotIn(value, str(raised.exception))

    def test_a_process_with_a_connection_name_does_not_start(self) -> None:
        value = "postgres://synthetic.invalid/not-a-real-database"
        result = subprocess.run(
            [sys.executable, "-c", "import django; django.setup()"],
            cwd=API_ROOT,
            env=clean_environment(GLOW_ENV="test", DATABASE_URL=value),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(value, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
