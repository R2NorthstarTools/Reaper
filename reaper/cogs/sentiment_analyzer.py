import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)


from transformers import pipeline
from discord.ext import commands
import asyncio
import random
from util import globals


class SentimentAnalyzer(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.sentiment = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
        )
        self.reset_message_cache()

    def reset_message_cache(self):
        self.bot.cached_sentiment = {}
        for channel in globals.config["channels"]["sentiment-analysis-channels"]:
            self.bot.cached_sentiment[channel] = {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
            }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content:
            return
        if (
            message.channel.id
            not in globals.config["channels"]["sentiment-analysis-channels"]
        ):
            return
        msg_ratio = globals.config["general"]["sentiment-analysis-ratio"]
        if random.randint(1, msg_ratio) != 1:
            return

        try:
            result = await asyncio.to_thread(
                self.sentiment, message.content
            )  # need to do this otherwise the bot will not do anything until this is done
        except Exception as e:
            logger.error(f"Error in sentiment analyzer: {e}")
            return

        self.bot.cached_sentiment[message.channel.id][result[0]["label"]] += 1

        total_negative = self.bot.cached_sentiment[message.channel.id]["negative"]
        total_normal = (
            self.bot.cached_sentiment[message.channel.id]["neutral"]
            + self.bot.cached_sentiment[message.channel.id]["positive"]
        )

        total = total_negative + total_normal

        messages_to_cache = globals.config["general"]["sentiment-analysis-cache"]

        if total >= messages_to_cache:
            if total_negative > total_normal:
                moderator_channel = self.bot.get_channel(
                    globals.config["channels"]["sentiment-analysis-warn-channel"]
                )
                await moderator_channel.send(
                    f"Negative sentiment detected in {message.jump_url}! Out of the last {messages_to_cache} messages, {total_negative} were negative."
                )
            self.reset_message_cache()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SentimentAnalyzer(bot))
