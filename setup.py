# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='django-geoads',
    version='0.0.1',
    description='django app for geolocated ads',
    long_description=readme,
    author='Samuel Goldszmidt',
    author_email='samuel.goldszmidt@gmail.com',
    url='https://github.com/ouhouhsami/django-geoads',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    zip_safe=False,
    include_package_data=True,
)