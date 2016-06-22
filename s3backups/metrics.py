#!/usr/bin/env python


class Metrics(object):
    available_metrics = ()
    report = dict.fromkeys(available_metrics)

    def __init__(self):
        self.report = dict()

    @classmethod
    def available(self):
        return self.report.keys()

    @classmethod
    def add(self, metric):
        if not self.report.has_key(metric):
            self.report[metric] = None

    @classmethod
    def reset(self):
        for metric in self.available_metrics:
            self.report = dict.fromkeys(self.available_metrics)


    @classmethod
    def counter(cls, metric):
        if metric not in cls.available():
            raise AttributeError('\'%s\' is not an available metric.'% metric)

        def wrapper(fn):
            def _counter(*args, **kwargs):
                if cls.report[metric]:
                    cls.report[metric] += 1
                else:
                    cls.report[metric] = 1
                return fn(*args, **kwargs)
            return _counter
        return wrapper

