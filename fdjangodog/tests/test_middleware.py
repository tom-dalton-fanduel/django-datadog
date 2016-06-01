import pytest

from django.http import HttpRequest, HttpResponse, Http404

from fdjangodog.middleware import FDjangoDogMiddleware


MODULE_UNDER_TEST = "fdjangodog.middleware"


@pytest.fixture
def middleware():
    return FDjangoDogMiddleware()


@pytest.fixture
def unprocessed_request():
    request = HttpRequest()
    request.path = "/test"
    return request


@pytest.fixture
def processed_request(unprocessed_request, middleware):
    middleware.process_request(unprocessed_request)
    return unprocessed_request


@pytest.fixture
def response():
    return HttpResponse()


@pytest.fixture
def unhandled_error():
    return Exception()


@pytest.fixture
def statsd_mock(mocker):
    statsd = mocker.patch(MODULE_UNDER_TEST + ".statsd", autospec=True)
    return statsd


def test_process_request(processed_request):
    assert processed_request._dd_start_time > 0.0


def test_process_response(statsd_mock, middleware, processed_request, response):
    new_response = middleware.process_response(processed_request, response)

    assert new_response is response
    assert statsd_mock.histogram.call_count == 1


def test_process_response_ignores_unprocessed_request(statsd_mock, middleware, unprocessed_request, response):
    new_response = middleware.process_response(processed_request, response)

    assert new_response is response
    assert statsd_mock.histogram.call_count == 0


def test_process_exception(statsd_mock, middleware, processed_request, unhandled_error):
    middleware.process_exception(processed_request, unhandled_error)
    assert statsd_mock.histogram.call_count == 1


def test_process_exception_ignores_unprocessed_request(statsd_mock, middleware, unprocessed_request, unhandled_error):
    middleware.process_exception(unprocessed_request, unhandled_error)
    assert statsd_mock.histogram.call_count == 0


def test_process_exception_ignores_404(statsd_mock, middleware, processed_request):
    middleware.process_exception(processed_request, Http404())
    assert statsd_mock.histogram.call_count == 0
