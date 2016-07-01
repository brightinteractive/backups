#!/usr/bin/env python

import sys
from parser import parse_args
from utils.dry_run import DryRun
import curses

from aws import AWSMetrics, Restore
from display import Display


def setup():
    settings = parse_args()
    DryRun.state = getattr(settings, 'dry_run', False)
    return settings

def restore(window, settings):
    thread = Restore(settings.bucket) 
    thread.start()

    display = Display(thread, window)
    display.progress()

def main():
    settings = setup()
    curses.wrapper(restore, settings)


if __name__ == '__main__':
    sys.exit(main())

