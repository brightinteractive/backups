#!/usr/bin/env python

from time import sleep
import curses
from jinja2 import Environment, PackageLoader

from aws import AWSMetrics


class Display(object):
    REFRESH_PERIOD = 0.2

    def __init__(self, thread, window):
        self.thread = thread
        self.window = window
        self.jinja_env = Environment(loader=PackageLoader('s3backups', 'templates'))

    def progress(self):
        while self.thread.isAlive():
            self.update()
            sleep(self.REFRESH_PERIOD)
        self.window.getkey()
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
