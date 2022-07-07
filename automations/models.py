from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from automations.const import TriggerType
from mails.models import Email
from mails.utils import send_internal_notification, send_notification


class Trigger(models.Model):
    trigger_type = models.CharField(
        _("Trigger Type"), choices=TriggerType.choices, max_length=64
    )
    name = models.CharField(_("Name"), max_length=32)
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Trigger")
        verbose_name_plural = _("Triggers")


class Action(PolymorphicModel):
    name = models.CharField(_("Name"), max_length=64)
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Action")
        verbose_name_plural = _("Actions")


class EmailAction(Action):
    email = models.ForeignKey(Email, null=True, on_delete=models.SET_NULL)
    recipients = ArrayField(
        models.EmailField(),
        null=True,
        blank=True,
        verbose_name=_("Recipients"),
        help_text=_(
            "Enter a list of email addresses divided by a comma. "
            "In case of trigger notifications, this list will be used instead of the trigger recipient data."
        ),
    )

    is_trigger_notification = models.BooleanField(_("Trigger Notification"))
    is_internal_notification = models.BooleanField(_("Internal Notification"))

    def run(self, trigger_data=None):
        email_template = self.email
        recipients = self.recipients or trigger_data["recipients"]
        if trigger_data:
            email_template.body = email_template.insert_trigger_data(trigger_data)

        if self.is_internal_notification:
            send_internal_notification(email=email_template)

        elif self.is_trigger_notification:
            send_notification(email=email_template, recipients=recipients)

    class Meta:
        verbose_name = _("Email Action")
        verbose_name_plural = _("Email Actions")


class Automation(models.Model):
    name = models.CharField(_("Name"), max_length=64)
    trigger = models.ForeignKey(
        Trigger, null=True, on_delete=models.SET_NULL, verbose_name=_("Trigger")
    )
    actions = models.ManyToManyField(Action, verbose_name=_("Actions"))
    is_active = models.BooleanField(_("Is Active"), default=False)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Automation")
        verbose_name_plural = _("Automations")
