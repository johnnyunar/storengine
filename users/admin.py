from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import ShopUserChangeForm, ShopUserCreationForm
from .models import ShopUser, CookiesPreferences

admin.site.register(CookiesPreferences)


@admin.register(ShopUser)
class ShopUserAdmin(UserAdmin):
    add_form = ShopUserCreationForm
    form = ShopUserChangeForm
    model = ShopUser
    list_display = (
        "avatar_tag",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "send_internal_notifications",
    )
    list_display_links = ("avatar_tag", "email")
    list_filter = (
        "is_staff",
        "is_active",
    )
    readonly_fields = (
        "important_cookies",
        "analytic_cookies",
        "marketing_cookies",
        "cookies_updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "newsletter_subscribe",
                    "send_internal_notifications",
                    "avatar",
                    "password",
                )
            },
        ),
        (_("Permissions"), {"fields": ("is_staff", "is_active", "is_superuser")}),
        (
            "Cookies",
            {
                "fields": (
                    "important_cookies",
                    "analytic_cookies",
                    "marketing_cookies",
                    "cookies_updated_at",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

    def avatar_tag(self, obj):
        return format_html('<img src="{}"width="30"/>'.format(obj.avatar.url))

    def important_cookies(self, obj):
        return obj.cookies_preferences.important_cookies_accepted.astimezone(
            timezone.get_current_timezone()
        ).strftime("%d. %m. %Y %H:%M:%S")

    important_cookies.short_description = _("Important Cookies")

    def analytic_cookies(self, obj):
        return obj.cookies_preferences.analytic_cookies_accepted.astimezone(
            timezone.get_current_timezone()
        ).strftime("%d. %m. %Y %H:%M:%S")

    analytic_cookies.short_description = _("Analytic Cookies")

    def marketing_cookies(self, obj):
        return obj.cookies_preferences.marketing_cookies_accepted.astimezone(
            timezone.get_current_timezone()
        ).strftime("%d. %m. %Y %H:%M:%S")

    marketing_cookies.short_description = _("Marketing Cookies")

    def cookies_updated_at(self, obj):
        return obj.cookies_preferences.updated_at.astimezone(
            timezone.get_current_timezone()
        ).strftime("%d. %m. %Y %H:%M:%S")

    cookies_updated_at.short_description = _("Cookies Updated")

    avatar_tag.short_description = "avatar"
