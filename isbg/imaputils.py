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

"""Imap module for isbg."""

import email      # To eassily encapsulated emails messages
import imaplib
import socket     # to catch the socket.error exception
import time

try:
    from utils import __       # as script: py2 and py3, as module: py3
except (ValueError, ImportError):
    from isbg.utils import __  # as module: py3


def mail_content(mail):
    """Get the email message content."""
    if not isinstance(mail, email.message.Message):
        raise email.errors.MessageError(__(
            "mail '{}' is not a email.message.Message.".format(repr(mail))))
    try:
        return mail.as_bytes()  # python 3
    except AttributeError:
        return mail.as_string()


def new_message(body):
    """Get a email.message from a body email."""
    try:
        mail = email.message_from_string(body)  # python 2+3
    except (AttributeError, TypeError):
        mail = email.message_from_bytes(body)  # pylint: disable=no-member

    if mail.as_string() == "" or mail.as_string() == "\n":
        raise TypeError(
            __("body '{}' cannot be empty.".format(repr(body))))

    return mail


def get_message(imap, uid, append_to=None, logger=None, assertok=None):
    """Get a message by uid and optionaly append its uid to a list."""
    res = imap.uid("FETCH", uid, "(BODY.PEEK[])")
    assertok(res, 'uid fetch', uid, '(BODY.PEEK[])')
    mail = email.message.Message()  # an empty email
    if res[0] != "OK":
        assertok(res, 'uid fetch', uid, '(BODY.PEEK[])')
        try:
            body = res[1][0][1]
            mail = new_message(body)
        except Exception:  # pylint: disable=broad-except
            logger.warning(__(
                ("Confused - rfc822 fetch gave {} - The message was " +
                 "probably deleted while we were running").format(res)))
    else:
        body = res[1][0][1]
        mail = new_message(body)

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
            logger.warning(__(
                ("Error in IMAP connection: {} ... retry {} of {}"
                 ).format(exc, retry, max_retry)))
            if retry >= max_retry:
                raise Exception(exc)
            else:
                time.sleep(retry_time)
    logger.debug(__("Server capabilities: {}".format(imap.capability)))
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
