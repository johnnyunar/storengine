from django.conf import settings

from core.models import SiteConfiguration


def global_context(request):
    context = {
        "content_settings": SiteConfiguration.get_solo(),
        "base_url": settings.BASE_URL
    }
    return context
