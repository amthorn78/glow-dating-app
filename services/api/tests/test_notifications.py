"""P06.3: privacy-safe notifications at fixture scope (the brief's Outcome items 1 and 2).

The composer (``glow_domain.notifications``): its recipients, its content, its refusals read on
each delivery, and no duplicate push. F12's devices and settings: the transitions per
installation, the session binding, token custody (with the custody test, 3.2) and the defaults.
DM-44's "Tried" tables are cases here. Everything runs offline on the fixtures of
``glow_domain.notification_fixtures``; no provider, network or database is touched.
"""

import ast
import json
import logging
import re
import subprocess
import sys
import unittest
import uuid
from dataclasses import dataclass, fields
from datetime import timedelta
from pathlib import Path
from uuid import UUID

from glow_domain import chat
from glow_domain import notifications as n
from glow_domain.notification_fixtures import (
    FixtureNotificationWorld,
    FixturePushTransport,
    FixtureTokenStore,
    NotificationFixture,
    notification_fixture,
    synthetic_token,
)

API_ROOT = Path(__file__).resolve().parents[1]
UUID_TEXT = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
REASON_FORM = re.compile(r"[a-z_]+")


def register(device: UUID, token: str, version: int, key: str) -> dict[str, object]:
    return {
        "operation": "device",
        "meta": {"idempotency_key": key, "expected_version": version},
        "device_id": str(device),
        "action": "register",
        "provider_token": token,
    }


def revoke(device: UUID, version: int, key: str) -> dict[str, object]:
    return {
        "operation": "device",
        "meta": {"idempotency_key": key, "expected_version": version},
        "device_id": str(device),
        "action": "revoke",
        "provider_token": None,
    }


def settings(match: bool, message: bool, version: int, key: str) -> dict[str, object]:
    return {
        "operation": "notifications",
        "meta": {"idempotency_key": key, "expected_version": version},
        "match_notifications": match,
        "message_notifications": message,
    }


@dataclass
class Member:
    account: UUID
    session: UUID
    device: UUID

    @property
    def caller(self) -> n.Caller:
        return n.Caller(self.account, self.session, self.device)


class World:
    """Two members with a match (``first`` liked first; ``second``'s like completed it) and an
    accepted message from ``second`` to ``first``."""

    def __init__(self) -> None:
        self.fx: NotificationFixture = notification_fixture()
        world = self.fx.world
        self.first = self.member()
        self.second = self.member()
        self.match_id = world.add_match(self.first.account, completed_by=self.second.account)
        self.message_id = world.add_message(self.match_id, sender=self.second.account)
        self.keys = 0

    @property
    def service(self) -> n.NotificationService:
        return self.fx.service

    @property
    def world(self) -> FixtureNotificationWorld:
        return self.fx.world

    @property
    def tokens(self) -> FixtureTokenStore:
        return self.fx.tokens

    @property
    def transport(self) -> FixturePushTransport:
        return self.fx.transport

    def member(self) -> Member:
        account = self.fx.world.add_account()
        return Member(account, self.fx.world.open_session(account), uuid.uuid4())

    def key(self) -> str:
        self.keys += 1
        return f"key-{self.keys}"

    def version(self, member: Member) -> int:
        registration = self.service.registration(member.account, member.device)
        return 0 if registration is None else registration.version

    def register(self, member: Member, token: str | None = None) -> n.CommandResult:
        token = token or synthetic_token(self.key())
        intent = register(member.device, token, self.version(member), self.key())
        return self.service.device(member.caller, intent)

    def revoke(self, member: Member) -> n.CommandResult:
        return self.service.device(
            member.caller, revoke(member.device, self.version(member), self.key())
        )

    def set(self, member: Member, match: bool, message: bool) -> n.CommandResult:
        intent = settings(match, message, self.version(member), self.key())
        return self.service.settings(member.caller, intent)

    def enable(self, member: Member) -> None:
        assert self.register(member).outcome == "applied"
        assert self.set(member, True, True).outcome == "applied"

    def message_trigger(self, recipient: Member | None = None) -> n.MessageAccepted:
        target = recipient or self.first
        return n.MessageAccepted(uuid.uuid4(), self.match_id, self.message_id, target.account)

    def match_trigger(self, recipient: Member | None = None) -> n.MatchActivated:
        return n.MatchActivated(uuid.uuid4(), self.match_id, (recipient or self.first).account)

    def accepted(self) -> list[str]:
        return [
            push.idempotency_key for push in self.transport.recorded if push.outcome == "accepted"
        ]


# -- Outcome 1: the composer -------------------------------------------------------------------


class ComposerRecipientTests(unittest.TestCase):
    def test_a_message_notifies_the_other_member_never_its_sender(self) -> None:
        w = World()
        w.enable(w.first)
        w.enable(w.second)
        to_sender = w.service.deliver(w.message_trigger(w.second))
        self.assertEqual((to_sender.outcome, to_sender.reason), ("refused", n.RECIPIENT_IS_SENDER))
        self.assertEqual(w.transport.recorded, [])
        to_other = w.service.deliver(w.message_trigger(w.first))
        self.assertEqual((to_other.outcome, to_other.sent), ("sent", 1))
        self.assertEqual(len(w.transport.recorded), 1)

    def test_a_match_notifies_the_earlier_liker_never_the_member_who_completed_it(self) -> None:
        w = World()
        w.enable(w.first)
        w.enable(w.second)
        completer = w.service.deliver(w.match_trigger(w.second))
        self.assertEqual(
            (completer.outcome, completer.reason), ("refused", n.RECIPIENT_COMPLETED_MATCH)
        )
        earlier = w.service.deliver(w.match_trigger(w.first))
        self.assertEqual((earlier.outcome, earlier.sent), ("sent", 1))

    def test_a_recipient_outside_the_match_gets_nothing(self) -> None:
        w = World()
        stranger = w.member()
        w.enable(stranger)
        for trigger in (w.match_trigger(stranger), w.message_trigger(stranger)):
            result = w.service.deliver(trigger)
            self.assertEqual((result.outcome, result.reason), ("refused", chat.NOT_A_MEMBER))
        self.assertEqual(w.transport.recorded, [])

    def test_at_most_one_push_per_active_device_of_the_recipient(self) -> None:
        w = World()
        w.enable(w.first)
        phone = Member(w.first.account, w.first.session, uuid.uuid4())
        self.assertEqual(w.register(phone).outcome, "applied")
        result = w.service.deliver(w.message_trigger())
        self.assertEqual((result.outcome, result.sent), ("sent", 2))
        references = [push.reference for push in w.transport.recorded]
        self.assertEqual(len(set(references)), 2)


class ComposerContentTests(unittest.TestCase):
    def test_the_push_carries_only_the_kind_glows_wording_and_a_fixed_route(self) -> None:
        w = World()
        w.enable(w.first)
        w.service.deliver(w.match_trigger())
        w.service.deliver(w.message_trigger())
        payloads = [push.payload for push in w.transport.recorded]
        self.assertEqual(
            payloads,
            [
                {
                    "title": "Glow",
                    "body": "You have a new match.",
                    "data": {"kind": "match", "route": "/matches"},
                },
                {
                    "title": "Glow",
                    "body": "You have a new message.",
                    "data": {"kind": "message", "route": "/conversations"},
                },
            ],
        )
        for payload in payloads:
            text = json.dumps(payload)
            self.assertIsNone(UUID_TEXT.search(text), "an identifier in a push")
            for value in (str(w.match_id), str(w.message_id), str(w.first.account), "1", "2"):
                self.assertNotIn(value, text)

    def test_the_wording_and_routes_are_the_fixed_tables(self) -> None:
        self.assertEqual(n.TITLE, "Glow")
        self.assertEqual(
            dict(n.WORDING),
            {"match": "You have a new match.", "message": "You have a new message."},
        )
        self.assertEqual(dict(n.ROUTES), {"match": "/matches", "message": "/conversations"})
        self.assertEqual(n.KINDS, ("match", "message"))

    def test_the_trigger_types_have_no_field_for_a_body_name_birth_compatibility_or_provider(
        self,
    ) -> None:
        self.assertEqual(n.trigger_fields(n.MatchActivated), {"event_id", "match_id", "recipient"})
        self.assertEqual(
            n.trigger_fields(n.MessageAccepted),
            {"event_id", "match_id", "submission_id", "recipient"},
        )
        for trigger_type in (n.MatchActivated, n.MessageAccepted):
            for item in fields(trigger_type):
                self.assertEqual(item.type, "UUID")

    def test_the_composer_refuses_a_trigger_with_any_extra_field(self) -> None:
        w = World()
        w.enable(w.first)

        @dataclass(frozen=True)
        class WithBody(n.MessageAccepted):
            text: str = "a body"

        @dataclass(frozen=True)
        class Lookalike:
            event_id: UUID
            match_id: UUID
            submission_id: UUID
            recipient: UUID
            name: str

        good = w.message_trigger()
        extra = WithBody(good.event_id, good.match_id, good.submission_id, good.recipient)
        lookalike = Lookalike(
            good.event_id, good.match_id, good.submission_id, good.recipient, "Fictional"
        )
        wrong_type = n.MessageAccepted(
            good.event_id,
            good.match_id,
            good.submission_id,
            str(good.recipient),  # type: ignore[arg-type]
        )
        for trigger in (extra, lookalike, wrong_type, {"event_id": good.event_id}, None):
            with self.subTest(trigger=type(trigger).__name__):
                result = w.service.deliver(trigger)
                self.assertEqual((result.outcome, result.reason), ("refused", n.TRIGGER_INVALID))
        self.assertEqual(w.transport.recorded, [])
        with self.assertRaises(AttributeError):
            object.__setattr__(good, "text", "a body")

    def test_a_trigger_from_an_event_payload_has_exactly_its_fields(self) -> None:
        event, match, submission, recipient = (str(uuid.uuid4()) for _ in range(4))
        parsed = n.parse_trigger(
            "message",
            {
                "event_id": event,
                "match_id": match,
                "submission_id": submission,
                "recipient": recipient,
            },
        )
        self.assertIsInstance(parsed, n.MessageAccepted)
        parsed_match = n.parse_trigger(
            "match", {"event_id": event, "match_id": match, "recipient": recipient}
        )
        self.assertIsInstance(parsed_match, n.MatchActivated)
        base = {"event_id": event, "match_id": match, "recipient": recipient}
        for kind, data in (
            ("match", {**base, "text": "a body"}),
            ("match", {**base, "name": "Fictional"}),
            ("match", {**base, "birth_date": "1990-06-15"}),
            ("match", {**base, "compatibility": "ready"}),
            ("match", {**base, "provider_message_id": "x"}),
            ("match", {"event_id": event, "match_id": match}),
            ("match", {**base, "recipient": recipient.upper()}),
            ("message", base),
            ("unknown", base),
        ):
            with self.subTest(kind=kind, keys=sorted(data)):
                with self.assertRaises(n.IntentError) as raised:
                    n.parse_trigger(kind, data)
                self.assertEqual(str(raised.exception), n.INTENT_INVALID)


class ComposerRefusalTests(unittest.TestCase):
    """DM-44 2.2's "Tried" cases, and the read rule's other checks, for either member."""

    def refused(self, change: str, member: str, expected: str) -> None:
        w = World()
        w.enable(w.first)
        target = getattr(w, member).account
        other = w.second.account if target == w.first.account else w.first.account
        world = w.world
        actions = {
            "block_by": lambda: world.block(target, other),
            "block_of": lambda: world.block(other, target),
            "suspended": lambda: world.set_account(target, "suspended"),
            "deletion_pending": lambda: world.set_account(target, "deletion_pending"),
            "deleted": lambda: world.set_account(target, "deleted"),
            "paused": lambda: world.set_profile(target, "paused"),
            "restricted": lambda: world.set_profile(target, "restricted"),
            "withdrawn": lambda: world.set_consent(target, "withdrawn"),
            "unmatched": lambda: world.set_match(w.match_id, "unmatched"),
            "match_restricted": lambda: world.set_match(w.match_id, "restricted"),
        }
        actions[change]()
        for trigger in (w.match_trigger(), w.message_trigger()):
            result = w.service.deliver(trigger)
            self.assertEqual((result.outcome, result.reason), ("refused", expected))
        self.assertEqual(w.transport.recorded, [])

    def test_a_block_either_way_refuses(self) -> None:
        for member in ("first", "second"):
            for change in ("block_by", "block_of"):
                with self.subTest(member=member, change=change):
                    self.refused(change, member, chat.BLOCKED)

    def test_an_account_that_is_not_active_refuses(self) -> None:
        for member in ("first", "second"):
            for change in ("suspended", "deletion_pending", "deleted"):
                with self.subTest(member=member, change=change):
                    self.refused(change, member, chat.ACCOUNT_NOT_ACTIVE)

    def test_a_paused_or_restricted_profile_refuses(self) -> None:
        for member in ("first", "second"):
            for change in ("paused", "restricted"):
                with self.subTest(member=member, change=change):
                    self.refused(change, member, chat.PROFILE_UNAVAILABLE)

    def test_a_withdrawn_consent_refuses(self) -> None:
        for member in ("first", "second"):
            with self.subTest(member=member):
                self.refused("withdrawn", member, chat.CONSENT_NOT_CURRENT)

    def test_a_match_that_is_not_active_refuses(self) -> None:
        self.refused("unmatched", "first", chat.MATCH_NOT_ACTIVE)
        self.refused("match_restricted", "first", chat.MATCH_NOT_ACTIVE)

    def test_a_message_notifies_only_after_its_acceptance(self) -> None:
        w = World()
        w.enable(w.first)
        for state in ("pending", "failed"):
            w.world.set_message(w.message_id, state)
            result = w.service.deliver(w.message_trigger())
            self.assertEqual((result.outcome, result.reason), ("refused", n.MESSAGE_NOT_ACCEPTED))
        other_match = w.world.add_match(w.first.account, completed_by=w.second.account)
        w.world.set_message(w.message_id, "accepted")
        mismatched = n.MessageAccepted(uuid.uuid4(), other_match, w.message_id, w.first.account)
        result = w.service.deliver(mismatched)
        self.assertEqual(result.reason, n.MESSAGE_MATCH_MISMATCH)
        self.assertEqual(w.transport.recorded, [])

    def test_the_recipients_setting_or_no_active_device_refuses(self) -> None:
        w = World()
        self.assertEqual(w.service.deliver(w.message_trigger()).reason, n.SETTING_OFF)
        w.register(w.first)
        w.set(w.first, True, False)
        self.assertEqual(w.service.deliver(w.message_trigger()).reason, n.SETTING_OFF)
        self.assertEqual(w.service.deliver(w.match_trigger()).outcome, "sent")
        w.revoke(w.first)
        self.assertEqual(w.service.deliver(w.match_trigger()).reason, n.NO_ACTIVE_DEVICE)
        self.assertEqual(len(w.transport.recorded), 1)

    def test_each_refusal_is_a_reason_code_with_no_personal_data(self) -> None:
        codes = [
            value
            for name, value in vars(n).items()
            if name.isupper() and isinstance(value, str) and value.islower() and "_" in value
        ]
        self.assertIn(n.RECIPIENT_IS_SENDER, codes)
        for code in codes:
            self.assertIsNotNone(REASON_FORM.fullmatch(code), code)
        w = World()
        w.enable(w.first)
        w.world.block(w.first.account, w.second.account)
        result = w.service.deliver(w.message_trigger())
        self.assertIsNotNone(REASON_FORM.fullmatch(result.reason))
        self.assertIsNone(UUID_TEXT.search(repr(result)))


class FactsOnEachDeliveryTests(unittest.TestCase):
    """The facts are read on each delivery, never from the trigger (DM-44 2.2)."""

    def redelivered_after(self, change: str) -> n.DeliveryResult:
        w = World()
        w.enable(w.first)
        trigger = w.message_trigger()
        w.transport.fail_next()
        first = w.service.deliver(trigger)
        self.assertEqual((first.outcome, first.reason), ("nothing", n.TRANSPORT_UNAVAILABLE))
        world = w.world
        {
            "block": lambda: world.block(w.second.account, w.first.account),
            "unmatch": lambda: world.set_match(w.match_id, "unmatched"),
            "sender_pauses": lambda: world.set_profile(w.second.account, "paused"),
            "recipient_withdraws": lambda: world.set_consent(w.first.account, "withdrawn"),
            "recipient_suspended": lambda: world.set_account(w.first.account, "suspended"),
            "setting_off": lambda: w.set(w.first, True, False),
        }[change]()
        result = w.service.deliver(trigger)
        self.assertEqual(w.accepted(), [])
        return result

    def test_a_change_between_deliveries_refuses_the_redelivery(self) -> None:
        expected = {
            "block": chat.BLOCKED,
            "unmatch": chat.MATCH_NOT_ACTIVE,
            "sender_pauses": chat.PROFILE_UNAVAILABLE,
            "recipient_withdraws": chat.CONSENT_NOT_CURRENT,
            "recipient_suspended": chat.ACCOUNT_NOT_ACTIVE,
            "setting_off": n.SETTING_OFF,
        }
        for change, reason in expected.items():
            with self.subTest(change=change):
                result = self.redelivered_after(change)
                self.assertEqual((result.outcome, result.reason), ("refused", reason))

    def test_a_message_accepted_after_a_block_or_an_unmatch_notifies_no_one(self) -> None:
        for change in ("block", "unmatch"):
            with self.subTest(change=change):
                w = World()
                w.enable(w.first)
                w.enable(w.second)
                if change == "block":
                    w.world.block(w.first.account, w.second.account)
                else:
                    w.world.set_match(w.match_id, "unmatched")
                for recipient in (w.first, w.second):
                    w.service.deliver(w.message_trigger(recipient))
                self.assertEqual(w.transport.recorded, [])

    def test_every_delivery_reads_the_facts(self) -> None:
        w = World()
        w.enable(w.first)
        trigger = w.message_trigger()
        before = w.world.reads
        w.service.deliver(trigger)
        after_first = w.world.reads
        w.service.deliver(trigger)
        self.assertGreater(after_first, before)
        self.assertEqual(w.world.reads - after_first, after_first - before)


class NoDuplicatePushTests(unittest.TestCase):
    """DM-44 3.3's "Tried" cases."""

    def two_devices(self) -> tuple[World, Member, Member]:
        w = World()
        w.enable(w.first)
        phone = Member(w.first.account, w.first.session, uuid.uuid4())
        self.assertEqual(w.register(phone).outcome, "applied")
        return w, w.first, phone

    def test_a_repeat_after_both_devices_succeeded_sends_nothing(self) -> None:
        w, _, _ = self.two_devices()
        trigger = w.message_trigger()
        self.assertEqual(w.service.deliver(trigger).sent, 2)
        again = w.service.deliver(trigger)
        self.assertEqual((again.outcome, again.reason), ("nothing", n.ALREADY_DELIVERED))
        keys = [push.idempotency_key for push in w.transport.recorded]
        self.assertEqual(len(keys), 2)
        self.assertEqual(len(set(keys)), 2)

    def test_a_failed_device_is_retried_alone(self) -> None:
        w, tablet, phone = self.two_devices()
        trigger = w.message_trigger()
        w.transport.fail_next()
        first = w.service.deliver(trigger)
        self.assertEqual((first.outcome, first.sent, first.pending), ("sent", 1, 1))
        failed_key = w.transport.recorded[0].idempotency_key
        again = w.service.deliver(trigger)
        self.assertEqual((again.outcome, again.sent, again.pending), ("sent", 1, 0))
        self.assertEqual(w.transport.recorded[-1].idempotency_key, failed_key)
        self.assertEqual(len(w.transport.recorded), 3)
        self.assertEqual(
            w.service.ledger_keys(),
            {
                n.NotificationService.ledger_key(trigger.event_id, tablet.device),
                n.NotificationService.ledger_key(trigger.event_id, phone.device),
            },
        )

    def test_a_send_the_transport_accepted_but_the_ledger_missed_is_a_repeat(self) -> None:
        w = World()
        w.enable(w.first)
        trigger = w.message_trigger()
        w.transport.lose_next_answer()
        first = w.service.deliver(trigger)
        self.assertEqual((first.outcome, first.reason), ("nothing", n.TRANSPORT_UNAVAILABLE))
        self.assertEqual(w.service.ledger_keys(), frozenset())
        again = w.service.deliver(trigger)
        self.assertEqual((again.outcome, again.reason), ("nothing", n.ALREADY_DELIVERED))
        self.assertEqual([push.outcome for push in w.transport.recorded], ["lost", "repeat"])
        self.assertEqual(len(w.service.ledger_keys()), 1)
        self.assertEqual(w.service.deliver(trigger).reason, n.ALREADY_DELIVERED)
        self.assertEqual(len(w.transport.recorded), 2)

    def test_a_device_revoked_and_registered_again_keeps_its_key(self) -> None:
        w = World()
        w.enable(w.first)
        trigger = w.message_trigger()
        self.assertEqual(w.service.deliver(trigger).sent, 1)
        w.revoke(w.first)
        self.assertEqual(w.register(w.first).outcome, "applied")
        again = w.service.deliver(trigger)
        self.assertEqual((again.outcome, again.reason), ("nothing", n.ALREADY_DELIVERED))
        self.assertEqual(len(w.transport.recorded), 1)

    def test_a_device_registered_after_the_first_delivery_gets_nothing(self) -> None:
        w = World()
        w.enable(w.first)
        trigger = w.message_trigger()
        self.assertEqual(w.service.deliver(trigger).sent, 1)
        late = Member(w.first.account, w.first.session, uuid.uuid4())
        self.assertEqual(w.register(late).outcome, "applied")
        self.assertEqual(w.service.deliver(trigger).reason, n.ALREADY_DELIVERED)
        self.assertEqual(len(w.transport.recorded), 1)
        fresh = w.service.deliver(w.message_trigger())
        self.assertEqual(fresh.sent, 2)

    def test_a_device_revoked_after_a_failed_send_gets_nothing(self) -> None:
        w, tablet, phone = self.two_devices()
        trigger = w.message_trigger()
        w.transport.fail_next()
        first = w.service.deliver(trigger)
        self.assertEqual((first.sent, first.pending), (1, 1))
        failed_reference = w.transport.recorded[0].reference
        failed = next(
            member
            for member in (tablet, phone)
            if (registration := w.service.registration(member.account, member.device)) is not None
            and registration.reference is not None
            and registration.reference.value == failed_reference
        )
        self.assertEqual(w.revoke(failed).outcome, "applied")
        again = w.service.deliver(trigger)
        self.assertEqual((again.outcome, again.reason), ("nothing", n.NO_ACTIVE_DEVICE))
        self.assertEqual(len(w.transport.recorded), 2)

    def test_the_transport_key_is_the_ledger_key_and_the_device_is_its_reference(self) -> None:
        w = World()
        token = synthetic_token("ledger")
        w.register(w.first, token)
        w.set(w.first, True, True)
        trigger = w.message_trigger()
        w.service.deliver(trigger)
        (push,) = w.transport.recorded
        self.assertEqual(
            push.idempotency_key,
            n.NotificationService.ledger_key(trigger.event_id, w.first.device),
        )
        self.assertNotIn(token, push.reference)
        registration = w.service.registration(w.first.account, w.first.device)
        assert registration is not None and registration.reference is not None
        self.assertEqual(push.reference, registration.reference.value)
        self.assertEqual(w.tokens.resolve(registration.reference), token)

    def test_a_registration_whose_session_is_not_current_is_not_active_for_the_composer(
        self,
    ) -> None:
        for change in ("revoked", "expired", "epoch", "clock"):
            with self.subTest(change=change):
                w = World()
                w.enable(w.first)
                if change == "epoch":
                    w.world.bump_epoch(w.first.account)
                elif change == "clock":
                    w.fx.clock.advance(timedelta(hours=2))
                else:
                    w.world.end_session(w.first.session, change)
                result = w.service.deliver(w.match_trigger())
                self.assertEqual((result.outcome, result.reason), ("refused", n.NO_ACTIVE_DEVICE))
                self.assertEqual(w.transport.recorded, [])


# -- Outcome 2: devices and settings -----------------------------------------------------------


class TransitionTests(unittest.TestCase):
    """DM-44 1.1 and 1.2's "Tried" cases."""

    def test_register_rotate_revoke_and_register_again(self) -> None:
        w = World()
        member = w.first
        first = w.register(member)
        self.assertEqual((first.outcome, first.transition), ("applied", "register"))
        assert first.settings is not None
        self.assertEqual(first.settings.as_contract()["device_state"], "active")
        self.assertEqual(first.settings.version, 1)
        old = w.service.registration(member.account, member.device)
        assert old is not None and old.reference is not None
        rotated = w.register(member)
        self.assertEqual((rotated.outcome, rotated.transition), ("applied", "rotate"))
        new = w.service.registration(member.account, member.device)
        assert new is not None and new.reference is not None
        self.assertNotEqual(new.reference, old.reference)
        self.assertIn(old.reference, w.tokens.discarded)
        revoked = w.revoke(member)
        self.assertEqual((revoked.outcome, revoked.transition), ("applied", "revoke"))
        assert revoked.settings is not None
        self.assertEqual(revoked.settings.device_state, "revoked")
        again = w.register(member)
        self.assertEqual((again.outcome, again.transition), ("applied", "register"))

    def test_revoke_without_an_active_registration_is_forbidden(self) -> None:
        w = World()
        self.assertEqual(w.revoke(w.first).reason, n.TRANSITION_FORBIDDEN)
        w.register(w.first)
        w.revoke(w.first)
        self.assertEqual(w.revoke(w.first).reason, n.TRANSITION_FORBIDDEN)

    def test_a_second_installation_registers_on_its_own(self) -> None:
        w = World()
        w.register(w.first)
        phone = Member(w.first.account, w.first.session, uuid.uuid4())
        result = w.register(phone)
        self.assertEqual((result.outcome, result.transition), ("applied", "register"))
        tablet = w.service.registration(w.first.account, w.first.device)
        assert tablet is not None
        self.assertEqual(tablet.state, "active")

    def test_a_settings_intent_needs_the_installations_active_registration(self) -> None:
        w = World()
        none = w.service.settings(w.first.caller, settings(True, False, 0, w.key()))
        self.assertEqual((none.outcome, none.reason), ("refused", n.REGISTRATION_NOT_ACTIVE))
        w.register(w.first)
        w.revoke(w.first)
        revoked = w.set(w.first, True, False)
        self.assertEqual((revoked.outcome, revoked.reason), ("refused", n.REGISTRATION_NOT_ACTIVE))
        self.assertEqual(w.service.settings_of(w.first.account), n.Settings())
        w.register(w.first)
        applied = w.set(w.first, True, False)
        self.assertEqual(applied.outcome, "applied")
        assert applied.settings is not None
        self.assertEqual(
            applied.settings.as_contract(),
            {
                "kind": "notifications",
                "version": w.version(w.first),
                "match_notifications": True,
                "message_notifications": False,
                "device_state": "active",
            },
        )

    def test_command_meta_stale_versions_conflicts_and_replays(self) -> None:
        w = World()
        stale = w.service.device(
            w.first.caller, register(w.first.device, synthetic_token("s"), 3, "k-stale")
        )
        self.assertEqual(stale.reason, n.STALE_VERSION)
        intent = register(w.first.device, synthetic_token("a"), 0, "k-one")
        applied = w.service.device(w.first.caller, intent)
        self.assertEqual(applied.outcome, "applied")
        puts = w.tokens.puts
        version = w.version(w.first)
        replay = w.service.device(w.first.caller, intent)
        self.assertEqual(replay.outcome, "replayed")
        self.assertEqual(replay.receipt, applied.receipt)
        self.assertEqual((w.tokens.puts, w.version(w.first)), (puts, version))
        other_token = register(w.first.device, synthetic_token("b"), 0, "k-one")
        conflict = w.service.device(w.first.caller, other_token)
        self.assertEqual(conflict.reason, chat.IDEMPOTENCY_CONFLICT)
        self.assertEqual((w.tokens.puts, w.version(w.first)), (puts, version))
        stale_settings = w.service.settings(w.first.caller, settings(True, True, 0, "k-two"))
        self.assertEqual(stale_settings.reason, n.STALE_VERSION)
        settings_intent = settings(True, True, version, "k-three")
        self.assertEqual(w.service.settings(w.first.caller, settings_intent).outcome, "applied")
        after = w.version(w.first)
        self.assertEqual(w.service.settings(w.first.caller, settings_intent).outcome, "replayed")
        self.assertEqual(w.version(w.first), after)
        changed = settings(False, True, version, "k-three")
        self.assertEqual(
            w.service.settings(w.first.caller, changed).reason, chat.IDEMPOTENCY_CONFLICT
        )

    def test_a_settings_change_advances_every_installation_view_of_the_account(self) -> None:
        w = World()
        w.register(w.first)
        phone = Member(w.first.account, w.first.session, uuid.uuid4())
        w.register(phone)
        phone_version = w.version(phone)
        w.set(w.first, True, False)
        self.assertEqual(w.version(phone), phone_version + 1)
        stale = w.service.settings(phone.caller, settings(False, False, phone_version, w.key()))
        self.assertEqual(stale.reason, n.STALE_VERSION)

    def test_only_the_owner_reads_from_a_current_session_and_absence_is_explicit(self) -> None:
        w = World()
        absent = w.service.read(w.first.caller)
        self.assertEqual((absent.outcome, absent.settings), ("absent", None))
        w.enable(w.first)
        read = w.service.read(w.first.caller)
        assert read.settings is not None
        self.assertEqual(read.settings.device_state, "active")
        intruder = Member(w.second.account, w.second.session, w.first.device)
        other = w.service.read(intruder.caller)
        self.assertEqual((other.outcome, other.settings), ("absent", None))
        borrowed = n.Caller(w.second.account, w.first.session, w.first.device)
        self.assertEqual(w.service.read(borrowed).reason, n.SESSION_NOT_OWNER)
        w.world.end_session(w.first.session)
        self.assertEqual(w.service.read(w.first.caller).reason, chat.SESSION_NOT_VALID)

    def test_a_device_command_names_only_the_callers_installation(self) -> None:
        w = World()
        elsewhere = register(uuid.uuid4(), synthetic_token("x"), 0, "k-x")
        self.assertEqual(w.service.device(w.first.caller, elsewhere).reason, n.WRONG_INSTALLATION)

    def test_intents_follow_their_contracts(self) -> None:
        w = World()
        bad = [
            {**register(w.first.device, synthetic_token("x"), 0, "k"), "rotate": True},
            {**register(w.first.device, synthetic_token("x"), 0, "k"), "action": "rotate"},
            {**register(w.first.device, synthetic_token("x"), 0, "k"), "provider_token": ""},
            {**register(w.first.device, synthetic_token("x"), 0, "k"), "provider_token": "  "},
            {**register(w.first.device, synthetic_token("x"), 0, "k"), "provider_token": None},
            {**revoke(w.first.device, 0, "k"), "provider_token": synthetic_token("x")},
            {**register(w.first.device, "x" * 4097, 0, "k")},
            {**register(w.first.device, synthetic_token("x"), -1, "k")},
            {**register(w.first.device, synthetic_token("x"), True, "k")},
            {**register(w.first.device, synthetic_token("x"), 0, "-k")},
            {**register(w.first.device, synthetic_token("x"), 0, "k"), "device_id": "X"},
        ]
        for intent in bad:
            with self.subTest(intent=sorted(intent)):
                self.assertEqual(w.service.device(w.first.caller, intent).reason, n.INTENT_INVALID)
        for intent in (
            {**settings(True, False, 0, "k"), "device_id": str(w.first.device)},
            {**settings(True, False, 0, "k"), "match_notifications": 1},
            {**settings(True, False, 0, "k"), "operation": "device"},
        ):
            with self.subTest(intent=sorted(intent)):
                self.assertEqual(
                    w.service.settings(w.first.caller, intent).reason, n.INTENT_INVALID
                )
        self.assertIsNone(w.service.registration(w.first.account, w.first.device))


class SessionBindingTests(unittest.TestCase):
    def test_a_command_from_a_session_that_is_no_longer_current_is_refused(self) -> None:
        cases = {
            "revoked": chat.SESSION_NOT_VALID,
            "expired": chat.SESSION_NOT_VALID,
            "epoch": chat.SESSION_EPOCH_STALE,
            "clock": chat.SESSION_EXPIRED,
            "suspended": chat.ACCOUNT_NOT_ACTIVE,
            "missing": chat.SESSION_MISSING,
            "other_account": n.SESSION_NOT_OWNER,
        }
        for change, reason in cases.items():
            with self.subTest(change=change):
                w = World()
                w.register(w.first)
                member = w.first
                if change in ("revoked", "expired"):
                    w.world.end_session(member.session, change)
                elif change == "epoch":
                    w.world.bump_epoch(member.account)
                elif change == "clock":
                    w.fx.clock.advance(timedelta(hours=2))
                elif change == "suspended":
                    w.world.set_account(member.account, "suspended")
                elif change == "missing":
                    member = Member(member.account, uuid.uuid4(), member.device)
                else:
                    member = Member(member.account, w.second.session, member.device)
                version = w.version(w.first)
                for result in (
                    w.service.device(
                        member.caller, register(member.device, synthetic_token("r"), version, "a")
                    ),
                    w.service.device(member.caller, revoke(member.device, version, "b")),
                    w.service.settings(member.caller, settings(True, True, version, "c")),
                    w.service.read(member.caller),
                ):
                    self.assertEqual((result.outcome, result.reason), ("refused", reason))
                registration = w.service.registration(w.first.account, w.first.device)
                assert registration is not None
                self.assertEqual((registration.state, registration.version), ("active", 1))

    def test_each_registration_records_the_session_that_last_registered_or_rotated_it(
        self,
    ) -> None:
        w = World()
        w.register(w.first)
        first = w.service.registration(w.first.account, w.first.device)
        assert first is not None
        self.assertEqual(first.session_id, w.first.session)
        newer = Member(w.first.account, w.world.open_session(w.first.account), w.first.device)
        w.register(newer)
        rotated = w.service.registration(w.first.account, w.first.device)
        assert rotated is not None
        self.assertEqual(rotated.session_id, newer.session)

    def test_logout_revokes_the_registrations_the_ending_session_made_and_no_other(self) -> None:
        w = World()
        w.register(w.first)
        phone = Member(w.first.account, w.world.open_session(w.first.account), uuid.uuid4())
        w.register(phone)
        tablet = w.service.registration(w.first.account, w.first.device)
        assert tablet is not None and tablet.reference is not None
        reference = tablet.reference
        self.assertEqual(w.service.logout(w.first.session), (w.first.device,))
        ended = w.service.registration(w.first.account, w.first.device)
        kept = w.service.registration(phone.account, phone.device)
        assert ended is not None and kept is not None
        self.assertEqual(
            (ended.state, ended.ended_by, ended.reference), ("revoked", "logout", None)
        )
        self.assertEqual(kept.state, "active")
        self.assertIn(reference, w.tokens.discarded)
        self.assertEqual(w.service.logout(w.first.session), ())

    def test_registering_an_installation_active_for_another_account_revokes_it_first(
        self,
    ) -> None:
        w = World()
        w.register(w.first)
        before = w.service.registration(w.first.account, w.first.device)
        assert before is not None and before.reference is not None
        reference = before.reference
        newcomer = Member(w.second.account, w.second.session, w.first.device)
        result = w.register(newcomer)
        self.assertEqual((result.outcome, result.transition), ("applied", "register"))
        previous = w.service.registration(w.first.account, w.first.device)
        assert previous is not None
        self.assertEqual(
            (previous.state, previous.ended_by, previous.reference), ("revoked", "transfer", None)
        )
        self.assertIn(reference, w.tokens.discarded)
        current = w.service.registration(w.second.account, w.first.device)
        assert current is not None
        self.assertEqual(current.state, "active")
        back = w.register(w.first)
        self.assertEqual((back.outcome, back.transition), ("applied", "register"))
        moved = w.service.registration(w.second.account, w.first.device)
        assert moved is not None
        self.assertEqual((moved.state, moved.ended_by), ("revoked", "transfer"))


class CustodyTests(unittest.TestCase):
    def test_the_token_reaches_the_store_before_any_reference_is_saved(self) -> None:
        w = World()
        w.tokens.refuse_next_put()
        refused = w.register(w.first)
        self.assertEqual((refused.outcome, refused.reason), ("refused", n.TOKEN_STORE_REFUSED))
        self.assertIsNone(w.service.registration(w.first.account, w.first.device))
        self.assertEqual(w.service.read(w.first.caller).outcome, "absent")
        self.assertEqual(w.tokens.held, 0)
        applied = w.register(w.first)
        self.assertEqual(applied.outcome, "applied")
        self.assertEqual(w.tokens.held, 1)
        w.tokens.refuse_next_put()
        before = w.service.registration(w.first.account, w.first.device)
        refused_rotate = w.register(w.first)
        self.assertEqual(refused_rotate.reason, n.TOKEN_STORE_REFUSED)
        self.assertEqual(w.service.registration(w.first.account, w.first.device), before)

    def discarded_on(self, path: str) -> tuple[World, n.TokenReference]:
        w = World()
        w.register(w.first)
        registration = w.service.registration(w.first.account, w.first.device)
        assert registration is not None and registration.reference is not None
        reference = registration.reference
        if path == "revoke":
            w.revoke(w.first)
        elif path == "logout":
            w.service.logout(w.first.session)
        elif path == "transfer":
            w.register(Member(w.second.account, w.second.session, w.first.device))
        else:
            w.register(w.first)
        return w, reference

    def test_revoke_discards_the_old_token(self) -> None:
        w, reference = self.discarded_on("revoke")
        self.assertIn(reference, w.tokens.discarded)
        self.assertIsNone(w.tokens.resolve(reference))

    def test_logout_discards_the_old_token(self) -> None:
        w, reference = self.discarded_on("logout")
        self.assertIn(reference, w.tokens.discarded)
        self.assertIsNone(w.tokens.resolve(reference))

    def test_transfer_discards_the_old_token(self) -> None:
        w, reference = self.discarded_on("transfer")
        self.assertIn(reference, w.tokens.discarded)
        self.assertIsNone(w.tokens.resolve(reference))

    def test_rotate_discards_the_old_token(self) -> None:
        w, reference = self.discarded_on("rotate")
        self.assertIn(reference, w.tokens.discarded)
        self.assertIsNone(w.tokens.resolve(reference))
        self.assertEqual(w.tokens.held, 1)

    def test_a_failed_discard_still_ends_the_registration_and_is_retried(self) -> None:
        w = World()
        w.register(w.first)
        registration = w.service.registration(w.first.account, w.first.device)
        assert registration is not None and registration.reference is not None
        reference = registration.reference
        w.tokens.fail_next_discard()
        self.assertEqual(w.revoke(w.first).outcome, "applied")
        ended = w.service.registration(w.first.account, w.first.device)
        assert ended is not None
        self.assertEqual((ended.state, ended.reference), ("revoked", None))
        self.assertEqual(w.service.pending_discards, 1)
        self.assertNotIn(reference, w.tokens.discarded)
        w.enable(w.second)
        w.service.deliver(w.message_trigger())
        self.assertNotIn(reference.value, [push.reference for push in w.transport.recorded])
        self.assertEqual(w.service.retry_discards(), 0)
        self.assertIn(reference, w.tokens.discarded)
        self.assertIsNone(w.tokens.resolve(reference))

    def test_custody_types_print_as_withheld(self) -> None:
        token = n.ProviderToken(synthetic_token("print"))
        reference = n.TokenReference("fixture-token-ref-print")
        for value in (repr(token), str(token), f"{token}", repr(reference), str(reference)):
            self.assertNotIn("print", value)
        with self.assertRaises(TypeError):
            token.__reduce__()


class CustodyCaptureTests(unittest.TestCase):
    """The custody test (DM-44 3.2): a distinctive synthetic token through every path, with every
    log record captured at DEBUG from the root logger."""

    TOKEN = synthetic_token("CUSTODY-CANARY-7f3a9c")

    def test_no_token_or_reference_escapes(self) -> None:
        records: list[logging.LogRecord] = []

        class Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record)

        root = logging.getLogger()
        handler = Capture(level=logging.DEBUG)
        previous_level = root.level
        root.addHandler(handler)
        root.setLevel(logging.DEBUG)
        try:
            outputs, references, errors, w = self.exercise()
        finally:
            root.removeHandler(handler)
            root.setLevel(previous_level)
        self.assertTrue(records, "the paths logged nothing to check")
        self.assertTrue(references)
        for record in records:
            texts = (record.getMessage(), repr(record.args), str(record.msg))
            for text in texts:
                self.assertNotIn(self.TOKEN, text, "the token in a log record")
                for reference in references:
                    self.assertNotIn(reference, text, "a reference in a log record")
        for output in outputs:
            for text in (repr(output), str(output)):
                self.assertNotIn(self.TOKEN, text, "the token in a read, result or repr")
                for reference in references:
                    self.assertNotIn(reference, text, "a reference in a read or refusal")
        for error in errors:
            self.assertNotIn(self.TOKEN, str(error), "the token in an exception's text")
            self.assertNotIn(self.TOKEN, repr(error), "the token in an exception's text")
        for push in w.transport.recorded:
            self.assertNotIn(self.TOKEN, repr(push), "the token in what the transport recorded")

    def exercise(
        self,
    ) -> tuple[list[object], list[str], list[BaseException], World]:
        w = World()
        member = w.first
        outputs: list[object] = [w.service, w.tokens, w.transport, w.world]
        references: list[str] = []

        def note_reference(account: UUID, device: UUID) -> None:
            registration = w.service.registration(account, device)
            outputs.append(registration)
            if registration is not None and registration.reference is not None:
                references.append(registration.reference.value)

        register_intent = register(member.device, self.TOKEN, 0, "custody-register")
        outputs.append(w.service.device(member.caller, register_intent))  # register
        note_reference(member.account, member.device)
        outputs.append(w.service.device(member.caller, register_intent))  # replay
        conflict = register(member.device, self.TOKEN + "-other", 0, "custody-register")
        outputs.append(w.service.device(member.caller, conflict))  # refused: conflict
        stale = register(member.device, self.TOKEN, 0, "custody-stale")
        outputs.append(w.service.device(member.caller, stale))  # refused: stale version
        outputs.append(w.service.read(member.caller))
        outputs.append(w.set(member, True, True))
        rotate = register(member.device, self.TOKEN, w.version(member), "custody-rotate")
        outputs.append(w.service.device(member.caller, rotate))  # rotate
        note_reference(member.account, member.device)
        w.tokens.refuse_next_put()
        refused_put = register(member.device, self.TOKEN, w.version(member), "custody-refused")
        outputs.append(w.service.device(member.caller, refused_put))  # refused: the store
        outputs.append(w.service.deliver(w.message_trigger()))
        outputs.append(w.service.device(member.caller, revoke(member.device, 1, "custody-x")))
        outputs.append(w.revoke(member))  # revoke
        outputs.append(w.service.read(member.caller))
        again = register(member.device, self.TOKEN, w.version(member), "custody-again")
        outputs.append(w.service.device(member.caller, again))
        note_reference(member.account, member.device)
        outputs.append(w.service.logout(member.session))  # logout
        fresh = Member(member.account, w.world.open_session(member.account), member.device)
        back = register(fresh.device, self.TOKEN, w.version(fresh), "custody-back")
        outputs.append(w.service.device(fresh.caller, back))
        note_reference(fresh.account, fresh.device)
        newcomer = Member(w.second.account, w.second.session, member.device)
        transfer = register(newcomer.device, self.TOKEN, 0, "custody-transfer")
        outputs.append(w.service.device(newcomer.caller, transfer))  # transfer
        note_reference(newcomer.account, newcomer.device)
        note_reference(fresh.account, fresh.device)
        w.world.end_session(newcomer.session)
        late = revoke(newcomer.device, w.version(newcomer), "custody-late")
        outputs.append(w.service.device(newcomer.caller, late))  # refused: session
        bad = {**register(member.device, self.TOKEN, 0, "custody-bad"), "extra": self.TOKEN}
        outputs.append(w.service.device(fresh.caller, bad))  # refused: invalid intent
        errors: list[BaseException] = []
        for invalid in (
            bad,
            {**revoke(member.device, 0, "custody-e"), "provider_token": self.TOKEN},
            {**register(member.device, self.TOKEN, 0, "custody-e"), "device_id": self.TOKEN},
        ):
            try:
                n.parse_device_intent(invalid)
            except n.IntentError as error:
                errors.append(error)
        try:
            n.ProviderToken(self.TOKEN + " " * 5000)
        except n.IntentError as error:
            errors.append(error)
        self.assertEqual(len(errors), 4)
        outputs.append(n.parse_device_intent(register(member.device, self.TOKEN, 0, "custody-p")))
        return outputs, references, errors, w


class DefaultsTests(unittest.TestCase):
    def test_settings_default_to_off_for_both_kinds(self) -> None:
        w = World()
        self.assertEqual(w.service.settings_of(w.first.account), n.Settings(False, False, 0))
        result = w.register(w.first)
        assert result.settings is not None
        self.assertEqual(
            (result.settings.match_notifications, result.settings.message_notifications),
            (False, False),
        )
        read = w.service.read(w.first.caller)
        assert read.settings is not None
        self.assertEqual(read.settings.as_contract()["match_notifications"], False)
        self.assertEqual(read.settings.as_contract()["message_notifications"], False)

    def test_the_projection_has_the_contracts_fields_and_no_token_or_reference(self) -> None:
        names = {item.name for item in fields(n.NotificationSettingsView)}
        self.assertEqual(
            names, {"version", "match_notifications", "message_notifications", "device_state"}
        )
        contract = json.loads(
            (
                API_ROOT.parents[1] / "packages/contracts/production/gapp-api-v1.schema.json"
            ).read_text(encoding="utf-8")
        )["$defs"]["NotificationSettings"]
        view = n.NotificationSettingsView(1, False, False, "active").as_contract()
        self.assertEqual(set(view), set(contract["required"]))
        self.assertEqual(set(view), set(contract["properties"]))


class FixtureScopeTests(unittest.TestCase):
    def test_the_service_and_its_fixtures_refuse_any_other_environment(self) -> None:
        for environment in ("production", "staging", ""):
            with self.subTest(environment=environment):
                with self.assertRaises(ValueError):
                    notification_fixture(environment)

    @staticmethod
    def _imported_modules(source: str) -> set[str]:
        """Every module a source imports. An ``ImportFrom`` is read by its level, module and
        imported names: ``from . import x`` imports the sibling ``.x``, and ``from .m import y``
        imports ``.m`` (correction C1, item 2)."""
        imported: set[str] = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                prefix = "." * node.level
                if node.module:
                    imported.add(prefix + node.module)
                else:
                    imported.update(prefix + alias.name for alias in node.names)
        return imported

    def test_the_import_reading_names_each_relative_module(self) -> None:
        cases = {
            "from . import chat_provider_stream\n": {".chat_provider_stream"},
            "from . import chat, chat_provider_stream as s\n": {".chat", ".chat_provider_stream"},
            "from .. import x\n": {"..x"},
            "from .provider_fixtures import require_fixture_environment\n": {".provider_fixtures"},
            "from collections.abc import Callable\nimport json\n": {"collections.abc", "json"},
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(self._imported_modules(source), expected)

    def test_the_domain_module_imports_only_the_standard_library_and_its_two_neighbours(
        self,
    ) -> None:
        imported = self._imported_modules(
            (API_ROOT / "glow_domain" / "notifications.py").read_text("utf-8")
        )
        self.assertEqual(
            {name for name in imported if name.startswith(".")},
            {".chat", ".provider_fixtures"},
        )
        self.assertEqual(
            imported,
            {
                "__future__",
                "hashlib",
                "hmac",
                "json",
                "logging",
                "re",
                "secrets",
                "threading",
                "collections.abc",
                "dataclasses",
                "datetime",
                "typing",
                "uuid",
                ".chat",
                ".provider_fixtures",
            },
        )

    def test_the_runtime_imports_none_of_the_notification_modules(self) -> None:
        probe = (
            "import json, sys\n"
            "import django\n"
            "django.setup()\n"
            "import glow_api.settings, glow_api.urls, glow_api.wsgi\n"
            "print(json.dumps(sorted(m for m in sys.modules if m.startswith("
            "('glow_domain.notification', 'glow_domain.notifications')))))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=API_ROOT,
            env={
                "PATH": "/usr/bin:/bin",
                "LANG": "C.UTF-8",
                "DJANGO_SETTINGS_MODULE": "glow_api.settings",
                "GLOW_ENV": "test",
            },
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout.strip().splitlines()[-1]), [])
        for path in sorted((API_ROOT / "glow_api").glob("*.py")):
            with self.subTest(module=path.name):
                self.assertNotIn("notification", path.read_text(encoding="utf-8"))

    def test_the_domain_module_loads_without_django(self) -> None:
        probe = (
            "import sys\n"
            "class Hidden:\n"
            "    def find_spec(self, name, path=None, target=None):\n"
            "        if name.split('.')[0] in ('django', 'glow_persistence', 'glow_chat',"
            " 'glow_api', 'rest_framework'):\n"
            "            raise ImportError('hidden')\n"
            "        return None\n"
            "sys.meta_path.insert(0, Hidden())\n"
            "import glow_domain.notifications, glow_domain.notification_fixtures\n"
            "print('loaded')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=API_ROOT,
            env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "loaded")
