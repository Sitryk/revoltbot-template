import aiohttp
import functools
import os

import mutiny
from mutiny import models

_SUPPORTED_TYPES = (models.User, models.TextChannel, models.Message)


class MutinyPatch:
    def __init__(self, mutiny_object=None):
        assert isinstance(mutiny_object, _SUPPORTED_TYPES)
        self._mutiny_object = mutiny_object
        if mutiny_object:
            self.id = mutiny_object.id
        else:
            self.id = kwargs.get("_id") or kwargs.get("id")

    def __getattr__(self, key):
        """Access self._mutiny_object then self.raw_data"""
        try:
            ret = getattr(self._mutiny_object, key)
            return ret
        except AttributeError:
            pass

        try:
            ret = self.raw_data[key]
            return ret
        except KeyError:
            pass

        s = f"{self} has no attribute {key}"
        raise AttributeError(s)


class TextChannel(MutinyPatch):
    def __init__(self, **kwargs):
        super().__init__(kwargs.pop("mutiny_object"))
        self.raw_data = kwargs

    @property
    def mention(self):
        return f"<#{self.id}>"


class User(MutinyPatch):
    def __init__(self, **kwargs):
        super().__init__(kwargs.pop("mutiny_object"))
        self.raw_data = kwargs

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    @property
    def is_bot(self) -> bool:
        return not (getattr(self._mutiny_object, "bot") is None)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id


class Message(MutinyPatch):
    def __init__(self, **kwargs):
        super().__init__(kwargs.pop("mutiny_object"))
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
