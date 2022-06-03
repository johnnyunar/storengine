import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Union

import gopay
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from gopay import Language
from gopay.enums import Currency


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def authenticate_api():
    # TODO: Move to env
    return gopay.payments(
        {
            "goid": settings.GOPAY_GOID,
            "clientId": settings.GOPAY_CLIENT_ID,
            "clientSecret": settings.GOPAY_CLIENT_SECRET,
            "gatewayUrl": settings.GOPAY_URL,
            "isProductionMode": settings.GOPAY_IS_PRODUCTION,
        }
    )


def create_gopay_order(order=None):
    api = authenticate_api()

    response = api.create_payment(
        {
            "payer": {
                "contact": {
                    "first_name": order.billing_address.first_name,
                    "last_name": order.billing_address.last_name,
                    "email": order.billing_address.email,
                    "phone_number": str(order.billing_address.phone),
                    "city": order.billing_address.city,
                    "street": order.billing_address.address1,
                    "postal_code": order.billing_address.zip_code,
                    "country_code": order.billing_address.country.code,
                },
            },
            "amount": json.dumps(
                round(order.total_price.amount * 100), cls=JSONEncoder
            ),
            "currency": Currency.CZECH_CROWNS,
            "order_number": order.order_number,
            "order_description": "",
            "items": [
                {
                    "name": item.name,
                    "amount": json.dumps(
                        round(item.price.amount * 100), cls=JSONEncoder
                    ),
                }
                for item in order.items.all()
            ],
            "additional_params": [
                {"name": "invoicenumber", "value": order.order_number}
            ],
            "callback": {
                "return_url": f"{settings.BASE_URL}/order/{order.order_number}/callback/",
                "notification_url": f"{settings.BASE_URL}/gopay-notify/",
            },
            "lang": Language.CZECH,  # if lang is not specified, then default lang is used
        }
    )
    if response.has_succeed():
        return response.json["gw_url"]

    print(response)
    return reverse_lazy("shop:error")


def get_gopay_payment_details(payment_number) -> dict:
    api = authenticate_api()
    return api.get_status(payment_number).json


def get_gopay_payment_status(payment_number) -> Union[str, None]:
    return get_gopay_payment_details(payment_number).get("state")


def is_gopay_payment_paid(payment_number) -> bool:
    return get_gopay_payment_status(payment_number) == "PAID"


def update_gopay_orders():
    from shop.models import ServiceOrder, ProductOrder
    two_days_ago = timezone.now() - timedelta(days=2)
    filters = {
        "billing_type__name": "card-online",
        "paid": False,
        "created_at__gt": two_days_ago,
    }
    for order in ServiceOrder.objects.filter(**filters):
        order.update_payment_status()
    for order in ProductOrder.objects.filter(**filters):
        order.update_payment_status()
