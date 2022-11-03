from django.utils.translation import gettext_lazy as _
from wagtail.contrib.modeladmin.options import (
    modeladmin_register,
    ModelAdminGroup, ModelAdmin,
)

from automations import admin
from automations.models import Trigger, Automation, EmailAction


class TriggerAdmin(ModelAdmin):
    model = Trigger
    menu_icon = "fa-bolt"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = admin.TriggerAdmin.list_display
    list_filter = admin.TriggerAdmin.list_filter
    search_fields = admin.TriggerAdmin.search_fields
    form_fields_exclude = ("created_by",)


class ActionAdmin(ModelAdmin):
    model = EmailAction
    menu_icon = "fa-angle-right"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = admin.EmailActionAdmin.list_display
    list_filter = admin.EmailActionAdmin.list_filter
    search_fields = admin.EmailActionAdmin.search_fields
    form_fields_exclude = ("created_by",)


class AutomationAdmin(ModelAdmin):
    model = Automation
    menu_icon = "fa-angle-double-right"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = admin.AutomationAdmin.list_display
    list_filter = admin.AutomationAdmin.list_filter
    search_fields = admin.AutomationAdmin.search_fields
    form_fields_exclude = ("created_by",)


class AutomationsGroup(ModelAdminGroup):
    menu_label = _("Automations")
    menu_icon = "fa-bolt"
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (
        TriggerAdmin,
        ActionAdmin,
        AutomationAdmin,
    )


modeladmin_register(AutomationsGroup)
