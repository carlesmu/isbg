New
===

New in 2.0
-----------

* A more robust package, it can be used as a module and a script.
* Better documentation: using sphinx.
* using main() to run as script.
* Using standard cache `xdg_cache_home` to store information.

News in old releases
--------------------

New in 1.00
^^^^^^^^^^^

**DEPRECATION NOTICE:** if you used the `--ssl` parameter in 0.99, you now
need to stop using it! SSL is now used by default. If you want not to use
it, please use the `--nossl` parameter.

* The CLI interface is now implemented with docopt
* The README now includes the documentation
* New command `--imaplist` lists the directories in IMAP account
* Code now follows PEP-8 style guide
* Renamed variables to be consistent
* Added gmail integration (thanks to Orkim!)
* Added bash scripts for use with multiple accounts
* SSL is now used by default and "--ssl" parameter is now a "--nossl" parameter
* New command `--trackfile` now permits trackfile name configuration (thanks naevtamarkus!)
* New command `--partialrun` now enable isbg to run for only a few emails (thanks naevtamarkus!)
