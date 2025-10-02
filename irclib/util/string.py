"""IRC string utils."""

import operator
import string
from typing import (
    Callable,
    Final,
    Literal,
    NamedTuple,
    Optional,
    Protocol,
    SupportsIndex,
    Union,
)

__all__ = ("Casemap", "RFC1459", "STRICT_RFC1459", "ASCII", "String")


class Casemap(NamedTuple):
    """String case-map.

    Represents a mapping of lower to upper case letters
    """

    lower: str
    upper: str

    @property
    def lower_table(self) -> dict[int, int]:
        """The lower->upper translation table."""
        return str.maketrans(self.lower, self.upper)

    @property
    def upper_table(self) -> dict[int, int]:
        """The upper->lower table."""
        return str.maketrans(self.upper, self.lower)


RFC1459: Final = Casemap(
    "".join(map(chr, range(65, 95))), "".join(map(chr, range(97, 127)))
)
STRICT_RFC1459: Final = Casemap(
    "".join(map(chr, range(65, 94))), "".join(map(chr, range(97, 126)))
)
ASCII: Final = Casemap(
    "".join(map(chr, range(65, 91))), "".join(map(chr, range(97, 123)))
)


class TranslateTable(Protocol):
    def __getitem__(self, item: int, /) -> Union[str, int, None]:
        raise NotImplementedError


class String(str):
    """Case-insensitive string."""

    __slots__ = ("_casemap",)

    _casemap: Casemap

    def __new__(
        cls, value: str = "", casemap: Optional[Casemap] = None
    ) -> "String":
        """Construct new String and set casemap."""
        o = str.__new__(cls, value)
        o._casemap = casemap or ASCII  # noqa: SLF001
        return o

    def _wrap(self, value: str) -> "String":
        """Convert value to String with matching casemap."""
        return self.__class__.__new__(self.__class__, value, self.casemap)

    def __internal_cmp(
        self, other: object, cmp: Callable[[str, str], bool]
    ) -> Union[tuple[bool, Literal[True]], tuple[None, Literal[False]]]:
        if isinstance(other, String):
            return cmp(str(self.casefold()), str(other.casefold())), True

        if isinstance(other, str):
            return cmp(self, self._wrap(other)), True

        return None, False

    def translate(self, table: TranslateTable) -> "String":
        """Apply translation table to string."""
        return self._wrap(super().translate(table))

    @property
    def _capitalize(self) -> "String":
        return self[:1].upper() + self[1:].lower()

    def capitalize(self) -> "String":
        """Return a capitalized version of the string.

        More specifically, make the first character have upper case and the rest lower case.
        """
        return self._capitalize

    @property
    def _casefold(self) -> "String":
        return self.lower()

    def casefold(self) -> "String":
        """Casefold the string according to the casemap."""
        return self._casefold

    @property
    def _lower(self) -> "String":
        return self.translate(self.casemap.lower_table)

    def lower(self) -> "String":
        """Lowercase the string according to the casemap."""
        return self._lower

    @property
    def _upper(self) -> "String":
        return self.translate(self.casemap.upper_table)

    def upper(self) -> "String":
        """Uppercase the string according to the casemap."""
        return self._upper

    def count(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        """Count substring occurrences."""
        return str(self.casefold()).count(
            self._wrap(sub).casefold(), start, end
        )

    def startswith(
        self,
        prefix: Union[str, tuple[str, ...]],
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> bool:
        """Check if string starts with a prefix."""
        prefix_list: tuple[str, ...]
        prefix_list = (prefix,) if isinstance(prefix, str) else prefix

        mapped_list = tuple(self._wrap(p).casefold() for p in prefix_list)

        return str(self.casefold()).startswith(mapped_list, start, end)

    def endswith(
        self,
        suffix: Union[str, tuple[str, ...]],
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> bool:
        """Check if string ends with a suffix."""
        suffix_list: tuple[str, ...]
        suffix_list = (suffix,) if isinstance(suffix, str) else suffix

        mapped_list = tuple(self._wrap(p).casefold() for p in suffix_list)

        return str(self.casefold()).endswith(mapped_list, start, end)

    def find(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        """Find the substring in string."""
        return str(self.casefold()).find(self._wrap(sub).casefold(), start, end)

    def rfind(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        """Perform a reverse find."""
        return str(self.casefold()).rfind(
            self._wrap(sub).casefold(), start, end
        )

    def index(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        """Find the index of the substring."""
        return str(self.casefold()).index(
            self._wrap(sub).casefold(), start, end
        )

    def rindex(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        """Perform a reverse index."""
        return str(self.casefold()).rindex(
            self._wrap(sub).casefold(), start, end
        )

    def partition(self, sep: str) -> tuple["String", "String", "String"]:
        """Partition string on a separator."""
        pos = self.find(sep)
        if pos < 0:
            return self, self._wrap(""), self._wrap("")

        return self[:pos], self[pos : pos + len(sep)], self[pos + len(sep) :]

    def rpartition(self, sep: str) -> tuple["String", "String", "String"]:
        """Reverse partition a string on a separator."""
        pos = self.rfind(sep)
        if pos < 0:
            return self._wrap(""), self._wrap(""), self

        return self[:pos], self[pos : pos + len(sep)], self[pos + len(sep) :]

    def replace(
        self, old: str, new: str, count: SupportsIndex = -1
    ) -> "String":
        """Not currently implemented."""
        raise NotImplementedError

    def strip(self, chars: Optional[str] = None) -> "String":
        """Remove characters from the beginning and end of the string."""
        return self.lstrip(chars).rstrip(chars)

    def lstrip(self, chars: Optional[str] = None) -> "String":
        """Remove characters from the beginning of the string."""
        if chars is None:
            chars = string.whitespace

        chars = self._wrap(chars)

        start = 0
        while start < len(self) and self[start] in chars:
            start += 1

        return self[start:]

    def rstrip(self, chars: Optional[str] = None) -> "String":
        """Remove characters from the end of the string."""
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
        """Swap lower-case and upper-case characters."""
        return self._swapcase

    def title(self) -> str:
        """Not currently implemented."""
        raise NotImplementedError

    def split(
        self, sep: Optional[str] = None, maxsplit: SupportsIndex = -1
    ) -> list[str]:
        """Not currently implemented."""
        raise NotImplementedError

    def rsplit(
        self, sep: Optional[str] = None, maxsplit: SupportsIndex = -1
    ) -> list[str]:
        """Not currently implemented."""
        raise NotImplementedError

    @property
    def casemap(self) -> Casemap:
        """Casemap associated with this string."""
        return self._casemap

    def __getitem__(self, item: Union[SupportsIndex, slice]) -> "String":
        """Get substring."""
        return self._wrap(super().__getitem__(item))

    def __contains__(self, item: object) -> bool:
        """Check if `item` is in string case-insensitively."""
        if not isinstance(item, str):
            return False

        return self._wrap(item).casefold() in str(self.casefold())

    def __add__(self, other: str) -> "String":
        """Concat a string to this one."""
        return self._wrap(str(self) + other)

    def __lt__(self, other: str) -> bool:
        """Compare another string to this one case-insensitively."""
        res = self.__internal_cmp(other, operator.lt)
        if not res[1]:
            return NotImplemented

        return res[0]

    def __le__(self, other: str) -> bool:
        """Compare another string to this one case-insensitively."""
        res = self.__internal_cmp(other, operator.le)
        if not res[1]:
            return NotImplemented

        return res[0]

    def __eq__(self, other: object) -> bool:
        """Compare another string to this one case-insensitively."""
        res = self.__internal_cmp(other, operator.eq)
        if not res[1]:
            return NotImplemented

        return res[0]

    def __ne__(self, other: object) -> bool:
        """Compare another string to this one case-insensitively."""
        res = self.__internal_cmp(other, operator.ne)
        if not res[1]:
            return NotImplemented

        return res[0]

    def __gt__(self, other: str) -> bool:
        """Compare another string to this one case-insensitively."""
        res = self.__internal_cmp(other, operator.gt)
        if not res[1]:
            return NotImplemented

        return res[0]

    def __ge__(self, other: str) -> bool:
        """Compare another string to this one case-insensitively."""
        res = self.__internal_cmp(other, operator.ge)
        if not res[1]:
            return NotImplemented

        return res[0]

    def __hash__(self) -> int:
        """Hash the lowercase string."""
        return hash(str(self.lower()))
