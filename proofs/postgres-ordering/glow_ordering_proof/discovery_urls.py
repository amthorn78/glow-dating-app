"""The discovery suite's URL configuration (SV3 Stage A and Stage B): SV1's identity routes,
through which the suite signs in, SV2's member routes, through which it builds the cases' own
members, SV3's page route, and Stage B's action routes (like and pass, undo, unmatch, the match
read and block). All are imported unchanged; no staff route is served, and no route takes a match
intent."""

from glow_discovery.interaction_urls import urlpatterns as interaction_routes
from glow_discovery.urls import urlpatterns as discovery_routes
from glow_identity.urls import urlpatterns as identity_routes
from glow_profiles.urls import urlpatterns as profile_routes

urlpatterns = [*identity_routes, *profile_routes, *discovery_routes, *interaction_routes]
