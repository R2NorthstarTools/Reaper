import discord
from discord.ext import commands


class helpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Display information for using the bot")
    async def help(self, ctx):
        helpembed = discord.Embed(
            title="Spectre",
            description="Spectre is a bot created by Cyn (aka cooldudepugs) with major help from H0L0. Its purpose is to try to automatically solve issues that users have.",
            color=0x6495ED,
        )
        helpembed.add_field(name="", value="\u200b")
        helpembed.add_field(
            name="togglereplies",
            value="Toggles the bot replying to the person who used the command",
            inline=False,
        )
        helpembed.add_field(
            name="replystatus",
            value="Sends an embed about the status of replies for the user",
            inline=False,
        )
        helpembed.add_field(
            name="price",
            value="Shows the current price of Titanfall 2, and if it's on sale. Entering a region with a slash command allows you to search by region",
            inline=False,
        )
        helpembed.add_field(
            name="",
            value="You can view a full list of the commands on the [GitHub repo's wiki](https://github.com/itscynxx/Spectre/wiki)",
            inline=False,
        )
        await ctx.send(embed=helpembed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(helpCommand(bot))
