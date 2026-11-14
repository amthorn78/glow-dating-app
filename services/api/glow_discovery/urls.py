"""SV3 Stage A's member route (sealed until P11). The proof's discovery URL configuration serves it
beside SV1's identity routes and SV2's member routes; the production catalog's paths map stays empty
until P11 serves the routes. Stage B adds the action routes."""

from django.urls import path

from glow_discovery import views

urlpatterns = [
    path("api/v1/discovery/page", views.PageView.as_view(), name="glow_discovery_page"),
]
