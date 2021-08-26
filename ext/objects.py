import aiohttp
import functools
import os

from mutiny._internal.models import attachment, channel, message, permissions, server, user 

class MutinyPatch:

    def __init__(self, mutiny_object=None, **kwargs):
        self._mutiny_object = mutiny_object
        self.id = kwargs.pop('_id')

    def __getattr__(self, key):
        """Access self.__dict__ first then access self._mutiny_object"""
        try:
            ret = self.raw_data[key]
            return ret
        except KeyError:
            pass

        try:
            ret = getattr(self._mutiny_object, key)
            print(self._mutiny_object.__dict__)
            return ret
        except AttributeError:
            pass

        s = f'{self} has no attribute {key}'
        raise AttributeError(s)

class TextChannel(MutinyPatch):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raw_data = kwargs

    @property
    def mention(self):
        return f"<#{self.id}>"


class User(MutinyPatch):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raw_data = kwargs

    @property
    def mention(self):
        return f"<@{self.id}>"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id


class Message(MutinyPatch):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raw_data = kwargs


class Context:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.raw_data = kwargs

    def _update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.raw_data.update(kwargs)
