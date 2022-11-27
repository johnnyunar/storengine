from betterforms.multiform import MultiModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from shop.models import BillingAddress, Order, ShippingAddress


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
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
    field_order = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "address1",
        "city",
        "zip_code",
        "company",
        "country",
    )

    phone = PhoneNumberField(
        region="CZ",
        widget=PhoneNumberPrefixWidget(
            attrs={
                "placeholder": _("Phone Number"),
            },
            country_choices=[
                ("CZ", "CZ (+420)"),
            ],
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    if field.required:
                        field.widget = forms.TextInput(
                            attrs={"placeholder": field.label + " *"}
                        )
                    else:
                        field.widget = forms.TextInput(
                            attrs={"placeholder": field.label}
                        )
        self.fields["email"].widget = forms.EmailInput(
            attrs={"placeholder": "Email *"}
        )
        self.fields["country"].initial = "CZ"

    class Meta:
        model = BillingAddress
        exclude = ["full_name"]


class ShippingAddressForm(forms.ModelForm):
    field_order = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "address1",
        "city",
        "zip_code",
        "company",
        "country",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.required = False
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    field.widget = forms.TextInput(
                        attrs={"placeholder": field.label}
                    )
        self.fields["email"].widget = forms.EmailInput(
            attrs={"placeholder": "Email"}
        )
        self.fields["country"].initial = "CZ"

    class Meta:
        model = ShippingAddress
        exclude = ["full_name"]


class AddressMultiForm(MultiModelForm):
    form_classes = {
        "billing_address": BillingAddressForm,
        "shipping_address": ShippingAddressForm,
    }
