from ext import commands
from ext.objects import Context, Message

from mutiny import events

import rich
from rich import print

from urllib.parse import urlencode

COLOUR = ['#F66', '#FC6', '#CF6', '#6F6', '#6FC', '#6CF', '#66F', '#C6F']

class Embed:
    _KEYS = ('author', 'title', 'description', 'color', 'image_url')

    def __init__(self, **kwargs):
        self.author = kwargs.get('author', None)
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.color = kwargs.get('colour', None) or kwargs.get('color', None)
        self.image = kwargs.get('image_url', None) or kwargs.get('image', None)

    def __str__(self):
        query = {}
        for k in self._KEYS:
            if not (v := getattr(self, k)) is None:
                query[k] = v
        end = urlencode(query)
        # relying on third party for embed lol moment lololoololololol
        return "https://embed.rauf.workers.dev/?" + end


class Dev(commands.Plugin):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mention(self, ctx, id=None):
        """Mention the author"""
        if not id is None:
            user = await self.bot.fetch_user(id)
        else:
            user = ctx.message.author
        await ctx.channel.send(user.mention)

    @commands.command()
    async def rainbow(self, ctx):
        """Rainbow-ify text, color setting takes up a lot of character space."""
        msg = ctx.message.content.split(' ', 1)[-1]
        new = '$\\textsf{'
        at = 1
        for idx, c in enumerate(msg):
            at = idx % len(COLOUR)
            if c == ' ':
                new += ' '
                continue
            new += f"\\color{{{COLOUR[at-1]}}}{c}"
            if len(new) >= 1980:
                break
        new += '}$'
        await ctx.channel.send(new)

    @commands.command(hidden=True)
    async def embed(self, ctx):
        """Test custom embed"""
        e = Embed(colour='00ff00', title='Swaggy test')
        await ctx.channel.send(f"[]({e})")

    # @commands.listener(events.MessageEvent)
    # async def on_message(self, event):
    #     data = event.raw_data
    #     if data['author'] == self.bot.id:
    #             return

    #     if 'content' in data.keys() and isinstance((msg := data['content']), str) and 'SEND' in msg:
    #         await self.bot.send_to_channel(data['channel'], str(msg))

    #     pretty = rich.pretty.Pretty(event.raw_data)
    #     panel = rich.panel.Panel(pretty)
    #     print(panel)
    #     print(event.message)
    #     print(event.type)