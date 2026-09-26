"""Finding 3: preflight accepts exactly one dashboard user, the one Nathan confirmed."""

import unittest
from datetime import UTC, datetime
from typing import Any

import tests  # noqa: F401
from glow_stream_proof.proof_run import RunStopped, _utc_minute
from tests.fakes import make_run

CONFIRMED_NS = int(datetime(2026, 9, 24, 13, 7, 41, tzinfo=UTC).timestamp()) * 10**9


def dashboard_user(uid: str, created_at: Any = CONFIRMED_NS) -> dict[str, Any]:
    return {
        "id": uid,
        "role": "admin",
        "custom": {"dashboard_user": True, "staff_user": True},
        "created_at": created_at,
    }


class PreflightTest(unittest.TestCase):
    def preflight(self, users: list[dict[str, Any]], *, accept: bool = True) -> dict[str, Any]:
        run, server = make_run()
        run.accept_dashboard_user = accept
        for user in users:
            server.users[user["id"]] = user
        return run.preflight()

    def test_exactly_the_confirmed_user_is_accepted(self) -> None:
        result = self.preflight([dashboard_user("owner")])
        self.assertEqual(result["dashboard_users_present"], 1)
        iso = "2026-09-24T13:07:41.123456789Z"
        self.assertEqual(
            self.preflight([dashboard_user("owner", iso)])["dashboard_users_present"], 1
        )

    def test_two_dashboard_users_stop_the_run(self) -> None:
        with self.assertRaises(RunStopped) as stopped:
            self.preflight([dashboard_user("owner"), dashboard_user("second")])
        self.assertIn(
            "2 dashboard administrator users; exactly one is accepted", str(stopped.exception)
        )
        self.assertNotIn("owner", str(stopped.exception))  # no identifier is recorded

    def test_no_dashboard_user_stops_the_run_when_one_is_expected(self) -> None:
        with self.assertRaises(RunStopped) as stopped:
            self.preflight([])
        self.assertIn("0 dashboard administrator users", str(stopped.exception))

    def test_another_creation_time_stops_the_run(self) -> None:
        other = CONFIRMED_NS + 3600 * 10**9
        with self.assertRaises(RunStopped) as stopped:
            self.preflight([dashboard_user("owner", other)])
        self.assertIn("creation time", str(stopped.exception))

    def test_without_the_flag_the_dashboard_user_stops_the_run(self) -> None:
        with self.assertRaises(RunStopped):
            self.preflight([dashboard_user("owner")], accept=False)

    def test_utc_minute(self) -> None:
        self.assertEqual(_utc_minute(CONFIRMED_NS), "2026-09-24T13:07")
        self.assertEqual(_utc_minute(str(CONFIRMED_NS)), "2026-09-24T13:07")
        self.assertEqual(_utc_minute(CONFIRMED_NS // 10**6), "2026-09-24T13:07")
        self.assertEqual(_utc_minute("2026-09-24T15:07:41+02:00"), "2026-09-24T13:07")
        self.assertEqual(_utc_minute("2026-09-24T13:07:41.123456789Z"), "2026-09-24T13:07")
        self.assertIsNone(_utc_minute("2026-09-24T13:07:41"))  # no time zone
        self.assertIsNone(_utc_minute(None))
        self.assertIsNone(_utc_minute("yesterday"))


if __name__ == "__main__":
    unittest.main()
