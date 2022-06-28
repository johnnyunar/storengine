from html import unescape

from django.contrib import admin
from django.utils.html import format_html, strip_tags
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from core.models import (
    SiteConfiguration,
    Button,
    FrequentlyAskedQuestion
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


@admin.register(FrequentlyAskedQuestion)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question_tag", "answer_tag", "is_active")
    list_editable = ("is_active",)
    search_fields = ("question", "answer")
    list_display_link = ("question_tag", "answer_tag")
    list_filter = ("created_at",)

    readonly_fields = ("created_at", "updated_at")

    def question_tag(self, obj):
        return unescape(strip_tags(obj.question))

    def answer_tag(self, obj):
        return unescape(strip_tags(obj.answer))

    question_tag.short_description = _("Question")
    answer_tag.short_description = _("Answer")
