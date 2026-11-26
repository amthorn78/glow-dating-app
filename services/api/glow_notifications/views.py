"""F12's routes (the SV4 brief's D19, with DM-101's AM6 and AM7), sealed until integration: no
runtime URL configuration names them, and only the disposable-database proof's chat settings serve
them.

Each takes its actor from SV1's ``GlowActorAuthentication`` only (an ``active`` account with a
``valid``, unexpired session at the current epoch; ``unauthenticated``, 401, otherwise), never from
the body or another header, and the requesting installation from the ``Glow-Installation-Id``
header only (a lower-case UUID), never from an intent's fields:

- ``GET api/v1/notifications``: the requesting installation's ``NotificationSettings``;
  ``not_found`` for an installation with no registration for the account;
- ``POST api/v1/notifications/device``: a ``DeviceIntent`` (``register``, which is F12's rotate for
  an installation already active for the account, or ``revoke``), whose ``device_id`` must be the
  header's installation (``forbidden`` otherwise), answering ``NotificationSettings``;
- ``POST api/v1/notifications/settings``: a ``NotificationIntent``, answering
  ``NotificationSettings``.

A missing or malformed header, a body that is not a JSON object, an intent that is not its DTO, any
query string or another content type is ``invalid_request`` (400); the ``GET`` route refuses a body
(400); another method is ``invalid_request`` (405). Every refusal is the contract's ``Error``,
which names a code and never a value (``glow_notifications.contract.REFUSALS``), and each 401, at
the door or inside the locks, carries ``WWW-Authenticate: Bearer`` (AM6). A refusal is logged by its
internal reason code only: no token, reference, installation identifier or other value is logged
or served (AM7). Nothing is cached (``Cache-Control: no-store``).

**The token store** (D16; AM1): the device route takes it from the factory the setting
``GLOW_NOTIFICATIONS_TOKEN_STORE`` names (``glow_notifications.providers``), which only the
proof's chat settings name, with the in-memory fixture; without one the device command refuses
before any read or write (``provider_unavailable``). The read and the settings command need none.

**Transactions**: each command and read is the whole of its own transaction and refuses one its
caller holds, so every view here is ``non_atomic_requests``: ``ATOMIC_REQUESTS`` never wraps it.
No Django ``TestCase`` tests them: their database tests are the chat suite's cases
(``proofs/postgres-ordering``), through Django's test client with no enclosing transaction.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import RequestDataTooBig
from django.db import transaction
from django.utils.cache import add_never_cache_headers
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed, NotAuthenticated
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from glow_domain import notifications as n
from glow_identity.authentication import Actor, GlowActorAuthentication
from glow_notifications import contract, providers
from glow_notifications.persistence import OrmNotificationPersistence
from glow_profiles.contract import Invalid, app_response, error, new_request_id
from glow_profiles.tx import STATUS

logger = logging.getLogger("glow_notifications.views")


class _BadRequest(Exception):
    """The request is not the route's DTO, or carries a query string; nothing is echoed."""


def _no_store(response: Response) -> Response:
    add_never_cache_headers(response)
    response["Cache-Control"] = "no-store"
    return response


class JsonOnlyNegotiation(DefaultContentNegotiation):  # type: ignore[misc]
    """The JSON renderer, always (as chat's routes negotiate since A2-C1; DM-99 item 2): neither
    ``Accept`` nor the ``format`` override is read, so ``?format=xml`` meets the routes' own
    query-string refusal and ``Accept: text/html`` is answered as any other request."""

    def select_renderer(
        self, request: Any, renderers: list[Any], format_suffix: str | None = None
    ) -> tuple[Any, str]:
        renderer = next(r for r in renderers if isinstance(r, JSONRenderer))
        return renderer, renderer.media_type


class _NotificationRoute(APIView):  # type: ignore[misc]
    authentication_classes = [GlowActorAuthentication]
    permission_classes = [IsAuthenticated]
    content_negotiation_class = JsonOnlyNegotiation
    renderer_classes = [JSONRenderer]
    http_method_names = ["post"]

    @classmethod
    def as_view(cls, **initkwargs: Any) -> Any:
        # Each command and read is its own transaction, never inside ATOMIC_REQUESTS' one.
        return transaction.non_atomic_requests(super().as_view(**initkwargs))

    @staticmethod
    def _caller(request: Any) -> n.Caller:
        """The actor's account and session (SV1), and the header's installation (D19)."""
        actor = request.auth
        if not isinstance(actor, Actor):
            raise NotAuthenticated()
        if request.META.get("QUERY_STRING"):
            raise _BadRequest()
        try:
            installation = n.parse_installation(request.META.get(contract.INSTALLATION_HEADER))
        except n.IntentError:
            raise _BadRequest() from None
        return n.Caller(actor.account_id, actor.session_id, installation)

    @staticmethod
    def _body(request: Any) -> dict[str, Any]:
        content_type = request.META.get("CONTENT_TYPE", "")
        if content_type.split(";")[0].strip() != "application/json":
            raise _BadRequest()
        try:
            return contract.parse(request._request.body)
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
    def _refused(code: str, reason: str, *, retryable: bool = False) -> Response:
        logger.info("notifications route refused: %s", reason)
        response = Response(
            error(code, new_request_id(), retryable=retryable), status=STATUS.get(code, 503)
        )
        if code == contract.UNAUTHENTICATED:
            # AM6: a 401 from inside the locks carries the challenge, as the door's does.
            response["WWW-Authenticate"] = "Bearer"
        return _no_store(response)

    def _answer(self, result: n.CommandResult | n.ReadResult) -> Response:
        served = result.outcome in ("applied", "replayed", "read")
        if served and result.settings is not None:
            body = app_response(contract.settings(result.settings), new_request_id())
            return _no_store(Response(body))
        code, retryable = contract.refusal(result.outcome, result.reason)
        return self._refused(code, result.reason or result.outcome, retryable=retryable)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated | AuthenticationFailed):
            response = Response(error(contract.UNAUTHENTICATED, new_request_id()), status=401)
            response["WWW-Authenticate"] = "Bearer"
            return _no_store(response)
        if isinstance(exc, MethodNotAllowed):
            return _no_store(
                Response(error(contract.INVALID_REQUEST, new_request_id()), status=405)
            )
        if isinstance(exc, _BadRequest):
            return self._refused(contract.INVALID_REQUEST, contract.INVALID_REQUEST)
        return super().handle_exception(exc)


class NotificationsView(_NotificationRoute):
    """F12's read: the requesting installation's ``NotificationSettings`` (D19)."""

    http_method_names = ["get"]

    def get(self, request: Any) -> Response:
        caller = self._caller(request)
        self._no_body(request)
        return self._answer(OrmNotificationPersistence().read(caller))


class DeviceView(_NotificationRoute):
    """F12's ``DeviceIntent``: register (or rotate) and revoke (D19)."""

    def post(self, request: Any) -> Response:
        caller = self._caller(request)
        intent = self._body(request)
        persistence = OrmNotificationPersistence(tokens=providers.token_store())
        return self._answer(persistence.device(caller, intent))


class SettingsView(_NotificationRoute):
    """F12's ``NotificationIntent``: the account's settings (D19)."""

    def post(self, request: Any) -> Response:
        caller = self._caller(request)
        intent = self._body(request)
        return self._answer(OrmNotificationPersistence().settings(caller, intent))
