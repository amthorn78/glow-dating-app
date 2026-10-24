"""A read-only full view of the application's configuration, and the comparison of two
views (P06.2 Stage B2-C1; DM-17 2.1 and 2.3).

``baseline`` writes only the application settings the chat target names
(``configuration.APP_SETTING_KEYS``) and withholds the rest by design: push, upload and
webhook configuration can hold credentials. The correction pass needs a fuller read, for two
things. First, every settings key the application holds, so that a key the 25 September
record and the target do not name is listed with its value before anything is applied
(2.1: Stream can add an application setting as it added a permission, and
``configuration.verify`` compares only what the record names). Second, a comparison of every
field before and after each apply, so that an apply is shown to change only what it was
planned to change: D1 and D4 for the chat apply, D2 for the products apply (2.3:
``verify`` checks what the targets name; this check sees what they do not).

**What it reads** (:func:`read_view`), through the harness's
:class:`~glow_stream_proof.server_api.ServerApi` with a guard installed that refuses anything
but a GET (:func:`read_only_refusal`): the application (``GET /api/v2/app``: every settings
key, the ``.app`` grants and everything else the response carries), every chat channel type,
the roles, every Video call type, every Feeds visibility and every feed group. Nothing of
users, channels, messages or any other data is read. The view is written to ``.work/``
through :mod:`glow_stream_proof.workdir`'s leak-checked writer.

**Credential-like values are never written** (the standing credential rule, applied to
2.1). A value under a key whose name contains one of :data:`CREDENTIAL_KEY_PARTS` (``key``,
``secret``, ``token``, ``password``, ``credential``, ``cert`` (so ``certificate`` and Stream's
``p12_cert``), ``private`` or ``url``, or ``push``, ``sqs``, ``sns`` or ``webhook``, which cover
the push, SQS, SNS and webhook configuration subtrees) is written as its JSON type, whether it
is empty, and the SHA-256 of its canonical JSON, never the value (:func:`withheld`). A change
is still seen; the value is not. The rule is applied by key name alone, so it also digests a
few values that are no credential (``revoke_tokens_issued_before`` contains ``token``, a
channel type's ``url_enrichment`` contains ``url``); those still read in clear in
``baseline``'s snapshot.
The harness's redactor has already replaced the values under the keys it knows
(``redaction.is_sensitive_key``) before a body reaches this module; for those the digest is
that of the redaction marker, which the entry says, so a change of one non-empty value to
another is not seen there (a recorded limit), only a change between empty and non-empty.

**The comparison** (:func:`compare`) of two views compares every field of every read, value
and type, leaving aside only the fields named in :data:`VOLATILE_FIELDS` (``created_at``,
``updated_at`` and each response's ``duration``). Its output lists each changed path with its
before and after (or digest). A list of scalars (a role's grants) is compared as one value,
so an added grant shows the whole list before and after; a list of objects item by item, by
position, except the lists named in :data:`KEYED_LISTS` (the application's geofences, which
Stream returns in no fixed order; P06.2 Stage B2-C2), whose items are paired by their key.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from . import guard, products
from .redaction import REDACTED_API_KEY, REDACTED_JWT, REDACTED_SECRET
from .server_api import ServerApi

# A value under a key whose lower-cased name contains one of these is never written: its
# JSON type, whether it is empty and the SHA-256 of its canonical JSON stand in for it. The
# first eight name credentials (``cert`` covers ``certificate`` and Stream's ``p12_cert``); the
# last four are the configuration subtrees Stream keeps credentials in (push providers, SQS,
# SNS and webhooks).
CREDENTIAL_KEY_PARTS: tuple[str, ...] = (
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
)
# The fields the comparison leaves aside, by name, at any depth: Stream's timestamps on
# channel types, call types, feed groups and roles, and the ``duration`` every response
# carries.
VOLATILE_FIELDS: frozenset[str] = frozenset({"created_at", "updated_at", "duration"})
# The lists of objects the comparison keys by a field instead of by position, each named by
# its exact path in the views' reads (P06.2 Stage B2-C2; DM-18 3.3): Stream returns the
# application's geofences in no fixed order (two read-only views 79 s apart, with no apply
# between them, held the same nine geofences in two orders). Every other list of objects is
# compared by position, and a keyed list whose items do not each carry a unique key is too.
KEYED_LISTS: dict[str, str] = {"app.body.app.geofences": "name"}
# What the view reads, in order: (name, path). All GETs; ``baseline`` makes the same reads
# (and reads users and channels too, which the view never does).
READS: tuple[tuple[str, str], ...] = (
    ("app", "/api/v2/app"),
    ("channel_types", "/api/v2/chat/channeltypes"),
    ("roles", "/api/v2/roles"),
    ("call_types", products.CALL_TYPES),
    ("feed_visibilities", products.FEED_VISIBILITIES),
    ("feed_groups", products.FEED_GROUPS),
)
ABSENT = "(absent)"
# The keys of a :func:`digest` entry: such an entry is one value to the comparison.
_DIGEST_KEYS = frozenset({"type", "empty", "sha256"})
_REDACTION_MARKERS = frozenset({REDACTED_SECRET, REDACTED_JWT, REDACTED_API_KEY})


def is_credential_key(key: str) -> bool:
    """Whether a value under ``key`` is withheld: the name contains one of
    :data:`CREDENTIAL_KEY_PARTS`, in any letter case."""
    lowered = key.lower()
    return any(part in lowered for part in CREDENTIAL_KEY_PARTS)


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int | float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, list | tuple):
        return "array"
    return type(value).__name__


def _empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {} or value == ()


def digest(value: Any) -> dict[str, Any]:
    """What is written in place of a credential-like value: its JSON type, whether it is
    empty, and the SHA-256 of its canonical JSON (sorted keys, no spaces). A value the
    harness's redactor already replaced is said so."""
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    out: dict[str, Any] = {
        "type": _json_type(value),
        "empty": _empty(value),
        "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
    if isinstance(value, str) and value in _REDACTION_MARKERS:
        out["redacted_by_the_harness"] = True
    return out


def withheld(value: Any) -> Any:
    """A copy of ``value`` with every credential-like value replaced by its :func:`digest`:
    every mapping's keys are kept, lists are traversed, and a key that matches withholds
    its whole value, subtree and all."""
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for key, item in value.items():
            name = str(key)
            out[name] = digest(item) if is_credential_key(name) else withheld(item)
        return out
    if isinstance(value, list | tuple):
        return [withheld(item) for item in value]
    return value


def read_only_refusal(method: str, path: str, body: Any, params: Mapping[str, str]) -> str | None:
    """The guard the full view runs under: a GET or HEAD may be sent, nothing else. The
    refusal names the request's shape, never an identifier."""
    if method.upper() in ("GET", "HEAD"):
        return None
    return (
        f"full-view sends GETs only; refused {method.upper()} {guard.shape(guard.parts_of(path))}"
    )


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def read_view(api: ServerApi) -> dict[str, Any]:
    """The six reads, each kept with its status and its body with credential-like values
    withheld. A read that is not 2xx is kept as its answer (status, code, message), so a
    product that is not available is seen as such, and never raises here; a charge or limit
    signal stops as for every server request."""
    reads: dict[str, Any] = {}
    for name, path in READS:
        result = api.get(path)
        reads[name] = {
            "path": path,
            "status": result.status,
            "code": result.code,
            "message": result.message,
            "body": withheld(result.body),
        }
    return {
        "at": _stamp(),
        "reads": reads,
        "withheld_key_parts": list(CREDENTIAL_KEY_PARTS),
        "volatile_fields_left_aside_by_compare": sorted(VOLATILE_FIELDS),
    }


def _names(body: Any, key: str) -> list[str]:
    items = body.get(key) if isinstance(body, Mapping) else None
    if isinstance(items, Mapping):
        return sorted(str(k) for k in items)
    if isinstance(items, list):
        return sorted(str(i.get("name", i.get("id"))) for i in items if isinstance(i, Mapping))
    return []


def summary(view: Mapping[str, Any]) -> list[str]:
    """What the command prints: each read's status and the names or counts it holds, no
    value."""
    reads = view["reads"]
    app = reads["app"]["body"].get("app") if isinstance(reads["app"]["body"], Mapping) else None
    app_keys = sorted(app) if isinstance(app, Mapping) else []
    withheld_keys = [k for k in app_keys if is_credential_key(k)]
    lines = [
        f"app: HTTP {reads['app']['status']}; {len(app_keys)} keys, {len(withheld_keys)} of "
        f"them withheld (type, emptiness and digest only): {withheld_keys}",
        f"channel types: HTTP {reads['channel_types']['status']}; "
        f"{_names(reads['channel_types']['body'], 'channel_types')}",
        f"roles: HTTP {reads['roles']['status']}; {len(_names(reads['roles']['body'], 'roles'))}",
        f"video call types: HTTP {reads['call_types']['status']}; "
        f"{_names(reads['call_types']['body'], 'call_types')}",
        f"feed visibilities: HTTP {reads['feed_visibilities']['status']}; "
        f"{_names(reads['feed_visibilities']['body'], 'feed_visibilities')}",
        f"feed groups: HTTP {reads['feed_groups']['status']}; "
        f"{_names(reads['feed_groups']['body'], 'groups')}",
    ]
    return lines


# -- the comparison ---------------------------------------------------------------------


def _scalars(value: list[Any]) -> bool:
    return all(not isinstance(item, Mapping | list | tuple) for item in value)


def _is_digest(value: Any) -> bool:
    """Whether ``value`` is what :func:`digest` wrote in place of a withheld value."""
    return isinstance(value, Mapping) and _DIGEST_KEYS <= set(value) <= (
        _DIGEST_KEYS | {"redacted_by_the_harness"}
    )


def _keyed(items: Any, key: str) -> dict[str, Any] | None:
    """A list of objects as a mapping from each item's ``key`` to the item, or ``None`` when
    an item is not an object, lacks the key or repeats another's (then the list is compared by
    position, which never hides a change)."""
    out: dict[str, Any] = {}
    for item in items:
        if not isinstance(item, Mapping) or key not in item:
            return None
        name = str(item[key])
        if name in out:
            return None
        out[name] = item
    return out


def changed_fields(before: Any, after: Any, path: str = "") -> list[dict[str, Any]]:
    """Every field at which two JSON values differ, value or type, with the before and after
    at that path; the fields named in :data:`VOLATILE_FIELDS` are left aside at any depth. A
    key present on one side only is reported with :data:`ABSENT` on the other. A list of
    scalars is one value; a list of objects is compared item by item, by position, except a
    list named in :data:`KEYED_LISTS`, whose items are paired by their key (an item on one
    side only reported with :data:`ABSENT` on the other); a length that differs is reported
    with both lengths. A withheld value's digest entry is one value, so a changed
    credential-like value is one line, before and after digests."""
    if _is_digest(before) or _is_digest(after):
        if before == after:
            return []
        return [{"path": path or "(the whole value)", "before": before, "after": after}]
    if isinstance(before, Mapping) and isinstance(after, Mapping):
        out: list[dict[str, Any]] = []
        for key in sorted(set(before) | set(after), key=str):
            if str(key) in VOLATILE_FIELDS:
                continue
            sub = f"{path}.{key}" if path else str(key)
            if key not in before:
                out.append({"path": sub, "before": ABSENT, "after": after[key]})
            elif key not in after:
                out.append({"path": sub, "before": before[key], "after": ABSENT})
            else:
                out += changed_fields(before[key], after[key], sub)
        return out
    if isinstance(before, list | tuple) and isinstance(after, list | tuple):
        if _scalars(list(before)) and _scalars(list(after)):
            if list(before) == list(after) and [type(b) for b in before] == [
                type(a) for a in after
            ]:
                return []
            return [{"path": path or "(the whole value)", "before": before, "after": after}]
        items: list[dict[str, Any]] = []
        if len(before) != len(after):
            items.append(
                {
                    "path": f"{path or '(the whole value)'} (length)",
                    "before": len(before),
                    "after": len(after),
                }
            )
        key = KEYED_LISTS.get(path)
        keyed_before = _keyed(before, key) if key is not None else None
        keyed_after = _keyed(after, key) if key is not None else None
        if keyed_before is not None and keyed_after is not None:
            for name in sorted(set(keyed_before) | set(keyed_after)):
                sub = f"{path}[{key}={name}]"
                if name not in keyed_before:
                    items.append({"path": sub, "before": ABSENT, "after": keyed_after[name]})
                elif name not in keyed_after:
                    items.append({"path": sub, "before": keyed_before[name], "after": ABSENT})
                else:
                    items += changed_fields(keyed_before[name], keyed_after[name], sub)
            return items
        for index, (b, a) in enumerate(zip(before, after, strict=False)):
            items += changed_fields(b, a, f"{path}[{index}]")
        return items
    if before == after and type(before) is type(after):
        return []
    return [{"path": path or "(the whole value)", "before": before, "after": after}]


def compare(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The changed fields between two views' reads (:func:`changed_fields` on ``reads``)."""
    return changed_fields(before.get("reads"), after.get("reads"))


def render(changes: list[dict[str, Any]]) -> list[str]:
    """One line per changed field: its path, then before and after as JSON."""
    return [
        f"- {change['path']}: {json.dumps(change['before'], sort_keys=True, default=str)} -> "
        f"{json.dumps(change['after'], sort_keys=True, default=str)}"
        for change in changes
    ]


__all__ = [
    "ABSENT",
    "CREDENTIAL_KEY_PARTS",
    "KEYED_LISTS",
    "READS",
    "VOLATILE_FIELDS",
    "changed_fields",
    "compare",
    "digest",
    "is_credential_key",
    "read_only_refusal",
    "read_view",
    "render",
    "summary",
    "withheld",
]
