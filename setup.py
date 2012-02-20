#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='bettercache',
    version='0.5.3',
    description = "A suite of better cache tools for Django.",
    license = "MIT",
    author='Calvin Spealman',
    author_email='ironfroggy@gmail.com',
    url='http://github.com/ironfroggy/django-better-cache',
    packages = find_packages(),
    install_requires = [
        'celery >= 2.4.2',
        'httplib2 >= 0.6.0',
    ],
)
