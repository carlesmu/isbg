#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Test cases for sa_unwrap module."""


def test_unwrap_spam_from_spamassassin():
    """Test unwrap of examples/spam.from.spamassassin.eml --> 1 message."""
    import sa_unwrap
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
    import sa_unwrap
    f = open('examples/spam.eml', 'rb')
    mails = sa_unwrap.unwrap(f)
    f.close()
    assert mails is None
