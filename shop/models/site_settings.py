from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting


@register_setting(icon="fa-shopping-cart")
class ShopSettings(BaseSetting):
    shop_enabled = models.BooleanField(
        _("Shop Enabled"),
        default=False,
        help_text=_("Enable or disable shop features, like checkout or cart."),
    )

    class Meta:
        verbose_name = _("Shop Settings")
