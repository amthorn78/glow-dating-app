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
"""

from __future__ import annotations

import base64
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from .configuration import DEFAULT_TYPES, MATCH_TYPE

Expect = Literal["refused", "no-leak", "not-effective", "identity-kept", "carries-no-free-text"]
Outcome = Literal["success", "auth", "permission", "feature", "not-found", "input", "other"]

AUTH_CODES = frozenset({2, 5, 40, 41, 42, 43})
PERMISSION_CODES = frozenset({17, 70})
FEATURE_CODES = frozenset({18, 19})

PROOF_FILE_B64 = base64.b64encode(b"P06.1 synthetic proof file\n").decode("ascii")
# A 1x1 transparent PNG.
PROOF_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kg"
    "AAAABJRU5ErkJggg=="
)


@dataclass(frozen=True)
class SdkStep:
    session: str
    op: Literal["call", "request"]
    params: Mapping[str, Any]
    max_calls: int = 3


@dataclass(frozen=True)
class ServerRequest:
    method: str
    path: str
    body: Mapping[str, Any] | None = None
    params: Mapping[str, str] | None = None


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
        return "other"
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


def refused_verdict(outcome: Outcome, control_ok: bool | None) -> Verdict:
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
            expect="refused",
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
    for suffix, desc, leak in (
        ("read-ab", "query channel AB", ("{m_a_text}", "{m_b_text}")),
        ("channels", "query channels with an empty filter", ("{AB}", "{XD}")),
        ("users", "query users", ("{A}", "{B}", "{X}", "{D}")),
        ("message", "fetch XD's message by ID", ("{xd_text}",)),
    ):
        for who, token, proc in (
            ("guest", "server-issued guest token", "guest-role"),
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
            control=Control(kind="session", session="X"),
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
                [{"type": "glow.proof", "glow_text": "custom event free text"}],
                channel=ab,
            ),
            control=_replay(body_patch={"event": a_user}),
            phase=30,
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
            action="set a custom field on A's own membership in AB",
            expect="refused",
            step=_call(
                "A",
                "channel",
                "updateMemberPartial",
                [{"set": {"glow_note": "member free text"}}],
                channel=ab,
            ),
            control=_replay(
                keep_params=("user_id",),
                undo=(
                    ServerRequest(
                        "PATCH",
                        "/channels/" + T + "/{AB}/member",
                        {"unset": ["glow_note"]},
                        {"user_id": "{A}"},
                    ),
                ),
            ),
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
            control=Control(kind="custom", note="B connected and watching AB"),
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
            control=Control(kind="custom", note="B connected and watching AB"),
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


def all_cases() -> list[Case]:
    cases = (
        _tokens_and_access()
        + _reading()
        + _realtime()
        + _content()
        + _escalation()
        + _create_join()
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
    return problems
