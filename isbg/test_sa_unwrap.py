#!/usr/bin/env python2
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


def test_unwrap_spam_from_spamassassin():
    """Test unwrap of examples/spam.from.spamassassin.eml --> 1 message."""
    try:
        import sa_unwrap            # Python 2
    except ImportError:
        from isbg import sa_unwrap  # Python 3
    import email.message
    f = open('examples/spam.from.spamassassin.eml', 'rb')
    mails = sa_unwrap.unwrap(f)
    f.close()
    num_mails = 0
    for mail in mails:
        assert isinstance(mail, email.message.Message), \
            "%r is not a email.message.Message." % mails
        num_mails = num_mails + 1
    assert num_mails == 1, "%d mails found" % num_mails


def test_unwrap_spam():
    """Test unwrap of examples/spam.eml --> None."""
    try:
        import sa_unwrap             # Python 2
    except ImportError:
        from isbg import sa_unwrap   # Python 3
    f = open('examples/spam.eml', 'rb')
    mails = sa_unwrap.unwrap(f)
    f.close()
    assert mails is None
