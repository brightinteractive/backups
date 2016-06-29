#!/usr/bin/env python

import unittest, os

from mock import Mock, patch

from s3backups.restore import Restore, main, setup
from s3backups.parser import create_parser
from s3backups.s3 import S3Restore


class RestoreSetupTests(unittest.TestCase):
    def test__aws_credentials_are_available_as_environment_variables(self):
        setup()
        self.assertTrue(os.environ.has_key('AWS_SECRET_ACCESS_KEY'))
        self.assertTrue(os.environ.has_key('AWS_ACCESS_KEY_ID'))

class RestoreCommandLineTests(unittest.TestCase):
    def test__we_can_retrieve_the_name_of_the_bucket_to_be_restored_from_commandline_arguments(self):
        name_of_bucket_to_be_restored = 'test bucket'

        parser = create_parser()
        args = parser.parse_args([name_of_bucket_to_be_restored])

        self.assertEqual(args.bucket, name_of_bucket_to_be_restored)

    def test__we_can_set_retrieve_the_dry_run_state_from_commandline_arguments(self):
        parser = create_parser()

        args = parser.parse_args(['test-bucket', '--dry-run'])
        self.assertTrue(args.dry_run)

        args = parser.parse_args(['test-bucket',])
        self.assertFalse(args.dry_run)

class RestoreThreadTests(unittest.TestCase):
    def test__we_can_create_a_thread_to_restore_a_bucket(self):
        name_of_bucket_to_be_restored = 'test bucket'

        with patch.object(S3Restore, 'bucket') as restore_bucket:
            thread = Restore(name_of_bucket_to_be_restored)
            thread.start()
            restore_bucket.assert_called_with(name_of_bucket_to_be_restored)

