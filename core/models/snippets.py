from functools import partial
from html import unescape

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import TranslatableMixin, Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail_color_panel.edit_handlers import NativeColorPanel
from wagtail_color_panel.fields import ColorField

from core.utils import user_directory_path
from shop.forms import BillingAddressForm
from shop.models import Product, ProductType

from django.utils.html import strip_tags


@register_snippet
class Button(TranslatableMixin):
    name = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=_("This name shows up in admin only."),
    )
    text = models.CharField(max_length=64, blank=True, default="")
    link = models.CharField(max_length=512, blank=True, default="")
    custom_html = models.TextField(
        blank=True, default="", help_text="This option overwrites the link setting."
    )
    open_in_new_tab = models.BooleanField(default=True)

    color = ColorField(_("Color"), null=True, blank=True)
    text_color = ColorField(_("Text Color"), null=True, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("text"),
        FieldPanel("link"),
        FieldPanel("custom_html"),
        FieldPanel("open_in_new_tab"),
        NativeColorPanel("color"),
        NativeColorPanel("text_color"),
    ]

    def __str__(self):
        return self.name or f"{_('Button')} {self.pk}"

    class Meta:
        verbose_name = _("Button")
        verbose_name_plural = _("Buttons")
        unique_together = [("translation_key", "locale")]

    def render(self):
        target = "_blank" if self.open_in_new_tab else "_self"
        background_color = f"background-color: {self.color}" if self.color else ""
        text_color = f"color: {self.text_color}" if self.text_color else ""
        return format_html(
            f'<a href="{self.link}" target="{target}" class="cta center mb-5" '
            f'style="{background_color}; {text_color}">{self.text}</a>'
        )

    def clean(self):
        super(Button, self).clean()
        if not (self.custom_html or self.link):
            raise ValidationError(
                _("At least custom_html or a link must be specified.")
            )
        elif not (self.link and self.text):
            raise ValidationError(_("Link must be specified with text."))


@register_snippet
class PageSection(index.Indexed, TranslatableMixin, ClusterableModel):
    class SectionTypes(models.TextChoices):
        DEFAULT = "default_section", _("Default Section")
        FAQ = "faq_section", _("FAQ Section")
        CONTACT = "contact_section", _("Contact Section")
        COUNTERS = "counters_section", _("Counters Section")
        TESTIMONIALS = "testimonials_section", _("Testimonials Section")
        PRODUCT_CAROUSEL = "product_carousel_section", _("Product Carousel Section")
        PRODUCT_LIST_SQUARE = "product_list_square", _("Product List (Square Cards)")
        PRODUCT_LIST_TALL = "product_list_tall", _("Product List (Tall Cards)")
        CHECKOUT = "checkout_section", _("Checkout Section")

    created_by = CurrentUserField()

    section_type = models.CharField(
        _("Type"),
        max_length=125,
        choices=SectionTypes.choices,
        default=SectionTypes.DEFAULT,
    )
    name = models.TextField(_("Name"), max_length=128)
    text_color = ColorField(_("Text Color"), blank=True, null=True)
    background_color = ColorField(_("Background Color"), blank=True, null=True)

    text = RichTextField(_("Text"), null=True, blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("This image will show up on the right side of the section."),
        verbose_name=_("Image"),
    )

    button = models.ForeignKey(
        Button,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Button"),
    )

    iframe = models.TextField(
        _("Iframe"),
        null=True,
        blank=True,
        help_text=_(
            "If you need to embed any content in this section, you can paste the <iframe> code here. "
            "Tip: Content size not right? Look for width='XXX' and height='XXX' in the pasted code and change it! "
            "For example, you can use width='100%'."
        ),
    )

    panels = [
        FieldPanel("section_type"),
        FieldPanel("name"),
        MultiFieldPanel(
            [
                FieldPanel("text"),
                FieldPanel("image"),
                FieldPanel("button"),
                FieldPanel("iframe"),
                NativeColorPanel("text_color"),
                NativeColorPanel("background_color"),
            ],
            heading=_("General"),
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                InlinePanel("product_types", label=_("Product Types")),
                InlinePanel("products", label=_("Products")),
            ],
            heading=_("Products"),
            classname="collapsible collapsed",
            help_text=_(
                "Product types have higher priority. If you define both product types AND single products, "
                "only product types will be taken into account."
            ),
        ),
        MultiFieldPanel(
            [
                InlinePanel("testimonials", label=_("Testimonials")),
            ],
            heading=_("Testimonials"),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                InlinePanel("counters", label=_("Counters")),
            ],
            heading=_("Counters"),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                InlinePanel("faqs", label=_("FAQs")),
            ],
            heading=_("FAQs"),
            classname="collapsible collapsed",
        ),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("text", partial_match=True),
        index.SearchField("button", partial_match=True),
    ]

    class Meta:
        unique_together = [("translation_key", "locale")]

    def __str__(self):
        return self.name

    @property
    def faqs(self):
        return FrequentlyAskedQuestion.objects.filter(is_active=True)

    @property
    def billing_form(self):
        return BillingAddressForm()

    def get_template_name(self):
        obj_content_type = ContentType.objects.get_for_model(self)
        app_label = obj_content_type.app_label
        return f"{app_label}/snippets/_{self.section_type}.html"


class ProductPlacement(Orderable, models.Model):
    section = ParentalKey(
        PageSection, on_delete=models.CASCADE, related_name="products"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="+")

    class Meta(Orderable.Meta):
        verbose_name = "Products"
        verbose_name_plural = "Products"

    panels = [
        FieldPanel("product"),
    ]

    def __str__(self):
        return self.section.title + " -> " + self.product.name


class Testimonial(Orderable, models.Model):
    section = ParentalKey(
        PageSection, on_delete=models.CASCADE, related_name="testimonials"
    )
    text = models.TextField()
    author = models.CharField(max_length=64, verbose_name=_("Author"))

    is_active = models.BooleanField(_("Available"), default=True)

    def __str__(self):
        return self.section.title + " -> " + self.author

    class Meta(Orderable.Meta):
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    panels = [
        FieldPanel("text"),
        FieldPanel("author"),
        FieldPanel("is_active"),
    ]


class Counter(Orderable, models.Model):
    section = ParentalKey(
        PageSection, on_delete=models.CASCADE, related_name="counters"
    )
    number = models.CharField(_("Number"), max_length=8, help_text=_("E.g. 420 or 69+"))
    text = models.CharField(
        _("Text"), max_length=32, help_text=_("E.g. Clients or Lectures")
    )

    is_active = models.BooleanField(_("Available"), default=True)

    def __str__(self):
        return self.section.title + " -> " + self.text

    class Meta:
        verbose_name = _("Counter")
        verbose_name_plural = _("Counters")


class FrequentlyAskedQuestion(Orderable, models.Model):
    section = ParentalKey(
        PageSection, on_delete=models.CASCADE, related_name="faqs"
    )
    question = RichTextField(_("Question"))
    answer = RichTextField(_("Answer"))

    is_active = models.BooleanField(_("Available"), default=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Frequently Asked Question")
        verbose_name_plural = _("Frequently Asked Questions")

    def __str__(self):
        return self.section.title + " -> " + unescape(strip_tags(self.question))


class ProductTypePlacement(Orderable, models.Model):
    section = ParentalKey(
        PageSection, on_delete=models.CASCADE, related_name="product_types"
    )
    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name="+"
    )
    split_into_categories = models.BooleanField(
        _("Split Into Categories"),
        default=True,
        help_text=_("Split the displayed products into categories."),
    )

    class Meta(Orderable.Meta):
        verbose_name = "Product Types"
        verbose_name_plural = "Product Types"

    panels = [FieldPanel("product_type"), FieldPanel("split_into_categories")]

    def __str__(self):
        return self.section.name + " -> " + self.product_type.name


@register_snippet
class HeroSection(index.Indexed, TranslatableMixin):
    created_by = CurrentUserField()
    name = models.TextField(_("Name"), max_length=128)
    title = models.CharField(
        _("Hero Title"),
        max_length=64,
        blank=True,
        default="Store Engine",
        help_text=_("This is the big title that shows up in the hero section."),
    )

    subheading = models.CharField(
        _("Hero Subheading"),
        max_length=128,
        blank=True,
        default="",
        help_text=_(
            "This is the text that shows up under the title in the hero section."
        ),
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("This image shows up in the hero section."),
        verbose_name=_("Hero Image"),
    )

    video = models.FileField(
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

    enable_particles = models.BooleanField(_("Enable Particles"), default=False)

    class Meta:
        unique_together = [("translation_key", "locale")]

    panels = [
        FieldPanel("name"),
        FieldPanel("title"),
        FieldPanel("subheading"),
        FieldPanel("image"),
        FieldPanel("video"),
        FieldPanel("enable_particles"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("title", partial_match=True),
        index.SearchField("subheading", partial_match=True),
    ]

    def __str__(self):
        return self.name
