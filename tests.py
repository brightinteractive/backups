#!/usr/bin/env python

import unittest, os

import boto3
from mock import patch, Mock, MagicMock

import restore
from restore import S3Resource

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

    def test_create_s3_resource_returns_an_aws_s3_resource_using_session_param(self):
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

