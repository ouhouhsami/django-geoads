# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements/install_requires.txt') as reqs:
    install_requires = reqs.read().split('\n')

with open('requirements/dependency_links.txt') as reqs:
    dependency_links = reqs.read().split('\n')

version = __import__('django').get_version()

setup(
    name='django-geoads',
    version=version,
    description='Django app for geolocated ads',
    long_description=readme,
    author='Samuel Goldszmidt',
    author_email='samuel.goldszmidt@gmail.com',
    url='https://github.com/ouhouhsami/django-geoads',
    license=license,
    packages=find_packages(exclude=('docs', )),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    classifiers=['Development Status :: 2 - Pre-Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Utilities']
)
