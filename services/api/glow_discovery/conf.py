"""SV3's settings fragment: what a settings module that serves the discovery route adds to SV1's
(``glow_identity.conf``) and SV2's (``glow_profiles.conf``). It holds no key, password or
connection, and it selects no compatibility provider: the settings module that uses it does, and
only the proof's discovery settings select one, the fixture adapter (D6). ``ATOMIC_REQUESTS``
stays off: each page is the whole of its transaction. P11 wires the runtime."""

from __future__ import annotations

INSTALLED_APPS = ["glow_discovery.apps.DiscoveryConfig"]
