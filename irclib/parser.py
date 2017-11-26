"""
Simple IRC line parser

Backported from async-irc (https://github.com/snoonetIRC/async-irc.git)
"""

import re
from abc import ABCMeta, abstractmethod
from collections import namedtuple

from irclib.errors import ParseError
from irclib.util.frozendict import FrozenDict

TAGS_SENTINEL = '@'
TAGS_SEP = ';'
TAG_VALUE_SEP = '='

PREFIX_SENTINEL = ':'
PREFIX_USER_SEP = '!'
PREFIX_HOST_SEP = '@'

PARAM_SEP = ' '
TRAIL_SENTINEL = ':'

CAP_SEP = ' '
CAP_VALUE_SEP = '='

PREFIX_RE = re.compile(r'^:?(?P<nick>.+?)(?:!(?P<user>.+?))?(?:@(?P<host>.+?))?$')

TAG_VALUE_ESCAPES = {
    '\\s': ' ',
    '\\:': ';',
    '\\r': '\r',
    '\\n': '\n',
    '\\\\': '\\',
}

TAG_VALUE_UNESCAPES = {
    unescaped: escaped
    for escaped, unescaped in TAG_VALUE_ESCAPES.items()
}


class Parseable(metaclass=ABCMeta):
    """Abstract class for parseable objects"""

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse(text):
        """Parse the object from a string
        :type text: str
        """
        raise NotImplementedError


_Cap = namedtuple('_Cap', 'name value')


class Cap(Parseable, _Cap):
    """Represents a CAP entity as defined in IRCv3.2"""

    def __new__(cls, name, value=None):
        return _Cap.__new__(cls, name, value)

    def __str__(self):
        """
        :rtype: str
        """
        if self.value:
            return CAP_VALUE_SEP.join(self)

        return self.name

    @staticmethod
    def parse(text):
        """Parse a CAP entity from a string
        :type text: str
        """
        name, _, value = text.partition(CAP_VALUE_SEP)
        return Cap(name, value or None)


class CapList(Parseable, tuple):
    """Represents a list of CAP entities"""

    def __str__(self):
        """
        :rtype: str
        """
        return CAP_SEP.join(map(str, self))

    @staticmethod
    def parse(text):
        """Parse a list of CAPs from a string
        :type text: str
        """
        return CapList(map(Cap.parse, text.split(CAP_SEP)))


_MessageTag = namedtuple('_MessageTag', 'name value')


class MessageTag(Parseable, _MessageTag):
    """
    Basic class to wrap a message tag
    """

    def __new__(cls, name, value=None):
        return _MessageTag.__new__(cls, name, value)

    @staticmethod
    def unescape(value):
        """
        Replace the escaped characters in a tag value with their literals
        :param value: Escaped string
        :return: Unescaped string
        """
        new_value = ""
        found = False
        for i in range(len(value)):
            if found:
                found = False
                continue

            if value[i] == '\\':
                if i + 1 >= len(value):
                    raise ParseError("Unexpected end of string while parsing: {}".format(value))

                new_value += TAG_VALUE_ESCAPES[value[i:i + 2]]
                found = True
            else:
                new_value += value[i]

        return new_value

    @staticmethod
    def escape(value):
        """
        Replace characters with their escaped variants
        :param value: The raw string
        :return: The escaped string
        """
        return "".join(TAG_VALUE_UNESCAPES.get(c, c) for c in value)

    def __str__(self):
        if self.value:
            return "{}{}{}".format(
                self.name, TAG_VALUE_SEP, self.escape(self.value)
            )

        return self.name

    def __eq__(self, other):
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, type(self)):
            return tuple(self) == tuple(other)

        return NotImplemented

    @staticmethod
    def parse(text):
        """
        Parse a tag from a string
        :type text: str
        :param text: The basic tag string
        :return: The MessageTag object
        """
        name, _, value = text.partition(TAG_VALUE_SEP)
        if value:
            value = MessageTag.unescape(value)

        return MessageTag(name, value or None)


class TagList(Parseable, FrozenDict):
    """Object representing the list of message tags on a line"""

    def __init__(self, tags):
        super().__init__((tag.name, tag) for tag in tags)

    def __str__(self):
        return TAGS_SENTINEL + TAGS_SEP.join(map(str, self.values()))

    @staticmethod
    def parse(text):
        """
        Parse the list of tags from a string
        :type text: str
        :param text: The string to parse
        :return: The parsed object
        """
        return TagList(
            map(MessageTag.parse, filter(None, text.split(TAGS_SEP)))
        )


_Prefix = namedtuple('_Prefix', 'nick user host')


class Prefix(Parseable, _Prefix):
    """
    Object representing the prefix of a line
    """

    def __new__(cls, nick, user=None, host=None):
        return _Prefix.__new__(cls, nick, user, host)

    @property
    def mask(self):
        """
        The complete n!u@h mask
        """
        mask = self.nick
        if self.user:
            mask += PREFIX_USER_SEP + self.user

        if self.host:
            mask += PREFIX_HOST_SEP + self.host

        return mask

    def __str__(self):
        return PREFIX_SENTINEL + self.mask

    def __bool__(self):
        return bool(self.nick)

    @staticmethod
    def parse(text):
        """
        Parse the prefix from a string
        :type text: str
        :param text: String to parse
        :return: Parsed Object
        """
        if not text:
            return Prefix('', None, None)

        match = PREFIX_RE.match(text)
        if not match:
            raise ParseError("Invalid IRC prefix format")

        nick, user, host = match.groups()
        return Prefix(nick, user, host)


class ParamList(Parseable, tuple):
    """
    An object representing the parameter list from a line
    """

    def __new__(cls, seq, has_trail=False):
        seq = list(seq)
        has_trail = has_trail or (seq and PARAM_SEP in seq[-1])
        if seq:
            seq[-1] = (TRAIL_SENTINEL if has_trail else "") + seq[-1]

        return tuple.__new__(cls, seq)

    def __str__(self):
        return PARAM_SEP.join(self)

    @staticmethod
    def parse(text):
        """
        Parse a list of parameters
        :type text: str
        :param text: The list of parameters
        :return: The parsed object
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

        return ParamList(args, has_trail=has_trail)


_Message = namedtuple('_Message', 'tags prefix command parameters')


class Message(Parseable, _Message):
    """
    An object representing a parsed IRC line
    """

    def __new__(cls, tags=None, prefix=None, command=None, parameters=None):
        return _Message.__new__(cls, tags, prefix, command, parameters)

    def __str__(self):
        return PARAM_SEP.join(map(str, filter(None, self)))

    def __bool__(self):
        return any(self)

    def __eq__(self, other):
        if isinstance(other, (str, bytes)):
            return self == Message.parse(other)

        if isinstance(other, Message):
            return tuple(self) == tuple(other)

        return NotImplemented

    @staticmethod
    def parse(text):
        """Parse an IRC message in to objects
        :type text: str
        """
        if isinstance(text, bytes):
            text = text.decode(errors="ignore")

        tags = ''
        prefix = ''
        if text.startswith(TAGS_SENTINEL):
            tags, _, text = text.partition(PARAM_SEP)

        if text.startswith(PREFIX_SENTINEL):
            prefix, _, text = text.partition(PARAM_SEP)

        command, _, params = text.partition(PARAM_SEP)
        tags = TagList.parse(tags[1:])
        prefix = Prefix.parse(prefix[1:])
        command = command.upper()
        params = ParamList.parse(params)
        return Message(tags, prefix, command, params)
