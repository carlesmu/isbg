#!/usr/bin/env python
# -*- coding: utf-8 -*-

# test_sa_unwrap.py
# Copyright (C) 2017, Carles Muñoz Gorriz <carlesmu@internautas.org>
# This file is part of isbg.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""Test cases for sa_unwrap module."""

import os
import sys
import email.message

# We add the upper dir to the path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from isbg import sa_unwrap  # noqa: E402

try:
    PARSE_FILE = email.message_from_binary_file  # Python3
    MESSAGE = email.message_from_bytes           # Python3
except AttributeError:
    PARSE_FILE = email.message_from_file         # Python2
    MESSAGE = email.message_from_string          # Python2+3


def test_sa_unwrap_from_email():
    """Test function sa_unwrap_from_email."""
    """
    Test parsing a file with a message no multipart. It should return none.
    """
    f = open('examples/spam.eml', 'rb')
    ret = sa_unwrap.sa_unwrap_from_email(PARSE_FILE(f))
    f.close()
    assert ret is None, "%r is not a None." % ret

    """
    Test creating a multipart missage with 1 message from a file.
    It should return 1 Message.
    """
    f = open('examples/spam.from.spamassassin.eml', 'rb')
    ftext = f.read()
    ret = sa_unwrap.sa_unwrap_from_email(MESSAGE(ftext))
    f.close()
    num_mails = 0
    for mail in ret:
        assert isinstance(mail, email.message.Message), \
            "%r is not a email.message.Message[]." % ret
        num_mails = num_mails + 1
    assert num_mails == 1, "%d mails found" % num_mails

    if sys.version_info[0] > 3:  # Only python 3
        """
        Test a very simple message created from his bytes.
        It should return None.
        """
        # pylint: disable=no-member
        ret = sa_unwrap.sa_unwrap_from_email(email.message_from_bytes(b'0000'))
        assert ret is None, "%r is not a None." % ret

    """
    Test a very simple message created from his strings.
    It should return None.
    """
    ret = sa_unwrap.sa_unwrap_from_email(email.message_from_string('None'))
    assert ret is None, "%r is not a None." % ret


def test_unwrap():
    """Test funcition unwrap."""
    """Test unwrap of examples/spam.from.spamassassin.eml --> 1 message."""
    f = open('examples/spam.from.spamassassin.eml', 'rb')
    mails = sa_unwrap.unwrap(f)
    f.close()
    num_mails = 0
    for mail in mails:
        assert isinstance(mail, email.message.Message), \
            "%r is not a email.message.Message[]." % mails
        num_mails = num_mails + 1
    assert num_mails == 1, "%d mails found" % num_mails

    """Test unwrap of examples/spam.eml --> None."""
    f = open('examples/spam.eml', 'rb')
    mails = sa_unwrap.unwrap(f)
    f.close()
    assert mails is None


def test_run_1(capsys):
    """Test no multipart spam mail."""
    f = open('examples/spam.eml').read()
    sys.stdin = f
    sa_unwrap.run()
    out, err = capsys.readouterr()
    sa_unwrap.run()
    assert out == "No spam into the mail detected.\n"


def test_run_2(capsys):
    """Test multipart spam mail. Returns the multipart message."""
    f = open('examples/spam.from.spamassassin.eml').read()
    sys.stdin = f
    sa_unwrap.run()
    out, err = capsys.readouterr()
    assert out.startswith("Return-Path: ")