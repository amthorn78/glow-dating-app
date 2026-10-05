"""The outbox events the chat adapter writes (schema ``glow-chat-1``).

Each event carries only an aggregate reference, its version and a payload reference
(the data model: no chat, token or birth body in the outbox). Five of them are
delivered to the chat provider, each as exactly one provider call; the others are
logical events for later consumers and make no provider call.
"""

CHAT_SCHEMA_VERSION = "glow-chat-1"

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
    MATCH_ACTIVATED: "create_channel",
    MESSAGE_SUBMITTED: "send_message",
    CONTACT_REVOKED: "remove_members",
    ACCESS_REVOKED: "deactivate_user",
    SESSION_EPOCH_BUMPED: "revoke_user_tokens",
}
