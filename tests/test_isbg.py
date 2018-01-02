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


def test_ISBGError():
    """Test a ISBGError object creation."""
    import atexit
    atexit._run_exitfuncs()  # free the lockfile
    foo = isbg.ISBGError(0, "foo")
    try:
        raise foo
    except isbg.ISBGError as err:
        assert err.exitcode == 0
        assert err.message == "foo"


def test_isbg_run_01():
    """Test isbg_run()."""
    import atexit
    atexit._run_exitfuncs()  # free the lockfile
    try:
        isbg.isbg_run()
        raise "error. It should raise ISBGError"
    except isbg.ISBGError as err:
        assert err.exitcode == 0
        assert err.message.startswith("You need to specify your imap passw")


def test_isbg_run_02(capsys):
    """Test isbg_run() with __name__ = __main__."""
    import atexit
    atexit._run_exitfuncs()  # free the lockfile
    with mock.patch.object(isbg, "__name__", "__main__"):
        with pytest.raises(SystemExit) as wrapped_exit:
            isbg.isbg_run()
        assert wrapped_exit.type == SystemExit
        out, err = capsys.readouterr()
        assert err.startswith("You need to specify your imap passw")
