# SPDX-FileCopyrightText: 2017-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""IRC command data and utilities."""

from collections.abc import Iterator, Mapping
from typing import cast

import attr

__all__ = ("Command", "client_commands")


@attr.s(frozen=True, hash=True, auto_attribs=True)
class CommandArgument:
    """A single IRC command argument."""

    name: str
    required: bool | None = True

    @classmethod
    def parse(cls, s: str) -> "CommandArgument":
        """Parse a CommandArgument from an argument string.

        >>> CommandArgument.parse("[foo]")
        CommandArgument(name='foo', required=False)
        >>> CommandArgument.parse("<foo>")
        CommandArgument(name='foo', required=True)

        :param s: String to parse
        :return: Parsed argument
        """
        start_end = s[0] + s[-1]
        name = s[1:-1]
        if start_end == "<>":
            required = True
        elif start_end == "[]":
            required = False
        else:
            msg = f"Unable to parse argument: {s}"
            raise ValueError(msg)

        return cls(name, required)


@attr.s(frozen=True, hash=True, auto_attribs=True)
class Command:
    """A single IRC command."""

    name: str
    args: list[CommandArgument]
    min_args: int = 0
    max_args: int | None = None


class LookupDict(Mapping[str, Command]):
    """Command lookup dictionary."""

    def __init__(self, *commands: Command) -> None:
        for command in commands:
            setattr(self, command.name.lower(), command)
            setattr(self, command.name.upper(), command)

    def __getitem__(self, key: str) -> Command:
        try:
            return cast("Command", getattr(self, key))
        except AttributeError as e:
            raise KeyError(key) from e

    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


# Commands sent from the client to the server
client_commands = LookupDict(
    Command(
        "PRIVMSG",
        [CommandArgument.parse("<target>"), CommandArgument.parse("<content>")],
    ),
    Command(
        "NOTICE",
        [CommandArgument.parse("<target>"), CommandArgument.parse("<content>")],
    ),
    Command(
        "JOIN",
        [CommandArgument.parse("<channel>"), CommandArgument.parse("[key]")],
    ),
)
