"""The application configuration the proof applies, verifies and can restore.

Everything here is pure: plans are lists of requests computed from a snapshot,
and verification compares a re-read snapshot with the desired state. The live
command applies a plan through :class:`~glow_stream_proof.server_api.ServerApi`.

Design under proof: clients may only read their own match's channel. So:

* ``.app`` scope: the client roles ``user``, ``guest`` and ``anonymous`` get no
  application grants (no user search, no own-profile updates, no polls, no user
  groups, no uploads outside channels).
* Guest user creation is disabled.
* Every default channel type keeps its features but every role's grants are
  emptied, so no client role can create, join, read or send in it.
* ``glow-match``: members get ``read-channel`` only; every other role gets
  nothing; features a client could use to put content in front of the other
  member are off.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

MATCH_TYPE = "glow-match"
DEFAULT_TYPES = ("commerce", "gaming", "livestream", "messaging", "team")
CLIENT_APP_ROLES = ("user", "guest", "anonymous")
# Members may read their channel and nothing else. read-channel-members was
# removed on 25 September 2026 after the second live run: a member can write
# free-text custom data on its own membership (no permission governs that
# write), so the other member must not be able to read membership data.
MATCH_MEMBER_GRANTS = ("read-channel",)

# Features of the glow-match type. Read events stay on: the proof records that
# they carry no client free text. Typing events are off: on 25 September 2026
# the first live run (typing on) showed that a client's typing.start event
# delivers arbitrary custom fields, including free text, to the other member,
# and no permission governs typing events.
MATCH_FEATURES: dict[str, Any] = {
    "automod": "disabled",
    "automod_behavior": "flag",
    "max_message_length": 5000,
    "commands": [],
    "typing_events": False,
    "read_events": True,
    "connect_events": False,
    "custom_events": False,
    "reactions": False,
    "search": True,
    "replies": False,
    "quotes": False,
    "mutes": False,
    "uploads": False,
    "url_enrichment": False,
    "polls": False,
    "shared_locations": False,
    "user_message_reminders": False,
    "delivery_events": False,
    "count_messages": False,
    "mark_messages_pending": False,
    "push_notifications": False,
    "reminders": False,
}
# The create endpoint does not accept these; they are applied by an update.
_UPDATE_ONLY_FEATURES = ("quotes", "reminders")

APP_SETTING_KEYS = (
    "disable_auth_checks",
    "disable_permissions_checks",
    "permission_version",
    "guest_user_creation_disabled",
    "multi_tenant_enabled",
    "user_search_disallowed_roles",
    "enforce_unique_usernames",
    "revoke_tokens_issued_before",
    "before_message_send_hook_url",
    "custom_action_handler_url",
    "webhook_url",
    "event_hooks",
    "member_custom_on_typing_events_enabled",
    "member_custom_on_messages_enabled",
    "member_custom_on_mentioned_users_enabled",
    "channel_hide_members_only",
    "allow_multi_user_devices",
    "moderation_enabled",
    "image_moderation_enabled",
    "file_upload_config",
    "image_upload_config",
)
# Settings the proof requires as they are (the brief: the member_custom_on_*
# settings copy member custom data into messages, typing events and mentions,
# so they must stay off).
REQUIRED_APP_SETTINGS: dict[str, Any] = {
    "permission_version": "v2",
    "member_custom_on_typing_events_enabled": False,
    "member_custom_on_messages_enabled": False,
    "member_custom_on_mentioned_users_enabled": False,
}
CHANNEL_TYPE_FEATURE_KEYS = tuple(k for k in MATCH_FEATURES if k != "commands") + (
    "message_retention",
    "push_level",
    "skip_last_msg_update_for_system_msgs",
)


@dataclass(frozen=True)
class ApiRequest:
    method: str
    path: str
    body: dict[str, Any]
    purpose: str


def _app(snapshot: Mapping[str, Any]) -> Mapping[str, Any]:
    app = snapshot["app"]
    return cast(Mapping[str, Any], app["app"] if "app" in app else app)


def _types(snapshot: Mapping[str, Any]) -> Mapping[str, Any]:
    types = snapshot["channel_types"]
    return cast(Mapping[str, Any], types["channel_types"] if "channel_types" in types else types)


def baseline_record(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """The configuration needed to restore today's state; no users, no data."""
    app = _app(snapshot)
    types = _types(snapshot)
    return {
        "app_id": app.get("id"),
        "app_settings": {k: app.get(k) for k in APP_SETTING_KEYS if k in app},
        "app_grants": {role: list(app["grants"].get(role, [])) for role in CLIENT_APP_ROLES},
        "channel_types": {
            name: {
                "features": {k: cfg.get(k) for k in CHANNEL_TYPE_FEATURE_KEYS if k in cfg},
                "commands": sorted(c["name"] for c in cfg.get("commands", [])),
                "grants": {role: list(grants) for role, grants in sorted(cfg["grants"].items())},
            }
            for name, cfg in sorted(types.items())
        },
    }


def roles_in(snapshot: Mapping[str, Any]) -> list[str]:
    """Every role named in any channel type's grants (the roles a lock must cover)."""
    roles: set[str] = set()
    for cfg in _types(snapshot).values():
        roles.update(cfg.get("grants", {}).keys())
    return sorted(roles)


def match_type_grants(roles: list[str]) -> dict[str, list[str]]:
    grants: dict[str, list[str]] = {role: [] for role in roles}
    grants["channel_member"] = list(MATCH_MEMBER_GRANTS)
    return grants


def apply_plan(snapshot: Mapping[str, Any]) -> list[ApiRequest]:
    """Requests that bring the application to the desired configuration."""
    types = _types(snapshot)
    roles = roles_in(snapshot)
    plan = [
        ApiRequest(
            "PATCH",
            "/api/v2/app",
            {
                "disable_auth_checks": False,
                "disable_permissions_checks": False,
                "guest_user_creation_disabled": True,
                "grants": {role: [] for role in CLIENT_APP_ROLES},
            },
            "enforce auth and permission checks; disable guest creation; "
            "remove client roles' application grants",
        )
    ]
    for name in DEFAULT_TYPES:
        cfg = types[name]
        plan.append(
            ApiRequest(
                "PUT",
                f"/api/v2/chat/channeltypes/{name}",
                {
                    "automod": cfg["automod"],
                    "automod_behavior": cfg["automod_behavior"],
                    "max_message_length": cfg["max_message_length"],
                    "grants": {role: [] for role in roles},
                },
                f"lock default type {name}: empty grants for every role",
            )
        )
    create_body = {k: v for k, v in MATCH_FEATURES.items() if k not in _UPDATE_ONLY_FEATURES}
    create_body["grants"] = match_type_grants(roles)
    if MATCH_TYPE not in types:
        plan.append(
            ApiRequest(
                "POST",
                "/api/v2/chat/channeltypes",
                {"name": MATCH_TYPE, **create_body},
                f"create {MATCH_TYPE}",
            )
        )
    update_body = dict(MATCH_FEATURES)
    update_body["grants"] = match_type_grants(roles)
    plan.append(
        ApiRequest(
            "PUT",
            f"/api/v2/chat/channeltypes/{MATCH_TYPE}",
            update_body,
            f"set every {MATCH_TYPE} feature and grant",
        )
    )
    return plan


def verify(snapshot: Mapping[str, Any]) -> list[str]:
    """Differences between a re-read snapshot and the desired configuration."""
    problems: list[str] = []
    app = _app(snapshot)
    types = _types(snapshot)
    if app.get("disable_auth_checks") is not False:
        problems.append("disable_auth_checks is not false")
    if app.get("disable_permissions_checks") is not False:
        problems.append("disable_permissions_checks is not false")
    if app.get("guest_user_creation_disabled") is not True:
        problems.append("guest_user_creation_disabled is not true")
    for key, want in REQUIRED_APP_SETTINGS.items():
        have = app.get(key)
        if have != want or type(have) is not type(want):
            problems.append(f"{key} is {have!r}, want {want!r}")
    for role in CLIENT_APP_ROLES:
        granted = app.get("grants", {}).get(role, [])
        if granted:
            problems.append(f".app grants for {role} not empty: {granted}")
    for name in DEFAULT_TYPES:
        cfg = types.get(name)
        if cfg is None:
            problems.append(f"default type {name} missing")
            continue
        for role, granted in cfg.get("grants", {}).items():
            if granted:
                problems.append(f"{name} grants for {role} not empty: {granted}")
    match = types.get(MATCH_TYPE)
    if match is None:
        problems.append(f"{MATCH_TYPE} missing")
        return problems
    for key, want in MATCH_FEATURES.items():
        have = match.get(key)
        if key == "commands":
            have = sorted(c["name"] for c in match.get("commands", []))
        if have != want:
            problems.append(f"{MATCH_TYPE}.{key} is {have!r}, want {want!r}")
    for role, granted in match.get("grants", {}).items():
        want_grants = sorted(MATCH_MEMBER_GRANTS) if role == "channel_member" else []
        if sorted(granted) != want_grants:
            problems.append(f"{MATCH_TYPE} grants for {role} are {granted}, want {want_grants}")
    return problems


def restore_plan(record: Mapping[str, Any], *, delete_match_type: bool) -> list[ApiRequest]:
    """Requests that return the application to the recorded baseline.

    The match type can only be deleted once no channel of that type exists.
    """
    settings = record["app_settings"]
    plan = [
        ApiRequest(
            "PATCH",
            "/api/v2/app",
            {
                "guest_user_creation_disabled": settings["guest_user_creation_disabled"],
                "grants": copy.deepcopy(record["app_grants"]),
            },
            "restore guest creation and the client roles' application grants",
        )
    ]
    for name in DEFAULT_TYPES:
        cfg = record["channel_types"][name]
        features = cfg["features"]
        plan.append(
            ApiRequest(
                "PUT",
                f"/api/v2/chat/channeltypes/{name}",
                {
                    "automod": features["automod"],
                    "automod_behavior": features["automod_behavior"],
                    "max_message_length": features["max_message_length"],
                    "grants": copy.deepcopy(cfg["grants"]),
                },
                f"restore {name} grants recorded before the proof",
            )
        )
    if delete_match_type:
        plan.append(
            ApiRequest("DELETE", f"/api/v2/chat/channeltypes/{MATCH_TYPE}", {}, "delete match type")
        )
    return plan


def verify_restored(
    snapshot: Mapping[str, Any], record: Mapping[str, Any], *, match_type_deleted: bool
) -> list[str]:
    """Differences between a re-read snapshot and what :func:`restore_plan` sets."""
    problems: list[str] = []
    app = _app(snapshot)
    types = _types(snapshot)
    want_guest = record["app_settings"]["guest_user_creation_disabled"]
    if app.get("guest_user_creation_disabled") != want_guest:
        problems.append(
            f"guest_user_creation_disabled is {app.get('guest_user_creation_disabled')!r}, "
            f"want {want_guest!r}"
        )
    for role, want in record["app_grants"].items():
        have = app.get("grants", {}).get(role, [])
        if sorted(have) != sorted(want):
            problems.append(f".app grants for {role} are {sorted(have)}, want {sorted(want)}")
    for name in DEFAULT_TYPES:
        cfg = types.get(name)
        if cfg is None:
            problems.append(f"default type {name} missing")
            continue
        want_grants = record["channel_types"][name]["grants"]
        have_grants = cfg.get("grants", {})
        for role in sorted(set(want_grants) | set(have_grants)):
            have = sorted(have_grants.get(role, []))
            want = sorted(want_grants.get(role, []))
            if have != want:
                problems.append(f"{name} grants for {role} are {have}, want {want}")
    if match_type_deleted and MATCH_TYPE in types:
        problems.append(f"{MATCH_TYPE} still exists")
    return problems
