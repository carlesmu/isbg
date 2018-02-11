#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_imaputils.py
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

import email
import os
import sys
try:
    import pytest
except ImportError:
    pass


# We add the upper dir to the path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from isbg import imaputils  # noqa: E402


def test_mail_content():
    """Test mail_content function."""
    with pytest.raises(email.errors.MessageError,
                       message="mail 'None' is not a email.message.Message."):
        imaputils.mail_content(None)
    fmail = open('examples/spam.from.spamassassin.eml', 'rb')
    ftext = fmail.read()
    mail = imaputils.new_message(ftext)
    fmail.close()
    assert isinstance(imaputils.mail_content(mail), (str, bytes))


def test_new_message():
    """Test new_message function."""
    fmail = open('examples/spam.from.spamassassin.eml', 'rb')
    ftext = fmail.read()
    mail = imaputils.new_message(ftext)
    fmail.close()
    assert isinstance(mail, email.message.Message), \
        "%r is not a email.message.Message." % mail

    mail = imaputils.new_message("Foo")
    assert isinstance(mail, email.message.Message), \
        "%r is not a email.message.Message." % mail

    with pytest.raises((TypeError, AttributeError)):
        imaputils.new_message(None)
    with pytest.raises((TypeError, AttributeError)):
        imaputils.new_message(body="")


def test_get_message():
    """Test get_message."""
    # FIXME:
    pass


def test_imapflags():
    """Test imapflags."""
    #  FIXME:
    pass


class TestIsbgImap4(object):
    """Test IsbgImap4."""

    # FIXME:
    pass


class TestIsbgImap4_SSL(object):
    """Test IsbgImap4_SSL."""

    # FIXME:
    pass


def test_login_imap():
    """Test login_imap."""
    # FIXME:
    pass


class TestImapSettings(object):
    """Test object ImapSettings."""

    def test(self):
        """Test the object."""
        imapset = imaputils.ImapSettings()
        imaphash = imapset.hash
        assert imapset.hash == imaphash
        assert imapset.hash.hexdigest() == '56fdd686137c8645d44024096a0ed441'
        imapset.host = '127.0.0.1'
        assert imapset.hash.hexdigest() == 'ca057ebec07690c05f64959fff011c8d'
