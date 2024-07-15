from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
load_dotenv()
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-0p+86%^jdc*%ub1w9e5)shg^i-c!8&aj8jhd8k8&mjn-pz9=6w"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ['https://achlive-api.vercel.app']
# Application definition

INSTALLED_APPS = [
    #"daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    "accounts",
    "payment",
    "store",
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR/'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

SITE_ID = 1
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "URL":"postgres://default:vX8LF6bMeiHY@ep-restless-unit-98493640-pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb",
        "PRISMA_URL":"postgres://default:vX8LF6bMeiHY@ep-restless-unit-98493640-pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb?pgbouncer=true&connect_timeout=15",
        "URL_NON_POOLING":"postgres://default:vX8LF6bMeiHY@ep-restless-unit-98493640.us-east-1.postgres.vercel-storage.com:5432/verceldb",
        "USER":"default",
        "HOST":"ep-restless-unit-98493640-pooler.us-east-1.postgres.vercel-storage.com",
        "PASSWORD":"vX8LF6bMeiHY",
        "NAME":"verceldb",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True
COINBASE_COMMERCE_API_KEY = '77c13c31-17be-45f4-a9c2-ce12434c7ad4'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = BASE_DIR / "static_root"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Import necessary modules
from google.oauth2 import service_account
# Google Cloud Storage settings
GS_PROJECT_ID = 'uber-clone-first'
GS_BUCKET_NAME = 'godsonic'
# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    'uber-clone-first-c7bdb50d2274.json'
)
# Media files (uploads)
GS_MEDIA_BUCKET_NAME = GS_BUCKET_NAME
MEDIA_URL = f'https://storage.googleapis.com/{GS_MEDIA_BUCKET_NAME}/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = 'accounts.Customer'
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_HOST_USER = "deagusco@gmail.com"
EMAIL_HOST_PASSWORD = "Hsnxt9J1OThfYICB"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
CORS_ALLOW_ALL_ORIGINS = True
DEFAULT_FROM_EMAIL = "support@erblan.com"
#ASGI_APPLICATION = 'core.routing.application'