#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  imaputils.py
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

"""Imap mofule for isbg."""

import email      # To eassily encapsulated emails messages
import imaplib
import socket     # to catch the socket.error exception
import time


def get_message(imap, uid, append_to=None, logger=None, assertok=None):
    """Get a message by uid and optionaly append its uid to a list."""
    res = imap.uid("FETCH", uid, "(BODY.PEEK[])")
    assertok(res, 'uid fetch', uid, '(BODY.PEEK[])')
    mail = email.message.Message()  # an empty email
    if res[0] != "OK":
        assertok(res, 'uid fetch', uid, '(BODY.PEEK[])')
        try:
            body = res[1][0][1]
            mail = email.message_from_string(body)
        except Exception:  # pylint: disable=broad-except
            logger.warning(("Confused - rfc822 fetch gave %s - The message "
                            + "was probably deleted while we were running"),
                           res)
    else:
        body = res[1][0][1]
        mail = email.message_from_string(body)

    if append_to is not None:
        append_to.append(int(uid))

    return mail


def imapflags(flaglist):
    """Transform a list to a string as expected for the IMAP4 standard."""
    return '(' + ','.join(flaglist) + ')'


def login_imap(imapsets, nossl=False, logger=None, assertok=None):
    """Login to the imap server."""
    assert isinstance(imapsets, ImapSettings)
    max_retry = 10
    retry_time = 0.60   # seconds
    for retry in range(1, max_retry + 1):
        try:
            if nossl:
                imap = imaplib.IMAP4(imapsets.host, imapsets.port)
            else:
                imap = imaplib.IMAP4_SSL(imapsets.host, imapsets.port)
            break   # ok, exit from loop
        except socket.error as exc:
            logger.warning(('Error in IMAP connection: %s ... retry '
                            + '%d of %d'), exc, retry, max_retry)
            if retry >= max_retry:
                raise Exception(exc)
            else:
                time.sleep(retry_time)
    logger.debug('Server capabilities: %s', imap.capability)
    # Authenticate (only simple supported)
    res = imap.login(imapsets.user, imapsets.passwd)
    assertok(res, "login", imapsets.user, 'xxxxxxxx')
    return imap


class ImapSettings(object):
    """Class to stote the imap and boxes settings."""

    def __init__(self):
        """Set Imap settings."""
        self.host = 'localhost'
        self.port = 143
        self.user = ''
        self.passwd = None
        self.nossl = False
        # Set mailboxes:
        self.inbox = 'INBOX'
        self.spaminbox = 'INBOX.spam'
        self.learnspambox = None
        self.learnhambox = None
