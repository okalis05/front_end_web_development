import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-e$l7^qljr1%k$%w1*-yf+dax+3p6%)x8u0wkwlu&og4(i-xfb="

DEBUG = True

ALLOWED_HOSTS: list[str] = []


# External API keys
BALLDONTLIE_API_KEY = "9b7c6197-4fa2-4b6e-8a8c-937377bfea57"
BADL_KEY = ""  # optional WNBA BallDontLie key, if required
API_KEY = os.getenv("BALLDONTLIE_API_KEY")

WNBA_API_BASE_URL = "https://api.sportsdata.io/v3/wnba/stats/json"
WNBA_API_KEY = "YOUR_API_KEY_HERE"
MYSTICS_TEAM_ID = 13  # reserved if you use SportsData later

# in TEMPLATES[0]["OPTIONS"]["context_processors"]
"store.context_processors.store_context",

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Store API",
    "DESCRIPTION": "SaaS store API (products, orders, membership).",
    "VERSION": "1.0.0",
}
LOGIN_URL = "/store/login"
LOGIN_REDIRECT_URL = "/store/"
LOGOUT_REDIRECT_URL = "/store/"

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
# Application definition

INSTALLED_APPS = [
    "portfolio",
    "analytics",
    "playground",
    "pipeline",
    "banking",
    "store",
    "rest_framework",
    "drf_spectacular",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mse.urls"



WSGI_APPLICATION = "mse.wsgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",  # global templates folder
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # Needed for navbar cart count, categories, etc.
                "store.context_processors.current_tenant",
            ],
        },
    },
]


# Password validation

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",  # optional global static
]

STATIC_ROOT = BASE_DIR / "staticfiles"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Celery

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

CELERY_BEAT_SCHEDULE = {
    "refresh_mystics_stats_every_15_min": {
        "task": "analytics.tasks.refresh_mystics_data",
        "schedule": 15 * 60,  # every 15 minutes
    },
}


# OpenAI (for future AI features)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
