from django.conf import settings
from django.urls import path

from .views import DevelopmentRecommendationsView, LivenessView, ReadinessView

urlpatterns = [
    path("health/live", LivenessView.as_view(), name="liveness"),
    path("health/ready", ReadinessView.as_view(), name="readiness"),
]
if settings.GLOW_ENV in {"development", "test"}:
    urlpatterns.append(
        path(
            "api/v1/development/recommendations",
            DevelopmentRecommendationsView.as_view(),
            name="development-recommendations",
        )
    )
