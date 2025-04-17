import logging

import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import asyncio
import re
from typing import Optional

import discord
import requests
from discord import app_commands
from discord.ext import commands


class PaginationView(discord.ui.View):
    current_page: int = 0

    async def send(self, ctx):
        self.message = await ctx.send(
            embed=self.create_embed(self.data, self.data_key), view=self
        )

    def create_embed(self, data, data_key):
        key = self.data_key[self.current_page]
        mod = self.data[key]
        mod_embed_desc = f"By {mod['owner']}\n{mod['description']}"
        embed_title = f"{mod['name']} ({self.current_page + 1}/{len(self.data_key)})"
        embed_footer = f"{mod['total_dl']} Downloads | Last updated on {mod['last_update']} (YY/MM/DD)"
        embed = discord.Embed(title=embed_title, description=mod_embed_desc)
        embed.set_thumbnail(url=mod["icon_url"])
        embed.set_footer(text=embed_footer)
        self.mod_url = mod["ts_url"]
        return embed

    async def update_message(self, data, data_key):
        await self.message.edit(embed=self.create_embed(data, data_key), view=self)

    @discord.ui.button(label="View Mod", style=discord.ButtonStyle.success)
    async def link_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(self.mod_url, ephemeral=True)

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.primary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        self.current_page = (self.current_page - 1) % len(self.data_key)
        await self.update_message(self.data, self.data_key)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        self.current_page = (self.current_page + 1) % len(self.data_key)
        await self.update_message(self.data, self.data_key)


class ModSearch(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Search Northstar Thunderstore for mods")
    @app_commands.choices(
        method=[
            app_commands.Choice(name="Mod name", value="name"),
            app_commands.Choice(name="Mod author", value="owner"),
        ]
    )
    async def modsearch(
        self, ctx, search_string: str, method: Optional[app_commands.Choice[str]]
    ):
        if len(search_string) < 3:
            character_warning = await ctx.send(
                "Search must be at least 3 characters", ephemeral=True
            )
            await asyncio.sleep(5)
            await character_warning.delete()
            return

        try:
            response = requests.get("https://northstar.thunderstore.io/api/v1/package/")
            if response.status_code == 200:
                data = response.json()

        except requests.exceptions.RequestException as err:
            logger.warning(err)
            return

        mods = {}
        for i, item in enumerate(data):
            if method == "owner":
                match = re.search(search_string, item["owner"], re.IGNORECASE)
            else:
                match = re.search(search_string, item["name"], re.IGNORECASE)
            if match:
                if item[
                    "has_nsfw_content"
                ]:  # Prevent mods labelled as containing NSFW content from appearing in searches
                    continue
                downloads = 0
                for version in item["versions"]:
                    downloads = downloads + version["downloads"]
                mods[item["owner"] + "." + item["name"]] = {
                    "name": item["name"].replace("_", " "),
                    "owner": item["owner"],
                    "icon_url": item["versions"][0]["icon"],
                    "ts_url": item["package_url"],
                    "last_update": item["date_updated"][
                        : (item["date_updated"].index("T"))
                    ],  # Remove time from date string
                    "total_dl": downloads,
                    "description": item["versions"][0]["description"],
                }

        if not mods:
            no_mods_warning = await ctx.send("No mods found")
            await asyncio.sleep(5)
            await no_mods_warning.delete()
            return

        # Sort mods by most downloaded by default until we get better sorting later
        sorted_mods_by_dl = dict(
            sorted(mods.items(), key=lambda item: item[1]["total_dl"], reverse=True)
        )

        pages = list(sorted_mods_by_dl.keys())

        pagination_view = PaginationView()
        pagination_view.data_key = pages
        pagination_view.data = sorted_mods_by_dl
        await pagination_view.send(ctx)
        return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModSearch(bot))
