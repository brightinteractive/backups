#!/usr/bin/env python

import unittest, collections

from s3backups.metrics import Metrics


class MetricsTests(unittest.TestCase):
    def test__we_get_an_empty_list_when_there_are_no_available_maetrics(self):
        metrics = Metrics()
        available_metrics = metrics.available()
        self.assertIsInstance(available_metrics, collections.Iterable)
        self.assertEqual([], available_metrics)

    def test__we_can_get_a_list_of_available_metrics(self):
        metrics = Metrics()
        metrics.add('test_metric_name')
        available_metrics = metrics.available()
        self.assertIn('test_metric_name', available_metrics)

        allowed_metrics = ('test_metric_name', 'another_metric_name')
        metrics = Metrics()
        map(metrics.add, allowed_metrics)
        available_metrics = metrics.available()
        self.assertEqual(set(available_metrics), set(allowed_metrics))

    def test__we_dont_duplicate_metrics_when_adding_them(self):
        metrics = Metrics()
        metrics.add('test_metric_name')
        metrics.add('test_metric_name')

        available_metrics = metrics.available()
        self.assertEqual(len(available_metrics), 1)

    def test__we_can_get_a_report_of_all_metrics_and_their_values(self):
        allowed_metrics = ('test_metric_name', 'another_metric_name')
        metrics = Metrics()
        map(metrics.add, allowed_metrics)

        for metric in allowed_metrics:
            self.assertIn(metric, metrics.report.keys())

    def test__we_can_count_how_many_times_a_function_is_called(self):
        allowed_metric = 'how many times _test_function has been called'
        metrics = Metrics()
        metrics.add(allowed_metric)

        @Metrics.counter('how many times _test_function has been called', metrics)
        def _test_function():
            pass

        _test_function()
        metric_value = metrics.report['how many times _test_function has been called']
        self.assertEqual(metric_value, 1)

        _test_function()
        _test_function()
        metric_value = metrics.report['how many times _test_function has been called']
        self.assertEqual(metric_value, 3)

    def test__we_can_catch_a_bad_metric_name_at_compile_time(self):
        allowed_metric = 'allowed  metric name'
        metrics = Metrics()
        metrics.add(allowed_metric)

        with self.assertRaises(AttributeError):
            @Metrics.counter('name not included in allowed metrics tuple', metrics)
            def _test_function():
                pass

