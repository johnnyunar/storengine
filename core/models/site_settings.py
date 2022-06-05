from django.db import models
from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail_color_panel.fields import ColorField


@register_setting(icon="fa-hashtag")
class SocialMediaSettings(BaseSetting):
    facebook = models.URLField(help_text=_("Your Facebook page URL"))
    instagram = models.CharField(
        max_length=255, help_text=_("Your Instagram username, without the @")
    )
    trip_advisor = models.URLField(help_text=_("Your Trip Advisor page URL"))
    youtube = models.URLField(help_text=_("Your YouTube channel or user account URL"))
    tiktok = models.URLField(help_text=_("Your TikTok account URL"))

    class Meta:
        verbose_name = _("Social Media")


@register_setting(icon="fa-tint")
class BrandSettings(BaseSetting):
    logo = ImageField(_("Logo"), null=True, blank=True)
    primary_color = ColorField(_("Primary Color"), default="#4E8397")
    accent_color = ColorField(_("Accent Color"), default="#4E8397")

    text_color = ColorField(_("Text Color"), default="#FFFFFF")

    class Meta:
        verbose_name = _("Branding")
