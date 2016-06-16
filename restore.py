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

