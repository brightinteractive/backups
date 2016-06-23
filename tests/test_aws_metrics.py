#!/usr/bin/env python


import unittest

from mock import patch, Mock, MagicMock

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
        number_of_recorded_objects = AWSMetrics.report['number_of_objects']
        self.assertEqual(number_of_recorded_objects, 3)

    def test__we_can_record_the_number_of_requests_made(self):
        mock_response = self.mock_aws_response()
        mock_s3_object = Mock()
        mock_s3_object.restore_object = Mock(return_value=mock_response)

        S3Restore.call_restore(mock_s3_object)
        number_of_requests = AWSMetrics.report['number_of_requests']
        self.assertEqual(number_of_requests, 1)

        for _ in range(4): S3Restore.call_restore(mock_s3_object)
        number_of_requests = AWSMetrics.report['number_of_requests']
        self.assertEqual(number_of_requests, 5)

    def test__we_can_record_the_status_code_of_restore_reponses(self):
        status_codes_and_their_frequencies = { '200': 12, '300': 11, '302': 1, '202': 1, '505': 1}

        for status_code, number_of_responses in status_codes_and_their_frequencies.items():
            for response in range(number_of_responses):
                response = self.mock_aws_response(HTTPStatusCode=status_code)
                mock_s3_object = Mock()
                mock_s3_object.restore_object = MagicMock(return_value=response)
                S3Restore.call_restore(mock_s3_object)

        recorded_status_codes = AWSMetrics.report['restore_object_status_codes']
        self.assertEqual(status_codes_and_their_frequencies, recorded_status_codes)

    def mock_aws_response(self, **kwargs):
        response = { 'HTTPStatusCode': '200',
                'HostId': 'KX19tFhyBOCZfaDAk78nnkLiAvVV8fUgv11LMykrn3aXwZhJcimxZEbqRmUYaalq/beynjJ4Hmw=',
                'RequestId': '609FF741F8386E27' }
        response.update(kwargs)
        return { 'ResponseMetadata': response }
