import logging

import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import discord
import util.json_handler
from discord.ext import commands


replies = True

# Embeds about global enabling/denying automatic replies for the bot
replies_on_embed = discord.Embed(
    title="Automatic bot replies set to ***ON***", color=0x287E29
)
replies_off_embed = discord.Embed(
    title="Automatic bot replies set to ***OFF***", color=0xDC143C
)

# Embeds about the reply status of the bot
replystatusenabled = discord.Embed(
    title="Automatic bot replies are currently enabled", color=0x6495ED
)
replystatusdisabled = discord.Embed(
    title="Automatic bot replies are currently disabled", color=0xDC143C
)


def allow_replies():
    return replies


class GlobalReplies(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Enables replies across all servers
    @commands.hybrid_command(
        description="Globally enables Reaper replying to messages. Allowed users only."
    )
    async def toggleglobalreplies(self, ctx):
        allowed_users = util.json_handler.load_allowed_users()

        if str(ctx.author.id) in allowed_users:
            global replies

            if not replies:
                replies = True
                await ctx.send(embed=replies_on_embed)
                logger.info("Automatic bot replies are enabled")

            else:
                replies = False
                await ctx.send(embed=replies_off_embed)
                logger.info("Automatic bot replies are disabled")
        else:
            await ctx.send(
                "You don't have permission to use this command!", ephemeral=True
            )

    # Displays the current status of replies across all servers
    @commands.hybrid_command(description="Displays if bot replies are on or off")
    async def replystatus(self, ctx):
        users = util.json_handler.load_users()
        neverusers = util.json_handler.load_neverusers()
        allowedchannels = util.json_handler.load_allowed_channels()

        if replies:
            reply_status_embed = replystatusenabled
        else:
            reply_status_embed = replystatusdisabled

        if str(ctx.author.id) in neverusers:
            reply_status_embed.add_field(
                name=f"{ctx.author.display_name}'s ability to control replies:",
                value="Disabled",
                inline=False,
            )
        if str(ctx.author.id) in users:
            reply_status_embed.add_field(
                name=f"{ctx.author.display_name}'s automatic replies:",
                value="Disabled",
                inline=False,
            )
        if str(ctx.channel.id) in allowedchannels:
            reply_status_embed.add_field(
                name="Automatic replies in this channel:", value="Enabled"
            )
        await ctx.send(embed=reply_status_embed, ephemeral=True)
        reply_status_embed.clear_fields()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GlobalReplies(bot))
