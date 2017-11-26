from irclib.parser import Message, CapList


def test_line():
    assert Message.parse("COMMAND") == "COMMAND"
    assert Message.parse("command") == "COMMAND"

    msg1 = Message.parse("PRIVMSG")

    msg2 = Message.parse("@test=data;test1=more\sdata :nick!user@host COMMAND arg1 arg2 :trailing text")

    assert msg2.prefix.host == "host"


def test_cap():
    caps = CapList.parse("test test-1=blah")
