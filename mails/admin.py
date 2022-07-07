from django.contrib import admin

from mails.models import Email, EmailAttachment


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ["subject"]


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    exclude = ["user"]
    search_fields = ["name", "file", "file_name"]
