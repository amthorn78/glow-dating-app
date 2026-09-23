"""Fail-closed configuration for the P01 fixture foundation.

No production settings or credentials are inferred. Later phases must replace
the explicit production refusal only after implementing real providers.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal


class ConfigurationError(ValueError):
    """Invalid or unsupported application configuration; values are never echoed."""


@dataclass(frozen=True)
class Configuration:
    environment: Literal["development", "test"]
    compatibility_provider: Literal["fixture"] = "fixture"


def load_configuration(environ: Mapping[str, str]) -> Configuration:
    environment = environ.get("GLOW_ENV")
    provider = environ.get("GLOW_COMPATIBILITY_PROVIDER", "fixture")
    if environment is None:
        raise ConfigurationError("GLOW_ENV must be explicitly set; no default environment exists.")
    if environment in {"staging", "production"}:
        if provider == "fixture":
            raise ConfigurationError("Fixture providers are forbidden in staging and production.")
        raise ConfigurationError(
            "Staging and production are unavailable in this isolated development foundation."
        )
    if environment not in {"development", "test"}:
        raise ConfigurationError("GLOW_ENV must identify a supported environment.")
    if provider != "fixture":
        raise ConfigurationError("Only the fixture compatibility provider is implemented.")

    # Even unused inherited connection values indicate an incorrectly scoped
    # process. Reject them without reading, parsing, logging, or using values.
    forbidden_names = ("DATABASE_URL", "GLOW_DATABASE_URL", "HDE_API_URL", "HDE_API_TOKEN")
    if any(name in environ for name in forbidden_names):
        raise ConfigurationError(
            "Database and live HDE connection configuration are forbidden in the fixture process."
        )
    if environment == "development":
        return Configuration(environment="development")
    return Configuration(environment="test")
