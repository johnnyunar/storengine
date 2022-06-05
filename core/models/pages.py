from functools import partial

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin import panels
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable

from core.models import Button
from core.models.snippets import HeroSection
from core.utils import user_directory_path


class SimplePage(Page):
    content_panels = Page.content_panels + [
        InlinePanel("page_sections", label="Sections"),
    ]


class HomePage(Page):
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

    hero_section = models.ForeignKey(
        HeroSection, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Hero Section")
    )

    content_panels = Page.content_panels + [
        panels.FieldPanel("quiz_heading"),
        panels.FieldPanel("quiz_subheading"),
        panels.RichTextFieldPanel("about_me_text"),
        panels.FieldPanel("about_me_image"),
        panels.FieldPanel("hero_section"),
        InlinePanel("page_sections", label="Sections"),
    ]


class PageSectionPlacement(Orderable, models.Model):
    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="page_sections")
    section = models.ForeignKey(
        "PageSection", on_delete=models.CASCADE, related_name="+"
    )

    class Meta(Orderable.Meta):
        verbose_name = "Page Sections"
        verbose_name_plural = "Page Sections"

    panels = [
        FieldPanel("section"),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.section.text
