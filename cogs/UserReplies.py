import discord
import util.JsonHandler
from discord.ext import commands
from discord import app_commands

allowed_users = util.JsonHandler.load_allowed_users()


class UserReplies(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Slash command to disable replies for the user
    @commands.hybrid_command(
        description="Toggles replies for the user who uses the command"
    )
    async def togglereplies(self, ctx):
        data = util.JsonHandler.load_users()

        if str(ctx.author.id) in data:
            del data[str(ctx.author.id)]
            await ctx.send(
                "Succesfully enabled me automatically replying to your messages!",
                ephemeral=True,
            )

        else:
            data[str(ctx.author.id)] = f"{ctx.author.display_name}"
            await ctx.send(
                "Successfully disabled me automatically replying to your messages!",
                ephemeral=True,
            )

        util.JsonHandler.save_users(data)

    # Disable a user's automatic replies if they're being naughty :D
    @commands.hybrid_command(
        description="Disables reply toggling for selected user. Allowed users only."
    )
    @app_commands.describe(user="The user to disable reply toggling for")
    async def toggleuserreplies(self, ctx, user: discord.Member):
        data = util.JsonHandler.load_neverusers()

        if str(ctx.author.id) in allowed_users:
            if str(user.id) in data:
                del data[str(user.id)]

                await ctx.send(
                    f"Successfully enabled reply toggling for {user.name}!",
                    ephemeral=True,
                )

            else:
                data[str(user.id)] = "off"
                # This isn't very efficient but it works (I think)!
                await ctx.send(
                    f"Successfully disabled reply toggling for {user.name}!",
                    ephemeral=True,
                )

            util.JsonHandler.save_neverusers(data)
        else:
            await ctx.send(
                "You don't have permission to use this command!", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UserReplies(bot))
