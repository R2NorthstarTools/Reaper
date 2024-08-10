import discord
import util.json_handler
from discord.ext import commands


replies = True

# Embeds about global enabling/denying automatic replies for the bot
replieson = discord.Embed(title="Automatic bot replies set to ***ON***", color=0x287E29)
repliesoff = discord.Embed(
    title="Automatic bot replies set to ***OFF***", color=0xDC143C
)

# Embeds about the reply status of the bot
replystatusenabled = discord.Embed(
    title="Automatic bot replies are currently enabled", color=0x6495ED
)
replystatusdisabled = discord.Embed(
    title="Automatic bot replies are currently disabled", color=0xDC143C
)


def replycheck():
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
                await ctx.send(embed=replieson)
                print("Automatic bot replies are enabled")

            elif not replies:
                replies = False
                await ctx.send(embed=repliesoff)
                print("Automatic bot replies are disabled")
        else:
            await ctx.send(
                "You don't have permission to use this command!", ephemeral=True
            )

    # Displays the current status of replies across all servers
    @commands.hybrid_command(description="Displays if bot replies are on or off")
    async def replystatus(self, ctx):
        users = util.json_handler.load_users()
        neverusers = util.json_handler.load_neverusers()
        allowedchannels = util.json_handler.load_channels()

        if replies:
            if str(ctx.author.id) in neverusers:
                replystatusenabled.add_field(
                    name=f"{ctx.author.display_name}'s ability to control replies:",
                    value="Disabled",
                    inline=False,
                )
            if str(ctx.author.id) in users:
                replystatusenabled.add_field(
                    name=f"{ctx.author.display_name}'s automatic replies:",
                    value="Disabled",
                    inline=False,
                )
            if str(ctx.channel.id) in allowedchannels:
                replystatusenabled.add_field(
                    name="Automatic replies in this channel:", value="Enabled"
                )
            await ctx.send(embed=replystatusenabled, ephemeral=True)
            replystatusenabled.clear_fields()

        elif replies:
            if str(ctx.author.id) in neverusers:
                replystatusdisabled.add_field(
                    name=f"{ctx.author.display_name}'s ability to control replies:",
                    value="Disabled",
                    inline=False,
                )
            if str(ctx.author.id) in users:
                replystatusdisabled.add_field(
                    name=f"{ctx.author.display_name}'s automatic replies:",
                    value="Disabled",
                    inline=False,
                )
            if str(ctx.channel.id) in allowedchannels:
                replystatusdisabled.add_field(
                    name="Automatic replies in this channel:", value="Enabled"
                )
            await ctx.send(embed=replystatusdisabled, ephemeral=True)
            replystatusdisabled.clear_fields()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GlobalReplies(bot))
