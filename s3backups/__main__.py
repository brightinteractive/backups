#!/usr/bin/env python

from config import EnvironmentVariables
from parser import parse_args
from utils.dry_run import DryRun
import curses

from aws import AWSMetrics, Restore
from display import Display


def setup():
    EnvironmentVariables.inject()
    settings = parse_args()
    DryRun.state = getattr(settings, 'dry_run', False)
    return settings

def main(window, settings):
    thread = Restore(settings.bucket)
    thread.start()

    display = Display(thread, window)
    display.progress()


if __name__ == '__main__':
    settings = setup()
    curses.wrapper(main, settings)

