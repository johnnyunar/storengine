from datetime import timedelta
from functools import partial

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_currentuser.db.models import CurrentUserField
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from djrichtextfield.models import RichTextField
from phonenumber_field.modelfields import PhoneNumberField
from polymorphic.models import PolymorphicModel

from core.models import SiteConfiguration
from core.utils import user_directory_path
from shop.gopay_api import is_gopay_payment_paid
from shop.utils import generate_order_number
from users.models import ShopUser


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
        product_order = self.productorder_set.first()
        service_order = self.productorder_set.first()
        if product_order:
            product_order.is_paid = self.is_paid
            product_order.save()
        if service_order:
            service_order.is_paid = self.is_paid
            service_order.save()
        super(GopayPayment, self).save()

    class Meta:
        verbose_name = _("GoPay Payment")
        verbose_name_plural = _("GoPay Payments")


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

    class Meta:
        abstract = True


class CartProduct(CartItem):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    def save(self, **kwargs):
        self.price.amount = self.product.price.amount * self.amount
        super(CartItem, self).save()

    def __str__(self):
        return f"{self.amount}x {self.product.name}"


class CartService(CartItem):
    service = models.ForeignKey("Service", on_delete=models.CASCADE)

    def save(self, **kwargs):
        self.price.amount = self.service.price.amount * self.amount
        super(CartItem, self).save()

    def __str__(self):
        return f"{self.amount}x {self.service.name}"


class Cart(models.Model):
    created_by = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.CASCADE
    )
    cart_products = models.ManyToManyField("Product", through=CartProduct)
    cart_services = models.ManyToManyField("Service", through=CartService)

    total_price = MoneyField(
        _("Price"),
        max_digits=14,
        decimal_places=2,
        default_currency="CZK",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def add(self, item, amount=1):
        if type(item) is Product:
            CartProduct.objects.create(cart=self, product=item, amount=amount)
        elif type(item) is Service:
            CartService.objects.create(cart=self, service=item, amount=amount)

    def save(self, **kwargs):
        self.total_price.amount = sum(
            [item.price.amount for item in self.cart_items.all()]
        )
        super(Cart, self).save()

    def __str__(self):
        return f"{self.user.username} from {self.created_at}"


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=128)

    is_active = models.BooleanField(_("Available"), default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class BaseProduct(models.Model):
    created_by = CurrentUserField()
    name = models.CharField(_("Name"), max_length=128)

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Category"),
    )

    amount = models.CharField(_("Amount"), max_length=32, blank=True, default="")
    description = RichTextField(_("Description"), blank=True, default="")
    short_description = RichTextField(
        _("Short Description"), max_length=125, blank=True, default=""
    )
    external_url = models.URLField(_("External URL"), blank=True, default="")

    image = models.ImageField(
        _("Image"),
        upload_to=partial(user_directory_path, subdir="product_images"),
        blank=True,
        null=True,
    )

    price = MoneyField(
        _("Price"), max_digits=14, decimal_places=2, default_currency="CZK", null=True
    )

    is_active = models.BooleanField(_("Available"), default=True)

    ordering = models.PositiveIntegerField(
        _("Ordering"), default=0, blank=False, null=False
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("ordering",)
        abstract = True


class Product(BaseProduct):
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ("ordering",)


class Service(BaseProduct):
    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ("ordering",)


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
    company = models.CharField(_("Company"), max_length=200, blank=True, null=True)

    address1 = models.CharField(
        _("Address line 1"),
        max_length=1024,
    )

    address2 = models.CharField(
        _("Address line 2"),
        max_length=1024,
        blank=True,
        null=True,
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

    def __str__(self):
        return self.address1

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


class BillingType(models.Model):
    """Stores a single payment method available at the checkout."""

    created_by = CurrentUserField()
    display_name = models.CharField(
        _("Name"),
        max_length=255,
        help_text=_("Should be human readable, this will be displayed on checkout."),
    )
    name = models.SlugField(_("Slug"), max_length=255, unique=True)
    image = models.ImageField(
        _("Image"),
        upload_to=partial(user_directory_path, subdir="payment_method_images"),
        max_length=300,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(_("Available"))

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    ordering = models.PositiveIntegerField(
        _("Order"), default=0, blank=False, null=False
    )

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ("ordering",)
        verbose_name = _("Billing Type")
        verbose_name_plural = _("Billing Types")


class Order(PolymorphicModel):
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
    newsletter_subscribe = models.BooleanField(_("Newsletter Subscribe"), default=False)
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
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(self.id,),
        )

    full_name.fget.short_description = _("Full Name")

    def __str__(self):
        return self.order_number

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class ProductOrder(Order):
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

    items = models.ManyToManyField(Product, through="OrderProduct")

    def save(self, *args, **kwargs):
        super(ProductOrder, self).save()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product Order")
        verbose_name_plural = _("Product Orders")


class ServiceOrder(Order):
    GENDER_CHOICES = (
        ("male", _("Male")),
        ("female", _("Female")),
        ("other", _("Other / Don't wish to respond")),
    )

    GOAL_CHOICES = (
        ("reduce", _("Reduce")),
        ("gain", _("Gain")),
        ("sustain", _("Sustain")),
    )

    gender = models.CharField(_("Gender"), choices=GENDER_CHOICES, max_length=125)
    age = models.IntegerField(_("Age"))
    goal = models.CharField(_("Goal"), choices=GOAL_CHOICES, max_length=125)

    items = models.ManyToManyField(Service, through="OrderService")

    def save(self, *args, **kwargs):
        super(ServiceOrder, self).save()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Service Order")
        verbose_name_plural = _("Service Orders")


class OrderItem(models.Model):
    quantity = models.IntegerField(_("Quantity"))
    total_price = MoneyField(
        _("Total Price"),
        max_digits=14,
        decimal_places=2,
        default_currency="CZK",
        null=True,
    )
    order = models.Field()

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        abstract = True


class OrderService(OrderItem):
    order = models.ForeignKey(
        ServiceOrder, on_delete=models.CASCADE, verbose_name=_("Order")
    )
    product = models.ForeignKey(
        Service, on_delete=models.CASCADE, verbose_name=_("Service")
    )

    def save(self, *args, **kwargs):
        self.total_price = Money(
            self.product.price.amount * self.quantity, self.product.price.currency
        )
        if self.order.total_price:
            self.order.total_price.amount += self.total_price.amount
        else:
            self.order.total_price = Money(
                self.total_price.amount, self.product.price.currency
            )
        self.order.save()
        super(OrderItem, self).save(*args, **kwargs)

    @property
    def service(self):
        return self.product

    def __str__(self):
        return self.product.name


class OrderProduct(OrderItem):
    order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.total_price.currency = self.product.price.currency
        self.total_price.amount = self.product.price.amount * self.quantity
        self.order.total_price.amount += self.total_price.amount
        self.order.save()
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return self.product.name


class Invoice(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, editable=False, verbose_name=_("Order")
    )
    due_date = models.DateField(_("Due Date"), blank=True)

    def get_absolute_url(self):
        return reverse(
            "shop:invoice_detail", kwargs={"order_number": self.order.order_number}
        )

    def save(self, **kwargs):
        # Generate automatic Due Date
        config = SiteConfiguration.get_solo()
        if not self.due_date:
            self.due_date = self.order.created_at + timedelta(
                days=config.invoices_due_in_days
            )
        super(Invoice, self).save()

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


@receiver(post_save, sender=ServiceOrder)
@receiver(post_save, sender=ProductOrder)
def new_order_post_save(sender, instance, created, **kwargs):
    """Automatically generate a new Invoice record."""
    if created:
        Invoice.objects.create(order=instance)
