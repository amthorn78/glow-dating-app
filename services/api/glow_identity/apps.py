from django.apps import AppConfig


class IdentityConfig(AppConfig):  # type: ignore[misc]
    name = "glow_identity"
    verbose_name = "Glow identity (SV1; sealed until P11 wires it)"
