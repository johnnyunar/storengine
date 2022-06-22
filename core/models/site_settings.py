from django.db import models
from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail_color_panel.fields import ColorField


@register_setting(icon="fa-hashtag")
class ContactSettings(BaseSetting):
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

    facebook = models.URLField(help_text=_("Your Facebook page URL"), blank=True, null=True)
    instagram = models.URLField(help_text=_("Your Instagram Profile URL"), blank=True, null=True)
    linkedin = models.URLField(help_text=_("Your LinkedIn Profile URL"), blank=True, null=True)
    trip_advisor = models.URLField(help_text=_("Your Trip Advisor page URL"), blank=True, null=True)
    youtube = models.URLField(help_text=_("Your YouTube channel or user account URL"), blank=True, null=True)
    tiktok = models.URLField(help_text=_("Your TikTok account URL"), blank=True, null=True)

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
    social_panels = [
        FieldPanel("facebook"),
        FieldPanel("instagram"),
        FieldPanel("linkedin"),
        FieldPanel("trip_advisor"),
        FieldPanel("youtube"),
        FieldPanel("tiktok"),
    ]

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


@register_setting(icon="fa-tint")
class BrandSettings(BaseSetting):
    logo = ImageField(_("Logo"), null=True, blank=True)
    primary_color = ColorField(_("Primary Color"), default="#4E8397")
    accent_color = ColorField(_("Accent Color"), default="#4E8397")

    text_color = ColorField(_("Text Color"), default="#FFFFFF")

    show_footer_waves = models.BooleanField(_("Show Footer Waves"), default=False)

    class Meta:
        verbose_name = _("Branding")
