#!/usr/bin/env python

import unittest

from mock import patch, Mock

from s3backups.aws import S3Restore, AWSApiWrapper, AWSMetrics


class AWSMetricsTests(unittest.TestCase):
    def setUp(self):
        AWSMetrics.reset()

    @patch.object(S3Restore, '_object_should_be_restored', return_value=False)
    def test__we_can_incrementally_record_the_number_of_objects_in_a_bucket(self, mock_restore):
        S3Restore.restore_s3_object(object())
        number_of_recorded_objects = AWSMetrics.report['number_of_objects']
        self.assertEqual(number_of_recorded_objects, 1)

        S3Restore.restore_s3_object(object())
        S3Restore.restore_s3_object(object())
        S3Restore.restore_s3_object(object())
        number_of_recorded_objects = AWSMetrics.report['number_of_objects']
        self.assertEqual(number_of_recorded_objects, 4)

    @patch.object(AWSApiWrapper, 'get_s3_objects_by_bucket_name')
    def test__we_can_record_the_number_of_requests_made(self, mock_api):
        mock_s3_object = Mock()
        mock_s3_object.restore_object = Mock()

        S3Restore.call_restore(mock_s3_object)
        number_of_requests = AWSMetrics.report['number_of_requests']
        self.assertEqual(number_of_requests, 1)

        for _ in range(4): S3Restore.call_restore(mock_s3_object)
        number_of_requests = AWSMetrics.report['number_of_requests']
        self.assertEqual(number_of_requests, 5)

