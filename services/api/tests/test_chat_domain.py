"""P06.2 Stage A's pure domain pieces, offline: the contact port's types, the chat
provider port and its fixture adapter, and the token rules (item 4, D6)."""

import inspect
import unittest
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from glow_domain import chat, chat_provider, chat_tokens
from glow_domain.chat_provider import ChatProviderError, error_code
from glow_domain.chat_provider_fixtures import FixtureChatProvider, FixtureProviderOutage

NOW = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


class ContactPortTests(unittest.TestCase):
    def test_the_request_digest_binds_the_canonical_request(self) -> None:
        match = uuid4()
        one = chat.SendCommand(uuid4(), match, 1, "k1", "hello")
        self.assertEqual(
            one.request_digest, chat.SendCommand(uuid4(), match, 1, "k2", "hello").request_digest
        )
        self.assertNotEqual(
            one.request_digest, chat.SendCommand(uuid4(), match, 1, "k1", "other").request_digest
        )
        self.assertNotEqual(
            one.request_digest, chat.SendCommand(uuid4(), match, 2, "k1", "hello").request_digest
        )
        self.assertRegex(one.request_digest, r"^[0-9a-f]{64}$")

    def test_the_actor_is_never_a_field_of_the_request(self) -> None:
        fields = set(inspect.signature(chat.SendCommand).parameters)
        self.assertEqual(
            fields, {"session_id", "match_id", "contact_version", "idempotency_key", "text"}
        )

    def test_the_port_names_every_writer(self) -> None:
        writers = {
            name
            for name, member in vars(chat.ContactPersistence).items()
            if callable(member) and not name.startswith("_")
        }
        self.assertEqual(
            writers,
            {
                "activate_match",
                "open_session",
                "sign_out",
                "expire_session",
                "send",
                "block",
                "unblock",
                "unmatch",
                "suspend",
                "delete",
                "pause_profile",
                "resume_profile",
                "restrict_profile",
                "withdraw_consent",
                "accept_consent",
            },
        )

    def test_the_probe_holds_only_callables_and_the_consent_purpose_is_named(self) -> None:
        probe = chat.TransactionProbe()
        self.assertEqual(
            set(vars(probe)), {"on_begin", "after_first_lock", "after_locks", "before_commit"}
        )
        self.assertTrue(all(value is None for value in vars(probe).values()))
        self.assertEqual(chat.ONBOARDING_CONSENT_PURPOSE, "onboarding")

    def test_committed_outcomes(self) -> None:
        self.assertTrue(chat.ContactResult("authorized").committed)
        self.assertTrue(chat.ContactResult("applied").committed)
        for outcome in ("replayed", "no_change", "refused", "deadlock", "error"):
            self.assertFalse(chat.ContactResult(outcome).committed)  # type: ignore[arg-type]


class ProviderPortTests(unittest.TestCase):
    def test_only_glow_codes_and_never_provider_text(self) -> None:
        with self.assertRaises(ValueError):
            ChatProviderError("upstream said no")  # type: ignore[arg-type]
        self.assertEqual(error_code(ChatProviderError("member_unavailable")), "member_unavailable")
        self.assertEqual(error_code(RuntimeError("provider text")), "provider_unavailable")
        self.assertEqual(str(ChatProviderError("provider_rejected")), "provider_rejected")
        self.assertTrue(ChatProviderError("provider_unavailable").retryable)
        self.assertFalse(ChatProviderError("channel_unavailable").retryable)

    def test_the_operations_carry_identifiers_members_and_text_only(self) -> None:
        self.assertEqual(
            set(chat_provider.OPERATIONS),
            {
                "create_channel",
                "send_message",
                "remove_members",
                "deactivate_user",
                "revoke_user_tokens",
            },
        )
        arguments = set().union(*chat_provider.OPERATIONS.values())
        self.assertFalse(arguments & {"name", "image", "data", "custom", "extra_data"})
        for name in chat_provider.OPERATIONS:
            parameters = set(
                inspect.signature(getattr(chat_provider.ChatProvider, name)).parameters
            )
            self.assertEqual(parameters - {"self"}, set(chat_provider.OPERATIONS[name]))
        for forbidden in ("invite", "call", "feed", "activity", "ban", "hide", "freeze"):
            self.assertFalse(any(forbidden in name for name in dir(chat_provider.ChatProvider)))


class FixtureProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = FixtureChatProvider(environment="test")
        self.provider.create_channel("c1", ("u1", "u2"))

    def test_development_and_test_only(self) -> None:
        for environment in ("production", "staging", ""):
            with self.assertRaises(ValueError):
                FixtureChatProvider(environment=environment)

    def test_a_repeated_create_returns_the_channel_and_adds_no_member(self) -> None:
        self.provider.remove_members("c1", ("u1", "u2"))
        again = self.provider.create_channel("c1", ("u2", "u1"))
        self.assertTrue(again.already)
        self.assertEqual(self.provider.channels["c1"].members, set())
        with self.assertRaises(ChatProviderError) as raised:
            self.provider.create_channel("c1", ("u1", "u3"))
        self.assertEqual(raised.exception.code, "provider_rejected")

    def test_a_repeated_message_id_is_one_message(self) -> None:
        first = self.provider.send_message("c1", "u1", "m1", "hi")
        again = self.provider.send_message("c1", "u1", "m1", "hi")
        self.assertFalse(first.already)
        self.assertTrue(again.already)
        self.assertEqual(len(self.provider.channels["c1"].messages), 1)

    def test_a_removed_member_cannot_send_and_history_is_kept(self) -> None:
        self.provider.send_message("c1", "u1", "m1", "hi")
        self.provider.remove_members("c1", ("u1", "u2"))
        with self.assertRaises(ChatProviderError) as raised:
            self.provider.send_message("c1", "u1", "m2", "after")
        self.assertEqual(raised.exception.code, "member_unavailable")
        self.assertEqual(self.provider.channels["c1"].removals, [1])
        self.assertEqual([m for m, _, _ in self.provider.channels["c1"].messages], ["m1"])

    def test_deactivation_and_token_revocation(self) -> None:
        self.assertFalse(self.provider.deactivate_user("u1").already)
        self.assertTrue(self.provider.deactivate_user("u1").already)
        self.provider.revoke_user_tokens("u2", NOW)
        self.assertTrue(self.provider.revoke_user_tokens("u2", NOW).already)
        self.assertEqual(self.provider.users["u2"].token_cutoffs, [NOW])
        with self.assertRaises(ChatProviderError):
            self.provider.create_channel("c2", ("u1", "u3"))
        with self.assertRaises(ChatProviderError):
            self.provider.deactivate_user("unknown")

    def test_failures_before_and_after_the_effect(self) -> None:
        self.provider.fail_next("send_message")
        with self.assertRaises(ChatProviderError):
            self.provider.send_message("c1", "u1", "m1", "hi")
        self.assertEqual(self.provider.channels["c1"].messages, [])
        self.provider.fail_next("send_message", after_effect=True)
        with self.assertRaises(ChatProviderError):
            self.provider.send_message("c1", "u1", "m1", "hi")
        self.assertEqual(len(self.provider.channels["c1"].messages), 1)
        self.assertTrue(self.provider.send_message("c1", "u1", "m1", "hi").already)
        self.provider.fail_next("remove_members", code=None, text="provider says secret detail")
        with self.assertRaises(FixtureProviderOutage) as raised:
            self.provider.remove_members("c1", ("u1", "u2"))
        self.assertEqual(error_code(raised.exception), "provider_unavailable")
        outcomes = [c.outcome for c in self.provider.calls]
        self.assertIn("failed_before", outcomes)
        self.assertIn("failed_after", outcomes)

    def test_every_call_is_recorded_with_its_argument_names_only(self) -> None:
        self.provider.send_message("c1", "u1", "m1", "hi")
        for call in self.provider.calls:
            self.assertLessEqual(call.arguments, chat_provider.OPERATIONS[call.operation])


class TokenRuleTests(unittest.TestCase):
    """Item 4 (D6): a one-hour grant for a valid, current-epoch session of an active
    account, refused after a suspension or a deletion. No token is signed here."""

    def grant(self, **changes: object) -> chat_tokens.TokenGrant | chat_tokens.TokenRefusal:
        arguments: dict[str, object] = {
            "account": chat_tokens.TokenAccount("active", 1),
            "session": chat_tokens.TokenSession("valid", 1, NOW + timedelta(days=1)),
            "user_ref": "0" * 32,
            "identity_active": True,
            "now": NOW,
        }
        arguments.update(changes)
        return chat_tokens.grant_chat_token(**arguments)  # type: ignore[arg-type]

    def test_a_valid_session_gets_one_hour(self) -> None:
        grant = self.grant()
        assert isinstance(grant, chat_tokens.TokenGrant)
        self.assertEqual(grant.expires_at - grant.issued_at, timedelta(hours=1))
        self.assertEqual(chat_tokens.TOKEN_LIFETIME, timedelta(hours=1))
        self.assertEqual(grant.user_ref, "0" * 32)

    def test_refusals(self) -> None:
        cases = {
            "suspended": (
                {"account": chat_tokens.TokenAccount("suspended", 2)},
                "account_not_active",
            ),
            "deletion": (
                {"account": chat_tokens.TokenAccount("deletion_pending", 2)},
                "account_not_active",
            ),
            "unverified": (
                {"account": chat_tokens.TokenAccount("unverified", 1)},
                "account_not_active",
            ),
            "signed out": (
                {"session": chat_tokens.TokenSession("revoked", 1, NOW + timedelta(days=1))},
                "session_not_valid",
            ),
            "expired": ({"session": chat_tokens.TokenSession("valid", 1, NOW)}, "session_expired"),
            "stale epoch": (
                {"account": chat_tokens.TokenAccount("active", 2)},
                "session_epoch_stale",
            ),
            "no identity": ({"user_ref": None}, "no_chat_identity"),
            "deactivated identity": ({"identity_active": False}, "no_chat_identity"),
        }
        for label, (changes, code) in cases.items():
            with self.subTest(label):
                self.assertEqual(self.grant(**changes), chat_tokens.TokenRefusal(code))

    def test_a_naive_time_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.grant(now=datetime(2026, 10, 5, 12, 0))


if __name__ == "__main__":
    unittest.main()
