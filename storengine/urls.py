"""storengine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView
from wagtailautocomplete.urls.admin import (
    urlpatterns as autocomplete_admin_urls,
)

from core.views import (
    SetCookiesPreferencesView,
)

urlpatterns = [
    re_path(
        r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$",
        ServeView.as_view(),
        name="wagtailimages_serve",
    ),
    path("cms/autocomplete/", include(autocomplete_admin_urls)),
    path("djrichtextfield/", include("djrichtextfield.urls")),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path(
        "set-cookies-preferences/",
        SetCookiesPreferencesView.as_view(),
        name="set_cookies_preferences",
    ),
    path("sitemap.xml", sitemap),
    path("", include("shop.urls")),
    path("", include("users.urls")),
    path("", include(wagtail_urls)),
    # Left here for compatibility reasons before references are removed
    # path("", HomePageView.as_view(), name="home"),
    # path("contact/", ContactView.as_view(), name="contact"),
    # path("faq/", FAQView.as_view(), name="faq"),
    # path("quiz/", QuizView.as_view(), name="quiz"),
    # path("gdpr/", GDPRView.as_view(), name="gdpr"),
    # path(
    #    "terms-and-conditions/",
    #    TermsAndConditionsView.as_view(),
    #    name="terms_and_conditions",
    # ),
]

try:
    from storengine.settings import local_settings

    urlpatterns += static(
        local_settings.MEDIA_URL, document_root=local_settings.MEDIA_ROOT
    )
except ImportError:
    pass
