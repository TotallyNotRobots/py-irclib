"""Test commands util"""

import pytest

from irclib.util import commands
from irclib.util.commands import CommandArgument


def test_command_lookup() -> None:
    """Test looking up a command"""
    pm = commands.client_commands["privmsg"]
    assert pm is commands.client_commands["PRIVMSG"]
    assert pm is commands.client_commands.privmsg
    assert pm is commands.client_commands.PRIVMSG

    with pytest.raises(KeyError):
        _ = commands.client_commands["foo"]


@pytest.mark.parametrize(
    ("text", "name", "required"),
    [("<foo>", "foo", True), ("[foo]", "foo", False)],
)
def test_arg_parse(text: str, name: str, required: bool) -> None:
    """Test parsing an argument string"""
    arg = CommandArgument.parse(text)
    assert arg.name == name
    assert arg.required is required


def test_parse_error() -> None:
    """Test errors from CommandArgument.parse"""
    with pytest.raises(ValueError, match=r"Unable to parse argument: .*"):
        CommandArgument.parse("{a|b}")
