"""F12's routes (the SV4 brief's D19), sealed until integration. The proof's chat URL configuration
serves them beside SV1's identity routes, SV2's member routes, SV3's discovery and action routes
and chat's routes; no runtime URL configuration names them, and the production catalog's paths map
stays empty."""

from django.urls import path

from glow_notifications import views

urlpatterns = [
    path("api/v1/notifications", views.NotificationsView.as_view(), name="glow_notifications"),
    path(
        "api/v1/notifications/device",
        views.DeviceView.as_view(),
        name="glow_notifications_device",
    ),
    path(
        "api/v1/notifications/settings",
        views.SettingsView.as_view(),
        name="glow_notifications_settings",
    ),
]
