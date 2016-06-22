#!/usr/bin/env python

import argparse

import boto3

from metrics import Metrics


class AWSMetrics(Metrics):
    available_metrics = ('number_of_objects', 'number_of_requests')

AWSMetrics.reset()

class AWSApiWrapper(object):
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
        return bucket.objects.all()


class S3Restore(object):
    '''This class wraps Boto3 Object endpoints, see official Boto3 documentation:
        http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Object
    '''
    RestoreRequest = { 'Days' : 7 }
    def __init__(self):
       self.aws = AWSApiWrapper()
    
    @classmethod
    @AWSMetrics.counter('number_of_objects')
    def restore_s3_object(cls, s3_obj_summary):
        if cls._object_should_be_restored(s3_obj_summary):
            return cls.call_restore(s3_obj_summary)

    @classmethod
    def _object_should_be_restored(cls, s3_obj_summary):
        return cls.is_glacier_type(s3_obj_summary) and cls.is_not_restored(s3_obj_summary)

    @classmethod
    def is_glacier_type(cls, s3_obj_summary):
        return s3_obj_summary.storage_class == 'GLACIER'

    @classmethod
    def is_not_restored(cls, s3_obj_summary):
        s3_obj_detail = s3_obj_summary.Object()
        return s3_obj_detail.restore is None

    @classmethod
    @AWSMetrics.counter('number_of_requests')
    def call_restore(cls, s3_obj_summary):
        return s3_obj_summary.restore_object(RestoreRequest=cls.RestoreRequest)

    def bucket(self, bucket):
        objects = self.aws.get_s3_objects_by_bucket_name(bucket)
        for object in objects:
           self.restore_s3_object(object)


