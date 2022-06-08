from functools import partial

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import TranslatableMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail_color_panel.edit_handlers import NativeColorPanel
from wagtail_color_panel.fields import ColorField

from core.models import FrequentlyAskedQuestion
from core.utils import user_directory_path


@register_snippet
class Button(TranslatableMixin):
    name = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=_("This name shows up in admin only."),
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
        unique_together = [("translation_key", "locale")]

    def clean(self):
        super(Button, self).clean()
        if not (self.custom_html or self.link):
            raise ValidationError(
                _("At least custom_html or a link must be specified.")
            )
        elif not (self.link and self.text):
            raise ValidationError(_("Link must be specified with text."))


@register_snippet
class PageSection(index.Indexed, TranslatableMixin):
    class SectionTypes(models.TextChoices):
        DEFAULT = "default_section", _("Default Section")
        FAQ = "faq_section", _("FAQ Section")
        CONTACT = "contact_section", _("Contact Section")

    created_by = CurrentUserField()

    section_type = models.CharField(
        _("Type"),
        max_length=125,
        choices=SectionTypes.choices,
        default=SectionTypes.DEFAULT,
    )
    name = models.TextField(_("Name"), max_length=128)
    text_color = ColorField(_("Text Color"), blank=True, null=True)
    background_color = ColorField(_("Background Color"), blank=True, null=True)

    text = RichTextField(_("Text"), null=True, blank=True)

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

    iframe = models.TextField(
        _("Iframe"),
        null=True,
        blank=True,
        help_text=_(
            "If you need to embed any content in this section, you can paste the <iframe> code here. "
            "Tip: Content size not right? Look for width='XXX' and height='XXX' in the pasted code and change it! "
            "For example, you can use width='100%'."
        ),
    )

    panels = [
        FieldPanel("section_type"),
        FieldPanel("name"),
        FieldPanel("text"),
        FieldPanel("image"),
        FieldPanel("button"),
        FieldPanel("iframe"),
        NativeColorPanel("text_color"),
        NativeColorPanel("background_color"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("text", partial_match=True),
        index.SearchField("button", partial_match=True),
    ]

    class Meta:
        unique_together = [("translation_key", "locale")]

    def __str__(self):
        return self.name

    @property
    def faqs(self):
        return FrequentlyAskedQuestion.objects.filter(is_active=True)

    def get_template_name(self):
        obj_content_type = ContentType.objects.get_for_model(self)
        app_label = obj_content_type.app_label
        return f"{app_label}/snippets/_{self.section_type}.html"


@register_snippet
class HeroSection(index.Indexed, TranslatableMixin):
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

    class Meta:
        unique_together = [("translation_key", "locale")]

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
