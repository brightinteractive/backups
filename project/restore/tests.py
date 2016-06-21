#!/usr/bin/env python

import unittest, os

from mock import Mock, patch

from restore import main, setup
from parser import create_parser
from aws.aws import S3Restore


class RestoreCommandLineTests(unittest.TestCase):
    def test__we_can_retrieve_the_name_of_the_bucket_to_be_restored_from_commandline_arguments(self):
        name_of_bucket_to_be_restored = 'test bucket'

        parser = create_parser()
        args = parser.parse_args([name_of_bucket_to_be_restored])

        self.assertEqual(args.bucket, name_of_bucket_to_be_restored)

class RestoreMainTests(unittest.TestCase):
    def test__we_can_restore_the_bucket_passed_as_commandline_argument(self):
        mock_args = Mock()
        name_of_bucket_to_be_restored = 'test bucket'
        mock_args.bucket = name_of_bucket_to_be_restored

        with patch.object(S3Restore, 'bucket') as restore_bucket:
            main(mock_args)
            restore_bucket.assert_called_with(name_of_bucket_to_be_restored)

class RestoreSetupTests(unittest.TestCase):
    def test__aws_credentials_are_available_as_environment_variables(self):
        setup()
        self.assertTrue(os.environ.has_key('AWS_SECRET_ACCESS_KEY'))
        self.assertTrue(os.environ.has_key('AWS_ACCESS_KEY_ID'))

