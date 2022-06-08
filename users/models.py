from functools import partial

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.users.models import UserProfile

from core.utils import user_directory_path
from .managers import CustomUserManager


class CookiesPreferences(models.Model):
    important_cookies_accepted = models.DateTimeField(_("Important Cookies Accepted"))
    analytic_cookies_accepted = models.DateTimeField(_("Analytic Cookies Accepted"))
    marketing_cookies_accepted = models.DateTimeField(_("Marketing Cookies Accepted"))

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Cookies Preferences")
        verbose_name_plural = _("Cookies Preferences")


class ShopUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email"), unique=True)
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)

    avatar = models.ImageField(
        _("Avatar"),
        upload_to=partial(user_directory_path, subdir="avatar_images"),
        blank=True,
        null=True,
        default="accounts/default-user.png",
    )

    newsletter_subscribe = models.BooleanField(
        _("Newsletter Subscription"), default=False
    )

    send_internal_notifications = models.BooleanField(
        _("Send Internal Messages"),
        help_text=_("E.g. New orders notifications."),
        default=False,
    )

    cookies_preferences = models.OneToOneField(
        CookiesPreferences,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        editable=False,
        verbose_name=_("Cookies Preferences"),
    )

    is_staff = models.BooleanField(_("Is Staff"), default=False)
    is_active = models.BooleanField(_("Is Active"), default=True)
    date_joined = models.DateTimeField(_("Date Joined"), default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    panels = (
        FieldPanel("email"),
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("avatar"),
        FieldPanel("newsletter_subscribe"),
        FieldPanel("send_internal_notifications"),
        FieldPanel("is_staff"),
        FieldPanel("is_active"),
        FieldPanel("date_joined", classname="readonly")
    )

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def profile(self):
        return UserProfile.objects.get(user=self)

    def __str__(self):
        return "%s (%s)" % (self.full_name, self.email)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
