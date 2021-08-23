import aiohttp
import functools
import os

class Channel:

    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.raw_data = kwargs

    @property
    def mention(self):
        return f"<#{self.id}>"


class User:

    def __init__(self, **kwargs):
        self.id = kwargs['_id']
        self.username = kwargs.get('username', '')
        self.avatar = kwargs.get('avatar', None)
        self.badges = kwargs.get('bages', 0)
        self.relationship = kwargs.get('relationship', None)
        self.online = kwargs.get('online', None)
        self.bot = kwargs.get('bot', None)
        self.status = kwargs.get('status', None)
        self.raw_data = kwargs

    @property
    def mention(self):
        return f"<@{self.id}>"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id


class Message:

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.author = kwargs['author']
        self.content = kwargs['content']
        self.channel = kwargs['channel']
        self.raw_data = kwargs


class Context:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.raw_data = kwargs

    @classmethod
    def from_event(cls, event):
        return cls(_event=event, **event.raw_data)
