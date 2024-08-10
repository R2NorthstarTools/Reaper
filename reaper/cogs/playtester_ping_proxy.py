from discord.ext import commands
from util import globals


class PlayTesterPingProxy(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Command to ping playtesters
    @commands.hybrid_command(
        name="playtester_ping",
        description="Ping playtesters (requires one of modder/contributor/helper/moderator roles)",
    )
    async def playtester_ping(self, ctx):

        allowed_roles = set(globals.config["roles"]["ping-privileged-role-ids"])

        # Check whether command invoker has necessary roles
        if any(element.id in allowed_roles for element in ctx.author.roles):
            playtester_role_id = globals.config["roles"]["playtester-role-id"]
            await ctx.send(f"<@&{playtester_role_id}>")
        else:
            await ctx.send("Missing perms to ping playtesters", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlayTesterPingProxy(bot))
