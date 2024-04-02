"""Frozen Dict"""

from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

__all__ = ("FrozenDict",)

V = TypeVar("V", bound=Any)
SelfT = TypeVar("SelfT", bound="FrozenDict[Any]")


class FrozenDict(Mapping[str, V]):
    """Frozen Mapping.

    An immutable mapping of string -> Any type
    """

    __slots__ = ("__hash", "__data")

    def __getitem__(self, k: str) -> V:
        return self.__data[k]

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__data)

    def __init__(
        self,
        seq: Union[Mapping[str, V], Iterable[Tuple[str, V]], None] = None,
        **kwargs: V,
    ) -> None:
        d = dict(seq, **kwargs) if seq is not None else dict(**kwargs)

        self.__data: Dict[str, V] = d
        self.__hash: Optional[int] = None

    def copy(self: SelfT, **kwargs: V) -> SelfT:
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

    def __hash__(self) -> int:
        if self.__hash is None:
            self.__hash = hash(tuple(self.items()))

        return self.__hash
