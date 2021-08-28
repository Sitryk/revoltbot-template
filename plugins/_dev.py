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
        self.hello_enabled = False

    @commands.command()
    async def mention(self, ctx, id=None):
        """Mention the author"""
        if not id is None:
            user = await self.bot.fetch_user(id)
        else:
            user = ctx.message.author
        await ctx.channel.send(user.mention)

    @commands.command()
    async def rainbow(self, ctx, *msg):
        """Rainbow-ify text, color setting takes up a lot of character space."""
        msg = ' '.join(msg)
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

    @commands.command()
    async def togglehello(self, ctx):
        """Toggle the hello listener on"""
        self.hello_enabled = state = not self.hello_enabled
        await ctx.channel.send(f"Hello listener enabled: `{state}`")

    @commands.listener(events.MessageEvent)
    async def on_message(self, event):
        if not self.hello_enabled:
            return

        ctx = await self.bot.create_context(event)
        if ctx.author.is_bot or ctx.author.id == self.bot.user.id:
                return

        if (msg := ctx.message.content) and 'hello' in msg.lower():
            await ctx.channel.send("hello :)")
