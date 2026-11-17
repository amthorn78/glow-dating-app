"""SV3 Stage B's member routes (sealed until P11), beside Stage A's page route (``urls``), which
they leave unchanged. The proof's discovery URL configuration serves both, with SV1's identity
routes and SV2's member routes; the production catalog's paths map stays empty until P11 serves
the routes. No route takes a match intent (F09). Correction B-C1 (DM-74) adds one read, the
actor's own versions toward a profile (``GET api/v1/interactions/<profile_id>``)."""

from django.urls import path

from glow_discovery import interaction_views as views

urlpatterns = [
    path(
        "api/v1/discovery/interaction",
        views.InteractionView.as_view(),
        name="glow_discovery_interaction",
    ),
    path(
        "api/v1/discovery/interaction/undo",
        views.UndoView.as_view(),
        name="glow_discovery_undo",
    ),
    path("api/v1/matches/unmatch", views.UnmatchView.as_view(), name="glow_unmatch"),
    path("api/v1/matches/<uuid:match_id>", views.MatchView.as_view(), name="glow_match"),
    path("api/v1/blocks", views.BlockView.as_view(), name="glow_blocks"),
    path(
        "api/v1/interactions/<uuid:profile_id>",
        views.OwnVersionsView.as_view(),
        name="glow_own_interaction_versions",
    ),
]
