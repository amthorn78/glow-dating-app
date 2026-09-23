import os
import subprocess
import sys
from unittest import TestCase

from glow_api.configuration import ConfigurationError, load_configuration


class ConfigurationTests(TestCase):
    def test_environment_must_be_explicit(self):
        with self.assertRaises(ConfigurationError):
            load_configuration({})

    def test_unknown_or_blank_environment_fails_closed(self):
        for environment in ("", "dev", "PRODUCTION", " production "):
            with self.subTest(environment=environment), self.assertRaises(ConfigurationError):
                load_configuration({"GLOW_ENV": environment})

    def test_fixture_allowed_only_in_development_and_test(self):
        for environment in ("development", "test"):
            with self.subTest(environment=environment):
                self.assertEqual(
                    load_configuration({"GLOW_ENV": environment}).environment, environment
                )

    def test_live_environments_reject_all_provider_choices(self):
        for environment in ("staging", "production"):
            for provider in ("fixture", "live", ""):
                with self.subTest(environment=environment, provider=provider):
                    with self.assertRaises(ConfigurationError):
                        load_configuration(
                            {"GLOW_ENV": environment, "GLOW_COMPATIBILITY_PROVIDER": provider}
                        )

    def test_unknown_provider_rejected(self):
        with self.assertRaises(ConfigurationError):
            load_configuration({"GLOW_ENV": "test", "GLOW_COMPATIBILITY_PROVIDER": "live"})

    def test_connection_values_rejected_and_not_disclosed(self):
        for name in ("DATABASE_URL", "GLOW_DATABASE_URL", "HDE_API_URL", "HDE_API_TOKEN"):
            with self.subTest(name=name):
                marker = "synthetic-sensitive-value-not-a-real-secret"
                with self.assertRaises(ConfigurationError) as result:
                    load_configuration({"GLOW_ENV": "test", name: marker})
                self.assertNotIn(marker, str(result.exception))

    def test_process_cannot_boot_without_opt_in_or_in_production(self):
        for environment in (None, "production"):
            env = {"PATH": os.environ["PATH"], "DJANGO_SETTINGS_MODULE": "glow_api.settings"}
            if environment:
                env["GLOW_ENV"] = environment
            with self.subTest(environment=environment):
                process = subprocess.run(
                    [sys.executable, "-c", "import django; django.setup()"],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                self.assertNotEqual(process.returncode, 0)
                self.assertIn("ImproperlyConfigured", process.stderr)
