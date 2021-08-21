import asyncio
import os

from configparser import ConfigParser

from mutiny import Client, events
from mutiny._internal.rest import RESTClient

from ext.bot import Bot
from ext.objects import Channel, Context, User, Message


#############
### SETUP ###
#############

_PREFIX = "?>"
_TOKEN = os.environ['BOT_TOKEN']

bot = Bot(prefix=_PREFIX, token=_TOKEN)

# Listeners can be added by defining a single argument function
# decorated with `@client.listen()` and with its argument type-hinted
# with an appropriate event type:

@bot.listen()
async def on_ready(event: events.ReadyEvent) -> None:
    data = event.raw_data
    bot_info = data["users"][0]
    owner_id = bot_info['bot']['owner']
    owner = await bot.fetch_user(owner_id)
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
           "Connected to:",
          f"{len(data['servers'])} servers",
          f"{n_text} text channels",
          f"{n_voice} voice channels",
          f"Invite URL: https://app.revolt.chat/bot/{bot_info['_id']}",
           "-----------------------------------------"
           ]]

    print('\n'.join(startup_msg))


@bot.listen()
async def on_message(event: events.MessageEvent) -> None:
    dat = event.raw_data
    msg = dat.get('content', None)
    if not isinstance(msg, str) or not msg.startswith(bot.prefix):
        return

    important = msg[len(bot.prefix):]
    args = important.split(' ', 1)
    # if not important == '':
    #     args = important.split(' ')
    if bot.has_command(args[0]):
        cmd = bot._commands[args[0]]
        await cmd(event)
    else:
        print(f"Command {cmd_str} doesn't exist")


################################
### CUSTOM COMMAND EXTENSION ###
################################


@bot.command
async def ping(ev):
    """Pong."""
    ctx = Context.from_event(ev)
    await ctx.channel.send('Dong')

@bot.command
async def shutdown(ev):
    """Shutdown le bot."""
    ctx = Context.from_event(ev)
    if ctx.author != bot.owner:
        await ctx.channel.send('bugger off then')
        return
    else:
        await ctx.channel.send('Shutting down.')
        await bot.close()

@bot.command
async def help(ev):
    """Shows this help message"""
    ctx = Context.from_event(ev)
    sorted_cmds = dict(sorted(bot._commands.items(), key=lambda x: x[0].lower()))

    table = f"| Command| Usage | Description |\n"
    table += "|-|-|-|\n"
    for name, cmd in sorted_cmds.items():
        table += f"| {name} | {cmd.signature} | {cmd.__doc__} \n"
    await ctx.channel.send(table)

##############
### PLUGIN ###
##############

from plugins._dev import Dev
bot.add_plugin(Dev(bot))

#############
### ENTRY ###
#############

asyncio.run(bot.start())
