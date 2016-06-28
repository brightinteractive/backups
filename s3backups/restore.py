#!/usr/bin/env python

import argparse

from config import EnvironmentVariables
from parser import parse_args
from threading import Thread
from aws import S3Restore, AWSMetrics
from dry_run import DryRun
from jinja2 import Environment, PackageLoader
from time import sleep
import curses


class Restore(Thread):
    def __init__(self, bucket, *args, **kwargs):
        super(Restore, self).__init__(*args, **kwargs)
        self.restore = S3Restore()
        self.daemon = True
        self.bucket = bucket

    def run(self):
        self.restore.bucket(self.bucket)


class Display(object):
    REFRESH_PERIOD = 0.2

    def __init__(self, thread, window):
        self.thread = thread
        self.window = window
        self.jinja_env = Environment(loader=PackageLoader('restore', 'templates'))

    def progress(self):
        while self.thread.isAlive():
            self.update()
            sleep(self.REFRESH_PERIOD)
        window.getkey()
        curses.endwin()

    def update(self):
        context = self.generate_context()
        template = self.jinja_env.get_template('report.scr')
        page = template.render(**context)
        self.window.addstr(0, 0, page)
        self.window.refresh()

    def generate_context(self):
        context = dict()
        context.update(AWSMetrics.report)
        context['bucket_name'] = self.thread.bucket
        return context


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

