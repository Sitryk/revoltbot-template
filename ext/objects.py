import aiohttp
import functools
import os

from ulid import monotonic as ulid

BOT_TOKEN = os.environ['BOT_TOKEN']

class Channel:

    def __init__(self, id):
        self.id = id

    @property
    def mention(self):
        return f"<#{self.id}>"

    async def send(self, content: str, **kwargs):
        location = f"https://api.revolt.chat/channels/{self.id}/messages"
        nonce = ulid.new().str
        async with aiohttp.ClientSession(headers={"x-bot-token": BOT_TOKEN}) as session:
            await session.post(location, json={"content": content, "nonce": nonce, **kwargs})
            await session.close()


class User:

    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.username = kwargs.get('username', '')
        self.avatar = kwargs.get('avatar', None)
        self.badges = kwargs.get('bages', 0)
        self.relationship = kwargs.get('relationship', None)
        self.online = kwargs.get('online', None)

    @property
    def mention(self):
        return f"<@{self.id}>"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id


class Message:

    def __init__(self, id: str, author: User, content: str=None, channel: Channel=None):
        self.id = id
        self.author = author
        self.content = content
        self.channel = channel


class Context:

    def __init__(self, **kwargs):
        if (c_id := kwargs.get('channel', None)):
            self.channel = Channel(id=c_id)
        if (a_id := kwargs.get('author', None)):
            self.author = User(_id=a_id)
        self.raw_data = kwargs

    @classmethod
    def from_event(cls, event):
        return cls(_event=event, **event.raw_data)
