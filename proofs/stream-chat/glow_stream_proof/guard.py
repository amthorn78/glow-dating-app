"""One guard for every server call that changes users, channels, members or the app.

DM-04 finding 1 (P06.1-I2a). Every server request passes :func:`refusal` before
it is sent: the server client calls it from its request hook, so the SDK's
typed calls cannot bypass it (:mod:`glow_stream_proof.server_api`). A request
that bans, deactivates, deletes, revokes tokens, hides, freezes, removes a
member, or updates a user or member is refused when:

* it targets a user ID or a channel the run did not create: neither one the run
  recorded nor one whose ID contains the run's prefix; or
* it is a ``PATCH /api/v2/app`` other than a journalled temporary setting (guest
  user creation is the only one).

The guard goes further in the same direction. Every other request that changes
something must be of a kind the proof makes, with the same checks on every user
and channel it names; a channel type may change only in a journalled temporary
``glow-match`` toggle; and a request of any other kind is refused (for example
a batch channel update, a retention policy or a role). A message may be changed
or deleted only if the run recorded it (every mutating ``messages/{id}`` path,
since P06.1-I2b; until then only the delete). Reads (GET and HEAD, and the POST queries in
:data:`READ_POSTS`) are never refused.

Since P06.1-I2b the guard has a Video and Feeds scope (DM-05 finding 3): the same
families the runner's product op allows (:mod:`glow_stream_proof.products`), on calls,
feeds, activities, comments, reactions and follows the run created or recorded, plus
their deletes and the run's own users' Feeds data delete; the deny-list (join, go_live,
start_, stop_, broadcast, recording, transcription, caption, ring, notify, and the
fields ring, notify, video: true, create_notification_activity: true) is refused first;
and a Video or Feeds configuration write (a ``PUT`` of a call type's or a feed
visibility's grants) passes only in the scoped ``configure`` mode, whose scope allows
it, never during a run.

A refusal names the request's shape and the reason, never an identifier the run
did not create.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from . import products
from .configuration import MATCH_FEATURES, MATCH_TYPE

MUTATING = frozenset({"POST", "PUT", "PATCH", "DELETE"})
# POST requests that only read.
READ_POSTS = frozenset(
    {
        ("channels",),
        ("polls", "query"),
        ("messages", "history"),
        ("threads",),
        ("sync",),
        ("unread_batch",),
        # P06.1-I2b: the Video and Feeds queries.
        ("video", "calls"),
        ("video", "call", "members"),
        ("feeds", "feeds", "query"),
        ("feeds", "activities", "query"),
        ("feeds", "comments", "query"),
        ("feeds", "follows", "query"),
    }
)
# Keys whose values are user IDs (a string, or a list of strings or member objects).
USER_ID_KEYS = frozenset(
    {
        "user_id",
        "user_ids",
        "target_user_id",
        "target_id",
        "target_ids",
        "banned_by_id",
        "unbanned_by_id",
        "created_by_id",
        "blocked_user_id",
        "member_ids",
        "members",
        "add_members",
        "remove_members",
        "invites",
        "add_moderators",
        "demote_moderators",
        "assign_roles",
        "new_channel_owner_id",
        "new_call_owner_id",
        "created_by",
    }
)
# Keys whose object value is a user (its "id" is a user ID).
USER_OBJECT_KEYS = frozenset({"user", "banned_by", "unbanned_by", "created_by"})
# Keys whose values are channel CIDs ("type:id").
CHANNEL_KEYS = frozenset({"channel_cid", "channel_cids", "cid", "cids"})
# The fixed part of a glow-match type update, sent with its production values.
FIXED_TYPE_KEYS = ("automod", "automod_behavior", "max_message_length")
# The refusal of a request of a kind the proof does not make (P06.1-I2b: named once, for
# the Video and Feeds families too).
_OTHER_KIND = "not a kind of request this proof makes"
_USER_ACTIONS = frozenset(
    {"delete", "deactivate", "reactivate", "restore", "block", "unblock", "live_locations"}
)
_KEYWORDS = frozenset(
    {
        "app",
        "guest",
        "users",
        "channels",
        "channeltypes",
        "moderation",
        "messages",
        "polls",
        "usergroups",
        "threads",
        "query",
        "member",
        "members",
        "message",
        "event",
        "read",
        "unread",
        "hide",
        "show",
        "truncate",
        "file",
        "image",
        "ban",
        "unban",
        "mute",
        "unmute",
        "channel",
        "reaction",
        "reactions",
        "replies",
        "vote",
        "options",
        "batch",
        "history",
        "undelete",
        "action",
        # P06.1-I2b: Video and Feeds.
        "video",
        "feeds",
        "call",
        "calls",
        "calltypes",
        "feed_groups",
        "feed_visibilities",
        "activities",
        "comments",
        "follows",
        "join",
        *_USER_ACTIONS,
    }
)


class Scope(Protocol):
    """What the run created, and which temporary settings its journal holds."""

    def owns_user(self, user_id: str) -> bool: ...

    def owns_channel(self, channel: str) -> bool: ...

    def owns_message(self, message_id: str) -> bool: ...

    def owns_poll(self, poll_id: str) -> bool: ...

    def owns_group(self, group_id: str) -> bool: ...

    def journalled_app_settings(self) -> frozenset[str]: ...

    def journalled_type_features(self) -> frozenset[str]: ...

    # P06.1-I2b: Video and Feeds.
    def owns_call(self, call_id: str) -> bool: ...

    def owns_feed(self, feed_id: str) -> bool: ...

    def owns_activity(self, activity_id: str) -> bool: ...

    def owns_comment(self, comment_id: str) -> bool: ...

    def allows_product_configuration(self) -> bool: ...


@dataclass
class PrefixScope:
    """Ownership by prefix alone: what ``cleanup --apply`` may delete.

    Its journal is empty, so it refuses every application setting change.
    """

    prefix: str
    users: set[str] = field(default_factory=set)
    channels: set[str] = field(default_factory=set)

    def owns_user(self, user_id: str) -> bool:
        return user_id in self.users or self.prefix in user_id

    def owns_channel(self, channel: str) -> bool:
        return channel in self.channels or self.prefix in channel_id(channel)

    def owns_message(self, message_id: str) -> bool:
        return False

    def owns_poll(self, poll_id: str) -> bool:
        return False

    def owns_group(self, group_id: str) -> bool:
        return False

    def journalled_app_settings(self) -> frozenset[str]:
        return frozenset()

    def journalled_type_features(self) -> frozenset[str]:
        return frozenset()

    def owns_call(self, call_id: str) -> bool:
        return self.prefix in call_id

    def owns_feed(self, feed_id: str) -> bool:
        return self.prefix in feed_id

    def owns_activity(self, activity_id: str) -> bool:
        return False

    def owns_comment(self, comment_id: str) -> bool:
        return False

    def allows_product_configuration(self) -> bool:
        return False


@dataclass
class ConfigureScope(PrefixScope):
    """The scope of ``configure --products video,feeds --apply`` (P06.1-I2b): it owns
    nothing and allows one kind of request, a Video or Feeds configuration write."""

    def owns_user(self, user_id: str) -> bool:
        return False

    def owns_channel(self, channel: str) -> bool:
        return False

    def owns_call(self, call_id: str) -> bool:
        return False

    def owns_feed(self, feed_id: str) -> bool:
        return False

    def allows_product_configuration(self) -> bool:
        return True


def channel_id(channel: str) -> str:
    """The channel ID of a CID ("type:id") or of a bare ID."""
    return channel.split(":", 1)[1] if ":" in channel else channel


def parts_of(path: str) -> list[str]:
    """The path's segments after ``/api/v2/chat/`` or ``/api/v2/`` (v1 paths have neither)."""
    text = path.split("?", 1)[0].strip("/")
    for prefix in ("api/v2/chat/", "api/v2/"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    return [segment for segment in text.split("/") if segment]


def shape(parts: list[str]) -> str:
    """The path with every identifier replaced, for a refusal's message."""
    if parts[:1] == ["channels"] and len(parts) >= 3 and parts[1] not in _KEYWORDS:
        return "/".join(["channels", "{type}", "{id}", *(_generic(parts[3:]))])
    if parts[:2] == ["video", "call"] and len(parts) >= 4 and parts[2] not in _KEYWORDS:
        return "/".join(["video", "call", "{type}", "{id}", *(_generic(parts[4:]))])
    return "/".join(_generic(parts)) or "/"


def _generic(parts: Iterable[str]) -> list[str]:
    return [p if p in _KEYWORDS else "{id}" for p in parts]


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list | tuple):
        return [v for v in value if isinstance(v, str)]
    return []


def user_ids(obj: Any) -> list[str]:
    """Every user ID a request body or its parameters name."""
    found: list[str] = []
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if key == "users" and isinstance(value, Mapping):
                found += [str(k) for k in value]
            elif key in USER_ID_KEYS:
                found += _strings(value)
            if key in USER_OBJECT_KEYS and isinstance(value, Mapping):
                found += _strings(value.get("id"))
            if key == "users" and isinstance(value, list):
                found += [
                    str(item["id"])
                    for item in value
                    if isinstance(item, Mapping) and isinstance(item.get("id"), str)
                ]
            found += user_ids(value)
    elif isinstance(obj, list | tuple):
        for item in obj:
            found += user_ids(item)
    return found


def channel_refs(obj: Any) -> list[str]:
    """Every channel CID a request body or its parameters name."""
    found: list[str] = []
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if key in CHANNEL_KEYS:
                found += _strings(value)
            found += channel_refs(value)
    elif isinstance(obj, list | tuple):
        for item in obj:
            found += channel_refs(item)
    return found


def _unowned(users: Iterable[str], channels: Iterable[str], scope: Scope) -> str | None:
    if any(not scope.owns_user(u) for u in users):
        return "a user ID this run did not create"
    if any(not scope.owns_channel(c) for c in channels):
        return "a channel this run did not create"
    return None


def refusal(
    method: str, path: str, body: Any, params: Mapping[str, str] | None, scope: Scope
) -> str | None:
    """Why the guard refuses this server request, or ``None`` if it may be sent."""
    verb = method.upper()
    if verb not in MUTATING:
        return None
    parts = parts_of(path)
    if verb == "POST" and tuple(parts) in READ_POSTS:
        return None
    params = dict(params or {})
    reason = _reason(verb, parts, body, params, scope)
    if reason is None:
        return None
    return f"guard refused {verb} {shape(parts)}: {reason}"


def _reason(
    verb: str, parts: list[str], body: Any, params: Mapping[str, str], scope: Scope
) -> str | None:
    family = parts[0] if parts else ""
    users = user_ids(body) + user_ids(params)
    channels = channel_refs(body) + channel_refs(params)
    if family == "app":
        return _app(verb, parts, body, scope)
    if family == "channeltypes":
        return _channel_type(verb, parts, body, scope)
    if family == "users":
        if len(parts) >= 2 and parts[1] not in _USER_ACTIONS:
            users = [parts[1], *users]  # users/{user_id}/...
        if not users:
            return "no user named"
        return _unowned(users, channels, scope)
    if family == "guest":
        return _unowned(users, channels, scope) if users else "no user named"
    if family == "channels":
        if len(parts) == 2 and parts[1] == "delete":
            return _unowned(users, channels, scope) if channels else "no channel named"
        if len(parts) < 3 or parts[1] in _KEYWORDS:
            return "not a kind of request this proof makes"
        if len(parts) >= 5 and parts[3] == "member":
            # The deprecated member path: channels/{type}/{id}/member/{user_id} (P06.1-I2a).
            users = [parts[4], *users]
        return _unowned(users, [f"{parts[1]}:{parts[2]}", *channels], scope)
    if family == "moderation":
        if len(parts) < 2 or parts[1] not in ("ban", "unban", "mute", "unmute"):
            return "not a kind of request this proof makes"
        for source in (body, params):
            if isinstance(source, Mapping) and isinstance(source.get("type"), str):
                if isinstance(source.get("id"), str):
                    channels.append(f"{source['type']}:{source['id']}")
        return _unowned(users, channels, scope) if users else "no user named"
    if family == "messages":
        # Every mutating request on a message the run did not record is refused: an edit
        # or partial update (POST and PUT), an action, a reaction and its removal, an
        # undelete and a delete alike (P06.1-I2b; the I2a review's nit 4: until then only
        # the delete checked the message).
        if len(parts) >= 2 and parts[1] not in _KEYWORDS and not scope.owns_message(parts[1]):
            return "a message this run did not record"
        return _unowned(users, channels, scope)
    if family == "polls":
        if len(parts) >= 2 and not scope.owns_poll(parts[1]):
            return "a poll this run did not record"
        if len(parts) == 1 and verb in ("PUT", "PATCH"):
            # A poll update names its poll in the body (P06.1-I2a; the independent review).
            poll = body.get("id") if isinstance(body, Mapping) else None
            if not isinstance(poll, str) or not scope.owns_poll(poll):
                return "a poll this run did not record"
        return _unowned(users, channels, scope)
    if family == "usergroups":
        if len(parts) >= 2 and not scope.owns_group(parts[1]):
            return "a user group this run did not record"
        return _unowned(users, channels, scope)
    if family in ("video", "feeds"):
        return _product(verb, parts, body, params, users, scope)
    return "not a kind of request this proof makes"


def _product(
    verb: str,
    parts: list[str],
    body: Any,
    params: Mapping[str, str],
    users: list[str],
    scope: Scope,
) -> str | None:
    """The Video and Feeds scope (P06.1-I2b; DM-05 finding 3): the deny-list first, then a
    configuration write only in the scoped configure mode, then the families the runner's
    product op allows, on the run's own objects, plus their deletes."""
    path = "/api/v2/" + "/".join(parts)
    why = products.denied(path, body, params)
    if why:
        return f"on the Video and Feeds deny-list ({why})"
    if products.is_configuration_write(verb, path):
        if scope.allows_product_configuration():
            return None
        return "a Video or Feeds configuration change outside the scoped configure"
    if parts[0] == "video":
        return _video(verb, parts, users, scope)
    return _feeds(verb, parts, body, users, scope)


def _video(verb: str, parts: list[str], users: list[str], scope: Scope) -> str | None:
    # video/call/{type}/{id}: create or update; .../members, .../event, .../delete.
    if parts[1:2] == ["call"] and len(parts) >= 4 and parts[2] not in _KEYWORDS:
        tail = parts[4:]
        allowed = {(): ("POST", "PATCH"), ("members",): ("POST",), ("event",): ("POST",)}
        allowed[("delete",)] = ("POST",)
        if tuple(tail) not in allowed or verb not in allowed[tuple(tail)]:
            return _OTHER_KIND
        if not scope.owns_call(parts[3]):
            return "a call this run did not create"
        return _unowned(users, [], scope)
    return _OTHER_KIND


def _owned_feeds(fids: list[str], scope: Scope) -> str | None:
    if not fids:
        return "no feed named"
    if any(not scope.owns_feed(channel_id(fid)) for fid in fids):
        return "a feed this run did not create"
    return None


def _feeds(verb: str, parts: list[str], body: Any, users: list[str], scope: Scope) -> str | None:
    sub = parts[1:]
    named = body if isinstance(body, Mapping) else {}
    if sub[:1] == ["feed_groups"]:
        # feed_groups/{group}/feeds/{id}: create, update or delete a feed; a feed group
        # change is never made.
        if len(sub) == 4 and sub[2] == "feeds":
            return _owned_feeds([sub[3]], scope) or _unowned(users, [], scope)
        return _OTHER_KIND
    if sub == ["activities"] and verb == "POST":
        return _owned_feeds(_strings(named.get("feeds")), scope) or _unowned(users, [], scope)
    if sub[:1] == ["activities"] and len(sub) >= 2 and sub[1] not in _KEYWORDS:
        # activities/{id}: update or delete; activities/{id}/reactions[/{type}].
        if len(sub) > 2 and sub[2] != "reactions":
            return _OTHER_KIND
        if not scope.owns_activity(sub[1]):
            return "an activity this run did not record"
        return _unowned(users, [], scope)
    if sub == ["comments"] and verb == "POST":
        target = named.get("object_id")
        if named.get("object_type", "activity") != "activity" or not isinstance(target, str):
            return _OTHER_KIND
        if not scope.owns_activity(target):
            return "an activity this run did not record"
        return _unowned(users, [], scope)
    if sub[:1] == ["comments"] and len(sub) == 2 and sub[1] not in _KEYWORDS:
        if not scope.owns_comment(sub[1]):
            return "a comment this run did not record"
        return _unowned(users, [], scope)
    if sub == ["follows"] and verb == "POST":
        fids = _strings(named.get("source")) + _strings(named.get("target"))
        if len(fids) != 2:
            return "no feed named"
        return _owned_feeds(fids, scope) or _unowned(users, [], scope)
    if sub[:1] == ["follows"] and len(sub) == 3 and verb == "DELETE":
        return _owned_feeds(sub[1:3], scope) or _unowned(users, [], scope)
    if sub[:1] == ["users"] and len(sub) == 3 and sub[2] == "delete":
        # feeds/users/{user_id}/delete: the run's own user's Feeds data, at cleanup.
        return _unowned([sub[1], *users], [], scope)
    return _OTHER_KIND


def _app(verb: str, parts: list[str], body: Any, scope: Scope) -> str | None:
    keys = set(body) if isinstance(body, Mapping) else set()
    if verb != "PATCH" or len(parts) != 1 or not keys:
        return "not a journalled temporary setting"
    if not keys <= scope.journalled_app_settings():
        return "not a journalled temporary setting"
    return None


def _channel_type(verb: str, parts: list[str], body: Any, scope: Scope) -> str | None:
    if verb != "PUT" or parts[1:] != [MATCH_TYPE] or not isinstance(body, Mapping):
        return "not a journalled temporary toggle of the match type"
    fixed_ok = all(body.get(k, MATCH_FEATURES[k]) == MATCH_FEATURES[k] for k in FIXED_TYPE_KEYS)
    toggled = set(body) - set(FIXED_TYPE_KEYS)
    if not fixed_ok or not toggled <= scope.journalled_type_features():
        return "not a journalled temporary toggle of the match type"
    return None
