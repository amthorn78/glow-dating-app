"""The conversation reads behind ``glow_domain.chat_reads.ConversationReads`` (P06.2 Stage
C1; the brief's "Stage C under OD-45", points b, c and e, with DM-22's conditions).

It carries the send's protocol to the reads, as B1's grant does:

- every transaction runs at READ COMMITTED and takes the send's row locks in the send's
  canonical order (the lower account, the higher account, the match, the session), but
  ``FOR SHARE``: a read waits for a revocation in flight, which holds those rows ``FOR
  UPDATE``, and then reads its result; a revocation waits for a read in flight; no reader
  excludes another;
- every check is the send's, in the send's order, on the rows as locked, with the time
  read from ``clock_timestamp()`` after the locks (``OrmContactPersistence``'s own lock,
  clock and profile-and-consent helpers, so the two cannot drift);
- the history read checks in one transaction, which ends before the provider call; the
  call runs outside any transaction, so no lock is held across it and a safety action
  never waits on the provider; then a new transaction takes the same shared locks and
  checks again, and the page is returned only if that check passes too (DM-22 3.2);
- no read runs inside a transaction its caller has open (C1-C2, C1-C1's re-review, R1):
  inside an atomic block (``ATOMIC_REQUESTS``, a view's ``atomic``, a Django test case's
  own block) or on a connection with autocommit off (``transaction.set_autocommit(False)``)
  the first check would take its shared locks inside the caller's transaction, and they
  would stay held until it ends, across the provider call. So each read's transaction
  refuses before any statement: an ``error`` result, ``transaction_open``, with no lock
  taken and no provider called. Behind that, every transaction is durable (C1-C1, the
  exact-head review's finding 1), and the history read checks both conditions again
  immediately before the provider call;
- a read writes nothing (DM-22 2.3); the read-cursor command writes only the member's own
  ``ChatReadCursor`` row, after the same checks, in one transaction, with no provider call.

There is no switch here (DM-13 2.1). A probe may observe a read at its hold points; it
only signals and waits.

**Glow's rows define the conversation** (point b): a page is the match's accepted
``MessageSubmission`` rows, in acceptance order (``glow_domain.chat_reads``, DM-22 2.2):
the ``delivered_at`` of each message's ``message_submitted`` event, then its ``sequence``.
The member's own pending and failed submissions follow on the newest page only, with
their spool text, to that member alone; the other member's never appear. The provider is
asked only for the texts of the page's accepted messages, by the IDs Glow committed, in
one call; a page with no accepted message makes no call.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import IntegrityError, connection, transaction
from django.db.models import Q

from glow_chat import events
from glow_chat.contact import DEADLOCK_DETECTED, OrmContactPersistence, _Refused
from glow_domain import chat
from glow_domain.chat import TransactionProbe
from glow_domain.chat import TransactionTrace as Trace
from glow_domain.chat_provider import CHANNEL_UNAVAILABLE, error_code
from glow_domain.chat_reads import (
    CURSOR_INVALID,
    LIST_LIMIT,
    MESSAGE_UNAVAILABLE,
    UNSENT_LIMIT,
    AcceptedRow,
    ConversationEntry,
    CursorResult,
    HistoryPage,
    HistoryRequest,
    LatestMarker,
    ListResult,
    PageCursor,
    ReadCursorCommand,
    ReadProbe,
    ReadResult,
    TextReader,
    UnsentRow,
    page_messages,
)
from glow_persistence.models import AccountSession, Block, ChatBinding, ChatReadCursor, Match

# The send's own helpers: one lock, one clock and one profile-and-consent check for the
# send, the grant and the reads.
_lock_shared = OrmContactPersistence._lock_shared
_clock = OrmContactPersistence._clock
_contact_state_checks = OrmContactPersistence._contact_state_checks

_SUBMISSIONS = "glow_persistence_messagesubmission"
_EVENTS = "glow_persistence_outboxevent"
# A submission joined to its own ``message_submitted`` event of the chat schema.
_JOIN = (
    f"FROM {_SUBMISSIONS} s JOIN {_EVENTS} e ON e.aggregate_id = s.id"
    " AND e.event_type = %s AND e.schema_version = %s"
)
_JOIN_ARGS = [events.MESSAGE_SUBMITTED, events.CHAT_SCHEMA_VERSION]
# An accepted message: accepted, with its receipt recorded on its delivered event.
_ACCEPTED = "s.state = 'accepted' AND e.state = 'delivered'"
_ACCEPTED_ROW = (
    "SELECT s.id, s.actor_id, s.contact_version, s.request_digest, s.provider_message_ref,"
    " e.delivered_at, e.sequence " + _JOIN + " WHERE s.binding_id = %s AND " + _ACCEPTED
)

Position = tuple[datetime, int]

# The history read found an atomic block open just before the provider call: no
# provider call (DM-22 3.2). A second line behind ``TRANSACTION_OPEN``.
ATOMIC_BLOCK_OPEN = "atomic_block_open"
# The caller has a transaction open on the connection: an atomic block (a Django test
# case's included) or autocommit off. A read refuses before any statement (C1-C2, R1).
TRANSACTION_OPEN = "transaction_open"


class _Rollback(Exception):
    def __init__(self, reason: str, trace: Trace) -> None:
        super().__init__(reason)
        self.reason = reason
        self.trace = trace


@dataclass(frozen=True)
class _Members:
    actor_id: UUID
    other_id: UUID


@dataclass(frozen=True)
class _Selected:
    """What the history read's first check selected under its locks."""

    channel_ref: str | None
    accepted: tuple[AcceptedRow, ...]
    unsent: tuple[UnsentRow, ...]
    older: PageCursor | None
    newer: PageCursor | None


def _signal(probe: TransactionProbe | None, name: str) -> None:
    callback = getattr(probe, name, None) if probe is not None else None
    if callback is not None:
        callback()


def _caller_transaction_open() -> bool:
    """An atomic block is open (a Django test case's included), or autocommit is off, so
    a transaction begun by the caller would hold whatever a read locks (DM-22 3.2)."""
    return connection.in_atomic_block or not connection.get_autocommit()


def _run[T](
    body: Callable[[Any, TransactionProbe | None], T], probe: TransactionProbe | None
) -> tuple[T | None, str, str, Trace | None]:
    """One transaction: ``(value, outcome, reason, trace)``. A refusal rolls back and is a
    result; a deadlock or any other database error becomes a result; nothing is retried.

    It refuses before any statement, and before it enters its block, while the caller has a
    transaction open (an atomic block, a test case's included, or autocommit off): an
    ``error`` result, ``transaction_open``, with no lock taken (C1-C2, R1). This is checked
    outside the block, since inside any atomic block autocommit is off by design. The
    block is also durable: inside an enclosing atomic block Django raises ``RuntimeError``
    before any statement, and that is an ``error`` result, never a page (DM-22 3.2)."""
    trace: Trace | None = None
    try:
        # Inside the ``try``: reading autocommit may open the connection, and a database
        # that cannot be reached is an ``error`` result as before, never an exception.
        if _caller_transaction_open():
            return None, "error", TRANSACTION_OPEN, None
        with transaction.atomic(durable=True):
            cursor = connection.cursor()
            # The transaction's first statement: its backend and its start.
            cursor.execute("SELECT pg_backend_pid(), now()")
            pid, started = cursor.fetchone()
            trace = Trace(int(pid), started)
            if probe is not None and probe.on_begin is not None:
                probe.on_begin(int(pid))
            try:
                value = body(cursor, probe)
            except _Refused as refused:
                raise _Rollback(refused.reason, replace(trace, ended_at=_clock(cursor))) from None
            _signal(probe, "before_commit")
    except _Rollback as rollback:
        return None, "refused", rollback.reason, rollback.trace
    except Exception as exc:  # noqa: BLE001 - a result the caller judges; never retried
        cause = exc.__cause__
        # The driver's DeadlockDetected, by its SQLSTATE: the API installs no driver.
        if getattr(cause, "sqlstate", None) == DEADLOCK_DETECTED:
            return None, "deadlock", "DeadlockDetected", trace
        if isinstance(exc, IntegrityError):
            return None, "error", f"IntegrityError:{type(cause).__name__}", trace
        return None, "error", type(exc).__name__, trace
    return value, "ok", "", trace


def _blocked(first: UUID, second: UUID) -> bool:
    return bool(
        Block.objects.filter(state="active")
        .filter(Q(actor_id=first, target_id=second) | Q(actor_id=second, target_id=first))
        .exists()
    )


def _fetch(cursor: Any, sql: str, args: list[Any]) -> list[tuple[Any, ...]]:
    cursor.execute(sql, args)
    return list(cursor.fetchall())


def _position(cursor: Any, submission_id: UUID, binding_id: UUID) -> Position | None:
    """An accepted message's place in its conversation, if it is one of this binding's."""
    rows = _fetch(
        cursor,
        "SELECT e.delivered_at, e.sequence "
        + _JOIN
        + " WHERE s.id = %s AND s.binding_id = %s AND "
        + _ACCEPTED,
        [*_JOIN_ARGS, submission_id, binding_id],
    )
    return (rows[0][0], int(rows[0][1])) if rows else None


class OrmConversationReads:
    """``ConversationReads`` over ``glow_persistence``'s models, with the provider port's
    text read for the history read's texts."""

    def __init__(self, texts: TextReader) -> None:
        self.texts = texts

    # -- the send's checks, under the send's shared locks -------------------------------

    @staticmethod
    def _authorize(
        cursor: Any, probe: TransactionProbe | None, session_id: UUID, match_id: UUID
    ) -> _Members:
        """The send's checks for one conversation, in the send's order (``contact.send``),
        on the rows locked ``FOR SHARE`` in the send's order."""
        # Only identifiers are read before the locks: a match's pair and a session's
        # account never change, and the locked rows are checked against them (F2).
        first_pair = (
            Match.objects.filter(pk=match_id)
            .values_list("account_low_id", "account_high_id")
            .first()
        )
        session_account = (
            AccountSession.objects.filter(pk=session_id)
            .values_list("account_id", flat=True)
            .first()
        )
        if first_pair is None:
            raise _Refused(chat.MATCH_MISSING)
        if session_account is None:
            raise _Refused(chat.SESSION_MISSING)
        low_id, high_id = first_pair
        if session_account not in (low_id, high_id):
            raise _Refused(chat.NOT_A_MEMBER)
        actor_id: UUID = session_account
        other_id: UUID = high_id if actor_id == low_id else low_id
        low_state, low_epoch = _lock_shared(
            "glow_persistence_appaccount", low_id, ("state", "session_epoch"), cursor
        )
        _signal(probe, "after_first_lock")
        high_state, high_epoch = _lock_shared(
            "glow_persistence_appaccount", high_id, ("state", "session_epoch"), cursor
        )
        match_state, match_low, match_high = _lock_shared(
            "glow_persistence_match",
            match_id,
            ("state", "account_low_id", "account_high_id"),
            cursor,
        )
        locked_account, session_state, session_epoch, expires_at = _lock_shared(
            "glow_persistence_accountsession",
            session_id,
            ("account_id", "state", "epoch", "expires_at"),
            cursor,
        )
        _signal(probe, "after_locks")
        now = _clock(cursor)
        if match_state != "active":
            raise _Refused(chat.MATCH_NOT_ACTIVE)
        if (match_low, match_high) != (low_id, high_id):
            raise _Refused(chat.MATCH_CHANGED)
        if locked_account != actor_id:
            raise _Refused(chat.SESSION_CHANGED)
        if low_state != "active" or high_state != "active":
            raise _Refused(chat.ACCOUNT_NOT_ACTIVE)
        if session_state != "valid":
            raise _Refused(chat.SESSION_NOT_VALID)
        if expires_at <= now:
            raise _Refused(chat.SESSION_EXPIRED)
        if session_epoch != (low_epoch if actor_id == low_id else high_epoch):
            raise _Refused(chat.SESSION_EPOCH_STALE)
        if _blocked(actor_id, other_id):
            raise _Refused(chat.BLOCKED)
        # D5: both profiles visible and both onboarding consents accepted, read under the
        # account locks every writer of them takes.
        _contact_state_checks(low_id, high_id)
        return _Members(actor_id, other_id)

    # -- what a conversation shows the member ---------------------------------------------

    @staticmethod
    def _read_position(cursor: Any, match_id: UUID, account_id: UUID, binding_id: UUID) -> Any:
        last_read = (
            ChatReadCursor.objects.filter(match_id=match_id, account_id=account_id)
            .values_list("last_read_id", flat=True)
            .first()
        )
        return _position(cursor, last_read, binding_id) if last_read is not None else None

    @classmethod
    def _entry(
        cls, cursor: Any, match_id: UUID, actor_id: UUID, binding_id: UUID | None
    ) -> ConversationEntry:
        """Unread and the latest marker, from Glow's rows only. Unread counts the other
        member's accepted messages after the member's read cursor, in acceptance order
        (DM-22 6.3). The marker is the latest of the accepted messages and the member's own
        pending or failed submissions, never the other member's (6.1): its submission ID
        and its time, no text."""
        if binding_id is None:
            return ConversationEntry(match_id, 0, None)
        read = cls._read_position(cursor, match_id, actor_id, binding_id)
        unread_sql = (
            "SELECT count(*) "
            + _JOIN
            + " WHERE s.binding_id = %s AND "
            + _ACCEPTED
            + " AND s.actor_id <> %s"
        )
        unread_args: list[Any] = [*_JOIN_ARGS, binding_id, actor_id]
        if read is not None:
            unread_sql += " AND (e.delivered_at, e.sequence) > (%s, %s)"
            unread_args += [read[0], read[1]]
        unread = int(_fetch(cursor, unread_sql, unread_args)[0][0])
        latest = _fetch(
            cursor,
            "SELECT s.id, CASE WHEN s.state = 'accepted' THEN e.delivered_at"
            " ELSE e.available_at END AS latest_at "
            + _JOIN
            + " WHERE s.binding_id = %s AND (("
            + _ACCEPTED
            + ") OR (s.actor_id = %s AND s.state IN ('pending', 'failed')))"
            " ORDER BY latest_at DESC, e.sequence DESC LIMIT 1",
            [*_JOIN_ARGS, binding_id, actor_id],
        )
        marker = LatestMarker(latest[0][0], latest[0][1]) if latest else None
        return ConversationEntry(match_id, unread, marker)

    # -- the history read ---------------------------------------------------------------

    @staticmethod
    def _accepted(
        cursor: Any,
        binding_id: UUID,
        actor_id: UUID,
        where: str,
        args: list[Any],
        order: str,
        limit: int,
    ) -> list[AcceptedRow]:
        rows = _fetch(
            cursor,
            _ACCEPTED_ROW
            + where
            + f" ORDER BY e.delivered_at {order}, e.sequence {order} LIMIT %s",
            [*_JOIN_ARGS, binding_id, *args, limit],
        )
        return [
            AcceptedRow(row[0], row[1] == actor_id, row[5], int(row[2]), row[3], row[4])
            for row in rows
        ]

    @staticmethod
    def _unsent(cursor: Any, binding_id: UUID, actor_id: UUID) -> tuple[UnsentRow, ...]:
        """The member's own pending and failed submissions, the most recent ones, in the
        order they were sent."""
        rows = _fetch(
            cursor,
            "SELECT s.id, e.available_at, s.state, s.text "
            + _JOIN
            + " WHERE s.binding_id = %s AND s.actor_id = %s AND s.state IN ('pending', 'failed')"
            " ORDER BY e.available_at DESC, e.sequence DESC LIMIT %s",
            [*_JOIN_ARGS, binding_id, actor_id, UNSENT_LIMIT],
        )
        return tuple(UnsentRow(row[0], row[1], row[2], row[3]) for row in reversed(rows))

    def _select(
        self, cursor: Any, probe: TransactionProbe | None, request: HistoryRequest
    ) -> _Selected:
        """The first check, then the page's rows, under the same locks."""
        members = self._authorize(cursor, probe, request.session_id, request.match_id)
        page_cursor = request.cursor
        if page_cursor is not None and page_cursor.match_id != request.match_id:
            raise _Refused(CURSOR_INVALID)  # 6.4: bound to the match it was issued for
        binding = (
            ChatBinding.objects.filter(match_id=request.match_id)
            .values_list("id", "channel_ref")
            .first()
        )
        if binding is None:
            if page_cursor is not None:
                raise _Refused(CURSOR_INVALID)
            return _Selected(None, (), (), None, None)
        binding_id, channel_ref = binding
        actor, limit = members.actor_id, request.limit
        if page_cursor is None:
            rows = self._accepted(cursor, binding_id, actor, "", [], "DESC", limit + 1)
            more = len(rows) > limit
            accepted = rows[:limit][::-1]
            older = more
            at_head = True
        else:
            bound = _position(cursor, page_cursor.boundary, binding_id)
            if bound is None:
                raise _Refused(CURSOR_INVALID)
            if page_cursor.direction == "older":
                rows = self._accepted(
                    cursor,
                    binding_id,
                    actor,
                    " AND (e.delivered_at, e.sequence) < (%s, %s)",
                    [bound[0], bound[1]],
                    "DESC",
                    limit + 1,
                )
                older = len(rows) > limit
                accepted = rows[:limit][::-1]
                at_head = False
            else:
                rows = self._accepted(
                    cursor,
                    binding_id,
                    actor,
                    " AND (e.delivered_at, e.sequence) > (%s, %s)",
                    [bound[0], bound[1]],
                    "ASC",
                    limit + 1,
                )
                accepted = rows[:limit]
                older = bool(accepted)  # the boundary itself lies before them
                at_head = len(rows) <= limit
        match_id = request.match_id
        if accepted:
            newer: PageCursor | None = PageCursor("newer", match_id, accepted[-1].submission_id)
        elif page_cursor is not None and page_cursor.direction == "newer":
            newer = page_cursor  # nothing new yet: poll again from the same place
        else:
            newer = None
        older_cursor = (
            PageCursor("older", match_id, accepted[0].submission_id) if accepted and older else None
        )
        unsent = self._unsent(cursor, binding_id, actor) if at_head else ()
        return _Selected(channel_ref, tuple(accepted), unsent, older_cursor, newer)

    # The history read's steps, in the one order ``read_history`` runs them. They are
    # separate so the database job's planted controls (DM-22 3.3) can compose a broken
    # variant from these same steps; nothing here can change their order.

    def _first_check(
        self, request: HistoryRequest, probe: ReadProbe
    ) -> tuple[_Selected | None, ReadResult | None, Trace | None]:
        """The first check and the page's rows, in one transaction that ends here."""
        selected, outcome, reason, trace = _run(
            lambda cursor, held: self._select(cursor, held, request), probe.first
        )
        if selected is None:
            return None, ReadResult(_failed(outcome), reason, traces=_traces(trace)), trace
        return selected, None, trace

    def _provider_texts(self, selected: _Selected, probe: ReadProbe) -> tuple[dict[str, str], str]:
        """The provider call, outside any transaction: no lock is held across it (3.2). A
        failure is its Glow code (2.4); ``""`` when the texts came back."""
        if selected.channel_ref is None:
            return {}, CHANNEL_UNAVAILABLE
        asked = tuple(row.provider_message_ref for row in selected.accepted)
        try:
            texts = self.texts.read_message_texts(selected.channel_ref, asked)
        except Exception as error:  # noqa: BLE001 - kept only as its Glow code (2.4)
            return {}, error_code(error)
        if probe.after_provider_call is not None:
            probe.after_provider_call()
        return texts, ""

    def _final_check(
        self, request: HistoryRequest, probe: ReadProbe
    ) -> tuple[str, str, Trace | None]:
        """A new transaction that takes the same shared locks and makes the same checks,
        so it sees every revocation committed before it (3.2)."""
        _, outcome, reason, trace = _run(
            lambda cursor, held: self._authorize(
                cursor, held, request.session_id, request.match_id
            ),
            probe.final,
        )
        return outcome, reason, trace

    @staticmethod
    def _page(
        request: HistoryRequest, selected: _Selected, texts: dict[str, str], called: bool
    ) -> HistoryPage:
        messages, counted = page_messages(
            request.match_id, selected.accepted, selected.unsent, texts
        )
        return HistoryPage(
            request.match_id, messages, selected.older, selected.newer, called, counted
        )

    def read_history(
        self, request: HistoryRequest, *, probe: ReadProbe | None = None
    ) -> ReadResult:
        probe = probe or ReadProbe()
        selected, refused, first = self._first_check(request, probe)
        if selected is None:
            assert refused is not None
            return refused
        if not selected.accepted:
            # No accepted message: no provider call, and the one check is the answer.
            return ReadResult(
                "read", page=self._page(request, selected, {}, False), traces=_traces(first)
            )
        if _caller_transaction_open():
            # 3.2: an enclosing transaction would hold the first check's locks across the
            # call. ``_run`` refuses it before the first check; this second line refuses it
            # again immediately before the call, whatever ran in between.
            reason = ATOMIC_BLOCK_OPEN if connection.in_atomic_block else TRANSACTION_OPEN
            return ReadResult("error", reason, traces=_traces(first))
        texts, failure = self._provider_texts(selected, probe)
        if failure:
            return ReadResult("refused", failure, traces=_traces(first))
        outcome, reason, final = self._final_check(request, probe)
        traces = _traces(first, final)
        if outcome != "ok":
            return ReadResult(_failed(outcome), reason, traces=traces)
        return ReadResult("read", page=self._page(request, selected, texts, True), traces=traces)

    # -- the conversation list ----------------------------------------------------------

    def _list(
        self, cursor: Any, probe: TransactionProbe | None, session_id: UUID
    ) -> tuple[ConversationEntry, ...]:
        """The session's checks, then each conversation's own, under the shared locks of
        every account and match it names and of the session, in the canonical order
        (accounts, then matches, then the session). A conversation the member may no
        longer see is not listed. No provider is called."""
        session_account = (
            AccountSession.objects.filter(pk=session_id)
            .values_list("account_id", flat=True)
            .first()
        )
        if session_account is None:
            raise _Refused(chat.SESSION_MISSING)
        me: UUID = session_account
        matches = sorted(
            Match.objects.filter(
                Q(account_low_id=me) | Q(account_high_id=me), state="active"
            ).values_list("id", "account_low_id", "account_high_id")
        )
        accounts: dict[UUID, tuple[Any, Any]] = {}
        for index, account_id in enumerate(
            sorted({me} | {a for _, low, high in matches for a in (low, high)})
        ):
            accounts[account_id] = _lock_shared(
                "glow_persistence_appaccount", account_id, ("state", "session_epoch"), cursor
            )
            if index == 0:
                _signal(probe, "after_first_lock")
        locked_matches = {
            match_id: _lock_shared(
                "glow_persistence_match",
                match_id,
                ("state", "account_low_id", "account_high_id"),
                cursor,
            )
            for match_id, _, _ in matches
        }
        locked_account, session_state, session_epoch, expires_at = _lock_shared(
            "glow_persistence_accountsession",
            session_id,
            ("account_id", "state", "epoch", "expires_at"),
            cursor,
        )
        _signal(probe, "after_locks")
        now = _clock(cursor)
        # The session's checks (point c), as the send makes them.
        if locked_account != me:
            raise _Refused(chat.SESSION_CHANGED)
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
            state, locked_low, locked_high = locked_matches[match_id]
            other_id = high_id if me == low_id else low_id
            if state != "active" or (locked_low, locked_high) != (low_id, high_id):
                continue
            if accounts[other_id][0] != "active" or _blocked(me, other_id):
                continue
            try:
                _contact_state_checks(low_id, high_id)
            except _Refused:
                continue
            binding_id = (
                ChatBinding.objects.filter(match_id=match_id).values_list("id", flat=True).first()
            )
            entries.append(self._entry(cursor, match_id, me, binding_id))
        # The latest activity first; conversations with no message after them; the match ID
        # decides a tie, so the order is deterministic.
        entries.sort(
            key=lambda entry: (
                entry.latest is not None,
                entry.latest.at if entry.latest is not None else now,
                entry.match_id,
            ),
            reverse=True,
        )
        return tuple(entries[:LIST_LIMIT])

    def list_conversations(
        self, session_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ListResult:
        listed, outcome, reason, trace = _run(
            lambda cursor, held: self._list(cursor, held, session_id), probe
        )
        if listed is None:
            return ListResult(_failed(outcome), reason, trace=trace)
        return ListResult("listed", conversations=listed, trace=trace)

    # -- the read-cursor command --------------------------------------------------------

    def _move(
        self, cursor: Any, probe: TransactionProbe | None, command: ReadCursorCommand
    ) -> tuple[bool, ConversationEntry]:
        members = self._authorize(cursor, probe, command.session_id, command.match_id)
        binding_id = (
            ChatBinding.objects.filter(match_id=command.match_id)
            .values_list("id", flat=True)
            .first()
        )
        target = (
            _position(cursor, command.submission_id, binding_id) if binding_id is not None else None
        )
        if binding_id is None or target is None:
            raise _Refused(MESSAGE_UNAVAILABLE)
        actor = members.actor_id
        row = (
            ChatReadCursor.objects.select_for_update()
            .filter(match_id=command.match_id, account_id=actor)
            .first()
        )
        if row is None:
            try:
                with transaction.atomic():
                    ChatReadCursor.objects.create(match_id=command.match_id, account_id=actor)
            except IntegrityError:
                pass  # another command created it first; it is locked below
            row = ChatReadCursor.objects.select_for_update().get(
                match_id=command.match_id, account_id=actor
            )
        current = _position(cursor, row.last_read_id, binding_id) if row.last_read_id else None
        moved = current is None or target > current
        if moved:
            # Forward only, in acceptance order (DM-22 2.2, 6.3); a repeat changes nothing.
            row.last_read_id = command.submission_id
            row.version += 1
            row.save(update_fields=["last_read", "version", "updated_at"])
        return moved, self._entry(cursor, command.match_id, actor, binding_id)

    def move_read_cursor(
        self, command: ReadCursorCommand, *, probe: TransactionProbe | None = None
    ) -> CursorResult:
        done, outcome, reason, trace = _run(
            lambda cursor, held: self._move(cursor, held, command), probe
        )
        if done is None:
            return CursorResult(_failed(outcome), reason, trace=trace)
        moved, entry = done
        return CursorResult("moved" if moved else "no_change", entry=entry, trace=trace)


def _failed(outcome: str) -> Any:
    """A transaction's failure as a read's outcome: a refusal, a deadlock or an error."""
    return outcome if outcome in ("deadlock", "error") else "refused"


def _traces(*traces: Trace | None) -> tuple[Trace, ...]:
    return tuple(trace for trace in traces if trace is not None)
