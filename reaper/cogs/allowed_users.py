import typing

import discord
import util.json_handler
from discord import app_commands
from discord.ext import commands

allowed_users = util.json_handler.load_allowed_users()


class AllowedUsers(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        description="Removes a user from the allowed users list. Owner only."
    )
    @app_commands.describe(user="Toggle `user`'s ability to use specific bot commands")
    async def toggleusercommands(
        self,
        ctx,
        user: typing.Optional[discord.Member],
        role: typing.Optional[discord.Role],
    ):
        if ctx.author.id == self.bot.owner_id:
            if user is not None and role is not None:
                await ctx.send(
                    "Please only select either a user or a role to allow!",
                    ephemeral=True,
                )

            if user is not None:
                if str(user.id) in allowed_users:
                    del allowed_users[str(user.id)]
                    await ctx.send(
                        f"Successfully removed {user.name}'s ability to use bot commands!",
                        ephemeral=True,
                    )

                else:
                    allowed_users[str(user.id)] = user.display_name
                    await ctx.send(
                        f"Successfully allowed {user.name} to use bot commands!",
                        ephemeral=True,
                    )

            if role is not None:
                if str(role.id) in allowed_users:
                    del allowed_users[str(role.id)]
                    await ctx.send(
                        f"Succesfully remove {role.name}'s ability to use bot commands"
                    )

                else:
                    allowed_users[str(role.id)] = role.name
                    await ctx.send(
                        f"Successfully allowed {role.name} to use bot commands"
                    )

            else:
                await ctx.send(
                    "Please select either a user or a role to allow!", ephemeral=True
                )
                util.json_handler.save_allowed_users(allowed_users)

        else:
            await ctx.send(
                "You don't have permission to use this command!", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AllowedUsers(bot))
