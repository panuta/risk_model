from .base import *


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

ALLOWED_HOSTS = ['*']


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
SECRET_KEY = env('DJANGO_SECRET_KEY', default='THIS_IS_DUMMY_SECRET_KEY')


# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.console.EmailBackend')


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}


# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'


# Django Debug Toolbar
# ------------------------------------------------------------------------------

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ('debug_toolbar', )

INTERNAL_IPS = ['127.0.0.1', ]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
    # 'SHOW_TOOLBAR_CALLBACK': lambda r: False,
}


# Django Sass Processor
# ----------------------------------------------------------------------------
INSTALLED_APPS += ('sass_processor', )
STATICFILES_FINDERS += ('sass_processor.finders.CssFinder', )


# CUSTOM CONFIGURATION
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------

try:
    from .develop_local import *
except ImportError:
    pass
