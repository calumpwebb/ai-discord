import discord
from discord.ext import commands


def create_bot(settings):
    """Create and configure Discord bot"""

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    return bot
