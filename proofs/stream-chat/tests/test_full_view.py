"""P06.2 Stage B2-C1 (DM-17 2.1 and 2.3): the read-only full view of the configuration and
the comparison of two views (``glow_stream_proof/full_view.py``; the ``full-view`` and
``compare-views`` commands).

The view sends GETs only, under a guard that refuses anything else; a credential-like value
is written as its type, emptiness and digest, never its value; the comparison reports a
change in any field but the named volatile ones, value and type.
"""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import tests  # noqa: F401
from glow_stream_proof import cli, full_view
from glow_stream_proof import configuration as conf
from glow_stream_proof.redaction import REDACTED_SECRET
from glow_stream_proof.stops import GuardRefused
from glow_stream_proof.usage import UsageLedger
from tests.fakes import FakeServer
from tests.test_cli import FakeContext, _WritesTest
from tests.test_configuration import SIXTH_TYPE


def sha256(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def digest(value: Any) -> dict[str, Any]:
    return {
        "type": full_view._json_type(value),
        "empty": full_view._empty(value),
        "sha256": sha256(value),
    }


class CredentialKeyTest(unittest.TestCase):
    def test_the_constants(self) -> None:
        self.assertEqual(
            full_view.CREDENTIAL_KEY_PARTS,
            (
                "key",
                "secret",
                "token",
                "password",
                "credential",
                "cert",
                "private",
                "url",
                "push",
                "sqs",
                "sns",
                "webhook",
            ),
        )
        self.assertEqual(
            full_view.VOLATILE_FIELDS, frozenset({"created_at", "updated_at", "duration"})
        )

    def test_credential_like_keys_in_any_letter_case(self) -> None:
        for key in (
            "sqs_key",
            "sqs_secret",
            "sqs_url",
            "sns_key",
            "sns_secret",
            "sns_topic_arn",
            "webhook_url",
            "webhook_events",
            "push_notifications",
            "api_key",
            "APN_AUTH_KEY",
            "p12_cert",
            "app_certificate",
            "private_key",
            "firebase_credentials",
            "password",
            "access_token",
            "before_message_send_hook_url",
            "custom_action_handler_url",
            "moderation_webhook_url",
            "PushNotifications",
        ):
            self.assertTrue(full_view.is_credential_key(key), key)
        for key in (
            "grants",
            "name",
            "automod",
            "max_message_length",
            "permission_version",
            "disable_auth_checks",
            "file_upload_config",
            "event_hooks",
            "channel_configs",
            "call_types",
            "settings",
            "notification_settings",
            "moderation_enabled",
            "allowed_flag_reasons",
            "guest_user_creation_disabled",
        ):
            self.assertFalse(full_view.is_credential_key(key), key)

    def test_the_rule_reads_the_name_alone(self) -> None:
        # Two values that are no credential are digested too, as the module says: the rule
        # reads the key's name, and baseline's snapshot still shows them in clear.
        self.assertTrue(full_view.is_credential_key("revoke_tokens_issued_before"))
        self.assertTrue(full_view.is_credential_key("url_enrichment"))


APP: dict[str, Any] = {
    "app": {
        "name": "glow",
        "id": 1729640,
        "grants": {"user": [], "guest": [], "admin": ["search-user"]},
        "permission_version": "v2",
        "webhook_url": "",
        "sqs_key": "AKIA-not-a-real-key",
        "sqs_secret": REDACTED_SECRET,
        "sns_topic_arn": None,
        "push_notifications": {
            "version": "v2",
            "providers": [{"name": "p", "type": "firebase", "firebase_credentials": "{json}"}],
        },
        "datadog_info": {"api_key": "dd-fake", "site": "eu"},
        "event_hooks": [
            {"hook_type": "webhook", "webhook_url": "https://hooks.invalid/e", "enabled": True}
        ],
        "file_upload_config": {"size_limit": 0, "allowed_file_extensions": []},
        "channel_configs": {"messaging": {"url_enrichment": True, "reactions": True}},
    },
    "duration": "1.2ms",
}


class WithheldTest(unittest.TestCase):
    def test_credential_like_values_are_written_as_type_emptiness_and_digest(self) -> None:
        out = full_view.withheld(APP)
        app = out["app"]
        self.assertEqual(app["sqs_key"], digest("AKIA-not-a-real-key"))
        self.assertEqual(app["webhook_url"], digest(""))
        self.assertEqual(app["webhook_url"]["empty"], True)
        self.assertEqual(app["sns_topic_arn"], digest(None))
        self.assertEqual(app["sns_topic_arn"]["type"], "null")
        # A matching key withholds its whole subtree as one digest.
        self.assertEqual(app["push_notifications"], digest(APP["app"]["push_notifications"]))
        self.assertEqual(app["push_notifications"]["type"], "object")
        # A value the harness's redactor already replaced is said so.
        self.assertEqual(
            app["sqs_secret"], {**digest(REDACTED_SECRET), "redacted_by_the_harness": True}
        )
        # A credential key inside a subtree that is not itself credential-like, and inside
        # a list, is withheld on its own; its neighbours are kept.
        self.assertEqual(app["datadog_info"], {"api_key": digest("dd-fake"), "site": "eu"})
        self.assertEqual(
            app["event_hooks"],
            [
                {
                    "hook_type": "webhook",
                    "webhook_url": digest("https://hooks.invalid/e"),
                    "enabled": True,
                }
            ],
        )
        self.assertEqual(
            app["channel_configs"]["messaging"],
            {"url_enrichment": digest(True), "reactions": True},
        )
        # Everything else is kept as it is.
        for key in ("name", "id", "grants", "permission_version", "file_upload_config"):
            self.assertEqual(app[key], APP["app"][key], key)
        self.assertEqual(out["duration"], "1.2ms")
        text = json.dumps(out)
        for value in ("AKIA-not-a-real-key", "dd-fake", "hooks.invalid", "{json}", "firebase"):
            self.assertNotIn(value, text, value)

    def test_the_source_is_not_changed(self) -> None:
        source = copy.deepcopy(APP)
        full_view.withheld(source)
        self.assertEqual(source, APP)

    def test_a_change_is_still_seen(self) -> None:
        changed = copy.deepcopy(APP)
        changed["app"]["sqs_key"] = "AKIA-another"
        before, after = full_view.withheld(APP)["app"], full_view.withheld(changed)["app"]
        self.assertNotEqual(before["sqs_key"], after["sqs_key"])
        self.assertEqual(before["sqs_key"]["type"], after["sqs_key"]["type"])
        # A digest is the SHA-256 of the canonical JSON: sorted keys, no spaces.
        self.assertEqual(
            full_view.digest({"b": 1, "a": [1, 2]})["sha256"],
            hashlib.sha256(b'{"a":[1,2],"b":1}').hexdigest(),
        )


class ReadViewTest(unittest.TestCase):
    def test_the_view_sends_gets_only_and_reads_the_six_configurations(self) -> None:
        server = FakeServer(UsageLedger())
        server.guard = full_view.read_only_refusal
        view = full_view.read_view(server)  # type: ignore[arg-type]
        self.assertEqual([m for m, _p, _b in server.calls], ["GET"] * 6)
        self.assertEqual([p for _m, p, _b in server.calls], [p for _n, p in full_view.READS])
        self.assertEqual(
            list(view["reads"]),
            ["app", "channel_types", "roles", "call_types", "feed_visibilities", "feed_groups"],
        )
        app = view["reads"]["app"]["body"]["app"]
        self.assertEqual(app["permission_version"], "v2")  # a setting the target names, clear
        self.assertEqual(app["grants"]["user"], [])  # the .app grants, clear
        self.assertEqual(app["webhook_url"]["type"], "string")  # a url: its digest
        self.assertEqual(
            sorted(view["reads"]["channel_types"]["body"]["channel_types"]),
            sorted([*conf.DEFAULT_TYPES, SIXTH_TYPE, conf.MATCH_TYPE]),
        )
        self.assertEqual(view["reads"]["call_types"]["status"], 200)
        self.assertIn("default", view["reads"]["call_types"]["body"]["call_types"])
        self.assertIn("public", view["reads"]["feed_visibilities"]["body"]["feed_visibilities"])
        self.assertIn("user", view["reads"]["feed_groups"]["body"]["groups"])
        self.assertEqual(view["withheld_key_parts"], list(full_view.CREDENTIAL_KEY_PARTS))
        self.assertEqual(
            view["volatile_fields_left_aside_by_compare"], ["created_at", "duration", "updated_at"]
        )
        self.assertRegex(view["at"], r"^\d{8}T\d{6}Z$")

    def test_the_guard_refuses_anything_but_a_get(self) -> None:
        self.assertIsNone(full_view.read_only_refusal("GET", "/api/v2/app", None, {}))
        self.assertIsNone(full_view.read_only_refusal("head", "/api/v2/app", None, {}))
        self.assertEqual(
            full_view.read_only_refusal("POST", "/api/v2/users/u1/deactivate", {}, {}),
            "full-view sends GETs only; refused POST users/{id}/deactivate",
        )
        self.assertEqual(
            full_view.read_only_refusal("PATCH", "/api/v2/app", {"x": 1}, {}),
            "full-view sends GETs only; refused PATCH app",
        )
        server = FakeServer(UsageLedger())
        server.guard = full_view.read_only_refusal
        with self.assertRaises(GuardRefused):
            server.raw("PATCH", "/api/v2/app", body={"guest_user_creation_disabled": False})
        self.assertEqual(server.calls, [])  # refused before the fake answered or counted it
        self.assertEqual(server.raw("GET", "/api/v2/app").status, 200)

    def test_a_read_that_is_not_2xx_is_kept_as_its_answer(self) -> None:
        server = FakeServer(UsageLedger())
        server.products.available["feeds"] = False
        view = full_view.read_view(server)  # type: ignore[arg-type]
        read = view["reads"]["feed_visibilities"]
        self.assertEqual((read["status"], read["code"]), (403, 17))
        self.assertIn("not enabled", read["message"])
        self.assertEqual(view["reads"]["call_types"]["status"], 200)

    def test_no_credential_like_value_reaches_the_view(self) -> None:
        server = FakeServer(UsageLedger())
        server.app["sqs_key"] = "AKIA-fake-sqs"
        server.app["push_notifications"] = {
            "providers": [{"name": "p", "firebase_credentials": "fb-fake"}]
        }
        server.app["webhook_url"] = "https://hooks.invalid/w"
        view = full_view.read_view(server)  # type: ignore[arg-type]
        text = json.dumps(view)
        for value in ("AKIA-fake-sqs", "fb-fake", "hooks.invalid"):
            self.assertNotIn(value, text, value)
        app = view["reads"]["app"]["body"]["app"]
        self.assertEqual(app["sqs_key"], digest("AKIA-fake-sqs"))
        self.assertEqual(app["push_notifications"]["type"], "object")


class CompareTest(unittest.TestCase):
    def view(self) -> dict[str, Any]:
        return full_view.read_view(FakeServer(UsageLedger()))  # type: ignore[arg-type]

    def test_identical_views_have_no_change(self) -> None:
        self.assertEqual(full_view.compare(self.view(), self.view()), [])

    def test_a_change_in_an_unnamed_field_is_reported_with_its_before_and_after(self) -> None:
        before, after = self.view(), self.view()
        types = after["reads"]["channel_types"]["body"]["channel_types"]
        types[conf.MATCH_TYPE]["grants"]["channel_member"] = ["read-channel", "schedule-message"]
        after["reads"]["app"]["body"]["app"]["grants"]["user"] = ["search-user"]
        # The committed products baseline (which the fake models) holds lifecycle since B2-C2.
        default_settings = after["reads"]["call_types"]["body"]["call_types"]["default"]["settings"]
        self.assertEqual(default_settings["lifecycle"], {"mode": "reusable"})
        default_settings["lifecycle"] = {"mode": "single_use"}
        changes = full_view.compare(before, after)
        self.assertEqual(
            changes,
            [
                {"path": "app.body.app.grants.user", "before": [], "after": ["search-user"]},
                {
                    "path": "call_types.body.call_types.default.settings.lifecycle.mode",
                    "before": "reusable",
                    "after": "single_use",
                },
                {
                    "path": "channel_types.body.channel_types."
                    f"{conf.MATCH_TYPE}.grants.channel_member",
                    "before": ["read-channel"],
                    "after": ["read-channel", "schedule-message"],
                },
            ],
        )
        rendered = full_view.render(changes)
        self.assertEqual(len(rendered), 3)
        self.assertEqual(rendered[0], '- app.body.app.grants.user: [] -> ["search-user"]')

    def test_a_change_in_a_named_volatile_field_is_not(self) -> None:
        before, after = self.view(), self.view()
        after["reads"]["app"]["body"]["duration"] = "9ms"  # present on one side only
        types = after["reads"]["channel_types"]["body"]["channel_types"]
        types["team"]["updated_at"] = "2026-10-23T12:00:00Z"
        types["team"]["created_at"] = "2026-10-23T12:00:00Z"
        self.assertEqual(after["reads"]["feed_groups"]["body"]["duration"], "1ms")
        after["reads"]["feed_groups"]["body"]["duration"] = "2ms"
        self.assertEqual(full_view.compare(before, after), [])
        # A field of another name beside them is still reported.
        types["team"]["max_message_length"] = 1
        self.assertEqual(
            [c["path"] for c in full_view.compare(before, after)],
            ["channel_types.body.channel_types.team.max_message_length"],
        )

    def test_a_change_of_type_and_a_digest_change_are_reported(self) -> None:
        before, after = self.view(), self.view()
        app = after["reads"]["app"]["body"]["app"]
        self.assertIs(app["allow_multi_user_devices"], False)
        app["allow_multi_user_devices"] = 0  # the same meaning in Python, another JSON type
        app["webhook_url"] = full_view.digest("https://hooks.invalid/w")
        changes = full_view.compare(before, after)
        self.assertEqual(
            changes[0],
            {"path": "app.body.app.allow_multi_user_devices", "before": False, "after": 0},
        )
        self.assertEqual(changes[1]["path"], "app.body.app.webhook_url")
        self.assertEqual(
            (changes[1]["before"]["empty"], changes[1]["after"]["empty"]), (True, False)
        )
        self.assertEqual(len(changes), 2)
        self.assertNotIn("hooks.invalid", json.dumps(changes))
        # In a list of scalars a type change counts too.
        self.assertEqual(
            full_view.changed_fields([1, 2], [1, 2.0], "x"),
            [{"path": "x", "before": [1, 2], "after": [1, 2.0]}],
        )

    def test_a_key_on_one_side_only_and_a_list_of_objects(self) -> None:
        before, after = self.view(), self.view()
        del after["reads"]["app"]["body"]["app"]["moderation_enabled"]
        after["reads"]["roles"]["body"]["roles"] = [{"name": "r1", "scopes": ["chat"]}]
        changes = full_view.compare(before, after)
        self.assertEqual(
            changes,
            [
                {
                    "path": "app.body.app.moderation_enabled",
                    "before": True,
                    "after": full_view.ABSENT,
                },
                {"path": "roles.body.roles (length)", "before": 0, "after": 1},
            ],
        )
        # Lists of objects are compared item by item.
        self.assertEqual(
            full_view.changed_fields(
                [{"name": "r1", "scopes": ["chat"]}],
                [{"name": "r1", "scopes": ["chat", "video"]}],
                "r",
            ),
            [{"path": "r[0].scopes", "before": ["chat"], "after": ["chat", "video"]}],
        )


GEOFENCES = [
    {
        "country_codes": ["AT", "BE"],
        "description": "EU",
        "name": "european_union",
        "type": "inclusion",
    },
    {"country_codes": ["US"], "description": "US", "name": "united_states", "type": "inclusion"},
    {
        "country_codes": ["BY"],
        "description": "BY",
        "name": "belarus_exclusion",
        "type": "exclusion",
    },
]


class KeyedListTest(unittest.TestCase):
    """P06.2 Stage B2-C2 (DM-18 3.3): the application's geofences, which Stream returned in
    two orders in two read-only views 79 s apart, are paired by ``name``; every other list of
    objects is still compared by position."""

    def views(self) -> tuple[dict[str, Any], dict[str, Any]]:
        view = full_view.read_view(FakeServer(UsageLedger()))  # type: ignore[arg-type]
        view["reads"]["app"]["body"]["app"]["geofences"] = copy.deepcopy(GEOFENCES)
        return view, copy.deepcopy(view)

    def test_only_the_geofences_are_keyed_and_by_name(self) -> None:
        self.assertEqual(full_view.KEYED_LISTS, {"app.body.app.geofences": "name"})

    def test_the_same_geofences_in_another_order_are_no_change(self) -> None:
        before, after = self.views()
        after["reads"]["app"]["body"]["app"]["geofences"].reverse()
        self.assertEqual(full_view.compare(before, after), [])

    def test_a_changed_added_or_removed_geofence_is_still_reported(self) -> None:
        before, after = self.views()
        fences = after["reads"]["app"]["body"]["app"]["geofences"]
        fences.reverse()
        fences[0]["country_codes"] = ["BY", "RU"]  # belarus_exclusion, now first
        self.assertEqual(
            full_view.compare(before, after),
            [
                {
                    "path": "app.body.app.geofences[name=belarus_exclusion].country_codes",
                    "before": ["BY"],
                    "after": ["BY", "RU"],
                }
            ],
        )
        removed = fences.pop()  # european_union, last after the reverse
        fences.append({"country_codes": ["GB"], "name": "united_kingdom", "type": "inclusion"})
        fences.append(dict(GEOFENCES[0], name="extra"))
        changes = full_view.compare(before, after)
        self.assertEqual(
            [c["path"] for c in changes],
            [
                "app.body.app.geofences (length)",
                "app.body.app.geofences[name=belarus_exclusion].country_codes",
                "app.body.app.geofences[name=european_union]",
                "app.body.app.geofences[name=extra]",
                "app.body.app.geofences[name=united_kingdom]",
            ],
        )
        self.assertEqual((changes[0]["before"], changes[0]["after"]), (3, 4))
        self.assertEqual((changes[2]["before"], changes[2]["after"]), (removed, full_view.ABSENT))
        self.assertEqual(changes[3]["before"], full_view.ABSENT)

    def test_every_other_list_of_objects_is_still_compared_by_position(self) -> None:
        roles = [{"name": "r1", "scopes": ["chat"]}, {"name": "r2", "scopes": ["video"]}]
        self.assertEqual(
            [c["path"] for c in full_view.changed_fields(roles, roles[::-1], "roles.body.roles")],
            [
                "roles.body.roles[0].name",
                "roles.body.roles[0].scopes",
                "roles.body.roles[1].name",
                "roles.body.roles[1].scopes",
            ],
        )
        # The geofences named at another path are positional too.
        self.assertEqual(
            len(full_view.changed_fields(GEOFENCES, GEOFENCES[::-1], "app.body.geofences")), 8
        )

    def test_geofences_without_a_unique_name_are_compared_by_position(self) -> None:
        path = "app.body.app.geofences"
        twice = [dict(GEOFENCES[0]), dict(GEOFENCES[0], description="again")]
        self.assertEqual(
            full_view.changed_fields(twice, twice[::-1], path),
            [
                {"path": f"{path}[0].description", "before": "EU", "after": "again"},
                {"path": f"{path}[1].description", "before": "again", "after": "EU"},
            ],
        )
        unnamed = [{"country_codes": ["US"]}, {"country_codes": ["CA"]}]
        self.assertEqual(len(full_view.changed_fields(unnamed, unnamed[::-1], path)), 2)


class FullViewCommandTest(_WritesTest):
    def test_full_view_writes_the_view_under_the_read_only_guard(self) -> None:
        server = FakeServer(UsageLedger())
        ctx = FakeContext(server)
        self.assertEqual(cli.cmd_full_view(ctx), 0)  # type: ignore[arg-type]
        name, view = next((k, v) for k, v in self.written.items() if k.startswith("full-view-"))
        self.assertRegex(name, r"^full-view-\d{8}T\d{6}Z\.json$")
        self.assertEqual([m for m, _p, _b in server.calls], ["GET"] * 6)
        self.assertIs(server.guard, full_view.read_only_refusal)  # installed before the reads
        self.assertEqual(ctx.lines[0], f"full view written to .work/{name}")
        app_line = next(line for line in ctx.lines if line.startswith("app: HTTP 200; "))
        self.assertIn(
            "withheld (type, emptiness and digest only): ['custom_action_handler_url'", app_line
        )
        self.assertIn(
            "channel types: HTTP 200; "
            + str(sorted([*conf.DEFAULT_TYPES, SIXTH_TYPE, conf.MATCH_TYPE])),
            ctx.lines,
        )
        self.assertIn(
            "video call types: HTTP 200; "
            "['agent', 'audio_call', 'audio_room', 'default', 'development', 'livestream']",
            ctx.lines,
        )
        self.assertIn(
            "feed groups: HTTP 200; "
            "['foryou', 'notification', 'stories', 'story', 'timeline', 'user']",
            ctx.lines,
        )
        self.assertEqual(view["reads"]["app"]["status"], 200)
        # No value is printed: the lines name keys, names and counts only.
        self.assertFalse(any("v2" in line for line in ctx.lines), ctx.lines)

    def test_compare_views_prints_each_change_and_exits_one_when_they_differ(self) -> None:
        server = FakeServer(UsageLedger())
        ctx = FakeContext(server)
        stamps = iter(["20261023T120000Z", "20261023T120100Z", "20261023T120200Z"])
        with mock.patch.object(full_view, "_stamp", side_effect=lambda: next(stamps)):
            self.assertEqual(cli.cmd_full_view(ctx), 0)  # type: ignore[arg-type]
            server.match_type["grants"]["channel_member"] = ["read-channel", "schedule-message"]
            self.assertEqual(cli.cmd_full_view(ctx), 0)  # type: ignore[arg-type]
        names = sorted(k for k in self.written if k.startswith("full-view-"))
        self.assertEqual(
            names, ["full-view-20261023T120000Z.json", "full-view-20261023T120100Z.json"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name in names:
                path = Path(tmp) / name
                path.write_text(json.dumps(self.written[name]), encoding="utf-8")
                paths.append(path)
            ctx.lines.clear()
            self.assertEqual(cli.cmd_compare_views(ctx, paths[0], paths[1]), 1)  # type: ignore[arg-type]
            self.assertIn(
                f"- channel_types.body.channel_types.{conf.MATCH_TYPE}.grants.channel_member: "
                '["read-channel"] -> ["read-channel", "schedule-message"]',
                ctx.lines,
            )
            self.assertIn(
                "left aside (volatile fields): ['created_at', 'duration', 'updated_at']", ctx.lines
            )
            self.assertEqual(ctx.lines[-1], "changed fields: 1")
            record = next(v for k, v in self.written.items() if k.startswith("compare-views-"))
            self.assertEqual((record["before"], record["after"]), tuple(names))
            self.assertEqual(len(record["changes"]), 1)
            ctx.lines.clear()
            self.assertEqual(cli.cmd_compare_views(ctx, paths[1], paths[1]), 0)  # type: ignore[arg-type]
            self.assertEqual(ctx.lines[-1], "changed fields: 0")
        # The comparison calls nothing: the two full views made the only requests.
        self.assertEqual(len(server.calls), 12)


if __name__ == "__main__":
    unittest.main()
