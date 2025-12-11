# SPDX-FileCopyrightText: 2017-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test IRC parser."""

import datetime
from typing import TypedDict

import parser_tests.data
import pytest

from irclib.parser import (
    Cap,
    CapList,
    Message,
    MessageTag,
    ParamList,
    Parseable,
    Prefix,
    TagList,
)
from irclib.util.string import ASCII, String


class MsgAtoms(TypedDict):
    """Message components for test cases."""

    tags: dict[str, str]
    source: str
    verb: str
    params: list[str]


class MsgSplitCase(TypedDict):
    """Message parsing test case data."""

    input: str
    atoms: MsgAtoms


class UserHostAtoms(TypedDict):
    """Prefix components for test cases."""

    nick: str
    user: str
    host: str


class UserHostSplitCase(TypedDict):
    """Prefix parsing test case data."""

    source: str
    atoms: UserHostAtoms


class MsgJoinCase(TypedDict):
    """Message construction test case data."""

    atoms: MsgAtoms
    matches: list[str]


def test_line() -> None:
    """Test parsing a single IRC message."""
    assert Message.parse("COMMAND") == "COMMAND"
    assert Message.parse("command") == "COMMAND"

    msg1 = Message.parse("PRIVMSG")

    assert msg1.command == "PRIVMSG"

    msg2 = Message.parse(
        r"@test=data;test1=more\sdata :nick!user@host COMMAND arg1 arg2 :trailing text"
    )

    assert msg2.prefix
    assert msg2.prefix.host == "host"


class TestCap:
    """Test Cap class."""

    @pytest.mark.parametrize(
        ("name", "value", "expected"),
        [
            ("capname", "somevalue", "capname=somevalue"),
            ("capname", None, "capname"),
        ],
    )
    def test_str(self, name: str, value: str | None, expected: str) -> None:
        """Test string conversion."""
        c = Cap(name, value)
        assert str(c) == expected

    @pytest.mark.parametrize(("name", "value"), [("a", "b"), ("foo", "bar")])
    def test_eq(self, name: str, value: str) -> None:
        """Test equals."""
        assert Cap(name, value) == Cap(name, value)

    @pytest.mark.parametrize(
        ("name", "value", "string"),
        [("a", "b", "a=b"), ("foo", "bar", "foo=bar")],
    )
    def test_eq_str(self, name: str, value: str, string: str) -> None:
        """Test equals string."""
        assert Cap(name, value) == string
        assert string == Cap(name, value)

    @pytest.mark.parametrize(
        ("name", "value", "other_name", "other_value"),
        [
            ("a", "b", "c", "b"),
            ("a", "b", "a", "c"),
            ("a", "b", "c", "d"),
            ("foo", "bar", "baz", "zing"),
            ("foo", "bar", "baz", None),
            ("foo", None, "baz", None),
            ("foo", None, "baz", "zing"),
            ("foo", "bar", "foo", "zing"),
            ("foo", "bar", "foo", None),
            ("foo", None, "foo", "zing"),
        ],
    )
    def test_ne(
        self,
        name: str,
        value: str | None,
        other_name: str,
        other_value: str | None,
    ) -> None:
        """Test not-equals."""
        assert Cap(name, value) != Cap(other_name, other_value)
        assert Cap(other_name, other_value) != Cap(name, value)

    @pytest.mark.parametrize(
        ("name", "value", "string"),
        [
            ("a", "b", "c=b"),
            ("a", "b", "a=c"),
            ("a", "b", "c=d"),
            ("foo", "bar", "baz=zing"),
            ("foo", "bar", "foo=zing"),
            ("foo", "bar", "foo"),
            ("foo", "bar", "foo=baz"),
            ("foo", None, "foo=baz"),
            ("foo", None, "baz"),
        ],
    )
    def test_ne_str(self, name: str, value: str | None, string: str) -> None:
        """Test not-equals string."""
        assert Cap(name, value) != string
        assert string != Cap(name, value)

    @pytest.mark.parametrize(("obj", "other"), [(Cap("foo"), 1)])
    def test_no_cmp(self, obj: Cap, other: object) -> None:
        """Test not-equals."""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize(
        ("text", "name", "value"),
        [("vendor.example.org/cap-name", "vendor.example.org/cap-name", None)],
    )
    def test_parse(self, text: str, name: str, value: str | None) -> None:
        """Test parsing string."""
        cap = Cap.parse(text)
        assert cap.name == name
        assert cap.value == value


class TestCapList:
    """Test parsing a list of CAPs."""

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            (
                "blah blah-blah cap-1 test-cap=value-data",
                (
                    ("blah", None),
                    ("blah-blah", None),
                    ("cap-1", None),
                    ("test-cap", "value-data"),
                ),
            ),
            (
                "blah blah-blah cap-1 test-cap=value-data ",
                (
                    ("blah", None),
                    ("blah-blah", None),
                    ("cap-1", None),
                    ("test-cap", "value-data"),
                ),
            ),
            (
                ":blah blah-blah cap-1 test-cap=value-data",
                (
                    ("blah", None),
                    ("blah-blah", None),
                    ("cap-1", None),
                    ("test-cap", "value-data"),
                ),
            ),
            (
                ":blah blah-blah cap-1 test-cap=value-data ",
                (
                    ("blah", None),
                    ("blah-blah", None),
                    ("cap-1", None),
                    ("test-cap", "value-data"),
                ),
            ),
            ("", ()),
        ],
    )
    def test_parse(
        self, text: str, expected: tuple[tuple[str, str | None], ...]
    ) -> None:
        """Test string parsing."""
        parsed = CapList.parse(text)
        assert len(parsed) == len(expected)
        for (name, value), actual in zip(expected, parsed, strict=False):
            assert actual.name == name
            assert actual.value == value

    @pytest.mark.parametrize("caps", [[], [Cap("a"), Cap("b", "c")]])
    def test_eq_list(self, caps: list[Cap]) -> None:
        """Test equals list."""
        assert CapList(caps) == caps
        assert caps == CapList(caps)

    @pytest.mark.parametrize("caps", [[], [Cap("a"), Cap("b", "c")]])
    def test_ne_list(self, caps: list[Cap]) -> None:
        """Test not-equals list."""
        b = CapList(caps) != caps
        assert not b
        b1 = caps != CapList(caps)
        assert not b1

    @pytest.mark.parametrize(
        ("caps", "text"),
        [
            ([], ""),
            ([Cap("a"), Cap("b", "c")], "a b=c"),
            ([Cap("a"), Cap("b", "c")], "a b=c "),
        ],
    )
    def test_eq_str(self, caps: list[Cap], text: str) -> None:
        """Test equals strings."""
        assert CapList(caps) == text
        assert text == CapList(caps)

    @pytest.mark.parametrize(
        ("caps", "text"),
        [
            ([], ""),
            ([Cap("a"), Cap("b", "c")], "a b=c"),
            ([Cap("a"), Cap("b", "c")], "a b=c "),
        ],
    )
    def test_ne_str(self, caps: list[Cap], text: str) -> None:
        """Test not-equals strings."""
        b = CapList(caps) != text
        assert not b
        b1 = text != CapList(caps)
        assert not b1

    @pytest.mark.parametrize(
        ("obj", "other"), [(CapList(), None), (CapList(), 0)]
    )
    def test_no_cmp(self, obj: CapList, other: object) -> None:
        """Test not-equals."""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize(
        ("obj", "text"),
        [
            (CapList([Cap("foo")]), "foo"),
            (CapList([Cap("foo"), Cap("bar")]), "foo bar"),
            (CapList([Cap("foo"), Cap("bar=baz")]), "foo bar=baz"),
        ],
    )
    def test_str(self, obj: CapList, text: str) -> None:
        """Test string conversion."""
        assert str(obj) == text
        assert text == str(obj)


class TestMessageTag:
    """Test parsing a single message tag."""

    @pytest.mark.parametrize(
        ("text", "name", "value"),
        [
            ("a=b", "a", "b"),
            ("test/blah=", "test/blah", ""),
            (r"blah=aa\r\n\:\\", "blah", "aa\r\n;\\"),
            (r"blah=aa\r\n\s\:\\", "blah", "aa\r\n ;\\"),
            (r"blah=\s", "blah", " "),
            ("blah=\\", "blah", ""),
        ],
    )
    def test_parse(self, text: str, name: str, value: str | None) -> None:
        """Test parsing a string."""
        tag = MessageTag.parse(text)
        assert tag.name == name
        assert tag.value == value

    @pytest.mark.parametrize(("name", "value"), [("a", None), ("a", "b")])
    def test_eq(self, name: str, value: str | None) -> None:
        """Test equals."""
        assert MessageTag(name, value) == MessageTag(name, value)  # type: ignore[arg-type]

    @pytest.mark.parametrize(("name", "value"), [("a", None), ("a", "b")])
    def test_ne(self, name: str, value: str | None) -> None:
        """Test not-equals."""
        b = MessageTag(name, value) != MessageTag(name, value)  # type: ignore[arg-type]
        assert not b

    @pytest.mark.parametrize(
        ("name", "value", "text"),
        [("foo", None, "foo"), ("foo", "bar", "foo=bar")],
    )
    def test_eq_str(self, name: str, value: str | None, text: str) -> None:
        """Test equals string."""
        assert MessageTag(name, value) == text  # type: ignore[arg-type]
        assert text == MessageTag(name, value)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ("name", "value", "text"),
        [("foo", None, "foo"), ("foo", "bar", "foo=bar")],
    )
    def test_ne_str(self, name: str, value: str | None, text: str) -> None:
        """Test not-equals string."""
        b = MessageTag(name, value) != text  # type: ignore[arg-type]
        assert not b
        b1 = text != MessageTag(name, value)  # type: ignore[arg-type]
        assert not b1

    @pytest.mark.parametrize(
        ("obj", "other"), [(MessageTag(""), None), (MessageTag(""), 1)]
    )
    def test_no_cmp(self, obj: MessageTag, other: object) -> None:
        """Test not-equals other types."""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj


class TestTagList:
    """Test parsing a tag list."""

    @pytest.mark.parametrize(
        ("text", "tags"),
        [
            ("a;", [("a", "")]),
            ("a=1;", [("a", "1")]),
            ("a=1;b;c", [("a", "1"), ("b", ""), ("c", "")]),
            ("a=1;b;c;", [("a", "1"), ("b", ""), ("c", "")]),
            ("", []),
            (";", []),
            (r"a=ab\r\s\n\:\\;b=abc", [("a", "ab\r \n;\\"), ("b", "abc")]),
        ],
    )
    def test_parse(self, text: str, tags: list[tuple[str, str]]) -> None:
        """Test parsing from string."""
        tag_list = TagList.parse(text)

        assert len(tag_list) == len(tags)

        for name, value in tags:
            tag = tag_list[name]
            assert tag.name == name
            assert tag.value == value

    @pytest.mark.parametrize(
        "tags", [[], [MessageTag("a")], [MessageTag("b", "c")]]
    )
    def test_eq(self, tags: list[MessageTag]) -> None:
        """Test equals."""
        assert TagList(tags) == TagList(tags)

    @pytest.mark.parametrize(
        "tags", [[], [MessageTag("a")], [MessageTag("b", "c")]]
    )
    def test_ne(self, tags: list[MessageTag]) -> None:
        """Test not-equals."""
        b = TagList(tags) != TagList(tags)
        assert not b

    @pytest.mark.parametrize(
        "tags", [[], [MessageTag("a")], [MessageTag("b", "c")]]
    )
    def test_eq_list(self, tags: list[MessageTag]) -> None:
        """Test equals list."""
        assert TagList(tags) == tags
        assert tags == TagList(tags)

    @pytest.mark.parametrize(
        "tags", [[], [MessageTag("a")], [MessageTag("b", "c")]]
    )
    def test_ne_list(self, tags: list[MessageTag]) -> None:
        """Test not-equals list."""
        b = TagList(tags) != tags
        assert not b
        b1 = tags != TagList(tags)
        assert not b1

    @pytest.mark.parametrize(
        ("obj", "other"),
        [
            (TagList(), {}),
            (TagList([MessageTag("a")]), {"a": None}),
            (TagList([MessageTag("b", "c")]), {"b": "c"}),
        ],
    )
    def test_eq_dict(self, obj: TagList, other: dict[str, str | None]) -> None:
        """Test equals dict."""
        assert obj == other
        assert other == obj

    @pytest.mark.parametrize(
        ("obj", "other"),
        [
            (TagList(), {}),
            (TagList([MessageTag("a")]), {"a": None}),
            (TagList([MessageTag("b", "c")]), {"b": "c"}),
        ],
    )
    def test_ne_dict(self, obj: TagList, other: dict[str, str | None]) -> None:
        """Test not-equals dict."""
        b = obj != other
        assert not b
        b1 = other != obj
        assert not b1

    @pytest.mark.parametrize(
        ("tags", "text"),
        [([], ""), ([MessageTag("a")], "a"), ([MessageTag("b", "c")], "b=c")],
    )
    def test_eq_str(self, tags: list[MessageTag], text: str) -> None:
        """Test equals strings."""
        assert TagList(tags) == text
        assert text == TagList(tags)

    @pytest.mark.parametrize(
        ("tags", "text"),
        [([], ""), ([MessageTag("a")], "a"), ([MessageTag("b", "c")], "b=c")],
    )
    def test_ne_str(self, tags: list[MessageTag], text: str) -> None:
        """Test not-equals strings."""
        b = TagList(tags) != text
        assert not b
        b1 = text != TagList(tags)
        assert not b1

    @pytest.mark.parametrize(
        ("obj", "other"), [(TagList(), 0), (TagList(), None)]
    )
    def test_no_cmp(self, obj: TagList, other: object) -> None:
        """Test not-equals other types."""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj


class TestPrefix:
    """Test parsing a prefix."""

    @pytest.mark.parametrize(
        ("text", "nick", "user", "host"),
        [
            ("", "", "", ""),
            (":", "", "", ""),
            ("somenick", "somenick", "", ""),
            ("somenick!user", "somenick", "user", ""),
            ("somenick@host", "somenick", "", "host"),
            ("somenick!user@host", "somenick", "user", "host"),
            (":somenick", "somenick", "", ""),
            (":somenick!user", "somenick", "user", ""),
            (":somenick@host", "somenick", "", "host"),
            (":somenick!user@host", "somenick", "user", "host"),
            (":nick!@", "nick", "", ""),
            (":nick!user@", "nick", "user", ""),
            (":nick!@host", "nick", "", "host"),
            (":!@", "", "", ""),
            (":!user@", "", "user", ""),
            (":!@host", "", "", "host"),
            (":!user@host", "", "user", "host"),
        ],
    )
    def test_parse(self, text: str, nick: str, user: str, host: str) -> None:
        """Test parsing a string."""
        p = Prefix.parse(text)

        assert p.nick == nick
        assert p.user == user
        assert p.ident == user
        assert p.host == host

    @pytest.mark.parametrize(
        ("nick", "user", "host"),
        [
            ("nick", None, None),
            ("nick", "user", "host"),
            ("nick", None, "host"),
            ("nick", "user", None),
        ],
    )
    def test_eq(self, nick: str, user: str | None, host: str | None) -> None:
        """Test equals."""
        assert Prefix(nick, user, host) == Prefix(nick, user, host)

    @pytest.mark.parametrize(
        ("nick", "user", "host"),
        [
            ("nick", None, None),
            ("nick", "user", "host"),
            ("nick", None, "host"),
            ("nick", "user", None),
        ],
    )
    def test_ne(self, nick: str, user: str | None, host: str | None) -> None:
        """Test not-equals."""
        b = Prefix(nick, user, host) != Prefix(nick, user, host)
        assert not b

    @pytest.mark.parametrize(
        ("text", "nick", "user", "host"),
        [
            ("nick", "nick", None, None),
            ("nick!user@host", "nick", "user", "host"),
            ("nick@host", "nick", None, "host"),
            ("nick!user", "nick", "user", None),
        ],
    )
    def test_eq_str(
        self, text: str, nick: str | None, user: str | None, host: str | None
    ) -> None:
        """Test equals string."""
        assert Prefix(nick, user, host) == text
        assert text == Prefix(nick, user, host)

    @pytest.mark.parametrize(
        ("text", "nick", "user", "host"),
        [
            ("nick", "nick", None, None),
            ("nick!user@host", "nick", "user", "host"),
            ("nick@host", "nick", None, "host"),
            ("nick!user", "nick", "user", None),
        ],
    )
    def test_ne_str(
        self, text: str, nick: str | None, user: str | None, host: str | None
    ) -> None:
        """Test not-equals string comparisons."""
        b = Prefix(nick, user, host) != text
        assert not b
        b1 = text != Prefix(nick, user, host)
        assert not b1

    @pytest.mark.parametrize(
        ("obj", "other"),
        [(Prefix(""), 0), (Prefix(""), None), (Prefix(""), ())],
    )
    def test_no_cmp(self, obj: Prefix, other: object) -> None:
        """Test not-equals."""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize(
        ("obj", "nick", "user", "host"),
        [
            (Prefix("nick"), "nick", "", ""),
            (Prefix("nick", "user", "host"), "nick", "user", "host"),
            (Prefix("nick", host="host"), "nick", "", "host"),
            (Prefix("nick", "user"), "nick", "user", ""),
        ],
    )
    def test_unpack(
        self, obj: Prefix, nick: str | None, user: str | None, host: str | None
    ) -> None:
        """Test unpacking Prefix."""
        n, u, h = obj
        assert (n, u, h) == (nick, user, host)

    @pytest.mark.parametrize(
        ("nick", "user", "host"),
        [
            ("nick", "", ""),
            ("nick", None, None),
            ("nick", "user", "host"),
            ("nick", "", "host"),
            ("nick", "user", ""),
            ("nick", None, "host"),
            ("nick", "user", None),
            ("", "user", ""),
            ("", "user", "host"),
            ("", "", "host"),
            (None, "user", None),
            (None, "user", "host"),
            (None, None, "host"),
        ],
    )
    def test_bool(
        self, nick: str | None, user: str | None, host: str | None
    ) -> None:
        """Test cases where bool(Prefix) == True."""
        assert Prefix(nick, user, host)

    @pytest.mark.parametrize(
        ("nick", "user", "host"),
        [
            ("", "", ""),
            (None, None, None),
            ("", None, None),
            (None, "", None),
            (None, None, ""),
            ("", "", None),
            ("", None, ""),
            (None, "", ""),
        ],
    )
    def test_bool_false(
        self, nick: str | None, user: str | None, host: str | None
    ) -> None:
        """Test cases where bool(Prefix) == False."""
        assert not Prefix(nick, user, host)


class TestParamList:
    """Test parsing a parameter list."""

    @pytest.mark.parametrize(
        ("obj", "text"),
        [
            (ParamList(), ""),
            (ParamList("a"), "a"),
            (ParamList("a", "b"), "a b"),
            (ParamList("a", "b", has_trail=True), "a :b"),
            (ParamList("a", "b", ":c"), "a b ::c"),
            (ParamList("a", "b", "c "), "a b :c "),
            (ParamList("a", "b", ""), "a b :"),
        ],
    )
    def test_str(self, obj: ParamList, text: str) -> None:
        """Test string conversion."""
        assert str(obj) == text

    @pytest.mark.parametrize(
        "params",
        [[], [""], ["a"], ["a", "b"], ["a", ":b"], ["a", "b "], ["a", ""]],
    )
    def test_eq(self, params: list[str]) -> None:
        """Test equals."""
        assert ParamList(*params) == ParamList(*params)
        assert ParamList(*params) == ParamList.from_list(params)
        assert ParamList.from_list(params) == ParamList(*params)

    @pytest.mark.parametrize(
        "params",
        [[], [""], ["a"], ["a", "b"], ["a", ":b"], ["a", "b "], ["a", ""]],
    )
    def test_ne(self, params: list[str]) -> None:
        """Test not-equals."""
        b = ParamList(*params) != ParamList(*params)
        assert not b

    @pytest.mark.parametrize(
        ("obj", "other"), [(ParamList(), 0), (ParamList(), None)]
    )
    def test_no_cmp(self, obj: ParamList, other: object) -> None:
        """Test not-equals."""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj


class TestMessage:
    """Test parsing an entire IRC message."""

    def test_parse_bytes(self) -> None:
        """Test parsing bytes."""
        line = Message.parse(b"COMMAND some params :and stuff")
        assert line.command == "COMMAND"
        assert line.parameters == ["some", "params", "and stuff"]

    def test_parse_bytearray(self) -> None:
        """Test parsing bytearray."""
        line = Message.parse(bytearray(b"COMMAND some params :and stuff"))
        assert line.command == "COMMAND"
        assert line.parameters == ["some", "params", "and stuff"]

    def test_parse_memoryview(self) -> None:
        """Test parsing memoryview."""
        line = Message.parse(memoryview(b"COMMAND some params :and stuff"))
        assert line.command == "COMMAND"
        assert line.parameters == ["some", "params", "and stuff"]

    @pytest.mark.parametrize(
        ("obj", "text"),
        [
            (Message(None, None, None), ""),  # type: ignore[arg-type]
            (Message(None, None, None, None), ""),  # type: ignore[arg-type]
            (Message(None, None, None, []), ""),  # type: ignore[arg-type]
            (Message(None, None, "COMMAND"), "COMMAND"),
            (Message(["a=b"], None, "COMMAND"), "@a=b COMMAND"),
            (Message([MessageTag("a", "b")], None, "COMMAND"), "@a=b COMMAND"),  # type: ignore[list-item]
            (Message({"a": "b"}, None, "COMMAND"), "@a=b COMMAND"),
            (Message({"a": "b"}, "nick", "COMMAND"), "@a=b :nick COMMAND"),
            (Message(None, ("nick",), "COMMAND"), ":nick COMMAND"),
            (Message(None, ("nick", "user"), "COMMAND"), ":nick!user COMMAND"),
            (
                Message(None, ("nick", "user", "host"), "COMMAND"),
                ":nick!user@host COMMAND",
            ),
            (
                Message({"a": "b"}, "nick", "COMMAND", "a", "b"),
                "@a=b :nick COMMAND a b",
            ),
        ],
    )
    def test_str(self, obj: Message, text: str) -> None:
        """Test string conversion."""
        assert str(obj) == text

    @pytest.mark.parametrize(
        ("tags", "prefix", "command", "params"),
        [(None, None, "", []), ("some tag", None, "COMMAND", ["param", ""])],
    )
    def test_eq(
        self,
        tags: str | None,
        prefix: str | None,
        command: str,
        params: list[str],
    ) -> None:
        """Test equals."""
        assert Message(tags, prefix, command, params) == Message(
            tags, prefix, command, params
        )

    @pytest.mark.parametrize(
        ("tags", "prefix", "command", "params"),
        [(None, None, "", []), ("some tag", None, "COMMAND", ["param", ""])],
    )
    def test_ne(
        self,
        tags: str | None,
        prefix: str | None,
        command: str,
        params: list[str],
    ) -> None:
        """Test not-equals."""
        b = Message(tags, prefix, command, params) != Message(
            tags, prefix, command, params
        )
        assert not b

    @pytest.mark.parametrize(
        ("obj", "other"),
        [
            (Message(None, None, ""), 0),
            (Message(None, None, ""), None),
            (Message(None, None, ""), ()),
        ],
    )
    def test_no_cmp(self, obj: Message, other: object) -> None:
        """Test Message.__ne__."""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize("obj", [Message(None, None, "COMMAND")])
    def test_bool(self, obj: Message) -> None:
        """Test the cases where bool(Message) should return True."""
        assert obj

    @pytest.mark.parametrize(
        "obj",
        [
            Message(None, None, None),  # type: ignore[arg-type]
            Message(None, None, ""),
            Message(None, "", ""),
            Message("", "", ""),
            Message([], [], "", []),
            Message({}, [], "", []),
            Message(TagList(), Prefix(), "", ParamList()),
        ],
    )
    def test_bool_false(self, obj: Message) -> None:
        """Test all the cases where bool(Message) should return False."""
        assert not obj

    @pytest.mark.parametrize(
        ("msg", "expected"),
        [
            (
                "@time=2025-09-01T00:11:22.123Z FOO #bar :baz blah",
                datetime.datetime(
                    year=2025,
                    month=9,
                    day=1,
                    hour=0,
                    minute=11,
                    second=22,
                    microsecond=123000,
                    tzinfo=datetime.timezone.utc,
                ),
            ),
            (
                "FOO #bar :baz blah",
                datetime.datetime(
                    year=2006,
                    month=1,
                    day=2,
                    hour=3,
                    minute=4,
                    second=5,
                    microsecond=123456,
                    tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
                ),
            ),
        ],
    )
    def test_parse_server_time(
        self, msg: str, expected: datetime.datetime
    ) -> None:
        """Test server time parsing."""
        default_time = datetime.datetime(
            year=2006,
            month=1,
            day=2,
            hour=3,
            minute=4,
            second=5,
            microsecond=123456,
            tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
        )

        assert Message.parse(msg, time=default_time).time == expected

    @pytest.mark.parametrize(
        ("msg", "expected"),
        [
            ("@msgid=foo FOO #bar :baz blah", "foo"),
            ("FOO #bar :baz blah", None),
        ],
    )
    def test_parse_msgid(self, msg: str, expected: str | None) -> None:
        """Ensure message IDs are retrieved."""
        assert Message.parse(msg).message_id == expected

    @pytest.mark.parametrize(
        ("msg", "expected"),
        [
            ("@batch=foo FOO #bar :baz blah", "foo"),
            ("FOO #bar :baz blah", None),
        ],
    )
    def test_parse_batch(self, msg: str, expected: str | None) -> None:
        """Ensure batch IDs are retrieved."""
        assert Message.parse(msg).batch_id == expected

    def test_naive_datetime_warning(self) -> None:
        """Ensure warning about use of naive datetimes is present."""
        with pytest.warns(DeprecationWarning, match=".*naive.*"):
            Message(
                None,
                None,
                "cmd",
                time=datetime.datetime(year=1, month=1, day=1),  # noqa: DTZ001
            )

    @pytest.mark.parametrize(
        ("msg", "tag", "present"),
        [
            ("", "", False),
            ("@foo=bar FOO", "foo", True),
            ("@foo=bar FOO", "bar", False),
            ("@foo= FOO", "foo", True),
            ("@foo= FOO", "bar", False),
        ],
    )
    def test_has_tag(self, msg: str, tag: str, present: bool) -> None:
        """Test has_tag."""
        assert Message.parse(msg).has_tag(tag) == present


def test_trail() -> None:
    """Ensure this parser does not have the same issue as https://github.com/hexchat/hexchat/issues/2271."""
    text = "COMMAND thing thing :thing"
    parsed = Message.parse(text)

    assert parsed.command == "COMMAND"

    for i in range(3):
        assert parsed.parameters[i] == "thing"


@pytest.mark.parametrize(
    ("parse_type", "text"),
    [
        (MessageTag, "hi"),
        (MessageTag, "hello=world"),
        (MessageTag, "he\\:llo=\\swor\\r\\\\ld"),
        (TagList, "hi"),
        (TagList, "hello; there"),
        (TagList, "hello; there;"),
        (TagList, "hello=world; there"),
        (Prefix, "nick"),
        (Prefix, "nick!user"),
        (Prefix, "nick@host"),
        (Prefix, "nick!user@host"),
        (ParamList, "test test"),
        (ParamList, "test :test"),
        (ParamList, "test :test test"),
        (Message, "COMMAND"),
        (Message, "command"),
    ],
)
def test_comparisons(parse_type: type[Parseable], text: str) -> None:
    """Test comparing parsed objects to strings."""
    assert text == parse_type.parse(text)  # type: ignore[comparison-overlap]
    assert not text != parse_type.parse(text)  # type: ignore[comparison-overlap]


@pytest.mark.parametrize("data", parser_tests.data.msg_split["tests"])
def test_msg_split(data: MsgSplitCase) -> None:
    """Test splitting a message against the irc-parser-tests data."""
    msg = Message.parse(data["input"])
    atoms = data["atoms"].copy()

    # We store tags a bit differently than the test data expects, convert the format
    if msg.tags is not None:
        tags_dict = {name: tag.value for name, tag in msg.tags.items()}
    else:
        tags_dict = None

    assert tags_dict == atoms.get("tags", None)

    prefix = None if msg.prefix is None else str(msg.prefix)
    assert prefix == atoms.get("source", None)

    # Commands are case-insensitive
    assert String(msg.command, ASCII) == atoms.get("verb", None)

    assert list(msg.parameters) == atoms.get("params", [])


@pytest.mark.parametrize("data", parser_tests.data.userhost_split["tests"])
def test_userhost_split(data: UserHostSplitCase) -> None:
    """Ensure that user/host parsing passes against the irc-parser-tests data."""
    source = Prefix.parse(data["source"])
    atoms = data["atoms"].copy()

    assert source.nick == atoms.get("nick", "")
    assert source.user == atoms.get("user", "")
    assert source.host == atoms.get("host", "")


def test_message_tag_repr() -> None:
    """Test repr(MessageTag)."""
    m = MessageTag("foo", "bar")
    assert repr(m) == "MessageTag(name='foo', value='bar')"


@pytest.mark.parametrize("data", parser_tests.data.msg_join["tests"])
def test_msg_join(data: MsgJoinCase) -> None:
    """Ensure that message building passes all tests from the irc-parser-tests library."""
    atoms = data["atoms"]
    msg = Message(
        atoms.get("tags", None),
        atoms.get("source", None),
        atoms.get("verb", None),
        atoms.get("params", []),
    )

    matches = data["matches"]
    assert str(msg) in matches


@pytest.mark.parametrize(
    ("text", "has_trail"),
    [
        ("PRIVMSG #channel :message", True),
        ("PRIVMSG #channel :message text", True),
    ],
)
def test_has_trail(text: str, has_trail: bool) -> None:
    """Ensure that a message with trailing arguments is recorded as having a tril."""
    msg = Message.parse(text)
    assert msg.parameters.has_trail == has_trail
