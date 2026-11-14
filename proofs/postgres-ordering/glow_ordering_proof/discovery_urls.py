"""The discovery suite's URL configuration (SV3 Stage A): SV1's identity routes, through which the
suite signs in, SV2's member routes, through which it builds the cases' own members, and SV3's page
route. All are imported unchanged; no staff or action route is served."""

from glow_discovery.urls import urlpatterns as discovery_routes
from glow_identity.urls import urlpatterns as identity_routes
from glow_profiles.urls import urlpatterns as profile_routes

urlpatterns = [*identity_routes, *profile_routes, *discovery_routes]
