import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import discord
from discord.ext import commands
import os
import tomllib
from util import globals

# Load config into global var
with open("config.toml", "rb") as file:
    globals.config = tomllib.load(file)
    config = globals.config["general"]
    tokens = globals.config["tokens"]
import util.json_handler

if not os.path.exists("data"):
    os.makedirs("data")
util.json_handler.init_json()

allowed_users = util.json_handler.load_allowed_users()

INTENTS = discord.Intents.default()
INTENTS.message_content = True


# Config docs
# [general]
# "admin": <admin id>
# "prefix": "$"
# "cooldowntime": <cooldown seconds>
# "noreplylist": <name of list.json>
# "neverreplylist": <name of neverreplylist.json>
# "allowedchannels": <name of list.json>
# "allowedusers": <name of alloweduserslist.json>
#

bot = commands.Bot(
    intents=INTENTS, command_prefix=config["prefix"], owner_id=config["admin"]
)

bot.remove_command("help")


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())

    async def on_ready(self):
        await self.wait_until_ready()


@bot.event
async def setup_hook() -> None:
    for filename in os.listdir("./reaper/cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


client = aclient()


# Slash command to update commands
@bot.hybrid_command(
    name="sync", description="Syncs the bot's commands. Allowed users only."
)
async def sync(ctx):

    if str(ctx.author.id) in allowed_users or ctx.author.id == bot.owner_id:
        await bot.tree.sync()
        logger.info("Commands synced successfully!")
        await ctx.send("Commands synced successfully!")
    else:
        await ctx.send("You don't have permission to use this command!", ephemeral=True)


# Slash command to reload cogs
@bot.hybrid_command(
    name="reload", description="Reloads the bot's cogs. Allowed users only."
)
async def reload(ctx, cog):

    if str(ctx.author.id) in allowed_users:
        await bot.reload_extension(f"cogs.{cog}")
        logger.info(f"Reloaded {cog} successfully!")
        await ctx.send(f"Reloaded {cog} succesfully!", ephemeral=True)
    else:
        await ctx.send("You don't have permission to use this command!", ephemeral=True)


# Set the status for the bot
@bot.hybrid_command(description="Set the status of the bot. Allowed users only.")
async def setstatus(ctx, status: str):

    if str(ctx.author.id) in allowed_users:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name=f"{status}"
            )
        )
        await ctx.send(f"Set bot status to `Listening to {status}`!", ephemeral=True)
    else:
        await ctx.send("You don't have permission to use this command!", ephemeral=True)


logger.info("Starting bot")
bot.run(tokens["discord"])
