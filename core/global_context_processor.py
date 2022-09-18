from django.conf import settings
from wagtail.models import Locale

from core.models import SimplePage


def global_context(request):
    """This context can be accessed in any template."""
    pages = SimplePage.objects.live().in_menu().order_by('title', 'menu_order').distinct("title")
    context = {
        "base_url": settings.BASE_URL,
        "menu_pages": SimplePage.objects.filter(id__in=pages).live().in_menu().order_by("menu_order"),
        "locales": Locale.objects.all()
    }
    return context
