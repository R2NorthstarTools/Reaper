import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

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

        # Check whether command invoker has necessary roles and return early if they don't
        if not any(element.id in allowed_roles for element in ctx.author.roles):
            logger.info(
                f"{ctx.author.display_name} tried to ping playtesters but was lacking permissions to do so"
            )
            await ctx.send("Missing perms to ping playtesters", ephemeral=True)
            return

        playtester_role_id = globals.config["roles"]["playtester-role-id"]
        logger.info(f"{ctx.author.display_name} pinged playtesters")
        await ctx.send(f"<@&{playtester_role_id}>")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlayTesterPingProxy(bot))
