from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from mails.models import Email, EmailAttachment


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ["subject", "attachment_count"]
    autocomplete_fields = ["attachments"]

    @admin.display(description=_("Attachments"))
    def attachment_count(self, obj):
        return obj.attachments.count() or format_html(
            "<img src='/static/admin/img/icon-no.svg' alt='0'>"
        )


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    exclude = ["user"]
    search_fields = ["name", "file", "file_name"]
