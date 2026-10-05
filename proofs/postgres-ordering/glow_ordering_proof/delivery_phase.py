"""The delivery phase (P06.2 Stage A, items 2 and 3): the app's outbox delivery, run
in-process against the fixture provider on the disposable database.

It runs after both subjects' oracles, because delivery updates the rows the oracle reads
commit times from. First it drains the outbox: every chat event the adapter's cases,
races and controls wrote is delivered, first in, first out, as one provider call each.
Then it checks, for every world the design tags made, that the provider ended where the
database says it should: an active match's channel holds exactly its two members, a
revoked one holds none, every authorized message was delivered once and none after its
channel's members were removed, and every suspended or deleted member's provider user is
deactivated with one token revocation per epoch bump. Last, it runs the targeted cases:
each event kind, a retry after a fixture failure (before and after the provider acted),
provider text kept out, a revocation committed after a send's authorization and before
its delivery, and a dead letter.

No provider is called but the in-memory fixture; nothing reaches a network.
"""

from __future__ import annotations

import re
import sys
import time
from collections.abc import Callable
from typing import Any
from uuid import UUID

from glow_chat import events
from glow_chat.delivery import Delivery, OutboxDelivery
from glow_domain.chat_provider import OPERATIONS
from glow_domain.chat_provider_fixtures import FixtureChatProvider

from glow_ordering_proof import oracle
from glow_ordering_proof.cases import Context, World, make_world, send_request
from glow_ordering_proof.interface import Result
from glow_ordering_proof.observe import WORLD_TABLE, LogContext
from glow_ordering_proof.results import DeliveryReport

DRAIN_MAX_EVENTS = 60_000
DRAIN_MAX_SECONDS = 300.0
REF_FORM = re.compile(r"[0-9a-f]{32}")
# Text a provider could put in an error; it must never be kept or shown.
PROVIDER_TEXT = "fixture-provider-said: upstream detail that must not be kept"


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
        if identity.state != ("deactivated" if revoked else "active"):
            problems.append(f"identity {identity.state} for a {row.state} account")
        if user is None or user.active == revoked:
            problems.append(f"provider user state for a {row.state} account")
        elif len(user.token_cutoffs) != row.session_epoch - 1:
            problems.append(
                f"{len(user.token_cutoffs)} token revocations at epoch {row.session_epoch}"
            )
    dead = m.OutboxEvent.objects.filter(schema_version=oracle.ADAPTER_SCHEMA, state="dead_letter")
    design_matches = {match for match, _, _ in worlds}
    for event in dead:
        owner = event.aggregate_id
        if event.event_type == "message_submitted":
            owner = (
                m.MessageSubmission.objects.filter(pk=event.payload_ref)
                .values_list("binding__match_id", flat=True)
                .first()
            )
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


def _deliver(delivery: OutboxDelivery) -> list[Delivery]:
    done: list[Delivery] = delivery.deliver_due(limit=100)
    return done


def _receipt(result: Result) -> UUID:
    if result.receipt is None:
        raise DeliveryCheckFailed(f"no receipt: {result.label()}")
    return result.receipt.submission_id


def _each_kind(ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery) -> str:
    m = _models()
    world = _world(ctx, "each_kind")
    first = _deliver(delivery)
    _require([d.event_type for d in first] == ["match_activated"], first)
    binding = m.ChatBinding.objects.get(match_id=world.match)
    refs = {
        i.user_ref for i in m.ChatIdentity.objects.filter(account_id__in=(world.low, world.high))
    }
    _require(binding.state == "active", binding.state)
    channel = provider.channels[binding.channel_ref]
    _require(
        set(channel.created_members) == refs and channel.members == refs,
        "the delivery check did not hold",
    )
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
    _require(
        [(d.event_type, d.outcome) for d in second] == [("message_submitted", "delivered")],
        "the delivery check did not hold",
    )
    submission = m.MessageSubmission.objects.get(pk=_receipt(sent))
    _require(submission.state == "accepted")
    _require(
        [i for i, _, _ in channel.messages] == [submission.provider_message_ref],
        "the delivery check did not hold",
    )
    blocked = ctx.subject.block(world.high, world.low)
    _require(blocked.outcome == "applied", blocked.label())
    third = _deliver(delivery)
    _require(
        [(d.event_type, d.outcome) for d in third] == [("contact_revoked", "delivered")],
        "the delivery check did not hold",
    )
    binding.refresh_from_db()
    _require(
        binding.state == "revoked" and channel.members == set() and len(channel.messages) == 1,
        "the delivery check did not hold",
    )
    other = _world(ctx, "each_kind_account")
    _deliver(delivery)
    suspended = ctx.subject.suspend(other.low)
    _require(suspended.outcome == "applied", suspended.label())
    fourth = _deliver(delivery)
    _require(
        [(d.event_type, d.outcome) for d in fourth]
        == [
            ("access_revoked", "delivered"),
            ("session_epoch_bumped", "delivered"),
        ],
        fourth,
    )
    identity = m.ChatIdentity.objects.get(account_id=other.low)
    event = m.OutboxEvent.objects.get(event_type="session_epoch_bumped", aggregate_id=other.low)
    user = provider.users[identity.user_ref]
    _require(identity.state == "deactivated" and not user.active)
    _require(
        identity.tokens_revoked_before == event.available_at == user.token_cutoffs[-1],
        "the delivery check did not hold",
    )
    return (
        "channel created with exactly the two members, message sent with its committed ID,"
        " both members removed on a block with the history kept, user deactivated and its"
        " tokens revoked at the epoch bump's time"
    )


def _retry(ctx: Context, provider: FixtureChatProvider, delivery: OutboxDelivery) -> str:
    m = _models()
    world = _world(ctx, "retry")
    binding = m.ChatBinding.objects.get(match_id=world.match)
    provider.fail_next("create_channel")
    failed = _deliver(delivery)
    _require(
        [(d.outcome, d.code, d.attempts) for d in failed] == [("retry", "provider_unavailable", 1)],
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
    return (
        "a failed channel creation retried with the same channel ID (one channel); a lost"
        " answer to a send retried with the committed message ID (one message, the retry"
        " found it); provider text mapped to provider_unavailable and kept nowhere"
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
        [(d.event_type, d.outcome) for d in done]
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
    outcomes: list[str] = []
    for _ in range(delivery.max_attempts):
        provider.fail_next("create_channel")
        outcomes.extend(d.outcome for d in _deliver(delivery))
    _require(outcomes == ["retry"] * (delivery.max_attempts - 1) + ["dead_letter"], outcomes)
    binding = m.ChatBinding.objects.get(match_id=world.match)
    _require(
        binding.state == "failed" and binding.channel_ref not in provider.channels,
        "the delivery check did not hold",
    )
    refused = ctx.subject.send(send_request(world, key="k-dead"))
    _require(
        refused.outcome == "refused" and refused.reason == "binding_not_active", refused.label()
    )
    return (
        f"after {delivery.max_attempts} failed attempts the event is dead-lettered and the"
        " binding failed; a send to it is refused"
    )


TARGETED: tuple[tuple[str, Callable[[Context, FixtureChatProvider, OutboxDelivery], str]], ...] = (
    ("delivery of each event kind", _each_kind),
    ("a retry after a fixture failure", _retry),
    ("a revocation after the authorization, before the delivery", _revocation_before_delivery),
    ("a dead letter after the last attempt", _dead_letter),
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
