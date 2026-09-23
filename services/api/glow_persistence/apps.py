from django.apps import AppConfig


class PersistenceDesignConfig(AppConfig):
    name = "glow_persistence"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Glow app persistence design (P11 activation required)"
