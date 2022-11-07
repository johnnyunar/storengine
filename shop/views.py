import logging
from gettext import gettext as _

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect, Http404, \
    HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView
from django_htmx.http import trigger_client_event

from core.models import ControlCenter
from shop.api.packeta_api import Packeta
from shop.forms import AddressMultiForm
from shop.gopay_api import (
    create_gopay_order,
    get_gopay_payment_details,
)
from shop.models import (
    Product,
    BillingAddress,
    Cart,
    BillingType,
    GopayPayment,
    Invoice,
    Order,
    OrderItem,
)
from shop.models.models import ProductVariant, ShippingAddress

logger = logging.getLogger("django")


class ShopRequiredMixin(View):
    """
    Mixin that takes care controlling access to Shop-related views.
    Shop features can be disabled/enabled via the ControlCenter setting.
    """

    def dispatch(self, request, *args, **kwargs):
        shop_enabled = ControlCenter.for_request(request).shop_enabled

        if not shop_enabled:
            raise Http404

        return super().dispatch(request, args, kwargs)


class HtmxRequiredMixin(View):
    """
    Mixin that takes care controlling access to HTMX-related views.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.htmx:
            return HttpResponseForbidden()

        return super().dispatch(request, args, kwargs)


class ProductsView(TemplateView):
    template_name = "shop/products.html"

    def get_context_data(self, **kwargs):
        context = super(ProductsView, self).get_context_data()
        context["products"] = Product.objects.filter(is_active=True)
        return context


class GopayNotifyView(View):
    """View listening for GoPay notifications and updating appropriate GopayPayment objects."""

    def get(self, request):
        logger.info(f"Gopay notification received: {str(request.GET)}")
        payment_id = request.GET.get("id")
        if payment_id:
            payment_details = get_gopay_payment_details(payment_id)
            GopayPayment.objects.update_or_create(
                payment_id=payment_id,
                defaults={
                    "payment_status": payment_details["state"],
                    "payment_data": payment_details,
                },
            )
            return JsonResponse({"success": True})

        return JsonResponse(
            {"success": False, "message": "Missing Payment ID."}
        )


class CheckoutView(ShopRequiredMixin, CreateView):
    template_name = "shop/checkout.html"
    form_class = AddressMultiForm

    def get_initial(self):
        """Returns the initial data to use for forms on this view."""
        initial = super().get_initial()

        existing_billing_address = self.request.session.get("billing_address")
        if existing_billing_address:
            existing_billing_address = BillingAddress.objects.get(
                pk=existing_billing_address
            )
            initial.update(existing_billing_address.__dict__)
        else:
            initial["country"] = "CZ"

        return initial

    def get_success_url(self):
        try:
            Cart.objects.get(pk=self.request.session.get("cart")).delete()
        except Cart.DoesNotExist:
            pass
        if self.order.billing_type.name == "card-online":
            return create_gopay_order(self.order)

        return reverse_lazy("shop:thank_you")

    def form_valid(self, form):
        cart = Cart.objects.get(
            pk=self.request.session.get(
                "cart",
            )
        )

        if cart.must_be_paid_online and self.request.POST.get("pay_later"):
            return HttpResponseRedirect(self.request.path)

        user = (
            self.request.user if self.request.user.is_authenticated else None
        )
        billing_address, _created = BillingAddress.objects.get_or_create(
            **form["billing_address"].cleaned_data
        )
        if not form["shipping_address"].cleaned_data["address1"]:
            billing_address_dict = model_to_dict(billing_address)
            billing_address_dict.pop("id")
            billing_address_dict.pop("address_ptr")
            billing_address_dict["created_at"] = billing_address.created_at
            shipping_address, _created = ShippingAddress.objects.get_or_create(
                **billing_address_dict
            )
        else:
            shipping_address, _created = ShippingAddress.objects.get_or_create(
                **form["shipping_address"].cleaned_data
            )
        logger.info("SHIPPING ADDRESS HERE")
        logger.info(billing_address)
        logger.info(shipping_address)
        new_order = Order.objects.create(
            created_by=user,
            billing_address=billing_address,
            shipping_address=shipping_address,
            packeta_point_id=self.request.POST["packeta_point_id"] or None,
            packeta_point_name=self.request.POST["packeta_point_name"] or None,
        )

        for item in cart.cartitem_set.all():
            OrderItem.objects.create(
                quantity=item.amount,
                product=item.product,
                product_variant=item.product_variant,
                order=new_order,
                total_price=item.price,
            )
        self.order = new_order


        if self.request.POST.get("pay_now"):
            new_order.billing_type = BillingType.objects.get(
                name="card-online"
            )
        elif self.request.POST.get("pay_later"):
            new_order.billing_type = BillingType.objects.get(name="cash")

        new_order.save()

        # TODO: Move somewhere else. Maybe introduce checkout_complete signal?
        if new_order.packeta_point_id:
            packeta = Packeta()
            packeta.create_packet_from_order(new_order)

        return HttpResponseRedirect(self.get_success_url())


class PaymentCallbackView(View):
    """
    This view's URL is passed to GoPay payments as a callback url.
    This is the View that users come back to after GoPay payments.
    GoPay includes payment ID in the URL. Using the ID we can check
    the payment status and redirect to appropriate View.
    """

    def get(self, request, *args, **kwargs):
        order_number = self.kwargs["order_number"]
        order = Order.objects.get(order_number=order_number)
        payment_id = request.GET.get("id")
        if order and payment_id:
            payment_details = get_gopay_payment_details(payment_id)
            gopay_payment, _created = GopayPayment.objects.update_or_create(
                payment_id=payment_id,
                defaults={
                    "payment_status": payment_details["state"],
                    "payment_data": payment_details,
                },
            )
            order.gopay_payment = gopay_payment
            order.save()
            if order.is_paid:
                return HttpResponseRedirect(
                    reverse_lazy("shop:thank_you_paid")
                )
            else:
                return HttpResponseRedirect(
                    reverse_lazy("shop:thank_you_not_paid")
                )

        logger.info(
            f"Payment failed - Order: {order_number}, Payment ID: {payment_id if payment_id else None}"
        )
        return HttpResponseRedirect(reverse_lazy("shop:error"))


class ThankYouView(TemplateView):
    template_name = "shop/thank_you.html"


class ErrorView(TemplateView):
    template_name = "shop/error.html"


class AddToCartView(ShopRequiredMixin, View):
    """
    View accepting POST requests with Product PK and amount in body,
    adds the items to session's cart instance and returns rendered HTML cart.

    Amount defaults to 1 if not specified.

    The cart is created if there is no existing one.
    """

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        cart_pk = request.session.get("cart")
        item_pk = int(request.POST.get("item"))
        variant_pk = int(request.POST.get("variant", 0)) or None
        amount = int(request.POST.get("amount", 1))

        cart = Cart.objects.filter(pk=cart_pk).first()
        if not cart:  # Create a new cart if there is no cart in session
            cart = Cart.objects.create(created_by=user)
            request.session["cart"] = cart.pk

        item = Product.objects.get(pk=item_pk)
        if variant_pk:
            variant = ProductVariant.objects.get(pk=variant_pk)
        else:
            variant = None
        item_added = cart.add(item, variant, amount)
        response = render(request, "storengine/includes/_check_mark.html")
        if not item_added:
            response = render(request, "storengine/includes/_cross_mark.html")
        return trigger_client_event(
            response,
            "cartUpdated",
            {},
        )


class LoadCart(ShopRequiredMixin, HtmxRequiredMixin, TemplateView):
    template_name = "storengine/includes/_cart.html"


class InvoiceDetailView(ShopRequiredMixin, LoginRequiredMixin, DetailView):
    model = Invoice
    slug_url_kwarg = "order_number"
    slug_field = "order__order_number"

    def get(self, request, *args, **kwargs):
        if (
                request.user != self.get_object().order.created_by
                and not request.user.is_staff
        ):
            raise Http404

        return super(InvoiceDetailView, self).get(request, args, kwargs)


class LoadOrderSummary(ShopRequiredMixin, HtmxRequiredMixin, TemplateView):
    template_name = "shop/includes/_order_summary.html"


class LoadCartIcon(ShopRequiredMixin, HtmxRequiredMixin, TemplateView):
    template_name = "shop/includes/_cart_icon.html"
