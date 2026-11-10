"""SV2's settings fragment: what a settings module that serves the profile routes adds to SV1's
(``glow_identity.conf``). It holds no key, password or connection; the settings module that uses
it supplies them, as SV1's does. ``ATOMIC_REQUESTS`` stays off: each SV2 operation is the whole of
its transaction. The proof's profile settings use it; P11 wires the runtime."""

from __future__ import annotations

INSTALLED_APPS = ["glow_profiles.apps.ProfilesConfig"]
