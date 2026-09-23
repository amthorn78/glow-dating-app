"""Offline definition checks do not establish activation or real target ownership."""

from collections.abc import Mapping
from unittest import TestCase
from unittest.mock import patch

from glow_api.configuration import ConfigurationError, load_configuration
from glow_api.configuration_profiles import (
    FEATURE_ADAPTERS,
    FORBIDDEN_CONNECTION_NAMES,
    PROTECTED_SERVICE_IDS,
    REQUIRED_FUTURE_FEATURES,
    SECRET_SLOT_NAMES,
    SHARED_PROJECT_ID,
    IssueCategory,
    TargetIdentity,
    validate_profile,
)

# Synthetic test identifiers, never provisioned targets or secret values.
TARGET = TargetIdentity(
    SHARED_PROJECT_ID,
    "00000000-0000-4000-8000-000000000011",
    "00000000-0000-4000-8000-000000000012",
    "api",
    "staging",
)
SECRETS = frozenset(
    {"GLOW_DJANGO_SECRET_KEY", "GLOW_DATABASE_RUNTIME_SECRET"}
    | {FEATURE_ADAPTERS[name][1] for name in REQUIRED_FUTURE_FEATURES}
)


def future_definition():
    values = {
        "GLOW_ENV": "staging",
        "GLOW_ALLOWED_HOSTS": "api.example.test",
        "GLOW_ALLOWED_ORIGINS": "https://staff.example.test",
        "GLOW_RAILWAY_PROJECT_ID": TARGET.project_id,
        "GLOW_RAILWAY_ENVIRONMENT_ID": TARGET.environment_id,
        "GLOW_RAILWAY_SERVICE_ID": TARGET.service_id,
    }
    for name in REQUIRED_FUTURE_FEATURES:
        values[f"GLOW_FEATURE_{name.upper()}"] = "true"
        key = (
            "GLOW_COMPATIBILITY_PROVIDER"
            if name == "compatibility"
            else f"GLOW_{name.upper()}_ADAPTER"
        )
        values[key] = FEATURE_ADAPTERS[name][0]
    return values


class ProfileTests(TestCase):
    def future(self, overrides=None, targets=frozenset({TARGET}), secrets=SECRETS):
        values = future_definition()
        values.update(overrides or {})
        return validate_profile(values, owned_targets=targets, secret_names=secrets)

    def test_valid_future_definition_never_activates_or_calls_network(self):
        with patch("socket.create_connection", side_effect=AssertionError("network forbidden")):
            result = self.future()
        self.assertTrue(result.is_valid, result.errors)
        self.assertFalse(result.profile.runtime_available)
        self.assertIn(
            "runtime_activation_unavailable", {i.code for i in result.disabled_capabilities}
        )
        with self.assertRaises(ConfigurationError) as error:
            load_configuration(future_definition())
        self.assertEqual(error.exception.category, IssueCategory.DISABLED)

    def test_production_requires_own_target_manifest(self):
        self.assertFalse(self.future({"GLOW_ENV": "production"}).is_valid)
        target = TargetIdentity(
            TARGET.project_id, TARGET.environment_id, TARGET.service_id, "api", "production"
        )
        self.assertTrue(self.future({"GLOW_ENV": "production"}, frozenset({target})).is_valid)

    def test_categories_distinguish_actual_defects(self):
        for values, code, category in (
            ({}, "environment_required", IssueCategory.MISSING),
            ({"GLOW_ENV": "dev"}, "environment_unsupported", IssueCategory.UNSUPPORTED),
            (
                {"GLOW_ENV": "test", "GLOW_DEBUG": "yes"},
                "boolean_required",
                IssueCategory.MALFORMED,
            ),
            (
                {"GLOW_ENV": "test", "GLOW_DEBUG": "true"},
                "unsafe_security_default",
                IssueCategory.CONTRADICTORY,
            ),
        ):
            result = validate_profile(values)
            self.assertIn((code, category), {(i.code, i.category) for i in result.errors})
            self.assertIsNone(result.profile)

    def test_explicit_host_subset_is_not_silently_widened(self):
        config = load_configuration({"GLOW_ENV": "test", "GLOW_ALLOWED_HOSTS": "localhost"})
        self.assertEqual(config.allowed_hosts, ("localhost",))
        self.assertIn("testserver", load_configuration({"GLOW_ENV": "test"}).allowed_hosts)

    def test_optional_disabled_does_not_block_fixture_development(self):
        result = validate_profile({"GLOW_ENV": "test"})
        self.assertTrue(result.is_valid)
        self.assertTrue(result.disabled_capabilities)
        self.assertEqual(load_configuration({"GLOW_ENV": "test"}).environment, "test")

    def test_mandatory_capabilities_and_secret_slots_cannot_be_waived(self):
        for feature in REQUIRED_FUTURE_FEATURES:
            result = self.future({f"GLOW_FEATURE_{feature.upper()}": "false"})
            self.assertIn("required_future_feature", {i.code for i in result.errors})
        result = self.future(secrets=frozenset())
        self.assertEqual(
            {i.variables[0] for i in result.errors if i.code == "secret_slot_required"}, SECRETS
        )

    def test_fixture_security_and_billing_cannot_enter_future_profile(self):
        for override in (
            {"GLOW_COMPATIBILITY_PROVIDER": "fixture"},
            {"GLOW_SECURE_TRANSPORT": "false"},
            {"GLOW_DEBUG": "true"},
            {"GLOW_ALLOWED_HOSTS": "localhost"},
            {"GLOW_FEATURE_BILLING": "true", "GLOW_BILLING_ADAPTER": "revenuecat"},
        ):
            self.assertFalse(self.future(override).is_valid)

    def test_protected_target_rejected_even_with_misdeclared_ownership(self):
        self.assertFalse(self.future(targets=frozenset()).is_valid)
        for service in PROTECTED_SERVICE_IDS:
            target = TargetIdentity(
                SHARED_PROJECT_ID, TARGET.environment_id, service, "api", "staging"
            )
            self.assertFalse(
                self.future({"GLOW_RAILWAY_SERVICE_ID": service}, frozenset({target})).is_valid
            )
        for override in (
            {"GLOW_RAILWAY_PROJECT_ID": "00000000-0000-4000-8000-000000000013"},
            {"GLOW_RAILWAY_SERVICE_ID": "not-a-uuid"},
            {"GLOW_RAILWAY_ENVIRONMENT_ID": ""},
        ):
            self.assertFalse(self.future(override).is_valid)

    def test_hosts_and_origins_reject_malformed_or_unsafe_without_echo(self):
        for value in (
            "*",
            ".example.test",
            "https://example.test",
            "api.example.test:443",
            "a,b,b",
            "bad value",
            "999.999.999.999",
            "A.example.test",
        ):
            self.assertFalse(self.future({"GLOW_ALLOWED_HOSTS": value}).is_valid)
        for value in (
            "http://api.example.test",
            "https://user:sentinel@api.example.test",
            "https://@api.example.test",
            "https://api.example.test:",
            "https://api.example.test/path",
            "https://api.example.test?sentinel",
            "https://api.example.test/#sentinel",
            "https://api.example.test:bad",
            "https://api.example.test:0",
            "https://api.example.test?",
            "https://api.example.test\n",
        ):
            result = self.future({"GLOW_ALLOWED_ORIGINS": value})
            self.assertFalse(result.is_valid)
            self.assertNotIn(value, repr(result))

    def test_integer_and_combined_budget_limits(self):
        for name, values in {
            "GLOW_PROVIDER_TIMEOUT_SECONDS": ("0", "31", "NaN", "1.5", " 1"),
            "GLOW_RETRY_ATTEMPTS": ("0", "4", "-1"),
            "GLOW_RETRY_BUDGET_SECONDS": ("0", "121", "inf"),
        }.items():
            for value in values:
                self.assertFalse(validate_profile({"GLOW_ENV": "test", name: value}).is_valid)
        for budget, valid in (("89", False), ("90", True)):
            self.assertEqual(
                validate_profile(
                    {
                        "GLOW_ENV": "test",
                        "GLOW_PROVIDER_TIMEOUT_SECONDS": "30",
                        "GLOW_RETRY_ATTEMPTS": "3",
                        "GLOW_RETRY_BUDGET_SECONDS": budget,
                    }
                ).is_valid,
                valid,
            )

    def test_worker_definition_requires_broker_and_remains_inactive(self):
        target = TargetIdentity(
            TARGET.project_id, TARGET.environment_id, TARGET.service_id, "worker", "staging"
        )
        result = self.future({"GLOW_SERVICE_ROLE": "worker"}, frozenset({target}))
        self.assertIn("worker_broker_required", {i.code for i in result.errors})
        result = self.future(
            {"GLOW_SERVICE_ROLE": "worker", "GLOW_BROKER_ADAPTER": "redis"},
            frozenset({target}),
            SECRETS | {"GLOW_BROKER_SECRET"},
        )
        self.assertTrue(result.is_valid)
        with self.assertRaises(ConfigurationError):
            load_configuration({"GLOW_ENV": "test", "GLOW_SERVICE_ROLE": "worker"})

    def test_connection_and_secret_values_are_never_read(self):
        class UnreadableSecrets(Mapping):
            def __init__(self, name):
                self.name = name

            def __iter__(self):
                return iter(("GLOW_ENV", self.name))

            def __len__(self):
                return 2

            def __getitem__(self, name):
                if name == self.name:
                    raise AssertionError("secret read")
                if name == "GLOW_ENV":
                    return "test"
                raise KeyError(name)

        for name in FORBIDDEN_CONNECTION_NAMES | SECRET_SLOT_NAMES:
            with self.subTest(name=name), self.assertRaises(ConfigurationError):
                load_configuration(UnreadableSecrets(name))

    def test_unknown_and_public_names_do_not_leak_supplied_names_or_values(self):
        for name in ("EXPO_PUBLIC_PROVIDER_TOKEN", "EXPO_PUBLIC_DISGUISED_CREDENTIAL", "GLOW_TYPO"):
            with self.assertRaises(ConfigurationError) as error:
                load_configuration({"GLOW_ENV": "test", name: "synthetic-sensitive-sentinel"})
            self.assertNotIn(name, str(error.exception))
            self.assertNotIn("synthetic-sensitive-sentinel", str(error.exception))
