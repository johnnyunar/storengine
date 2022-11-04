import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_currentuser.db.models import CurrentUserField
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from phonenumber_field.modelfields import PhoneNumberField
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
)
from wagtail.admin.widgets import SwitchInput
from wagtail.fields import RichTextField
from wagtail.models import TranslatableMixin, Site, Orderable

from core.panels import ReadOnlyPanel
from shop.gopay_api import is_gopay_payment_paid
from shop.utils import generate_order_number
from users.models import ShopUser

logger = logging.getLogger("django")


class GopayPayment(models.Model):
    payment_id = models.CharField(
        _("Payment ID"), max_length=128, editable=False, unique=True
    )
    payment_status = models.CharField(
        _("Payment Status"), max_length=64, editable=False
    )
    payment_data = models.JSONField(_("Payment Data"), editable=False)
    is_paid = models.BooleanField(_("Paid"), default=False)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return self.payment_id

    def save(self, *args, **kwargs):
        self.is_paid = self.payment_status == "PAID"
        super(GopayPayment, self).save()
        order = self.order_set.first()
        if order:
            order.is_paid = self.is_paid
            order.save()

    class Meta:
        verbose_name = _("GoPay Payment")
        verbose_name_plural = _("GoPay Payments")

    panels = [
        FieldPanel("is_paid", widget=SwitchInput),
        ReadOnlyPanel("payment_id", heading=_("Payment ID")),
        ReadOnlyPanel("payment_status", heading=_("Payment Status")),
        ReadOnlyPanel("payment_data", heading=_("Payment Data")),
        ReadOnlyPanel("created_at", heading=_("Created At")),
        ReadOnlyPanel("updated_at", heading=_("Updated At")),
    ]


class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)

    amount = models.PositiveIntegerField(_("Amount"))
    price = MoneyField(
        _("Price"),
        max_digits=14,
        decimal_places=2,
        default_currency="CZK",
        null=True,
        blank=True,
    )

    # TODO: on_delete handling
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    product_variant = models.ForeignKey(
        "ProductVariant", blank=True, null=True, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def save(self, **kwargs):
        if not self.price:
            self.price = Money(0, self.product.price.currency)
        self.price.amount = self.product.price.amount * self.amount
        super(CartItem, self).save()

    def __str__(self):
        return f"{self.amount}x {self.product.name}"

    class Meta:
        ordering = ("created_at",)


class Cart(models.Model):
    created_by = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def add(self, item, variant, amount=1) -> bool:
        if (variant and not variant.available()) or (
            not variant and item.variants.exists()
        ):
            return False

        try:
            cart_item = CartItem.objects.get(
                cart=self, product=item, product_variant=variant
            )
            new_amount = cart_item.amount + amount
            if new_amount == 0:
                cart_item.delete()
                if not self.items.exists():
                    self.delete()
            else:
                cart_item.amount = new_amount
                cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart=self, product=item, product_variant=variant, amount=amount
            )

        return True

    @property
    def total_price(self):
        items = self.items.all()
        if items:
            return Money(
                sum([item.price.amount for item in items]),
                currency=items.first().price.currency,
            )

        return Money(0)

    @property
    def items(self):
        return self.cartitem_set

    @property
    def must_be_paid_online(self):
        return self.items.filter(product__must_be_paid_online=True).exists()

    def __str__(self):
        return f"{self.created_by.email if self.created_by else 'Anonymous'} from {self.created_at}"


class Category(TranslatableMixin):
    name = models.CharField(_("Name"), max_length=128)

    is_active = models.BooleanField(_("Available"), default=True)

    panels = [FieldPanel("name"), FieldPanel("is_active", widget=SwitchInput)]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        unique_together = [("translation_key", "locale")]


class ProductType(TranslatableMixin):
    name = models.CharField(_("Name"), max_length=128)

    is_active = models.BooleanField(_("Available"), default=True)

    @property
    def products(self):
        return Product.objects.filter(
            is_active=True, product_type=self
        ).order_by("category")

    def __str__(self):
        return self.name

    panels = [FieldPanel("name"), FieldPanel("is_active", widget=SwitchInput)]

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")
        unique_together = [("translation_key", "locale")]


class ProductVariant(Orderable, TranslatableMixin):
    product = ParentalKey(
        "Product", on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(_("Name"), max_length=128)
    variant_id = models.CharField(
        _("Variant ID"), max_length=32, blank=True, null=True
    )
    pcs_in_stock = models.PositiveIntegerField(
        _("Pieces In Stock"),
        null=True,
        blank=True,
    )

    def available(self):
        return self.pcs_in_stock > 0

    class Meta:
        unique_together = [("translation_key", "locale")]
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Product Variants")

    def __str__(self):
        return f"{self.name} ({self.variant_id})"


class Product(TranslatableMixin, ClusterableModel):
    class RecurrenceTypes(models.TextChoices):
        DAILY = "daily", _("Day")
        WEEKLY = "weekly", _("Week")
        MONTHLY = "monthly", _("Month")
        YEARLY = "yearly", _("Year")

    created_by = CurrentUserField()
    name = models.CharField(_("Name"), max_length=128)
    product_id = models.CharField(
        _("Variant ID"), max_length=32, blank=True, null=True, unique=True
    )
    related_products = models.ManyToManyField("self", blank=True)

    product_type = models.ForeignKey(
        ProductType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Product Type"),
    )

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Category"),
    )

    amount = models.CharField(
        _("Amount"),
        max_length=32,
        blank=True,
        default="",
        help_text=_("Just an orientation text, if applicable. E.g. 500g"),
    )
    description = RichTextField(_("Description"), blank=True, default="")
    short_description = RichTextField(
        _("Short Description"), max_length=125, blank=True, default=""
    )
    external_url = models.URLField(
        _("External URL"),
        blank=True,
        default="",
        help_text=_(
            "Is the product for sale on another site? Just paste the product's link right here!"
        ),
    )

    price = MoneyField(
        _("Price"),
        max_digits=14,
        decimal_places=2,
        default_currency="CZK",
        null=True,
    )

    payment_recurrence = models.CharField(
        _("Payment Recurrence"),
        choices=RecurrenceTypes.choices,
        max_length=64,
        null=True,
        blank=True,
    )

    preorder_end_date = models.DateTimeField(
        _("Preorder End Date"),
        null=True,
        blank=True,
        help_text=_(
            "If this product is for preorder, you can set the preorder end date here."
        ),
    )

    variants_name = models.CharField(
        _("Variants Name"),
        max_length=64,
        default="size",
    )

    must_be_paid_online = models.BooleanField(
        _("Product Must Be Paid Online"), default=False
    )

    is_active = models.BooleanField(_("Available"), default=True)

    autocomplete_search_field = "name"

    def autocomplete_label(self):
        return self.name

    def available(self):
        if self.variants.exists():
            return self.variants.filter(pcs_in_stock__gt=0).exists()

        return True

    @property
    def image(self):
        if self.images.exists():
            return self.images.first().image

        return None

    panels = [
        FieldPanel("is_active", widget=SwitchInput),
        FieldPanel("must_be_paid_online", widget=SwitchInput),
        FieldPanel("name"),
        MultiFieldPanel(
            [
                FieldPanel("price"),
                FieldPanel("payment_recurrence"),
            ],
            heading=_("Price"),
        ),
        InlinePanel("images", heading=_("Images")),
        FieldPanel("product_type"),
        FieldPanel("category"),
        FieldPanel("amount"),
        MultiFieldPanel(
            [
                FieldPanel("description", classname="mb-5"),
                FieldPanel("short_description"),
            ],
            heading=_("Description"),
        ),
        FieldPanel("external_url"),
        FieldPanel("preorder_end_date"),
        MultiFieldPanel(
            [
                FieldPanel("variants_name", classname="mb-5"),
                InlinePanel("variants"),
            ],
            heading=_("Variants"),
        ),
        FieldPanel("related_products"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [("translation_key", "locale")]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ("name",)


class ProductImage(Orderable):
    product = ParentalKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Image"),
    )

    panels = [
        FieldPanel("image"),
    ]


class Address(models.Model):
    created_by = models.ForeignKey(
        ShopUser,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        verbose_name=_("User"),
    )

    first_name = models.CharField(
        _("First Name"),
        max_length=1024,
    )

    last_name = models.CharField(
        _("Last Name"),
        max_length=1024,
    )

    email = models.EmailField(_("Email"))
    phone = PhoneNumberField(_("Phone Number"))
    company = models.CharField(
        _("Company"), max_length=200, blank=True, null=True
    )

    address1 = models.CharField(
        _("Street Address"),
        max_length=1024,
    )

    zip_code = models.CharField(
        _("ZIP"),
        max_length=12,
    )

    city = models.CharField(
        _("City"),
        max_length=1024,
    )

    country = CountryField(_("Country"))

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def find_duplicate(self):
        return (
            type(self)
            .objects.filter(
                first_name__iexact=self.first_name,
                last_name__iexact=self.last_name,
                email__iexact=self.email,
                phone__exact=self.phone,
                company__iexact=self.company,
                address1__iexact=self.address1,
                zip_code__exact=self.zip_code,
                city__iexact=self.city,
                country__exact=self.country,
            )
            .exclude(pk=self.pk)
            .first()
        )

    def __str__(self):
        return f"{self.full_name} ({self.email}) - {self.address1}, {self.zip_code} {self.city}"

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")


class ShippingAddress(Address):
    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")


class BillingAddress(Address):
    class Meta:
        verbose_name = _("Billing Address")
        verbose_name_plural = _("Billing Addresses")


class BillingType(TranslatableMixin):
    """Stores a single payment method available at the checkout."""

    created_by = CurrentUserField()
    display_name = models.CharField(
        _("Name"),
        max_length=255,
        help_text=_(
            "Should be human readable, this will be displayed on checkout."
        ),
    )
    name = models.SlugField(_("Code"), max_length=255, unique=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image"),
    )

    is_active = models.BooleanField(_("Available"))

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = _("Billing Type")
        verbose_name_plural = _("Billing Types")
        unique_together = [("translation_key", "locale")]


class BillingAddressBlock(blocks.StructBlock):
    first_name = blocks.CharBlock()
    last_name = blocks.CharBlock()

    class Meta:
        icon = "address"


class Order(ClusterableModel):
    created_by = models.ForeignKey(
        ShopUser,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    total_price = MoneyField(
        _("Total Price"),
        max_digits=14,
        decimal_places=2,
        default_currency="CZK",
        null=True,
    )

    billing_address = models.ForeignKey(
        BillingAddress,
        on_delete=models.CASCADE,
        verbose_name=_("Billing Address"),
        null=True,
    )

    billing_type = models.ForeignKey(
        BillingType,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Billing Type"),
    )
    newsletter_subscribe = models.BooleanField(
        _("Newsletter Subscribe"), default=False
    )
    is_paid = models.BooleanField(_("Paid"), default=False)
    order_number = models.CharField(
        _("Order Number"),
        max_length=25,
        unique=True,
        default=generate_order_number,
    )

    internal_notification_sent = models.BooleanField(
        _("Internal Notification Sent"), default=False
    )
    confirmation_email_sent = models.BooleanField(
        _("Confirmation Email Sent"), default=False
    )

    gopay_payment = models.ForeignKey(
        GopayPayment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("GoPay Payment"),
    )

    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.CASCADE,
        verbose_name=_("Shipping Address"),
        blank=True,
        null=True,
    )
    shipping_type = models.CharField(
        _("Shipping Type"), max_length=300, blank=True, null=True
    )

    post_save_triggered = models.BooleanField(default=False)

    panels = [
        ReadOnlyPanel("order_number", heading=_("Order Number")),
        FieldPanel("is_paid", widget=SwitchInput),
        FieldPanel("total_price"),
        FieldPanel("billing_type"),
        FieldPanel("billing_address"),
        FieldPanel("shipping_address"),
        FieldPanel("shipping_type"),
        ReadOnlyPanel(
            content="gopay_payment",
            heading=_("GoPay Payment"),
        ),
        InlinePanel("items", heading=_("Items")),
    ]

    def update_total_price(self):
        instance_qs = Order.objects.filter(pk=self.pk)

        # Using qs.update() to avoid calling save()
        if self.items.exists():
            instance_qs.update(
                total_price=Money(
                    sum(
                        [item.total_price.amount for item in self.items.all()]
                    ),
                    currency=self.items.first().total_price.currency,
                )
            )
        else:
            instance_qs.update(
                total_price=Money(0, currency=settings.CURRENCIES[0])
            )

        self.refresh_from_db()

    def save(self, *args, **kwargs):
        if self.gopay_payment:
            self.is_paid = self.gopay_payment.is_paid

        super(Order, self).save()

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    @property
    def full_name(self):
        return self.billing_address.full_name if self.billing_address else ""

    @property
    def invoice(self):
        return self.invoice_set.first()

    def update_gopay_payment(self):
        pass

    def update_payment_status(self):
        self.paid = is_gopay_payment_paid(self.gopay_payment_id)
        self.save()

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse(
            "admin:%s_%s_change"
            % (content_type.app_label, content_type.model),
            args=(self.id,),
        )

    full_name.fget.short_description = _("Full Name")

    def __str__(self):
        return self.order_number

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderItem(models.Model):
    quantity = models.IntegerField(_("Quantity"))
    total_price = MoneyField(
        _("Total Price"),
        max_digits=14,
        decimal_places=2,
        default_currency="CZK",
        null=True,
    )
    order = ParentalKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
        blank=False,
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    product_variant = models.ForeignKey(
        "ProductVariant",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Product Variant"),
    )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            current_obj = OrderItem.objects.get(pk=self.pk)
            current_quantity = current_obj.quantity
        else:
            current_quantity = 0

        if current_quantity != self.quantity and self.product_variant:
            quantity_delta = current_quantity - self.quantity
            self.product_variant.pcs_in_stock += quantity_delta
            try:
                # Preventing TransactionManagementError: You can't execute queries until the end of the 'atomic' block
                with transaction.atomic():
                    self.product_variant.save()
            except IntegrityError:
                self.quantity += self.product_variant.pcs_in_stock
                self.product_variant.pcs_in_stock = 0
                self.product_variant.save()

        self.total_price = Money(
            self.product.price.amount * self.quantity,
            self.product.price.currency,
        )

        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")


@receiver(post_save, sender=OrderItem)
def order_item_post_save(sender, instance, **kwargs):
    instance.order.update_total_price()


class Invoice(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        editable=False,
        verbose_name=_("Order"),
    )
    due_date = models.DateField(_("Due Date"), blank=True)

    def get_absolute_url(self):
        return reverse(
            "shop:invoice_detail",
            kwargs={"order_number": self.order.order_number},
        )

    def save(self, **kwargs):
        from core.models import ContactSettings

        # Generate automatic Due Date
        config = ContactSettings.for_site(site=Site.objects.first())
        if not self.due_date:
            self.due_date = self.order.created_at + timedelta(
                days=config.invoices_due_in_days
            )
        super(Invoice, self).save()

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


@receiver(post_save, sender=Order)
def new_order_post_save(sender, instance, created, **kwargs):
    """Automatically generate a new Invoice record."""
    if created:
        Invoice.objects.create(order=instance)
