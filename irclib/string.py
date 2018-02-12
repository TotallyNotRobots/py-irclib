# coding=utf-8
"""
IRC string utils
"""
import operator
from functools import wraps


class Casemap(tuple):
    __slots__ = ()

    def __new__(cls, lower, upper):
        return tuple.__new__(cls, (lower, upper))

    @property
    def lower_table(self):
        return str.maketrans(self.lower, self.upper)

    @property
    def upper_table(self):
        return str.maketrans(self.upper, self.lower)

    @property
    def lower(self):
        return self[0]

    @property
    def upper(self):
        return self[1]


RFC1459 = Casemap("".join(map(chr, range(65, 95))), "".join(map(chr, range(97, 127))))
STRICT_RFC1459 = Casemap("".join(map(chr, range(65, 94))), "".join(map(chr, range(97, 126))))
ASCII = Casemap("".join(map(chr, range(65, 91))), "".join(map(chr, range(97, 123))))

sentinel = object()


class cached_property:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except AttributeError:  # pragma: no cover
            self.__doc__ = ""

        self.name = wrapped.__name__

    def __get__(self, inst, owner, _sentinel=sentinel):
        if inst is None:
            return self

        val = inst._cache.get(self.name, _sentinel)
        if val is not _sentinel:
            return val

        inst._cache[self.name] = val = self.wrapped(inst)
        return val

    def __set__(self, inst, value):
        raise AttributeError("cached property is read-only")


class cached_method(cached_property):
    def __get__(self, inst, owner, _sentinel=sentinel):
        return lambda: cached_property.__get__(self, inst, owner, _sentinel)


def type_wrap(super_index, wrap_out=True):
    def _decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not isinstance(args[super_index], String):
                args = list(args)
                args[super_index] = self._wrap(args[super_index])

            if wrap_out:
                return self._wrap(func(self, *args, **kwargs))

            return func(self, *args, **kwargs)

        return wrapper

    return lambda func: _decorate(func)


class String(str):
    __slots__ = ("_casemap", "_cache")

    def _wrap(self, value):
        return self.__class__(value, self.casemap)

    @cached_method
    def __hash__(self):
        return hash(str(self.lower()))

    def __new__(cls, value='', casemap=None):
        return str.__new__(cls, value)

    def __init__(self, value='', casemap=None):
        super().__init__()
        self._cache = dict(casemap=casemap)

    def __internal_cmp(self, other, cmp):
        if isinstance(other, String):
            return cmp(str(self.casefold()), str(other.casefold()))

        return cmp(self, self._wrap(other))

    def __lt__(self, other):
        return self.__internal_cmp(other, operator.lt)

    def __le__(self, other):
        return self.__internal_cmp(other, operator.le)

    def __eq__(self, other):
        return self.__internal_cmp(other, operator.eq)

    def __ne__(self, other):
        return self.__internal_cmp(other, operator.ne)

    def __gt__(self, other):
        return self.__internal_cmp(other, operator.gt)

    def __ge__(self, other):
        return self.__internal_cmp(other, operator.ge)

    @type_wrap(0, False)
    def __contains__(self, item):
        return item.casefold() in str(self.casefold())

    def __getitem__(self, item):
        return self._wrap(super().__getitem__(item))

    def translate(self, table):
        return self._wrap(super().translate(table))

    @cached_method
    def capitalize(self):
        return self[:1].upper() + self[1:].lower()

    @cached_method
    def casefold(self):
        return self.lower()

    @cached_method
    def lower(self):
        return self.translate(self.casemap.lower_table)

    @cached_method
    def upper(self):
        return self.translate(self.casemap.upper_table)

    @type_wrap(0)
    def count(self, c, start=None, end=None):
        return str(self.casefold()).count(c.casefold(), start, end)

    @type_wrap(0)
    def startswith(self, prefix, start=None, end=None):
        return str(self.casefold()).startswith(prefix.lower(), start, end)

    @type_wrap(0)
    def endswith(self, suffix, start=None, end=None):
        return str(self.casefold()).endswith(suffix.casefold(), start, end)

    @type_wrap(0)
    def find(self, sub, start=None, end=None):
        return str(self.casefold()).find(sub.casefold(), start, end)

    @type_wrap(0)
    def rfind(self, sub, start=None, end=None):
        return str(self.casefold()).rfind(sub.casefold(), start, end)

    @type_wrap(0)
    def index(self, sub, start=None, end=None):
        return str(self.casefold()).index(sub.casefold(), start, end)

    @type_wrap(0)
    def rindex(self, sub, start=None, end=None):
        return str(self.casefold()).rindex(sub.casefold(), start, end)

    @type_wrap(0, False)
    def partition(self, sep):
        pos = self.find(sep)
        if pos < 0:
            return self, self._wrap(""), self._wrap("")

        return self[:pos], self[pos:pos + len(sep)], self[pos + len(sep):]

    @type_wrap(0, False)
    def rpartition(self, sep):
        pos = self.rfind(sep)
        if pos < 0:
            return self._wrap(""), self._wrap(""), self

        return self[:pos], self[pos:pos + len(sep)], self[pos + len(sep):]

    def replace(self, old, new, count=-1):
        raise NotImplementedError

    def strip(self, chars=None):
        return self.lstrip(chars).rstrip(chars)

    def lstrip(self, chars=None):
        raise NotImplementedError

    def rstrip(self, chars=None):
        raise NotImplementedError

    @cached_method
    def swapcase(self):
        tr = self.casemap.lower_table + self.casemap.upper_table

        return self.translate(tr)

    def title(self):
        raise NotImplementedError

    def split(self, sep=None, maxsplit=-1):
        raise NotImplementedError

    def rsplit(self, sep=None, maxsplit=-1):
        raise NotImplementedError

    @cached_property
    def casemap(self):
        raise RuntimeError("String.casefold property not properly cached")
