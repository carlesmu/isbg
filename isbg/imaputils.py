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
import re         # For regular expressions
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


def assertok(name):
    """Decorate with self.assertok."""
    def assertok_decorator(func):
        def func_wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            if self.assertok:
                if name == 'login':
                    self.assertok(res, name, args[0], 'xxxxxxxx')
                elif name == 'uid':
                    self.assertok(res, name + " " + args[0], args[1:])
                else:
                    self.assertok(res, name, *args, **kwargs)
            return res
        return func_wrapper
    return assertok_decorator


class IsbgImap4(object):
    """Proxy class for imaplib.IMAP4 or imaplib.IMAP4_SSL."""

    def __init__(self, host='', port=143, nossl=False, assertok=None):
        """Create a imaplib.IMAP4[_SSL] with an assertok method."""
        self.assertok = assertok
        self.nossl = nossl
        if nossl:
            self.imap = imaplib.IMAP4(host, port)
        else:
            self.imap = imaplib.IMAP4_SSL(host, port)

    # @assertok('append')  <-- it fails in some servers
    def append(self, mailbox, flags, date_time, message):
        """Append message to named mailbox."""
        return self.imap.append(mailbox, flags, date_time, message)

    @assertok('cabability')
    def capability(self):
        """Fetch capabilities list from server."""
        return self.imap.capability()

    @assertok('expunge')
    def expunge(self):
        """Permanently remove deleted items from selected mailbox."""
        return self.imap.expunge()

    @assertok('list')
    def list(self, directory='""', pattern='*'):
        """List mailbox names in directory matching pattern."""
        return self.imap.list(directory, pattern)

    @assertok('login')
    def login(self, user, passwd):
        """Identify client using plain text password."""
        return self.imap.login(user, passwd)

    @assertok('logout')
    def logout(self):
        """Shutdown connection to server."""
        return self.imap.logout()

    @assertok('status')
    def status(self, mailbox, names):
        """Request named status conditions for mailbox."""
        return self.imap.status(mailbox, names)

    @assertok('select')
    def select(self, mailbox='INBOX', readonly=False):
        """Select a Mailbox."""
        return self.imap.select(mailbox, readonly)

    @assertok('uid')
    def uid(self, command, *args):
        """Execute "command arg ..." with messages identified by UID."""
        return self.imap.uid(command, *args)

    def get_uidvalidity(self, mailbox):
        """Validate a mailbox."""
        uidvalidity = 0
        mbstatus = self.imap.status(mailbox, '(UIDVALIDITY)')
        if mbstatus[0] == 'OK':
            body = mbstatus[1][0].decode()
            uidval = re.search('UIDVALIDITY ([0-9]+)', body)
            if uidval is not None:
                uidvalidity = int(uidval.groups()[0])
        return uidvalidity


def login_imap(imapsets, logger=None, assertok=None):
    """Login to the imap server."""
    if not isinstance(imapsets, ImapSettings):
        raise TypeError("imapsets is not a ImapSettings")

    max_retry = 10
    retry_time = 0.60   # seconds
    for retry in range(1, max_retry + 1):
        try:
            imap = IsbgImap4(imapsets.host, imapsets.port, imapsets.nossl,
                             assertok)
            break   # ok, exit from loop
        except socket.error as exc:
            if logger:
                logger.warning(__(
                    ("Error in IMAP connection: {} ... retry {} of {}"
                     ).format(exc, retry, max_retry)))
            if retry >= max_retry:
                raise Exception(exc)
            else:
                time.sleep(retry_time)
    if logger:
        logger.debug(__("Server capabilities: {}".format(
            imap.capability()[1])))
    if imapsets.nossl and logger:
        logger.warning("WARNING: Using insecure IMAP connection: without SSL.")
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
        if self._hashed_host != self.host or \
                self._hashed_user != self.user or \
                self._hashed_port != self.port:
            self._hashed_host = self.host
            self._hashed_user = self.user
            self._hashed_port = self.port
            self._hash = ImapSettings.get_hash(self.host, self.user, self.port)
        return self._hash

    @staticmethod
    def get_hash(host, user, port):
        """Get a hash with the host, user and port."""
        newhash = md5()
        newhash.update(host.encode())
        newhash.update(user.encode())
        newhash.update(repr(port).encode())
        return newhash
