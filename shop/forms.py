from django import forms

from shop.models import ServiceOrder, BillingAddress


class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        exclude = [
            "billing_address",
            "shipping_address",
            "total_price",
            "item",
            "shipping_type",
            "billing_type",
            "paid",
            "order_number",
            "internal_notification_sent",
            "confirmation_email_sent",
        ]


class BillingAddressForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].initial = "CZ"

    class Meta:
        model = BillingAddress
        exclude = ["full_name"]
