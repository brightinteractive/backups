#!/usr/bin/env python

import unittest, os, collections
from Queue import Queue

import boto3
from mock import patch, Mock, MagicMock

from s3backups.aws import AWSApiWrapper, S3Restore
from utils import mock_aws_response


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


class S3RestoreTests(unittest.TestCase):
    def setUp(self):
        S3Restore.reset()

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

    @patch.object(S3Restore, 'restore_s3_object')
    @patch.object(AWSApiWrapper, 'get_s3_objects_by_bucket_name')
    def test__we_can_restore_all_the_objects_in_a_named_s3_bucket(self, aws_api_call, s3_restore_call):
        s3_object = Mock()
        mock_bucket_contents = [s3_object, s3_object, s3_object]
        number_of_objects_in_mock_bucket = len(mock_bucket_contents)
        aws_api_call.return_value = mock_bucket_contents

        restore = S3Restore()
        restore.bucket('test bucket')

        self.assertEqual(s3_restore_call.call_count, 3)

    @patch.object(AWSApiWrapper, 'get_s3_objects_by_bucket_name')
    def test__we_can_add_all_objects_to_a_queue(self, aws_api_call):
        mock_bucket_contents = [Mock(), Mock(), Mock()]
        aws_api_call.return_value = mock_bucket_contents

        restore = S3Restore()
        restore.producer(mock_bucket_contents)

        '''Q: why > 1? A: Becuase the queue is never empty, there is always a sentinel objeect in its tail'''
        while restore.queue.qsize() > 1:
            obj = restore.queue.get()
            self.assertIn(obj, mock_bucket_contents)

        thread_safe_queue = Queue
        self.assertIsInstance(restore.queue, thread_safe_queue)

    def test__the_object_queue_is_thread_safe(self):
        restore = S3Restore()
        thread_safe_queue = Queue
        self.assertIsInstance(restore.queue, thread_safe_queue)

    @patch.object(S3Restore, 'restore_s3_object')
    def test__we_consume_all_objects_in_the_queue_until_there_are_none(self, s3_restore_call):
        mock_bucket_contents = [Mock(), Mock(), Mock()]
        restore = S3Restore()
        restore.producer(mock_bucket_contents)

        restore.consumer()

        self.assertEqual(s3_restore_call.call_count, 3)
        # there's one object left...
        self.assertEqual(restore.queue.qsize(), 1)
        # ...and that object is the sentinel, not an s3object
        self.assertEqual(restore.queue.get(), restore._sentinel)

    def test__we_create_a_single_producer_thread(self):
        restore = S3Restore()
        mock_bucket_contents = [Mock(), Mock(), Mock()]
        producer_thread = restore._create_single_producer_thread(mock_bucket_contents)
        # has producer target
        self.assertEqual(producer_thread._Thread__target, restore.producer)

    def test__we_create_as_many_consumer_threads_as_there_are_objects_in_an_aws_objects_page(self):
        restore = S3Restore()
        aws_objects_page_size = restore.aws.PAGE_SIZE

        consumer_threads = restore._create_consumer_threads()
        number_of_consumer_threads = len(consumer_threads)

        self.assertEqual(number_of_consumer_threads, aws_objects_page_size)

