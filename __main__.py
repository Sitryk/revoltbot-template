import asyncio
from functools import partial
import json
import logging
import os
import pathlib
import time

# RICH TEXT FORMATTING
from rich.console import Console
from rich.pretty import Pretty
from rich.panel import Panel
from rich import print

from mutiny import Client, events

from ext.bot import Bot
from ext import errors
from ext import objects


logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("revoltbot.main")


#############
### SETUP ###
#############


_CONF_FILE = pathlib.Path(__file__).parent / "bot_config.json"
_CONFIG = None

## First time token and prefix input?
console = Console()

try:
    with open(_CONF_FILE, "r") as f:
        _CONFIG = json.load(f)
except FileNotFoundError:
    IN_TOKEN = input("Bot token: ")
    print("Use | to delimeter multiple prefixes")
    IN_PREFIXES = input("Bot prefixes: ").split("|")

    with open(_CONF_FILE, mode="w") as f:
        json.dump({"TOKEN": IN_TOKEN, "PREFIXES": IN_PREFIXES}, f)
    _TOKEN = IN_TOKEN
    _PREFIXES = IN_PREFIXES
except Exception as e:
    console.print_exception(show_locals=True)
    # print(e)
else:
    _TOKEN = _CONFIG["TOKEN"]
    _PREFIXES = _CONFIG["PREFIXES"]


bot = Bot(prefixes=_PREFIXES, token=_TOKEN)


# Listeners can be added by defining a single argument function
# decorated with `@client.listen()` and with its argument type-hinted
# with an appropriate event type:


@bot.listen()
async def on_ready(event: events.ReadyEvent) -> None:
    data = event.raw_data
    owner = objects.User(mutiny_object=await bot._ensure_user(bot.user.bot.owner_id))
    bot.owner = owner
    bot.init_time = time.time()

    n_text = 0
    n_voice = 0
    for channel in data["channels"]:
        if channel["channel_type"] == "TextChannel":
            n_text += 1
        elif channel["channel_type"] == "VoiceChannel":
            n_voice += 1

    startup_msg = [
        f"~~ Revolt.chat Bot, powered by Mutiny ~~",
        f"Hi, I'm {bot.user.username}",
        f"I belong to {owner.username} [{owner.id}]",
        f"Prefixes: {_PREFIXES}",
        "Connected to:",
        f"{len(data['servers'])} servers",
        f"{n_text} text channels",
        f"{n_voice} voice channels",
        f"Invite URL: https://app.revolt.chat/bot/{bot.user.id}",
    ]
    WIDTH = len(max(startup_msg, key=len))
    startup_msg = [s.center(WIDTH) for s in startup_msg]
    [startup_msg.insert(index, "-" * WIDTH) for index in (0, 2, len(startup_msg) + 2)]

    pretty = Pretty(bot._commands)
    panel = Panel(pretty)
    print(panel)
    print()
    print("\n".join(startup_msg))


@bot.listen()
async def on_message(event: events.MessageEvent) -> None:
    dat = event.raw_data
    # for now I'm going to start getting and fetching
    # users just to have them in state from the start
    try:
        user = bot.get_user(dat["author"])
    except KeyError:
        user = await bot.fetch_user(dat["author"])
    finally:
        if user:
            user = objects.User(mutiny_object=user)

    msg = dat.get("content", None)
    if not isinstance(msg, str):
        print(event)
        return

    # author is a bot
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
    p_ctx.channel = objects.TextChannel(mutiny_object=bot.get_channel(dat["channel"]))
    # cant inject this send function :(
    p_ctx.channel.send = partial(bot.send_to_channel, p_ctx.channel.id)
    p_ctx.author = user
    p_ctx.message = objects.Message(
        mutiny_object=event.message, author=p_ctx.author, content=msg, channel=p_ctx.channel
    )

    ctx = p_ctx
    # all commands take ctx oh well.
    ctx.command_args = [ctx, *ctx.command_args]
    try:
        await ctx.command(*ctx.command_args)
    except Exception as e:
        log.exception("Something went wrong:", exc_info=e)
        await ctx.channel.send(str(e))


################################
### CUSTOM COMMAND EXTENSION ###
################################


@bot.command()
async def help(ctx):
    """Shows this help message"""
    sorted_cmds = dict(sorted(bot._commands.items(), key=lambda x: x[0].lower()))

    table = f"| Command| Usage | Description |\n"
    table += "|-|-|-|\n"
    for name, cmd in sorted_cmds.items():
        if cmd.hidden:
            continue
        table += f"| {name} | {cmd.signature} | {cmd.__doc__} \n"
    await ctx.channel.send(table)


@bot.command()
async def load(ctx, plugin: str):
    """Load a plugin."""
    try:
        await bot.load_plugin(f"plugins.{plugin}")
    except errors.PluginError as e:
        await ctx.channel.send(f"Error: {e}")
    else:
        await ctx.channel.send(f"Loaded {plugin}.")


@bot.command()
async def unload(ctx, plugin: str):
    """Unload a plugin."""
    try:
        await bot.unload_plugin(plugin)
    except errors.PluginError as e:
        await ctx.channel.send(f"Error: {e}")
    else:
        await ctx.channel.send(f"Unloaded {plugin}.")


@bot.command()
async def reload(ctx, plugin: str):
    """Reload a plugin."""
    try:
        await bot.unload_plugin(plugin)
        await bot.load_plugin(f"plugins.{plugin}")
    except errors.PluginError as e:
        await ctx.channel.send(f"Error: {e}")
    else:
        await ctx.channel.send(f"Reloaded {plugin}.")


@bot.command()
async def plugins(ctx):
    """List all loaded plugins"""
    await ctx.channel.send("Loaded plugins:" + " , ".join(bot.plugins.keys()))


#############
### ENTRY ###
#############


async def main():
    try:
        await bot.start()
    finally:
        await bot.close()
        # give Windows's asyncio event loop some time to prevent RuntimeError...
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
