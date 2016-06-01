import time

from django.conf import settings
from django.core.urlresolvers import resolve
from django.http import Http404

from datadog import statsd


class FDjangoDogMiddleware(object):
    APP_NAME = settings.FDJANGODOG_APP_NAME
    DD_TIMING_ATTRIBUTE = '_dd_start_time'

    def __init__(self):
        self.stats = statsd

        self.timing_metric = '{}.request_time'.format(self.APP_NAME)

    def _get_elapsed_time(self, request):
        return time.time() - getattr(request, self.DD_TIMING_ATTRIBUTE)

    def _get_request_path(self, request):
        path = request.path
        view = resolve(path)
        if view:
            path = view.url_name
        return path

    def _get_metric_tags(self, request, response=None, success=True):
        path = self._get_request_path(request)

        tags = [
            'path:{}'.format(path),
            'success:{}'.format(success),
        ]

        if response:
            tags.append('status_code:{}'.format(response.status_code))

        return tags

    def _record_request_time(self, request, tags):
        self.stats.histogram(self.timing_metric, self._get_elapsed_time(request), tags=tags)

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

        if isinstance(exception, Http404):
            return

        tags = self._get_metric_tags(request, success=False)
        self._record_request_time(request, tags)
