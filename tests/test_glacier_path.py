import unittest

from s3backups.aws import GlacierPath
from s3backups.aws.glacier import main

from datetime import datetime

class GlacierPathTests(unittest.TestCase):
    def test__we_can_split_key_and_timestamp_from_path(self):
        path =  '0/some-asset.jpeg_2014-02-13 18:19:06'
        key, stamp = GlacierPath.split(path)
        self.assertEquals('0/some-asset.jpeg', key)
        self.assertEquals('2014-02-13 18:19:06', stamp)

    def test__we_can_get_key_from_path_when_path_is_not_timestamped(self):
        path =  '0/some-asset.jpeg'
        key, stamp = GlacierPath.split(path)
        self.assertEquals('0/some-asset.jpeg', key)
        self.assertIsNone(stamp)

    def test__we_can_get_entire_path_when_timestamp_is_malformed(self):
        path =  '0/some-asset.jpeg_malformed 2013'
        key, stamp = GlacierPath.split(path)
        self.assertEquals('0/some-asset.jpeg_malformed 2013', key)

    def test__we_can_get_a_datetime_object_from_timestamp(self):
        path =  '0/some-asset.jpeg_2014-02-13 18:19:06'
        expected_datetime = datetime(year=2014,month=02,day=13,hour=18,minute=19,second=06)
        date = GlacierPath.datetime(path)
        self.assertEquals(expected_datetime, date)

    def test_datetime_returns_None_when_datetimestamp_not_present_in_path(self):
        path =  '0/some-asset.jpeg'
        date = GlacierPath.datetime(path)
        self.assertIsNone(date)

    def test__we_can_extract_key_from_path(self):
        path =  '0/some-asset.jpeg_2014-02-13 18:19:06'
        key = GlacierPath.key(path)
        self.assertEquals('0/some-asset.jpeg', key)

    def test__we_can_get_key_from_path_even_if_timestamp_is_not_present(self):
        path =  '0/some-asset.jpeg'
        key = GlacierPath.key(path)
        self.assertEquals('0/some-asset.jpeg', key)

    def test_key_returns_entire_path_when_datetime_malformed(self):
        path =  '0/some-a.jpeg2014malformed-02-13 18:19:06'
        key = GlacierPath.key(path)
        self.assertEquals('0/some-a.jpeg2014malformed-02-13 18:19:06', key)

    def test_main_extracts_keys_from_a_list_of_paths(self):
        paths = ['0/some-a.jpeg2014malformed-02-13 18:19:06', '89/some-a.jpeg_2012-02-13 18:19:06']
        keys = main(paths)
        self.assertIn('0/some-a.jpeg2014malformed-02-13 18:19:06', keys)
        self.assertIn('89/some-a.jpeg',keys)

    def test_main_returns_empty_list_when_no_paths_are_passed(self):
        paths = []
        keys = main(paths)
        self.assertEquals([],keys)

