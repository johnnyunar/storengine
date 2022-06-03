from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup

from shop import admin
from shop.models import Product, Order


class ProductAdmin(ModelAdmin):
    model = Product
    menu_icon = "fa-tags"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = admin.ProductAdmin.list_display
    list_filter = admin.ProductAdmin.list_filter
    search_fields = admin.ProductAdmin.search_fields


class OrderAdmin(ModelAdmin):
    model = Order
    menu_icon = "fa-shopping-basket"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = admin.OrderAdmin.list_display
    search_fields = admin.OrderAdmin.search_fields


class ShopGroup(ModelAdminGroup):
    menu_label = 'Shop'
    menu_icon = 'fa-shopping-bag'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (ProductAdmin, OrderAdmin)


modeladmin_register(ShopGroup)
