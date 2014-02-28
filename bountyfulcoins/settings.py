"""
Django settings for bountyfulcoins project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import os.path

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'PLEASE_GENERATE_A_NEW_KEY_FOR_PRODUCTION_PLEASE_THANK_YOU'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

ADMINS = (
    ('Bountyful Coins', 'contact@bountyfulcoins.com'),
)

ALLOWED_HOSTS = []

# Set the Site ID
SITE_ID = 1

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'south',
    'devserver',
    'registration',
    'captcha',

    'bountyfulcoinsapp',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bountyfulcoins.urls'
WSGI_APPLICATION = 'bountyfulcoins.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bountyfulcoinsdb',
        'USER': 'bountyful',
        'PASSWORD': 'bountyful',
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
LOGIN_URL = '/login/'


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
RECAPTCHA_USE_SSL = True
RECAPTCHA_PUBLIC_KEY = '6Ld6Su8SAAAAAEjAGF4Lt3mOzfhK6snc3Ub_SYBt'
RECAPTCHA_PRIVATE_KEY = 'PLEASE_USE_REAL_KEY_IN_PRODUCTION'

# an issue with pydns prevents this from working properly
CHECK_MX = False
CHECK_EMAIL_EXISTS = False

FEATURE_POST_MIN_CHARGE = 0.01594
FEATURE_POST_DAILY_CHARGE = 0.01594

ADDRESSES_LIVE_SYNC = True  # turn this off when running sync in cron
ADDRESSES_SYNC_FREQUENCE = 60 * 5  # five minutes
