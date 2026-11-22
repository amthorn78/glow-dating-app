"""The chat suite's URL configuration (SV4 A2; its brief's D10): SV1's identity routes, through
which the suite signs in, SV2's member routes, through which it builds the cases' own members,
SV3's page and action routes (the match read and SV4 A2's match list among them), through which it
matches them, and chat's routes (D8). All are imported unchanged; no staff route is served, no
route takes a match intent and none a ``ChannelIntent``."""

from glow_chat.urls import urlpatterns as chat_routes
from glow_discovery.interaction_urls import urlpatterns as interaction_routes
from glow_discovery.urls import urlpatterns as discovery_routes
from glow_identity.urls import urlpatterns as identity_routes
from glow_profiles.urls import urlpatterns as profile_routes

urlpatterns = [
    *identity_routes,
    *profile_routes,
    *discovery_routes,
    *interaction_routes,
    *chat_routes,
]
