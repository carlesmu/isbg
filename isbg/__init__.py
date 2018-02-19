#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""isbg scans an IMAP Inbox and runs every entry against SpamAssassin.

For any entries that match, the message is copied to another folder,
and the original marked or deleted.

See Also
========
For command line usage see help( isbg.__main__ ).

Examples
========
    >>> import isbg
    >>> sbg = isbg.ISBG()
    >>> sbg.imapsets.host = "imap.example.org"
    >>> sbg.imapsets.port = 993
    >>> sbg.imapsets.user = "example@example.org"
    >>> sbg.imapsets.passwd = "xxxxxxxx"
    >>> sbg.imapsets.inbox = "INBOX"
    >>> sbg.imapsets.spaminbox = "Spam"
    >>> sbg.imapsets.learnspambox = "Spam"
    >>> sbg.imapsets.learnhambox = "NOSPAM"
    >>> # Set the number of mails to chech
    >>> sbg.partialrun = 4         # Only check 4 mails for every proc.
    >>> sbg.verbose = True         # Show more info
    >>> sbg.ignorelockfile = True  # Ignore lock file
    >>> sbg.removelock()           # if there is a lock file
    >>> sbg.do_isbg()         # Connects to the imap and checks for spam

"""


from .isbg import ISBG, __version__

__all__ = ["ISBG", "__version__"]
