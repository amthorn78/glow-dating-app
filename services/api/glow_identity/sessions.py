"""Glow's ``USERSESSIONS_ADAPTER`` (the SV1 brief's D6; DM-46's N1).

Installing ``allauth.usersessions`` for D5's reference also serves the member's session list
(``app/v1/auth/sessions``), whose ``DELETE`` ends the chosen sessions through this adapter's
``end_sessions``, at allauth's layer only. Glow's adapter ends each chosen session at both
layers: ``sign_out`` for the ``AccountSession`` whose reference is the row's primary key, if
there is one, then the row's own ``end()``. allauth limits the choices to the request user's
own rows (``SelectSessionsInput``), and logs out when the current session is among them.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from allauth.usersessions.adapter import DefaultUserSessionsAdapter

from glow_identity import revocation


class GlowUserSessionsAdapter(DefaultUserSessionsAdapter):  # type: ignore[misc]
    def end_sessions(self, sessions: Iterable[Any]) -> None:
        for session in sessions:
            revocation.end_user_session(session)
