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
    >>> isbg.set_imap_opts(isbg.set_imap_opts(imaphost="imap.example.org",
    >>>                    imapport=993,
    >>>                    imapuser="example",
    >>>                    imappasswd="xxxxxxxx",
    >>>                    nossl=False)   # Set the imap options
    >>> isbg.set_mailboxes(inbox="INBOX",
    >>>                    spaminbox="Spam",
    >>>                    learnspambox="Spam",
    >>>                    learnhambox="NOSPAM")  # Set the mailbox info
    >>> # Set the number of mails to chech
    >>> isbg.set_trackfile_opts(partialrun=4)
    >>> isbg.set_reporting_opts(verbose=True) # Show more info
    >>> isbg.do_isbg()    # Connects to the imap and checks for spam
    >>> # Before rerun it after an interrupted process.
    >>> isbg.removelock()
"""


from isbg import ISBG, __version__

__all__ = ["ISBG", "__version__"]
