"""isbg scans an IMAP Inbox and runs every entry against SpamAssassin.

For any entries that match, the message is copied to another folder,
and the original marked or deleted.

This software was mainly written Roger Binns <rogerb@rogerbinns.com>
and maintained by Thomas Lecavelier <thomas@lecavelier.name> since
novembre 2009. You may use isbg under any OSI approved open source
license such as those listed at http://opensource.org/licenses/alphabetical

See Also:

    For command line usage see help(isbg.isbg).

Examples:

    >>> import isbg
    >>> isbg = isbg.ISBG()
    >>> isbg.imapsets.host = "imap.example.org"
    >>> isbg.imapsets.port = imapport=993
    >>> isbg.imapsets.user = "example@example.org"
    >>> isbg.imapsets.passwd = "xxxxxxxx"
    >>> isbg.imapsets.inbox = "INBOX"
    >>> isbg.imapsets.spaminbox = "Spam"
    >>> isbg.imapsets.learnspambox = "Spam"
    >>> isbg.imapsets.learnhambox = "NOSPAM"
    >>> # Set the number of mails to chech
    >>> isbg.set_trackfile_opts(partialrun=4)
    >>> isbg.set_reporting_opts(verbose=True)  # Show more info
    >>> isbg.set_lockfile_opts(ignorelockfile=True)
    >>> isbg.removelock()  # if there is a lock file
    >>> isbg.do_isbg()     # Connects to the imap and checks for spam
"""


from isbg import ISBG, __version__

__all__ = ["ISBG", "__version__"]
