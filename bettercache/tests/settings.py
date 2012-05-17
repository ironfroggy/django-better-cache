import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DEBUG = True
ROOT_URLCONF = 'proxley.urls'
INSTALLED_APPS = ( 'bettercache', )

CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
}

BETTERCACHE_LOCAL_POSTCHECK = 120
DATABASES = {
    'default': {
                'ENGINE': 'sqlite3',
                'NAME': ':memory:',
    }
}
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
