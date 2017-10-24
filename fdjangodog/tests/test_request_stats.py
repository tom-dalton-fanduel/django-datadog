from .. import request_stats


def test_request_duration():
    rd = request_stats.RequestDuration()

    rd.finish_recording()
    value = rd.get_metric_value()

    assert isinstance(value, float)
    # Somewhat-ugly check that the value is broadly sane
    assert value > 0.0
    assert value < 1.0


def test_request_rss_memory_used():
    rrmu = request_stats.RequestRSSMemoryUsedMB()
    # Try to force some memory to be allocated, this is a yucky hack
    list(range(1000000))

    rrmu.finish_recording()
    value = rrmu.get_metric_value()

    assert isinstance(value, float)
    assert value > 0.0
    # Worst case guesstimate, if each int in the python tuple takes 50 bytes, then 1M ints would be 50MB
    assert value < 50.0
