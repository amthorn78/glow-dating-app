"""Chat's routes (the SV4 brief's D8; F11), sealed until integration: no runtime URL configuration
names them, and only the disposable-database proof's chat settings serve them.

Each takes its actor from SV1's ``GlowActorAuthentication`` only (an ``active`` account with a
``valid``, unexpired session at the current epoch; ``unauthenticated``, 401, otherwise), never from
the body or another header, and passes the actor's session to ``glow_chat``, whose session, never a
field of the request, names the actor:

- ``POST api/v1/chat/messages``: ``MessageIntent``, answering ``MessageSubmission``, through
  ``glow_chat``'s ``send`` unchanged, with ``meta.expected_version`` as the send's contact version
  (D6: a match's version, which ``MatchProjection`` serves). Every refusal from either member's
  state or from the end of contact answers one code (``glow_chat.contract.send_error``);
- ``GET api/v1/chat/conversations``: ``ConversationList``, through ``list_conversations`` under
  D5, bounded before it locks (``glow_chat.route_reads``), each conversation ``open`` or
  ``read_only`` (D9);
- ``POST api/v1/chat/history``: ``MessagePageRequest``, answering ``MessagePage``, through
  ``read_history`` under D5 (a body, as SV3's page route takes ``PageRequest``);
- ``POST api/v1/chat/read-cursor``: ``ReadCursorIntent``, answering ``ConversationSummary``,
  through ``move_read_cursor``.

On each ``POST`` route, a body that is not its DTO, any query string or another content type is
``invalid_request`` (400); the ``GET`` route refuses a query string and a body (400); on every
route another method is ``invalid_request`` (405), as SV2's and SV3's routes answer. Every
refusal is the contract's ``Error``, which names a code and never a value; a refusal is logged by
its internal code only, and no text, value or identifier is logged. Nothing is cached
(``Cache-Control: no-store``). There is no ``ChannelIntent`` route (OD-45).

**The provider** (D8). The history read needs a text reader. The reads' views take it from a
factory named by the setting ``GLOW_CHAT_TEXT_READER`` (a dotted path to a callable that returns
one), which only the proof's chat settings name, with the in-memory fixture; the served runtime
names none. Without it, each read's view refuses to run (``provider_unavailable``, 503) before any
read. The send needs none: it calls no provider.

**Transactions** (D8; the P11 plan's R4). The reads refuse any transaction their caller holds, so
every view here is ``non_atomic_requests``: ``ATOMIC_REQUESTS`` never wraps it, and each read and
the send is the whole of its own transaction. Its tests are ``TransactionTestCase``s.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any
from uuid import UUID

from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.db import transaction
from django.utils.cache import add_never_cache_headers
from django.utils.module_loading import import_string
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from glow_chat import contract
from glow_chat.contact import OrmContactPersistence
from glow_chat.route_reads import RouteConversationReads, is_read_only, marked
from glow_domain import chat_projections as projections
from glow_domain.chat import SendCommand
from glow_domain.chat_reads import CursorError, TextReader
from glow_identity.authentication import Actor, GlowActorAuthentication
from glow_persistence.models import MessageSubmission
from glow_profiles.contract import Invalid, app_response, error, new_request_id
from glow_profiles.tx import INVALID_REQUEST, PROVIDER_UNAVAILABLE, STATUS, UNAUTHENTICATED

logger = logging.getLogger("glow_chat.views")

# D8: the setting naming the history read's text reader; only the proof's chat settings set it.
TEXT_READER_SETTING = "GLOW_CHAT_TEXT_READER"
NO_TEXT_READER = "no_text_reader"
STALE_VERSION = "stale_version"


class _BadRequest(Exception):
    """The request is not the route's DTO, or carries a query string; nothing is echoed."""


class _Refusal(Exception):
    """A refusal before any read or write: a contract code and an internal reason."""

    def __init__(self, code: str, reason: str, *, retryable: bool = False) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason
        self.retryable = retryable


def _no_store(response: Response) -> Response:
    add_never_cache_headers(response)
    response["Cache-Control"] = "no-store"
    return response


def text_reader() -> TextReader:
    """D8: the text reader the setting's factory returns; a refusal when no factory is named."""
    factory_path = getattr(settings, TEXT_READER_SETTING, None)
    if not isinstance(factory_path, str) or not factory_path:
        raise _Refusal(PROVIDER_UNAVAILABLE, NO_TEXT_READER)
    factory: Callable[[], TextReader] = import_string(factory_path)
    return factory()


def reads() -> RouteConversationReads:
    return RouteConversationReads(text_reader())


class _ChatRoute(APIView):  # type: ignore[misc]
    authentication_classes = [GlowActorAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    @classmethod
    def as_view(cls, **initkwargs: Any) -> Any:
        # D8: never inside ATOMIC_REQUESTS' transaction; each read and the send is its own.
        return transaction.non_atomic_requests(super().as_view(**initkwargs))

    @staticmethod
    def _actor(request: Any) -> Actor:
        actor = request.auth
        if not isinstance(actor, Actor):
            raise NotAuthenticated()
        if request.META.get("QUERY_STRING"):
            raise _BadRequest()
        return actor

    @staticmethod
    def _body(request: Any, definition: str) -> dict[str, Any]:
        content_type = request.META.get("CONTENT_TYPE", "")
        if content_type.split(";")[0].strip() != "application/json":
            raise _BadRequest()
        try:
            return contract.parse(definition, request._request.body)
        except (Invalid, RequestDataTooBig):
            raise _BadRequest() from None

    @staticmethod
    def _no_body(request: Any) -> None:
        try:
            sent = request._request.body
        except RequestDataTooBig:
            raise _BadRequest() from None
        if sent:
            raise _BadRequest()

    @staticmethod
    def _served(data: dict[str, Any]) -> Response:
        return _no_store(Response(app_response(data, new_request_id())))

    @staticmethod
    def _refused(code: str, reason: str, *, retryable: bool = False) -> Response:
        logger.info("chat route refused: %s", reason)
        return _no_store(
            Response(
                error(code, new_request_id(), retryable=retryable),
                status=STATUS.get(code, 503),
            )
        )

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated | AuthenticationFailed):
            response = Response(error(UNAUTHENTICATED, new_request_id()), status=401)
            response["WWW-Authenticate"] = "Bearer"
            return _no_store(response)
        if isinstance(exc, MethodNotAllowed):
            return _no_store(Response(error(INVALID_REQUEST, new_request_id()), status=405))
        if isinstance(exc, _BadRequest):
            return self._refused(INVALID_REQUEST, INVALID_REQUEST)
        if isinstance(exc, _Refusal):
            return self._refused(exc.code, exc.reason, retryable=exc.retryable)
        return super().handle_exception(exc)


class MessageView(_ChatRoute):
    """F11's send: ``MessageIntent``, answering ``MessageSubmission`` (D8, D6)."""

    def post(self, request: Any) -> Response:
        actor = self._actor(request)
        intent = self._body(request, "MessageIntent")
        meta = intent["meta"]
        command = SendCommand(
            session_id=actor.session_id,
            match_id=UUID(intent["match_id"]),
            contact_version=int(meta["expected_version"]),
            idempotency_key=str(meta["idempotency_key"]),
            text=intent["text"],
        )
        persistence = OrmContactPersistence(provider=settings.GLOW_IDENTITY_CHAT_PROVIDER)
        result = persistence.send(command)
        if result.outcome in ("authorized", "replayed") and result.receipt is not None:
            row = (
                MessageSubmission.objects.filter(pk=result.receipt.submission_id)
                .values_list("version", "state")
                .first()
            )
            if row is None:
                code, retryable = contract.send_error("refused", "submission_missing")
                return self._refused(code, "submission_missing", retryable=retryable)
            version, state = row
            return self._served(
                contract.message_submission(str(result.receipt.submission_id), version, state)
            )
        code, retryable = contract.send_error(result.outcome, result.reason)
        return self._refused(code, result.reason, retryable=retryable)


class ConversationListView(_ChatRoute):
    """F11's conversation list (D5, D8, D9)."""

    http_method_names = ["get"]

    def get(self, request: Any) -> Response:
        actor = self._actor(request)
        self._no_body(request)
        result = reads().list_conversations(actor.session_id)
        if result.outcome != "listed":
            code, retryable = contract.read_error(result.outcome, result.reason)
            return self._refused(code, result.reason, retryable=retryable)
        return self._served(contract.conversation_list(marked(result.conversations)))


class HistoryView(_ChatRoute):
    """F11's history page: ``MessagePageRequest``, answering ``MessagePage`` (D5, D8)."""

    def post(self, request: Any) -> Response:
        actor = self._actor(request)
        dto = self._body(request, "MessagePageRequest")
        reader = reads()
        try:
            page_request = projections.page_request(dto, actor.session_id)
        except CursorError:
            return self._refused(STALE_VERSION, "cursor_unreadable")
        result = reader.read_history(page_request)
        if result.outcome != "read" or result.page is None:
            code, retryable = contract.read_error(result.outcome, result.reason)
            return self._refused(code, result.reason, retryable=retryable)
        return self._served(projections.message_page(result.page))


class ReadCursorView(_ChatRoute):
    """F11's read cursor: ``ReadCursorIntent``, answering ``ConversationSummary`` (D5, D9)."""

    def post(self, request: Any) -> Response:
        actor = self._actor(request)
        dto = self._body(request, "ReadCursorIntent")
        reader = reads()
        result = reader.move_read_cursor(projections.read_cursor_command(dto, actor.session_id))
        if result.outcome not in ("moved", "no_change") or result.entry is None:
            code, retryable = contract.read_error(result.outcome, result.reason)
            return self._refused(code, result.reason, retryable=retryable)
        return self._served(
            contract.conversation_summary(result.entry, read_only=is_read_only(result.entry))
        )
