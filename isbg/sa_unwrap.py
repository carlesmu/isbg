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
    >>> import io
    >>> import isbg.sa_unwrap
    >>> f = open('examples/spam.from.spamassassin.eml','rb')
    >>> isbg.sa_unwrap.unwrap(io.BytesIO(f.read()))
    >>> f.close()
    or
    $ cat examples/spam.from.spamassassin.eml | sa_unwrap

"""

# import byte parser if it exists (on python 3)
try:
    from email.parser import BytesParser
except ImportError:
    # on python 2, use old parser
    from email.parser import Parser
    BytesParser = Parser
import sys


def unwrap(msg_stream):
    """Parse and unwrap message."""
    parser = BytesParser()
    msg = parser.parse(msg_stream)
    if msg.is_multipart():
        parts = []
        ploads = msg.get_payload()
        for pload in ploads:
            if pload.get_param('x-spam-type', '') == 'original':
                if hasattr(pload, 'as_bytes'):
                    pl_bytes = pload.as_bytes()
                else:
                    pl_bytes = pload.as_string()
                el_idx = pl_bytes.index(b'\n\n')
                parts.append(pl_bytes[el_idx + 2:])
        if len(parts) > 0:
            return parts
    return None


def run():
    """It runs when this module is called from the command line."""
    # select byte streams if they exist (on python 3)
    if hasattr(sys.stdin, 'buffer'):
        # pylint complains Instance of 'file' has no 'buffer' member
        # (no-member) using:
        # inb = sys.stdin.buffer
        inb = getattr(sys.stdin, 'buffer')
        outb = getattr(sys.stdout, 'buffer')
    else:
        # on python 2 use regular streams
        inb = sys.stdin
        outb = sys.stdout

    spams = unwrap(inb)
    if spams is not None:
        for spam in spams:
            outb.write(spam)
    else:
        print("No spam into the mail detected.")


if __name__ == '__main__':
    run()
