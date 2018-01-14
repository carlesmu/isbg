#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_utils.py
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

"""Test cases for isbg module."""

import os
import sys

# We add the upper dir to the path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from isbg import utils  # noqa: E402


def test_BraceMessage():
    """Test BraceMessage."""
    ret = utils.BraceMessage("Test {} {}".format(1, "is one."))
    assert str(ret) == "Test 1 is one."
    ret = utils.__("Test {} {}".format(1, "is one."))
    assert str(ret) == "Test 1 is one."
