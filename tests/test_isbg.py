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


class TestISBG(object):
    """Tests for class ISBG."""

    def test_parse_args(self):
        """Test parse_args."""
        # Remove pytest options:
        orig_args = sys.argv[:]

        # Parse command line:
        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--flag",
                   "--noninteractive"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        sbg.parse_args()
        assert sbg.imapsets.host == "localhost"
        assert sbg.imapsets.user == "anonymous"
        assert sbg.imapsets.passwd == "none"

        # Parse with unknown option
        del sys.argv[1:]
        for op in ["--foo"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        with pytest.raises(SystemExit, match="[options]",
                           message="It should rise a docopt SystemExit"):
            sbg.parse_args()

        # Parse with bogus deletehigherthan
        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--deletehigherthan",
                   "0"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        with pytest.raises(isbg.ISBGError, match="too small",
                           message="It should rise a too small ISBGError"):
            sbg.parse_args()

        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--deletehigherthan",
                   "foo"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        with pytest.raises(isbg.ISBGError, match="Unrecognized score",
                           message=("It should rise a unrecognized score" +
                                    "ISBGError")):
            sbg.parse_args()

        # Parse with ok deletehigherthan
        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--deletehigherthan",
                   "8"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        sbg.parse_args()
        assert sbg.deletehigherthan == 8.0

        # Parse with bogus maxsize
        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--maxsize", "0"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        with pytest.raises(isbg.ISBGError, match="too small",
                           message="It should rise a too small ISBGError"):
            sbg.parse_args()

        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--maxsize", "foo"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        with pytest.raises(isbg.ISBGError, match="Unrecognised size",
                           message=("It should rise a Unrecognised size" +
                                    "ISBGError")):
            sbg.parse_args()

        # Parse with ok maxsize
        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--maxsize", "12000"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        sbg.parse_args()
        assert sbg.maxsize == 12000

        # Parse with bogus partialrun
        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--partialrun", "0"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        with pytest.raises(isbg.ISBGError, match="equal to 1 or higher",
                           message=("It should rise a equial to 1 or higher " +
                                    "ISBGError")):
            sbg.parse_args()

        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--dryrun", "--partialrun", "foo"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        with pytest.raises(ValueError, match="invalid literal",
                           message=("It should rise a invalid literal " +
                                    "ValueError")):
            sbg.parse_args()

        # Parse with ok partialrun and verbose and nossl
        del sys.argv[1:]
        for op in ["--imaphost", "localhost", "--imapuser", "anonymous",
                   "--imappasswd", "none", "--verbose", "--partialrun", "10",
                   "--nossl"]:
            sys.argv.append(op)
        sbg = isbg.ISBG()
        sbg.parse_args()
        assert sbg.partialrun == 10

        # Restore pytest options:
        del sys.argv[1:]
        sys.argv = orig_args[:]

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
        print sbg.passwordhash
        sbg.do_passwordhash()
        assert len(sbg.passwordhash) == sbg.passwordhashlen

    def test_do_isbg(self):
        """Test do_isbg."""
        # Remove pytest options:
        orig_args = sys.argv[:]

        sbg = isbg.ISBG()
        with pytest.raises(isbg.ISBGError, match="specify your imap password",
                           message=("It should rise a specify imap password " +
                                    "ISBGError")):
            sbg.do_isbg()

        # Restore pytest options:
        del sys.argv[1:]
        sys.argv = orig_args[:]
