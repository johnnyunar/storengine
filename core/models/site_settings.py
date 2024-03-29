from django.db import models
from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.admin.panels import ObjectList, TabbedInterface, FieldPanel
from wagtail.admin.widgets import SwitchInput
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.models import Orderable
from wagtail_color_panel.edit_handlers import NativeColorPanel
from wagtail_color_panel.fields import ColorField

from core.models import fonts


@register_setting(icon="fa-cogs")
class ControlCenter(BaseSetting):
    shop_enabled = models.BooleanField(
        _("Shop Enabled"),
        default=False,
        help_text=_("Enable or disable shop features, like checkout or cart."),
    )

    shipping_address_enabled = models.BooleanField(
        _("Shipping Address Enabled"),
        default=True,
        help_text=_(
            "Enable or disable the shipping address field in checkout."
        ),
    )

    pickup_point_enabled = models.BooleanField(
        _("Pickup Point Enabled"),
        default=True,
        help_text=_("Enable or disable the pickup point field in checkout."),
    )

    accounts_enabled = models.BooleanField(
        _("Account Features Enabled"),
        default=False,
        help_text=_(
            "Enable or disable account features, like login, signup, or profile page."
        ),
    )

    notification_bar_show = models.BooleanField(
        _("Show Notification Bar"),
        default=False,
    )

    notification_bar_text = models.CharField(
        _("Notification Text"), max_length=512, blank=True, null=True
    )

    notifications_panels = [
        FieldPanel("notification_bar_show", widget=SwitchInput),
        FieldPanel("notification_bar_text"),
    ]

    shop_panels = [
        FieldPanel("shop_enabled", widget=SwitchInput),
        MultiFieldPanel([
            FieldPanel("shipping_address_enabled", widget=SwitchInput),
            FieldPanel("pickup_point_enabled", widget=SwitchInput),
        ], heading=_("Checkout"))
    ]

    accounts_panels = [FieldPanel("accounts_enabled", widget=SwitchInput)]

    edit_handler = TabbedInterface(
        [
            ObjectList(notifications_panels, heading=_("Notifications")),
            ObjectList(shop_panels, heading=_("Shop")),
            ObjectList(accounts_panels, heading=_("Accounts")),
        ]
    )

    class Meta:
        verbose_name = _("Control Center")


@register_setting(icon="fa-hashtag")
class ContactSettings(BaseSetting, ClusterableModel):
    full_name = models.CharField(
        _("Full Name"),
        max_length=128,
        blank=True,
        default="Store Engine",
    )

    business_title = models.CharField(
        _("Business Title"),
        max_length=64,
        blank=True,
        null=True,
        default="Eshop Platform",
        help_text=_('E.g. "Personal Coach"'),
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

    contact_address = models.CharField(
        _("Contact Address"), blank=True, null=True, max_length=128
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

    # Legal

    gdpr_url = models.URLField(_("GDPR URL"), blank=True, null=True)
    terms_and_conditions_url = models.URLField(
        _("Terms And Conditions URL"), blank=True, null=True
    )

    contact_panels = [
        FieldPanel("full_name"),
        FieldPanel("business_title"),
        FieldPanel("phone_number"),
        FieldPanel("email"),
        FieldPanel("contact_address"),
    ]

    social_panels = [InlinePanel("social_links", heading=_("Social Links"))]

    billing_panels = [
        FieldPanel("vat_id"),
        FieldPanel("billing_address"),
        FieldPanel("billing_address_zip"),
        FieldPanel("billing_address_city"),
        FieldPanel("invoices_due_in_days"),
        FieldPanel("bank_account"),
        FieldPanel("vat_payer", widget=SwitchInput),
    ]

    legal_panels = [
        FieldPanel("gdpr_url"),
        FieldPanel("terms_and_conditions_url"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(contact_panels, heading=_("Contact")),
            ObjectList(social_panels, heading=_("Social")),
            ObjectList(billing_panels, heading=_("Billing")),
            ObjectList(legal_panels, heading=_("Legal")),
        ]
    )

    class Meta:
        verbose_name = _("Contact")


class SocialLink(Orderable, models.Model):
    settings = ParentalKey(
        ContactSettings, on_delete=models.CASCADE, related_name="social_links"
    )
    name = models.CharField(
        _("Name"), max_length=64, help_text=_("E.g. Twitter")
    )

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
        FieldPanel("is_active", widget=SwitchInput),
    ]

    def __str__(self):
        return self.name


@register_setting(icon="fa-tint")
class BrandSettings(BaseSetting):
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
    )

    google_font = models.ForeignKey(
        "GoogleFont",
        on_delete=models.SET(fonts.get_default_font),
        default=fonts.get_default_font_id,
    )

    # Colors
    primary_color = ColorField(_("Primary Color"), default="#1D2228")
    accent_color = ColorField(_("Accent Color"), default="#FB8122")

    text_color = ColorField(_("Text Color"), default="#FFFFFF")
    error_color = ColorField(
        _("Error Color"),
        default="#FF7B76",
        help_text=_("The color of error messages in forms."),
    )

    cart_color = ColorField(_("Cart Color"), default="#1D2938")
    cart_text_color = ColorField(_("Cart Text Color"), default="#FFFFFF")

    notification_bar_color = ColorField(
        _("Notification Bar Color"), default="#C26F5E"
    )
    notification_bar_text_color = ColorField(
        _("Notification Bar Text Color"), default="#FFFFFF"
    )

    show_footer_waves = models.BooleanField(
        _("Show Footer Waves"), default=False
    )

    footer_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("This image shows up in the footer section."),
        verbose_name=_("Footer Image"),
    )

    general_panels = [
        FieldPanel("logo"),
        FieldPanel("google_font"),
        MultiFieldPanel(
            (
                NativeColorPanel("primary_color"),
                NativeColorPanel("accent_color"),
                NativeColorPanel("text_color"),
                NativeColorPanel("error_color"),
                NativeColorPanel("cart_color"),
                NativeColorPanel("cart_text_color"),
                NativeColorPanel("notification_bar_color"),
                NativeColorPanel("notification_bar_text_color"),
            ),
            heading=_("Colors"),
        ),
    ]

    footer_panels = [
        FieldPanel("show_footer_waves", widget=SwitchInput),
        FieldPanel("footer_image"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(general_panels, heading="General"),
            ObjectList(footer_panels, heading="Footer"),
        ]
    )

    class Meta:
        verbose_name = _("Branding")
