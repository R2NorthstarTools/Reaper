from discord.ext import commands
import urllib


class DocSearch(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        description="Generates a search query link for NorthstarDocs based on search term"
    )
    async def docsearch(self, ctx, *, query):
        query = query.replace(" ", "+")
        # convert special characters to link friendly format
        urllib.parse.quote_plus(query)
        await ctx.send(f"https://docs.northstar.tf/?q={query}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DocSearch(bot))
