import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from core.utils import is_admin_logged_in
from shop.models import (
    Product,
    ShippingAddress,
    BillingAddress,
    BillingType,
    GopayPayment,
    Category, Order, Invoice, OrderItem,
)


@admin.register(GopayPayment)
class GopayPaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "payment_status", "order_num")
    readonly_fields = (
        "payment_id",
        "payment_status",
        "order_num",
        "pretty_data",
        "created_at",
        "updated_at",
    )

    def pretty_data(self, instance):
        """Function to display pretty version of our data"""

        response = json.dumps(instance.payment_data, sort_keys=True, indent=2)
        response = response[:5000]
        formatter = HtmlFormatter(style="colorful")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        return mark_safe(style + response)

    def order_num(self, instance):
        return instance.payment_data["order_number"]

    order_num.short_description = _("Order Number")
    pretty_data.short_description = _("Payment Data")


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(Product)
class ProductAdmin(TabbedTranslationAdmin):
    list_display = (
        "ordering",
        "name",
        "amount",
        "description_tag",
        "category",
        "price",
        "is_active",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active", "category")
    search_fields = ("name", "description", "price")
    list_display_links = ("name", "description_tag")
    exclude = ("created_by",)

    def description_tag(self, obj):
        return format_html(f"{obj.description[:30]}...")

    description_tag.short_description = _("Description")


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "address1", "city", "zip_code", "country")
    list_display_links = ("full_name", "address1")
    readonly_fields = ("created_by", "created_at", "updated_at")

    search_fields = ("full_name", "address1", "city", "zip_code", "country", "created_by")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BillingAddress)
class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "address1", "city", "zip_code", "country")
    list_display_links = ("full_name", "address1")
    readonly_fields = ("created_by", "created_at", "updated_at")

    search_fields = ("full_name", "address1", "city", "zip_code", "country", "created_by")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BillingType)
class BillingTypeAdmin(TabbedTranslationAdmin):
    list_display = ("image_tag", "display_name", "is_active")
    list_display_links = ("image_tag", "display_name")
    list_filter = ("is_active",)

    readonly_fields = ("created_at", "updated_at")
    exclude = ("created_by",)

    prepopulated_fields = {"name": ("display_name",)}

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}"width="70"/>'.format(obj.image.url))

        return ""

    def has_add_permission(self, request, obj=None):
        return is_admin_logged_in(request)

    def has_change_permission(self, request, obj=None):
        return is_admin_logged_in(request)

    image_tag.short_description = ""


class OrderItemInline(admin.TabularInline):
    readonly_fields = ("image_tag",)
    extra = 0

    model = OrderItem
    fields = (
        "total_price",
        "product",
        "quantity",
    )

    def image_tag(self, obj):
        return format_html('<img src="{}"width="70"/>'.format(obj.product.image.url))

    image_tag.short_description = ""

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "is_paid",
        "order_number",
        "full_name",
        "created_at",
        "billing_type",
        "total_price",
    )
    list_display_links = ("order_number", "created_at")
    list_filter = ("is_paid", "billing_type", "created_at")
    readonly_fields = (
        "order_number",
        "gopay_payment_id",
        "newsletter_subscribe",
        "created_by",
        "confirmation_email_sent",
        "internal_notification_sent",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "order_number",
        "billing_address__first_name",
        "billing_address__last_name",
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("order", "view_on_site_link")
    readonly_fields = ("order",)

    def has_add_permission(self, request):
        return False

    @admin.display(description="")
    def view_on_site_link(self, obj):
        return format_html(f"<a href={obj.get_absolute_url()}>{_('View')}</a>")
