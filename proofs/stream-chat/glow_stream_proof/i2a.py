"""P06.1-I2a: the cases besides the mechanism families (glow_stream_proof.mechanisms).

* ``TD-expiry``: token expiry and reconnection, on a second device of A.
* ``OUT-send``: the outage, injected inside the process only (DM-04 finding 3).
* ``S15-map``: the S15 mapping: which member fields a member can set, what the
  other member receives, and whether the server can overwrite or clear the data.
* ``F9-pin`` and ``F9-archive``: A's per-member flags, and whether B can read them.
* ``F9-invite-accept`` and ``F9-invite-reject``: an invite answered with a message.
* ``EO-channel``, ``EO-user`` and ``EO-message``: the existence oracle.
* G2's new setup: a guest created server-side that connects by its ID only.

Every server request passes the run's guard. The verdict rules are the README's
("Verdict rules", P06.1-I2a).
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Mapping
from typing import Any

import httpx
from getstream.models import ChannelInput, ChannelMemberRequest

from . import matrix
from . import proof_run as pr
from .app_send import AppSendService
from .client_bridge import ClientSession, Reply
from .configuration import MATCH_TYPE
from .redaction import describe_token
from .server_api import ApiResult, ServerApi
from .stops import RunStopped
from .usage import GuardrailStop

T = MATCH_TYPE
# A mapping records what Stream does; it judges nothing (S15-map).
RECORDED = "RECORDED (a mapping, not a verdict)"
# TD-expiry: the second device's token lives this long, and the case waits this much
# past its expiry before it tries again.
EXPIRY_TTL_SECONDS = 25
EXPIRY_MARGIN_SECONDS = 3
REFUSALS = ("auth", "permission")
# Member fields restored to false when they had no stored value.
BOOLEAN_MEMBER_FIELDS = frozenset(
    {"notifications_muted", "is_moderator", "banned", "shadow_banned", "invited"}
)


# -- helpers ---------------------------------------------------------------------------


def _call(
    run: pr.ProofRun,
    label: str,
    target: str,
    method: str,
    args: list[Any],
    channel: str | None = None,
    max_calls: int = 2,
) -> Reply:
    params: dict[str, Any] = {"target": target, "method": method, "args": args}
    if channel is not None:
        params.update({"type": T, "id": channel})
    return run._send(run.sessions[label], "call", max_calls=max_calls, **params)


def server_member(run: pr.ProofRun, channel_id: str, user_id: str) -> dict[str, Any] | None:
    """The member's stored record, read server-side; ``None`` when absent or unread."""
    result = run.api.get(
        "/api/v2/chat/members",
        params={
            "payload": json.dumps(
                {"type": T, "id": channel_id, "filter_conditions": {}, "limit": 10}
            )
        },
    )
    members = result.body.get("members") if isinstance(result.body, dict) else None
    for member in members if result.ok and isinstance(members, list) else []:
        if isinstance(member, dict) and member.get("user_id") == user_id:
            return member
    return None


def member_value(member: Mapping[str, Any] | None, field: str) -> Any:
    """A member field as stored: a built-in flag's timestamp, or a custom field."""
    if member is None:
        return None
    if field in ("pinned", "archived"):
        return member.get(f"{field}_at")
    if field in member:
        return member[field]
    custom = member.get("custom")
    return custom.get(field) if isinstance(custom, Mapping) else None


def member_entries(obj: Any, user_id: str) -> list[dict[str, Any]]:
    """Every member record for ``user_id`` anywhere in ``obj``."""
    found: list[dict[str, Any]] = []
    if isinstance(obj, Mapping):
        if obj.get("user_id") == user_id:
            found.append(dict(obj))
        for value in obj.values():
            found += member_entries(value, user_id)
    elif isinstance(obj, list):
        for item in obj:
            found += member_entries(item, user_id)
    return found


def channel_has_text(run: pr.ProofRun, cid: str, text: str) -> bool | None:
    """Whether the channel's messages, read server-side, include ``text``."""
    result = run.api.raw(
        "POST",
        "/api/v2/chat/channels",
        body={"filter_conditions": {"cid": cid}, "limit": 1, "message_limit": 100},
    )
    channels = result.body.get("channels") if isinstance(result.body, dict) else None
    if not result.ok or not isinstance(channels, list):
        return None
    return bool(matrix.find_terms(channels, [text]))


def _short(result: ApiResult) -> str:
    return f"{result.status}" + (f" / code {result.code}" if result.code is not None else "")


# -- tokens and devices: expiry and reconnection ------------------------------------------


def token_expiry(run: pr.ProofRun, case: matrix.Case, _arg: str) -> pr.CaseResult:
    """A second device of A with a short-lived token: before and after its expiry, its
    REST read, its open connection and a reconnection; A's first device alongside.

    HOLDS when the expired token's REST read and its reconnection both get an
    authentication or permission error after the same requests succeeded before
    expiry; FAIL when either succeeds after expiry. The open connection's delivery
    after expiry, and the first device's access, are recorded as observations.
    """
    a, ab = run.ctx["A"], run.ctx["AB"]
    token = run.api.user_token(a, EXPIRY_TTL_SECONDS)
    claims = describe_token(token).get("claims") or {}
    exp = claims.get("exp")
    label = "A-expiring"
    # Never a key named like a credential ("token", "*_token"): the redactor hides it.
    detail: dict[str, Any] = {
        "expiry": {
            "lifetime_s": exp - claims["iat"]
            if isinstance(exp, int) and isinstance(claims.get("iat"), int)
            else None
        }
    }
    session = run._session(label, token, max_api_calls=20)
    try:
        connected = pr._ws_answer(run._send(session, "connect", max_calls=3, user={"id": a}))
        watched = pr._http_answer(_call(run, label, "channel", "watch", [], ab))
        before = pr._http_answer(_call(run, label, "channel", "query", [matrix.READ_OPTIONS], ab))
        before_probe = _probe(run, (label, "A"), "before expiry")
        detail["before_expiry"] = {
            "connect": pr._observed(connected),
            "watch": pr._observed(watched),
            "read": pr._observed(before),
            "probe": before_probe,
        }
        run._observe(
            run._result(
                case,
                "REST and WebSocket with a token past its expiry",
                "expiry not reached",
                "the same requests before expiry",
                matrix.Verdict(matrix.INCONCLUSIVE, "the case did not reach the expiry"),
                detail,
            )
        )
        if isinstance(exp, int):
            wait = exp + EXPIRY_MARGIN_SECONDS - time.time()
            if wait > 0:
                time.sleep(wait)
        after = pr._http_answer(_call(run, label, "channel", "query", [matrix.READ_OPTIONS], ab))
        after_probe = _probe(run, (label, "A"), "after expiry")
        first_device = pr._http_answer(
            _call(run, "A", "channel", "query", [matrix.READ_OPTIONS], ab)
        )
        run._send(session, "disconnect", max_calls=2)
        reconnect = pr._ws_answer(run._send(session, "connect", max_calls=3, user={"id": a}))
    finally:
        session.close()
        run.sessions.pop(label, None)
    kept_open = (after_probe.get("received") or {}).get(label)
    detail["after_expiry"] = {
        "read": pr._observed(after),
        "probe": after_probe,
        "reconnect": pr._observed(reconnect),
        "first_device_read": pr._observed(first_device),
        "open_connection_received": kept_open,
    }
    if connected.outcome != "success" or before.outcome != "success":
        verdict = matrix.Verdict(matrix.INCONCLUSIVE, "the controls before expiry did not succeed")
    elif after.outcome == "success" or reconnect.outcome == "success":
        still = [
            n
            for n, x in (("the REST read", after), ("the reconnection", reconnect))
            if x.outcome == "success"
        ]
        verdict = matrix.Verdict(matrix.FAIL, f"{' and '.join(still)} succeeded after expiry")
    elif after.outcome in REFUSALS and reconnect.outcome in REFUSALS:
        verdict = matrix.Verdict(
            matrix.HOLDS,
            "the expired token is refused for the REST read and the reconnection; both "
            "succeeded before expiry",
        )
    else:
        verdict = matrix.Verdict(
            matrix.INCONCLUSIVE,
            f"refusal not attributable (read {after.outcome}, reconnect {reconnect.outcome})",
        )
    return run._result(
        case,
        "REST and WebSocket with a token past its expiry",
        f"after expiry: read {pr._observed(after)}; reconnect {pr._observed(reconnect)}; "
        f"open connection received the probe {kept_open}; first device read "
        f"{pr._observed(first_device)}",
        f"before expiry: connect {pr._observed(connected)}; read {pr._observed(before)}",
        verdict,
        detail,
    )


def _probe(run: pr.ProofRun, labels: tuple[str, ...], phase: str) -> dict[str, Any]:
    """B's message to AB, sent server-side; which of ``labels`` received it."""
    sent = run.send_as(T, run.ctx["AB"], run.ctx["B"], f"{phase} probe {run.prefix}")
    message_id = pr._dig(sent.body, "message.id")
    received: dict[str, Any] = {}
    for n, label in enumerate(labels):
        events = run._events(label, wait_ms=pr.EVENT_WAIT_MS if n == 0 else 200)
        received[label] = any(
            e.get("type") == "message.new" and pr._dig(e, "message.id") == message_id
            for e in events
        )
    return {"received": received}


# -- the outage, injected inside the process ----------------------------------------------


class _Unreachable:
    """An ``httpx`` transport handler that refuses every request with a connection error,
    so the SDK's error path runs and no request leaves the process."""

    def __init__(self) -> None:
        self.attempts: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.attempts.append(f"{request.method} {request.url.path}")
        raise httpx.ConnectError("injected outage: no request leaves the process", request=request)


class _Sender:
    def __init__(self, api: ServerApi) -> None:
        self.api = api
        self.messages: set[str] = set()

    def send_as(self, channel_type: str, channel_id: str, user_id: str, text: str) -> ApiResult:
        return pr.server_send(self.api, self.messages, channel_type, channel_id, user_id, text)


def outage(run: pr.ProofRun, case: matrix.Case, _arg: str) -> pr.CaseResult:
    """The app send path while the provider cannot be reached (DM-04 finding 3).

    HOLDS when the send is refused (the provider's error, no message ID), the match
    state and the run's record are unchanged, a server-side read finds no such
    message, the transport saw exactly the one request, and the same send through
    the reachable provider then succeeds (the control). FAIL when anything of the
    send was kept or the path raised instead of refusing. No address is used.
    """
    unreachable = _Unreachable()
    api = ServerApi(
        run.credentials, run.ledger, run.redactor, transport=httpx.MockTransport(unreachable)
    )
    api.guard = run._guard_refusal
    sender = _Sender(api)
    text = f"outage probe {run.prefix}"
    state_before = run.state.snapshot()
    recorded_before = set(run.messages)
    escaped: str | None = None
    try:
        outcome = AppSendService(run.state, sender, T).send(run.ctx["A"], run.ctx["AB"], text)
    except (GuardrailStop, RunStopped):
        raise
    except Exception as exc:  # the path raised instead of refusing
        outcome = None
        escaped = f"{type(exc).__name__}: {run._text(exc)}"
    finally:
        api.close()
    unchanged = (
        run.state.snapshot() == state_before
        and set(run.messages) == recorded_before
        and not sender.messages
    )
    detail: dict[str, Any] = {
        "injection": "httpx.MockTransport raising httpx.ConnectError; no address is used",
        "transport_attempts": unreachable.attempts,
        "app_send": {
            "decision": outcome.decision.reason if outcome else None,
            "provider_error": outcome.provider_error if outcome else None,
            "message_id": outcome.message_id if outcome else None,
            "raised": escaped,
        },
        "state_unchanged": unchanged,
    }
    run._observe(
        run._result(
            case,
            "app send path, provider unreachable",
            f"provider error {detail['app_send']['provider_error']}",
            "control not completed",
            matrix.Verdict(matrix.INCONCLUSIVE, "the server read and the control were not made"),
            detail,
        )
    )
    found = channel_has_text(run, run.ctx["AB_cid"], text)
    detail["message_found_server_side"] = found
    control = AppSendService(run.state, run, T).send(run.ctx["A"], run.ctx["AB"], text)
    control_desc = f"the same send with the provider reachable: sent {control.sent}"
    if escaped is not None:
        verdict = matrix.Verdict(matrix.FAIL, f"the app send path raised: {escaped}")
    elif outcome is None or outcome.message_id or outcome.sent or not unchanged or found:
        verdict = matrix.Verdict(matrix.FAIL, "the refused send left state behind")
    elif (
        outcome.provider_error
        and len(unreachable.attempts) == 1
        and found is False
        and control.sent
    ):
        verdict = matrix.Verdict(
            matrix.HOLDS,
            "refused with the provider's connection error; nothing kept; the same send "
            "succeeded with the provider reachable",
        )
    else:
        verdict = matrix.Verdict(
            matrix.INCONCLUSIVE,
            f"transport attempts {len(unreachable.attempts)}; message found {found}; "
            f"control sent {control.sent}",
        )
    return run._result(
        case,
        "app send path, provider unreachable",
        f"refused: {detail['app_send']['provider_error']}; state unchanged {unchanged}; "
        f"message found server-side {found}",
        control_desc,
        verdict,
        detail,
    )


# -- the S15 mapping -------------------------------------------------------------------------


def s15_fields(flat: str) -> tuple[tuple[str, Any], ...]:
    return (
        ("glow_note", f"s15map{flat}"),
        ("pinned", True),
        ("archived", True),
        ("notifications_muted", True),
        ("channel_role", "channel_moderator"),
        ("is_moderator", True),
        ("banned", True),
        ("shadow_banned", True),
        ("invited", True),
    )


def _applied(field: str, before: Any, after: Any, value: Any) -> bool:
    if field in ("pinned", "archived"):
        return after is not None and before is None
    return bool(after == value and before != value)


def s15_map(run: pr.ProofRun, case: matrix.Case, _arg: str) -> pr.CaseResult:
    """For each member field: A's own write, what the server stores, what B receives;
    a refused write is replayed by the server (its control); every change is restored.
    Then the server overwrites and clears A's custom data. It records, never judges."""
    a, ab = run.ctx["A"], run.ctx["AB"]
    flat = run.prefix.replace("-", "")
    path = f"/channels/{T}/{ab}/member"
    table: dict[str, Any] = {}
    detail: dict[str, Any] = {"fields": table}
    for field, value in s15_fields(flat):
        run._events("B", wait_ms=0)
        original = server_member(run, ab, a)
        was = member_value(original, field)
        answer = pr._http_answer(
            _call(run, "A", "channel", "updateMemberPartial", [{"set": {field: value}}], ab)
        )
        stored = server_member(run, ab, a)
        applied = _applied(field, was, member_value(stored, field), value)
        entry: dict[str, Any] = {"member_write": pr._observed(answer), "applied": applied}
        if answer.outcome in REFUSALS:
            replay = run.api.raw("PATCH", path, body={"set": {field: value}}, params={"user_id": a})
            entry["server_control"] = _short(replay)
            stored = server_member(run, ab, a)
            entry["applied_by_control"] = _applied(field, was, member_value(stored, field), value)
        events, local = run._events_split("B")
        entry["b_event_types"] = sorted({str(e.get("type")) for e in events})
        entry["b_local_event_types_dropped"] = local
        if field == "glow_note":
            entry["b_events_carry_value"] = bool(matrix.find_terms(events, [str(value)]))
        if applied:
            view = pr._responses(_call(run, "B", "channel", "query", [matrix.READ_OPTIONS], ab))
            shown = [member_value(m, field) for m in member_entries(view, a)]
            entry["b_query_shows_it"] = any(
                v is not None and (field in ("pinned", "archived") or v == value) for v in shown
            )
        if applied or entry.get("applied_by_control"):
            entry["restored"] = _restore_member_field(run, case, ab, a, field, was)
        table[field] = entry
        run._observe(
            run._result(
                case,
                f"PATCH /channels/glow-match/{{AB}}/member ({field})",
                f"mapped {len(table)} fields",
                "-",
                matrix.Verdict(matrix.INCONCLUSIVE, "the mapping did not finish"),
                detail,
            )
        )
    marker = f"serverset{flat}"
    overwrite = run.api.raw(
        "PATCH", path, body={"set": {"glow_note": marker}}, params={"user_id": a}
    )
    after_set = member_value(server_member(run, ab, a), "glow_note")
    clear = run.api.raw("PATCH", path, body={"unset": ["glow_note"]}, params={"user_id": a})
    after_clear = member_value(server_member(run, ab, a), "glow_note")
    detail["server_overwrite"] = {"answer": _short(overwrite), "stored": after_set == marker}
    detail["server_clear"] = {"answer": _short(clear), "absent_after": after_clear is None}
    detail["member_custom_settings_read_live"] = {
        k: v for k, v in run.settings.items() if k.startswith("member_custom_on_")
    }
    settable = [f for f, e in table.items() if e["applied"]]
    refused = [f for f, e in table.items() if e["member_write"].split(" ")[0] in ("401", "403")]
    ignored = [f for f in table if f not in settable and f not in refused]
    return run._result(
        case,
        "PATCH /channels/glow-match/{AB}/member (A's own membership)",
        f"A set {settable or 'none'}; refused {refused or 'none'}; accepted but not stored "
        f"{ignored or 'none'}",
        f"server overwrite stored {detail['server_overwrite']['stored']}; server clear "
        f"removed it {detail['server_clear']['absent_after']}",
        matrix.Verdict(RECORDED, "the S15 mapping; see the detail"),
        detail,
    )


def _restore_member_field(
    run: pr.ProofRun, case: matrix.Case, channel_id: str, user_id: str, field: str, was: Any
) -> str:
    """Put a member field back and verify it; a restore that fails stops the run after
    this case (it acts on the run's own member of the run's own channel)."""
    path = f"/channels/{T}/{channel_id}/member"
    if field in ("pinned", "archived") or (was is None and field in BOOLEAN_MEMBER_FIELDS):
        body: dict[str, Any] = {"set": {field: False}}
    elif was is None:
        body = {"unset": [field]}
    else:
        body = {"set": {field: was}}
    done = run.api.raw("PATCH", path, body=body, params={"user_id": user_id})
    now = member_value(server_member(run, channel_id, user_id), field)
    if field in ("pinned", "archived"):
        back = now is None
    elif was is None:
        back = now in (None, False)
    else:
        back = now == was
    restored = done.ok and back
    if not restored:
        run._defer_stop(
            f"{case.id}: A's member field {field} was not restored: PATCH {_short(done)}; "
            f"stored {now!r}"
        )
    return f"{_short(done)}; verified {restored}"


# -- F9: A's own pinned and archived flags -------------------------------------------------


def own_member_flag(run: pr.ProofRun, case: matrix.Case, flag: str) -> pr.CaseResult:
    """A pins or archives AB for itself; can B read it?

    FAIL when B's channel read or events show A's flag; HOLDS (filtered) when A's
    write is stored and B's reads and events do not show it; HOLDS (accepted, not
    applied) when the write is accepted but not stored; on an authentication or
    permission refusal, HOLDS when the server's replay of the same request succeeds.
    """
    a, ab = run.ctx["A"], run.ctx["AB"]
    run._events("B", wait_ms=0)
    was = member_value(server_member(run, ab, a), flag)
    reply = _call(run, "A", "channel", "pin" if flag == "pinned" else "archive", [], ab)
    answer = pr._http_answer(reply)
    stored = member_value(server_member(run, ab, a), flag)
    applied = stored is not None and was is None
    view = pr._responses(_call(run, "B", "channel", "query", [matrix.READ_OPTIONS], ab))
    events, local = run._events_split("B")
    leaks = []
    if any(member_value(m, flag) for m in member_entries(view, a)):
        leaks.append("B's channel query")
    carriers = sorted(
        {
            str(e.get("type"))
            for e in events
            if any(member_value(m, flag) for m in member_entries(e, a))
        }
    )
    if carriers:
        leaks.append(f"B's events ({', '.join(carriers)})")
    detail: dict[str, Any] = {
        "stored": applied,
        "b_event_types": sorted({str(e.get("type")) for e in events}),
        "b_local_event_types_dropped": local,
    }
    control = "-"
    control_ok = False
    if answer.outcome in REFUSALS and answer.record is not None:
        replay = run.api.raw(
            "PATCH",
            "/" + str(answer.record.get("path")).lstrip("/"),
            body=answer.record.get("body"),
        )
        control_ok = replay.ok
        control = f"server replay PATCH -> {_short(replay)}"
        applied = applied or member_value(server_member(run, ab, a), flag) is not None
    if applied:
        detail["restored"] = _restore_member_field(run, case, ab, a, flag, None)
    if leaks:
        verdict = matrix.Verdict(matrix.FAIL, f"B reads that A {flag} AB: {', '.join(leaks)}")
    elif answer.outcome == "success" and detail["stored"]:
        verdict = matrix.Verdict(
            matrix.HOLDS_FILTERED, "stored for A; B's channel read and events do not show it"
        )
    elif answer.outcome == "success":
        verdict = matrix.Verdict(matrix.HOLDS_IGNORED, "accepted; not stored")
    else:
        verdict = matrix.refused_verdict(answer.outcome, control_ok)
    return run._result(
        case,
        pr._request_line(answer.record, run.ctx),
        pr._observed(answer),
        control,
        verdict,
        detail,
    )


# -- F9: invites answered with a message ----------------------------------------------------


def invite(run: pr.ProofRun, case: matrix.Case, kind: str) -> pr.CaseResult:
    """B, invited to a channel of A's, accepts or rejects the invite with a message.

    FAIL when B's request succeeds, or its text reaches A; on an authentication or
    permission refusal, HOLDS when the server's replay of the same request succeeds.
    """
    a, b = run.ctx["A"], run.ctx["B"]
    channel = f"{run.prefix}-ch-in-{kind}"
    run.ctx[f"CH_in_{kind}"] = channel
    run.ledger.reserve("channels")
    run.channels.append(f"{T}:{channel}")
    run.api.sdk.chat.get_or_create_channel(
        type=T,
        id=channel,
        data=ChannelInput(
            created_by_id=a,
            members=[ChannelMemberRequest(user_id=a)],
            invites=[ChannelMemberRequest(user_id=b)],
        ),
    )
    watch = pr._http_answer(_call(run, "A", "channel", "watch", [], channel))
    run._events("A", wait_ms=0)
    text = f"invite {kind} text {run.prefix}"
    method = "acceptInvite" if kind == "accept" else "rejectInvite"
    answer = pr._http_answer(
        _call(run, "B", "channel", method, [{"message": {"text": text}}], channel)
    )
    events, _ = run._events_split("A")
    reached = sorted({str(e.get("type")) for e in events if matrix.find_terms(e, [text])})
    stored = channel_has_text(run, f"{T}:{channel}", text)
    detail: dict[str, Any] = {
        "a_watch": pr._observed(watch),
        "a_event_types": sorted({str(e.get("type")) for e in events}),
        "text_reached_a_in": reached,
        "text_stored": stored,
    }
    run._observe(
        run._result(
            case,
            pr._request_line(answer.record, run.ctx),
            pr._observed(answer),
            "control not completed",
            matrix.Verdict(matrix.FAIL, f"B's {kind} succeeded")
            if answer.outcome == "success"
            else matrix.Verdict(matrix.INCONCLUSIVE, "the control was not completed"),
            detail,
        )
    )
    control_ok = False
    control = "-"
    if answer.outcome in REFUSALS and answer.record is not None:
        body = matrix.deep_merge(
            answer.record.get("body"), {"user_id": b, "message": {"user_id": b}}
        )
        replay = run.api.raw("POST", "/" + str(answer.record.get("path")).lstrip("/"), body=body)
        control_ok = replay.ok
        control = f"server replay POST -> {_short(replay)}"
    if answer.outcome == "success" or reached or stored:
        # Read before the control's replay, so only B's own request can have done it.
        why = [f"B's {kind} with a message succeeded"] if answer.outcome == "success" else []
        if reached:
            why.append(f"the text reached A in {', '.join(reached)}")
        if stored:
            why.append("the text is stored in the channel")
        verdict = matrix.Verdict(matrix.FAIL, "; ".join(why))
    else:
        verdict = matrix.refused_verdict(answer.outcome, control_ok)
    return run._result(
        case,
        pr._request_line(answer.record, run.ctx),
        pr._observed(answer),
        control,
        verdict,
        detail,
    )


# -- the existence oracle ------------------------------------------------------------------


def _normal(answer: pr.Answer, ids: tuple[str, ...]) -> tuple[Any, ...]:
    """What a client can tell from an answer: status, code and message, IDs replaced."""
    response = answer.record.get("response") if answer.record else None
    message = response.get("message") if isinstance(response, dict) else None
    text = str(message or "")
    for identifier in ids:
        text = text.replace(identifier, "{id}")
    if answer.outcome == "success" and isinstance(response, dict):
        # Two successes differ when they return different amounts of data.
        text = f"keys {sorted(response)}; size {len(json.dumps(response))}"
    return answer.status, answer.code, text


def oracle(run: pr.ProofRun, case: matrix.Case, kind: str) -> pr.CaseResult:
    """A's refusal for an existing ID against its refusal for one that does not exist.

    FAIL (an existence oracle) when any pair's status, code or message (with the IDs
    replaced) differs; HOLDS when every pair is identical and the control shows the
    existing ID exists; INCONCLUSIVE otherwise.
    """
    none = f"{run.prefix}-none"
    pairs: list[tuple[str, pr.Answer, pr.Answer]] = []
    undo: list[str] = []
    if kind == "channel":
        existing, missing = run.ctx["XD"], f"{none}-channel"
        for name, method in (("query", "query"), ("watch", "watch")):
            args = [matrix.READ_OPTIONS] if method == "query" else []
            pairs.append(
                (
                    name,
                    pr._http_answer(_call(run, "A", "channel", method, args, existing)),
                    pr._http_answer(_call(run, "A", "channel", method, args, missing)),
                )
            )
        pairs.append(
            (
                "GET channel",
                pr._http_answer(
                    run._send(
                        run.sessions["A"], "get", max_calls=1, path=f"/channels/{T}/{existing}"
                    )
                ),
                pr._http_answer(
                    run._send(
                        run.sessions["A"], "get", max_calls=1, path=f"/channels/{T}/{missing}"
                    )
                ),
            )
        )
        control = pr._http_answer(
            _call(run, "X", "channel", "query", [matrix.READ_OPTIONS], existing)
        )
        created = channel_has_text(run, f"{T}:{missing}", missing)
        if created:
            # A request above created it: counted and recorded, so cleanup deletes it.
            run.ledger.reserve("channels")
            run.channels.append(f"{T}:{missing}")
            undo.append("the missing channel was created and is deleted at cleanup")
        ids: tuple[str, ...] = (existing, missing)
    elif kind == "user":
        existing, missing = run.ctx["X"], f"{none}-user"
        pairs.append(
            (
                "queryUsers",
                pr._http_answer(
                    _call(run, "A", "client", "queryUsers", [{"id": {"$eq": existing}}])
                ),
                pr._http_answer(
                    _call(run, "A", "client", "queryUsers", [{"id": {"$eq": missing}}])
                ),
            )
        )
        added = pr._http_answer(
            _call(run, "A", "channel", "addMembers", [[existing]], run.ctx["AB"])
        )
        if added.outcome == "success":
            done = run.api.raw(
                "POST", f"/channels/{T}/{run.ctx['AB']}", body={"remove_members": [existing]}
            )
            undo.append(f"X was added to AB; removed again ({_short(done)})")
        pairs.append(
            (
                "addMembers",
                added,
                pr._http_answer(
                    _call(run, "A", "channel", "addMembers", [[missing]], run.ctx["AB"])
                ),
            )
        )
        try:
            control_user = run._server_user(existing)
        except (GuardrailStop, RunStopped):
            raise
        except Exception:  # Stream did not answer the listing with 2xx
            control_user = None
        control = pr.Answer("success" if control_user else "no-response", None, None, None)
        ids = (existing, missing)
    else:
        existing, missing = run.ctx["m_x"], f"{none}-message"
        pairs.append(
            (
                "getMessage",
                pr._http_answer(_call(run, "A", "client", "getMessage", [existing])),
                pr._http_answer(_call(run, "A", "client", "getMessage", [missing])),
            )
        )
        control = pr._http_answer(_call(run, "X", "client", "getMessage", [existing]))
        ids = (existing, missing)
    compared: dict[str, Any] = {}
    differ: list[str] = []
    for name, found, absent in pairs:
        same = _normal(found, ids) == _normal(absent, ids)
        compared[name] = {
            "existing": pr._observed(found),
            "missing": pr._observed(absent),
            "identical": same,
        }
        if not same:
            differ.append(f"{name}: existing {pr._observed(found)}, missing {pr._observed(absent)}")
    answered = all(f.outcome != "no-response" and m.outcome != "no-response" for _, f, m in pairs)
    if differ:
        verdict = matrix.Verdict(matrix.FAIL, "an existence oracle: " + "; ".join(differ))
    elif answered and control.outcome == "success":
        verdict = matrix.Verdict(
            matrix.HOLDS, "the answers for an existing and a missing ID are identical"
        )
    else:
        verdict = matrix.Verdict(
            matrix.INCONCLUSIVE, "a request had no answer, or the control did not succeed"
        )
    detail = {"pairs": compared, "undo": undo or None}
    return run._result(
        case,
        ", ".join(name for name, _, _ in pairs),
        "; ".join(
            f"{n}: {'identical' if c['identical'] else 'differ'}" for n, c in compared.items()
        ),
        f"the existing ID exists: {pr._observed(control)}",
        verdict,
        json.loads(pr._generic(json.dumps(detail), run.ctx)),
    )


# -- G2's new setup ---------------------------------------------------------------------------


def g2_session(run: pr.ProofRun) -> tuple[ClientSession | None, dict[str, Any]]:
    """A guest created server-side, connected with its ID only (the I1 review's finding 6).

    If the application refuses to create it while guest creation is disabled, the
    setting is enabled for the moment of the creation, journalled, and disabled again
    and verified, as G1's control does.
    """
    requested = f"{run.prefix}-g2"
    note: dict[str, Any] = {"requested_id": "{prefix}-g2"}
    run.ledger.reserve("users")
    created, token = run.api.create_guest({"id": requested})
    note["server_create"] = _short(created)
    if created.status == 403:
        change = run._guest_creation_change()
        with run._temporary(change):
            on = run._set_guest_creation_disabled(False)
            time.sleep(pr.TYPE_CHANGE_SETTLE_SECONDS)
            created, token = run.api.create_guest({"id": requested})
        note["with_guest_creation_enabled"] = {
            "enable": _short(on),
            "server_create": _short(created),
            "restored": change.note,
        }
    stored = pr._dig(created.body, "user.id")
    if not created.ok or not isinstance(stored, str) or token is None:
        run.ledger.release("users")
        note["result"] = "no guest was created"
        return None, note
    run.users.append(stored)
    run.ctx["g2_id"] = stored
    # The form Stream stored it in: its own prefix, then the requested ID.
    head = stored[: -len(requested)] if stored.endswith(requested) else None
    if head is None:
        note["stored_form"] = "not the requested ID with a prefix"
    elif re.fullmatch(r"guest-[0-9a-fA-F-]+-", head):
        note["stored_form"] = "guest-<id>-{prefix}-g2"
    else:
        note["stored_form"] = f"{head}{{prefix}}-g2"
    note["role"] = pr._dig(created.body, "user.role")
    session = run._session("g2", token, max_api_calls=30)
    reply = run._send(session, "connect", max_calls=3, user={"id": stored})
    run.connect_replies["g2"] = reply
    connected = pr._ws_answer(reply)
    note["connect"] = pr._observed(connected)
    note["connected_role"] = ((reply.data or {}).get("me") or {}).get("role") if reply.ok else None
    if connected.outcome != "success":
        session.close()
        run.sessions.pop("g2", None)
        return None, note
    return session, note
