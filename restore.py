#!/usr/bin/env python

import argparse


def create_parser():
    parser = argparse.ArgumentParser(description='AssetBank S3 restore from Glacier')
    parser.add_argument('bucket', help='name of backup bucket to restore')
    return parser

