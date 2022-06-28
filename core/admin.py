from html import unescape

from django.contrib import admin
from django.utils.html import format_html, strip_tags
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from core.models import (
    SiteConfiguration,
    Button,
)
from core.models.fonts import GoogleFontVariant, GoogleFontSubset, GoogleFont

admin.site.register(GoogleFontVariant)
admin.site.register(GoogleFontSubset)
admin.site.register(GoogleFont)


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    search_fields = ("name", "text_en", "text_cs", "link_en", "link_cs", "color")


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin, admin.ModelAdmin):
    pass
