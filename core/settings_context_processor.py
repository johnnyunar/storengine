from django.conf import settings
from wagtail.models import Page

from core.models import SiteConfiguration


def global_context(request):
    context = {
        "content_settings": SiteConfiguration.get_solo(),
        "base_url": settings.BASE_URL,
        "menu_pages": Page.objects.live().in_menu()
    }
    return context
