Changelog
=========

Development
-----------
What has been done since last release.

* Using standard cache *xdg_cache_home* to store information, usually 
  *$HOME/.cache/isbg/*. If you have stored your password with and old releases
  you should re-store it and delete the old stored files, you would find the
  old ones as *$HOME/.isbg*.
* A more robust package, it can be used as a module and a script.
* Now we depend of *chardet* for better detect the mails encodings.
* Using main() to run as script.
* python3 support.
* Modularized.
* Added a default --partialrun of 50. Use partialrun=0 to retain the
  old behaviour.
* Ddocumentation: use sphinx and suport to upload it to `Read the docs`__.

.. __: https://isbg.readthedocs.io/


Released
--------

isbg 1.00 (20160106)
~~~~~~~~~~~~~~~~~~~~
  * The CLI interface is now implemented with docopt
  * The README now includes the documentation
  * New command --imaplist lists the directories in IMAP account
  * Code now follows PEP-8 style guide
  * Renamed variables to be consistent
  * Added gmail integration (thanks to Orkim!)
  * Added bash scripts for use with multiple accounts
  * SSL is now used by default and "--ssl" parameter is now a "--nossl" parameter
  * New command "--trackfile" now permits trackfile name configuration (thanks naevtamarkus!)
  * New command "--partialrun" now enable isbg to run for only a few emails (thanks naevtamarkus!)

isbg 0.99 (20100303)
~~~~~~~~~~~~~~~~~~~~
  * Drastic speed enhancement (thanks to Ajenbo!)
  * deletehighterthen, fix expunge, movehamto (thanks to AJenbo!)
  * Learn spam/ham before scanning
  * Call IMAP SEARCH command instead of fetching and checking manually
  * Ignore lockfile when too old (4h by default)
  * Switch to ignore lockfile
  * Bug fix: SSL now work.
  * Don't crash anymore when parsing weird attachement (like MS Office files)

isbg 0.98 (20091201)
~~~~~~~~~~~~~~~~~~~~
  * Teach spam and ham from specific folders
  * Compatibility from py2.4 to py2.6