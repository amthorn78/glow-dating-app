"""The identity suite's Django settings (SV1; its brief's D10).

Like the proof's own settings (``glow_ordering_proof.settings``), it never imports the API's
settings; it refuses to start when a forbidden connection name or any ``PG*`` name is present;
it connects only to the disposable database the proof's own variables name, with every libpq
option explicit and the password read from a passfile; every new connection must find its
database's comment equal to the run's marker; and it installs the proof package, whose
``dbshell`` refuses. The identity database is a second database in the same disposable
PostgreSQL, with its own marker.

On top of that it takes SV1's fragment (``glow_identity.conf``: ``glow_identity``, allauth's
apps, ``django.contrib.sessions`` and the identity URL configuration), and the two keys generated
for the run, each read from a file named by its variable (``identity_environment``): the JWT
signing key and this module's ``SECRET_KEY``. ``ATOMIC_REQUESTS`` is off: SV1 never runs a
``glow_chat`` operation inside an open transaction (D6).

Run with ``DJANGO_SETTINGS_MODULE=glow_ordering_proof.identity_settings`` in a clean process.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from psycopg import IsolationLevel

from glow_ordering_proof import environment, identity_environment, marker

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
# glow_identity, glow_chat and glow_persistence are imported from services/api unchanged.
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

environment.require_clean_environment(os.environ)
_options = environment.connection_options(os.environ)
marker.install(environment.expected_comment(environment.database_marker(os.environ)))

from glow_identity import conf as _identity  # noqa: E402 - after the API's path is added

globals().update(_identity.settings())

INSTALLED_APPS = [*_identity.INSTALLED_APPS, "glow_ordering_proof.apps.ProofConfig"]
SECRET_KEY = identity_environment.secret_key(os.environ)
HEADLESS_JWT_PRIVATE_KEY = identity_environment.jwt_private_key(os.environ)
# Django's test client is the only client (D10): no host is served.
ALLOWED_HOSTS = ["testserver"]
DATABASES = {"default": environment.django_database(_options)}
# P06.DB's design: READ COMMITTED with row locks.
DATABASES["default"]["OPTIONS"]["isolation_level"] = IsolationLevel.READ_COMMITTED  # type: ignore[index]
DATABASES["default"]["ATOMIC_REQUESTS"] = False
# Every record goes to the root logger at DEBUG, where the suite's capture reads it
# (acceptance check 12); no handler is configured here, so nothing is printed by it.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "DEBUG", "handlers": []},
    "loggers": {"django": {"level": "DEBUG", "handlers": [], "propagate": True}},
}
