"""Read-only snapshot of the application's configuration and data."""

from __future__ import annotations

import json
from typing import Any

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
