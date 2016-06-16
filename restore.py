#!/usr/bin/env python

import boto3

class S3Resource(object):
    def __init__(self):
        self.session = self.create_aws_session()
        self.resource = self.create_s3_resource(self.session)

    @classmethod
    def create_aws_session(cls):
        return boto3.session.Session()

    @classmethod
    def create_s3_resource(cls, session):
        return session.resource('s3')

    def get_s3_bucket_by_name(self, bucket_name):
        return self.resource.Bucket(bucket_name)

    def get_s3_objects_by_bucket_name(self, bucket_name):
        bucket = self.get_s3_bucket_by_name(bucket_name)
        return bucket.objects.all()

class S3Restore(object):
    RestoreRequest = { 'Days' : 7 }

    @classmethod
    def restore_s3_object(cls, s3_obj_summary):
        if cls.is_glacier_type(s3_obj_summary) and cls.is_not_restored(s3_obj_summary):
            cls.call_restore(s3_obj_summary)

    @classmethod
    def is_glacier_type(cls, s3_obj_summary):
        return s3_obj_summary.storage_class == 'GLACIER'

    @classmethod
    def is_not_restored(cls, s3_obj_summary):
        s3_obj_detail = s3_obj_summary.Object()
        return s3_obj_detail.restore is None

    @classmethod
    def call_restore(cls, s3_obj_summary):
        return s3_obj_summary.restore_object(RestoreRequest=cls.RestoreRequest)

