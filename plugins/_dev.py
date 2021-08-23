from ext import commands
from ext.objects import Context, Message

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

    @commands.command()
    async def embed(self, ctx):
        """Test custom embed"""
        e = Embed(colour='00ff00', title='Swaggy test')
        await ctx.channel.send(f"[]({e})")

    @commands.command()
    async def say(self, ctx, msg: str):
        await ctx.channel.send(msg)

    @commands.command()
    async def test(self, ctx, *, rest: str):
        await ctx.channel.send(rest)

    @commands.group()
    async def group1(self, ctx):
        """group1 parent"""
        await ctx.channel.send('group1')

    @group1.command()
    async def s1(self, ctx):
        """group1 sub1"""
        await ctx.channel.send('g1s1')

    @group1.group()
    async def s2(self, ctx, *args):
        """group1 sub2"""
        await ctx.channel.send(f"g1s2 {args}")

    @s2.command()
    async def subsub(self, ctx):
        await ctx.channel.send("group sub sub")