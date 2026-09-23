"""Validated artifact entrypoint; fixture execution remains loopback-only."""

import json
import os
import re
import sys
from collections.abc import Mapping

from .configuration import ConfigurationError, load_configuration


class RuntimeConfigurationError(ValueError):
    """Fixed, value-free diagnostic for the process boundary."""


def runtime_command(environ: Mapping[str, str]) -> list[str]:
    """Validate before server/app imports and return fixed executable arguments."""
    configuration = load_configuration(environ)
    if any(name.startswith("GUNICORN_") for name in environ):
        raise RuntimeConfigurationError("Server override configuration is unsupported.")
    if environ.get("DJANGO_SETTINGS_MODULE", "glow_api.settings") != "glow_api.settings":
        raise RuntimeConfigurationError("Settings-module override is unsupported.")
    port = environ.get("PORT", "8000")
    if not re.fullmatch(r"[0-9]{4,5}", port) or not 1024 <= int(port) <= 65535:
        raise RuntimeConfigurationError("PORT must be an unprivileged TCP port.")
    return [
        sys.executable,
        "-m",
        "gunicorn",
        "--config",
        "python:glow_api.gunicorn_conf",
        "--bind",
        f"127.0.0.1:{int(port)}",
        "--workers",
        "1",
        "--worker-class",
        "sync",
        "--timeout",
        str(configuration.timeout_seconds),
        "--graceful-timeout",
        "5",
        "--keep-alive",
        "2",
        "--limit-request-line",
        "2048",
        "--limit-request-fields",
        "32",
        "--limit-request-field_size",
        "4096",
        "--forwarded-allow-ips",
        "",
        "--max-requests",
        "1000",
        "--worker-tmp-dir",
        "/tmp",
        "--preload",
        "glow_api.wsgi:application",
    ]


def main() -> None:
    try:
        if len(sys.argv) != 1:
            raise RuntimeConfigurationError("Entrypoint arguments are unsupported.")
        command = runtime_command(os.environ)
    except (ConfigurationError, RuntimeConfigurationError):
        # Do not print config values, exception traces, argv or inherited env.
        print(json.dumps({"event": "runtime_refused", "code": "configuration_invalid"}), flush=True)
        raise SystemExit(78) from None
    environ = dict(os.environ)
    environ["DJANGO_SETTINGS_MODULE"] = "glow_api.settings"
    # Replacing this process makes Gunicorn the signal recipient/PID 1 in Docker.
    # There is no shell, migration hook, supervisor loop or startup network probe.
    os.execvpe(command[0], command, environ)


if __name__ == "__main__":
    main()
