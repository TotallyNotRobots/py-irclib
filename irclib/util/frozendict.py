class FrozenDict(dict):
    __slots__ = ("__hash",)

    __setitem__ = None
    __delitem__ = None

    pop = None
    popitem = None

    clear = None
    setdefault = None
    update = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__hash = None

    def copy(self, **kwargs):
        return self.__class__(self, **kwargs)

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash(tuple(self.items()))

        return self.__hash
