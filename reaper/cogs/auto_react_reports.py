import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import datetime
import discord
from discord.ext import commands
from util import globals


def check_fails_formatting_criteria(message_content: str) -> bool:

    # I fought regex and regex won, leaving in case someone wants to take a crack at it, this wasted around 15 minutes of fiddling
    # if not re.match(
    #     r"(?im)^name:\s*(.*?)\s*$^server:\s*(.*?)\s*$^reason:\s*(.*?)\s*$^evidence:\s*(.*?)\s*$",
    #     message.content,
    #     re.MULTILINE | re.IGNORECASE,
    # ):
    #     await message.author.send("regex didnt match")

    # This is my non regex attempt that worked on the first try and took a minute lol
    lines = message_content.split("\n")
    expected = ["name", "server", "reason", "evidence"]
    if len(lines) < len(expected):
        return True

    for i, line in enumerate(lines):
        if i >= len(expected):
            break
        if not line.lower().startswith(expected[i]):
            return True

    return False


class AutoReactReports(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.last_time = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        self.last_channel = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content:
            return

        if message.channel.id == globals.config["channels"]["report-users-channel-id"]:
            # This is to check if the message is a "Person started a thread" message
            if message.type == discord.MessageType.thread_created:
                return

            # There was a note here explaining the need for a sleep between each reaction add.
            # However, this works perfectly fine, and I have had another bot on the same library
            # do this with 10 emotes in a list work perfectly 100% of the time

            emotes = [
                "🔴",
                "🟠",
                "🟢",
            ]
            for emote in emotes:
                await message.add_reaction(emote)

            format_response_text = f"""
Thank you for your report ({message.jump_url}), please edit it to match this format:
```
Name:
Server:
Reason:
Evidence:
```
"""
        result = check_fails_formatting_criteria(message.content)
        print(f"{result=}")
        if result:
            await message.author.send(format_response_text)

        self.last_time = datetime.datetime.now(datetime.timezone.utc)
        self.last_channel = message.channel.id


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoReactReports(bot))
