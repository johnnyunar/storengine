"""
Django settings for storengine project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import dj_database_url
import sentry_sdk
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration

import storengine

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
SECRET_KEY = os.environ.get("STORENGINE_SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ENV = os.environ.get("ENV", "PROD").upper()

BASE_URL = os.environ.get("BASE_URL")

ADMINS = (("Jan Unar", "johnny@unar.dev"),)

SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "storengine-dev.herokuapp.com",
    "storengine.herokuapp.com",
]

INTERNAL_IPS = ["127.0.0.1"]

SITE_ID = 1

WAGTAIL_SITE_NAME = "Store Engine"
WAGTAILADMIN_BASE_URL = "/cms/"

# Application definition

INSTALLED_APPS = [
    "users",
    # Development static files serving
    "whitenoise.runserver_nostatic",
    # 3rd party
    # --- wagtail ---
    "wagtail_localize",
    "wagtail_localize.locales",  # This replaces "wagtail.locales"
    "wagtail_localize.modeladmin",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.modeladmin",
    "wagtail.contrib.styleguide",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtailfontawesome",
    "wagtail_color_panel",
    "wagtail",
    "modelcluster",
    "taggit",
    # --- wagtail ---
    # Overriding 3rd party
    "polymorphic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "sorl.thumbnail",
    "formtools",
    "djrichtextfield",
    "solo",
    "django_cleanup.apps.CleanupConfig",
    "djmoney",
    # local
    "core.apps.CoreConfig",
    "shop.apps.ShopConfig",
    "mails.apps.MailsConfig",
    "automations.apps.AutomationsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_currentuser.middleware.ThreadLocalUserMiddleware",
    "django_referrer_policy.middleware.ReferrerPolicyMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

X_FRAME_OPTIONS = "SAMEORIGIN"

REFERRER_POLICY = "origin"

AUTH_USER_MODEL = "users.ShopUser"

ROOT_URLCONF = "storengine.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.global_context_processor.global_context",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "storengine.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
    }
}

# Heroku: Update database configuration from $DATABASE_URL.
db_from_env = dj_database_url.config()
DATABASES["default"].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Prague"
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_FORMAT = "d/m/Y"
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", "English"),
    ("cs", "Czech"),
    ("ar", "Arabic"),
    ("nl", "Dutch"),
    ("de", "German"),
    ("fi", "Finnish"),
    ("fr", "French"),
    ("it", "Italian"),
    ("ja", "Japanese"),
    ("ko", "Korean"),
    ("no", "Norwegian"),
    ("pl", "Polish"),
    ("pt", "Portuguese"),
    ("ru", "Russian"),
    ("es", "Spanish"),
    ("sk", "Slovak"),
    ("sl", "Slovenian"),
    ("sr", "Serbian"),
    ("sv", "Swedish"),
    ("sw", "Swahili"),
    ("tr", "Turkish"),
    ("uk", "Ukrainian"),
    ("zh", "Chinese"),
]

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

CURRENCIES = ("CZK", "EUR")

WAGTAIL_I18N_ENABLED = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"

THUMBNAIL_QUALITY = 75
THUMBNAIL_PRESERVE_FORMAT = True

# USE AWS S3 to serve media files on production
if ENV != "LOCAL":
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY_ID = os.environ.get("AWS_SECRET_ACCESS_KEY_ID")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
    AWS_S3_REGION_NAME = "eu-central-1"
    AWS_S3_OBJECT_PARAMETERS = {"ContentDisposition": "attachment"}
    AWS_S3_ADDRESSING_STYLE = "virtual"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# LOGGING SETTINGS
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                    "%(asctime)s [%(process)d] [%(levelname)s] "
                    + "pathname=%(pathname)s lineno=%(lineno)s "
                    + "funcname=%(funcName)s %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

WAGTAILEMBEDS_RESPONSIVE_HTML = True

WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {
        "WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea",
        "OPTIONS": {
            "features": [
                "bold",
                "italic",
                "center",
                "h1",
                "h2",
                "h3",
                "h4",
                "ol",
                "ul",
                "link",
                "document-link",
                "image",
                "embed",
                "code",
            ]
        },
    },
}

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SENTRY_DSN = os.environ.get("SENTRY_DSN")
# Sentry
if ENV != "LOCAL":
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        release=f"storengine@{storengine.VERSION}",
        environment=ENV,
    )

# GOOGLE CONFIG
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# GOPAY CONFIG
GOPAY_URL = os.environ.get("GOPAY_URL")
GOPAY_GOID = os.environ.get("GOPAY_GOID")
GOPAY_CLIENT_ID = os.environ.get("GOPAY_CLIENT_ID")
GOPAY_CLIENT_SECRET = os.environ.get("GOPAY_CLIENT_SECRET")
GOPAY_IS_PRODUCTION = ENV == "PROD"

# EMAIL
EMAIL_HOST = "smtp.titan.email"
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_PORT = 465
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_SSL = True

ADMIN_EMAIL = "info@adambuzek.cz"
SUPPORT_EMAIL = "info@adambuzek.cz"
DEFAULT_FROM_EMAIL = ADMIN_EMAIL
SERVER_EMAIL = ADMIN_EMAIL
