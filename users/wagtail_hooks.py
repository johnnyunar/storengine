from django.templatetags.static import static
from django.utils.html import format_html
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from users.models import ShopUser


@hooks.register("construct_settings_menu")
def hide_user_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != "users"]


class UserAdmin(ThumbnailMixin, ModelAdmin):
    model = ShopUser
    menu_label = "Shop Users"
    menu_icon = "user"
    add_to_settings_menu = True
    list_display = ("admin_thumb", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser")
    ordering = ("email",)
    form_fields_exclude = ("password",)
    thumb_image_field_name = "avatar"
    thumb_classname = "avatar-thumb"  # this is the default
    thumb_default = static("users/images/default-user.png")
    thumb_col_header_text = ""


modeladmin_register(UserAdmin)
