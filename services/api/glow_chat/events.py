"""The outbox events the chat adapter writes (schema ``glow-chat-1``).

Each event carries only an aggregate reference, its version and a payload reference
(the data model: no chat, token or birth body in the outbox). Six of them are
delivered to the chat provider, each as exactly one provider call; the others are
logical events for later consumers and make no provider call.

``identity_created`` (P06.2 B1, CX4) is written when match activation creates a
member's ``ChatIdentity``, before the channel's own event in the same transaction, and
is delivered as the provisioning of that user; the channel event never waits for it
(DM-15 3.2): an unprovisioned member dead-letters the channel.
"""

CHAT_SCHEMA_VERSION = "glow-chat-1"

IDENTITY_CREATED = "identity_created"
MATCH_ACTIVATED = "match_activated"
MESSAGE_SUBMITTED = "message_submitted"
CONTACT_REVOKED = "contact_revoked"
ACCESS_REVOKED = "access_revoked"
SESSION_EPOCH_BUMPED = "session_epoch_bumped"
BLOCK_CHANGED = "block_changed"
SESSION_REVOKED = "session_revoked"
SESSION_EXPIRED = "session_expired"
PROFILE_PAUSED = "profile_paused"
PROFILE_RESUMED = "profile_resumed"
PROFILE_RESTRICTED = "profile_restricted"
CONSENT_ACCEPTED = "consent_accepted"
CONSENT_WITHDRAWN = "consent_withdrawn"

# Event type -> the one provider operation its delivery makes.
DELIVERED: dict[str, str] = {
    IDENTITY_CREATED: "provision_user",
    MATCH_ACTIVATED: "create_channel",
    MESSAGE_SUBMITTED: "send_message",
    CONTACT_REVOKED: "remove_members",
    ACCESS_REVOKED: "deactivate_user",
    SESSION_EPOCH_BUMPED: "revoke_user_tokens",
}
