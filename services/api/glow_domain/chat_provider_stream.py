"""The Stream adapter on the chat provider port, and the client token's signer (P06.2
Stage B2; the brief's design points c to e, with DM-16's conditions).

**Its place.** Beside the port and its fixture adapter in ``glow_domain``, because the seal
(DM-16 2.3) requires that it import nothing from Django, ``glow_persistence`` or
``glow_chat``: only the port, the token module and the SDK. ``glow_domain`` is the
Django-free package, so the harness can import this module by path without Django
(DM-16 4.6), and the runtime's seal keeps it out of every runtime import
(``tests/test_chat_sealed_runtime.py``). P11 decides how the runtime builds a client and
where the pin moves.

**An injected client, nothing else** (2.4). The adapter holds the ``getstream`` client it
is given and never constructs one: no ``Stream(...)``, no ``Stream.from_env()``, no
settings loader, no environment variable. In the conformance run the client is the
harness's own, so every request passes its guard, budget ledger and redaction.

**What it sends** (design point d; DM-16 4.2). Provisioning creates the user with its ID
only; channel creation in ``glow-match`` with exactly the two members and the first of them
as the creator (``created_by_id``: Stream's server-side creation requires a creator, as every
creation of P06.1's harness sent one; it is one of the two members, never a name, image or
custom field); a message with its committed ID, its text and its sender; removal of both
members; deactivation with an empty body; a per-user revocation with the cut-off it is
given, as ``glow_domain.chat_tokens.revocation_cutoff_sent`` produced it (3.4). No name,
image, role or custom field is ever sent, and no ID shape is enforced (DM-13 2.1).

**Read first, then act** (4.4). Provisioning reads the user and creates it only when
Stream does not have it, so it never changes an existing user: never resets a field,
reactivates or clears a token cut-off (a deactivated user counts as held). Channel creation
reads the channel and creates it only when absent, so a repeat never sends the members to
an existing channel. Removal reads the channel's members and sends the removal only while
one of the two is present. Deactivation and revocation read the user and never create one;
a revocation whose cut-off is not later than the one Stream holds sends nothing, so a repeat
never lowers a cut-off. ``already=True`` is returned where the read shows the object is
there, and for a message whose ID Stream reports as existing.

**The exception boundary** (4.1). Only the SDK's own API error (``StreamApiException``) and
its transport errors and timeouts (``StreamTransportException``, ``httpx.TransportError``)
are mapped to Glow codes. Every other exception propagates unchanged: the harness's
``GuardRefused``, ``RunStopped`` and ``GuardrailStop`` among them. A mapped error is raised
after its ``except`` block, so neither its ``__cause__`` nor its ``__context__`` holds the
SDK's error (both are ``None`` unless the caller is itself handling an exception).
A non-2xx body that the SDK cannot parse into its ``APIError`` (for example, one with
``code`` and ``message`` only) raises the SDK's own ``KeyError`` before a
``StreamApiException`` exists; that ``KeyError`` propagates unmapped, as an undecodable 2xx
body's does (DM-16 4.1), and delivery keeps it as a retryable ``provider_unavailable``.

**Codes from status and number** (4.5). Each mapping is decided by the HTTP status and
Stream's numeric ``code``: a transport error, a timeout, a 5xx, a 429 or a success that
could not be read is ``provider_unavailable``; 404 with code 16 is the operation's missing
object (``channel_unavailable`` for a channel, ``member_unavailable`` for a user); every
other 4xx is ``provider_rejected``. Where one number covers several causes (a 400 with
code 4 on a send) the message's text is tested in memory only, never stored, returned or
logged; ``StreamProviderError`` carries the two numbers beside the Glow code, nothing else.

**The text read** (P06.2 Stage C1; the brief's "Stage C under OD-45", point b; DM-22
2.1). ``read_message_texts`` makes one ``get_many_messages`` call (``GET
/api/v2/chat/channels/glow-match/{id}/messages`` with the asked IDs), never with
``member_custom_include``. From the answer it reads each message's ID and text, and its
``type`` and deleted markers (``deleted_at``, ``deleted_for_me``) only to leave it out:
a message whose type is not ``regular``, or that carries a deleted marker, is not
returned, so the history read shows it as unavailable whatever its text. Every other
field (the user, the member, custom data, reactions, attachments, timestamps) is dropped,
and so is every message Glow did not ask for; an ID answered twice is not trusted and left
out. Its errors map as every operation's: 404 with code 16 is ``channel_unavailable``, and a
success without its list of messages is ``provider_unavailable``.

**The signer** (design point e; DM-16 3.1 to 3.3). ``getstream`` 6.1.0's ``create_token``
sets ``iat`` to its own clock minus 5 s and ``exp`` to its own clock plus a lifetime, with
no parameter for either, so the pre-approved fallback signs the token here: HS256 with the
injected client's own secret, read at signing time and never kept; the claims are exactly
``user_id``, ``iat`` (the grant's ``issued_at`` truncated to the second, less
``IAT_BACKDATE_SECONDS``, which is 0) and ``exp`` (the grant's ``expires_at`` truncated to
the second, never later; the SDK's clock plays no part).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import httpx
import jwt
from getstream.exceptions import StreamApiException, StreamTransportException
from getstream.models import (
    ChannelInput,
    ChannelMemberRequest,
    MessageRequest,
    QueryUsersPayload,
    UpdateUserPartialRequest,
    UserRequest,
)

from .chat_provider import (
    CHANNEL_UNAVAILABLE,
    MEMBER_UNAVAILABLE,
    PROVIDER_REJECTED,
    PROVIDER_UNAVAILABLE,
    ChatErrorCode,
    ChatProviderError,
    ProviderReceipt,
    text_read_ids,
)
from .chat_tokens import TokenGrant

PROVIDER_NAME = "stream"
CHANNEL_TYPE = "glow-match"
# The fixed number of whole seconds taken off the truncated issue time (DM-16 3.1). It is
# 0 unless Stream refuses a token whose ``iat`` is the current second; never more than 5.
IAT_BACKDATE_SECONDS = 0
# Stream's "object does not exist" answer.
_NOT_FOUND = (404, 16)
# Stream's input error, which covers several causes on a send (4.5).
_INPUT_ERROR = (400, 4)
# Tested in memory on Stream's message, never stored, returned or logged.
_ALREADY_EXISTS = re.compile(r"already exists", re.IGNORECASE)
_USER_MISSING = re.compile(
    r"\buser\b.*\b(not exist|does not exist|do not exist|not found|deactivated)\b"
    r"|\b(not exist|not found|deactivated)\b.*\buser\b",
    re.IGNORECASE,
)


class StreamProviderError(ChatProviderError):
    """A Glow code, with the HTTP status and Stream's numeric code that decided it (two
    numbers; never Stream's text). ``None`` for a transport error or a timeout."""

    def __init__(
        self, code: ChatErrorCode, *, status: int | None = None, number: int | None = None
    ) -> None:
        super().__init__(code)
        self.status = status
        self.number = number


def _mapped(error: BaseException, *, missing: ChatErrorCode) -> StreamProviderError:
    """The Glow code for one of the SDK's own errors (4.5). ``missing`` is the code for the
    operation's object when Stream does not have it (404 with code 16)."""
    if isinstance(error, (StreamTransportException, httpx.TransportError)):
        return StreamProviderError(PROVIDER_UNAVAILABLE)
    if not isinstance(error, StreamApiException):
        raise TypeError("not one of the SDK's own errors")
    status = error.status_code if isinstance(error.status_code, int) else None
    number = error.code if isinstance(error.code, int) else None
    if status is None or status < 400 or status >= 500 or status == 429:
        return StreamProviderError(PROVIDER_UNAVAILABLE, status=status, number=number)
    if (status, number) == _NOT_FOUND:
        return StreamProviderError(missing, status=status, number=number)
    return StreamProviderError(PROVIDER_REJECTED, status=status, number=number)


def _guarded[T](call: Callable[[], T], *, missing: ChatErrorCode) -> T:
    """Run one SDK call, mapping only the SDK's own errors (4.1); the Glow error is raised
    after the ``except`` block, so neither its ``__cause__`` nor its ``__context__`` holds
    the SDK's error, and no provider text travels with the Glow code."""
    try:
        return call()
    except (StreamApiException, StreamTransportException, httpx.TransportError) as error:
        refused = _mapped(error, missing=missing)
    raise refused


def _cutoff_text(cutoff: datetime) -> str:
    """The cut-off as Stream takes it (RFC 3339, UTC), exactly as given: whole seconds when
    the caller sent whole seconds, the microseconds kept otherwise (3.4)."""
    if cutoff.tzinfo is None:
        raise ValueError("an aware cut-off is required")
    utc = cutoff.astimezone(UTC)
    fraction = f".{utc.microsecond:06d}" if utc.microsecond else ""
    return utc.strftime("%Y-%m-%dT%H:%M:%S") + fraction + "Z"


class StreamChatProvider:
    """The chat provider port on Stream Chat, through one injected ``getstream`` client."""

    name = PROVIDER_NAME

    def __init__(self, client: Any) -> None:
        self._client = client

    # -- reads -------------------------------------------------------------------------

    def _users(self, user_ids: tuple[str, ...]) -> dict[str, Any]:
        """The users Stream holds among ``user_ids``, deactivated ones included."""
        payload = QueryUsersPayload(
            filter_conditions={"id": {"$in": list(user_ids)}},
            include_deactivated_users=True,
            limit=len(user_ids),
        )
        response = _guarded(lambda: self._client.query_users(payload), missing=MEMBER_UNAVAILABLE)
        found: dict[str, Any] = {}
        for user in response.data.users or []:
            if user.id in user_ids:
                found[user.id] = user
        return found

    def _channel(self, channel_id: str) -> Any | None:
        """The channel's state (its members among it), or ``None`` when Stream has none."""
        cid = f"{CHANNEL_TYPE}:{channel_id}"
        response = _guarded(
            lambda: self._client.chat.query_channels(
                filter_conditions={"cid": cid}, limit=1, member_limit=10
            ),
            missing=CHANNEL_UNAVAILABLE,
        )
        for entry in response.data.channels or []:
            if entry.channel is not None and entry.channel.cid == cid:
                return entry
        return None

    # -- the port ------------------------------------------------------------------------

    def provision_user(self, user_id: str) -> ProviderReceipt:
        if user_id in self._users((user_id,)):
            return ProviderReceipt(user_id, already=True)
        response = _guarded(
            lambda: self._client.update_users({user_id: UserRequest(id=user_id)}),
            missing=MEMBER_UNAVAILABLE,
        )
        if user_id not in (response.data.users or {}):
            # Stream answered without the user: nothing to trust; a retry reads first.
            raise StreamProviderError(PROVIDER_UNAVAILABLE, status=response.status_code())
        return ProviderReceipt(user_id)

    def create_channel(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        if len(set(members)) != 2:
            raise StreamProviderError(PROVIDER_REJECTED)
        held = self._users(members)
        for member in members:
            user = held.get(member)
            if user is None or user.deactivated_at is not None:
                raise StreamProviderError(MEMBER_UNAVAILABLE)
        if self._channel(channel_id) is not None:
            # Never the members again to a channel Stream already has (4.4).
            return ProviderReceipt(channel_id, already=True)
        data = ChannelInput(
            created_by_id=members[0],
            members=[ChannelMemberRequest(user_id=member) for member in members],
        )
        response = _guarded(
            lambda: self._client.chat.get_or_create_channel(
                type=CHANNEL_TYPE, id=channel_id, data=data
            ),
            missing=CHANNEL_UNAVAILABLE,
        )
        channel = response.data.channel
        if channel is None or channel.cid != f"{CHANNEL_TYPE}:{channel_id}":
            raise StreamProviderError(PROVIDER_UNAVAILABLE, status=response.status_code())
        return ProviderReceipt(channel_id)

    def send_message(
        self, channel_id: str, sender: str, message_id: str, text: str
    ) -> ProviderReceipt:
        message = MessageRequest(id=message_id, text=text, user_id=sender)
        try:
            response = self._client.chat.send_message(
                type=CHANNEL_TYPE, id=channel_id, message=message
            )
        except (StreamApiException, StreamTransportException, httpx.TransportError) as error:
            if _reports_existing(error):
                # Stream reports the committed ID exists: a repeat (design point d).
                return ProviderReceipt(message_id, already=True)
            refused = _send_error(error)
        else:
            if response.data.message is None or response.data.message.id != message_id:
                raise StreamProviderError(PROVIDER_REJECTED, status=response.status_code())
            return ProviderReceipt(message_id)
        # After the block, as in _guarded: no SDK error in __cause__ or __context__.
        raise refused

    def remove_members(self, channel_id: str, members: tuple[str, str]) -> ProviderReceipt:
        state = self._channel(channel_id)
        if state is None:
            raise StreamProviderError(CHANNEL_UNAVAILABLE)
        present = {member.user_id for member in state.members or []} & set(members)
        if not present:
            return ProviderReceipt(channel_id, already=True)
        _guarded(
            lambda: self._client.chat.update_channel(
                type=CHANNEL_TYPE, id=channel_id, remove_members=list(members)
            ),
            missing=CHANNEL_UNAVAILABLE,
        )
        return ProviderReceipt(channel_id)

    def deactivate_user(self, user_id: str) -> ProviderReceipt:
        user = self._users((user_id,)).get(user_id)
        if user is None:
            raise StreamProviderError(MEMBER_UNAVAILABLE)
        if user.deactivated_at is not None:
            return ProviderReceipt(user_id, already=True)
        _guarded(lambda: self._client.deactivate_user(user_id=user_id), missing=MEMBER_UNAVAILABLE)
        return ProviderReceipt(user_id)

    def revoke_user_tokens(self, user_id: str, issued_before: datetime) -> ProviderReceipt:
        text = _cutoff_text(issued_before)
        user = self._users((user_id,)).get(user_id)
        if user is None:
            raise StreamProviderError(MEMBER_UNAVAILABLE)
        held = user.revoke_tokens_issued_before
        if isinstance(held, datetime) and held >= issued_before:
            # Never lower a cut-off Stream already holds (4.4).
            return ProviderReceipt(user_id, already=True)
        update = UpdateUserPartialRequest(id=user_id, set={"revoke_tokens_issued_before": text})
        _guarded(lambda: self._client.update_users_partial([update]), missing=MEMBER_UNAVAILABLE)
        return ProviderReceipt(user_id)

    def read_message_texts(self, channel_id: str, message_ids: tuple[str, ...]) -> dict[str, str]:
        asked = text_read_ids(message_ids)
        response = _guarded(
            lambda: self._client.chat.get_many_messages(
                type=CHANNEL_TYPE, id=channel_id, ids=list(asked)
            ),
            missing=CHANNEL_UNAVAILABLE,
        )
        messages = response.data.messages
        if not isinstance(messages, list):
            # A success without its list of messages could not be read: an outage, never an
            # answer without every message (DM-22 2.4).
            raise StreamProviderError(PROVIDER_UNAVAILABLE, status=response.status_code())
        wanted = set(asked)
        answered: set[str] = set()
        texts: dict[str, str] = {}
        for message in messages:
            message_id = message.id
            if message_id not in wanted:
                continue  # never a message Glow did not ask for
            if message_id in answered:
                texts.pop(message_id, None)  # one ID answered twice: neither is trusted
                continue
            answered.add(message_id)
            if _shows_text(message):
                texts[message_id] = message.text
        return texts


def _shows_text(message: Any) -> bool:
    """Whether a returned message's text may reach the history read (DM-22 2.1): a
    ``regular`` message with no deleted marker and a text. Nothing else of it is read."""
    return (
        message.type == "regular"
        and message.deleted_at is None
        and not message.deleted_for_me
        and isinstance(message.text, str)
    )


def _numbers(error: StreamApiException) -> tuple[int | None, int | None, str]:
    status = error.status_code if isinstance(error.status_code, int) else None
    number = error.code if isinstance(error.code, int) else None
    message = error.message if isinstance(error.message, str) else ""
    return status, number, message


def _reports_existing(error: BaseException) -> bool:
    """Whether a send's error is Stream reporting that the message's ID exists: an input
    error (400, code 4) whose text says so; the text is tested here and nowhere kept."""
    if not isinstance(error, StreamApiException):
        return False
    status, number, message = _numbers(error)
    return (status, number) == _INPUT_ERROR and bool(_ALREADY_EXISTS.search(message))


def _send_error(error: BaseException) -> StreamProviderError:
    """A send's error (4.5): an input error or a 404 naming the user as absent or
    deactivated is the member; a 404 otherwise is the channel; the rest as every call."""
    if isinstance(error, StreamApiException):
        status, number, message = _numbers(error)
        about_user = (status, number) in (_INPUT_ERROR, _NOT_FOUND)
        if about_user and _USER_MISSING.search(message):
            return StreamProviderError(MEMBER_UNAVAILABLE, status=status, number=number)
    return _mapped(error, missing=CHANNEL_UNAVAILABLE)


# -- the signer --------------------------------------------------------------------------


def _whole_second(moment: datetime) -> int:
    """The moment truncated to the whole second, as a Unix time; aware times only."""
    if moment.tzinfo is None:
        raise ValueError("an aware time is required")
    return int(moment.replace(microsecond=0).timestamp())


def token_claims(grant: TokenGrant) -> dict[str, Any]:
    """Exactly ``user_id``, ``iat`` and ``exp``, from the grant (DM-16 3.1, 3.2, 3.3)."""
    return {
        "user_id": grant.user_ref,
        "iat": _whole_second(grant.issued_at) - IAT_BACKDATE_SECONDS,
        "exp": _whole_second(grant.expires_at),
    }


def sign_chat_token(grant: TokenGrant, client: Any) -> str:
    """The client's token for a grant, signed HS256 with the injected client's own secret,
    read here and kept nowhere (DM-16 3.3)."""
    token = jwt.encode(token_claims(grant), client.api_secret, algorithm="HS256")
    if not isinstance(token, str):
        raise TypeError("the JWT library returned a non-string token")
    return token
