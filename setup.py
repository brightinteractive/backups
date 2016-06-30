#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='s3backups',
        version='0.1',
        description='',
        url='http://github.com/brightinteractive/s3backups',
        author='Anthony S.G. Evans',
        author_email='anthony@bright-interactive.com',
        license='Copyright Bright Interactive',
        packages=find_packages(),
        entry_points={
            'console_scripts': ['s3backups=s3backups.__main__:main',],
            },
        install_requires=[
        "boto3",
        "Jinja2",
        "s3backups"
        ],
        include_package_data = True, 
        zip_safe=False)
