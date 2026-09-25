"""Server-side credential loading.

Only the server process calls :func:`load_server_credentials`. It reads the
three ``STREAM_*`` names from its own environment, refuses to run when an HDE
connection name is present, and refuses any application other than the
development application 1729640. The secret is never part of ``repr``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

EXPECTED_APP_ID = "1729640"
SERVER_VARIABLES = ("STREAM_APP_ID", "STREAM_API_KEY", "STREAM_API_SECRET")
FORBIDDEN_VARIABLES = ("DATABASE_URL", "HD_API_KEY", "GEO_API_KEY")


class EnvironmentRefused(RuntimeError):
    """The process environment is not safe or not complete for a live run."""


@dataclass(frozen=True)
class ServerCredentials:
    app_id: str
    api_key: str
    _secret: str = field(repr=False, compare=False)

    def secret(self) -> str:
        return self._secret

    def __repr__(self) -> str:
        return f"ServerCredentials(app_id={self.app_id!r}, api_key={self.api_key!r}, secret=<held>)"


def forbidden_names_present(environ: Mapping[str, str]) -> list[str]:
    """Names (never values) of HDE-shared variables present in ``environ``."""
    return [name for name in FORBIDDEN_VARIABLES if name in environ]


def load_server_credentials(environ: Mapping[str, str]) -> ServerCredentials:
    present = forbidden_names_present(environ)
    if present:
        raise EnvironmentRefused(
            "HDE-shared variables present: " + ", ".join(present) + "; refusing to run"
        )
    missing = [name for name in SERVER_VARIABLES if not environ.get(name)]
    if missing:
        raise EnvironmentRefused("missing or empty: " + ", ".join(missing))
    app_id = environ["STREAM_APP_ID"]
    if app_id != EXPECTED_APP_ID:
        raise EnvironmentRefused(
            f"STREAM_APP_ID is not the development application {EXPECTED_APP_ID}"
        )
    return ServerCredentials(
        app_id=app_id,
        api_key=environ["STREAM_API_KEY"],
        _secret=environ["STREAM_API_SECRET"],
    )
