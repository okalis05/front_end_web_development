import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-local-dev-only")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "portfolio",
    "banking",
    "pipeline",
    "channels",
    "rest_framework",
    "drf_spectacular",
    "store",
    "csp",
    "sentinel",
    "mystics_site",
    "dashboards",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "store.middleware.TenantMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "mse.urls"
WSGI_APPLICATION = "mse.wsgi.application"
ASGI_APPLICATION = "mse.asgi.application"

REDIS_URL = os.getenv("REDIS_URL", "").strip()
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", str(BASE_DIR / "db.sqlite3")),
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "banking.context_processors.banking_ai_flags",
            ],
        },
    },
]
TEMPLATES[0]["APP_DIRS"] = True


LOGIN_URL = "store:login"
LOGIN_REDIRECT_URL = "store:dashboard"
LOGOUT_REDIRECT_URL = "store:login"

STORE_TENANT_COOKIE = "store_org"

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STORE_STRIPE_ENABLED = bool(STRIPE_SECRET_KEY)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
SPECTACULAR_SETTINGS = {
    "TITLE": "MSE Platform API",
    "DESCRIPTION": "Unified API for store + analytics + pipeline services.",
    "VERSION": "1.0.0",
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

PIPELINE_DBT_PROJECT_DIR = os.getenv("PIPELINE_DBT_PROJECT_DIR", str(BASE_DIR / "pipeline" / "dbt_project"))
PIPELINE_DBT_PROFILES_DIR = os.getenv("PIPELINE_DBT_PROFILES_DIR", PIPELINE_DBT_PROJECT_DIR)

PREFECT_API_URL = os.getenv("PREFECT_API_URL", "http://127.0.0.1:4200/api")
PREFECT_API_TOKEN = os.getenv("PREFECT_API_TOKEN", "")
PREFECT_HTTP_TIMEOUT = os.getenv("PREFECT_HTTP_TIMEOUT", "10")

BANKING_AI_ENABLED = True

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

CELERY_BEAT_SCHEDULE = {
    "sentinel-tick-sports": {"task": "sentinel.tick_industry", "schedule": 5.0, "args": ("sports",)},
    "sentinel-tick-mortgage": {"task": "sentinel.tick_industry", "schedule": 5.0, "args": ("mortgage",)},
    "sentinel-tick-retail": {"task": "sentinel.tick_industry", "schedule": 5.0, "args": ("retail",)},
    "sentinel-tick-healthcare": {"task": "sentinel.tick_industry", "schedule": 5.0, "args": ("healthcare",)},
    "refresh_mystics_stats_every_15_min": {"task": "analytics.tasks.refresh_mystics_data", "schedule": 15 * 60},
}

TABLEAU_EMBED_ALLOWED_HOSTS = os.getenv(
    "TABLEAU_EMBED_ALLOWED_HOSTS",
    "public.tableau.com,prod-useast-a.online.tableau.com",
)

TABLEAU_VIEWS = {
    "executive_overview": os.getenv("TABLEAU_VIEW_EXECUTIVE_OVERVIEW", ""),
    "readmissions": os.getenv("TABLEAU_VIEW_READMISSIONS", ""),
    "cost_impact": os.getenv("TABLEAU_VIEW_COST_IMPACT", ""),
    "hospital_profile": os.getenv("TABLEAU_VIEW_HOSPITAL_PROFILE", ""),
}

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# This does NOT block embedding Tableau inside your site (it blocks other sites framing YOU).
# Keeping it is fine.
X_FRAME_OPTIONS = "DENY"

# django-csp >= 4.0 configuration (REQUIRED FORMAT)

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),

        "base-uri": ("'self'",),
        "object-src": ("'none'",),

        # Do NOT allow other sites to iframe YOUR app
        "frame-ancestors": ("'none'",),

        # Allow Tableau runtime
         "script-src": (
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
            "https://public.tableau.com",
            "https://prod-useast-a.online.tableau.com",
            "https://cdn.plot.ly",
        ),


        "style-src": (
            "'self'",
            "'unsafe-inline'",
            "https://public.tableau.com",
            "https://prod-useast-a.online.tableau.com",
            "https://fonts.googleapis.com",
        ),

        "img-src": (
            "'self'",
            "data:",
            "blob:",
            "https:",
        ),

        "font-src": (
            "'self'",
            "data:",
            "https:",
            "https://fonts.gstatic.com",
        ),

        "connect-src": (
            "'self'",
            "https:",
            "ws:",
            "wss:",
        ),

        # 👇 THIS is what allows Tableau embeds to render
        "frame-src": (
            "'self'",
            "https://public.tableau.com",
            "https://prod-useast-a.online.tableau.com",
        ),
    }
}

POWERBI_VIZ_REPORTS = {
    "executive_overview": {
        "title": "Executive Overview",
        "subtitle": "Boardroom snapshot: wins, efficiency, availability, engagement",
        "section_id": "executive_overview",
        "embed_url": "",  # paste Power BI “Publish to web” iframe src URL
    },
    "player_impact": {
        "title": "Player Impact & Asset Value",
        "subtitle": "Who moves outcomes beyond minutes and contracts",
        "section_id": "player_impact",
        "embed_url": "",
    },
    "health_risk": {
        "title": "Health, Availability & Risk",
        "subtitle": "Durability, missed games, and performance drop-offs",
        "section_id": "health_risk",
        "embed_url": "",
    },
    "revenue_fans": {
        "title": "Fan & Revenue Impact",
        "subtitle": "Attendance lift, star effect, and business translation",
        "section_id": "revenue_fans",
        "embed_url": "",
    },
}
