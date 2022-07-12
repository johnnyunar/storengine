from django.conf import settings
from wagtail.models import Page, Locale


def global_context(request):
    """This context can be accessed in any template."""
    context = {
        "base_url": settings.BASE_URL,
        "menu_pages": Page.objects.live().in_menu().order_by("title").distinct("title"),
        "locales": Locale.objects.all()
    }
    return context
