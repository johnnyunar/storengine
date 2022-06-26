from django.urls import path
from django.utils.translation import gettext_lazy as _

from shop import views

app_name = "shop"

urlpatterns = [
    path("add-to-cart/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("order/<str:order_number>/callback/", views.PaymentCallbackView.as_view(), name="order_payment_callback"),
    path("thank-you/", views.ThankYouView.as_view(), name="thank_you"),
    path("thank-you/paid/",
         views.ThankYouView.as_view(extra_context={"description": _("Thank You for your order! It is paid.")}),
         name="thank_you_paid"),
    path("thank-you/not-paid/", views.ThankYouView.as_view(extra_context={"description": _(
        "Thank You for your order! It was not paid, please check your payment status in your email.")}),
         name="thank_you_not_paid"),
    path("error/", views.ErrorView.as_view(), name="error"),
    path("gopay-notify/", views.GopayNotifyView.as_view(), name="gopay_notify"),
    path("invoice/<str:order_number>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
]
