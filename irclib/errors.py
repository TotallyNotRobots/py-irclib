# SPDX-FileCopyrightText: 2017-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Library exceptions."""

__all__ = ("ParseError",)


class ParseError(ValueError):
    """An exception representing some error during parsing."""
