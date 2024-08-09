from PIL import Image
import pytesseract
from discord.ext import commands
import re
import util.json_handler
import os
import discord


information_message = "Please note that I'm a bot automatically reading your image. There is a chance this information is wrong, in which case please ping @geckoeidechse"

vanillaPlus = discord.Embed(
    description="If you're using VanillaPlus, please make sure to read the instructions [on the mod page](https://northstar.thunderstore.io/package/NanohmProtogen/VanillaPlus/) (if you're updating from an older version, the steps have changed, so please read it again)\n\nIf you AREN'T using VanillaPlus, make sure you didn't disable any core mods. You can see if they're enabled or disabled in `R2Northstar/enabledmods.json`. Either change `false` to `true` on disabled core mods, or delete `enabledmods.json` and ALL mods will automatically enable",
    color=0x5D3FD3,
)
vanillaPlus.add_field(
    name="",
    value=information_message,
)

operationNotPermitted = discord.Embed(
    description="EA's default install directory has some issues associated with it, which can be solved by following the [wiki section about this error](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#cannot-write-log-file-when-using-northstar-on-ea-app)",
    color=0x5D3FD3,
)
operationNotPermitted.add_field(
    name="",
    value=information_message,
)

modFailedSanity = discord.Embed(
    description="The \"Mod failed sanity check\" error is specific to FlightCore, and means that the mod isn't properly formatted and FlightCore can't automatically install it. However, you can still follow the [manual mod install guide](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/manual-installation#installing-northstar-mods-manually) to install the mod you wanted.",
    color=0x5D3FD3,
)
modFailedSanity.add_field(
    name="",
    value=information_message,
)

logFile = discord.Embed(
    description='I noticed you encountered the "Failed creating log file!" error.\n\nPlease follow the [wiki section](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#cannot-write-log-file-when-using-northstar-on-ea-app) for solving this issue.',
    color=0x5D3FD3,
)
logFile.add_field(
    name="",
    value=information_message,
)

msvcp = discord.Embed(
    description='The "MSVCP120.dll" or "MSVCR120.dll" error comes up when you\'re missing a dependency Titanfall 2 uses to run. Follow the [wiki section for this issue](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#msvcr) to solve it.',
    color=0x5D3FD3,
)
msvcp.add_field(
    name="",
    value=information_message,
)

playeraccount = discord.Embed(
    description='Try following the guide on solving the "Couldn\'t find player account" and "Invalid master server token" errors [here](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#playeraccount)',
    color=0x5D3FD3,
)
playeraccount.add_field(
    name="",
    value=information_message,
)

originOffline = discord.Embed(
    description='Try following the guide on solving the "Origin Offline" and "Origin logged out" errors [here](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#origin-offline)',
    color=0x5D3FD3,
)
originOffline.add_field(
    name="",
    value=information_message,
)

scriptComp = discord.Embed(
    description="From this image alone, we can't see what's causing the issue. Please send a screenshot of the console (open it by hitting the `~` key), or send the newest log. You can find logs in `Titanfall2/R2Northstar/logs`, with the newest being on the bottom by default.",
    color=0x5D3FD3,
)
scriptComp.add_field(
    name="",
    value=information_message,
)


class imageStuff(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        channels = util.json_handler.load_channels()
        users = util.json_handler.load_users()

        if str(message.author.id) in users:
            return

        if str(message.channel.id) in channels or str(message.channel.name).startswith(
            "ticket"
        ):
            if message.attachments:

                if message.attachments[0].filename.endswith(
                    ".jpg"
                ) or message.attachments[0].filename.endswith(".png"):
                    await message.attachments[0].save("image.png")

                image = Image.open("image.png")
                text = pytesseract.image_to_string(image)
                print(text)

                if re.search(
                    "encountered.client.script.compilation.error", text.lower()
                ) and re.search("error|help", message.content.lower()):
                    await message.channel.send(embed=scriptComp, reference=message)

                elif re.search(
                    "invalid.or.expired.masterserver.token", text.lower()
                ) or re.search("couldn.find.player.account", text.lower()):
                    await message.channel.send(embed=playeraccount, reference=message)

                elif re.search("origin.offline", text.lower()) or re.search(
                    "origin_logged_out", text.lower()
                ):
                    await message.channel.send(embed=originOffline, reference=message)

                elif re.search("MSVCP120|MSVCR120", text.lower()):
                    await message.channel.send(embed=msvcp, reference=message)

                elif re.search("failed.creating.log.file", text.lower()):
                    await message.channel.send(embed=logFile, reference=message)

                # FlightCore specific errors
                elif re.search("mod.failed.sanity.check", text.lower()):
                    await message.channel.send(embed=modFailedSanity, reference=message)

                # Viper specific errors
                elif re.search("operation.not.permitted", text.lower()) and re.search(
                    "ea.games", text.lower()
                ):
                    await message.channel.send(
                        embed=operationNotPermitted, reference=message
                    )

                elif re.search(
                    "compile.error.undefined.variable", text.lower()
                ) and re.search("progression_getpreference", text.lower()):
                    await message.channel.send(embed=vanillaPlus, reference=message)

                os.remove("image.png")
                # is this bad? probably
                # does it work? also probably


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(imageStuff(bot))
