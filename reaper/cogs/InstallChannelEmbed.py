import discord
import util.JsonHandler
from discord.ext import commands

replies = True

# Embeds for the installation channel - Help mention
helpembed = discord.Embed(title="Having issues with Northstar?", color=0xFFF9AC)
helpembed.add_field(
    name="Troubleshooting issues with Northstar or installing Northstar",
    value="Check out the [FAQ](https://r2northstar.gitbook.io/r2northstar-wiki/faq) and [troubleshooting](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting) pages of the wiki for your error\n\nIf you can't find your error, feel free to open a ticket in the [help channel](https://discordapp.com/channels/920776187884732556/922663326994018366/1101924175343517827) by reading the embedded message and clicking the button to open a ticket",
)

# Embeds for the installation channel - Manual
manual = discord.Embed(
    title="Manual Installation",
    description="Note: Does not automatically update. You will have to do this every time Northstar has an update, and install mods and mod dependencies yourself\n",
    color=0xFF6969,
)
manual.add_field(
    name="\u200b",
    value="Download the newest `.zip` from the [releases page](https://github.com/R2Northstar/Northstar/releases/latest)\n\nFollow the [Manual installation guide](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/manual-installation)",
)

# Embeds for the installation channel - Automatic
installation = discord.Embed(
    title="Automatic Installation for Northstar (recommended)",
    description="Automatic updates and mod installation are also parts of mod managers",
    color=0x69FF69,
)
installation.add_field(
    name="FlightCore",
    value="Simple, easy to use mod manager and Northstar installer. Most stable mod manager.\n\nWorks on Windows and Linux, and is actively updated.\n\n[Download (Windows)](https://r2northstartools.github.io/FlightCore/index.html?win-setup)\n\n[Guide to setting up FlightCore](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/northstar-installers/flightcore-guide)",
    inline=True,
)
installation.add_field(
    name="VTOL",
    value="Advanced, feature rich mod manager and Northstar installer. Additionally very useful if you might want to make mods.\n\nWorks on Windows, and is actively updated.\n\n[Download (Windows)](https://github.com/BigSpice/VTOL/releases/latest/download/VTOL_Installer.msi)\n\n[Guide to setting up VTOL](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/northstar-installers/vtol-guide)",
    inline=True,
)
installation.add_field(
    name="Viper",
    value="Simple, easy to use mod manager and Northstar installer. Good when it works.\n\nWorks on Windows and Linux, and occasionally recieves bug fix updates.\n\n[Download (Windows)](https://0negal.github.io/viper/index.html?win-setup)\n\n[Guide to setting up Viper](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/northstar-installers/viper-guide)",
    inline=True,
)


class InstallationChannel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Slash command to send the embeds for the installation channel
    @commands.hybrid_command(
        description="Information for the #installation channel. Allowed users only."
    )
    async def installation(
        self, ctx
    ):  # Yes, this gives an "Interaction failed" error. This is intended. This is so only the embeds show and no "x person used slash command" text appears
        allowed_users = util.JsonHandler.load_allowed_users()

        if str(ctx.author.id) in allowed_users:
            await ctx.channel.send(embed=helpembed)
            await ctx.channel.send(embed=manual)
            await ctx.channel.send(embed=installation)

        else:
            await ctx.channel.send(
                "You don't have permission to use this command!", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InstallationChannel(bot))
