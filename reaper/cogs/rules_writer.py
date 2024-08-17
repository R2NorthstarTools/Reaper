import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import asyncio
import re
import requests
import util.json_handler
from discord.ext import commands


def grab_rules_from_repo():
    """Grabs the rules from the corresponding GitHub repo and extracts them from the Markdown document"""

    rules_link = "https://raw.githubusercontent.com/R2Northstar/NorthstarWiki/main/docs/other/moderation/rules.md"

    # Fetch the markdown file from the URL
    response = requests.get(rules_link)

    # Check if the request was successful
    if response.status_code != 200:
        logger.error(f"Failed to fetch the markdown file: {response.status_code}")
        raise Exception(f"Failed to fetch the markdown file: {response.status_code}")

    # Get the raw markdown content
    markdown_content = response.text

    # Regular expression to find the first code block
    code_block_pattern = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)

    # Search for the first code block
    match = code_block_pattern.search(markdown_content)

    if match:
        # Extract and return the content of the first code block
        return match.group(1).strip()
    else:
        return None  # No code block found


def split_into_sized_sections(input_string, limit=2000):
    sections = []
    current_section = ""

    # Split the input string into lines
    lines = input_string.split('\n')

    for line in lines:
        # Check if adding this line will exceed the limit
        if len(current_section) + len(line) + 1 > limit:  # +1 for the newline character
            # Save the current section and start a new one
            sections.append(current_section)
            current_section = line
        else:
            # Otherwise, add the line to the current section
            current_section += "\n" + line

    # Add the last section if exists
    if current_section:
        sections.append(current_section)

    return sections


def parse_rules():
    """
    Parses rules into individual sections.
    For now this is just based on newlines to avoid message size limit. In the future these sections could be separated based on more sophisticated logic to allow for embed messages etc
    """
    raw_rules = grab_rules_from_repo()

    parsed_rules = split_into_sized_sections(raw_rules)

    return parsed_rules


class RulesWriter(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Slash command to send the embeds for the installation channel
    @commands.hybrid_command(
        description="Pulls Discord rules from wiki and writes them to the channel the commmand is called from."
    )
    async def write_rules(
        self, ctx
    ):  # Yes, this gives an "Interaction failed" error. This is intended. This is so only the embeds show and no "x person used slash command" text appears
        allowed_users = util.json_handler.load_allowed_users()

        if not str(ctx.author.id) in allowed_users:
            await ctx.channel.send(
                "You don't have permission to use this command!", ephemeral=True
            )
            return

        # Get parsed rules
        parsed_rules = parse_rules()

        # Send them
        for section in parsed_rules:

            # Skip empty lines until they are fixed upstream
            if not section:
                continue

            await ctx.channel.send(section)
            await asyncio.sleep(0.5)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RulesWriter(bot))
