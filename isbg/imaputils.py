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
    from hashlib import md5
except ImportError:
    from md5 import md5

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


def get_message(imap, uid, append_to=None, logger=None):
    """Get a message by uid and optionaly append its uid to a list."""
    res = imap.uid("FETCH", uid, "(BODY.PEEK[])")
    mail = email.message.Message()  # an empty email
    if res[0] != "OK":
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


class IsbgImap4(imaplib.IMAP4, object):
    """Extends a imaplib.IMAP4_SSL with an assertok method."""

    def __init__(self, host='', port=143, assertok=None):
        """Create a imaplib.IMAP4 with an assertok method."""
        self.assertok = assertok
        super(IsbgImap4, self).__init__(host, port)

    def login(self, user, passwd):
        """Identify client using plain text password."""
        res = super(IsbgImap4, self).login(user, passwd)
        if self.assertok:
            self.assertok(res, "login", user, 'xxxxxxxx')
        return res

    def select(self, mailbox='INBOX', readonly=False):
        """Select a Mailbox."""
        res = super(IsbgImap4, self).select(mailbox, readonly)
        if self.assertok:
            self.assertok(res, 'select', mailbox, readonly)
        return res

    def uid(self, command, *args):
        """Execute "command arg ..." with messages identified by UID."""
        res = super(IsbgImap4, self).uid(command, *args)
        if self.assertok:
            self.assertok(res, 'uid ' + command, *args)
        return res

    def list(self, directory='""', pattern='*'):
        """List mailbox names in directory matching pattern."""
        res = super(IsbgImap4, self).list(directory, pattern)
        if self.assertok:
            self.assertok(res, 'list', directory, pattern)
        return res


class IsbgImap4_SSL(imaplib.IMAP4_SSL, object):
    """Extends a imaplib.IMAP4_SSL with an assertok method."""

    def __init__(self, host='', port=143, assertok=None):
        """Create a imaplib.IMAP4_SSL with an assertok method."""
        self.assertok = assertok
        super(IsbgImap4_SSL, self).__init__(host, port)

    def login(self, user, passwd):
        """Identify client using plain text password."""
        res = super(IsbgImap4_SSL, self).login(user, passwd)
        if self.assertok:
            self.assertok(res, "login", user, 'xxxxxxxx')
        return res

    def select(self, mailbox='INBOX', readonly=False):
        """Select a Mailbox."""
        res = super(IsbgImap4_SSL, self).select(mailbox, readonly)
        if self.assertok:
            self.assertok(res, 'select', mailbox, readonly)
        return res

    def uid(self, command, *args):
        """Execute "command arg ..." with messages identified by UID."""
        res = super(IsbgImap4_SSL, self).uid(command, *args)
        if self.assertok:
            self.assertok(res, 'uid ' + command, *args)
        return res

    def list(self, directory='""', pattern='*'):
        """List mailbox names in directory matching pattern."""
        res = super(IsbgImap4_SSL, self).list(directory, pattern)
        if self.assertok:
            self.assertok(res, 'list', directory, pattern)
        return res


def login_imap(imapsets, nossl=False, logger=None, assertok=None):
    """Login to the imap server."""
    assert isinstance(imapsets, ImapSettings)
    max_retry = 10
    retry_time = 0.60   # seconds
    for retry in range(1, max_retry + 1):
        try:
            if nossl:
                imap = IsbgImap4(imapsets.host, imapsets.port, assertok)
            else:
                imap = IsbgImap4_SSL(imapsets.host, imapsets.port, assertok)
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
    imap.login(imapsets.user, imapsets.passwd)
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
        #
        self._hashed_host = None
        self._hashed_user = None
        self._hashed_port = None
        self._hash = self.hash

    @property
    def hash(self):
        """Get the hash property builf from the host, user and port."""
        if self._hashed_host == self.host and \
                self._hashed_user == self.user and \
                self._hashed_port == self.port:
            return self._hash
        else:
            self._hashed_host = self.host
            self._hashed_user = self.user
            self._hashed_port = self.port
            return ImapSettings.get_hash(self.host, self.user, self.port)

    @staticmethod
    def get_hash(host, user, port):
        """Get a hash with the host, user and port."""
        newhash = md5()
        newhash.update(host.encode())
        newhash.update(user.encode())
        newhash.update(repr(port).encode())
        return newhash
