#!/usr/bin/env python
from __future__ import print_function

import fileinput, sys, re
from datetime import datetime

'''
AWS Glacier objects are date-time stamped. The stamp conforms to the pattern:
    _yyyy-mm-dd hh-mm-ss
    _2014-02-13 18:19:06
The stamp is appended to the object key name, for example:
    some_picture.jpeg_2014-02-13 18:19:06
This script removes the date-time stamp from the object key and returns the object key.
'''

class GlacierPath(object):

    glacier_object_pattern  = r'^(?P<object_key>.*)_(?P<datetime_stamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$'
    regexp = re.compile(glacier_object_pattern)

    @classmethod
    def split(cls, path):
        glacier_path = cls._split_glacier_path(path)
        return glacier_path.get('object_key'), glacier_path.get('datetime_stamp')

    @classmethod
    def datetime(cls, path):
        return cls._generate_datetime_from_glacier_path(path)

    @classmethod
    def key(cls, path):
        object_key, datetime_suffix = cls.split(path)
        return object_key

    @classmethod
    def _split_glacier_path(cls, glacier_path):
        default_object_key = glacier_path
        output = { 'object_key' : default_object_key }
        match = re.match(cls.regexp, glacier_path) 
        if match:
            output.update(match.groupdict())
        return output

    @classmethod
    def _generate_datetime_from_glacier_path(cls, path):
        object_key, datetime_suffix = cls.split(path)
        if datetime_suffix:
            return datetime.strptime(datetime_suffix, '%Y-%m-%d %H:%M:%S')

def main(paths):
    return map(GlacierPath.key, paths)

if __name__ == '__main__':
    commandline_input = sys.argv[1:] or fileinput.input()
    paths  = [line.strip() for line in commandline_input]
    keys = main(paths)
    map(print, keys)

