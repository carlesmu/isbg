#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  spamaproc.py
#  This file is part of isbg.
#
#  Copyright 2018 Carles Muñoz Gorriz <carlesmu@internautas.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

"""Spam processing module for isbg."""
# pylint: disable=no-member

from __future__ import print_function

try:                               # as script: py2 and py3, as module: py3
    import isbg
    import imaputils
    import sa_unwrap
    import utils
    from utils import __
except (ValueError, ImportError):  # as module: py3
    from isbg import isbg
    from isbg import imaputils
    from isbg import sa_unwrap
    from isbg import utils
    from isbg.utils import __

import logging


class Sa_Learn(object):
    """Comodity class to store information about learning processes."""

    tolearn = 0
    learnt = 0
    uids = []
    origpastuids = []


class SpamAssassin(object):
    """Learn and process spams from a imap account."""

    alreadylearnt = "Message was already un/learned"

    _required_kwargs = []
    _kwargs = ['imap', 'spamc', 'logger', 'partialrun', 'dryrun',
               'learnthendestroy', 'gmail', 'learnthenflag', 'learnunflagged',
               'learnflagged']

    def __init__(self, **kwargs):
        """Initialize a SpamAssassin object."""
        for k in self._required_kwargs:
            if k not in kwargs:
                raise TypeError("Missed required keyword argument: {}".format(
                                k))

        for k in self._kwargs:
            setattr(self, k, None)

        for k in kwargs:
            if k not in self._kwargs:
                raise TypeError("Unknown keyword argument: {}".format(k))
            setattr(self, k, kwargs[k])

        # pylint: disable=access-member-before-definition
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
            self.logger.addHandler(logging.StreamHandler())

        # what we use to set flags on the original spam in imapbox
        self.spamflagscmd = "+FLAGS.SILENT"

    @property
    def cmd_save(self):
        """Is the command that dumps out a munged message including report."""
        if self.spamc:  # pylint: disable=no-member
            return ["spamc"]
        else:
            return ["spamassassin"]

    @property
    def cmd_test(self):
        """Is the command to use to test if the message is spam."""
        if self.spamc:  # pylint: disable=no-member
            return ["spamc", "-c"]
        else:
            return ["spamassassin", "--exit-code"]

    @classmethod
    def create_from_isbg(cls, sbg):
        """Return a instance with the required args from ```ISBG```."""
        kw = dict()
        for k in cls._kwargs:
            kw[k] = getattr(sbg, k)
        return SpamAssassin(**kw)

    @staticmethod
    def get_formated_uids(uids, origpastuids, partialrun):
        """Get the uids formated."""
        uids = sorted(uids[0].split(), key=int, reverse=True)
        origpastuids = [u for u in origpastuids if str(u) in uids]
        uids = [u for u in uids if int(u) not in origpastuids]
        # Take only X elements if partialrun is enabled
        if partialrun:
            uids = uids[:int(partialrun)]
        return uids, origpastuids

    def learn(self, folder, learn_type, move_to, origpastuids):
        """Learn the spams (and if requested deleted or move them)."""
        sa_learning = Sa_Learn()

        # Sanity checks:
        if learn_type not in ['spam', 'ham']:
            raise isbg.ISBGError(-1, message="Unknown learn_type")
        if self.imap is None:
            raise isbg.ISBGError(-1, message="Imap is required")

        self.logger.debug("Teach {} to SA from: {}".format(learn_type, folder))

        self.imap.select(folder)
        if self.learnunflagged:
            typ, uids = self.imap.uid("SEARCH", None, "UNFLAGGED")
        elif self.learnflagged:
            typ, uids = self.imap.uid("SEARCH", None, "(FLAGGED)")
        else:
            typ, uids = self.imap.uid("SEARCH", None, "ALL")

        uids, sa_learning.origpastuids = SpamAssassin.get_formated_uids(
            uids, origpastuids, self.partialrun)

        sa_learning.tolearn = len(uids)

        for uid in uids:
            mail = imaputils.get_message(self.imap, uid, logger=self.logger)

            # Unwrap spamassassin reports
            unwrapped = sa_unwrap.unwrap(mail)
            if unwrapped is not None:
                self.logger.debug("{} Unwrapped: {}".format(
                    uid, utils.shorten(imaputils.mail_content(
                        unwrapped[0]), 140)))

            if unwrapped is not None and unwrapped:  # len(unwrapped)>0
                mail = unwrapped[0]

            if self.dryrun:
                out = self.alreadylearnt
                code = 0
            else:
                proc = utils.popen(["spamc", "--learntype=" + learn_type])
                try:
                    out = proc.communicate(imaputils.mail_content(mail))[0]
                except Exception:  # pylint: disable=broad-except
                    self.logger.exception('spamc error for mail {}'.format(
                        uid))
                    self.logger.debug(repr(imaputils.mail_content(mail)))
                    continue
                code = proc.returncode
                proc.stdin.close()

            if code == 69 or code == 74:
                raise isbg.ISBGError(
                    isbg.__exitcodes__['flags'],
                    "spamd is misconfigured (use --allow-tell)")

            if out.strip() == self.alreadylearnt or code == 6:
                self.logger.debug(__(
                    "Already learnt {} (spamc return code {})".format(uid,
                                                                      code)))
            else:
                sa_learning.learnt += 1
                self.logger.debug(__(
                    "Learnt {} (spamc return code {})".format(uid, code)))
            sa_learning.uids.append(int(uid))

            if not self.dryrun:
                if self.learnthendestroy:
                    if self.gmail:
                        self.imap.uid("COPY", uid, "[Gmail]/Trash")
                    else:
                        self.imap.uid("STORE", uid, self.spamflagscmd,
                                      "(\\Deleted)")
                elif move_to is not None:
                    self.imap.uid("COPY", uid, move_to)
                elif self.learnthenflag:
                    self.imap.uid("STORE", uid, self.spamflagscmd,
                                  "(\\Flagged)")

        return sa_learning
