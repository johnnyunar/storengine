from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shop.models import BillingAddress, ShippingAddress


class AddressTypeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Address Type")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "type"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("billing", _("Billing Address")),
            ("shipping", _("Shipping Address")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "billing":
            return BillingAddress.objects.all()
        if self.value() == "shipping":
            return ShippingAddress.objects.all()
