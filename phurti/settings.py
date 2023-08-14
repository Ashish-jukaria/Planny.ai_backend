"""
Django settings for phurti project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
from django.utils.translation import ugettext_lazy as _


from shop.constants import RAZORPAY

load_dotenv(find_dotenv())

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DB_URL = os.environ.get("DB_URL_PRODUCTION")  # This url is link to the DB
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
API_KEY_2FACTOR = os.environ.get("API_KEY_2FACTOR")  # Temperory API key
SECRET_KEY = os.environ.get("SECRET_KEY_DJANGO")

if DB_URL:
    DEBUG = True
else:
    DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # vendor
    "rest_framework",
    # 'corsheaders',
    "rest_framework_simplejwt",
    "storages",
    "django_crontab",
    # apps
    # 'phurti',
    "account",
    "contactus",
    "customer",
    "phurti",
    "shop",
    "operations",
    "notifications",
    "payments",
    "dashboard",
    "plan",

]

APPEND_SLASH = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Coresheader middleware
    "corsheaders.middleware.CorsMiddleware",
    # 'phurti.middleware.request_response.RequestLogMiddleware',
    "phurti.middleware.request_filter.OperationsMiddleware",
    # tenant middleware
    "phurti.middleware.tenant_middleware.TenantMiddleware",
    "phurti.middleware.user_middleware.SetAuthUserModelMiddleware",
]

ROOT_URLCONF = "phurti.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "frontend/phurti/build"),
            os.path.join(BASE_DIR, "frontend/theme/build"),
        ],
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

WSGI_APPLICATION = "phurti.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if DB_URL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_URL,
            "PORT": "5432",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

CORS_ORIGIN_ALLOW_ALL = True

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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'frontend/Phurti/build/static'),
# ]

# JWT config
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}

AUTH_USER_MODEL = "account.Profile"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "static/media")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/phurti/build/static"),
]

# For Collecticting static files in static folder and  production server
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# TWILIO AUTH
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

SENDER_SMS = os.environ.get("SENDER_SMS")
INVOICE_LINK = os.environ.get("INVOICE_LINK")

# RAZORPAY AUTH
RAZORPAY_API_KEY = os.environ.get("RAZORPAY_API_KEY")
RAZORPAY_API_SECRET_KEY = os.environ.get("RAZORPAY_API_SECRET_KEY")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET")


# Adding S3 access

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
# Tell django-storages the domain to use to refer to static files.
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")

# Tell the staticfiles app to use S3Boto3 storage when writing the collected static files (when
# you run `collectstatic`).

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# STATICFILES_LOCATION = 'static'
# STATICFILES_STORAGE = 'storage.StaticStorage'

# RAZORPAY KEYS
RAZORPAY_API_KEY = os.environ.get("RAZORPAY_API_KEY")
RAZORPAY_API_SECRET_KEY = os.environ.get("RAZORPAY_API_SECRET_KEY")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET")

# PAYTM KEYS
PAYTM_MERCHANT_ID = os.environ.get("PAYTM_MERCHANT_ID")
PAYTM_MERCHANT_KEY = os.environ.get("PAYTM_MERCHANT_KEY")
PAYTM_WEBSITE = os.environ.get("PAYTM_WEBSITE")
PAYTM_CHANNEL_ID = os.environ.get("PAYTM_CHANNEL_ID")
PAYTM_INDUSTRY_TYPE_ID = os.environ.get("PAYTM_INDUSTRY_TYPE_ID")
PAYTM_HOST = os.environ.get("PAYTM_HOST")

MEDIAFILES_LOCATION = "phurti-cloudfront"
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    DEFAULT_FILE_STORAGE = "storage.MediaStorage"
    # print("Uploading in S3")

AWS_S3_OBJECT_PARAMETERS = {
    "Expires": "Thu, 31 Dec 2099 20:00:00 GMT",
    "CacheControl": "max-age=94608000",
}
DATETIME_FORMAT = "%Y-%m-%d %H:%m"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

PHONES = os.environ.get("PHONES", default="").split(",")
VOICE_PHONES = os.environ.get("VOICE_PHONES", default="").split(",")

# Cron Scheduler
CRONJOBS = [
    ("1 0 * * *", "shop.cron.deactivate_subscription"),
    ("0 23 * * *", "shop.cron.create_subs_order"),
    ("0 20 * * *", "scripts.inventory_tracker.daily_inventory_tracker"),
    (
        "*/5 * * * *",
        "shop.cron.send_reminder",
        ">> /orderscheduler_data/scheduled_job.log",
    ),
    ("0 */6 * * *", "phurti.scripts.out_of_stock_reminder.check_sellable_inventory"),
    ("0 23 * * *", "phurti.scripts.upload_log.upload"),
    ("0 0 * * *", "shop.cron.deactivate_inventory"),
    ("0 6 * * *", "shop.cron.deactivate_inventory"),
]
# Loggers
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "phurti": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "phurti.log",
            "formatter": "timestamp",
        },
        "request_response": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "request_response.log",
            "formatter": "timestamp",
        },
    },
    "loggers": {
        "phurti": {
            "handlers": ["phurti"],
            "level": "DEBUG",
        },
        "request_response": {
            "handlers": ["request_response"],
            "level": "DEBUG",
        },
    },
    "formatters": {
        "timestamp": {
            "format": "{asctime} {levelname} {message}",
            "style": "{",
        },
    },
}

DISCOUNT_SETTINGS = {
    "discount_code_type": "A",
    "maximum_discount": 50,
    "minimum_order_value": 400,
    "apply_type": "cart",
    "value": 50,
    "discount_promotional_enabled": os.environ.get(
        "DISCOUNT_PROMOTIONAL_ENABLED", "false"
    ),
    "maximum_count": os.environ.get("MAXIMUM_COUNT", 0),
    "discount_category": [
        39,
        5,
        60,
        16,
        42,
        1,
        40,
        41,
        19,
        3,
        22,
        25,
        50,
        11,
        26,
        27,
        28,
        29,
        13,
        30,
        14,
        31,
        17,
        12,
        9,
        18,
        32,
        15,
        34,
        35,
        36,
        6,
        21,
        43,
        20,
        37,
        38,
        7,
        45,
        46,
        47,
        48,
        49,
        44,
        56,
        52,
        53,
        54,
        55,
        4,
        51,
        58,
        59,
        57,
        61,
        62,
        2,
        106,
        65,
        66,
        96,
        68,
        69,
        70,
        71,
        79,
        73,
        74,
        75,
        76,
        77,
        78,
        72,
        80,
        63,
        82,
        83,
        119,
        92,
        88,
        89,
        90,
        99,
        116,
        93,
        81,
        95,
        97,
        98,
        94,
        100,
        101,
        104,
        102,
        105,
        64,
        107,
        108,
        109,
        110,
        111,
        112,
        67,
        114,
        115,
        91,
        117,
        118,
        113,
        120,
        103,
        84,
        121,
        122,
        123,
        124,
        125,
        126,
        127,
        10,
        128,
        129,
    ],
}

DELIVERY_CHARGES = {
    "default": 10,
    "variables": [
        {"start_time": "6:0:1", "end_time": "0:59:59", "amount": 10},
        {"start_time": "1:0:0", "end_time": "3:0:0", "amount": 25},
        {"start_time": "3:0:1", "end_time": "6:0:0", "amount": 50},
    ],
}
INVENTORY = {"8": {"0:0:0": 0, "6:0:0": 1}, "5": {"0:0:0": 0, "6:0:0": 0}}

DELIVERY_ALERTS = {
    "inventory_name": "Whitefield",
    "inventory_code": "INV00000003",
    "inventory_id": 8,
    "message": "",
}

OPERATIONAL = True
UNOPERATIONAL_MESSAGE = "We're currently not accepting orders due to high demand."

FCM_API_KEY = os.environ.get("FCM_API_KEY", "")
OTP_SEND = False
MESSAGE_SEND = False


# Payment Mode
# key should be lower
PAYMENT_TOGGLER = {"paytm": True, "razorpay": False}

BYPASS_INV_LOCK = os.environ.get("BYPASS_INV_LOCK", default="").split(",")

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = (
    "https://8213db9509584aa6b9fee8af66ee68b6@o1268819.ingest.sentry.io/6457252"
)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)


COMPANY_URL = os.environ.get("COMPANY_URL")
DEFAULT_TENANT_ID = os.environ.get("DEFAULT_TENANT_ID")