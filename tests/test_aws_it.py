#!/usr/bin/env python

import unittest, os, collections

import boto3

from s3backups.aws import AWSApiWrapper


class AWSApiWrapperTestsIT(unittest.TestCase):
    def test__we_can_create_an_aws_session(self):
        aws = AWSApiWrapper()
        session = aws.create_aws_session()
        self.assertIsInstance(session, boto3.session.Session)

    def test__we_can_get_an_s3_resource(self):
        aws = AWSApiWrapper()
        resource = aws.create_s3_resource()
        self.assertIsInstance(resource, boto3.resources.base.ServiceResource)

    def test__we_can_get_all_objects_within_a_named_bucket(self):
        
        ''' For this test to pass there must be a bucket called:
            test-we-can-get-all-objects-from-a-named-bucket
        and it must have 3 objects in it: one.txt, two.txt, three.txt
        '''
        bucket = 'test-we-can-get-all-objects-from-a-named-bucket'
        expected_object_keys = set(['one.txt', 'two.txt', 'three.txt'])
        aws = AWSApiWrapper()

        objects = aws.get_s3_objects_by_bucket_name(bucket)

        returned_object_keys = set([object.key for object in objects])
        self.assertEqual(expected_object_keys, returned_object_keys)

    def test__we_can_copy_an_object_to_another_bucket(self):
        ''' For this tet to pass there must be a bucket called test-copy-source and test-copy-dest, 
            test-copy-dest must contain a file called one.txt
        '''
        aws = AWSApiWrapper()
        # delete all objects in destination bucket
        for object in aws.get_s3_objects_by_bucket_name('test-copy-dest'): object.delete()
        src = aws.create_s3_object('test-copy-source', 'one.txt') 
        dest = aws.create_s3_object('test-copy-dest', 'one.txt') 

        aws.copy(src, 'test-copy-dest')

        bucket = aws.get_s3_bucket_by_name('test-copy-dest')
        dest.get()

