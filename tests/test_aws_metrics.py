#!/usr/bin/env python


import unittest

from mock import patch, Mock, MagicMock

from s3backups.aws import AWSApiWrapper, AWSMetrics, ObjectRestore 
from utils import mock_aws_response


class AWSMetricsTests(unittest.TestCase):
    def setUp(self):
        AWSMetrics.reset()

    @patch.object(ObjectRestore, '_object_should_be_restored', return_value=False)
    def test__we_can_incrementally_record_the_number_of_objects_in_a_bucket(self, mock_restore):
        ObjectRestore.restore_s3_object(object())
        number_of_recorded_objects = AWSMetrics.report['number_of_objects']
        self.assertEqual(number_of_recorded_objects, 1)

        ObjectRestore.restore_s3_object(object())
        ObjectRestore.restore_s3_object(object())
        number_of_recorded_objects = AWSMetrics.report['number_of_objects']
        self.assertEqual(number_of_recorded_objects, 3)

    def test__we_can_record_the_number_of_requests_made(self):
        mock_response = mock_aws_response()
        mock_s3_object = Mock()
        mock_s3_object.restore_object = Mock(return_value=mock_response)

        ObjectRestore.call_restore(mock_s3_object)
        number_of_requests = AWSMetrics.report['number_of_requests']
        self.assertEqual(number_of_requests, 1)

        for _ in range(4): ObjectRestore.call_restore(mock_s3_object)
        number_of_requests = AWSMetrics.report['number_of_requests']
        self.assertEqual(number_of_requests, 5)

    def test__we_can_record_the_status_code_of_restore_reponses(self):
        status_codes_and_their_frequencies = { '200': 12, '300': 11, '302': 1, '202': 1, '505': 1}

        for status_code, number_of_responses in status_codes_and_their_frequencies.items():
            for response in range(number_of_responses):
                response = mock_aws_response(HTTPStatusCode=status_code)
                mock_s3_object = Mock()
                mock_s3_object.restore_object = MagicMock(return_value=response)
                ObjectRestore.call_restore(mock_s3_object)

        recorded_status_codes = AWSMetrics.report['restore_object_status_codes']
        self.assertEqual(status_codes_and_their_frequencies, recorded_status_codes)

    def test__we_can_record_the_number_glacier_objects(self):
        mock_s3_glacier_object = Mock()
        mock_s3_glacier_object.storage_class = 'GLACIER'

        mock_s3_standard_object = Mock()
        mock_s3_standard_object.storage_class = 'STANDARD'

        ObjectRestore.is_glacier_type(mock_s3_glacier_object)
        ObjectRestore.is_glacier_type(mock_s3_standard_object)

        number_of_glacier_objects = AWSMetrics.report['number_of_glacier_objects']
        self.assertEquals(number_of_glacier_objects, 1)

    def test__we_can_record_the_number_of_unrestored_objects(self):
        mock_s3_unrestored_object = Mock()
        mock_s3_detail_object = Mock()
        mock_s3_unrestored_object.Object = MagicMock(return_value=mock_s3_detail_object)
        mock_s3_detail_object.restore = None

        mock_s3_restored_object = Mock()
        mock_s3_detail_object = Mock()
        mock_s3_restored_object.Object = MagicMock(return_value=mock_s3_detail_object)
        mock_s3_detail_object.restore = 'I am restored'

        ObjectRestore.is_not_restored(mock_s3_unrestored_object)
        ObjectRestore.is_not_restored(mock_s3_restored_object)

        number_of_unrestored_objects = AWSMetrics.report['number_of_unrestored_objects']
        self.assertEquals(number_of_unrestored_objects, 1)

