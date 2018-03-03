#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Installation and build information for isbg."""

import ast
import os
import re

from setuptools import setup

LDESC = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# We get the version from isbg/isbg.py
_VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')
with open('isbg/isbg.py', 'rb') as f:
    _VERSION = str(ast.literal_eval(_VERSION_RE.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='isbg',
    version=_VERSION,  # to change it, change isbg/isbg.py: __version__
    description=(
        'a script that makes it easy to scan an IMAP inbox for spam using'
        + 'SpamAssassin and get your spam moved to another folder.'),
    long_description=LDESC,
    keywords='email imap spamassasin filter',
    author='Thomas Lecavelier',
    author_email='thomas@lecavelier.name',
    license='See LICENCE file.',
    packages=['isbg'],
    entry_points={
        'console_scripts': [
            'isbg = isbg.__main__:main',
            'sa_unwrap = isbg.sa_unwrap:run',
        ]
    },
    install_requires=['docopt', 'chardet'],
    tests_require=['pytest', 'mock', 'spamc'],
    url='https://github.com/isbg/isbg',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Email :: Post-Office :: IMAP',
        'Topic :: Communications :: Email :: Filters',
        'Topic :: Utilities',
    ]
)
