.. isbg documentation master file, created by
   sphinx-quickstart on Sat Feb 17 12:46:51 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

IMAP Spam Begone
================

`isbg` is a script and a python module that makes it easy to scan an IMAP inbox
for spam using SpamAssassin and get your spam moved to another folder.

Unlike the normal mode of deployments for *SpamAssassin*, `isbg` does not need
to be involved in mail delivery, and can run on completely different machines
to where your mailbox actually is. So this is the perfect tool to take good
care of your ISP mailbox without having to leave it.

Contents
--------
.. toctree::
   :maxdepth: 2
   :numbered:

   README
   NEWS
   TODO
   api_index

Links
-----
* `🚀 Github <https://github.com/carlesmu/isbg>`_
* `💾 Download Releases <https://pypi.python.org/pypi/isbg>`_
* :doc:`🕮 API Reference  <api_index>`
