#!/usr/bin/env python

import argparse

from config import EnvironmentVariables
from parser import parse_args


def setup(settings):
    EnvironmentVariables.inject()
    DryRun.state = getattr(settings, 'dry_run', False)


if __name__ == '__main__':
    settings = parse_args()
    setup(settings)
