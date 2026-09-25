import copy
import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import configuration as conf

ROLES = ["admin", "anonymous", "channel_member", "channel_moderator", "guest", "moderator", "user"]


def _type(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "automod": "disabled",
        "automod_behavior": "flag",
        "max_message_length": 5000,
        "typing_events": True,
        "reactions": True,
        "commands": [{"name": "giphy"}],
        "grants": {
            "user": ["create-channel", "read-channel-owner"],
            "channel_member": ["read-channel", "create-message"],
            "guest": [],
            "admin": ["read-channel"],
        },
    }


def snapshot() -> dict[str, Any]:
    return {
        "app": {
            "app": {
                "id": 1729640,
                "disable_auth_checks": False,
                "disable_permissions_checks": False,
                "permission_version": "v2",
                "guest_user_creation_disabled": False,
                "grants": {
                    "user": ["search-user", "update-user-owner"],
                    "guest": ["search-user"],
                    "anonymous": [],
                    "admin": ["search-user"],
                },
            }
        },
        "channel_types": {"channel_types": {n: _type(n) for n in conf.DEFAULT_TYPES}},
        "users": {"users": [{"id": "someone", "custom": {"first_name": "Private"}}]},
    }


def configured(snap: dict[str, Any]) -> dict[str, Any]:
    """What the application looks like after the plan is applied."""
    snap = copy.deepcopy(snap)
    app = snap["app"]["app"]
    app["guest_user_creation_disabled"] = True
    for role in conf.CLIENT_APP_ROLES:
        app["grants"][role] = []
    roles = conf.roles_in(snap)
    for name in conf.DEFAULT_TYPES:
        snap["channel_types"]["channel_types"][name]["grants"] = {r: [] for r in roles}
    match = {k: v for k, v in conf.MATCH_FEATURES.items() if k != "commands"}
    match["commands"] = []
    match["grants"] = conf.match_type_grants(roles)
    snap["channel_types"]["channel_types"][conf.MATCH_TYPE] = match
    return snap


class ConfigurationTest(unittest.TestCase):
    def test_plan_enforces_checks_and_locks_everything(self) -> None:
        plan = conf.apply_plan(snapshot())
        app_patch = plan[0]
        self.assertEqual((app_patch.method, app_patch.path), ("PATCH", "/api/v2/app"))
        self.assertIs(app_patch.body["disable_auth_checks"], False)
        self.assertIs(app_patch.body["disable_permissions_checks"], False)
        self.assertIs(app_patch.body["guest_user_creation_disabled"], True)
        self.assertEqual(app_patch.body["grants"], {"user": [], "guest": [], "anonymous": []})
        locks = [s for s in plan if s.path.split("/")[-1] in conf.DEFAULT_TYPES]
        self.assertEqual(len(locks), len(conf.DEFAULT_TYPES))
        for lock in locks:
            self.assertEqual(set(lock.body["grants"]), {"admin", "channel_member", "guest", "user"})
            self.assertTrue(all(v == [] for v in lock.body["grants"].values()))
            self.assertNotIn("reactions", lock.body)  # features of default types are untouched

    def test_match_type_is_read_only_for_members(self) -> None:
        plan = conf.apply_plan(snapshot())
        create = next(s for s in plan if s.method == "POST")
        self.assertEqual(create.body["name"], conf.MATCH_TYPE)
        grants = create.body["grants"]
        self.assertEqual(grants["channel_member"], ["read-channel"])
        self.assertTrue(all(v == [] for r, v in grants.items() if r != "channel_member"))
        for feature in (
            "reactions",
            "replies",
            "uploads",
            "polls",
            "custom_events",
            "shared_locations",
            "url_enrichment",
            "mutes",
        ):
            self.assertIs(create.body[feature], False, feature)
        self.assertNotIn("quotes", create.body)  # create does not accept it
        update = plan[-1]
        self.assertIs(update.body["quotes"], False)
        self.assertEqual(update.body["commands"], [])

    def test_existing_match_type_is_updated_not_recreated(self) -> None:
        plan = conf.apply_plan(configured(snapshot()))
        self.assertFalse(any(s.method == "POST" for s in plan))

    def test_verify(self) -> None:
        self.assertNotEqual(conf.verify(snapshot()), [])
        self.assertEqual(conf.verify(configured(snapshot())), [])
        drift = configured(snapshot())
        drift["channel_types"]["channel_types"][conf.MATCH_TYPE]["grants"]["user"] = [
            "read-channel"
        ]
        self.assertTrue(any("user" in p for p in conf.verify(drift)))
        drift = configured(snapshot())
        drift["app"]["app"]["disable_auth_checks"] = True
        self.assertIn("disable_auth_checks is not false", conf.verify(drift))

    def test_baseline_record_holds_no_user_data(self) -> None:
        record = conf.baseline_record(snapshot())
        self.assertNotIn("users", record)
        self.assertNotIn("Private", repr(record))
        self.assertEqual(record["app_grants"]["user"], ["search-user", "update-user-owner"])
        self.assertEqual(record["channel_types"]["messaging"]["commands"], ["giphy"])

    def test_restore_plan_uses_recorded_grants(self) -> None:
        record = conf.baseline_record(snapshot())
        plan = conf.restore_plan(record, delete_match_type=False)
        self.assertIs(plan[0].body["guest_user_creation_disabled"], False)
        self.assertEqual(plan[0].body["grants"]["user"], ["search-user", "update-user-owner"])
        messaging = next(s for s in plan if s.path.endswith("/messaging"))
        self.assertEqual(messaging.body["grants"]["user"], ["create-channel", "read-channel-owner"])
        self.assertFalse(any(s.method == "DELETE" for s in plan))
        with_delete = conf.restore_plan(record, delete_match_type=True)
        self.assertEqual(with_delete[-1].method, "DELETE")


if __name__ == "__main__":
    unittest.main()
