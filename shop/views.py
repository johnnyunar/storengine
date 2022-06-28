import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView

from core.models import ControlCenter
from shop.forms import BillingAddressForm
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

logger = logging.getLogger("django")


class ShopRequiredMixin(View):
    def dispatch(self, request, *args, **kwargs):
        shop_enabled = ControlCenter.for_request(request).shop_enabled

        if not shop_enabled:
            raise Http404

        return super().dispatch(request, args, kwargs)


class ProductsView(TemplateView):
    template_name = "shop/products.html"

    def get_context_data(self, **kwargs):
        context = super(ProductsView, self).get_context_data()
        context["products"] = Product.objects.filter(is_active=True)
        return context


class GopayNotifyView(View):
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

        return JsonResponse({"success": False, "message": "Missing Payment ID."})


class ServicesView(TemplateView):
    template_name = "shop/services.html"

    def get_context_data(self, **kwargs):
        context = super(ServicesView, self).get_context_data()
        context["services"] = Product.objects.filter(is_active=True)
        return context


class OrderStep1(CreateView):
    template_name = "shop/service_order_step_1.html"
    model = Order
    fields = ["age", "gender", "goal", "newsletter_subscribe"]

    def get_success_url(self):
        service_pk = self.kwargs["pk"]
        self.request.session["service_order"] = self.object.pk
        return reverse_lazy("shop:service_order_step_2", args=[service_pk])

    def get_initial(self):
        initial = super().get_initial()
        existing_order = self.request.session.get("service_order")
        if existing_order:
            try:
                existing_order = Order.objects.get(pk=existing_order)
                initial.update(existing_order.__dict__)
            except Order.DoesNotExist:
                del self.request.session["service_order"]

        return initial

    def form_valid(self, form):
        existing_order = self.request.session.get("service_order")
        if existing_order:
            existing_order = Order.objects.get(pk=existing_order)
            form.instance = existing_order
            self.object = form.save()
            self.request.session["service_order"] = self.object

        return super().form_valid(form)


class CheckoutView(ShopRequiredMixin, CreateView):
    template_name = "shop/checkout.html"
    model = BillingAddress
    form_class = BillingAddressForm

    def get_initial(self):
        """Returns the initial data to use for forms on this view."""
        print(self.request.session["cart"])

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
        user = self.request.user if self.request.user.is_authenticated else None
        self.object = form.save()
        new_order = Order.objects.create(created_by=user, billing_address=self.object)
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    quantity=item.amount,
                    product=item.product,
                    order=new_order,
                    total_price=item.price,
                )
                for item in Cart.objects.get(
                pk=self.request.session.get(
                    "cart",
                )
            ).cartitem_set.all()
            ]
        )
        self.order = new_order
        self.order.update_total_price()

        if self.request.POST.get("pay_now"):
            new_order.billing_type = BillingType.objects.get(name="card-online")
        elif self.request.POST.get("pay_later"):
            new_order.billing_type = BillingType.objects.get(name="cash")

        new_order.save()

        return super().form_valid(form)


class PaymentCallbackView(View):
    def get(self, request, *args, **kwargs):
        order_number = self.kwargs["order_number"]
        order = Order.objects.get(order_number=order_number)
        payment_id = request.GET.get("id")
        if order and payment_id:
            payment_details = get_gopay_payment_details(payment_id)
            gopay_payment, created = GopayPayment.objects.update_or_create(
                payment_id=payment_id,
                defaults={
                    "payment_status": payment_details["state"],
                    "payment_data": payment_details,
                },
            )
            if created:
                order.gopay_payment = gopay_payment
                order.save()
            if order.is_paid:
                return HttpResponseRedirect(reverse_lazy("shop:thank_you_paid"))
            else:
                return HttpResponseRedirect(reverse_lazy("shop:thank_you_not_paid"))

        logger.info(f"Payment failed - Order: {order_number}, Payment ID: {payment_id}")
        return HttpResponseRedirect(reverse_lazy("shop:error"))


class ThankYouView(TemplateView):
    template_name = "shop/thank_you.html"


class ErrorView(TemplateView):
    template_name = "shop/error.html"


class AddToCartView(ShopRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        cart_pk = request.session.get("cart")
        item_pk = int(request.POST.get("item"))
        amount = int(request.POST.get("amount", 1))

        cart = Cart.objects.filter(pk=cart_pk).first()
        if not cart:  # Create a new cart if there is no cart in session
            cart = Cart.objects.create(created_by=user)
            request.session["cart"] = cart.pk

        item = Product.objects.get(pk=item_pk)
        cart.add(item, amount)
        return render(request, "storengine/includes/_cart.html")


class InvoiceDetailView(ShopRequiredMixin, LoginRequiredMixin, DetailView):
    model = Invoice
    slug_url_kwarg = "order_number"
    slug_field = "order__order_number"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().order.user and not request.user.is_staff:
            raise Http404

        return super(InvoiceDetailView, self).get(request, args, kwargs)
