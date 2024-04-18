"""Test frozendict util."""

from irclib.util.frozendict import FrozenDict


def test_dict() -> None:
    """Test basic dict functions."""
    fd = FrozenDict(a=1, b=2)
    assert fd["a"] == 1
    assert fd["b"] == 2

    assert len(fd) == 2
    assert set(fd.keys()) == {"a", "b"}


def test_init_literal() -> None:
    """Test initializing with a dict literal."""
    fd = FrozenDict({"a": 1, "b": 2})
    assert fd["a"] == 1
    assert fd["b"] == 2

    assert len(fd) == 2
    assert set(fd.keys()) == {"a", "b"}


def test_copy() -> None:
    """Test dict copy."""
    fd = FrozenDict([("a", 1), ("b", 2)])
    fd1 = fd.copy()
    assert len(fd1) == 2
    assert fd1["a"] == 1
    assert fd1["b"] == 2

    fd2 = fd.copy(c=3)
    assert fd2["a"] == 1
    assert fd2["b"] == 2
    assert fd2["c"] == 3
    assert len(fd2) == 3

    fd3 = fd.copy(a=3)
    assert fd3["a"] == 3
    assert fd3["b"] == 2


def test_hash() -> None:
    """Test dict hashes."""
    fd = FrozenDict(a=1, b=2)
    fd1 = FrozenDict({"a": 1, "b": 2})
    assert fd == fd1
    assert hash(fd) == hash(fd1)
    h = hash(fd)
    h1 = hash(fd)
    assert h == h1
