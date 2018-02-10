#!/usr/bin/python
# -*- coding: utf-8 -*-

r"""
parse an rfc2822 email message and unwrap it if contains spam attached.

To know it it chechks for an x-spam-type=original payload.

Works on python 2.7+ and 3.x (uses some fairly ugly hacks to do so)

Does not perfectly preserve whitespace (esp. \r\n vs. \n and \t vs space), also
does that differently between python 2 and python 3, but this should not impact
spam-learning purposes.

Example:

    It will return the original mail into a spamassassin mail:
    >>> import isbg.sa_unwrap
    >>> f = open('examples/spam.from.spamassassin.eml','rb')
    >>> spams = isbg.sa_unwrap.unwrap(f)
    >>> f.close()
    >>> for spam in spams:
    >>>     print(spam)
    or
    $ sa_unwrap < examples/spam.from.spamassassin.eml
    $ sa_unwrap < examples/spam.eml

"""

from __future__ import print_function  # Now we can use print(...

import email
import email.message
from io import IOBase
import sys

# works with python 2 and 3
try:
    FILE_TYPES = (file, IOBase)
except NameError:
    FILE_TYPES = (IOBase,)  # Python 3

try:
    PARSE_FILE = email.message_from_binary_file  # Python3
    MESSAGE = email.message_from_bytes           # Python3
except AttributeError:
    PARSE_FILE = email.message_from_file         # Python2
    MESSAGE = email.message_from_string          # Python2+3


def sa_unwrap_from_email(msg):
    """Unwrap a email from the spamassasin email."""
    if msg.is_multipart():
        parts = []
        ploads = msg.get_payload()
        for pload in ploads:
            if pload.get_param('x-spam-type', '') == 'original':
                # We remove the headers added by spamassassin:
                if hasattr(pload, 'as_bytes'):
                    pl_bytes = pload.as_bytes()
                else:
                    pl_bytes = pload.as_string()
                el_idx = pl_bytes.index(b'\n\n')
                parts.append(MESSAGE(pl_bytes[el_idx + 2:]))
        if parts:  # len(parts) > 0
            return parts
    return None


def unwrap(mail):
    """Unwrap a email from the spamassasin email.

    the mail could be a email.message.Email, a file or a string or buffer.
    It ruturns a list with all the email.message.Email founds.
    """
    if isinstance(mail, email.message.Message):
        return sa_unwrap_from_email(mail)
    if isinstance(mail, FILE_TYPES):  # files are also stdin...
        return sa_unwrap_from_email(PARSE_FILE(mail))
    return sa_unwrap_from_email(email.message_from_string(mail))


def run():
    """Run when this module is called from the command line."""
    # select byte streams if they exist (on python 3)
    if hasattr(sys.stdin, 'buffer'):
        inb = sys.stdin.buffer    # pylint: disable=no-member
    else:
        # on python 2 use regular streams
        inb = sys.stdin

    spams = unwrap(inb)
    if spams is not None:
        for spam in spams:
            print(spam.as_string())
    else:
        print("No spam into the mail detected.")


if __name__ == '__main__':
    run()
