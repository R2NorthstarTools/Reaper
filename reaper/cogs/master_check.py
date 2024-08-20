from discord.ext import commands
import util.master_status


class MasterCheck(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Check Northstar master server status")
    async def ms_status(self, ctx):
        if util.master_status.is_master_down() is True:
            await ctx.send("Master server is likely **DOWN**")
            return

        if util.master_status.is_master_down() is False:
            await ctx.send("Master server is **UP**")
            return

        await ctx.send("Reaper encountered an exception while talking to MS")
        return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MasterCheck(bot))
