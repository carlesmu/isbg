#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
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

# From https://docs.python.org/3/howto/logging-cookbook.html
# Get free of the pylint logging-format-interpolation warning using __

"""Utils for isbg."""

import os
from subprocess import Popen, PIPE


def dehexof(string):
    """Tanslate a hexadecimal string to his string value."""
    res = ""
    while string:
        res = res + chr(16 * hexdigit(string[0]) + hexdigit(string[1]))
        string = string[2:]
    return res


def hexdigit(char):
    """Tanslate a hexadecimal character his decimal (int) value."""
    if char >= '0' and char <= '9':
        return ord(char) - ord('0')
    if char >= 'a' and char <= 'f':
        return 10 + ord(char) - ord('a')
    if char >= 'A' and char <= 'F':
        return 10 + ord(char) - ord('A')
    raise ValueError(repr(char) + " is not a valid hexadecimal digit")


def hexof(string):
    """Translate a string to a string with its hexadecimal value."""
    res = ""
    for i in string:
        res = res + ("%02x" % ord(i))
    return res


def popen(cmd):
    """Call for Popen, helper method."""
    if os.name == 'nt':
        return Popen(cmd, stdin=PIPE, stdout=PIPE)
    else:
        return Popen(cmd, stdin=PIPE, stdout=PIPE, close_fds=True)


def shorten(inp, length):
    """Short a dict or a list or other object to a maximus length."""
    if isinstance(inp, dict):
        return dict([(k, shorten(v, length)) for k, v in inp.items()])
    elif isinstance(inp, (list, tuple)):
        return [shorten(x, length) for x in inp]
    return truncate(inp, length)


def truncate(inp, length):
    """Truncate a string to  a maximus length of his repr."""
    if length < 3:
        raise ValueError("length should be 3 or greater")
    if len(inp) > length:
        return repr(inp)[:length - 3] + '...'
    return inp


class BraceMessage(object):
    """Comodity class to format a string."""

    def __init__(self, fmt, *args, **kwargs):
        """Initialize the object."""
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        """Return the string formated."""
        return self.fmt.format(*self.args, **self.kwargs)


__ = BraceMessage  # pylint: disable=invalid-name
