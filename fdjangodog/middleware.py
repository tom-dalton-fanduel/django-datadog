import time

from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404

from datadog import statsd


class FDjangoDogMiddleware(object):
    APP_NAME = settings.FDJANGODOG_APP_NAME
    DD_TIMING_ATTRIBUTE = '_dd_start_time'

    def __init__(self):
        self.stats = statsd

        self.timing_metric = '{}.request_time'.format(self.APP_NAME)

    def _get_elapsed_time(self, request):
        return time.time() - getattr(request, self.DD_TIMING_ATTRIBUTE)

    def _get_request_namespace_and_handler(self, request):
        try:
            match = resolve(request.path)
        except Resolver404:
            return None, None

        namespace = match.namespace

        if match.url_name:
            handler_name = "url:{}".format(match.url_name)
        else:
            handler_name = "view:{}".format(match.view_name)

        return namespace, handler_name

    def _get_metric_tags(self, request, response=None, exception=None):
        tags = []

        if request.method:
            tags.append('method:{}'.format(request.method))

        namespace, handler = self._get_request_namespace_and_handler(request)
        if namespace:
            tags.append('namespace:{}'.format(namespace))
        if handler:
            tags.append('handler:{}'.format(handler))

        if response:
            tags.append('status_code:{}'.format(response.status_code))

        if exception:
            tags.append('exception:{}'.format(exception.__class__.__name__))

        return tags

    def _record_request_time(self, request, tags):
        self.stats.histogram(metric=self.timing_metric, value=self._get_elapsed_time(request), tags=tags)

    def process_request(self, request):
        setattr(request, self.DD_TIMING_ATTRIBUTE, time.time())

    def process_response(self, request, response):
        """Submit timing metrics from the current request."""
        if not hasattr(request, self.DD_TIMING_ATTRIBUTE):
            return response

        tags = self._get_metric_tags(request, response)
        self._record_request_time(request, tags)

        return response

    def process_exception(self, request, exception):
        """Captures Django view exceptions as Datadog events."""
        if not hasattr(request, self.DD_TIMING_ATTRIBUTE):
            return

        tags = self._get_metric_tags(request, exception=exception)
        self._record_request_time(request, tags)
