#!/usr/bin/env python

import unittest, os

import boto3
from mock import patch, Mock, MagicMock

import restore
from restore import S3Resource, S3Restore

class ResourceTests(unittest.TestCase):

    def test_create_aws_session_returns_an_aws_session(self):
        session = S3Resource.create_aws_session()
        self.assertIsInstance(session, boto3.session.Session)

    def test_create_aws_session_creates_session_with_credentials_from_environmet_variables(self):
        test_credentials = {
                'AWS_ACCESS_KEY_ID':'test access key',
                'AWS_SECRET_ACCESS_KEY':'test secret key'
                }

        with patch.dict('os.environ', test_credentials):
            session = S3Resource.create_aws_session()
            credentials = session.get_credentials()
            self.assertEqual(test_credentials['AWS_ACCESS_KEY_ID'], credentials.access_key)
            self.assertEqual(test_credentials['AWS_SECRET_ACCESS_KEY'], credentials.secret_key)

    def test_create_s3_resource_returns_a_resource_using_session_param(self):
        mock_resource = object()
        mock_session = Mock()
        mock_session.resource = MagicMock(return_value=mock_resource)

        resource = S3Resource.create_s3_resource(mock_session)
        self.assertEqual(resource, mock_resource)

        mock_session.resource.assert_called_with('s3')

    @patch.object(restore.S3Resource,'create_s3_resource')
    def test_get_s3_bucket_by_name_passes_expected_name_to_expected_boto3_api_call(self, mock):
        mock_resource = Mock()
        mock_resource.Bucket = MagicMock()
        mock.return_value = mock_resource

        expected_name = object()
        expected_api_call = mock_resource.Bucket

        resource = S3Resource()
        resource.get_s3_bucket_by_name(expected_name)

        expected_api_call.assert_called_with(expected_name)

    @patch.object(restore.S3Resource,'create_s3_resource')
    def test_get_s3_bucket_by_name_returns_result_of_expected_boto3_api_call(self, mock):
        result_of_api_call = object()

        mock_resource = Mock()
        mock_resource.Bucket = Mock()
        mock.return_value = mock_resource

        expected_api_call = mock_resource.Bucket
        expected_api_call.return_value = result_of_api_call

        resource = S3Resource()
        result = resource.get_s3_bucket_by_name('test name')
        expected_api_call.assert_called_once()
        self.assertEqual(result_of_api_call, result_of_api_call)

    @patch.object(restore.S3Resource,'create_s3_resource')
    def test_get_s3_objects_by_bucket_returns_result_of_expected_boto3_api_call(self, mock_resource):
        result_of_api_call = object()

        mock_bucket = Mock()
        mock_bucket.objects = Mock()
        mock_bucket.objects.all = MagicMock(return_value=result_of_api_call)
        expected_api_call = mock_bucket.objects.all

        with patch.object(S3Resource, 'get_s3_bucket_by_name', return_value=mock_bucket):
            resource = S3Resource()
            result = resource.get_s3_objects_by_bucket_name('test name')
            expected_api_call.assert_called_once()
            self.assertEqual(result, result_of_api_call)

    def test_is_glacier_type_returns_true_for_glacier_objects_and_false_otherwise(self):
        mock_summary_object = Mock()
        mock_summary_object.storage_class = 'GLACIER'
        self.assertTrue(S3Restore.is_glacier_type(mock_summary_object))

        mock_summary_object.storage_class = 'Something else'
        self.assertFalse(S3Restore.is_glacier_type(mock_summary_object))

    def test_is_not_restored_returns_true_if_s3_object_is_not_restored(self):
        mock_detail_object = Mock()
        mock_summary_object = Mock()
        mock_summary_object.Object = MagicMock(return_value=mock_detail_object)

        mock_detail_object.restore = None
        self.assertTrue(S3Restore.is_not_restored(mock_summary_object))

        mock_detail_object.restore = 'returns a string is restore is in progress or completed'
        self.assertFalse(S3Restore.is_not_restored(mock_summary_object))

    def test_restore_s3_object_calls_call_restore_when_object_is_glacier_and_not_restored(self):
        mock_detail_object = Mock()
        mock_summary_object = Mock()
        mock_summary_object.Object = MagicMock(return_value=mock_detail_object)

        mock_summary_object.storage_class = 'GLACIER'
        mock_detail_object.restore = None

        with patch.object(S3Restore, 'call_restore') as mock:
            S3Restore.restore_s3_object(mock_summary_object)
            mock.assert_called_once()

        self.assertTrue(S3Restore.is_glacier_type(mock_summary_object))

    def test_restore_s3_object_calls_call_restore_with_same_s3_object(self):
        mock_detail_object = Mock()
        mock_summary_object = Mock()
        mock_summary_object.Object = MagicMock(return_value=mock_detail_object)

        mock_summary_object.storage_class = 'GLACIER'
        mock_detail_object.restore = None

        with patch.object(S3Restore, 'call_restore') as mock:
            S3Restore.restore_s3_object(mock_summary_object)
            mock.assert_called_with(mock_summary_object)

    def test_call_restore_makes_expected_boto3_api_call(self):
        mock_summary_object = Mock()
        mock_summary_object.restore_object = Mock()
        expected_api_call = mock_summary_object.restore_object

        S3Restore.call_restore(mock_summary_object)
        expected_api_call.assert_called_once()

    def test_call_restore_returns_result_from_expected_boto3_api_call(self):
        result_from_api = object()
        mock_summary_object = Mock()
        mock_summary_object.restore_object = MagicMock(return_value=result_from_api)
        expected_api_call = mock_summary_object.restore_object

        result = S3Restore.call_restore(mock_summary_object)
        expected_api_call.assert_called_once()
        self.assertEqual(result, result_from_api)

    def test_call_restore_makes_a_restore_request_for_7_days(self):
        mock_summary_object = Mock()
        mock_summary_object.restore_object = Mock()
        expected_api_call = mock_summary_object.restore_object

        result = S3Restore.call_restore(mock_summary_object)
        expected_api_call.assert_called_with(RestoreRequest={ 'Days' : 7 })

