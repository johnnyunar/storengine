from functools import partial

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin import panels
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable

from core.models import Button, PageSection
from core.utils import user_directory_path


class HomePage(Page):
    hero_title = models.CharField(
        _("Hero Title"),
        max_length=64,
        blank=True,
        default="SNAPSHOP",
        help_text=_("This is the big title that shows up in the hero section."),
    )

    hero_image = models.ImageField(
        _("Hero Section Image"),
        blank=True,
        null=True,
        upload_to=partial(user_directory_path, subdir="hero_images"),
        max_length=300,
    )

    hero_video = models.FileField(
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

    subheading_text = models.CharField(
        _("Hero Subheading"),
        max_length=128,
        blank=True,
        default="",
        help_text=_("This is the text that shows up under the title in the hero section."),
    )

    quiz_heading = models.TextField(_("Quiz Heading"), blank=True, null=True)
    quiz_subheading = models.TextField(_("Quiz Subheading"), blank=True, null=True)

    about_me_text = RichTextField(blank=True, default="")
    about_me_image = models.ImageField(
        _("About Me Section Image"),
        blank=True,
        null=True,
        upload_to=partial(user_directory_path, subdir="about_me_images"),
        max_length=300,
    )

    cta_button = models.ForeignKey(
        Button,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="CTA Button",
    )

    content_panels = Page.content_panels + [
        panels.FieldPanel('hero_title'),
        panels.FieldPanel('hero_image'),
        panels.FieldPanel('hero_video'),
        panels.FieldPanel('subheading_text'),
        panels.FieldPanel('quiz_heading'),
        panels.FieldPanel('quiz_subheading'),
        panels.RichTextFieldPanel('about_me_text'),
        panels.FieldPanel('about_me_image'),
        InlinePanel('page_sections', label="Sections"),
    ]


class HomePageSectionPlacement(Orderable, models.Model):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='page_sections')
    section = models.ForeignKey("PageSection", on_delete=models.CASCADE, related_name='+')

    class Meta(Orderable.Meta):
        verbose_name = "Page Sections"
        verbose_name_plural = "Page Sections"

    panels = [
        FieldPanel('section'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.section.text
