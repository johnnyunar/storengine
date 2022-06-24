from django.db import models
from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface, InlinePanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.models import Orderable
from wagtail_color_panel.fields import ColorField

from core.models import fonts


@register_setting(icon="fa-hashtag")
class ContactSettings(BaseSetting, ClusterableModel):
    full_name = models.CharField(
        _("Full Name"),
        max_length=64,
        blank=True,
        default="Store Engine",
    )

    vat_id = models.CharField(
        _("VAT ID"),
        max_length=10,
        blank=True,
        default="",
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=16,
        blank=True,
        null=True,
    )

    email = models.EmailField(
        _("Email"),
        blank=True,
        null=True,
    )

    # Billing
    billing_address = models.CharField(
        _("Billing Address"), blank=True, null=True, max_length=128
    )
    billing_address_zip = models.CharField(
        _("ZIP"), blank=True, null=True, max_length=16
    )
    billing_address_city = models.CharField(
        _("City"), blank=True, null=True, max_length=64
    )
    invoices_due_in_days = models.PositiveIntegerField(
        _("Default Number of Days until Invoice is Due"), default=14
    )
    bank_account = models.CharField(
        _("Bank Account"), blank=True, null=True, max_length=64
    )
    vat_payer = models.BooleanField(_("VAT Payer"), default=False)

    contact_panels = [
        FieldPanel("full_name"),
        FieldPanel("phone_number"),
        FieldPanel("email"),
    ]

    social_panels = [InlinePanel("social_links", heading=_("Social Links"))]

    billing_panels = [
        FieldPanel("vat_id"),
        FieldPanel("billing_address"),
        FieldPanel("billing_address_zip"),
        FieldPanel("billing_address_city"),
        FieldPanel("invoices_due_in_days"),
        FieldPanel("bank_account"),
        FieldPanel("vat_payer"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(contact_panels, heading="Contact"),
            ObjectList(social_panels, heading="Social"),
            ObjectList(billing_panels, heading="Billing"),
        ]
    )

    class Meta:
        verbose_name = _("Contact")


class SocialLink(Orderable, models.Model):
    settings = ParentalKey(
        ContactSettings, on_delete=models.CASCADE, related_name="social_links"
    )
    name = models.CharField(_("Name"), max_length=64, help_text=_("E.g. Twitter"))

    url = models.URLField(
        _("URL"), max_length=512, help_text=_("E.g. https://twitter.com/home/")
    )

    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Icon"),
    )

    is_active = models.BooleanField(_("Available"), default=True)

    class Meta(Orderable.Meta):
        verbose_name = "Social Links"
        verbose_name_plural = "Social Links"

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
        FieldPanel("icon"),
        FieldPanel("is_active"),
    ]

    def __str__(self):
        return self.name


@register_setting(icon="fa-tint")
class BrandSettings(BaseSetting):
    logo = ImageField(_("Logo"), null=True, blank=True)
    google_font = models.ForeignKey(
        "GoogleFont",
        on_delete=models.SET(fonts.get_default_font),
        default=fonts.get_default_font_id,
    )
    primary_color = ColorField(_("Primary Color"), default="#4E8397")
    accent_color = ColorField(_("Accent Color"), default="#4E8397")

    text_color = ColorField(_("Text Color"), default="#FFFFFF")

    show_footer_waves = models.BooleanField(_("Show Footer Waves"), default=False)

    class Meta:
        verbose_name = _("Branding")
