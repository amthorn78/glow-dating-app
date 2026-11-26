"""SV4 B1's settings fragment: what a settings module that serves F12's routes adds to SV1's
(``glow_identity.conf``) and SV2's (``glow_profiles.conf``). It holds no key, password or
connection, and it names no token store or push transport: the settings module that uses it does,
and only the proof's chat settings name one, the in-memory fixture (the SV4 brief's D16; DM-101's
AM1). ``ATOMIC_REQUESTS`` stays off: each command and read is the whole of its transaction, and
F12's views are ``non_atomic_requests`` whatever it says. Integration wires the runtime."""

from __future__ import annotations

INSTALLED_APPS = ["glow_notifications.apps.NotificationsConfig"]
