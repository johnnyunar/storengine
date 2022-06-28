from functools import partial
from html import unescape

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from solo.models import SingletonModel
from wagtail.fields import RichTextField
from wagtail.models import TranslatableMixin

from core.utils import user_directory_path


class Counter(TranslatableMixin):
    number = models.CharField(_("Number"), max_length=8, help_text=_("E.g. 420 or 69+"))
    text = models.CharField(
        _("Text"), max_length=32, help_text=_("E.g. Clients or Lectures")
    )

    is_active = models.BooleanField(_("Available"), default=True)

    def __str__(self):
        return f"{self.number} {self.text}"

    class Meta:
        verbose_name = _("Counter")
        verbose_name_plural = _("Counters")
        unique_together = [("translation_key", "locale")]


class FrequentlyAskedQuestion(TranslatableMixin):
    question = RichTextField(_("Question"))
    answer = RichTextField(_("Answer"))

    is_active = models.BooleanField(_("Available"), default=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Frequently Asked Question")
        verbose_name_plural = _("Frequently Asked Questions")
        unique_together = [("translation_key", "locale")]

    def __str__(self):
        return unescape(strip_tags(self.question))


class QuizRecord(models.Model):
    GENDER_CHOICES = (
        ("male", _("Male")),
        ("female", _("Female")),
        ("other", _("Other / Don't wish to respond"))
    )

    GOAL_CHOICES = (
        ("reduce", _("Reduce")),
        ("gain", _("Gain")),
        ("sustain", _("Sustain"))
    )

    gender = models.CharField(_("Gender"), max_length=32, choices=GENDER_CHOICES)
    age = models.IntegerField(_("Age"))
    goal = models.CharField(_("Goal"), max_length=32, choices=GOAL_CHOICES)
    first_name = models.CharField(_("First Name"), max_length=64)
    email = models.EmailField()

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.email} ({self.created_at})"

    class Meta:
        verbose_name = _("Quiz Record")
        verbose_name_plural = _("Quiz Records")


class SiteConfiguration(SingletonModel):
    """
    Model representing general site configuration
    """

    created_by = CurrentUserField()
    # Notification Bar
    notification_bar_show = models.BooleanField(
        _("Show notification bar"),
        blank=True,
        default=0,
    )
    notification_bar_text = models.CharField(
        _("Notification text"),
        max_length=512,
        blank=True,
        default="",
    )

    hero_video = models.FileField(
        _("Hero Video"),
        upload_to=partial(user_directory_path, subdir="hero_videos"),
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )

    footer_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Footer Image"),
    )

    gdpr_file = models.FileField(
        _("GDPR Document"),
        blank=True,
        null=True,
        upload_to=partial(user_directory_path, subdir="legal_documents"),
        max_length=300,
    )

    terms_and_conditions_file = models.FileField(
        _("Terms And Conditions Document"),
        blank=True,
        null=True,
        upload_to=partial(user_directory_path, subdir="legal_documents"),
        max_length=300,
    )

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = _("Site Configuration")

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if type(field) is models.URLField:
                field_value = self.__getattribute__(field.name)
                if field_value.startswith("http") and not field_value.startswith(
                        "https"
                ):
                    self.__setattr__(
                        field.name,
                        field_value.replace("http", "https"),
                    )

        super(SiteConfiguration, self).save()
