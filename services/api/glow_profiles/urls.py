"""SV2's member routes (sealed until P11). The proof's profile URL configuration serves them beside
SV1's identity routes. No staff route exists (D1); the production catalog's paths map stays empty
until P11 serves the routes."""

from django.urls import path

from glow_profiles import views

urlpatterns = [
    path("api/v1/profile", views.ProfileView.as_view(), name="glow_profile"),
    path("api/v1/profile/completion", views.CompletionView.as_view(), name="glow_completion"),
    path("api/v1/profile/visibility", views.VisibilityView.as_view(), name="glow_visibility"),
    path("api/v1/profile/fields", views.FieldsView.as_view(), name="glow_profile_fields"),
    path("api/v1/profile/preferences", views.PreferencesView.as_view(), name="glow_preferences"),
    path("api/v1/profile/filters", views.FiltersView.as_view(), name="glow_filters"),
    path("api/v1/profile/area", views.AreaView.as_view(), name="glow_area"),
    path("api/v1/profile/area/nearest", views.NearestAreaView.as_view(), name="glow_area_nearest"),
    path("api/v1/profile/catalog", views.CatalogView.as_view(), name="glow_catalog"),
    path(
        "api/v1/profile/<uuid:profile_id>",
        views.ProfileByIdView.as_view(),
        name="glow_profile_by_id",
    ),
    path("api/v1/consent", views.ConsentView.as_view(), name="glow_consent"),
    path("api/v1/consent/sensitive", views.SensitiveConsentView.as_view(), name="glow_sensitive"),
    path("api/v1/eligibility/adult", views.AdultCheckView.as_view(), name="glow_adult_check"),
    path("api/v1/birth-input", views.BirthInputView.as_view(), name="glow_birth_input"),
    path(
        "api/v1/birth-input/<uuid:input_id>",
        views.BirthInputByIdView.as_view(),
        name="glow_birth_input_by_id",
    ),
]
