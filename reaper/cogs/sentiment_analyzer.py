import discord
from transformers import pipeline
from discord.ext import commands


class SentimentAnalyzer(commands.Cog):

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        sentiments = [
            pipeline(
                "sentiment-analysis",
                model="finiteautomata/bertweet-base-sentiment-analysis",
                tokenizer="finiteautomata/bertweet-base-sentiment-analysis",
            ),
            pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
            ),
            pipeline(
                "sentiment-analysis",
                model="avichr/heBERT_sentiment_analysis",
                tokenizer="avichr/heBERT_sentiment_analysis",
            )
        ]
        for sentiment in sentiments:
            try:
                await message.channel.send(sentiment(message.content))
            except:
                await message.channel.send("Message too big for model.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SentimentAnalyzer(bot))
