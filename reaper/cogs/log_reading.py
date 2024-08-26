import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import discord
from discord.ext import commands
import util.json_handler
from time import sleep
import requests
import shutil
import os
import re


def decodetext(text, text_to_filter, text_to_filter2):
    filtered_bytes = text.replace(b"\x82", b"")
    decoded_string = filtered_bytes.decode("utf-8")
    split_v2 = str(decoded_string)
    lines_split = split_v2.splitlines()
    new_text = ""
    for i in lines_split:
        if text_to_filter in i or text_to_filter2 in i:
            new_text = new_text + i + "\n"
    return new_text


def version_check():
    try:
        gh_api_response = requests.get(
            "https://api.github.com/repos/R2Northstar/Northstar/releases/latest"
        )
        if gh_api_response.status_code == 200:
            gh_data = gh_api_response.json()
        else:
            logger.warn(
                f"Error code when retrieving GitHub API: {gh_api_response.status_code}"
            )
    except requests.exceptions.RequestException as err:
        logger.warn(f"GitHub API request failed: {err}")
        return None

    ns_current_version = gh_data["name"][
        1:
    ]  # This gets the version as the raw version number without the "v". So '1.7.3' vs 'v1.7.3'
    return ns_current_version


audio_list = []
mod_split_list = []
mods_list = []
mods_list_disabled = []
mods_disabled_core = []

problem = discord.Embed(
    title="Problems I found in your log:", description="", color=0x5D3FD3
)
dm_log = discord.Embed(title="Somebody sent a log!", description="", color=0x5D3FD3)
old_log = discord.Embed(
    title="It looks like the log you've sent is older! Please send the newest one.",
    description="Windows puts the newest logs at the bottom of the logs folder due to how they're named.",
    color=0x5D3FD3,
)


class LogButtons(discord.ui.View):

    # note: disabled mods still appear in enabled list. dunno why
    @discord.ui.button(label="List of enabled mods", style=discord.ButtonStyle.success)
    async def mod_list(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        mod_string = ""
        for mod in mods_list:
            if mod + "\n" in mods_list_disabled:
                continue
            else:
                mod_string = mod_string + "- " + mod

        await interaction.response.send_message(
            f"The user has the following mods enabled: \n{mod_string}", ephemeral=True
        )

    @discord.ui.button(label="List of disabled mods", style=discord.ButtonStyle.red)
    async def mod_list_disabled(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        mod_string_disabled = ""
        for mod in mods_list_disabled:
            mod_string_disabled = mod_string_disabled + "- " + mod

        await interaction.response.send_message(
            f"The user has the following mods disabled: \n{mod_string_disabled}",
            ephemeral=True,
        )


class LogReading(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    @commands.Cog.listener()
    async def on_message(self, message):

        global hud
        global callback
        global compile_error_client_kill_callback
        global problem_found
        global audio_problem
        global rgb_error
        global framework_error
        global mods_installed
        global crash_counter
        global better_server_browser
        global old_version
        global disabled_core_mod
        hud = False
        callback = False
        compile_error_client_kill_callback = False
        problem_found = False
        audio_problem = False
        rgb_error = False
        framework_error = False
        bad_mod = ""
        mods_installed = False
        better_server_browser = False
        old_version = False
        disabled_core_mod = False
        crash_counter = 0

        view = LogButtons()

        allowed_channels = util.json_handler.load_allowed_channels()
        if message.author.bot:
            return

        if str(message.channel.id) in allowed_channels or str(
            message.channel.name
        ).startswith("ticket"):
            if message.attachments:
                filename = message.attachments[0].filename
                if "nslog" in filename and filename.endswith(".txt"):

                    mods_list.clear()
                    mods_list_disabled.clear()
                    mods_disabled_core.clear()

                    logger.info("Found a log!")
                    if not os.path.exists("Logs"):
                        os.mkdir("Logs")

                    await message.attachments[0].save("Logs/nslogunparsed.txt")
                    with open(r"Logs/nslogunparsed.txt", "r") as file:
                        lines = file.readlines()

                        for i, line in enumerate(lines):
                            if "NorthstarLauncher version:" in line:

                                ver_split = line.split("version:")[1]
                                if ver_split.strip() == "0.0.0.1+dev":
                                    return
                                elif ver_split.strip() < version_check():
                                    dm_log.add_field(
                                        name="",
                                        value=f"Version: {ver_split.strip()}",
                                        inline=False,
                                    )
                                    problem_found = True
                                    old_version = True

                            # Check mods

                            if "(DISABLED)" in line:
                                if (
                                    "Northstar.Client" in line
                                    or "Northtar.Custom" in line
                                    or "Northstar.CustomServers" in line
                                ):
                                    disabled_core_mod = True
                                    mods_disabled_core.append(line.split("'")[1])
                                logger.info(line.split("'")[1])
                                mods_list_disabled.append(line.split("'")[1])

                            if "blacklisted mod" in line:
                                mods_list_disabled.append(
                                    line.split('"')[1] + " (blacklisted)\n"
                                )

                            if "Loading mod" in line:

                                if "R2Northstar" in line:
                                    continue
                                else:
                                    for mod in mods_list_disabled:
                                        if mod + "\n" in line:
                                            continue
                                        else:
                                            mods_list.append(
                                                line.split("Loading mod")[1]
                                            )

                                # Check if HUD Revamp is installed: conflicts with Client Kill callback
                                if "HUD Revamp" in line:
                                    dm_log.add_field(
                                        name="",
                                        value="HUD Revamp: True",
                                        inline=False,
                                    )
                                    logger.info("I found HUD Revamp!")
                                    hud = True

                                # Check if Client Kill callback is installed: conflicts with HUD Revamp
                                if "ClientKillCallback" in line:
                                    dm_log.add_field(
                                        name="",
                                        value="Client Kill Callback: True",
                                        inline=False,
                                    )
                                    logger.info("I found Client Kill Callback!")
                                    problem_found = True
                                    callback = True

                                # Check if the OLD, merged better server browser is loading. It's broken now and causes issues
                                if "Better.Serverbrowser" in line:
                                    dm_log.add_field(
                                        name="",
                                        value="Better.Serverbrowser: True",
                                        inline=False,
                                    )
                                    logger.info("I found better server browser!")
                                    problem_found = True
                                    better_server_browser = True

                            # Check for a compile error for missing Client Kill callback as a dependency, or when there's a conflict with it
                            if (
                                'COMPILE ERROR expected ",", found identifier "inputParams"'
                                in line
                            ):
                                dm_log.add_field(
                                    name="",
                                    value="Client kill callback compile error: True",
                                    inline=False,
                                )
                                logger.info("I found a compile error!")
                                problem_found = True
                                compile_error_client_kill_callback = True

                            if (
                                'COMPILE ERROR Undefined variable "ModSettings_AddDropdown"'
                                in line
                            ):
                                dm_log.add_field(
                                    name="",
                                    value="Missing negativbild: True",
                                    inline=False,
                                )
                                logger.info("I found a person missing negativbild!")
                                problem_found = True
                                rgb_error = True

                            if (
                                'COMPILE ERROR Undefined variable "NS_InternalLoadFile"'
                                in line
                            ):
                                dm_log.add_field(
                                    name="",
                                    value="Titan Framework issue: True",
                                    inline=False,
                                )
                                logger.info("I found a titan framework issue >:(")
                                problem_found = True
                                framework_error = True

                            # Check for audio replacements being loaded
                            # If 2 seperate mods replacing the same audio are enabled at the same time the game fucking kills itself
                            if "Finished async read of audio sample" in line:

                                if "packages" in line:
                                    # Split the string after "R2Northstar/mods" to keep the folder name onwards
                                    a = line.split("R2Northstar\\packages")[1]
                                if "R2Northstar\\mods" in line:
                                    a = line.split("R2Northstar\\mods")[1]
                                # Split the previous split at "audio" to cleanly format as "FolderName, audioname"
                                # side note: why the fuck don't we use the mod name at all literally anywhere even when registering the audio fully
                                b = a.split("audio")
                                # Further clean up the last split
                                c = [item.split("\\")[1] for item in b]

                                # Add these to the audio list for checking for errors
                                audio_list.append(c)
                            # Checks for first line of the crash section of the log
                            if (
                                "[NORTHSTAR] [error] Northstar has crashed! a minidump has been written and exception info is available below:"
                                in line
                            ):
                                # Stores the previous line (right before the crash), we have to skip the version printout
                                checkLine = lines[i - 2]
                                crash_counter += 1
                                # More than 1 crash, flip multiCrash to true. Only needs to happen once so check for equality
                                # if crashCounter == 2:
                                #     multiCrash = True
                                # Check for paks being loaded right before crash, only search if one crash
                                if "LoadStreamPak" in checkLine and crash_counter == 1:
                                    mod_problem = True
                                    # Use regex to grab the name of the pak that probably failed
                                    match = re.search(
                                        r"LoadStreamPak: (\S+)", checkLine
                                    )
                                    global bad_stream_pak_load
                                    bad_stream_pak_load = str(match.group(1))
                                    problem_found = True

                                    # this shit is so fucking gross oh my fucking god
                                    # i am so sorry for what i did to your code tony
                                    for line_again in lines:
                                        if (
                                            f"registered starpak '{bad_stream_pak_load}'"
                                            in line_again
                                        ):

                                            match = re.search(
                                                r"Mod\s+(.*?)\s+registered",
                                                line_again,
                                            )
                                            bad_stream_pak_load = match.group(
                                                1
                                            )  # Store problematic mod in global var

                                    file.close()

                                    with open(r"Logs/nslogstarpaks.txt", "w") as file1:
                                        file1.write(
                                            f"Bad streampak: {bad_stream_pak_load}"
                                        )
                                        file1.close()

                                    with open(r"Logs/nslogstarpaks.txt", "r") as file2:
                                        lines = file2.readlines()

                                        for i, line in enumerate(lines):
                                            if "Bad streampak: " in line:
                                                bad_mod = line.split("Bad streampak: ")[
                                                    1
                                                ]

                                                # Run back over the log to find what mod the pak is registered with
                                                if bad_mod == "Northstar.Custom":
                                                    double_barrel_crash = True
                                                file2.close()
                                                break  # End the loop as it is no longer useful

                    # Properly set up the list for actual checking
                    d = list(set(tuple(audio) for audio in audio_list))

                    # Set up a list for checking duplicates
                    audio_duplicates_list = {}

                    for item in d:
                        # Grab the audio replacement string (e.g. "player_killed_indicator") and add it to a list to check directly for conflicts
                        audio_duplicate = item[1]

                        # If the audio override already in the list, add the mod name to the list
                        if audio_duplicate in audio_duplicates_list:
                            audio_duplicates_list[audio_duplicate].append(item[0])
                        else:
                            audio_duplicates_list[audio_duplicate] = [item[0]]

                    for audio_duplicate, names in audio_duplicates_list.items():
                        if len(names) > 1:
                            problem_found = True
                            logger.info(
                                f"Found duplicates of {audio_duplicate}: {', '.join(names)}"
                            )

                    if problem_found:
                        logger.info("Found problems in the log! Replying...")
                        await message.channel.typing()
                        sleep(5)

                        if disabled_core_mod:
                            disabled_core_string = ""

                            if len(mods_disabled_core) > 1:
                                if len(mods_disabled_core) == 2:
                                    for mod in mods_disabled_core:
                                        disabled_core_string = (
                                            disabled_core_string + mod
                                        )

                                problem.add_field(
                                    name="Disabled core mods",
                                    value=f"The core mods {disabled_core_string} are disabled! Please re-enable them using a mod manager or by deleting `Titanfall2/R2Northstar/enabledmods.json` (this only applies if trying to play Northstar. If you are playing vanilla via Northstar and encountering an issue, it is something else)",
                                    inline=False,
                                )

                            elif len(mods_disabled_core) == 1:
                                for mod in mods_disabled_core:
                                    disabled_core_string = disabled_core_string + mod
                                problem.add_field(
                                    name="Disabled core mod",
                                    value=f"The core mod {disabled_core_string} is disabled! Please re-enable it using a mod manager or by deleting `Titanfall2/R2Northstar/enabledmods.json` (this only applies if trying to play Northstar. If you are playing vanilla via Northstar and encountering an issue, it is something else)",
                                    inline=False,
                                )

                        if hud and callback and compile_error_client_kill_callback:
                            problem.add_field(
                                name="",
                                value="I noticed you have both HUD Revamp and Client Kill Callback installed. Currently, these two mods create conflicts. The easiest way to solve this is to delete/disable HUD Revamp.",
                                inline=False,
                            )

                        else:

                            if compile_error_client_kill_callback:
                                problem.add_field(
                                    name="Missing dependency!",
                                    value="One or more mods you have may require the mod [Client killcallback](https://northstar.thunderstore.io/package/S2Mods/KraberPrimrose/) to work. Please install or update the mod via a mod manager or Thunderstore.",
                                    inline=False,
                                )

                        if rgb_error:
                            problem.add_field(
                                name="Missing dependency!",
                                value="One or more mods you have may require the mod [Negativbild](https://northstar.thunderstore.io/package/odds/Negativbild/) to work. Please install or update this mod via a mod manager or Thundersore",
                            )

                        if framework_error:
                            problem.add_field(
                                name="Titan Framework",
                                value="Currently, Titan Framework expects a work in progress Northstar feature to function. As such, having it installed will cause issues (temporarily, until the feature is implemented), which uninstalling it will fix. You can temporarily make it work by manually installing the mod by moving the plugins inside the `plugins` folder of the mod into `r2northstar/plugins`, however this is a TEMPORARY fix, and you'll have to undo it when Northstar gets its next update.",
                                inline=False,
                            )

                        if better_server_browser:
                            problem.add_field(
                                name="Better server browser",
                                value='There are two mods called better server browser. The one called "Better.Serverbrowser" causes issues when installed, as it was added to Northstar a while ago. Removing it should fix that specific issue.',
                            )

                        for audio_duplicate, names in audio_duplicates_list.items():
                            if len(names) > 1:
                                audio_problem = True
                                problem.add_field(
                                    name="Audio replacement conflict",
                                    value=f"The following mods replace the same audio (`{audio_duplicate}`):\n {', '.join(names)}",
                                    inline=False,
                                )
                                dm_log.add_field(
                                    name="Audio replacement conflict",
                                    value=f"The following mods replace the same audio (`{audio_duplicate}`):\n {', '.join(names)}",
                                    inline=False,
                                )

                        if old_version:
                            problem.add_field(
                                name="Older Version",
                                value=f"It seems that you're running an older version of Northstar. Updating may not solve your issue, but you should do it anyway. The current version is {await version_check()}. Please update by using one of the methods in the [installation channel](https://discord.com/channels/920776187884732556/922662496588943430).",
                                inline=False,
                            )
                            problem.add_field(
                                name="\u200b",
                                value="If you've already updated and are still seeing this, please check if you have a file called `Northstar.dll` in `Titanfall2/R2Northstar`. If you do, delete it, and try launching again.",
                                inline=False,
                            )

                        if audio_problem:
                            problem.add_field(
                                name="Fixing audio replacement conflicts",
                                value="Please remove mods until only one of these audio mods are enabled. These names aren't perfect to what they are for the mod, however they are the file names for the mod, so you can just remove the folder matching the name from `Titanfall2/R2Northstar/mods`.",
                                inline=False,
                            )

                        if mod_problem:
                            if double_barrel_crash:

                                problem.add_field(
                                    name="Mod crashing",
                                    value="Northstar crashed right after loading the double barrel assets.\nPlease try deleting `w_shotgun_doublebarrel.mdl` from `Titanfall2/R2Northstar/mods/Northstar.Custom/mod/models/weapon/shotgun_doublebarrel`.\nDoing this will solve this specific crash, but will make you hold an error when trying to use the double barrel in game.",
                                )

                            else:

                                problem.add_field(
                                    name="Mod crashing",
                                    value=f"Northstar crashed right after attempting to load as asset from the mod `{bad_mod}`. Please try removing/disabling this mod to see if this solves the issue.",
                                )

                        problem.add_field(
                            name="",
                            value="Please note that I am a bot and am still heavily being worked on. There is a chance that some or all of this information is incorrect, in which case I apologize.\nIf you still encounter issues after doing this, please send another log.",
                            inline=False,
                        )
                        await message.channel.send(embed=problem, reference=message)

                        dm_me = await self.bot.fetch_user(self.bot.owner_id)

                        if len(problem.fields) > 0:
                            problem.add_field(
                                name="",
                                value="Please note that I am a bot and am still heavily being worked on. There is a chance that some or all of this information is incorrect, in which case I apologize.\nIf you still encounter issues after doing this, please send another log.",
                                inline=False,
                            )
                            await message.channel.send(
                                embed=problem, reference=message, view=view
                            )
                            dm_log.add_field(
                                name="I found an issue in the log and replied!",
                                value=f"A link to their log can be found here: {message.jump_url}",
                            )
                            await dm_me.send(embed=dm_log)
                        else:
                            await dm_me.send(
                                f"I failed to respond to a log! The log can be found here: {message.jump_url}"
                            )
                            await message.channel.send(
                                "I failed to respond to the log properly!"
                            )

                        dm_log.clear_fields()

                        audio_duplicates_list.clear()
                        audio_list.clear()
                        problem.clear_fields()
                        hud = False
                        callback = False
                        compile_error_client_kill_callback = False
                        problem_found = False
                        rgb_error = False
                        framework_error = False
                        better_server_browser = False
                        old_version = False
                        mod_problem = False
                        bad_mod = ""

                    elif not problem_found:
                        dm_me = await self.bot.fetch_user(self.bot.owner_id)
                        dm_log.add_field(
                            name="I didn't find any issues!",
                            value=f"Here's a log you could potentially train from: {message.jump_url}",
                        )
                        await dm_me.send(embed=dm_log)
                        dm_log.clear_fields()

                        logger.info("I didn't find any problems in the log!")

                    shutil.rmtree("Logs")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LogReading(bot))
