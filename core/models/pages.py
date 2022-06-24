from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin import panels
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    TabbedInterface,
    ObjectList,
)
from wagtail.models import Page, Orderable
from wagtail_meta_preview.panels import (
    FacebookPreviewPanel,
    TwitterPreviewPanel,
    GooglePreviewPanel,
)

from core.models.snippets import HeroSection


class SimplePage(Page):
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("SEO image"),
    )

    content_panels = Page.content_panels + [
        InlinePanel("page_sections", label="Sections"),
    ]

    seo_panels = [
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel("og_image"),
            ],
            heading="Facebook",
        ),
        GooglePreviewPanel(heading="Google Preview"),
        FacebookPreviewPanel(heading="Facebook Preview"),
        TwitterPreviewPanel(heading="Twitter Preview"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(seo_panels, heading="SEO"),
            ObjectList(Page.settings_panels, heading=_("Settings")),
        ]
    )


class HomePage(Page):
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("SEO image"),
    )

    hero_section = models.ForeignKey(
        HeroSection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Hero Section"),
    )

    content_panels = Page.content_panels + [
        panels.FieldPanel("hero_section"),
        InlinePanel("page_sections", label="Sections"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(SimplePage.seo_panels, heading="SEO"),
            ObjectList(Page.settings_panels, heading=_("Settings")),
        ]
    )


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
