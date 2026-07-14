"""
Django settings for config project.
"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'channels',
    'apps.monitoring.apps.MonitoringConfig',
    'apps.detection.apps.DetectionConfig',
    'apps.deception.apps.DeceptionConfig',
    'apps.api',
    'apps.dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.api.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'config.urls'
ASGI_APPLICATION = 'config.asgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend' / 'dist'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

if os.environ.get("DATABASE_URL"):
    import dj_database_url
    DATABASES = {'default': dj_database_url.config(default=os.environ["DATABASE_URL"])}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'dist']

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'apps.api.permissions.CRDSPermission',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.environ.get('CRDS_ANON_RATE', '60/min'),
        'user': os.environ.get('CRDS_USER_RATE', '300/min'),
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'apps.api.exceptions.crds_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_MINUTES', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_DAYS', '7'))),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'CRDS API',
    'DESCRIPTION': 'Cognitive Ransomware Defense System - Endpoint Detection API',
    'VERSION': '2.0.0',
}

CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173',
).split(',')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')]},
    } if os.environ.get('REDIS_URL') else {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CRDS endpoint detection configuration ---
CRDS_WATCH_PATHS = [
    str(BASE_DIR / "demo_files"),
    *[
        path.strip()
        for path in os.environ.get("CRDS_WATCH_PATHS", "").split(",")
        if path.strip()
    ],
]
CRDS_EXTRA_DRIVES = [
    path.strip()
    for path in os.environ.get("CRDS_EXTRA_DRIVES", "").split(",")
    if path.strip()
]
CRDS_RECURSIVE_MONITORING = os.environ.get("CRDS_RECURSIVE_MONITORING", "true").lower() in {"1", "true", "yes"}
CRDS_FEATURE_WINDOW_SECONDS = float(os.environ.get("CRDS_FEATURE_WINDOW_SECONDS", "20"))
CRDS_THRESHOLD_HIGH = float(os.environ.get("CRDS_THRESHOLD_HIGH", "0.75"))
CRDS_THRESHOLD_MEDIUM = float(os.environ.get("CRDS_THRESHOLD_MEDIUM", "0.5"))
CRDS_SCORE_WEIGHTS = {
    "ai": float(os.environ.get("CRDS_WEIGHT_AI", "0.35")),
    "rules": float(os.environ.get("CRDS_WEIGHT_RULES", "0.30")),
    "honeypot": float(os.environ.get("CRDS_WEIGHT_HONEYPOT", "0.20")),
    "yara": float(os.environ.get("CRDS_WEIGHT_YARA", "0.10")),
    "intel": float(os.environ.get("CRDS_WEIGHT_INTEL", "0.05")),
}
CRDS_RESPONSE = {
    "dry_run": os.environ.get("CRDS_RESPONSE_DRY_RUN", "true").lower() in {"1", "true", "yes"},
    "threshold": float(os.environ.get("CRDS_RESPONSE_THRESHOLD", "0.85")),
    "quarantine_dir": os.environ.get("CRDS_QUARANTINE_DIR", str(BASE_DIR / "quarantine")),
    "actions": {
        "kill_process": os.environ.get("CRDS_RESP_KILL", "false").lower() in {"1", "true", "yes"},
        "suspend_process": os.environ.get("CRDS_RESP_SUSPEND", "false").lower() in {"1", "true", "yes"},
        "quarantine_executable": os.environ.get("CRDS_RESP_QUARANTINE", "true").lower() in {"1", "true", "yes"},
        "block_executable_hash": os.environ.get("CRDS_RESP_BLOCK_HASH", "true").lower() in {"1", "true", "yes"},
        "disconnect_network": os.environ.get("CRDS_RESP_NET_ISOLATE", "false").lower() in {"1", "true", "yes"},
        "protect_remaining_files": os.environ.get("CRDS_RESP_PROTECT", "true").lower() in {"1", "true", "yes"},
        "create_incident_report": True,
        "forensic_log": True,
    },
}

CRDS_PUBLIC_PATHS = {
    '/healthz',
    '/api/schema/',
    '/api/docs/',
    '/api/auth/login/',
    '/api/auth/register/',
}

CRDS_AUTO_START_MONITORING = os.environ.get("CRDS_AUTO_START_MONITORING", "false").lower() in {"1", "true", "yes"}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(BASE_DIR / 'logs' / 'crds.log'),
            'maxBytes': 5_000_000,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'apps': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

(BASE_DIR / 'logs').mkdir(exist_ok=True)
