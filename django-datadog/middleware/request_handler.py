# std lib
import time
import traceback
try:
    import json
except ImportError:
    import simplejson as json

# django
from django.http import Http404
from django.conf import settings
from django.core.urlresolvers import resolve

# Data dog API
from datadog import initialize
from datadog import ThreadStats

dd_init_options = {
    'api_key': settings.DATADOG_API_KEY,
    'app_key': settings.DATADOG_APP_KEY
}

initialize(**dd_init_options)


class DatadogMiddleware(object):
    DD_TIMING_ATTRIBUTE = '_dd_start_time'

    def __init__(self):
        app_name = settings.DATADOG_APP_NAME
        self.stats = ThreadStats()
        self.stats.start()
        self.error_metric = '{0}.errors'.format(app_name)
        self.timing_metric = '{0}.request_time'.format(app_name)
        self.event_tags = [app_name, 'exception']

    def process_request(self, request):
        setattr(request, self.DD_TIMING_ATTRIBUTE, time.time())

    def process_response(self, request, response):
        """ Submit timing metrics from the current request """
        if not hasattr(request, self.DD_TIMING_ATTRIBUTE):
            return response

        # Calculate request time and submit to Datadog
        request_time = time.time() - getattr(request, self.DD_TIMING_ATTRIBUTE)
        tags = self._get_metric_tags(request)
        self.stats.histogram(self.timing_metric, request_time, tags=tags)

        return response

    def process_exception(self, request, exception):
        """ Captures Django view exceptions as Datadog events """
        if isinstance(exception, Http404):
            # Don't report 404 not found
            return

        # Get a formatted version of the traceback.
        exc = traceback.format_exc()

        # Make request.META json-serializable.
        szble = {}
        for k, v in request.META.items():
            if isinstance(v, (list, basestring, bool, int, float, long)):
                szble[k] = v
            else:
                szble[k] = str(v)

        title = 'Exception from {0}'.format(request.path)
        text = "Traceback:\n@@@\n{0}\n@@@\nMetadata:\n@@@\n{1}\n@@@" \
            .format(exc, json.dumps(szble, indent=2))

        # Submit the exception to Datadog
        self.stats.event(title, text, alert_type='error', aggregation_key=request.path, tags=self.event_tags)

        # Increment our errors metric
        tags = self._get_metric_tags(request)
        self.stats.increment(self.error_metric, tags=tags)

    def _get_metric_tags(self, request):
        path = request.path
        view = resolve(path)
        if view:
            path = view.url_name
        return ['path:{0}'.format(path)]

