import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import discord
from discord.ext import commands
import util.json_handler
import requests
import re
import io


async def version_check():
    try:
        gh_api_response = requests.get(
            "https://api.github.com/repos/R2Northstar/Northstar/releases/latest"
        )
        if gh_api_response.status_code == 200:
            gh_data = gh_api_response.json()
        else:
            logger.error(
                f"Error code when retrieving GitHub API: {gh_api_response.status_code}"
            )
            return None
    except requests.exceptions.RequestException as err:
        logger.error(f"GitHub API request failed: {err}")
        return None

    ns_current_version = gh_data["name"][1:]
    # This gets the version as the raw version number without the "v". So '1.7.3' vs 'v1.7.3'
    return ns_current_version


class Mod:
    def __init__(
        self,
        name: str,
        version: str,
        core: bool = False,
        enabled: bool = True,
        blacklisted: bool = False,
    ):
        self.name = name
        self.version = version
        self.core = core
        self.enabled = enabled
        self.blacklisted = blacklisted

    def __str__(self):
        if self.version:
            if self.blacklisted:
                return f"{self.name} - {self.version} - Blacklisted"
            elif self.core:
                return f"{self.name} - {self.version} - Core"
            else:
                return f"{self.name} - {self.version}"
        return self.name


class LogButtons(discord.ui.View):

    def __init__(self, mods):
        super().__init__()
        self.mods = mods
        self.timeout = None  # make buttons last forever

    @discord.ui.button(label="List of enabled mods", style=discord.ButtonStyle.success)
    async def mod_list(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        mod_string = ""
        for mod in self.mods:
            if mod.enabled:
                mod_string += str(mod) + "\n"

        if len(mod_string) > 2000:  # Discord message limit
            mod_string = mod_string[:1997] + "..."

        if mod_string == "":
            mod_string = "No enabled mods found"

        await interaction.response.send_message(mod_string, ephemeral=True)

    @discord.ui.button(label="List of disabled mods", style=discord.ButtonStyle.red)
    async def mod_list_disabled(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        mod_string = ""
        for mod in self.mods:
            if not mod.enabled:
                mod_string += str(mod) + "\n"

        if len(mod_string) > 2000:  # Discord message limit
            mod_string = mod_string[:1997] + "..."

        if mod_string == "":
            mod_string = "No disabled mods found"

        await interaction.response.send_message(mod_string, ephemeral=True)


class LogReading(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        allowed_channels = util.json_handler.load_allowed_channels()
        if message.author.bot:
            return
        if str(message.channel.id) not in allowed_channels and not str(
            message.channel.name
        ).startswith("ticket"):
            return
        problem = discord.Embed(
            title="Problems I found in your log:", description="", color=0x5D3FD3
        )
        dm_log = discord.Embed(
            title="Somebody sent a log!", description="", color=0x5D3FD3
        )

        log_file = io.BytesIO()
        if message.attachments:
            for attachment in message.attachments:
                if (
                    attachment.filename.endswith(".txt")
                    and "nslog" in attachment.filename
                ):
                    await attachment.save(log_file)
                    logger.info("Found a log!")
                    break
            else:
                return
        else:
            return
        log_file.seek(0)
        lines = []
        for line in log_file:
            lines.append(line.decode("utf-8").strip())
        log = "\n".join(lines)

        mods = []

        northstar_match = re.search(r"NorthstarLauncher version: \s*(.*)", log)
        if northstar_match:
            version_number = northstar_match.group(1).strip()[:-2]
            latest_version = await version_check()
            if version_number == "0.0.0.1+dev":
                return
            if latest_version.strip() > version_number:
                problem.add_field(
                    name="Outdated Northstar Version",
                    value=f"It seems that you're running an older version of Northstar ({version_number}). Updating may not solve your issue, but you should do it anyway. The current version is {latest_version}. Please update by using one of the methods in the [installation channel](https://discord.com/channels/920776187884732556/922662496588943430).\n\nIf you've already updated and are still seeing this, please check if you have a file called `Northstar.dll` in `Titanfall2/R2Northstar`. If you do, delete it, and try launching again.",
                    inline=False,
                )
                dm_log.add_field(
                    name="Outdated Northstar Version",
                    value=f"Their version: {version_number}",
                    inline=False,
                )

        # Check if core mods disabled, mod checking
        mod_matches = re.finditer(
            r"'([^']*)' loaded successfully, version (\d+\.\d+\.\d+)( \(DISABLED\))?",
            log,
        )
        disabled_core_mods = []
        if mod_matches:
            for mod_match in mod_matches:
                name = mod_match.group(1)
                version = mod_match.group(2)
                disabled = bool(mod_match.group(3))
                core = False
                if name in [
                    "Northstar.Client",
                    "Northstar.Custom",
                    "Northstar.CustomServers",
                ]:
                    core = True
                if disabled and core:
                    disabled_core_mods.append(name)
                mods.append(Mod(name, version, core=core, enabled=not disabled))
                # TODO: blacklisted mods, might not be worth it since its like never used

        if len(disabled_core_mods) > 0:
            problem.add_field(
                name="Disabled core mods:",
                value=f"The core mods {', '.join(disabled_core_mods)} are disabled! Please re-enable them using a mod manager or by deleting `Titanfall2/R2Northstar/enabledmods.json` (this only applies if trying to play Northstar. If you are playing vanilla via Northstar and encountering an issue, this does not apply)",
                inline=False,
            )
            dm_log.add_field(
                name="Goober turned off core mods",
                value=f"Core mods that are disabled: {', '.join(disabled_core_mods)}",
                inline=False,
            )

        # Compile errors
        compile_search = re.search(r"COMPILE ERROR\s*(.*)", log)
        if compile_search:
            details = compile_search.group(1)
            if 'expected ",", found indentifier "inputParams"' in details:
                hud = False
                callback = False
                # its ok to check the mods now because all of the mods will have been loaded at this point
                for mod in mods:
                    if mod.name == "HUD Revamp":
                        hud = True
                    if mod.name == "ClientKillCallback":
                        callback = True
                if hud and callback:  # TODO: is this still true?
                    problem.add_field(
                        name="Mod Incompatibility",
                        value="I noticed you have both HUD Revamp and Client Kill Callback installed. Currently, these two mods create conflicts. The easiest way to solve this is to delete/disable HUD Revamp.",
                        inline=False,
                    )
                    dm_log.add_field(
                        name="Mod Incompatibility",
                        value="HUD Revamp",
                        inline=False,
                    )
                else:
                    problem.add_field(
                        name="Missing dependency!",
                        value="One or more mods you have may require the mod [Client killcallback](https://northstar.thunderstore.io/package/S2Mods/KraberPrimrose/) to work. Please install or update the mod via a mod manager or Thunderstore.",
                        inline=False,
                    )
                    dm_log.add_field(
                        name="Missing dependency!",
                        value="Client killcallback",
                        inline=False,
                    )
            elif 'Undefined variable "ModSettings_AddDropdown"' in details:
                problem.add_field(
                    name="Missing dependency!",
                    value="One or more mods you have may require the mod [Negativbild](https://northstar.thunderstore.io/package/odds/Negativbild/) to work. Please install or update this mod via a mod manager or Thundersore",
                    inline=False,
                )
                dm_log.add_field(
                    name="Missing dependency!",
                    value="Negativbild",
                    inline=False,
                )
            elif (
                'COMPILE ERROR Undefined variable "NS_InternalLoadFile"' in details
            ):  # TODO: check if this is still needed
                problem.add_field(
                    name="Titan Framework",
                    value="Currently, Titan Framework expects a work in progress Northstar feature to function. As such, having it installed will cause issues (temporarily, until the feature is implemented), which uninstalling it will fix. You can temporarily make it work by manually installing the mod by moving the plugins inside the `plugins` folder of the mod into `r2northstar/plugins`, however this is a TEMPORARY fix, and you'll have to undo it when Northstar gets its next update.",
                    inline=False,
                )
                dm_log.add_field(
                    name="Titan Framework",
                    value="",
                    inline=False,
                )
            else:
                problem.add_field(
                    name="Unknown compile error",
                    value=f"`{details}`\nOne or more of your mods are either broken, clashing, or incompatible. Try removing any mods you added recently or check if they require any dependencies. Please wait for a human to assist you further.",
                    inline=False,
                )
                dm_log.add_field(
                    name="Unknown compile error",
                    value=f"`{details}`",
                    inline=False,
                )
        if re.match(
            r'.*Failed reading masterserver authentication response: encountered parse error "Invalid value.".*',
            log,
            re.DOTALL,
        ):

            dm_log.add_field(
                name="",
                value="Cloudflare issue: True",
                inline=False,
            )
            problem.add_field(
                name="Server setup error",
                value="If you are trying to setup a server, you likely made an error while setting it up. Please double check your port forwarding and try again.",
                inline=False,
            )
        script_error_match = re.search(r"SCRIPT ERROR: (.*)", log)
        if script_error_match:
            details = script_error_match.group(1)
            dm_log.add_field(
                name="",
                value="SCRIPT ERROR: True",
                inline=False,
            )
            problem.add_field(
                name="Script Error",
                value=f"`{details}`\nYou likely have a broken or incompatible mod, please wait for a human to assist you further.",
                inline=False,
            )

        # Audio can be loaded under /packages or /mods so its easier to have two regexes
        audio_matches_case1 = re.findall(
            r"Finished async read of audio sample R2Northstar\\packages\\([^\\]+)\\mods\\[^\\]+\\audio\\([^\\]+)",
            log,
        )

        audio_matches_case2 = re.findall(
            r"Finished async read of audio sample R2Northstar\\mods\\([^\\]+)\\audio\\([^\\]+)",
            log,
        )

        loaded_audio = {}
        for mod_folder, audio_folder in audio_matches_case1 + audio_matches_case2:
            if audio_folder not in loaded_audio:
                loaded_audio[audio_folder] = []
            if mod_folder not in loaded_audio[audio_folder]:
                loaded_audio[audio_folder].append(mod_folder)

        audio_conflicts = []
        for audio_folder, mod_folders in loaded_audio.items():
            if len(mod_folders) > 1:
                audio_conflicts.append(audio_folder)

        if audio_conflicts:

            formatted_conflicts = ""
            for audio_conflict in audio_conflicts:
                formatted_conflicts += f"The following mods are replacing the same audio (`{audio_conflict}`):\n"
                formatted_conflicts += ", ".join(loaded_audio[audio_conflict]) + "\n"

            dm_log.add_field(
                name="",
                value="Duplicate audio found!",
                inline=False,
            )
            problem.add_field(
                name="Duplicate audio",
                value=f"{formatted_conflicts}\nThese mods have conflicting audio replacements. It's possible that this might be causing your crash.",
                inline=False,
            )

        view = LogButtons(mods)
        dm_me = await self.bot.fetch_user(self.bot.owner_id)

        if problem.fields:
            problem.add_field(
                name="",
                value="Please note that I am a bot and am still heavily being worked on. There is a chance that some or all of this information is incorrect, in which case I apologize.\nIf you still encounter issues after doing this, please send another log.",
                inline=False,
            )
        else:
            problem.add_field(
                name="No common issues found!",
                value="While waiting for a human to help you, consider the following:\n- Have you recently added any mods?\n- Does this issue persist when you disable all of your mods?",
            )
        await message.reply(embed=problem, view=view)
        if dm_log.fields:
            dm_log.add_field(
                name="I found an issue in the log and replied!",
                value=f"A link to their log can be found here: {message.jump_url}",
            )
        else:
            dm_log.add_field(
                name="I didn't find any issues in a log!",
                value=f"Here's a log you can train from: {message.jump_url}",
            )
        await dm_me.send(embed=dm_log)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LogReading(bot))
