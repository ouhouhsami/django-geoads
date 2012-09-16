"""
python setup.py test

"""
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = 'example_project.settings'
from example_project import settings

settings.TEST_RUNNER = 'django.contrib.gis.tests.GeoDjangoTestSuiteRunner'

print settings

"""
settings.INSTALLED_APPS = (
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
    'geoads',
    'customads',
    'moderation',
)
"""


def main():
    from django.test.utils import get_runner
    print settings.TEST_RUNNER
    test_runner = get_runner(settings)(interactive=False)
    failures = test_runner.run_tests(['customads',])
    sys.exit(failures)


if __name__ == '__main__':
    main()
