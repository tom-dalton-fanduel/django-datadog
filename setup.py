import os
import sys
from setuptools import setup


setup(
    name='fdjangodog',
    version='0.5.2',
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
        'datadog>=0.16.0',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
