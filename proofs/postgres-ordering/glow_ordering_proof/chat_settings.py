"""The chat suite's Django settings (SV4 A2; its brief's D10).

Like the discovery suite's settings (``glow_ordering_proof.discovery_settings``), it never imports
the API's settings; it refuses to start when a forbidden connection name or any ``PG*`` name is
present; it connects only to the disposable database the proof's own variables name, with every
libpq option explicit and the password read from a passfile; every new connection must find its
database's comment equal to the run's marker; and it installs the proof package, whose
``dbshell`` refuses. The chat database, ``glow_chat_proof``, is the only suite database in its
own job's PostgreSQL (SV4 A0's split, D2), beside one decoy database carrying another marker.

On top of SV1's fragment (``glow_identity.conf``), SV2's (``glow_profiles.conf``) and SV3's
(``glow_discovery.conf``) it serves the chat URL configuration (``glow_ordering_proof.chat_urls``:
SV1's identity routes, through which the suite signs in, SV2's member routes, through which it
builds the cases' own members, SV3's page and action routes, through which it matches them, and
chat's routes, D8). Its two keys, the JWT signing key and its own ``SECRET_KEY``, are generated
for the run and each read from a file named by its variable (``identity_environment``; the job
names the chat suite's own files). ``ATOMIC_REQUESTS`` is off; chat's views are
``non_atomic_requests`` whatever it says (D8), and a case shows it.

**The provider** (D8): these settings alone name the history read's text reader,
``GLOW_CHAT_TEXT_READER``, the in-memory fixture provider the suite delivers to
(``chat_support.text_reader``). No provider call leaves the process; no HDE call is possible, as
the discovery settings' fixture compatibility adapter is in-process.

Run with ``DJANGO_SETTINGS_MODULE=glow_ordering_proof.chat_settings`` in a clean process.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from psycopg import IsolationLevel

from glow_ordering_proof import environment, identity_environment, marker

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
# glow_chat, glow_discovery, glow_profiles, glow_identity and glow_persistence are imported from
# services/api unchanged.
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

environment.require_clean_environment(os.environ)
_options = environment.connection_options(os.environ)
marker.install(environment.expected_comment(environment.database_marker(os.environ)))

from glow_discovery import conf as _discovery  # noqa: E402 - after the API's path is added
from glow_identity import conf as _identity  # noqa: E402
from glow_profiles import conf as _profiles  # noqa: E402

globals().update(_identity.settings())

INSTALLED_APPS = [
    *_identity.INSTALLED_APPS,
    *_profiles.INSTALLED_APPS,
    *_discovery.INSTALLED_APPS,
    "glow_ordering_proof.apps.ProofConfig",
]
ROOT_URLCONF = "glow_ordering_proof.chat_urls"
SECRET_KEY = identity_environment.secret_key(os.environ)
HEADLESS_JWT_PRIVATE_KEY = identity_environment.jwt_private_key(os.environ)
# Django's test client is the only client: no host is served.
ALLOWED_HOSTS = ["testserver"]
DATABASES = {"default": environment.django_database(_options)}
# P06.DB's design: READ COMMITTED with row locks.
DATABASES["default"]["OPTIONS"]["isolation_level"] = IsolationLevel.READ_COMMITTED  # type: ignore[index]
DATABASES["default"]["ATOMIC_REQUESTS"] = False
# SV3's D6: the fixture compatibility adapter, selected here only, in the test environment, for
# the pages through which the cases' members like each other.
GLOW_DISCOVERY_COMPATIBILITY_FIXTURE = "explicitly-synthetic-ready"
GLOW_DISCOVERY_ENVIRONMENT = "test"
# D8, "The provider": the history read's text reader, the in-memory fixture, named here only.
GLOW_CHAT_TEXT_READER = "glow_ordering_proof.chat_support.text_reader"
# Every record goes to the root logger at DEBUG, where the suite's capture reads it; no handler is
# configured here, so nothing is printed by it.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "DEBUG", "handlers": []},
    "loggers": {"django": {"level": "DEBUG", "handlers": [], "propagate": True}},
}
