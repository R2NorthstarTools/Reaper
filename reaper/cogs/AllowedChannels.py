import util.JsonHandler
from discord.ext import commands


class AllowedChannels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        description="Enables automatic replies for the current channel. Allowed users only."
    )
    async def togglechannel(self, ctx):
        allowed_users = util.JsonHandler.load_allowed_users()
        data = util.JsonHandler.load_channels()

        if str(ctx.author.id) in allowed_users:
            if str(ctx.channel.id) in data:
                del data[str(ctx.channel.id)]

                await ctx.send(
                    "Successfully disabled automatic replies in this channel!"
                )
            else:
                data[str(ctx.channel.id)] = f"{ctx.guild.name} - {ctx.channel.name}"

                await ctx.send(
                    "Successfully enabled automatic replies in this channel!"
                )

            util.JsonHandler.save_channels(data)
        else:
            await ctx.send(
                "You don't have permission to use this command", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AllowedChannels(bot))
