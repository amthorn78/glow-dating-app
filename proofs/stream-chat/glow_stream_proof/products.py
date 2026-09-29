"""Stream Video and Feeds: what the proof may send them, and their lockdown (P06.1-I2b).

The brief: "Video and Feeds: what a user token can do, and a lockdown by configuration
only. No media session, no push, nothing that could incur a charge." Glow uses neither
product; the same user token reaches both.

What this module holds:

* **The allowlist and the deny-list** (DM-05 finding 3). A client may send a product
  request only through the runner's ``product`` op, whose path allowlist and deny-list
  are in ``client/product-op.cjs``; the server-side guard (:mod:`glow_stream_proof.guard`)
  carries the same tables from here, plus the deletes of run-owned objects and, in the
  scoped ``configure`` mode only, the two configuration writes. ``tests/test_products.py``
  drives the JS file and checks that the two tables agree. Refused before anything is
  sent: a path holding ``join``, ``go_live``, ``start_``, ``stop_``, ``broadcast``,
  ``recording``, ``transcription``, ``caption``, ``ring``, ``notify``, ``rtmp``, ``hls``
  or ``egress``; a body or query carrying ``ring`` or ``notify``, ``video: true`` or
  ``create_notification_activity: true`` (each key in any letter case, and true as a
  boolean or as ``"true"`` in any letter case; P06.1-C4); any method and path outside
  the allowlist. Since P06.1-C4 the runner applies the op's check to every request it
  sends to either product's host or to a path under ``/api/v2/video`` or
  ``/api/v2/feeds``, whatever op made it (:func:`is_product_path`; the I2b review's
  finding 1).
* **The configuration**, read-only: the call types and their grants (Video), the feed
  visibilities and their grants, and the feed groups (Feeds). Stream configures Chat
  grants per channel type, Feeds grants per feed visibility and Video grants per call
  type; feed groups carry no grants (Stream, "Permissions"; the research in the
  evidence record's "P06.1-I2b").
* **The lockdown target**: the client roles ``user``, ``guest`` and ``anonymous`` hold no
  grant in any call type or feed visibility. The plan is a difference: one ``PUT`` per
  call type or visibility where a client role still holds a grant, naming only those
  roles with ``[]``. Stream documents that "a grants update only changes the roles
  mentioned in the request", so ``admin`` and the resource roles (``call_member``,
  ``feed_member``, ...) are untouched: this lockdown is narrower than I1's, which emptied
  every role's chat grants, ``admin`` included (DM-05 finding 9 (a)).
* **Availability**: whether a product answers its configuration read. Stream documents no
  "product not enabled" error; its Feeds migration guide says a 404 means "the endpoints
  are not yet available on your app's deployment". A product whose read is not 2xx is
  recorded as not available or not verified, never locked, and never a difference.
* **The product-finding rule** (DM-05 finding 2 (c)): a 4xx answer other than 402 whose
  code is not 99 and whose message says the product is not enabled or not available is
  that product's finding, not a charge signal (:func:`unavailable_answer`; the "upgrade"
  exemption is in :func:`glow_stream_proof.usage.charge_signal`).

Nothing here calls Stream except :func:`read_configuration`, :func:`list_objects` and
:func:`probe`, which only read.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .configuration import ApiRequest
from .server_api import ApiResult, ServerApi
from .usage import product_unavailable_wording

PRODUCTS = ("video", "feeds")
# The roles the lockdown empties; equal to configuration.CLIENT_APP_ROLES (a test says so).
CLIENT_ROLES = ("user", "guest", "anonymous")

# Configuration paths (the only writes the scoped configure may make are PUTs under the
# first and the third).
CALL_TYPES = "/api/v2/video/calltypes"
FEED_GROUPS = "/api/v2/feeds/feed_groups"
FEED_VISIBILITIES = "/api/v2/feeds/feed_visibilities"

# Set by the commit after the live ``configure --products video,feeds --apply`` to the UTC
# stamp of that apply: from then on ``configuration.verify`` compares the products'
# state with the lockdown target too, so preflight, the end of every run and the dry-run
# ``configure`` see any drift. Before the apply the products' differences are the plan,
# not drift, and the runs before the lockdown (run 1, run V1) must be allowed. Applied on
# 27 September 2026 at 05:58:31 UTC (its record: configure-products-20260927T055831Z).
LOCKDOWN_APPLIED: str | None = "2026-09-27T05:58:31Z"

# The committed Video and Feeds baseline, read before the lockdown (``baseline`` then
# ``record-products-baseline``, 27 September 2026). Since P06.1-C4 :func:`verify` compares
# every other role's grants, each call type's settings and notification settings, and each
# feed group's recorded fields with it (the I2b review's finding 2).
PRODUCTS_BASELINE = (
    Path(__file__).resolve().parent.parent / "baseline" / "video-feeds-1729640-2026-09-27.json"
)

_SEG = r"[^/]+"
# (pattern, methods): what a client may send through the runner's product op.
CLIENT_ALLOWLIST: tuple[tuple[re.Pattern[str], frozenset[str]], ...] = (
    (re.compile(rf"^/api/v2/video/call/{_SEG}/{_SEG}$"), frozenset({"GET", "POST", "PATCH"})),
    (re.compile(rf"^/api/v2/video/call/{_SEG}/{_SEG}/members$"), frozenset({"POST"})),
    (re.compile(rf"^/api/v2/video/call/{_SEG}/{_SEG}/event$"), frozenset({"POST"})),
    (re.compile(r"^/api/v2/video/call/members$"), frozenset({"POST"})),
    (re.compile(r"^/api/v2/video/calls$"), frozenset({"POST"})),
    (re.compile(rf"^/api/v2/feeds/feed_groups/{_SEG}/feeds/{_SEG}$"), frozenset({"POST", "PUT"})),
    (re.compile(r"^/api/v2/feeds/feeds/query$"), frozenset({"POST"})),
    (re.compile(r"^/api/v2/feeds/activities$"), frozenset({"POST"})),
    (re.compile(r"^/api/v2/feeds/activities/query$"), frozenset({"POST"})),
    (re.compile(rf"^/api/v2/feeds/activities/{_SEG}$"), frozenset({"GET", "PUT"})),
    (re.compile(rf"^/api/v2/feeds/activities/{_SEG}/reactions$"), frozenset({"POST"})),
    (re.compile(r"^/api/v2/feeds/comments$"), frozenset({"POST"})),
    (re.compile(r"^/api/v2/feeds/comments/query$"), frozenset({"POST"})),
    (re.compile(rf"^/api/v2/feeds/comments/{_SEG}$"), frozenset({"GET"})),
    (re.compile(r"^/api/v2/feeds/follows$"), frozenset({"POST"})),
    (re.compile(r"^/api/v2/feeds/follows/query$"), frozenset({"POST"})),
)
DENIED_PATH_WORDS = (
    "join",
    "go_live",
    "start_",
    "stop_",
    "broadcast",
    "recording",
    "transcription",
    "caption",
    "ring",
    "notify",
    "rtmp",
    "hls",
    "egress",
)
DENIED_KEYS = ("ring", "notify")
DENIED_TRUE_KEYS = ("video", "create_notification_activity")
# Stream's Feeds migration guide on a 404 from a Feeds endpoint.
_NOT_ON_DEPLOYMENT = "the endpoints are not available on the application's deployment"


def _is_true(item: Any) -> bool:
    """A boolean true, or the string ``"true"`` in any letter case."""
    return item is True or (isinstance(item, str) and item.lower() == "true")


def denied_field(value: Any) -> str | None:
    """The key of a denied field anywhere in a body or query, in lower case, or ``None``.
    A key matches in any letter case, and a denied-true key's value is a boolean true or
    ``"true"`` in any letter case (P06.1-C4; the I2b review's nit 3)."""
    if isinstance(value, list | tuple):
        for item in value:
            found = denied_field(item)
            if found:
                return found
        return None
    if isinstance(value, Mapping):
        for key, item in value.items():
            # In any letter case (P06.1-C4; the I2b review's nit 3): Stream's JSON
            # decoding may match a field name without regard to case.
            name = str(key).lower()
            if name in DENIED_KEYS:
                return name
            if name in DENIED_TRUE_KEYS and _is_true(item):
                return f"{name}: true"
            found = denied_field(item)
            if found:
                return found
    return None


# Where a Video or Feeds request can go on any Stream host: the REST prefixes and the Video
# and Feeds clients' own bare forms (as client/product-op.cjs's PRODUCT_PREFIXES).
PRODUCT_PREFIXES = ("/api/v2/video", "/api/v2/feeds", "/video", "/feeds")
DECODE_ROUNDS = 8
_ESCAPE = re.compile(r"%([0-9A-Fa-f]{2})")


def _decode_once(text: str) -> str:
    """One round of percent-decoding, byte by byte (``%XX`` becomes the character with that
    code), so that it never fails: an escape that is not valid UTF-8 (``%ff``, ``%c0``) is
    decoded like any other, one that is not hex (``%zz``) is left (P06.1-C4; C4's own review
    found that a strict decode stopped at ``%ff`` and left the whole path undecoded)."""
    return _ESCAPE.sub(lambda m: chr(int(m.group(1), 16)), text)


def normalized_path(path: str) -> str | None:
    """A path as a server may read it: the query dropped, percent-encoding decoded until it
    no longer changes, backslashes read as slashes, empty and dot segments resolved; letter
    case is kept. ``None`` when it still changes after :data:`DECODE_ROUNDS` rounds. The
    Python mirror of ``normalizedPath`` in ``client/product-op.cjs``; a test compares the two
    (P06.1-C4)."""
    text = path.split("?", 1)[0].replace("\\", "/")
    for _ in range(DECODE_ROUNDS):
        decoded = _decode_once(text).replace("\\", "/")
        if decoded == text:
            break
        text = decoded
    else:
        return None
    out: list[str] = []
    for segment in text.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if out:
                out.pop()
        else:
            out.append(segment)
    return "/" + "/".join(out)


def is_product_path(path: str) -> bool:
    """Whether a path reaches Video or Feeds once letter case, percent-encoding and dot
    segments are normalized (P06.1-C4; the I2b review's finding 1). A path whose encoding
    does not settle counts as one: the runner refuses it."""
    normalized = normalized_path(path)
    if normalized is None:
        return True
    folded = normalized.lower()
    return any(folded == p or folded.startswith(p + "/") for p in PRODUCT_PREFIXES)


def denied_path(path: str) -> str | None:
    """Why a path is on the deny-list, or ``None``."""
    clean = path.split("?", 1)[0]
    for segment in clean.lower().split("/"):
        for word in DENIED_PATH_WORDS:
            if word in segment:
                return f"denied path ({word})"
    return None


def denied(path: str, body: Any, params: Mapping[str, Any] | None) -> str | None:
    """Why a Video or Feeds request is on the deny-list, or ``None``."""
    why = denied_path(path)
    if why:
        return why
    field = denied_field(body) or denied_field(params)
    if field:
        return f"denied field ({field})"
    return None


def client_refusal(
    method: str, path: str, body: Any, params: Mapping[str, Any] | None
) -> str | None:
    """Why the client's product op refuses this request (the Python mirror of
    ``client/product-op.cjs``, in the same order), or ``None`` when it may be sent."""
    clean = path.split("?", 1)[0]
    why = denied_path(path)
    if why:
        return why
    if "?" in path:
        return "query parameters belong in params, not in the path"
    field = denied_field(body) or denied_field(params)
    if field:
        return f"denied field ({field})"
    verb = method.upper()
    for pattern, methods in CLIENT_ALLOWLIST:
        if pattern.match(clean):
            if verb in methods:
                return None
            return f"method {verb} is not allowed on this path"
    return "path outside the Video and Feeds allowlist"


def is_configuration_write(method: str, path: str) -> bool:
    """A ``PUT`` of one call type's or one feed visibility's grants: the only writes the
    scoped ``configure`` may make."""
    clean = path.split("?", 1)[0].rstrip("/")
    if method.upper() != "PUT":
        return False
    return bool(
        re.match(rf"^{CALL_TYPES}/{_SEG}$", clean)
        or re.match(rf"^{FEED_VISIBILITIES}/{_SEG}$", clean)
    )


# -- reading the configuration ---------------------------------------------------------


def _answer(result: ApiResult) -> dict[str, Any]:
    return {"status": result.status, "code": result.code, "message": result.message}


def availability(result: ApiResult) -> str:
    """What a product's configuration read shows: ``available``, ``not available: …`` or
    ``not verified: …`` (Stream documents no "product not enabled" answer)."""
    if result.ok:
        return "available"
    why = f"HTTP {result.status} code {result.code}" + (
        f": {result.message}" if result.message else ""
    )
    if result.status == 404:
        return f"not available: {why} ({_NOT_ON_DEPLOYMENT})"
    if unavailable_answer(result.status, result.code, result.message):
        return f"not available: {why}"
    return f"not verified: {why}"


def unavailable_answer(status: int | None, code: int | None, message: str | None) -> str | None:
    """The product-finding rule (DM-05 finding 2 (c)): a 4xx other than 402 and 404, whose
    code is not 99, whose message says the product (not an object or a field of the
    request) is not enabled or not available to the application. Such an answer is that
    product's finding, not a charge signal, and not a refusal under the matrix quality
    rule. A 404 is "does not exist" (an object), except from a configuration read
    (:func:`availability`)."""
    if status is None or not 400 <= status < 500 or status in (402, 404) or code == 99:
        return None
    if product_unavailable_wording(message):
        return f"HTTP {status} code {code}: {message}"
    return None


def _grants(item: Any) -> dict[str, list[str]]:
    grants = item.get("grants") if isinstance(item, Mapping) else None
    if not isinstance(grants, Mapping):
        return {}
    return {str(role): [str(g) for g in (granted or [])] for role, granted in grants.items()}


def read_configuration(api: ServerApi) -> dict[str, Any]:
    """Both products' configuration, read-only: the call types and their grants, the feed
    visibilities and their grants, and the feed groups. A read that is not 2xx is kept
    as its answer, with the product's availability."""
    call_types = api.get(CALL_TYPES)
    visibilities = api.get(FEED_VISIBILITIES)
    groups = api.get(FEED_GROUPS)
    types = call_types.body.get("call_types") if isinstance(call_types.body, Mapping) else None
    vis = (
        visibilities.body.get("feed_visibilities")
        if isinstance(visibilities.body, Mapping)
        else None
    )
    grp = groups.body.get("groups") if isinstance(groups.body, Mapping) else None
    return {
        "video": {
            "availability": availability(call_types),
            "read": _answer(call_types),
            "call_types": {
                str(name): {
                    "grants": _grants(cfg),
                    "settings": cfg.get("settings") if isinstance(cfg, Mapping) else None,
                    "notification_settings": (
                        cfg.get("notification_settings") if isinstance(cfg, Mapping) else None
                    ),
                }
                for name, cfg in sorted((types or {}).items())
            }
            if isinstance(types, Mapping)
            else {},
        },
        "feeds": {
            "availability": availability(visibilities),
            "read": _answer(visibilities),
            "feed_visibilities": {
                str(name): {"grants": _grants(cfg)} for name, cfg in sorted((vis or {}).items())
            }
            if isinstance(vis, Mapping)
            else {},
            "feed_groups_read": {**_answer(groups), "availability": availability(groups)},
            "feed_groups": {
                str(gid): {
                    "default_visibility": (
                        cfg.get("default_visibility") if isinstance(cfg, Mapping) else None
                    ),
                    "default_follower_role": (
                        cfg.get("default_follower_role") if isinstance(cfg, Mapping) else None
                    ),
                }
                for gid, cfg in sorted((grp or {}).items())
            }
            if isinstance(grp, Mapping)
            else {},
        },
    }


def probe(api: ServerApi) -> dict[str, Any]:
    """The availability probe (the I2b prompt, section 5): one read per product, and what
    it answered. The guard never refuses a read."""
    state = read_configuration(api)
    return {
        "video": {
            "request": f"GET {CALL_TYPES}",
            "availability": state["video"]["availability"],
            "answer": state["video"]["read"],
            "call_types": sorted(state["video"]["call_types"]),
        },
        "feeds": {
            "request": f"GET {FEED_VISIBILITIES}; GET {FEED_GROUPS}",
            "availability": state["feeds"]["availability"],
            "answer": state["feeds"]["read"],
            "feed_visibilities": sorted(state["feeds"]["feed_visibilities"]),
            "feed_groups_read": state["feeds"]["feed_groups_read"],
            "feed_groups": sorted(state["feeds"]["feed_groups"]),
        },
    }


def _scopes(state: Mapping[str, Any]) -> list[tuple[str, str, str, dict[str, list[str]]]]:
    """(product, kind, name, grants) for every call type and feed visibility read."""
    out: list[tuple[str, str, str, dict[str, list[str]]]] = []
    video = state.get("video") or {}
    for name, cfg in sorted((video.get("call_types") or {}).items()):
        out.append(("video", "call type", str(name), dict(cfg.get("grants") or {})))
    feeds = state.get("feeds") or {}
    for name, cfg in sorted((feeds.get("feed_visibilities") or {}).items()):
        out.append(("feeds", "feed visibility", str(name), dict(cfg.get("grants") or {})))
    return out


def _available(state: Mapping[str, Any], product: str) -> bool:
    return (state.get(product) or {}).get("availability") == "available"


def lockdown_plan(state: Mapping[str, Any]) -> list[ApiRequest]:
    """The difference from ``state`` to the target: one ``PUT`` per call type or feed
    visibility where a client role still holds a grant, naming only those roles with
    ``[]``. Nothing for a product that is not available, and nothing for a scope that
    already reads as the target."""
    plan: list[ApiRequest] = []
    for product, kind, name, grants in _scopes(state):
        if not _available(state, product):
            continue
        roles = [role for role in CLIENT_ROLES if grants.get(role)]
        if not roles:
            continue
        base = CALL_TYPES if product == "video" else FEED_VISIBILITIES
        plan.append(
            ApiRequest(
                "PUT",
                f"{base}/{name}",
                {"grants": {role: [] for role in roles}},
                f"{product}: remove the {kind} {name} grants of " + ", ".join(roles),
            )
        )
    return plan


def verify(state: Mapping[str, Any], recorded: Mapping[str, Any] | None = None) -> list[str]:
    """Differences between ``state`` and the lockdown target, for the available products.
    A product that is not available has nothing to lock and is no difference; one whose
    read is not verified (a 5xx, an outage) is a difference, because its state is not
    known. The client roles must hold no grant; since P06.1-C4 everything else the
    committed baseline records must be as it records it (:func:`baseline_differences`;
    ``recorded`` defaults to :data:`PRODUCTS_BASELINE`)."""
    problems: list[str] = []
    for product in PRODUCTS:
        entry = state.get(product) or {}
        note = str(entry.get("availability") or "not read")
        if note.startswith("not verified") or note == "not read":
            problems.append(f"{product} configuration {note}")
    for product, kind, name, grants in _scopes(state):
        if not _available(state, product):
            continue
        for role in CLIENT_ROLES:
            if grants.get(role):
                problems.append(
                    f"{product} {kind} {name}: grants for {role} not empty: {grants[role]}"
                )
    problems += baseline_differences(state, recorded_products() if recorded is None else recorded)
    return problems


def recorded_products() -> dict[str, Any]:
    """The committed Video and Feeds baseline (:data:`PRODUCTS_BASELINE`)."""
    return dict(json.loads(PRODUCTS_BASELINE.read_text(encoding="utf-8")))


def _changed_paths(have: Any, want: Any, path: str = "") -> list[str]:
    """The dotted paths at which two JSON values differ: a mapping key by key, a list by its
    length and then item by item (C4's own review), a scalar by value and type."""
    if isinstance(have, Mapping) and isinstance(want, Mapping):
        out: list[str] = []
        for key in sorted(set(have) | set(want), key=str):
            sub = f"{path}.{key}" if path else str(key)
            if key not in have or key not in want:
                out.append(sub + (" (not in the baseline)" if key not in want else " (missing)"))
            else:
                out += _changed_paths(have[key], want[key], sub)
        return out
    if isinstance(have, list) and isinstance(want, list):
        if len(have) != len(want):
            return [f"{path or '(the whole value)'} (length {len(have)}, want {len(want)})"]
        items: list[str] = []
        for index, (h, w) in enumerate(zip(have, want, strict=True)):
            items += _changed_paths(h, w, f"{path}[{index}]")
        return items
    if have == want and type(have) is type(want):
        return []
    return [path or "(the whole value)"]


def _shown(paths: list[str], limit: int = 8) -> str:
    return ", ".join(paths[:limit]) + (
        f" and {len(paths) - limit} more" if len(paths) > limit else ""
    )


def baseline_differences(state: Mapping[str, Any], recorded: Mapping[str, Any]) -> list[str]:
    """What the lockdown must have left as the committed baseline records it, for each
    available product (P06.1-C4; the I2b review's finding 2): every role's grants other
    than the client roles' (compared as sets), each call type's ``settings`` and
    ``notification_settings`` (compared field by field, value and type), and each feed
    group's ``default_visibility`` and ``default_follower_role``. A call type, a feed
    visibility, a feed group or a role present on one side only is a difference. Every
    field :func:`baseline_record` keeps is compared except ``availability`` (checked by
    :func:`verify`'s own rule) and the three read answers (``read``,
    ``feed_groups_read``), which describe the read, not the configuration; no kept field
    is a timestamp or another volatile value."""
    problems: list[str] = []
    for product, key, kind in (
        ("video", "call_types", "call type"),
        ("feeds", "feed_visibilities", "feed visibility"),
    ):
        if not _available(state, product):
            continue
        have_scopes = (state.get(product) or {}).get(key) or {}
        want_scopes = (recorded.get(product) or {}).get(key) or {}
        for name in sorted(set(have_scopes) | set(want_scopes)):
            label = f"{product} {kind} {name}"
            if name not in want_scopes:
                problems.append(f"{label}: not in the committed baseline")
                continue
            if name not in have_scopes:
                problems.append(f"{label}: missing (the committed baseline has it)")
                continue
            have, want = have_scopes[name], want_scopes[name]
            have_grants = dict(have.get("grants") or {})
            want_grants = dict(want.get("grants") or {})
            for role in sorted((set(have_grants) | set(want_grants)) - set(CLIENT_ROLES)):
                if role not in want_grants:
                    problems.append(
                        f"{label}: grants for {role} not in the committed baseline: "
                        f"{sorted(have_grants[role])}"
                    )
                elif role not in have_grants:
                    problems.append(
                        f"{label}: grants for {role} missing; the committed baseline has "
                        f"{sorted(want_grants[role])}"
                    )
                elif sorted(have_grants[role]) != sorted(want_grants[role]):
                    added = sorted(set(have_grants[role]) - set(want_grants[role]))
                    removed = sorted(set(want_grants[role]) - set(have_grants[role]))
                    problems.append(
                        f"{label}: grants for {role} differ from the committed baseline "
                        f"(added {added}, removed {removed})"
                    )
            if product == "video":
                for field in ("settings", "notification_settings"):
                    changed = _changed_paths(have.get(field), want.get(field))
                    if changed:
                        problems.append(
                            f"{label}: {field} differ from the committed baseline at "
                            + _shown(changed)
                        )
    if _available(state, "feeds"):
        have_groups = (state.get("feeds") or {}).get("feed_groups") or {}
        want_groups = (recorded.get("feeds") or {}).get("feed_groups") or {}
        for gid in sorted(set(have_groups) | set(want_groups)):
            label = f"feeds feed group {gid}"
            if gid not in want_groups:
                problems.append(f"{label}: not in the committed baseline")
            elif gid not in have_groups:
                problems.append(f"{label}: missing (the committed baseline has it)")
            else:
                for field in ("default_visibility", "default_follower_role"):
                    have_value = (have_groups[gid] or {}).get(field)
                    want_value = (want_groups[gid] or {}).get(field)
                    if have_value != want_value:
                        problems.append(
                            f"{label}: {field} is {have_value!r}; the committed baseline "
                            f"has {want_value!r}"
                        )
    return problems


def baseline_record(state: Mapping[str, Any], app_id: str) -> dict[str, Any]:
    """The products' configuration before the lockdown: settings and grants only, no user
    and no data (committed as ``baseline/video-feeds-<app>-<date>.json``)."""
    video = state.get("video") or {}
    feeds = state.get("feeds") or {}
    return {
        "app_id": app_id,
        "video": {
            "availability": video.get("availability"),
            "read": video.get("read"),
            "call_types": {
                name: {
                    "grants": dict(cfg.get("grants") or {}),
                    "settings": cfg.get("settings"),
                    "notification_settings": cfg.get("notification_settings"),
                }
                for name, cfg in sorted((video.get("call_types") or {}).items())
            },
        },
        "feeds": {
            "availability": feeds.get("availability"),
            "read": feeds.get("read"),
            "feed_visibilities": {
                name: {"grants": dict(cfg.get("grants") or {})}
                for name, cfg in sorted((feeds.get("feed_visibilities") or {}).items())
            },
            "feed_groups_read": feeds.get("feed_groups_read"),
            "feed_groups": dict(feeds.get("feed_groups") or {}),
        },
    }


# -- the products' objects -------------------------------------------------------------


def list_objects(api: ServerApi, state: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Every call, feed and activity in the application (the proof's are the only ones).
    A listing Stream does not answer with 2xx is "not available: …" when the product's
    configuration read (``state``, from :func:`read_configuration`) shows the product is
    not available, so that no object of it can exist; otherwise it is "not verified: …",
    whatever its own message says (the independent check of I2b, finding 3)."""
    out: dict[str, Any] = {}
    calls = api.raw("POST", "/api/v2/video/calls", body={"filter_conditions": {}, "limit": 100})
    feeds = api.raw("POST", "/api/v2/feeds/feeds/query", body={"limit": 100})
    activities = api.raw("POST", "/api/v2/feeds/activities/query", body={"limit": 100})

    def call_id(item: Any) -> str:
        call = item.get("call") if isinstance(item, Mapping) else None
        return str(call.get("cid")) if isinstance(call, Mapping) else str(item)

    def feed_id(item: Any) -> str:
        return str(item.get("feed")) if isinstance(item, Mapping) else str(item)

    def activity_id(item: Any) -> str:
        return str(item.get("id")) if isinstance(item, Mapping) else str(item)

    for key, result, items_key, ident in (
        ("calls", calls, "calls", call_id),
        ("feeds", feeds, "feeds", feed_id),
        ("activities", activities, "activities", activity_id),
    ):
        items = result.body.get(items_key) if isinstance(result.body, Mapping) else None
        if result.ok and isinstance(items, list):
            out[f"remaining_{key}"] = [ident(i) for i in items]
        else:
            out[f"remaining_{key}"] = None
            product = "video" if key == "calls" else "feeds"
            product_state = str(((state or {}).get(product) or {}).get("availability") or "")
            why = f"HTTP {result.status} code {result.code}" + (
                f": {result.message}" if result.message else ""
            )
            if product_state.startswith("not available"):
                out[f"{key}_listing"] = f"{product_state} (the listing got {why})"
            else:
                out[f"{key}_listing"] = f"not verified: {why}"
    return out


OBJECT_KINDS = ("calls", "feeds", "activities")
OBJECT_NAMES = {"calls": "call", "feeds": "feed", "activities": "activity"}


def is_lockdown_body(body: Any) -> bool:
    """Whether a configuration write's body is the lockdown's and nothing else: ``grants``
    alone, naming only client roles, each ``[]`` (the independent check of I2b, nit 4)."""
    if not isinstance(body, Mapping) or set(body) != {"grants"}:
        return False
    grants = body["grants"]
    if not isinstance(grants, Mapping) or not grants:
        return False
    return all(role in CLIENT_ROLES and granted == [] for role, granted in grants.items())
