import pytest
from pytest import raises

from irclib.errors import ParseError
from irclib.parser import Message, CapList, Cap, MessageTag, TagList, Prefix, ParamList


def test_line():
    assert Message.parse("COMMAND") == "COMMAND"
    assert Message.parse("command") == "COMMAND"

    msg1 = Message.parse("PRIVMSG")

    assert msg1.command == "PRIVMSG"

    msg2 = Message.parse("@test=data;test1=more\sdata :nick!user@host COMMAND arg1 arg2 :trailing text")

    assert msg2.prefix.host == "host"


class TestCaps:
    def test_cap_list(self):
        cases = (
            (
                "blah blah-blah cap-1 test-cap=value-data",
                (("blah", None), ("blah-blah", None), ("cap-1", None), ("test-cap", "value-data"))
            ),
            (
                "blah blah-blah cap-1 test-cap=value-data ",
                (("blah", None), ("blah-blah", None), ("cap-1", None), ("test-cap", "value-data"))
            ),
            (
                ":blah blah-blah cap-1 test-cap=value-data",
                (("blah", None), ("blah-blah", None), ("cap-1", None), ("test-cap", "value-data"))
            ),
            (
                ":blah blah-blah cap-1 test-cap=value-data ",
                (("blah", None), ("blah-blah", None), ("cap-1", None), ("test-cap", "value-data"))
            ),
        )

        for text, expected in cases:
            parsed = CapList.parse(text)
            assert len(parsed) == len(expected)
            for (name, value), actual in zip(expected, parsed):
                assert actual.name == name
                assert actual.value == value

    def test_caps(self):
        cases = (
            ("vendor.example.org/cap-name", "vendor.example.org/cap-name", None),
        )

        for text, name, value in cases:
            cap = Cap.parse(text)
            assert cap.name == name
            assert cap.value == value


def test_message_tags():
    cases = (
        ("a=b", "a", "b"),
        ("test/blah=", "test/blah", None),
        ("blah=aa\\r\\n\\:\\\\", "blah", "aa\r\n;\\"),
    )
    for text, name, value in cases:
        tag = MessageTag.parse(text)
        assert tag.name == name
        assert tag.value == value

    with raises(ParseError):
        MessageTag.parse("key=value\\")


def test_trail():
    """Ensure this parser does not have the same issue as https://github.com/hexchat/hexchat/issues/2271"""
    text = "COMMAND thing thing :thing"
    parsed = Message.parse(text)

    assert "COMMAND" == parsed.command

    for i in range(3):
        assert "thing" == parsed.parameters[i]


@pytest.mark.parametrize('parse_type,text', [
    (MessageTag, 'hi'),
    (MessageTag, 'hello=world'),
    (MessageTag, 'he\\:llo=\\swor\\r\\\\ld'),

    (TagList, 'hi'),
    (TagList, 'hello; there'),
    (TagList, 'hello; there;'),
    (TagList, 'hello=world; there'),

    (Prefix, 'nick'),
    (Prefix, 'nick!user'),
    (Prefix, 'nick@host'),
    (Prefix, 'nick!user@host'),

    (ParamList, 'test test'),
    (ParamList, 'test :test'),
    (ParamList, 'test :test test'),

    (Message, 'COMMAND'),
    (Message, 'command'),
])
def test_comparisons(parse_type, text):
    assert text == parse_type.parse(text)
    assert not text != parse_type.parse(text)
