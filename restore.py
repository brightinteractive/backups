#!/usr/bin/env python

import boto3

def create_aws_session():
    return boto3.session.Session()
