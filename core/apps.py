from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"
    verbose_name = "Web"


def ready(self):
    from core import google_fonts_updater
    google_fonts_updater.start()
