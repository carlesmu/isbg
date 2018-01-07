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


def test_shorten():
    """Test the shorten function."""
    # We try with dicts:
    dic = {'1': 'Option 1', '2': 'Option 2', '3': 'Option 3'}
    assert dic == isbg.shorten(dic, 8), "The dicts should be the same."
    dic2 = isbg.shorten(dic, 7)
    assert dic != dic2, "The dicts should be diferents."
    for k in ['1', '2', '3']:
        assert dic2[k] == '\'Opt...', "Unexpected shortened string."

    # We try with lists:
    ls = ['Option 1', 'Option 2', 'Option 3']
    assert ls == isbg.shorten(ls, 8)
    ls2 = isbg.shorten(ls, 7)
    for k in ls2:
        assert k == '\'Opt...'

    # We try with strings:
    assert "Option 1" == isbg.shorten("Option 1", 8), \
        "Strings should be the same."
    assert "\'Opt..." == isbg.shorten("Option 1", 7), \
        "Strings should be diferents."

    # Others:
    with pytest.raises(TypeError, message="None should raise a TypeError."):
        isbg.shorten(None, 8)
    with pytest.raises(TypeError, message="None should raise a TypeError."):
        isbg.shorten(None, 7)
    with pytest.raises(TypeError, message="None should raise a TypeError."):
        isbg.shorten(False, 8)
    with pytest.raises(TypeError, message="None should raise a TypeError."):
        isbg.shorten(True, 7)
    with pytest.raises(TypeError, message="int should raise a TypeError."):
        isbg.shorten(1, 7)
    with pytest.raises(TypeError, message="float should raise a TypeError."):
        isbg.shorten(1.0, 7)
    with pytest.raises(ValueError, message="length should be at least 3."):
        isbg.shorten("123", 2)


def test_ISBGError():
    """Test a ISBGError object creation."""
    with pytest.raises(isbg.ISBGError, match="foo"):
        raise isbg.ISBGError(0, "foo")


def test_isbg_run():
    """Test isbg_run()."""
    # Remove pytest options:
    args = sys.argv[:]
    del sys.argv[1:]
    sys.argv.append("--ignorelockfile")

    with pytest.raises(isbg.ISBGError,
                       match="Missed required option: --imaphost",
                       message="Not error or unexpected error message"):
        isbg.isbg_run()

    with mock.patch.object(isbg, "__name__", "__main__"):
        with pytest.raises(SystemExit, match="0",
                           message="Not error or unexpected error"):
            isbg.isbg_run()

    sys.argv.append("--version")
    with mock.patch.object(isbg, "__name__", "__main__"):
        with pytest.raises(SystemExit,
                           message="Not error or unexpected error"):
            isbg.isbg_run()

    # Restore pytest options:
    sys.argv = args[:]
