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

"""Imap utils module for isbg - IMAP Spam Begone."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import email      # To easily encapsulated emails messages
import imaplib
import re         # For regular expressions
import socket     # to catch the socket.error exception
import time

from hashlib import md5

from isbg import utils
from .utils import __


def mail_content(mail):
    """Get the email message content.

    Args:
        mail (email.message.Message): The email message.
    Returns:
        bytes | str: The contents, with headers, of the email message.

    """
    if not isinstance(mail, email.message.Message):
        raise email.errors.MessageError(
            "mail '{}' is not a email.message.Message.".format(repr(mail)))
    try:
        return mail.as_bytes()  # python 3
    except (AttributeError, UnicodeEncodeError):
        return mail.as_string()


def new_message(body):
    """Get a email.message from a body email.

    Note: If there are problems encoding it, it will replace it to ascii.

    Args:
        body (bytes | str): The content, with or witout headers, of a email
            message.
    Returns:
        email.message.Message: The object representing it.

    """
    mail = None

    if isinstance(body, bytes):
        try:
            mail = email.message_from_bytes(body)  # pylint: disable=no-member
            if mail.as_bytes() in [b'', b'\n']:
                raise TypeError(
                    __("body '{}' cannot be empty.".format(repr(body))))
            return mail
        except AttributeError:  # py2
            pass

    try:
        mail = email.message_from_string(body)
    except UnicodeEncodeError:
        body = body.encode("ascii", errors='replace')
        mail = email.message_from_string(body)
    if mail.as_string() in ['', '\n']:
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


def bytes_to_ascii(func):
    """Decorate a method to return his return value as ascii."""
    def func_wrapper(cls, *args, **kwargs):
        return utils.get_ascii_or_value(func(cls, *args, **kwargs))
    return func_wrapper


def assertok(name):
    """Decorate with assertok."""
    def assertok_decorator(func):
        def func_wrapper(cls, *args, **kwargs):
            res = func(cls, *args, **kwargs)
            if cls.assertok:
                if name == 'login':
                    cls.assertok(res, name, args[0], 'xxxxxxxx')
                elif name == 'uid':
                    cls.assertok(res, name + " " + args[0], args[1:])
                else:
                    cls.assertok(res, name, *args, **kwargs)
            return res
        return func_wrapper
    return assertok_decorator


class IsbgImap4(object):
    """Proxy class for `imaplib.IMAP4` and `imaplib.IMAP4_SSL`."""

    def __init__(self, host='', port=143, nossl=False, assertok=None):
        """Create a imaplib.IMAP4[_SSL] with an assertok method."""
        self.assertok = assertok
        self.nossl = nossl
        if nossl:
            self.imap = imaplib.IMAP4(host, port)
        else:
            self.imap = imaplib.IMAP4_SSL(host, port)

    # @assertok('append')  <-- it fails in some servers
    @bytes_to_ascii
    def append(self, mailbox, flags, date_time, message):
        """Append message to named mailbox."""
        return self.imap.append(mailbox, flags, date_time, message)

    @assertok('cabability')
    @bytes_to_ascii
    def capability(self):
        """Fetch capabilities list from server."""
        return self.imap.capability()

    @assertok('expunge')
    @bytes_to_ascii
    def expunge(self):
        """Permanently remove deleted items from selected mailbox."""
        return self.imap.expunge()

    @assertok('list')
    @bytes_to_ascii
    def list(self, directory='""', pattern='*'):
        """List mailbox names in directory matching pattern."""
        return self.imap.list(directory, pattern)

    @assertok('login')
    @bytes_to_ascii
    def login(self, user, passwd):
        """Identify client using plain text password."""
        return self.imap.login(user, passwd)

    @assertok('logout')
    @bytes_to_ascii
    def logout(self):
        """Shutdown connection to server."""
        return self.imap.logout()

    @assertok('status')
    @bytes_to_ascii
    def status(self, mailbox, names):
        """Request named status conditions for mailbox."""
        return self.imap.status(mailbox, names)

    @assertok('select')
    @bytes_to_ascii
    def select(self, mailbox='INBOX', readonly=False):
        """Select a Mailbox."""
        return self.imap.select(mailbox, readonly)

    @assertok('uid')
    @bytes_to_ascii
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
        self.host = 'localhost'      #: IMAP host name or IP.
        self.port = 143              #: IMAP port to connect.
        self.user = ''               #: IMAP user name.
        self.passwd = None           #: Password for the IMAP user name.
        self.nossl = False           #: Not use ssl for IMAP connection.

        #: Inbox folder, default to ```INBOX```.
        self.inbox = 'INBOX'
        #: Spam folder, default to ```INBOX.spam```.
        self.spaminbox = 'INBOX.spam'

        self.learnspambox = None     #: Folder used to learn spam messages.
        self.learnhambox = None      #: Folder used to learn non-spam messages.

        self._hashed_host = None
        self._hashed_user = None
        self._hashed_port = None
        self._hash = self.hash

    @property
    def hash(self):
        """Get the hash property built from the host, user and port.

        :getter: Gets hash string.
        :type: str.

        """
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
        """Get a hash with the host, user and port.

        Args:
            host (str): IMAP host name.
            user (str): IMAP user name.
            port (int): IMAP connection port.

        """
        newhash = md5()
        newhash.update(host.encode())
        newhash.update(user.encode())
        newhash.update(repr(port).encode())
        return newhash
