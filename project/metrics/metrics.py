#!/usr/bin/env python


class Metrics(object):
    def __init__(self, allowed_metrics):
        for metric in allowed_metrics:
            setattr(self, metric, None)

    def available(self):
        return self.report().keys()

    def report(self):
        return self.__dict__

    @staticmethod
    def counter(metric, metric_obj):
        if metric not in metric_obj.available():
            raise AttributeError('\'%s\' is not an available metric.'% metric)

        def wrapper(fn):
            def _counter(*args, **kwargs):
                if metric_obj.__dict__[metric]:
                    metric_obj.__dict__[metric] += 1
                else:
                    metric_obj.__dict__[metric] = 1
                return fn()
            return _counter
        return wrapper

