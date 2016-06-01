import pytest

from django.http import HttpRequest, HttpResponse

from fdjangodog.middleware import FDjangoDogMiddleware


MODULE_UNDER_TEST = "fdjangodog.middleware"


@pytest.fixture
def middleware():
    return FDjangoDogMiddleware()


@pytest.fixture
def processed_request(middleware):
    request = HttpRequest()
    request.path = "/test"
    middleware.process_request(request)
    return request


@pytest.fixture
def statsd_mock(mocker):
    statsd = mocker.patch(MODULE_UNDER_TEST + ".statsd", autospec=True)
    return statsd


def test_process_request(middleware):
    request = HttpRequest()

    middleware.process_request(request)

    assert request._dd_start_time > 0.0


def test_process_response(statsd_mock, middleware, processed_request):
    response = HttpResponse()

    middleware.process_response(processed_request, response)

    assert statsd_mock.histogram.call_count == 1


def test_process_exception(statsd_mock, middleware, processed_request):
    error = Exception()

    middleware.process_exception(processed_request, error)

    assert statsd_mock.histogram.call_count == 1
