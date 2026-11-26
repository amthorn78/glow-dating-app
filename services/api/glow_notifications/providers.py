"""The token store's and the push transport's factory hooks (the SV4 brief's D16; DM-101's AM1).

F12's code reaches the token store, and SV4 B2's deliverer the push transport, only through a
factory a setting names (a dotted path to a callable that returns one), as chat's history read
reaches its text reader (``GLOW_CHAT_TEXT_READER``): ``GLOW_NOTIFICATIONS_TOKEN_STORE`` and
``GLOW_NOTIFICATIONS_PUSH_TRANSPORT``. Only the disposable-database proof's chat settings name
them, each with its in-memory fixture (``FixtureTokenStore``, ``FixturePushTransport``), which
keeps its own refusal outside development and test (``require_fixture_environment``). The served
runtime names neither; with none named the hook answers ``None``, and whatever needs one refuses
without it (``provider_unavailable``): the device command's ``no_token_store``. No provider, network
client or credential is reached from here: P09.2 brings the real token and P11B the transport.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.utils.module_loading import import_string

from glow_domain.notifications import PushTransport, TokenStore

TOKEN_STORE_SETTING = "GLOW_NOTIFICATIONS_TOKEN_STORE"
PUSH_TRANSPORT_SETTING = "GLOW_NOTIFICATIONS_PUSH_TRANSPORT"


def _made(setting: str) -> Any:
    path = getattr(settings, setting, None)
    if not isinstance(path, str) or not path:
        return None
    factory: Callable[[], Any] = import_string(path)
    return factory()


def token_store() -> TokenStore | None:
    """The token store the setting's factory returns, or ``None`` when no factory is named."""
    store: TokenStore | None = _made(TOKEN_STORE_SETTING)
    return store


def push_transport() -> PushTransport | None:
    """The push transport the setting's factory returns, or ``None`` when no factory is named. SV4
    B1 has no caller; SV4 B2's deliverer takes it here."""
    transport: PushTransport | None = _made(PUSH_TRANSPORT_SETTING)
    return transport
