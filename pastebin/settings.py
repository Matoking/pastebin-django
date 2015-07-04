"""
Django settings for pastebin project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'correct horse battery staple'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [".pastesite.matoking.com"]

# Limits
# Limit the amount of paste submissions, edits, etc. unregistered guests and registered users
# can do over a specified time period
#
# If the user is registered, user-specific limit is used,
# otherwise the guest-specific limit is used
#
# The limit can be disabled by setting it to -1, which means the amount of actions the user performs
# won't be tracked

# Paste upload limits
MAX_PASTE_UPLOADS_PERIOD = 86400 # 24 hours

MAX_PASTE_UPLOADS_PER_GUEST = 20
MAX_PASTE_UPLOADS_PER_USER = 40

# Paste edit limits
MAX_PASTE_EDITS_PERIOD = 86400 # 24 hours

MAX_PASTE_EDITS_PER_USER = 50

# Comment limits
MAX_COMMENTS_PERIOD = 1800 # 30 minutes

MAX_COMMENTS_PER_USER = 20

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.humanize',
    
    'widget_tweaks', # Allows more fine-grained control of HTML in forms
    'lineage', # Used for navbar template tags
    'debug_toolbar',
    
    'pastebin',
    'home',
    'pastes',
    'users',
    'comments',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    
    # Required by django-lineage
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'cached_auth.Middleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pastebin.middleware.PastebinMiddleware',
)

INTERNAL_IPS = (
    "192.168.1.3"
)

ROOT_URLCONF = 'pastebin.urls'

WSGI_APPLICATION = 'pastebin.wsgi.application'

# Templates

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pastesite_old',
        'USER': 'superman',
        'PASSWORD': 'superpass',
        'HOST': 'localhost',
        'PORT': '', # Default
    }
}

# Cache
CACHES = {
    # 'default' is a Redis server working as a LRU cache (non-persistent)
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "TIMEOUT": 15, # Use a relatively short timeout since a lot of things on the site
                       # can change regularly
    },
    # 'persistent' is a Redis server working as a persistent storage
    "persistent": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6380/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}

# Use Redis as a session cache
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "" # Change this to directory to where all static files should be copied to

STATICFILES_DIRS = ( '%s/../../static/' % os.path.realpath(__file__), )
