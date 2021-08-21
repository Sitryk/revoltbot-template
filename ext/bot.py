import os

import aiohttp

from mutiny._internal.client import Client
from . import commands
from . import objects

class Bot(Client):
    _commands = {}
    _aliased_commands = {}

    def __init__(self, prefix: str, *, token: str):
        self.prefix = prefix
        super().__init__(token=token)

    def command(self, func) -> None:
        cmd = commands.command()(func)
        name = cmd.name
        self.add_command(name, cmd)
        return

    def has_command(self, name):
        return name in self._commands.keys() or name in self._aliased_commands.keys()

    async def fetch_user(self, id: str) -> dict:
        """Make a GET request for user info"""
        user_url = f"https://api.revolt.chat/users/{id}"
        async with aiohttp.ClientSession(headers=self._rest.headers) as session:
            resp = await session.get(user_url)
            user_obj = await resp.json()
        return objects.User(**user_obj)

    def add_command(self, name: str, command: commands.Command) -> bool:
        self._commands[name] = command
        for alias in command.aliases:
            self._aliased_commands[alias] = command
        return True

    def remove_command(self, name: str) -> bool:
        cmd = self._commands.pop(name)
        for alias in cmd.aliases:
            self._aliased_commands.pop(alias)
        return True

    def add_plugin(self, plugin_cls):
        for cmd_name, cmd in plugin_cls._commands.items():
            # for some reason the commands plugin isn't updated at this point so
            # just gonna inject it lol
            cmd.plugin = plugin_cls
            self.add_command(cmd_name, cmd)

    def remove_plugin(self, plugin_cls):
        for cmd_name in plugin_cls._commands.keys():
            self.remove_command(cmd_name)