from django import template
from django.db.models import QuerySet
from wagtail.models import Page, Locale

register = template.Library()


@register.filter
def filter_by_locale(
    pages: QuerySet[Page], language_code: str, default_fallback=True
) -> QuerySet:
    """
    Filter given Pages by given language code.

    :param default_fallback: Return Pages for the default locale in case of empty QS
    :param pages: Page objects to filter
    :param language_code: E.g. "en"
    :return: Filtered QuerySet<Page>
    """
    localized_pages = pages.filter(locale__language_code=language_code)
    if not localized_pages and default_fallback:
        localized_pages = pages.filter(locale=Locale.get_default())

    return localized_pages
