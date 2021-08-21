from ext import commands
from ext.objects import Context, Message

COLOUR = ['#F66', '#FC6', '#CF6', '#6F6', '#6FC', '#6CF', '#66F', '#C6F']

class Dev(commands.Plugin):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mention(self, event):
        """Mention the author"""
        ctx = Context.from_event(event)
        user = await self.bot.fetch_user(ctx.author.id)
        await ctx.channel.send(user.mention)

    @commands.command()
    async def rainbow(self, event):
        """Rainbow-ify text"""
        ctx = Context.from_event(event)
        msg = event.raw_data['content'].split(' ', 1)[-1]
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
