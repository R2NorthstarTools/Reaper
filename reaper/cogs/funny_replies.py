import logging

import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import discord
import util.json_handler
from discord.ext import commands

allowed_users = util.json_handler.load_allowed_users()


class FunnyReplies(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        description="Generates a search query link for NorthstarDocs based on search term"
    )
    async def ticks(self, ctx):
        await ctx.send(
            file=discord.File("assets/diag_reaper_fragdrone_launch_alert_2ch_v2_01.wav")
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FunnyReplies(bot))
