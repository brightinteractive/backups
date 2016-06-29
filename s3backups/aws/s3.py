#!/usr/bin/env python

from Queue import Queue
from threading import Thread

from s3backups.utils.dry_run import DryRun
from api import AWSApiWrapper
from metrics import AWSMetrics


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

