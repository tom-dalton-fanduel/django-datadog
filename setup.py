import os
import sys
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='fdjangodog',
    version='0.1.0',
    packages = [
        'fdjangodog',
        'fdjangodog.middleware'
    ],
    include_package_data = True,
    license = 'BSD',
    description = 'Simple Django middleware for submitting timings and exceptions to Datadog.',
    long_description = README,
    author='Tom Dalton',
    author_email='tom.dalton@fanduel.com',
    install_requires=[
        'datadog==0.12.0',
    ]
)
