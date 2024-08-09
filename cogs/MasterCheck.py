from discord.ext import commands
import util.MasterStatus


class MasterCheck(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Check Northstar master server status")
    async def ms_status(self, ctx):
        if util.MasterStatus.IsMasterDown() is True:
            await ctx.send("Master server is likely **DOWN**")
            return
        elif util.MasterStatus.IsMasterDown() is False:
            await ctx.send("Master server is **UP**")
            return
        else:
            await ctx.send("Spectre encountered an exception while talking to MS")
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MasterCheck(bot))
