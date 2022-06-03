from django.conf import settings
from django.utils import timezone


def generate_order_number():
    """
    Function to generate a new order number with format 'YYMM00000',
    where 00000 is number of orders in the month
    """
    from shop.models import Order

    year = str(timezone.now().strftime("%y"))
    month = str(timezone.now().strftime("%m"))
    num_orders = Order.objects.filter(created_at__month=timezone.now().month).count()
    orders_this_month = str.zfill(str(num_orders + 1), 5)

    order_number = year + month + orders_this_month

    if settings.ENV == "PROD":
        return order_number

    return settings.ENV + order_number


def clear_service_order_session(request):
    del request.session["service_order"]
    del request.session["billing_address"]
