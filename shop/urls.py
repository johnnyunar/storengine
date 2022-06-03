from django.urls import path
from django.utils.translation import gettext_lazy as _

from shop import views

app_name = "shop"

urlpatterns = [
    path("add-to-cart/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("services/<int:pk>/enter/1/", views.ServiceOrderStep1.as_view(), name="service_order_step_1"),
    path("services/<int:pk>/enter/2/", views.ServiceOrderStep2.as_view(), name="service_order_step_2"),
    path("products/", views.ProductsView.as_view(), name="products"),
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
