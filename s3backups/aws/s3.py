#!/usr/bin/env python

from Queue import Queue
from threading import Thread

from s3backups.utils.dry_run import DryRun
from api import AWSApiWrapper
from metrics import AWSMetrics
from glacier import GlacierPath


class ObjectRestore(object):
    RestoreRequest = { 'Days' : 7 }

    @classmethod
    @AWSMetrics.counter('number_of_objects')
    def restore_s3_object(cls, s3_obj_summary):
        if cls._object_should_be_restored(s3_obj_summary):
            return cls.call_restore(s3_obj_summary)

    @classmethod
    @AWSMetrics.counter('number_of_glacier_objects', when_returns=True)
    def is_glacier_type(cls, s3_obj_summary):
        return s3_obj_summary.storage_class == 'GLACIER'

    @classmethod
    @AWSMetrics.counter('number_of_unrestored_objects', when_returns=True)
    def is_not_restored(cls, s3_obj_summary):
        s3_obj_detail = s3_obj_summary.Object()
        return s3_obj_detail.restore is None

    @classmethod
    @DryRun.ignore()
    @AWSMetrics.status_code('restore_object_status_codes')
    @AWSMetrics.counter('number_of_requests')
    def call_restore(cls, s3_obj_summary):
        return s3_obj_summary.restore_object(RestoreRequest=cls.RestoreRequest)

    @classmethod
    def _object_should_be_restored(cls, s3_obj_summary):
        return cls.is_glacier_type(s3_obj_summary) and cls.is_not_restored(s3_obj_summary)


class BucketRestore(object):
    _sentinel = object()
    _queue = Queue()

    def __init__(self):
       self.aws = AWSApiWrapper()
       self.MAX_THREAD_COUNT = self.aws.PAGE_SIZE

    @classmethod
    def reset(cls):
        cls._queue = Queue()

    def bucket(self, bucket):
        objects = self._get_s3_objects_by_bucket_name(bucket)
        self._restore_objects_with_threads(objects)

    def producer(self, objects):
        for object in objects:
            self._queue.put(object)
        self._queue.put(self._sentinel)

    def consumer(self):
        while True:
            data  = self._queue.get()
            if data == self._sentinel:
                self._queue.put(self._sentinel)
                break
            ObjectRestore.restore_s3_object(data)

    @classmethod
    def _start_threads(cls, threads):
        for thread in threads:
            thread.start()
        return threads

    @classmethod
    def _block_until_threads_finish(cls, threads):
        for thread in threads: thread.join()
        return threads

    def _restore_objects_with_threads(self, objects):
        producer_thread = self._create_single_producer_thread(objects)
        consumer_threads = self._create_consumer_threads()

        producer_thread.start()
        self._start_threads(consumer_threads)

        self._block_until_threads_finish(consumer_threads)

    def _create_single_producer_thread(self, objects):
        thread = Thread(target=self.producer, args=(objects,))
        thread.daemon = True
        return thread

    def _create_consumer_threads(self):
        threads = []
        for _ in range(self.MAX_THREAD_COUNT):
            thread = Thread(target=self.consumer)
            thread.daemon = True
            threads.append(thread)
        return threads

    def _get_s3_objects_by_bucket_name(self, bucket):
        return self.aws.get_s3_objects_by_bucket_name(bucket)


class Restore(Thread):
    def __init__(self, bucket, *args, **kwargs):
        super(Restore, self).__init__(*args, **kwargs)
        self.restore = BucketRestore()
        self.daemon = True
        self.bucket = bucket

    def run(self):
        self.restore.bucket(self.bucket)


class ObjectCopy(object):
    @classmethod
    def has_timestamp(cls, s3_object):
        key, timestamp = GlacierPath.split(s3_object.key)
        return bool(timestamp)

    @classmethod
    def extract_key(cls, s3_object):
        key, timestamp = GlacierPath.split(s3_object.key)
        return key

    @classmethod
    def have_identical_keys(cls, s3_object_A, s3_object_B):
        key_A, timestamp_A = GlacierPath.split(s3_object_A.key)
        key_B, timestamp_B = GlacierPath.split(s3_object_B.key)
        return (key_A == key_B)

    @classmethod
    def get_latest(cls, s3_object_A, s3_object_B):
        timestamp_A = GlacierPath.datetime(s3_object_A.key)
        timestamp_B = GlacierPath.datetime(s3_object_B.key)
        try:
            if timestamp_A > timestamp_B:
                return s3_object_A
            else:
                return s3_object_B
        except TypeError:
            if timestamp_A:
                return s3_object_A
            else:
                return s3_object_B


class BucketCopy(object):
    def __init__(self, bucket_name):
        self.aws = AWSApiWrapper()
        self.bucket = bucket_name 

        self._latest_object = None

    def copy(self, bucket_name):
        objects = self._get_s3_objects_by_bucket_name(bucket_name)
        self._copy_objects(objects)

    def copy_object(self, s3_object):
        return self.aws.copy(s3_object, self.bucket)

    def copy_latest(self):
        if self._latest_object:
            latest_object_key = ObjectCopy.extract_key(self._latest_object)
            self.copy_object(self._latest_object, new_key=latest_object_key) 
            self._latest_object = None

    def _copy_objects(self, objects):
        for s3object in objects:
            if not ObjectCopy.has_timestamp(s3object):
                self.copy_object(s3object)
            else:
                if self._latest_object:
                    if ObjectCopy.have_identical_keys(s3object, self._latest_object):
                        self._latest_object = ObjectCopy.get_latest(s3object, self._latest_object)
                    else:
                        self.copy_latest()
                else:
                    self._latest_object = s3object

        self._flush()

    def _flush(self):
        self.copy_latest()

    def _get_s3_objects_by_bucket_name(self, bucket):
        return self.aws.get_s3_objects_by_bucket_name(bucket)

