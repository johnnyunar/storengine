from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mails'
    verbose_name = _("Mails")
