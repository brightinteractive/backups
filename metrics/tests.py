#!/usr/bin/env python

import unittest, collections

from metrics import Metrics, _Config


class MetricsTests(unittest.TestCase):
    def test__we_can_get_a_list_of_available_metrics(self):
        metrics = Metrics()
        available_metrics = metrics.available()
        self.assertIsInstance(available_metrics, collections.Iterable)

    def test__we_can_configure_what_metrics_are_available(self):
        _Config.allowed_metrics = ( 'test_metric_name', )
        metrics = Metrics()
        available_metrics = metrics.available()
        self.assertEqual(set(available_metrics), set(_Config.allowed_metrics))

        _Config.allowed_metrics = ( 'test_metric_name','another_metric_name' )
        metrics = Metrics()
        available_metrics = metrics.available()
        self.assertEqual(set(available_metrics), set(_Config.allowed_metrics))

        _Config.allowed_metrics = ()
        metrics = Metrics()
        available_metrics = metrics.available()
        self.assertEqual(set(available_metrics), set(_Config.allowed_metrics))

    def test__we_can_get_a_report_of_all_metrics_and_their_values(self):
        metrics = Metrics()
        metrics = metrics.report()

        available_metrics = _Config.allowed_metrics
        for metric in available_metrics:
            self.assertIn(metric, metrics.keys())

    def test__we_can_count_how_many_times_a_function_is_called(self):
        _Config.allowed_metrics = ('how many times _test_function has been called',)
        metrics = Metrics()

        @Metrics.counter('how many times _test_function has been called', metrics)
        def _test_function():
            pass

        _test_function()
        metric_value = metrics.__dict__['how many times _test_function has been called']
        self.assertEqual(metric_value, 1)

        _test_function()
        _test_function()
        metric_value = metrics.__dict__['how many times _test_function has been called']
        self.assertEqual(metric_value, 3)

    def test__we_can_catch_a_bad_metric_name_at_compile_time(self):
        _Config.allowed_metrics = ('allowed  metric name',)
        metrics = Metrics()

        with self.assertRaises(AttributeError):
            @Metrics.counter('name not included in allowed metrics tuple', metrics)
            def _test_function():
                pass
