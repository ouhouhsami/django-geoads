# Django settings for localized_classified_ads project.
import os
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BYPASS_GEOCODE = False

GEOADS_ASYNC = False

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'tmp/email-messages/'


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

ADMINS = ('admin@geoads.com',)

MANAGERS = ADMINS

DJANGO_MODERATION_MODERATORS = (
    'test@example.com',
)


TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'

# I exclude admin.py files from my coverage
# these files does'nt set anything spectial
COVERAGE_MODULE_EXCLUDES = ['tests$','factories', 'settings$', 'urls$', 'locale$', '__init__', 'django',
                                    'migrations', 'admin']

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'coverage_report')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geoads_db',
        'USER': 'postgres', 
    }
}

GEOCODE = 'nominatim'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'abc'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'tests.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',
    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    'django_filters',
    'django_rq',
    'moderation',
    'customads',
    'geoads',
    'geoads.contrib.moderation', 
)

# specific test setting for coverage information


#SOUTH_TESTS_MIGRATE = False
#SKIP_SOUTH_TESTS = True

# for testing purposes, profile page = home/search page
ADS_PROFILE_URL = '/'
# for testing purposes, profile signup page = home/search page
ADS_PROFILE_SIGNUP = '/'


# QUEUE

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}


if DEBUG:
    for queueConfig in RQ_QUEUES.itervalues():
        queueConfig['ASYNC'] = False
