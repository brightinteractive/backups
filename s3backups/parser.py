#!/usr/bin/env python

import argparse

def create_parser():
    parser = argparse.ArgumentParser(description='AssetBank S3 restore from Glacier')
    parser.add_argument('bucket', help='name of backup bucket to restore')
    parser.add_argument('--dry-run', action='store_true', help='run restore in read only mode (no restore requests are sent)')
    return parser

def parse_args():
    parser = create_parser()
    return parser.parse_args()
