"""The profile suite's URL configuration (SV2 Stage A): SV1's identity routes (allauth's headless
API for the ``app`` client and ``api/v1/account/access``), through which the suite signs in, and
SV2's member routes. Both are imported unchanged; no staff route is served."""

from glow_identity.urls import urlpatterns as identity_routes
from glow_profiles.urls import urlpatterns as profile_routes

urlpatterns = [*identity_routes, *profile_routes]
