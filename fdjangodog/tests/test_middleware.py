import pytest

from django.http import HttpResponse
from django.test.client import RequestFactory

from fdjangodog.middleware import FDjangoDogMiddleware
from django.http.response import Http404


MODULE_UNDER_TEST = "fdjangodog.middleware"


@pytest.fixture
def middleware():
    return FDjangoDogMiddleware()


@pytest.fixture
def named_request():
    rf = RequestFactory()
    return rf.get('/named_path/')


@pytest.fixture
def unnamed_request():
    rf = RequestFactory()
    return rf.get('/unnamed_path/')


@pytest.fixture
def namespaced_request():
    rf = RequestFactory()
    return rf.get('/namespaced_path/test/')


@pytest.fixture
def processed_request(named_request, middleware):
    middleware.process_request(named_request)
    return named_request


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

    __, kwargs = statsd_mock.histogram.call_args
    assert kwargs['metric'] == 'fdjangodog_app_name.request_time'
    assert kwargs['value'] > 0.0
    assert kwargs['tags'] == ['method:GET', 'handler:url:a_url_name', 'status_code:200']


def test_process_request__unnamed_url(statsd_mock, middleware, unnamed_request, response):
    middleware.process_request(unnamed_request)

    middleware.process_response(unnamed_request, response)

    __, kwargs = statsd_mock.histogram.call_args
    assert 'handler:view:django.views.generic.base.View' in kwargs['tags']


def test_process_request__namedspaced_url(statsd_mock, middleware, namespaced_request, response):
    middleware.process_request(namespaced_request)

    middleware.process_response(namespaced_request, response)

    __, kwargs = statsd_mock.histogram.call_args
    assert 'namespace:a_namespace' in kwargs['tags']
    assert 'handler:url:a_namespaced_url' in kwargs['tags']


def test_process_response__method(statsd_mock, middleware):
    rf = RequestFactory()
    request = rf.post('/named_path/')
    middleware.process_request(request)
    response = HttpResponse()

    middleware.process_response(request, response)

    __, kwargs = statsd_mock.histogram.call_args
    assert 'method:POST' in kwargs['tags']


def test_process_response__status_code(statsd_mock, middleware, processed_request):
    response = HttpResponse(status=302)
    middleware.process_response(processed_request, response)

    __, kwargs = statsd_mock.histogram.call_args

    assert 'status_code:302' in kwargs['tags']


def test_process_response__ignores_unprocessed_request(statsd_mock, middleware, named_request, response):
    middleware.process_response(named_request, response)
    assert statsd_mock.histogram.call_count == 0


def test_process_exception(statsd_mock, middleware, processed_request, unhandled_error):
    middleware.process_exception(processed_request, unhandled_error)

    __, kwargs = statsd_mock.histogram.call_args
    assert kwargs['metric'] == 'fdjangodog_app_name.request_time'
    assert kwargs['value'] > 0.0
    assert kwargs['tags'] == ['method:GET', 'handler:url:a_url_name', 'exception:Exception']


def test_process_exception__ignores_unprocessed_request(statsd_mock, middleware, named_request, unhandled_error):
    middleware.process_exception(named_request, unhandled_error)
    assert statsd_mock.histogram.call_count == 0


def test_process_exception__handles_http_404(statsd_mock, middleware):
    rf = RequestFactory()
    request = rf.get('/this_doesnt_exist/')
    middleware.process_request(request)
    middleware.process_exception(request, Http404())

    __, kwargs = statsd_mock.histogram.call_args
    assert kwargs['tags'] == ['method:GET', 'exception:Http404']
