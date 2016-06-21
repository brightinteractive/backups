#!/usr/bin/env python


class Metrics(object):
    def __init__(self):
        self.report = dict()

    def available(self):
        return self.report.keys()

    def add(self, metric):
        if not self.report.has_key(metric):
            self.report[metric] = None

    @staticmethod
    def counter(metric, metric_obj):
        if metric not in metric_obj.available():
            raise AttributeError('\'%s\' is not an available metric.'% metric)

        def wrapper(fn):
            def _counter(*args, **kwargs):
                if metric_obj.report[metric]:
                    metric_obj.report[metric] += 1
                else:
                    metric_obj.report[metric] = 1
                return fn(*args, **kwargs)
            return _counter
        return wrapper

