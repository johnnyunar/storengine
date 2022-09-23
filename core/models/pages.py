from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin import panels
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.admin.panels import (
    TabbedInterface,
    ObjectList,
)
from wagtail.admin.widgets import SwitchInput
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.fields import RichTextField
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

    seo_keywords = models.CharField(
        _("Keywords"),
        max_length=512,
        null=True,
        blank=True,
        help_text=_(
            "Comma-separated keywords for search engines. For Example: food, friends, travelling"
        ),
    )

    menu_order = models.PositiveIntegerField(
        _("Menu Order"),
        null=True,
        blank=True,
    )

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title", classname="title"),
                FieldPanel("slug"),
            ],
            heading=_("Navigation"),
        ),
        InlinePanel("page_sections", label="Sections"),
    ]

    seo_panels = [
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel("seo_keywords"),
                FieldPanel("og_image"),
            ],
            heading=_("For search engines"),
        ),
        GooglePreviewPanel(heading="Google Preview"),
        FacebookPreviewPanel(heading="Facebook Preview"),
        TwitterPreviewPanel(heading="Twitter Preview"),
    ]

    settings_panels = [
                          MultiFieldPanel(
                              [FieldPanel("show_in_menus", widget=SwitchInput), FieldPanel("menu_order")],
                              heading=_("For site menus"),
                          ),
                      ] + Page.settings_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(seo_panels, heading="SEO"),
            ObjectList(settings_panels, heading=_("Settings")),
        ]
    )

    def save(self, *args, **kwargs):
        all_order_numbers = SimplePage.objects.exclude(pk=self.pk).values_list(
            "menu_order", flat=True
        )
        # If there is an order conflict, update all pages accordingly
        if self.menu_order in all_order_numbers:
            SimplePage.objects.filter(menu_order__gte=self.menu_order).update(
                menu_order=F("menu_order") + 1
            )

        super().save()


class HomePage(Page):
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("SEO image"),
    )

    seo_keywords = models.CharField(
        _("Keywords"),
        max_length=512,
        null=True,
        blank=True,
        help_text=_(
            "Comma-separated keywords for search engines. For Example: food, friends, travelling"
        ),
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


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]
