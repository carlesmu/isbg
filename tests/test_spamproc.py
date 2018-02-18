#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_spamaproc.py
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

"""Tests for spamproc.py."""
import os
import sys
try:
    import pytest
except ImportError:
    pass

# We add the upper dir to the path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))
from isbg import spamproc  # noqa: E402
from isbg import isbg      # noqa: E402


class Test_Sa_Learn(object):
    """Tests for SA_Learn."""

    def test_sa_learn(self):
        """Test for sa_learn."""
        learn = spamproc.Sa_Learn()
        assert learn.tolearn == 0
        assert learn.learnt == 0
        assert len(learn.uids) == 0


class Test_SpamAssassin(object):
    """Tests for SpamAssassin."""

    _kwargs = ['imap', 'spamc', 'logger', 'partialrun', 'dryrun',
               'learnthendestroy', 'gmail', 'learnthenflag', 'learnunflagged',
               'learnflagged']

    def test__kwars(self):
        """Test _kwargs is up to date."""
        assert self._kwargs == spamproc.SpamAssassin()._kwargs

    def test___init__(self):
        """Test __init__."""
        sa = spamproc.SpamAssassin()
        # All args spected has been initialized:
        for k in self._kwargs:
            assert k in dir(sa)

    def test_cmd_save(self):
        """Test cmd_save."""
        sa = spamproc.SpamAssassin()
        assert sa.cmd_save == ['spamassassin']
        sa.spamc = True
        assert sa.cmd_save == ["spamc"]
        sa.spamc = False
        assert sa.cmd_save == ['spamassassin']

    def test_cmd_test(self):
        """Test cmd_test."""
        sa = spamproc.SpamAssassin()
        assert sa.cmd_test == ["spamassassin", "--exit-code"]
        sa.spamc = True
        assert sa.cmd_test == ["spamc", "-c"]
        sa.spamc = False
        assert sa.cmd_test == ["spamassassin", "--exit-code"]

    def test_create_from_isbg(self):
        """Test create_from_isbg."""
        sbg = isbg.ISBG()
        sa = spamproc.SpamAssassin.create_from_isbg(sbg)
        assert sa.imap is None  # pylint: disable=no-member
        assert sa.logger is not None

    def test_learn_checks(self):
        """Test learn checks."""
        sa = spamproc.SpamAssassin()
        with pytest.raises(isbg.ISBGError, match="Unknown learn_type",
                           message="Should rise error."):
            sa.learn('Spam', '', None, [])

        with pytest.raises(isbg.ISBGError, match="Imap is required",
                           message="Should rise error."):
            sa.learn('Spam', 'ham', None, [])
