"""SV1's URL configuration (sealed until P11): allauth's headless API for the ``app`` client,
under ``_allauth/app/v1/``, and the one Glow route. No browser client, specification or
headed allauth view is served."""

from django.urls import include, path

from glow_identity.views import AccountAccessView

urlpatterns = [
    path("_allauth/", include("allauth.headless.urls")),
    path("api/v1/account/access", AccountAccessView.as_view(), name="glow_account_access"),
]
