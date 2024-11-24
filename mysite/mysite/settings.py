import os
from pathlib import Path

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent  # Django project dir
BASE_DIR = PROJECT_DIR.parent  # Git root


SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = int(os.getenv("DEBUG", default=0))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", default="").split(" ")

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", default="").split(" ")

INSTALLED_APPS = [
    # Local
    "base.apps.BaseConfig",
    "home",
    "search",
    "blog.apps.BlogConfig",
    "partners.apps.PartnersConfig",
    "locations.apps.LocationsConfig",
    # Wagtail contrib
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.settings",
    "wagtail.contrib.styleguide",
    # Wagtail core
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail_localize",
    "wagtail_localize.locales",
    "wagtail",
    "modelcluster",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Third party
    "debug_toolbar",
    "django_extensions",
    "taggit",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]  # <-- Debug toolbar needs this

SITE_ID = 1

ROOT_URLCONF = "mysite.urls"

# Mailpit
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "127.0.0.1"
EMAIL_PORT = 1025

# Email
DEFAULT_FROM_EMAIL = "'Ventanita' <noreply@ventanita.com.ar>"
DEFAULT_TO_EMAIL = "gurupratap.matharu@gmail.com"
SERVER_EMAIL = "wagtail@ventanita.com.ar"
RECIPIENT_LIST = [
    "gurupratap.matharu@gmail.com",
    "veerplaying@gmail.com",
]

ADMINS = [
    ("Veer", "veerplaying@gmail.com"),
    ("Gurupratap", "gurupratap.matharu@gmail.com"),
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST", default="db"),
        "PORT": 5432,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "es"

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", _("English")),
    ("es", _("Spanish")),
    ("pt", _("Portuguese")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "America/Buenos_Aires"

WAGTAIL_I18N_ENABLED = True

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/staticb/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


MEDIA_URL = "/mediab/"
MEDIA_ROOT = BASE_DIR / "media"

MESSAGE_TAGS = {messages.ERROR: "danger"}

# Wagtail settings

WAGTAIL_SITE_NAME = "Ventanita"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL")

# Pagination
DEFAULT_PER_PAGE = 8

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "wagtail.log",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "WARNING",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
        "formatter": "verbose",
    },
    "loggers": {
        "wagtail": {
            "level": os.getenv("WAGTAIL_LOG_LEVEL", default="INFO"),
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "django": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["file", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = None

if not DEBUG:
    # EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    # EMAIL_HOST = "smtp.mailgun.org"
    # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    # EMAIL_PORT = 587
    # EMAIL_USE_TLS = True

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 31536000

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    X_FRAME_OPTIONS = "DENY"

    # Sentry

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        environment="wagtail",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.1,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
