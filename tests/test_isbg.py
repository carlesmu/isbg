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

# With atexit._run_exitfuncs()  we free the lockfile, but we lost coverage
# statistics.

import os
import sys
try:
    import pytest
except ImportError:
    pass

try:
    from unittest import mock  # Python 3
except ImportError:
    import mock                # Python 2

# We add the upper dir to the path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from isbg import isbg  # noqa: E402


def test_hexof_dehexof():
    """Test the dehexof function."""
    dehex = isbg.dehexof("F02f")
    assert dehex == "\xf0/"
    assert isbg.hexof(dehex) == "f02f"
    with pytest.raises(ValueError,
                       match=repr("G") + " is not a valid hexadecimal digit",
                       message="Not error or unexpected error message"):
        isbg.dehexof("G")


def test_ISBGError():
    """Test a ISBGError object creation."""
    with pytest.raises(isbg.ISBGError, match="foo"):
        raise isbg.ISBGError(0, "foo")


def test_isbg_run_01():
    """Test isbg_run()."""
    # Remove pytest options:
    args = sys.argv
    del sys.argv[1:]

    with pytest.raises(isbg.ISBGError,
                       match="You need to specify your imap password",
                       message="Not error or unexpected error message"):
        isbg.isbg_run()

    with mock.patch.object(isbg, "__name__", "__main__"):
        with pytest.raises(SystemExit, match="30",
                           message="Not error or unexpected error message"):
            isbg.isbg_run()

    # Restore pytest options:
    sys.argv = args
