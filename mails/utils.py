import logging
import mimetypes
from smtplib import SMTPSenderRefused

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import ProgrammingError

from core.utils import textify_html
from mails.models import Email
from users.models import ShopUser

logger = logging.getLogger("django")

try:
    INTERNAL_NOTIFICATIONS_MAILING_LIST = list(
        ShopUser.objects.filter(
            is_staff=True, send_internal_notifications=True
        ).values_list("email", flat=True)
    )
except ProgrammingError:
    INTERNAL_NOTIFICATIONS_MAILING_LIST = []


def send_notification(
    email: Email = None,
    recipients: list = None,
    subject: str = None,
    body: str = None,
) -> bool:
    """
    Sends a notification email.

    :param email: Email object that already includes all email data.
    :param recipients: List of recipients
    :param subject: Provide when used without the Email instance
    :param body: Provide when used without the Email instance
    """
    if type(recipients) is str:
        recipients = [recipients]  # Convert to list for Django Emails
    for recipient in recipients:
        if email:
            text_body = textify_html(email.body)
            msg = EmailMultiAlternatives(
                email.subject,
                text_body,
                settings.ADMIN_EMAIL,
                to=[recipient],
                reply_to=[settings.SUPPORT_EMAIL],
                attachments=[
                    (
                        attachment.file_name,
                        attachment.file.file.read(),
                        mimetypes.guess_type(attachment.file.file.name)[0],
                    )
                    for attachment in email.email_attachments.all()
                ],
            )
            msg.attach_alternative(email.body, "text/html")
            try:
                msg.send()
            except SMTPSenderRefused:
                logger.warning(
                    "SMTP Error while sending notification.", exc_info=True
                )
        elif subject and body:
            try:
                EmailMultiAlternatives(
                    subject,
                    body,
                    settings.ADMIN_EMAIL,
                    to=[recipient],
                    reply_to=[settings.SUPPORT_EMAIL],
                ).send()
            except SMTPSenderRefused:
                logger.warning(
                    "SMTP Error while sending notification.", exc_info=True
                )

    return True  # TODO: return message status


def send_internal_notification(
    email: Email = None, subject: str = None, body: str = None
) -> bool:
    """Same as send_notification(), but automatically sets the recipients to internal addresses."""
    return send_notification(
        email=email,
        recipients=INTERNAL_NOTIFICATIONS_MAILING_LIST,
        subject=subject,
        body=body,
    )
