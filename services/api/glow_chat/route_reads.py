"""The conversation reads as chat's routes serve them (the SV4 brief's D8 and D9), sealed until
integration.

``RouteConversationReads`` is ``glow_chat.reads.OrmConversationReads`` with two additions, and
``reads.py`` is unchanged: the history read is the adapter's own, and the read rule, the causes,
the shared locks, the clock and the refusal of a caller's transaction are its, called as they
are.

**The list's locks** (D8; the P11 plan's C1 finding 4). The adapter's list locks every account
and every active match of the member, so its 200 cap bounds the output, not the locked set. Here
the list first bounds its candidates, with no lock: the member's active matches, ranked as the
list is ordered (those with a message first, by the latest activity the member may see, then by
match ID, newest first), the top ``LIST_BOUND`` (200). Then it locks only those, ``FOR SHARE``,
in the canonical order, one statement per table: every account they name with the member's own,
by ID; then their matches, by ID; then the member's session; then ``chat.history``'s pointer
(SV2's D19 order), as the adapter's list does. Each candidate is then judged under D5's read rule
by the adapter's own helpers. A candidate whose rank moved between the bound and the locks is
judged on its locked rows; a hidden one leaves its place empty, so the list can hold fewer than
200 conversations when more than 200 matches are active.

**The read-only mark** (D9). Each conversation the list serves, and the read cursor's answer,
carries whether D5 serves it read-only: whether any cause is present, read by the adapter's own
``_causes`` in the same transaction, under the same shared account locks that every writer of a
profile, a consent decision or an account state takes first, so it reads what the rule read. The
rule has already served the conversation, so every cause present reads ``read_only``.

There is no switch here (DM-13 2.1): a probe only observes the hold points, as the adapter's do.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from glow_chat.contact import _Refused
from glow_chat.reads import (
    _ACCEPTED,
    _JOIN,
    _JOIN_ARGS,
    READABLE_OTHER_STATES,
    OrmConversationReads,
    _blocked,
    _causes,
    _clock,
    _history,
    _lock_shared,
    _signal,
    readable,
)
from glow_domain import chat
from glow_domain.chat import TransactionProbe
from glow_domain.chat_reads import LIST_LIMIT, ConversationEntry, ReadCursorCommand
from glow_persistence.models import AccountSession, ChatBinding, Match

# D8: the candidates the list locks, at most; the list's own ceiling.
LIST_BOUND = LIST_LIMIT

_ACCOUNTS = "glow_persistence_appaccount"
_MATCHES = "glow_persistence_match"
_SESSIONS = "glow_persistence_accountsession"

# The latest activity of one match the member may see, as the adapter's list orders it
# (``OrmConversationReads._entry``'s marker): an accepted message's acceptance, or one of the
# member's own pending or failed submissions; never the other member's unsent ones.
_LATEST = (
    "(SELECT max(CASE WHEN s.state = 'accepted' THEN e.delivered_at ELSE e.available_at END) "
    + _JOIN
    + " WHERE s.binding_id = b.id AND (("
    + _ACCEPTED
    + ") OR (s.actor_id = %s AND s.state IN ('pending', 'failed'))))"
)
# D8: the bounded candidates, with no lock: one statement.
CANDIDATES = (
    "SELECT m.id, m.account_low_id, m.account_high_id, "
    + _LATEST
    + " AS latest_at FROM glow_persistence_match m"
    " LEFT JOIN glow_persistence_chatbinding b ON b.match_id = m.id"
    " WHERE m.state = 'active' AND (m.account_low_id = %s OR m.account_high_id = %s)"
    " ORDER BY latest_at DESC NULLS LAST, m.id DESC LIMIT %s"
)


@dataclass(frozen=True)
class ServedEntry(ConversationEntry):
    """A conversation the routes serve: the adapter's entry, and whether D5 serves it read-only."""

    read_only: bool = False


def _lock_many(
    cursor: Any, table: str, ids: Sequence[UUID], columns: tuple[str, ...]
) -> dict[UUID, tuple[Any, ...]]:
    """Rows by primary key, ``FOR SHARE``, in one statement, in key order: PostgreSQL locks the
    rows as the sorted result reaches its lock step, so they are taken in that order. A row that
    is absent is absent from the answer; the caller judges it."""
    if not ids:
        return {}
    cursor.execute(
        f"SELECT id, {', '.join(columns)} FROM {table} WHERE id = ANY(%s) ORDER BY id FOR SHARE",
        [list(ids)],
    )
    return {row[0]: tuple(row[1:]) for row in cursor.fetchall()}


class RouteConversationReads(OrmConversationReads):
    """The adapter's reads, with D8's bounded list and D9's read-only mark."""

    @staticmethod
    def candidates(cursor: Any, me: UUID) -> list[tuple[UUID, UUID, UUID]]:
        """D8: the member's active matches, ranked as the list orders them, the top
        ``LIST_BOUND``, read with no lock."""
        # The latest activity's parameters come first, as its select-list item does.
        cursor.execute(CANDIDATES, [*_JOIN_ARGS, me, me, me, LIST_BOUND])
        return [(row[0], row[1], row[2]) for row in cursor.fetchall()]

    @staticmethod
    def _read_only(actor_id: UUID, other_id: UUID, other_state: str) -> bool:
        """D9: whether a conversation the rule serves has a cause, which it serves read-only."""
        return bool(_causes(actor_id, other_id, other_state))

    def _list(
        self, cursor: Any, probe: TransactionProbe | None, session_id: UUID
    ) -> tuple[ConversationEntry, ...]:
        """The adapter's list, bounded before it locks (D8), each entry marked (D9)."""
        session_account = (
            AccountSession.objects.filter(pk=session_id)
            .values_list("account_id", flat=True)
            .first()
        )
        if session_account is None:
            raise _Refused(chat.SESSION_MISSING)
        me: UUID = session_account
        matches = self.candidates(cursor, me)
        accounts = _lock_many(
            cursor,
            _ACCOUNTS,
            sorted({me} | {a for _, low, high in matches for a in (low, high)}),
            ("state", "session_epoch"),
        )
        _signal(probe, "after_first_lock")
        locked_matches = _lock_many(
            cursor,
            _MATCHES,
            sorted(match_id for match_id, _, _ in matches),
            ("state", "account_low_id", "account_high_id"),
        )
        locked_account, session_state, session_epoch, expires_at = _lock_shared(
            _SESSIONS, session_id, ("account_id", "state", "epoch", "expires_at"), cursor
        )
        # D5: the setting's pointer, after the row locks (SV2's D19 order).
        history = _history(cursor)
        _signal(probe, "after_locks")
        now = _clock(cursor)
        # The session's checks, as the adapter's list makes them.
        if locked_account != me:
            raise _Refused(chat.SESSION_CHANGED)
        if me not in accounts:
            raise _Refused(chat.ACCOUNT_MISSING)
        my_state, my_epoch = accounts[me]
        if my_state != "active":
            raise _Refused(chat.ACCOUNT_NOT_ACTIVE)
        if session_state != "valid":
            raise _Refused(chat.SESSION_NOT_VALID)
        if expires_at <= now:
            raise _Refused(chat.SESSION_EXPIRED)
        if session_epoch != my_epoch:
            raise _Refused(chat.SESSION_EPOCH_STALE)
        entries: list[ConversationEntry] = []
        for match_id, low_id, high_id in matches:
            locked = locked_matches.get(match_id)
            other_id = high_id if me == low_id else low_id
            if locked is None or other_id not in accounts:
                continue
            state, locked_low, locked_high = locked
            if state != "active" or (locked_low, locked_high) != (low_id, high_id):
                continue
            other_state = str(accounts[other_id][0])
            if other_state not in READABLE_OTHER_STATES or _blocked(me, other_id):
                continue
            try:
                causes = _causes(me, other_id, other_state)
            except _Refused:
                continue
            if not readable(causes, history):
                continue
            binding_id = (
                ChatBinding.objects.filter(match_id=match_id).values_list("id", flat=True).first()
            )
            entry = self._entry(cursor, match_id, me, binding_id)
            read_only = bool(causes)
            entries.append(ServedEntry(entry.match_id, entry.unread, entry.latest, read_only))
        # The adapter's order: the latest activity first; conversations with no message after
        # them; the match ID decides a tie.
        entries.sort(
            key=lambda entry: (
                entry.latest is not None,
                entry.latest.at if entry.latest is not None else now,
                entry.match_id,
            ),
            reverse=True,
        )
        return tuple(entries[:LIST_LIMIT])

    def _move(
        self, cursor: Any, probe: TransactionProbe | None, command: ReadCursorCommand
    ) -> tuple[bool, ConversationEntry]:
        """The adapter's read-cursor command, its answer marked (D9) in the same transaction."""
        moved, entry = super()._move(cursor, probe, command)
        actor_id: UUID = (
            AccountSession.objects.filter(pk=command.session_id)
            .values_list("account_id", flat=True)
            .get()
        )
        low_id, high_id = (
            Match.objects.filter(pk=command.match_id)
            .values_list("account_low_id", "account_high_id")
            .get()
        )
        other_id: UUID = high_id if actor_id == low_id else low_id
        # The other account's row, which the rule locked ``FOR SHARE`` in this transaction, so
        # no writer has changed it since.
        cursor.execute(f"SELECT state FROM {_ACCOUNTS} WHERE id = %s", [other_id])
        other_state = str(cursor.fetchone()[0])
        read_only = self._read_only(actor_id, other_id, other_state)
        return moved, ServedEntry(entry.match_id, entry.unread, entry.latest, read_only)


def is_read_only(entry: ConversationEntry) -> bool:
    """Whether a served entry is read-only; an entry of the adapter's own is never marked."""
    return isinstance(entry, ServedEntry) and entry.read_only


def marked(entries: Sequence[ConversationEntry]) -> list[tuple[ConversationEntry, bool]]:
    return [(entry, is_read_only(entry)) for entry in entries]
