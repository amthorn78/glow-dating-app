"""The member's routes (the SV2 brief's D11 and D17), sealed until P11.

Every route takes its actor from SV1's ``GlowActorAuthentication`` only (an ``active`` account
with a ``valid``, unexpired session at the current epoch), never from the body or another header,
and reads or writes the actor's own objects only: an object ID that is not the actor's is
``not_found``. Every refusal is the contract's ``Error``: ``unauthenticated`` with a 401,
``invalid_request`` with a 400 for a body that is not its DTO, any query string, or another method
(405), and the operations' own codes. No error or log line carries a submitted value: a refusal
names a code, never a field's value. Nothing is cached (``Cache-Control: no-store``).

No route reaches a staff operation (``glow_profiles.staff``); P07's staff API exposes those.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any
from uuid import UUID

from django.core.exceptions import RequestDataTooBig
from django.utils.cache import add_never_cache_headers
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from glow_identity.authentication import Actor, GlowActorAuthentication
from glow_profiles import contract, media, operations
from glow_profiles.tx import INVALID_REQUEST, PROVIDER_UNAVAILABLE, STATUS, UNAUTHENTICATED, Result

logger = logging.getLogger("glow_profiles.views")

Command = Callable[..., Result]


class _BadRequest(Exception):
    """The request is not its route's DTO, or carries a query string; nothing is echoed."""


class _Route(APIView):  # type: ignore[misc]
    authentication_classes = [GlowActorAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]
    reads: str | None = None
    definition: str | None = None
    command: Command | None = None

    # -- plumbing -----------------------------------------------------------------------------

    @staticmethod
    def _actor(request: Any) -> Actor:
        actor = request.auth
        if not isinstance(actor, Actor):
            raise NotAuthenticated()
        return actor

    @staticmethod
    def _no_query(request: Any) -> None:
        # D5: nothing travels in a URL; no route takes a query string.
        if request.META.get("QUERY_STRING"):
            raise _BadRequest()

    def _body(self, request: Any) -> dict[str, Any]:
        content_type = request.META.get("CONTENT_TYPE", "")
        if content_type.split(";")[0].strip() != "application/json":
            raise _BadRequest()
        try:
            raw = request._request.body
        except RequestDataTooBig:
            raise _BadRequest() from None
        assert self.definition is not None
        try:
            return contract.parse(self.definition, raw)
        except contract.Invalid:
            raise _BadRequest() from None

    def _answer(self, result: Result) -> Response:
        request_id = contract.new_request_id()
        if result.ok and result.data is not None:
            return self._no_store(Response(contract.app_response(result.data, request_id)))
        code = result.code or PROVIDER_UNAVAILABLE
        logger.info("profile route refused: %s", result.reason)
        return self._no_store(
            Response(
                contract.error(code, request_id, retryable=code == PROVIDER_UNAVAILABLE),
                status=STATUS.get(code, 503),
            )
        )

    @staticmethod
    def _no_store(response: Response) -> Response:
        add_never_cache_headers(response)
        response["Cache-Control"] = "no-store"
        return response

    # -- handlers -----------------------------------------------------------------------------

    def get(self, request: Any, **kwargs: Any) -> Response:
        actor = self._actor(request)
        self._no_query(request)
        assert self.reads is not None
        object_id = next((value for value in kwargs.values() if isinstance(value, UUID)), None)
        return self._answer(operations.read(actor.account_id, self.reads, object_id))

    def post(self, request: Any) -> Response:
        actor = self._actor(request)
        self._no_query(request)
        intent = self._body(request)
        command = type(self).command
        assert command is not None
        return self._answer(command(actor.account_id, intent))

    def handle_exception(self, exc: Exception) -> Response:
        request_id = contract.new_request_id()
        if isinstance(exc, NotAuthenticated | AuthenticationFailed):
            response = Response(contract.error(UNAUTHENTICATED, request_id), status=401)
            response["WWW-Authenticate"] = "Bearer"
            return self._no_store(response)
        if isinstance(exc, MethodNotAllowed):
            return self._no_store(Response(contract.error(INVALID_REQUEST, request_id), status=405))
        if isinstance(exc, _BadRequest):
            logger.info("profile route refused: %s", INVALID_REQUEST)
            return self._no_store(Response(contract.error(INVALID_REQUEST, request_id), status=400))
        return super().handle_exception(exc)


def _command(function: Callable[..., Result]) -> Command:
    def call(account_id: UUID, intent: dict[str, Any]) -> Result:
        return function(account_id, intent)

    return call


class ProfileView(_Route):
    http_method_names = ["get", "post"]
    reads = "profile"
    definition = "ProfileIntent"
    command = staticmethod(_command(operations.save_profile))


class ProfileByIdView(_Route):
    reads = "profile"


class CompletionView(_Route):
    reads = "completion"


class VisibilityView(_Route):
    http_method_names = ["post"]
    definition = "VisibilityIntent"
    command = staticmethod(_command(operations.set_visibility))


class FieldsView(_Route):
    http_method_names = ["get", "post"]
    reads = "fields"
    definition = "ProfileFieldIntent"
    command = staticmethod(_command(operations.set_field))


class PreferencesView(_Route):
    http_method_names = ["get", "post"]
    reads = "preferences"
    definition = "PreferencesIntent"
    command = staticmethod(_command(operations.set_preferences))


class FiltersView(_Route):
    http_method_names = ["get", "post"]
    reads = "filters"
    definition = "FiltersIntent"
    command = staticmethod(_command(operations.set_filters))


class AreaView(_Route):
    http_method_names = ["get", "post"]
    reads = "area"
    definition = "AreaIntent"
    command = staticmethod(_command(operations.set_area))


class NearestAreaView(_Route):
    """D5: the phone-location query, POST with the coordinates in the body only."""

    http_method_names = ["post"]
    definition = "AreaQuery"
    command = staticmethod(_command(operations.nearest_area))


class CatalogView(_Route):
    reads = "catalog"


class ConsentView(_Route):
    http_method_names = ["get", "post"]
    reads = "consent"
    definition = "ConsentIntent"
    command = staticmethod(_command(operations.decide_onboarding_consent))


class SensitiveConsentView(_Route):
    http_method_names = ["get", "post"]
    reads = "sensitive_consent"
    definition = "SensitiveConsentIntent"
    command = staticmethod(_command(operations.decide_sensitive_consent))


class AdultCheckView(_Route):
    http_method_names = ["get", "post"]
    reads = "age_state"
    definition = "AdultCheckIntent"
    command = staticmethod(_command(operations.adult_check))


class BirthInputView(_Route):
    http_method_names = ["get", "post"]
    reads = "birth_input"
    definition = "BirthInputIntent"
    command = staticmethod(_command(operations.save_birth_input))


class BirthInputByIdView(_Route):
    reads = "birth_input"


class MediaView(_Route):
    """F05: the owner's collection, and their ``MediaIntent`` (a grant, a removal, an order). No
    route delivers a provider or system event."""

    http_method_names = ["get", "post"]
    reads = "media"
    definition = "MediaIntent"
    command = staticmethod(_command(media.command))


class MediaByIdView(_Route):
    reads = "media_asset"
