from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin import panels
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Page, Orderable

from core.models.snippets import HeroSection


class SimplePage(Page):
    content_panels = Page.content_panels + [
        InlinePanel("page_sections", label="Sections"),
    ]


class HomePage(Page):
    hero_section = models.ForeignKey(
        HeroSection, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Hero Section")
    )

    content_panels = Page.content_panels + [
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
