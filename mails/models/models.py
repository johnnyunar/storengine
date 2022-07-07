import mimetypes
from functools import partial

from django.conf import settings
from django.db import models
from django.template import Template, Context, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from djrichtextfield.models import RichTextField
from djrichtextfield.widgets import RichTextWidget
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import TranslatableMixin


class EmailTemplate(TranslatableMixin):
    title = models.CharField(_("Title"), max_length=128)
    description = models.CharField(
        _("Description"), null=True, blank=True, max_length=256
    )
    content = RichTextField(_("Content"), null=True, blank=True)

    def __str__(self):
        return self.title


def get_email_templates() -> list[dict]:
    """Loads Email Templates from db."""
    return [
        {
            "title": template.title,
            "description": template.description,
            "content": template.content,
        }
        for template in EmailTemplate.objects.all()
    ]


class EmailRichTextField(RichTextField):
    """
    RichTextField modified specifically for Emails because of dynamic templates from db.
    """

    def formfield(self, **kwargs):
        template_settings = {"templates": get_email_templates(), "convert_urls": False}
        if self.field_settings:
            self.field_settings.update(template_settings)
        else:
            self.field_settings = template_settings
        kwargs["widget"] = RichTextWidget(
            field_settings=self.field_settings, sanitizer=self.sanitizer
        )
        return super(RichTextField, self).formfield(**kwargs)


class Email(ClusterableModel):
    subject = models.CharField(max_length=128)
    body = EmailRichTextField(
        _("Body"),
        null=True,
        blank=True,
    )

    def insert_trigger_data(self, trigger_data):
        template = Template(self.body)
        trigger_data = Context(trigger_data)
        return template.render(trigger_data)

    def __str__(self):
        return self.subject

    panels = [
        FieldPanel("subject"),
        FieldPanel("body"),
        InlinePanel("email_attachments", heading=_("Attachments")),
    ]

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")


class EmailAttachment(models.Model):
    email = ParentalKey(
        Email, on_delete=models.CASCADE, related_name="email_attachments"
    )
    created_by = CurrentUserField()
    name = models.CharField(_("Name"), max_length=125)
    file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("File"),
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
