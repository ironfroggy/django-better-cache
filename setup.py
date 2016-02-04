#!/usr/bin/env python
from sys import version_info
from setuptools import setup, find_packages

install_requires = ['httplib2']

if version_info < (2, 7):
    install_requires.append('ordereddict')

setup(name='bettercache',
    version='0.7',
    description = "A suite of better cache tools for Django.",
    license = "MIT",
    author='Calvin Spealman, Cox Media Group',
    author_email='ironfroggy@gmail.com, opensource@coxinc.com',
    url='http://github.com/ironfroggy/django-better-cache',
    packages = find_packages(),
    install_requires = install_requires,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
