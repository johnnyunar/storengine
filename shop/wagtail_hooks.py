from html import unescape

from django.utils.html import strip_tags, format_html
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
    ModelAdminGroup,
)
from wagtail_localize.modeladmin.options import TranslatableModelAdmin

from core import admin as core_admin
from core.models import FrequentlyAskedQuestion, Testimonial, Counter
from shop import admin
from shop.models import (
    Product,
    Order,
    BillingAddress,
    ShippingAddress,
    ProductType,
    Category,
)


class ProductAdmin(TranslatableModelAdmin):
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
    form_fields_exclude = ("created_by",)

    def description_tag(self, obj):
        return format_html(f"{obj.description[:30]}...")


class ProductTypeAdmin(TranslatableModelAdmin):
    model = ProductType
    menu_icon = "fa-cube"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    form_fields_exclude = ("created_by",)


class CategoryAdmin(TranslatableModelAdmin):
    model = Category
    menu_icon = "fa-cubes"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    form_fields_exclude = ("created_by",)


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


class BillingAddressAdmin(ModelAdmin):
    model = BillingAddress
    menu_icon = "fa-address-book"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = admin.BillingAddressAdmin.list_display
    search_fields = admin.BillingAddressAdmin.search_fields


class ShippingAddressAdmin(ModelAdmin):
    model = ShippingAddress
    menu_icon = "fa-address-book-o"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = admin.ShippingAddressAdmin.list_display
    search_fields = admin.ShippingAddressAdmin.search_fields


class FAQAdmin(TranslatableModelAdmin):
    model = FrequentlyAskedQuestion
    menu_icon = "fa-question"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    inspect_view_enabled = True
    list_display = core_admin.FAQAdmin.list_display
    search_fields = core_admin.FAQAdmin.search_fields

    def question_tag(self, obj):
        return unescape(strip_tags(obj.question))

    def answer_tag(self, obj):
        return unescape(strip_tags(obj.answer))


class TestimonialAdmin(TranslatableModelAdmin):
    model = Testimonial
    menu_icon = "fa-thumbs-up"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    inspect_view_enabled = True
    list_display = core_admin.TestimonialAdmin.list_display
    search_fields = core_admin.TestimonialAdmin.search_fields

    def text_column(self, obj):
        return f"{obj.text[:30]}..." if obj.text else ""

    text_column.short_description = "text"


class CounterAdmin(TranslatableModelAdmin):
    model = Counter
    menu_icon = "fa-plus-circle"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    inspect_view_enabled = True
    list_display = core_admin.CounterAdmin.list_display
    search_fields = core_admin.CounterAdmin.search_fields


class ShopGroup(ModelAdminGroup):
    menu_label = "Shop"
    menu_icon = "fa-shopping-bag"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (
        ProductAdmin,
        OrderAdmin,
        BillingAddressAdmin,
        ShippingAddressAdmin,
        CategoryAdmin,
        ProductTypeAdmin,
        FAQAdmin,
    )


modeladmin_register(TestimonialAdmin)
modeladmin_register(CounterAdmin)
modeladmin_register(ShopGroup)
