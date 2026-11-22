"""The chat token revocation's cut-off (P06.2 item 4, D6; DM-15 5.2).

No provider token is issued (OD-45): Glow's API serves the conversation, and SV4 A1 removed
the token grant and its signer (its brief's D7). Every session-epoch bump still revokes the
user's provider tokens (``glow_chat.delivery``), as defence in depth kept until the live
adapter is configured at integration (DM-96).

A provider's per-user token revocation compares a token's issue time with its cut-off in
whole seconds. ``revocation_cutoff_sent`` is the value sent for a cut-off: the next whole
second, strictly after the exact time (DM-15 5.2), so every token issued at or before the
cut-off is covered; Glow keeps the exact time.
"""

from __future__ import annotations

from datetime import datetime, timedelta


def revocation_cutoff_sent(cutoff: datetime) -> datetime:
    """The cut-off as sent to the provider: the next whole second, strictly greater than
    the exact cut-off, so a cut-off of exactly 10.000000 s is sent as 11 (DM-15 5.2). A
    token whose ``iat`` is the issue time truncated to the second is then revoked whenever
    it was issued at or before the cut-off."""
    if cutoff.tzinfo is None:
        raise ValueError("an aware time is required")
    return cutoff.replace(microsecond=0) + timedelta(seconds=1)
