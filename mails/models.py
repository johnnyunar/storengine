import mimetypes
from functools import partial

from django.conf import settings
from django.db import models
from django.template import Template, Context
from django.template.loader import render_to_string

from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from djrichtextfield.models import RichTextField

from core.utils import user_directory_path

EMAIL_TEMPLATES = [
    {
        "title": _("Order Confirmation Email"),
        "description": _("This email format is great for order confirmations."),
        "content": render_to_string(
            "mails/order_confirmation.html",
            context={"base_url": settings.BASE_URL},
        ),
    },
    {
        "title": _("Internal Notification Email"),
        "description": _("This email format is great for internal notifications."),
        "content": render_to_string(
            "mails/internal_notification.html",
            context={"base_url": settings.BASE_URL},
        ),
    },
]


class EmailAttachment(models.Model):
    created_by =  CurrentUserField()
    name = models.CharField(_("Name"), max_length=125)
    file = models.FileField(
        _("File"),
        upload_to=partial(user_directory_path, subdir="email_attachments"),
        blank=True,
        null=True,
        default="accounts/default-user.png",
    )
    file_name = models.CharField(
        _("Send as"),
        max_length=32,
        help_text=_(
            "This filename will be used as the attachment name. For example: my_great_ebook.pdf. "
            "In case you enter a filename without extension (my_great_ebook), "
            "the extension will be added automatically corresponding to the uploaded file."
        ),
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def save(self, *args, **kwargs):
        # Override the save method to add a file extension corresponding to the uploaded file
        # in case there was a file name without an extension provided
        if not mimetypes.guess_type(self.file_name)[0]:
            self.file_name += mimetypes.guess_extension(
                mimetypes.guess_type(self.file.name)[0]
            )
        super(EmailAttachment, self).save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Email Attachment")
        verbose_name_plural = _("Email Attachments")


class Email(models.Model):
    subject = models.CharField(max_length=128)
    body = RichTextField(
        field_settings={
            "templates": EMAIL_TEMPLATES,
            "convert_urls": False,
        }
    )
    attachments = models.ManyToManyField(
        EmailAttachment, blank=True, verbose_name=_("Attachments")
    )

    def insert_trigger_data(self, trigger_data):
        template = Template(self.body)
        trigger_data = Context(trigger_data)
        return template.render(trigger_data)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")
