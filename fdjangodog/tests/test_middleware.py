import pytest

import django
from django.http.response import Http404, HttpResponse
from django.test.client import RequestFactory

from fdjangodog import middleware


_DJANGO_VERSION = django.__version__.split('.')

if _DJANGO_VERSION[0:2] == ['1', '9']:
    @pytest.fixture
    def fdd_middleware():
        return middleware.FDjangoDogMiddleware()

elif _DJANGO_VERSION[0:2] == ['1', '10'] or _DJANGO_VERSION[0:2] == ['1', '11']:
    @pytest.fixture
    def fdd_middleware(mocker):
        return middleware.FDjangoDogMiddleware(get_response=mocker.Mock())

else:
    pytest.fail("Unsupported django version: ".format(django.__version__))


@pytest.fixture
def named_request():
    rf = RequestFactory()
    return rf.get('/named_path/')


@pytest.fixture
def processed_request(named_request, fdd_middleware):
    fdd_middleware.process_request(named_request)
    return named_request


@pytest.fixture
def response():
    return HttpResponse()


@pytest.fixture
def statsd_mock(mocker):
    return mocker.patch.object(middleware, "statsd", autospec=True)


def test_process_request(processed_request):
    assert processed_request._dd_start_time > 0.0


def test_process_response(statsd_mock, fdd_middleware, processed_request, response):
    new_response = fdd_middleware.process_response(processed_request, response)

    assert new_response is response

    __, kwargs = statsd_mock.histogram.call_args
    assert kwargs['metric'] == 'fdjangodog_app_name.request_time'
    assert kwargs['value'] > 0.0
    assert kwargs['tags'] == ['method:GET', 'handler:url:a_url_name', 'status_code:200']


@pytest.fixture
def unnamed_request():
    rf = RequestFactory()
    return rf.get('/unnamed_path/')


def test_process_request__unnamed_url(statsd_mock, fdd_middleware, unnamed_request, response):
    fdd_middleware.process_request(unnamed_request)

    fdd_middleware.process_response(unnamed_request, response)

    __, kwargs = statsd_mock.histogram.call_args
    assert 'handler:view:django.views.generic.base.View' in kwargs['tags']


@pytest.fixture
def namespaced_request():
    rf = RequestFactory()
    return rf.get('/namespaced_path/test/')


def test_process_request__namedspaced_url(statsd_mock, fdd_middleware, namespaced_request, response):
    fdd_middleware.process_request(namespaced_request)

    fdd_middleware.process_response(namespaced_request, response)

    __, kwargs = statsd_mock.histogram.call_args
    assert 'namespace:a_namespace' in kwargs['tags']
    assert 'handler:url:a_namespaced_url' in kwargs['tags']


def test_process_response__method(statsd_mock, fdd_middleware):
    rf = RequestFactory()
    request = rf.post('/named_path/')
    fdd_middleware.process_request(request)
    response = HttpResponse()

    fdd_middleware.process_response(request, response)

    __, kwargs = statsd_mock.histogram.call_args
    assert 'method:POST' in kwargs['tags']


def test_process_response__status_code(statsd_mock, fdd_middleware, processed_request):
    response = HttpResponse(status=302)
    fdd_middleware.process_response(processed_request, response)

    __, kwargs = statsd_mock.histogram.call_args

    assert 'status_code:302' in kwargs['tags']


def test_process_response__ignores_unprocessed_request(statsd_mock, fdd_middleware, named_request, response):
    fdd_middleware.process_response(named_request, response)
    assert statsd_mock.histogram.call_count == 0


@pytest.fixture
def unhandled_error():
    return Exception()


def test_process_exception(statsd_mock, fdd_middleware, processed_request, unhandled_error):
    fdd_middleware.process_exception(processed_request, unhandled_error)

    __, kwargs = statsd_mock.histogram.call_args
    assert kwargs['metric'] == 'fdjangodog_app_name.request_time'
    assert kwargs['value'] > 0.0
    assert kwargs['tags'] == ['method:GET', 'handler:url:a_url_name', 'exception:Exception']


def test_process_exception__ignores_unprocessed_request(statsd_mock, fdd_middleware, named_request, unhandled_error):
    fdd_middleware.process_exception(named_request, unhandled_error)
    assert statsd_mock.histogram.call_count == 0


def test_process_exception__handles_http_404(statsd_mock, fdd_middleware):
    rf = RequestFactory()
    request = rf.get('/this_doesnt_exist/')
    fdd_middleware.process_request(request)
    fdd_middleware.process_exception(request, Http404())

    __, kwargs = statsd_mock.histogram.call_args
    assert kwargs['tags'] == ['method:GET', 'exception:Http404']
