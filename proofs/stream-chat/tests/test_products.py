"""P06.1-I2b: Stream Video and Feeds (``glow_stream_proof/products.py`` and the runner's
product op, ``client/product-op.cjs``).

The allowlist and the deny-list are in code, in both places, and must agree; the
lockdown plan is a difference that names only the client roles still holding a grant;
the products' availability and the product-finding rule are read from Stream's answers;
the listings and the baseline record hold no user data.
"""

import json
import subprocess
import unittest
from typing import Any

import tests  # noqa: F401
from glow_stream_proof import configuration, products
from glow_stream_proof.client_bridge import RUNNER
from glow_stream_proof.server_api import ApiResult
from glow_stream_proof.usage import UsageLedger
from tests.fakes import FakeServer

PRODUCT_OP = RUNNER.parent / "product-op.cjs"
CALL = "/api/v2/video/call/default/p061i1-x-call"
FEED = "/api/v2/feeds/feed_groups/user/feeds/p061i1-x-ua"

# (method, path, body, params, allowed by the client op?)
TABLE: list[tuple[str, str, Any, Any, bool]] = [
    ("POST", CALL, {"data": {"custom": {"glow_note": "x"}}}, None, True),
    ("GET", CALL, None, None, True),
    ("PATCH", CALL, {"custom": {"glow_note": "y"}}, None, True),
    ("PUT", CALL, {"custom": {}}, None, False),
    ("DELETE", CALL, None, None, False),
    ("POST", CALL + "/members", {"update_members": [{"user_id": "u"}]}, None, True),
    ("POST", CALL + "/event", {"custom": {"glow_note": "e"}}, None, True),
    ("POST", "/api/v2/video/calls", {"filter_conditions": {}}, None, True),
    ("POST", "/api/v2/video/call/members", {"id": "x", "type": "default"}, None, True),
    ("POST", CALL + "/delete", {"hard": True}, None, False),
    ("GET", "/api/v2/video/calltypes", None, None, False),
    ("PUT", "/api/v2/video/calltypes/default", {"grants": {"user": []}}, None, False),
    ("POST", FEED, {"data": {"custom": {}}}, None, True),
    ("PUT", FEED, {"custom": {}}, None, True),
    ("DELETE", FEED, None, {"hard_delete": "true"}, False),
    ("POST", "/api/v2/feeds/feeds/query", {"limit": 10}, None, True),
    (
        "POST",
        "/api/v2/feeds/activities",
        {"type": "post", "feeds": ["user:x"], "text": "t"},
        None,
        True,
    ),
    ("POST", "/api/v2/feeds/activities/query", {"filter": {}}, None, True),
    ("GET", "/api/v2/feeds/activities/a-1", None, None, True),
    ("PUT", "/api/v2/feeds/activities/a-1", {"text": "t"}, None, True),
    ("DELETE", "/api/v2/feeds/activities/a-1", None, None, False),
    ("POST", "/api/v2/feeds/activities/a-1/reactions", {"type": "like"}, None, True),
    ("DELETE", "/api/v2/feeds/activities/a-1/reactions/like", None, {"user_id": "u"}, False),
    ("POST", "/api/v2/feeds/comments", {"comment": "c", "object_id": "a-1"}, None, True),
    ("POST", "/api/v2/feeds/comments/query", {"filter": {}}, None, True),
    ("GET", "/api/v2/feeds/comments/c-1", None, None, True),
    ("DELETE", "/api/v2/feeds/comments/c-1", None, None, False),
    ("POST", "/api/v2/feeds/follows", {"source": "timeline:b", "target": "user:a"}, None, True),
    ("POST", "/api/v2/feeds/follows/query", {"filter": {}}, None, True),
    ("DELETE", "/api/v2/feeds/follows/timeline:b/user:a", None, None, False),
    ("GET", "/api/v2/feeds/feed_visibilities", None, None, False),
    ("PUT", "/api/v2/feeds/feed_visibilities/public", {"grants": {"user": []}}, None, False),
    ("POST", "/api/v2/feeds/users/u/delete", {}, None, False),
    ("POST", "/api/v2/chat/channels", {"filter_conditions": {}}, None, False),
    ("GET", "/channels/glow-match/x", None, None, False),
    # The deny-list: a media session, a push, a recording, a broadcast.
    ("POST", CALL + "/join", {}, None, False),
    ("POST", CALL + "/go_live", {}, None, False),
    ("POST", CALL + "/start_recording", {}, None, False),
    ("POST", CALL + "/stop_recording", {}, None, False),
    ("POST", CALL + "/start_transcription", {}, None, False),
    ("POST", CALL + "/start_closed_captions", {}, None, False),
    ("POST", CALL + "/rtmp_broadcasts", {}, None, False),
    ("GET", CALL + "/recordings", None, None, False),
    ("POST", CALL + "/ring", {}, None, False),
    ("POST", CALL, {"ring": True}, None, False),
    ("POST", CALL, {"ring": False}, None, False),
    ("POST", CALL, {"notify": True}, None, False),
    ("POST", CALL, {"video": True}, None, False),
    ("POST", CALL, {"video": False}, None, True),
    ("POST", CALL, {"data": {"video": True}}, None, False),
    ("POST", CALL, {"data": {"members": [{"user_id": "u", "custom": {"ring": 1}}]}}, None, False),
    ("GET", CALL, None, {"ring": "true"}, False),
    ("GET", CALL, None, {"video": "true"}, False),
    ("GET", CALL, None, {"members_limit": "10"}, True),
    (
        "POST",
        "/api/v2/feeds/activities",
        {"feeds": ["user:x"], "create_notification_activity": True},
        None,
        False,
    ),
    ("POST", "/api/v2/feeds/activities", {"feeds": ["user:x"], "skip_push": True}, None, True),
    ("POST", CALL + "?ring=true", {}, None, False),
]


def js_refusals(rows: list[tuple[str, str, Any, Any, bool]]) -> list[str | None]:
    """What ``client/product-op.cjs`` says for each row, run with node."""
    script = (
        "const { productRefusal } = require(process.argv[1]);\n"
        "const rows = JSON.parse(require('fs').readFileSync(0, 'utf8'));\n"
        "const out = rows.map(r => productRefusal(r[0], r[1], r[2], r[3]));\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    done = subprocess.run(
        ["node", "-e", script, str(PRODUCT_OP)],
        input=json.dumps([list(r[:4]) for r in rows]),
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    return list(json.loads(done.stdout))


class AllowlistTest(unittest.TestCase):
    def test_the_python_table(self) -> None:
        for method, path, body, params, allowed in TABLE:
            why = products.client_refusal(method, path, body, params)
            self.assertEqual(why is None, allowed, (method, path, body, params, why))

    def test_the_runner_agrees_with_the_guard(self) -> None:
        """The JS op and the Python table refuse and allow the same requests, for the same
        reasons (DM-05 finding 3: the code enforces the list, in both places)."""
        for (method, path, body, params, allowed), js in zip(
            TABLE, js_refusals(TABLE), strict=True
        ):
            py = products.client_refusal(method, path, body, params)
            self.assertEqual(js is None, allowed, (method, path, js))
            self.assertEqual(js, py, (method, path))

    def test_the_deny_list_is_named_first(self) -> None:
        self.assertEqual(
            products.client_refusal("POST", CALL + "/join", {}, None), "denied path (join)"
        )
        self.assertEqual(
            products.client_refusal("POST", CALL, {"data": {"ring": True}}, None),
            "denied field (ring)",
        )
        self.assertEqual(
            products.client_refusal("POST", CALL, {"video": True}, None),
            "denied field (video: true)",
        )
        self.assertEqual(
            products.client_refusal("GET", "/api/v2/video/calltypes", None, None),
            "path outside the Video and Feeds allowlist",
        )
        self.assertEqual(
            products.client_refusal("DELETE", CALL, None, None),
            "method DELETE is not allowed on this path",
        )

    def test_denied_alone(self) -> None:
        self.assertIsNone(products.denied(CALL, {"custom": {"x": 1}}, None))
        self.assertEqual(products.denied(CALL + "/hls", None, None), "denied path (hls)")
        self.assertEqual(products.denied(CALL, None, {"notify": "true"}), "denied field (notify)")
        self.assertEqual(
            products.denied(
                "/api/v2/feeds/activities", {"create_notification_activity": "true"}, None
            ),
            "denied field (create_notification_activity: true)",
        )

    def test_configuration_writes(self) -> None:
        self.assertTrue(products.is_configuration_write("PUT", "/api/v2/video/calltypes/default"))
        self.assertTrue(
            products.is_configuration_write("put", "/api/v2/feeds/feed_visibilities/public")
        )
        for method, path in (
            ("POST", "/api/v2/video/calltypes"),
            ("DELETE", "/api/v2/video/calltypes/default"),
            ("PUT", "/api/v2/video/calltypes"),
            ("PUT", "/api/v2/feeds/feed_groups/user"),
            ("PUT", "/api/v2/feeds/feed_visibilities/public/x"),
            ("PATCH", "/api/v2/app"),
        ):
            self.assertFalse(products.is_configuration_write(method, path), (method, path))

    def test_the_client_roles_are_the_configurations(self) -> None:
        self.assertEqual(products.CLIENT_ROLES, configuration.CLIENT_APP_ROLES)


def answer(
    status: int, body: Any = None, code: int | None = None, message: str | None = None
) -> ApiResult:
    return ApiResult("GET", "/x", status, code, message, body if body is not None else {})


def state(
    video: dict[str, dict[str, list[str]]] | None = None,
    feeds: dict[str, dict[str, list[str]]] | None = None,
    *,
    video_available: str = "available",
    feeds_available: str = "available",
) -> dict[str, Any]:
    return {
        "video": {
            "availability": video_available,
            "read": {"status": 200, "code": None, "message": None},
            "call_types": {name: {"grants": grants} for name, grants in (video or {}).items()},
        },
        "feeds": {
            "availability": feeds_available,
            "read": {"status": 200, "code": None, "message": None},
            "feed_visibilities": {
                name: {"grants": grants} for name, grants in (feeds or {}).items()
            },
            "feed_groups_read": {
                "status": 200,
                "code": None,
                "message": None,
                "availability": "available",
            },
            "feed_groups": {"user": {"default_visibility": "visible"}},
        },
    }


class AvailabilityTest(unittest.TestCase):
    def test_availability_from_the_configuration_read(self) -> None:
        self.assertEqual(products.availability(answer(200, {"call_types": {}})), "available")
        self.assertEqual(
            products.availability(answer(404, code=16, message="Not Found")),
            "not available: HTTP 404 code 16: Not Found (the endpoints are not available on the "
            "application's deployment)",
        )
        self.assertEqual(
            products.availability(
                answer(
                    403,
                    code=17,
                    message="Feeds is not enabled for this application. Upgrade your plan.",
                )
            ),
            "not available: HTTP 403 code 17: Feeds is not enabled for this application. Upgrade "
            "your plan.",
        )
        self.assertEqual(
            products.availability(answer(500, code=-1, message="internal")),
            "not verified: HTTP 500 code -1: internal",
        )
        # Stream's ordinary permission refusal says nothing about the product.
        self.assertEqual(
            products.availability(answer(403, code=17, message="Not Allowed")),
            "not verified: HTTP 403 code 17: Not Allowed",
        )

    def test_the_product_finding_rule(self) -> None:
        """DM-05 finding 2 (c): a 4xx other than 402, code not 99, wording that the product
        is not enabled or not available."""
        self.assertEqual(
            products.unavailable_answer(403, 17, "Video is not enabled for this app"),
            "HTTP 403 code 17: Video is not enabled for this app",
        )
        self.assertIsNotNone(
            products.unavailable_answer(400, 4, "feeds v3 is not available on your plan")
        )
        self.assertIsNotNone(products.unavailable_answer(403, 17, "This feature is disabled"))
        for status, code, message in (
            (402, 17, "Video is not enabled"),  # 402 is always a charge signal
            (403, 99, "Video is not enabled"),  # code 99 too
            (403, 17, "Not Allowed"),  # an ordinary refusal
            (403, 17, "Upgrade your plan"),  # no wording that the product is not enabled
            (200, None, "Video is not enabled"),
            (500, -1, "Video is not enabled"),
            (None, None, "Video is not enabled"),
            (403, 17, None),
        ):
            self.assertIsNone(
                products.unavailable_answer(status, code, message), (status, code, message)
            )


class LockdownPlanTest(unittest.TestCase):
    def test_the_plan_is_a_difference_naming_only_the_client_roles_with_grants(self) -> None:
        current = state(
            video={
                "default": {
                    "admin": ["create-call"],
                    "user": ["create-call", "read-call"],
                    "guest": [],
                    "call_member": ["read-call"],
                },
                "development": {
                    "user": ["create-call"],
                    "guest": ["read-call"],
                    "anonymous": ["read-call"],
                },
                "audio_room": {"admin": ["create-call"], "user": []},
            },
            feeds={
                "public": {"user": ["read-feed"], "feed_member": ["add-activity"]},
                "private": {"feed_member": ["add-activity"]},
            },
        )
        plan = products.lockdown_plan(current)
        self.assertEqual(
            [(s.method, s.path, s.body) for s in plan],
            [
                ("PUT", "/api/v2/video/calltypes/default", {"grants": {"user": []}}),
                (
                    "PUT",
                    "/api/v2/video/calltypes/development",
                    {"grants": {"user": [], "guest": [], "anonymous": []}},
                ),
                ("PUT", "/api/v2/feeds/feed_visibilities/public", {"grants": {"user": []}}),
            ],
        )
        # Every planned request is a configuration write of the two families.
        for step in plan:
            self.assertTrue(products.is_configuration_write(step.method, step.path), step.path)
        # admin and the resource roles are never named: the lockdown is narrower than I1's.
        for step in plan:
            self.assertFalse(set(step.body["grants"]) - set(products.CLIENT_ROLES), step.body)

    def test_a_locked_state_has_no_plan_and_no_difference(self) -> None:
        locked = state(
            video={"default": {"admin": ["create-call"], "user": [], "call_member": ["read-call"]}},
            feeds={"public": {"user": [], "feed_member": ["add-activity"]}},
        )
        self.assertEqual(products.lockdown_plan(locked), [])
        self.assertEqual(products.verify(locked), [])

    def test_verify_names_each_client_grant_left(self) -> None:
        current = state(
            video={"default": {"user": ["read-call"], "guest": ["read-call"]}},
            feeds={"visible": {"anonymous": ["read-feed"]}},
        )
        self.assertEqual(
            products.verify(current),
            [
                "video call type default: grants for user not empty: ['read-call']",
                "video call type default: grants for guest not empty: ['read-call']",
                "feeds feed visibility visible: grants for anonymous not empty: ['read-feed']",
            ],
        )

    def test_a_product_that_is_not_available_is_neither_planned_nor_a_difference(self) -> None:
        current = state(
            video={"default": {"user": ["read-call"]}},
            feeds={"public": {"user": ["read-feed"]}},
            feeds_available="not available: HTTP 404 code 16: Not Found (the endpoints are not "
            "available on the application's deployment)",
        )
        plan = products.lockdown_plan(current)
        self.assertEqual([s.path for s in plan], ["/api/v2/video/calltypes/default"])
        self.assertEqual(
            products.verify(current),
            ["video call type default: grants for user not empty: ['read-call']"],
        )

    def test_a_read_that_is_not_verified_is_a_difference(self) -> None:
        current = state(video_available="not verified: HTTP 500 code -1: internal")
        self.assertEqual(products.lockdown_plan(current), [])
        self.assertEqual(
            products.verify(current),
            ["video configuration not verified: HTTP 500 code -1: internal"],
        )


class ReadAndListTest(unittest.TestCase):
    def test_read_configuration_and_the_baseline_record(self) -> None:
        server = FakeServer(UsageLedger())
        read = products.read_configuration(server)  # type: ignore[arg-type]
        self.assertEqual(read["video"]["availability"], "available")
        self.assertEqual(sorted(read["video"]["call_types"]), ["default", "development"])
        self.assertEqual(read["feeds"]["availability"], "available")
        self.assertEqual(sorted(read["feeds"]["feed_groups"]), ["notification", "timeline", "user"])
        self.assertEqual(server.products.seen[0][1], products.CALL_TYPES)
        record = products.baseline_record(read, "1729640")
        self.assertEqual(record["app_id"], "1729640")
        text = json.dumps(record)
        # No user, member or object: the record is settings and grants only.
        for word in ("user_id", "members", "created_by", '"activity"', "email", '"text"'):
            self.assertNotIn(word, text, word)
        self.assertEqual(
            record["video"]["call_types"]["default"]["grants"],
            read["video"]["call_types"]["default"]["grants"],
        )
        self.assertIn("settings", record["video"]["call_types"]["default"])

    def test_read_configuration_when_a_product_is_not_available(self) -> None:
        server = FakeServer(UsageLedger())
        server.products.available["feeds"] = False
        read = products.read_configuration(server)  # type: ignore[arg-type]
        self.assertTrue(
            read["feeds"]["availability"].startswith(
                "not available: HTTP 403 code 17: Feeds is not enabled"
            )
        )
        self.assertEqual(read["feeds"]["feed_visibilities"], {})
        self.assertEqual(read["video"]["availability"], "available")
        probe = products.probe(server)  # type: ignore[arg-type]
        self.assertEqual(probe["feeds"]["feed_visibilities"], [])
        self.assertEqual(probe["video"]["call_types"], ["default", "development"])

    def test_list_objects(self) -> None:
        server = FakeServer(UsageLedger())
        listed = products.list_objects(server)  # type: ignore[arg-type]
        self.assertEqual(
            listed, {"remaining_calls": [], "remaining_feeds": [], "remaining_activities": []}
        )
        state_ = server.products
        state_.calls["default:p061i1-c"] = {
            "id": "p061i1-c",
            "type": "default",
            "custom": {},
            "members": [],
            "created_by": "u",
        }
        state_.feeds["user:p061i1-ua"] = {"user_id": "p061i1-ua", "custom": {}}
        state_.activities["a-1"] = {
            "type": "post",
            "text": "t",
            "feeds": ["user:p061i1-ua"],
            "user_id": "p061i1-ua",
            "custom": {},
        }
        listed = products.list_objects(server)  # type: ignore[arg-type]
        self.assertEqual(listed["remaining_calls"], ["default:p061i1-c"])
        self.assertEqual(listed["remaining_feeds"], ["user:p061i1-ua"])
        self.assertEqual(listed["remaining_activities"], ["a-1"])
        server.products.available["video"] = False
        listed = products.list_objects(server)  # type: ignore[arg-type]
        self.assertIsNone(listed["remaining_calls"])
        self.assertTrue(listed["calls_listing"].startswith("not available: HTTP 403 code 17"))
        self.assertEqual(listed["remaining_feeds"], ["user:p061i1-ua"])


if __name__ == "__main__":
    unittest.main()
