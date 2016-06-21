#!/usr/bin/env python

import argparse

from aws.aws import S3Restore
from config import EnvironmentVariables
from parser import parse_args


def setup():
    EnvironmentVariables.inject()

def main(args):
    bucket = args.bucket
    restore = S3Restore()
    restore.bucket(bucket)

if __name__ == '__main__':
    setup()
    args = parse_args()
    main(args)

