"""Test IRC parser"""
import parser_tests.data
import pytest

from irclib.parser import (
    Cap,
    CapList,
    Message,
    MessageTag,
    ParamList,
    Prefix,
    TagList,
)
from irclib.util.string import ASCII, String


def test_line():
    """Test parsing a single IRC message"""
    assert Message.parse("COMMAND") == "COMMAND"
    assert Message.parse("command") == "COMMAND"

    msg1 = Message.parse("PRIVMSG")

    assert msg1.command == "PRIVMSG"

    msg2 = Message.parse(
        r"@test=data;test1=more\sdata :nick!user@host COMMAND arg1 arg2 :trailing text"
    )

    assert msg2.prefix.host == "host"


class TestCap:
    """Test Cap class"""

    @pytest.mark.parametrize(
        "name,value,expected",
        [
            ("capname", "somevalue", "capname=somevalue"),
            ("capname", None, "capname"),
        ],
    )
    def test_str(self, name, value, expected):
        """Test string conversion"""
        c = Cap(name, value)
        assert str(c) == expected

    @pytest.mark.parametrize(
        "name,value",
        [
            ("a", "b"),
            ("foo", "bar"),
        ],
    )
    def test_eq(self, name, value):
        """Test equals"""
        assert Cap(name, value) == Cap(name, value)

    @pytest.mark.parametrize(
        "name,value,string",
        [
            ("a", "b", "a=b"),
            ("foo", "bar", "foo=bar"),
        ],
    )
    def test_eq_str(self, name, value, string):
        """Test equals string"""
        assert Cap(name, value) == string
        assert string == Cap(name, value)

    @pytest.mark.parametrize(
        "name,value,other_name,other_value",
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
    def test_ne(self, name, value, other_name, other_value):
        """Test not-equals"""
        assert Cap(name, value) != Cap(other_name, other_value)
        assert Cap(other_name, other_value) != Cap(name, value)

    @pytest.mark.parametrize(
        "name,value,string",
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
    def test_ne_str(self, name, value, string):
        """Test not-equals string"""
        assert Cap(name, value) != string
        assert string != Cap(name, value)

    @pytest.mark.parametrize(
        "obj,other",
        [
            (Cap("foo"), 1),
        ],
    )
    def test_no_cmp(self, obj, other):
        """Test not-equals"""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize(
        "text,name,value",
        [
            (
                "vendor.example.org/cap-name",
                "vendor.example.org/cap-name",
                None,
            ),
        ],
    )
    def test_parse(self, text, name, value):
        """Test parsing string"""
        cap = Cap.parse(text)
        assert cap.name == name
        assert cap.value == value


class TestCapList:
    """Test parsing a list of CAPs"""

    @pytest.mark.parametrize(
        "text,expected",
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
            (
                "",
                (),
            ),
        ],
    )
    def test_parse(self, text, expected):
        """Test string parsing"""
        parsed = CapList.parse(text)
        assert len(parsed) == len(expected)
        for (name, value), actual in zip(expected, parsed):
            assert actual.name == name
            assert actual.value == value

    @pytest.mark.parametrize("caps", [[], [Cap("a"), Cap("b", "c")]])
    def test_eq_list(self, caps):
        """Test equals list"""
        assert CapList(caps) == caps
        assert caps == CapList(caps)

    @pytest.mark.parametrize(
        "caps",
        [
            [],
            [Cap("a"), Cap("b", "c")],
        ],
    )
    def test_ne_list(self, caps):
        """Test not-equals list"""
        b = CapList(caps) != caps
        assert not b
        b1 = caps != CapList(caps)
        assert not b1

    @pytest.mark.parametrize(
        "caps,text",
        [
            ([], ""),
            ([Cap("a"), Cap("b", "c")], "a b=c"),
            ([Cap("a"), Cap("b", "c")], "a b=c "),
        ],
    )
    def test_eq_str(self, caps, text):
        """Test equals strings"""
        assert CapList(caps) == text
        assert text == CapList(caps)

    @pytest.mark.parametrize(
        "caps,text",
        [
            ([], ""),
            ([Cap("a"), Cap("b", "c")], "a b=c"),
            ([Cap("a"), Cap("b", "c")], "a b=c "),
        ],
    )
    def test_ne_str(self, caps, text):
        """Test not-equals strings"""
        b = CapList(caps) != text
        assert not b
        b1 = text != CapList(caps)
        assert not b1

    @pytest.mark.parametrize(
        "obj,other",
        [
            (CapList(), None),
            (CapList(), 0),
        ],
    )
    def test_no_cmp(self, obj, other):
        """Test not-equals"""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize(
        "obj,text",
        [
            (CapList([Cap("foo")]), "foo"),
            (CapList([Cap("foo"), Cap("bar")]), "foo bar"),
            (CapList([Cap("foo"), Cap("bar=baz")]), "foo bar=baz"),
        ],
    )
    def test_str(self, obj, text):
        """Test string conversion"""
        assert str(obj) == text
        assert text == str(obj)


class TestMessageTag:
    """Test parsing a single message tag"""

    @pytest.mark.parametrize(
        "text,name,value",
        [
            ("a=b", "a", "b"),
            ("test/blah=", "test/blah", ""),
            (r"blah=aa\r\n\:\\", "blah", "aa\r\n;\\"),
            (r"blah=aa\r\n\s\:\\", "blah", "aa\r\n ;\\"),
            (r"blah=\s", "blah", " "),
            ("blah=\\", "blah", ""),
        ],
    )
    def test_parse(self, text, name, value):
        """Test parsing a string"""
        tag = MessageTag.parse(text)
        assert tag.name == name
        assert tag.value == value

    @pytest.mark.parametrize(
        "name,value",
        [
            ("a", None),
            ("a", "b"),
        ],
    )
    def test_eq(self, name, value):
        """Test equals"""
        assert MessageTag(name, value) == MessageTag(name, value)

    @pytest.mark.parametrize(
        "name,value",
        [
            ("a", None),
            ("a", "b"),
        ],
    )
    def test_ne(self, name, value):
        """Test not-equals"""
        b = MessageTag(name, value) != MessageTag(name, value)
        assert not b

    @pytest.mark.parametrize(
        "name,value,text",
        [
            ("foo", None, "foo"),
            ("foo", "bar", "foo=bar"),
        ],
    )
    def test_eq_str(self, name, value, text):
        """Test equals string"""
        assert MessageTag(name, value) == text
        assert text == MessageTag(name, value)

    @pytest.mark.parametrize(
        "name,value,text",
        [
            ("foo", None, "foo"),
            ("foo", "bar", "foo=bar"),
        ],
    )
    def test_ne_str(self, name, value, text):
        """Test not-equals string"""
        b = MessageTag(name, value) != text
        assert not b
        b1 = text != MessageTag(name, value)
        assert not b1

    @pytest.mark.parametrize(
        "obj,other",
        [
            (MessageTag(""), None),
            (MessageTag(""), 1),
        ],
    )
    def test_no_cmp(self, obj, other):
        """Test not-equals other types"""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj


class TestTagList:
    """Test parsing a tag list"""

    @pytest.mark.parametrize(
        "text,tags",
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
    def test_parse(self, text, tags):
        """Test parsing from string"""
        tag_list = TagList.parse(text)

        assert len(tag_list) == len(tags)

        for name, value in tags:
            tag = tag_list[name]
            assert tag.name == name
            assert tag.value == value

    @pytest.mark.parametrize(
        "tags",
        [
            [],
            [MessageTag("a")],
            [MessageTag("b", "c")],
        ],
    )
    def test_eq(self, tags):
        """Test equals"""
        assert TagList(tags) == TagList(tags)

    @pytest.mark.parametrize(
        "tags",
        [
            [],
            [MessageTag("a")],
            [MessageTag("b", "c")],
        ],
    )
    def test_ne(self, tags):
        """Test not-equals"""
        b = TagList(tags) != TagList(tags)
        assert not b

    @pytest.mark.parametrize(
        "tags",
        [
            [],
            [MessageTag("a")],
            [MessageTag("b", "c")],
        ],
    )
    def test_eq_list(self, tags):
        """Test equals list"""
        assert TagList(tags) == tags
        assert tags == TagList(tags)

    @pytest.mark.parametrize(
        "tags",
        [
            [],
            [MessageTag("a")],
            [MessageTag("b", "c")],
        ],
    )
    def test_ne_list(self, tags):
        """Test not-equals list"""
        b = TagList(tags) != tags
        assert not b
        b1 = tags != TagList(tags)
        assert not b1

    @pytest.mark.parametrize(
        "obj,other",
        [
            (TagList(), {}),
            (TagList([MessageTag("a")]), {"a": None}),
            (TagList([MessageTag("b", "c")]), {"b": "c"}),
        ],
    )
    def test_eq_dict(self, obj, other):
        """Test equals dict"""
        assert obj == other
        assert other == obj

    @pytest.mark.parametrize(
        "obj,other",
        [
            (TagList(), {}),
            (TagList([MessageTag("a")]), {"a": None}),
            (TagList([MessageTag("b", "c")]), {"b": "c"}),
        ],
    )
    def test_ne_dict(self, obj, other):
        """Test not-equals dict"""
        b = obj != other
        assert not b
        b1 = other != obj
        assert not b1

    @pytest.mark.parametrize(
        "tags,text",
        [
            ([], ""),
            ([MessageTag("a")], "a"),
            ([MessageTag("b", "c")], "b=c"),
        ],
    )
    def test_eq_str(self, tags, text):
        """Test equals strings"""
        assert TagList(tags) == text
        assert text == TagList(tags)

    @pytest.mark.parametrize(
        "tags,text",
        [
            ([], ""),
            ([MessageTag("a")], "a"),
            ([MessageTag("b", "c")], "b=c"),
        ],
    )
    def test_ne_str(self, tags, text):
        """Test not-equals strings"""
        b = TagList(tags) != text
        assert not b
        b1 = text != TagList(tags)
        assert not b1

    @pytest.mark.parametrize(
        "obj,other",
        [
            (TagList(), 0),
            (TagList(), None),
        ],
    )
    def test_no_cmp(self, obj, other):
        """Test not-equals other types"""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj


class TestPrefix:
    """Test parsing a prefix"""

    @pytest.mark.parametrize(
        "text,nick,user,host",
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
    def test_parse(self, text, nick, user, host):
        """Test parsing a string"""
        p = Prefix.parse(text)

        assert p.nick == nick
        assert p.user == user
        assert p.ident == user
        assert p.host == host

    @pytest.mark.parametrize(
        "nick,user,host",
        [
            ("nick", None, None),
            ("nick", "user", "host"),
            ("nick", None, "host"),
            ("nick", "user", None),
        ],
    )
    def test_eq(self, nick, user, host):
        """Test equals"""
        assert Prefix(nick, user, host) == Prefix(nick, user, host)

    @pytest.mark.parametrize(
        "nick,user,host",
        [
            ("nick", None, None),
            ("nick", "user", "host"),
            ("nick", None, "host"),
            ("nick", "user", None),
        ],
    )
    def test_ne(self, nick, user, host):
        """Test not-equals"""
        b = Prefix(nick, user, host) != Prefix(nick, user, host)
        assert not b

    @pytest.mark.parametrize(
        "text,nick,user,host",
        [
            ("nick", "nick", None, None),
            ("nick!user@host", "nick", "user", "host"),
            ("nick@host", "nick", None, "host"),
            ("nick!user", "nick", "user", None),
        ],
    )
    def test_eq_str(self, text, nick, user, host):
        """Test equals string"""
        assert Prefix(nick, user, host) == text
        assert text == Prefix(nick, user, host)

    @pytest.mark.parametrize(
        "text,nick,user,host",
        [
            ("nick", "nick", None, None),
            ("nick!user@host", "nick", "user", "host"),
            ("nick@host", "nick", None, "host"),
            ("nick!user", "nick", "user", None),
        ],
    )
    def test_ne_str(self, text, nick, user, host):
        """Test not-equals string comparisons"""
        b = Prefix(nick, user, host) != text
        assert not b
        b1 = text != Prefix(nick, user, host)
        assert not b1

    @pytest.mark.parametrize(
        "obj,other",
        [
            (Prefix(""), 0),
            (Prefix(""), None),
            (Prefix(""), ()),
        ],
    )
    def test_no_cmp(self, obj, other):
        """Test not-equals"""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize(
        "obj,nick,user,host",
        [
            (Prefix("nick"), "nick", "", ""),
            (Prefix("nick", "user", "host"), "nick", "user", "host"),
            (Prefix("nick", host="host"), "nick", "", "host"),
            (Prefix("nick", "user"), "nick", "user", ""),
        ],
    )
    def test_unpack(self, obj, nick, user, host):
        """Test unpacking Prefix"""
        n, u, h = obj
        assert (n, u, h) == (nick, user, host)

    @pytest.mark.parametrize(
        "nick,user,host",
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
    def test_bool(self, nick, user, host):
        """Test cases where bool(Prefix) == True"""
        assert Prefix(nick, user, host)

    @pytest.mark.parametrize(
        "nick,user,host",
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
    def test_bool_false(self, nick, user, host):
        """Test cases where bool(Prefix) == False"""
        assert not Prefix(nick, user, host)


class TestParamList:
    """Test parsing a parameter list"""

    @pytest.mark.parametrize(
        "obj,text",
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
    def test_str(self, obj, text):
        """Test string conversion"""
        assert str(obj) == text

    @pytest.mark.parametrize(
        "params",
        [
            [],
            [""],
            ["a"],
            ["a", "b"],
            ["a", ":b"],
            ["a", "b "],
            ["a", ""],
        ],
    )
    def test_eq(self, params):
        """Test equals"""
        assert ParamList(*params) == ParamList(*params)
        assert ParamList(*params) == ParamList.from_list(params)
        assert ParamList.from_list(params) == ParamList(*params)

    @pytest.mark.parametrize(
        "params",
        [
            [],
            [""],
            ["a"],
            ["a", "b"],
            ["a", ":b"],
            ["a", "b "],
            ["a", ""],
        ],
    )
    def test_ne(self, params):
        """Test not-equals"""
        b = ParamList(*params) != ParamList(*params)
        assert not b

    @pytest.mark.parametrize(
        "obj,other",
        [
            (ParamList(), 0),
            (ParamList(), None),
        ],
    )
    def test_no_cmp(self, obj, other):
        """Test not-equals"""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj


class TestMessage:
    """Test parsing an entire IRC message"""

    def test_parse_bytes(self):
        """Test parsing bytes"""
        line = Message.parse(b"COMMAND some params :and stuff")
        assert line.command == "COMMAND"
        assert line.parameters == ["some", "params", "and stuff"]

    @pytest.mark.parametrize(
        "obj,text",
        [
            (Message(None, None, None), ""),
            (Message(None, None, None, None), ""),
            (Message(None, None, None, []), ""),
            (Message(None, None, "COMMAND"), "COMMAND"),
            (Message(["a=b"], None, "COMMAND"), "@a=b COMMAND"),
            (Message([MessageTag("a", "b")], None, "COMMAND"), "@a=b COMMAND"),
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
    def test_str(self, obj, text):
        """Test string conversion"""
        assert str(obj) == text

    @pytest.mark.parametrize(
        "tags,prefix,command,params",
        [
            (None, None, None, None),
            ("some tag", None, "COMMAND", ["param", ""]),
        ],
    )
    def test_eq(self, tags, prefix, command, params):
        """Test equals"""
        assert Message(tags, prefix, command, params) == Message(
            tags, prefix, command, params
        )

    @pytest.mark.parametrize(
        "tags,prefix,command,params",
        [
            (None, None, None, None),
            ("some tag", None, "COMMAND", ["param", ""]),
        ],
    )
    def test_ne(self, tags, prefix, command, params):
        """Test not-equals"""
        b = Message(tags, prefix, command, params) != Message(
            tags, prefix, command, params
        )
        assert not b

    @pytest.mark.parametrize(
        "obj,other",
        [
            (Message(None, None, None), 0),
            (Message(None, None, None), None),
            (Message(None, None, None), ()),
        ],
    )
    def test_no_cmp(self, obj, other):
        """Test Message.__ne__"""
        assert obj != other
        assert other != obj

        assert not obj == other
        assert not other == obj

    @pytest.mark.parametrize(
        "obj",
        [
            Message(None, None, "COMMAND"),
        ],
    )
    def test_bool(self, obj):
        """Test the cases where bool(Message) should return True"""
        assert obj

    @pytest.mark.parametrize(
        "obj",
        [
            Message(None, None, None),
            Message(None, None, ""),
            Message(None, "", ""),
            Message("", "", ""),
            Message([], [], "", []),
            Message({}, [], "", []),
            Message(TagList(), Prefix(), "", ParamList()),
        ],
    )
    def test_bool_false(self, obj):
        """Test all the cases where bool(Message) should return False"""
        assert not obj


def test_trail():
    """
    Ensure this parser does not have the same
    issue as https://github.com/hexchat/hexchat/issues/2271
    """
    text = "COMMAND thing thing :thing"
    parsed = Message.parse(text)

    assert parsed.command == "COMMAND"

    for i in range(3):
        assert parsed.parameters[i] == "thing"


@pytest.mark.parametrize(
    "parse_type,text",
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
def test_comparisons(parse_type, text):
    """Test comparing parsed objects to strings"""
    assert text == parse_type.parse(text)
    assert not text != parse_type.parse(text)


@pytest.mark.parametrize("data", parser_tests.data.msg_split["tests"])
def test_msg_split(data):
    """Test splitting a message against the irc-parser-tests data"""
    msg = Message.parse(data["input"])
    atoms = data["atoms"].copy()

    # We store tags a bit differently than the test data expects, convert the format
    if msg.tags is not None:
        tags_dict = {name: tag.value for name, tag in msg.tags.items()}
    else:
        tags_dict = None

    assert tags_dict == atoms.pop("tags", None)

    prefix = None if msg.prefix is None else str(msg.prefix)
    assert prefix == atoms.pop("source", None)

    # Commands are case-insensitive
    assert String(msg.command, ASCII) == atoms.pop("verb", None)

    assert list(msg.parameters) == atoms.pop("params", [])

    # Make sure we handled everything
    assert not atoms


@pytest.mark.parametrize("data", parser_tests.data.userhost_split["tests"])
def test_userhost_split(data):
    """Ensure that yser/host parsing passes against the irc-parser-tests data"""
    source = Prefix.parse(data["source"])
    atoms = data["atoms"].copy()

    assert source.nick == atoms.pop("nick", "")
    assert source.user == atoms.pop("user", "")
    assert source.host == atoms.pop("host", "")

    assert not atoms


@pytest.mark.parametrize("data", parser_tests.data.msg_join["tests"])
def test_msg_join(data):
    """
    Ensure that message building passes all tests from
    the irc-parser-tests library.
    """
    atoms = data["atoms"]
    msg = Message(
        atoms.pop("tags", None),
        atoms.pop("source", None),
        atoms.pop("verb", None),
        atoms.pop("params", []),
    )

    assert not atoms, "Not all atoms were handled"

    matches = data["matches"]
    assert str(msg) in matches


@pytest.mark.parametrize(
    "text,has_trail",
    (
        ("PRIVMSG #channel :message", True),
        ("PRIVMSG #channel :message text", True),
    ),
)
def test_has_trail(text, has_trail):
    """Ensure that a message with trailing arguments is recorded as having a tril"""
    msg = Message.parse(text)
    assert msg.parameters.has_trail == has_trail
