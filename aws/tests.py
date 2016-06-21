#!/usr/bin/env python

import unittest, os, collections

import boto3
from mock import patch, Mock, MagicMock

from aws import AWSApiWrapper, S3Restore


class AWSApiWrapperTests(unittest.TestCase):

    def test__we_can_create_an_aws_session_with_credentials_stored_in_environment_variables(self):
        test_credentials = {
                'AWS_ACCESS_KEY_ID':'test access key',
                'AWS_SECRET_ACCESS_KEY':'test secret key'
                }

        with patch.dict('os.environ', test_credentials):
            aws = AWSApiWrapper()
            session = aws.create_aws_session()
            credentials = session.get_credentials()
            self.assertEqual(test_credentials['AWS_ACCESS_KEY_ID'], credentials.access_key)
            self.assertEqual(test_credentials['AWS_SECRET_ACCESS_KEY'], credentials.secret_key)

    def test__we_can_identify_an_s3_object_with_glacier_storage_class(self):
        mock_s3_object = Mock()
        mock_s3_object.storage_class = 'GLACIER'
        self.assertTrue(S3Restore.is_glacier_type(mock_s3_object))

        mock_s3_object.storage_class = 'STANDARD'
        self.assertFalse(S3Restore.is_glacier_type(mock_s3_object))

    def test__we_can_identify_an_s3_object_that_has_yet_to_be_restored(self):
        mock_detail_object = Mock()
        mock_summary_object = Mock()
        mock_summary_object.Object = MagicMock(return_value=mock_detail_object)

        mock_detail_object.restore = None
        self.assertTrue(S3Restore.is_not_restored(mock_summary_object))

        mock_detail_object.restore = 'returns a string is restore is in progress or completed'
        self.assertFalse(S3Restore.is_not_restored(mock_summary_object))

    def test__we_call_restore_when_we_identify_an_s3_object_that_is_glacier_storage_class_and_is_in_an_unrestored_state(self):
        mock_detail_object = Mock()
        mock_summary_object = Mock()
        mock_summary_object.Object = MagicMock(return_value=mock_detail_object)

        mock_summary_object.storage_class = 'GLACIER'
        mock_detail_object.restore = None

        with patch.object(S3Restore, 'call_restore') as call_to_restore:
            S3Restore.restore_s3_object(mock_summary_object)
            call_to_restore.assert_called_once()
            call_to_restore.assert_called_with(mock_summary_object)

        self.assertTrue(S3Restore.is_glacier_type(mock_summary_object))

    def test__we_restore_an_object_for_seven_days(self):
        mock_summary_object = Mock()
        mock_summary_object.restore_object = Mock()
        expected_api_call = mock_summary_object.restore_object

        result = S3Restore.call_restore(mock_summary_object)
        expected_api_call.assert_called_with(RestoreRequest={ 'Days' : 7 })

