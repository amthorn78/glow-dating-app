"""Only liveness, honest readiness, and an explicitly synthetic smoke route."""

from typing import Any

from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .fixtures import recommendations


# DRF ships no typing marker; keep this one framework inheritance boundary explicit.
class PublicReadOnlyView(APIView):  # type: ignore[misc]
    authentication_classes: list[Any] = []
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def finalize_response(self, request: Any, response: Any, *args: Any, **kwargs: Any) -> Any:
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


class LivenessView(PublicReadOnlyView):
    def get(self, request: Any) -> Response:
        return Response({"status": "alive"})


class ReadinessView(PublicReadOnlyView):
    def get(self, request: Any) -> Response:
        return Response(
            {
                "status": "not_ready",
                "mode": "fixture",
                "reason": "live_integrations_not_configured",
            },
            status=503,
        )


class DevelopmentRecommendationsView(PublicReadOnlyView):
    def get(self, request: Any) -> Response:
        # The URL is also conditionally registered; retain a per-request guard.
        if settings.GLOW_ENV not in {"development", "test"}:
            return Response({"detail": "Not found."}, status=404)
        return Response(recommendations())
