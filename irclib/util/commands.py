"""IRC command data and utilities"""

from typing import Iterator, List, Mapping, Optional, cast

import attr

__all__ = ("Command", "client_commands")


@attr.s(frozen=True, hash=True, auto_attribs=True)
class CommandArgument:
    """A single IRC command argument"""

    name: str
    required: Optional[bool] = True

    @classmethod
    def parse(cls, s: str) -> "CommandArgument":
        """
        Parse a CommandArgument from an argument string

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
            raise ValueError("Unable to parse argument: " + s)

        return cls(name, required)


@attr.s(frozen=True, hash=True, auto_attribs=True)
class Command:
    """A single IRC command"""

    name: str
    args: List[CommandArgument]
    min_args: int = 0
    max_args: Optional[int] = None


class LookupDict(Mapping[str, Command]):
    """Command lookup dictionary"""

    def __init__(self, *commands: Command) -> None:
        for command in commands:
            setattr(self, command.name.lower(), command)
            setattr(self, command.name.upper(), command)

    def __getitem__(self, key: str) -> Command:
        try:
            return cast(Command, getattr(self, key))
        except AttributeError as e:
            raise KeyError(key) from e

    def __len__(self) -> int:
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
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
