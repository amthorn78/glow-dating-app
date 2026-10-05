"""The proof's process environment: what it refuses, and the connection it accepts.

Pure functions over a mapping, so the offline tests can show each refusal without a
database. Names are inspected; values are never read except for the proof's own
``PROOF_DB_*`` variables, and a refusal message names variables, never values.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

# The API's forbidden connection names (services/api/glow_api/configuration_profiles.py,
# FORBIDDEN_CONNECTION_NAMES), copied rather than imported: importing the API's
# configuration module is the coupling D1 forbids. tests/test_settings_refusals.py
# reads the API's set from its source and fails if the two differ.
API_FORBIDDEN_CONNECTION_NAMES = frozenset(
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
# Any PG* name: libpq reads them as connection defaults (PGPASSFILE, PGSERVICE,
# PGSSLMODE, PGOPTIONS, PGSERVICEFILE and the rest), so none may be present.
LIBPQ_PREFIX = "PG"

# The proof's own names: never PG*, DATABASE_URL or GLOW_*.
HOST = "PROOF_DB_HOST"
PORT = "PROOF_DB_PORT"
NAME = "PROOF_DB_NAME"
USER = "PROOF_DB_USER"
PASSFILE = "PROOF_DB_PASSFILE"
# The run's marker (brief D1; DM-10 2.1): generated for the run by whoever creates the
# disposable database, which carries it as its comment. Not a libpq option.
MARKER = "PROOF_DB_MARKER"
PROOF_NAMES = (HOST, PORT, NAME, USER, PASSFILE, MARKER)

# secrets.token_hex(16): exactly 32 lowercase hexadecimal characters, nothing around them.
MARKER_FORM = re.compile(r"[0-9a-f]{32}")
# The database's whole comment must be this prefix followed by the marker.
MARKER_COMMENT_PREFIX = "glow-ordering-proof:"

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class RefusedEnvironment(Exception):
    """The process environment carries a name the proof refuses to start with."""


class RefusedConnection(Exception):
    """The proof's connection options name something other than a disposable local database."""


@dataclass(frozen=True)
class ConnectionOptions:
    """Explicit libpq options: no service name, so nothing comes from libpq's environment
    or its default files (~/.pgpass, pg_service.conf)."""

    host: str
    port: int
    name: str
    user: str
    passfile: str

    @property
    def unix_socket(self) -> bool:
        return self.host.startswith("/")


def refused_names(environ: Mapping[str, str]) -> tuple[str, ...]:
    """The names present that forbid a start: the API's forbidden connection names and
    every PG* name. Presence alone counts, an empty value included."""
    return tuple(
        sorted(
            name
            for name in environ
            if name in API_FORBIDDEN_CONNECTION_NAMES or name.startswith(LIBPQ_PREFIX)
        )
    )


def require_clean_environment(environ: Mapping[str, str]) -> None:
    present = refused_names(environ)
    if present:
        raise RefusedEnvironment(
            "refusing to start: forbidden or libpq (PG*) variable names present: "
            + ", ".join(present)
        )


def connection_options(environ: Mapping[str, str]) -> ConnectionOptions:
    """The proof's connection from its own variables. Loopback or a Unix-socket
    directory only; every option explicit; no service name."""
    missing = tuple(name for name in PROOF_NAMES if name not in environ)
    if missing:
        raise RefusedConnection("connection options missing: " + ", ".join(missing))
    host = environ[HOST]
    if host not in LOOPBACK_HOSTS and not host.startswith("/"):
        raise RefusedConnection(
            f"{HOST} must be a loopback host or a Unix-socket directory; refusing this host"
        )
    try:
        port = int(environ[PORT])
    except ValueError:
        raise RefusedConnection(f"{PORT} must be an integer") from None
    if not 1 <= port <= 65535:
        raise RefusedConnection(f"{PORT} must be a port number")
    passfile = environ[PASSFILE]
    if not passfile.startswith("/"):
        raise RefusedConnection(f"{PASSFILE} must be an absolute path")
    for name in (NAME, USER):
        value = environ[name]
        if not value or not value.replace("_", "").isalnum():
            raise RefusedConnection(f"{name} must be a plain identifier")
    return ConnectionOptions(host, port, environ[NAME], environ[USER], passfile)


def database_marker(environ: Mapping[str, str]) -> str:
    """The run's marker from ``PROOF_DB_MARKER``: exactly 32 lowercase hexadecimal
    characters (``secrets.token_hex(16)``). An empty, short, long, padded, prefixed or
    upper-case value is refused, so an empty marker can never match the bare prefix."""
    if MARKER not in environ:
        raise RefusedConnection("connection options missing: " + MARKER)
    if MARKER_FORM.fullmatch(environ[MARKER]) is None:
        raise RefusedConnection(
            f"{MARKER} must be exactly 32 lowercase hexadecimal characters"
            " (secrets.token_hex(16)); refusing this value"
        )
    return environ[MARKER]


def expected_comment(marker: str) -> str:
    """The comment the run's database must carry, compared as a whole string."""
    return MARKER_COMMENT_PREFIX + marker


def django_database(options: ConnectionOptions) -> dict[str, object]:
    """Django's DATABASES['default'] for the options. OPTIONS reach libpq through
    psycopg unchanged: passfile (the password is read from that file only), sslmode
    and gssencmode disabled for a local database, and an application name that
    pg_stat_activity shows."""
    return {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": options.host,
        "PORT": str(options.port),
        "NAME": options.name,
        "USER": options.user,
        "OPTIONS": {
            "passfile": options.passfile,
            "sslmode": "disable",
            "gssencmode": "disable",
            "connect_timeout": 10,
            "application_name": "glow-postgres-ordering-proof",
        },
    }
