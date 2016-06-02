import os
import sys
from setuptools import setup


setup(
    name='fdjangodog',
    version='0.1.0',
    packages = [
        'fdjangodog',
    ],
    include_package_data = True,
    license = 'BSD',
    description = 'Simple Django middleware for submitting timings and exceptions to Datadog.',
    url='https://github.com/tom-dalton-fanduel/fdjangodog',
    author='Tom Dalton',
    author_email='tom.dalton@fanduel.com',
    install_requires=[
        'datadog==0.12.0',
    ]
)
