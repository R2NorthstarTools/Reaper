import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import discord
from discord.ext import commands
from time import sleep


class TicketsAutoResponse(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        if not str(channel.name).startswith("ticket"):
            # Not a ticket channel, ignore
            return

        logger.info(
            f"Detected new channel created and classified as ticket channel: {channel.name}"
        )
        await channel.typing()
        sleep(3)
        await channel.send(
            """
I'm a bot automatically replying to the ticket being opened.

If you're having an issue with the Northstar client itself, please send a log so that I can try to automatically read it, or a human can read it better. You can do this by going to `Titanfall2/R2Northstar/logs` and sending the newest `nslog` you have.
Make sure not to send an `nsdmp`, and that you send the newest one! The newest ones are near the bottom by default on windows.

If I don't automatically respond, please wait for a human to assist. If you're getting an error MESSAGE in game, you could also try typing that out here, as I automatically reply to some of those as well.
"""
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TicketsAutoResponse(bot))
