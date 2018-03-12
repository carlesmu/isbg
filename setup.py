#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Installation and build information for isbg."""

import ast
import os
import re
import subprocess
import sys

from distutils.command.build import build as _build
from setuptools import setup


class Build(_build):
    """Customize setuptools build command."""

    def run(self):
        """Create the docs (html and manpage)."""
        ret = subprocess.call(['make', 'docs'])
        if ret != 0:
            sys.stderr.write(u"Error in call to «make doc»")
            sys.exit(ret)
        _build.run(self)


# We get the isbg README.rst as package long description:
with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'rb') as f:
    LDESC = f.read().decode('utf-8')

# We get the version from isbg/isbg.py:
_VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')
with open(os.path.join(os.path.dirname(__file__), 'isbg/isbg.py'), 'rb') as f:
    _VERSION = str(ast.literal_eval(_VERSION_RE.search(
        f.read().decode('utf-8')).group(1)))

# Only setup_require pytest-runner when test are called
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

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
    cmdclass={
        'build': Build,
    },
    install_requires=['docopt'],
    extras_require={
        'chardet': ['chardet'],
        'cchardet': ['cchardet'],
    },
    setup_requires=pytest_runner,
    tests_require=['pytest', 'mock', 'pytest-cov'],
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
