from irclib.string import String, ASCII, RFC1459


def test_comparisons():
    str1 = String("A", ASCII)
    str2 = String("a", ASCII)

    assert str1.casemap is ASCII
    assert str2.casemap is ASCII

    assert str1 == "A"
    assert str2 == "a"

    assert str1.lower() == "a"
    assert str2.lower() == "a"

    assert str1.upper() == "A"
    assert str2.upper() == "A"

    assert str1 == str1
    assert str1 == str2

    assert str1 == "a"
    assert "a" == str1

    assert str2 == "a"
    assert "a" == str2

    assert str1 == "A"
    assert "A" == str1

    assert str2 == "A"
    assert "A" == str2

    assert not str1 > str2
    assert not str1 > "a"

    assert "B" > str2
    assert str2 < "B"


def test_rfc1459():
    str1 = String("ABC|{", RFC1459)
    str2 = String("abc\\[", RFC1459)

    assert str1 == str2
    assert str1.lower() == str2.lower()
    assert str1.upper() == str2.upper()
