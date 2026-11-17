"""The member's action routes (the SV3 brief's D9 to D13, for Stage B's parts; F08 to F10, F13),
sealed until P11, beside Stage A's page route (``views``), which they leave unchanged.

Each takes its actor from SV1's ``GlowActorAuthentication`` only (an ``active`` account with a
``valid``, unexpired session at the current epoch; ``unauthenticated``, 401, otherwise), never from
the body or another header:

- ``POST api/v1/discovery/interaction``: ``InteractionIntent``, answering ``InteractionOutcome``
  (F08's like and pass; F09's match on reciprocal likes, D9 and D10);
- ``POST api/v1/discovery/interaction/undo``: D13's ``InteractionUndoIntent``, answering D13's
  ``InteractionUndoOutcome`` (D12's undo);
- ``POST api/v1/matches/unmatch``: ``UnmatchIntent``, answering ``MatchProjection`` (F10; D11);
- ``POST api/v1/blocks``: ``BlockIntent``, answering ``BlockOutcome`` (F13; D11);
- ``GET api/v1/matches/<match_id>``: ``MatchProjection``, for a participant (F09);
- ``GET api/v1/interactions/<profile_id>``: D13's ``OwnInteractionVersions``, the actor's own
  directional row and own block toward that profile, each state and version (F08, F13; DM-74;
  correction B-C1): the same 200 answer, ``none`` and ``0``, wherever the actor has no row, whether
  the profile exists or not and whatever its state, never ``not_found`` for a profile, and never
  the other member's rows. A body is ``invalid_request``, as a query string is.

On each ``POST`` route, a body that is not its DTO, any query string or another content type is
``invalid_request`` (400), and on every route another method is ``invalid_request`` (405), as
SV2's and Stage A's routes answer. The two ``GET`` routes refuse a query string (400) and read no
content type; ``GET api/v1/interactions/<profile_id>`` refuses a body (400), and
``GET api/v1/matches/<match_id>`` reads none. Another
member's match is ``not_found``. A stale or consumed batch, a target outside it, an ineligible
target or a consumed candidate is the generic stale response (``stale_version``, 409), the same
whatever the cause (D8), and an expected version that is not the object's is ``stale_version``
too. Every refusal is the contract's ``Error``, which names a code and never a value; a refusal is
logged by its internal code only. Nothing is cached (``Cache-Control: no-store``). No route takes a
match intent: a match is made only by reciprocal likes (F09).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any
from uuid import UUID

from django.core.exceptions import RequestDataTooBig
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from glow_discovery import contract, interactions
from glow_discovery.views import _BadRequest, _no_store
from glow_identity.authentication import Actor, GlowActorAuthentication
from glow_profiles.contract import Invalid, app_response, error, new_request_id
from glow_profiles.tx import (
    INVALID_REQUEST,
    PROVIDER_UNAVAILABLE,
    STATUS,
    UNAUTHENTICATED,
    Result,
)

logger = logging.getLogger("glow_discovery.interaction_views")

Command = Callable[..., Result]


class _Route(APIView):  # type: ignore[misc]
    authentication_classes = [GlowActorAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]
    definition: str | None = None
    command: Command | None = None

    @staticmethod
    def _actor(request: Any) -> Actor:
        actor = request.auth
        if not isinstance(actor, Actor):
            raise NotAuthenticated()
        if request.META.get("QUERY_STRING"):
            raise _BadRequest()
        return actor

    @staticmethod
    def _answer(result: Result) -> Response:
        request_id = new_request_id()
        if result.ok and result.data is not None:
            return _no_store(Response(app_response(result.data, request_id)))
        code = result.code or PROVIDER_UNAVAILABLE
        logger.info("interaction route refused: %s", result.reason)
        return _no_store(
            Response(
                error(code, request_id, retryable=code == PROVIDER_UNAVAILABLE),
                status=STATUS.get(code, 503),
            )
        )

    def post(self, request: Any) -> Response:
        actor = self._actor(request)
        content_type = request.META.get("CONTENT_TYPE", "")
        if content_type.split(";")[0].strip() != "application/json":
            raise _BadRequest()
        assert self.definition is not None
        try:
            intent = contract.parse(self.definition, request._request.body)
        except (Invalid, RequestDataTooBig):
            raise _BadRequest() from None
        command = type(self).command
        assert command is not None
        return self._answer(command(actor.account_id, intent))

    def handle_exception(self, exc: Exception) -> Response:
        request_id = new_request_id()
        if isinstance(exc, NotAuthenticated | AuthenticationFailed):
            response = Response(error(UNAUTHENTICATED, request_id), status=401)
            response["WWW-Authenticate"] = "Bearer"
            return _no_store(response)
        if isinstance(exc, MethodNotAllowed):
            return _no_store(Response(error(INVALID_REQUEST, request_id), status=405))
        if isinstance(exc, _BadRequest):
            logger.info("interaction route refused: %s", INVALID_REQUEST)
            return _no_store(Response(error(INVALID_REQUEST, request_id), status=400))
        return super().handle_exception(exc)


def _command(function: Callable[..., Result]) -> Command:
    def call(account_id: UUID, intent: dict[str, Any]) -> Result:
        return function(account_id, intent)

    return call


class InteractionView(_Route):
    """F08's like and pass, and F09's match on reciprocal likes (D9, D10)."""

    definition = "InteractionIntent"
    command = staticmethod(_command(interactions.interact))


class UndoView(_Route):
    """D12's undo of the actor's most recent pass (D13's ``InteractionUndoIntent``)."""

    definition = "InteractionUndoIntent"
    command = staticmethod(_command(interactions.undo))


class UnmatchView(_Route):
    """F10's unmatch (D11)."""

    definition = "UnmatchIntent"
    command = staticmethod(_command(interactions.unmatch))


class BlockView(_Route):
    """F13's block and unblock (D11)."""

    definition = "BlockIntent"
    command = staticmethod(_command(interactions.block))


class MatchView(_Route):
    """F09's ``MatchProjection`` by its ID, for a participant only (``not_found`` otherwise)."""

    http_method_names = ["get"]

    def get(self, request: Any, match_id: UUID) -> Response:
        actor = self._actor(request)
        return self._answer(interactions.read_match(actor.account_id, match_id))


class OwnVersionsView(_Route):
    """The actor's own versions toward a profile (D13; DM-74; correction B-C1), for the actor
    only: the same answer whatever the profile's state, never ``not_found`` for a profile."""

    http_method_names = ["get"]

    def get(self, request: Any, profile_id: UUID) -> Response:
        actor = self._actor(request)
        try:
            sent = request._request.body
        except RequestDataTooBig:
            raise _BadRequest() from None
        if sent:
            raise _BadRequest()
        return self._answer(interactions.read_own_versions(actor.account_id, profile_id))
