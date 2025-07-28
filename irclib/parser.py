"""Simple IRC line parser.

Backported from async-irc (https://github.com/snoonetIRC/async-irc.git)
"""

import re
from abc import ABCMeta, abstractmethod
from typing import (
    Dict,
    Final,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import Self, TypeAlias

from irclib.errors import ParseError

__all__ = (
    "Cap",
    "CapList",
    "MessageTag",
    "TagList",
    "Prefix",
    "ParamList",
    "Message",
)
MsgTagList: TypeAlias = Optional["TagList"]
MsgPrefix: TypeAlias = Optional["Prefix"]
MessageTuple: TypeAlias = Tuple[MsgTagList, MsgPrefix, str, "ParamList"]

TAGS_SENTINEL: Final = "@"
TAGS_SEP: Final = ";"
TAG_VALUE_SEP: Final = "="

PREFIX_SENTINEL: Final = ":"
PREFIX_USER_SEP: Final = "!"
PREFIX_HOST_SEP: Final = "@"

PARAM_SEP: Final = " "
TRAIL_SENTINEL: Final = ":"

CAP_SEP: Final = " "
CAP_VALUE_SEP: Final = "="

PREFIX_RE: Final = re.compile(
    r"^:?(?P<nick>.*?)(?:!(?P<user>.*?))?(?:@(?P<host>.*?))?$"
)

TAG_VALUE_ESCAPES: Final = {
    "\\s": " ",
    "\\:": ";",
    "\\r": "\r",
    "\\n": "\n",
    "\\\\": "\\",
}

TAG_VALUE_UNESCAPES: Final = {
    unescaped: escaped for escaped, unescaped in TAG_VALUE_ESCAPES.items()
}

SelfT = TypeVar("SelfT")


class Parseable(metaclass=ABCMeta):
    """Abstract class for parseable objects."""

    @classmethod
    @abstractmethod
    def parse(cls, text: str) -> Self:
        """Parse the object from a string."""
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class Cap(Parseable):
    """Represents a CAP entity as defined in IRCv3.2."""

    def __init__(self, name: str, value: Optional[str] = None) -> None:
        """Construct Cap object.

        Args:
            name: Cap name
            value: Optional Cap value. Defaults to None.
        """
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        """CAP name."""
        return self._name

    @property
    def value(self) -> Optional[str]:
        """CAP value."""
        return self._value

    def as_tuple(self) -> Tuple[str, Optional[str]]:
        """Get data as a tuple of values."""
        return self.name, self.value

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse a CAP entity from a string."""
        name, _, value = text.partition(CAP_VALUE_SEP)
        return cls(name, value or None)

    def __eq__(self, other: object) -> bool:
        """Compare against another cap."""
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, Cap):
            return self.as_tuple() == other.as_tuple()

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare against another cap."""
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, Cap):
            return self.as_tuple() != other.as_tuple()

        return NotImplemented

    def __str__(self) -> str:
        """Represent cap as a string."""
        if self.value:
            return CAP_VALUE_SEP.join((self.name, self.value))

        return self.name


class CapList(Parseable, List[Cap]):
    """Represents a list of CAP entities."""

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse a list of CAPs from a string."""
        if text.startswith(":"):
            text = text[1:]  # Remove leading colon

        # We want to strip any leading or trailing whitespace
        # Some networks (ie: freenode) send a trailing space in a CAP ACK
        stripped = text.strip()

        caps: Iterable[Cap]
        caps = (
            [] if not text else (Cap.parse(s) for s in stripped.split(CAP_SEP))
        )

        return cls(caps)

    def __eq__(self, other: object) -> bool:
        """Compare to a string cap list or list of Cap objects."""
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, list):
            return list(self) == list(other)

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare to a string cap list or sequence of Cap objects."""
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, list):
            return list(self) != list(other)

        return NotImplemented

    def __str__(self) -> str:
        """Represent the list of caps as a string."""
        return CAP_SEP.join(map(str, self))


class MessageTag(Parseable):
    """Basic class to wrap a message tag."""

    def __init__(
        self, name: str, value: str = "", *, has_value: bool = False
    ) -> None:
        """Construct a message tag object.

        Args:
            name: Tag name
            value: Optional tag value. Defaults to "".
            has_value: Whether this tag has a value set. Defaults to False.
        """
        self._name = name
        self._value = value or ""
        self._has_value = has_value

    @property
    def name(self) -> str:
        """Message tag name."""
        return self._name

    @property
    def value(self) -> str:
        """Message tag value."""
        return self._value

    @staticmethod
    def unescape(value: str) -> str:
        """Replace the escaped characters in a tag value with their literals.

        :param value: Escaped string
        :return: Unescaped string
        """
        new_value = ""
        escaped = False
        for char in value:
            if escaped:
                new_value += TAG_VALUE_ESCAPES.get(f"\\{char}", char)
                escaped = False
            elif char == "\\":
                escaped = True
            else:
                new_value += char

        return new_value

    @staticmethod
    def escape(value: str) -> str:
        """Replace characters with their escaped variants.

        :param value: The raw string
        :return: The escaped string
        """
        return "".join(TAG_VALUE_UNESCAPES.get(c, c) for c in value)

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse a tag from a string.

        Arguments:
            text: The basic tag string

        Returns:
            The MessageTag object
        """
        name, sep, value = text.partition(TAG_VALUE_SEP)
        if value:
            value = MessageTag.unescape(value)

        return cls(name, value, has_value=bool(sep))

    def __eq__(self, other: object) -> bool:
        """Compare tag to a string representing a tag or another tag object."""
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, MessageTag):
            return self.name == other.name and self.value == other.value

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare tag to a string representing a tag or another tag object."""
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, MessageTag):
            return not (self.name == other.name and self.value == other.value)

        return NotImplemented

    def __repr__(self) -> str:
        """Represent the tag object in a form useful for debugging."""
        return f"MessageTag(name={self.name!r}, value={self.value!r})"

    def __str__(self) -> str:
        """Represent the tag object as a string representation of a tag."""
        if self.value or self._has_value:
            return f"{self.name}{TAG_VALUE_SEP}{self.escape(self.value)}"

        return self.name


class TagList(Parseable, Dict[str, MessageTag]):
    """Object representing the list of message tags on a line."""

    def __init__(self, tags: Iterable[MessageTag] = ()) -> None:
        """Construct a tag list with optional tags.

        Args:
            tags: Tags to initialize the list with. Defaults to ().
        """
        super().__init__((tag.name, tag) for tag in tags)

    @staticmethod
    def _cmp_type_map(
        obj: object,
    ) -> Union[
        Tuple[dict[str, MessageTag], Literal[True]], Tuple[None, Literal[False]]
    ]:
        if isinstance(obj, str):
            return TagList.parse(obj), True

        if isinstance(obj, dict):
            sample = next(iter(obj.values()), None)
            if obj and (sample is None or isinstance(sample, str)):
                # Handle str -> str dict
                return TagList.from_dict(obj), True

            # Handle str -> MessageTag dict
            return dict(obj), True

        if isinstance(obj, list):
            return TagList(obj), True

        return None, False

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse the list of tags from a string.

        :param text: The string to parse
        :return: The parsed object
        """
        return cls(map(MessageTag.parse, filter(None, text.split(TAGS_SEP))))

    @classmethod
    def from_dict(cls, tags: Dict[str, str]) -> Self:
        """Create a TagList from a dict of tags."""
        return cls(MessageTag(k, v) for k, v in tags.items())

    def __eq__(self, other: object) -> bool:
        """Compare to another tag list, string, or list of MessageTag objects."""
        res = self._cmp_type_map(other)
        if not res[1]:
            return NotImplemented

        return dict(self) == dict(res[0])

    def __ne__(self, other: object) -> bool:
        """Compare to another tag list, string, or list of MessageTag objects."""
        res = self._cmp_type_map(other)
        if not res[1]:
            return NotImplemented

        return dict(self) != dict(res[0])

    def __str__(self) -> str:
        """Represent the tag list as a string."""
        return TAGS_SEP.join(map(str, self.values()))


class Prefix(Parseable):
    """Object representing the prefix of a line."""

    def __init__(
        self,
        nick: Optional[str] = None,
        user: Optional[str] = None,
        host: Optional[str] = None,
    ) -> None:
        """Construct a prefix."""
        self._nick = nick or ""
        self._user = user or ""
        self._host = host or ""

    @property
    def nick(self) -> str:
        """IRC nickname."""
        return self._nick

    @property
    def user(self) -> str:
        """IRC ident/username."""
        return self._user

    @property
    def ident(self) -> str:
        """IRC ident. Alias for `user`."""
        return self.user

    @property
    def host(self) -> str:
        """Hostname."""
        return self._host

    @property
    def mask(self) -> str:
        """The complete n!u@h mask."""
        mask = self.nick
        if self.user:
            mask += PREFIX_USER_SEP + self.user

        if self.host:
            mask += PREFIX_HOST_SEP + self.host

        return mask

    @property
    def _data(self) -> Tuple[str, str, str]:
        return self.nick, self.user, self.host

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse the prefix from a string.

        Arguments:
            text: String to parse

        Returns:
            Parsed Object
        """
        if not text:
            return cls()

        match = PREFIX_RE.match(text)
        if not match:  # pragma: no cover
            # This should never trip, we are pretty lenient with prefixes
            msg = "Invalid IRC prefix format"
            raise ParseError(msg)

        nick, user, host = match.groups()
        return cls(nick, user, host)

    def __iter__(self) -> Iterator[str]:
        """Iterator over the prefix components."""
        return iter(self._data)

    def __eq__(self, other: object) -> bool:
        """Compare to prefix string or another prefix object."""
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, Prefix):
            return self._data == other._data

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare to prefix string or another prefix object."""
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, Prefix):
            return self._data != other._data

        return NotImplemented

    def __bool__(self) -> bool:
        """Return whether the prefix contains any values."""
        return any(self)

    def __str__(self) -> str:
        """Represent the prefix as a string."""
        return self.mask


class ParamList(Parseable, List[str]):
    """An object representing the parameter list from a line."""

    def __init__(self, *params: str, has_trail: bool = False) -> None:
        """Construct list of parameters."""
        super().__init__(params)
        self._has_trail = has_trail

    @property
    def has_trail(self) -> bool:
        """Does the parameter list end with a trailing parameter."""
        return self._has_trail

    @classmethod
    def from_list(cls, data: Sequence[str]) -> Self:
        """Create a ParamList from a Sequence of strings."""
        if not data:
            return cls()

        args = list(data[:-1])
        if data[-1].startswith(TRAIL_SENTINEL) or not data[-1]:
            has_trail = True
            args.append(data[-1])
        else:
            has_trail = False
            args.append(data[-1])

        return cls(*args, has_trail=has_trail)

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse a list of parameters.

        Arguments:
            text: The list of parameters

        Returns:
            The parsed object
        """
        args = []
        has_trail = False
        while text:
            if text[0] == TRAIL_SENTINEL:
                args.append(text[1:])
                has_trail = True
                break

            arg, _, text = text.partition(PARAM_SEP)
            if arg:
                args.append(arg)

        return cls(*args, has_trail=has_trail)

    def __eq__(self, other: object) -> bool:
        """Compare to string or list of parameters."""
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, list):
            return list(self) == list(self.from_list(other))

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare to string or list of parameters."""
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, list):
            return list(self) != list(other)

        return NotImplemented

    def __str__(self) -> str:
        """Represent this parameter list as a string."""
        if not self:
            return ""

        needs_trail = (
            PARAM_SEP in self[-1]
            or self[-1].startswith(TRAIL_SENTINEL)
            or not self[-1]
        )

        if self.has_trail or needs_trail:
            return PARAM_SEP.join(self[:-1] + [TRAIL_SENTINEL + self[-1]])

        return PARAM_SEP.join(self)


def _parse_tags(
    tags: Union[TagList, Dict[str, str], str, None, List[str]],
) -> MsgTagList:
    if isinstance(tags, TagList):
        return tags

    if isinstance(tags, dict):
        return TagList.from_dict(cast(Dict[str, str], tags))

    if isinstance(tags, str):
        return TagList.parse(tags)

    if tags is None:
        return None

    return TagList(MessageTag.parse(str(tag)) for tag in tags)


def _parse_prefix(prefix: Union[Prefix, str, None, Iterable[str]]) -> MsgPrefix:
    if isinstance(prefix, Prefix):
        return prefix

    if isinstance(prefix, str):
        return Prefix.parse(prefix)

    if prefix is None:
        return None

    return Prefix(*prefix)


def _parse_params(
    parameters: Tuple[Union[str, List[str], ParamList], ...],
) -> ParamList:
    if len(parameters) == 1 and not isinstance(parameters[0], str):
        # This seems to be a list
        if isinstance(parameters[0], ParamList):
            return parameters[0]

        return ParamList.from_list(parameters[0])

    return ParamList.from_list(cast(Tuple[str, ...], parameters))


class Message(Parseable):
    """An object representing a parsed IRC line."""

    def __init__(
        self,
        tags: Union[TagList, Dict[str, str], str, None, List[str]],
        prefix: Union[str, Prefix, None, Iterable[str]],
        command: str,
        *parameters: Union[str, List[str], ParamList],
    ) -> None:
        """Construct message object."""
        self._tags = _parse_tags(tags)
        self._prefix = _parse_prefix(prefix)
        self._command = command
        self._parameters = _parse_params(parameters)

    @property
    def tags(self) -> MsgTagList:
        """IRC tag list."""
        return self._tags

    @property
    def prefix(self) -> MsgPrefix:
        """IRC prefix."""
        return self._prefix

    @property
    def command(self) -> str:
        """IRC command."""
        return self._command

    @property
    def parameters(self) -> ParamList:
        """Command parameter list."""
        return self._parameters

    def as_tuple(self) -> MessageTuple:
        """Get the message object as a tuple of values."""
        return self.tags, self.prefix, self.command, self.parameters

    @classmethod
    def parse(cls, text: Union[str, bytes]) -> Self:
        """Parse an IRC message in to objects."""
        if isinstance(text, memoryview):
            text = text.tobytes().decode(errors="ignore")

        if isinstance(text, (bytes, bytearray)):
            text = text.decode(errors="ignore")

        tags = ""
        prefix = ""
        if text.startswith(TAGS_SENTINEL):
            tags, _, text = text.partition(PARAM_SEP)

        if text.startswith(PREFIX_SENTINEL):
            prefix, _, text = text.partition(PARAM_SEP)

        command, _, params = text.partition(PARAM_SEP)
        # Differentiate empty tags '@ CMD' from no tags 'CMD'
        tags_obj = TagList.parse(tags[1:]) if tags else None
        # Differentiate empty prefix ': CMD' from no prefix 'CMD'
        prefix_obj = Prefix.parse(prefix[1:]) if prefix else None
        command = command.upper()
        param_obj = ParamList.parse(params)
        return cls(tags_obj, prefix_obj, command, param_obj)

    def __eq__(self, other: object) -> bool:
        """Compare to another message which can be str, bytes, or a Message object."""
        if isinstance(other, (str, bytes)):
            return self == Message.parse(other)

        if isinstance(other, Message):
            return self.as_tuple() == other.as_tuple()

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare to another message which can be str, bytes, or a Message object."""
        if isinstance(other, (str, bytes)):
            return self != Message.parse(other)

        if isinstance(other, Message):
            return self.as_tuple() != other.as_tuple()

        return NotImplemented

    def __bool__(self) -> bool:
        """Check if the line is empty or not."""
        return any(self.as_tuple())

    def __str__(self) -> str:
        """Represent this Message as a properly formatted IRC line."""
        tag_str = "" if self.tags is None else TAGS_SENTINEL + str(self.tags)
        prefix_str = (
            "" if self.prefix is None else PREFIX_SENTINEL + str(self.prefix)
        )

        return PARAM_SEP.join(
            str(s)
            for s in (tag_str, prefix_str, self.command, self.parameters)
            if s
        )
