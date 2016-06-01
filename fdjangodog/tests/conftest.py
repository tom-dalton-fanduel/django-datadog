from django.conf import settings


TEST_SETTINGS = {
    "FDJANGODOG_APP_NAME": "fdjango_app_name",
}


def pytest_configure(config):
    """Setup the django environment for the tests."""

    settings.configure(**TEST_SETTINGS)
