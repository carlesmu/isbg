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
    >>> sbg.set_trackfile_opts(partialrun=4)
    >>> sbg.set_reporting_opts(verbose=True)  # Show more info
    >>> sbg.set_lockfile_opts(ignorelockfile=True)
    >>> sbg.removelock()  # if there is a lock file
    >>> sbg.do_isbg()     # Connects to the imap and checks for spam

"""


from .isbg import ISBG, __version__

__all__ = ["ISBG", "__version__"]
