from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from automations.models import Automation, Trigger, Action, EmailAction


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger_type", "is_active")


@admin.register(Action)
class ActionAdmin(PolymorphicParentModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name", "action_id")
    base_model = Action
    child_models = (EmailAction,)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(EmailAction)
class EmailActionAdmin(PolymorphicChildModelAdmin):
    list_display = ("name", "email", "recipients", "is_internal_notification", "is_trigger_notification")
    search_fields = ("email__name",)


@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger", "is_active")
