import os
from ulid import monotonic as ulid

import aiohttp



from mutiny._internal.client import Client
from . import commands
from . import objects
from . import errors

class Bot(Client):
    _commands = {}
    _aliased_commands = {}

    def __init__(self, prefixes: list[str], *, token: str):
        prefixes.sort(key=len, reverse=True)
        self.prefixes = prefixes
        super().__init__(token=token)

    # think this should be returning a decorator not being its own...
    def command(self, *args,**kwargs) -> None:
        def deco(func):
            cmd = commands.command(*args, **kwargs)(func)
            name = cmd.full_name
            self.add_command(name, cmd)
        return deco

    def _parse_arguments(self, ctx):
        pass

    async def process_commands(self, content) -> objects.Context:
        # print(content)
        used_prefix = None
        for prefix in self.prefixes:
            if content.startswith(prefix):
                used_prefix = prefix
                content = content[len(prefix):]
                break

        if used_prefix is None:
            return

        # print('prefix found')

        valid_cmd_name = None
        if ' ' in content:
            # I'm going to just impose 5 groups deep is enough...
            MAX_SUBGROUPS = 5
            split_content = content.split(' ', MAX_SUBGROUPS-1)
            # anything with less than 5 splits need to not index out of range
            MAX_SUBGROUPS = min(len(split_content), MAX_SUBGROUPS)
            for idx, i in enumerate(split_content, 1):
                attempt = ' '.join(split_content[:idx-MAX_SUBGROUPS])
                if self.has_command(attempt):
                    valid_cmd_name = attempt
                    continue
                else:
                    break
        else:
            if self.has_command(content):
                valid_cmd_name = content

        if valid_cmd_name is None:
            return
        command = self.get_command(valid_cmd_name)

        rest = content[len(valid_cmd_name):]
        args = [s for s in rest.split(' ') if not s == '']
        reduce_args = 0 if command.plugin is None else 1
        print(command.signature.parameters)
        args = args[:len(command.signature.parameters) - reduce_args]
        partial_ctx = objects.Context(prefix=used_prefix, command=command, command_args=args)
        return partial_ctx

    def has_command(self, full_name: str) -> bool:
        return full_name in self._commands.keys() or full_name in self._aliased_commands.keys()

    def get_command(self, full_name: str) -> commands.Command:
        cmd = self._commands.get(full_name, None) or self._aliased_commands.get(full_name, None)
        return cmd

    # anything fetching should be part of the mutiny Client
    async def fetch_channel(self, id: str) -> dict:
        """Make a GET request for channe info"""
        channel_url = f"https://api.revolt.chat/channels/{id}"
        async with aiohttp.ClientSession(headers=self._rest.headers) as session:
            resp = await session.get(channel_url)
            channel_data = await resp.json()
            await session.close()
        return objects.Channel(**channel_data)

    async def fetch_user(self, id: str) -> dict:
        """Make a GET request for user info"""
        user_url = f"https://api.revolt.chat/users/{id}"
        async with aiohttp.ClientSession(headers=self._rest.headers) as session:
            resp = await session.get(user_url)
            user_data = await resp.json()
            await session.close()
        return objects.User(**user_data)

    async def send_to_channel(self, channel_id, content, **kwargs):
        location = f"https://api.revolt.chat/channels/{channel_id}/messages"
        nonce = ulid.new().str
        async with aiohttp.ClientSession(headers=self._rest.headers) as session:
            await session.post(location, json={"content": content, "nonce": nonce, **kwargs})
            await session.close()

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

    def add_plugin(self, plugin_cls: commands.Plugin):
        for cmd_name, cmd in plugin_cls._commands.items():
            # for some reason the commands plugin isn't updated at this point so
            # just gonna inject it lol
            cmd.plugin = plugin_cls
            self.add_command(cmd_name, cmd)

    def remove_plugin(self, plugin_cls: commands.Plugin):
        for cmd_name in plugin_cls._commands.keys():
            self.remove_command(cmd_name)