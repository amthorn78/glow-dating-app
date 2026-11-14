"""The member's page route (the SV3 brief's D13 for Stage A; F07), sealed until P11.

``POST api/v1/discovery/page`` takes a ``PageRequest`` body and answers a ``CandidateCardPage`` in
the ``AppResponse`` envelope. It takes its actor from SV1's ``GlowActorAuthentication`` only (an
``active`` account with a ``valid``, unexpired session at the current epoch; ``unauthenticated``,
401, otherwise), never from the body or another header, and pages only the actor's own batches:
another viewer's cursor or batch is the generic stale response (``stale_version``, 409), as are a
forged, expired or outdated one. A body that is not the DTO, any query string, another content type
or another method is ``invalid_request`` (400; 405 for the method, as SV2's routes answer). A viewer
who fails a predicate is ``forbidden`` (403). Every refusal is the contract's ``Error``, which names
a code and never a value, and no log line carries a value: a refusal is logged by its internal code.
Nothing is cached (``Cache-Control: no-store``). Stage A serves no action route.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import RequestDataTooBig
from django.utils.cache import add_never_cache_headers
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from glow_discovery import contract, pages
from glow_identity.authentication import Actor, GlowActorAuthentication
from glow_profiles.contract import Invalid, app_response, error, new_request_id
from glow_profiles.tx import INVALID_REQUEST, PROVIDER_UNAVAILABLE, STATUS, UNAUTHENTICATED

logger = logging.getLogger("glow_discovery.views")


class _BadRequest(Exception):
    """The request is not a ``PageRequest``, or carries a query string; nothing is echoed."""


def _no_store(response: Response) -> Response:
    add_never_cache_headers(response)
    response["Cache-Control"] = "no-store"
    return response


class PageView(APIView):  # type: ignore[misc]
    authentication_classes = [GlowActorAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def post(self, request: Any) -> Response:
        actor = request.auth
        if not isinstance(actor, Actor):
            raise NotAuthenticated()
        if request.META.get("QUERY_STRING"):
            raise _BadRequest()
        content_type = request.META.get("CONTENT_TYPE", "")
        if content_type.split(";")[0].strip() != "application/json":
            raise _BadRequest()
        try:
            intent = contract.parse_page_request(request._request.body)
        except (Invalid, RequestDataTooBig):
            raise _BadRequest() from None
        result = pages.page(actor.account_id, intent)
        request_id = new_request_id()
        if result.ok and result.data is not None:
            return _no_store(Response(app_response(result.data, request_id)))
        code = result.code or PROVIDER_UNAVAILABLE
        logger.info("discovery route refused: %s", result.reason)
        return _no_store(
            Response(
                error(code, request_id, retryable=code == PROVIDER_UNAVAILABLE),
                status=STATUS.get(code, 503),
            )
        )

    def handle_exception(self, exc: Exception) -> Response:
        request_id = new_request_id()
        if isinstance(exc, NotAuthenticated | AuthenticationFailed):
            response = Response(error(UNAUTHENTICATED, request_id), status=401)
            response["WWW-Authenticate"] = "Bearer"
            return _no_store(response)
        if isinstance(exc, MethodNotAllowed):
            return _no_store(Response(error(INVALID_REQUEST, request_id), status=405))
        if isinstance(exc, _BadRequest):
            logger.info("discovery route refused: %s", INVALID_REQUEST)
            return _no_store(Response(error(INVALID_REQUEST, request_id), status=400))
        return super().handle_exception(exc)
