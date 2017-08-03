# FDjangoDog

[![Build Status](https://travis-ci.org/tom-dalton-fanduel/fdjangodog.svg?branch=master)](https://travis-ci.org/tom-dalton-fanduel/fdjangodog)

A simple Django middleware for submitting timings and exceptions to Datadog using DogStatsD.

This project was originally forked from https://github.com/conorbranagan/django-datadog


## Requirements

Python:
* Tested with 2.7, 3.4, 3.5, and 3.6

Django
* Tested with 1.9, 1.10, and 1.11


## Installation

Download the code into your project and install it.

```bash
git clone git://github.com/tom-dalton-fanduel/fdjangodog.git
cd fdjangodog
python setup.py install
```

Add `fdjangodog` to your list of installed apps.

```python
INSTALLED_APPS += ('fdjangodog', )
```

Add the following configuration to your projects' `settings.py` file:

```python
FDJANGODOG_APP_NAME = 'my_app'  # Used as the prefix for all metric names - e.g. this would give 'my_app.request_time'
FDJANGODOG_STATSD_HOST = 'mystatsdhost' # Optional. Use this if your statsd host is not localhost
```

Add the Datadog request handler to your middleware in `settings.py`. In order to capture the most accurate timing data,
and to ensure the tags are set correctly, it should be the 'outermost' (e.g. first in the list) middleware.

```python
MIDDLEWARE_CLASSES.insert(0, 'fdjangodog.middleware.FDjangoDogMiddleware')
```


## Usage

Once the middlewhere is installed, you'll start receiving timing data in your Datadog.

- `my_app.request_time.{avg,max,min}`

Note: `my_app` will be replaced by whatever value you give for `DATADOG_APP_NAME`.

This is tagged with:
* `method`: The HTTP method of the request
* `namespace`: The url namespace in which the matching url rule is found
** See https://docs.djangoproject.com/en/1.9/ref/urlresolvers/#django.core.urlresolvers.ResolverMatch.namespace
* `handler`: The name of the handler for the request - this will be in one of these forms of:
** `url:<url_name>` if the url resolver rule was named ([ResolverMatch.url_name](https://docs.djangoproject.com/en/1.11/ref/urlresolvers/#django.urls.ResolverMatch.url_name))
** `view:<view_name>` if the url resolver rule was not named ([ResolverMatch.view_name](https://docs.djangoproject.com/en/1.11/ref/urlresolvers/#django.urls.ResolverMatch.view_name))
* `status_code`: The http response status code (e.g. 200, 503 etc).
* `exception`: The name of the exception class in the case of an unhandled exception

## Development

Locally, Tox is used to test the project in multiple versions of python.

```
make test
```

Travis CI is also setup to test pull requests in the same way.
