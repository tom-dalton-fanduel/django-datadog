import os
import time

import psutil


class RequestStatisticBase(object):
    metric_name = ''

    def finish_recording(self):
        raise NotImplementedError()

    def get_metric_value(self):
        raise NotImplementedError()


class RequestDuration(RequestStatisticBase):
    metric_name = 'request_time'

    def __init__(self):
        self.start_time = time.time()
        self.end_time = None

    def finish_recording(self):
        self.end_time = time.time()

    def get_metric_value(self):
        return self.end_time - self.start_time


class RequestRSSMemoryUsedMB(RequestStatisticBase):
    metric_name = 'request_rss_mb'

    def __init__(self):
        self.start_memory_info = psutil.Process(os.getpid()).memory_info()
        self.end_memory_info = None

    def finish_recording(self):
        self.end_memory_info = psutil.Process(os.getpid()).memory_info()

    def get_metric_value(self):
        rss_diff_bytes = self.end_memory_info.rss - self.start_memory_info.rss
        return float(rss_diff_bytes) / 1000000
