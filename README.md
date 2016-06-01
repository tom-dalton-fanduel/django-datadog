# FDjangoDog

A simple Django middleware for submitting timings and exceptions to Datadog.

This project was originally forked from https://github.com/conorbranagan/django-datadog


## Requirements

Tested in python 2.7 and 3.5. Other versions may or may not work!


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
```

Add the Datadog request handler to your middleware in `settings.py`. In order to capture the most accurate timing data,
and to ensure the `success` tag is set correctly, it should be the 'outermost' (e.g. first in the list) middleware.

```python
MIDDLEWARE_CLASSES.insert(0, 'fdjangodog.middleware.FDjangoDogMiddleware')
```


## Usage

Once the middlewhere is installed, you'll start receiving timing data in your Datadog.

- `my_app.request_time.{avg,max,min}`

Note: `my_app` will be replaced by whatever value you give for `DATADOG_APP_NAME`.

This is tagged with:
* `success`: whether an unhandled exception occurred
* `path`: The canonical route/path of the request
* `status_code`: The http response status code (e.g. 200, 503 etc).


## Development

The project using tox:

```
make test
```
