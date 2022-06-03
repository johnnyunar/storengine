from html import unescape

from django.contrib import admin
from django.utils.html import format_html, strip_tags
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin, TabbedTranslationAdmin
from solo.admin import SingletonModelAdmin

from core.models import (
    SiteConfiguration,
    Testimonial,
    Ebook,
    Button,
    FrequentlyAskedQuestion, Counter,
)


@admin.register(Button)
class ButtonAdmin(TabbedTranslationAdmin):
    search_fields = ("name", "text_en", "text_cs", "link_en", "link_cs", "color")


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin, TabbedTranslationAdmin):
    save_on_top = True

    fieldsets = (
        (
            _("Homepage"),
            {
                "fields": (
                    "hero_image",
                    "hero_video",
                    "about_me_image",
                    "hero_title",
                    "cta_button",
                    "subheading_text",
                    "quiz_heading",
                    "quiz_subheading",
                    "ebook_text",
                    "about_me_text",
                )
            },
        ),
        (
            _("Notifications"),
            {
                "fields": (
                    "notification_bar_show",
                    "notification_bar_text",
                )
            },
        ),
        (
            _("Global"),
            {"fields": ("footer_image",)},
        ),
        (
            _("Contact"),
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "email",
                    "instagram_link",
                    "facebook_link",
                    "linkedin_link",
                )
            },
        ),
        (
            _("Billing"),
            {
                "fields": (
                    "bank_account",
                    "vat_id",
                    "billing_address",
                    "billing_address_zip",
                    "billing_address_city",
                    "invoices_due_in_days",
                    "vat_payer",
                )
            },
        ),
        (
            _("Legal"),
            {
                "fields": (
                    "gdpr_file_cs",
                    "gdpr_file_en",
                    "terms_and_conditions_file_cs",
                    "terms_and_conditions_file_en",
                    "gdpr_text_cs",
                    "gdpr_text_en",
                    "terms_and_conditions_text_cs",
                    "terms_and_conditions_text_en",
                )
            },
        ),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ("order", "author", "text_column")
    list_display_links = ("author", "text_column")

    def text_column(self, obj):
        return f"{obj.text[:30]}..." if obj.text else ""

    text_column.short_description = "text"


@admin.register(Counter)
class CounterAdmin(TranslationAdmin):
    save_on_top = True
    list_display = ("ordering", "number", "text", "is_active")
    list_display_links = ("number", "text")
    list_editable = ("is_active",)


@admin.register(Ebook)
class EbookAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ("image_tag", "title", "plan_type")
    search_fields = ("title", "author", "plan_type")
    list_display_links = ("image_tag", "title")

    fields = (
        "title",
        "author",
        "image",
        "file",
        "plan_type",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}"width="70"/>'.format(obj.image.url))

        return ""

    image_tag.short_description = ""


@admin.register(FrequentlyAskedQuestion)
class FAQAdmin(TabbedTranslationAdmin):
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
