#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open('requirements.txt') as f:
    REQUIRES = f.readlines()

with open('test-requirements.txt') as f:
    TESTS_REQUIRES = f.readlines()

with open('VERSION') as f:
    VERSION = f.read()

setup(
    name='unbound-zone-feeder',
    version=VERSION,
    description='Scheduled zone feeder for unbound DNS servers',
    long_description='',
    url='https://www.github.com/UiP9AV6Y/docker-unbound-zone-feeder',
    author='Gordon Bleux',
    author_email='UiP9AV6Y+uzf@protonmail.com',
    license='MIT',
    packages=['unbound_zone_feeder',],
    test_suite="tests",
    extras_require={},
    setup_requires=[],
    tests_require=TESTS_REQUIRES,
    install_requires=REQUIRES,
    entry_points = {
        'console_scripts': ['unbound-zone-feeder=unbound_zone_feeder.__main__:main'],
    },
    keywords=[
        'schedule', 'blackhole', 'dns', 'unbound',
    ],
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: System Administrators',
    'Topic :: Internet :: Name Service (DNS)',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Natural Language :: English',
    ],
)
