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
                # Every setting the committed baseline records, as the live application
                # returns them (P06.1-I2a: verify compares them).
                **conf.recorded_app_settings(),
                "id": 1729640,
                "disable_auth_checks": False,
                "disable_permissions_checks": False,
                "permission_version": "v2",
                "member_custom_on_typing_events_enabled": False,
                "member_custom_on_messages_enabled": False,
                "member_custom_on_mentioned_users_enabled": False,
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

    def test_verify_checks_permission_version_and_member_custom_settings(self) -> None:
        # Nit 9, and the brief: the member_custom_on_* settings stay off.
        for key, bad in (
            ("permission_version", "v1"),
            ("member_custom_on_typing_events_enabled", True),
            ("member_custom_on_messages_enabled", True),
            ("member_custom_on_mentioned_users_enabled", True),
        ):
            drift = configured(snapshot())
            drift["app"]["app"][key] = bad
            self.assertTrue(any(p.startswith(key) for p in conf.verify(drift)), key)
            missing = configured(snapshot())
            del missing["app"]["app"][key]
            self.assertTrue(any(p.startswith(key) for p in conf.verify(missing)), key)

    def test_verify_restored(self) -> None:
        # Nit 10: what restore --apply re-reads is compared with the recorded baseline.
        record = conf.baseline_record(snapshot())
        self.assertEqual(conf.verify_restored(snapshot(), record, match_type_deleted=False), [])
        locked = configured(snapshot())
        problems = conf.verify_restored(locked, record, match_type_deleted=True)
        self.assertIn("guest_user_creation_disabled is True, want False", problems)
        self.assertIn(
            ".app grants for user are [], want ['search-user', 'update-user-owner']", problems
        )
        self.assertTrue(any(p.startswith("messaging grants for user") for p in problems))
        self.assertIn(f"{conf.MATCH_TYPE} still exists", problems)
        # The review's nit: the fields restore_plan sends for each default type.
        drift = snapshot()
        drift["channel_types"]["channel_types"]["team"]["max_message_length"] = 1
        self.assertEqual(
            conf.verify_restored(drift, record, match_type_deleted=False),
            ["team.max_message_length is 1, want 5000"],
        )

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


class RecordedSettingsTest(unittest.TestCase):
    """P06.1-I2a, DM-04 finding 2: verify compares every setting the baseline records.

    Preflight, the end of a run and the dry-run configure all rely on verify, so an
    application-wide token revocation or a hook is seen by each of them.
    """

    def test_an_application_wide_token_revocation_is_a_difference(self) -> None:
        drift = configured(snapshot())
        drift["app"]["app"]["revoke_tokens_issued_before"] = "2026-09-26T12:00:00Z"
        self.assertIn(
            "revoke_tokens_issued_before is '2026-09-26T12:00:00Z', recorded None",
            conf.verify(drift),
        )

    def test_every_hook_is_a_difference(self) -> None:
        for key, value in (
            ("webhook_url", "https://hooks.invalid/w"),
            ("custom_action_handler_url", "https://hooks.invalid/c"),
            ("event_hooks", [{"url": "https://hooks.invalid/e"}]),
            ("before_message_send_hook_url", "https://hooks.invalid/b"),
        ):
            drift = configured(snapshot())
            drift["app"]["app"][key] = value
            self.assertTrue(any(p.startswith(key) for p in conf.verify(drift)), key)

    def test_every_recorded_setting_is_compared_except_guest_creation(self) -> None:
        recorded = conf.recorded_app_settings()
        own_rules = {"disable_auth_checks", "disable_permissions_checks"}
        own_rules |= {"guest_user_creation_disabled", *conf.REQUIRED_APP_SETTINGS}
        compared = sorted(set(recorded) - own_rules)
        self.assertIn("revoke_tokens_issued_before", compared)
        for key in compared:
            drift = configured(snapshot())
            drift["app"]["app"][key] = "changed"
            self.assertIn(f"{key} is 'changed', recorded {recorded[key]!r}", conf.verify(drift))
            missing = configured(snapshot())
            del missing["app"]["app"][key]
            self.assertIn(f"{key} is absent, recorded {recorded[key]!r}", conf.verify(missing))
        # Guest creation differs from the record on purpose: the lockdown disables it.
        self.assertIs(recorded["guest_user_creation_disabled"], False)
        self.assertEqual(conf.verify(configured(snapshot())), [])

    def test_a_value_of_another_type_is_a_difference(self) -> None:
        # The I2a review's nit 3 (P06.1-I2b): 0 == False in Python, so the type is
        # compared too; a setting that reads as another type has changed.
        problems = conf.recorded_differences(
            {"allow_multi_user_devices": 0}, {"allow_multi_user_devices": False}
        )
        self.assertEqual(problems, ["allow_multi_user_devices is 0, recorded False"])
        self.assertEqual(
            conf.recorded_differences({"webhook_url": None}, {"webhook_url": ""}),
            ["webhook_url is None, recorded ''"],
        )
        self.assertEqual(
            conf.recorded_differences(
                {"allow_multi_user_devices": False}, {"allow_multi_user_devices": False}
            ),
            [],
        )

    def test_a_setting_the_baseline_did_not_record_may_be_absent_or_empty(self) -> None:
        self.assertNotIn("before_message_send_hook_url", conf.recorded_app_settings())
        empties: tuple[Any, ...] = (None, "", [], {}, False)
        for value in empties:
            quiet = configured(snapshot())
            quiet["app"]["app"]["before_message_send_hook_url"] = value
            quiet["app"]["app"]["channel_hide_members_only"] = value
            self.assertEqual(conf.verify(quiet), [], value)
        loud = configured(snapshot())
        loud["app"]["app"]["channel_hide_members_only"] = True
        self.assertIn("channel_hide_members_only is True, recorded as absent", conf.verify(loud))

    def test_the_committed_record_is_the_default(self) -> None:
        recorded = conf.recorded_app_settings()
        self.assertIsNone(recorded["revoke_tokens_issued_before"])
        self.assertEqual((recorded["webhook_url"], recorded["custom_action_handler_url"]), ("", ""))
        self.assertEqual(recorded["event_hooks"], [])
        other = {**recorded, "webhook_url": "https://hooks.invalid/w"}
        # With another record, the live value is compared with that one instead.
        self.assertIn(
            "webhook_url is '', recorded 'https://hooks.invalid/w'",
            conf.verify(configured(snapshot()), other),
        )


if __name__ == "__main__":
    unittest.main()


class ProductDifferencesTest(unittest.TestCase):
    """P06.1-I2b: ``verify`` compares the Video and Feeds target too, from the commit that
    records the live apply (``products.LOCKDOWN_APPLIED``) on; before it the products'
    differences are the plan, not drift, and the runs before the lockdown are allowed."""

    def state(self, user_grants: list[str]) -> dict[str, Any]:
        return {
            "video": {
                "availability": "available",
                "read": {},
                "call_types": {
                    "default": {"grants": {"user": user_grants, "admin": ["create-call"]}}
                },
            },
            "feeds": {
                "availability": "available",
                "read": {},
                "feed_visibilities": {"public": {"grants": {"user": user_grants}}},
                "feed_groups_read": {},
                "feed_groups": {},
            },
        }

    def test_without_the_products_state_nothing_is_compared(self) -> None:
        self.assertEqual(conf.product_differences(snapshot(), locked=True), [])
        self.assertEqual(conf.verify(configured(snapshot())), [])

    def test_the_recorded_apply_is_the_live_applys_utc_stamp(self) -> None:
        from glow_stream_proof import products

        # Set by the commit after the live apply of 27 September 2026; from then on every
        # verify compares the products (below).
        self.assertEqual(products.LOCKDOWN_APPLIED, "2026-09-27T05:58:31Z")
        self.assertRegex(products.LOCKDOWN_APPLIED or "", r"^2026-09-27T\d\d:\d\d:\d\dZ$")

    def test_with_no_recorded_apply_the_differences_are_not_drift(self) -> None:
        from unittest import mock

        from glow_stream_proof import products

        snap = configured(snapshot())
        snap["products"] = self.state(["create-call"])
        with mock.patch.object(products, "LOCKDOWN_APPLIED", None):
            self.assertEqual(conf.product_differences(snap), [])
            self.assertEqual(conf.verify(snap), [])
        self.assertEqual(
            conf.product_differences(snap, locked=True),
            [
                "video/feeds: video call type default: grants for user not empty: ['create-call']",
                "video/feeds: feeds feed visibility public: grants for user not empty: "
                "['create-call']",
            ],
        )
        self.assertEqual(conf.product_differences(snap, locked=False), [])

    def test_after_the_apply_verify_sees_drift(self) -> None:
        from unittest import mock

        from glow_stream_proof import products

        snap = configured(snapshot())
        snap["products"] = self.state(["create-call"])
        with mock.patch.object(products, "LOCKDOWN_APPLIED", "2026-09-27T00:00:00Z"):
            self.assertEqual(
                conf.verify(snap),
                [
                    "video/feeds: video call type default: grants for user not empty: "
                    "['create-call']",
                    "video/feeds: feeds feed visibility public: grants for user not empty: "
                    "['create-call']",
                ],
            )
            snap["products"] = self.state([])
            self.assertEqual(conf.verify(snap), [])
