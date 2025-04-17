import logging

import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import datetime
import re

import discord
import util.json_handler
import util.master_status
from cogs.global_replies import allow_replies
from discord.ext import commands
from util import globals

# Embed for automatically replying to potential questions about installing Northstar
installing = discord.Embed(
    description="I noticed that you may have asked for help installing Northstar. Please read the [installation channel](https://discordapp.com/channels/920776187884732556/922662496588943430) for ways to install Northstar",
    color=0x5D3FD3,
)

# Embed for help uninstalling Northstar
uninstalling = discord.Embed(
    description="I noticed that you may have asked for help uninstalling Northstar.\nIf you just want to play vanilla multiplayer, launch vanilla. If you added launch options to Steam or EA, removing them will launch vanilla.\n\nTo fully uninstall Northstar, simply deleting `Northstar.dll`, `NorthstarLauncher.exe`, and the `R2Northstar` folder from your Titanfall2 directory would effectively stop it from working.\n\nTo remove ALL related files, also delete `LEGAL.txt`, `r2ds.bat`, `wsock32.dll` from `Titanfall2/bin/x64_retail`, and `d3d11.dll`, `GFSDK_SSAO.win64.dll`, and `GFSDK_TXAA.win64.dll` from `Titanfall2/bin/x64_dedi`",
    color=0x5D3FD3,
)

# Embed for automatically replying to potential questions about a controller not working
controller = discord.Embed(
    description="I noticed you may have asked for help regarding a controller not working.",
    color=0x5D3FD3,
)
controller.add_field(
    name="\u200b",
    value="Try following the [controller not working](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#controller-not-working) wiki section for multiple ways you can fix a controller not working on Northstar.",
)

# Embed for automatically replying to potential questions about installing mods for Northstar
installmods = discord.Embed(
    description="I noticed that you may have asked for help installing mods. You can do this automatically or manually.",
    color=0x5D3FD3,
)
installmods.add_field(
    name="Automatic mod installation",
    value="Simply use a mod manager and navigate to the mods browser to automatically find and install mods.",
)
installmods.add_field(
    name="Manual mod installation",
    value="See the [manual mod installation section](https://docs.northstar.tf/Wiki/installing-northstar/manual-installation/#installing-northstar-mods-manually) of the wiki.",
)

# Embed for automatically replying to mentions of "Couldn't find player account"
playeraccount = discord.Embed(
    description='I noticed that you may have asked for help regarding the "Couldn\'t find player account" error. Please read the [wiki section for this issue](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#couldnt-find-player-accountinvalid-master-server-token) to solve the error.',
    color=0x5D3FD3,
)

# Embed for automatically replying to mentions of "What is Northstar?"
northstarInfo = discord.Embed(
    title="I noticed you may have asked a question about what Northstar is.",
    description="Northstar is a mod loader for Titanfall 2 with a focus on community server hosting and support for modding to replace models, sounds, textures, or even add new gamemodes. To install, you can check and read the [installation channel](https://discordapp.com/channels/920776187884732556/922662496588943430).",
)

# Embed for automatically replying to potential mentions of "Authentication Failed", meant to be enabled when the Master Server Northstar is run on is down
msdownembed = discord.Embed(
    title='I noticed you may have mentioned the error "Authentication Failed".',
    description="Currently, the master server Northstar's server browser operates on is down. This means that currently you can't connect and aren't alone in having the error. Please wait for the master server to come back up and continue to check [the annoucements channel](https://discord.com/channels/920776187884732556/920780605132800080) for more updates.",
    color=0x5D3FD3,
)

# Embed for letting users know the fastify error response doesn't matter if they aren't hosting a server
fastifyError = discord.Embed(
    title='I noticed you may have mentioned the "NO GAMESERVER RESPONSE"/"got fastify error response" error message while asking for help.',
    description="This error only applies if you are trying to host a server, in which case your ports likely aren't forwarded properly. If you aren't trying to host a server, your actual error is something else happening. Please look for other mentions of issues, or send a log.",
    color=0x5D3FD3,
)

# Embed for default EA stuff
ea = discord.Embed(
    title='I noticed you may have asked for help regarding the "Couldn\'t write log file!" error.',
    description="If you have the game installed on EA, please follow the [wiki section](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#cannot-write-log-file-when-using-northstar-on-ea-app) for solving this issue.",
    color=0x5D3FD3,
)

# Embed for first person animations
first_person_animations_embed = discord.Embed(
    title="I noticed you may have asked for about first person embark and execution animations",
    description="First person embark and execution animations are controlled server side for technical reasons set by the base game. In order to see them you need to join a server that has them enabled or create your own.",
    color=0x5D3FD3,
)


class AutoResponse(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.last_time = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        self.last_channel = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        users = util.json_handler.load_users()
        neverusers = util.json_handler.load_neverusers()
        enabledchannels = util.json_handler.load_allowed_channels()
        time_diff = (
            datetime.datetime.now(datetime.timezone.utc) - self.last_time
        ).total_seconds()

        if not message.guild:
            return

        if not (
            time_diff > globals.config["general"]["cooldowntime"]
            or message.channel.id != self.last_channel
        ):
            self.last_channel = message.channel.id
            logger.warning(
                "Tried to send message while on cooldown! Didn't send message!"
            )
            return

        if not allow_replies():
            return

        if str(message.author.id) in users:
            return

        if str(message.author.id) in neverusers:
            return

        if not (
            str(message.channel.id) in enabledchannels
            or str(message.channel.name).startswith("ticket")
        ):
            return

        # Should stop all bot messages
        if message.author.bot:
            return

        if re.search("player.*account", message.content.lower()):
            await message.channel.send(reference=message, embed=playeraccount)
            logger.info("Couldn't find player account embed reply sent")

        elif re.search("failed.creating log file", message.content.lower()):
            await message.channel.send(reference=message, embed=ea)
            logger.info("Default EA App directory embed reply sent")

        elif re.search("controller.not.working", message.content.lower()) or re.search(
            "can.i.use.controller.*northstar", message.content.lower()
        ):
            await message.channel.send(reference=message, embed=controller)
            logger.info("Controller embed reply sent")

        elif re.search("authentication.*failed", message.content.lower()) or re.search(
            "cant.*join", message.content.lower()
        ):
            if util.master_status.is_master_down():
                await message.channel.send(reference=message, embed=msdownembed)
            else:
                return

        elif re.search("how |help ", message.content.lower()) and re.search(
            "uninstall.northstar", message.content.lower()
        ):
            await message.channel.send(reference=message, embed=uninstalling)
            logger.info("Installing Northstar embed reply sent")

        elif re.search("how |help ", message.content.lower()) and re.search(
            "install.northstar", message.content.lower()
        ):
            await message.channel.send(reference=message, embed=installing)
            logger.info("Uninstalling Northstar embed reply sent")

        elif (
            re.search("how |help ", message.content.lower())
            and re.search("titanfall|northstar", message.content.lower())
            and re.search("install.*mods", message.content.lower())
        ):
            await message.channel.send(reference=message, embed=installmods)
            await message.channel.send(
                "https://cdn.discordapp.com/attachments/942391932137668618/1069362595192127578/instruction_bruh.png"
            )
            logger.info("Northstar mods installing embed reply sent")

        elif (
            re.search("(1st|first).person", message.content.lower())
            and re.search("mod|northstar|titanfall", message.content.lower())
            and re.search("animation|embark|embark", message.content.lower())
        ):
            await message.channel.send(
                reference=message, embed=first_person_animations_embed
            )
            logger.info("First person animations embed reply sent")

        self.last_time = datetime.datetime.now(datetime.timezone.utc)
        self.last_channel = message.channel.id


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoResponse(bot))
