#!/usr/bin/env python

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import s3backups


class PyTest(TestCommand):
    '''installs minimal requirements and runs tests'''
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--verbose', './tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))

tests_require = [
        'pytest', 
        'mock'
        ]

install_requires = [
        "boto3>=1.3.1",
        "Jinja2>=2.8",
        ]

setup(name='s3backups',
        version=s3backups.__version__,
        description=s3backups.__doc__.strip(),
        download_url='http://github.com/brightinteractive/s3backups',
        author=s3backups.__author__,
        author_email='anthony@bright-interactive.com',
        license='Copyright Bright Interactive',
        packages=find_packages(),
        entry_points={
            'console_scripts': ['s3backups=s3backups.__main__:main',],
            },
        install_requires=install_requires,
        tests_require=tests_require,
        cmdclass={'test':PyTest},
        include_package_data = True, 
        zip_safe=False, 
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Utilities'
            ],
        )
