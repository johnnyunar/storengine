from functools import partial

from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from djrichtextfield.models import RichTextField
from solo.models import SingletonModel

from core.utils import user_directory_path


class Testimonial(models.Model):
    """
    Testimonials that show up on the homepage
    """

    text = models.TextField()
    author = models.CharField(max_length=64, verbose_name="Autor")
    order = models.PositiveIntegerField(_("Order"), default=0, blank=False, null=False)

    def __str__(self):
        return self.author

    class Meta:
        ordering = ("order",)
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")


class Ebook(models.Model):
    """
    Ebook that can be used all over the app
    """

    PLAN_CHOICES = (
        ("reduce", _("Reduce")),
        ("gain", _("Gain")),
        ("sustain", _("Sustain")),
    )

    created_by = CurrentUserField()

    title = models.CharField(max_length=256, verbose_name=_("Title"))
    author = models.CharField(max_length=64, default="Snap Shop", verbose_name=_("Author"))
    image = models.ImageField(
        verbose_name=_("Image"),
        upload_to=partial(user_directory_path, subdir="ebook_images"),
        blank=True,
        null=True,
    )
    file = models.FileField(
        verbose_name=_("File"),
        upload_to=partial(user_directory_path, subdir="ebook_files"),
        blank=True,
        null=True,
    )

    plan_type = models.CharField(
        _("Plan Type"),
        choices=PLAN_CHOICES,
        unique=True,
        blank=True,
        null=True,
        max_length=64,
    )

    created_at = models.DateTimeField(_("Added At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Ebook")
        verbose_name_plural = _("Ebooks")


class Button(models.Model):
    name = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="This name shows up in admin only.",
    )
    text = models.CharField(max_length=64, blank=True, default="")
    link = models.CharField(max_length=512, blank=True, default="")
    custom_html = models.TextField(
        blank=True, default="", help_text="This option overwrites the link setting."
    )
    open_in_new_tab = models.BooleanField(default=True)

    color = ColorField(default="#0e0e0e")

    def __str__(self):
        return self.name or f"{_('Button')} {self.pk}"

    class Meta:
        verbose_name = _("Button")
        verbose_name_plural = _("Buttons")

    def clean(self):
        super(Button, self).clean()
        if not (self.custom_html or self.link):
            raise ValidationError(
                _("At least custom_html or a link must be specified.")
            )
        elif not (self.link and self.text):
            raise ValidationError(_("Link must be specified with text."))


class Counter(models.Model):
    number = models.CharField(_("Number"), max_length=8, help_text=_("E.g. 420 or 69+"))
    text = models.CharField(
        _("Text"), max_length=32, help_text=_("E.g. Clients or Lectures")
    )

    ordering = models.PositiveIntegerField(
        _("Ordering"), default=0, blank=False, null=False
    )

    is_active = models.BooleanField(_("Available"), default=True)

    def __str__(self):
        return f"{self.number} {self.text}"

    class Meta:
        ordering = ("ordering",)
        verbose_name = _("Counter")
        verbose_name_plural = _("Counters")


class FrequentlyAskedQuestion(models.Model):
    question = RichTextField(_("Question"))
    answer = RichTextField(_("Answer"))

    ordering = models.PositiveIntegerField(
        _("Ordering"), default=0, blank=False, null=False
    )

    is_active = models.BooleanField(_("Available"), default=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        ordering = ("ordering",)
        verbose_name = _("Frequently Asked Question")
        verbose_name_plural = _("Frequently Asked Questions")


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

    # Homepage
    hero_title = models.CharField(
        _("Hero Title"),
        max_length=64,
        blank=True,
        default="Snapshop",
        help_text=_("This is the big title that shows up in the hero section."),
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

    subheading_text = models.CharField(
        _("Hero Subheading"),
        max_length=128,
        blank=True,
        default="",
        help_text=_("This is the text that shows up under the title in the hero section."),
    )

    quiz_heading = models.TextField(_("Quiz Heading"), blank=True, null=True)
    quiz_subheading = models.TextField(_("Quiz Subheading"), blank=True, null=True)

    about_me_text = RichTextField(blank=True, default="")
    about_me_image = models.ImageField(
        _("About Me Section Image"),
        blank=True,
        null=True,
        upload_to=partial(user_directory_path, subdir="about_me_images"),
        max_length=300,
    )

    second_section_text = RichTextField(blank=True, default="")

    cta_button = models.ForeignKey(
        Button,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="CTA Button",
    )

    hero_image = models.ImageField(
        _("Hero Section Image"),
        blank=True,
        null=True,
        upload_to=partial(user_directory_path, subdir="hero_images"),
        max_length=300,
    )

    ebook_text = RichTextField(_("Ebook Text"), blank=True, default="")

    footer_image = models.ImageField(
        _("Footer Section Image"),
        blank=True,
        null=True,
        upload_to=partial(user_directory_path, subdir="footer_images"),
        max_length=300,
    )

    # Contact
    full_name = models.CharField(
        _("Full Name"),
        max_length=64,
        blank=True,
        default="Snap Shop",
    )

    vat_id = models.CharField(
        _("VAT ID"),
        max_length=10,
        blank=True,
        default="",
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=16,
        blank=True,
        default="",
    )

    email = models.EmailField(
        _("Email"),
        blank=True,
        default="",
    )

    instagram_link = models.URLField(max_length=512, blank=True, default="")
    facebook_link = models.URLField(max_length=512, blank=True, default="")
    linkedin_link = models.URLField(max_length=512, blank=True, default="")

    gdpr_text = RichTextField(_("GDPR Text"), blank=True, default="")
    terms_and_conditions_text = RichTextField(
        _("Terms And Conditions Text"), blank=True, default=""
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

    # Billing
    billing_address = models.CharField(_("Billing Address"), blank=True, null=True, max_length=128)
    billing_address_zip = models.CharField(_("ZIP"), blank=True, null=True, max_length=16)
    billing_address_city = models.CharField(_("City"), blank=True, null=True, max_length=64)
    invoices_due_in_days = models.PositiveIntegerField(_("Default Number of Days until Invoice is Due"), default=14)
    bank_account = models.CharField(_("Bank Account"), blank=True, null=True, max_length=64)
    vat_payer = models.BooleanField(_("VAT Payer"), default=False)

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
