#!/usr/bin/env python

import unittest

from restore import create_parser


class RestoreCommandLineTests(unittest.TestCase):
    def test__we_can_parse_and_retreive_the_name_of_the_bucket_to_be_restored(self):
        name_of_bucket_to_be_restored = 'test bucket'

        parser = create_parser()
        args = parser.parse_args([name_of_bucket_to_be_restored])

        self.assertEqual(args.bucket, name_of_bucket_to_be_restored)

