import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import discord
from discord.ext import commands
import re
import requests
from util import globals

url = "https://api.github.com/graphql"
github_access_token = globals.config["tokens"]["github"]


def get_latest_discussion():
    headers = {"Authorization": f"Bearer {github_access_token}"}

    query = """
    query {
        repository(owner: "R2Northstar", name: "Northstar") {
            discussions(first: 1 categoryId: "DIC_kwDOGkM8Yc4CN-04") {
                edges {
                    node {
                        url
                        body
                    }
                }
            }
        }
    }
    """
    try:
        response = requests.post(url, json={"query": query}, headers=headers)
        if response.status_code == 200:
            raw_data = response.json()
        else:
            logger.error(f"GitHub API returned HTTP code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as err:
        logger.warn(f"GitHub API request failed: {err}")
        return None

    discussion_post = {
        "body": raw_data["data"]["repository"]["discussions"]["edges"][0]["node"][
            "body"
        ],
        "url": raw_data["data"]["repository"]["discussions"]["edges"][0]["node"]["url"],
    }

    return discussion_post


def get_latest_release_name():
    headers = {"Authorization": f"Bearer {github_access_token}"}

    try:
        response = requests.get(
            "https://api.github.com/repos/R2Northstar/NorthstarLauncher/releases",
            headers=headers,
        )

    except requests.exceptions.RequestException as err:
        logger.warn(f"GitHub API request failed: {err}")
        return None

    return response.json()[0]["tag_name"]


class PlayTesterPing(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        playtest_ping_channel = self.bot.get_channel(
            globals.config["channels"]["playtesters-channel-id"]
        )
        thunderstore_release_channel = self.bot.get_channel(
            globals.config["channels"]["thunderstore-releases-channel-id"]
        )

        if message.author == self.bot.user:
            return

        if message.channel == thunderstore_release_channel:
            if not message.embeds:
                return
            if (
                re.search(
                    r"NorthstarReleaseCandidate v\d+.\d+.\d+", message.embeds[0].title
                )
                and message.embeds[0].author.name == "northstar"
            ):
                data = get_latest_discussion()
                rc_version = get_latest_release_name()

                embed = discord.Embed(title="Changelog:", description=data["body"])

                embed.set_author(
                    name="Northstar " + rc_version,
                    icon_url="https://avatars.githubusercontent.com/u/86304187",
                )

                ping_message = await playtest_ping_channel.send(
                    f"""<@&936669179359141908>
There is a new Northstar release candidate, `{rc_version}`. If you find any issues or have feedback, please inform us in the thread attached to this message.
## **Installation**:
**If you have __not__ installed a release candidate before:**
Go to settings in FlightCore, and enable testing release channels. After you've done that, go to the play tab, click the arrow next to `LAUNCH GAME`, and select `Northstar release candidate`. Then, click the `UPDATE` button.

**If you have installed a release candidate before:**
Make sure your release channel is still set to `Northstar release candidate`, and click the `UPDATE` button.
## **Release Notes**:
<{data["url"]}>""",
                    embed=embed,
                )
                await ping_message.create_thread(name=rc_version)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlayTesterPing(bot))
