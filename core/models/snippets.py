from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail_color_panel.edit_handlers import NativeColorPanel
from wagtail_color_panel.fields import ColorField


@register_snippet
class Button(models.Model):
    name = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="This name shows up in admin only.",
    )
    text = models.CharField(max_length=64, blank=True, default="")
    link = models.CharField(max_length=512, blank=True, default="")
    custom_html = models.TextField(
        blank=True, default="", help_text="This option overwrites the link setting."
    )
    open_in_new_tab = models.BooleanField(default=True)

    color = ColorField(default="#0e0e0e")

    panels = [
        FieldPanel('name'),
        FieldPanel('text'),
        FieldPanel('link'),
        FieldPanel('custom_html'),
        FieldPanel('open_in_new_tab'),
        NativeColorPanel('color'),
    ]

    def __str__(self):
        return self.name or f"{_('Button')} {self.pk}"

    class Meta:
        verbose_name = _("Button")
        verbose_name_plural = _("Buttons")

    def clean(self):
        super(Button, self).clean()
        if not (self.custom_html or self.link):
            raise ValidationError(
                _("At least custom_html or a link must be specified.")
            )
        elif not (self.link and self.text):
            raise ValidationError(_("Link must be specified with text."))


@register_snippet
class PageSection(index.Indexed, models.Model):
    created_by = CurrentUserField()
    name = models.TextField(_("Name"), max_length=128)
    text = RichTextField(_("Text"))
    button = models.ForeignKey(
        Button,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Button"),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("text"),
        FieldPanel("button"),
    ]

    search_fields = [
        index.SearchField('name', partial_match=True),
        index.SearchField('text', partial_match=True),
        index.SearchField('button', partial_match=True),
    ]

    def __str__(self):
        return self.name
