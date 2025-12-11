# SPDX-FileCopyrightText: 2017-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test IRC string class."""

import pytest

from irclib.util.string import ASCII, RFC1459, String


def test_comparisons() -> None:
    """Test comparison logic."""
    # pylint: disable=misplaced-comparison-constant, unneeded-not
    str1 = String("A", ASCII)
    str1_ = str1
    str2 = String("a", ASCII)

    assert str1.casemap is ASCII
    assert str2.casemap is ASCII

    assert str1 == "A"
    assert str2 == "a"

    assert str(str1.lower()) == "a"
    assert str(str2.lower()) == "a"

    assert str(str1.upper()) == "A"
    assert str(str2.upper()) == "A"

    assert str1 == str1_
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
    assert not str2 > "B"
    assert str2 < "B"
    assert not "B" < str2
    assert not str2 >= "B"
    assert str2 <= "B"
    assert "B" >= str2
    assert not "B" <= str2

    with pytest.raises(TypeError):
        assert not str2 < 1  # type: ignore[operator]

    with pytest.raises(TypeError):
        assert not str2 <= 1  # type: ignore[operator]

    with pytest.raises(TypeError):
        assert not str2 > 1  # type: ignore[operator]

    with pytest.raises(TypeError):
        assert not str2 >= 1  # type: ignore[operator]

    assert not str2 == 1
    assert str2 != 1

    assert str2 != "B"

    assert str1 != 5


def test_getitem() -> None:
    """Test `getitem`."""
    s = String("abc")
    assert s[0] == "a"
    assert isinstance(s[0], String)
    assert s[0].casemap is s.casemap


def test_capitalize() -> None:
    """Test `capitalize`."""
    s = String("abC")
    assert s.capitalize() == "Abc"


def test_swapcase() -> None:
    """Test `swapcase`."""
    s = String("abC")
    assert s.swapcase() == "ABc"


def test_startswith() -> None:
    """Test `startswith`."""
    s = String("aBc")
    assert s.startswith("a")
    assert s.startswith("ab")
    assert s.startswith(String("aB"))
    assert s.startswith(("a", "b"))


def test_endswith() -> None:
    """Test `endswith`."""
    s = String("aBc")
    assert s.endswith("c")
    assert s.endswith("bC")
    assert s.endswith(String("bc"))
    assert s.endswith(("b", "c"))


def test_find() -> None:
    """Test `find`."""
    s = String("AbCB")
    assert s.find("B") == 1
    assert s.find(String("B")) == 1
    assert s.find("d") == -1


def test_rfind() -> None:
    """Test `rfind`."""
    s = String("AbCB")
    assert s.rfind("B") == 3
    assert s.rfind(String("B")) == 3
    assert s.rfind("d") == -1


def test_index() -> None:
    """Test `index`."""
    s = String("AbCB")
    assert s.index("B") == 1
    assert s.index(String("B")) == 1
    with pytest.raises(ValueError, match="substring not found"):
        s.index("d")


def test_rindex() -> None:
    """Test `rindex`."""
    s = String("AbCB")
    assert s.rindex("B") == 3
    assert s.rindex(String("B")) == 3
    with pytest.raises(ValueError, match="substring not found"):
        s.rindex("d")


def test_count() -> None:
    """Test `count`."""
    assert String("aabbcc").count("a") == 2
    assert String("aabbcc").count(String("a")) == 2


def test_hash() -> None:
    """Test hashing a string."""
    assert hash(String("ABC")) == hash(String("abc"))


def test_contains() -> None:
    """Test `in` operator."""
    assert "a" in String("abc")
    assert String("a") in String("abc")
    assert 445 not in String("abc")  # type: ignore[comparison-overlap]


def test_instance() -> None:
    """Ensure that basic strings aren't being counted as String."""
    assert not isinstance("a", String)


def test_rfc1459() -> None:
    """Test rfc1459 casemap."""
    str1 = String("ABC|{", RFC1459)
    str2 = String("abc\\[", RFC1459)

    assert str1 == str2
    assert str(str1.lower()) == str(str2.lower())
    assert str(str1.upper()) == str(str2.upper())


def test_partition() -> None:
    """Test partition."""
    s = String("ABc")
    assert s.partition("b") == ("A", "B", "c")
    assert s.partition("d") == ("ABc", "", "")


def test_rpartition() -> None:
    """Test rpartition."""
    s = String("AbCbAcBa")
    assert s.rpartition("b") == ("AbCbAc", "B", "a")
    assert s.rpartition("d") == ("", "", "AbCbAcBa")


def test_strip() -> None:
    """Test stripping characters."""
    s = String("AbCbAcBa")
    assert s.strip("d") == "AbCbAcBa"
    assert s.strip("a") == "bCbAcB"
    s1 = String(" ABc  ")
    assert s1.strip() == "ABc"
