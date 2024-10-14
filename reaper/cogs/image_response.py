import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

from PIL import Image
import pytesseract
from discord.ext import commands
import re
import util.json_handler
import io
import discord


information_message = "Please note that I'm a bot automatically reading your image. There is a chance this information is wrong, in which case please ping @geckoeidechse"
common_embed_color = 0x5D3FD3

vanilla_plus = discord.Embed(
    description="If you're using VanillaPlus, please make sure to read the instructions [on the mod page](https://northstar.thunderstore.io/package/NanohmProtogen/VanillaPlus/) (if you're updating from an older version, the steps have changed, so please read it again)\n\nIf you AREN'T using VanillaPlus, make sure you didn't disable any core mods. You can see if they're enabled or disabled in `R2Northstar/enabledmods.json`. Either change `false` to `true` on disabled core mods, or delete `enabledmods.json` and ALL mods will automatically enable",
    color=common_embed_color,
)
vanilla_plus.add_field(
    name="",
    value=information_message,
)

operation_not_permitted = discord.Embed(
    description="EA's default install directory has some issues associated with it, which can be solved by following the [wiki section about this error](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#cannot-write-log-file-when-using-northstar-on-ea-app)",
    color=common_embed_color,
)
operation_not_permitted.add_field(
    name="",
    value=information_message,
)

mod_failed_sanity = discord.Embed(
    description="The \"Mod failed sanity check\" error is specific to FlightCore, and means that the mod isn't properly formatted and FlightCore can't automatically install it. However, you can still follow the [manual mod install guide](https://docs.northstar.tf/Wiki/installing-northstar/manual-installation/#installing-northstar-mods-manually) to install the mod you wanted.",
    color=common_embed_color,
)
mod_failed_sanity.add_field(
    name="",
    value=information_message,
)

log_file = discord.Embed(
    description='I noticed you encountered the "Failed creating log file!" error.\n\nPlease follow the [wiki section](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#cannot-write-log-file-when-using-northstar-on-ea-app) for solving this issue.',
    color=common_embed_color,
)
log_file.add_field(
    name="",
    value=information_message,
)

msvcp = discord.Embed(
    description='The "MSVCP120.dll" or "MSVCR120.dll" error comes up when you\'re missing a dependency Titanfall 2 uses to run. Follow the [wiki section for this issue](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#msvcr120dll-msvcp120dll-not-found) to solve it.',
    color=common_embed_color,
)
msvcp.add_field(
    name="",
    value=information_message,
)

playeraccount = discord.Embed(
    description='Try following the guide on solving the "Couldn\'t find player account" and "Invalid master server token" errors [here](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#couldnt-find-player-accountinvalid-master-server-token)',
    color=common_embed_color,
)
playeraccount.add_field(
    name="",
    value=information_message,
)

origin_offline = discord.Embed(
    description='Try following the guide on solving the "Origin Offline" and "Origin logged out" errors [here](https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#origin-offlineorigin_logged_out)',
    color=common_embed_color,
)
origin_offline.add_field(
    name="",
    value=information_message,
)

script_comp = discord.Embed(
    description="From this image alone, we can't see what's causing the issue. Please send a screenshot of the console (open it by hitting the `~` key), or send the newest log. You can find logs in `Titanfall2/R2Northstar/logs`, with the newest being on the bottom by default.",
    color=common_embed_color,
)
script_comp.add_field(
    name="",
    value=information_message,
)

engine_error = discord.Embed(
    description="Found a screenshot showing 'Engine Error'. Uploading a log file might be useful to resolve this issue",
    color=common_embed_color,
)
engine_error.add_field(
    name="",
    value=information_message,
)

engine_error_device_hung = discord.Embed(
    description="Found a screenshot showing 'ERROR_DEVICE_HUNG'. Maybe try one of the fixes described here: https://www.getdroidtips.com/titanfall-2-dxgi-error-device-hung-error-fix/",
    color=common_embed_color,
)
engine_error_device_hung.add_field(
    name="",
    value=information_message,
)

engine_error_loaded_more_than_once = discord.Embed(
    description="Found a screenshot showing 'X is being loaded more than once from Y'. This is likely caused by a mod being installed multiple times or a faulty mod. Try disabling all mods except then `Northstar.XYZ` ones and see if the issue still persists.",
    color=common_embed_color,
)
engine_error_loaded_more_than_once.add_field(
    name="",
    value=information_message,
)

tcp_port_info = discord.Embed(
    description="Detect mention of a TCP port in the image. Should this be about forwarding then note that only the UDP port needs to forwarded. Forwarding TCP is no longer needed for hosting a Northstar server and has no effect since over a year.",
    color=common_embed_color,
)
tcp_port_info.add_field(
    name="",
    value=information_message,
)

flightcore_default_titanfall_ea_default_path = discord.Embed(
    description="Detected FlightCore error message with mention of default install path for Titanfall2 using EA App.\nUsing the instructions provided in the following link might resolve your issue: https://docs.northstar.tf/Wiki/installing-northstar/troubleshooting/#cannot-write-log-file-when-using-northstar-on-ea-app",
    color=common_embed_color,
)
flightcore_default_titanfall_ea_default_path.add_field(
    name="",
    value=information_message,
)

flightcore_tauri_ipc_error = discord.Embed(
    description="Detected FlightCore error message with mention of `_TAURI_IPC_` error\nTry restarting FlightCore to resolve the error. If that doesn't work, please make an issue on [GitHub](<https://github.com/R2NorthstarTools/FlightCore/issues>) or ping `@geckoeidechse`",
    color=common_embed_color,
)
flightcore_tauri_ipc_error.add_field(
    name="",
    value=information_message,
)


async def handle_response(text: str, message):
    if re.search(
        "encountered.client.script.compilation.error", text.lower()
    ) and re.search("error|help", message.content.lower()):
        await message.channel.send(embed=script_comp, reference=message)
        return

    if re.search("invalid.or.expired.masterserver.token", text.lower()) or re.search(
        "couldn.find.player.account", text.lower()
    ):
        await message.channel.send(embed=playeraccount, reference=message)
        return

    if re.search("origin.offline", text.lower()) or re.search(
        "origin_logged_out", text.lower()
    ):
        await message.channel.send(embed=origin_offline, reference=message)
        return

    if re.search("MSVCP120|MSVCR120", text.lower()):
        await message.channel.send(embed=msvcp, reference=message)
        return

    if re.search("failed.creating.log.file", text.lower()):
        await message.channel.send(embed=log_file, reference=message)
        return

    # FlightCore specific errors
    if re.search("mod.failed.sanity.check", text.lower()):
        await message.channel.send(embed=mod_failed_sanity, reference=message)
        return

    # Viper specific errors
    if re.search("operation.not.permitted", text.lower()) and re.search(
        "ea.games", text.lower()
    ):
        await message.channel.send(embed=operation_not_permitted, reference=message)
        return

    if re.search("compile.error.undefined.variable", text.lower()) and re.search(
        "progression_getpreference", text.lower()
    ):
        await message.channel.send(embed=vanilla_plus, reference=message)
        return

    if re.search("engine.error", text.lower()):
        if re.search("error_device_hung", text.lower()):
            await message.channel.send(
                embed=engine_error_device_hung, reference=message
            )
            return

        if re.search("is.being.loaded.more.than.once.from", text.lower()):
            await message.channel.send(
                embed=engine_error_loaded_more_than_once, reference=message
            )
            return

        await message.channel.send(embed=engine_error, reference=message)
        return

    if re.search("tcp|top", text.lower()) and re.search("808.", text.lower()):
        await message.channel.send(embed=tcp_port_info, reference=message)
        return

    if (
        re.search("flightcore", text.lower())
        and re.search("cannot.install.to.default.ea.app.install.path.", text.lower())
        and re.search("move.titanfall", text.lower())
    ):
        await message.channel.send(
            embed=flightcore_default_titanfall_ea_default_path, reference=message
        )
        return

    # TypeError: window._TAURI_IPC_is not a function
    if (
        re.search("typeerror", text.lower())
        and re.search("tauri", text.lower())
        and re.search("ipc", text.lower())
    ):
        await message.channel.send(embed=flightcore_tauri_ipc_error, reference=message)
        return


class imageStuff(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        allowed_channels = util.json_handler.load_allowed_channels()
        users = util.json_handler.load_users()

        if str(message.author.id) in users:
            return

        if not message.guild:
            return

        if not (
            str(message.channel.id) in allowed_channels
            or str(message.channel.name).startswith("ticket")
        ):
            return

        if not message.attachments:
            return

        for current_message_attachment in message.attachments:
            if not (
                current_message_attachment.filename.endswith(".jpg")
                or current_message_attachment.filename.endswith(".png")
            ):
                continue

            image_data = await current_message_attachment.read()

            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image)
            logger.info(text)

            await handle_response(text, message)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(imageStuff(bot))
