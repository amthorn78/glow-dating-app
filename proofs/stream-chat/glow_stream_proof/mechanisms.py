"""P06.1-I2a: revocation mechanisms, suspension and deletion, one case each.

Nathan's history policy (OD-12): after an unmatch or block, neither person can
send or see the conversation, and the history is kept out of sight only for
safety reports. Each mechanism is one case (the brief's I2a; DM-02 B2; DM-04
finding 6), on a channel of its own:

* channel-level, each on its own channel, with the same pair of synthetic users:
  member removal (``remove``), a channel ban (``ban``), hiding (``hide``) and
  freezing (``freeze``). The mechanism acts on M1; M2 is the other member.
* account-level, each with a user of its own: the per-user
  ``revoke_tokens_issued_before`` (``revoke``, on R, with two devices),
  deactivation (``deactivate``, on S: Stream's documented way to stop a user's
  requests and connections while keeping its data) and a hard user delete
  (``delete``, on H). M2 is the other member.

Every mechanism is applied by the server, through the run's guard. For each
member, four things are recorded before and after it, by the same member:

* ``rest``: a read of the channel over REST by the member's existing session;
* ``ws``: whether the member's already-open WebSocket subscription receives the
  channel's events: a server-side channel update and a message from the other
  member, collected in one window;
* ``token_reuse``: a new session with the member's existing token connects and
  reads the channel;
* ``s15``: the member's own ``updateMemberPartial`` write.

A dimension is ``ended`` only on Stream's authentication or permission error,
recorded by status and code, after the same request by the same member succeeded
before the mechanism (the matrix quality rule), and ``not ended`` when it still
succeeds. The subscription is ``ended`` only when the member's open connection
received none of the probe's events while a listener (the other member, when it
is still entitled) received them in the same window. Anything else is ``not
shown``.

Also recorded: the event types each member receives when the mechanism is applied
(the SDK's local events excluded), any system message the provider adds, where
the acting user appears in them, whether the channel's messages are retained
(a server-side read), the app send path's refusal without a Stream call, Stream's
answer to a server-side send on the affected member's behalf (an observation, not
a verdict: server-side calls bypass Stream's permission checks), and, for the
channel-level mechanisms, whether the affected member's own client can undo it
(the same request replayed by the server is its control).

The verdict (README, "Verdict rules"): MEETS the history policy when every
dimension is ended for the member it is applied to (for a freeze, both members),
its client cannot undo it and the messages are retained; DOES NOT MEET it when a
dimension is not ended, the client undid it or the messages are gone; otherwise
INCONCLUSIVE, naming what was not shown.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from getstream.models import ChannelInput, ChannelMemberRequest, UserRequest

from . import matrix
from . import proof_run as pr
from .app_send import AppSendService
from .client_bridge import ClientSession, ClientSessionEnded, Reply
from .configuration import MATCH_TYPE
from .redaction import describe_token

T = MATCH_TYPE

ENDED = "ended"
NOT_ENDED = "not ended"
NOT_SHOWN = "not shown"

MEETS = "MEETS the history policy"
FALLS_SHORT = "DOES NOT MEET the history policy"

DIMENSIONS = ("rest", "ws", "token_reuse", "s15")
OTHER = "M2"
# The session labels the families use; the I1 sessions are the others.
FAMILY_LABELS = ("M1", "M2", "R", "S", "H")
# A token issued within this many seconds after a per-user revocation time is
# refused by design: the server SDK back-dates ``iat`` by 5 s (DM-04 finding 9(b)).
IAT_BACKDATE_SECONDS = 5
# How long after the revocation time the harness waits before it issues the token
# that must be accepted: past the back-dating, with a second to spare.
REVOKE_REISSUE_AFTER_SECONDS = IAT_BACKDATE_SECONDS + 2
DELETE_TASK_POLLS = 30


@dataclass(frozen=True)
class Mechanism:
    key: str
    scope: Literal["channel", "account"]
    affected: str
    # The affected member's own client request that would undo it, if any.
    undo: str | None = None
    # How many client sessions (devices) the affected member has.
    devices: int = 1
    # Whether the mechanism acts on every member of its channel (a freeze).
    both: bool = False
    # Whether the server names the other member as the acting user.
    actor: bool = False


MECHANISMS: dict[str, Mechanism] = {
    "remove": Mechanism("remove", "channel", "M1", undo="rejoin", actor=True),
    "ban": Mechanism("ban", "channel", "M1", undo="unban", actor=True),
    "hide": Mechanism("hide", "channel", "M1", undo="show"),
    "freeze": Mechanism("freeze", "channel", "M1", undo="unfreeze", both=True, actor=True),
    "revoke": Mechanism("revoke", "account", "R", devices=2),
    "deactivate": Mechanism("deactivate", "account", "S"),
    "delete": Mechanism("delete", "account", "H"),
}


# -- the rules (pure functions, tested offline) ---------------------------------------


def dimension(before: pr.Answer | None, after: pr.Answer | None) -> dict[str, str]:
    """``ended`` only on an authentication or permission refusal after the same
    request by the same member succeeded before the mechanism."""
    if before is None or before.outcome != "success":
        shown = pr._observed(before) if before is not None else "not made"
        return {"status": NOT_SHOWN, "why": f"no successful control before ({shown})"}
    if after is None:
        return {"status": NOT_SHOWN, "why": "not made after the mechanism"}
    if after.outcome in ("auth", "permission"):
        return {"status": ENDED, "why": pr._observed(after)}
    if after.outcome == "success":
        return {"status": NOT_ENDED, "why": pr._observed(after)}
    return {
        "status": NOT_SHOWN,
        "why": f"refusal not attributable ({after.outcome}): {pr._observed(after)}",
    }


def ws_dimension(
    before: bool | None, after: bool | None, listener: bool | None, accepted: bool
) -> dict[str, str]:
    """``ended`` only when the open connection received no probe event after the
    mechanism while a listener received one in the same window."""
    if not before:
        return {"status": NOT_SHOWN, "why": "the open connection missed the probe before"}
    if after:
        return {"status": NOT_ENDED, "why": "the open connection still received the probe"}
    if after is None:
        return {"status": NOT_SHOWN, "why": "the events could not be collected"}
    if not accepted:
        return {"status": NOT_SHOWN, "why": "no probe was accepted after the mechanism"}
    if not listener:
        return {"status": NOT_SHOWN, "why": "no listener received the probe after the mechanism"}
    return {"status": ENDED, "why": "no probe event arrived; the listener received it"}


def token_dimension(
    control_connect: pr.Answer | None,
    control_query: pr.Answer | None,
    connect: pr.Answer | None,
    query: pr.Answer | None,
) -> dict[str, str]:
    """A new session with the member's existing token: ``ended`` when its connect,
    or its read of the channel, gets an authentication or permission refusal after
    the member's own connect and read succeeded before the mechanism."""
    controls = (control_connect, control_query)
    if any(c is None or c.outcome != "success" for c in controls):
        return {"status": NOT_SHOWN, "why": "no successful connect and read before"}
    if connect is None:
        return {"status": NOT_SHOWN, "why": "not made after the mechanism"}
    if connect.outcome in ("auth", "permission"):
        return {"status": ENDED, "why": f"connect {pr._observed(connect)}"}
    if connect.outcome != "success":
        return {"status": NOT_SHOWN, "why": f"connect {pr._observed(connect)}"}
    if query is None:
        return {"status": NOT_SHOWN, "why": "connected; the read was not made"}
    if query.outcome in ("auth", "permission"):
        return {"status": ENDED, "why": f"connected; read {pr._observed(query)}"}
    if query.outcome == "success":
        return {"status": NOT_ENDED, "why": f"connected; read {pr._observed(query)}"}
    return {"status": NOT_SHOWN, "why": f"connected; read {pr._observed(query)}"}


def policy_verdict(
    judged: Mapping[str, Mapping[str, Mapping[str, str]]],
    undo: matrix.Verdict | None,
    retained: bool | None,
) -> matrix.Verdict:
    """The mechanism against the history policy, for the members it acts on.

    ``judged`` maps each judged member (its session label) to its dimensions;
    ``undo`` is the verdict of the member's own attempt to undo it (``None`` when
    the mechanism has no client undo); ``retained`` whether the server still holds
    the channel's messages (``None`` when that could not be read).
    """
    not_ended = [
        f"{dim} for {label}"
        for label, dims in judged.items()
        for dim in DIMENSIONS
        if dims.get(dim, {}).get("status") == NOT_ENDED
    ]
    not_shown = [
        f"{dim} for {label}"
        for label, dims in judged.items()
        for dim in DIMENSIONS
        if dims.get(dim, {}).get("status") not in (ENDED, NOT_ENDED)
    ]
    reasons: list[str] = []
    if not_ended:
        reasons.append("does not end " + ", ".join(not_ended))
    if undo is not None and undo.label == matrix.FAIL:
        reasons.append("the member's own client undid it")
    if retained is False:
        reasons.append("the channel's messages are not retained")
    if reasons:
        return matrix.Verdict(FALLS_SHORT, "; ".join(reasons))
    gaps = list(not_shown)
    if undo is not None and undo.label != matrix.HOLDS:
        gaps.append(f"the client's undo ({undo.label})")
    if retained is None:
        gaps.append("retention")
    if gaps:
        return matrix.Verdict(matrix.INCONCLUSIVE, "not shown: " + ", ".join(gaps))
    ends = "ends REST reads, the open subscription, token reuse and the S15 write"
    undo_text = "; its client cannot undo it" if undo is not None else ""
    return matrix.Verdict(MEETS, f"{ends}{undo_text}; the messages are retained")


def value_paths(obj: Any, needles: Mapping[str, str], path: str = "") -> list[str]:
    """Where each needle (an identifier or name) appears in ``obj``, as ``path=name``."""
    found: list[str] = []
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            found += value_paths(value, needles, f"{path}.{key}" if path else str(key))
    elif isinstance(obj, list):
        for item in obj:
            found += value_paths(item, needles, f"{path}[]")
    elif isinstance(obj, str):
        found += [f"{path}={name}" for needle, name in needles.items() if needle and needle in obj]
    return sorted(set(found))


# Lists that name every member or watcher of a channel: a path under one of them
# does not name who acted.
_LIST_PARTS = ("members[]", "watchers[]", "read[]")


def actor_paths(paths: list[str]) -> list[str]:
    return [p for p in paths if not any(part in p for part in _LIST_PARTS)]


# -- users, channels and sessions --------------------------------------------------------


def user_id(run: pr.ProofRun, key: str) -> str:
    return f"{run.prefix}-u{key.lower()}"


def ensure_user(run: pr.ProofRun, key: str) -> str:
    """Create synthetic user ``key`` once per run, with a token; return its ID."""
    uid = user_id(run, key)
    if key in run._tokens:
        return uid
    run.ctx[key] = uid
    run.ctx[f"{key}_name"] = f"Synthetic {key} {run.prefix[-6:]}"
    run.ledger.reserve("users")
    run.users.append(uid)  # recorded before the request, so cleanup deletes it
    run.api.sdk.upsert_users(UserRequest(id=uid, name=run.ctx[f"{key}_name"], role="user"))
    token = run.api.user_token(uid, pr.TOKEN_TTL_SECONDS)
    run._tokens[key] = token
    run.token_claims[key] = describe_token(token)
    return uid


def create_channel(run: pr.ProofRun, channel_id: str, members: list[str], owner: str) -> None:
    run.ledger.reserve("channels")
    run.channels.append(f"{T}:{channel_id}")  # recorded before the request
    run.api.sdk.chat.get_or_create_channel(
        type=T,
        id=channel_id,
        data=ChannelInput(
            created_by_id=owner,
            members=[ChannelMemberRequest(user_id=m) for m in members],
        ),
    )


def ensure_session(run: pr.ProofRun, label: str, key: str, token: str) -> ClientSession:
    """The client session ``label`` for user ``key``, connected; one per label per run."""
    session = run.sessions.get(label)
    if session is not None and getattr(session, "ended", None) is None:
        return session
    session = run._session(label, token)
    run.connect_replies[label] = run._send(
        session, "connect", max_calls=3, user={"id": run.ctx[key]}
    )
    return session


def close_session(run: pr.ProofRun, label: str) -> None:
    session = run.sessions.pop(label, None)
    if session is not None:
        session.close()


# -- one mechanism -------------------------------------------------------------------------


def run_mechanism(run: pr.ProofRun, case: matrix.Case, key: str) -> pr.CaseResult:
    return Family(run, case, MECHANISMS[key]).execute()


class Family:
    """One mechanism on its own channel: setup, before, apply, after, undo, verdict."""

    def __init__(self, run: pr.ProofRun, case: matrix.Case, mech: Mechanism) -> None:
        self.run = run
        self.case = case
        self.mech = mech
        self.flat = run.prefix.replace("-", "")
        self.channel = f"{run.prefix}-ch-{mech.key}"
        self.cid = f"{T}:{self.channel}"
        self.affected = mech.affected
        self.labels = [mech.affected]
        if mech.devices == 2:
            self.labels.append(f"{mech.affected}-2")
        self.labels.append(OTHER)
        self.tokens: dict[str, str] = {}
        self.history_text = f"history {mech.key} {run.prefix}"
        self.history_id: str | None = None
        self.affected_history_id: str | None = None
        self.before: dict[str, dict[str, Any]] = {label: {} for label in self.labels}
        self.after: dict[str, dict[str, Any]] = {label: {} for label in self.labels}
        self.table: dict[str, dict[str, dict[str, str]]] = {}
        self.detail: dict[str, Any] = {"mechanism": mech.key, "scope": mech.scope}
        self.request = "-"
        self.undo_verdict: matrix.Verdict | None = None
        self.retained: bool | None = None
        # The family's own sessions (not the shared M1 and M2), closed at its end.
        self.own_sessions: list[str] = []
        self.revoked_at = 0
        self.message_ids_before: set[str] = set()

    # -- helpers --

    def member(self, label: str) -> str:
        return label.split("-", 1)[0]

    def uid(self, label: str) -> str:
        return self.run.ctx[self.member(label)]

    def generic(self, text: str) -> str:
        return pr._generic(text, self.run.ctx)

    def call(self, label: str, method: str, args: list[Any], max_calls: int = 2) -> Reply:
        session = self.run.sessions[label]
        return self.run._send(
            session,
            "call",
            max_calls=max_calls,
            target="channel",
            method=method,
            args=args,
            type=T,
            id=self.channel,
        )

    def query(self, label: str) -> tuple[pr.Answer, bool]:
        reply = self.call(label, "query", [matrix.READ_OPTIONS])
        sees = bool(matrix.find_terms(pr._responses(reply), [self.history_text]))
        return pr._http_answer(reply), sees

    def s15_write(self, label: str, phase: str) -> pr.Answer:
        marker = f"{phase}note{self.flat}{self.mech.key}"
        return pr._http_answer(
            self.call(label, "updateMemberPartial", [{"set": {"glow_note": marker}}])
        )

    def observe(self, verdict: matrix.Verdict, observed: str) -> pr.CaseResult:
        return self.run._observe(
            self.run._result(
                self.case,
                self.request,
                observed,
                "the same requests by the same members before the mechanism",
                verdict,
                self.snapshot(),
            )
        )

    def snapshot(self) -> dict[str, Any]:
        copied: dict[str, Any] = json.loads(
            json.dumps({**self.detail, "table": self.table}, default=str)
        )
        return copied

    def events(self, wait_ms: int) -> dict[str, dict[str, Any]]:
        """Each session's events since the last collection: those for this channel (or
        for no channel), the SDK's local event types, and whether the connection closed."""
        out: dict[str, dict[str, Any]] = {}
        first = True
        for label in self.labels:
            session = self.run.sessions.get(label)
            if session is None:
                out[label] = {"collected": False}
                continue
            reply = self.run._send(
                session, "events", max_calls=0, wait_ms=wait_ms if first else 200
            )
            first = False
            raw = [e for e in (reply.data or {}).get("events") or [] if isinstance(e, dict)]
            local = [e for e in raw if e.get("type") in matrix.LOCAL_EVENT_TYPES]
            delivered = [
                e
                for e in raw
                if e.get("type") not in matrix.LOCAL_EVENT_TYPES
                and e.get("cid") in (self.cid, None)
            ]
            out[label] = {
                "collected": True,
                "events": delivered,
                "types": sorted({str(e.get("type")) for e in delivered}),
                "local_types": sorted({str(e.get("type")) for e in local}),
                "connection_closed": any(
                    e.get("type") == "connection.changed" and e.get("online") is False
                    for e in local
                ),
                "other_channels": sum(
                    1
                    for e in raw
                    if e.get("type") not in matrix.LOCAL_EVENT_TYPES
                    and e.get("cid") not in (self.cid, None)
                ),
            }
        return out

    def probes(self, phase: str) -> dict[str, Any]:
        """A server-side channel update and a message from the other member, then one
        window: which sessions received either."""
        marker = f"{phase}probe{self.flat}{self.mech.key}"
        update = self.run.api.raw(
            "PATCH", f"/channels/{T}/{self.channel}", body={"set": {"glow_probe": marker}}
        )
        text = f"{phase} probe {self.mech.key} {self.run.prefix}"
        sent = self.run.api.raw(
            "POST",
            f"/channels/{T}/{self.channel}/message",
            body={"message": {"text": text, "user_id": self.run.ctx[OTHER]}},
        )
        message_id = pr._dig(sent.body, "message.id") if sent.ok else None
        if isinstance(message_id, str):
            self.run.messages.add(message_id)
        seen = self.events(pr.EVENT_WAIT_MS)
        received: dict[str, Any] = {}
        for label, got in seen.items():
            if not got.get("collected"):
                received[label] = None
                continue
            events = got["events"]
            received[label] = {
                "channel_update": any(
                    e.get("type") == "channel.updated" and matrix.find_terms(e, [marker])
                    for e in events
                ),
                "message": message_id is not None
                and any(
                    e.get("type") == "message.new" and pr._dig(e, "message.id") == message_id
                    for e in events
                ),
                "types": got["types"],
                "local_types": got["local_types"],
                "connection_closed": got["connection_closed"],
            }
        return {
            "update": f"{update.status}" + (f" / code {update.code}" if update.code else ""),
            "message": f"{sent.status}" + (f" / code {sent.code}" if sent.code else ""),
            "accepted": update.ok or sent.ok,
            "received": received,
        }

    @staticmethod
    def got_probe(received: Any) -> bool | None:
        if not isinstance(received, Mapping):
            return None
        return bool(received.get("channel_update") or received.get("message"))

    def server_channel(self) -> tuple[bool | None, list[dict[str, Any]], list[dict[str, Any]]]:
        """Whether the channel exists, its messages and its members, read server-side;
        ``None`` when Stream did not answer the read with 2xx."""
        result = self.run.api.raw(
            "POST",
            "/api/v2/chat/channels",
            body={"filter_conditions": {"cid": self.cid}, "limit": 1, "message_limit": 100},
        )
        channels = result.body.get("channels") if isinstance(result.body, dict) else None
        if not result.ok or not isinstance(channels, list):
            return None, [], []
        if not channels or not isinstance(channels[0], dict):
            return False, [], []
        messages = [m for m in channels[0].get("messages") or [] if isinstance(m, dict)]
        members = [m for m in channels[0].get("members") or [] if isinstance(m, dict)]
        return True, messages, members

    def server_members(self) -> list[dict[str, Any]] | None:
        result = self.run.api.get(
            "/api/v2/chat/members",
            params={
                "payload": json.dumps(
                    {"type": T, "id": self.channel, "filter_conditions": {}, "limit": 10}
                )
            },
        )
        members = result.body.get("members") if isinstance(result.body, dict) else None
        if not result.ok or not isinstance(members, list):
            return None
        return [m for m in members if isinstance(m, dict)]

    def member_note(self, members: list[dict[str, Any]] | None, label: str) -> Any:
        """The member's stored ``glow_note``: its value, "absent", "not a member" or "not read"."""
        if members is None:
            return "not read"
        for m in members:
            if m.get("user_id") == self.uid(label):
                note = m.get("glow_note", (m.get("custom") or {}).get("glow_note"))
                return self.generic(str(note)) if note is not None else "absent"
        return "not a member"

    # -- the steps --

    def execute(self) -> pr.CaseResult:
        try:
            self.setup()
            self.observe(matrix.Verdict(matrix.INCONCLUSIVE, "set up; not yet applied"), "set up")
            self.collect_before()
            self.observe(
                matrix.Verdict(matrix.INCONCLUSIVE, "controls made; not yet applied"),
                "controls made",
            )
            if not self.apply():
                answer = self.detail["apply"]["answer"]
                return self.observe(
                    matrix.Verdict(
                        matrix.INCONCLUSIVE, f"Stream did not apply the mechanism ({answer})"
                    ),
                    f"not applied: {answer}",
                )
            self.observe(
                matrix.Verdict(matrix.INCONCLUSIVE, "applied; nothing observed after it yet"),
                f"applied: {self.detail['apply']['answer']}",
            )
            self.collect_after()
            self.judge_dimensions()
            self.observe(
                matrix.Verdict(matrix.INCONCLUSIVE, "observed; retention and undo not yet made"),
                self.summary(),
            )
            self.send_checks()
            self.retention()
            if self.mech.undo is not None:
                self.undo()
            verdict = self.verdict()
            return self.observe(verdict, self.summary())
        finally:
            for label in self.own_sessions:
                close_session(self.run, label)

    def setup(self) -> None:
        run, mech = self.run, self.mech
        affected_id = ensure_user(run, mech.affected)
        other_id = ensure_user(run, OTHER)
        run.ctx[f"CH_{mech.key}"] = self.channel
        create_channel(run, self.channel, [affected_id, other_id], other_id)
        run.state.add_match(affected_id, other_id, self.channel)
        self.tokens = {mech.affected: run._tokens[mech.affected], OTHER: run._tokens[OTHER]}
        if mech.devices == 2:
            second = f"{mech.affected}-2"
            self.tokens[second] = run.api.user_token(affected_id, pr.TOKEN_TTL_SECONDS)
            run.token_claims[second] = describe_token(self.tokens[second])
        for label in self.labels:
            ensure_session(run, label, self.member(label), self.tokens[label])
            if label not in ("M1", OTHER):
                self.own_sessions.append(label)
        watched = {
            label: pr._observed(pr._http_answer(self.call(label, "watch", [])))
            for label in self.labels
        }
        history = run.send_as(T, self.channel, other_id, self.history_text)
        self.history_id = pr._dig(history.body, "message.id")
        if mech.scope == "account":
            mine = run.send_as(T, self.channel, affected_id, f"affected history {self.flat}")
            self.affected_history_id = pr._dig(mine.body, "message.id")
        self.detail["setup"] = {
            "channel": "{" + f"CH_{mech.key}" + "}",
            "connected": {
                label: pr._observed(pr._ws_answer(run.connect_replies[label]))
                for label in self.labels
            },
            "watch": watched,
        }

    def collect_before(self) -> None:
        for label in self.labels:
            answer, sees = self.query(label)
            self.before[label]["rest"] = answer
            self.before[label]["sees_history"] = sees
            self.before[label]["s15"] = self.s15_write(label, "before")
        probe = self.probes("before")
        for label in self.labels:
            self.before[label]["ws"] = self.got_probe(probe["received"].get(label))
        self.detail["before"] = {
            label: {
                "rest": pr._observed(self.before[label]["rest"]),
                "sees_history": self.before[label]["sees_history"],
                "s15": pr._observed(self.before[label]["s15"]),
                "ws_probe_received": self.before[label]["ws"],
            }
            for label in self.labels
        }
        self.detail["before_probe"] = probe
        _, messages, _ = self.server_channel()
        self.detail["messages_before"] = len(messages)
        self.message_ids_before = {str(m.get("id")) for m in messages}

    # -- apply --

    def apply(self) -> bool:
        """Apply the mechanism server-side; whether Stream accepted it."""
        run, mech = self.run, self.mech
        affected_id, other_id = run.ctx[mech.affected], run.ctx[OTHER]
        applied_at = datetime.now(UTC)
        result: Any
        body: dict[str, Any]
        if mech.key == "remove":
            body = {"remove_members": [affected_id], "user_id": other_id}
            result = run.api.raw("POST", f"/channels/{T}/{self.channel}", body=body)
        elif mech.key == "ban":
            body = {
                "target_user_id": affected_id,
                "banned_by_id": other_id,
                "channel_cid": self.cid,
            }
            result = run.api.raw("POST", "/api/v2/moderation/ban", body=body)
        elif mech.key == "hide":
            body = {"user_id": affected_id, "clear_history": False}
            result = run.api.raw("POST", f"/channels/{T}/{self.channel}/hide", body=body)
        elif mech.key == "freeze":
            body = {"set": {"frozen": True}, "user_id": other_id}
            result = run.api.raw("PATCH", f"/channels/{T}/{self.channel}", body=body)
        elif mech.key == "revoke":
            revoke_at = int(time.time())
            self.revoked_at = revoke_at
            stamp = datetime.fromtimestamp(revoke_at, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            body = {"users": [{"id": affected_id, "set": {"revoke_tokens_issued_before": stamp}}]}
            result = run.api.raw("PATCH", "/api/v2/users", body=body)
            # Issued at once: its iat (back-dated 5 s) falls before the revocation time.
            self.tokens["early"] = run.api.user_token(affected_id, pr.TOKEN_TTL_SECONDS)
        elif mech.key == "deactivate":
            body = {"mark_messages_deleted": False}
            result = run.api.raw("POST", f"/api/v2/users/{affected_id}/deactivate", body=body)
        else:  # delete
            # A hard user delete requires hard messages and conversations (Stream's users
            # documentation); the options are sent explicitly and recorded.
            body = {
                "user_ids": [affected_id],
                "user": "hard",
                "messages": "hard",
                "conversations": "hard",
            }
            result = run.api.raw("POST", "/api/v2/users/delete", body=body)
        self.request = f"{result.method} {self.generic(result.path)}"
        self.detail["apply"] = {
            "request": self.request,
            "body": json.loads(self.generic(json.dumps(body))),
            "answer": f"{result.status}" + (f" / code {result.code}" if result.code else ""),
            "answer_keys": sorted(result.body) if isinstance(result.body, dict) else None,
            "at": applied_at.strftime("%H:%M:%S"),
            "actor_named": "{M2}" if mech.actor else None,
        }
        if not result.ok:
            self.detail["apply"]["message"] = self.generic(result.message or "")
            return False
        if mech.key == "delete":
            task = pr._dig(result.body, "task_id")
            self.detail["apply"]["task"] = self.run._wait_task(
                task if isinstance(task, str) else None
            )
            if self.detail["apply"]["task"] == "completed":
                # Deleted: cleanup must not name it again (a batch delete could refuse it).
                run.users.remove(affected_id)
        self.detail["on_apply"] = self.describe_events(self.events(pr.EVENT_WAIT_MS))
        exists, messages, _ = self.server_channel()
        new = [m for m in messages if str(m.get("id")) not in self.message_ids_before]
        self.detail["system_messages"] = [
            {
                "type": m.get("type"),
                "text": self.generic(str(m.get("text"))),
                "user": self.generic(str(pr._dig(m, "user.id"))),
                "actor_paths": actor_paths(value_paths(m, self.needles())),
            }
            for m in new
            if m.get("type") == "system" or pr._dig(m, "user.id") not in self.run.ctx.values()
        ]
        self.detail["channel_exists_after_apply"] = exists
        if mech.key == "delete" and exists is False and self.cid in run.channels:
            # The hard delete removed the channel (a conversation of two or fewer
            # members); cleanup must not name it again.
            run.channels.remove(self.cid)
            self.detail["channel_deleted_by_the_mechanism"] = True
        return True

    def needles(self) -> dict[str, str]:
        ctx = self.run.ctx
        return {ctx[OTHER]: "{M2}", ctx.get(f"{OTHER}_name", ""): "{M2_name}"}

    def describe_events(self, seen: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for label, got in seen.items():
            if not got.get("collected"):
                out[label] = "not collected"
                continue
            paths = [
                f"{event.get('type')}: {path}"
                for event in got["events"]
                for path in value_paths(event, self.needles())
            ]
            out[label] = {
                "types": got["types"],
                "local_types": got["local_types"],
                "connection_closed": got["connection_closed"],
                "names_actor": actor_paths(paths) if self.mech.actor else "no actor named",
            }
        return out

    # -- after --

    def collect_after(self) -> None:
        run, mech = self.run, self.mech
        for label in self.labels:
            try:
                answer, sees = self.query(label)
            except ClientSessionEnded as exc:
                self.after[label]["rest_error"] = run._text(exc)
                continue
            self.after[label]["rest"] = answer
            self.after[label]["sees_history"] = sees
            self.after[label]["s15"] = self.s15_write(label, "after")
        if mech.key == "hide":
            self.detail["hidden_in_channel_list"] = self.listed(mech.affected)
        for label in self.labels:
            self.after[label]["token_reuse"] = self.reuse(label, self.tokens[label])
        if mech.key == "revoke":
            self.reissued()
        probe = self.probes("after")
        for label in self.labels:
            self.after[label]["ws"] = self.got_probe(probe["received"].get(label))
        self.detail["after_probe"] = probe
        if mech.key == "hide":
            self.detail["listed_after_a_new_message"] = self.listed(mech.affected)
        self.detail["after"] = {
            label: {
                "rest": pr._observed(self.after[label]["rest"])
                if "rest" in self.after[label]
                else self.after[label].get("rest_error"),
                "sees_history": self.after[label].get("sees_history"),
                "s15": pr._observed(self.after[label]["s15"])
                if "s15" in self.after[label]
                else None,
                "token_reuse": {
                    k: pr._observed(v) if v is not None else "not made"
                    for k, v in (self.after[label].get("token_reuse") or {}).items()
                },
                "ws_probe_received": self.after[label].get("ws"),
            }
            for label in self.labels
        }

    def listed(self, label: str) -> str:
        """Whether the member's channel list includes the channel (a hidden one is left out)."""
        reply = self.run._send(
            self.run.sessions[label],
            "call",
            max_calls=2,
            target="client",
            method="queryChannels",
            args=[{"cid": self.cid}, [], {"state": False, "watch": False, "presence": False}],
        )
        answer = pr._http_answer(reply)
        if answer.outcome != "success":
            return f"not shown ({pr._observed(answer)})"
        return "listed" if matrix.find_terms(pr._responses(reply), [self.channel]) else "not listed"

    def reuse(self, label: str, token: str) -> dict[str, Any]:
        """A new session with ``token``: connect, then read the channel; then closed."""
        reuse_label = f"{label}-reuse-{self.mech.key}"
        session = self.run._session(reuse_label, token, max_api_calls=10)
        try:
            con = self.run._send(
                session, "connect", max_calls=3, user={"id": self.run.ctx[self.member(label)]}
            )
            connected = pr._ws_answer(con)
            query = None
            if connected.outcome == "success":
                query = pr._http_answer(
                    self.run._send(
                        session,
                        "call",
                        max_calls=2,
                        target="channel",
                        method="query",
                        args=[matrix.READ_OPTIONS],
                        type=T,
                        id=self.channel,
                    )
                )
        finally:
            close_session(self.run, reuse_label)
        return {"connect": connected, "query": query}

    def reissued(self) -> None:
        """Tokens issued after the revocation: one at once (refused by design, iat
        back-dated) and one past the back-dating (accepted)."""
        run = self.run
        affected_id = run.ctx[self.mech.affected]
        wait = self.revoked_at + REVOKE_REISSUE_AFTER_SECONDS - time.time()
        if wait > 0:
            time.sleep(wait)
        self.tokens["late"] = run.api.user_token(affected_id, pr.TOKEN_TTL_SECONDS)
        tokens: dict[str, Any] = {}
        for name in (self.mech.affected, f"{self.mech.affected}-2", "early", "late"):
            claims = describe_token(self.tokens[name]).get("claims")
            iat = claims.get("iat") if isinstance(claims, dict) else None
            entry: dict[str, Any] = {
                "iat_minus_revocation_s": iat - self.revoked_at if isinstance(iat, int) else None
            }
            if name in ("early", "late"):
                used = self.reuse(f"{self.mech.affected}-{name}", self.tokens[name])
                entry["connect"] = pr._observed(used["connect"])
                entry["read"] = pr._observed(used["query"]) if used["query"] else "not made"
            tokens[name] = entry
        self.detail["tokens_after_revocation"] = tokens

    def judge_dimensions(self) -> None:
        for label in self.labels:
            before, after = self.before[label], self.after[label]
            connect = pr._ws_answer(self.run.connect_replies[label])
            reuse = after.get("token_reuse") or {}
            listener = self.listener(label)
            self.table[label] = {
                "rest": dimension(before.get("rest"), after.get("rest")),
                "ws": ws_dimension(
                    before.get("ws"),
                    after.get("ws"),
                    listener,
                    bool(self.detail.get("after_probe", {}).get("accepted")),
                ),
                "token_reuse": token_dimension(
                    connect, before.get("rest"), reuse.get("connect"), reuse.get("query")
                ),
                "s15": dimension(before.get("s15"), after.get("s15")),
            }
            if after.get("rest_error"):
                self.table[label]["rest"] = {"status": NOT_SHOWN, "why": after["rest_error"]}

    def listener(self, label: str) -> bool | None:
        """Whether a member still entitled to the channel received the probe after it."""
        if self.member(label) == OTHER or self.mech.both:
            others = [lbl for lbl in self.labels if lbl != label]
        else:
            others = [OTHER]
        got = [self.after[lbl].get("ws") for lbl in others]
        return any(bool(g) for g in got) if got else None

    # -- send, retention and undo --

    def send_checks(self) -> None:
        run, mech = self.run, self.mech
        affected_id, other_id = run.ctx[mech.affected], run.ctx[OTHER]
        # The app's own record of the unmatch or block for this pair.
        if mech.key in ("ban", "freeze"):
            run.state.block(other_id, affected_id)
            recorded = "block"
        else:
            run.state.unmatch(self.channel)
            recorded = "unmatch"
        before = run.ledger.run.api_calls
        service = AppSendService(run.state, run, T)
        outcomes = [
            service.send(affected_id, self.channel, f"app send after {mech.key}"),
            service.send(other_id, self.channel, f"app send after {mech.key}"),
        ]
        after = run.ledger.run.api_calls
        run._check(
            f"AP12-{mech.key}",
            f"app send path refuses both members' sends after {mech.key} (recorded as "
            f"{recorded}) without calling Stream",
            all(not o.decision.allowed and not o.stream_called for o in outcomes)
            and before == after,
            f"decisions {[o.decision.reason for o in outcomes]}; API calls before {before}, "
            f"after {after}",
        )
        sent = run.api.raw(
            "POST",
            f"/channels/{T}/{self.channel}/message",
            body={
                "message": {
                    "text": f"server send as the affected member after {mech.key} {run.prefix}",
                    "user_id": affected_id,
                }
            },
        )
        message_id = pr._dig(sent.body, "message.id") if sent.ok else None
        if isinstance(message_id, str):
            run.messages.add(message_id)
        self.detail["server_send_as_affected"] = {
            "answer": f"{sent.status}" + (f" / code {sent.code}" if sent.code else ""),
            "message": self.generic(sent.message) if sent.message else None,
            "rule": "an observation, not a verdict: server-side calls bypass Stream's "
            "permission checks",
        }

    def retention(self) -> None:
        exists, messages, members = self.server_channel()
        ids = {str(m.get("id")) for m in messages}
        if exists is None:
            self.retained = None
        elif exists is False:
            self.retained = False
        else:
            self.retained = self.history_id in ids
        affected = next((m for m in messages if m.get("id") == self.affected_history_id), None)
        self.detail["retention"] = {
            "channel_exists": exists,
            "history_retained": self.retained,
            "messages": len(messages),
            "affected_member_message": (
                None
                if self.affected_history_id is None
                else (
                    "not retained"
                    if affected is None
                    else {
                        "type": affected.get("type"),
                        "author": self.generic(str(pr._dig(affected, "user.id"))),
                        "deleted": bool(affected.get("deleted_at")),
                    }
                )
            ),
        }
        self.detail["member_custom_after"] = {
            label: self.member_note(self.server_members() if exists else None, label)
            for label in (self.mech.affected, OTHER)
        }

    def undo(self) -> None:
        """The affected member's own client tries to undo the mechanism; the server's
        replay of the same request is the control (and undoes it)."""
        mech = self.mech
        label = mech.affected
        if mech.undo == "rejoin":
            reply = self.call(label, "addMembers", [[self.run.ctx[label]]])
        elif mech.undo == "unban":
            reply = self.call(label, "unbanUser", [self.run.ctx[label]])
        elif mech.undo == "show":
            reply = self.call(label, "show", [])
        else:  # unfreeze
            reply = self.call(label, "updatePartial", [{"set": {"frozen": False}}])
        answer = pr._http_answer(reply)
        record = answer.record
        control_ok = False
        control = "no client request to replay"
        if record is not None:
            path = "/" + str(record.get("path") or "").lstrip("/")
            params = {
                k: v if isinstance(v, str) else json.dumps(v)
                for k, v in (record.get("params") or {}).items()
                if k not in ("api_key", "user_id", "connection_id")
            }
            body = record.get("body")
            if mech.undo == "show":
                body = {"user_id": self.run.ctx[label]}
            method = str(record.get("method"))
            replay = self.run.api.raw(
                method,
                path,
                body=None if method in ("GET", "DELETE") else body,
                params=params or None,
            )
            control_ok = replay.ok
            control = f"server replay {method} -> {replay.status}" + (
                f" / code {replay.code}" if replay.code else ""
            )
        self.undo_verdict = matrix.refused_verdict(answer.outcome, control_ok)
        self.detail["client_undo"] = {
            "request": pr._request_line(record, self.run.ctx),
            "answer": pr._observed(answer),
            "control": control,
            "verdict": f"{self.undo_verdict.label}: {self.undo_verdict.reason}",
        }
        if mech.undo == "rejoin":
            # The S15 mapping: is the member's custom data kept across removal and re-adding?
            self.detail["member_custom_after_readd"] = self.member_note(
                self.server_members(), label
            )

    # -- the verdict --

    def judged(self) -> dict[str, dict[str, dict[str, str]]]:
        labels = [lbl for lbl in self.labels if self.member(lbl) == self.mech.affected]
        if self.mech.both:
            labels = list(self.labels)
        return {label: self.table.get(label, {}) for label in labels}

    def verdict(self) -> matrix.Verdict:
        return policy_verdict(self.judged(), self.undo_verdict, self.retained)

    def summary(self) -> str:
        parts = []
        for label in self.labels:
            dims = self.table.get(label)
            if not dims:
                continue
            shown = ", ".join(f"{d} {dims[d]['status']}" for d in DIMENSIONS if d in dims)
            parts.append(f"{label}: {shown}")
        if self.retained is not None:
            parts.append(f"history retained {self.retained}")
        if self.undo_verdict is not None:
            parts.append(f"client undo: {self.undo_verdict.label}")
        return "; ".join(parts) or "-"
