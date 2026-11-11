"""The discovery tests' URL configuration: SV1's identity routes, SV2's member routes and SV3's page
route, as the proof's discovery URL configuration composes them. The runtime never loads it."""

from glow_discovery.urls import urlpatterns as discovery_routes
from glow_identity.urls import urlpatterns as identity_routes
from glow_profiles.urls import urlpatterns as profile_routes

urlpatterns = [*identity_routes, *profile_routes, *discovery_routes]
