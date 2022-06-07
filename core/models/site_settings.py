from django.db import models
from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail_color_panel.fields import ColorField


@register_setting(icon="fa-hashtag")
class ContactSettings(BaseSetting):
    full_name = models.CharField(
        _("Full Name"),
        max_length=64,
        blank=True,
        default="Snap Shop",
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
        default="",
    )

    email = models.EmailField(
        _("Email"),
        blank=True,
        default="",
    )

    facebook = models.URLField(help_text=_("Your Facebook page URL"))
    instagram = models.URLField(help_text=_("Your Instagram Profile URL"))
    linkedin = models.URLField(help_text=_("Your LinkedIn Profile URL"))
    trip_advisor = models.URLField(help_text=_("Your Trip Advisor page URL"))
    youtube = models.URLField(help_text=_("Your YouTube channel or user account URL"))
    tiktok = models.URLField(help_text=_("Your TikTok account URL"))

    class Meta:
        verbose_name = _("Contact")


@register_setting(icon="fa-tint")
class BrandSettings(BaseSetting):
    logo = ImageField(_("Logo"), null=True, blank=True)
    primary_color = ColorField(_("Primary Color"), default="#4E8397")
    accent_color = ColorField(_("Accent Color"), default="#4E8397")

    text_color = ColorField(_("Text Color"), default="#FFFFFF")

    class Meta:
        verbose_name = _("Branding")
