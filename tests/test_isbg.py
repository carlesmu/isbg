#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_isbg.py
#  This file is part of isbg.
#
#  Copyright 2018 Carles Muñoz Gorriz <carlesmu@internautas.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

"""Test cases for isbg module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# With atexit._run_exitfuncs()  we free the lockfile, but we lost coverage
# statistics.

import os
import sys
try:
    import pytest
except ImportError:
    pass

import base64

# We add the upper dir to the path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from isbg import isbg  # noqa: E402


def test_ISBGError():
    """Test a ISBGError object creation."""
    with pytest.raises(isbg.ISBGError, match="foo"):
        raise isbg.ISBGError(0, "foo")


class TestISBG(object):
    """Tests for class ISBG."""

    def test_set_filename(self):
        """Test set_filename."""
        sbg = isbg.ISBG()
        filename = isbg.ISBG.set_filename(sbg.imapsets, "track")
        assert os.path.dirname(filename) != ""
        assert os.path.basename(filename) != ""
        assert os.path.basename(filename).startswith("track")
        filename = isbg.ISBG.set_filename(sbg.imapsets, "password")
        assert os.path.dirname(filename) != ""
        assert os.path.basename(filename) != ""
        assert os.path.basename(filename).startswith(".isbg-")

    def test___do_passwordhash(self):
        """Test __do_passwordhash."""
        sbg = isbg.ISBG()
        sbg.do_passwordhash()
        assert len(sbg.passwordhash) == sbg.passwordhashlen

    def test_removelock(self):
        """Test removelock."""
        sbg = isbg.ISBG()
        sbg.removelock()
        assert os.path.exists(sbg.lockfilename) is False, \
            "File should not exist."
        lockfile = open(sbg.lockfilename, 'w')
        lockfile.write(repr(os.getpid()))
        lockfile.close()
        assert os.path.exists(sbg.lockfilename), "File should exist."
        sbg.removelock()
        assert os.path.exists(sbg.lockfilename) is False, \
            "File should not exist."

    def test_setpwd(self):
        """Test setpwd."""
        sbg = isbg.ISBG()
        sbg.do_passwordhash()
        # We construct a password:
        pas = sbg.setpw(u"test", sbg.passwordhash)
        pas = pas.encode("base64")
        res = """QVMVEGQ2ODYxMzdjODY0NWQ0NDAyNDA5NmEwZWQ0NDEwNjdlYmQxMTY0ZGUyMDliMWQ1ZjgzODMw
YzBjMDBlYWE3OWI1NzU1MzEzZmUzNmU3M2YzMGM5MmU1NmE2YjFlMDM0NTIxZTg1MWFlNzM0MTgy
NDQ5NDNlYWU1N2YwMzI0M2VhYTI0MTAyYTgwOWZkYjA5ZTBmZjkzM2UwYzIwZWI4YzhiZjZiMTRh
NTZlOTUwYjUyNjM5MzdhNTNjMWNmOWFjNGY3ODQyZDE4MWMxNWNkMDA0MjRkODZiNmQ4NzZjM2Ez
NTk2YTEyMDIyYTM4ZDc3YjM3Mzk2OGNlMzc1Yg==
"""
        assert pas == res, "Unexpected password encoded"

    def test_getpwd(self):
        """Test getpwd."""
        sbg = isbg.ISBG()
        sbg.do_passwordhash()
        pas = """QVMVEGQ2ODYxMzdjODY0NWQ0NDAyNDA5NmEwZWQ0NDEwNjdlYmQxMTY0ZGUyMDliMWQ1ZjgzODMw
YzBjMDBlYWE3OWI1NzU1MzEzZmUzNmU3M2YzMGM5MmU1NmE2YjFlMDM0NTIxZTg1MWFlNzM0MTgy
NDQ5NDNlYWU1N2YwMzI0M2VhYTI0MTAyYTgwOWZkYjA5ZTBmZjkzM2UwYzIwZWI4YzhiZjZiMTRh
NTZlOTUwYjUyNjM5MzdhNTNjMWNmOWFjNGY3ODQyZDE4MWMxNWNkMDA0MjRkODZiNmQ4NzZjM2Ez
NTk2YTEyMDIyYTM4ZDc3YjM3Mzk2OGNlMzc1Yg==
"""
        pas = base64.b64decode(pas).decode("utf-8")
        ret = sbg.getpw(pas, sbg.passwordhash)
        assert ret == u"test"

    def test_do_isbg(self):
        """Test do_isbg."""
        sbg = isbg.ISBG()
        with pytest.raises(isbg.ISBGError, match="specify your imap password",
                           message=("It should rise a specify imap password " +
                                    "ISBGError")):
            sbg.do_isbg()
