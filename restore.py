#!/usr/bin/env python

import boto3

class S3Resource(object):
    def __init__(self, session=None, resource=None):
        self.session = session or self.create_aws_session()
        self.resource = resource or self.create_s3_resource(self.session)

    @classmethod
    def create_aws_session(cls):
        return boto3.session.Session()

    @classmethod
    def create_s3_resource(cls, session=None):
        session = session or cls.create_aws_session()
        return session.resource('s3')

    def get_s3_bucket_by_name(self, bucket_name):
        return self.resource.Bucket(bucket_name)

