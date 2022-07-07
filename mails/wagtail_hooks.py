from wagtail.contrib.modeladmin.options import (
    modeladmin_register,
    ModelAdminGroup,
    ModelAdmin,
)

from automations import admin
from automations.models import Trigger, Automation, EmailAction
from mails import admin as mails_admin
from mails.models import Email
from mails.models.models import EmailTemplate


class EmailAdmin(ModelAdmin):
    model = Email
    menu_icon = "fa-envelope"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = mails_admin.EmailAdmin.list_display
    list_filter = mails_admin.EmailAdmin.list_filter
    search_fields = mails_admin.EmailAdmin.search_fields
    form_fields_exclude = ("created_by",)


class EmailTemplateAdmin(ModelAdmin):
    model = EmailTemplate
    menu_icon = "fa-envelope-o"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = ("title", "description")
    list_filter = ("title", "description")
    search_fields = ("title", "description")
    form_fields_exclude = ("created_by",)


class EmailsGroup(ModelAdminGroup):
    menu_label = "Emails"
    menu_icon = "fa-envelope"
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (EmailAdmin, EmailTemplateAdmin)


modeladmin_register(EmailsGroup)
