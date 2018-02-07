import environ


ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('app')

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)

if READ_DOT_ENV_FILE:
    env_file = str(ROOT_DIR.path('.env'))
    env.read_env(env_file)

# WEBSITE
# ------------------------------------------------------------------------------

WEBSITE_NAME = 'Risk Model'
WEBSITE_DOMAIN = 'example.com'  # Not include subdomain
WEBSITE_URL = 'http://www.' + WEBSITE_DOMAIN


# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (

)

# Apps specific for this project go here.
LOCAL_APPS = (
    # 'app.data',
    'app.risk',

)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'app.contrib.sites.migrations'
}


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', False)


# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)


# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
EMAIL_SUBJECT_PREFIX = ''


# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
ADMINS = (
    ("""Administrator""", 'admin@example.com'),
)

MANAGERS = ADMINS


# DATABASE
# ------------------------------------------------------------------------------
# DATABASES = {
#     'default': env.db('DATABASE_URL', default='sqlite:///database.db'),
# }
# DATABASES['default']['ATOMIC_REQUESTS'] = True


DATABASES = {
    'default': {
        'ENGINE': 'zappa_django_utils.db.backends.s3sqlite',
        'NAME': 'database.db',
        'BUCKET': 'riskmodel-sqlite'
    }
}


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

USE_TZ = True


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------

STATIC_ROOT = str(ROOT_DIR('staticfiles'))
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# MEDIA CONFIGURATION
# ----------------------------------------------------------------------------

MEDIA_ROOT = str(APPS_DIR('media'))
MEDIA_URL = '/media/'


# URL Configuration
# ----------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

ADMIN_URL = 'admin/'


# Django Sequences
# ----------------------------------------------------------------------------
INSTALLED_APPS += ('sequences.apps.SequencesConfig', )


# Django Sass Processor
# ----------------------------------------------------------------------------
INSTALLED_APPS += ('sass_processor', )
STATICFILES_FINDERS += ('sass_processor.finders.CssFinder', )


# Zappa
# ----------------------------------------------------------------------------
INSTALLED_APPS += ('zappa_django_utils',)
