"""SV1's one Glow route (the SV1 brief's Outcome 5): the member's own ``AccountAccess``.

Served only to an actor from ``GlowActorAuthentication``: an ``active`` account with a ``valid``
session (D7). Every refusal is the contract's ``Error``: ``unauthenticated`` with a 401 for a
missing or refused token, ``invalid_request`` for another method. Nothing is cached.
"""

from __future__ import annotations

from typing import Any

from django.utils.cache import add_never_cache_headers
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from glow_identity import access
from glow_identity.authentication import Actor, GlowActorAuthentication


class AccountAccessView(APIView):  # type: ignore[misc]
    authentication_classes = [GlowActorAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request: Any) -> Response:
        actor = request.auth
        if not isinstance(actor, Actor):
            raise NotAuthenticated()
        data = access.account_access(
            actor.account_id, actor.account_version, actor.account_state, actor.session_state
        )
        return self._no_store(Response(access.app_response(data, access.new_request_id())))

    def handle_exception(self, exc: Exception) -> Response:
        request_id = access.new_request_id()
        if isinstance(exc, NotAuthenticated | AuthenticationFailed):
            response = Response(access.error("unauthenticated", request_id), status=401)
            response["WWW-Authenticate"] = "Bearer"
            return self._no_store(response)
        if isinstance(exc, MethodNotAllowed):
            return self._no_store(Response(access.error("invalid_request", request_id), status=405))
        return super().handle_exception(exc)

    @staticmethod
    def _no_store(response: Response) -> Response:
        add_never_cache_headers(response)
        response["Cache-Control"] = "no-store"
        return response
