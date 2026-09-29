"""The proof's own Django settings (D1, D3 condition 1).

Never imports the API's settings or ``glow_persistence.static_settings``. It refuses
to start when a forbidden connection name or any ``PG*`` name is present, and it
connects only to the disposable database named by the proof's own variables, with
every libpq option explicit and the password read from a passfile.

Run with ``DJANGO_SETTINGS_MODULE=glow_ordering_proof.settings`` in a clean process
(``env -i PATH=... HOME=... LANG=C.UTF-8 PROOF_DB_...``).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from psycopg import IsolationLevel

from glow_ordering_proof import environment

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
# glow_persistence is imported from services/api unchanged; nothing else of the API is.
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

environment.require_clean_environment(os.environ)
_options = environment.connection_options(os.environ)

# Django insists on a SECRET_KEY. The proof signs nothing and serves nothing; this is a
# fixed placeholder, not a secret.
SECRET_KEY = "p06-db-proof-placeholder-not-a-secret"
DEBUG = False
ALLOWED_HOSTS: list[str] = []
ROOT_URLCONF = None
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "glow_persistence.apps.PersistenceDesignConfig",
]
DATABASES = {"default": environment.django_database(_options)}
# D5: READ COMMITTED with row locks is the design. Every transaction begins at this level.
DATABASES["default"]["OPTIONS"]["isolation_level"] = IsolationLevel.READ_COMMITTED  # type: ignore[index]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "auth.User"
USE_TZ = True
TIME_ZONE = "UTC"
