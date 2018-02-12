from collections import Mapping


class Command:
    def __init__(self, name, args=None, min_args=0, max_args=None):
        self.name = name
        self.args = args
        self.min_args = min_args
        self.max_args = max_args


class LookupDict(Mapping):
    def __init__(self, *commands):
        for command in commands:
            setattr(self, command.name.lower(), command)
            setattr(self, command.name.upper(), command)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError as e:
            raise KeyError(key) from e

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


# Commands sent from the client to the server
client_commands = LookupDict(
    Command('PRIVMSG', "<target> <content>"),
    Command('NOTICE', "<target> <content>"),
)

