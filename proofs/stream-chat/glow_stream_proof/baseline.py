"""Read-only snapshot of the application's configuration and data."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .configuration import APP_SETTING_KEYS
from .server_api import ServerApi


def read_snapshot(api: ServerApi) -> dict[str, Any]:
    app = api.require(api.get("/api/v2/app")).body
    channel_types = api.require(api.get("/api/v2/chat/channeltypes")).body
    roles = api.require(api.get("/api/v2/roles")).body
    users = api.require(
        api.get(
            "/api/v2/users",
            params={
                "payload": json.dumps(
                    {"filter_conditions": {}, "limit": 100, "include_deactivated_users": True}
                )
            },
        )
    ).body
    channels = api.require(
        api.raw("POST", "/api/v2/chat/channels", body={"filter_conditions": {}, "limit": 30})
    ).body
    return {
        "app": app,
        "channel_types": channel_types,
        "roles": roles,
        "users": users,
        "channels": channels,
    }


def read_configuration(api: ServerApi) -> dict[str, Any]:
    """Only what :func:`configuration.verify` needs: the app and the channel types."""
    app = api.require(api.get("/api/v2/app")).body
    channel_types = api.require(api.get("/api/v2/chat/channeltypes")).body
    return {"app": app, "channel_types": channel_types}


def public_snapshot(snapshot: Mapping[str, Any], prefix_root: str) -> dict[str, Any]:
    """The snapshot as it may be written to ``.work/``.

    It keeps the app's id, the settings the proof reads and the grants, the
    channel types and the role names. Users and channels are reduced to counts,
    plus the identifiers the proof itself created (they contain ``prefix_root``).
    No other user's identifier, name or custom field is kept, and no other app
    field (push, upload or webhook configuration) is written.
    """
    source = snapshot["app"]
    app = source.get("app", source) if isinstance(source, Mapping) else {}
    public_app: dict[str, Any] = {k: app.get(k) for k in APP_SETTING_KEYS if k in app}
    public_app["id"] = app.get("id")
    public_app["grants"] = app.get("grants", {})
    roles = snapshot.get("roles", {}).get("roles", [])
    users = snapshot.get("users", {}).get("users", [])
    ids = [str(u.get("id")) for u in users]
    channels = snapshot.get("channels", {}).get("channels", [])
    cids = [str((c.get("channel") or {}).get("cid")) for c in channels]
    return {
        "app": {"app": public_app},
        "channel_types": snapshot["channel_types"],
        "roles": {"roles": [{"name": r.get("name")} for r in roles if isinstance(r, Mapping)]},
        "users": {
            "count": len(users),
            "proof_user_ids": [i for i in ids if prefix_root in i],
            "dashboard_users": sum(
                1 for u in users if (u.get("custom") or {}).get("dashboard_user") is True
            ),
            "deleted_user_artifacts": sum(1 for i in ids if i.startswith("deleted-user-")),
            "other_users": sum(1 for i in ids if prefix_root not in i),
        },
        "channels": {
            "count": len(cids),
            "proof_cids": [c for c in cids if prefix_root in c],
        },
    }
