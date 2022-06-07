from functools import partial

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from polymorphic.models import PolymorphicModel
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail_color_panel.edit_handlers import NativeColorPanel

from wagtail_color_panel.fields import ColorField

from core.utils import user_directory_path, camel_to_snake


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
        FieldPanel("name"),
        FieldPanel("text"),
        FieldPanel("link"),
        FieldPanel("custom_html"),
        FieldPanel("open_in_new_tab"),
        NativeColorPanel("color"),
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


class PageSection(index.Indexed, PolymorphicModel):
    created_by = CurrentUserField()
    name = models.TextField(_("Name"), max_length=128)
    text_color = ColorField(_("Text Color"), blank=True, null=True)
    background_color = ColorField(_("Background Color"), blank=True, null=True)

    panels = [
        FieldPanel("name"),
        NativeColorPanel("text_color"),
        NativeColorPanel("background_color"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    def __str__(self):
        return self.name

    def get_template_name(self):
        obj_content_type = ContentType.objects.get_for_model(self)
        app_label = obj_content_type.app_label
        print(f"{app_label}/snippets/_{camel_to_snake(self.__class__.__name__)}.html")
        return f"{app_label}/snippets/_{camel_to_snake(self.__class__.__name__)}.html"

    def render(self):
        return format_html(
            render_to_string(
                self.get_template_name(),
                context={"section": self},
            )
        )


@register_snippet
class BasicPageSection(PageSection):
    text = RichTextField(_("Text"))

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("This image will show up on the right side of the section."),
        verbose_name=_("Image"),
    )

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
        FieldPanel("image"),
        FieldPanel("button"),
        NativeColorPanel("text_color"),
        NativeColorPanel("background_color"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("text", partial_match=True),
        index.SearchField("button", partial_match=True),
    ]

    def __str__(self):
        return self.name


@register_snippet
class HeroSection(index.Indexed, models.Model):
    created_by = CurrentUserField()
    name = models.TextField(_("Name"), max_length=128)
    title = models.CharField(
        _("Hero Title"),
        max_length=64,
        blank=True,
        default="SNAPSHOP",
        help_text=_("This is the big title that shows up in the hero section."),
    )

    subheading = models.CharField(
        _("Hero Subheading"),
        max_length=128,
        blank=True,
        default="",
        help_text=_(
            "This is the text that shows up under the title in the hero section."
        ),
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("This image shows up in the hero section."),
        verbose_name=_("Hero Image"),
    )

    video = models.FileField(
        _("Hero Video"),
        upload_to=partial(user_directory_path, subdir="hero_videos"),
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("title"),
        FieldPanel("subheading"),
        FieldPanel("image"),
        FieldPanel("video"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("title", partial_match=True),
        index.SearchField("subheading", partial_match=True),
    ]

    def __str__(self):
        return self.name


@register_snippet
class ContactSection(PageSection):
    pass
