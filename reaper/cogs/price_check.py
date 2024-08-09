import typing, requests
from discord.ext import commands
from bs4 import BeautifulSoup
from discord import app_commands

TF2_STORE_STEAMAPI_URL = "https://store.steampowered.com/api/appdetails?appids=1237970"


class PriceCheck(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        description="Display current price of Titanfall 2 on Steam"
    )
    @app_commands.choices(
        region=[
            app_commands.Choice(name="US", value="US"),
            app_commands.Choice(name="EU", value="DE"),
            app_commands.Choice(name="CA", value="CA"),
            app_commands.Choice(name="AU", value="AU"),
            app_commands.Choice(name="GB", value="GB"),
        ]
    )
    async def price(self, ctx, region: typing.Optional[app_commands.Choice[str]]):
        # Initial request sent to the Steam API to make sure TF2 is on sale
        # Price values are returned via bs4 scraping so we can have regional prices
        try:
            api_response = requests.get(TF2_STORE_STEAMAPI_URL)

            if api_response.status_code == 200:
                data = api_response.json()
            else:
                message = f"Steam API returned code: {api_response.status_code}"
                await ctx.send(message)
                return
        except requests.exceptions.RequestException as err:
            message = f"Steam API Request failed: {err}"
            await ctx.send(message)
            return

        sale_percent = data["1237970"]["data"]["price_overview"]["discount_percent"]

        if sale_percent != 0:
            base_url = "https://store.steampowered.com/app/1237970/Titanfall_2/?cc="

            if region is None:
                try:
                    response = requests.get(base_url + "US")

                    if response.status_code != 200:
                        message = f"Web request returned code: {response.status_code}"
                        await ctx.send(message)
                        return

                except requests.exceptions.RequestException as err:
                    message = f"Web request failed: {err}"
                    await ctx.send(message)
                    return

            else:
                try:
                    response = requests.get(base_url + region.value)

                    if response.status_code != 200:
                        message = f"Web request returned code: {response.status_code}"
                        await ctx.send(message)
                        return

                except requests.exceptions.RequestException as err:
                    message = f"Web request failed: {err}"
                    await ctx.send(message)
                    return

            soup = BeautifulSoup(response.content, "lxml")
            final_price = soup.find("div", class_="discount_final_price")
            standard_price = soup.find("div", class_="discount_original_price")
            message = f"Titanfall 2 is **ON SALE for {str(sale_percent)}% OFF**!\nStandard Price: **{standard_price.text.strip()}**\nSale Price: **{final_price.text.strip()}**\n<https://store.steampowered.com/app/1237970/Titanfall_2/>"
            await ctx.send(message)
            return

        else:
            base_url = "https://store.steampowered.com/app/1237970/Titanfall_2/?cc="
            if region is None:
                try:
                    response = requests.get(base_url + "US")

                    if response.status_code != 200:
                        message = f"Web request returned code: {response.status_code}"
                        await ctx.send(message)
                        return

                except requests.exceptions.RequestException as err:
                    message = f"Web request failed: {err}"
                    await ctx.send(message)
                    return

            else:
                try:
                    response = requests.get(base_url + region.value)

                    if response.status_code != 200:
                        message = f"Web request returned code: {response.status_code}"
                        await ctx.send(message)
                        return

                except requests.exceptions.RequestException as err:
                    message = f"Web request failed: {err}"
                    await ctx.send(message)
                    return

            soup = BeautifulSoup(response.content, "lxml")
            standard_price = soup.find("div", class_="game_purchase_price")
            message = f"Titanfall 2 is **not** on sale.\nCurrent Price: **{standard_price.text.strip()}**\n<https://store.steampowered.com/app/1237970/Titanfall_2/>"
            await ctx.send(message)
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PriceCheck(bot))
