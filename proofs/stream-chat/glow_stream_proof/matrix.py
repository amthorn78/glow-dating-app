"""The bypass matrix: case definitions, refusal classification and verdicts.

A case is a client action that must not succeed. Most cases are one SDK call
made by a client session (``A``, ``B`` or ``X``). Each case has a positive
control: the same request replayed with server authentication, or the same SDK
call by the member who is authorized, must succeed, which shows that the
request is well formed. Cases whose procedure is not a single SDK call
(tokens, guest and anonymous access, profile changes on connect, realtime)
carry ``procedure`` and are run by the executor.

Placeholders such as ``{A}`` or ``{AB}`` are filled from the run context.

Matrix quality rule (P06.1 brief): a refusal counts only when Stream returns an
authentication error (HTTP 401) or a permission error (HTTP 403) with Stream's
code. A 400 or 404, or a refusal that cannot be attributed, does not count.

The status and code are always taken from Stream's recorded answer to the
request under test, never from an error the SDK raised. A request that has no
recorded answer (the SDK failed locally, or returned without sending anything)
is the outcome ``no-response``, which is never a HOLDS.
"""

from __future__ import annotations

import base64
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from . import products
from .configuration import DEFAULT_TYPES, MATCH_TYPE

Expect = Literal[
    "refused",
    "no-leak",
    "not-effective",
    "identity-kept",
    "carries-no-free-text",
    # P06.1-I2a
    "ends-access",
    "no-oracle",
    "mapping",
    "refuses-without-state",
]
Outcome = Literal[
    "success", "auth", "permission", "feature", "not-found", "input", "other", "no-response"
]

# Token refusals. Code 2 is Stream's API-key error, not a token refusal, so it
# is not attributable to the token under test.
AUTH_CODES = frozenset({5, 40, 41, 42, 43})
PERMISSION_CODES = frozenset({17, 70})
FEATURE_CODES = frozenset({18, 19})

# Events the client SDK dispatches itself rather than receiving from Stream: the
# "local events" in stream-chat 9.53.0's EVENT_MAP, plus health checks. A
# client's own query raises ``channels.queried`` with the full queried state, so
# these are never evidence of what Stream delivered to that client.
LOCAL_EVENT_TYPES = frozenset(
    {
        "health.check",
        "message.read_locally",
        "channels.queried",
        "offline_reactions.queried",
        "connection.changed",
        "connection.recovered",
        "transport.changed",
        "capabilities.changed",
        "live_location_sharing.started",
        "live_location_sharing.stopped",
    }
)

PROOF_FILE_B64 = base64.b64encode(b"P06.1 synthetic proof file\n").decode("ascii")
# A 1x1 transparent PNG.
PROOF_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kg"
    "AAAABJRU5ErkJggg=="
)


@dataclass(frozen=True)
class SdkStep:
    session: str
    # ``product``: the runner's Video and Feeds op (P06.1-I2b).
    op: Literal["call", "product"]
    params: Mapping[str, Any]
    max_calls: int = 3


@dataclass(frozen=True)
class ServerRequest:
    method: str
    path: str
    body: Mapping[str, Any] | None = None
    params: Mapping[str, str] | None = None
    # Values of the answer kept in the run's context: {context name: dotted path}
    # (P06.1-I2b: a fixture's activity ID).
    capture: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Control:
    kind: Literal["server-replay", "session", "server-upload", "custom", "none"]
    session: str | None = None
    body_patch: Mapping[str, Any] = field(default_factory=dict)
    keep_params: tuple[str, ...] = ()
    add_params: Mapping[str, str] = field(default_factory=dict)
    creates_channel: bool = False
    capture: Mapping[str, str] = field(default_factory=dict)
    undo: tuple[ServerRequest, ...] = ()
    expect_terms: tuple[str, ...] = ()
    note: str = ""
    # The undo reverses the client's change and the control's replay's alike (an
    # idempotent create, a member added, data set), so a client success is not undone a
    # second time after the replay made the undo: a second delete of the same object
    # would get 404 (P06.1-I2b; the Video and Feeds cases).
    undo_once: bool = False


@dataclass(frozen=True)
class Case:
    id: str
    group: str
    actor: str
    token: str
    action: str
    expect: Expect
    control: Control
    step: SdkStep | None = None
    procedure: str | None = None
    leak_terms: tuple[str, ...] = ()
    phase: int = 50
    # Channel-level feature overrides applied to AB for the permission-layer phase.
    feature_override: Mapping[str, Any] = field(default_factory=dict)
    # Type-level features enabled briefly for features Stream cannot override per
    # channel (custom events, polls); restored and verified right after.
    type_override: Mapping[str, Any] = field(default_factory=dict)
    # The most API calls the case can use; the run starts it only with that many left
    # beyond the calls kept for the end of the run (P06.1-I2a: the I2a cases use more
    # than the 30 an I1 case can).
    calls: int = 30
    # Server requests that put the case's objects in place before its step (P06.1-I2b:
    # a call or a feed the run owns, an activity of A's). Each is sent once per run,
    # through the guard, and what it creates is recorded for cleanup.
    fixture: tuple[ServerRequest, ...] = ()


# -- placeholders ---------------------------------------------------------------

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


class MissingPlaceholder(KeyError):
    pass


def substitute(value: Any, ctx: Mapping[str, str]) -> Any:
    """Fill ``{name}`` placeholders in strings, dict keys and nested values."""
    if isinstance(value, str):

        def repl(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in ctx:
                raise MissingPlaceholder(name)
            return ctx[name]

        return _PLACEHOLDER.sub(repl, value)
    if isinstance(value, Mapping):
        return {substitute(k, ctx): substitute(v, ctx) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [substitute(v, ctx) for v in value]
    return value


def deep_merge(base: Any, patch: Mapping[str, Any]) -> Any:
    if not isinstance(base, dict):
        base = {}
    out = dict(base)
    for key, value in patch.items():
        if isinstance(value, Mapping) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


# -- classification and verdicts --------------------------------------------------


def classify(status: int | None, code: int | None) -> Outcome:
    if status is None:
        return "no-response"
    if 200 <= status < 300:
        return "success"
    if status == 401 and code in AUTH_CODES:
        return "auth"
    if status == 403 and code in PERMISSION_CODES:
        return "permission"
    if status == 400 and code in FEATURE_CODES:
        return "feature"
    if status == 404:
        return "not-found"
    if status == 400:
        return "input"
    return "other"


def find_terms(obj: Any, terms: tuple[str, ...] | list[str]) -> list[str]:
    text = json.dumps(obj, sort_keys=True, default=str)
    return [t for t in terms if t and t in text]


def serialized_request(record: Mapping[str, Any]) -> str:
    """The request as the client sent it: its path, query and body (P06.1-I2b)."""
    return json.dumps(
        {"path": record.get("path"), "params": record.get("params"), "body": record.get("body")},
        sort_keys=True,
        default=str,
    )


def carried_terms(records: list[dict[str, Any]], terms: list[str]) -> list[str]:
    """The terms that appear, as substrings, anywhere in the serialized requests a
    command sent: the sender already had them, so their presence in an answer discloses
    nothing (P06.1-I2b; the disclosure rule the manager decided on I2a, with its review's
    detail: F9-sync carries XD's ID inside the cid string)."""
    sent = "\n".join(serialized_request(r) for r in records)
    return [t for t in terms if t and t in sent]


def term_paths(obj: Any, terms: list[str], path: str = "") -> dict[str, list[str]]:
    """Where each term appears in ``obj``: the key names down to the string that holds it,
    with ``[]`` for a list item (P06.1-I2b: the row keeps where a term was found)."""
    found: dict[str, list[str]] = {}
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            for term, paths in term_paths(
                value, terms, f"{path}.{key}" if path else str(key)
            ).items():
                found.setdefault(term, []).extend(paths)
    elif isinstance(obj, list):
        for item in obj:
            for term, paths in term_paths(item, terms, f"{path}[]").items():
                found.setdefault(term, []).extend(paths)
    elif isinstance(obj, str):
        for term in terms:
            if term and term in obj:
                found.setdefault(term, []).append(path or "(the string itself)")
    return {t: sorted(set(p)) for t, p in found.items()}


@dataclass(frozen=True)
class Verdict:
    label: str
    reason: str


HOLDS = "HOLDS"
HOLDS_FILTERED = "HOLDS (filtered, not refused)"
HOLDS_IGNORED = "HOLDS (accepted, not applied)"
REFUSED_FEATURE = "REFUSED (feature off; not a permission error)"
FAIL = "FAIL"
INCONCLUSIVE = "INCONCLUSIVE"
# P06.1-I2a: a revocation mechanism judged against the history policy (mechanisms.py).
MEETS = "MEETS the history policy"
FALLS_SHORT = "DOES NOT MEET the history policy"
# P06.1-I2b: a Video or Feeds answer that the product is not enabled or not available
# to the application (the product-finding rule; DM-05 finding 2 (c)): neither a refusal
# under the quality rule nor a charge signal; it ends that product's cases.
NOT_AVAILABLE = "NOT AVAILABLE (the product is not enabled for the application)"
# What an interrupted case keeps: the failure was observed (the independent review of
# P06.1-I2a, point 7). Anything else becomes INCONCLUSIVE.
KEPT_WHEN_INTERRUPTED = frozenset({FAIL, FALLS_SHORT})


NO_RESPONSE_REASON = "no answer from Stream was recorded for the request under test"


def refused_verdict(outcome: Outcome, control_ok: bool | None) -> Verdict:
    if outcome == "no-response":
        return Verdict(INCONCLUSIVE, NO_RESPONSE_REASON)
    if outcome == "success":
        return Verdict(FAIL, "the client action succeeded")
    if outcome in ("auth", "permission"):
        if control_ok:
            return Verdict(HOLDS, f"{outcome} error; control succeeded")
        return Verdict(INCONCLUSIVE, f"{outcome} error, but the positive control did not succeed")
    if outcome == "feature":
        if control_ok:
            return Verdict(REFUSED_FEATURE, "400 feature error; control succeeded")
        return Verdict(REFUSED_FEATURE, "400 feature error; control did not succeed")
    return Verdict(INCONCLUSIVE, f"refusal not attributable ({outcome})")


def no_leak_verdict(
    outcome: Outcome, leaks: list[str], control_ok: bool | None, control_found: bool
) -> Verdict:
    if leaks:
        return Verdict(FAIL, "response disclosed: " + ", ".join(leaks))
    if outcome == "no-response":
        return Verdict(INCONCLUSIVE, NO_RESPONSE_REASON)
    if outcome in ("auth", "permission"):
        if control_ok:
            return Verdict(HOLDS, f"{outcome} error; control succeeded")
        return Verdict(INCONCLUSIVE, f"{outcome} error, but the positive control did not succeed")
    if outcome == "success":
        if control_ok and control_found:
            return Verdict(
                HOLDS_FILTERED, "succeeded with none of the target data; control found it"
            )
        return Verdict(INCONCLUSIVE, "succeeded without the data, but the control did not find it")
    if outcome == "feature":
        return Verdict(REFUSED_FEATURE, "400 feature error")
    return Verdict(INCONCLUSIVE, f"refusal not attributable ({outcome})")


def not_effective_verdict(applied: bool, outcome: Outcome, control_ok: bool | None) -> Verdict:
    if applied:
        return Verdict(FAIL, "the change reached Stream's stored state")
    if outcome == "no-response":
        return Verdict(INCONCLUSIVE, NO_RESPONSE_REASON + "; stored state unchanged")
    if outcome in ("auth", "permission"):
        return Verdict(
            HOLDS if control_ok else INCONCLUSIVE,
            f"{outcome} error; stored state unchanged"
            + ("" if control_ok else "; control did not succeed"),
        )
    if outcome == "success":
        return Verdict(
            HOLDS_IGNORED if control_ok else INCONCLUSIVE,
            "request accepted but the stored state is unchanged"
            + ("" if control_ok else "; control did not succeed"),
        )
    return Verdict(INCONCLUSIVE, f"unexpected outcome ({outcome}); stored state unchanged")


# -- case definitions -------------------------------------------------------------

T = MATCH_TYPE
READ_OPTIONS = {"state": True, "watch": False, "presence": False}


def _call(
    session: str,
    target: str,
    method: str,
    args: list[Any],
    *,
    channel: tuple[str, str] | None = None,
    channel_data: Mapping[str, Any] | None = None,
    max_calls: int = 3,
) -> SdkStep:
    params: dict[str, Any] = {"target": target, "method": method, "args": args}
    if channel is not None:
        params["type"], params["id"] = channel
    if channel_data is not None:
        params["channel_data"] = dict(channel_data)
    return SdkStep(session=session, op="call", params=params, max_calls=max_calls)


def _replay(**kwargs: Any) -> Control:
    return Control(kind="server-replay", **kwargs)


def _product(
    session: str,
    method: str,
    path: str,
    body: Mapping[str, Any] | None = None,
    *,
    params: Mapping[str, str] | None = None,
    max_calls: int = 2,
) -> SdkStep:
    """A Video or Feeds request through the runner's product op (P06.1-I2b)."""
    step_params: dict[str, Any] = {"method": method, "path": path}
    if body is not None:
        step_params["body"] = dict(body)
    if params is not None:
        step_params["params"] = dict(params)
    return SdkStep(session=session, op="product", params=step_params, max_calls=max_calls)


# P06.1-I2b: the case groups of the two products, and the sets the live plan names.
PRODUCT_GROUPS: dict[str, str] = {"video": "video", "feeds": "feeds"}
# Run 1, the chat reruns only (the I2b prompt, section 5), in this order.
RUN_1_CASES = (
    "RV-remove",
    "SD-deactivate",
    "F9-thread",
    "F9-sync",
    "EO-channel",
    "EO-user",
    "EO-message",
    "S3a",
)


def product_of(case: Case) -> str | None:
    """The product a case belongs to (``video`` or ``feeds``), or ``None``."""
    return PRODUCT_GROUPS.get(case.group)


def product_case_ids(product: str | None = None) -> list[str]:
    """The Video and Feeds cases (run V1 and run V2), in the matrix's order."""
    return [
        c.id
        for c in all_cases()
        if product_of(c) is not None and (product is None or product_of(c) == product)
    ]


def _tokens_and_access() -> list[Case]:
    cases: list[Case] = []
    for cid, token, desc in (
        ("T1", "development token for A", "a development token (signature 'devtoken')"),
        ("T2", "A's claims signed with a wrong secret", "a token signed with a wrong secret"),
        ("T3", "A's token, expired", "an expired but correctly signed token"),
    ):
        cases.append(
            Case(
                id=f"{cid}-rest",
                group="tokens",
                actor="A",
                token=token,
                action=f"query own channel AB over REST with {desc}",
                expect="refused",
                control=Control(kind="custom", session="A", note="A's valid token, same query"),
                procedure=f"token-rest:{cid}",
                phase=10,
            )
        )
        cases.append(
            Case(
                id=f"{cid}-ws",
                group="tokens",
                actor="A",
                token=token,
                action=f"open a WebSocket connection as A with {desc}",
                expect="refused",
                control=Control(kind="custom", session="A", note="A's valid token connected"),
                procedure=f"token-ws:{cid}",
                phase=10,
            )
        )
    cases += [
        Case(
            id="T4-ws",
            group="tokens",
            actor="A",
            token="A's valid token",
            action="open a WebSocket connection claiming user B (local SDK check skipped)",
            expect="identity-kept",
            control=Control(kind="custom", session="B", note="B's own token connected as B"),
            procedure="token-ws:T4",
            phase=10,
        ),
        Case(
            id="T4-rest-xd",
            group="tokens",
            actor="A",
            token="A's valid token",
            action="query XD with user_id=X in the request (claims to act as X)",
            expect="refused",
            control=Control(kind="custom", session="X", note="X's own session, same query"),
            procedure="token-rest-claim:XD",
            phase=10,
        ),
        Case(
            id="T4-rest-unread",
            group="tokens",
            actor="A",
            token="A's valid token",
            action="read unread counts with user_id=B in the request (claims to act as B)",
            expect="identity-kept",
            control=Control(kind="custom", note="A's and B's own unread counts differ"),
            procedure="token-rest-claim:unread",
            phase=10,
        ),
        Case(
            id="G1-create",
            group="guest-anonymous",
            actor="none",
            token="API key only",
            action="create a guest user client-side (setGuestUser)",
            expect="refused",
            control=_replay(note="server creates the same guest"),
            procedure="guest-create",
            phase=15,
        ),
    ]
    read_ab_terms = (
        "{m_a_text}",
        "{m_b_text}",
        "{AB}",
        "{A}",
        "{B}",
        "{A_name}",
        "{B_name}",
        "{m_a}",
        "{m_b}",
    )
    for suffix, desc, leak in (
        ("read-ab", "query channel AB", read_ab_terms),
        ("channels", "query channels whose members include A", ("{AB}", "{XD}")),
        ("users", "query users", ("{A}", "{B}", "{X}", "{D}")),
        ("message", "fetch XD's message by ID", ("{xd_text}", "{m_x}", "{X}", "{XD}")),
    ):
        for who, token, proc in (
            ("guest", "guest created by G1's control", "guest-role"),
            ("anonymous", "none (anonymous)", "anonymous"),
        ):
            gid = "G2" if who == "guest" else "G3"
            cases.append(
                Case(
                    id=f"{gid}-{suffix}",
                    group="guest-anonymous",
                    actor=who,
                    token=token,
                    action=desc,
                    expect="no-leak",
                    control=Control(kind="custom", note="authorized member or server"),
                    procedure=f"{proc}:{suffix}",
                    leak_terms=leak,
                    phase=15,
                )
            )
    return cases


def _reading() -> list[Case]:
    xd_terms = ("{XD}", "{xd_text}", "{X}", "{D}")
    return [
        Case(
            id="R1",
            group="reading",
            actor="A",
            token="A's valid token",
            action="watch XD",
            expect="refused",
            step=_call("A", "channel", "watch", [], channel=(T, "{XD}")),
            control=Control(kind="session", session="X"),
            phase=20,
        ),
        Case(
            id="R2",
            group="reading",
            actor="A",
            token="A's valid token",
            action="query XD without watching",
            expect="refused",
            step=_call("A", "channel", "query", [READ_OPTIONS], channel=(T, "{XD}")),
            control=Control(kind="session", session="X"),
            phase=20,
        ),
        Case(
            id="R3",
            group="reading",
            actor="A",
            token="A's valid token",
            action="query channels whose members include X",
            expect="no-leak",
            step=_call(
                "A", "client", "queryChannels", [{"members": {"$in": ["{X}"]}}, [], READ_OPTIONS]
            ),
            control=Control(kind="session", session="X", expect_terms=("{XD}",)),
            leak_terms=xd_terms,
            phase=20,
        ),
        Case(
            id="R4",
            group="reading",
            actor="A",
            token="A's valid token",
            action="query channels whose members include D",
            expect="no-leak",
            step=_call(
                "A", "client", "queryChannels", [{"members": {"$in": ["{D}"]}}, [], READ_OPTIONS]
            ),
            control=Control(kind="session", session="X", expect_terms=("{XD}",)),
            leak_terms=xd_terms,
            phase=20,
        ),
        Case(
            id="R5",
            group="reading",
            actor="A",
            token="A's valid token",
            action="query channels by XD's cid",
            expect="no-leak",
            step=_call("A", "client", "queryChannels", [{"cid": "{XD_cid}"}, [], READ_OPTIONS]),
            control=Control(kind="session", session="X", expect_terms=("{XD}",)),
            leak_terms=xd_terms,
            phase=20,
        ),
        Case(
            id="R6",
            group="reading",
            actor="A",
            token="A's valid token",
            action="fetch XD's message by its ID",
            expect="refused",
            step=_call("A", "client", "getMessage", ["{m_x}"]),
            control=Control(kind="session", session="X"),
            leak_terms=("{xd_text}",),
            phase=20,
        ),
        Case(
            id="R7a",
            group="reading",
            actor="A",
            token="A's valid token",
            action="search messages in XD's cid for XD's text",
            expect="no-leak",
            step=_call(
                "A",
                "client",
                "search",
                [{"cid": {"$in": ["{XD_cid}"]}}, "{xd_text}", {"limit": 10}],
            ),
            control=Control(kind="session", session="X", expect_terms=("{xd_text}",)),
            leak_terms=("{xd_text}", "{m_x}"),
            phase=20,
        ),
        Case(
            id="R7b",
            group="reading",
            actor="A",
            token="A's valid token",
            action="search every glow-match channel for XD's text",
            expect="no-leak",
            step=_call("A", "client", "search", [{"type": T}, "{xd_text}", {"limit": 10}]),
            control=Control(kind="session", session="X", expect_terms=("{xd_text}",)),
            leak_terms=("{xd_text}", "{m_x}"),
            phase=20,
        ),
        Case(
            id="R8a",
            group="reading",
            actor="A",
            token="A's valid token",
            action="query users X and D",
            expect="no-leak",
            step=_call("A", "client", "queryUsers", [{"id": {"$in": ["{X}", "{D}"]}}]),
            control=_replay(expect_terms=("{X}", "{D}")),
            leak_terms=("{X}", "{D}", "{X_name}", "{D_name}"),
            phase=20,
        ),
        Case(
            id="R8b",
            group="reading",
            actor="A",
            token="A's valid token",
            action="query users by role (everyone with role user)",
            expect="no-leak",
            step=_call("A", "client", "queryUsers", [{"role": "user"}]),
            control=_replay(expect_terms=("{X}",)),
            leak_terms=("{X}", "{D}", "{B}"),
            phase=20,
        ),
        Case(
            id="R9",
            group="reading",
            actor="A",
            token="A's valid token",
            action="query XD's members",
            expect="refused",
            step=_call("A", "channel", "queryMembers", [{}], channel=(T, "{XD}")),
            # No client may read member lists (members have read-channel only).
            control=_replay(),
            leak_terms=("{X}", "{D}"),
            phase=20,
        ),
    ]


def _content() -> list[Case]:
    ab = (T, "{AB}")
    a_user = {"user_id": "{A}"}
    return [
        Case(
            id="S1",
            group="content",
            actor="A",
            token="A's valid token",
            action="send a message to AB",
            expect="refused",
            step=_call("A", "channel", "sendMessage", [{"text": "direct send by A"}], channel=ab),
            control=_replay(body_patch={"message": a_user}, capture={"m_ctl": "message.id"}),
            phase=30,
        ),
        Case(
            id="S2",
            group="content",
            actor="A",
            token="A's valid token",
            action="reply in a thread to B's server-sent message",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "sendMessage",
                [{"text": "thread reply by A", "parent_id": "{m_b}"}],
                channel=ab,
            ),
            control=_replay(body_patch={"message": a_user}),
            phase=30,
            feature_override={"replies": True},
        ),
        Case(
            id="S3a",
            group="content",
            actor="A",
            token="A's valid token",
            action="edit A's own server-sent message",
            expect="refused",
            step=_call("A", "client", "updateMessage", [{"id": "{m_a}", "text": "edited by A"}]),
            control=_replay(
                body_patch={"message": a_user},
                undo=(
                    ServerRequest(
                        "POST",
                        "/messages/{m_a}",
                        {"message": {"id": "{m_a}", "text": "{m_a_text}", "user_id": "{A}"}},
                    ),
                ),
            ),
            phase=30,
        ),
        Case(
            id="S3b",
            group="content",
            actor="A",
            token="A's valid token",
            action="edit B's server-sent message",
            expect="refused",
            step=_call("A", "client", "updateMessage", [{"id": "{m_b}", "text": "edited by A"}]),
            control=_replay(
                body_patch={"message": {"user_id": "{B}"}},
                undo=(
                    ServerRequest(
                        "POST",
                        "/messages/{m_b}",
                        {"message": {"id": "{m_b}", "text": "{m_b_text}", "user_id": "{B}"}},
                    ),
                ),
            ),
            phase=30,
        ),
        Case(
            id="S5",
            group="content",
            actor="A",
            token="A's valid token",
            action="react to B's message",
            expect="refused",
            step=_call("A", "channel", "sendReaction", ["{m_b}", {"type": "love"}], channel=ab),
            control=_replay(
                body_patch={"reaction": a_user},
                undo=(
                    ServerRequest(
                        "DELETE", "/messages/{m_b}/reaction/love", params={"user_id": "{A}"}
                    ),
                ),
            ),
            phase=30,
            feature_override={"reactions": True},
        ),
        Case(
            id="S6",
            group="content",
            actor="A",
            token="A's valid token",
            action="upload a file to AB",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "sendFile",
                [{"__buffer_b64": PROOF_FILE_B64}, "proof.txt", "text/plain"],
                channel=ab,
            ),
            control=Control(kind="server-upload", note="server uploads the same file as A"),
            phase=30,
            feature_override={"uploads": True},
        ),
        Case(
            id="S7",
            group="content",
            actor="A",
            token="A's valid token",
            action="upload an image to AB",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "sendImage",
                [{"__buffer_b64": PROOF_PNG_B64}, "proof.png", "image/png"],
                channel=ab,
            ),
            control=Control(kind="server-upload", note="server uploads the same image as A"),
            phase=30,
            feature_override={"uploads": True},
        ),
        Case(
            id="S8",
            group="content",
            actor="A",
            token="A's valid token",
            action="pin B's message",
            expect="refused",
            step=_call("A", "client", "pinMessage", ["{m_b}"]),
            control=_replay(
                body_patch=a_user,
                undo=(
                    ServerRequest(
                        "PUT", "/messages/{m_b}", {"set": {"pinned": False}, "user_id": "{A}"}
                    ),
                ),
            ),
            phase=30,
        ),
        Case(
            id="S9",
            group="content",
            actor="A",
            token="A's valid token",
            action="create a poll",
            expect="refused",
            step=_call(
                "A",
                "client",
                "createPoll",
                [{"name": "poll by A", "options": [{"text": "yes"}, {"text": "no"}]}],
            ),
            control=_replay(body_patch=a_user, capture={"ctl_poll": "poll.id"}),
            phase=30,
        ),
        Case(
            id="S10",
            group="content",
            actor="A",
            token="A's valid token",
            action="vote on a poll in AB",
            expect="refused",
            control=Control(kind="custom", note="server votes as A on the same poll"),
            procedure="poll-vote",
            phase=30,
        ),
        Case(
            id="S11",
            group="content",
            actor="A",
            token="A's valid token",
            action="send a slash command (/giphy) to AB",
            expect="refused",
            step=_call("A", "channel", "sendMessage", [{"text": "/giphy proof"}], channel=ab),
            control=_replay(body_patch={"message": a_user}),
            phase=30,
        ),
        Case(
            id="S12",
            group="content",
            actor="A",
            token="A's valid token",
            action="send a custom event with free text to AB",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "sendEvent",
                [{"type": "glow_proof", "glow_text": "custom event free text"}],
                channel=ab,
            ),
            control=_replay(body_patch={"event": a_user}),
            phase=30,
            type_override={"custom_events": True},
        ),
        Case(
            id="S13",
            group="content",
            actor="A",
            token="A's valid token",
            action="change A's own name and a custom profile field",
            expect="refused",
            step=_call(
                "A",
                "client",
                "partialUpdateUser",
                [{"id": "{A}", "set": {"name": "renamed by A", "glow_bio": "profile free text"}}],
            ),
            control=_replay(
                undo=(
                    ServerRequest(
                        "PATCH",
                        "/users",
                        {
                            "users": [
                                {"id": "{A}", "set": {"name": "{A_name}"}, "unset": ["glow_bio"]}
                            ]
                        },
                    ),
                ),
            ),
            phase=30,
        ),
        Case(
            id="S14",
            group="content",
            actor="A",
            token="A's valid token",
            action="change A's own profile by connecting with new name, image and custom field",
            expect="not-effective",
            control=Control(kind="custom", note="server sets the same fields; then restores"),
            procedure="profile-on-connect",
            phase=30,
        ),
        Case(
            id="S15",
            group="content",
            actor="A",
            token="A's valid token",
            action="set a free-text custom field on A's own membership in AB (can B read it?)",
            expect="no-leak",
            control=Control(
                kind="custom",
                note="server sets the same field; B's reads with read-channel-members granted",
            ),
            procedure="member-custom",
            leak_terms=("{member_marker}",),
            phase=30,
        ),
        Case(
            id="S16",
            group="content",
            actor="A",
            token="A's valid token",
            action="create a user group containing A and B",
            expect="refused",
            step=_call(
                "A",
                "client",
                "createUserGroup",
                [{"name": "{prefix} group by A", "member_ids": ["{A}", "{B}"]}],
            ),
            control=_replay(
                body_patch={"created_by_id": "{A}"}, capture={"ctl_group": "user_group.id"}
            ),
            phase=30,
        ),
        Case(
            id="RT2",
            group="realtime",
            actor="A",
            token="A's valid token",
            action="typing event carrying a free-text field (what B receives)",
            expect="carries-no-free-text",
            # No positive control: no member may send a typing event while typing
            # events are off, so an authentication or permission refusal is
            # INCONCLUSIVE (P06.1-C3).
            control=Control(
                kind="custom",
                note="B connected and watching AB; no member may send the same event",
            ),
            procedure="typing-payload",
            phase=25,
        ),
        Case(
            id="RT3",
            group="realtime",
            actor="A",
            token="A's valid token",
            action="read event carrying a free-text field (what B receives)",
            expect="carries-no-free-text",
            # The positive control of a refusal: B's own markRead with the same body
            # (P06.1-C3).
            control=Control(
                kind="custom",
                session="B",
                note="B connected and watching AB; B's own markRead with the same body",
            ),
            procedure="read-payload",
            phase=25,
        ),
    ]


def _realtime() -> list[Case]:
    return [
        Case(
            id="RT1",
            group="realtime",
            actor="A",
            token="A's valid token",
            action="while connected, receive events for AB and none for XD",
            expect="no-leak",
            control=Control(kind="custom", note="X receives XD's event"),
            procedure="realtime-isolation",
            leak_terms=("{XD}", "{xd_text}"),
            phase=25,
        ),
    ]


def _escalation() -> list[Case]:
    return [
        Case(
            id="E1",
            group="self-escalation",
            actor="A",
            token="A's valid token",
            action="set A's own role to admin (partial update)",
            expect="refused",
            step=_call(
                "A", "client", "partialUpdateUser", [{"id": "{A}", "set": {"role": "admin"}}]
            ),
            control=_replay(
                undo=(
                    ServerRequest(
                        "PATCH", "/users", {"users": [{"id": "{A}", "set": {"role": "user"}}]}
                    ),
                ),
            ),
            phase=40,
        ),
        Case(
            id="E2",
            group="self-escalation",
            actor="A",
            token="A's valid token",
            action="set A's own role to admin (upsert)",
            expect="refused",
            step=_call("A", "client", "upsertUser", [{"id": "{A}", "role": "admin"}]),
            control=_replay(
                undo=(
                    ServerRequest(
                        "PATCH", "/users", {"users": [{"id": "{A}", "set": {"role": "user"}}]}
                    ),
                ),
            ),
            phase=40,
        ),
        Case(
            id="E3",
            group="self-escalation",
            actor="A",
            token="A's valid token",
            action="set A's own teams",
            expect="refused",
            step=_call(
                "A", "client", "partialUpdateUser", [{"id": "{A}", "set": {"teams": ["glow"]}}]
            ),
            control=_replay(
                undo=(
                    ServerRequest(
                        "PATCH", "/users", {"users": [{"id": "{A}", "unset": ["teams"]}]}
                    ),
                ),
            ),
            phase=40,
        ),
        Case(
            id="E6",
            group="self-escalation",
            actor="A",
            token="A's valid token",
            action="set A's own channel_role to channel_moderator (member partial update)",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "updateMemberPartial",
                [{"set": {"channel_role": "channel_moderator"}}],
                channel=(T, "{AB}"),
            ),
            control=_replay(
                keep_params=("user_id",),
                undo=(
                    ServerRequest(
                        "PATCH",
                        "/channels/" + T + "/{AB}/member",
                        {"set": {"channel_role": "channel_member"}},
                        {"user_id": "{A}"},
                    ),
                ),
            ),
            phase=40,
        ),
        Case(
            id="E4",
            group="self-escalation",
            actor="A",
            token="A's valid token",
            action="assign A the channel_moderator role in AB",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "assignRoles",
                [[{"user_id": "{A}", "channel_role": "channel_moderator"}]],
                channel=(T, "{AB}"),
            ),
            control=_replay(
                undo=(
                    ServerRequest(
                        "POST",
                        "/channels/" + T + "/{AB}",
                        {"assign_roles": [{"user_id": "{A}", "channel_role": "channel_member"}]},
                    ),
                ),
            ),
            phase=40,
        ),
        Case(
            id="E5",
            group="self-escalation",
            actor="A",
            token="A's valid token",
            action="connect claiming role admin in the user object",
            expect="not-effective",
            control=Control(kind="custom", note="E1's control shows the server can set a role"),
            procedure="role-on-connect",
            phase=40,
        ),
    ]


def _create_join() -> list[Case]:
    cases = [
        Case(
            id="C1",
            group="create-join",
            actor="A",
            token="A's valid token",
            action=f"create a {T} channel with members A and B",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "create",
                [],
                channel=(T, "{prefix}-c1"),
                channel_data={"members": ["{A}", "{B}"]},
            ),
            control=_replay(body_patch={"data": {"created_by_id": "{A}"}}, creates_channel=True),
            phase=50,
        )
    ]
    for n, ctype in enumerate(DEFAULT_TYPES, start=2):
        ch = (ctype, f"{{prefix}}-c{n}")
        path = f"/channels/{ctype}/{{prefix}}-c{n}"
        cases += [
            Case(
                id=f"C{n}-create",
                group="create-join",
                actor="A",
                token="A's valid token",
                action=f"create a {ctype} channel with members A and B",
                expect="refused",
                step=_call(
                    "A",
                    "channel",
                    "create",
                    [],
                    channel=ch,
                    channel_data={"members": ["{A}", "{B}"]},
                ),
                control=_replay(
                    body_patch={"data": {"created_by_id": "{A}"}}, creates_channel=True
                ),
                phase=50 + n,
            ),
            Case(
                id=f"C{n}-read",
                group="create-join",
                actor="A",
                token="A's valid token",
                action=f"read that {ctype} channel as one of its members",
                expect="refused",
                step=_call("A", "channel", "query", [READ_OPTIONS], channel=ch),
                control=_replay(),
                phase=50 + n,
            ),
            Case(
                id=f"C{n}-send",
                group="create-join",
                actor="A",
                token="A's valid token",
                action=f"send in that {ctype} channel as one of its members",
                expect="refused",
                step=_call(
                    "A", "channel", "sendMessage", [{"text": f"send by A in {ctype}"}], channel=ch
                ),
                control=_replay(body_patch={"message": {"user_id": "{A}"}}),
                phase=50 + n,
            ),
            Case(
                id=f"C{n}-join",
                group="create-join",
                actor="X",
                token="X's valid token",
                action=f"join that {ctype} channel (add own membership)",
                expect="refused",
                step=_call("X", "channel", "addMembers", [["{X}"]], channel=ch),
                control=_replay(undo=(ServerRequest("POST", path, {"remove_members": ["{X}"]}),)),
                phase=50 + n,
            ),
        ]
    ab = (T, "{AB}")
    ab_path = "/channels/" + T + "/{AB}"
    cases += [
        Case(
            id="C7",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="add X to AB",
            expect="refused",
            step=_call("A", "channel", "addMembers", [["{X}"]], channel=ab),
            control=_replay(undo=(ServerRequest("POST", ab_path, {"remove_members": ["{X}"]}),)),
            phase=58,
        ),
        Case(
            id="C8",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="add itself to XD",
            expect="refused",
            step=_call("A", "channel", "addMembers", [["{A}"]], channel=(T, "{XD}")),
            control=_replay(
                undo=(
                    ServerRequest("POST", "/channels/" + T + "/{XD}", {"remove_members": ["{A}"]}),
                )
            ),
            phase=58,
        ),
        Case(
            id="C9",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="remove B from AB",
            expect="refused",
            step=_call("A", "channel", "removeMembers", [["{B}"]], channel=ab),
            control=_replay(undo=(ServerRequest("POST", ab_path, {"add_members": ["{B}"]}),)),
            phase=58,
        ),
        Case(
            id="C10a",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="change AB's data (partial update: name and a custom field)",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "updatePartial",
                [{"set": {"name": "renamed by A", "glow_topic": "channel free text"}}],
                channel=ab,
            ),
            control=_replay(
                undo=(ServerRequest("PATCH", ab_path, {"unset": ["name", "glow_topic"]}),)
            ),
            phase=58,
        ),
        Case(
            id="C10b",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="change AB's data (full update)",
            expect="refused",
            step=_call("A", "channel", "update", [{"name": "renamed by A"}], channel=ab),
            control=_replay(undo=(ServerRequest("PATCH", ab_path, {"unset": ["name"]}),)),
            phase=58,
        ),
        Case(
            id="C11",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="freeze AB",
            expect="refused",
            step=_call("A", "channel", "updatePartial", [{"set": {"frozen": True}}], channel=ab),
            control=_replay(undo=(ServerRequest("PATCH", ab_path, {"set": {"frozen": False}}),)),
            phase=58,
        ),
        Case(
            id="S4a",
            group="content",
            actor="A",
            token="A's valid token",
            action="delete A's own server-sent message",
            expect="refused",
            step=_call("A", "client", "deleteMessage", ["{m_a}"]),
            control=_replay(),
            phase=70,
        ),
        Case(
            id="S4b",
            group="content",
            actor="A",
            token="A's valid token",
            action="delete B's server-sent message",
            expect="refused",
            step=_call("A", "client", "deleteMessage", ["{m_b}"]),
            control=_replay(),
            phase=70,
        ),
        Case(
            id="C12",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="truncate AB",
            expect="refused",
            step=_call("A", "channel", "truncate", [], channel=ab),
            control=_replay(),
            phase=80,
        ),
        Case(
            id="C13",
            group="create-join",
            actor="A",
            token="A's valid token",
            action="delete AB",
            expect="refused",
            step=_call("A", "channel", "delete", [], channel=ab),
            control=_replay(),
            phase=90,
        ),
    ]
    return cases


def _revocation() -> list[Case]:
    """P06.1-I2a: each mechanism under the history policy, on a channel of its own
    (glow_stream_proof.mechanisms). Phases from 100 run after the I1 matrix."""
    control = Control(
        kind="custom", note="the same requests by the same members before the mechanism"
    )
    specs = (
        ("RV-remove", "revocation", "remove M1 from its channel (M2 named as the acting user)"),
        ("RV-ban", "revocation", "ban M1 in its channel (M2 named as the banning user)"),
        ("RV-hide", "revocation", "hide the channel for M1"),
        ("RV-freeze", "revocation", "freeze the channel (M2 named as the acting user)"),
        ("RV-revoke", "revocation", "revoke R's tokens issued before now (R has two devices)"),
        ("SD-deactivate", "suspension-deletion", "deactivate S (messages kept)"),
        ("SD-delete", "suspension-deletion", "hard-delete H (messages and conversations hard)"),
    )
    return [
        Case(
            id=case_id,
            group=group,
            actor="server",
            token="server",
            action=action,
            expect="ends-access",
            control=control,
            procedure=f"mechanism:{case_id.split('-', 1)[1]}",
            phase=100 + n,
            calls=120,
        )
        for n, (case_id, group, action) in enumerate(specs)
    ]


def _i2a() -> list[Case]:
    """P06.1-I2a's other cases (glow_stream_proof.i2a): the existence oracle, the
    endpoints the I1 matrix never tried (the I1 review's finding 9), the S15 mapping,
    token expiry and the outage injection."""
    ab = (T, "{AB}")
    xd = (T, "{XD}")
    ab_path = "/channels/" + T + "/{AB}"
    xd_terms = ("{xd_text}", "{m_x}", "{X}", "{D}", "{XD}")
    a_token = "A's valid token"
    cases = [
        Case(
            id=f"EO-{kind}",
            group="existence-oracle",
            actor="A",
            token=a_token,
            action=action,
            expect="no-oracle",
            control=Control(kind="custom", note="the existing ID exists (an entitled read)"),
            procedure=f"oracle:{kind}",
            phase=21,
            calls=40,
        )
        for kind, action in (
            ("channel", "read, watch, GET and sync XD against a channel that does not exist"),
            ("user", "query X, and add X to AB, against a user that does not exist"),
            ("message", "fetch XD's message against a message that does not exist"),
        )
    ]
    reads = (
        ("F9-replies", "get the replies to XD's message", "channel", "getReplies", ["{m_x}"]),
        ("F9-reactions", "get the reactions to XD's message", "channel", "getReactions", ["{m_x}"]),
        ("F9-by-id", "get XD's message by ID in XD", "channel", "getMessagesById", [["{m_x}"]]),
        (
            "F9-query-reactions",
            "query the reactions to XD's message",
            "client",
            "queryReactions",
            ["{m_x}", {}],
        ),
        (
            "F9-thread",
            "get the thread of XD's message (the SDK watches it)",
            "client",
            "getThread",
            ["{m_x}"],
        ),
    )
    for case_id, action, target, method, args in reads:
        cases.append(
            Case(
                id=case_id,
                group="finding-9",
                actor="A",
                token=a_token,
                action=action,
                expect="refused",
                step=_call("A", target, method, args, channel=xd if target == "channel" else None),
                control=Control(kind="session", session="X"),
                leak_terms=xd_terms,
                phase=22,
            )
        )
    cases += [
        Case(
            id="F9-history",
            group="finding-9",
            actor="A",
            token=a_token,
            action="query the edit history of XD's message (a server-side API)",
            expect="refused",
            step=_call("A", "client", "queryMessageHistory", [{"message_id": "{m_x}"}]),
            control=_replay(),
            leak_terms=xd_terms,
            phase=22,
        ),
        Case(
            id="F9-sync",
            group="finding-9",
            actor="A",
            token=a_token,
            action="sync XD's events since the run started",
            expect="no-leak",
            step=_call("A", "client", "sync", [["{XD_cid}"], "{run_start}"]),
            control=Control(kind="session", session="X", expect_terms=("{xd_text}",)),
            leak_terms=xd_terms,
            phase=22,
        ),
        Case(
            id="F9-ai",
            group="finding-9",
            actor="A",
            token=a_token,
            action="send an AI state event with free text to AB (updateAIState)",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "updateAIState",
                ["{m_b}", "AI_STATE_THINKING", {"ai_message": "ai free text {prefix}"}],
                channel=ab,
            ),
            control=_replay(body_patch={"event": {"user_id": "{A}"}}),
            phase=31,
            type_override={"custom_events": True},
        ),
        Case(
            id="F9-member-other",
            group="finding-9",
            actor="A",
            token=a_token,
            action="set a custom field on B's membership in AB (partialUpdateMember)",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "partialUpdateMember",
                ["{B}", {"set": {"glow_note": "written by A {prefix}"}}],
                channel=ab,
            ),
            control=_replay(
                undo=(ServerRequest("PATCH", ab_path + "/member/{B}", {"unset": ["glow_note"]}),)
            ),
            phase=31,
        ),
        Case(
            id="S15-map",
            group="content",
            actor="A",
            token=a_token,
            action="map the member fields A can set on its own membership, what B receives, "
            "and the server's overwrite and clear",
            expect="mapping",
            control=Control(kind="custom", note="the server's replay of each refused write"),
            procedure="s15-map",
            phase=32,
            calls=110,
        ),
    ]
    for flag, name in (("pinned", "pin"), ("archived", "archive")):
        cases.append(
            Case(
                id=f"F9-{name}",
                group="finding-9",
                actor="A",
                token=a_token,
                action=f"{name} AB for itself (can B read it?)",
                expect="no-leak",
                control=Control(kind="custom", note="the server's member read"),
                procedure=f"own-member-flag:{flag}",
                leak_terms=(f"{flag}_at",),
                phase=33,
                calls=40,
            )
        )
    for kind in ("accept", "reject"):
        cases.append(
            Case(
                id=f"F9-invite-{kind}",
                group="finding-9",
                actor="B",
                token="B's valid token",
                action=f"{kind} an invite to a channel of A's, with a message",
                expect="refused",
                control=Control(kind="custom", note="the server's replay of the same request"),
                procedure=f"invite:{kind}",
                phase=34,
                calls=40,
            )
        )
    cases += [
        Case(
            id="TD-expiry",
            group="tokens-devices",
            actor="A",
            token="a second token of A's, valid for 25 s",
            action="read AB, keep a connection and reconnect after the token expires, "
            "with A's first device alongside",
            expect="refused",
            control=Control(kind="custom", note="the same requests before expiry"),
            procedure="token-expiry",
            phase=60,
            calls=40,
        ),
        Case(
            id="OUT-send",
            group="outage",
            actor="app",
            token="server",
            action="the app send path with the provider unreachable (a connection error "
            "injected inside the process)",
            expect="refuses-without-state",
            control=Control(kind="custom", note="the same send with the provider reachable"),
            procedure="outage",
            phase=61,
            calls=20,
        ),
    ]
    for case_id, method, shadow in (
        ("F9-ban", "banUser", False),
        ("F9-shadowban", "shadowBan", True),
    ):
        undo_params = {"target_user_id": "{B}", "type": T, "id": "{AB}"}
        if shadow:
            undo_params["shadow"] = "true"
        cases.append(
            Case(
                id=case_id,
                group="finding-9",
                actor="A",
                token=a_token,
                action=("shadow-ban" if shadow else "ban") + " B in AB, with a reason",
                expect="refused",
                step=_call(
                    "A",
                    "channel",
                    method,
                    ["{B}", {"reason": "ban free text {prefix}"}],
                    channel=ab,
                ),
                control=_replay(
                    body_patch={"banned_by_id": "{A}"},
                    undo=(ServerRequest("DELETE", "/moderation/ban", None, undo_params),),
                ),
                phase=64,
            )
        )
    cases.append(
        Case(
            id="F9-leave",
            group="finding-9",
            actor="A",
            token=a_token,
            action="leave AB with a message",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "removeMembers",
                [["{A}"], {"text": "leave free text {prefix}"}],
                channel=ab,
            ),
            control=_replay(
                body_patch={"message": {"user_id": "{A}"}},
                undo=(ServerRequest("POST", ab_path, {"add_members": ["{A}"]}),),
            ),
            phase=65,
        )
    )
    return cases


def _products() -> list[Case]:
    """P06.1-I2b: what a user token can do in Video and Feeds (the brief: "what a user
    token can do, and a lockdown by configuration only"). Every request goes through the
    runner's product op, whose allowlist and deny-list are in code; no request rings,
    notifies, joins, records or broadcasts. Each case's objects are the run's own: a
    fixture creates them server-side when the case needs them, cleanup deletes them.
    Before the lockdown a FAIL records a capability; after it every case must HOLD, and a
    FAIL is a capability the configuration did not remove. Phase 91 (Video) and 92
    (Feeds): after C13, the last case on AB, and before the families."""
    a_token, b_token = "A's valid token", "B's valid token"
    call = "/api/v2/video/call/default/{CALL}"
    call_x = "/api/v2/video/call/default/{CALL_x}"
    members_a_b = [{"user_id": "{A}"}, {"user_id": "{B}"}]
    # The fixtures: a call of A's with A and B as members, a call of A's with A alone.
    fixture_call = ServerRequest(
        "POST",
        call,
        {
            "data": {
                "created_by_id": "{A}",
                "custom": {"glow_note": "{vd_text}"},
                "members": members_a_b,
            }
        },
    )
    fixture_call_x = ServerRequest(
        "POST",
        call_x,
        {
            "data": {
                "created_by_id": "{A}",
                "custom": {"glow_note": "{vd_text}"},
                "members": [{"user_id": "{A}"}],
            }
        },
    )
    delete_hard = {"hard": True}
    video: list[Case] = [
        Case(
            id="VD-create",
            group="video",
            actor="A",
            token=a_token,
            action="create a call (type default) with custom data and A and B as members",
            expect="refused",
            step=_product(
                "A",
                "POST",
                "/api/v2/video/call/default/{CALL_a}",
                {"data": {"custom": {"glow_note": "{vd_text}"}, "members": members_a_b}},
            ),
            control=_replay(
                body_patch={"data": {"created_by_id": "{A}"}},
                undo_once=True,
                undo=(
                    ServerRequest(
                        "POST", "/api/v2/video/call/default/{CALL_a}/delete", delete_hard
                    ),
                ),
            ),
            phase=91,
        ),
        Case(
            id="VD-create-dev",
            group="video",
            actor="A",
            token=a_token,
            action="create a call of the built-in development type with A and B as members",
            expect="refused",
            step=_product(
                "A",
                "POST",
                "/api/v2/video/call/development/{CALL_dev}",
                {"data": {"custom": {"glow_note": "{vd_text}"}, "members": members_a_b}},
            ),
            control=_replay(
                body_patch={"data": {"created_by_id": "{A}"}},
                undo_once=True,
                undo=(
                    ServerRequest(
                        "POST", "/api/v2/video/call/development/{CALL_dev}/delete", delete_hard
                    ),
                ),
            ),
            phase=91,
        ),
        Case(
            id="VD-read",
            group="video",
            actor="A",
            token=a_token,
            action="read a call A is a member of (a call the server created with A and B)",
            expect="refused",
            step=_product("A", "GET", call),
            control=_replay(),
            fixture=(fixture_call,),
            phase=91,
        ),
        Case(
            id="VD-read-other",
            group="video",
            actor="B",
            token=b_token,
            action="read A's call, which B is not a member of (can B see its custom data?)",
            expect="no-leak",
            step=_product("B", "GET", call_x),
            control=Control(kind="session", session="A", expect_terms=("{vd_text}",)),
            leak_terms=("{vd_text}", "{A}"),
            fixture=(fixture_call_x,),
            phase=91,
        ),
        Case(
            id="VD-update",
            group="video",
            actor="A",
            token=a_token,
            action="update the custom data of a call A is a member of",
            expect="refused",
            step=_product("A", "PATCH", call, {"custom": {"glow_note": "updated {vd_text}"}}),
            control=_replay(
                undo_once=True,
                undo=(ServerRequest("PATCH", call, {"custom": {"glow_note": "{vd_text}"}}),),
            ),
            fixture=(fixture_call,),
            phase=91,
        ),
        Case(
            id="VD-members",
            group="video",
            actor="A",
            token=a_token,
            action="add B as a member of A's call",
            expect="refused",
            step=_product(
                "A", "POST", call_x + "/members", {"update_members": [{"user_id": "{B}"}]}
            ),
            control=_replay(
                undo_once=True,
                undo=(ServerRequest("POST", call_x + "/members", {"remove_members": ["{B}"]}),),
            ),
            fixture=(fixture_call_x,),
            phase=91,
        ),
        Case(
            id="VD-event",
            group="video",
            actor="A",
            token=a_token,
            action="send a custom event with free text to a call A and B are members of",
            expect="refused",
            step=_product(
                "A", "POST", call + "/event", {"custom": {"glow_note": "event {vd_text}"}}
            ),
            control=_replay(body_patch={"user_id": "{A}"}),
            fixture=(fixture_call,),
            phase=91,
        ),
        Case(
            id="VD-query",
            group="video",
            actor="B",
            token=b_token,
            action="query the calls A created (can B find A's call?)",
            expect="no-leak",
            step=_product(
                "B",
                "POST",
                "/api/v2/video/calls",
                {"filter_conditions": {"created_by_user_id": "{A}"}, "limit": 10},
            ),
            control=_replay(expect_terms=("{CALL_x}",)),
            leak_terms=("{CALL_x}", "{vd_text}"),
            fixture=(fixture_call_x,),
            phase=91,
        ),
    ]
    feed_a = "/api/v2/feeds/feed_groups/{FG}/feeds/{A}"
    feed_b = "/api/v2/feeds/feed_groups/{FG}/feeds/{B}"
    timeline_b = "/api/v2/feeds/feed_groups/{FGT}/feeds/{B}"
    # The fixtures: A's and B's feeds, B's timeline, and an activity of A's in A's feed.
    fixture_feed_a = ServerRequest("POST", feed_a, {"user_id": "{A}"})
    fixture_feed_b = ServerRequest("POST", feed_b, {"user_id": "{B}"})
    fixture_timeline_b = ServerRequest("POST", timeline_b, {"user_id": "{B}"})
    fixture_activity = ServerRequest(
        "POST",
        "/api/v2/feeds/activities",
        {
            "type": "post",
            "feeds": ["{FG}:{A}"],
            "text": "{fd_text}",
            "user_id": "{A}",
            "skip_push": True,
        },
        capture={"ACT": "activity.id"},
    )
    with_activity = (fixture_feed_a, fixture_activity)
    feeds: list[Case] = [
        Case(
            id="FD-feed",
            group="feeds",
            actor="A",
            token=a_token,
            action="create A's own feed with custom data (get or create)",
            expect="refused",
            step=_product("A", "POST", feed_a, {"data": {"custom": {"glow_note": "feed of {A}"}}}),
            # No undo: Stream does not recreate a deleted feed ID ("feed with id ... has
            # been deleted", run V1 of 27 September 2026), and the later Feeds cases need
            # A's feed; the replay's feed stays, recorded, and cleanup deletes it.
            control=_replay(body_patch={"user_id": "{A}"}),
            phase=92,
        ),
        Case(
            id="FD-activity",
            group="feeds",
            actor="A",
            token=a_token,
            action="add an activity with free text to A's own feed",
            expect="refused",
            step=_product(
                "A",
                "POST",
                "/api/v2/feeds/activities",
                {"type": "post", "feeds": ["{FG}:{A}"], "text": "{fd_text}", "skip_push": True},
            ),
            control=_replay(body_patch={"user_id": "{A}"}),
            fixture=(fixture_feed_a,),
            phase=92,
        ),
        Case(
            id="FD-other-feed",
            group="feeds",
            actor="A",
            token=a_token,
            action="add an activity with free text to B's feed",
            expect="refused",
            step=_product(
                "A",
                "POST",
                "/api/v2/feeds/activities",
                {
                    "type": "post",
                    "feeds": ["{FG}:{B}"],
                    "text": "to B {fd_text}",
                    "skip_push": True,
                },
            ),
            control=_replay(body_patch={"user_id": "{A}"}),
            fixture=(fixture_feed_b,),
            phase=92,
        ),
        Case(
            id="FD-read",
            group="feeds",
            actor="B",
            token=b_token,
            action="read A's feed (can B see A's activity?)",
            expect="no-leak",
            step=_product("B", "POST", feed_a, {"limit": 10}),
            control=Control(kind="session", session="A", expect_terms=("{fd_text}",)),
            leak_terms=("{fd_text}", "{ACT}"),
            fixture=with_activity,
            phase=92,
        ),
        Case(
            id="FD-query",
            group="feeds",
            actor="B",
            token=b_token,
            action="query A's activities (can B find them?)",
            expect="no-leak",
            step=_product(
                "B",
                "POST",
                "/api/v2/feeds/activities/query",
                {"filter": {"user_id": "{A}"}, "limit": 10},
            ),
            control=_replay(expect_terms=("{fd_text}",)),
            leak_terms=("{fd_text}", "{ACT}"),
            fixture=with_activity,
            phase=92,
        ),
        Case(
            id="FD-follow",
            group="feeds",
            actor="B",
            token=b_token,
            action="follow A's feed from B's timeline",
            expect="refused",
            step=_product(
                "B",
                "POST",
                "/api/v2/feeds/follows",
                {"source": "{FGT}:{B}", "target": "{FG}:{A}", "skip_push": True},
            ),
            control=_replay(
                undo_once=True,
                undo=(ServerRequest("DELETE", "/api/v2/feeds/follows/{FGT}:{B}/{FG}:{A}"),),
            ),
            fixture=(fixture_feed_a, fixture_timeline_b),
            phase=92,
        ),
        Case(
            id="FD-comment",
            group="feeds",
            actor="B",
            token=b_token,
            action="comment with free text on A's activity",
            expect="refused",
            step=_product(
                "B",
                "POST",
                "/api/v2/feeds/comments",
                {
                    "comment": "comment {fd_text}",
                    "object_id": "{ACT}",
                    "object_type": "activity",
                    "skip_push": True,
                },
            ),
            control=_replay(body_patch={"user_id": "{B}"}),
            fixture=with_activity,
            phase=92,
        ),
        Case(
            id="FD-reaction",
            group="feeds",
            actor="B",
            token=b_token,
            action="react to A's activity",
            expect="refused",
            step=_product(
                "B",
                "POST",
                "/api/v2/feeds/activities/{ACT}/reactions",
                {"type": "like", "skip_push": True},
            ),
            control=_replay(
                body_patch={"user_id": "{B}"},
                undo_once=True,
                undo=(
                    ServerRequest(
                        "DELETE",
                        "/api/v2/feeds/activities/{ACT}/reactions/like",
                        None,
                        {"user_id": "{B}"},
                    ),
                ),
            ),
            fixture=with_activity,
            phase=92,
        ),
        Case(
            id="FD-update",
            group="feeds",
            actor="A",
            token=a_token,
            action="edit the text and custom data of A's own activity",
            expect="refused",
            step=_product(
                "A",
                "PUT",
                "/api/v2/feeds/activities/{ACT}",
                {"text": "edited {fd_text}", "custom": {"glow_note": "edited"}},
            ),
            control=_replay(
                body_patch={"user_id": "{A}"},
                undo_once=True,
                undo=(
                    ServerRequest(
                        "PUT",
                        "/api/v2/feeds/activities/{ACT}",
                        {"text": "{fd_text}", "custom": {}, "user_id": "{A}"},
                    ),
                ),
            ),
            fixture=with_activity,
            phase=92,
        ),
        Case(
            id="FD-feed-custom",
            group="feeds",
            actor="A",
            token=a_token,
            action="update the custom data of A's own feed",
            expect="refused",
            step=_product("A", "PUT", feed_a, {"custom": {"glow_note": "feed {fd_text}"}}),
            control=_replay(
                undo_once=True,
                undo=(ServerRequest("PUT", feed_a, {"custom": {}}),),
            ),
            fixture=(fixture_feed_a,),
            phase=92,
        ),
    ]
    return video + feeds


def all_cases() -> list[Case]:
    cases = (
        _tokens_and_access()
        + _reading()
        + _realtime()
        + _content()
        + _escalation()
        + _create_join()
        + _i2a()
        + _products()
        + _revocation()
    )
    return sorted(cases, key=lambda c: c.phase)


def validate(cases: list[Case]) -> list[str]:
    """Structural problems in the matrix definition (used by the offline tests)."""
    problems = []
    seen: set[str] = set()
    for case in cases:
        if case.id in seen:
            problems.append(f"duplicate case id {case.id}")
        seen.add(case.id)
        if (case.step is None) == (case.procedure is None):
            problems.append(f"{case.id}: needs exactly one of step or procedure")
        if case.control.kind == "none":
            problems.append(f"{case.id}: every case needs a positive control")
        if case.control.kind == "session" and not case.control.session:
            problems.append(f"{case.id}: session control without a session")
        if case.expect == "no-leak" and not case.leak_terms:
            problems.append(f"{case.id}: no-leak case without leak terms")
        if case.step is not None and case.step.session not in ("A", "B", "X"):
            problems.append(f"{case.id}: unknown session {case.step.session}")
        if case.step is not None and case.step.op == "product":
            # P06.1-I2b: a product step names only what the runner's op allows.
            params = case.step.params
            why = products.client_refusal(
                str(params.get("method")),
                str(params.get("path")),
                params.get("body"),
                params.get("params"),
            )
            if why is not None:
                problems.append(f"{case.id}: the product op would refuse its step: {why}")
        if product_of(case) is not None and case.phase >= 100:
            problems.append(f"{case.id}: a product case runs before the families")
    return problems
