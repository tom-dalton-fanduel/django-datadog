from datadog import DogStatsd
from django.conf import settings

from . import request_stats


try:
    from django.urls import resolve, Resolver404
except ImportError:
    from django.core.urlresolvers import resolve, Resolver404

try:
    from django.utils.deprecation import MiddlewareMixin
    base_class = MiddlewareMixin
except ImportError:
    base_class = object


statsd_host = getattr(settings, 'FDJANGODOG_STATSD_HOST', 'localhost')
statsd_port = getattr(settings, 'FDJANGODOG_STATSD_PORT', 8125)
statsd = DogStatsd(host=statsd_host, port=statsd_port)


class FDjangoDogMiddleware(base_class):
    APP_NAME = settings.FDJANGODOG_APP_NAME
    REQUEST_STATS_ATTRIBUTE = '_fdjangodog_stats'
    STATS_CLASSES = (
        request_stats.RequestDuration,
        request_stats.RequestRSSMemoryUsedMB,
    )

    def __init__(self, *args, **kwargs):
        super(FDjangoDogMiddleware, self).__init__(*args, **kwargs)

        self.statsd = statsd

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

    def _record_metrics(self, request, response=None, exception=None):
        request_stats = getattr(request, self.REQUEST_STATS_ATTRIBUTE, tuple())

        for request_stat in request_stats:
            request_stat.finish_recording()

        if response:
            tags = self._get_metric_tags(request, response=response)
        else:
            tags = self._get_metric_tags(request, exception=exception)

        for request_stat in request_stats:
            full_metric_name = self.APP_NAME + "." + request_stat.metric_name
            self.statsd.histogram(
                metric=full_metric_name,
                value=request_stat.get_metric_value(),
                tags=tags,
            )

    def process_request(self, request):
        setattr(request, self.REQUEST_STATS_ATTRIBUTE, [cls() for cls in self.STATS_CLASSES])

    def process_response(self, request, response):
        self._record_metrics(request, response=response)
        return response

    def process_exception(self, request, exception):
        self._record_metrics(request, exception=exception)
