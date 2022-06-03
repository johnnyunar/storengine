import mimetypes

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import ProgrammingError

from core.utils import textify_html
from mails.models import Email
from users.models import ShopUser

try:
    INTERNAL_NOTIFICATIONS_MAILING_LIST = list(
        ShopUser.objects.filter(
            is_staff=True, send_internal_notifications=True
        ).values_list("email", flat=True)
    )
except ProgrammingError:
    INTERNAL_NOTIFICATIONS_MAILING_LIST = []


def send_notification(
        email: Email = None, recipients: list = None, subject: str = None, body: str = None
):
    if type(recipients) is str:
        recipients = [recipients]  # Convert to list for Django Emails
    if email:
        text_body = textify_html(email.body)
        msg = EmailMultiAlternatives(
            email.subject,
            text_body,
            settings.ADMIN_EMAIL,
            bcc=recipients,
            reply_to=["no-reply@adambuzek.cz"],
            attachments=[
                (attachment.file_name, attachment.file.read(), mimetypes.guess_type(attachment.file.name)[0])
                for attachment in email.attachments.all()
            ],
        )
        msg.attach_alternative(email.body, "text/html")
        msg.send()
    elif subject and body:
        EmailMultiAlternatives(
            subject,
            body,
            settings.ADMIN_EMAIL,
            bcc=recipients,
            reply_to=["no-reply@adambuzek.cz"],
        ).send()

    return True  # TODO: return message status


def send_internal_notification(
        email: Email = None, subject: str = None, body: str = None
):
    return send_notification(
        email=email,
        recipients=INTERNAL_NOTIFICATIONS_MAILING_LIST,
        subject=subject,
        body=body,
    )
