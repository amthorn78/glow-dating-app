from django.apps import AppConfig


class DiscoveryConfig(AppConfig):  # type: ignore[misc]
    name = "glow_discovery"
    verbose_name = "Glow discovery (SV3; sealed until P11 wires it)"

    def ready(self) -> None:
        # D6 (PF01 section 5): a fixture compatibility provider is refused outside development
        # and test at boot, before any page is served.
        from glow_discovery import policy

        policy.require_fixture_environment()
