"""Chat's routes (the SV4 brief's D8), sealed until integration. The proof's chat URL configuration
serves them beside SV1's identity routes, SV2's member routes and SV3's discovery and action
routes; no runtime URL configuration names them, and the production catalog's paths map stays
empty. There is no ``ChannelIntent`` route (OD-45)."""

from django.urls import path

from glow_chat import views

urlpatterns = [
    path("api/v1/chat/messages", views.MessageView.as_view(), name="glow_chat_messages"),
    path(
        "api/v1/chat/conversations",
        views.ConversationListView.as_view(),
        name="glow_chat_conversations",
    ),
    path("api/v1/chat/history", views.HistoryView.as_view(), name="glow_chat_history"),
    path("api/v1/chat/read-cursor", views.ReadCursorView.as_view(), name="glow_chat_read_cursor"),
]
