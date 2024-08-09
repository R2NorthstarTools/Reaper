import discord
import util.json_handler
from discord.ext import commands
import tomllib

COGS = (
    "cogs.allowed_channels",
    "cogs.allowed_users",
    "cogs.auto_response",
    "cogs.global_replies",
    "cogs.help_command",
    "cogs.image_response",
    "cogs.install_channel_embed",
    "cogs.log_reading",
    "cogs.master_check",
    "cogs.mod_search",
    "cogs.playtester_ping",
    "cogs.price_check",
    "cogs.user_replies",
)
INTENTS = discord.Intents.default()
INTENTS.message_content = True

with open("config.toml", "rb") as file:
    whole_config = tomllib.load(file)
    config = whole_config["general"]
    tokens = whole_config["tokens"]
allowed_users = util.json_handler.load_allowed_users()

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


client = aclient()


# Slash command to update commands
@bot.hybrid_command(
    name="sync", description="Syncs the bot's commands. Allowed users only."
)
async def sync(ctx):

    if str(ctx.author.id) in allowed_users or ctx.author.id == bot.owner_id:
        await bot.tree.sync()
        print("Commands synced successfully!")
        await ctx.send("Commands synced successfully!")
    else:
        await ctx.send("You don't have permission to use this command!", ephemeral=True)


# Slash command to reload cogs
@bot.hybrid_command(
    name="reload", description="Reloads the bot's cogs. Allowed users only."
)
async def reload(ctx):

    if str(ctx.author.id) in allowed_users:
        for cog in COGS:
            await bot.reload_extension(cog)
        print("Reloaded cogs successfully!")
        await ctx.send("Reloaded cogs succesfully!", ephemeral=True)
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


util.json_handler.init_json()
bot.run(tokens["discord"])
