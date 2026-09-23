"""Executable P02 contract oracle, not an authentication or persistence adapter.

Contexts are test-only authoritative facts. Production services must acquire them
from authenticated identity, scoped repositories and current policy; never JSON.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

FLOWS = {
    flow["id"]: flow
    for flow in json.loads((Path(__file__).parent / "production/flows-v1.json").read_text())[
        "flows"
    ]
}


@dataclass(frozen=True)
class Context:
    actor_id: str | None
    role: str
    owner_id: str | None
    participant_ids: tuple[str, ...] = ()
    scopes: frozenset[str] = field(default_factory=frozenset)
    session_state: str = "valid"
    object_id: str = "object-1"
    scoped_object_ids: frozenset[str] = field(default_factory=frozenset)
    active_match: bool = False
    current_version: int = 1
    expected_version: int = 1
    eligible: bool | None = None
    policies: frozenset[str] = field(default_factory=frozenset)


def authorized(role, context):
    if (
        role in ("owner", "participant", "moderator", "support")
        and context.session_state != "valid"
    ):
        return False
    if context.role != role:
        return False
    if role == "owner":
        return context.actor_id is not None and context.actor_id == context.owner_id
    if role == "participant":
        return context.actor_id is not None and context.actor_id in context.participant_ids
    if role in ("moderator", "support"):
        return (
            context.actor_id is not None
            and f"{role}:case" in context.scopes
            and context.object_id in context.scoped_object_ids
        )
    return role in ("auth", "system", "provider", "public", "presentation")


def read_projection(flow_id, definition, context):
    roles = FLOWS[flow_id]["projection_roles"].get(definition, ())
    if any(authorized(role, context) for role in roles):
        return "allowed"
    return "not_found"


def transition(flow_id, event, before, after, context):
    """Typed contract outcome; caller supplies current object and trusted context."""
    rule = next(
        (
            item
            for item in FLOWS[flow_id]["transitions"]
            if (item["event"], item["from"], item["to"]) == (event, before, after)
        ),
        None,
    )
    if rule is None:
        return "state_conflict"
    if not authorized(rule["role"], context):
        return "forbidden"
    if context.current_version != context.expected_version:
        return "stale_version"
    if not set(rule["policies"]).issubset(context.policies):
        return "policy_unresolved"
    if rule["active_match"] and not context.active_match:
        return "forbidden"
    if rule["eligible"] and context.eligible is not True:
        return "forbidden"
    return "allowed"
