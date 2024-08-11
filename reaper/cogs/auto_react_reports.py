import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import datetime
import discord
from discord.ext import commands
from cogs.global_replies import replycheck
from util import globals


class AutoReactReports(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.last_time = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        self.last_channel = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        time_diff = (
            datetime.datetime.now(datetime.timezone.utc) - self.last_time
        ).total_seconds()

        if not (
            time_diff > globals.config["general"]["cooldowntime"]
            or message.channel.id != self.last_channel
        ):
            self.last_channel = message.channel.id
            logger.warn("Tried to send message while on cooldown! Didn't send message!")
            return

        if replycheck():
            if (
                message.channel.id
                == globals.config["channels"]["report-users-channel-id"]
            ):
                # This is to check if the message is a "Person started a thread" message
                if message.type != discord.MessageType.thread_created:

                    # There was a note here explaining the need for a sleep between each reaction add.
                    # However, this works perfectly fine, and I have had another bot on the same library
                    # do this with 10 emotes in a list work perfectly 100% of the time

                    emotes = [
                        "🔴",
                        "🟠",
                        "🟢",
                    ]
                    for emote in emotes:
                        await message.add_reaction(emote)

            self.last_time = datetime.datetime.now(datetime.timezone.utc)
        self.last_channel = message.channel.id


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoReactReports(bot))
