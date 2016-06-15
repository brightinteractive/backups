#!/usr/bin/env python

import boto3

class S3Resource(object):
    def __init__(self):
        session = create_aws_session()
        resource = create_s3_resource(session)

    @classmethod
    def create_aws_session(cls):
        return boto3.session.Session()

    @classmethod
    def create_s3_resource(cls, session=None):
        session = session or cls.create_aws_session()
        return session.resource('s3')

