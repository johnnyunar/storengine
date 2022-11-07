from django.utils.html import format_html
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
    ModelAdminGroup,
)
from wagtail_localize.modeladmin.options import TranslatableModelAdmin

from shop import admin
from shop.models import (
    Product,
    Order,
    BillingAddress,
    ShippingAddress,
    ProductType,
    Category,
    BillingType,
    GopayPayment,
    Packet,
)


class ProductAdmin(TranslatableModelAdmin):
    model = Product
    menu_icon = "fa-tags"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = admin.ProductAdmin.list_display
    list_filter = admin.ProductAdmin.list_filter
    search_fields = admin.ProductAdmin.search_fields
    form_fields_exclude = ("created_by",)

    def description_tag(self, obj):
        return format_html(f"{obj.description[:30]}...")


class ProductTypeAdmin(TranslatableModelAdmin):
    model = ProductType
    menu_icon = "fa-cube"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    form_fields_exclude = ("created_by",)


class CategoryAdmin(TranslatableModelAdmin):
    model = Category
    menu_icon = "fa-cubes"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    form_fields_exclude = ("created_by",)


class OrderAdmin(ModelAdmin):
    model = Order
    menu_icon = "fa-shopping-basket"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = admin.OrderAdmin.list_display
    search_fields = admin.OrderAdmin.search_fields
    list_export = admin.OrderAdmin.list_display  # TODO: More export fields


class GopayPaymentAdmin(ModelAdmin):
    model = GopayPayment
    menu_icon = "fa-paypal"
    menu_order = 1000
    list_display = (
        "payment_id",
        "payment_status",
        "order_num",
        "created_at",
        "updated_at",
    )
    search_fields = admin.GopayPaymentAdmin.search_fields
    list_export = (
        admin.GopayPaymentAdmin.list_display
    )  # TODO: More export fields

    def order_num(self, instance):
        return instance.payment_data["order_number"]


class BillingAddressAdmin(ModelAdmin):
    model = BillingAddress
    menu_icon = "fa-address-book"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = admin.BillingAddressAdmin.list_display
    search_fields = admin.BillingAddressAdmin.search_fields


class ShippingAddressAdmin(ModelAdmin):
    model = ShippingAddress
    menu_icon = "fa-address-book-o"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = admin.ShippingAddressAdmin.list_display
    search_fields = admin.ShippingAddressAdmin.search_fields


class BillingTypeAdmin(TranslatableModelAdmin):
    model = BillingType
    menu_icon = "fa-credit-card"
    menu_order = 200
    add_to_settings_menu = True
    exclude_from_explorer = False
    inspect_view_enabled = True
    list_display = admin.BillingTypeAdmin.list_display
    search_fields = admin.BillingTypeAdmin.search_fields
    form_fields_exclude = ("created_by",)


class PacketAdmin(ModelAdmin):
    model = Packet
    menu_icon = "fa-archive"
    menu_order = 500
    search_fields = ("packet_id",)
    form_fields_exclude = ("created_by",)
    list_filter = ("status_code", "status_display_name")

    def description_tag(self, obj):
        return format_html(f"{obj.description[:30]}...")


class ShopGroup(ModelAdminGroup):
    menu_label = "Shop"
    menu_icon = "fa-shopping-bag"
    menu_order = 200
    items = (
        ProductAdmin,
        OrderAdmin,
        BillingAddressAdmin,
        ShippingAddressAdmin,
        CategoryAdmin,
        ProductTypeAdmin,
        BillingTypeAdmin,
        GopayPaymentAdmin,
        PacketAdmin
    )


modeladmin_register(ShopGroup)
