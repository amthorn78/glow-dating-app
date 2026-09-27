"""A fake of Stream's Video and Feeds for the offline tests (P06.1-I2b).

:class:`ProductState` keeps the two products' configuration (call types and their
grants, feed visibilities and their grants, feed groups) and their objects (calls,
feeds, activities, comments, reactions, follows), and answers the requests the harness
and a client can send them, the way Stream's documentation describes: a grants update
changes only the roles it names; a hard-deleted feed takes its activities with it and
its ID is not reused ("feed with id ... has been deleted"); a user's Feeds data delete
removes everything of that user's. The defaults are a model,
not Stream's behaviour: the built-in call types' default grants and the visibilities'
default grants are not published.

Knobs: ``available[product]`` (a product that is not available answers every request
with the configured status, code and message); ``allowed`` (what a client with the
``user`` role may do, by capability name); ``others_readable`` (whether a user may read
a call or feed it is not a member of).

:class:`ProductBehaviour` answers a fake client session's ``product`` op with this
state, as the session's own user.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from glow_stream_proof.client_bridge import Reply

PREFIX = "p061i1-simulated"
UNAVAILABLE_MESSAGE = (
    "{product} is not enabled for this application. Upgrade your plan to enable it."
)
CLIENT_ROLES = ("user", "guest", "anonymous")
# What a fresh application's call types and visibilities grant (a model).
DEFAULT_CALL_TYPE_GRANTS: dict[str, dict[str, list[str]]] = {
    "default": {
        "admin": ["create-call", "read-call", "update-call", "update-call-member", "join-call"],
        "user": ["create-call", "read-call", "update-call", "update-call-member", "join-call"],
        "call_member": ["read-call", "join-call", "send-audio", "send-video"],
        "guest": [],
        "anonymous": [],
    },
    "development": {
        "admin": ["create-call", "read-call", "update-call", "update-call-member", "join-call"],
        "user": ["create-call", "read-call", "update-call", "update-call-member", "join-call"],
        "call_member": ["read-call", "join-call", "send-audio", "send-video"],
        "guest": ["create-call", "read-call"],
        "anonymous": ["read-call"],
    },
}
DEFAULT_VISIBILITY_GRANTS: dict[str, dict[str, list[str]]] = {
    "public": {
        "user": [
            "read-feed",
            "read-activities",
            "add-activity",
            "add-comment",
            "add-activity-reaction",
            "follow",
        ],
        "feed_member": ["read-feed", "read-activities", "add-activity"],
        "guest": ["read-feed"],
        "anonymous": [],
    },
    "visible": {
        "user": ["read-feed", "read-activities", "follow", "add-comment", "add-activity-reaction"],
        "feed_member": ["read-feed", "read-activities", "add-activity"],
        "guest": [],
        "anonymous": [],
    },
    "private": {"feed_member": ["read-feed", "read-activities", "add-activity"]},
}
DEFAULT_FEED_GROUPS: dict[str, dict[str, Any]] = {
    "user": {"default_visibility": "visible", "default_follower_role": "feed_follower"},
    "timeline": {"default_visibility": "private", "default_follower_role": "feed_follower"},
    "notification": {"default_visibility": "private", "default_follower_role": "feed_follower"},
}
# Every capability a client with the user role may have in this fake, by the request.
ALL_CAPABILITIES = frozenset(
    {
        "create-call",
        "read-call",
        "update-call",
        "update-call-member",
        "send-event",
        "query-calls",
        "create-feed",
        "read-feed",
        "update-feed",
        "add-activity",
        "read-activities",
        "update-activity",
        "add-comment",
        "add-activity-reaction",
        "follow",
    }
)
_SEG = r"[^/]+"


def _dig(obj: Any, dotted: str) -> Any:
    for part in dotted.split("."):
        if not isinstance(obj, Mapping):
            return None
        obj = obj.get(part)
    return obj


@dataclass
class ProductState:
    available: dict[str, bool] = field(default_factory=lambda: {"video": True, "feeds": True})
    unavailable_status: int = 403
    unavailable_code: int = 17
    unavailable_message: str = UNAVAILABLE_MESSAGE
    call_type_grants: dict[str, dict[str, list[str]]] = field(
        default_factory=lambda: {
            k: {r: list(g) for r, g in v.items()} for k, v in DEFAULT_CALL_TYPE_GRANTS.items()
        }
    )
    visibility_grants: dict[str, dict[str, list[str]]] = field(
        default_factory=lambda: {
            k: {r: list(g) for r, g in v.items()} for k, v in DEFAULT_VISIBILITY_GRANTS.items()
        }
    )
    feed_groups: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {k: dict(v) for k, v in DEFAULT_FEED_GROUPS.items()}
    )
    # What a client with the user role may do; the server may do everything.
    allowed: set[str] = field(default_factory=lambda: set(ALL_CAPABILITIES))
    others_readable: bool = True
    # What a call's member and a feed's owner may do whatever the user role's grants: the
    # resource roles (call_member, feed_member) the lockdown does not touch.
    member_capabilities: set[str] = field(default_factory=lambda: {"read-call"})
    owner_capabilities: set[str] = field(
        default_factory=lambda: {
            "read-feed",
            "read-activities",
            "add-activity",
            "update-activity",
            "update-feed",
        }
    )
    # Objects.
    calls: dict[str, dict[str, Any]] = field(default_factory=dict)  # cid -> call
    feeds: dict[str, dict[str, Any]] = field(default_factory=dict)  # fid -> feed
    activities: dict[str, dict[str, Any]] = field(default_factory=dict)
    comments: dict[str, dict[str, Any]] = field(default_factory=dict)
    reactions: set[tuple[str, str, str]] = field(default_factory=set)
    follows: set[tuple[str, str]] = field(default_factory=set)
    events: list[dict[str, Any]] = field(default_factory=list)
    user_data_deleted: list[str] = field(default_factory=list)
    deleted_feeds: set[str] = field(default_factory=set)  # a deleted feed ID is not reused
    counter: int = 0
    # Every (method, path, actor) answered, for the tests.
    seen: list[tuple[str, str, str | None]] = field(default_factory=list)

    # -- helpers --

    def _next(self, kind: str) -> str:
        self.counter += 1
        return f"{kind}-{self.counter}"

    def _unavailable(self, product: str) -> tuple[int, dict[str, Any]]:
        return self.unavailable_status, {
            "code": self.unavailable_code,
            "message": self.unavailable_message.format(product=product.capitalize()),
        }

    @staticmethod
    def _refused(what: str = "Not Allowed") -> tuple[int, dict[str, Any]]:
        return 403, {"code": 17, "message": what}

    @staticmethod
    def _missing(what: str) -> tuple[int, dict[str, Any]]:
        return 404, {"code": 16, "message": f"{what} does not exist"}

    def _may(
        self, actor: str | None, capability: str, *, member: bool = False, owner: bool = False
    ) -> bool:
        if actor is None or capability in self.allowed:
            return True
        if member and capability in self.member_capabilities:
            return True
        return owner and capability in self.owner_capabilities

    def _call_view(self, cid: str) -> dict[str, Any]:
        call = self.calls[cid]
        return {
            "call": {
                "cid": cid,
                "id": call["id"],
                "type": call["type"],
                "custom": dict(call["custom"]),
                "created_by": {"id": call["created_by"]},
            },
            "members": [{"user_id": m, "user": {"id": m}} for m in call["members"]],
            "own_capabilities": [],
            "duration": "1.23ms",
        }

    def _feed_view(self, fid: str) -> dict[str, Any]:
        feed = self.feeds[fid]
        group, _, feed_id = fid.partition(":")
        return {
            "feed": fid,
            "id": feed_id,
            "group_id": group,
            "custom": dict(feed["custom"]),
            "created_by": {"id": feed["user_id"]},
        }

    def _activity_view(self, activity_id: str) -> dict[str, Any]:
        activity = self.activities[activity_id]
        return {
            "id": activity_id,
            "type": activity["type"],
            "text": activity["text"],
            "feeds": list(activity["feeds"]),
            "custom": dict(activity["custom"]),
            "user": {"id": activity["user_id"]},
        }

    # -- the requests --

    def request(
        self,
        method: str,
        path: str,
        body: Any,
        params: Mapping[str, Any] | None,
        *,
        actor: str | None,
    ) -> tuple[int, Any]:
        """Answer one request; ``actor`` is the client's user, or ``None`` for the server."""
        self.seen.append((method, path, actor))
        product = "video" if path.startswith("/api/v2/video/") else "feeds"
        if not self.available.get(product, True):
            return self._unavailable(product)
        body = body if isinstance(body, Mapping) else {}
        params = dict(params or {})
        parts = [p for p in path.split("?", 1)[0].strip("/").split("/") if p][2:]  # after api/v2
        if product == "video":
            return self._video(method, parts, body, params, actor)
        return self._feeds(method, parts, body, params, actor)

    def _video(
        self,
        method: str,
        parts: list[str],
        body: Mapping[str, Any],
        params: dict[str, Any],
        actor: str | None,
    ) -> tuple[int, Any]:
        sub = parts[1:]
        if sub == ["calltypes"] and method == "GET":
            return 200, {
                "duration": "1ms",
                "call_types": {
                    name: {
                        "name": name,
                        "grants": {r: list(g) for r, g in grants.items()},
                        "settings": {"audio": {"mic_default_on": True}},
                        "notification_settings": {"enabled": False},
                    }
                    for name, grants in self.call_type_grants.items()
                },
            }
        if sub[:1] == ["calltypes"] and len(sub) == 2 and method == "PUT":
            grants = self.call_type_grants.get(sub[1])
            if grants is None:
                return self._missing("call type")
            for role, granted in (body.get("grants") or {}).items():
                grants[role] = list(granted)  # only the roles named change
            return 201, {"duration": "1ms", "name": sub[1], "grants": grants}
        if sub == ["calls"] and method == "POST":
            creator = _dig(body, "filter_conditions.created_by_user_id")
            listed = [
                self._call_view(cid)
                for cid, call in sorted(self.calls.items())
                if (creator is None or call["created_by"] == creator)
                and (actor is None or self.others_readable or actor in call["members"])
            ]
            if actor is not None and not self._may(actor, "query-calls"):
                return self._refused()
            return 201, {"duration": "1ms", "calls": listed}
        if sub == ["call", "members"] and method == "POST":
            cid = f"{body.get('type')}:{body.get('id')}"
            if cid not in self.calls:
                return self._missing("call")
            return 201, {"duration": "1ms", "members": self._call_view(cid)["members"]}
        if sub[:1] == ["call"] and len(sub) >= 3:
            call_type, call_id, tail = sub[1], sub[2], sub[3:]
            cid = f"{call_type}:{call_id}"
            if call_type not in self.call_type_grants:
                return self._missing("call type")
            if tail == [] and method == "POST":
                if cid not in self.calls:
                    if not self._may(actor, "create-call"):
                        return self._refused()
                    data = body.get("data") or {}
                    members = [
                        m["user_id"] for m in data.get("members") or [] if isinstance(m, Mapping)
                    ]
                    creator = actor or data.get("created_by_id") or "server"
                    if creator not in members:
                        members.insert(0, creator)
                    self.calls[cid] = {
                        "id": call_id,
                        "type": call_type,
                        "custom": dict(data.get("custom") or {}),
                        "members": members,
                        "created_by": creator,
                    }
                    return 201, {**self._call_view(cid), "created": True}
                if not self._may(actor, "read-call", member=actor in self.calls[cid]["members"]):
                    return self._refused()
                return 201, {**self._call_view(cid), "created": False}
            if cid not in self.calls:
                return self._missing("call")
            call = self.calls[cid]
            member = actor is None or actor in call["members"]
            if tail == [] and method == "GET":
                if not self._may(actor, "read-call", member=member):
                    return self._refused()
                if actor is not None and not member and not self.others_readable:
                    return self._refused()
                return 200, self._call_view(cid)
            if tail == [] and method == "PATCH":
                if not self._may(actor, "update-call", member=member):
                    return self._refused()
                call["custom"] = {**call["custom"], **(body.get("custom") or {})}
                return 200, self._call_view(cid)
            if tail == ["members"] and method == "POST":
                if not self._may(actor, "update-call-member", member=member):
                    return self._refused()
                for m in body.get("update_members") or []:
                    if isinstance(m, Mapping) and m.get("user_id") not in call["members"]:
                        call["members"].append(str(m["user_id"]))
                for uid in body.get("remove_members") or []:
                    if uid in call["members"]:
                        call["members"].remove(uid)
                return 200, {"duration": "1ms", "members": self._call_view(cid)["members"]}
            if tail == ["event"] and method == "POST":
                if not self._may(actor, "send-event", member=member):
                    return self._refused()
                self.events.append(
                    {"cid": cid, "custom": dict(body.get("custom") or {}), "user": actor}
                )
                return 201, {"duration": "1ms", "event": {"type": "custom", "call_cid": cid}}
            if tail == ["delete"] and method == "POST":
                if actor is not None:
                    return self._refused()
                del self.calls[cid]
                return 200, {"duration": "1ms", "task_id": "t1"}
        return self._refused("Not a kind of request this fake answers")

    def _feeds(
        self,
        method: str,
        parts: list[str],
        body: Mapping[str, Any],
        params: dict[str, Any],
        actor: str | None,
    ) -> tuple[int, Any]:
        sub = parts[1:]
        if sub == ["feed_visibilities"] and method == "GET":
            return 200, {
                "duration": "1ms",
                "feed_visibilities": {
                    name: {"name": name, "grants": {r: list(g) for r, g in grants.items()}}
                    for name, grants in self.visibility_grants.items()
                },
            }
        if sub[:1] == ["feed_visibilities"] and len(sub) == 2 and method == "PUT":
            grants = self.visibility_grants.get(sub[1])
            if grants is None:
                return self._missing("feed visibility")
            for role, granted in (body.get("grants") or {}).items():
                grants[role] = list(granted)
            return 200, {"duration": "1ms", "feed_visibility": {"name": sub[1], "grants": grants}}
        if sub == ["feed_groups"] and method == "GET":
            return 200, {
                "duration": "1ms",
                "groups": {k: {"id": k, **v} for k, v in self.feed_groups.items()},
            }
        if sub[:1] == ["feed_groups"] and len(sub) == 4 and sub[2] == "feeds":
            group, feed_id = sub[1], sub[3]
            fid = f"{group}:{feed_id}"
            if group not in self.feed_groups:
                return self._missing("feed group")
            if method == "POST":
                if fid in self.deleted_feeds and fid not in self.feeds:
                    return 404, {
                        "code": 16,
                        "message": "GetOrCreateFeed failed with error: "
                        f'"feed with id: {feed_id} has been deleted"',
                    }
                if fid not in self.feeds:
                    if not self._may(actor, "create-feed"):
                        return self._refused()
                    owner = actor or body.get("user_id") or feed_id
                    data = body.get("data") or {}
                    self.feeds[fid] = {"user_id": owner, "custom": dict(data.get("custom") or {})}
                    created = True
                else:
                    created = False
                    feed = self.feeds[fid]
                    own = actor is None or feed["user_id"] == actor
                    if not self._may(actor, "read-feed", owner=own):
                        return self._refused()
                    if not own and not self.others_readable:
                        return self._refused()
                acts = [
                    self._activity_view(a)
                    for a, act in sorted(self.activities.items())
                    if fid in act["feeds"]
                ]
                return 201, {
                    "duration": "1ms",
                    "created": created,
                    "feed": self._feed_view(fid),
                    "activities": acts,
                }
            if fid not in self.feeds:
                return self._missing("feed")
            if method == "PUT":
                if not self._may(
                    actor, "update-feed", owner=actor is None or self.feeds[fid]["user_id"] == actor
                ):
                    return self._refused()
                self.feeds[fid]["custom"] = dict(body.get("custom") or {})
                return 200, {"duration": "1ms", "feed": self._feed_view(fid)}
            if method == "DELETE":
                if actor is not None:
                    return self._refused()
                del self.feeds[fid]
                self.deleted_feeds.add(fid)
                for a in [a for a, act in self.activities.items() if fid in act["feeds"]]:
                    self._drop_activity(a)
                self.follows = {f for f in self.follows if fid not in f}
                return 200, {"duration": "1ms"}
        if sub == ["feeds", "query"] and method == "POST":
            return 201, {
                "duration": "1ms",
                "feeds": [self._feed_view(f) for f in sorted(self.feeds)],
            }
        if sub == ["activities"] and method == "POST":
            fids = [str(f) for f in body.get("feeds") or []]
            if any(f not in self.feeds for f in fids):
                return self._missing("feed")
            owner = actor or body.get("user_id") or "server"
            for f in fids:
                # Only the feed's owner, a member or a moderator may post into it (Stream's
                # "visible" and "private" visibilities); the server may.
                if actor is not None and self.feeds[f]["user_id"] != actor:
                    return self._refused()
            if not self._may(actor, "add-activity", owner=bool(fids)):
                return self._refused()
            activity_id = self._next("a")
            self.activities[activity_id] = {
                "type": body.get("type"),
                "text": body.get("text"),
                "feeds": fids,
                "user_id": owner,
                "custom": dict(body.get("custom") or {}),
            }
            return 201, {"duration": "1ms", "activity": self._activity_view(activity_id)}
        if sub == ["activities", "query"] and method == "POST":
            if not self._may(actor, "read-activities"):
                return self._refused()
            wanted = _dig(body, "filter.user_id")
            listed = [
                self._activity_view(a)
                for a, act in sorted(self.activities.items())
                if (wanted is None or act["user_id"] == wanted)
                and (actor is None or self.others_readable or act["user_id"] == actor)
            ]
            return 201, {"duration": "1ms", "activities": listed}
        if sub[:1] == ["activities"] and len(sub) >= 2:
            activity_id, tail = sub[1], sub[2:]
            if activity_id not in self.activities:
                return self._missing("activity")
            activity = self.activities[activity_id]
            if tail == [] and method == "GET":
                return 200, {"duration": "1ms", "activity": self._activity_view(activity_id)}
            if tail == [] and method == "PUT":
                if actor is not None and activity["user_id"] != actor:
                    return self._refused()
                if not self._may(actor, "update-activity", owner=True):
                    return self._refused()
                if "text" in body:
                    activity["text"] = body["text"]
                if "custom" in body:
                    activity["custom"] = dict(body["custom"] or {})
                return 200, {"duration": "1ms", "activity": self._activity_view(activity_id)}
            if tail == [] and method == "DELETE":
                if actor is not None:
                    return self._refused()
                self._drop_activity(activity_id)
                return 200, {"duration": "1ms"}
            if tail == ["reactions"] and method == "POST":
                if not self._may(actor, "add-activity-reaction"):
                    return self._refused()
                user = actor or body.get("user_id") or "server"
                kind = str(body.get("type"))
                self.reactions.add((activity_id, kind, user))
                return 201, {
                    "duration": "1ms",
                    "activity": self._activity_view(activity_id),
                    "reaction": {"activity_id": activity_id, "type": kind, "user": {"id": user}},
                }
            if len(tail) == 2 and tail[0] == "reactions" and method == "DELETE":
                if actor is not None:
                    return self._refused()
                user = str(params.get("user_id"))
                if (activity_id, tail[1], user) not in self.reactions:
                    return self._missing("reaction")
                self.reactions.discard((activity_id, tail[1], user))
                return 200, {"duration": "1ms"}
        if sub == ["comments"] and method == "POST":
            if not self._may(actor, "add-comment"):
                return self._refused()
            target = str(body.get("object_id"))
            if target not in self.activities:
                return self._missing("activity")
            user = actor or body.get("user_id") or "server"
            comment_id = self._next("c")
            self.comments[comment_id] = {
                "object_id": target,
                "text": body.get("comment"),
                "user_id": user,
            }
            return 201, {
                "duration": "1ms",
                "comment": {
                    "id": comment_id,
                    "object_id": target,
                    "text": body.get("comment"),
                    "user": {"id": user},
                },
            }
        if sub == ["comments", "query"] and method == "POST":
            return 201, {
                "duration": "1ms",
                "comments": [{"id": c, **v} for c, v in sorted(self.comments.items())],
            }
        if sub[:1] == ["comments"] and len(sub) == 2:
            if sub[1] not in self.comments:
                return self._missing("comment")
            if method == "GET":
                return 200, {"duration": "1ms", "comment": {"id": sub[1], **self.comments[sub[1]]}}
            if method == "DELETE":
                if actor is not None:
                    return self._refused()
                del self.comments[sub[1]]
                return 200, {"duration": "1ms"}
        if sub == ["follows"] and method == "POST":
            if not self._may(actor, "follow"):
                return self._refused()
            source, target = str(body.get("source")), str(body.get("target"))
            if source not in self.feeds or target not in self.feeds:
                return self._missing("feed")
            if actor is not None and self.feeds[source]["user_id"] != actor:
                return self._refused()
            self.follows.add((source, target))
            return 201, {
                "duration": "1ms",
                "follow": {
                    "source_feed": self._feed_view(source),
                    "target_feed": self._feed_view(target),
                },
            }
        if sub == ["follows", "query"] and method == "POST":
            return 201, {
                "duration": "1ms",
                "follows": [
                    {"source_feed": {"feed": s}, "target_feed": {"feed": t}}
                    for s, t in sorted(self.follows)
                ],
            }
        if sub[:1] == ["follows"] and len(sub) == 3 and method == "DELETE":
            if actor is not None:
                return self._refused()
            pair = (sub[1], sub[2])
            if pair not in self.follows:
                return self._missing("follow")
            self.follows.discard(pair)
            return 200, {"duration": "1ms"}
        if sub[:1] == ["users"] and len(sub) == 3 and sub[2] == "delete" and method == "POST":
            if actor is not None:
                return self._refused()
            uid = sub[1]
            self.user_data_deleted.append(uid)
            for fid in [f for f, feed in self.feeds.items() if feed["user_id"] == uid]:
                del self.feeds[fid]
                self.follows = {f for f in self.follows if fid not in f}
            for a in [a for a, act in self.activities.items() if act["user_id"] == uid]:
                self._drop_activity(a)
            for c in [c for c, com in self.comments.items() if com["user_id"] == uid]:
                del self.comments[c]
            self.reactions = {r for r in self.reactions if r[2] != uid}
            return 200, {"duration": "1ms"}
        return self._refused("Not a kind of request this fake answers")

    def _drop_activity(self, activity_id: str) -> None:
        self.activities.pop(activity_id, None)
        for c in [c for c, com in self.comments.items() if com["object_id"] == activity_id]:
            del self.comments[c]
        self.reactions = {r for r in self.reactions if r[0] != activity_id}


def client_record(
    method: str,
    path: str,
    body: Any,
    params: Mapping[str, Any] | None,
    user_id: str,
    status: int,
    response: Any,
) -> dict[str, Any]:
    """A request record as the runner writes one for a product request."""
    return {
        "method": method.upper(),
        "path": path,
        "params": {"user_id": user_id, "api_key": "k", **dict(params or {})},
        "body": body,
        "status": status,
        "response": response,
    }


def client_reply(
    method: str,
    path: str,
    body: Any,
    params: Mapping[str, Any] | None,
    user_id: str,
    status: int,
    response: Any,
) -> Reply:
    rec = client_record(method, path, body, params, user_id, status, response)
    if status < 300:
        return Reply(True, {}, None, [rec], api_calls=1)
    code = response.get("code") if isinstance(response, Mapping) else None
    message = response.get("message") if isinstance(response, Mapping) else None
    error = {"status": status, "code": code, "message": message, "kind": "api"}
    return Reply(False, None, error, [rec], api_calls=1)


@dataclass
class ProductBehaviour:
    """Answers a fake client session's ``product`` op from a :class:`ProductState`, as the
    session's user (``{PREFIX}-u<label>``)."""

    state: ProductState
    prefix: str = PREFIX

    def user_of(self, label: str) -> str:
        return f"{self.prefix}-u{label.split('-', 1)[0].lower()}"

    def __call__(self, session: Any, op: str, params: dict[str, Any]) -> Reply | None:
        if op != "product":
            return None
        method, path = str(params.get("method")), str(params.get("path"))
        body, query = params.get("body"), params.get("params")
        uid = self.user_of(session.label)
        status, response = self.state.request(method, path, body, query, actor=uid)
        return client_reply(method, path, body, query, uid, status, response)


def is_product_path(path: str) -> bool:
    return bool(re.match(r"^/api/v2/(video|feeds)/", path))
