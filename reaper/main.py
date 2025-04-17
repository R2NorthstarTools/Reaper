import logging

import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import os

import discord
import tomllib
from discord.ext import commands
from util import global_variables

# Load config into global var
with open("config.toml", "rb") as file:
    global_variables.config = tomllib.load(file)
    config = global_variables.config["general"]
    tokens = global_variables.config["tokens"]
import util.json_handler

if not os.path.exists("data"):
    os.makedirs("data")
util.json_handler.init_json()

allowed_users = util.json_handler.load_allowed_users()

COGS = (
    "cogs.allowed_channels",
    "cogs.allowed_users",
    "cogs.auto_react_reports",
    "cogs.auto_response",
    "cogs.doc_search",
    "cogs.global_replies",
    "cogs.help_command",
    "cogs.image_response",
    "cogs.install_channel_embed",
    "cogs.log_reading",
    "cogs.master_check",
    "cogs.mod_search",
    "cogs.playtester_ping_proxy",
    "cogs.playtester_ping_release_candidate",
    "cogs.price_check",
    "cogs.rules_writer",
    "cogs.sentiment_analyzer",
    "cogs.ticket_auto_response",
    "cogs.user_replies",
)
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
    for cog in COGS:
        await bot.load_extension(cog)
        logger.info(f"Loaded {cog}")


client = aclient()


# Slash command to update commands
@bot.hybrid_command(
    name="sync", description="Syncs the bot's commands. Allowed users only."
)
async def sync(ctx):
    if not (str(ctx.author.id) in allowed_users or ctx.author.id == bot.owner_id):
        await ctx.send("You don't have permission to use this command!", ephemeral=True)
        return

    await bot.tree.sync()
    logger.info("Commands synced successfully!")
    await ctx.send("Commands synced successfully!")


# Slash command to reload cogs
@bot.hybrid_command(
    name="reload", description="Reloads the bot's cogs. Allowed users only."
)
async def reload(ctx):
    if str(ctx.author.id) not in allowed_users:
        await ctx.send("You don't have permission to use this command!", ephemeral=True)
        return

    for cog in COGS:
        await bot.reload_extension(cog)
        logger.info(f"Reloaded {cog}")
    await ctx.send("Reloaded cogs succesfully!", ephemeral=True)


# Set the status for the bot
@bot.hybrid_command(description="Set the status of the bot. Allowed users only.")
async def setstatus(ctx, status: str):
    if str(ctx.author.id) not in allowed_users:
        await ctx.send("You don't have permission to use this command!", ephemeral=True)
        return

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=f"{status}")
    )
    await ctx.send(f"Set bot status to `Listening to {status}`!", ephemeral=True)


logger.info("Starting bot")
bot.run(tokens["discord"])
