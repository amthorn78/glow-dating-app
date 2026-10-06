"""The delivery phase (P06.2 Stage A, items 2 and 3; Stage B1, CX4, CX6, F1 and F3): the
app's outbox delivery, run in-process against the fixture provider on the disposable
database.

It runs after both subjects' oracles, because delivery updates the rows the oracle reads
commit times from. First it drains the outbox: every chat event the adapter's cases,
races and controls wrote is delivered, first in, first out, as one provider call each.
Then it checks, for every world the design tags made, that the provider ended where the
database says it should: every member's user provisioned, an active match's channel
holds exactly its two members, a revoked one holds none, every authorized message was
delivered once and none after its channel's members were removed, and every suspended
or deleted member's provider user is deactivated with one token revocation per epoch
bump. Last, it runs the targeted cases: each event kind, with the provisioning before
the channel; the order key against an app clock that runs backwards (DM-15 3.1); a retry
after a fixture failure (before and after the provider acted); provider text kept out; a
revocation committed after a send's authorization and before its delivery; a dead letter
after the last attempt; a lost provisioning response (3.3); a lost creation response
followed by a revocation (CX6, 4.5); each dead-lettered revocation marking its row, and
no message into a marked binding (F3, 4.5).

No provider is called but the in-memory fixture; nothing reaches a network.
"""

from __future__ import annotations

import re
import sys
import time
from collections.abc import Callable
from datetime import timedelta
from typing import Any
from uuid import UUID

from glow_chat import events
from glow_chat.delivery import Delivery, OutboxDelivery
from glow_domain.chat_provider import OPERATIONS
from glow_domain.chat_provider_fixtures import FixtureChatProvider
from glow_domain.chat_tokens import revocation_cutoff_sent

from glow_ordering_proof import oracle
from glow_ordering_proof.cases import Context, Pair, World, make_pair, make_world, send_request
from glow_ordering_proof.interface import Result
from glow_ordering_proof.observe import WORLD_TABLE, LogContext
from glow_ordering_proof.results import DeliveryReport

DRAIN_MAX_EVENTS = 60_000
DRAIN_MAX_SECONDS = 300.0
REF_FORM = re.compile(r"[0-9a-f]{32}")
# Text a provider could put in an error; it must never be kept or shown.
PROVIDER_TEXT = "fixture-provider-said: upstream detail that must not be kept"
ORDER_REPEATS = 25


class DeliveryCheckFailed(AssertionError):
    """A targeted delivery case did not hold."""


def _require(condition: object, detail: object = "") -> None:
    if not condition:
        line = sys._getframe(1).f_lineno
        raise DeliveryCheckFailed(f"delivery_phase.py:{line}: {detail}".rstrip(": "))


def _models() -> Any:
    from glow_persistence import models

    return models


def _drain(delivery: OutboxDelivery, report: DeliveryReport) -> None:
    started = time.monotonic()
    stalled = 0
    while True:
        batch = delivery.deliver_due(limit=1000)
        for item in batch:
            report.drained += 1
            report.outcomes[f"{item.event_type}={item.outcome}"] += 1
            if item.outcome == "dead_letter":
                report.dead_letters[f"{item.event_type}:{item.code}"] += 1
        if not batch:
            break
        if batch[-1].outcome in ("retry", "lost_lease"):
            stalled += 1
            if stalled > 10:
                break
        if report.drained > DRAIN_MAX_EVENTS or time.monotonic() - started > DRAIN_MAX_SECONDS:
            break
    report.seconds = time.monotonic() - started
    m = _models()
    left = m.OutboxEvent.objects.filter(
        schema_version=oracle.ADAPTER_SCHEMA,
        state__in=("pending", "leased"),
        event_type__in=tuple(events.DELIVERED),
    ).count()
    report.check(
        "drain",
        left == 0 and stalled == 0,
        f"{report.drained} events in {report.seconds:.1f} s; {left} chat events left;"
        f" {stalled} stalled passes",
    )


def _design_worlds() -> list[tuple[UUID, UUID, UUID]]:
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT match_id, low_id, high_id FROM {WORLD_TABLE}"
            " WHERE subject = 'adapter' AND run_tag LIKE 'design:%%'"
        )
        return [(row[0], row[1], row[2]) for row in cursor.fetchall()]


def _end_state(provider: FixtureChatProvider, report: DeliveryReport) -> None:
    """Every design world, against the provider it was delivered to."""
    m = _models()
    worlds = _design_worlds()
    accounts = {a for _, low, high in worlds for a in (low, high)}
    identities = {
        row.account_id: row
        for row in m.ChatIdentity.objects.filter(account_id__in=accounts, provider=provider.name)
    }
    problems: list[str] = []
    messages = 0
    for match_id, low, high in worlds:
        match = m.Match.objects.get(pk=match_id)
        binding = m.ChatBinding.objects.get(match_id=match_id)
        refs = {identities[low].user_ref, identities[high].user_ref}
        channel = provider.channels.get(binding.channel_ref)
        if channel is None:
            problems.append(f"no channel for match {match_id}")
            continue
        if set(channel.created_members) != refs:
            problems.append(f"channel of {match_id} created with other members")
        active = match.state == "active"
        if binding.state != ("active" if active else "revoked"):
            problems.append(f"binding {binding.state} for a {match.state} match {match_id}")
        if binding.reconcile_code is not None:
            problems.append(f"a marked binding in a design world: {match_id}")
        if channel.members != (refs if active else set()):
            problems.append(f"channel members of a {match.state} match {match_id}")
        submissions = list(m.MessageSubmission.objects.filter(binding=binding))
        if any(s.state != "accepted" for s in submissions):
            problems.append(f"an undelivered submission in {match_id}")
        sent = [message_id for message_id, _, _ in channel.messages]
        messages += len(sent)
        if sorted(sent) != sorted(s.provider_message_ref for s in submissions):
            problems.append(f"messages of {match_id} differ from its submissions")
        if channel.removals and channel.removals[0] != len(channel.messages):
            problems.append(f"a message after the removal in {match_id}")
    deactivated = 0
    for account in accounts:
        row = m.AppAccount.objects.get(pk=account)
        identity = identities[account]
        user = provider.users.get(identity.user_ref)
        revoked = row.state in ("suspended", "deletion_pending")
        deactivated += revoked
        # B1 (CX4): every identity was provisioned, and is active or deactivated.
        if identity.state != ("deactivated" if revoked else "active"):
            problems.append(f"identity {identity.state} for a {row.state} account")
        if identity.reconcile_code is not None:
            problems.append(f"a marked identity in a design world: {account}")
        if user is None or user.active == revoked:
            problems.append(f"provider user state for a {row.state} account")
        elif len(user.token_cutoffs) != row.session_epoch - 1:
            problems.append(
                f"{len(user.token_cutoffs)} token revocations at epoch {row.session_epoch}"
            )
    dead = m.OutboxEvent.objects.filter(schema_version=oracle.ADAPTER_SCHEMA, state="dead_letter")
    design_matches = {match for match, _, _ in worlds}
    identity_accounts = {
        identity_id: account_id
        for account_id, identity_id in m.ChatIdentity.objects.filter(
            account_id__in=accounts
        ).values_list("account_id", "id")
    }
    for event in dead:
        owner = event.aggregate_id
        if event.event_type == "message_submitted":
            owner = (
                m.MessageSubmission.objects.filter(pk=event.payload_ref)
                .values_list("binding__match_id", flat=True)
                .first()
            )
        elif event.event_type == "identity_created":
            owner = identity_accounts.get(event.aggregate_id)
        if owner in design_matches or owner in accounts:
            problems.append(f"a dead letter in a design world: {event.event_type}")
    report.check(
        "end state of every design world",
        not problems,
        f"{len(worlds)} worlds, {len(accounts)} accounts ({deactivated} deactivated),"
        f" {messages} messages; " + ("; ".join(problems[:5]) or "as the database says"),
    )
    extra = [
        c
        for c in provider.calls
        if c.operation not in OPERATIONS or c.arguments - OPERATIONS[c.operation]
    ]
    report.check(
        "identifiers and members only",
        not extra,
        f"{len(provider.calls)} provider calls, operations"
        f" {sorted({c.operation for c in provider.calls})}; no name, image or custom field,"
        " and no invite, call, feed or activity",
    )


def _world(ctx: Context, name: str) -> World:
    ctx.log.context = LogContext(run_tag=f"delivery:{name}", variant="adapter")
    return make_world(ctx)


def _pair(ctx: Context, name: str) -> Pair:
    ctx.log.context = LogContext(run_tag=f"delivery:{name}", variant="adapter")
    return make_pair(ctx)


def _deliver(delivery: OutboxDelivery) -> list[Delivery]:
    done: list[Delivery] = delivery.deliver_due(limit=100)
    return done


def _kinds(done: list[Delivery]) -> list[tuple[str, str]]:
    return [(d.event_type, d.outcome) for d in done]


def _receipt(result: Result) -> UUID:
    if result.receipt is None:
        raise DeliveryCheckFailed(f"no receipt: {result.label()}")
    return result.receipt.submission_id


def _identity(account_id: UUID) -> Any:
    return _models().ChatIdentity.objects.get(account_id=account_id)


def _fail_until_dead(
    provider: FixtureChatProvider,
    delivery: OutboxDelivery,
    operations: tuple[str, ...],
    *,
    after_effect: bool,
    until: str,
) -> list[Delivery]:
    """Every attempt of each of ``operations`` fails, before or after its effect, and the
    outbox is delivered pass by pass until an event of type ``until`` is dead-lettered;
    everything delivered meanwhile, in order (a pass runs on past a dead letter to the
    events behind it, and stops at a retry)."""
    for operation in operations:
        for _ in range(delivery.max_attempts):
            provider.fail_next(operation, after_effect=after_effect)
    done: list[Delivery] = []
    for _ in range(delivery.max_attempts * len(operations) + 2):
        done.extend(_deliver(delivery))
        if any(d.event_type == until and d.outcome == "dead_letter" for d in done):
            return done
    raise DeliveryCheckFailed(f"{until} was not dead-lettered: {_kinds(done)}")


def _outcomes(done: list[Delivery], event_type: str) -> list[str]:
    return [d.outcome for d in done if d.event_type == event_type]


def _each_kind(ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery) -> str:
    m = _models()
    world = _world(ctx, "each_kind")
    first = _deliver(delivery)
    # CX4 (DM-15 3.1 and 3.4): both provisionings, then the channel, each one call.
    _require(
        [d.event_type for d in first]
        == ["identity_created", "identity_created", "match_activated"],
        first,
    )
    _require(all(d.outcome == "delivered" and d.provider_called for d in first), first)
    _require(
        [c.operation for c in provider.calls[-3:]]
        == ["provision_user", "provision_user", "create_channel"],
        provider.calls[-3:],
    )
    binding = m.ChatBinding.objects.get(match_id=world.match)
    identities = list(m.ChatIdentity.objects.filter(account_id__in=(world.low, world.high)))
    refs = {i.user_ref for i in identities}
    _require(all(i.state == "active" for i in identities), [i.state for i in identities])
    _require(binding.state == "active", binding.state)
    channel = provider.channels[binding.channel_ref]
    _require(
        set(channel.created_members) == refs and channel.members == refs,
        "the delivery check did not hold",
    )
    _require(all(provider.users[ref].active for ref in refs))
    for ref in (*refs, binding.channel_ref):
        _require(REF_FORM.fullmatch(ref), "a provider identifier is not 32 hexadecimal characters")
        for account in (world.low, world.high):
            _require(
                account.hex not in ref and str(account) not in ref,
                "the delivery check did not hold",
            )
    sent = ctx.subject.send(send_request(world, key="k-each"))
    _require(sent.outcome == "authorized" and sent.receipt is not None, sent.label())
    second = _deliver(delivery)
    _require(_kinds(second) == [("message_submitted", "delivered")], second)
    submission = m.MessageSubmission.objects.get(pk=_receipt(sent))
    _require(submission.state == "accepted")
    _require(
        [i for i, _, _ in channel.messages] == [submission.provider_message_ref],
        "the delivery check did not hold",
    )
    blocked = ctx.subject.block(world.high, world.low)
    _require(blocked.outcome == "applied", blocked.label())
    third = _deliver(delivery)
    _require(_kinds(third) == [("contact_revoked", "delivered")], third)
    binding.refresh_from_db()
    _require(
        binding.state == "revoked" and channel.members == set() and len(channel.messages) == 1,
        "the delivery check did not hold",
    )
    _require(binding.reconcile_code is None)
    other = _world(ctx, "each_kind_account")
    _deliver(delivery)
    suspended = ctx.subject.suspend(other.low)
    _require(suspended.outcome == "applied", suspended.label())
    fourth = _deliver(delivery)
    _require(
        _kinds(fourth)
        == [
            ("access_revoked", "delivered"),
            ("session_epoch_bumped", "delivered"),
        ],
        fourth,
    )
    identity = _identity(other.low)
    event = m.OutboxEvent.objects.get(event_type="session_epoch_bumped", aggregate_id=other.low)
    user = provider.users[identity.user_ref]
    _require(identity.state == "deactivated" and not user.active)
    # F1 (DM-15 5.2): the stored cut-off is exact; the provider got the next whole second.
    _require(identity.tokens_revoked_before == event.available_at, "the stored cut-off")
    _require(
        user.token_cutoffs[-1] == revocation_cutoff_sent(event.available_at),
        f"sent {user.token_cutoffs[-1]} for the cut-off {event.available_at}",
    )
    _require(
        user.token_cutoffs[-1] > event.available_at and user.token_cutoffs[-1].microsecond == 0
    )
    return (
        "both users provisioned, then the channel created with exactly the two members; message"
        " sent with its committed ID; both members removed on a block with the history kept;"
        " user deactivated and its tokens revoked at the next whole second after the bump's"
        " time, which is stored exact"
    )


def _retry(ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery) -> str:
    m = _models()
    world = _world(ctx, "retry")
    binding = m.ChatBinding.objects.get(match_id=world.match)
    provider.fail_next("create_channel")
    failed = _deliver(delivery)
    _require(
        [(d.event_type, d.outcome, d.code, d.attempts) for d in failed]
        == [
            ("identity_created", "delivered", None, 1),
            ("identity_created", "delivered", None, 1),
            ("match_activated", "retry", "provider_unavailable", 1),
        ],
        failed,
    )
    binding.refresh_from_db()
    _require(
        binding.state == "pending" and binding.channel_ref not in provider.channels,
        "the delivery check did not hold",
    )
    again = _deliver(delivery)
    _require([(d.outcome, d.attempts) for d in again] == [("delivered", 2)], again)
    creates = [c for c in provider.calls if c.operation == "create_channel"][-2:]
    _require([c.outcome for c in creates] == ["failed_before", "ok"], creates)
    sent = ctx.subject.send(send_request(world, key="k-retry"))
    _require(sent.receipt is not None, sent.label())
    submission = m.MessageSubmission.objects.get(pk=_receipt(sent))
    message_id = submission.provider_message_ref
    provider.fail_next("send_message", after_effect=True)  # the provider acted; the answer was lost
    lost = _deliver(delivery)
    _require([(d.outcome, d.code) for d in lost] == [("retry", "provider_unavailable")], lost)
    submission.refresh_from_db()
    _require(
        submission.state == "pending" and submission.provider_message_ref == message_id,
        "the delivery check did not hold",
    )
    redelivered = _deliver(delivery)
    _require([(d.outcome, d.already) for d in redelivered] == [("delivered", True)], redelivered)
    channel = provider.channels[binding.channel_ref]
    _require([i for i, _, _ in channel.messages] == [message_id])
    submission.refresh_from_db()
    _require(
        submission.state == "accepted" and submission.provider_message_ref == message_id,
        "the delivery check did not hold",
    )
    provider.fail_next("remove_members", code=None, text=PROVIDER_TEXT)
    _require(
        ctx.subject.unmatch(world.low, world.match).outcome == "applied",
        "the delivery check did not hold",
    )
    raw = _deliver(delivery)
    _require([(d.outcome, d.code) for d in raw] == [("retry", "provider_unavailable")], raw)
    _require(PROVIDER_TEXT not in repr(raw))
    for event in m.OutboxEvent.objects.filter(aggregate_id=world.match):
        _require(PROVIDER_TEXT not in repr(vars(event)))
    removed = _deliver(delivery)
    _require([d.outcome for d in removed] == ["delivered"], removed)
    _require(channel.members == set())
    binding.refresh_from_db()
    _require(binding.state == "revoked" and binding.reconcile_code is None)
    return (
        "a failed channel creation retried with the same channel ID (one channel); a lost"
        " answer to a send retried with the committed message ID (one message, the retry"
        " found it); provider text mapped to provider_unavailable and kept nowhere; a retried"
        " event marks nothing"
    )


def _revocation_before_delivery(
    ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery
) -> str:
    m = _models()
    world = _world(ctx, "revocation_before_delivery")
    _deliver(delivery)
    sent = ctx.subject.send(send_request(world, key="k-before"))
    _require(sent.receipt is not None, sent.label())
    _require(
        ctx.subject.unmatch(world.high, world.match).outcome == "applied",
        "the delivery check did not hold",
    )
    done = _deliver(delivery)
    _require(
        _kinds(done)
        == [
            ("message_submitted", "delivered"),
            ("contact_revoked", "delivered"),
        ],
        done,
    )
    binding = m.ChatBinding.objects.get(match_id=world.match)
    channel = provider.channels[binding.channel_ref]
    submission = m.MessageSubmission.objects.get(pk=_receipt(sent))
    _require(
        submission.state == "accepted" and binding.state == "revoked",
        "the delivery check did not hold",
    )
    _require(
        [i for i, _, _ in channel.messages] == [submission.provider_message_ref],
        "the delivery check did not hold",
    )
    _require(
        channel.removals == [1] and channel.members == set(), "the delivery check did not hold"
    )
    _require(_deliver(delivery) == [])
    _require(len(channel.messages) == 1)
    return (
        "the authorization committed first, so its message was delivered into the history,"
        " then both members were removed; it stays accepted in Glow's record, no member can"
        " read the channel, and nothing re-sends it"
    )


def _dead_letter(ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery) -> str:
    m = _models()
    world = _world(ctx, "dead_letter")
    done = _fail_until_dead(
        provider, delivery, ("create_channel",), after_effect=False, until="match_activated"
    )
    outcomes = _outcomes(done, "match_activated")
    _require(outcomes == ["retry"] * (delivery.max_attempts - 1) + ["dead_letter"], outcomes)
    binding = m.ChatBinding.objects.get(match_id=world.match)
    _require(
        binding.state == "failed" and binding.channel_ref not in provider.channels,
        "the delivery check did not hold",
    )
    # F3: the dead letter marks the binding with the Glow code of its last attempt.
    _require(binding.reconcile_code == "provider_unavailable", binding.reconcile_code)
    refused = ctx.subject.send(send_request(world, key="k-dead"))
    _require(
        refused.outcome == "refused" and refused.reason == "binding_not_active", refused.label()
    )
    return (
        f"after {delivery.max_attempts} failed attempts the event is dead-lettered and the"
        " binding failed and marked provider_unavailable; a send to it is refused"
    )


def _order_key(ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery) -> str:
    """DM-15 3.1: the events one activation writes are delivered in the order it wrote
    them, by the database-assigned sequence, over repeated runs, with the app's clock
    running backwards so that created_at would order them the other way."""
    from django.utils import timezone

    m = _models()
    real = timezone.now
    step = [0]

    def backwards() -> Any:
        step[0] += 1
        return real() - timedelta(seconds=step[0])

    worlds: list[World] = []
    timezone.now = backwards
    try:
        for _ in range(ORDER_REPEATS):
            worlds.append(_world(ctx, "order_key"))
    finally:
        timezone.now = real
    reversed_clocks = 0
    for world in worlds:
        identities = list(m.ChatIdentity.objects.filter(account_id__in=(world.low, world.high)))
        rows = list(
            m.OutboxEvent.objects.filter(
                aggregate_id__in=[i.id for i in identities] + [world.match],
                event_type__in=("identity_created", "match_activated"),
            ).order_by("sequence")
        )
        _require(len(rows) == 3, [r.event_type for r in rows])
        _require([r.event_type for r in rows] == ["identity_created"] * 2 + ["match_activated"])
        _require(len({r.available_at for r in rows}) == 1, "one clock_timestamp per transaction")
        _require(rows[0].sequence < rows[1].sequence < rows[2].sequence)
        # The app's clock ran backwards: created_at would put the channel first.
        if rows[0].created_at > rows[1].created_at > rows[2].created_at:
            reversed_clocks += 1
    _require(reversed_clocks == ORDER_REPEATS, f"{reversed_clocks} worlds with a reversed clock")
    before = len(provider.calls)
    done = _deliver(delivery)
    _require(len(done) == 3 * ORDER_REPEATS, len(done))
    _require(all(d.outcome == "delivered" for d in done), done[:3])
    _require(
        [d.event_type for d in done]
        == ["identity_created", "identity_created", "match_activated"] * ORDER_REPEATS,
        [d.event_type for d in done][:6],
    )
    calls = [c.operation for c in provider.calls[before:]]
    _require(
        calls == ["provision_user", "provision_user", "create_channel"] * ORDER_REPEATS, calls[:6]
    )
    return (
        f"{ORDER_REPEATS} activations with the app clock running backwards: in every one the"
        " two provisionings precede the channel by the database-assigned sequence, all three"
        " share one available_at, and created_at would have ordered them the other way;"
        " delivered and called in that order"
    )


def _lost_provisioning(
    ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery
) -> str:
    """DM-15 3.2 and 3.3: a provisioning whose response is lost dead-letters and marks the
    identity; the channel then dead-letters with member_unavailable without a call; a
    later deactivation and token revocation still make their calls, whether or not the
    provider holds the user."""
    m = _models()
    # (a) The provider acted, the answer was lost, every time.
    world = _world(ctx, "lost_provisioning")
    before = len(provider.calls)
    done = _fail_until_dead(
        provider, delivery, ("provision_user",), after_effect=True, until="identity_created"
    )
    # The first member's provisioning: four retries and the dead letter; the second
    # member's, delivered; then the channel, dead-lettered without a call (DM-15 3.2).
    _require(
        _outcomes(done, "identity_created")
        == ["retry"] * (delivery.max_attempts - 1) + ["dead_letter", "delivered"],
        _kinds(done),
    )
    _require(_outcomes(done, "match_activated") == ["dead_letter"], _kinds(done))
    channel_event = next(d for d in done if d.event_type == "match_activated")
    _require(channel_event.code == "member_unavailable" and not channel_event.provider_called)
    _require(all(c.operation == "provision_user" for c in provider.calls[before:]))
    dead = next(d for d in done if d.outcome == "dead_letter")
    first_identity = m.ChatIdentity.objects.get(
        pk=m.OutboxEvent.objects.get(pk=dead.event_id).aggregate_id
    )
    marked_account = first_identity.account_id
    _require(first_identity.state == "pending", first_identity.state)
    _require(first_identity.reconcile_code == "provider_unavailable", first_identity.reconcile_code)
    _require(first_identity.user_ref in provider.users, "the provider holds the user")
    binding = m.ChatBinding.objects.get(match_id=world.match)
    _require(binding.state == "failed" and binding.reconcile_code == "member_unavailable")
    refused = ctx.subject.send(send_request(world, key="k-lost-prov"))
    _require(
        refused.outcome == "refused" and refused.reason == "binding_not_active", refused.label()
    )
    # A grant for the marked, unprovisioned identity is refused too (5.1).
    session = world.session_of(marked_account)
    granted = ctx.state_subject.grant_token(session)
    _require(granted.outcome == "refused" and granted.reason == "no_chat_identity", granted.label())
    _require(ctx.subject.suspend(marked_account).outcome == "applied")
    later = _deliver(delivery)
    _require(
        _kinds(later) == [("access_revoked", "delivered"), ("session_epoch_bumped", "delivered")],
        _kinds(later),
    )
    _require(all(d.provider_called and not d.already for d in later), later)
    first_identity.refresh_from_db()
    user = provider.users[first_identity.user_ref]
    _require(first_identity.state == "deactivated" and not user.active)
    _require(first_identity.reconcile_code == "provider_unavailable", "the mark is kept")
    _require(len(user.token_cutoffs) == 1)
    # (b) The provider never acted: the user does not exist there.
    other = _world(ctx, "lost_provisioning_never_created")
    done = _fail_until_dead(
        provider, delivery, ("provision_user",), after_effect=False, until="identity_created"
    )
    _require(_outcomes(done, "match_activated") == ["dead_letter"], _kinds(done))
    dead = next(d for d in done if d.outcome == "dead_letter")
    missing = m.ChatIdentity.objects.get(
        pk=m.OutboxEvent.objects.get(pk=dead.event_id).aggregate_id
    )
    _require(missing.user_ref not in provider.users, "the provider does not hold the user")
    _require(ctx.subject.delete(missing.account_id).outcome == "applied")
    later = _deliver(delivery)
    _require(
        _kinds(later) == [("access_revoked", "delivered"), ("session_epoch_bumped", "delivered")],
        _kinds(later),
    )
    # The calls were made; a user the provider does not have counts as deactivated and revoked.
    _require(all(d.provider_called and d.already for d in later), later)
    _require(
        [c.outcome for c in provider.calls[-2:]] == ["member_unavailable", "member_unavailable"],
        provider.calls[-2:],
    )
    missing.refresh_from_db()
    _require(missing.state == "deactivated" and missing.tokens_revoked_before is not None)
    _require(missing.reconcile_code == "provider_unavailable")
    _require(other.match is not None)
    return (
        "a provisioning whose answer was lost dead-lettered after 5 attempts and marked the"
        " identity (pending, provider_unavailable); the channel dead-lettered member_unavailable"
        " without a call and the binding failed and marked; a grant was refused; the later"
        " deactivation and token revocation made their calls (the user existed), and for a user"
        " the provider never created they counted as done"
    )


def _lost_creation_then_revocation(
    ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery
) -> str:
    """CX6 (DM-15 4.5): a creation whose response was lost leaves the binding failed and
    marked while the channel exists; a revocation still removes both members, and the
    binding is recorded revoked, the mark kept. A channel the provider never created
    counts as removed."""
    m = _models()
    world = _world(ctx, "lost_creation")
    done = _fail_until_dead(
        provider, delivery, ("create_channel",), after_effect=True, until="match_activated"
    )
    _require(_outcomes(done, "match_activated")[-1] == "dead_letter", _kinds(done))
    binding = m.ChatBinding.objects.get(match_id=world.match)
    channel = provider.channels.get(binding.channel_ref)
    _require(channel is not None and len(channel.members) == 2, "the channel exists")
    assert channel is not None
    _require(binding.state == "failed" and binding.reconcile_code == "provider_unavailable")
    refused = ctx.subject.send(send_request(world, key="k-lost-create"))
    _require(
        refused.outcome == "refused" and refused.reason == "binding_not_active", refused.label()
    )
    _require(ctx.subject.block(world.low, world.high).outcome == "applied")
    removed = _deliver(delivery)
    _require(_kinds(removed) == [("contact_revoked", "delivered")], _kinds(removed))
    _require(removed[0].provider_called and not removed[0].already)
    _require(channel.members == set(), "both members removed")
    binding.refresh_from_db()
    _require(binding.state == "revoked" and binding.reconcile_code == "provider_unavailable")
    # The channel the provider never created.
    other = _world(ctx, "lost_creation_never_created")
    done = _fail_until_dead(
        provider, delivery, ("create_channel",), after_effect=False, until="match_activated"
    )
    _require(_outcomes(done, "match_activated")[-1] == "dead_letter", _kinds(done))
    binding = m.ChatBinding.objects.get(match_id=other.match)
    _require(binding.channel_ref not in provider.channels)
    _require(ctx.subject.unmatch(other.high, other.match).outcome == "applied")
    removed = _deliver(delivery)
    _require(_kinds(removed) == [("contact_revoked", "delivered")], _kinds(removed))
    _require(removed[0].provider_called and removed[0].already, removed)
    _require(provider.calls[-1].outcome == "channel_unavailable", provider.calls[-1])
    binding.refresh_from_db()
    _require(binding.state == "revoked" and binding.reconcile_code == "provider_unavailable")
    return (
        "a creation whose answer was lost left the binding failed and marked while the channel"
        " held both members; the block's removal was still made and emptied it, and the binding"
        " is revoked with its mark kept; for a channel the provider never created the removal"
        " counted as done (channel_unavailable) and the binding is revoked"
    )


def _dead_lettered_revocations_mark(
    ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery
) -> str:
    """F3: a dead-lettered contact_revoked, access_revoked or session_epoch_bumped marks
    its row; and no message is delivered into a marked binding (DM-15 4.5)."""
    m = _models()
    world = _world(ctx, "marks_contact")
    _deliver(delivery)
    _require(ctx.subject.unmatch(world.low, world.match).outcome == "applied")
    done = _fail_until_dead(
        provider, delivery, ("remove_members",), after_effect=False, until="contact_revoked"
    )
    _require(
        _outcomes(done, "contact_revoked")
        == ["retry"] * (delivery.max_attempts - 1) + ["dead_letter"],
        _kinds(done),
    )
    binding = m.ChatBinding.objects.get(match_id=world.match)
    _require(binding.state == "active" and binding.reconcile_code == "provider_unavailable")
    channel = provider.channels[binding.channel_ref]
    _require(len(channel.members) == 2, "the provider still holds both members")
    other = _world(ctx, "marks_account")
    _deliver(delivery)
    _require(ctx.subject.suspend(other.low).outcome == "applied")
    done = _fail_until_dead(
        provider,
        delivery,
        ("deactivate_user", "revoke_user_tokens"),
        after_effect=False,
        until="session_epoch_bumped",
    )
    retried_then_dead = ["retry"] * (delivery.max_attempts - 1) + ["dead_letter"]
    _require(_outcomes(done, "access_revoked") == retried_then_dead, _kinds(done))
    _require(_outcomes(done, "session_epoch_bumped") == retried_then_dead, _kinds(done))
    identity = _identity(other.low)
    _require(identity.state == "active" and identity.reconcile_code == "provider_unavailable")
    _require(identity.tokens_revoked_before is None)
    _require(identity.reconcile_code == "provider_unavailable")
    # A message authorized into a binding that is then marked is never delivered.
    third = _world(ctx, "marks_message")
    _deliver(delivery)
    sent = ctx.subject.send(send_request(third, key="k-marked"))
    _require(sent.receipt is not None, sent.label())
    m.ChatBinding.objects.filter(match_id=third.match).update(reconcile_code="provider_unavailable")
    before = len(provider.calls)
    dead = _deliver(delivery)
    _require(_kinds(dead) == [("message_submitted", "dead_letter")], _kinds(dead))
    _require(dead[0].code == "channel_unavailable" and not dead[0].provider_called)
    _require(len(provider.calls) == before, "no provider call")
    submission = m.MessageSubmission.objects.get(pk=_receipt(sent))
    _require(submission.state == "failed")
    binding = m.ChatBinding.objects.get(match_id=third.match)
    _require(provider.channels[binding.channel_ref].messages == [])
    return (
        "a dead-lettered removal marked its binding provider_unavailable (still active, both"
        " members still at the provider); a dead-lettered deactivation and token revocation"
        " marked their identity; a message authorized into a binding marked afterwards was"
        " dead-lettered channel_unavailable without a call"
    )


TARGETED: tuple[tuple[str, Callable[[Context, FixtureChatProvider, OutboxDelivery], str]], ...] = (
    ("delivery of each event kind", _each_kind),
    ("the order key: provisioning before the channel", _order_key),
    ("a retry after a fixture failure", _retry),
    ("a revocation after the authorization, before the delivery", _revocation_before_delivery),
    ("a dead letter after the last attempt", _dead_letter),
    ("a lost provisioning response", _lost_provisioning),
    ("a lost creation response, then a revocation", _lost_creation_then_revocation),
    ("dead-lettered revocations mark their rows", _dead_lettered_revocations_mark),
)


def run_delivery_phase(ctx: Context) -> DeliveryReport:
    provider = FixtureChatProvider(environment="test")
    delivery = OutboxDelivery(provider)
    report = DeliveryReport()
    steps: tuple[tuple[str, Callable[[], None]], ...] = (
        ("drain", lambda: _drain(delivery, report)),
        ("end state of every design world", lambda: _end_state(provider, report)),
    )
    for name, step in steps:
        try:
            step()
        except Exception as exc:  # noqa: BLE001 - a failed check, shown in the table
            report.check(name, False, f"{type(exc).__name__}: {exc}"[:300])
    for name, test in TARGETED:
        try:
            detail = test(ctx, provider, delivery)
            report.check(name, True, detail)
        except Exception as exc:  # noqa: BLE001 - a failed check, shown in the table
            report.check(name, False, f"{type(exc).__name__}: {exc}"[:300])
    return report
