import asyncio
from functools import partial
import json
import os
import pathlib

from mutiny import Client, events
from mutiny._internal.rest import RESTClient

from ext.bot import Bot
from ext import objects


#############
### SETUP ###
#############

_CONF_FILE = pathlib.Path(__file__).parent / "bot_config.json"
_CONFIG = None

## First time token and prefix input?

try:
    with open(_CONF_FILE, 'r') as f:
        _CONFIG = json.load(f)
except FileNotFoundError:
    IN_TOKEN = input('Bot token: ')
    print('Use | to delimeter multiple prefixes')
    IN_PREFIXES = input('Bot prefixes: ').split('|')

    with open(_CONF_FILE, mode='w') as f:
        json.dump({'TOKEN':IN_TOKEN,'PREFIXES':IN_PREFIXES}, f)
    _TOKEN = IN_TOKEN
    _PREFIXES = IN_PREFIXES
except Exception as e:
    print(e)
else:
    _TOKEN = _CONFIG['TOKEN']
    _PREFIXES = _CONFIG['PREFIXES']



bot = Bot(prefixes=_PREFIXES, token=_TOKEN)

# Listeners can be added by defining a single argument function
# decorated with `@client.listen()` and with its argument type-hinted
# with an appropriate event type:

@bot.listen()
async def on_ready(event: events.ReadyEvent) -> None:
    data = event.raw_data
    bot_info = data["users"][0]
    owner_id = bot_info['bot']['owner']
    owner = await bot.fetch_user(owner_id)
    bot.id = bot_info["_id"]
    bot.owner = owner

    n_text = 0
    n_voice = 0
    for channel in data["channels"]:
        if channel["channel_type"] == "TextChannel":
            n_text += 1
        elif channel["channel_type"] == "VoiceChannel":
            n_voice += 1

    CENTER_BY = 80

    startup_msg = [s.center(CENTER_BY) for s in [".\n",
           "----------------------------------------",
          f"~~ Revolt.chat Bot, powered by Mutiny ~~",
           "----------------------------------------",
          f"Hi, I'm {bot_info['username']}",
          f"I belong to {owner.username} [{owner.id}]",
          f"Prefixes: {_PREFIXES}",
           "Connected to:",
          f"{len(data['servers'])} servers",
          f"{n_text} text channels",
          f"{n_voice} voice channels",
          f"Invite URL: https://app.revolt.chat/bot/{bot_info['_id']}",
           "-----------------------------------------"
           ]]

    print(bot._commands)
    print('\n'.join(startup_msg))


@bot.listen()
async def on_message(event: events.MessageEvent) -> None:
    dat = event.raw_data
    msg = dat.get('content', None)
    if not isinstance(msg, str):
        print(event)
        return

    # also gross fetching the user every time because
    # the users aren't cached and we don't know if the
    # author is a bot
    user = await bot.fetch_user(dat['author'])
    if "bot" in user.raw_data.keys():
        return

    # partial context
    # also process_commands should raise CommandErrors
    # about stuff that we can dispatch and use
    p_ctx = await bot.process_commands(msg)

    # command doesn't exist although prefix was used
    if p_ctx is None:
        return

    # fill the rest of p_ctx in such as channel objects etc.
    p_ctx.event = event
    p_ctx.channel = await bot.fetch_channel(id=dat['channel'])
    p_ctx.channel.send = partial(bot.send_to_channel, p_ctx.channel.id)
    p_ctx.author = await bot.fetch_user(id=dat['author'])
    p_ctx.message = objects.Message(id=dat['_id'], author=p_ctx.author, content=msg, channel=p_ctx.channel)

    ctx = p_ctx
    # all commands take ctx oh well.
    ctx.command_args = [ctx, *ctx.command_args]
    await ctx.command(*ctx.command_args)


################################
### CUSTOM COMMAND EXTENSION ###
################################


@bot.command()
async def ping(ctx):
    """Pong."""
    await ctx.channel.send('Dong')

@bot.command()
async def shutdown(ctx):
    """Shutdown le bot."""
    if ctx.author != bot.owner:
        await ctx.channel.send("Not allowed, pal.")
        return
    else:
        await ctx.channel.send('Shutting down.')
        await bot.close()

@bot.command()
async def help(ctx):
    """Shows this help message"""
    sorted_cmds = dict(sorted(bot._commands.items(), key=lambda x: x[0].lower()))

    table = f"| Command| Usage | Description |\n"
    table += "|-|-|-|\n"
    for name, cmd in sorted_cmds.items():
        table += f"| {name} | {cmd.signature} | {cmd.__doc__} \n"
    await ctx.channel.send(table)

@bot.command()
async def load(ctx, *cogs):
    """load cog(s) NOTIMEPLEMTERNDDED"""
    pass


##############
### PLUGIN ###
##############

from plugins._dev import Dev
bot.add_plugin(Dev(bot))

#############
### ENTRY ###
#############

asyncio.run(bot.start())
