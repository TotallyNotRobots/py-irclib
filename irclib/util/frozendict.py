"""Frozen Dict."""

from collections.abc import Iterable, Iterator, Mapping
from typing import Dict, Optional, Tuple, TypeVar, Union

from typing_extensions import Self

__all__ = ("FrozenDict",)

_V = TypeVar("_V")


class FrozenDict(Mapping[str, _V]):
    """Frozen Mapping.

    An immutable mapping of string -> Any type
    """

    __slots__ = ("__hash", "__data")

    def __init__(
        self,
        seq: Union[Mapping[str, _V], Iterable[tuple[str, _V]], None] = None,
        **kwargs: _V,
    ) -> None:
        """Construct a FrozenDict."""
        d = dict(seq, **kwargs) if seq is not None else dict(**kwargs)

        self.__data: dict[str, _V] = d
        self.__hash: Optional[int] = None

    def copy(self, **kwargs: _V) -> Self:
        """Copy dict, replacing values according to kwargs.

        >>> fd = FrozenDict(a=1)
        >>> fd["a"]
        1
        >>> fd1 = fd.copy(a=2)
        >>> fd1["a"]
        2
        >>> fd["a"]
        1
        """
        return self.__class__(self.__data, **kwargs)

    def __getitem__(self, k: str) -> _V:
        """Retrieve an item from the dict by key."""
        return self.__data[k]

    def __iter__(self) -> Iterator[str]:
        """Iterate the keys of the dict."""
        return iter(self.__data)

    def __len__(self) -> int:
        """Number of keys in the dict."""
        return len(self.__data)

    def __hash__(self) -> int:
        """Get hash for the dict."""
        if self.__hash is None:
            self.__hash = hash(tuple(self.items()))

        return self.__hash
