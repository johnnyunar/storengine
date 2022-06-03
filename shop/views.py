import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView

from shop.gopay_api import (
    create_gopay_order,
    get_gopay_payment_details,
)
from shop.models import (
    Service,
    Product,
    ServiceOrder,
    BillingAddress,
    Cart,
    OrderService,
    BillingType,
    GopayPayment, Invoice,
)
from shop.utils import clear_service_order_session

logger = logging.getLogger("django")


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
        context["services"] = Service.objects.filter(is_active=True)
        return context


class ServiceOrderStep1(CreateView):
    template_name = "shop/service_order_step_1.html"
    model = ServiceOrder
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
                existing_order = ServiceOrder.objects.get(pk=existing_order)
                initial.update(existing_order.__dict__)
            except ServiceOrder.DoesNotExist:
                del self.request.session["service_order"]

        return initial

    def form_valid(self, form):
        existing_order = self.request.session.get("service_order")
        if existing_order:
            existing_order = ServiceOrder.objects.get(pk=existing_order)
            form.instance = existing_order
            self.object = form.save()
            self.request.session["service_order"] = self.object

        return super().form_valid(form)


class ServiceOrderStep2(CreateView):
    template_name = "shop/service_order_step_2.html"
    model = BillingAddress
    fields = "__all__"

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
        self.request.session["billing_address"] = self.object.pk
        service_order = ServiceOrder.objects.get(
            pk=self.request.session["service_order"]
        )
        service_order.billing_address = self.object
        user = self.request.user if self.request.user.is_authenticated else None
        service_order.created_by = user
        service_order.save()

        clear_service_order_session(self.request)

        if service_order.billing_type.name == "card-online":
            return create_gopay_order(service_order)

        return reverse_lazy("shop:thank_you")

    def form_valid(self, form):
        service_order = ServiceOrder.objects.get(
            pk=self.request.session["service_order"]
        )
        service = Service.objects.get(pk=self.kwargs["pk"])

        existing_billing_address = self.request.session.get("billing_address")
        if existing_billing_address:
            try:
                existing_billing_address = BillingAddress.objects.get(
                    pk=existing_billing_address
                )
                form.instance = existing_billing_address
            except BillingAddress.DoesNotExist:
                del self.request.session["billing_address"]

        self.object = form.save()
        self.request.session["billing_address"] = self.object

        if (
                not service_order.items.exists()
        ):  # Prevent adding more order items on multiple validations
            OrderService.objects.create(
                order=service_order, product=service, quantity=1
            )

        if self.request.POST.get("pay_now"):
            service_order.billing_type = BillingType.objects.get(name="card-online")
            service_order.save()
        elif self.request.POST.get("pay_later"):
            service_order.billing_type = BillingType.objects.get(name="cash")
            service_order.save()

        return super().form_valid(form)


class PaymentCallbackView(View):
    def get(self, request, *args, **kwargs):
        order_number = self.kwargs["order_number"]
        order = ServiceOrder.objects.get(order_number=order_number)
        payment_id = request.GET.get("id")
        if order and payment_id:
            payment_details = get_gopay_payment_details(payment_id)
            gopay_payment = GopayPayment.objects.create(
                payment_id=payment_id,
                payment_status=payment_details["state"],
                payment_data=payment_details,
            )
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


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            user = request.user if request.user.is_authenticated else None
            cart = request.session.get("cart")
            item = request.POST.get("item")
            amount = request.POST.get("amount", 1)

            if not cart:  # Create a new cart if there is no cart in session
                cart = Cart.objects.create(user=user)
                request.session["cart"] = cart

            cart.add(item, amount)
            return JsonResponse({"success": True})

        return JsonResponse(
            status=400,
            data={"success": False, "message": "Invalid request. AJAX required."},
        )


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    slug_url_kwarg = "order_number"
    slug_field = "order__order_number"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().order.user and not request.user.is_staff:
            raise Http404

        return super(InvoiceDetailView, self).get(request, args, kwargs)
