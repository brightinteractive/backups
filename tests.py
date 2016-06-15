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

    def test_create_s3_resource_creates_new_session_if_one_is_not_passed_to_it(self):
        with patch.object(S3Resource, 'create_aws_session') as mock:
            S3Resource.create_s3_resource()
            mock.assert_called_once()

