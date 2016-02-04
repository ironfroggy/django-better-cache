import os
import django

SECRET_KEY = "test"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DEBUG = True
ROOT_URLCONF = 'proxley.urls'
INSTALLED_APPS = ( 'bettercache', )

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

BETTERCACHE_LOCAL_POSTCHECK = 120
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
if django.VERSION >= (1, 3):
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

ADMINS = ( )
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
USE_L10N = False
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
    )),
)
TEMPLATE_DIRS = ( os.path.join(PROJECT_ROOT, 'templates'),)
MIDDLEWARE_CLASSES = ( )
SECRET_KEY = "test"
