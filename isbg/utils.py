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
