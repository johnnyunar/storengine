from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AutomationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "automations"
    verbose_name = _("Automations")

    def ready(self):
        import automations.receivers  # Allow signal receivers to be run in a separate file
