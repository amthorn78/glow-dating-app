"""Fail-closed served configuration, separate from future offline profile validation."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from .configuration_profiles import (
    LOOPBACK_HOSTS,
    ConfigurationIssue,
    IssueCategory,
    forbidden_configuration,
    validate_profile,
)


class ConfigurationError(ValueError):
    """Categorized diagnostics expose only fixed codes and known variable names."""

    def __init__(self, issue: ConfigurationIssue) -> None:
        self.category = issue.category
        self.code = issue.code
        self.variables = issue.variables
        super().__init__(issue.safe_message())


@dataclass(frozen=True)
class Configuration:
    environment: Literal["development", "test"]
    compatibility_provider: Literal["fixture"] = "fixture"
    allowed_hosts: tuple[str, ...] = LOOPBACK_HOSTS
    allowed_origins: tuple[str, ...] = ()
    timeout_seconds: int = 10
    retry_attempts: int = 3


def load_configuration(environ: Mapping[str, str]) -> Configuration:
    # Deny inherited connections by name without inspecting values.
    forbidden = forbidden_configuration(environ)
    if forbidden:
        raise ConfigurationError(forbidden[0])
    environment = environ.get("GLOW_ENV")
    if environment in {"staging", "production"}:
        raise ConfigurationError(
            ConfigurationIssue(
                IssueCategory.DISABLED, "runtime_activation_unavailable", ("GLOW_ENV",)
            )
        )
    validation = validate_profile(environ)
    if validation.errors:
        raise ConfigurationError(validation.errors[0])
    profile = validation.profile
    assert profile is not None
    # Offline feature definitions do not authorize additional served capabilities.
    if profile.service_role != "api" or any(
        feature.enabled and feature.name != "compatibility" for feature in profile.features
    ):
        raise ConfigurationError(
            ConfigurationIssue(IssueCategory.DISABLED, "capability_unimplemented")
        )
    if not next(feature.enabled for feature in profile.features if feature.name == "compatibility"):
        raise ConfigurationError(
            ConfigurationIssue(IssueCategory.CONTRADICTORY, "fixture_required")
        )
    hosts = profile.allowed_hosts
    return Configuration(
        environment="test" if environment == "test" else "development",
        allowed_hosts=hosts,
        allowed_origins=profile.allowed_origins,
        timeout_seconds=profile.timeout_seconds,
        retry_attempts=profile.retry_attempts,
    )
