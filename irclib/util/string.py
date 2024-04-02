"""
IRC string utils
"""

import operator
import string
from typing import (
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Protocol,
    SupportsIndex,
    Tuple,
    Union,
)

__all__ = ("Casemap", "RFC1459", "STRICT_RFC1459", "ASCII", "String")


class Casemap(NamedTuple):
    """String case-map

    Represents a mapping of lower to upper case letters
    """

    lower: str
    upper: str

    @property
    def lower_table(self) -> Dict[int, int]:
        """The lower->upper translation table"""
        return str.maketrans(self.lower, self.upper)

    @property
    def upper_table(self) -> Dict[int, int]:
        """The upper->lower table"""
        return str.maketrans(self.upper, self.lower)


RFC1459 = Casemap(
    "".join(map(chr, range(65, 95))), "".join(map(chr, range(97, 127)))
)
STRICT_RFC1459 = Casemap(
    "".join(map(chr, range(65, 94))), "".join(map(chr, range(97, 126)))
)
ASCII = Casemap(
    "".join(map(chr, range(65, 91))), "".join(map(chr, range(97, 123)))
)


class TranslateTable(Protocol):
    def __getitem__(self, item: int, /) -> Union[str, int, None]:
        raise NotImplementedError


class String(str):
    """Case-insensitive string"""

    __slots__ = ("_casemap",)

    _casemap: Casemap

    def _wrap(self, value: str) -> "String":
        return self.__class__.__new__(self.__class__, value, self.casemap)

    def __new__(
        cls, value: str = "", casemap: Optional[Casemap] = None
    ) -> "String":
        o = str.__new__(cls, value)
        o._casemap = casemap or ASCII  # noqa: SLF001
        return o

    def __hash__(self) -> int:
        return hash(str(self.lower()))

    def __internal_cmp(
        self, other: object, cmp: Callable[[str, str], bool]
    ) -> bool:
        if isinstance(other, String):
            return cmp(str(self.casefold()), str(other.casefold()))

        if isinstance(other, str):
            return cmp(self, self._wrap(other))

        return NotImplemented

    def __lt__(self, other: str) -> bool:
        return self.__internal_cmp(other, operator.lt)

    def __le__(self, other: str) -> bool:
        return self.__internal_cmp(other, operator.le)

    def __eq__(self, other: object) -> bool:
        return self.__internal_cmp(other, operator.eq)

    def __ne__(self, other: object) -> bool:
        return self.__internal_cmp(other, operator.ne)

    def __gt__(self, other: str) -> bool:
        return self.__internal_cmp(other, operator.gt)

    def __ge__(self, other: str) -> bool:
        return self.__internal_cmp(other, operator.ge)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, str):
            return False

        return self._wrap(item).casefold() in str(self.casefold())

    def __getitem__(self, item: Union[SupportsIndex, slice]) -> "String":
        return self._wrap(super().__getitem__(item))

    def translate(self, table: TranslateTable) -> "String":
        return self._wrap(super().translate(table))

    @property
    def _capitalize(self) -> "String":
        return self[:1].upper() + self[1:].lower()

    def __add__(self, other: str) -> "String":
        return self._wrap(str(self) + other)

    def capitalize(self) -> "String":
        return self._capitalize

    @property
    def _casefold(self) -> "String":
        return self.lower()

    def casefold(self) -> "String":
        return self._casefold

    @property
    def _lower(self) -> "String":
        return self.translate(self.casemap.lower_table)

    def lower(self) -> "String":
        return self._lower

    @property
    def _upper(self) -> "String":
        return self.translate(self.casemap.upper_table)

    def upper(self) -> "String":
        return self._upper

    def count(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        return str(self.casefold()).count(
            self._wrap(sub).casefold(), start, end
        )

    def startswith(
        self,
        prefix: Union[str, Tuple[str, ...]],
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> bool:
        prefix_list: Tuple[str, ...]
        prefix_list = (prefix,) if isinstance(prefix, str) else prefix

        mapped_list = tuple(self._wrap(p).casefold() for p in prefix_list)

        return str(self.casefold()).startswith(mapped_list, start, end)

    def endswith(
        self,
        suffix: Union[str, Tuple[str, ...]],
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> bool:
        suffix_list: Tuple[str, ...]
        suffix_list = (suffix,) if isinstance(suffix, str) else suffix

        mapped_list = tuple(self._wrap(p).casefold() for p in suffix_list)

        return str(self.casefold()).endswith(mapped_list, start, end)

    def find(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        return str(self.casefold()).find(self._wrap(sub).casefold(), start, end)

    def rfind(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        return str(self.casefold()).rfind(
            self._wrap(sub).casefold(), start, end
        )

    def index(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        return str(self.casefold()).index(
            self._wrap(sub).casefold(), start, end
        )

    def rindex(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        return str(self.casefold()).rindex(
            self._wrap(sub).casefold(), start, end
        )

    def partition(self, sep: str) -> Tuple["String", "String", "String"]:
        pos = self.find(sep)
        if pos < 0:
            return self, self._wrap(""), self._wrap("")

        return self[:pos], self[pos : pos + len(sep)], self[pos + len(sep) :]

    def rpartition(self, sep: str) -> Tuple["String", "String", "String"]:
        pos = self.rfind(sep)
        if pos < 0:
            return self._wrap(""), self._wrap(""), self

        return self[:pos], self[pos : pos + len(sep)], self[pos + len(sep) :]

    def replace(
        self, old: str, new: str, count: SupportsIndex = -1
    ) -> "String":
        raise NotImplementedError

    def strip(self, chars: Optional[str] = None) -> "String":
        return self.lstrip(chars).rstrip(chars)

    def lstrip(self, chars: Optional[str] = None) -> "String":
        if chars is None:
            chars = string.whitespace

        chars = self._wrap(chars)

        start = 0
        while start < len(self) and self[start] in chars:
            start += 1

        return self[start:]

    def rstrip(self, chars: Optional[str] = None) -> "String":
        if chars is None:
            chars = string.whitespace

        chars = self._wrap(chars)

        end = len(self)
        while end > 0 and self[end - 1] in chars:
            end -= 1

        return self[:end]

    @property
    def _swapcase(self) -> "String":
        trans = self.casemap.lower_table.copy()
        trans.update(self.casemap.upper_table)

        return self.translate(trans)

    def swapcase(self) -> "String":
        return self._swapcase

    def title(self) -> str:
        raise NotImplementedError

    def split(
        self, sep: Optional[str] = None, maxsplit: SupportsIndex = -1
    ) -> List[str]:
        raise NotImplementedError

    def rsplit(
        self, sep: Optional[str] = None, maxsplit: SupportsIndex = -1
    ) -> List[str]:
        raise NotImplementedError

    @property
    def casemap(self) -> Casemap:
        """Casemap associated with this string"""
        return self._casemap
