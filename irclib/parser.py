"""
Simple IRC line parser

Backported from async-irc (https://github.com/snoonetIRC/async-irc.git)
"""

import re
from abc import ABCMeta, abstractmethod

from irclib.errors import ParseError

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

PREFIX_RE = re.compile(r'^:?(?P<nick>.*?)(?:!(?P<user>.*?))?(?:@(?P<host>.*?))?$')

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


class Cap(Parseable):
    """Represents a CAP entity as defined in IRCv3.2"""

    def __init__(self, name, value=None):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def _data(self):
        return self.name, self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, Cap):
            return tuple(self) == tuple(other)

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, Cap):
            return tuple(self) != tuple(other)

        return NotImplemented

    def __str__(self):
        """
        :rtype: str
        """
        if self.value:
            return CAP_VALUE_SEP.join(self)

        return self.name

    def __iter__(self):
        """
        Allow unpacking as a tuple
        """
        return iter(self._data)

    @staticmethod
    def parse(text):
        """Parse a CAP entity from a string
        :type text: str
        """
        name, _, value = text.partition(CAP_VALUE_SEP)
        return Cap(name, value or None)


class CapList(Parseable, list):
    """Represents a list of CAP entities"""

    def __eq__(self, other):
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, list):
            return list(self) == list(other)

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, list):
            return list(self) != list(other)

        return NotImplemented

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
        if text.startswith(':'):
            text = text[1:]  # Remove leading colon

        # We want to strip any leading or trailing whitespace
        # Some networks (ie: freenode) send a trailing space in a CAP ACK
        stripped = text.strip()

        return CapList(map(Cap.parse, stripped.split(CAP_SEP)))


class MessageTag(Parseable):
    """
    Basic class to wrap a message tag
    """

    def __init__(self, name, value=None):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def __iter__(self):
        return iter((self.name, self.value))

    @staticmethod
    def unescape(value):
        """
        Replace the escaped characters in a tag value with their literals
        :param value: Escaped string
        :return: Unescaped string
        """
        new_value = ""
        escaped = False
        for i, c in enumerate(value):
            if escaped:
                new_value += TAG_VALUE_ESCAPES.get('\\{}'.format(c), c)
                escaped = False
            elif c == '\\':
                escaped = True
            else:
                new_value += c

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

        if isinstance(other, MessageTag):
            return tuple(self) == tuple(other)

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, MessageTag):
            return tuple(self) != tuple(other)

        return NotImplemented

    @staticmethod
    def parse(text):
        """
        Parse a tag from a string
        :type text: str
        :param text: The basic tag string
        :return: The MessageTag object
        """
        name, sep, value = text.partition(TAG_VALUE_SEP)
        if value:
            value = MessageTag.unescape(value)

        return MessageTag(name, value if sep else None)


class TagList(Parseable, dict):
    """Object representing the list of message tags on a line"""

    def __init__(self, tags):
        super().__init__((tag.name, tag) for tag in tags)

    def __str__(self):
        return TAGS_SEP.join(map(str, self.values()))

    def __eq__(self, other):
        if isinstance(other, str):
            return self == TagList.parse(other)

        if isinstance(other, dict):
            return dict(self) == dict(other)

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, str):
            return self != TagList.parse(other)

        if isinstance(other, dict):
            return dict(self) != dict(other)

        return NotImplemented

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

    @staticmethod
    def from_dict(tags):
        return TagList(
            MessageTag(k, v) for k, v in tags.items()
        )


class Prefix(Parseable):
    """
    Object representing the prefix of a line
    """

    def __init__(self, nick, user=None, host=None):
        self._nick = nick or ''
        self._user = user or ''
        self._host = host or ''

    @property
    def nick(self):
        return self._nick

    @property
    def user(self):
        return self._user

    @property
    def ident(self):
        return self._user

    @property
    def host(self):
        return self._host

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

    @property
    def _data(self):
        return self.nick, self.user, self.host

    def __iter__(self):
        return iter(self._data)

    def __str__(self):
        return self.mask

    def __bool__(self):
        return bool(self.nick)

    def __eq__(self, other):
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, Prefix):
            return self._data == other._data

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, Prefix):
            return self._data != other._data

        return NotImplemented

    @staticmethod
    def parse(text):
        """
        Parse the prefix from a string
        :type text: str
        :param text: String to parse
        :return: Parsed Object
        """
        if not text:
            return Prefix('')

        match = PREFIX_RE.match(text)
        if not match:
            raise ParseError("Invalid IRC prefix format")

        nick, user, host = match.groups()
        return Prefix(nick, user, host)


class ParamList(Parseable, list):
    """
    An object representing the parameter list from a line
    """

    def __init__(self, *params, has_trail=False):
        super().__init__(params)
        self._has_trail = has_trail

    @property
    def has_trail(self):
        return self._has_trail

    def __str__(self):
        if not self:
            return ''

        if self.has_trail or PARAM_SEP in self[-1]:
            return PARAM_SEP.join(self[:-1] + [TRAIL_SENTINEL + self[-1]])

        return PARAM_SEP.join(self)

    def __eq__(self, other):
        if isinstance(other, str):
            return self == self.parse(other)

        if isinstance(other, list):
            return list(self) == list(self.from_list(other))

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, str):
            return self != self.parse(other)

        if isinstance(other, list):
            return list(self) != list(other)

        return NotImplemented

    @staticmethod
    def from_list(data):
        if not data:
            return ParamList()

        args = list(data[:-1])
        if data[-1].startswith(TRAIL_SENTINEL) or not data[-1]:
            has_trail = True
            args.append(data[-1])
        else:
            has_trail = False
            args.append(data[-1])

        return ParamList(*args, has_trail=has_trail)

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

        return ParamList(*args, has_trail=has_trail)


class Message(Parseable):
    """
    An object representing a parsed IRC line
    """

    def __init__(self, tags, prefix, command, *parameters):
        if isinstance(tags, TagList):
            self._tags = tags
        elif isinstance(tags, dict):
            self._tags = TagList.from_dict(tags)
        elif isinstance(tags, str):
            self._tags = TagList.parse(tags)
        elif tags is None:
            self._tags = None
        else:
            self._tags = TagList(MessageTag.parse(str(tag)) for tag in tags)

        if isinstance(prefix, Prefix):
            self._prefix = prefix
        elif isinstance(prefix, str):
            self._prefix = Prefix.parse(prefix)
        elif prefix is None:
            self._prefix = None
        else:
            self._prefix = Prefix(*prefix)

        self._command = command

        if len(parameters) == 1 and not isinstance(parameters, str):
            if isinstance(parameters, ParamList):
                self._parameters = parameters[0]
            else:
                self._parameters = ParamList.from_list(parameters[0])
        else:
            self._parameters = ParamList.parse(parameters)

    @property
    def tags(self):
        return self._tags

    @property
    def prefix(self):
        return self._prefix

    @property
    def command(self):
        return self._command

    @property
    def parameters(self):
        return self._parameters

    def __iter__(self):
        return iter((self.tags, self.prefix, self.command, self.parameters))

    def __str__(self):
        tag_str = '' if self.tags is None else TAGS_SENTINEL + str(self.tags)
        prefix_str = '' if self.prefix is None else PREFIX_SENTINEL + str(self.prefix)

        return PARAM_SEP.join(
            str(s) for s in (
                tag_str, prefix_str, self.command, self.parameters
            )
            if s
        )

    def __bool__(self):
        return any(self)

    def __eq__(self, other):
        if isinstance(other, (str, bytes)):
            return self == Message.parse(other)

        if isinstance(other, Message):
            return tuple(self) == tuple(other)

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, (str, bytes)):
            return self != Message.parse(other)

        if isinstance(other, Message):
            return tuple(self) != tuple(other)

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
        # Differentiate empty tags '@ CMD' from no tags 'CMD'
        tags = TagList.parse(tags[1:]) if tags else None
        # Differentiate empty prefix ': CMD' from no prefix 'CMD'
        prefix = Prefix.parse(prefix[1:]) if prefix else None
        command = command.upper()
        params = ParamList.parse(params)
        return Message(tags, prefix, command, params)
