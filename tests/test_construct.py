# SPDX-FileCopyrightText: 2017-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test constructing message objects."""

from irclib.parser import Message


def test_param_construct() -> None:
    """Test constructing Message objects."""
    msg = Message(None, None, "PRIVMSG", "#channel", "Message thing")
    assert str(msg) == "PRIVMSG #channel :Message thing"

    msg = Message(None, None, "PRIVMSG", ["#channel", "Message thing"])
    assert str(msg) == "PRIVMSG #channel :Message thing"

    msg = Message(None, None, "PRIVMSG", ["#channel", ":Message thing"])
    assert str(msg) == "PRIVMSG #channel ::Message thing"

    msg = Message(None, None, "PRIVMSG", [""])
    assert str(msg) == "PRIVMSG :"
