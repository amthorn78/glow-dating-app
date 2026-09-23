from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from glow_api.fixtures import recommendations


class EndpointTests(SimpleTestCase):
    # SimpleTestCase disallows all database access. No TestCase/DB test runner
    # setup, fixtures loaded into SQL, or SQLite connection is used.
    databases = set()

    def test_no_database_backend_or_auth_apps_installed(self):
        self.assertEqual(settings.DATABASES["default"]["ENGINE"], "django.db.backends.dummy")
        self.assertNotIn("django.contrib.auth", settings.INSTALLED_APPS)
        self.assertNotIn("django.contrib.sessions", settings.INSTALLED_APPS)

    def test_live_and_ready_are_distinct_without_network_or_database(self):
        with patch("socket.socket", side_effect=AssertionError("No network in smoke views")):
            live = self.client.get("/health/live")
            ready = self.client.get("/health/ready")
        self.assertEqual(live.status_code, 200)
        self.assertEqual(live.json(), {"status": "alive"})
        self.assertEqual(ready.status_code, 503)
        self.assertEqual(ready.json()["status"], "not_ready")
        self.assertEqual(ready.json()["mode"], "fixture")

    def test_synthetic_route_is_deterministic_and_never_claims_compatibility(self):
        with patch("socket.socket", side_effect=AssertionError("No provider network")):
            first = self.client.get("/api/v1/development/recommendations")
            second = self.client.get("/api/v1/development/recommendations")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), second.json())
        body = first.json()
        self.assertEqual(set(body), {"mode", "contract_version", "items"})
        self.assertEqual(body["mode"], "fixture")
        self.assertEqual(body["contract_version"], "gapp-dev-v1")
        self.assertGreater(len(body["items"]), 0)
        for item in body["items"]:
            self.assertEqual(
                set(item), {"profile_id", "display_name", "age", "summary", "compatibility"}
            )
            self.assertTrue(item["profile_id"].startswith("fixture-"))
            self.assertGreaterEqual(item["age"], 18)
            self.assertEqual(item["compatibility"], {"status": "pending", "source": "fixture"})

    def test_response_mutation_does_not_change_later_fixture_data(self):
        changed = recommendations()
        changed["items"][0]["display_name"] = "Changed"
        changed["items"][0]["compatibility"]["status"] = "unsupported"
        fresh = recommendations()
        self.assertNotEqual(fresh["items"][0]["display_name"], "Changed")
        self.assertEqual(fresh["items"][0]["compatibility"]["status"], "pending")

    @override_settings(GLOW_ENV="production")
    def test_route_guard_fails_closed_even_if_url_was_loaded_in_test(self):
        self.assertEqual(self.client.get("/api/v1/development/recommendations").status_code, 404)

    def test_reads_are_not_cached_and_writes_are_rejected(self):
        for path in ("/health/live", "/health/ready", "/api/v1/development/recommendations"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response["Cache-Control"], "no-store")
                self.assertEqual(response["X-Content-Type-Options"], "nosniff")
                for method in ("post", "put", "patch", "delete"):
                    self.assertEqual(getattr(self.client, method)(path).status_code, 405)

    def test_unrecognized_hosts_are_rejected(self):
        self.assertEqual(
            self.client.get("/health/live", HTTP_HOST="unexpected.invalid").status_code, 400
        )

    def test_android_emulator_host_alias_is_allowed_without_arbitrary_private_hosts(self):
        self.assertEqual(
            self.client.get(
                "/api/v1/development/recommendations", HTTP_HOST="10.0.2.2:8000"
            ).status_code,
            200,
        )
        for host in ("10.0.2.3:8000", "192.168.1.12:8000", "10.0.2.2.example.test:8000"):
            with self.subTest(host=host):
                self.assertEqual(self.client.get("/health/live", HTTP_HOST=host).status_code, 400)

    def test_no_account_or_production_recommendation_route_exists(self):
        for path in ("/api/v1/recommendations", "/api/v1/auth/login", "/admin/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
