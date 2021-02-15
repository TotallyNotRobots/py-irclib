"""Test numerics util"""
from irclib.util import numerics


def test_lookup():
    """Test looking up a numeric"""
    n = numerics.numerics["001"]
    assert n is numerics.numerics.from_int(1)
    assert n is numerics.numerics.from_name("RPL_WELCOME")


def test_iter():
    """Test iterating the numerics list"""
    assert list(numerics.numerics)[0] == "001"


def test_len():
    """Test checking the length of the numerics list"""
    assert len(numerics.numerics) > 0
