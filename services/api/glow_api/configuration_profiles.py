"""Offline profile definitions, never an activation or credential-loading path."""

import ipaddress
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal, cast
from urllib.parse import urlsplit
from uuid import UUID

Environment = Literal["development", "test", "staging", "production"]
SHARED_PROJECT_ID = "ce01529f-679f-4f52-a979-23113299a59b"
PROTECTED_SERVICE_IDS = frozenset(
    {
        "62e7b993-6d30-48b4-9059-c1884b16e90b",  # HDE
        "bfedf816-d6d4-4155-b495-cd6416e91e49",  # legacy backend
        "c4d54416-d1ab-4818-898b-9b9be03bc69a",  # protected PostgreSQL
        "87b4810c-3e23-4d27-b7fc-0bca7131ed37",  # protected Redis
    }
)
LOOPBACK_HOSTS = ("localhost", "127.0.0.1", "[::1]", "10.0.2.2")
# Presence is checked before reading any connection/credential value, including empty values.
FORBIDDEN_CONNECTION_NAMES = frozenset(
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
PUBLIC_NAMES = frozenset({"EXPO_PUBLIC_GLOW_MODE", "EXPO_PUBLIC_GLOW_API_BASE_URL"})


class IssueCategory(StrEnum):
    MISSING = "missing"
    MALFORMED = "malformed"
    CONTRADICTORY = "contradictory"
    UNSUPPORTED = "unsupported"
    DISABLED = "disabled"


@dataclass(frozen=True)
class ConfigurationIssue:
    category: IssueCategory
    code: str
    variables: tuple[str, ...] = ()

    def safe_message(self) -> str:
        return f"{self.category.value}: {self.code} ({', '.join(self.variables)})"


@dataclass(frozen=True)
class TargetIdentity:
    """Non-secret identity supplied from an independently verified ownership manifest."""

    project_id: str
    environment_id: str
    service_id: str
    role: Literal["api", "worker"]
    environment: Literal["staging", "production"]


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    enabled: bool
    adapter: str


@dataclass(frozen=True)
class ConfigurationProfile:
    environment: Environment
    service_role: Literal["api", "worker"]
    allowed_hosts: tuple[str, ...] = field(repr=False)
    allowed_origins: tuple[str, ...] = field(repr=False)
    timeout_seconds: int
    retry_attempts: int
    retry_budget_seconds: int
    persistence_adapter: Literal["disabled", "postgresql"]
    broker_adapter: Literal["disabled", "redis"]
    features: tuple[FeatureDefinition, ...]
    target: TargetIdentity | None = field(repr=False)
    # Records only known required slot names; never credential values or references.
    required_secret_names: frozenset[str]
    runtime_available: Literal[False] = False


@dataclass(frozen=True)
class ProfileValidation:
    profile: ConfigurationProfile | None
    errors: tuple[ConfigurationIssue, ...]
    disabled_capabilities: tuple[ConfigurationIssue, ...]

    @property
    def is_valid(self) -> bool:
        """Definition consistency only; never readiness or permission to start."""
        return not self.errors and self.profile is not None


# New future configuration choices, not installed/activated adapters or vendor wire contracts.
FEATURE_ADAPTERS = {
    "compatibility": ("hde", "GLOW_HDE_API_TOKEN"),
    "media": ("cloudflare", "GLOW_MEDIA_API_TOKEN"),
    "mail": ("smtp", "GLOW_MAIL_CREDENTIAL"),
    "chat": ("stream", "GLOW_CHAT_API_SECRET"),
    "push": ("expo", "GLOW_PUSH_ACCESS_TOKEN"),
    "monitoring": ("disabled", "GLOW_MONITORING_TOKEN"),
    "billing": ("revenuecat", "GLOW_BILLING_WEBHOOK_SECRET"),
}
REQUIRED_FUTURE_FEATURES = frozenset({"compatibility", "media", "mail", "chat", "push"})
SECRET_SLOT_NAMES = frozenset(
    {
        "GLOW_DJANGO_SECRET_KEY",
        "GLOW_DATABASE_RUNTIME_SECRET",
        "GLOW_DATABASE_MIGRATION_SECRET",
        "GLOW_BROKER_SECRET",
        *(secret for _, secret in FEATURE_ADAPTERS.values()),
    }
)
PROFILE_NAMES = frozenset(
    {
        "GLOW_ENV",
        "GLOW_SERVICE_ROLE",
        "GLOW_DEBUG",
        "GLOW_SECURE_TRANSPORT",
        "GLOW_ALLOWED_HOSTS",
        "GLOW_ALLOWED_ORIGINS",
        "GLOW_PROVIDER_TIMEOUT_SECONDS",
        "GLOW_RETRY_ATTEMPTS",
        "GLOW_RETRY_BUDGET_SECONDS",
        "GLOW_PERSISTENCE_ADAPTER",
        "GLOW_BROKER_ADAPTER",
        "GLOW_COMPATIBILITY_PROVIDER",
        "GLOW_RAILWAY_PROJECT_ID",
        "GLOW_RAILWAY_ENVIRONMENT_ID",
        "GLOW_RAILWAY_SERVICE_ID",
        *(f"GLOW_FEATURE_{name.upper()}" for name in FEATURE_ADAPTERS),
        *(f"GLOW_{name.upper()}_ADAPTER" for name in FEATURE_ADAPTERS if name != "compatibility"),
    }
)


def forbidden_configuration(environ: Mapping[str, str]) -> tuple[ConfigurationIssue, ...]:
    issues: list[ConfigurationIssue] = []
    present = tuple(sorted((FORBIDDEN_CONNECTION_NAMES | SECRET_SLOT_NAMES).intersection(environ)))
    if present:
        issues.append(
            ConfigurationIssue(IssueCategory.CONTRADICTORY, "inherited_connection", present)
        )
    if any(
        name.startswith("GLOW_")
        and name not in PROFILE_NAMES
        and name not in FORBIDDEN_CONNECTION_NAMES
        and name not in SECRET_SLOT_NAMES
        for name in environ
    ):
        issues.append(ConfigurationIssue(IssueCategory.UNSUPPORTED, "unknown_glow_variable"))
    # Closed public-name allowlist: a renamed token cannot evade keyword heuristics.
    if any(name.startswith("EXPO_PUBLIC_") and name not in PUBLIC_NAMES for name in environ):
        issues.append(
            ConfigurationIssue(IssueCategory.CONTRADICTORY, "unapproved_mobile_public_variable")
        )
    return tuple(issues)


def _host_valid(value: str) -> bool:
    if value == "[::1]":
        return True
    if not value or len(value) > 253 or value != value.lower():
        return False
    if all(part.isdigit() for part in value.split(".")):
        try:
            ipaddress.IPv4Address(value)
            return True
        except ValueError:
            return False
    return all(
        re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part) is not None
        for part in value.split(".")
    )


def _origin_valid(value: str, future: bool) -> bool:
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value):
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        return False
    if not host or (port is not None and port < 1):
        return False
    if (
        parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or parsed.netloc.endswith(":")
    ):
        return False
    if "?" in value or "#" in value or not _host_valid(f"[{host}]" if ":" in host else host):
        return False
    if parsed.scheme == "https":
        return True
    return (
        not future
        and parsed.scheme == "http"
        and host in {"localhost", "127.0.0.1", "::1", "10.0.2.2"}
    )


def validate_profile(
    environ: Mapping[str, str],
    *,
    owned_targets: frozenset[TargetIdentity] = frozenset(),
    secret_names: frozenset[str] = frozenset(),
) -> ProfileValidation:
    """Validate offline definitions using slot presence and verified non-secret targets.

    Does no I/O, never reads connection/secret values, never loads adapters, and
    returns runtime_available=False even for a fully consistent future profile.
    The caller owns manifest provenance; matching UUIDs alone are not ownership proof.
    """
    errors = list(forbidden_configuration(environ))
    disabled: list[ConfigurationIssue] = []

    def issue(category: IssueCategory, code: str, *names: str) -> None:
        errors.append(ConfigurationIssue(category, code, names))

    def integer(name: str, default: int, lower: int, upper: int) -> int:
        value = environ.get(name, str(default))
        if re.fullmatch(r"[0-9]{1,5}", value) is None or not lower <= int(value) <= upper:
            issue(IssueCategory.MALFORMED, "integer_out_of_bounds", name)
            return default
        return int(value)

    def boolean(name: str, default: bool) -> bool:
        value = environ.get(name, "true" if default else "false")
        if value not in {"true", "false"}:
            issue(IssueCategory.MALFORMED, "boolean_required", name)
        return value == "true"

    raw_environment = environ.get("GLOW_ENV")
    if raw_environment is None:
        issue(IssueCategory.MISSING, "environment_required", "GLOW_ENV")
    elif raw_environment not in {"development", "test", "staging", "production"}:
        issue(IssueCategory.UNSUPPORTED, "environment_unsupported", "GLOW_ENV")
    else:
        environment = cast(Environment, raw_environment)
        future = environment in {"staging", "production"}
        raw_role = environ.get("GLOW_SERVICE_ROLE", "api")
        role: Literal["api", "worker"] = "worker" if raw_role == "worker" else "api"
        if raw_role not in {"api", "worker"}:
            issue(IssueCategory.UNSUPPORTED, "service_role_unsupported", "GLOW_SERVICE_ROLE")
        debug = boolean("GLOW_DEBUG", False)
        secure = boolean("GLOW_SECURE_TRANSPORT", future)
        if debug or (future and not secure):
            issue(
                IssueCategory.CONTRADICTORY,
                "unsafe_security_default",
                "GLOW_DEBUG",
                "GLOW_SECURE_TRANSPORT",
            )
        default_hosts = (*LOOPBACK_HOSTS, "testserver") if environment == "test" else LOOPBACK_HOSTS
        host_value = environ.get("GLOW_ALLOWED_HOSTS", "" if future else ",".join(default_hosts))
        hosts = tuple(host_value.split(",")) if host_value else ()
        if not hosts:
            issue(IssueCategory.MISSING, "hosts_required", "GLOW_ALLOWED_HOSTS")
        elif (
            len(hosts) > 20
            or len(set(hosts)) != len(hosts)
            or not all(_host_valid(host) for host in hosts)
        ):
            issue(IssueCategory.MALFORMED, "host_allowlist_invalid", "GLOW_ALLOWED_HOSTS")
        elif not future and any(host not in (*LOOPBACK_HOSTS, "testserver") for host in hosts):
            issue(IssueCategory.CONTRADICTORY, "fixture_host_scope", "GLOW_ALLOWED_HOSTS")
        elif future and any(host in (*LOOPBACK_HOSTS, "testserver") for host in hosts):
            issue(IssueCategory.CONTRADICTORY, "future_host_scope", "GLOW_ALLOWED_HOSTS")
        origin_value = environ.get("GLOW_ALLOWED_ORIGINS", "")
        origins = tuple(origin_value.split(",")) if origin_value else ()
        if (
            len(origins) > 20
            or len(set(origins)) != len(origins)
            or not all(_origin_valid(origin, future) for origin in origins)
        ):
            issue(IssueCategory.MALFORMED, "origin_allowlist_invalid", "GLOW_ALLOWED_ORIGINS")
        timeout = integer("GLOW_PROVIDER_TIMEOUT_SECONDS", 10, 1, 30)
        attempts = integer("GLOW_RETRY_ATTEMPTS", 3, 1, 3)
        budget = integer("GLOW_RETRY_BUDGET_SECONDS", 45, 1, 120)
        if timeout * attempts > budget:
            issue(
                IssueCategory.CONTRADICTORY,
                "retry_budget_insufficient",
                "GLOW_RETRY_BUDGET_SECONDS",
            )
        persistence = environ.get(
            "GLOW_PERSISTENCE_ADAPTER", "postgresql" if future else "disabled"
        )
        broker = environ.get("GLOW_BROKER_ADAPTER", "disabled")
        if persistence not in {"disabled", "postgresql"} or broker not in {"disabled", "redis"}:
            issue(
                IssueCategory.UNSUPPORTED,
                "storage_adapter_unsupported",
                "GLOW_PERSISTENCE_ADAPTER",
                "GLOW_BROKER_ADAPTER",
            )
        if (future and persistence != "postgresql") or (
            not future and (persistence != "disabled" or broker != "disabled")
        ):
            issue(
                IssueCategory.CONTRADICTORY,
                "storage_mode_conflict",
                "GLOW_PERSISTENCE_ADAPTER",
                "GLOW_BROKER_ADAPTER",
            )
        if future and role == "worker" and broker != "redis":
            issue(IssueCategory.MISSING, "worker_broker_required", "GLOW_BROKER_ADAPTER")
        required_secrets = (
            {"GLOW_DJANGO_SECRET_KEY", "GLOW_DATABASE_RUNTIME_SECRET"} if future else set()
        )
        if future and broker == "redis":
            required_secrets.add("GLOW_BROKER_SECRET")
        features: list[FeatureDefinition] = []
        for name, (planned_adapter, secret) in FEATURE_ADAPTERS.items():
            enabled_name = f"GLOW_FEATURE_{name.upper()}"
            adapter_name = (
                "GLOW_COMPATIBILITY_PROVIDER"
                if name == "compatibility"
                else f"GLOW_{name.upper()}_ADAPTER"
            )
            enabled = boolean(enabled_name, name == "compatibility" and not future)
            adapter = environ.get(adapter_name, "fixture" if enabled and not future else "disabled")
            if adapter not in {"disabled", "fixture", planned_adapter}:
                issue(IssueCategory.UNSUPPORTED, "adapter_unsupported", adapter_name)
            if future and adapter == "fixture":
                issue(IssueCategory.CONTRADICTORY, "fixture_forbidden", adapter_name)
            if enabled == (adapter == "disabled"):
                issue(
                    IssueCategory.CONTRADICTORY,
                    "feature_adapter_conflict",
                    enabled_name,
                    adapter_name,
                )
            if future and name in REQUIRED_FUTURE_FEATURES and not enabled:
                issue(IssueCategory.MISSING, "required_future_feature", enabled_name)
            if not future and enabled and adapter != "fixture":
                issue(IssueCategory.UNSUPPORTED, "live_adapter_unimplemented", adapter_name)
            if name == "billing" and enabled:
                issue(IssueCategory.DISABLED, "billing_decision_pending", enabled_name)
            if enabled and future:
                required_secrets.add(secret)
            if not enabled or future:
                disabled.append(
                    ConfigurationIssue(
                        IssueCategory.DISABLED, "adapter_not_activated", (adapter_name,)
                    )
                )
            features.append(FeatureDefinition(name, enabled, adapter))
        target = None
        target_names = (
            "GLOW_RAILWAY_PROJECT_ID",
            "GLOW_RAILWAY_ENVIRONMENT_ID",
            "GLOW_RAILWAY_SERVICE_ID",
        )
        if future:
            raw_ids = tuple(environ.get(name, "") for name in target_names)
            for name, value in zip(target_names, raw_ids, strict=True):
                if not value:
                    issue(IssueCategory.MISSING, "target_identity_required", name)
                else:
                    try:
                        valid = str(UUID(value)) == value
                    except ValueError:
                        valid = False
                    if not valid:
                        issue(IssueCategory.MALFORMED, "target_uuid_invalid", name)
            target = TargetIdentity(
                raw_ids[0],
                raw_ids[1],
                raw_ids[2],
                role,
                "staging" if environment == "staging" else "production",
            )
            if target.project_id != SHARED_PROJECT_ID or target.service_id in PROTECTED_SERVICE_IDS:
                issue(
                    IssueCategory.CONTRADICTORY, "target_protected_or_wrong_project", *target_names
                )
            if target not in owned_targets:
                issue(IssueCategory.MISSING, "verified_app_target_required", *target_names)
        elif any(name in environ for name in target_names):
            issue(IssueCategory.CONTRADICTORY, "local_target_forbidden", *target_names)
        for secret in sorted(required_secrets - secret_names):
            issue(IssueCategory.MISSING, "secret_slot_required", secret)
        disabled.append(
            ConfigurationIssue(IssueCategory.DISABLED, "runtime_activation_unavailable")
        )
        profile = ConfigurationProfile(
            environment,
            role,
            hosts,
            origins,
            timeout,
            attempts,
            budget,
            cast(Literal["disabled", "postgresql"], persistence),
            cast(Literal["disabled", "redis"], broker),
            tuple(features),
            target,
            frozenset(required_secrets),
        )
        return ProfileValidation(None if errors else profile, tuple(errors), tuple(disabled))
    return ProfileValidation(None, tuple(errors), tuple(disabled))
