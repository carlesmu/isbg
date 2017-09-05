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
    >>> spam = isbg.sa_unwrap.unwrap(f.read())
    >>> f.close()
    >>> spam
    or
    $ cat examples/spam.from.spamassassin.eml | sa_unwrap

"""


import email
import email.message
import sys


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
                parts.append(email.message_from_string(pl_bytes[el_idx + 2:]))
        if len(parts) > 0:
            return parts
    return None


def unwrap(mail):
    """Unwrap a email from the spamassasin email.

    the mail could be a email.message.Email, a file or a string or buffer.
    It ruturns a list with all the email.message.Email founds.
    """
    if isinstance(mail, email.message.Message):
        return sa_unwrap_from_email(mail)
    if isinstance(mail, file):  # files are also stdin...
        return sa_unwrap_from_email(email.message_from_file(mail))
    return sa_unwrap_from_email(email.message_from_string(mail))


def run():
    """It runs when this module is called from the command line."""
    # select byte streams if they exist (on python 3)
    if hasattr(sys.stdin, 'buffer'):
        inb = sys.stdin.buffer    # pylint: disable=no-member
        outb = sys.stdout.buffer  # pylint: disable=no-member
    else:
        # on python 2 use regular streams
        inb = sys.stdin
        outb = sys.stdout

    spams = unwrap(inb)
    if spams is not None:
        for spam in spams:
            outb.write(spam.as_string())
    else:
        print "No spam into the mail detected."


if __name__ == '__main__':
    run()
