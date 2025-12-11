# SPDX-FileCopyrightText: 2017-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test numerics util."""

from irclib.util import numerics


def test_lookup() -> None:
    """Test looking up a numeric."""
    n = numerics.numerics["001"]
    assert n is numerics.numerics.from_int(1)
    assert n is numerics.numerics.from_name("RPL_WELCOME")


def test_iter() -> None:
    """Test iterating the numerics list."""
    assert next(iter(numerics.numerics)) == "001"


def test_len() -> None:
    """Test checking the length of the numerics list."""
    assert len(numerics.numerics) > 0
