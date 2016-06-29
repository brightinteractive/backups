#!/usr/bin/env python

import unittest

from s3backups.dry_run import DryRun

from mock import Mock, patch

class DryRunTest(unittest.TestCase):
    def test__we_can_prevent_a_function_call_when_we_are_in_dry_run_mode(self):
        DryRun.state = True
        
        @DryRun.ignore()
        def throw_exeception():
            raise Exception()

        try:
            throw_exeception()
        except:
            self.fail('function should not throw an Eception, it should be ignored')

    def test__we_can_dont_prevent_a_function_call_when_we_are_not_in_dry_run_mode(self):
        DryRun.state = False
        
        @DryRun.ignore()
        def throw_exeception():
            raise Exception()
        
        with self.assertRaises(Exception):
            throw_exeception()

