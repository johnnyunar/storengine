import logging

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
from wagtail.admin.panels import FieldPanel
from wagtail.admin.widgets import SwitchInput
from wagtailautocomplete.edit_handlers import AutocompletePanel

from automations.const import TriggerType
from mails.models import Email
from mails.utils import send_internal_notification, send_notification
from shop.models import Product

logger = logging.getLogger("django")


class Trigger(models.Model):
    """
    Triggers are used in automation flows.

    They can only be created using the types predefined in TriggerType.choices.
    """

    trigger_type = models.CharField(
        _("Trigger Type"), choices=TriggerType.choices, max_length=64
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        verbose_name=_("Products"),
        help_text=_(
            "You can choose to fire this trigger for selected products only."
        ),
    )
    name = models.CharField(_("Name"), max_length=32)
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Trigger")
        verbose_name_plural = _("Triggers")

    panels = [
        FieldPanel("trigger_type"),
        AutocompletePanel("products", target_model=Product),
        FieldPanel("name"),
        FieldPanel("is_active", widget=SwitchInput),
    ]


class Action(PolymorphicModel):
    """
    Base model for all action types. This model allows us
    to create multiple Action instances with polymorphic fields
    and then query all of them using single Action query.
    Each child model should implement the run() method with action logic.
    """

    name = models.CharField(_("Name"), max_length=64)
    is_active = models.BooleanField(_("Is Active"), default=True)

    autocomplete_search_field = 'name'

    def autocomplete_label(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Action")
        verbose_name_plural = _("Actions")


class EmailAction(Action):
    """
    Action specific for emails.
    """

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

    # TODO: Add proper return value
    def run(self, trigger_data: dict = None) -> None:
        """
        Runs action's specific logic.
        :param trigger_data: Context used to render email template. Usually injected by connected trigger object.
        """
        email_template = self.email
        recipients = self.recipients or trigger_data["recipients"]
        if trigger_data:
            email_template.body = email_template.insert_trigger_data(
                trigger_data
            )

        if self.is_internal_notification:
            send_internal_notification(email=email_template)

        elif self.is_trigger_notification:
            send_notification(email=email_template, recipients=recipients)

        logger.info(f"Email action {self.name} triggered.")

    class Meta:
        verbose_name = _("Email Action")
        verbose_name_plural = _("Email Actions")


class Automation(models.Model):
    """
    Automation objects store individual automation flows consisting of a Trigger and an action set.
    For Automations usage see `receivers.py`.
    """

    name = models.CharField(_("Name"), max_length=64)
    trigger = models.ForeignKey(
        Trigger,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Trigger"),
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

    panels = [
        FieldPanel("name"),
        FieldPanel("trigger"),
        AutocompletePanel("actions", target_model=Action),
        FieldPanel("is_active", widget=SwitchInput),
    ]
