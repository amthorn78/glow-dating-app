"""G-04's records (SV4 B2; its brief's D27; P09.3a's matrix, G-04, for the fraud-ban rows USF-18,
UST-08, UST-14, UST-15, UST-17 and UST-18): who received a member's messages, and who answered.
Sealed and not served: no route, view or runtime module names it, and the served runtime imports
none of it. P07.2's staff tooling will read it, and the fraud-ban flag and the notice itself are
P07.2's; a hold that survives a hard deletion is P08.1's (G-05), since ``MessageSubmission.actor``
cascades.

**No new table.** The records are already Glow's rows: each accepted ``MessageSubmission`` names its
sender and its binding's match, whose other member received it, and no writer deletes either today
(a deletion is ``deletion_pending``; a block or an unmatch changes the match's state only). So the
read keeps every recipient after an unmatch and after a block. It names accounts and a yes or no
only, never a message's text, a provider identifier or a count (DM-101's note on D27).
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from django.db import connection

# One statement, so one snapshot: each match in which the sender has an accepted message, its
# other member, and whether that member has an accepted message of their own in it.
RECIPIENTS = (
    "SELECT m.id,"
    " CASE WHEN m.account_low_id = %(sender)s THEN m.account_high_id ELSE m.account_low_id END,"
    " EXISTS (SELECT 1 FROM glow_persistence_messagesubmission r"
    " JOIN glow_persistence_chatbinding rb ON rb.id = r.binding_id"
    " WHERE rb.match_id = m.id AND r.state = 'accepted' AND r.actor_id = CASE"
    " WHEN m.account_low_id = %(sender)s THEN m.account_high_id ELSE m.account_low_id END)"
    " FROM glow_persistence_match m"
    " WHERE EXISTS (SELECT 1 FROM glow_persistence_messagesubmission s"
    " JOIN glow_persistence_chatbinding b ON b.id = s.binding_id"
    " WHERE b.match_id = m.id AND s.state = 'accepted' AND s.actor_id = %(sender)s)"
    " ORDER BY m.id"
)


@dataclass(frozen=True)
class Recipient:
    """A member who received an accepted message from the sender, in one match, and whether they
    sent one back there."""

    account_id: UUID
    match_id: UUID
    answered: bool


def message_recipients(sender: UUID) -> tuple[Recipient, ...]:
    """Each member who received an accepted message from ``sender``, by match, whatever the match's
    state now, and whether they answered in that match."""
    with connection.cursor() as cursor:
        cursor.execute(RECIPIENTS, {"sender": sender})
        rows = cursor.fetchall()
    return tuple(Recipient(UUID(str(row[1])), UUID(str(row[0])), bool(row[2])) for row in rows)
