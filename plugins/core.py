from ext import commands
from ext.objects import Context

import aiohttp
import json
import io
import time
import platform
import mutiny

class Core(commands.Plugin):

    def __init__(self, bot):
        self.bot = bot

    async def update_user(self, data: dict):
        """Update the bot."""
        headers = self.bot._rest.headers
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.patch("https://api.revolt.chat/users/@me", json=data) as r:
                status = r.status
            await session.close()
        return status

    #async def update_username(self, data: dict):
    #    """Update the bot username."""
    #    headers = self.bot._rest.headers
    #    async with aiohttp.ClientSession(headers=headers) as session:
    #        async with session.patch(f"https://api.revolt.chat/bots/{self.bot.id}", json=data) as r:
    #            status = r.status
    #        await session.close()
    #    return status

    def secondsToText(self, secs):
        """Convert seconds to readable format."""
        secs = int(secs)
        days = secs//86400
        hours = (secs - days*86400)//3600
        minutes = (secs - days*86400 - hours*3600)//60
        seconds = secs - days*86400 - hours*3600 - minutes*60
        result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
        ("{0} hour{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
        ("{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
        ("{0} second{1} ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
        return result

    @commands.command()
    async def ping(self, ctx):
        """Pong."""
        before = time.monotonic()
        message = await ctx.channel.send("Pls wait...")
        ping = (time.monotonic() - before) * 1000
        await ctx.channel.send(f"Ping pong! {int(ping)}ms")

    @commands.command()
    async def shutdown(self, ctx):
        """Shutdown the bot."""
        if ctx.author.id != self.bot.owner.id:
            return await ctx.channel.send("Unauthorised.")
        else:
            await ctx.channel.send("Shutting down.")
            await self.bot.close()

    @commands.command()
    async def info(self, ctx):
        """Bot information."""
        mutinyv = mutiny.__version__
        pythonv = platform.python_version()
        botinfo = await self.bot.fetch_user(self.bot.id)
        name = botinfo.username
        avatar = botinfo.avatar["_id"]
        msg = f"# [](https://autumn.revolt.chat/avatars/{avatar}?width=240)[{name}](/@{self.bot.id})\n"
        msg += f"**Mutiny:** [{mutinyv}](https://pypi.org/project/mutiny/)\n"
        msg += f"**Python:** [{pythonv}](https://www.python.org)\n"
        msg += f"**Invite URL:** https://app.revolt.chat/bot/{self.bot.id}"
        await ctx.channel.send(msg)

    @commands.command()
    async def uptime(self, ctx):
        """Bot uptime."""
        uptime = self.secondsToText(time.time() - self.bot.init_time)
        since = time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(self.bot.init_time))
        await ctx.channel.send(f"**Uptime:** {uptime}\n**Since:** {since} UTC")

    @commands.group()
    async def set(self, ctx):
        """Set bot information."""
        pass

    @set.command()
    async def remove(self, ctx, info):
        """Remove the bot's information. Avatar, Banner, Profile, Status"""
        if ctx.author != self.bot.owner:
            return await ctx.channel.send("Unauthorised.")
        if info.lower() == "avatar":
            json_data = {"remove": "Avatar"}
            success = await self.update_user(json_data)
            if success == 200:
                await ctx.channel.send("Avatar removed!")
            else:
                await ctx.channel.send(f"Removal failed. ({success})")
        elif info.lower() == "banner":
            json_data = {"remove": "ProfileBackground"}
            success = await self.update_user(json_data)
            if success == 200:
                await ctx.channel.send("Banner removed!")
            else:
                await ctx.channel.send(f"Removal failed. ({success})")
        elif info.lower() == "profile":
            json_data = {"remove": "ProfileContent"}
            success = await self.update_user(json_data)
            if success == 200:
                await ctx.channel.send("Profile removed!")
            else:
                await ctx.channel.send(f"Removal failed. ({success})")
        elif info.lower() == "status":
            json_data = {"remove": "StatusText"}
            success = await self.update_user(json_data)
            if success == 200:
                await ctx.channel.send("Status removed!")
            else:
                await ctx.channel.send(f"Removal failed. ({success})")
        else:
            await ctx.channel.send(f"`{info}` isn't a valid option.")

    @set.command()
    async def avatar(self, ctx, url):
        """Update the bot's avatar."""
        if ctx.author != self.bot.owner:
            return await ctx.channel.send("Unauthorised.")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                avatar = io.BytesIO(await resp.read())
            form = aiohttp.FormData()
            form.add_field("file", avatar, content_type="application/octet-stream")
            async with session.post("https://autumn.revolt.chat/avatars", data=form) as resp:
                avatar_str = await resp.text()
            await session.close()
        avatar_id = json.loads(avatar_str)
        json_data = {"avatar": avatar_id["id"]}
        success = await self.update_user(json_data)
        if success == 200:
            await ctx.channel.send("Avatar updated!")
        else:
            await ctx.channel.send(f"Update failed. ({success})")

    @set.command()
    async def banner(self, ctx, url):
        """Update the bot's banner."""
        if ctx.author != self.bot.owner:
            return await ctx.channel.send("Unauthorised.")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                banner = io.BytesIO(await resp.read())
            form = aiohttp.FormData()
            form.add_field("file", banner, content_type="application/octet-stream")
            async with session.post("https://autumn.revolt.chat/backgrounds", data=form) as resp:
                banner_str = await resp.text()
            await session.close()
        banner_id = json.loads(banner_str)
        json_data = {"profile": {"background": banner_id["id"]}}
        success = await self.update_user(json_data)
        if success == 200:
            await ctx.channel.send("Banner updated!")
        else:
            await ctx.channel.send(f"Update failed. ({success})")

    @set.command()
    async def presence(self, ctx, presence):
        """Update the bot's presence. Busy, Idle, Invisible, Online."""
        if ctx.author != self.bot.owner:
            return await ctx.channel.send("Unauthorised.")
        presli = ["busy", "idle", "invisible", "online"]
        for i in presli:
            if presence.lower() == i:
                botinfo = await self.bot.fetch_user(self.bot.id)
                if botinfo.status is None:
                    json_data = {"status": {"presence": presence.title()}}
                elif "text" not in botinfo.status:
                    json_data = {"status": {"presence": presence.title()}}
                else:
                    status = botinfo.status["text"]
                    json_data = {"status": {"text": status, "presence": presence.title()}}
                success = await self.update_user(json_data)
                if success == 200:
                    await ctx.channel.send("Presence updated!")
                else:
                    await ctx.channel.send(f"Update failed. ({success})")

    @set.command()
    async def status(self, ctx, *status):
        """Update the bot's status."""
        if ctx.author != self.bot.owner:
            return await ctx.channel.send("Unauthorised.")
        botinfo = await self.bot.fetch_user(self.bot.id)
        if botinfo.status is None:
            json_data = {"status": {"text": " ".join(status)}}
        elif "presence" not in botinfo.status:
            json_data = {"status": {"text": " ".join(status)}}
        else:
            presence = botinfo.status["presence"]
            json_data = {"status": {"text": " ".join(status), "presence": presence}}
        success = await self.update_user(json_data)
        if success == 200:
            await ctx.channel.send("Status updated!")
        else:
            await ctx.channel.send(f"Update failed. ({success})")

    @set.command()
    async def profile(self, ctx, *text):
        """Update the bot's profile."""
        if ctx.author != self.bot.owner:
            return await ctx.channel.send("Unauthorised.")
        json_data = {"profile": {"content": " ".join(text)}}
        success = await self.update_user(json_data)
        if success == 200:
            await ctx.channel.send("Profile updated!")
        else:
            await ctx.channel.send(f"Update failed. ({success})")

    #@set.command()
    #async def username(self, ctx, username):
    #    """Update the bot's username"""
    #    if ctx.author != self.bot.owner:
    #        return await ctx.channel.send("Unauthorised.")
    #    json_data = {"name": username}
    #    success = await self.update_username(json_data)
    #    if success == 200:
    #        await ctx.channel.send("Username updated!")
    #    else:
    #        await ctx.channel.send(f"Update failed. ({success})")


async def setup(bot):
    bot.add_plugin(Core(bot))