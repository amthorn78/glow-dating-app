"""The profile tests' URL configuration: SV1's identity routes and SV2's member routes, as the
proof's profile URL configuration composes them. The served runtime never loads this module."""

from glow_identity.urls import urlpatterns as identity_routes
from glow_profiles.urls import urlpatterns as profile_routes

urlpatterns = [*identity_routes, *profile_routes]
