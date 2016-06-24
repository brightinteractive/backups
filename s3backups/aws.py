#!/usr/bin/env python

import argparse
from Queue import Queue
from threading import Thread

import boto3

from metrics import Metrics


class AWSMetrics(Metrics):
    available_metrics = (
            'number_of_glacier_objects',
            'number_of_unrestored_objects',
            'restore_object_status_codes',
            'number_of_objects',
            'number_of_requests'
            )

    @classmethod
    def status_code(cls, metric):
        if metric not in cls.available():
            raise AttributeError('\'%s\' is not an available metric.'% metric)

        def wrapper(fn):
            def _status_code(*args, **kwargs):
                response = fn(*args, **kwargs)
                status_code = response['ResponseMetadata']['HTTPStatusCode']
                with cls._lock:
                    if cls.report[metric]:
                        if cls.report[metric].has_key(status_code):
                            cls.report[metric][status_code] += 1
                        else:
                            cls.report[metric][status_code] = 1
                    else:
                        cls.report[metric] = { status_code : 1 }
                return response
            return _status_code
        return wrapper


AWSMetrics.reset()


class AWSApiWrapper(object):
    PAGE_SIZE = 1000
    def __init__(self):
        self.session = self.create_aws_session()
        self.resource = self.create_s3_resource()

    def create_aws_session(self):
        return boto3.session.Session()

    def create_s3_resource(self):
        return self.session.resource('s3')

    def get_s3_bucket_by_name(self, bucket_name):
        return self.resource.Bucket(bucket_name)

    def get_s3_objects_by_bucket_name(self, bucket_name):
        bucket = self.get_s3_bucket_by_name(bucket_name)
        return bucket.objects.page_size(count=self.PAGE_SIZE)


class S3Restore(object):
    _sentinel = object()
    queue = Queue()

    RestoreRequest = { 'Days' : 7 }

    def __init__(self):
       self.aws = AWSApiWrapper()
       self.MAX_THREAD_COUNT = self.aws.PAGE_SIZE
    
    @classmethod
    @AWSMetrics.counter('number_of_objects')
    def restore_s3_object(cls, s3_obj_summary):
        if cls._object_should_be_restored(s3_obj_summary):
            return cls.call_restore(s3_obj_summary)

    @classmethod
    def _object_should_be_restored(cls, s3_obj_summary):
        return cls.is_glacier_type(s3_obj_summary) and cls.is_not_restored(s3_obj_summary)

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
    def reset(cls):
        cls.queue = Queue()

    @classmethod
    @AWSMetrics.status_code('restore_object_status_codes')
    @AWSMetrics.counter('number_of_requests')
    def call_restore(cls, s3_obj_summary):
        return s3_obj_summary.restore_object(RestoreRequest=cls.RestoreRequest)

    @classmethod
    def _start_threads(cls, threads):
        for thread in threads: thread.start()
        return threads

    @classmethod
    def _block_until_threads_finish(cls, threads):
        for thread in threads: thread.join()
        return threads

    def bucket(self, bucket):
        objects = self._get_s3_objects_by_bucket_name(bucket)
        self._restore_objects_with_threads(objects)

    def producer(self, objects):
        for object in objects:
            self.queue.put(object)
        self.queue.put(self._sentinel)

    def consumer(self):
        while True:
            data  = self.queue.get()
            if data == self._sentinel:
                self.queue.put(self._sentinel)
                break
            self.restore_s3_object(data)

    def _restore_objects_with_threads(self, objects):
        producer_thread = self._create_single_producer_thread(objects)
        consumer_threads = self._create_consumer_threads()
        
        producer_thread.start()
        self._start_threads(consumer_threads)

        self._block_until_threads_finish(consumer_threads)

    def _create_single_producer_thread(self, objects):
        return Thread(target=self.producer, args=(objects,))

    def _create_consumer_threads(self):
        return [Thread(target=self.consumer) for _ in range(self.MAX_THREAD_COUNT)]

    def _get_s3_objects_by_bucket_name(self, bucket):
        return self.aws.get_s3_objects_by_bucket_name(bucket)

