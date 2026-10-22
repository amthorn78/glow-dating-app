"""Outbox delivery to the chat provider (P06.2 Stage A, items 2 and 3; Stage B1, CX4,
CX6, F1 and F3).

Each due event of the chat schema becomes exactly one provider call:

1. **Lease.** The undelivered chat events are read in delivery order, and each in turn
   is locked by its key (``FOR UPDATE``) in one transaction and, when it is due, marked
   ``leased`` with a lease expiry and one more attempt. Everything the call needs is read
   here: the committed user ID, the committed channel ID, the members' provider user
   IDs, the committed message ID.
2. **Call.** One provider call, outside any transaction. A provider error is kept only
   as its Glow code (``glow_domain.chat_provider.error_code``); no provider text is
   stored, logged or returned.
3. **Receipt.** In a second transaction the event is locked again and, if the lease is
   still this one, the receipt is recorded (the ``ChatIdentity``'s state or token
   cut-off, ``ChatBinding.state``, the ``MessageSubmission``'s state with its committed
   ``provider_message_ref``) and the event marked ``delivered``.

A retry repeats the same call with the same committed identifiers, so the provider
never gets a second user, channel, message or member. Delivery is first in, first out:
events are taken in ``(available_at, sequence)`` order, where ``sequence`` is the
database-assigned order column (DM-15 3.1), so the events one transaction wrote are
delivered in the order it wrote them; a failed event that may be retried stays at the
head, so nothing overtakes it. After ``max_attempts``, or on a final error code, the
event is dead-lettered.

**Provisioning before the channel** (CX4; DM-15 3.1 to 3.5): a member's identity is
``pending`` until its provisioning is delivered. A channel event that finds a member not
``active`` does not wait: its provisioning, ordered ahead of it, is settled, so the
channel dead-letters with ``member_unavailable``.

**The reconciliation mark** (F3, CX6; DM-15 4.5): a dead letter of a provisioning, a
channel's creation, a removal, a deactivation or a token revocation marks the row it
concerns, the identity or the binding, with ``reconcile_code``, the Glow code of its
last attempt, whether or not a call was made (B1-C1, R3); only an event whose row does
not exist marks nothing. The ``pending`` binding a channel event failed to create
becomes ``failed``. A message is never delivered into a marked, ``revoked`` or
``failed`` binding. A revocation of such a binding still makes its removal, and a
channel the provider does not have counts as removed; a deactivation or token
revocation of a marked identity still makes its call, and a user the provider does not
have counts as deactivated or revoked. Reconciliation itself is P11's (the data
model, "Chat contact and the outbox").

**The cut-off** of a per-user token revocation is the epoch bump's time read after its
account lock (``event.available_at``); it is sent rounded up to the next whole second,
strictly (DM-15 5.2), and stored exact.

Stage A runs this in-process under the disposable-database proof, against the fixture
provider; there is no deployed worker before P11 (DM-13 item 9), and one deliverer at a
time is assumed.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal
from uuid import UUID

from django.db import connection, transaction

from glow_chat import events
from glow_domain.chat_provider import (
    CHANNEL_UNAVAILABLE,
    MEMBER_UNAVAILABLE,
    PROVIDER_REJECTED,
    PROVIDER_UNAVAILABLE,
    RETRYABLE,
    ChatProvider,
    ChatProviderError,
    ProviderReceipt,
    error_code,
)
from glow_domain.chat_tokens import revocation_cutoff_sent
from glow_persistence.models import (
    ChatBinding,
    ChatIdentity,
    Match,
    MessageSubmission,
    OutboxEvent,
)

MAX_ATTEMPTS = 5
LEASE = timedelta(seconds=30)

DeliveryOutcome = Literal["delivered", "skipped", "retry", "dead_letter", "lost_lease"]


@dataclass(frozen=True)
class Delivery:
    """What one delivery did. ``code`` is a Glow code, never provider text."""

    event_id: UUID
    event_type: str
    outcome: DeliveryOutcome
    attempts: int
    code: str | None = None
    provider_called: bool = False
    already: bool = False


@dataclass(frozen=True)
class _Plan:
    """The one call an event needs, read under its lease; ``None`` call: none needed.
    ``on_dead_letter`` takes the dead letter's Glow code."""

    call: Callable[[], ProviderReceipt] | None
    record: Callable[[ProviderReceipt, datetime], None]
    on_dead_letter: Callable[[str | None], None]
    code: str | None = None  # set when the event can only be dead-lettered


def _clock() -> datetime:
    with connection.cursor() as cursor:
        cursor.execute("SELECT clock_timestamp()")
        value = cursor.fetchone()[0]
    assert isinstance(value, datetime)
    return value


def _nothing(*_: object) -> None:
    return None


def _mark_binding(binding_id: UUID, code: str | None, *, fail_pending: bool) -> None:
    """The reconciliation mark on a binding (F3, CX6): the dead letter's Glow code, and
    ``failed`` for a channel whose creation was never confirmed."""
    row = ChatBinding.objects.select_for_update().get(pk=binding_id)
    fields = ["reconcile_code", "version", "updated_at"]
    row.reconcile_code = code or PROVIDER_UNAVAILABLE
    if fail_pending and row.state == "pending":
        row.state = "failed"
        fields.append("state")
    row.version += 1
    row.save(update_fields=fields)


def _mark_identity(identity_id: UUID, code: str | None) -> None:
    """The reconciliation mark on an identity (F3; DM-15 3.3)."""
    row = ChatIdentity.objects.select_for_update().get(pk=identity_id)
    row.reconcile_code = code or PROVIDER_UNAVAILABLE
    row.version += 1
    row.save(update_fields=["reconcile_code", "version", "updated_at"])


def _counts_as_done(call: Callable[[], ProviderReceipt], ref: str, code: str) -> ProviderReceipt:
    """A removal, deactivation or revocation whose object the provider does not have
    counts as done (CX6; DM-15 3.3 and 4.5): only ``code``, only for this plan."""
    try:
        return call()
    except ChatProviderError as error:
        if error.code == code:
            return ProviderReceipt(ref, already=True)
        raise


class OutboxDelivery:
    def __init__(
        self,
        provider: ChatProvider,
        *,
        max_attempts: int = MAX_ATTEMPTS,
        lease: timedelta = LEASE,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("at least one attempt")
        self.provider = provider
        self.max_attempts = max_attempts
        self.lease = lease

    # -- what each event needs ------------------------------------------------------

    def _identity(self, account_id: UUID) -> Any:
        return ChatIdentity.objects.filter(
            account_id=account_id, provider=self.provider.name
        ).first()

    def _members(self, match_id: UUID) -> list[Any] | None:
        """Both members' identities, or None when the match or an identity is missing."""
        pair = (
            Match.objects.filter(pk=match_id)
            .values_list("account_low_id", "account_high_id")
            .first()
        )
        if pair is None:
            return None
        identities = [self._identity(account_id) for account_id in pair]
        if any(identity is None for identity in identities):
            return None
        return identities

    def _plan(self, event: Any) -> _Plan:
        kind = event.event_type
        provider = self.provider
        if kind == events.IDENTITY_CREATED:
            identity = ChatIdentity.objects.filter(pk=event.payload_ref).first()
            if identity is None:
                # No row to mark.
                return _Plan(None, _nothing, _nothing, PROVIDER_REJECTED)
            identity_id = identity.id
            user_ref = identity.user_ref

            def mark(code: str | None) -> None:
                _mark_identity(identity_id, code)

            if identity.provider != provider.name:
                # F3: every dead-lettered event that concerns a row marks it (B1-C1, R3).
                return _Plan(None, _nothing, mark, PROVIDER_REJECTED)

            def provisioned(receipt: ProviderReceipt, now: datetime) -> None:
                # DM-15 3.2: provisioned only on the provider's receipt.
                row = ChatIdentity.objects.select_for_update().get(pk=identity_id)
                if row.state == "pending":
                    row.state = "active"
                    row.version += 1
                    row.save(update_fields=["state", "version", "updated_at"])

            return _Plan(lambda: provider.provision_user(user_ref), provisioned, mark)

        if kind == events.MATCH_ACTIVATED:
            binding = ChatBinding.objects.filter(pk=event.payload_ref).first()
            if binding is None:
                # No row to mark.
                return _Plan(None, _nothing, _nothing, PROVIDER_REJECTED)
            binding_id = binding.id

            def failed_binding(code: str | None) -> None:
                _mark_binding(binding_id, code, fail_pending=True)

            if binding.provider != provider.name:
                return _Plan(None, _nothing, failed_binding, PROVIDER_REJECTED)
            members = self._members(binding.match_id)
            if members is None or any(member.state != "active" for member in members):
                # DM-15 3.2: a member not provisioned (its provisioning, ordered ahead,
                # was dead-lettered) or already deactivated: never wait, never call.
                return _Plan(None, _nothing, failed_binding, MEMBER_UNAVAILABLE)
            pair: tuple[str, str] = (members[0].user_ref, members[1].user_ref)
            channel_id = binding.channel_ref

            def created(receipt: ProviderReceipt, now: datetime) -> None:
                row = ChatBinding.objects.select_for_update().get(pk=binding_id)
                if row.state == "pending":
                    row.state = "active"
                    row.version += 1
                    row.save(update_fields=["state", "version", "updated_at"])

            return _Plan(lambda: provider.create_channel(channel_id, pair), created, failed_binding)

        if kind == events.MESSAGE_SUBMITTED:
            submission = MessageSubmission.objects.filter(pk=event.payload_ref).first()
            if submission is None:
                # No row to mark; a message's dead letter fails its submission, never a mark.
                return _Plan(None, _nothing, _nothing, PROVIDER_REJECTED)
            submission_id = submission.id

            def failed_submission(code: str | None) -> None:
                MessageSubmission.objects.filter(pk=submission_id, state="pending").update(
                    state="failed"
                )

            binding = submission.binding
            if (
                binding.provider != provider.name
                or binding.state in ("revoked", "failed")
                or binding.reconcile_code is not None
            ):
                # Never into a channel whose members were removed, that never existed, or
                # whose state at the provider is in doubt (DM-15 4.5).
                return _Plan(None, _nothing, failed_submission, CHANNEL_UNAVAILABLE)
            if binding.state != "active":
                # The channel's creation is still ahead of this message: wait for it.
                return _Plan(None, _nothing, failed_submission, PROVIDER_UNAVAILABLE)
            sender = self._identity(submission.actor_id)
            if sender is None or sender.state != "active" or submission.text is None:
                return _Plan(None, _nothing, failed_submission, MEMBER_UNAVAILABLE)
            channel_id = binding.channel_ref
            sender_ref = sender.user_ref
            message_id = submission.provider_message_ref
            text = submission.text

            def accepted(receipt: ProviderReceipt, now: datetime) -> None:
                row = MessageSubmission.objects.select_for_update().get(pk=submission_id)
                if row.state == "pending" and receipt.ref == row.provider_message_ref:
                    row.state = "accepted"
                    row.version += 1
                    row.save(update_fields=["state", "version", "updated_at"])

            return _Plan(
                lambda: provider.send_message(channel_id, sender_ref, message_id, text),
                accepted,
                failed_submission,
            )

        if kind == events.CONTACT_REVOKED:
            binding = ChatBinding.objects.filter(match_id=event.aggregate_id).first()
            if binding is None:
                # No channel was ever bound: nothing to remove, and no dead letter.
                return _Plan(None, _nothing, _nothing)
            binding_id = binding.id

            def mark(code: str | None) -> None:
                _mark_binding(binding_id, code, fail_pending=False)

            if binding.provider != provider.name:
                return _Plan(None, _nothing, mark, PROVIDER_REJECTED)
            members = self._members(event.aggregate_id)
            if members is None or binding.channel_ref is None:
                # F3: a removal that cannot be made still marks its binding (B1-C1, R3).
                return _Plan(None, _nothing, mark, MEMBER_UNAVAILABLE)
            both: tuple[str, str] = (members[0].user_ref, members[1].user_ref)
            channel_id = binding.channel_ref

            def remove() -> ProviderReceipt:
                # CX6 (DM-15 4.5): a failed or marked binding may still have its channel
                # at the provider, so the removal is always made; a channel the provider
                # does not have counts as removed.
                return _counts_as_done(
                    lambda: provider.remove_members(channel_id, both),
                    channel_id,
                    CHANNEL_UNAVAILABLE,
                )

            def removed(receipt: ProviderReceipt, now: datetime) -> None:
                # The mark's reason is kept: the row stays P11's to reconcile.
                row = ChatBinding.objects.select_for_update().get(pk=binding_id)
                if row.state != "revoked":
                    row.state = "revoked"
                    row.version += 1
                    row.save(update_fields=["state", "version", "updated_at"])

            return _Plan(remove, removed, mark)

        if kind in (events.ACCESS_REVOKED, events.SESSION_EPOCH_BUMPED):
            identity = self._identity(event.aggregate_id)
            if identity is None:
                # No provider user was ever committed for the account: nothing to do.
                return _Plan(None, _nothing, _nothing)
            identity_id = identity.id
            user_ref = identity.user_ref

            def mark(code: str | None) -> None:
                _mark_identity(identity_id, code)

            if kind == events.ACCESS_REVOKED:

                def deactivate() -> ProviderReceipt:
                    # DM-15 3.3: a user the provider does not have counts as deactivated.
                    return _counts_as_done(
                        lambda: provider.deactivate_user(user_ref), user_ref, MEMBER_UNAVAILABLE
                    )

                def deactivated(receipt: ProviderReceipt, now: datetime) -> None:
                    row = ChatIdentity.objects.select_for_update().get(pk=identity_id)
                    if row.state != "deactivated":
                        row.state = "deactivated"
                        row.version += 1
                        row.save(update_fields=["state", "version", "updated_at"])

                return _Plan(deactivate, deactivated, mark)
            # F1 (DM-14 item 3, point 4): the cut-off is the bump's time read after its
            # account lock, kept exact here and sent at the next whole second (point 3).
            cutoff = event.available_at
            sent = revocation_cutoff_sent(cutoff)

            def revoke() -> ProviderReceipt:
                # DM-15 3.3: a user the provider does not have counts as revoked.
                return _counts_as_done(
                    lambda: provider.revoke_user_tokens(user_ref, sent),
                    user_ref,
                    MEMBER_UNAVAILABLE,
                )

            def revoked(receipt: ProviderReceipt, now: datetime) -> None:
                row = ChatIdentity.objects.select_for_update().get(pk=identity_id)
                if row.tokens_revoked_before is None or row.tokens_revoked_before < cutoff:
                    row.tokens_revoked_before = cutoff
                    row.version += 1
                    row.save(update_fields=["tokens_revoked_before", "version", "updated_at"])

            return _Plan(revoke, revoked, mark)

        # A kind this delivery does not know concerns no row it can mark.
        return _Plan(None, _nothing, _nothing, PROVIDER_REJECTED)

    # -- one event --------------------------------------------------------------------

    def _due_ids(self, count: int) -> list[UUID]:
        """The first ``count`` undelivered chat events, in delivery order: by
        ``available_at``, then the database-assigned ``sequence`` (DM-15 3.1)."""
        ids = (
            OutboxEvent.objects.filter(
                schema_version=events.CHAT_SCHEMA_VERSION,
                event_type__in=tuple(events.DELIVERED),
                state__in=("pending", "leased"),
            )
            .order_by("available_at", "sequence")
            .values_list("id", flat=True)[:count]
        )
        return list(ids)

    def deliver_next(self) -> Delivery | None:
        """Deliver the head of the chat outbox, or return None when it is not due."""
        head = self._due_ids(1)
        return self._deliver(head[0]) if head else None

    def _deliver(self, event_id: UUID) -> Delivery | None:
        """Lease one event by its key, call the provider once, record the receipt. None
        when the event is not due, already settled, or held by a live lease."""
        with transaction.atomic():
            event = OutboxEvent.objects.select_for_update().filter(pk=event_id).first()
            if event is None or event.state not in ("pending", "leased"):
                return None
            now = _clock()
            if event.available_at > now:
                return None
            if event.state == "leased" and event.lease_expires_at > now:
                return None  # held by a live lease: nothing overtakes it
            event.state = "leased"
            event.lease_expires_at = now + self.lease
            event.attempts += 1
            event.version += 1
            event.save(
                update_fields=["state", "lease_expires_at", "attempts", "version", "updated_at"]
            )
            attempts = event.attempts
            plan = self._plan(event)
            if plan.call is None:
                return self._settle(event, plan, None, plan.code, now, provider_called=False)
        receipt: ProviderReceipt | None = None
        code: str | None = None
        try:
            receipt = plan.call()
        except Exception as error:  # noqa: BLE001 - kept only as its Glow code
            code = error_code(error)
        with transaction.atomic():
            event = OutboxEvent.objects.select_for_update().get(pk=event.id)
            if event.state != "leased" or event.attempts != attempts:
                return Delivery(event.id, event.event_type, "lost_lease", attempts, code, True)
            return self._settle(event, plan, receipt, code, _clock(), provider_called=True)

    def _settle(
        self,
        event: Any,
        plan: _Plan,
        receipt: ProviderReceipt | None,
        code: str | None,
        now: datetime,
        *,
        provider_called: bool,
    ) -> Delivery:
        """Inside the event's transaction: record the receipt and mark it delivered, or
        release it for a retry, or dead-letter it and mark the row it concerns."""
        if code is None:
            if receipt is not None:
                plan.record(receipt, now)
            event.state = "delivered"
            event.delivered_at = now
            event.lease_expires_at = None
            event.version += 1
            event.save(
                update_fields=["state", "delivered_at", "lease_expires_at", "version", "updated_at"]
            )
            outcome: DeliveryOutcome = "delivered" if provider_called else "skipped"
            already = receipt.already if receipt is not None else False
            return Delivery(
                event.id, event.event_type, outcome, event.attempts, None, provider_called, already
            )
        if code in RETRYABLE and event.attempts < self.max_attempts:
            # Back to the head of the queue: available_at is unchanged.
            event.state = "pending"
            event.lease_expires_at = None
            event.version += 1
            event.save(update_fields=["state", "lease_expires_at", "version", "updated_at"])
            return Delivery(
                event.id, event.event_type, "retry", event.attempts, code, provider_called
            )
        plan.on_dead_letter(code)
        event.state = "dead_letter"
        event.lease_expires_at = None
        event.version += 1
        event.save(update_fields=["state", "lease_expires_at", "version", "updated_at"])
        return Delivery(
            event.id, event.event_type, "dead_letter", event.attempts, code, provider_called
        )

    # -- the loop -----------------------------------------------------------------------

    def deliver_due(self, *, limit: int, batch: int = 100) -> list[Delivery]:
        """Deliver due events in order until none is due, ``limit`` is reached, or one
        must be retried (it stays at the head; the next pass tries it first). The heads
        are read ``batch`` at a time and each is leased by its key; events of one
        channel or one user commit in their delivery order (their writers share an
        account lock), so a batch never puts one of them before an earlier one."""
        done: list[Delivery] = []
        while len(done) < limit:
            ids = self._due_ids(min(batch, limit - len(done)))
            if not ids:
                break
            for event_id in ids:
                delivery = self._deliver(event_id)
                if delivery is None:
                    return done
                done.append(delivery)
                if delivery.outcome in ("retry", "lost_lease"):
                    return done
        return done
