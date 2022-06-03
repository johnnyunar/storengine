from django.db import models
from django.utils.translation import gettext_lazy as _


class TriggerType(models.TextChoices):
    NEW_USER = "new_user", _("New User")
    NEW_ORDER = "new_order", _("New Order")
    NEW_QUIZ_RECORD = "new_quiz_record", _("New Quiz Record")
