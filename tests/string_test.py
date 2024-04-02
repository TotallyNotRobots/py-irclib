"""Test IRC string class"""

import pytest

from irclib.util.string import ASCII, RFC1459, String


def test_comparisons():
    """Test comparison logic"""
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

    assert str2 != "B"


def test_getitem():
    """Test `getitem`"""
    s = String("abc")
    assert s[0] == "a"
    assert isinstance(s[0], String)
    assert s[0].casemap is s.casemap


def test_capitalize():
    """Test `capitalize`"""
    s = String("abC")
    assert s.capitalize() == "Abc"


def test_swapcase():
    """Test `swapcase`"""
    s = String("abC")
    assert s.swapcase() == "ABc"


def test_startswith():
    """Test `startswith`"""
    s = String("aBc")
    assert s.startswith("a")
    assert s.startswith("ab")
    assert s.startswith(String("aB"))
    assert s.startswith(("a", "b"))


def test_endswith():
    """Test `endswith`"""
    s = String("aBc")
    assert s.endswith("c")
    assert s.endswith("bC")
    assert s.endswith(String("bc"))
    assert s.endswith(("b", "c"))


def test_find():
    """Test `find`"""
    s = String("AbCB")
    assert s.find("B") == 1
    assert s.find(String("B")) == 1
    assert s.find("d") == -1


def test_rfind():
    """Test `rfind`"""
    s = String("AbCB")
    assert s.rfind("B") == 3
    assert s.rfind(String("B")) == 3
    assert s.rfind("d") == -1


def test_index():
    """Test `index`"""
    s = String("AbCB")
    assert s.index("B") == 1
    assert s.index(String("B")) == 1
    with pytest.raises(ValueError):
        s.index("d")


def test_rindex():
    """Test `rindex`"""
    s = String("AbCB")
    assert s.rindex("B") == 3
    assert s.rindex(String("B")) == 3
    with pytest.raises(ValueError):
        s.rindex("d")


def test_count():
    """Test `count`"""
    assert String("aabbcc").count("a") == 2
    assert String("aabbcc").count(String("a")) == 2


def test_hash():
    """Test hashing a string"""
    assert hash(String("ABC")) == hash(String("abc"))


def test_contains():
    """Test `in` operator"""
    assert "a" in String("abc")
    assert String("a") in String("abc")


def test_instance():
    """Ensure that basic strings aren't being counted as String"""
    assert not isinstance("a", String)


def test_rfc1459():
    """Test rfc1459 casemap"""
    str1 = String("ABC|{", RFC1459)
    str2 = String("abc\\[", RFC1459)

    assert str1 == str2
    assert str(str1.lower()) == str(str2.lower())
    assert str(str1.upper()) == str(str2.upper())


def test_partition():
    """Test partition"""
    s = String("ABc")
    assert s.partition("b") == ("A", "B", "c")
    assert s.partition("d") == ("ABc", "", "")


def test_rpartition():
    """Test rpartition"""
    s = String("AbCbAcBa")
    assert s.rpartition("b") == ("AbCbAc", "B", "a")
    assert s.rpartition("d") == ("", "", "AbCbAcBa")


def test_strip():
    """Test stripping characters"""
    s = String("AbCbAcBa")
    assert s.strip("d") == "AbCbAcBa"
    assert s.strip("a") == "bCbAcB"
    s1 = String(" ABc  ")
    assert s1.strip() == "ABc"
